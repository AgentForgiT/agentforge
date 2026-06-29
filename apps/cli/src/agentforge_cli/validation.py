from __future__ import annotations

from pathlib import Path
import sys


def validate_context(root: Path):
    validation_module = load_aics_validation(root)
    return validation_module.validate_aics(root)


def load_aics_validation(root: Path):
    scripts_dir = find_repo_root(root) / "scripts"
    scripts_dir_text = str(scripts_dir)
    if scripts_dir_text not in sys.path:
        sys.path.insert(0, scripts_dir_text)

    import aics_validation

    return aics_validation


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if _is_repo_root(candidate):
            return candidate

    package_repo_root = Path(__file__).resolve().parents[4]
    if _is_repo_root(package_repo_root):
        return package_repo_root

    raise RuntimeError("could not locate AgentForge repository root for AICS validation")


def _is_repo_root(path: Path) -> bool:
    return (path / "scripts" / "aics_validation.py").is_file()
