from __future__ import annotations

from pathlib import Path
import sys

from aics_validation import validate_aics


REQUIRED_FILES = (
    "README.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "ROADMAP.md",
    "CHANGELOG.md",
    ".agentforge/constitution.md",
    ".agentforge/charter.md",
    ".agentforge/decisions.md",
    ".agentforge/architecture.md",
    ".agentforge/repo-map.md",
    ".agentforge/adrs/0001-modular-monorepo.md",
    ".agentforge/adrs/0002-gateway-module-placement.md",
    ".agentforge/decisions/0002-prototype-repository-disposition.md",
    ".agentforge/decisions/0003-cli-path-for-aics-validation.md",
    ".agentforge/requirements/gateway-reconciliation.md",
    ".agentforge/requirements/canonical-cli-mvp.md",
    ".agentforge/specs/aics-v0.1.md",
    ".agentforge/specs/aics-validation-v0.1.md",
    ".agentforge/rfcs/RFC_TEMPLATE.md",
    ".agentforge/adrs/ADR_TEMPLATE.md",
    ".agentforge/agents/AGENTS.md",
    ".agentforge/agents/CODEX.md",
    "apps/cli/README.md",
    "apps/cli/pyproject.toml",
    "apps/cli/bin/agentforge.py",
    "apps/cli/src/agentforge_cli/cli.py",
    "apps/cli/tests/test_cli.py",
    "apps/gateway/README.md",
    "apps/gateway/config.example.json",
    "apps/gateway/src/agentforge_gateway/app.py",
    "apps/gateway/tests/test_app.py",
    "docs/gateway.md",
    "docs/aics.md",
    "examples/gateway/openai-compatible-curl.md",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/workflows/bootstrap-validate.yml",
)


REQUIRED_DIRS = (
    ".agentforge",
    ".agentforge/adrs",
    ".agentforge/rfcs",
    ".agentforge/requirements",
    ".agentforge/specs",
    ".agentforge/agents",
    ".agentforge/standards",
    "apps",
    "apps/cli",
    "apps/cli/tests",
    "apps/gateway",
    "packages",
    "docs",
    "examples",
    "examples/gateway",
    "scripts",
    "tests",
    "tools",
)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors: list[str] = []

    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            errors.append(f"missing file: {relative}")

    for relative in REQUIRED_DIRS:
        if not (root / relative).is_dir():
            errors.append(f"missing directory: {relative}")

    errors.extend(validate_aics(root).errors)

    if errors:
        for error in errors:
            print(error)
        return 1

    print("bootstrap ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
