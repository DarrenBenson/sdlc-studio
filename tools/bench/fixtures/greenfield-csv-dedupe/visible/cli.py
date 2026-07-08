#!/usr/bin/env python3
"""A tiny CSV utility CLI.

Subcommands:
  count <path>    Print the number of data rows (excluding the header).
"""
from __future__ import annotations

import argparse
import csv
import sys


def cmd_count(args: argparse.Namespace) -> int:
    with open(args.path, newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    data_rows = rows[1:] if rows else []
    print(len(data_rows))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Tiny CSV utility CLI.")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("count", help="Print the number of data rows.")
    c.add_argument("path")
    c.set_defaults(func=cmd_count)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
