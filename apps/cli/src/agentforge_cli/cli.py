from __future__ import annotations

import argparse
from pathlib import Path

from .explanation import explain_context
from .scaffolding import init_context
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

    init_context_parser = subparsers.add_parser(
        "init-context",
        help="Initialize a minimal AICS project context",
    )
    init_context_parser.add_argument(
        "project_path",
        nargs="?",
        default=".",
        help="Project root to initialize",
    )

    explain_context_parser = subparsers.add_parser(
        "explain-context",
        help="Explain an AICS project context",
    )
    explain_context_parser.add_argument(
        "project_path",
        nargs="?",
        default=".",
        help="Project root to explain",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "validate-context":
        return _run_validate_context(Path(args.project_path))
    if args.command == "init-context":
        return _run_init_context(Path(args.project_path))
    if args.command == "explain-context":
        return _run_explain_context(Path(args.project_path))

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


def _run_init_context(project_path: Path) -> int:
    result = init_context(project_path)
    if not result.ok:
        for error in result.errors:
            print(error)
        return 1

    print(f"initialized AICS context: {result.root}")
    return 0


def _run_explain_context(project_path: Path) -> int:
    result = explain_context(project_path)
    if not result.ok:
        for error in result.errors:
            print(error)
        return 1

    for line in result.lines:
        print(line)
    return 0
