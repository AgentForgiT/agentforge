from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentforge_gateway.config import ModelConfig
from agentforge_gateway.errors import UpstreamProviderError
from agentforge_gateway.responses import normalize_chat_completion_response, normalize_stream_chunk


MODEL = ModelConfig(
    name="public-coder",
    provider="test",
    provider_model="upstream-coder",
)


def valid_chunk() -> dict[str, object]:
    return {
        "id": "chatcmpl-chunk",
        "object": "chat.completion.chunk",
        "created": 123,
        "model": "upstream-coder",
        "choices": [
            {
                "index": 0,
                "delta": {"content": "Hello"},
                "finish_reason": None,
            }
        ],
    }


def valid_response() -> dict[str, object]:
    return {
        "id": "chatcmpl-test",
        "object": "chat.completion",
        "created": 123,
        "model": "upstream-coder",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": "Done."},
                "finish_reason": "stop",
            }
        ],
        "usage": {"total_tokens": 3},
    }


class ChatCompletionResponseTests(unittest.TestCase):
    def test_normalizes_public_model_alias_and_preserves_provider_fields(self) -> None:
        response = valid_response()

        normalized = normalize_chat_completion_response(MODEL, response)

        self.assertEqual(normalized["model"], "public-coder")
        self.assertEqual(normalized["id"], "chatcmpl-test")
        self.assertEqual(normalized["usage"], {"total_tokens": 3})
        self.assertEqual(normalized["choices"], response["choices"])

    def test_does_not_mutate_provider_response(self) -> None:
        response = valid_response()

        normalized = normalize_chat_completion_response(MODEL, response)

        self.assertIsNot(normalized, response)
        self.assertEqual(response["model"], "upstream-coder")

    def test_rejects_non_object_response(self) -> None:
        with self.assertRaises(UpstreamProviderError) as ctx:
            normalize_chat_completion_response(MODEL, [])

        self.assertIn("non-object", str(ctx.exception))

    def test_rejects_missing_chat_completion_object_marker(self) -> None:
        response = valid_response()
        response["object"] = "completion"

        with self.assertRaises(UpstreamProviderError) as ctx:
            normalize_chat_completion_response(MODEL, response)

        self.assertIn("object", str(ctx.exception))

    def test_rejects_missing_choices(self) -> None:
        response = valid_response()
        response.pop("choices")

        with self.assertRaises(UpstreamProviderError) as ctx:
            normalize_chat_completion_response(MODEL, response)

        self.assertIn("choices", str(ctx.exception))

    def test_rejects_empty_choices(self) -> None:
        response = valid_response()
        response["choices"] = []

        with self.assertRaises(UpstreamProviderError) as ctx:
            normalize_chat_completion_response(MODEL, response)

        self.assertIn("choices", str(ctx.exception))

    def test_rejects_non_object_first_choice(self) -> None:
        response = valid_response()
        response["choices"] = ["invalid"]

        with self.assertRaises(UpstreamProviderError) as ctx:
            normalize_chat_completion_response(MODEL, response)

        self.assertIn("choice", str(ctx.exception))

    def test_rejects_missing_assistant_message(self) -> None:
        response = valid_response()
        response["choices"] = [{"index": 0, "finish_reason": "stop"}]

        with self.assertRaises(UpstreamProviderError) as ctx:
            normalize_chat_completion_response(MODEL, response)

        self.assertIn("message", str(ctx.exception))

    def test_rejects_non_assistant_message_role(self) -> None:
        response = valid_response()
        response["choices"] = [{"message": {"role": "user", "content": "Done."}}]

        with self.assertRaises(UpstreamProviderError) as ctx:
            normalize_chat_completion_response(MODEL, response)

        self.assertIn("role", str(ctx.exception))

    def test_accepts_null_message_content_for_reasoning_models(self) -> None:
        response = valid_response()
        response["choices"] = [{"message": {
            "role": "assistant",
            "content": None,
            "reasoning": "reasoning trace emitted by upstream model",
        }}]

        normalized = normalize_chat_completion_response(MODEL, response)

        self.assertIsNone(normalized["choices"][0]["message"]["content"])
        self.assertEqual(
            normalized["choices"][0]["message"]["reasoning"],
            "reasoning trace emitted by upstream model",
        )

    def test_rejects_non_string_non_null_message_content(self) -> None:
        response = valid_response()
        response["choices"] = [{"message": {"role": "assistant", "content": 42}}]

        with self.assertRaises(UpstreamProviderError) as ctx:
            normalize_chat_completion_response(MODEL, response)

        self.assertIn("content", str(ctx.exception))

    def test_accepts_live_reasoning_model_response_shape(self) -> None:
        # Captured from the live OpenRouter exchange (2026-08-01):
        # model openai/gpt-oss-20b:free, provider "Darkbloom".
        response = {
            "id": "gen-1785575446-LRXyfb1EsnREEpteuFUK",
            "object": "chat.completion",
            "created": 1785575446,
            "model": "openai/gpt-oss-20b:free",
            "provider": "Darkbloom",
            "choices": [{
                "index": 0,
                "logprobs": None,
                "finish_reason": "length",
                "native_finish_reason": "length",
                "message": {
                    "role": "assistant",
                    "content": None,
                    "refusal": None,
                    "reasoning": "The user says: \"Reply with exactly: AGENTFORGE_LIVE_OK\".",
                    "reasoning_details": [{
                        "type": "reasoning.text",
                        "text": "The user says: \"Reply with exactly: AGENTFORGE_LIVE_OK\".",
                        "format": "unknown",
                        "index": 0,
                    }],
                },
            }],
            "usage": {"prompt_tokens": 78, "completion_tokens": 20, "total_tokens": 98},
        }

        normalized = normalize_chat_completion_response(MODEL, response)

        message = normalized["choices"][0]["message"]
        self.assertIsNone(message["content"])
        self.assertEqual(message["reasoning"], 'The user says: "Reply with exactly: AGENTFORGE_LIVE_OK".')
        self.assertEqual(message["reasoning_details"][0]["type"], "reasoning.text")
        self.assertEqual(message["reasoning_details"][0]["index"], 0)
        # public alias replaces upstream model id; everything else passes through
        self.assertEqual(normalized["model"], "public-coder")
        self.assertEqual(normalized["provider"], "Darkbloom")
        self.assertEqual(normalized["id"], "gen-1785575446-LRXyfb1EsnREEpteuFUK")


class StreamChunkNormalizationTests(unittest.TestCase):
    def test_normalizes_public_model_alias_and_preserves_chunk_fields(self) -> None:
        chunk = valid_chunk()

        normalized = normalize_stream_chunk(MODEL, chunk)

        self.assertEqual(normalized["model"], "public-coder")
        self.assertEqual(normalized["id"], "chatcmpl-chunk")
        self.assertEqual(normalized["object"], "chat.completion.chunk")
        self.assertEqual(normalized["choices"], chunk["choices"])

    def test_does_not_mutate_provider_chunk(self) -> None:
        chunk = valid_chunk()

        normalized = normalize_stream_chunk(MODEL, chunk)

        self.assertIsNot(normalized, chunk)
        self.assertEqual(chunk["model"], "upstream-coder")

    def test_accepts_finish_reason_string(self) -> None:
        chunk = valid_chunk()
        chunk["choices"][0]["finish_reason"] = "stop"

        normalized = normalize_stream_chunk(MODEL, chunk)

        self.assertEqual(normalized["choices"][0]["finish_reason"], "stop")

    def test_rejects_non_object_chunk(self) -> None:
        with self.assertRaises(UpstreamProviderError) as ctx:
            normalize_stream_chunk(MODEL, [])

        self.assertIn("non-object stream chunk", str(ctx.exception))

    def test_rejects_missing_chunk_object_marker(self) -> None:
        chunk = valid_chunk()
        chunk["object"] = "chat.completion"

        with self.assertRaises(UpstreamProviderError) as ctx:
            normalize_stream_chunk(MODEL, chunk)

        self.assertIn("object", str(ctx.exception))

    def test_rejects_missing_choices(self) -> None:
        chunk = valid_chunk()
        chunk.pop("choices")

        with self.assertRaises(UpstreamProviderError) as ctx:
            normalize_stream_chunk(MODEL, chunk)

        self.assertIn("choices", str(ctx.exception))

    def test_rejects_non_dict_delta(self) -> None:
        chunk = valid_chunk()
        chunk["choices"] = [{"index": 0, "delta": "content", "finish_reason": None}]

        with self.assertRaises(UpstreamProviderError) as ctx:
            normalize_stream_chunk(MODEL, chunk)

        self.assertIn("delta", str(ctx.exception))

    def test_rejects_invalid_finish_reason(self) -> None:
        chunk = valid_chunk()
        chunk["choices"] = [{"index": 0, "delta": {}, "finish_reason": 7}]

        with self.assertRaises(UpstreamProviderError) as ctx:
            normalize_stream_chunk(MODEL, chunk)

        self.assertIn("finish reason", str(ctx.exception))

    def test_accepts_streaming_reasoning_delta_empty_content(self) -> None:
        # Captured from the live OpenRouter exchange (2026-08-01):
        # reasoning models stream delta.content="" with reasoning fields.
        chunk = {
            "id": "gen-1785575555-2HAntMe39OSiIm0c2kQb",
            "object": "chat.completion.chunk",
            "created": 1785575555,
            "model": "openai/gpt-oss-20b:free",
            "provider": "Darkbloom",
            "choices": [{
                "index": 0,
                "delta": {
                    "content": "",
                    "role": "assistant",
                    "reasoning": "The user wants",
                    "reasoning_details": [{
                        "type": "reasoning.text",
                        "text": "The user wants",
                        "format": "unknown",
                        "index": 0,
                    }],
                },
                "finish_reason": None,
                "native_finish_reason": None,
            }],
        }

        normalized = normalize_stream_chunk(MODEL, chunk)

        delta = normalized["choices"][0]["delta"]
        self.assertEqual(delta["content"], "")
        self.assertEqual(delta["reasoning"], "The user wants")
        self.assertEqual(delta["reasoning_details"][0]["type"], "reasoning.text")
        self.assertEqual(normalized["model"], "public-coder")
        self.assertEqual(normalized["provider"], "Darkbloom")

    def test_accepts_streaming_reasoning_delta_null_content(self) -> None:
        chunk = valid_chunk()
        chunk["choices"] = [{
            "index": 0,
            "delta": {"content": None, "role": "assistant", "reasoning": "thinking"},
            "finish_reason": None,
        }]

        normalized = normalize_stream_chunk(MODEL, chunk)

        self.assertIsNone(normalized["choices"][0]["delta"]["content"])
        self.assertEqual(normalized["choices"][0]["delta"]["reasoning"], "thinking")

    def test_accepts_streaming_finish_stop_with_reasoning(self) -> None:
        chunk = valid_chunk()
        chunk["choices"] = [{
            "index": 0,
            "delta": {"content": "", "role": "assistant"},
            "finish_reason": "stop",
        }]

        normalized = normalize_stream_chunk(MODEL, chunk)

        self.assertEqual(normalized["choices"][0]["finish_reason"], "stop")


if __name__ == "__main__":
    unittest.main()
