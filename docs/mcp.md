# MCP: Registering the AgentForge Gateway

The gateway exposes an MCP server surface at `POST /mcp` (ADR-0026). Any MCP client can register it as a server and drive the gateway's providers as tools.

## Claude Code

### One command (user scope)

```bash
claude mcp add agentforge --transport http --url http://127.0.0.1:8080/mcp
```

### Project scope (`.mcp.json`)

```json
{
  "mcpServers": {
    "agentforge": {
      "type": "http",
      "url": "http://127.0.0.1:8080/mcp"
    }
  }
}
```

### With gateway auth enabled

When the gateway runs with `server.api_key_env` set (ADR-0023), pass the key via the client's environment:

```json
{
  "mcpServers": {
    "agentforge": {
      "type": "http",
      "url": "http://127.0.0.1:8080/mcp",
      "env": {
        "AGENTFORGE_API_KEY": "your-key"
      }
    }
  }
}
```

## Tools exposed

| Tool | Purpose |
| --- | --- |
| `gateway_health` | Gateway status |
| `gateway_list_models` | Registered model aliases |
| `gateway_chat_completion` | Chat completion (OpenAI surface) |
| `gateway_anthropic_message` | Messages call (Anthropic surface) |

Every tool routes through the same governance: provider adapters, model aliases, error envelopes, auth, and rate limiting apply exactly as on the HTTP surfaces.

## Verify

```bash
curl http://127.0.0.1:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```
