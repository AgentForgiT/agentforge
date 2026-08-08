"""MCP client mode (ADR-0039): the gateway calls remote MCP servers.

Outbound mirror of the inbound ``/mcp`` server surface.
- stdlib-only HTTP JSON-RPC 2.0 transport (urllib), injectable for offline tests.
- Keyless by default (local trust boundary); optional auth header via env name.
- Error translation: remote failures surface as ``upstream_provider_error``
  envelopes, never raw exceptions to the gateway client.
"""

from __future__ import annotations

import json
import os
import time
import urllib.request
from collections.abc import Callable
from typing import Any

from .config import McpServerConfig
from .errors import GatewayError

# Transport signature: (url, body_dict, headers_dict, timeout) -> (status, response_text)
Transport = Callable[[str, dict[str, Any], dict[str, str], float], tuple[int, str]]


class McpClientError(GatewayError):
    """A remote MCP server call failed and was translated to an error record."""


class McpClient:
    """JSON-RPC 2.0 client for one remote MCP server.

    Lazy by design: nothing hits the network until a method is called.
    """

    def __init__(
        self,
        config: McpServerConfig,
        transport: Transport | None = None,
    ) -> None:
        self.config = config
        self._transport = transport or self._default_transport
        self._request_id = 0

    # ------------------------------------------------------------------ public

    def initialize(self) -> dict[str, Any]:
        """MCP `initialize` handshake. Returns the server's capabilities."""
        result = self._call("initialize", {"protocolVersion": "2025-03-26", "capabilities": {}})
        if not isinstance(result, dict):
            raise McpClientError(f"mcp server '{self.config.name}': initialize returned a non-object")
        return result

    def tools_list(self) -> list[dict[str, Any]]:
        """MCP `tools/list`. Returns the remote tool definitions list."""
        result = self._call("tools/list", {})
        tools = result.get("tools") if isinstance(result, dict) else None
        if not isinstance(tools, list):
            raise McpClientError(f"mcp server '{self.config.name}': tools/list returned no tools array")
        return tools

    def tools_call(self, name: str, arguments: dict[str, Any] | None) -> str:
        """MCP `tools/call`. Flattens the remote content array to a string."""
        result = self._call("tools/call", {"name": name, "arguments": arguments or {}})
        if not isinstance(result, dict):
            raise McpClientError(f"mcp server '{self.config.name}': tools/call returned a non-object")
        if result.get("isError"):
            content = result.get("content")
            detail = _flatten_content(content) if content else "unknown error"
            raise McpClientError(f"mcp server '{self.config.name}': tool '{name}' failed: {detail}")
        return _flatten_content(result.get("content"))

    # ------------------------------------------------------------------ #
    # transport
    # ------------------------------------------------------------------ #

    def _call(self, method: str, params: dict[str, Any]) -> Any:
        self._request_id += 1
        body = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": method,
            "params": params,
        }
        headers = {"Content-Type": "application/json"}
        if self.config.auth_header_env:
            token = os.environ.get(self.config.auth_header_env)
            if not token:
                raise McpClientError(
                    f"mcp server '{self.config.name}': auth header env ${self.config.auth_header_env} is not set"
                )
            headers["Authorization"] = f"Bearer {token}"

        status, text = self._transport(self.config.url, body, headers, self.config.timeout_seconds)
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            raise McpClientError(
                f"mcp server '{self.config.name}': non-JSON response (HTTP {status})"
            ) from None

        if status >= 400:
            message = parsed.get("error", {}).get("message") if isinstance(parsed, dict) else None
            raise McpClientError(
                f"mcp server '{self.config.name}': HTTP {status}"
                + (f": {message}" if message else "")
            )

        if not isinstance(parsed, dict):
            raise McpClientError(f"mcp server '{self.config.name}': response is not a JSON-RPC object")
        if "error" in parsed and parsed["error"] is not None:
            err = parsed["error"]
            message = err.get("message") if isinstance(err, dict) else str(err)
            code = err.get("code") if isinstance(err, dict) else None
            raise McpClientError(
                f"mcp server '{self.config.name}': JSON-RPC error {code}: {message}"
            )
        return parsed.get("result")

    @staticmethod
    def _default_transport(url: str, body: dict[str, Any], headers: dict[str, str], timeout: float) -> tuple[int, str]:
        request = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - config-declared local endpoint
            return response.status, response.read().decode("utf-8", errors="replace")


def _flatten_content(content: Any) -> str:
    """Flatten an MCP content array (text parts) to a single string."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
            elif isinstance(item, str):
                parts.append(item)
        return "\n".join(parts)
    return str(content or "")


def build_mcp_clients(
    configs: dict[str, McpServerConfig],
    transport: Transport | None = None,
) -> dict[str, McpClient]:
    """Build one :class:`McpClient` per configured server (lazy, no network)."""
    return {name: McpClient(cfg, transport=transport) for name, cfg in configs.items()}