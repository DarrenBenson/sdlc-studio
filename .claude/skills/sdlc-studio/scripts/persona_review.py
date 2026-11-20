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
adds, `persona-evidence` and `persona-registry-role`. A card whose bytes are not UTF-8 is held
outside the table as `card-not-utf8`, which blocks: the validators name it with the line of its
first such byte and read it with each such byte replaced, so it never stops every other card
being judged. It exits 1 when any printed finding blocks, 0 when every one is
reported or none is, and 2 when `--card` names no card. Other scripts call
`check(root, card=None)`, which returns the same findings as dicts carrying `rule`,
`severity`, `heading`, `file` and `message`. Read-only.

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

`blocking(root, card)` is what holds a project card from framing a brief: each blocking rule it
breaks, and its latest ledger row when that row is a FAIL, whatever the card's bytes are now,
until a later PASS. `persona_resolve` calls it for every project seat card it resolves and
raises `refusal`'s text, which names the card, each rule and `remedy`, the one command to run
next (for a card that is not UTF-8, saving it as UTF-8 and the `check` that judges it). `review_owed` names a card with no review row, or one changed since its PASS: it still
frames the brief. `standard_mode` reads `personas.standard` from the project's config: `block`,
the default, refuses such a card; `report` frames it, and `report_line` is the one stderr line
naming it, its rules and the remedy. Any other value is read as `block`, with one stderr line
naming the key and its two values. `project_upgrade.py --apply` sets `report` for a project that
holds its own cards and has no value.

`owed [--format text|json]` names each card owed a review, one `persona review owed:` line
each, ending in the `remedy` line that briefs its review: never reviewed, changed since its PASS
(by the recorded body hash, never the file's time or git history), or a PASS dated before the
commit date of the newest release tag (by the commit's date, not the tag's name; compared by
day). A FAIL is not owed: `blocking` holds the card. It exits 0, owed or not: an owed review is
reported, never refused. `check` reports the same cards under `persona-review-owed`,
`release_cut.py changelog-cut` prints each line, and `sprint.py plan` prints only their count.
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
    "persona-review-owed": ("Freshness", REPORTED),
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

#: The hold on a card whose bytes are not UTF-8, which `validate.read_card` names. No rule of the
#: table can judge such a card, so like a FAIL review it holds the card from outside the table,
#: under Format, and it always blocks.
NOT_UTF8 = "card-not-utf8"

_SKIP = {"index.md", "readme.md", "consult-guide.md"}
_EVIDENCE_HEAD_RE = re.compile(r"^##\s+Evidence\b.*$", re.M)
_NEXT_HEAD_RE = re.compile(r"^#{1,2}\s", re.M)
_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
_DECISION_RE = re.compile(r"\bD\d{4}\b")
_PROJECT_LESSON_RE = re.compile(r"\bL-\d{4}\b")
#: A release tag: a version, `v` optional (`v6.4.0`, `6.4.0`, `v6.5.0-rc1`).
_RELEASE_TAG_RE = re.compile(r"^v?\d+\.\d+")


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
#: How the standard holds a project's own cards: `block` (the default) refuses a card that breaks
#: a blocking rule or whose latest review failed; `report` frames it and names it on stderr.
STANDARD_KEY = "personas.standard"
STANDARD_MODES = ("block", "report")
#: The standard a review judges a card against.
STANDARD = Path(__file__).resolve().parent.parent / "best-practices" / "persona.md"
OWN_SEAT = "a seat never reviews its own card"
_ROLE_GROUP_RE = re.compile(r"\([^()]*\)")


class ReviewRefused(ValueError):
    """A brief or a record the review cannot stand behind; the message names the reason."""


def _classify(rule: str) -> tuple[str, str]:
    """`(heading, severity)` for a rule: the table's row, the not-UTF-8 hold's own (Format,
    blocks), or unclassified and reported for a rule the table does not hold."""
    return ("Format", BLOCKS) if rule == NOT_UTF8 else RULES.get(rule, (UNCLASSIFIED, REPORTED))


def severity_of(rule: str) -> str:
    """`blocks` or `reported` for a rule; a rule the table does not hold is reported, and the
    not-UTF-8 hold blocks."""
    return _classify(rule)[1]


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


def check(root: Path | str, card: Path | str | None = None, *,
          evidence: bool = True, owed: bool = False) -> list[dict]:
    """Every finding against the standard, one dict per finding: `rule`, `severity` (blocks or
    reported), `heading`, `file`, `message`, and `line` or `goal` where the check names one.
    With `card`, only that card's findings; the cast-level ones sit on no card. `evidence=False`
    leaves out the `persona-evidence` rule, which reads the lessons and the artefact corpus;
    `owed=True` adds `persona-review-owed`, which reads the ledger and git's tags (the `check`
    command and a review brief ask for it)."""
    import validate  # noqa: PLC0415 - deferred: validate imports this module for its labels
    root = Path(root).resolve()
    stakeholders = root / "sdlc-studio" / "personas" / "stakeholders"
    personas = _persona_cards(root)
    raw = [*validate.check_personas(root), *validate.check_seats(root),
           *(_evidence_findings(root, personas + _seat_cards(root)) if evidence else ()),
           *_registry_findings(root, personas),
           *(_owed_findings(root) if owed else ())]
    out: list[dict] = []
    for f in raw:
        path = Path(f["file"]).resolve()
        if f["rule"] in OUTSIDE or stakeholders in path.parents:
            continue
        if card is not None and path != Path(card).resolve():
            continue
        heading, severity = _classify(f["rule"])
        row = {"rule": f["rule"], "severity": severity, "heading": heading,
               "file": str(path), "message": f["message"]}
        row.update({k: f[k] for k in ("line", "goal") if k in f})
        out.append(row)
    return sorted(out, key=lambda r: (r["file"], r["rule"]))


def blocking_findings(root: Path | str) -> list[dict]:
    """`check` of every card with only what `blocking` reads: a rule `reported` that is costly
    to read (the evidence corpus, the ledger and tags) is left out."""
    return check(root, evidence=blocks("persona-evidence"), owed=blocks("persona-review-owed"))


def held_cards(root: Path | str, cards: list[Path | str] | None = None,
               findings: list[dict] | None = None) -> dict[Path, list[dict]]:
    """`blocking` for many cards from one `check`: `{card path: what holds it}` for each persona
    and seat card in the project, or each of `cards`, leaving out every card nothing holds.
    `findings` passes a `check` already read, so a caller judging cards twice reads it once."""
    root = Path(root).resolve()
    if findings is None:
        findings = blocking_findings(root)
    paths = ([Path(c).resolve() for c in cards] if cards is not None
             else [p.resolve() for p in _persona_cards(root) + _seat_cards(root)])
    out: dict[Path, list[dict]] = {}
    for path in dict.fromkeys(paths):
        held = _held(root, path, findings)
        if held:
            out[path] = held
    return out


def release_tag(root: Path | str) -> tuple[str, str] | None:
    """The newest release tag by the date of the commit it points at, as `(tag, that commit's
    date as YYYY-MM-DD)`; None with no release tag, or no git to ask. An annotated tag is read
    through to its commit, so the day it was tagged does not count."""
    fmt = ("%(refname:short)%09%(*committerdate:unix)%09%(*committerdate:short)"
           "%09%(committerdate:unix)%09%(committerdate:short)")
    try:
        done = subprocess.run(["git", "-C", str(root), "for-each-ref", f"--format={fmt}",
                               "refs/tags"], capture_output=True, text=True, timeout=30,
                              check=False)
    except (OSError, subprocess.SubprocessError):
        return None
    best: tuple[int, str, str] | None = None
    for row in done.stdout.splitlines() if done.returncode == 0 else ():
        parts = row.split("\t")
        if len(parts) != 5 or not _RELEASE_TAG_RE.match(parts[0]):
            continue
        when, day = (parts[1], parts[2]) if parts[1] else (parts[3], parts[4])
        if when.isdigit() and (best is None or int(when) > best[0]):
            best = (int(when), parts[0], day)
    return (best[1], best[2]) if best else None


def owed(root: Path | str, findings: list[dict] | None = None) -> list[dict]:
    """Each persona and seat card owed a review, in card order: `{card, why, remedy, line}`,
    `card` relative to the root, `remedy` the `remedy` line briefing its review and `line` the
    one `persona review owed:` line naming it and ending in that remedy. Owed when it has no
    review row, when its latest review is a PASS of other bytes (the body hash, so the reviewed
    marker is no change and a reverted edit is none), or when that PASS is dated before the
    newest release tag's commit, compared by day. A FAIL is held by `blocking`, not owed.
    `findings` passes a `blocking_findings` already read, so the remedies read none again."""
    root = Path(root).resolve()
    rows = _owed_why(root)
    if rows and findings is None:
        findings = blocking_findings(root)
    out: list[dict] = []
    for path, rel, why in rows:
        run = remedy(root, path, findings)
        out.append({"card": rel, "why": why, "remedy": run,
                    "line": f"persona review owed: {rel} - {why}. {run}"})
    return out


def _owed_why(root: Path) -> list[tuple[Path, str, str]]:
    """`(card path, card relative to the root, why it is owed)` for each card `owed` names."""
    import persona_gen  # noqa: PLC0415 - sibling; the one card hash
    latest = {r["card"]: r for r in ledger_rows(root)}
    tag = release_tag(root)
    out: list[tuple[Path, str, str]] = []
    for path in _persona_cards(root) + _seat_cards(root):
        rel = _rel(str(path.resolve()), root)
        last = latest.get(rel)
        if last is None:
            why = "never reviewed"
        elif last["outcome"].upper() != "PASS":
            continue
        elif last["hash"] != persona_gen.body_hash(sdlc_md.read_text_safe(path)):
            why = f"changed since its review of {last['date']}"
        elif tag is not None and last["date"] < tag[1]:
            why = (f"not reviewed since {tag[0]}: its PASS of {last['date']} is dated before the "
                   f"tag commit's date, {tag[1]} (compared by day: the PASS date against the tag "
                   "commit's date)")
        else:
            continue
        out.append((path.resolve(), rel, why))
    return out


def _owed_findings(root: Path) -> list[dict]:
    """`persona-review-owed`: each card `owed` names."""
    return [{"rule": "persona-review-owed", "file": str(path), "message": why}
            for path, _rel_path, why in _owed_why(root)]


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
    and the `record` command. Raises ReviewRefused for the card's own seat,
    persona_resolve.UnknownSeat (a ValueError) for a seat no card fills, and
    persona_resolve.StandardRefused (a RenderError) when the persona standard holds the
    reviewing seat's own card."""
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
              for f in check(root, path, owed=True)] or ["  none"]
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
    import validate  # noqa: PLC0415 - deferred: validate imports this module for its labels
    root = Path(root).resolve()
    path = _review_card(root, card)
    rel = _rel(str(path), root)
    unreadable = validate.read_card(path, "error")[1]
    if unreadable:
        raise ReviewRefused(f"{rel} cannot be reviewed as written: {unreadable['message']}, "
                            "then record its review")
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


def ledger_rows(root: Path | str) -> list[dict]:
    """The review ledger's rows in the order they were appended, each keyed by its column
    lower-cased (`card`, `hash`, `outcome`, `reviewer`, `seat`, `run by`, `date`, `rules`);
    none when there is no ledger."""
    text = sdlc_md.read_text_safe(Path(root) / LEDGER_REL)
    keys = [c.lower() for c in LEDGER_COLUMNS]
    rows = [sdlc_md.table_cells(ln) for ln in text.splitlines()]
    return [dict(zip(keys, r)) for r in rows
            if r and len(r) == len(keys) and r[0] != LEDGER_COLUMNS[0]]


def latest_review(root: Path | str, card: Path | str) -> dict | None:
    """The card's last row in the ledger, whatever hash it carries, or None when it has none."""
    root = Path(root).resolve()
    rel = _rel(str(Path(card).resolve()), root)
    return next((r for r in reversed(ledger_rows(root)) if r["card"] == rel), None)


def blocking(root: Path | str, card: Path | str) -> list[dict]:
    """What holds `card` from framing a brief, as `check` rows: each rule that blocks and fails
    on it, then its latest review when that review is a FAIL, held whatever the card's bytes are
    now until a later PASS. Empty when the card may frame one."""
    root, path = Path(root).resolve(), Path(card).resolve()
    return _held(root, path, check(root, path, evidence=blocks("persona-evidence")))


def _held(root: Path, path: Path, findings: list[dict]) -> list[dict]:
    """`blocking` over findings already read: those on `path` that block, then its FAIL."""
    held = [f for f in findings if f["severity"] == BLOCKS and Path(f["file"]) == path]
    last = latest_review(root, path)
    if last is not None and last["outcome"].upper() == "FAIL":
        held.append({"rule": last["rules"], "severity": BLOCKS, "heading": "Review",
                     "file": str(path),
                     "message": f"its latest review is a FAIL by {last['reviewer']} on "
                                f"{last['date']}, run by {last['run by']}; a PASS recorded "
                                "for the card as it stands lifts it"})
    return held


def remedy(root: Path | str, card: Path | str, findings: list[dict] | None = None) -> str:
    """The line naming what to run next for `card`: `Run next:` and the command briefing a
    seat other than its own to review it, the first in the roster whose own card nothing holds.
    When every other seat's card is held too, no brief can run, so the line says so and names
    the way out instead of a command that would be refused. A card that is not UTF-8 is saved
    as UTF-8 first, so its line names that and the `check` that then judges it. `findings`
    passes a `blocking_findings` already read."""
    import persona_resolve  # noqa: PLC0415 - sibling; the seat roster
    root, path = Path(root).resolve(), Path(card).resolve()
    script = _rel(str(Path(__file__).resolve()), root)
    rel = _rel(str(path), root)
    if findings is None:
        findings = check(root, evidence=blocks("persona-evidence"))
    if any(f["rule"] == NOT_UTF8 and Path(f["file"]) == path for f in findings):
        return f"Run next: save {rel} as UTF-8, then python3 {script} check --card {rel}"
    own = _own_seat(root, path)
    others = [s for s in persona_resolve.seat_roster(root) if s != own]
    roles = {p.resolve(): persona_resolve.card_role(p) for p in _seat_cards(root)}

    def clear(seat: str) -> bool:
        return all(not _held(root, p, findings) for p, role in roles.items() if role == seat)
    seat = next((s for s in others if clear(s)), None)
    if seat is None:
        held = " and ".join([", ".join(others[:-1]), others[-1]] if len(others) > 1 else others)
        return (f"No other seat is clear to review it: the {held} seat cards are each held "
                "too. Lift one first (fix what breaks the standard on it, or record a PASS for "
                f"it with `python3 {script} record` where a FAIL holds it), then brief that "
                f"seat on {rel}.")
    return f"Run next: python3 {script} brief --card {rel} --seat {seat}"


def refusal(root: Path | str, card: Path | str, held: list[dict]) -> str:
    """The refusal for a card `blocking` holds: the card, each rule with its message, and the
    `remedy` line. Names no other card, since none stands in for it."""
    root = Path(root).resolve()
    rel = _rel(str(Path(card).resolve()), root)
    lines = [f"{rel} breaks the persona standard (best-practices/persona.md), so it frames "
             "no brief and no other card stands in for it:"]
    lines += [f"  {f['rule']} ({f['heading']}): {f['message']}" for f in held]
    lines += [remedy(root, card)]
    return "\n".join(lines)


def standard_mode(root: Path | str) -> str:
    """`personas.standard` from the project's config: `block` when it is unset, `report` or
    `block` as set, and `block` for any other value, printing one stderr line naming the key and
    its two values, so a mistyped value never turns the refusal off."""
    value = sdlc_md.project_override(root, STANDARD_KEY)
    if value is None:
        return "block"
    mode = str(value).strip().lower()
    if mode in STANDARD_MODES:
        return mode
    print(f"{STANDARD_KEY} is {value!r}, which is neither block nor report, so it is read as "
          "block", file=sys.stderr)
    return "block"


def report_line(root: Path | str, card: Path | str, held: list[dict]) -> str:
    """The one stderr line naming a card `blocking` holds while `personas.standard` is
    `report`: the card, each rule with its message, and the `remedy` line."""
    root = Path(root).resolve()
    rel = _rel(str(Path(card).resolve()), root)
    rules = "; ".join(f"{f['rule']}: {' '.join(f['message'].split())}" for f in held)
    return (f"persona card blocked (report mode): {rel} breaks the persona standard - {rules}. "
            f"It frames the brief while {STANDARD_KEY} is report; set it to block to refuse it. "
            f"{remedy(root, card)}")


def review_owed(root: Path | str, card: Path | str) -> str | None:
    """One line naming `card` as owed its persona review, when it has no review row or has
    changed since its PASS; None when a PASS covers it as it stands, or a FAIL holds it."""
    import persona_gen  # noqa: PLC0415 - sibling; the one card hash
    root, path = Path(root).resolve(), Path(card).resolve()
    last = latest_review(root, path)
    if last is None:
        why = "has no review recorded"
    elif last["outcome"].upper() != "PASS":
        return None
    elif last["hash"] != persona_gen.body_hash(path.read_text(encoding="utf-8")):
        why = f"has changed since its PASS on {last['date']}"
    else:
        return None
    return (f"persona review owed: {_rel(str(path), root)} {why} in {LEDGER_REL}; it frames "
            f"the brief meanwhile. {remedy(root, path)}")


def cmd_brief(args: argparse.Namespace) -> int:
    """Print the review brief; exit 2 for the card's own seat, a seat no card fills, or a
    reviewing seat whose own card the persona standard holds (its refusal printed, with the
    line naming what to run next for that card)."""
    import persona_resolve  # noqa: PLC0415 - sibling; its RenderError is the standard's refusal
    try:
        print(brief(args.root, args.card, args.seat))
    except (ValueError, persona_resolve.RenderError) as exc:
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
    findings = check(root, card, owed=True)
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


def cmd_owed(args: argparse.Namespace) -> int:
    """Print each card owed a review; exit 0 either way, since an owed review is reported."""
    found = owed(args.root)
    if args.format == "json":
        print(json.dumps({"owed": found, "tag": release_tag(args.root)}, indent=2))
        return 0
    for o in found:
        print(o["line"])
    print(f"persona reviews owed: {len(found)} (reported, never refused; each line ends in the "
          "command that briefs its review)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Construct the argparse parser for the check, brief, record and owed subcommands."""
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
    o = sub.add_parser("owed", help="Name each card owed a review: never reviewed, changed "
                                    "since its PASS, or not reviewed since the newest release "
                                    "tag (by day); exits 0.")
    o.add_argument("--root", default=".", help="Repo root (default: .)")
    o.add_argument("--format", choices=("text", "json"), default="text")
    o.set_defaults(func=cmd_owed)
    sdlc_md.add_global_root(p)
    return p


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and dispatch to the chosen subcommand."""
    args = build_parser().parse_args(argv)
    args.root = str(sdlc_md.resolve_root(args))
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
