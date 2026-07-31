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

    def test_rejects_non_string_message_content(self) -> None:
        response = valid_response()
        response["choices"] = [{"message": {"role": "assistant", "content": None}}]

        with self.assertRaises(UpstreamProviderError) as ctx:
            normalize_chat_completion_response(MODEL, response)

        self.assertIn("content", str(ctx.exception))


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


if __name__ == "__main__":
    unittest.main()
