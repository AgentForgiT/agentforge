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
    serve_twin_parser.add_argument(
        "--generator-url",
        default=None,
        help="OpenAI-compatible chat-completions URL for /ask (default local gateway)",
    )
    serve_twin_parser.add_argument(
        "--generator-model",
        default=None,
        help="Generator model (default mock-coder)",
    )
    serve_twin_parser.add_argument(
        "--generator-key",
        default=None,
        help="Bearer key for the generator (ADR-0031)",
    )

    auth_key_parser = subparsers.add_parser(
        "auth-key",
        help="Manage named gateway API keys (ADR-0031)",
    )
    auth_key_sub = auth_key_parser.add_subparsers(dest="auth_action", required=True)
    add_parser = auth_key_sub.add_parser("add", help="Add a named key (prints the key once)")
    add_parser.add_argument("--name", required=True, help="Key name (user/workload)")
    add_parser.add_argument("--rate-limit", type=int, default=None, help="Per-key requests/minute")
    add_parser.add_argument("--file", default=None, help="Key store path (default .agentforge/auth-keys.json)")
    list_parser = auth_key_sub.add_parser("list", help="List key names + rate limits (never keys)")
    list_parser.add_argument("--file", default=None, help="Key store path")
    revoke_parser = auth_key_sub.add_parser("revoke", help="Revoke a named key")
    revoke_parser.add_argument("--name", required=True, help="Key name to revoke")
    revoke_parser.add_argument("--file", default=None, help="Key store path")

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
        return _run_serve_twin(Path(args.project_path), args.port, args.generator_url, args.generator_model, args.generator_key)
    if args.command == "auth-key":
        return _run_auth_key(args)
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


def _run_serve_twin(project_path: Path, port: int, generator_url: str | None = None, generator_model: str | None = None, generator_key: str | None = None) -> int:
    from .twin_service import resolve_generator_config, serve_twin

    generator = resolve_generator_config(generator_url, generator_model, generator_key)
    result = serve_twin(project_path, port=port, generator=generator)
    if not result.ok:
        for error in result.errors:
            print(error)
        return 1

    print(f"serving twin at http://127.0.0.1:{port} (Ctrl+C to stop)")
    print(f"generator: {generator.model} @ {generator.url}")
    try:
        import time

        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        return 0


def _default_key_store() -> Path:
    return Path(".agentforge") / "auth-keys.json"


def _run_auth_key(args: Any) -> int:
    from .authkeys import add_key, list_keys, revoke_key

    store = Path(args.file) if args.file else _default_key_store()
    if args.auth_action == "add":
        result = add_key(store, args.name, rate_limit_rpm=args.rate_limit)
        if not result.ok:
            for error in result.errors:
                print(error)
            return 1
        print(f"added key '{args.name}' — copy the key now, it will not be shown again:")
        print(result.new_key)
        return 0
    if args.auth_action == "list":
        result = list_keys(store)
        if not result.ok:
            for error in result.errors:
                print(error)
            return 1
        return 0
    if args.auth_action == "revoke":
        result = revoke_key(store, args.name)
        if not result.ok:
            for error in result.errors:
                print(error)
            return 1
        print(f"revoked key '{args.name}'")
        return 0
    return 2


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
