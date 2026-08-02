from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class SdkInstallSmokeTests(unittest.TestCase):
    def test_editable_install_imports_sdk(self) -> None:
        with temp_virtualenv() as venv_python:
            install = subprocess.run(
                [str(venv_python), "-m", "pip", "install", "--no-build-isolation", "-e", str(ROOT)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(install.returncode, 0, install.stderr)

            import_result = subprocess.run(
                [str(venv_python), "-c", "from agentforge_sdk import AgentForgeClient; print('sdk import ok')"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(import_result.returncode, 0, import_result.stderr)
            self.assertIn("sdk import ok", import_result.stdout)

    def test_sdist_and_wheel_build(self) -> None:
        import importlib.util
        import tempfile

        if importlib.util.find_spec("build") is None:
            self.skipTest("python -m build not available in this interpreter")

        with tempfile.TemporaryDirectory() as tmp:
            outdir = Path(tmp) / "dist"
            build = subprocess.run(
                [sys.executable, "-m", "build", "--outdir", str(outdir), str(ROOT)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(build.returncode, 0, build.stderr)
            wheels = list(outdir.glob("*.whl"))
            sdists = list(outdir.glob("*.tar.gz"))
            self.assertEqual(len(wheels), 1, f"expected one wheel, got {[w.name for w in wheels]}")
            self.assertEqual(len(sdists), 1, f"expected one sdist, got {[s.name for s in sdists]}")


class temp_virtualenv:
    def __enter__(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        venv_dir = Path(self.temp_dir.name) / "venv"
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True, capture_output=True)
        if sys.platform == "win32":
            self.python = venv_dir / "Scripts" / "python.exe"
        else:
            self.python = venv_dir / "bin" / "python"
        return self.python

    def __exit__(self, *args: object) -> None:
        self.temp_dir.cleanup()


if __name__ == "__main__":
    unittest.main()
