from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .validation import load_aics_validation

AICS_SPEC_VERSION = "0.2"
VERSION_MARKER = ".agentforge/aics-version"

METADATA_FILES = (
    ".agentforge/constitution.md",
    ".agentforge/charter.md",
    ".agentforge/decisions.md",
    ".agentforge/architecture.md",
    ".agentforge/repo-map.md",
    ".agentforge/agents/AGENTS.md",
)

FIELD_MAP = {
    "Status": "status",
    "Phase": "phase",
    "Applies to": "applies-to",
    "Last updated": "last-updated",
    "Version": "version",
}


@dataclass(frozen=True)
class MigrateContextResult:
    root: Path
    migrated: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return not self.errors


def migrate_context(project_path: Path) -> MigrateContextResult:
    """Migrate an AICS v0.1 context to v0.2, additively.

    - Converts plain `Metadata:` blocks in metadata-checked files into
      YAML front matter (with `aics-version: 0.2`).
    - Adds the `.agentforge/aics-version` marker when absent.
    - Never deletes or rewrites content outside the metadata block.
    """
    root = project_path.resolve()
    if not root.is_dir():
        return MigrateContextResult(root=root, errors=(f"project path is not a directory: {project_path}",))

    migrated: list[str] = []
    errors: list[str] = []

    for relative in METADATA_FILES:
        path = root / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if _has_front_matter(text):
            continue  # already v0.2 style
        if "Metadata:" not in text:
            continue  # nothing to migrate; validation will report it
        try:
            converted = _metadata_to_front_matter(text)
        except ValueError as exc:
            errors.append(f"{relative}: {exc}")
            continue
        path.write_text(converted, encoding="utf-8")
        migrated.append(relative)

    marker = root / VERSION_MARKER
    if not marker.is_file():
        try:
            marker.write_text(AICS_SPEC_VERSION + "\n", encoding="utf-8")
            migrated.append(VERSION_MARKER)
        except OSError as exc:
            errors.append(f"could not write {VERSION_MARKER}: {exc}")

    return MigrateContextResult(root=root, migrated=tuple(migrated), errors=tuple(errors))


def _has_front_matter(text: str) -> bool:
    return text.startswith("---")


def _metadata_to_front_matter(text: str) -> str:
    """Convert a leading plain Metadata: block into YAML front matter.

    The Metadata block must appear before the first `##` section heading.
    Returns the full document with front matter prepended and the plain
    block removed. Raises ValueError if the block cannot be parsed.
    """
    lines = text.splitlines(keepends=True)

    meta_idx = None
    for i, line in enumerate(lines):
        if line.strip() == "Metadata:":
            meta_idx = i
            break
    if meta_idx is None:
        raise ValueError("no Metadata: block found")

    # only migrate blocks that appear before the first section heading
    first_heading = None
    for i, line in enumerate(lines):
        if line.lstrip().startswith("## "):
            first_heading = i
            break
    if first_heading is not None and meta_idx > first_heading:
        raise ValueError("Metadata block is not at the top of the document")

    fields: list[tuple[str, str]] = []
    j = meta_idx + 1
    while j < len(lines):
        stripped = lines[j].strip()
        if stripped.startswith("- "):
            raw = stripped[2:].strip()
            key, _, value = raw.partition(":")
            if not value.strip():
                raise ValueError(f"Metadata field '{key}' has no value")
            fields.append((key.strip(), value.strip()))
            j += 1
        elif stripped == "":
            k = j
            while k < len(lines) and lines[k].strip() == "":
                k += 1
            if k < len(lines) and lines[k].strip().startswith("- "):
                j = k
                continue
            break
        else:
            break

    if not fields:
        raise ValueError("Metadata block has no fields")

    end = j
    if end < len(lines) and lines[end].strip() == "":
        end += 1

    head = lines[:meta_idx]
    body = lines[end:]
    while head and head[-1].strip() == "":
        head.pop()

    front = ["---\n"]
    for key, value in fields:
        mapped = FIELD_MAP.get(key, key.lower().replace(" ", "-"))
        front.append(f"{mapped}: {value}\n")
    front.append("aics-version: 0.2\n")
    front.append("---\n")

    return "".join(front + head + ["\n"] + body)
