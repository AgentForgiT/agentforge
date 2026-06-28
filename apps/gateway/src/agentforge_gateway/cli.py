from __future__ import annotations

import argparse

from .app import create_server


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agentforge-gateway")
    parser.add_argument("--config", default=None, help="Path to config JSON file")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    server = create_server(args.config)
    host, port = server.server_address
    print(f"AgentForge Gateway listening on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping AgentForge Gateway")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
