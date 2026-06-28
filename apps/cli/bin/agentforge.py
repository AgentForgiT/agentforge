from __future__ import annotations

from pathlib import Path
import sys


def main() -> int:
    src_dir = Path(__file__).resolve().parents[1] / "src"
    sys.path.insert(0, str(src_dir))

    from agentforge_cli.cli import main as cli_main

    return cli_main()


if __name__ == "__main__":
    raise SystemExit(main())
