from __future__ import annotations

import json
from urllib.error import HTTPError


def sse_data(line: bytes | str) -> str | None:
    text = line.decode("utf-8").strip() if isinstance(line, bytes) else str(line).strip()
    if not text or not text.startswith("data:"):
        return None
    return text[len("data:") :].strip()


def http_error_message(provider_name: str, exc: HTTPError) -> str:
    raw = exc.read().decode("utf-8", errors="replace")
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = {}

    message = raw.strip()
    if isinstance(parsed, dict):
        error = parsed.get("error")
        if isinstance(error, dict) and error.get("message"):
            message = str(error["message"])
        elif parsed.get("message"):
            message = str(parsed["message"])

    return f"provider '{provider_name}' request failed with status {exc.code}: {message}"
