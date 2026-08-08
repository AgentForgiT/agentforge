"""Offline tests for MCP client mode (ADR-0039) — no network, no keys.

The transport is injected as a fake returning canned JSON-RPC responses and
recording the requests it received, so the whole module is deterministic.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentforge_gateway.app import GatewayApp
from agentforge_gateway.config import DEFAULT_CONFIG, GatewayConfig, ModelConfig, ProviderConfig, McpServerConfig
from agentforge_gateway.errors import GatewayError
from agentforge_gateway.mcpclient import McpClient, McpClientError, build_mcp_clients


def _config_with_mcp(mcp_servers: dict[str, McpServerConfig]) -> GatewayConfig:
    base = DEFAULT_CONFIG
    return GatewayConfig(
        host=base.host,
        port=base.port,
        models=base.models,
        providers=base.providers,
        log_level=base.log_level,
        mcp_servers=mcp_servers,
    )


def _mcp_server(name: str, url: str = "http://127.0.0.1:3001/mcp") -> McpServerConfig:
    return McpServerConfig(name=name, url=url)


class FakeMcpTransport:
    """Records JSON-RPC requests; returns canned responses per method."""

    def __init__(self, responses: dict[str, object] | None = None, status: int = 200, raw_text: str | None = None) -> None:
        self.calls: list[dict[str, object]] = []
        self.responses = responses or {}
        self.status = status
        self.raw_text = raw_text

    def __call__(self, url: str, body: dict[str, object], headers: dict[str, str], timeout: float) -> tuple[int, str]:
        self.calls.append({"url": url, "body": body, "headers": headers, "timeout": timeout})
        if self.raw_text is not None:
            return self.status, self.raw_text
        method = body["method"]
        result = self.responses.get(method, {"ok": True})
        return self.status, json.dumps({"jsonrpc": "2.0", "id": body["id"], "result": result})


class McpClientUnitTests(unittest.TestCase):
    def test_initialize_sends_handshake(self) -> None:
        transport = FakeMcpTransport(responses={"initialize": {"protocolVersion": "2025-03-26", "capabilities": {}}})
        client = McpClient(_mcp_server("files"), transport=transport)
        result = client.initialize()
        self.assertEqual(result["protocolVersion"], "2025-03-26")
        self.assertEqual(transport.calls[0]["body"]["method"], "initialize")
        self.assertEqual(transport.calls[0]["body"]["params"]["protocolVersion"], "2025-03-26")
        self.assertEqual(transport.calls[0]["url"], "http://127.0.0.1:3001/mcp")

    def test_tools_list_returns_tools(self) -> None:
        transport = FakeMcpTransport(responses={"tools/list": {"tools": [{"name": "read_file", "description": "Read a file"}]}})
        client = McpClient(_mcp_server("files"), transport=transport)
        tools = client.tools_list()
        self.assertEqual(tools[0]["name"], "read_file")

    def test_tools_call_flattens_content(self) -> None:
        transport = FakeMcpTransport(
            responses={"tools/call": {"content": [{"type": "text", "text": "line1"}, {"type": "text", "text": "line2"}]}}
        )
        client = McpClient(_mcp_server("files"), transport=transport)
        result = client.tools_call("read_file", {"path": "/tmp/x"})
        self.assertEqual(result, "line1\nline2")
        self.assertEqual(transport.calls[0]["body"]["method"], "tools/call")
        self.assertEqual(transport.calls[0]["body"]["params"]["arguments"], {"path": "/tmp/x"})

    def test_http_error_translates_to_mcp_client_error(self) -> None:
        transport = FakeMcpTransport(status=500, raw_text=json.dumps({"error": {"message": "boom"}}))
        client = McpClient(_mcp_server("files"), transport=transport)
        with self.assertRaises(McpClientError) as ctx:
            client.tools_list()
        self.assertIn("HTTP 500", str(ctx.exception))
        self.assertIn("boom", str(ctx.exception))

    def test_json_rpc_error_translates(self) -> None:
        transport = FakeMcpTransport()
        transport.raw_text = json.dumps({"jsonrpc": "2.0", "id": 1, "error": {"code": -32601, "message": "Method not found"}})
        client = McpClient(_mcp_server("files"), transport=transport)
        with self.assertRaises(McpClientError) as ctx:
            client.tools_list()
        self.assertIn("-32601", str(ctx.exception))
        self.assertIn("Method not found", str(ctx.exception))

    def test_non_json_response_translates(self) -> None:
        transport = FakeMcpTransport(status=200, raw_text="<html>not json</html>")
        client = McpClient(_mcp_server("files"), transport=transport)
        with self.assertRaises(McpClientError) as ctx:
            client.tools_list()
        self.assertIn("non-JSON", str(ctx.exception))

    def test_tool_error_flag_translates(self) -> None:
        transport = FakeMcpTransport(
            responses={"tools/call": {"isError": True, "content": [{"type": "text", "text": "disk full"}]}}
        )
        client = McpClient(_mcp_server("files"), transport=transport)
        with self.assertRaises(McpClientError) as ctx:
            client.tools_call("write_file", {})
        self.assertIn("disk full", str(ctx.exception))

    def test_auth_header_from_env(self) -> None:
        os.environ["AF_TEST_MCP_TOKEN"] = "sekret"
        try:
            transport = FakeMcpTransport(responses={"tools/list": {"tools": []}})
            client = McpClient(
                McpServerConfig(name="sec", url="http://x/mcp", auth_header_env="AF_TEST_MCP_TOKEN"),
                transport=transport,
            )
            client.tools_list()
            self.assertEqual(transport.calls[0]["headers"]["Authorization"], "Bearer sekret")
        finally:
            os.environ.pop("AF_TEST_MCP_TOKEN", None)

    def test_auth_env_missing_is_an_error(self) -> None:
        transport = FakeMcpTransport(responses={"tools/list": {"tools": []}})
        client = McpClient(
            McpServerConfig(name="sec", url="http://x/mcp", auth_header_env="AF_TEST_MCP_TOKEN_NOPE"),
            transport=transport,
        )
        with self.assertRaises(McpClientError) as ctx:
            client.tools_list()
        self.assertIn("auth header env", str(ctx.exception))

    def test_mcp_client_error_is_a_gateway_error(self) -> None:
        self.assertTrue(issubclass(McpClientError, GatewayError))


class McpClientConfigTests(unittest.TestCase):
    def test_parse_mcp_servers(self) -> None:
        from agentforge_gateway.config import parse_config

        config = parse_config(
            {
                "server": {
                    "mcp_servers": {
                        "notes": {"url": "http://127.0.0.1:3001/mcp", "timeout_seconds": 12},
                        "sec": {"url": "http://127.0.0.1:3002/mcp", "auth_header_env": "AF_MCP_TOKEN"},
                    }
                },
                "models": {"m": {"provider": "mock", "provider_model": "m1"}},
                "providers": {"mock": {"type": "mock"}},
            }
        )
        self.assertEqual(set(config.mcp_servers), {"notes", "sec"})
        self.assertEqual(config.mcp_servers["notes"].url, "http://127.0.0.1:3001/mcp")
        self.assertEqual(config.mcp_servers["notes"].timeout_seconds, 12.0)
        self.assertEqual(config.mcp_servers["sec"].auth_header_env, "AF_MCP_TOKEN")

    def test_no_mcp_servers_defaults_empty(self) -> None:
        from agentforge_gateway.config import parse_config

        config = parse_config(
            {
                "models": {"m": {"provider": "mock", "provider_model": "m1"}},
                "providers": {"mock": {"type": "mock"}},
            }
        )
        self.assertEqual(config.mcp_servers, {})

    def test_example_config_parses(self) -> None:
        from agentforge_gateway.config import load_config

        config = load_config(str(ROOT / "config.mcp-client.example.json"))
        self.assertEqual(set(config.mcp_servers), {"local-notes", "secured-tools"})


class GatewayAppMcpClientTests(unittest.TestCase):
    def setUp(self) -> None:
        self.transport = FakeMcpTransport(
            responses={
                "tools/list": {
                    "tools": [
                        {"name": "read_file", "description": "Read a file", "inputSchema": {"type": "object"}},
                        {"name": "write_file", "description": "Write a file"},
                    ]
                },
                "tools/call": {"content": [{"type": "text", "text": "file contents"}]},
            }
        )
        self.app = GatewayApp(
            _config_with_mcp({"files": _mcp_server("files")}),
            mcp_transport=self.transport,
        )

    def test_mcp_tools_are_namespaced(self) -> None:
        tools = self.app.mcp_tools()
        names = [t["name"] for t in tools]
        self.assertEqual(names, ["mcp_files.read_file", "mcp_files.write_file"])
        self.assertEqual(tools[0]["description"], "Read a file")

    def test_call_mcp_tool_dispatches(self) -> None:
        result = self.app.call_mcp_tool("mcp_files.read_file", {"path": "/x"})
        self.assertEqual(result, "file contents")
        call = self.transport.calls[-1]
        self.assertEqual(call["body"]["method"], "tools/call")
        self.assertEqual(call["body"]["params"]["name"], "read_file")

    def test_unknown_tool_raises(self) -> None:
        with self.assertRaises(McpClientError):
            self.app.call_mcp_tool("mcp_other.tool", {})
        with self.assertRaises(McpClientError):
            self.app.call_mcp_tool("not_a_tool", {})

    def test_no_servers_means_empty_tools(self) -> None:
        app = GatewayApp(DEFAULT_CONFIG, mcp_transport=self.transport)
        self.assertEqual(app.mcp_tools(), [])
        with self.assertRaises(McpClientError):
            app.call_mcp_tool("mcp_files.read_file", {})


if __name__ == "__main__":
    unittest.main()