# AgentForge SDK

Dependency-free Python client for the AgentForge gateway (ADR-0025).

```python
from agentforge_sdk import AgentForgeClient

client = AgentForgeClient("http://127.0.0.1:8080", api_key="optional")

client.health()  # {"status": "ok", ...}
client.models()  # {"data": [...]}

# OpenAI surface
client.chat_completions("mock-coder", [{"role": "user", "content": "Hi"}])

# streaming
for chunk in client.chat_completions("mock-coder", [{"role": "user", "content": "Hi"}], stream=True):
    print(chunk)

# Anthropic Messages surface
client.anthropic_messages("mock-coder", [{"role": "user", "content": "Hi"}])
```

Stdlib only (`urllib.request` + `json`). Errors surface as `AgentForgeError(status, body)`.
