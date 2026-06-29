from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .validation import validate_context


GOVERNANCE_ENTRYPOINTS = (
    ".agentforge/constitution.md",
    ".agentforge/charter.md",
    ".agentforge/decisions.md",
    ".agentforge/architecture.md",
    ".agentforge/repo-map.md",
    ".agentforge/agents/AGENTS.md",
)


@dataclass(frozen=True)
class ContextExplanation:
    root: Path
    lines: tuple[str, ...]
    errors: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return not self.errors


def explain_context(project_path: Path) -> ContextExplanation:
    root = project_path.resolve()
    if not root.exists():
        return ContextExplanation(
            root=root,
            lines=(),
            errors=(f"project path does not exist: {project_path}",),
        )
    if not root.is_dir():
        return ContextExplanation(
            root=root,
            lines=(),
            errors=(f"project path is not a directory: {project_path}",),
        )

    try:
        validation_result = validate_context(root)
    except RuntimeError as exc:
        return ContextExplanation(root=root, lines=(), errors=(str(exc),))

    lines: list[str] = [
        "AgentForge context explanation",
        f"Project root: {root}",
        f"AICS validation: {'passed' if validation_result.ok else 'failed'}",
        f"Context root: {_describe_path(root, '.agentforge')}",
        "Read next:",
    ]

    for relative in GOVERNANCE_ENTRYPOINTS:
        lines.append(f"- {relative} ({_status(root, relative)})")

    if validation_result.ok:
        lines.extend(
            [
                "Validation signals:",
                "- context is complete for AICS v0.1 validation",
            ]
        )
    else:
        lines.append("Validation signals:")
        lines.extend(f"- {error}" for error in validation_result.errors)

    return ContextExplanation(root=root, lines=tuple(lines))


def _describe_path(root: Path, relative: str) -> str:
    path = root / relative
    if path.is_dir():
        return f"{relative} (present)"
    if path.exists():
        return f"{relative} (not a directory)"
    return f"{relative} (missing)"


def _status(root: Path, relative: str) -> str:
    path = root / relative
    if path.is_file():
        return "present"
    if path.exists():
        return "not a file"
    return "missing"
