# Security Policy

AgentForge treats security as a design constraint.

## Reporting

Do not open public issues for suspected vulnerabilities. Use private disclosure channels once the project publishes a dedicated security contact.

## Principles

- never commit provider API keys or gateway secrets
- redact authorization headers in logs
- avoid prompt and completion logging by default
- document trust boundaries
- prefer explicit configuration over hidden behavior

## Revision History

- 2026-06-28: Initial draft.
