from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from importlib.resources import files
from pathlib import Path
import json

from .validation import load_aics_validation


@dataclass(frozen=True)
class BuildTwinResult:
    root: Path
    output: Path | None = None
    errors: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return not self.errors


def build_twin(project_path: Path) -> BuildTwinResult:
    """Generate the engineering twin profile (ADR-0028).

    Reads AICS context + optional gateway config, writes
    context/twin.json validated against twin.schema.json. Read-only
    with respect to AICS files; idempotent.
    """
    root = project_path.resolve()
    if not root.is_dir():
        return BuildTwinResult(root=root, errors=(f"project path is not a directory: {project_path}",))

    # AICS level from the canonical validator
    try:
        validation = load_aics_validation(root).validate_aics(root)
    except RuntimeError as exc:
        return BuildTwinResult(root=root, errors=(str(exc),))

    context_dir = root / "context"
    try:
        context_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return BuildTwinResult(root=root, errors=(f"could not create context/: {exc}",))

    profile = {
        "schema_version": "0.1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "aics_version": _aics_version(root),
        "profile": {
            "project_name": root.name or "project",
            "repo_root": str(root),
            "aics_level": validation.level,
        },
        "governance": _governance(root),
    }

    gateway = _gateway_surface(root)
    if gateway is not None:
        profile["gateway"] = gateway

    try:
        _validate_against_schema(profile)
    except ValueError as exc:
        return BuildTwinResult(root=root, errors=(f"twin profile failed schema validation: {exc}",))

    output = context_dir / "twin.json"
    try:
        output.write_text(json.dumps(profile, indent=2) + "\n", encoding="utf-8")
    except OSError as exc:
        return BuildTwinResult(root=root, errors=(f"could not write {output}: {exc}",))

    return BuildTwinResult(root=root, output=output)


def _aics_version(root: Path) -> str:
    marker = root / ".agentforge" / "aics-version"
    if marker.is_file():
        return marker.read_text(encoding="utf-8").strip()
    return "0.1"


def _governance(root: Path) -> dict[str, object]:
    agentforge = root / ".agentforge"
    adr_dir = agentforge / "adrs"
    rfc_dir = agentforge / "rfcs"

    def rel(path: Path) -> str:
        return path.relative_to(root).as_posix() if path.exists() else ""

    decision_register: list[dict[str, str]] = []
    decisions_path = agentforge / "decisions.md"
    if decisions_path.is_file():
        for line in decisions_path.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("|") and "ADR-" in line and "Accepted" in line:
                parts = [p.strip() for p in line.strip().strip("|").split("|")]
                if len(parts) >= 4:
                    decision_register.append({"id": parts[0], "date": parts[1], "title": parts[3]})

    return {
        "constitution": rel(agentforge / "constitution.md"),
        "charter": rel(agentforge / "charter.md"),
        "decisions": rel(decisions_path),
        "architecture": rel(agentforge / "architecture.md"),
        "repo_map": rel(agentforge / "repo-map.md"),
        "agents": rel(agentforge / "agents" / "AGENTS.md"),
        "adr_count": sum(1 for p in adr_dir.glob("*.md")) if adr_dir.is_dir() else 0,
        "rfc_count": sum(1 for p in rfc_dir.glob("*.md")) if rfc_dir.is_dir() else 0,
        "decision_register": decision_register,
    }


def _gateway_surface(root: Path) -> dict[str, object] | None:
    configs = sorted((root / "apps" / "gateway").glob("config*.json")) if (root / "apps" / "gateway").is_dir() else []
    if not configs:
        return None
    try:
        import sys

        gateway_src = root / "apps" / "gateway" / "src"
        if str(gateway_src) not in sys.path:
            sys.path.insert(0, str(gateway_src))
        from agentforge_gateway.config import load_config

        config = load_config(configs[0])
    except Exception:
        # gateway config present but not parseable here (e.g. env-keyed);
        # report the config paths without a full parse
        return {
            "models": [],
            "providers": [],
            "surfaces": ["/health", "/v1/models", "/v1/chat/completions", "/v1/messages"],
            "config_files": [c.relative_to(root).as_posix() for c in configs],
        }

    return {
        "models": [
            {"alias": name, "provider": model.provider, "provider_model": model.provider_model}
            for name, model in sorted(config.models.items())
        ],
        "providers": [name for name in sorted(config.providers)],
        "surfaces": ["/health", "/v1/models", "/v1/chat/completions", "/v1/messages", "/mcp"],
        "config_files": [c.relative_to(root).as_posix() for c in configs],
    }


def _validate_against_schema(profile: dict[str, object]) -> None:
    """Minimal structural validation against twin.schema.json expectations
    (stdlib only; no jsonschema dependency)."""
    if profile.get("schema_version") != "0.1":
        raise ValueError("schema_version must be '0.1'")
    if "profile" not in profile or "governance" not in profile:
        raise ValueError("missing profile or governance")
    if not isinstance(profile["profile"], dict) or "aics_level" not in profile["profile"]:
        raise ValueError("profile.aics_level missing")
    level = profile["profile"]["aics_level"]
    if not isinstance(level, int) or not 1 <= level <= 3:
        raise ValueError("profile.aics_level must be 1..3")
    governance = profile["governance"]
    if not isinstance(governance, dict):
        raise ValueError("governance must be an object")
    for key in ("constitution", "charter", "decisions", "architecture", "repo_map", "agents"):
        if key not in governance:
            raise ValueError(f"governance.{key} missing")
