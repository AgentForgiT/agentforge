from __future__ import annotations

import io
import json
import os
import sys
import unittest
from pathlib import Path
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentforge_gateway.config import ModelConfig, ProviderConfig
from agentforge_gateway.errors import ProviderConfigurationError, UpstreamProviderError
from agentforge_gateway.providers import AnthropicProvider, build_provider, supported_provider_types


def model_config(name: str = "anthropic-sonnet", provider_model: str = "claude-sonnet-4-5") -> ModelConfig:
    return ModelConfig(name=name, provider="anthropic", provider_model=provider_model)


def provider_config(**overrides: object) -> ProviderConfig:
    base: dict[str, object] = {
        "name": "anthropic",
        "type": "anthropic",
        "base_url": "https://api.anthropic.com",
        "api_key_env": "ANTHROPIC_API_KEY",
        "timeout_seconds": 30.0,
        "headers": {},
    }
    base.update(overrides)
    return ProviderConfig(**base)  # type: ignore[arg-type]


class FakeResponse:
    def __init__(self, payload: bytes, status: int = 200) -> None:
        self._payload = payload
        self.status = status

    def read(self) -> bytes:
        return self._payload

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None


class FakeStreamResponse:
    def __init__(self, lines: list[str], status: int = 200) -> None:
        self._buffer = io.BytesIO("".join(lines).encode("utf-8"))
        self.status = status

    def __iter__(self):
        return self

    def __next__(self) -> bytes:
        line = self._buffer.readline()
        if not line:
            raise StopIteration
        return line

    def __enter__(self) -> "FakeStreamResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None


def anthropic_response(content: list[dict[str, object]], stop_reason: str = "end_turn") -> dict[str, object]:
    return {
        "id": "msg_01ABC",
        "type": "message",
        "role": "assistant",
        "content": content,
        "model": "claude-sonnet-4-5",
        "stop_reason": stop_reason,
        "stop_sequence": None,
        "usage": {"input_tokens": 10, "output_tokens": 5},
    }


class AnthropicProviderContractTests(unittest.TestCase):
    def test_success_maps_anthropic_response_to_openai_shape(self) -> None:
        captured: dict[str, object] = {}

        def fake_urlopen(request, timeout: float) -> FakeResponse:
            captured["url"] = request.full_url
            captured["headers"] = dict(request.headers)
            captured["body"] = json.loads(request.data.decode("utf-8"))
            return FakeResponse(json.dumps(anthropic_response([{"type": "text", "text": "Hello from Claude"}])).encode("utf-8"))

        provider = AnthropicProvider(provider_config(), urlopen_fn=fake_urlopen)
        os.environ["ANTHROPIC_API_KEY"] = "sk-ant-test"
        try:
            result = provider.chat_completion(
                model_config(),
                {"model": "x", "messages": [{"role": "user", "content": "Hi"}]},
            )
        finally:
            del os.environ["ANTHROPIC_API_KEY"]

        self.assertEqual(result["object"], "chat.completion")
        self.assertEqual(result["model"], "anthropic-sonnet")
        self.assertEqual(result["choices"][0]["message"]["content"], "Hello from Claude")
        self.assertEqual(result["choices"][0]["finish_reason"], "stop")
        self.assertEqual(result["usage"]["prompt_tokens"], 10)
        self.assertEqual(result["usage"]["completion_tokens"], 5)

    def test_request_uses_anthropic_headers_and_url(self) -> None:
        captured: dict[str, object] = {}

        def fake_urlopen(request, timeout: float) -> FakeResponse:
            captured["url"] = request.full_url
            captured["headers"] = dict(request.headers)
            return FakeResponse(json.dumps(anthropic_response([{"type": "text", "text": "ok"}])).encode("utf-8"))

        provider = AnthropicProvider(provider_config(), urlopen_fn=fake_urlopen)
        os.environ["ANTHROPIC_API_KEY"] = "sk-ant-test"
        try:
            provider.chat_completion(model_config(), {"messages": [{"role": "user", "content": "Hi"}]})
        finally:
            del os.environ["ANTHROPIC_API_KEY"]

        self.assertEqual(captured["url"], "https://api.anthropic.com/v1/messages")
        lowered = {k.lower(): v for k, v in captured["headers"].items()}
        self.assertEqual(lowered["x-api-key"], "sk-ant-test")
        self.assertEqual(lowered["anthropic-version"], "2023-06-01")
        self.assertNotIn("authorization", lowered)

    def test_request_translation_system_fold_and_tools(self) -> None:
        captured: dict[str, object] = {}

        def fake_urlopen(request, timeout: float) -> FakeResponse:
            captured["body"] = json.loads(request.data.decode("utf-8"))
            return FakeResponse(json.dumps(anthropic_response([{"type": "text", "text": "ok"}])).encode("utf-8"))

        provider = AnthropicProvider(provider_config(), urlopen_fn=fake_urlopen)
        os.environ["ANTHROPIC_API_KEY"] = "k"
        try:
            provider.chat_completion(
                model_config(),
                {
                    "messages": [
                        {"role": "system", "content": "You are terse."},
                        {"role": "user", "content": "Hi"},
                    ],
                    "tools": [
                        {
                            "type": "function",
                            "function": {
                                "name": "get_weather",
                                "description": "weather",
                                "parameters": {"type": "object", "properties": {"city": {"type": "string"}}},
                            },
                        }
                    ],
                },
            )
        finally:
            del os.environ["ANTHROPIC_API_KEY"]

        body = captured["body"]
        self.assertEqual(body["system"], "You are terse.")
        self.assertEqual(body["messages"][0]["role"], "user")
        self.assertEqual(body["tools"][0]["name"], "get_weather")
        self.assertEqual(body["tools"][0]["input_schema"]["properties"]["city"]["type"], "string")
        self.assertEqual(body["max_tokens"], 4096)

    def test_request_translation_tool_calls_and_results(self) -> None:
        captured: dict[str, object] = {}

        def fake_urlopen(request, timeout: float) -> FakeResponse:
            captured["body"] = json.loads(request.data.decode("utf-8"))
            return FakeResponse(json.dumps(anthropic_response([{"type": "text", "text": "ok"}])).encode("utf-8"))

        provider = AnthropicProvider(provider_config(), urlopen_fn=fake_urlopen)
        os.environ["ANTHROPIC_API_KEY"] = "k"
        try:
            provider.chat_completion(
                model_config(),
                {
                    "messages": [
                        {"role": "user", "content": "Use tool"},
                        {
                            "role": "assistant",
                            "content": "Checking",
                            "tool_calls": [
                                {
                                    "id": "call_1",
                                    "type": "function",
                                    "function": {"name": "get_weather", "arguments": '{"city": "Lagos"}'},
                                }
                            ],
                        },
                        {"role": "tool", "tool_call_id": "call_1", "content": "32C"},
                    ]
                },
            )
        finally:
            del os.environ["ANTHROPIC_API_KEY"]

        body = captured["body"]
        assistant = body["messages"][1]
        self.assertEqual(assistant["content"][0]["type"], "text")
        self.assertEqual(assistant["content"][1]["type"], "tool_use")
        self.assertEqual(assistant["content"][1]["name"], "get_weather")
        self.assertEqual(assistant["content"][1]["input"], {"city": "Lagos"})
        user = body["messages"][2]
        self.assertEqual(user["content"][0]["type"], "tool_result")
        self.assertEqual(user["content"][0]["tool_use_id"], "call_1")
        self.assertEqual(user["content"][0]["content"], "32C")

    def test_response_tool_use_maps_to_tool_calls(self) -> None:
        def fake_urlopen(request, timeout: float) -> FakeResponse:
            return FakeResponse(
                json.dumps(
                    anthropic_response(
                        [
                            {"type": "text", "text": "Let me check"},
                            {"type": "tool_use", "id": "toolu_1", "name": "get_weather", "input": {"city": "Lagos"}},
                        ],
                        stop_reason="tool_use",
                    )
                ).encode("utf-8")
            )

        provider = AnthropicProvider(provider_config(), urlopen_fn=fake_urlopen)
        os.environ["ANTHROPIC_API_KEY"] = "k"
        try:
            result = provider.chat_completion(model_config(), {"messages": [{"role": "user", "content": "Weather?"}]})
        finally:
            del os.environ["ANTHROPIC_API_KEY"]

        self.assertEqual(result["choices"][0]["finish_reason"], "tool_calls")
        message = result["choices"][0]["message"]
        self.assertEqual(message["content"], "Let me check")
        self.assertEqual(message["tool_calls"][0]["id"], "toolu_1")
        self.assertEqual(message["tool_calls"][0]["function"]["name"], "get_weather")
        self.assertEqual(json.loads(message["tool_calls"][0]["function"]["arguments"]), {"city": "Lagos"})

    def test_missing_api_key_raises_configuration_error(self) -> None:
        provider = AnthropicProvider(provider_config())
        with self.assertRaises(ProviderConfigurationError):
            provider.chat_completion(model_config(), {"messages": [{"role": "user", "content": "Hi"}]})

    def test_http_error_translates_to_upstream_error(self) -> None:
        def fake_urlopen(request, timeout: float) -> FakeResponse:
            raise HTTPError(
                "https://api.anthropic.com/v1/messages",
                401,
                "Unauthorized",
                None,
                io.BytesIO(b'{"type":"error","error":{"type":"authentication_error","message":"bad key"}}'),
            )

        provider = AnthropicProvider(provider_config(), urlopen_fn=fake_urlopen)
        os.environ["ANTHROPIC_API_KEY"] = "k"
        try:
            with self.assertRaises(UpstreamProviderError):
                provider.chat_completion(model_config(), {"messages": [{"role": "user", "content": "Hi"}]})
        finally:
            del os.environ["ANTHROPIC_API_KEY"]

    def test_streaming_translates_anthropic_events_to_openai_chunks(self) -> None:
        def fake_urlopen(request, timeout: float) -> FakeStreamResponse:
            events = [
                {"type": "message_start", "message": {"id": "msg_1", "type": "message", "role": "assistant", "content": []}},
                {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}},
                {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "Hello "}},
                {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "world"}},
                {"type": "content_block_stop", "index": 0},
                {"type": "message_delta", "delta": {"stop_reason": "end_turn", "stop_sequence": None}, "usage": {"output_tokens": 5}},
                {"type": "message_stop"},
            ]
            lines = ["event: " + e["type"] + "\n" + "data: " + json.dumps(e) + "\n\n" for e in events]
            return FakeStreamResponse(lines)

        provider = AnthropicProvider(provider_config(), urlopen_fn=fake_urlopen)
        os.environ["ANTHROPIC_API_KEY"] = "k"
        try:
            chunks = list(provider.chat_completion_stream(model_config(), {"messages": [{"role": "user", "content": "Hi"}], "stream": True}))
        finally:
            del os.environ["ANTHROPIC_API_KEY"]

        self.assertEqual(chunks[0]["object"], "chat.completion.chunk")
        self.assertEqual(chunks[0]["choices"][0]["delta"]["role"], "assistant")
        texts = [c["choices"][0]["delta"]["content"] for c in chunks if "content" in c["choices"][0]["delta"]]
        self.assertEqual(texts, ["Hello ", "world"])
        finish = [c["choices"][0]["finish_reason"] for c in chunks if c["choices"][0]["finish_reason"]]
        self.assertEqual(finish, ["stop"])

    def test_streaming_tool_input_json_delta_maps_to_tool_calls(self) -> None:
        def fake_urlopen(request, timeout: float) -> FakeStreamResponse:
            events = [
                {"type": "message_start", "message": {"id": "msg_1"}},
                {"type": "content_block_start", "index": 0, "content_block": {"type": "tool_use", "id": "toolu_1", "name": "f", "input": {}}},
                {"type": "content_block_delta", "index": 0, "delta": {"type": "input_json_delta", "partial_json": '{"a": 1}'}},
                {"type": "content_block_stop", "index": 0},
                {"type": "message_delta", "delta": {"stop_reason": "tool_use"}},
                {"type": "message_stop"},
            ]
            lines = ["event: " + e["type"] + "\n" + "data: " + json.dumps(e) + "\n\n" for e in events]
            return FakeStreamResponse(lines)

        provider = AnthropicProvider(provider_config(), urlopen_fn=fake_urlopen)
        os.environ["ANTHROPIC_API_KEY"] = "k"
        try:
            chunks = list(provider.chat_completion_stream(model_config(), {"messages": [{"role": "user", "content": "Hi"}], "stream": True}))
        finally:
            del os.environ["ANTHROPIC_API_KEY"]

        tool_deltas = [c for c in chunks if c["choices"][0]["delta"].get("tool_calls")]
        self.assertEqual(len(tool_deltas), 1)
        self.assertEqual(tool_deltas[0]["choices"][0]["delta"]["tool_calls"][0]["function"]["arguments"], '{"a": 1}')
        finish = [c["choices"][0]["finish_reason"] for c in chunks if c["choices"][0]["finish_reason"]]
        self.assertEqual(finish, ["tool_calls"])


class AnthropicProviderRegistrationTests(unittest.TestCase):
    def test_build_provider_returns_anthropic_provider(self) -> None:
        provider = build_provider(provider_config())
        self.assertIsInstance(provider, AnthropicProvider)

    def test_supported_provider_types_includes_anthropic(self) -> None:
        self.assertIn("anthropic", supported_provider_types())

    def test_example_config_parses(self) -> None:
        from agentforge_gateway.config import load_config

        config = load_config(ROOT / "config.anthropic.example.json")
        self.assertEqual(config.models["anthropic-sonnet"].provider, "anthropic")
        self.assertEqual(config.providers["anthropic"].type, "anthropic")
        self.assertEqual(config.providers["anthropic"].api_key_env, "ANTHROPIC_API_KEY")


if __name__ == "__main__":
    unittest.main()
