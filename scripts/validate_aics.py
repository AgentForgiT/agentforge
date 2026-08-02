from __future__ import annotations

from pathlib import Path
import sys

from aics_validation import validate_aics


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    result = validate_aics(root)
    if not result.ok:
        for error in result.errors:
            print(error)
        return 1

    level_names = {1: "Context Present", 2: "Context Governed", 3: "Context Validated"}
    print(f"aics ok (level {result.level}: {level_names.get(result.level, '?')})")
    for warning in result.warnings:
        print(f"warning: {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
