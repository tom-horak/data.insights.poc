"""CLI.

  di run <agent> --input data.json [--out report.md] [--dry-run]
  di run-dir <agent> [--input-dir data/raw/<agent>] [--out-dir outputs/<agent>] [--overwrite] [--dry-run]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .runner import run, run_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="di")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("run", help="spustí agenta nad jedním souborem")
    p.add_argument("agent")
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--out", type=Path)
    p.add_argument("--dry-run", action="store_true", help="jen vypíše sestavený prompt")

    d = sub.add_parser("run-dir", help="vyhodnotí všechny vstupy (*.json, *.txt) ve složce")
    d.add_argument("agent")
    d.add_argument("--input-dir", type=Path, help="výchozí: data/raw/<agent>")
    d.add_argument("--out-dir", type=Path, help="výchozí: outputs/<agent>")
    d.add_argument("--overwrite", action="store_true", help="přepíše existující výstupy")
    d.add_argument("--dry-run", action="store_true", help="jen zvaliduje a sestaví prompty, nevolá model")

    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")

    if args.command == "run":
        result = run(args.agent, args.input, dry_run=args.dry_run)
        if args.out and not args.dry_run:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(result, encoding="utf-8")
            print(f"Uloženo: {args.out}")
        else:
            print(result)
        return 0

    res = run_dir(
        args.agent,
        args.input_dir or Path("data/raw") / args.agent,
        args.out_dir or Path("outputs") / args.agent,
        dry_run=args.dry_run,
        overwrite=args.overwrite,
    )
    print(f"\nHotovo: {len(res.ok)} OK, {len(res.skipped)} přeskočeno, {len(res.failed)} chyb")
    return 1 if res.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
