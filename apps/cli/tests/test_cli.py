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

from agentforge_cli.cli import main


class CliValidateContextTests(unittest.TestCase):
    def test_validates_current_repo(self) -> None:
        result, output = run_cli(["validate-context", str(ROOT)])

        self.assertEqual(result, 0)
        self.assertEqual(output, "aics ok\n")

    def test_validates_explicit_example_path(self) -> None:
        result, output = run_cli(["validate-context", str(ROOT / "examples" / "aics" / "minimal-project")])

        self.assertEqual(result, 0)
        self.assertEqual(output, "aics ok\n")

    def test_reports_missing_required_file(self) -> None:
        with copied_example() as project:
            (project / ".agentforge" / "constitution.md").unlink()

            result, output = run_cli(["validate-context", str(project)])

        self.assertEqual(result, 1)
        self.assertIn("missing AICS file: .agentforge/constitution.md", output)

    def test_reports_invalid_metadata(self) -> None:
        with copied_example() as project:
            charter = project / ".agentforge" / "charter.md"
            charter.write_text("# Charter\n\nNo metadata here.\n", encoding="utf-8")

            result, output = run_cli(["validate-context", str(project)])

        self.assertEqual(result, 1)
        self.assertIn("missing Metadata block: .agentforge/charter.md", output)

    def test_reports_missing_project_path_as_usage_error(self) -> None:
        result, output = run_cli(["validate-context", str(ROOT / "missing-project")])

        self.assertEqual(result, 2)
        self.assertIn("project path does not exist:", output)

    def test_reports_no_command_as_usage_error(self) -> None:
        result, output = run_cli([])

        self.assertEqual(result, 2)
        self.assertIn("usage: agentforge", output)

    def test_init_context_scaffolds_new_target_directory(self) -> None:
        with temp_project_dir() as temp_dir:
            project = temp_dir / "scaffolded-project"

            result, output = run_cli(["init-context", str(project)])
            validation_result, validation_output = run_cli(["validate-context", str(project)])

            self.assertTrue((project / ".agentforge" / "constitution.md").is_file())
            self.assertTrue((project / ".agentforge" / "standards").is_dir())

        self.assertEqual(result, 0)
        self.assertIn("initialized AICS context:", output)
        self.assertEqual(validation_result, 0)
        self.assertEqual(validation_output, "aics ok\n")

    def test_init_context_scaffolds_existing_directory_without_conflict(self) -> None:
        with temp_project_dir() as project:
            readme = project / "README.md"
            readme.write_text("# Existing project\n", encoding="utf-8")

            result, output = run_cli(["init-context", str(project)])
            validation_result, validation_output = run_cli(["validate-context", str(project)])

            self.assertEqual(readme.read_text(encoding="utf-8"), "# Existing project\n")

        self.assertEqual(result, 0)
        self.assertIn("initialized AICS context:", output)
        self.assertEqual(validation_result, 0)
        self.assertEqual(validation_output, "aics ok\n")

    def test_init_context_reports_conflicts_without_writing_other_files(self) -> None:
        with temp_project_dir() as project:
            managed_dir = project / ".agentforge"
            managed_dir.mkdir(parents=True)
            constitution = managed_dir / "constitution.md"
            constitution.write_text("custom constitution\n", encoding="utf-8")

            result, output = run_cli(["init-context", str(project)])

            self.assertEqual(constitution.read_text(encoding="utf-8"), "custom constitution\n")
            self.assertFalse((managed_dir / "charter.md").exists())

        self.assertEqual(result, 1)
        self.assertIn("scaffold conflict: .agentforge/constitution.md already exists", output)

    def test_init_context_reports_file_target_as_error(self) -> None:
        with temp_project_dir() as temp_dir:
            project_file = temp_dir / "project.txt"
            project_file.write_text("not a directory\n", encoding="utf-8")

            result, output = run_cli(["init-context", str(project_file)])

        self.assertEqual(result, 1)
        self.assertIn("project path is not a directory:", output)

    def test_explain_context_reports_current_repo(self) -> None:
        result, output = run_cli(["explain-context", str(ROOT)])

        self.assertEqual(result, 0)
        self.assertIn("AgentForge context explanation\n", output)
        self.assertIn(f"Project root: {ROOT}", output)
        self.assertIn("AICS validation: passed", output)
        self.assertIn("Context root: .agentforge (present)", output)
        self.assertIn("- .agentforge/constitution.md (present)", output)
        self.assertIn("- context is complete for AICS v0.1 validation", output)

    def test_explain_context_reports_scaffolded_project(self) -> None:
        with temp_project_dir() as temp_dir:
            project = temp_dir / "scaffolded-project"
            run_cli(["init-context", str(project)])

            result, output = run_cli(["explain-context", str(project)])

        self.assertEqual(result, 0)
        self.assertIn("AICS validation: passed", output)
        self.assertIn("- .agentforge/agents/AGENTS.md (present)", output)

    def test_explain_context_reports_invalid_context_without_failing(self) -> None:
        with copied_example() as project:
            (project / ".agentforge" / "constitution.md").unlink()

            result, output = run_cli(["explain-context", str(project)])

        self.assertEqual(result, 0)
        self.assertIn("AICS validation: failed", output)
        self.assertIn("- .agentforge/constitution.md (missing)", output)
        self.assertIn("- missing AICS file: .agentforge/constitution.md", output)

    def test_explain_context_reports_missing_project_path(self) -> None:
        result, output = run_cli(["explain-context", str(ROOT / "missing-project")])

        self.assertEqual(result, 1)
        self.assertIn("project path does not exist:", output)

    def test_doctor_reports_current_repo_as_healthy(self) -> None:
        result, output = run_cli(["doctor", str(ROOT)])

        self.assertEqual(result, 0)
        self.assertIn("AgentForge doctor\n", output)
        self.assertIn(f"Project root: {ROOT}", output)
        self.assertIn("Overall status: healthy", output)
        self.assertIn("AICS validation: passed", output)
        self.assertIn("Context root: .agentforge (present)", output)
        self.assertIn("- required directories: passed", output)
        self.assertIn("- required files: passed", output)
        self.assertIn("- metadata blocks: passed", output)
        self.assertIn("- required template text: passed", output)
        self.assertIn("- context is healthy for AICS v0.1 validation", output)

    def test_doctor_reports_explicit_example_as_healthy(self) -> None:
        result, output = run_cli(["doctor", str(ROOT / "examples" / "aics" / "minimal-project")])

        self.assertEqual(result, 0)
        self.assertIn("Overall status: healthy", output)
        self.assertIn("AICS validation: passed", output)

    def test_doctor_reports_scaffolded_project_as_healthy(self) -> None:
        with temp_project_dir() as temp_dir:
            project = temp_dir / "scaffolded-project"
            run_cli(["init-context", str(project)])

            result, output = run_cli(["doctor", str(project)])

        self.assertEqual(result, 0)
        self.assertIn("Overall status: healthy", output)
        self.assertIn("- context is healthy for AICS v0.1 validation", output)

    def test_doctor_reports_invalid_context_as_unhealthy(self) -> None:
        with copied_example() as project:
            (project / ".agentforge" / "constitution.md").unlink()

            result, output = run_cli(["doctor", str(project)])

        self.assertEqual(result, 1)
        self.assertIn("Overall status: unhealthy", output)
        self.assertIn("AICS validation: failed", output)
        self.assertIn("- required files: failed (1 missing)", output)
        self.assertIn("- missing AICS file: .agentforge/constitution.md", output)
        self.assertIn("Next action: fix the validation signals", output)

    def test_doctor_reports_invalid_metadata_as_unhealthy(self) -> None:
        with copied_example() as project:
            charter = project / ".agentforge" / "charter.md"
            charter.write_text("# Charter\n\nNo metadata here.\n", encoding="utf-8")

            result, output = run_cli(["doctor", str(project)])

        self.assertEqual(result, 1)
        self.assertIn("Overall status: unhealthy", output)
        self.assertIn("- metadata blocks: failed (1 missing)", output)
        self.assertIn("- missing Metadata block: .agentforge/charter.md", output)

    def test_doctor_reports_missing_project_path(self) -> None:
        result, output = run_cli(["doctor", str(ROOT / "missing-project")])

        self.assertEqual(result, 1)
        self.assertIn("project path does not exist:", output)

def run_cli(args: list[str]) -> tuple[int, str]:
    stdout = io.StringIO()
    with redirect_stdout(stdout):
        result = main(args)
    return result, stdout.getvalue()


class copied_example:
    def __enter__(self) -> Path:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="agentforge-cli-test-"))
        self.project = self.temp_dir / "minimal-project"
        shutil.copytree(ROOT / "examples" / "aics" / "minimal-project", self.project)
        return self.project

    def __exit__(self, *args: object) -> None:
        shutil.rmtree(self.temp_dir)


class temp_project_dir:
    def __enter__(self) -> Path:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="agentforge-cli-init-"))
        return self.temp_dir

    def __exit__(self, *args: object) -> None:
        shutil.rmtree(self.temp_dir)


if __name__ == "__main__":
    unittest.main()
