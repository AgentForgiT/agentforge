from __future__ import annotations

import sys
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from aics_validation import (
    AICS_METADATA_FILES,
    AICS_SPEC_VERSION,
    validate_aics,
    _parse_front_matter,
    _has_front_matter,
    _has_plain_metadata,
)


FRONT_MATTER = """---
status: active
aics-version: 0.2
---

# Title

Body text.
"""

PLAIN_METADATA = """# Title

Metadata:

- Status: Active
- Phase: Genesis

## Purpose

Body.
"""

NO_METADATA = """# Title

No metadata here.
"""

AGENTS_MD = """---
status: active
aics-version: 0.2
---

# AGENTS Operating Manual

This manual references the constitution, the charter, the ADR
register, and the RFC process.
"""


def build_context(files: dict[str, str]) -> Path:
    tmp = tempfile.mkdtemp()
    root = Path(tmp)
    # required empty dirs
    for rel in (".agentforge", ".agentforge/adrs", ".agentforge/agents", ".agentforge/rfcs", ".agentforge/standards"):
        (root / rel).mkdir(parents=True, exist_ok=True)
    for rel, content in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return root


def full_v02_context() -> dict[str, str]:
    files: dict[str, str] = {}
    for rel in AICS_METADATA_FILES:
        files[rel] = AGENTS_MD if rel.endswith("AGENTS.md") else FRONT_MATTER
    files[".agentforge/adrs/ADR_TEMPLATE.md"] = "# ADR Template\n\nContext\nDecision\nConsequences\n"
    files[".agentforge/rfcs/RFC_TEMPLATE.md"] = "# RFC Template\n\nPurpose\nProposal\nRisks\n"
    files[".agentforge/aics-version"] = "0.2\n"
    return files


class FrontMatterParsingTests(unittest.TestCase):
    def test_parses_front_matter_fields(self) -> None:
        fields = _parse_front_matter(FRONT_MATTER)
        self.assertEqual(fields.get("status"), "active")
        self.assertEqual(fields.get("aics-version"), "0.2")

    def test_plain_metadata_has_no_front_matter(self) -> None:
        self.assertFalse(_has_front_matter(PLAIN_METADATA))
        self.assertTrue(_has_plain_metadata(PLAIN_METADATA))

    def test_front_matter_detected(self) -> None:
        self.assertTrue(_has_front_matter(FRONT_MATTER))

    def test_no_metadata_detected(self) -> None:
        self.assertFalse(_has_front_matter(NO_METADATA))
        self.assertFalse(_has_plain_metadata(NO_METADATA))


class AicsV02ValidationTests(unittest.TestCase):
    def test_v02_context_reaches_level_3(self) -> None:
        root = build_context(full_v02_context())
        result = validate_aics(root)
        self.assertTrue(result.ok, result.errors)
        self.assertEqual(result.level, 3)

    def test_v01_plain_metadata_context_reaches_level_2(self) -> None:
        files = full_v02_context()
        for rel in AICS_METADATA_FILES:
            if rel.endswith("AGENTS.md"):
                files[rel] = PLAIN_METADATA + "\nThis manual references the constitution, the charter, the ADR register, and the RFC process.\n"
            else:
                files[rel] = PLAIN_METADATA
        files.pop(".agentforge/aics-version")
        root = build_context(files)
        result = validate_aics(root)
        self.assertTrue(result.ok, result.errors)
        self.assertEqual(result.level, 2)
        self.assertTrue(any("front matter preferred" in w for w in result.warnings))

    def test_missing_version_marker_caps_at_level_2(self) -> None:
        files = full_v02_context()
        files.pop(".agentforge/aics-version")
        root = build_context(files)
        result = validate_aics(root)
        self.assertTrue(result.ok, result.errors)
        self.assertEqual(result.level, 2)
        self.assertTrue(any("version marker" in w for w in result.warnings))

    def test_plain_metadata_at_level3_target_warns(self) -> None:
        files = full_v02_context()
        files[AICS_METADATA_FILES[0]] = PLAIN_METADATA
        root = build_context(files)
        result = validate_aics(root)
        self.assertTrue(result.ok, result.errors)
        self.assertEqual(result.level, 2)
        self.assertTrue(any("lack front matter" in w for w in result.warnings))

    def test_missing_required_file_is_level_1(self) -> None:
        files = full_v02_context()
        files.pop(".agentforge/constitution.md")
        root = build_context(files)
        result = validate_aics(root)
        self.assertFalse(result.ok)
        self.assertEqual(result.level, 1)

    def test_wrong_aics_version_in_marker_warns(self) -> None:
        files = full_v02_context()
        files[".agentforge/aics-version"] = "0.1\n"
        root = build_context(files)
        result = validate_aics(root)
        self.assertTrue(result.ok, result.errors)
        self.assertEqual(result.level, 2)
        self.assertTrue(any("version marker" in w for w in result.warnings))

    def test_agentforge_repo_is_level_3(self) -> None:
        result = validate_aics(ROOT)
        self.assertTrue(result.ok, result.errors)
        self.assertEqual(result.level, 3)
        self.assertEqual(AICS_SPEC_VERSION, "0.2")


if __name__ == "__main__":
    unittest.main()
