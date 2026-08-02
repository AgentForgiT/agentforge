from __future__ import annotations

from dataclasses import dataclass, field
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

AICS_RECOMMENDED_FILES = (
    ".agentforge/vision.md",
    ".agentforge/roadmap.md",
    ".agentforge/glossary.md",
    ".agentforge/tech-stack.md",
    ".agentforge/milestones.md",
)

AICS_VERSION_MARKER = ".agentforge/aics-version"
AICS_SPEC_VERSION = "0.2"

REQUIRED_TEXT = {
    ".agentforge/agents/AGENTS.md": ("constitution", "charter", "ADR", "RFC"),
    ".agentforge/adrs/ADR_TEMPLATE.md": ("Context", "Decision", "Consequences"),
    ".agentforge/rfcs/RFC_TEMPLATE.md": ("Purpose", "Proposal", "Risks"),
}


@dataclass(frozen=True)
class ValidationResult:
    errors: tuple[str, ...]
    warnings: tuple[str, ...] = ()
    level: int = 1

    @property
    def ok(self) -> bool:
        return not self.errors


def _parse_front_matter(text: str) -> dict[str, str]:
    """Parse a leading YAML-like front matter block using string checks only.

    Returns an empty dict when the text has no front matter block.
    """
    if not text.startswith("---"):
        return {}
    lines = text.splitlines()
    if len(lines) < 3:
        return {}
    # find the closing delimiter within the first 20 lines
    close_idx = None
    for i in range(1, min(20, len(lines))):
        if lines[i].strip() == "---":
            close_idx = i
            break
    if close_idx is None:
        return {}
    fields: dict[str, str] = {}
    for line in lines[1:close_idx]:
        stripped = line.strip()
        if ":" in stripped:
            key, _, value = stripped.partition(":")
            fields[key.strip()] = value.strip().strip("'\"")
    return fields


def _has_front_matter(text: str) -> bool:
    return bool(_parse_front_matter(text))


def _has_plain_metadata(text: str) -> bool:
    return "Metadata:" in text


def _has_metadata(text: str) -> bool:
    return _has_front_matter(text) or _has_plain_metadata(text)


def validate_aics(root: Path) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    level = 1

    for relative in AICS_REQUIRED_DIRS:
        if not (root / relative).is_dir():
            errors.append(f"missing AICS directory: {relative}")

    for relative in AICS_REQUIRED_FILES:
        if not (root / relative).is_file():
            errors.append(f"missing AICS file: {relative}")

    for relative in AICS_RECOMMENDED_FILES:
        if not (root / relative).is_file():
            warnings.append(f"recommended file missing: {relative}")

    if errors:
        return ValidationResult(tuple(errors), tuple(warnings), level=1)

    # Level 2: metadata (either style) + templates + required text
    level = 2
    metadata_files_with_front_matter: list[str] = []
    for relative in AICS_METADATA_FILES:
        path = root / relative
        if not path.is_file():
            continue
        text = _read_text(path)
        if not _has_metadata(text):
            errors.append(f"missing Metadata block: {relative}")
        elif _has_front_matter(text):
            metadata_files_with_front_matter.append(relative)
        else:
            warnings.append(f"plain Metadata block (front matter preferred): {relative}")

    for relative, expected_values in REQUIRED_TEXT.items():
        path = root / relative
        if not path.is_file():
            continue
        text = _read_text(path)
        for expected in expected_values:
            if expected not in text:
                errors.append(f"missing required text '{expected}': {relative}")

    if errors:
        return ValidationResult(tuple(errors), tuple(warnings), level=2)

    # Level 3: front matter with aics-version in metadata files + version marker
    version_marker = root / AICS_VERSION_MARKER
    marker_ok = version_marker.is_file() and version_marker.read_text(encoding="utf-8").strip() == AICS_SPEC_VERSION
    if not marker_ok:
        warnings.append(f"missing or outdated version marker: {AICS_VERSION_MARKER} (expected '{AICS_SPEC_VERSION}')")

    if len(metadata_files_with_front_matter) == len(AICS_METADATA_FILES):
        all_front_matter_v02 = all(
            _parse_front_matter(_read_text(root / relative)).get("aics-version") == AICS_SPEC_VERSION
            for relative in AICS_METADATA_FILES
        )
        if marker_ok and all_front_matter_v02:
            level = 3
        else:
            if not all_front_matter_v02:
                warnings.append("some metadata files lack aics-version: 0.2 front matter")
    else:
        warnings.append("some metadata files lack front matter (Level 3 requires it)")

    return ValidationResult(tuple(errors), tuple(warnings), level=level)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")
