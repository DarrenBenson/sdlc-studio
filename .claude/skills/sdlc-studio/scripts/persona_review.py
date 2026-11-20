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

`brief --card PATH --seat ROLE` frames a review of one card by a seat other than its own: the
seat card to adopt, the standard page, the card, every finding `check` reports for it with its
severity, and the `record` command. It exits 2, printing no brief, when the seat is the card's
own (a seat never reviews its own card) or no card fills the seat.

`record --card PATH --outcome pass|fail --reviewer "NAME (ROLE)" [--run-by NAME] [--rule RULE]`
appends one row to `sdlc-studio/reviews/persona-reviews.md`, writing its header on the first
record: the card, its body hash (`persona_gen.body_hash`, which leaves out the generation stamp
and the reviewed marker), the outcome, the reviewer, the seat read from the reviewer's first
`(role)` group, who ran the review (`--run-by`, else the repository's `git config user.name`),
the date and the rules a FAIL names. The ledger records who asserted a review; it is evidence
of that assertion, not proof the review happened. A PASS on a generated card still carrying its
provisional stamp turns the stamp into the dated reviewed marker `persona_gen.py accept` writes.
It exits 2, writing nothing, for a FAIL naming no rule, a rule the standard does not hold, a
reviewer naming no `(role)` group or a role no seat card declares, no person to name as having
run it, the card's own seat, or a PASS while a rule that blocks still fails on the card.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
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


#: The review ledger: append-only and committed, beside the other review ledgers. Never under
#: `sdlc-studio/personas/`, where every reader of persona cards would read it as one.
LEDGER_REL = Path("sdlc-studio") / "reviews" / "persona-reviews.md"
LEDGER_COLUMNS = ("Card", "Hash", "Outcome", "Reviewer", "Seat", "Run by", "Date", "Rules")
_LEDGER_HEAD = (
    "# Persona Reviews\n\n"
    "One row per review of a persona or seat card against the persona standard, appended by "
    "`persona_review.py record`. Hash is the card's body hash, the card without its generation "
    "stamp or reviewed marker. Run by names who asserted the review: the row is evidence of "
    "that assertion, not proof the review happened.\n\n")
#: The standard a review judges a card against.
STANDARD = Path(__file__).resolve().parent.parent / "best-practices" / "persona.md"
OWN_SEAT = "a seat never reviews its own card"
_ROLE_GROUP_RE = re.compile(r"\([^()]*\)")


class ReviewRefused(ValueError):
    """A brief or a record the review cannot stand behind; the message names the reason."""


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


def _review_card(root: Path, card: Path | str) -> Path:
    """The persona or seat card `card` names, relative to the root or absolute."""
    path = Path(card) if Path(card).is_absolute() else root / card
    if path.resolve() not in {p.resolve() for p in _persona_cards(root) + _seat_cards(root)}:
        raise ReviewRefused(f"{card} is no persona card in sdlc-studio/personas/ or seat card "
                            "in sdlc-studio/personas/seats/")
    return path.resolve()


def _own_seat(root: Path, card: Path) -> str | None:
    """The seat a seat card is the charter of, by its declared role; a persona card has none."""
    import persona_resolve  # noqa: PLC0415 - sibling; the one declared-role reader
    seats = (root / "sdlc-studio" / "personas" / "seats").resolve()
    return persona_resolve.card_role(card) if card.parent == seats else None


def _refuse_own_seat(root: Path, card: Path, seat: str) -> None:
    own = _own_seat(root, card)
    if own is not None and own == seat:
        raise ReviewRefused(f"{OWN_SEAT}: {_rel(str(card), root)} is the {own} seat's card; "
                            "brief or record any other seat")


def brief(root: Path | str, card: Path | str, seat: str) -> str:
    """The brief that frames `seat` to review `card` against the standard: the seat card to
    adopt, the standard page, the card, each finding `check` reports for it with its severity,
    and the `record` command. Raises ReviewRefused for the card's own seat, and
    persona_resolve.UnknownSeat (a ValueError) for a seat no card fills."""
    import persona_resolve  # noqa: PLC0415 - sibling; the resolver every review brief calls
    root = Path(root).resolve()
    path = _review_card(root, card)
    seat = seat.strip().lower()
    _refuse_own_seat(root, path, seat)
    adopt = persona_resolve.review_card(root, seat)
    reviewer = f"{persona_resolve.seat_name(adopt, seat)} ({seat})"
    rel = _rel(str(path), root)
    lines = [f"Persona review: the {seat} seat reviews {rel} against the persona standard.", "",
             f"Adopt the {seat} seat card, its review render: {_rel(str(adopt), root)}",
             f"The standard: {STANDARD} - judge the card under each heading, answering the "
             "questions each one asks that no rule can.",
             f"Card under review: {rel}", "",
             "Its findings from `persona_review.py check`, the floor your judgement starts from:"]
    lines += [f"  {f['severity']:<8} {f['rule']} ({f['heading']}): {f['message']}"
              for f in check(root, path)] or ["  none"]
    lines += ["", "A PASS is refused while a finding that blocks stands; a FAIL names each rule "
              "it failed with --rule. Record the verdict:",
              f"  python3 {_rel(str(Path(__file__).resolve()), root)} record --card {rel} "
              f"--outcome pass|fail --reviewer \"{reviewer}\" [--rule <rule> ...] "
              "[--run-by \"<who ran the review>\"]"]
    return "\n".join(lines)


def _git_user(root: Path) -> str | None:
    """The repository's `git config user.name`, or None when git sets none."""
    try:
        done = subprocess.run(["git", "-C", str(root), "config", "user.name"],
                              capture_output=True, text=True, timeout=30, check=False)
    except (OSError, subprocess.SubprocessError):
        return None
    return (done.stdout.strip() or None) if done.returncode == 0 else None


def record(root: Path | str, card: Path | str, outcome: str, reviewer: str,
           run_by: str | None = None, rules: list[str] | tuple[str, ...] = (),
           today: str | None = None) -> dict:
    """Append one review of `card` to the ledger and return the row as a dict. Every refusal
    raises ReviewRefused before anything is written. A PASS clears a generated card's
    provisional stamp (`persona_gen.accept`); the row's `accepted` says whether it did."""
    import critic  # noqa: PLC0415 - sibling; the one reader of a recorded seat
    import persona_gen  # noqa: PLC0415 - sibling; the one card hash and the accept path
    import persona_resolve  # noqa: PLC0415
    root = Path(root).resolve()
    path = _review_card(root, card)
    rel = _rel(str(path), root)
    outcome = outcome.strip().upper()
    if outcome not in ("PASS", "FAIL"):
        raise ReviewRefused(f"--outcome is pass or fail, not {outcome.lower()!r}")
    rules = list(dict.fromkeys(r.strip() for r in rules if r.strip()))
    unknown = [r for r in rules if r not in RULES]
    if unknown:
        raise ReviewRefused("; ".join(f"{r} is no rule the standard holds" for r in unknown)
                            + f" (best-practices/persona.md: {', '.join(RULES)})")
    if outcome == "FAIL" and not rules:
        raise ReviewRefused("a FAIL names the rule it failed: pass --rule <rule> for each")
    seat = critic.recorded_seat(reviewer)
    if seat is None:
        raise ReviewRefused(f"the reviewer {reviewer!r} names no (role) group: write it as "
                            "\"Name (role)\", the seat that reviewed")
    roster = persona_resolve.seat_roster(root)
    if seat not in roster:
        raise ReviewRefused(f"no seat card declares the role {seat!r} (seats: "
                            f"{', '.join(roster)})")
    _refuse_own_seat(root, path, seat)
    who = (run_by if run_by is not None else _git_user(root) or "").strip()
    if not who:
        raise ReviewRefused("no --run-by and no git user.name to default to: name the person "
                            "who ran this review with --run-by" if run_by is None else
                            "--run-by names no one: name the person who ran this review")
    if not _ROLE_GROUP_RE.sub("", who).strip():
        raise ReviewRefused(f"--run-by names a seat, not a person ({who!r}): name the person "
                            "who ran this review")
    if outcome == "PASS":
        held = sorted({f["rule"] for f in check(root, path) if f["severity"] == BLOCKS})
        if held:
            raise ReviewRefused(f"{', '.join(held)} {'blocks' if len(held) == 1 else 'block'} "
                                f"on {rel}: a PASS cannot stand while a blocking rule fails; "
                                "fix the card, or record a FAIL naming the rule")
    row = {"card": rel, "hash": persona_gen.body_hash(path.read_text(encoding="utf-8")),
           "outcome": outcome, "reviewer": reviewer.strip(), "seat": seat, "run_by": who,
           "date": today or sdlc_md.now_date(), "rules": ", ".join(rules) or "-"}
    try:
        line = sdlc_md.join_row(list(row.values()))
    except ValueError as exc:
        raise ReviewRefused(str(exc)) from None
    ledger = root / LEDGER_REL
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with sdlc_md.allocation_lock(root):
        text = ledger.read_text(encoding="utf-8") if ledger.exists() else (
            _LEDGER_HEAD + sdlc_md.join_row(list(LEDGER_COLUMNS)) + "\n"
            + sdlc_md.join_row(["---"] * len(LEDGER_COLUMNS)) + "\n")
        sdlc_md.atomic_write(ledger, text + ("" if text.endswith("\n") else "\n") + line + "\n")
    row["accepted"] = outcome == "PASS" and persona_gen.accept(path, row["date"])
    return row


def cmd_brief(args: argparse.Namespace) -> int:
    """Print the review brief; exit 2 for the card's own seat or a seat no card fills."""
    try:
        print(brief(args.root, args.card, args.seat))
    except ValueError as exc:
        print(f"persona_review brief refused: {exc}", file=sys.stderr)
        return 2
    return 0


def cmd_record(args: argparse.Namespace) -> int:
    """Append the review to the ledger; exit 2, writing nothing, on a refusal."""
    try:
        row = record(args.root, args.card, args.outcome, args.reviewer, args.run_by,
                     args.rule or ())
    except ValueError as exc:
        print(f"persona_review record refused: {exc}", file=sys.stderr)
        return 2
    print(f"recorded {row['outcome']} for {row['card']} by {row['reviewer']}, run by "
          f"{row['run_by']} (hash {row['hash']}) in {LEDGER_REL}")
    if row["accepted"]:
        print(f"cleared the provisional stamp on {row['card']}: it carries the reviewed marker")
    return 0


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
    b = sub.add_parser("brief", help="Brief a seat other than the card's own to review it "
                                     "against the standard, with the card's findings.")
    b.add_argument("--root", default=".", help="Repo root (default: .)")
    b.add_argument("--card", required=True, help="The card to review (a path, relative to "
                                                 "the root)")
    b.add_argument("--seat", required=True, help="The reviewing seat's role; never the card's "
                                                 "own")
    b.set_defaults(func=cmd_brief)
    r = sub.add_parser("record", help="Append a review's outcome to sdlc-studio/reviews/"
                                      "persona-reviews.md against the card's body hash.")
    r.add_argument("--root", default=".", help="Repo root (default: .)")
    r.add_argument("--card", required=True, help="The card reviewed (a path, relative to the "
                                                 "root)")
    r.add_argument("--outcome", required=True, choices=("pass", "fail"))
    r.add_argument("--reviewer", required=True, help='"Name (role)": the seat is the first '
                                                     "(role) group")
    r.add_argument("--run-by", help="The person who ran the review (default: git config "
                                    "user.name)")
    r.add_argument("--rule", action="append", help="A rule the card failed (repeatable; a "
                                                   "FAIL names at least one)")
    r.set_defaults(func=cmd_record)
    sdlc_md.add_global_root(p)
    return p


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and dispatch to the chosen subcommand."""
    args = build_parser().parse_args(argv)
    args.root = str(sdlc_md.resolve_root(args))
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
