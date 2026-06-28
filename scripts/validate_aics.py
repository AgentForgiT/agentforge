from __future__ import annotations

from pathlib import Path

from aics_validation import validate_aics


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    result = validate_aics(root)
    if not result.ok:
        for error in result.errors:
            print(error)
        return 1

    print("aics ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
