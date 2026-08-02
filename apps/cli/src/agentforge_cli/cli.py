from __future__ import annotations

import argparse
from pathlib import Path

from .diagnostics import diagnose_context
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

    migrate_context_parser = subparsers.add_parser(
        "migrate-context",
        help="Migrate an AICS v0.1 context to v0.2 (additive)",
    )
    migrate_context_parser.add_argument(
        "project_path",
        nargs="?",
        default=".",
        help="Project root to migrate",
    )

    build_twin_parser = subparsers.add_parser(
        "build-twin",
        help="Build the engineering twin profile (context/twin.json)",
    )
    build_twin_parser.add_argument(
        "project_path",
        nargs="?",
        default=".",
        help="Project root to build the twin for",
    )

    serve_twin_parser = subparsers.add_parser(
        "serve-twin",
        help="Serve the engineering twin profile read-only over HTTP",
    )
    serve_twin_parser.add_argument(
        "project_path",
        nargs="?",
        default=".",
        help="Project root whose twin to serve",
    )
    serve_twin_parser.add_argument(
        "--port",
        type=int,
        default=8737,
        help="Port to bind (default 8737)",
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

    doctor_parser = subparsers.add_parser(
        "doctor",
        help="Diagnose local AICS project context health",
    )
    doctor_parser.add_argument(
        "project_path",
        nargs="?",
        default=".",
        help="Project root to diagnose",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "validate-context":
        return _run_validate_context(Path(args.project_path))
    if args.command == "init-context":
        return _run_init_context(Path(args.project_path))
    if args.command == "migrate-context":
        return _run_migrate_context(Path(args.project_path))
    if args.command == "build-twin":
        return _run_build_twin(Path(args.project_path))
    if args.command == "serve-twin":
        return _run_serve_twin(Path(args.project_path), args.port)
    if args.command == "explain-context":
        return _run_explain_context(Path(args.project_path))
    if args.command == "doctor":
        return _run_doctor(Path(args.project_path))

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

    level_names = {1: "Context Present", 2: "Context Governed", 3: "Context Validated"}
    print(f"aics ok (level {result.level}: {level_names.get(result.level, '?')})")
    for warning in result.warnings:
        print(f"warning: {warning}")
    return 0


def _run_init_context(project_path: Path) -> int:
    result = init_context(project_path)
    if not result.ok:
        for error in result.errors:
            print(error)
        return 1

    print(f"initialized AICS context: {result.root}")
    return 0


def _run_migrate_context(project_path: Path) -> int:
    from .migration import migrate_context

    result = migrate_context(project_path)
    if not result.ok:
        for error in result.errors:
            print(error)
        return 1

    print(f"migrated AICS context to v0.2: {result.root}")
    for relative in result.migrated:
        print(f"  migrated: {relative}")
    return 0


def _run_build_twin(project_path: Path) -> int:
    from .twin import build_twin

    result = build_twin(project_path)
    if not result.ok:
        for error in result.errors:
            print(error)
        return 1

    print(f"built engineering twin profile: {result.output}")
    return 0


def _run_serve_twin(project_path: Path, port: int) -> int:
    from .twin_service import serve_twin

    result = serve_twin(project_path, port=port)
    if not result.ok:
        for error in result.errors:
            print(error)
        return 1

    print(f"serving twin at http://127.0.0.1:{port} (Ctrl+C to stop)")
    try:
        import time

        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
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


def _run_doctor(project_path: Path) -> int:
    result = diagnose_context(project_path)
    if not result.ok:
        for error in result.errors:
            print(error)
        return 1

    for line in result.lines:
        print(line)
    return 0 if result.healthy else 1
