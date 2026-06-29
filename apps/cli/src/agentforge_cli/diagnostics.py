from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .validation import load_aics_validation


@dataclass(frozen=True)
class DoctorReport:
    root: Path
    healthy: bool
    lines: tuple[str, ...]
    errors: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return not self.errors


def diagnose_context(project_path: Path) -> DoctorReport:
    root = project_path.resolve()
    if not root.exists():
        return DoctorReport(
            root=root,
            healthy=False,
            lines=(),
            errors=(f"project path does not exist: {project_path}",),
        )
    if not root.is_dir():
        return DoctorReport(
            root=root,
            healthy=False,
            lines=(),
            errors=(f"project path is not a directory: {project_path}",),
        )

    try:
        validation_module = load_aics_validation(root)
        validation_result = validation_module.validate_aics(root)
    except RuntimeError as exc:
        return DoctorReport(root=root, healthy=False, lines=(), errors=(str(exc),))

    healthy = validation_result.ok
    lines: list[str] = [
        "AgentForge doctor",
        f"Project root: {root}",
        f"Overall status: {'healthy' if healthy else 'unhealthy'}",
        f"AICS validation: {'passed' if validation_result.ok else 'failed'}",
        f"Context root: {_describe_context_root(root)}",
        "Local checks:",
        f"- required directories: {_summarize_required_dirs(root, validation_module.AICS_REQUIRED_DIRS)}",
        f"- required files: {_summarize_required_files(root, validation_module.AICS_REQUIRED_FILES)}",
        f"- metadata blocks: {_summarize_metadata(root, validation_module.AICS_METADATA_FILES)}",
        f"- required template text: {_summarize_required_text(root, validation_module.REQUIRED_TEXT)}",
        "Validation signals:",
    ]

    if validation_result.ok:
        lines.append("- context is healthy for AICS v0.1 validation")
        lines.append("Next action: continue with agentforge explain-context or implementation work.")
    else:
        lines.extend(f"- {error}" for error in validation_result.errors)
        lines.append("Next action: fix the validation signals, or run agentforge init-context on a new project.")

    return DoctorReport(root=root, healthy=healthy, lines=tuple(lines))


def _describe_context_root(root: Path) -> str:
    path = root / ".agentforge"
    if path.is_dir():
        return ".agentforge (present)"
    if path.exists():
        return ".agentforge (not a directory)"
    return ".agentforge (missing)"


def _summarize_required_dirs(root: Path, required_dirs: tuple[str, ...]) -> str:
    missing = tuple(relative for relative in required_dirs if not (root / relative).is_dir())
    return _summarize_missing(missing)


def _summarize_required_files(root: Path, required_files: tuple[str, ...]) -> str:
    missing = tuple(relative for relative in required_files if not (root / relative).is_file())
    return _summarize_missing(missing)


def _summarize_metadata(root: Path, metadata_files: tuple[str, ...]) -> str:
    missing = []
    for relative in metadata_files:
        path = root / relative
        if path.is_file() and "Metadata:" not in path.read_text(encoding="utf-8"):
            missing.append(relative)
    return _summarize_missing(tuple(missing))


def _summarize_required_text(root: Path, required_text: dict[str, tuple[str, ...]]) -> str:
    missing = []
    for relative, expected_values in required_text.items():
        path = root / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for expected in expected_values:
            if expected not in text:
                missing.append(f"{relative} missing '{expected}'")
    return _summarize_missing(tuple(missing))


def _summarize_missing(missing: tuple[str, ...]) -> str:
    if not missing:
        return "passed"
    return f"failed ({len(missing)} missing)"
