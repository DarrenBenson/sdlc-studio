#!/usr/bin/env python3
"""Resolve the worker amigo for a delegated sub-agent, most-specific-first.

The sprint loop frames each delegated worker (build / test) as an amigo seat rather than
a generic agent. This resolver picks the identity to frame it with, most-specific-first:

  1. a role-matched project seat     - <root>/sdlc-studio/personas/seats/*.md whose DECLARED
     role matches the seat (the converged home; cards are named after people, so
     matched by the machine-readable `<!-- role: ... -->` field, never the filename or H1 prose)
  2. the legacy amigos file          - <root>/sdlc-studio/personas/amigos/<seat>.md
     (retired home; resolves only when no seat claims the role, with a migrate warning)
  3. the skill default amigo         - <skill>/templates/personas/amigos/<seat>.md
     (Dani / Sam / Lena, the zero-setup fallback)
  4. generic                         - no card; the contract prompt alone

`--skip-personas` forces the generic path. The framing is ALWAYS appended AFTER the concrete
contract (file list, ACs, gates) the caller supplies - it never replaces it. Independence is the
floor regardless of identity: the resolved worker is a separate instance from its reviewer, proven
by the critic author != reviewer gate. Read-only; pure stdlib.

The `resolve-consult` subcommand exposes the same declared-role chain to the consult workflow, so an
authored seat drives a consult too (not only a delegated worker). It resolves by declared role:
a role-matched project seat, else the skill default seat, else the generic enriched seat schema; a
consult needs the review render, so a matched project seat lacking it is a hard error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import version_check  # noqa: E402
from lib import sdlc_md  # noqa: E402

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


def generic_schema() -> Path | None:
    """The generic enriched seat schema - the consult fallback when no seat fills the role."""
    skill = version_check.skill_root()
    if not skill:
        return None
    p = Path(skill) / "templates" / "personas" / "amigo-template.md"
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
    """The most-specific card for a seat, seats-first: a role-matched personas/seats/
    card is THE project home and always wins; a legacy personas/amigos/ card resolves
    only as a warned fallback when no seat claims the role; else the skill default,
    else None (generic). `skip_personas` short-circuits to None.

    For `render="review"`, a resolved PROJECT seat card that lacks its review-render sections is a
    HARD ERROR (RenderError) - never a silent fallback to the generic default. The
    shipped default cards always carry the sections, so the error scopes to a half-authored seat."""
    if skip_personas:
        return None
    # Converged home: a declared-role seat card is THE project
    # authority. The legacy personas/amigos/<seat>.md path resolves only when no seat
    # claims the role - the old amigos-first order silently shadowed every authored or
    # generated seat on projects that had been through `project upgrade`.
    card = seat_card(root, seat)
    if card is None:
        card = project_card(root, seat)
        if card is not None:
            print(f"warning: resolved legacy card {card} - personas/amigos/ is the retired "
                  f"home; migrate the card to personas/seats/ with a declared "
                  f"`<!-- role: {seat} -->` (project upgrade migrates it mechanically)",
                  file=sys.stderr)
    if card is not None:
        if render == "review" and not _has_review_render(card):
            raise RenderError(
                f"seat card {card} (role '{seat}') is missing its review render "
                f"({', '.join(_REVIEW_SECTIONS)}); fill it or remove the card - "
                f"the resolver will not silently fall back to the generic default.")
        return card
    return default_card(seat)


def resolve_consult(root: Path | str, role: str) -> Path | None:
    """The seat card a consult runs against, by declared `role:`, most-specific-first:
    a project review seat whose declared role matches, else the skill default seat for that role,
    else the generic enriched seat schema. Reuses the delegation chain (`seat_card` keys on the
    declared field, never the filename or H1 prose), so consult and delegation honour the same
    authored seat.

    A consult always critiques, so the resolved card needs its review render: a matched PROJECT seat
    missing those sections is a HARD ERROR (RenderError), never a silent fallback to the generic
    schema. The shipped default and the generic schema always carry the sections."""
    card = seat_card(root, role)
    if card is not None:
        if not _has_review_render(card):
            raise RenderError(
                f"seat card {card} (role '{role}') is missing its review render "
                f"({', '.join(_REVIEW_SECTIONS)}); fill it or remove the card - "
                f"a consult will not silently fall back to the generic schema.")
        return card
    return default_card(role) or generic_schema()


# The Three-Amigos panel per ceremony. The ORDER encodes who leads: `refine` is engineering-led
# (a request is largely a build breakdown), `triage` is QA-led (is it reproducible? what is the
# real defect?). The whole panel weighs in; the lead is named first. One definition, so refine and
# triage resolve the same seats the same way.
REFINE_PANEL = ("engineering", "product", "qa")
TRIAGE_PANEL = ("qa", "engineering", "product")


def seat_name(card: Path | None, role: str) -> str:
    """The human name of a seat from its card H1 (`# Dani Okafor - Engineering amigo` -> 'Dani
    Okafor'), or the capitalised role when there is no card (the `--skip-personas` / generic path),
    so a consult always has a name to attribute a question to."""
    if card is not None:
        try:
            in_fence = False
            for ln in card.read_text(encoding="utf-8").splitlines():
                if ln.lstrip().startswith("```"):   # skip fenced code: a `# x` inside it is not the H1
                    in_fence = not in_fence
                    continue
                if not in_fence and ln.startswith("# "):
                    return ln[2:].split(" - ", 1)[0].strip() or role.capitalize()
        except OSError:
            pass
    return role.capitalize()


def amigo_panel(root: Path | str, roles, *, skip_personas: bool = False,
                render: str = "review") -> list[dict]:
    """Resolve each role in `roles` to its named amigo seat for a consult, IN ORDER (the first is
    the lead). Returns `[{role, seat, card_path, framing}]`. `skip_personas` yields `card=None` and
    empty framing throughout - a byte-equivalent, unframed panel - so the flag is honoured the same
    way `frame` already honours it. A matched PROJECT seat missing its review render raises
    RenderError (never a silent generic fallback), exactly as `resolve_consult` does."""
    panel: list[dict] = []
    for role in roles:
        card = None if skip_personas else resolve_consult(root, role)
        panel.append({"role": role, "seat": seat_name(card, role),
                      "card_path": str(card) if card else None,
                      "framing": frame(card, role, render)})
    return panel


def consult(root: Path | str, roles, questions, *, skip_personas: bool = False) -> dict:
    """A structured Three-Amigos consult over a set of open questions: the resolved `panel` (named
    seats, lead first) and the `questions` to take to it. The questions go to the WHOLE panel -
    each amigo weighs in by their lens - rather than auto-assigning a question to one seat, a guess
    the tool has no basis to make. Blank questions are dropped. An empty question list still
    resolves the panel, so a caller can name who WOULD be consulted. Returns
    `{panel, questions, seats, lead}`; `lead` is the first seat (the ceremony's leading lens)."""
    qs = [q for q in (questions or []) if str(q).strip()]
    full = amigo_panel(root, roles, skip_personas=skip_personas)
    # A consult SUMMARY names the seats; it does NOT carry each seat's full charter body (the
    # multi-KB `framing`). refine/triage store and record only the names, so dumping the framing
    # into their `--format json` was dead weight. An agent that actually RUNS the consult resolves
    # the framing itself via `amigo_panel` / `resolve-consult`. So the summary drops it here.
    p = [{k: v for k, v in x.items() if k != "framing"} for x in full]
    return {"panel": p, "questions": qs, "seats": [x["seat"] for x in p],
            "lead": p[0]["seat"] if p else None}


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
    if getattr(args, "format", "text") == "json":
        print(json.dumps({"seat": args.seat, "render": args.render,
                          "card_path": str(card) if card else None,
                          "framing": frame(card, args.seat, args.render)}, indent=2))
        return 0
    if args.path_only:
        print(str(card) if card else "")
        return 0
    print(frame(card, args.seat, args.render))
    return 0


_CONSULT_LINE_RE = re.compile(r"(?m)^>?\s*\*\*Consulted:\*\*.*$")
_CONSULT_SECTION_RE = re.compile(r"(?ms)^## Amigo Consult\b.*?(?=^## |\Z)")


def record_consult(path: Path | str, result: dict, today: str) -> bool:
    """Record on the artefact WHICH amigo seats were consulted and the open questions, so a consult
    leaves an audit trail on the request/Issue itself, not only in stdout. Writes a machine-readable
    `> **Consulted:**` metadata line (named seats + date) and an idempotent `## Amigo Consult`
    section listing the questions and the panel (lead named first). Both are UPDATED IN PLACE on a
    re-run, never duplicated. A no-op (returns False) when there were no open questions - a consult
    with nothing to settle leaves no trace. Uses `lib.sdlc_md` writers, so it honours the same
    atomic-write and Status-anchoring the link writers do."""
    from lib import sdlc_md as _md
    p = Path(path)
    questions = [q for q in (result.get("questions") or []) if str(q).strip()]
    panel = result.get("panel") or []
    if not questions or not panel:
        return False
    # Collapse each question to a single line before rendering: a question carrying an embedded
    # newline + `## ` would otherwise inject a fake heading into the section, which the
    # section-bounded-by-`^## ` regex then splits on - duplicating the injected block on every
    # re-run and breaking idempotency. A question is one line by contract, so this only ever
    # normalises a malformed one.
    questions = [" ".join(str(q).split()) for q in questions]
    seats = ", ".join(x["seat"] for x in panel)
    lead = result.get("lead")
    line = f"> **Consulted:** {seats} ({today})"
    text = p.read_text(encoding="utf-8")
    text = (_CONSULT_LINE_RE.sub(line, text, count=1) if _CONSULT_LINE_RE.search(text)
            else None)
    if text is None:                       # no line yet: anchor it after Status
        _md.insert_after_status(p, line)
        text = p.read_text(encoding="utf-8")
    roster = ", ".join(f"{x['seat']} ({x['role']}{', lead' if x['seat'] == lead else ''})"
                       for x in panel)
    section = (f"## Amigo Consult\n\n"
               f"_Consulted {today}: {roster}. Settle before building._\n\n"
               + "".join(f"- {q}\n" for q in questions))
    if _CONSULT_SECTION_RE.search(text):
        text = _CONSULT_SECTION_RE.sub(section + "\n", text, count=1)
    else:
        text = text.rstrip("\n") + "\n\n" + section + "\n"
    _md.atomic_write(p, text if text.endswith("\n") else text + "\n")
    return True


def cmd_panel(args: argparse.Namespace) -> int:
    roles = {"refine": REFINE_PANEL, "triage": TRIAGE_PANEL}[args.ceremony]
    try:
        result = consult(args.root, roles, args.question or [], skip_personas=args.skip_personas)
    except RenderError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if getattr(args, "format", "text") == "json":
        print(json.dumps(result, indent=2))
        return 0
    named = ", ".join(f"{p['seat']} ({p['role']})" for p in result["panel"])
    lead = result["lead"]
    print(f"{args.ceremony} amigo panel ({lead} leads): {named}")
    if result["questions"]:
        print(f"take these {len(result['questions'])} question(s) to the panel:")
        for q in result["questions"]:
            print(f"  - {q}")
    return 0


def cmd_resolve_consult(args: argparse.Namespace) -> int:
    try:
        card = resolve_consult(args.root, args.role.lower())
    except RenderError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.path_only:
        print(str(card) if card else "")
        return 0
    print(frame(card, args.role.lower(), "review"))
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
    sdlc_md.add_format_arg(r)
    r.set_defaults(func=cmd_resolve)
    c = sub.add_parser("resolve-consult",
                       help="Resolve the seat a consult runs against, by declared role (review render).")
    c.add_argument("--role", required=True, help="the declared seat role to resolve (e.g. engineering, qa, product, ux)")
    c.add_argument("--root", default=".", help="project root")
    c.add_argument("--path-only", action="store_true", help="print the resolved card path, not its body")
    c.set_defaults(func=cmd_resolve_consult)
    pn = sub.add_parser("panel",
                        help="Resolve the Three-Amigos panel for a ceremony (refine/triage) and "
                             "the seats questions go to (lead named first).")
    pn.add_argument("--ceremony", required=True, choices=("refine", "triage"))
    pn.add_argument("--question", action="append", metavar="TEXT",
                    help="an open question for the panel. Repeatable.")
    pn.add_argument("--root", default=".", help="project root")
    pn.add_argument("--skip-personas", action="store_true", help="force the generic path (no framing)")
    sdlc_md.add_format_arg(pn)
    pn.set_defaults(func=cmd_panel)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
