#!/usr/bin/env python3
"""persona_review.py - hold every persona and seat card to the persona standard.

`best-practices/persona.md` is the standard: seven headings, each naming the rules that check
it and the questions the reviewing seat answers that no rule can. `RULES` below is the one
table behind it: each rule's standard heading and whether it `blocks` or is `reported`. A rule
blocks when it is card-level, deterministic and its failure makes the card mislead a brief;
every other rule is reported. `validate.py seats` and `validate.py personas` read their
`blocks resolve` label from this table and keep their own severity words and exit codes.

`check [--card PATH] [--format text|json]` reports each card under `sdlc-studio/personas/`
(design personas) and `sdlc-studio/personas/seats/` (review seats) against every rule: the
findings of `validate.check_personas` and `validate.check_seats`, plus the two this script
adds, `persona-evidence` and `persona-registry-role`. It exits 1 when any printed finding
blocks, 0 when every one is reported or none is, and 2 when `--card` names no card. Other
scripts call `check(root, card=None)`, which returns the same findings as dicts carrying
`rule`, `severity`, `heading`, `file` and `message`. Read-only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402

BLOCKS = "blocks"
REPORTED = "reported"

#: The standard's one table: rule -> (the heading of `best-practices/persona.md` it checks,
#: blocks or reported). The page lists each rule under its heading with this severity, and the
#: rule definitions live in reference-persona.md's rule table.
RULES: dict[str, tuple[str, str]] = {
    "persona-cast-role": ("Format", REPORTED),
    "persona-section": ("Format", REPORTED),
    "seat-unreadable": ("Format", REPORTED),
    "seat-no-role": ("Format", REPORTED),
    "seat-unknown-role": ("Format", BLOCKS),
    "seat-no-review-render": ("Format", BLOCKS),
    "seat-demographic-fluff": ("Identity", BLOCKS),
    "persona-evidence": ("Evidence", REPORTED),
    "persona-goal-verify": ("Testable goals", REPORTED),
    "persona-goal-scope": ("Testable goals", REPORTED),
    "persona-registry-role": ("Consistency with the cast", BLOCKS),
    "seat-persona-unknown": ("Consistency with the cast", BLOCKS),
    "seat-persona-role": ("Consistency with the cast", BLOCKS),
    "persona-one-primary": ("Consistency with the cast", REPORTED),
    "seat-duplicate-role": ("Consistency with the cast", REPORTED),
    "seat-cast-size": ("Consistency with the cast", REPORTED),
    "seat-core-missing": ("Consistency with the cast", REPORTED),
    "seat-malformed-stamp": ("Freshness", REPORTED),
}

#: Rules the validators mint that judge no persona or seat card's content, so `check` never
#: prints them: where the files sit, and the generation flow's `--require-stamp` floor.
OUTSIDE: dict[str, str] = {
    "persona-layout": "where persona files sit, not what a card says",
    "persona-legacy": "the legacy single-file layout, not a card",
    "seat-no-stamp": "the generation flow's --require-stamp floor",
    "seat-require-miss": "the generation flow's --require-stamp floor",
}

#: The heading a rule the table does not hold is printed under, so a rule a validator gains
#: with no row here is seen rather than dropped.
UNCLASSIFIED = "unclassified"

_SKIP = {"index.md", "readme.md", "consult-guide.md"}
_EVIDENCE_HEAD_RE = re.compile(r"^##\s+Evidence\b.*$", re.M)
_NEXT_HEAD_RE = re.compile(r"^#{1,2}\s", re.M)
_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
_DECISION_RE = re.compile(r"\bD\d{4}\b")
_PROJECT_LESSON_RE = re.compile(r"\bL-\d{4}\b")


def severity_of(rule: str) -> str:
    """`blocks` or `reported` for a rule; a rule the table does not hold is reported."""
    return RULES.get(rule, (UNCLASSIFIED, REPORTED))[1]


def blocks(rule: str) -> bool:
    """Whether a finding of this rule blocks: the one answer every reader of the table uses."""
    return severity_of(rule) == BLOCKS


def _persona_cards(root: Path) -> list[Path]:
    pdir = root / "sdlc-studio" / "personas"
    return [p for p in sorted(pdir.glob("*.md")) if p.is_file()
            and p.name.lower() not in _SKIP and not p.name.startswith("_")] if pdir.is_dir() else []


def _seat_cards(root: Path) -> list[Path]:
    sdir = root / "sdlc-studio" / "personas" / "seats"
    return [p for p in sorted(sdir.glob("*.md")) if p.is_file()] if sdir.is_dir() else []


def _card_name(text: str) -> str | None:
    m = re.search(r"^#\s+(.+?)\s*$", text, re.M)
    return m.group(1).split(" - ")[0].strip() if m and "{{" not in m.group(1) else None


def evidence_ids(text: str) -> list[str] | None:
    """The ids the card's `## Evidence` section cites, in order, or None when it has none.
    HTML comments are not read, so a template's example cites nothing."""
    head = _EVIDENCE_HEAD_RE.search(text)
    if head is None:
        return None
    rest = text[head.end():]
    nxt = _NEXT_HEAD_RE.search(rest)
    section = _COMMENT_RE.sub("", rest[:nxt.start()] if nxt else rest)
    found = [m.group(1) for m in sdlc_md.CITED_ID_RE.finditer(section)]
    found += [m.group(0) for m in sdlc_md.ANY_ID_SEARCH_RE.finditer(section)]
    found += _DECISION_RE.findall(section) + _PROJECT_LESSON_RE.findall(section)
    return sorted(dict.fromkeys(found), key=section.find)


def _resolver(root: Path):
    """A function telling whether an id resolves: a lesson in the skill's registry or the
    project's, else whatever `persona_memory.resolves` accepts as a learning's evidence (an
    artefact on disk, a decisions row)."""
    import lessons  # noqa: PLC0415 - deferred: only the evidence rule reads them
    import persona_memory  # noqa: PLC0415
    skill = {p.name.split("-", 1)[0].removesuffix(".md")
             for p in lessons.SKILL_LESSONS_DIR.glob("LL*.md")}
    project = set(_PROJECT_LESSON_RE.findall(
        sdlc_md.read_text_safe(root / lessons.DEFAULT_PROJECT_FILE)))

    def resolves(rec_id: str) -> bool:
        if re.fullmatch(r"LL\d{4}", rec_id):
            return rec_id in skill
        if _PROJECT_LESSON_RE.fullmatch(rec_id):
            return rec_id in project
        return persona_memory.resolves(root, rec_id)
    return resolves


def _evidence_findings(root: Path, cards: list[Path]) -> list[dict]:
    """`persona-evidence`: a card whose Evidence section is missing, cites no id, or cites only
    ids that resolve to nothing."""
    resolves = _resolver(root)
    out: list[dict] = []
    for p in cards:
        ids = evidence_ids(sdlc_md.read_text_safe(p))
        if ids is None:
            message = ("no `## Evidence` section - cite the ids (an artefact, a decision, a "
                       "lesson) that ground this card")
        elif not ids:
            message = "the Evidence section cites no id - a heading alone grounds nothing"
        elif not any(resolves(i) for i in ids):
            message = ("the Evidence section cites only ids that resolve to nothing: "
                       + ", ".join(ids))
        else:
            continue
        out.append({"rule": "persona-evidence", "file": str(p), "message": message})
    return out


def _registry_findings(root: Path, cards: list[Path]) -> list[dict]:
    """`persona-registry-role`: a card whose Cast role is not the role `personas/index.md`
    declares for that persona. Silent when there is no registry to read."""
    import validate  # noqa: PLC0415 - deferred: validate reads this table back
    reg = sdlc_md.persona_registry(root)
    if not reg.available:
        return []
    out: list[dict] = []
    for p in cards:
        text = sdlc_md.read_text_safe(p)
        role, name = validate._persona_cast_role(text), _card_name(text)
        entry = next((e for e in reg.entries if e.card and Path(e.card) == p.resolve()), None)
        entry = entry or (reg.find(name) if name else None)
        if role is None or entry is None or entry.role == role:
            continue
        who = name or entry.name
        out.append({"rule": "persona-registry-role", "file": str(p),
                    "message": f"{who}'s card gives Cast role {role.capitalize()}, but "
                               f"personas/index.md declares {who} {entry.role.capitalize()}"})
    return out


def check(root: Path | str, card: Path | str | None = None) -> list[dict]:
    """Every finding against the standard, one dict per finding: `rule`, `severity` (blocks or
    reported), `heading`, `file`, `message`, and `line` or `goal` where the check names one.
    With `card`, only that card's findings; the cast-level ones sit on no card."""
    import validate  # noqa: PLC0415 - deferred: validate imports this module for its labels
    root = Path(root).resolve()
    stakeholders = root / "sdlc-studio" / "personas" / "stakeholders"
    personas = _persona_cards(root)
    raw = [*validate.check_personas(root), *validate.check_seats(root),
           *_evidence_findings(root, personas + _seat_cards(root)),
           *_registry_findings(root, personas)]
    out: list[dict] = []
    for f in raw:
        path = Path(f["file"]).resolve()
        if f["rule"] in OUTSIDE or stakeholders in path.parents:
            continue
        if card is not None and path != Path(card).resolve():
            continue
        heading, severity = RULES.get(f["rule"], (UNCLASSIFIED, REPORTED))
        row = {"rule": f["rule"], "severity": severity, "heading": heading,
               "file": str(path), "message": f["message"]}
        row.update({k: f[k] for k in ("line", "goal") if k in f})
        out.append(row)
    return sorted(out, key=lambda r: (r["file"], r["rule"]))


def _rel(path: str, root: Path) -> str:
    try:
        return str(Path(path).relative_to(root))
    except ValueError:
        return path


def cmd_check(args: argparse.Namespace) -> int:
    """Print each card's findings; exit 1 when any blocks."""
    root = Path(args.root)
    card = None
    if args.card:
        card = Path(args.card) if Path(args.card).is_absolute() else root / args.card
        if card.resolve() not in {p.resolve() for p in _persona_cards(root) + _seat_cards(root)}:
            print(f"error: {args.card} is no persona card in sdlc-studio/personas/ or seat card "
                  "in sdlc-studio/personas/seats/", file=sys.stderr)
            return 2
    findings = check(root, card)
    n_blocks = sum(1 for f in findings if f["severity"] == BLOCKS)
    if args.format == "json":
        print(json.dumps({"findings": findings,
                          "summary": {BLOCKS: n_blocks, REPORTED: len(findings) - n_blocks}},
                         indent=2))
    else:
        for f in findings:
            print(f"{f['severity']:<8} {f['rule']} ({f['heading']}) "
                  f"{_rel(f['file'], root)}: {f['message']}")
        print(f"persona standard: blocks={n_blocks} reported={len(findings) - n_blocks} "
              "(best-practices/persona.md)")
    return 1 if n_blocks else 0


def build_parser() -> argparse.ArgumentParser:
    """Construct the argparse parser for the check subcommand."""
    p = argparse.ArgumentParser(prog="persona_review.py",
                                description="Hold persona and seat cards to the persona "
                                            "standard (best-practices/persona.md).")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="Report each persona and seat card against the standard, "
                                     "rule by rule, blocks or reported; exits 1 on a block.")
    c.add_argument("--root", default=".", help="Repo root (default: .)")
    c.add_argument("--card", help="Report this one card (a path, relative to the root)")
    c.add_argument("--format", choices=("text", "json"), default="text")
    c.set_defaults(func=cmd_check)
    sdlc_md.add_global_root(p)
    return p


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and dispatch to the chosen subcommand."""
    args = build_parser().parse_args(argv)
    args.root = str(sdlc_md.resolve_root(args))
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
