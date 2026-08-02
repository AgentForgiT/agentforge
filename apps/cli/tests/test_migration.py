from __future__ import annotations

import io
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "apps" / "cli" / "src"))

from agentforge_cli.migration import migrate_context, _metadata_to_front_matter
from agentforge_cli.scaffolding import TEMPLATE_VERSION, init_context
from agentforge_cli.validation import validate_context

V01_CONSTITUTION = """# Test Constitution

Metadata:

- Status: Draft
- Applies to: test project
- Last updated: 2026-08-01

## Purpose

Body content that must survive migration.
"""


class TemplateVersionTests(unittest.TestCase):
    def test_scaffold_uses_v02_templates(self) -> None:
        self.assertEqual(TEMPLATE_VERSION, "context-v0.2")

    def test_scaffold_validates_at_level_3(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "fresh-project"
            result = init_context(project)
            self.assertTrue(result.ok, result.errors)
            validation = validate_context(project)
            self.assertTrue(validation.ok, validation.errors)
            self.assertEqual(validation.level, 3)

    def test_scaffold_writes_version_marker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "marked"
            init_context(project)
            marker = project / ".agentforge" / "aics-version"
            self.assertTrue(marker.is_file())
            self.assertEqual(marker.read_text(encoding="utf-8").strip(), "0.2")


class FrontMatterConversionTests(unittest.TestCase):
    def test_converts_metadata_block_to_front_matter(self) -> None:
        converted = _metadata_to_front_matter(V01_CONSTITUTION)
        self.assertTrue(converted.startswith("---\n"))
        self.assertIn("status: Draft", converted)
        self.assertIn("applies-to: test project", converted)
        self.assertIn("last-updated: 2026-08-01", converted)
        self.assertIn("aics-version: 0.2", converted)
        self.assertNotIn("Metadata:", converted)
        # body preserved
        self.assertIn("Body content that must survive migration.", converted)
        self.assertIn("# Test Constitution", converted)

    def test_metadata_below_heading_rejected(self) -> None:
        bad = "# Title\n\n## Section\n\nMetadata:\n\n- Status: Draft\n"
        with self.assertRaises(ValueError):
            _metadata_to_front_matter(bad)


class MigrateContextTests(unittest.TestCase):
    def _build_v01_context(self, root: Path) -> None:
        dirs = (".agentforge", ".agentforge/adrs", ".agentforge/agents", ".agentforge/rfcs", ".agentforge/standards")
        for rel in dirs:
            (root / rel).mkdir(parents=True, exist_ok=True)
        files = {
            ".agentforge/constitution.md": V01_CONSTITUTION,
            ".agentforge/charter.md": V01_CONSTITUTION.replace("Constitution", "Charter"),
            ".agentforge/decisions.md": V01_CONSTITUTION.replace("Constitution", "Decisions"),
            ".agentforge/architecture.md": V01_CONSTITUTION.replace("Constitution", "Architecture"),
            ".agentforge/repo-map.md": V01_CONSTITUTION.replace("Constitution", "Repo Map"),
            ".agentforge/agents/AGENTS.md": V01_CONSTITUTION + "\nThe AGENTS manual references the constitution, charter, ADR, RFC.\n",
            ".agentforge/adrs/ADR_TEMPLATE.md": "# ADR\n\nContext\nDecision\nConsequences\n",
            ".agentforge/rfcs/RFC_TEMPLATE.md": "# RFC\n\nPurpose\nProposal\nRisks\n",
        }
        for rel, content in files.items():
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

    def test_migrates_v01_to_v02(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "v01"
            self._build_v01_context(project)

            result = migrate_context(project)
            self.assertTrue(result.ok, result.errors)
            self.assertIn(".agentforge/constitution.md", result.migrated)
            self.assertIn(".agentforge/aics-version", result.migrated)

            validation = validate_context(project)
            self.assertTrue(validation.ok, validation.errors)
            self.assertEqual(validation.level, 3)

    def test_migration_preserves_body_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "v01"
            self._build_v01_context(project)
            migrate_context(project)
            migrated = (project / ".agentforge" / "constitution.md").read_text(encoding="utf-8")
            self.assertIn("Body content that must survive migration.", migrated)

    def test_migration_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "v01"
            self._build_v01_context(project)
            first = migrate_context(project)
            self.assertTrue(first.ok)
            self.assertEqual(len(first.migrated), 7)
            second = migrate_context(project)
            self.assertTrue(second.ok)
            self.assertEqual(len(second.migrated), 0)

    def test_migration_skips_already_front_matter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "v02"
            init_context(project)
            result = migrate_context(project)
            self.assertTrue(result.ok, result.errors)
            self.assertEqual(len(result.migrated), 0)


class MigrateCliTests(unittest.TestCase):
    def run_cli(self, args: list[str]) -> tuple[int, str]:
        from agentforge_cli.cli import main

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(args)
        return code, buffer.getvalue()

    def test_migrate_command_reports_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "v01"
            (project / ".agentforge").mkdir(parents=True)
            (project / ".agentforge" / "constitution.md").write_text(V01_CONSTITUTION, encoding="utf-8")
            code, output = self.run_cli(["migrate-context", str(project)])
            self.assertEqual(code, 0)
            self.assertIn("migrated AICS context to v0.2", output)
            self.assertIn("migrated: .agentforge/constitution.md", output)

    def test_migrate_missing_path_is_error(self) -> None:
        code, output = self.run_cli(["migrate-context", str(ROOT / "no-such-project")])
        self.assertEqual(code, 1)
        self.assertIn("not a directory", output)


if __name__ == "__main__":
    unittest.main()
