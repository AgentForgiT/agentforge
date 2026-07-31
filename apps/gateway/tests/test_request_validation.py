from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentforge_gateway.errors import BadRequestError
from agentforge_gateway.requests import validate_chat_completion_request


class ChatCompletionRequestValidationTests(unittest.TestCase):
    def test_valid_request_returns_typed_result_and_preserves_body(self) -> None:
        body = {
            "model": "mock-coder",
            "messages": [{"role": "user", "content": "Hello"}],
            "temperature": 0.2,
        }

        request = validate_chat_completion_request(body)

        self.assertEqual(request.model, "mock-coder")
        self.assertEqual(request.messages, [{"role": "user", "content": "Hello"}])
        self.assertIs(request.body, body)
        self.assertEqual(request.body["temperature"], 0.2)

    def test_rejects_missing_model(self) -> None:
        with self.assertRaises(BadRequestError) as ctx:
            validate_chat_completion_request({"messages": [{"role": "user", "content": "Hello"}]})

        self.assertIn("request requires a model", str(ctx.exception))

    def test_rejects_empty_model(self) -> None:
        with self.assertRaises(BadRequestError) as ctx:
            validate_chat_completion_request({"model": "", "messages": [{"role": "user", "content": "Hello"}]})

        self.assertIn("request requires a model", str(ctx.exception))

    def test_rejects_missing_messages(self) -> None:
        with self.assertRaises(BadRequestError) as ctx:
            validate_chat_completion_request({"model": "mock-coder"})

        self.assertIn("request requires non-empty messages", str(ctx.exception))

    def test_rejects_non_list_messages(self) -> None:
        with self.assertRaises(BadRequestError) as ctx:
            validate_chat_completion_request({"model": "mock-coder", "messages": "Hello"})

        self.assertIn("request requires non-empty messages", str(ctx.exception))

    def test_rejects_empty_messages(self) -> None:
        with self.assertRaises(BadRequestError) as ctx:
            validate_chat_completion_request({"model": "mock-coder", "messages": []})

        self.assertIn("request requires non-empty messages", str(ctx.exception))

    def test_accepts_stream_true(self) -> None:
        request = validate_chat_completion_request(
            {
                "model": "mock-coder",
                "stream": True,
                "messages": [{"role": "user", "content": "Hello"}],
            }
        )

        self.assertTrue(request.stream)

    def test_stream_defaults_to_false(self) -> None:
        request = validate_chat_completion_request(
            {"model": "mock-coder", "messages": [{"role": "user", "content": "Hello"}]}
        )

        self.assertFalse(request.stream)

    def test_accepts_stream_false(self) -> None:
        request = validate_chat_completion_request(
            {
                "model": "mock-coder",
                "stream": False,
                "messages": [{"role": "user", "content": "Hello"}],
            }
        )

        self.assertFalse(request.stream)

    def test_rejects_non_boolean_stream(self) -> None:
        with self.assertRaises(BadRequestError) as ctx:
            validate_chat_completion_request(
                {
                    "model": "mock-coder",
                    "stream": "true",
                    "messages": [{"role": "user", "content": "Hello"}],
                }
            )

        self.assertIn("stream must be a boolean", str(ctx.exception))

    def test_rejects_numeric_stream(self) -> None:
        with self.assertRaises(BadRequestError) as ctx:
            validate_chat_completion_request(
                {
                    "model": "mock-coder",
                    "stream": 1,
                    "messages": [{"role": "user", "content": "Hello"}],
                }
            )

        self.assertIn("stream must be a boolean", str(ctx.exception))

    def test_rejects_malformed_message(self) -> None:
        with self.assertRaises(BadRequestError) as ctx:
            validate_chat_completion_request({"model": "mock-coder", "messages": [{"role": "user"}]})

        self.assertIn("each message requires role and content", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
