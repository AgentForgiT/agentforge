from __future__ import annotations

import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "apps" / "cli" / "src"))

from agentforge_cli.twin import build_twin
from agentforge_cli.scaffolding import init_context


class BuildTwinTests(unittest.TestCase):
    def test_builds_twin_for_scaffolded_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "twin-project"
            init_context(project)
            result = build_twin(project)
            self.assertTrue(result.ok, result.errors)
            self.assertIsNotNone(result.output)
            profile = json.loads(result.output.read_text(encoding="utf-8"))
            self.assertEqual(profile["schema_version"], "0.1")
            self.assertEqual(profile["aics_version"], "0.2")
            self.assertEqual(profile["profile"]["aics_level"], 3)
            self.assertEqual(profile["profile"]["project_name"], "twin-project")

    def test_governance_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "gov"
            init_context(project)
            result = build_twin(project)
            governance = json.loads(result.output.read_text(encoding="utf-8"))["governance"]
            for key in ("constitution", "charter", "decisions", "architecture", "repo_map", "agents"):
                self.assertTrue(governance[key].endswith(".md"), key)
            self.assertEqual(governance["adr_count"], 1)  # scaffold ships ADR_TEMPLATE.md
            self.assertIsInstance(governance["decision_register"], list)

    def test_read_only_with_respect_to_aics(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "ro"
            init_context(project)
            constitution = (project / ".agentforge" / "constitution.md").read_text(encoding="utf-8")
            build_twin(project)
            after = (project / ".agentforge" / "constitution.md").read_text(encoding="utf-8")
            self.assertEqual(constitution, after)

    def test_idempotent_structure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "idem"
            init_context(project)
            build_twin(project)
            first = json.loads((project / "context" / "twin.json").read_text(encoding="utf-8"))
            build_twin(project)
            second = json.loads((project / "context" / "twin.json").read_text(encoding="utf-8"))
            first["generated_at"] = ""
            second["generated_at"] = ""
            self.assertEqual(first, second)

    def test_missing_path_is_error(self) -> None:
        result = build_twin(ROOT / "no-such-project")
        self.assertFalse(result.ok)
        self.assertIn("not a directory", result.errors[0])

    def test_gateway_surface_included_when_config_present(self) -> None:
        # the AgentForge repo itself has apps/gateway configs
        result = build_twin(ROOT)
        self.assertTrue(result.ok, result.errors)
        profile = json.loads(result.output.read_text(encoding="utf-8"))
        self.assertIn("gateway", profile)
        self.assertGreater(len(profile["gateway"]["models"]), 0)
        self.assertIn("/v1/chat/completions", profile["gateway"]["surfaces"])


class BuildTwinCliTests(unittest.TestCase):
    def run_cli(self, args: list[str]) -> tuple[int, str]:
        from agentforge_cli.cli import main

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(args)
        return code, buffer.getvalue()

    def test_build_twin_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "cli-twin"
            init_context(project)
            code, output = self.run_cli(["build-twin", str(project)])
            self.assertEqual(code, 0)
            self.assertIn("built engineering twin profile", output)
            self.assertTrue((project / "context" / "twin.json").is_file())


if __name__ == "__main__":
    unittest.main()
