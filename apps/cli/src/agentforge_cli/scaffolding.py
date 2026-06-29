from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from importlib.resources import files
from pathlib import Path, PurePosixPath


SCAFFOLD_DIRECTORIES = (
    ".agentforge",
    ".agentforge/adrs",
    ".agentforge/agents",
    ".agentforge/rfcs",
    ".agentforge/standards",
)

SCAFFOLD_FILES = (
    ".agentforge/constitution.md",
    ".agentforge/charter.md",
    ".agentforge/decisions.md",
    ".agentforge/architecture.md",
    ".agentforge/repo-map.md",
    ".agentforge/agents/AGENTS.md",
    ".agentforge/adrs/ADR_TEMPLATE.md",
    ".agentforge/rfcs/RFC_TEMPLATE.md",
    ".agentforge/standards/.gitkeep",
)


@dataclass(frozen=True)
class InitContextResult:
    root: Path
    errors: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return not self.errors


def init_context(project_path: Path) -> InitContextResult:
    root = project_path.resolve()
    if root.exists() and not root.is_dir():
        return InitContextResult(
            root=root,
            errors=(f"project path is not a directory: {project_path}",),
        )

    errors = tuple(_collect_conflicts(root))
    if errors:
        return InitContextResult(root=root, errors=errors)

    try:
        root.mkdir(parents=True, exist_ok=True)
        for relative in SCAFFOLD_DIRECTORIES:
            (root / relative).mkdir(parents=True, exist_ok=True)

        substitutions = {
            "{{PROJECT_NAME}}": root.name or "project",
            "{{DATE}}": date.today().isoformat(),
        }
        for relative in SCAFFOLD_FILES:
            destination = root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(
                _render_template(_read_template(relative), substitutions),
                encoding="utf-8",
            )
    except OSError as exc:
        return InitContextResult(
            root=root,
            errors=(f"could not initialize context at {root}: {exc}",),
        )

    return InitContextResult(root=root)


def _collect_conflicts(root: Path) -> list[str]:
    errors: list[str] = []

    for relative in SCAFFOLD_DIRECTORIES:
        path = root / relative
        if path.exists() and not path.is_dir():
            errors.append(f"scaffold conflict: {relative} exists and is not a directory")

    for relative in SCAFFOLD_FILES:
        path = root / relative
        if path.exists():
            errors.append(f"scaffold conflict: {relative} already exists")

    return errors


def _read_template(relative_path: str) -> str:
    template_root = files("agentforge_cli").joinpath("templates", "context-v0.1")
    template_path = template_root
    for part in PurePosixPath(relative_path).parts:
        template_path = template_path.joinpath(part)
    return template_path.read_text(encoding="utf-8")


def _render_template(template: str, substitutions: dict[str, str]) -> str:
    rendered = template
    for placeholder, value in substitutions.items():
        rendered = rendered.replace(placeholder, value)
    return rendered
