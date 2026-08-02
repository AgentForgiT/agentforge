from __future__ import annotations

from typing import Any
import json

from .errors import GatewayError
from .logger import get_logger

PROTOCOL_VERSION = "2026-07-28"
SERVER_NAME = "agentforge-gateway"
SERVER_VERSION = "0.0.29"

# JSON-RPC error codes
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603

TOOL_DEFINITIONS = [
    {
        "name": "gateway_health",
        "description": "Report the AgentForge gateway health status.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "gateway_list_models",
        "description": "List the models registered on the AgentForge gateway.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "gateway_chat_completion",
        "description": "Run a chat completion through the gateway (OpenAI surface).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "model": {"type": "string", "description": "Gateway model alias"},
                "messages": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "role": {"type": "string"},
                            "content": {"type": "string"},
                        },
                    },
                },
            },
            "required": ["model", "messages"],
        },
    },
    {
        "name": "gateway_anthropic_message",
        "description": "Run an Anthropic Messages call through the gateway (Anthropic surface).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "model": {"type": "string", "description": "Gateway model alias"},
                "messages": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "role": {"type": "string"},
                            "content": {"type": "string"},
                        },
                    },
                },
                "max_tokens": {"type": "integer", "default": 4096},
            },
            "required": ["model", "messages"],
        },
    },
]


class McpServer:
    """Minimal stdlib MCP (Model Context Protocol) server over JSON-RPC 2.0.

    Exposes gateway capabilities as tools (ADR-0026). The gateway app
    provides the capability functions; this class handles the protocol.
    """

    def __init__(self, app: Any) -> None:
        self.app = app

    def handle(self, raw_body: str) -> dict[str, Any]:
        try:
            request = json.loads(raw_body)
        except json.JSONDecodeError:
            return _error(None, PARSE_ERROR, "parse error")

        if not isinstance(request, dict) or request.get("jsonrpc") != "2.0":
            return _error(None, INVALID_REQUEST, "invalid request")

        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params") or {}
        if not isinstance(method, str):
            return _error(request_id, INVALID_REQUEST, "invalid request")

        try:
            if method == "initialize":
                return _success(request_id, self._initialize(params))
            if method == "tools/list":
                return _success(request_id, {"tools": TOOL_DEFINITIONS})
            if method == "tools/call":
                return _success(request_id, self._call_tool(params))
            if method in ("resources/list", "prompts/list"):
                return _success(request_id, {"resources": []} if method == "resources/list" else {"prompts": []})
            return _error(request_id, METHOD_NOT_FOUND, f"method not found: {method}")
        except McpToolError as exc:
            return _error(request_id, INVALID_PARAMS, str(exc))
        except GatewayError as exc:
            get_logger().error("mcp tool gateway error: %s", exc.message)
            return _success(
                request_id,
                {"content": [{"type": "text", "text": f"gateway error: {exc.message}"}], "isError": True},
            )
        except Exception:
            get_logger().error("mcp internal error", exc_info=True)
            return _error(request_id, INTERNAL_ERROR, "internal error")

    # --- protocol handlers ---

    def _initialize(self, params: Any) -> dict[str, Any]:
        return {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
        }

    def _call_tool(self, params: Any) -> dict[str, Any]:
        if not isinstance(params, dict):
            raise McpToolError("invalid params")
        name = params.get("name")
        arguments = params.get("arguments") or {}
        if not isinstance(name, str):
            raise McpToolError("tool name required")
        if not isinstance(arguments, dict):
            raise McpToolError("tool arguments must be an object")

        if name == "gateway_health":
            text = json.dumps(self.app.health())
        elif name == "gateway_list_models":
            text = json.dumps(self.app.models())
        elif name == "gateway_chat_completion":
            text = self._chat_completion(arguments)
        elif name == "gateway_anthropic_message":
            text = self._anthropic_message(arguments)
        else:
            raise McpToolError(f"unknown tool: {name}")

        return {"content": [{"type": "text", "text": text}], "isError": False}

    def _chat_completion(self, arguments: dict[str, Any]) -> str:
        model = arguments.get("model")
        messages = arguments.get("messages")
        if not isinstance(model, str) or not isinstance(messages, list):
            raise McpToolError("gateway_chat_completion requires model (string) and messages (array)")
        response = self.app.chat_completions({"model": model, "messages": messages, "stream": False})
        choices = response.get("choices")
        if not isinstance(choices, list) or not choices:
            raise GatewayError("provider returned no choices")
        message = choices[0].get("message") if isinstance(choices[0], dict) else None
        content = message.get("content") if isinstance(message, dict) else None
        return content if isinstance(content, str) else json.dumps(response)

    def _anthropic_message(self, arguments: dict[str, Any]) -> str:
        model = arguments.get("model")
        messages = arguments.get("messages")
        if not isinstance(model, str) or not isinstance(messages, list):
            raise McpToolError("gateway_anthropic_message requires model (string) and messages (array)")
        max_tokens = arguments.get("max_tokens", 4096)
        body: dict[str, Any] = {"model": model, "messages": messages, "max_tokens": max_tokens, "stream": False}
        response = self.app.anthropic_messages(body)
        content = response.get("content")
        if isinstance(content, list):
            parts = [str(block.get("text", "")) for block in content if isinstance(block, dict) and block.get("type") == "text"]
            return "".join(parts)
        return json.dumps(response)


class McpToolError(Exception):
    pass


def _success(request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _error(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}
