from __future__ import annotations

import io
import json
import sys
from pathlib import Path
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentforge_gateway.app import GatewayApp
from agentforge_gateway.config import DEFAULT_CONFIG, GatewayConfig
from agentforge_gateway.errors import BadRequestError
from agentforge_gateway.anthropic import (
    normalize_anthropic_response,
    to_openai_body,
    validate_anthropic_messages_request,
)


def anthropic_request(model: str = "mock-coder", stream: bool = False) -> dict[str, object]:
    return {
        "model": model,
        "max_tokens": 1024,
        "stream": stream,
        "messages": [{"role": "user", "content": "Hello"}],
    }


class AnthropicValidationTests(unittest.TestCase):
    def test_valid_request(self) -> None:
        request = validate_anthropic_messages_request(anthropic_request())
        self.assertEqual(request.model, "mock-coder")
        self.assertEqual(request.stream, False)
        self.assertEqual(request.messages[0]["content"], "Hello")

    def test_missing_model(self) -> None:
        with self.assertRaises(BadRequestError):
            validate_anthropic_messages_request({"messages": [{"role": "user", "content": "Hi"}]})

    def test_missing_messages(self) -> None:
        with self.assertRaises(BadRequestError):
            validate_anthropic_messages_request({"model": "mock-coder"})

    def test_empty_messages(self) -> None:
        with self.assertRaises(BadRequestError):
            validate_anthropic_messages_request({"model": "mock-coder", "messages": []})

    def test_non_boolean_stream(self) -> None:
        with self.assertRaises(BadRequestError):
            validate_anthropic_messages_request(anthropic_request(stream="true"))  # type: ignore[arg-type]

    def test_unsupported_role(self) -> None:
        with self.assertRaises(BadRequestError):
            validate_anthropic_messages_request(
                {"model": "mock-coder", "messages": [{"role": "system", "content": "Hi"}]}
            )

    def test_bad_max_tokens(self) -> None:
        with self.assertRaises(BadRequestError):
            validate_anthropic_messages_request({**anthropic_request(), "max_tokens": -1})

    def test_string_content_accepted(self) -> None:
        request = validate_anthropic_messages_request(anthropic_request())
        self.assertEqual(request.messages[0]["content"], "Hello")


class AnthropicTranslationTests(unittest.TestCase):
    def test_to_openai_body_flattens_content(self) -> None:
        body = {
            "model": "mock-coder",
            "system": "You are helpful.",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Part one. "},
                        {"type": "text", "text": "Part two."},
                    ],
                }
            ],
        }
        request = validate_anthropic_messages_request(body)
        openai_body = to_openai_body(request)
        self.assertEqual(openai_body["messages"][0]["role"], "system")
        self.assertEqual(openai_body["messages"][0]["content"], "You are helpful.")
        self.assertEqual(openai_body["messages"][1]["role"], "user")
        self.assertEqual(openai_body["messages"][1]["content"], "Part one. \nPart two.")

    def test_to_openai_body_accepts_system_list(self) -> None:
        body = {
            "model": "mock-coder",
            "system": [{"type": "text", "text": "Be brief."}],
            "messages": [{"role": "user", "content": "Hi"}],
        }
        request = validate_anthropic_messages_request(body)
        openai_body = to_openai_body(request)
        self.assertEqual(openai_body["messages"][0]["content"], "Be brief.")

    def test_to_openai_body_rejects_image_block(self) -> None:
        body = {
            "model": "mock-coder",
            "messages": [
                {"role": "user", "content": [{"type": "image", "source": {"type": "base64"}}]}
            ],
        }
        request = validate_anthropic_messages_request(body)
        with self.assertRaises(BadRequestError):
            to_openai_body(request)

    def test_to_openai_body_surfaces_tool_result_as_text(self) -> None:
        body = {
            "model": "mock-coder",
            "messages": [
                {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "t1", "content": "42"}]}
            ],
        }
        request = validate_anthropic_messages_request(body)
        openai_body = to_openai_body(request)
        self.assertEqual(openai_body["messages"][0]["role"], "tool")
        self.assertEqual(openai_body["messages"][0]["content"], "42")

    def test_to_openai_body_rejects_tool_result_without_id(self) -> None:
        body = {
            "model": "mock-coder",
            "messages": [{"role": "user", "content": [{"type": "tool_result", "content": "42"}]}],
        }
        request = validate_anthropic_messages_request(body)
        with self.assertRaises(BadRequestError):
            to_openai_body(request)


class AnthropicResponseTests(unittest.TestCase):
    def test_normalize_anthropic_response(self) -> None:
        model = DEFAULT_CONFIG.models["mock-coder"]
        openai_response = {
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": 123,
            "model": "mock-coder",
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": "Hello there"},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 5, "completion_tokens": 2, "total_tokens": 7},
        }
        result = normalize_anthropic_response(model, openai_response)
        self.assertEqual(result["type"], "message")
        self.assertEqual(result["role"], "assistant")
        self.assertEqual(result["content"], [{"type": "text", "text": "Hello there"}])
        self.assertEqual(result["model"], "mock-coder")
        self.assertEqual(result["stop_reason"], "end_turn")
        self.assertEqual(result["usage"]["input_tokens"], 5)
        self.assertEqual(result["usage"]["output_tokens"], 2)

    def test_normalize_maps_length_finish(self) -> None:
        model = DEFAULT_CONFIG.models["mock-coder"]
        openai_response = {
            "object": "chat.completion",
            "choices": [{"index": 0, "message": {"role": "assistant", "content": "x"}, "finish_reason": "length"}],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1},
        }
        result = normalize_anthropic_response(model, openai_response)
        self.assertEqual(result["stop_reason"], "max_tokens")

    def test_normalize_rejects_bad_shape(self) -> None:
        model = DEFAULT_CONFIG.models["mock-coder"]
        with self.assertRaises(Exception):
            normalize_anthropic_response(model, {"object": "chat.completion", "choices": []})


class AnthropicSseTests(unittest.TestCase):
    def test_stream_event_sequence(self) -> None:
        from agentforge_gateway.anthropic import anthropic_sse_events

        model = DEFAULT_CONFIG.models["mock-coder"]

        def fake_stream():
            yield {"object": "chat.completion.chunk", "choices": [{"index": 0, "delta": {"role": "assistant"}, "finish_reason": None}]}
            yield {"object": "chat.completion.chunk", "choices": [{"index": 0, "delta": {"content": "Hello "}, "finish_reason": None}]}
            yield {"object": "chat.completion.chunk", "choices": [{"index": 0, "delta": {"content": "world"}, "finish_reason": None}]}
            yield {"object": "chat.completion.chunk", "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]}

        events = list(anthropic_sse_events(model, fake_stream()))
        names = [name for name, _ in events]
        self.assertEqual(names, [
            "message_start",
            "content_block_start",
            "content_block_delta",
            "content_block_delta",
            "content_block_stop",
            "message_delta",
            "message_stop",
        ])

        first_name, first_data = events[0]
        self.assertEqual(first_name, "message_start")
        self.assertEqual(first_data["message"]["model"], "mock-coder")

        delta_names = [n for n, _ in events if n == "content_block_delta"]
        delta_data = [d for n, d in events if n == "content_block_delta"]
        self.assertEqual(delta_names, ["content_block_delta", "content_block_delta"])
        self.assertEqual(delta_data[0]["delta"], {"type": "text_delta", "text": "Hello "})
        self.assertEqual(delta_data[1]["delta"], {"type": "text_delta", "text": "world"})

        msg_delta = [d for n, d in events if n == "message_delta"][0]
        self.assertEqual(msg_delta["delta"]["stop_reason"], "end_turn")


class AnthropicToolMappingTests(unittest.TestCase):
    def test_tools_parameter_translates_to_openai_functions(self) -> None:
        body = {
            "model": "mock-coder",
            "tools": [
                {
                    "name": "get_weather",
                    "description": "Get weather for a city",
                    "input_schema": {
                        "type": "object",
                        "properties": {"city": {"type": "string"}},
                        "required": ["city"],
                    },
                }
            ],
            "messages": [{"role": "user", "content": "Weather in Lagos?"}],
        }
        request = validate_anthropic_messages_request(body)
        openai_body = to_openai_body(request)
        self.assertEqual(openai_body["tools"][0]["type"], "function")
        self.assertEqual(openai_body["tools"][0]["function"]["name"], "get_weather")
        self.assertEqual(openai_body["tools"][0]["function"]["parameters"]["required"], ["city"])

    def test_tools_missing_name_rejected(self) -> None:
        body = {
            "model": "mock-coder",
            "tools": [{"description": "no name"}],
            "messages": [{"role": "user", "content": "Hi"}],
        }
        request = validate_anthropic_messages_request(body)
        with self.assertRaises(BadRequestError):
            to_openai_body(request)

    def test_assistant_tool_use_block_translates_to_tool_calls(self) -> None:
        body = {
            "model": "mock-coder",
            "messages": [
                {"role": "user", "content": "Use the tool"},
                {
                    "role": "assistant",
                    "content": [
                        {"type": "text", "text": "Let me check."},
                        {
                            "type": "tool_use",
                            "id": "toolu_01",
                            "name": "get_weather",
                            "input": {"city": "Abuja"},
                        },
                    ],
                },
                {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "toolu_01", "content": "32C"}]},
            ],
        }
        request = validate_anthropic_messages_request(body)
        openai_body = to_openai_body(request)

        assistant = openai_body["messages"][1]
        self.assertEqual(assistant["role"], "assistant")
        self.assertEqual(assistant["content"], "Let me check.")
        self.assertEqual(assistant["tool_calls"][0]["id"], "toolu_01")
        self.assertEqual(assistant["tool_calls"][0]["type"], "function")
        self.assertEqual(assistant["tool_calls"][0]["function"]["name"], "get_weather")
        self.assertEqual(assistant["tool_calls"][0]["function"]["arguments"], '{"city": "Abuja"}')

        tool_msg = openai_body["messages"][2]
        self.assertEqual(tool_msg["role"], "tool")
        self.assertEqual(tool_msg["tool_call_id"], "toolu_01")
        self.assertEqual(tool_msg["content"], "32C")

    def test_tool_result_structured_content_surfaces_text(self) -> None:
        body = {
            "model": "mock-coder",
            "messages": [
                {"role": "user", "content": "Check"},
                {"role": "assistant", "content": [{"type": "tool_use", "id": "t1", "name": "f", "input": {}}]},
                {
                    "role": "user",
                    "content": [
                        {"type": "tool_result", "tool_use_id": "t1", "content": [{"type": "text", "text": "42"}]}
                    ],
                },
            ],
        }
        request = validate_anthropic_messages_request(body)
        openai_body = to_openai_body(request)
        tool_msg = openai_body["messages"][2]
        self.assertEqual(tool_msg["role"], "tool")
        self.assertEqual(tool_msg["content"], "42")

    def test_thinking_param_accepted_and_passed_through(self) -> None:
        body = {
            "model": "mock-coder",
            "thinking": {"type": "enabled", "budget_tokens": 1024},
            "messages": [{"role": "user", "content": "Think hard"}],
        }
        request = validate_anthropic_messages_request(body)
        openai_body = to_openai_body(request)
        self.assertEqual(openai_body["thinking"]["type"], "enabled")


class AnthropicToolResponseTests(unittest.TestCase):
    def test_response_tool_calls_render_as_tool_use_blocks(self) -> None:
        model = DEFAULT_CONFIG.models["mock-coder"]
        openai_response = {
            "object": "chat.completion",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Checking the weather.",
                        "tool_calls": [
                            {
                                "id": "call_1",
                                "type": "function",
                                "function": {"name": "get_weather", "arguments": '{"city": "Lagos"}'},
                            }
                        ],
                    },
                    "finish_reason": "tool_calls",
                }
            ],
            "usage": {"prompt_tokens": 5, "completion_tokens": 3},
        }
        result = normalize_anthropic_response(model, openai_response)
        self.assertEqual(result["content"][0], {"type": "text", "text": "Checking the weather."})
        self.assertEqual(result["content"][1]["type"], "tool_use")
        self.assertEqual(result["content"][1]["id"], "call_1")
        self.assertEqual(result["content"][1]["name"], "get_weather")
        self.assertEqual(result["content"][1]["input"], {"city": "Lagos"})
        self.assertEqual(result["stop_reason"], "tool_use")

    def test_response_tool_calls_malformed_arguments_tolerated(self) -> None:
        model = DEFAULT_CONFIG.models["mock-coder"]
        openai_response = {
            "object": "chat.completion",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {"id": "c1", "type": "function", "function": {"name": "f", "arguments": "{bad json"}}
                        ],
                    },
                    "finish_reason": "tool_calls",
                }
            ],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1},
        }
        result = normalize_anthropic_response(model, openai_response)
        self.assertEqual(result["content"][0]["input"], {})


class AnthropicToolSseTests(unittest.TestCase):
    def test_stream_tool_calls_emit_input_json_delta(self) -> None:
        from agentforge_gateway.anthropic import anthropic_sse_events

        model = DEFAULT_CONFIG.models["mock-coder"]

        def fake_stream():
            yield {"object": "chat.completion.chunk", "choices": [{"index": 0, "delta": {}, "finish_reason": None}]}
            yield {
                "object": "chat.completion.chunk",
                "choices": [
                    {
                        "index": 0,
                        "delta": {
                            "tool_calls": [
                                {
                                    "index": 0,
                                    "id": "call_1",
                                    "type": "function",
                                    "function": {"name": "get_weather", "arguments": ""},
                                }
                            ]
                        },
                        "finish_reason": None,
                    }
                ],
            }
            yield {
                "object": "chat.completion.chunk",
                "choices": [
                    {
                        "index": 0,
                        "delta": {
                            "tool_calls": [
                                {"index": 0, "function": {"arguments": '{"city": "Abuja"}'}}
                            ]
                        },
                        "finish_reason": None,
                    }
                ],
            }
            yield {
                "object": "chat.completion.chunk",
                "choices": [{"index": 0, "delta": {}, "finish_reason": "tool_calls"}],
            }

        events = list(anthropic_sse_events(model, fake_stream()))
        names = [n for n, _ in events]

        # tool-use block starts at index 1 (no text block emitted)
        start_events = [d for n, d in events if n == "content_block_start"]
        self.assertEqual(len(start_events), 1)
        self.assertEqual(start_events[0]["index"], 1)
        self.assertEqual(start_events[0]["content_block"]["type"], "tool_use")
        self.assertEqual(start_events[0]["content_block"]["name"], "get_weather")

        delta_events = [d for n, d in events if n == "content_block_delta"]
        self.assertEqual(len(delta_events), 1)
        self.assertEqual(delta_events[0]["delta"]["type"], "input_json_delta")
        self.assertEqual(delta_events[0]["delta"]["partial_json"], '{"city": "Abuja"}')

        stop_events = [d for n, d in events if n == "content_block_stop"]
        self.assertEqual(len(stop_events), 1)
        self.assertEqual(stop_events[0]["index"], 1)

        # tail is standard
        self.assertEqual(names[-2], "message_delta")
        self.assertEqual(names[-1], "message_stop")

    def test_stream_text_and_tool_blocks_coexist(self) -> None:
        from agentforge_gateway.anthropic import anthropic_sse_events

        model = DEFAULT_CONFIG.models["mock-coder"]

        def fake_stream():
            yield {"object": "chat.completion.chunk", "choices": [{"index": 0, "delta": {"content": "Sure,"}, "finish_reason": None}]}
            yield {
                "object": "chat.completion.chunk",
                "choices": [
                    {
                        "index": 0,
                        "delta": {
                            "tool_calls": [
                                {"index": 0, "id": "c1", "function": {"name": "f", "arguments": "{}"}}
                            ]
                        },
                        "finish_reason": None,
                    }
                ],
            }
            yield {"object": "chat.completion.chunk", "choices": [{"index": 0, "delta": {}, "finish_reason": "tool_calls"}]}

        events = list(anthropic_sse_events(model, fake_stream()))
        starts = [d for n, d in events if n == "content_block_start"]
        # text block index 0, tool block index 1
        self.assertEqual([s["index"] for s in starts], [0, 1])
        self.assertEqual(starts[0]["content_block"]["type"], "text")
        self.assertEqual(starts[1]["content_block"]["type"], "tool_use")
        stops = [d for n, d in events if n == "content_block_stop"]
        self.assertEqual([s["index"] for s in stops], [0, 1])


class AnthropicEndpointTests(unittest.TestCase):
    def test_messages_endpoint_non_streaming(self) -> None:
        from agentforge_gateway.app import create_handler
        from http.server import ThreadingHTTPServer
        import threading

        app = GatewayApp(DEFAULT_CONFIG)
        server = ThreadingHTTPServer(("127.0.0.1", 0), create_handler(app))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        host, port = server.server_address
        base = f"http://{host}:{port}"
        try:
            request = Request(
                f"{base}/v1/messages",
                data=json.dumps(anthropic_request()).encode("utf-8"),
                headers={"Content-Type": "application/json", "x-api-key": "test-key"},
                method="POST",
            )
            with urlopen(request) as response:
                self.assertEqual(response.status, 200)
                body = json.loads(response.read().decode("utf-8"))
            self.assertEqual(body["type"], "message")
            self.assertEqual(body["content"][0]["type"], "text")
            self.assertIn("Mock response from mock-coder", body["content"][0]["text"])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    def test_messages_endpoint_missing_key_ok(self) -> None:
        from agentforge_gateway.app import create_handler
        from http.server import ThreadingHTTPServer
        import threading

        app = GatewayApp(DEFAULT_CONFIG)
        server = ThreadingHTTPServer(("127.0.0.1", 0), create_handler(app))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        host, port = server.server_address
        base = f"http://{host}:{port}"
        try:
            request = Request(
                f"{base}/v1/messages",
                data=json.dumps(anthropic_request()).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(request) as response:
                body = json.loads(response.read().decode("utf-8"))
            self.assertEqual(body["type"], "message")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    def test_messages_endpoint_bad_request_uses_anthropic_envelope(self) -> None:
        from agentforge_gateway.app import create_handler
        from http.server import ThreadingHTTPServer
        import threading

        app = GatewayApp(DEFAULT_CONFIG)
        server = ThreadingHTTPServer(("127.0.0.1", 0), create_handler(app))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        host, port = server.server_address
        base = f"http://{host}:{port}"
        try:
            request = Request(
                f"{base}/v1/messages",
                data=json.dumps({"model": "mock-coder", "messages": []}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with self.assertRaises(HTTPError) as ctx:
                urlopen(request)
            self.assertEqual(ctx.exception.code, 400)
            body = json.loads(ctx.exception.read().decode("utf-8"))
            self.assertEqual(body["type"], "error")
            self.assertEqual(body["error"]["type"], "bad_request")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    def test_messages_endpoint_unknown_model(self) -> None:
        from agentforge_gateway.app import create_handler
        from http.server import ThreadingHTTPServer
        import threading

        app = GatewayApp(DEFAULT_CONFIG)
        server = ThreadingHTTPServer(("127.0.0.1", 0), create_handler(app))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        host, port = server.server_address
        base = f"http://{host}:{port}"
        try:
            request = Request(
                f"{base}/v1/messages",
                data=json.dumps(anthropic_request(model="does-not-exist")).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with self.assertRaises(HTTPError) as ctx:
                urlopen(request)
            self.assertEqual(ctx.exception.code, 404)
            body = json.loads(ctx.exception.read().decode("utf-8"))
            self.assertEqual(body["type"], "error")
            self.assertEqual(body["error"]["type"], "model_not_found")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    def test_messages_endpoint_streaming_wire_format(self) -> None:
        from agentforge_gateway.app import create_handler
        from http.server import ThreadingHTTPServer
        import threading

        app = GatewayApp(DEFAULT_CONFIG)
        server = ThreadingHTTPServer(("127.0.0.1", 0), create_handler(app))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        host, port = server.server_address
        base = f"http://{host}:{port}"
        try:
            request = Request(
                f"{base}/v1/messages",
                data=json.dumps(anthropic_request(stream=True)).encode("utf-8"),
                headers={"Content-Type": "application/json", "x-api-key": "k"},
                method="POST",
            )
            with urlopen(request) as response:
                self.assertEqual(response.status, 200)
                self.assertEqual(response.headers.get("Content-Type"), "text/event-stream")
                raw = response.read().decode("utf-8")

            # Anthropic SSE: each event = "event: <name>\ndata: <json>\n\n"
            events = []
            for block in raw.strip().split("\n\n"):
                lines = block.strip().split("\n")
                if not lines:
                    continue
                event_line = [l for l in lines if l.startswith("event: ")]
                data_line = [l for l in lines if l.startswith("data: ")]
                self.assertTrue(event_line, f"missing event: line in block: {block!r}")
                self.assertTrue(data_line, f"missing data: line in block: {block!r}")
                name = event_line[0][7:]
                payload = json.loads(data_line[0][6:])
                events.append((name, payload))

            names = [n for n, _ in events]
            # structural sequence: fixed head/tail, variable delta count
            self.assertEqual(names[0], "message_start")
            self.assertEqual(names[1], "content_block_start")
            self.assertIn("content_block_delta", names)
            # all deltas contiguous; tail = content_block_stop -> message_delta -> message_stop
            last_delta = max(i for i, n in enumerate(names) if n == "content_block_delta")
            self.assertEqual(names[last_delta + 1:], ["content_block_stop", "message_delta", "message_stop"])
            for i in range(2, last_delta + 1):
                self.assertEqual(names[i], "content_block_delta")

            # every delta carries a text_delta
            for i in range(2, last_delta + 1):
                self.assertEqual(events[i][1]["delta"]["type"], "text_delta")
                self.assertTrue(events[i][1]["delta"]["text"])

            # message_delta carries a stop_reason
            msg_delta = events[last_delta + 2][1]
            self.assertIn(msg_delta["delta"]["stop_reason"], ("end_turn", "max_tokens"))
            # no [DONE] sentinel in Anthropic wire format
            self.assertNotIn("[DONE]", raw)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
