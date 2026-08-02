from __future__ import annotations

from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
import json
import threading
import urllib.parse


@dataclass(frozen=True)
class ServeTwinResult:
    root: Path
    port: int
    errors: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return not self.errors


def serve_twin(project_path: Path, port: int = 8737, host: str = "127.0.0.1") -> ServeTwinResult:
    """Serve the twin profile read-only over HTTP (ADR-0029).

    Endpoints: GET /twin.json, GET /search?q=<terms>, GET /.
    Stdlib only; never writes; binds 127.0.0.1 by default.
    """
    root = project_path.resolve()
    if not root.is_dir():
        return ServeTwinResult(root=root, port=port, errors=(f"project path is not a directory: {project_path}",))

    handler = make_handler(root)
    server = ThreadingHTTPServer((host, port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return ServeTwinResult(root=root, port=port)


def make_handler(root: Path) -> type[BaseHTTPRequestHandler]:
    twin_path = root / "context" / "twin.json"

    class TwinHandler(BaseHTTPRequestHandler):
        server_version = "AgentForgeTwin/0.1"

        def log_message(self, format: str, *args: object) -> None:
            return

        def do_GET(self) -> None:
            parsed = urllib.parse.urlparse(self.path)
            try:
                if parsed.path == "/twin.json":
                    self._serve_twin()
                elif parsed.path == "/search":
                    self._serve_search(parsed.query)
                elif parsed.path == "/":
                    self._serve_index()
                else:
                    self._send_json(404, {"error": "not found"})
            except Exception:
                self._send_json(500, {"error": "internal error"})

        def _serve_twin(self) -> None:
            if not twin_path.is_file():
                self._send_json(
                    404,
                    {"error": "twin profile not found — run `agentforge build-twin` first"},
                )
                return
            try:
                profile = json.loads(twin_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                self._send_json(500, {"error": "twin.json is not valid JSON — run build-twin"})
                return
            self._send_json(200, profile)

        def _serve_search(self, query: str) -> None:
            params = urllib.parse.parse_qs(query)
            q = (params.get("q") or [""])[0].strip()
            if not q:
                self._send_json(400, {"error": "query parameter 'q' is required"})
                return
            results = search_twin(root, q)
            self._send_json(200, {"query": q, "results": results})

        def _serve_index(self) -> None:
            html = _index_html(root)
            payload = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def _send_json(self, status: int, body: dict[str, Any]) -> None:
            payload = json.dumps(body).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

    return TwinHandler


def search_twin(root: Path, query: str) -> list[dict[str, Any]]:
    """Deterministic keyword search over the governance corpus (ADR-0029).

    Searches ADR titles (from files), the decision register (from the
    twin profile), and governance file names. Ranked by term overlap.
    """
    terms = [t.lower() for t in query.split() if t]
    results: list[dict[str, Any]] = []

    # ADR titles from the adrs directory
    adr_dir = root / ".agentforge" / "adrs"
    if adr_dir.is_dir():
        for path in sorted(adr_dir.glob("*.md")):
            if path.name == "ADR_TEMPLATE.md":
                continue
            title = _adr_title(path)
            score = _score(title, terms) + _score(path.name, terms)
            if score > 0:
                results.append(
                    {
                        "type": "adr",
                        "id": path.stem,
                        "title": title,
                        "path": path.relative_to(root).as_posix(),
                        "score": score,
                    }
                )

    # decision register from the twin profile
    twin_path = root / "context" / "twin.json"
    if twin_path.is_file():
        try:
            profile = json.loads(twin_path.read_text(encoding="utf-8"))
            for entry in profile.get("governance", {}).get("decision_register", []):
                title = entry.get("title", "")
                score = _score(title, terms) + _score(entry.get("id", ""), terms)
                if score > 0:
                    results.append(
                        {
                            "type": "decision",
                            "id": entry.get("id", ""),
                            "title": title,
                            "path": ".agentforge/decisions.md",
                            "score": score,
                        }
                    )
        except (json.JSONDecodeError, OSError):
            pass

    # governance file names
    for name in ("constitution", "charter", "decisions", "architecture", "repo-map"):
        if _score(name, terms) > 0:
            results.append(
                {
                    "type": "file",
                    "id": name,
                    "title": f".agentforge/{name}.md",
                    "path": f".agentforge/{name}.md",
                    "score": _score(name, terms),
                }
            )

    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:20]


def _adr_title(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("# ") and not stripped.startswith("# ADR Template"):
            return stripped[2:].strip()
    return path.stem


def _score(text: str, terms: list[str]) -> int:
    lowered = text.lower()
    return sum(1 for term in terms if term in lowered)


def _index_html(root: Path) -> str:
    twin_path = root / "context" / "twin.json"
    name = root.name or "project"
    level = "—"
    if twin_path.is_file():
        try:
            profile = json.loads(twin_path.read_text(encoding="utf-8"))
            level = str(profile.get("profile", {}).get("aics_level", "—"))
        except (json.JSONDecodeError, OSError):
            pass
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>AgentForge Twin — {name}</title>
<style>body{{font-family:system-ui,sans-serif;background:#06080d;color:#e2e8f0;max-width:720px;margin:64px auto;padding:0 24px;line-height:1.6}}
h1{{font-weight:400}}code{{font-family:monospace;color:#67e8f9;background:#111726;padding:1px 5px;border-radius:4px}}
input{{background:#0c1019;border:1px solid #1c2538;color:#e2e8f0;padding:10px;border-radius:6px;width:70%;font-family:monospace}}
button{{background:#818cf8;color:#fff;border:none;padding:10px 16px;border-radius:6px;cursor:pointer}}</style></head>
<body>
<h1>AgentForge Twin — <em>{name}</em></h1>
<p>AICS level: <code>{level}</code> · <a href="/twin.json" style="color:#67e8f9">twin.json</a></p>
<form action="/search" method="get"><input name="q" placeholder="search governance (e.g. streaming, auth, AICS)"><button>Search</button></form>
</body></html>"""
