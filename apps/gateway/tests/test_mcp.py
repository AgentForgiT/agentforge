from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentforge_gateway.app import GatewayApp
from agentforge_gateway.config import DEFAULT_CONFIG
from agentforge_gateway.mcp import TOOL_DEFINITIONS, PROTOCOL_VERSION, McpServer


def mcp_server() -> McpServer:
    return GatewayApp(DEFAULT_CONFIG).mcp


def rpc(method: str, params: dict[str, object] | None = None, request_id: int = 1) -> dict[str, object]:
    request: dict[str, object] = {"jsonrpc": "2.0", "id": request_id, "method": method}
    if params is not None:
        request["params"] = params
    return mcp_server().handle(json.dumps(request))


class McpInitializeTests(unittest.TestCase):
    def test_initialize_handshake(self) -> None:
        response = rpc("initialize", {"protocolVersion": "2026-07-28", "capabilities": {}, "clientInfo": {}})
        self.assertEqual(response["jsonrpc"], "2.0")
        result = response["result"]
        self.assertEqual(result["protocolVersion"], PROTOCOL_VERSION)
        self.assertEqual(result["serverInfo"]["name"], "agentforge-gateway")
        self.assertIn("tools", result["capabilities"])
        self.assertIn("resources", result["capabilities"])
        self.assertIn("prompts", result["capabilities"])

    def test_resources_and_prompts_expose_content(self) -> None:
        resources = rpc("resources/list")
        uris = [r["uri"] for r in resources["result"]["resources"]]
        self.assertEqual(uris, ["models://registry", "models://config"])
        prompts = rpc("prompts/list")
        names = [p["name"] for p in prompts["result"]["prompts"]]
        self.assertEqual(names, ["request-builder", "config-review", "error-diagnosis"])


class McpResourcesTests(unittest.TestCase):
    def test_read_registry(self) -> None:
        response = rpc("resources/read", {"uri": "models://registry"})
        contents = response["result"]["contents"]
        self.assertEqual(contents[0]["uri"], "models://registry")
        self.assertEqual(contents[0]["mimeType"], "application/json")
        self.assertIn("mock-coder", contents[0]["text"])

    def test_read_config_redacts_secrets(self) -> None:
        response = rpc("resources/read", {"uri": "models://config"})
        text = response["result"]["contents"][0]["text"]
        self.assertNotIn("sk-", text)
        self.assertNotIn("af-k-", text)
        self.assertNotIn("redacted", text)  # marker must not leak a value

    def test_read_unknown_uri_errors(self) -> None:
        response = rpc("resources/read", {"uri": "models://nope"})
        self.assertEqual(response["error"]["code"], -32602)


class McpPromptsTests(unittest.TestCase):
    def test_request_builder_prompt(self) -> None:
        response = rpc(
            "prompts/get",
            {"name": "request-builder", "arguments": {"model": "mock-coder", "user": "Hello"}},
        )
        result = response["result"]
        self.assertEqual(result["description"], "Build an OpenAI-compatible chat-completions request body.")
        body = result["messages"][0]["content"]["text"]
        self.assertIn('"model": "mock-coder"', body)
        self.assertIn('"content": "Hello"', body)

    def test_request_builder_with_system(self) -> None:
        response = rpc(
            "prompts/get",
            {"name": "request-builder", "arguments": {"model": "m", "system": "Be terse.", "user": "Hi"}},
        )
        body = response["result"]["messages"][0]["content"]["text"]
        self.assertIn('"role": "system"', body)

    def test_config_review_prompt_includes_config(self) -> None:
        response = rpc(
            "prompts/get",
            {"name": "config-review", "arguments": {"config": '{"server": {"port": 8080}}'}},
        )
        text = response["result"]["messages"][0]["content"]["text"]
        self.assertIn("keyless local trust", text)
        self.assertIn('{"server": {"port": 8080}}', text)

    def test_error_diagnosis_prompt(self) -> None:
        response = rpc(
            "prompts/get",
            {"name": "error-diagnosis", "arguments": {"error": '{"error": {"type": "bad_request"}}'}},
        )
        text = response["result"]["messages"][0]["content"]["text"]
        self.assertIn("error envelope", text)

    def test_prompt_missing_required_arg_errors(self) -> None:
        response = rpc("prompts/get", {"name": "request-builder", "arguments": {"model": "m"}})
        self.assertEqual(response["error"]["code"], -32602)
        self.assertIn("user", response["error"]["message"])

    def test_prompt_unknown_name_errors(self) -> None:
        response = rpc("prompts/get", {"name": "nope", "arguments": {}})
        self.assertEqual(response["error"]["code"], -32602)
        self.assertIn("unknown prompt", response["error"]["message"])


class McpToolsListTests(unittest.TestCase):
    def test_lists_four_tools_with_schemas(self) -> None:
        response = rpc("tools/list")
        tools = response["result"]["tools"]
        names = [tool["name"] for tool in tools]
        self.assertEqual(
            names,
            ["gateway_health", "gateway_list_models", "gateway_chat_completion", "gateway_anthropic_message"],
        )
        for tool in tools:
            self.assertIn("description", tool)
            self.assertIn("inputSchema", tool)
            self.assertEqual(tool["inputSchema"]["type"], "object")

    def test_tool_definitions_consistent(self) -> None:
        self.assertEqual(len(TOOL_DEFINITIONS), 4)
        required = TOOL_DEFINITIONS[2]["inputSchema"]["required"]
        self.assertEqual(required, ["model", "messages"])


class McpToolsCallTests(unittest.TestCase):
    def test_gateway_health_tool(self) -> None:
        response = rpc("tools/call", {"name": "gateway_health", "arguments": {}})
        result = response["result"]
        self.assertEqual(result["isError"], False)
        self.assertEqual(result["content"][0]["type"], "text")
        self.assertIn("ok", result["content"][0]["text"])

    def test_gateway_list_models_tool(self) -> None:
        response = rpc("tools/call", {"name": "gateway_list_models", "arguments": {}})
        result = response["result"]
        self.assertIn("mock-coder", result["content"][0]["text"])

    def test_gateway_chat_completion_tool(self) -> None:
        response = rpc(
            "tools/call",
            {
                "name": "gateway_chat_completion",
                "arguments": {"model": "mock-coder", "messages": [{"role": "user", "content": "Hello"}]},
            },
        )
        result = response["result"]
        self.assertEqual(result["isError"], False)
        self.assertIn("Mock response from mock-coder", result["content"][0]["text"])

    def test_gateway_anthropic_message_tool(self) -> None:
        response = rpc(
            "tools/call",
            {
                "name": "gateway_anthropic_message",
                "arguments": {"model": "mock-coder", "messages": [{"role": "user", "content": "Hi"}]},
            },
        )
        result = response["result"]
        self.assertEqual(result["isError"], False)
        self.assertIn("Mock response from mock-coder", result["content"][0]["text"])

    def test_unknown_tool_returns_jsonrpc_error(self) -> None:
        response = rpc("tools/call", {"name": "nope", "arguments": {}})
        self.assertEqual(response["error"]["code"], -32602)
        self.assertIn("unknown tool", response["error"]["message"])

    def test_missing_arguments_returns_jsonrpc_error(self) -> None:
        response = rpc("tools/call", {"name": "gateway_chat_completion"})
        self.assertEqual(response["error"]["code"], -32602)

    def test_unknown_model_returns_is_error_result(self) -> None:
        response = rpc(
            "tools/call",
            {
                "name": "gateway_chat_completion",
                "arguments": {"model": "no-such-model", "messages": [{"role": "user", "content": "Hi"}]},
            },
        )
        result = response["result"]
        self.assertEqual(result["isError"], True)
        self.assertIn("gateway error", result["content"][0]["text"])


class McpProtocolErrorTests(unittest.TestCase):
    def test_malformed_json_returns_parse_error(self) -> None:
        response = mcp_server().handle("{not json")
        self.assertEqual(response["error"]["code"], -32700)

    def test_non_jsonrpc_request_rejected(self) -> None:
        response = mcp_server().handle(json.dumps({"id": 1, "method": "initialize"}))
        self.assertEqual(response["error"]["code"], -32600)

    def test_unknown_method_returns_method_not_found(self) -> None:
        response = rpc("do-something")
        self.assertEqual(response["error"]["code"], -32601)

    def test_request_id_preserved(self) -> None:
        response = rpc("tools/list", request_id=42)
        self.assertEqual(response["id"], 42)


if __name__ == "__main__":
    unittest.main()
