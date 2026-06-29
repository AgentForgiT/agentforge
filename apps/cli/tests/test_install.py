from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[3]


class CliInstallSmokeTests(unittest.TestCase):
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

            repo_result = subprocess.run(
                [str(command), "validate-context", str(ROOT)],
                cwd=str(ROOT),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            self.assertEqual(repo_result.returncode, 0, repo_result.stderr)
            self.assertEqual(repo_result.stdout, "aics ok\n")

            example_result = subprocess.run(
                [str(command), "validate-context", str(ROOT / "examples" / "aics" / "minimal-project")],
                cwd=str(ROOT),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

            scaffold_temp = Path(tempfile.mkdtemp(prefix="agentforge-cli-scaffold-"))
            scaffold_project = scaffold_temp / "scaffolded-project"
            scaffold_result = subprocess.run(
                [str(command), "init-context", str(scaffold_project)],
                cwd=str(ROOT),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            self.assertEqual(scaffold_result.returncode, 0, scaffold_result.stderr)
            self.assertIn("initialized AICS context:", scaffold_result.stdout)

            scaffold_validate = subprocess.run(
                [str(command), "validate-context", str(scaffold_project)],
                cwd=str(ROOT),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            self.assertEqual(scaffold_validate.returncode, 0, scaffold_validate.stderr)
            self.assertEqual(scaffold_validate.stdout, "aics ok\n")
            shutil.rmtree(scaffold_temp)

        self.assertEqual(example_result.returncode, 0, example_result.stderr)
        self.assertEqual(example_result.stdout, "aics ok\n")


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
