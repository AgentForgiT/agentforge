from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentforge_gateway.errors import error_response, invalid_json_response, not_found_response


class ErrorResponseTests(unittest.TestCase):
    def test_error_response_uses_standard_envelope(self) -> None:
        self.assertEqual(
            error_response("missing", "not_found"),
            {"error": {"message": "missing", "type": "not_found"}},
        )

    def test_not_found_response_uses_standard_envelope(self) -> None:
        self.assertEqual(
            not_found_response(),
            {"error": {"message": "not found", "type": "not_found"}},
        )

    def test_invalid_json_response_uses_standard_envelope(self) -> None:
        self.assertEqual(
            invalid_json_response(),
            {"error": {"message": "invalid JSON body", "type": "bad_request"}},
        )


if __name__ == "__main__":
    unittest.main()
