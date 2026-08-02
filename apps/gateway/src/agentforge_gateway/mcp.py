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

RESOURCE_DEFINITIONS = [
    {
        "uri": "models://registry",
        "name": "Model Registry",
        "description": "The live model registry (GET /v1/models shape).",
        "mimeType": "application/json",
    },
    {
        "uri": "models://config",
        "name": "Gateway Configuration",
        "description": "The active gateway configuration, redacted (no secrets).",
        "mimeType": "application/json",
    },
]

PROMPT_DEFINITIONS = [
    {
        "name": "request-builder",
        "description": "Build an OpenAI-compatible chat-completions request body.",
        "arguments": [
            {"name": "model", "required": True, "description": "Gateway model alias"},
            {"name": "system", "required": False, "description": "System prompt"},
            {"name": "user", "required": True, "description": "User message"},
        ],
    },
    {
        "name": "config-review",
        "description": "Review a gateway config for common pitfalls.",
        "arguments": [
            {"name": "config", "required": True, "description": "Gateway config JSON to review"}
        ],
    },
    {
        "name": "error-diagnosis",
        "description": "Explain a gateway error envelope and suggest fixes.",
        "arguments": [
            {"name": "error", "required": True, "description": "Gateway error envelope JSON"}
        ],
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
            if method == "resources/list":
                return _success(request_id, {"resources": RESOURCE_DEFINITIONS})
            if method == "resources/read":
                return _success(request_id, self._read_resource(params))
            if method == "prompts/list":
                return _success(request_id, {"prompts": PROMPT_DEFINITIONS})
            if method == "prompts/get":
                return _success(request_id, self._get_prompt(params))
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
            "capabilities": {
                "tools": {"listChanged": False},
                "resources": {"subscribe": False, "listChanged": False},
                "prompts": {"listChanged": False},
            },
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
        }

    def _read_resource(self, params: Any) -> dict[str, Any]:
        if not isinstance(params, dict):
            raise McpToolError("invalid params")
        uri = params.get("uri")
        if not isinstance(uri, str):
            raise McpToolError("resource uri required")
        if uri == "models://registry":
            text = json.dumps(self.app.models(), indent=2)
        elif uri == "models://config":
            text = json.dumps(_redacted_config(self.app), indent=2)
        else:
            raise McpToolError(f"unknown resource: {uri}")
        return {"contents": [{"uri": uri, "mimeType": "application/json", "text": text}]}

    def _get_prompt(self, params: Any) -> dict[str, Any]:
        if not isinstance(params, dict):
            raise McpToolError("invalid params")
        name = params.get("name")
        if not isinstance(name, str):
            raise McpToolError("prompt name required")
        arguments = params.get("arguments") or {}
        if not isinstance(arguments, dict):
            raise McpToolError("prompt arguments must be an object")

        if name == "request-builder":
            self._require_args(arguments, ["model", "user"])
            model = arguments["model"]
            system = arguments.get("system", "")
            user = arguments["user"]
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": user})
            body = json.dumps({"model": model, "messages": messages}, indent=2)
            return {
                "description": "Build an OpenAI-compatible chat-completions request body.",
                "messages": [
                    {"role": "user", "content": {"type": "text", "text": body}}
                ],
            }
        if name == "config-review":
            self._require_args(arguments, ["config"])
            return {
                "description": "Review a gateway config for common pitfalls.",
                "messages": [
                    {
                        "role": "user",
                        "content": {
                            "type": "text",
                            "text": (
                                "Review this AgentForge gateway config for common pitfalls:\n"
                                "- keyless local trust vs named keys (ADR-0017/0031)\n"
                                "- CORS origin (ADR-0018)\n"
                                "- rate limits (ADR-0023)\n\n"
                                + arguments["config"]
                            ),
                        },
                    }
                ],
            }
        if name == "error-diagnosis":
            self._require_args(arguments, ["error"])
            return {
                "description": "Explain a gateway error envelope and suggest fixes.",
                "messages": [
                    {
                        "role": "user",
                        "content": {
                            "type": "text",
                            "text": (
                                "Explain this AgentForge gateway error envelope and suggest fixes:\n\n"
                                + arguments["error"]
                            ),
                        },
                    }
                ],
            }
        raise McpToolError(f"unknown prompt: {name}")

    @staticmethod
    def _require_args(arguments: dict[str, Any], required: list[str]) -> None:
        missing = [arg for arg in required if not arguments.get(arg)]
        if missing:
            raise McpToolError(f"missing required prompt arguments: {', '.join(missing)}")

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


def _redacted_config(app: Any) -> dict[str, Any]:
    """Config resource view, redacted (ADR-0037 / ADR-0015 privacy).

    Never renders API key values or provider secrets.
    """
    config = app.config
    providers = {}
    for name, provider in config.providers.items():
        entry: dict[str, Any] = {"type": provider.type, "base_url": provider.base_url}
        if provider.api_key_env:
            entry["api_key_env"] = provider.api_key_env
            entry["api_key"] = "***redacted***"
        if provider.headers:
            entry["headers"] = {k: ("***redacted***" if k.lower() in ("authorization", "x-api-key") else v) for k, v in provider.headers.items()}
        providers[name] = entry

    server: dict[str, Any] = {
        "host": config.host,
        "port": config.port,
        "log_level": config.log_level,
        "cors_origin": config.cors_origin,
        "rate_limit_rpm": config.rate_limit_rpm,
    }
    if config.api_key_env:
        server["api_key_env"] = config.api_key_env
        server["api_key"] = "***redacted***"
    if config.auth_keys_file:
        server["auth_keys_file"] = config.auth_keys_file

    return {
        "server": server,
        "models": {
            name: {"provider": model.provider, "provider_model": model.provider_model}
            for name, model in sorted(config.models.items())
        },
        "providers": providers,
    }


def _success(request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _error(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}
