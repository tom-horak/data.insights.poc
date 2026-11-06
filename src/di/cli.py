"""CLI: `di run <agent> --input data.json [--out report.md] [--dry-run]`."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .runner import run


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="di")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("run", help="spustí agenta")
    p.add_argument("agent")
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--out", type=Path)
    p.add_argument("--dry-run", action="store_true", help="jen vypíše sestavený prompt")
    args = parser.parse_args(argv)

    sys.stdout.reconfigure(encoding="utf-8")
    result = run(args.agent, args.input, dry_run=args.dry_run)
    if args.out and not args.dry_run:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(result, encoding="utf-8")
        print(f"Uloženo: {args.out}")
    else:
        print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
