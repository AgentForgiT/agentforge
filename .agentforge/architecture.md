# AgentForge Architecture

Metadata:

- Status: Draft
- Phase: Genesis
- Last updated: 2026-06-28

## Purpose

This document describes the initial repository and ecosystem architecture.

## Repository Strategy

AgentForge starts with a modular monorepo named `agentforge`.

Initial organization repositories should be:

- `.github`: organization profile, templates, governance defaults, reusable workflows
- `agentforge`: canonical engineering monorepo
- `handbook`: long-form documentation and learning material
- `website`: public site and documentation portal

Subsystems such as gateway, providers, integrations, MCP, workflows, benchmarks, SDK, and CLI begin as modules inside `agentforge`.

## Monorepo Layout

- `apps/gateway`: AI gateway application
- `apps/cli`: future user-facing CLI
- `apps/playground`: future interactive playground
- `packages/providers`: provider adapters
- `packages/integrations`: IDE and agentic coding tool integrations
- `packages/mcp`: MCP tooling
- `packages/workflows`: reusable automation workflows
- `packages/benchmarks`: evaluation tools
- `packages/sdk`: client libraries and shared SDK code

Directories may be introduced as modules mature. Empty modules should not be added merely for appearance.

## Extraction Criteria

A module may become a standalone repository when one or more conditions hold:

- independent release cadence is required
- contributor ownership differs significantly
- CI/runtime costs become too large for the monorepo
- governance needs diverge
- downstream consumers need a smaller dedicated repository

Extraction requires an ADR.

## Revision History

- 2026-06-28: Initial draft.
