from __future__ import annotations

from pathlib import Path
import sys


def validate_context(root: Path):
    scripts_dir = _repo_root() / "scripts"
    scripts_dir_text = str(scripts_dir)
    if scripts_dir_text not in sys.path:
        sys.path.insert(0, scripts_dir_text)

    from aics_validation import validate_aics

    return validate_aics(root)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]
