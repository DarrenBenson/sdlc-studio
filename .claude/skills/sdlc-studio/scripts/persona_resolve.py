#!/usr/bin/env python3
"""Resolve the worker amigo for a delegated sub-agent, most-specific-first.

The sprint loop frames each delegated worker (build / test) as an amigo seat rather than
a generic agent. This resolver picks the identity to frame it with, in priority order:

  1. a project-authored practitioner amigo  - <root>/sdlc-studio/personas/amigos/<seat>.md
     (the operator's specialised identity; the richer and more project-specific, the better)
  2. the skill default amigo                - <skill>/templates/personas/amigos/<seat>.md
     (Dani / Sam / Lena, editable per project)
  3. generic                                - no card; the contract prompt alone

`--skip-personas` forces the generic path. The framing is ALWAYS appended AFTER the concrete
contract (file list, ACs, gates) the caller supplies - it never replaces it. Independence is the
floor regardless of identity: the resolved worker is a separate instance from its reviewer, proven
by the critic author != reviewer gate. Read-only; pure stdlib.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import version_check  # noqa: E402

SEATS = ("engineering", "qa", "product")
# Which render of the dual-render amigo card the caller wants framed.
RENDERS = ("build", "review")


def project_card(root: Path | str, seat: str) -> Path | None:
    """A project-authored practitioner amigo override, if present."""
    p = Path(root) / "sdlc-studio" / "personas" / "amigos" / f"{seat}.md"
    return p if p.is_file() else None


def default_card(seat: str) -> Path | None:
    """The skill's shipped default amigo card, if present."""
    skill = version_check.skill_root()
    if not skill:
        return None
    p = Path(skill) / "templates" / "personas" / "amigos" / f"{seat}.md"
    return p if p.is_file() else None


def resolve_card(root: Path | str, seat: str, skip_personas: bool = False) -> Path | None:
    """The most-specific amigo card for a seat: project override, else skill default,
    else None (generic). `skip_personas` short-circuits to None."""
    if skip_personas:
        return None
    return project_card(root, seat) or default_card(seat)


def frame(card: Path | None, seat: str, render: str) -> str:
    """The framing text to append after the caller's concrete contract. Empty string for
    the generic path, so `--skip-personas` yields a byte-equivalent contract."""
    if card is None:
        return ""
    body = card.read_text(encoding="utf-8")
    note = (
        f"\n\n---\n\nYou are the {seat} amigo. Adopt the charter below as your working stance "
        f"(the {render} render). It is a disposition layer ONLY: the concrete contract above - the "
        f"file list, the acceptance criteria, and the quality gates - is law and is never overridden "
        f"by it. You are a separate instance from your reviewer; you never sign off your own work.\n\n"
    )
    return note + body


def cmd_resolve(args: argparse.Namespace) -> int:
    if args.seat not in SEATS:
        print(f"unknown seat '{args.seat}' (expected: {', '.join(SEATS)})", file=sys.stderr)
        return 2
    card = resolve_card(args.root, args.seat, args.skip_personas)
    if args.path_only:
        print(str(card) if card else "")
        return 0
    print(frame(card, args.seat, args.render))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Resolve the worker amigo for a delegated sub-agent.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("resolve", help="Print the framing for a seat (most-specific-first).")
    r.add_argument("--seat", required=True, help=f"one of: {', '.join(SEATS)}")
    r.add_argument("--render", default="build", choices=RENDERS, help="dual-render: build or review")
    r.add_argument("--root", default=".", help="project root")
    r.add_argument("--skip-personas", action="store_true", help="force the generic path (no framing)")
    r.add_argument("--path-only", action="store_true", help="print the resolved card path, not its body")
    r.set_defaults(func=cmd_resolve)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
