#!/usr/bin/env python3
"""Resolve the worker amigo for a delegated sub-agent, most-specific-first.

The sprint loop frames each delegated worker (build / test) as an amigo seat rather than
a generic agent. This resolver picks the identity to frame it with, most-specific-first:

  1. an explicit practitioner amigo  - <root>/sdlc-studio/personas/amigos/<seat>.md
     (the legacy filename override; kept for back-compat)
  2. a role-matched review seat      - <root>/sdlc-studio/personas/seats/*.md whose DECLARED
     role matches the seat (the project's authored "Three Amigos"; named after people, so
     matched by the machine-readable `<!-- role: ... -->` field, never the filename or H1 prose)
  3. the skill default amigo         - <skill>/templates/personas/amigos/<seat>.md
     (Dani / Sam / Lena, editable per project)
  4. generic                         - no card; the contract prompt alone

`--skip-personas` forces the generic path. The framing is ALWAYS appended AFTER the concrete
contract (file list, ACs, gates) the caller supplies - it never replaces it. Independence is the
floor regardless of identity: the resolved worker is a separate instance from its reviewer, proven
by the critic author != reviewer gate. Read-only; pure stdlib.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import version_check  # noqa: E402

SEATS = ("engineering", "qa", "product")
# Which render of the dual-render amigo card the caller wants framed.
RENDERS = ("build", "review")

# The machine-readable seat-role declaration. Keyed on, never the H1 prose or filename, so a
# seat card named after a person ("Sarah") still maps deterministically to its seat.
_ROLE_RE = re.compile(r"<!--\s*role:\s*([a-z][a-z0-9-]*)\s*-->", re.I)
# The review-render section headings a seat must carry to be framed for --render review.
_REVIEW_SECTIONS = ("Lens", "Pushes Back When", "Shadow")


class RenderError(RuntimeError):
    """A resolved seat card lacks the sections its requested render needs - a hard
    error, never a silent fallback to the generic default."""


def card_role(path: Path | str) -> str | None:
    """The declared role of a card from its `<!-- role: ... -->` field, lower-cased, or None.

    Reads the declared field only - never the H1 prose or the filename - so resolution is
    deterministic at the boundary (a renamed heading or a person-named file cannot mislead it)."""
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError:
        return None
    m = _ROLE_RE.search(text)
    return m.group(1).lower() if m else None


def project_card(root: Path | str, seat: str) -> Path | None:
    """An explicit practitioner amigo override at the legacy filename path, if present."""
    p = Path(root) / "sdlc-studio" / "personas" / "amigos" / f"{seat}.md"
    return p if p.is_file() else None


def seat_card(root: Path | str, seat: str) -> Path | None:
    """A project review seat whose DECLARED role matches `seat`, from personas/seats/.

    Cards are named after people, so the match is on the declared `role:` field,
    never the filename. Two cards claiming one role: pick deterministically (lexical by filename)
    and warn. Zero claiming it: return None so resolve_card falls through to the default - never
    crash. Read-only."""
    sdir = Path(root) / "sdlc-studio" / "personas" / "seats"
    if not sdir.is_dir():
        return None
    matches = sorted(p for p in sdir.glob("*.md") if card_role(p) == seat)
    if not matches:
        return None
    if len(matches) > 1:
        names = ", ".join(p.name for p in matches)
        print(f"warning: {len(matches)} seat cards declare role '{seat}' ({names}); "
              f"using {matches[0].name} (lexical-first). Declare one card per role to remove "
              f"the ambiguity.", file=sys.stderr)
    return matches[0]


def default_card(seat: str) -> Path | None:
    """The skill's shipped default amigo card, if present."""
    skill = version_check.skill_root()
    if not skill:
        return None
    p = Path(skill) / "templates" / "personas" / "amigos" / f"{seat}.md"
    return p if p.is_file() else None


def _has_review_render(path: Path) -> bool:
    """True if the card carries every review-render section heading."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return False
    return all(re.search(rf"^##+\s+{re.escape(s)}\b", text, re.M) for s in _REVIEW_SECTIONS)


def resolve_card(root: Path | str, seat: str, skip_personas: bool = False,
                 render: str = "build") -> Path | None:
    """The most-specific amigo card for a seat, most-specific-first: explicit amigo override,
    else a role-matched review seat, else the skill default, else None (generic).
    `skip_personas` short-circuits to None.

    For `render="review"`, a resolved PROJECT seat card that lacks its review-render sections is a
    HARD ERROR (RenderError) - never a silent fallback to the generic default. The
    shipped default cards always carry the sections, so the error scopes to a half-authored seat."""
    if skip_personas:
        return None
    card = project_card(root, seat) or seat_card(root, seat)
    if card is not None:
        if render == "review" and not _has_review_render(card):
            raise RenderError(
                f"seat card {card} (role '{seat}') is missing its review render "
                f"({', '.join(_REVIEW_SECTIONS)}); fill it or remove the card - "
                f"the resolver will not silently fall back to the generic default.")
        return card
    return default_card(seat)


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
    try:
        card = resolve_card(args.root, args.seat, args.skip_personas, args.render)
    except RenderError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
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
