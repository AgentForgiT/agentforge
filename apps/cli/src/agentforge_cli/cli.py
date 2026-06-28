from __future__ import annotations

import argparse
from pathlib import Path

from .validation import validate_context


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agentforge")
    subparsers = parser.add_subparsers(dest="command")

    validate_context_parser = subparsers.add_parser(
        "validate-context",
        help="Validate an AICS project context",
    )
    validate_context_parser.add_argument(
        "project_path",
        nargs="?",
        default=".",
        help="Project root to validate",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "validate-context":
        return _run_validate_context(Path(args.project_path))

    parser.print_help()
    return 2


def _run_validate_context(project_path: Path) -> int:
    root = project_path.resolve()
    if not root.exists():
        print(f"project path does not exist: {project_path}")
        return 2

    result = validate_context(root)
    if not result.ok:
        for error in result.errors:
            print(error)
        return 1

    print("aics ok")
    return 0

