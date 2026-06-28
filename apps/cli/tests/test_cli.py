from __future__ import annotations

import io
import os
from pathlib import Path
import shutil
import subprocess
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

    def test_editable_install_exposes_agentforge_command(self) -> None:
        with temp_virtualenv() as venv_python:
            install = subprocess.run(
                [
                    str(venv_python),
                    "-m",
                    "pip",
                    "install",
                    "--no-build-isolation",
                    "-e",
                    str(ROOT / "apps" / "cli"),
                ],
                cwd=str(ROOT),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            self.assertEqual(install.returncode, 0, install.stderr)

            command = resolve_agentforge_command(venv_python)
            result = subprocess.run(
                [str(command), "validate-context", str(ROOT)],
                cwd=str(ROOT),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "aics ok\n")


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


class temp_virtualenv:
    def __enter__(self) -> Path:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="agentforge-cli-venv-"))
        result = subprocess.run(
            [sys.executable, "-m", "venv", "--system-site-packages", str(self.temp_dir)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise AssertionError(result.stderr)
        return resolve_venv_python(self.temp_dir)

    def __exit__(self, *args: object) -> None:
        shutil.rmtree(self.temp_dir)


def resolve_venv_python(venv_dir: Path) -> Path:
    scripts_dir = "Scripts" if os.name == "nt" else "bin"
    executable = "python.exe" if os.name == "nt" else "python"
    return venv_dir / scripts_dir / executable


def resolve_agentforge_command(venv_python: Path) -> Path:
    scripts_dir = venv_python.parent
    executable = "agentforge.exe" if os.name == "nt" else "agentforge"
    return scripts_dir / executable


if __name__ == "__main__":
    unittest.main()
