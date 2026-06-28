from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


AICS_REQUIRED_DIRS = (
    ".agentforge",
    ".agentforge/adrs",
    ".agentforge/agents",
    ".agentforge/rfcs",
    ".agentforge/standards",
)

AICS_REQUIRED_FILES = (
    ".agentforge/constitution.md",
    ".agentforge/charter.md",
    ".agentforge/decisions.md",
    ".agentforge/architecture.md",
    ".agentforge/repo-map.md",
    ".agentforge/agents/AGENTS.md",
    ".agentforge/adrs/ADR_TEMPLATE.md",
    ".agentforge/rfcs/RFC_TEMPLATE.md",
)

AICS_METADATA_FILES = (
    ".agentforge/constitution.md",
    ".agentforge/charter.md",
    ".agentforge/decisions.md",
    ".agentforge/architecture.md",
    ".agentforge/repo-map.md",
    ".agentforge/agents/AGENTS.md",
)

REQUIRED_TEXT = {
    ".agentforge/agents/AGENTS.md": ("constitution", "charter", "ADR", "RFC"),
    ".agentforge/adrs/ADR_TEMPLATE.md": ("Context", "Decision", "Consequences"),
    ".agentforge/rfcs/RFC_TEMPLATE.md": ("Purpose", "Proposal", "Risks"),
}


@dataclass(frozen=True)
class ValidationResult:
    errors: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.errors


def validate_aics(root: Path) -> ValidationResult:
    errors: list[str] = []

    for relative in AICS_REQUIRED_DIRS:
        if not (root / relative).is_dir():
            errors.append(f"missing AICS directory: {relative}")

    for relative in AICS_REQUIRED_FILES:
        if not (root / relative).is_file():
            errors.append(f"missing AICS file: {relative}")

    for relative in AICS_METADATA_FILES:
        path = root / relative
        if path.is_file() and "Metadata:" not in _read_text(path):
            errors.append(f"missing Metadata block: {relative}")

    for relative, expected_values in REQUIRED_TEXT.items():
        path = root / relative
        if not path.is_file():
            continue
        text = _read_text(path)
        for expected in expected_values:
            if expected not in text:
                errors.append(f"missing required text '{expected}': {relative}")

    return ValidationResult(tuple(errors))


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")
