#!/usr/bin/env python3
"""SDLC Studio critic-verdict record.

The independent non-author critic judges each unit's diff against the
AC intent. Its verdict used to be ephemeral, so nothing could confirm the critic
actually ran. Here it is a committed, append-only record
(`sdlc-studio/reviews/critic-verdicts.md`), so the conformance gate can require it:
"the critic ran" becomes a deterministic, auditable signal - the cheap part of
the deferred Stop-Hook, with no harness dependency.

Each verdict now stamps both the reviewer and the author (the authoring seat /
delegation id that produced the diff and tests). The conformance gate hard-fails any
unit whose reviewer id equals its author id, or that has no recorded author - a
self-review never clears the Done gate. This independence floor holds for generic
workers too, not only persona-framed ones. Pure stdlib.
"""
from __future__ import annotations

import argparse
import contextlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import run_state, sdlc_md  # noqa: E402

APPROVE, REJECT = "APPROVE", "REJECT"
#: The only words a verdict row may carry. Every writer checks this one tuple.
VERDICTS = (APPROVE, REJECT)
# Visible grandfather marker for units closed before the independence gate existed
# (under the prior risk-scaled policy that permitted light-tier self-review). Stamped
# once by the migration; never produced by the sprint loop. See is_pre_gate.
PRE_GATE = "pre-gate"
# Every verdict is a DELIVERY verdict: the post-implementation critic the conformance
# `critiqued` stage reads. Plan review is retired, and no command records or briefs one; the
# `plan-review` phase survives only as an internal parameter, so the historical plan ledger
# stays readable.
PHASES = ("delivery", "plan-review")
_FILE = {"delivery": "critic-verdicts.md", "plan-review": "plan-review-verdicts.md"}
# Delivery header is byte-identical to the original (a freshly created delivery log must not
# change); the historical plan-review log has its own title and eighth column.
_TABLE = ("| Unit | Verdict | Reviewer | Author | Date | Brief | Tier | Issues |\n"
          "| --- | --- | --- | --- | --- | --- | --- | --- |\n")
#: The review depths. `full` is the adversarial pass - mutations, boundaries, silent-failure
#: paths, claims verified by execution. `light` is the bounded pass a low-risk unit earns.
TIERS = ("full", "light")
#: What an operator's explicit `--tier` records, so their choice is distinguishable from a
#: derived one. A tier nobody chose and a tier somebody chose are different facts about a
#: review, and a record that cannot tell them apart cannot be used to judge the derivation.
EXPLICIT_SUFFIX = " (explicit)"
#: The band-to-tier table, declared ONCE. `route.estimate` bands every unit trivial / low /
#: medium / high / extreme; only the bottom two earn the bounded pass. Measured over this
#: repository's 1,171 stories and bugs the split is 183 light to 988 full, which is what makes
#: this a gate rather than a config key wearing the appearance of one.
BAND_TIER = {"trivial": "light", "low": "light",
             "medium": "full", "high": "full", "extreme": "full"}
#: An unresolvable band tiers FULL. Unknown risk fails towards the deeper review, because the
#: cost of a needless full pass is tokens and the cost of a needless light one is a defect.
UNKNOWN_BAND_TIER = "full"
#: The historical plan-review table's shape. Its eighth cell named the pre-code artefact a plan
#: review judged; nothing writes a kind or reads one now, so the cell is kept only because the
#: file on disk has it.
_PLAN_TABLE = ("| Unit | Verdict | Reviewer | Author | Date | Brief | Kind | Issues |\n"
               "| --- | --- | --- | --- | --- | --- | --- | --- |\n")
_HEADERS = {
    "delivery": (
        "# Critic Verdicts\n\n"
        "> Append-only. The independent non-author critic's verdict per unit.\n"
        "> APPROVE = ready; REJECT = repair before Done. Latest row per unit wins.\n"
        "> Reviewer must differ from Author - a self-review never clears the Done gate.\n\n"
        + _TABLE),
    "plan-review": (
        "# Plan-Review Verdicts\n\n"
        "> Append-only. The independent non-author plan reviewer's verdict per unit -\n"
        "> the pre-implementation AC-vs-spec check. Latest row per unit wins.\n"
        "> Reviewer must differ from the plan author - a self-review never clears the gate.\n\n"
        + _PLAN_TABLE),
}


def _header(phase: str) -> str:
    return _HEADERS[phase]


HEADER = _HEADERS["delivery"]
#: The seven-column shape both logs shared before either grew its eighth column. Still the
#: reader for any row written then - and the row is complete, not damaged: it simply predates
#: the distinction its phase now records.
_COLS = ("unit", "verdict", "reviewer", "author", "date", "brief", "issues")
_DELIVERY_COLS = ("unit", "verdict", "reviewer", "author", "date", "brief", "tier", "issues")
_PLAN_COLS = ("unit", "verdict", "reviewer", "author", "date", "brief", "kind", "issues")
#: Each phase's own eight-column shape. The two logs diverge because they record different
#: facts - a delivery verdict has a review DEPTH, a plan review has an ARTEFACT - and forcing
#: one schema on both would put a meaningless column in each.
_COLS_BY_PHASE = {"delivery": _DELIVERY_COLS, "plan-review": _PLAN_COLS}



#: Written beside a fingerprint in the Brief cell by an earlier `record` when the fingerprint
#: matched no brief the repo could then produce. Nothing writes it now; `_brief_key` still reads
#: a historical row carrying it as unbriefed.
UNMATCHED_MARK = "unmatched"


_REJOINDER_MARK = "\n\n--- RE-REVIEW (rejoinder) ---"


def rejoinder_fingerprint(text: str, phase: str = "delivery") -> str:
    """The fingerprint a rejoinder brief carries: its BASE brief plus its phase, never the prior
    verdict quoted beneath. The base is what identifies the seat and the unit's state at this
    round; the quoted prior is the seat's own earlier words, which the ledger holds as fields
    and no reader could re-render byte for byte - so a fingerprint over the whole text would be
    one no re-review could reproduce."""
    base = text.split(_REJOINDER_MARK, 1)[0]
    return brief_fingerprint(base + f"\n<rejoinder:{phase}>")


def brief_fingerprint(brief_text: str) -> str:
    """A stable short digest of the brief a seat was given.

    Recorded beside a verdict so a hand-written prompt is DETECTABLE rather than assumed absent.
    RUN-01KYX375 measured what that distinction is worth: four hand-written prompts returned
    eight sprawling repo-wide findings, while the same units re-briefed from this tool returned
    one precise finding each with zero pre-existing noise - and nothing in the record told the
    two apart.

    Content-addressed and stable, never clock- or random-seeded: a fingerprint that differs
    between two identical briefs can never be compared, which would make the field decorative.

    The file-history section is left out: it moves when another unit sharing a file lands, so
    digesting it would change the fingerprint between briefing and recording.
    """
    import hashlib  # noqa: PLC0415 - local; only this path needs it
    import reconcile  # noqa: PLC0415 - sibling; the section's renderer owns its shape
    normalised = " ".join(reconcile.strip_file_history(brief_text or "").split())
    if not normalised:
        return ""
    return hashlib.sha256(normalised.encode("utf-8")).hexdigest()[:12]

def verdicts_path(repo_root: Path | str, phase: str = "delivery") -> Path:
    return Path(repo_root) / "sdlc-studio" / "reviews" / _FILE[phase]


#: A run of backticks that opens or closes a code span. NOT a single backtick: markdown
#: pairs a run of N with the next run of exactly N, so a ``double`` span's opener is two.
#: A backslash-escaped backtick is excluded - `\\`` is a literal backtick, needs no partner,
#: and reading it as a delimiter refused values markdown holds perfectly well.
_TICK_RUN = re.compile(r"(?<!\\)`+")
#: An underscore that is not already escaped. The lookbehind is what makes the pass
#: idempotent, and idempotence is not a nicety here: every value that goes back through this
#: function - a re-recorded verdict, a closure quoting a finding - was being escaped again,
#: which is how the repair record came to carry hundreds of doubled escapes.
_BARE_UNDERSCORE = re.compile(r"(?<!\\)_")


def _scan_ticks(text: str) -> tuple[list[tuple[int, int]], list[int]]:
    """The code spans in `text`, and the offset of every backtick run nothing closes.

    Markdown pairs a run of N backticks with the NEXT run of exactly N. The single-backtick
    pattern this replaces could not see that: it read the two backticks opening a ``double``
    span as a complete empty span, so the span's own contents were escaped as prose and the
    identifier came out with backslashes in it - the very corruption this function exists to
    prevent, in the one shape nobody had written a case for.
    """
    runs = [(m.start(), m.end()) for m in _TICK_RUN.finditer(text)]
    spans: list[tuple[int, int]] = []
    paired: set[int] = set()
    i = 0
    while i < len(runs):
        width = runs[i][1] - runs[i][0]
        close = next((j for j in range(i + 1, len(runs))
                      if runs[j][1] - runs[j][0] == width), None)
        if close is None:
            i += 1
            continue
        spans.append((runs[i][0], runs[close][1]))
        paired.update({i, close})
        i = close + 1
    return spans, [runs[i][0] for i in range(len(runs)) if i not in paired]


def _escape_outside_spans(text: str) -> str:
    """Escape underscores in `text`, leaving the interior of every code span alone."""
    out, last = [], 0
    for start, end in _scan_ticks(text)[0]:
        out.append(_BARE_UNDERSCORE.sub(r"\\_", text[last:start]))
        out.append(text[start:end])
        last = end
    out.append(_BARE_UNDERSCORE.sub(r"\\_", text[last:]))
    return "".join(out)


#: How much of the value to quote either side of the stray backtick. A LEADING excerpt was
#: useless: 71% of this repo's review-ledger findings cells run past 120 characters, and in
#: every corpus row this rule refuses, the first 120 characters hold no backtick at all - so
#: the message quoted text that could not be the fault and named a remedy for it.
_EXCERPT_RADIUS = 60


def _excerpt(text: str, at: int) -> str:
    """`text` around offset `at`, elided at both ends, so the quote holds the stray."""
    start, end = max(0, at - _EXCERPT_RADIUS), min(len(text), at + _EXCERPT_RADIUS + 1)
    return ("..." if start else "") + text[start:end] + ("..." if end < len(text) else "")


def _edge_whitespace_span(text: str) -> tuple[int, str, str] | None:
    """The first code span markdownlint's MD038 refuses: its offset, the span, and the edge.

    Every span is judged, not only the first. The interior is read after CommonMark's padding
    rule - one space removed from each end when both ends are a space and the interior is not
    all spaces - because that is what renders, and what MD038 measures. Whatever remains that
    begins or ends in whitespace is refused, a tab included. An all-space interior is admitted:
    MD038 passes it and CommonMark keeps its spaces, so it records what it says.

    Padding the span is no remedy, which is why this is a refusal. One space each side is
    stripped on render, so the edge space is lost; two or more each side still raises MD038.
    """
    for start, end in _scan_ticks(text)[0]:
        width = _TICK_RUN.match(text, start).end() - start
        interior = text[start + width:end - width]
        if not interior.strip(" "):
            continue
        if interior.startswith(" ") and interior.endswith(" "):
            interior = interior[1:-1]
        first, last = interior[:1].isspace(), interior[-1:].isspace()
        if first or last:
            edge = ("leading and trailing edges" if first and last
                    else "leading edge" if first else "trailing edge")
            return start, text[start:end], edge
    return None


def _clean(value: str) -> str:
    """A free-text value as a ledger cell: escaped for its CONTEXT, and refused if unwritable.

    Four rules, and each was learned from a blocked commit:

    The underscore escape applies OUTSIDE code spans only. Markdown does not process a
    backslash inside a span, so escaping there wrote the backslash into the record - every
    identifier a reviewer named came out wrong in the three files this project uses as its
    account of what review found.

    The pipe and newline substitutions apply EVERYWHERE, span interiors included. These rows
    are built by f-string rather than by a row joiner, so this function is the only thing
    standing between a reviewer's piped shell command and a forged column.

    An ODD number of backticks is REFUSED rather than balanced. An unbalanced span turns the
    rest of the row into code and markdownlint then refuses the whole file, so the value cannot
    be written as it stands - but rewriting a reviewer's words to make them fit is a worse
    answer than telling the author while they can still edit. Refusing also catches the caller
    that TRUNCATED a quotation mid-span, which balancing would have silently papered over.

    A code span whose rendered interior begins or ends in whitespace is REFUSED for the same
    reason: markdownlint's MD038 refuses it, and the next commit touching the ledger is blocked
    by a row its committer did not write. Every writer that cleans through here inherits it.
    """
    text = str(value or "")
    # Parity over the DELIMITER backticks only. A backslash-escaped backtick is a literal
    # one and never opened a span, so counting it refused values markdown writes correctly.
    # Odd parity always leaves a run unpaired, which is the one this message points at.
    unclosed = _scan_ticks(text)[1]
    if unclosed and sum(len(m.group(0)) for m in _TICK_RUN.finditer(text)) % 2:
        at = unclosed[0]
        raise ValueError(
            f"refused: the value carries an odd number of backticks, so its last code span "
            f"never closes and markdownlint refuses the file it is written into. Close the "
            f"span or drop the stray backtick - it is not balanced here, because rewriting "
            f"what a reviewer wrote is worse than refusing it. The stray is at character "
            f"{at} of {len(text)}, here: {_excerpt(text, at)!r}")
    text = text.replace("|", "/").replace("\n", " ").strip()
    # Judged AFTER the newline substitution: a span broken across lines renders the break as a
    # space, so its edge is only visible once the row's own shape has been applied.
    if (found := _edge_whitespace_span(text)) is not None:
        at, span, edge = found
        raise ValueError(
            f"refused: the code span {span!r} carries whitespace on its {edge}, and "
            f"markdownlint (MD038) refuses the file it is written into. Padding cannot carry "
            f"that space either: CommonMark strips one space from each side of a padded span, "
            f"so no code span holds a value whose first or last character is whitespace. "
            f"Quote the value without the space and say in prose that it has one, or move the "
            f"literal out of the span. The span starts at character {at} of {len(text)}.")
    return _escape_outside_spans(text)


def record_verdict(repo_root: Path | str, unit: str, verdict: str,
                   reviewer: str = "independent-critic", author: str = "",
                   issues: str = "", phase: str = "delivery", brief: str = "",
                   tier: str | None = None, tier_explicit: bool = False) -> Path:
    """Append a critic verdict for a unit (creating the table if absent).

    `author` is the authoring seat / delegation instance id that produced the diff
    and tests. It is recorded alongside the reviewer so the conformance gate can prove
    reviewer != author - independence you cannot verify is independence you do not have.
    `phase` is internal and defaults to `delivery`, the only phase any command records.

    A DELIVERY verdict is held to the review rounds here, so every writer is: `round_refusal`
    refuses it with nothing written, and a REJECT at the cap carries the unit (`carry_at_cap`).
    A carry that fails raises `CarryFailed`, whose message says the REJECT row WAS written.
    """
    path, _round, bug = _record(repo_root, unit, verdict, reviewer, author, issues, phase,
                                brief, tier, tier_explicit)
    if bug:
        print(carried_notice(unit, bug), file=sys.stderr)
    return path


def _record(repo_root, unit, verdict, reviewer, author, issues="", phase="delivery", brief="",
            tier=None, tier_explicit=False) -> tuple[Path, int | None, str | None]:
    """Write the verdict, then carry the unit if it is a REJECT at the cap: the ledger path,
    the row's round in its delivery (None off the delivery phase) and the carried bug's id
    (None when nothing was carried)."""
    path, _row = _write_verdict(repo_root, unit, verdict, reviewer, author, issues, phase,
                                brief, tier, tier_explicit)
    if phase != "delivery":
        return path, None, None
    rounds = delivery_rounds(repo_root, unit)
    return path, len(rounds), _carry_if_capped(repo_root, unit, verdict, path, rounds)


def _write_verdict(repo_root, unit, verdict, reviewer, author, issues, phase, brief,
                   tier, tier_explicit) -> tuple[Path, str]:
    """Check and write one verdict row, returning the ledger path AND the row it wrote. A
    delivery verdict's round is checked under the ledger lock, so two writers cannot both take
    the last round."""
    if str(verdict or "").upper() not in VERDICTS:
        raise ValueError(f"{verdict!r} is not a verdict - expected one of {', '.join(VERDICTS)}")
    if phase not in PHASES:
        raise ValueError(f"unknown critic phase {phase!r} - expected one of {PHASES}")
    path = verdicts_path(repo_root, phase)
    # BOTH ids floored to `-`, not just the author. The reviewer had no floor, which is what let
    # an empty value reach the ledger; `is_independent` then read `"" != "alice"` as True and the
    # row passed as independently reviewed. Flooring here means the empty case is visible in the
    # log as well as refused by the predicate - a reader can see the cell is blank rather than
    # meeting a row that merely looks unremarkable.
    if phase == "delivery" and tier is not None and tier not in TIERS:
        raise ValueError(f"unknown review tier {tier!r} - expected one of {', '.join(TIERS)}")
    # ABSENT is `-`, not a defaulted `full`. A verdict recorded without a tier genuinely cannot
    # say at what depth it was taken, and reading absence as `full` would let every historical
    # row claim a depth nobody recorded - the exact over-claim the Brief column was added to
    # stop. The historical plan ledger's eighth cell (its Kind) takes `-` the same way.
    recorded = (f"{tier}{EXPLICIT_SUFFIX if tier_explicit else ''}"
                if tier and phase == "delivery" else "-")
    extra_cell = f"{_clean(recorded)} | "
    row = (f"| {sdlc_md.norm_id(unit)} | {verdict.upper()} | {_clean(reviewer) or '-'} | "
           f"{_clean(author) or '-'} | "
           f"{sdlc_md.now_date()} | {_clean(brief) or '-'} | {extra_cell}"
           f"{_clean(issues) or '-'} |\n")
    if phase == "delivery":
        _mark_review_base(repo_root, unit)
    with _ledger_lock(path):
        if phase == "delivery" and (why := round_refusal(repo_root, unit, reviewer)):
            raise ValueError(why)
        if not path.exists():
            sdlc_md.atomic_write(path, _header(phase))
        _ensure_brief_column(path)
        _ensure_eighth_column(path, "Kind" if phase == "plan-review" else "Tier")
        _write_verdict_row(path, row)
    return path, row


def _ledger_lock(path: Path):
    """The lock every write to a review ledger holds, so parallel reviewers lose no row. Every
    ledger lives at `<root>/sdlc-studio/reviews/`, so the root's shared lock serves them all."""
    path.parent.mkdir(parents=True, exist_ok=True)
    return sdlc_md.allocation_lock(path.parents[2])


@contextlib.contextmanager
def provisional_verdict(repo_root: Path | str, unit: str, verdict: str, reviewer: str,
                        author: str, issues: str = "", pending=None):
    """Record a delivery verdict that stands only if the block's transition lands.

    `transition set --verdict` writes the verdict before the gated transition, because a gate
    may read it. When the block raises while `pending()` is still true - the unit still at its
    from-status, so the transition was refused - the row is withdrawn, and a ledger the row
    created is removed, so a refused close leaves no verdict behind; a withdrawal the lock
    times out names the row it leaves and lets the refusal through. A raise after the status
    write landed keeps the row: the unit's new status stands on it. A REJECT at the cap is
    carried once the row stands, as `record_verdict` carries it."""
    path = verdicts_path(repo_root)
    existed = path.exists()
    path, row = _write_verdict(repo_root, unit, verdict, reviewer, author, issues, "delivery",
                               "", None, False)
    try:
        yield path
    except BaseException:
        if pending is not None and not pending():
            try:
                if bug := _carry_if_capped(repo_root, unit, verdict, path):
                    print(carried_notice(unit, bug), file=sys.stderr)
            except CarryFailed as exc:
                print(f"error: {exc}", file=sys.stderr)
            raise
        try:
            with _ledger_lock(path):
                text = path.read_text(encoding="utf-8")
                at = text.rfind(row)
                if at >= 0:
                    text = text[:at] + text[at + len(row):]
                if not existed and text == _header("delivery"):
                    path.unlink()
                else:
                    sdlc_md.atomic_write(path, text)
        except sdlc_md.AllocationLockTimeout as exc:
            # the refusal below is the reason; the row it leaves behind is the damage to name
            print(f"error: the provisional {verdict.upper()} row for {sdlc_md.norm_id(unit)} "
                  f"could not be withdrawn and still stands; remove that row from {path} "
                  f"once the lock is free - {exc.reason}",
                  file=sys.stderr)
        raise
    if bug := _carry_if_capped(repo_root, unit, verdict, path):
        print(carried_notice(unit, bug), file=sys.stderr)


def _ensure_brief_column(path: Path) -> None:
    """Widen a pre-Brief verdict table in place, padding existing rows with `-`.

    The table header is written once, when the log is created, so a log that predates the
    Brief column keeps a six-column header while new rows carry seven cells - which is not a
    valid markdown table, and markdownlint MD056 refuses the commit.

    This pads rather than rewrites: every recorded cell keeps its value and its position, and
    the added cell is `-`, the same ABSENT marker a hand-written prompt records. That is the
    honest value for these rows, because a verdict taken before the column existed genuinely
    cannot say which brief produced it. The log stays append-only in the sense that matters -
    no judgement anybody recorded is altered or removed.
    """
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if not line.lstrip().startswith("| Unit |"):
            continue
        if "| Brief |" in line:
            return
        lines[i] = line.replace("| Issues |", "| Brief | Issues |", 1)
        if i + 1 < len(lines) and set(lines[i + 1].strip()) <= set("|-: "):
            lines[i + 1] = lines[i + 1].replace("| --- |", "| --- | --- |", 1)
        for j in range(i + 2, len(lines)):
            if not lines[j].lstrip().startswith("|"):
                break
            cells = sdlc_md.table_cells(lines[j])
            if len(cells) != 6:
                continue
            body = lines[j].rstrip("\n").rstrip()
            body = body[:-1].rstrip() if body.endswith("|") else body
            head, _, last = body.rpartition("|")
            lines[j] = f"{head}| - |{last.rstrip()} |\n"
        sdlc_md.atomic_write(path, "".join(lines))
        return


def _ensure_eighth_column(path: Path, name: str) -> None:
    """Widen a seven-column verdict table in place, padding existing rows with `-`.

    ONE migration for both logs, because they grew their eighth column for the same reason and
    would otherwise carry two copies of this loop (LL0016). `name` is `Kind` on the historical
    plan-review log and `Tier` on the delivery one; `-` is what a row written before the column
    honestly means, because a verdict taken then cannot say what the column records.

    The header is written once, when a log is created, so a log that predates the column keeps a
    seven-column header while new rows carry eight - not a valid markdown table, and markdownlint
    MD056 refuses the commit.

    This PADS rather than rewrites: every recorded cell keeps its value and its position. This
    sprint already watched a column added to VELOCITY.md shift every historical row, so that the
    estimate column read back the actual - the same mistake, one file over.
    """
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if not line.lstrip().startswith("| Unit |"):
            continue
        if f"| {name} |" in line:
            return
        lines[i] = line.replace("| Issues |", f"| {name} | Issues |", 1)
        if i + 1 < len(lines) and set(lines[i + 1].strip()) <= set("|-: "):
            lines[i + 1] = lines[i + 1].replace("| --- |", "| --- | --- |", 1)
        for j in range(i + 2, len(lines)):
            if not lines[j].lstrip().startswith("|"):
                break
            if len(sdlc_md.table_cells(lines[j])) != 7:
                continue
            body = lines[j].rstrip("\n").rstrip()
            body = body[:-1].rstrip() if body.endswith("|") else body
            head, _, last = body.rpartition("|")
            lines[j] = f"{head}| - |{last.rstrip()} |\n"
        sdlc_md.atomic_write(path, "".join(lines))
        return


def _write_verdict_row(path: Path, row: str) -> None:
    """Add a verdict row, keeping the table one contiguous block.

    With no supersession section present this is a plain O_APPEND write, byte-identical to
    what it has always done. Once records have been added below the table, the row goes in
    after the last table line instead, so the table does not acquire a paragraph in the
    middle of it. Nothing already written is removed or altered either way.
    """
    text = path.read_text(encoding="utf-8")
    if SUPERSEDE_HEADING not in text:
        with path.open("a", encoding="utf-8") as fh:  # append-only
            fh.write(row)
        return
    lines = text.splitlines(keepends=True)
    table = [i for i, line in enumerate(lines) if line.lstrip().startswith("|")]
    if not table:
        with path.open("a", encoding="utf-8") as fh:
            fh.write(row)
        return
    last = table[-1]
    if not lines[last].endswith("\n"):
        lines[last] += "\n"
    lines.insert(last + 1, row)
    sdlc_md.atomic_write(path, "".join(lines))


def read_verdicts(repo_root: Path | str, phase: str = "delivery") -> list[dict]:
    """All recorded verdicts for `phase`, in order, as
    {unit, verdict, reviewer, author, date, issues} plus the supersession annotation
    {superseded, superseded_reason, superseded_by, superseded_at}.

    Reads both the current 6-column rows and any legacy 5-column rows (no Author) that
    pre-date the independence gate; a legacy row's author is the empty string. A retired
    row is still returned, marked - dropping it would lose the record that it happened,
    which is the reason the log is append-only in the first place.
    """
    path = verdicts_path(repo_root, phase)
    if not path.exists():
        return []
    out: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = sdlc_md.table_cells(line)  # escaped-pipe-aware
        if not cells or cells[0] in ("Unit",):
            continue
        if len(cells) == 8:
            out.append(dict(zip(_COLS_BY_PHASE[phase], cells)))
        elif len(cells) == 7:
            row = dict(zip(_COLS, cells))
            if phase == "delivery":
                # A tier is UNKNOWN on such a row, never `full`. Absent and full are different
                # facts, and only absent is true of a verdict taken before the column existed.
                row["tier"] = ""
            out.append(row)
        elif len(cells) == 6:  # pre-brief: Unit, Verdict, Reviewer, Author, Date, Issues.
            # Read, never rewritten. Every verdict recorded before the brief column existed is a
            # real judgement somebody made, and dropping it to "unparseable" would retire the
            # adversarial record wholesale. Its brief is ABSENT rather than empty, which is the
            # same thing a hand-written prompt records - correct, because that is exactly what
            # those rows cannot distinguish about themselves.
            older = dict(zip(("unit", "verdict", "reviewer", "author", "date", "issues"), cells))
            older["brief"] = ""
            if phase == "delivery":
                older["tier"] = ""
            out.append(older)
        elif len(cells) == 5:  # legacy: Unit, Verdict, Reviewer, Date, Issues
            legacy = dict(zip(("unit", "verdict", "reviewer", "date", "issues"), cells))
            legacy["author"] = ""
            if phase == "delivery":
                legacy["tier"] = ""
            out.append(legacy)
        else:
            # A row that is neither current (6 cols) nor legacy (5) - a torn write from a
            # crash mid-append. Surface it: silently dropping a verdict is a false "no
            # verdict" signal at the gate. Report and skip, never swallow.
            print(f"warning: malformed row in {path} ({len(cells)} cells, expected 6 or 5), "
                  f"skipped: {' | '.join(cells)[:100]}", file=sys.stderr)
    return _number_rounds(_annotate_superseded(out, read_supersessions(repo_root, phase)))


def _number_rounds(rows: list[dict]) -> list[dict]:
    """Stamp each row with its `round`: its ordinal among the unit's live rows in this ledger.

    Derived rather than stored. The ledger is append-only and one reviewer records one row per
    round, so the round IS the row's position; a stored copy could only disagree with it. A
    superseded row records an event ruled not to have happened, so it is no round (`None`).
    """
    seen: dict[str, int] = {}
    for row in rows:
        if is_superseded(row):
            row["round"] = None
            continue
        unit = sdlc_md.norm_id(row.get("unit", ""))
        seen[unit] = seen.get(unit, 0) + 1
        row["round"] = seen[unit]
    return rows


def delivery_rounds(repo_root: Path | str, unit: str, state: dict | None = None) -> list[dict]:
    """The live delivery verdict rows of `unit`'s CURRENT delivery, oldest first, each `round`
    numbered from 1 within it.

    In an open run holding the unit: the rows written since the run first reviewed it (its
    `REVIEW_BASE`), so a unit carried out of an earlier run starts again at round 1. Outside
    one: the rows since the APPROVE that closed the previous delivery. A final APPROVE closes
    the current delivery rather than starting the next, so its rounds still count against a
    further verdict: outside a run nothing else marks where a new delivery began."""
    uid = sdlc_md.norm_id(unit)
    rows = [r for r in read_verdicts(repo_root) if sdlc_md.norm_id(r.get("unit", "")) == uid]
    # A caller holding a run's own record (the report of a sealed run) counts against THAT
    # run's base whether or not it is still open: a figure that moved when the run sealed would
    # invalidate the very page the seal signs.
    given = state is not None and uid in ((state or {}).get(run_state.REVIEW_BASE) or {})
    state = state if state is not None else (run_state.read(repo_root) or {})
    if given or run_state.batch_holds(state, uid):
        base = (state.get(run_state.REVIEW_BASE) or {}).get(uid)
        rows = [r for r in rows[base:] if not is_superseded(r)] if isinstance(base, int) else []
    else:
        rows = [r for r in rows if not is_superseded(r)]
        closed = [i for i, r in enumerate(rows[:-1])
                  if str(r.get("verdict") or "").upper() == APPROVE]
        rows = rows[closed[-1] + 1:] if closed else rows
    return [{**r, "round": n} for n, r in enumerate(rows, 1)]


def _mark_review_base(repo_root: Path | str, unit: str) -> None:
    """Fix `unit`'s REVIEW_BASE at its row count now, before its first review in the open run
    holding it. A no-op outside such a run, or once the base is fixed."""
    uid = sdlc_md.norm_id(unit)
    state = run_state.read(repo_root) or {}
    if run_state.batch_holds(state, uid) and uid not in (state.get(run_state.REVIEW_BASE) or {}):
        run_state.mark_review_base(repo_root, uid, sum(
            1 for r in read_verdicts(repo_root) if sdlc_md.norm_id(r.get("unit", "")) == uid))


def review_rounds(repo_root: Path | str, unit: str, state: dict | None = None) -> int:
    """How many review rounds `unit`'s current delivery has recorded (`delivery_rounds`)."""
    return len(delivery_rounds(repo_root, unit, state))


def unit_review_rounds(repo_root: Path | str, unit: str, phase: str = "delivery") -> list[dict]:
    """Every LIVE recorded verdict for one unit, oldest first - the unit's review ROUNDS.

    `verdict_for` answers "where does this unit stand", which is one row. Escalation asks a
    different question: how many times has this been round, and did it converge? That needs the
    sequence, so a superseded row is dropped (a named authoriser ruled it did not happen) while
    every surviving round is kept.
    """
    want = sdlc_md.norm_id(unit)
    return [r for r in read_verdicts(repo_root, phase)
            if sdlc_md.norm_id(r.get("unit", "")) == want and not is_superseded(r)]


def seat_verdicts(repo_root: Path | str, unit: str, phase: str = "delivery") -> dict:
    """The LATEST verdict each reviewing seat gave on a unit, as `{reviewer: VERDICT}`.

    A split panel is a different escalation from a repeatedly-rejecting one: seats that
    disagree need the operator to break the tie, not another repair round. Latest per seat,
    because a seat that rejected and then approved has resolved its own objection.
    """
    out: dict = {}
    for row in unit_review_rounds(repo_root, unit, phase):
        who = str(row.get("reviewer") or "").strip()
        if who:
            out[who] = str(row.get("verdict") or "").strip().upper()
    return out


def verdict_for(repo_root: Path | str, unit: str, phase: str = "delivery"):
    """The latest LIVE recorded verdict for a unit in `phase`, or None. Defaults to the
    delivery log, so the conformance `critiqued` gate is unaffected by plan-review rows.

    A superseded row is skipped: it records an event that a named authoriser has ruled did
    not happen, so acting on it would be acting on a known-false fact. A unit whose only row
    is superseded therefore has NO verdict, which is different from having an approval.

    EXCEPT a NEGATIVE one, which needs a PRINCIPAL-grade supersession to retire. The grade
    required scales with the direction the mistake fails. Retiring an approval weakly loses an
    approval, and a gate with one fewer approval refuses - it fails closed. Retiring a REJECT
    weakly deletes the one record that blocks the unit, and the gate then reports it covered by
    an independent pass. `record_supersession` refuses to write such a record, but a hand
    append walks round the tool, and a plain truthiness test on the flag honoured it: an author
    could retire the review blocking their own work with one line naming themselves as
    authoriser and `-` as boundary. `_is_principal_superseded` was already written as the
    read-time backstop for exactly that, and only the sign-off gate consulted it - so the two
    gates enforced different independence rules, and the weaker one was the one guarding the
    honesty check.
    """
    seen = _live_verdict_rows(repo_root, unit, phase)
    latest = seen[-1] if seen else None
    unanswered = _unanswered_rejects(seen)
    # THE LATEST unanswered REJECT, and the tie-break is load-bearing rather than incidental:
    # reporting the EARLIEST instead leaves 18 units non-conformant rather than 19, and the unit
    # it drops is US0671 - the first one this bug's own Steps to Reproduce names as masked. The
    # reading that gives the tidier number is the one that hides the example.
    return unanswered[-1] if unanswered else latest


def _live_verdict_rows(repo_root: Path | str, unit: str, phase: str = "delivery") -> list[dict]:
    """The unit's verdict rows a reader may act on, oldest first - THE supersession rule.

    A superseded row is dropped, except a REJECT whose supersession is not principal-grade
    (`verdict_for` states why). `verdict_for` and `standing_rejects` both read this, so the
    reader that says whether a unit carries a rejection and the reader that says whether it is
    answered cannot hold two copies of the rule: a second copy simplified to "is it superseded"
    passed the whole suite and let an author-superseded REJECT through the transition guard
    while `coverage_state` read the unit unreviewed.
    """
    target = sdlc_md.norm_id(unit)
    out: list[dict] = []
    for v in read_verdicts(repo_root, phase):
        if sdlc_md.norm_id(v["unit"]) != target:
            continue
        if v.get("superseded") and ((v.get("verdict") or "").upper() != REJECT
                                    or _is_principal_superseded(repo_root, unit, v)):
            continue
        out.append(v)
    return out


#: The day the same-reviewer round rule (`round_refusal`) shipped. An APPROVE recorded on or
#: after it answers only its own reviewer's REJECT; before it, seats were named per round, so
#: the brief fingerprint is the only key that pairs a round-2 APPROVE with its REJECT.
ROUND_RULE_SHIPPED = "2026-09-23"
#: The first day no delivery REJECT could be answered by a `critic.py repair` row: the verb was
#: retired on 2026-09-25, the day of the last repair row, so a REJECT dated that day or earlier
#: could still be. A unit that reached Done over such a REJECT passed the gate of its day, and
#: `conformance.verdict_half_ok` reads it as critiqued by the REJECT's own date, never by the
#: frozen ledger. Nothing that judges current work reads it.
REPAIR_VERB_RETIRED = "2026-09-26"


def _unanswered_rejects(rows: list[dict]) -> list[dict]:
    """Every REJECT in one unit's rows that no LATER APPROVE has answered, oldest first.

    A REJECT is answered by an APPROVE from the SAME reviewer at a later round: round 2 is the
    round-1 reviewer re-checking the fixes (`round_refusal` refuses any other reviewer), so the
    key is (unit, reviewer, round). The brief fingerprint is a second key for an APPROVE dated
    before that rule (`ROUND_RULE_SHIPPED`), whose seats were named per round (`qa-seat-<epic>`
    against `qa-seat-close-r2`); dropping it would reopen the historical units it pairs. After
    the rule a fingerprint answers nothing, so no invented `--brief` can retire another seat's
    REJECT. An absent fingerprint matches nothing.
    """
    out = []
    for i, r in enumerate(rows):
        if not str(r.get("verdict") or "").upper().startswith(REJECT):
            continue
        fp, who = _brief_key(r), _id(r.get("reviewer", ""))
        if any(str(l.get("verdict") or "").upper().startswith(APPROVE)
               and ((who and _id(l.get("reviewer", "")) == who)
                    or (fp and _brief_key(l) == fp
                        and str(l.get("date") or "") < ROUND_RULE_SHIPPED))
               for l in rows[i + 1:]):
            continue
        out.append(r)
    return out


def _brief_key(row: dict) -> str:
    """A verdict row's brief fingerprint, or `""` when it has none.

    The ledger writes `-` for an absent brief (`_clean(brief) or '-'` at the write site), so the
    empty string this check was originally written against is a state `record` has never
    produced and `if not fp` never fired.

    A historical cell `record` MARKED unmatched is not provenance either: its fingerprint matched
    no brief the repo could produce when it was recorded. Reading it as briefed would let two
    marked rows sharing a value pair and answer a rejection. Nothing writes the mark any more,
    but the rows that carry it stay in the ledger.
    """
    cell = str(row.get("brief") or "").strip(" -")
    return "" if UNMATCHED_MARK in cell.split() else cell


def standing_rejects(repo_root: Path | str, unit: str, phase: str = "delivery") -> list[dict]:
    """The REJECT rows a reader should NAME for this unit, oldest first, or `[]` for none.

    Every rejection no later same-brief APPROVE retired; and when one did retire them all, the
    latest REJECT still, because this answers "which rejection is this about", never "is it
    answered". A same-brief APPROVE the unit's own author recorded retires the row here and in
    `verdict_for`, yet `coverage_state` reads the unit `unreviewed` - so a caller asks that for
    the answer and this for the name. A superseded REJECT counts unless the supersession is
    principal-grade - read through `_live_verdict_rows`, the one copy of that rule
    `verdict_for` reads too.
    """
    live = _live_verdict_rows(repo_root, unit, phase)
    rejects = [v for v in live if str(v.get("verdict") or "").upper().startswith(REJECT)]
    return _unanswered_rejects(live) or rejects[-1:]


# --- Supersession (a verdict row retired by addition) ----------------------------------
# A verdict row can record an event that did not happen - a reviewer mis-entered, a verdict
# filed against the wrong unit. The log's authority comes from nobody editing it, so the
# correction is made by ADDING a record that retires the row, never by deleting the row or
# widening it with another column (the row parser reads 6 or 5 cells and warns on anything
# else, so a 7th column would turn every row into a torn-write warning). The record is
# written below the table as prose for the same reason: a pipe-delimited erratum would be
# read as a malformed verdict.
SUPERSEDE_HEADING = "## Supersessions"
_SUPERSEDE_INTRO = (
    "\n" + SUPERSEDE_HEADING + "\n\n"
    "> Appended, never edited in place. Each record retires one verdict row above: the row\n"
    "> stays in the table and every reader marks it superseded, so the log is corrected by\n"
    "> addition. Prose, not a table - the row parser reads every pipe-delimited line here.\n\n")
#: Record fields, in write order. Also the parse boundary: a value runs to the next of these
#: keys, so a reason containing punctuation (or a semicolon-separated agent id) stays whole.
_SUPERSEDE_KEYS = ("unit", "row-date", "row-verdict", "row-reviewer", "row-author",
                   "authorised-by", "boundary", "reason", "recorded")
_SUPERSEDE_COLS = ("unit", "row_date", "row_verdict", "row_reviewer", "row_author",
                   "authorised_by", "boundary", "reason", "recorded")
_SUPERSEDE_PREFIX = "SUPERSEDED "


def _supersede_value(value: str, escape: bool = True) -> str:
    """One field of a supersession record: single-line, pipe-free (so no reader mistakes it
    for a table row), and with any embedded ` key=` sequence defused to ` key:` so free prose
    cannot forge a field boundary. `escape` off for a value copied from a table cell, which
    already carries the markdown escaping `_clean` applies - doubling it would store a value
    that no longer reads back as what the row says."""
    out = _clean(value) if escape else value.replace("|", "/").replace("\n", " ").strip()
    for key in _SUPERSEDE_KEYS:
        out = out.replace(f" {key}=", f" {key}:")
    return " ".join(out.split())


def _supersede_field(body: str, key: str) -> str:
    boundary = "|".join(re.escape(k) for k in _SUPERSEDE_KEYS)
    m = re.search(rf"(?:^|\s){re.escape(key)}=(.*?)(?=\s(?:{boundary})=|$)", body)
    return m.group(1).strip().replace("\\_", "_") if m else ""


def read_supersessions(repo_root: Path | str, phase: str = "delivery") -> list[dict]:
    """Every supersession record in `phase`'s log, in order, as {unit, row_date, row_verdict,
    row_reviewer, row_author, authorised_by, boundary, reason, recorded}."""
    path = verdicts_path(repo_root, phase)
    if not path.exists():
        return []
    out: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith(_SUPERSEDE_PREFIX):
            continue
        body = stripped[len(_SUPERSEDE_PREFIX):]
        out.append({col: _supersede_field(body, key)
                    for col, key in zip(_SUPERSEDE_COLS, _SUPERSEDE_KEYS)})
    return out


def _supersession_index(records: list[dict]) -> dict:
    """Supersession records grouped by NORMALISED unit id, with their join keys pre-computed.

    The join was a cross-product: every row walked every record, and every comparison
    normalised four ids. Over this repository - 848 verdict rows against 32 records - that is
    27,136 comparisons per annotation, and the ledger is annotated on EVERY lookup, so a single
    whole-workspace conformance run made 16,837,139 of them and 37 million id normalisations
    A record retires a row of ITS OWN unit or of none, so the unit is the index.
    """
    index: dict = {}
    for rec in records:
        key = (sdlc_md.norm_id(rec.get("unit", "")),
               rec.get("row_date", ""),
               (rec.get("row_verdict", "") or "").upper(),
               _id(rec.get("row_reviewer", "")))
        index.setdefault(key, rec)      # first record wins, as `next()` did
    return index


def _annotate_superseded(rows: list[dict], records: list[dict]) -> list[dict]:
    """Mark each row a supersession record retires. Every row carries the `superseded*` keys,
    so a reader never has to tell 'live' from 'field absent'."""
    index = _supersession_index(records)
    for row in rows:
        rec = index.get((sdlc_md.norm_id(row.get("unit", "")),
                         row.get("date", ""),
                         (row.get("verdict", "") or "").upper(),
                         _id(row.get("reviewer", ""))))
        row["superseded"] = rec is not None
        row["superseded_reason"] = rec["reason"] if rec else ""
        row["superseded_by"] = rec["authorised_by"] if rec else ""
        row["superseded_boundary"] = rec.get("boundary", "") if rec else ""
        row["superseded_at"] = rec["recorded"] if rec else ""
    return rows


def is_superseded(verdict: dict | None) -> bool:
    """True when a verdict row has been retired by a recorded supersession."""
    return bool(verdict) and bool(verdict.get("superseded"))


def _adversarial_worker_ids(repo_root: Path | str, unit: str,
                            exclude_row: dict | None = None) -> set[str]:
    """Every reviewer id that did adversarial or review WORK on the unit in-session: the
    reviewers on its verdict and sprint-level-review rows OTHER than the one under correction.
    A principal wrongly named on a single verdict row appears in NONE of these - a reviewer of
    record signs off; they do not file a second verdict - which is the recordable distinction
    between a mis-attribution and an author retiring a true verdict. `exclude_row` is the
    verdict row a supersession is about: its own reviewer is not counted FROM that row, so the
    party the correction concerns cannot veto their own correction. The retired evidence ledger
    is not read: one verdict ledger says who reviewed a unit.
    Superseded rows are read RAW here: independence is about who touched the unit, and this set is
    what decides whether a supersession may retire that fact - it cannot depend on the answer."""
    target = sdlc_md.norm_id(unit)
    ids: set[str] = set()
    for ph in PHASES:
        for v in read_verdicts(repo_root, ph):
            if sdlc_md.norm_id(v["unit"]) != target:
                continue
            if exclude_row is not None and _matches_row(v, exclude_row):
                continue
            ids.add(_id(v["reviewer"]))
    for sr in sprint_reviews(repo_root):
        if target in _covered_ids(sr):
            ids.add(_id(sr["reviewer"]))
    ids.discard("")
    return ids


def _matches_row(row: dict, other: dict) -> bool:
    """Two verdict rows are the same row: same date, reviewer and verdict for one unit."""
    return (row.get("date", "") == other.get("date", "")
            and _id(row.get("reviewer", "")) == _id(other.get("reviewer", ""))
            and (row.get("verdict", "") or "").upper() == (other.get("verdict", "") or "").upper())


def record_supersession(repo_root: Path | str, unit: str, date: str, reason: str,
                        authorised_by: str, boundary: str, reviewer: str | None = None,
                        verdict: str | None = None, phase: str = "delivery") -> Path:
    """Retire one verdict row by appending a supersession record naming it.

    The row is identified by unit and date, narrowed with `reviewer` and `verdict` when a
    unit carries more than one row that day. Refusals, all loud and all writing nothing:

    - no row matches, or more than one does - a correction pointing at nothing (or at an
      unspecified one of several) is a false erratum;
    - no authoriser, or no `boundary` (the separate trust boundary the authoriser acted in) -
      superseding can retire an independence attribution, so it is held to the sign-off's own
      rule: a correction with no recorded boundary is a hand edit with extra steps;
    - an authoriser who is the row's own AUTHOR, or who did in-session review work on the unit
      (a reviewer on any other verdict or frozen sprint-review row) - a party the
      author controls cannot authorise retiring the review that blocks it. The row's own wrongly
      named reviewer is NOT refused on that row alone: a row naming the wrong reviewer is exactly
      the case this exists for, and the person wrongly named is the one who can rule the pass
      never ran - provided they did no other reviewing work on the unit;
    - no reason.
    """
    if phase not in PHASES:
        raise ValueError(f"unknown critic phase {phase!r} - expected one of {PHASES}")
    if not (reason or "").strip():
        raise ValueError("a supersession needs a --reason - retiring a recorded event "
                         "without stating why is the quiet rewrite this log exists to prevent")
    if not (authorised_by or "").strip():
        raise ValueError("a supersession needs --authorised-by naming who authorised it - "
                         "an unauthorised correction to an append-only log is a hand edit "
                         "with extra steps")
    if not (boundary or "").strip():
        raise ValueError("a supersession needs --boundary naming the separate trust boundary "
                         "its authoriser acted in - superseding can retire an independence "
                         "attribution, so it is held to the sign-off's own rule")
    target, want_date = sdlc_md.norm_id(unit), (date or "").strip()
    candidates = [v for v in read_verdicts(repo_root, phase)
                  if sdlc_md.norm_id(v["unit"]) == target and v["date"] == want_date]
    if reviewer:
        candidates = [v for v in candidates if _id(v["reviewer"]) == _id(reviewer)]
    if verdict:
        candidates = [v for v in candidates if v["verdict"].upper() == verdict.upper()]
    if not candidates:
        dates = sorted({v["date"] for v in read_verdicts(repo_root, phase)
                        if sdlc_md.norm_id(v["unit"]) == target})
        seen = f"rows dated {', '.join(dates)}" if dates else "no rows at all"
        raise ValueError(f"no {phase} verdict row for {target} dated {want_date!r} "
                         f"(that unit has {seen}) - a supersession that points at nothing "
                         f"is a false erratum; nothing written")
    if len(candidates) > 1:
        raise ValueError(
            f"{len(candidates)} {phase} verdict rows match {target} dated {want_date} - "
            f"narrow it with --reviewer and/or --verdict; retiring an unspecified one of "
            f"several is not a correction")
    row = candidates[0]
    if _id(authorised_by) == _id(row["author"]):
        raise ValueError(
            f"authoriser {authorised_by!r} is the row's own author - the party that wrote "
            f"the row cannot authorise retiring it; name an authoriser outside it")
    if _id(authorised_by) in _adversarial_worker_ids(repo_root, unit, exclude_row=row):
        raise ValueError(
            f"authoriser {authorised_by!r} did in-session review work on {target} (a reviewer "
            f"on another verdict or sprint-review row) - a party the author "
            f"controls cannot authorise retiring the review, on the sign-off's independence "
            f"rule; name a principal in a separate trust boundary")
    path = verdicts_path(repo_root, phase)
    record = _SUPERSEDE_PREFIX + " ".join(
        f"{key}={value}" for key, value in zip(_SUPERSEDE_KEYS, (
            sdlc_md.norm_id(row["unit"]), row["date"], row["verdict"].upper(),
            _supersede_value(row["reviewer"], escape=False),
            _supersede_value(row["author"] or "-", escape=False),
            _supersede_value(authorised_by), _supersede_value(boundary),
            _supersede_value(reason), sdlc_md.now_date())))
    with _ledger_lock(path):
        text = path.read_text(encoding="utf-8")
        with path.open("a", encoding="utf-8") as fh:  # append-only, below the table
            fh.write(_SUPERSEDE_INTRO if SUPERSEDE_HEADING not in text else "\n")
            fh.write(record + "\n")
    return path


# --- Ledger rows ------------------------------------------------------------------------
# One verdict ledger (`critic-verdicts.md`) says whether a unit was reviewed. The evidence
# ledger (`critic-evidence.md`) and the per-unit sign-off ledger are frozen history that nothing
# reads; the operator signs the run once at `sprint sign`.


def _append_row(path: Path, header: str, cells: tuple[str, ...]) -> Path:
    with _ledger_lock(path):
        if not path.exists():
            sdlc_md.atomic_write(path, header)
        with path.open("a", encoding="utf-8") as fh:  # append-only
            fh.write("| " + " | ".join(cells) + " |\n")
    return path


def _read_rows(path: Path, cols: tuple[str, ...]) -> list[dict]:
    """The table's DATA rows. The markdown header is identified by matching the whole cell
    tuple against the declared column names, not by a first-column literal: the previous
    check knew only `Unit`, so a table led by any other column (the sprint-review table's
    `Base`) returned its own header as data. Matching every column generalises to each table
    this serves and cannot lapse when the next one is added."""
    if not path.exists():
        return []
    header = tuple(c.strip().lower() for c in cols)
    out: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = sdlc_md.table_cells(line)  # escaped-pipe-aware
        # A row SHORT by trailing columns is read, with those columns absent. Every column this
        # family has ever gained was appended, so a short row is one written before the newest
        # column and is complete for its own era. Requiring an exact width dropped such a row
        # entirely - which for the sign-off log would have silently un-signed every unit signed
        # before the Capacity column, and the two-role gate would have started refusing them.
        #
        # Short by ANY number, not by one. The bound was `len(cols) - 1`, which tolerated a
        # single era of appends and no more: two columns added in one change made every older
        # row unreadable, on every consuming project's ledger at upgrade. The floor is two
        # cells because a row must at least name a unit and one field to be a row at all.
        if not cells or not (2 <= len(cells) <= len(cols)):
            continue
        if tuple(c.strip().lower() for c in cells) == header[:len(cells)]:
            continue
        row = dict(zip(cols, cells))
        for missing in cols[len(cells):]:
            row[missing] = ""
        out.append(row)
    return out


def split_items(text: str) -> list[str]:
    """Split a channel string into items on an UNESCAPED `;`, unescaping as it goes.

    A SCANNER, not a lookbehind. `(?<!\\\\);` cannot tell a backslash that escapes the semicolon
    from one that is itself escaped, so a value ending in a real backslash silently swallowed the
    item after it - the same silence this function exists to end, one layer down.

    Prose is a poor container for records and the structured file paths exist for that reason,
    but the flag form has to keep working, so a value that needs a semicolon can escape it.
    """
    out, buf, i, n = [], [], 0, len(text or "")
    while i < n:
        ch = text[i]
        if ch == "\\" and i + 1 < n and text[i + 1] in ";\\":
            buf.append(text[i + 1])          # an escaped `;` or an escaped `\`
            i += 2
            continue
        if ch == ";":
            item = "".join(buf).strip()
            if item:
                out.append(item)
            buf = []
            i += 1
            continue
        buf.append(ch)
        i += 1
    item = "".join(buf).strip()
    if item:
        out.append(item)
    return out


def _is_principal_superseded(repo_root: Path | str, unit: str, row: dict) -> bool:
    """True when a verdict row's attribution is retired by a PRINCIPAL-authorised supersession -
    the only kind that stops the row's reviewer counting toward independence. This re-checks the
    recorded supersession at READ time (record_supersession refuses at write time, but a
    hand-appended record walks round the tool):
    the correction must name a boundary, its authoriser must not be the row's own author, and the
    authoriser must not itself have done in-session review work on the unit (judged excluding this
    row). An author-reachable or boundary-less correction retires the VERDICT but not the fact
    that the named reviewer acted, so the gate keeps counting them."""
    if not row.get("superseded"):
        return False
    if not (row.get("superseded_boundary") or "").strip():
        return False
    authoriser = _id(row.get("superseded_by", ""))
    if not authoriser or authoriser == _id(row.get("author", "")):
        return False
    return authoriser not in _adversarial_worker_ids(repo_root, unit, exclude_row=row)


def session_reviewer_ids(repo_root: Path | str, unit: str) -> set[str]:
    """Every reviewer id recorded on the unit's verdict and sprint-level-review rows.
    A principal drawn from this set is a reviewer signing off its own review (or the author's
    proxy), and `sprint sign` refuses it: the reviewer of record must differ from BOTH the
    author and the adversarial reviewer, per-unit or sprint-scope alike.

    A superseded row STILL CONTRIBUTES unless the supersession was PRINCIPAL-authorised
    (`_is_principal_superseded`). Superseding retires a VERDICT; it cannot un-make the historical
    fact that the named reviewer acted - so an author-reachable correction leaves the reviewer
    counting. That closes the bypass an unconditional exclusion opened (author supersedes the
    REJECT blocking it, its seat drops out, its own subagent signs off - refused, superseded,
    accepted, measured end to end). The one attribution that IS retired is a principal's
    correction of a MIS-FILED row - a reviewer wrongly named who did no other reviewing work -
    which is what un-strands the unit the incident stranded."""
    target = sdlc_md.norm_id(unit)
    ids: set[str] = set()
    for phase in PHASES:  # BOTH verdict phases - a plan-review seat is still the author's spawn
        for v in read_verdicts(repo_root, phase):
            if sdlc_md.norm_id(v["unit"]) != target:
                continue
            if _is_principal_superseded(repo_root, unit, v):
                continue  # a principal-authorised correction retires the attribution too
            ids.add(_id(v["reviewer"]))
    for sr in sprint_reviews(repo_root):  # a sprint-level review covering this unit
        if target in _covered_ids(sr):
            ids.add(_id(sr["reviewer"]))
    ids.discard("")
    return ids


# --- Sprint-level review (frozen: read, never written) -----------------------------------
# A closing full-diff pass once covered a batch at once, recorded as one row naming the units.
# No verb writes the ledger now: a unit is reviewed by its own delivery verdict. It is the only
# record that some historical Done units were reviewed, so it is still READ, frozen - a row dated
# before `REPAIR_VERB_RETIRED` covers the units it names, and a later row covers nothing
# (`sprint_reviews`). Coverage NEVER overrides a per-unit REJECT.
_SPRINT_FILE = "sprint-review-record.md"
_SPRINT_COLS = ("base", "reviewer", "author", "verdict", "date", "units", "findings")


def sprint_review_path(repo_root: Path | str) -> Path:
    return Path(repo_root) / "sdlc-studio" / "reviews" / _SPRINT_FILE


#: A goal clause's possible verdicts. `partial` exists because a goal with more than one clause
#: is routinely reached in part, and collapsing that to achieved-or-missed forces the closer to
#: overstate or understate. The vocabulary is closed: an unrecognised verdict is refused rather
#: than stored, or the close would report a word nothing downstream can read.
GOAL_VERDICTS = ("achieved", "partial", "missed")


def goal_panel(repo_root: Path | str, clauses: list[str], seats: list[str], author: str,
               verdicts: dict | None = None) -> dict:
    """A per-clause verdict on the Sprint Goal from a panel of seats the AUTHOR IS NOT ON.

    The author is REFUSED from the panel rather than warned about. A warning is advice, and the
    whole value of the judgement is that it was not made by the person whose work is being
    judged - the two-role rule at close exists for the same reason, and a goal verdict the
    author signed is the one place that rule was never applied.

    Each clause carries the EVIDENCE the panel relied on, not only its word. A verdict with no
    evidence behind it cannot be reviewed later, and this project has twice recorded a
    completion claim that reading the evidence would have refused.
    """
    clauses = [c.strip() for c in (clauses or []) if str(c).strip()]
    if not clauses:
        raise ValueError("a goal panel needs at least one clause to judge - a goal nobody broke "
                         "into clauses is judged as one clause, never as none")
    panel = [s.strip() for s in (seats or []) if str(s).strip()]
    if not panel:
        raise ValueError("a goal panel needs at least one seat - an empty panel returns a "
                         "verdict nobody gave")
    if not (author or "").strip():
        raise ValueError("a goal panel needs the AUTHOR named, so it can prove the author is "
                         "not on it - an unnamed author cannot be excluded")
    conflicted = [s for s in panel if _id(s) == _id(author)]
    if conflicted:
        raise ValueError(
            f"goal panel refused: {', '.join(conflicted)} is the author - a panel including the "
            f"author is the author marking their own homework, which is the one thing this "
            f"judgement exists to prevent. Convene seats outside the authoring context")
    supplied = verdicts or {}
    # A key matching no clause is REFUSED, not dropped. `supplied.get(clause)` is keyed by the
    # stripped clause text, so a key differing by case or a trailing space took a seat's
    # `missed` and silently made it an unanswered `partial` - the same class as an unrecognised
    # verdict word, which this function already refuses rather than ignores.
    unmatched = [k for k in supplied if k not in clauses]
    if unmatched:
        raise ValueError(
            f"goal panel refused: verdict key(s) {unmatched!r} match no clause of this goal "
            f"({clauses!r}) - a key that matches nothing drops the verdict behind it without "
            f"a word, which is how a `missed` becomes a `partial`")
    out: list[dict] = []
    for clause in clauses:
        given = supplied.get(clause) or {}
        rows = []
        for seat in panel:
            entry = given.get(seat)
            if entry is None:
                rows.append({"seat": seat, "verdict": None, "evidence": ""})
                continue
            if isinstance(entry, str):
                entry = {"verdict": entry, "evidence": ""}
            v = str(entry.get("verdict", "")).strip().lower()
            if v not in GOAL_VERDICTS:
                raise ValueError(
                    f"{seat} returned {entry.get('verdict')!r} for {clause!r} - a clause verdict "
                    f"must be one of {', '.join(GOAL_VERDICTS)}")
            rows.append({"seat": seat, "verdict": v,
                         "evidence": str(entry.get("evidence", "")).strip()})
        answered = [r for r in rows if r["verdict"]]
        if not answered:
            verdict = None
        elif all(r["verdict"] == "achieved" for r in answered):
            verdict = "achieved"
        elif all(r["verdict"] == "missed" for r in answered):
            verdict = "missed"
        else:
            # Disagreement is PARTIAL, never the majority word. A clause one seat says was
            # missed is not achieved because two others disagree; reporting the majority would
            # let a dissent vanish into a number.
            verdict = "partial"
        out.append({"clause": clause, "verdict": verdict, "seats": rows,
                    "evidence": [r["evidence"] for r in rows if r["evidence"]],
                    "unanswered": [r["seat"] for r in rows if not r["verdict"]]})
    # None when NOTHING was answered. This function raises on an empty seat list precisely
    # because "an empty panel returns a verdict nobody gave", and then returned `partial` for a
    # panel where no seat answered a single clause - which is the same verdict nobody gave,
    # reached by a different route.
    answered = [c for c in out if c["verdict"]]
    overall = (None if not answered
               else "achieved" if all(c["verdict"] == "achieved" for c in out)
               else "missed" if all(c["verdict"] == "missed" for c in out)
               else "partial")
    return {"author": author, "panel": panel, "clauses": out, "verdict": overall}


#: Priorities that describe a defect a release cannot carry. Read as a FLOOR: a defect at
#: one of these blocks a close whatever the clause reasoning says, because "the goal was met
#: anyway" is not an answer to a user who cannot work around it.
#: Priority and severity words ordered MOST SEVERE FIRST, across the vocabularies projects
#: actually use. One ordering rather than a list of blocking words: a flat list has to remember
#: every synonym, and the one this shipped with remembered `p0/p1/critical/blocker` while this
#: corpus files 104 `Severity: High` bugs and an adversarial reviewer writes `major`. Every one
#: of them was leavable.
#: TIERS, not a flat order: `high` and `major` are the same severity written by two different
#: readers (a bug filer and an adversarial reviewer), and an ordering that puts one below the
#: other makes the cut depend on which word someone happened to type.
PRIORITY_TIERS = (
    ("p0", "sev0", "blocker", "critical"),
    ("p1", "sev1", "high", "major"),
    ("p2", "sev2", "medium", "moderate", "normal"),
    ("p3", "sev3", "low", "minor", "trivial", "nice-to-have"),
)
PRIORITY_ORDER = tuple(word for tier in PRIORITY_TIERS for word in tier)

#: The default cut, INCLUSIVE: every word at or above it blocks. A project moves the cut with
#: `review.blocking_priority` in `.config.yaml` - one value to set, rather than a list to keep
#: in step with its own vocabulary.
BLOCKING_CUT = "high"


def blocking_priorities(repo_root: Path | str | None = None) -> tuple:
    """Every priority word at or above this project's blocking cut.

    DERIVED from `PRIORITY_ORDER` and one cut, so a project that files High/Medium/Low and one
    that files P0..P3 are both covered without either being enumerated here. An unrecognised
    cut falls back to the shipped default rather than to an empty floor: a floor nobody
    configured must not silently become no floor at all."""
    cut = BLOCKING_CUT
    if repo_root is not None:
        declared = sdlc_md.project_override(repo_root, "review.blocking_priority", None)
        if declared and _normalise_priority(str(declared)) in PRIORITY_ORDER:
            cut = _normalise_priority(str(declared))
    depth = next(i for i, tier in enumerate(PRIORITY_TIERS) if cut in tier)
    return tuple(word for tier in PRIORITY_TIERS[:depth + 1] for word in tier)


_PRIORITY_DECORATION = re.compile(r"[^a-z0-9-]+")


def _normalise_priority(value: str) -> str:
    """`"High (severity)"`, `" **P1** "`, `"Sev-1"` -> the bare word the ordering knows.

    A decorated field value compared raw is a value that never matches, which is half of why
    the floor never fired."""
    text = _PRIORITY_DECORATION.sub(" ", str(value or "").strip().lower()).strip()
    for token in text.split():
        # Both spellings of a hyphenated tier word: `sev-1` and `sev1`, `nice-to-have` intact.
        # Trying only one is how half a vocabulary goes unrecognised.
        for candidate in (token.strip("-"), token.replace("-", "")):
            if candidate in PRIORITY_ORDER:
                return candidate
    return text.split()[0] if text.split() else ""


#: Kept as the shipped default for callers that ask for the constant. Derived, never typed.
BLOCKING_PRIORITIES = blocking_priorities(None)


def judge_defects_against_goal(defects: list[dict], clauses: list[str],
                               repo_root: Path | str | None = None) -> dict:
    """Which open defects BLOCK a close and which can be left, judged against the goal.

    `{blocking, leavable}`. A defect blocks when it falsifies a goal clause - it names one, or
    an explicit `falsifies` says so - or when its priority is one a release cannot carry.
    Everything else is LEAVABLE and recorded with its priority and the reasoning, never
    silently dropped: the decision to ship with a known defect is a decision, and one nobody
    wrote down is indistinguishable from not having noticed.

    The severity floor exists because a clause argument can be made for almost anything. A
    defect at P0/P1 blocks whatever the reasoning says.
    """
    lowered = [c.strip().lower() for c in (clauses or []) if str(c).strip()]
    floor = blocking_priorities(repo_root)
    blocking, leavable = [], []
    for d in defects or []:
        priority = _normalise_priority(d.get("priority") or d.get("severity") or "")
        named = str(d.get("falsifies") or "").strip().lower()
        clause = next((c for c in lowered if named and (named in c or c in named)), None)
        if clause is None and named:
            clause = named          # names a clause this goal does not carry: still a claim
        if clause:
            blocking.append({**d, "why": f"falsifies the goal clause: {clause}"})
        elif priority in floor:
            blocking.append({**d, "why": f"priority {priority} - a defect a release cannot "
                                         f"carry blocks the close whatever the clause "
                                         f"reasoning says"})
        else:
            leavable.append({**d, "why": f"falsifies no goal clause; priority "
                                         f"{priority or 'unstated'} - recorded leavable, not "
                                         f"dropped"})
    return {"blocking": blocking, "leavable": leavable}


def sprint_reviews(repo_root: Path | str) -> list[dict]:
    """The frozen batch-review rows that still count: those dated before `REPAIR_VERB_RETIRED`.

    THE one read of the ledger, so every reader - conformance, the close, the sign, the report
    and `sprint_review_for` - applies the same date licence. The ledger's last row predates the
    constant, so it reuses the repair ledger's day rather than pinning a second one. An undated
    row, or one dated on or after the constant, covers nothing: no verb writes one now, and a
    hand-appended row cannot mint coverage for new work.
    """
    return [r for r in _read_rows(sprint_review_path(repo_root), _SPRINT_COLS)
            if _dated_before(r.get("date"), REPAIR_VERB_RETIRED)]


def _dated_before(cell, day: str) -> bool:
    """True when a row's Date cell is an ISO date strictly before `day`; blank or unparseable
    reads False, so an undated row is never taken for history."""
    when = str(cell or "").strip()[:10]
    return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", when)) and when < day


#: Two REJECTs on one unit is the point at which the repair has stopped converging.
PANEL_REJECT_LIMIT = 2


def review_rounds_across_ledgers(repo_root: Path | str, unit: str,
                                 phase: str = "delivery") -> list[dict]:
    """Every recorded adversarial round on one unit, from BOTH ledgers, oldest first.

    A unit's rounds live in two files and the question "has this stopped converging" spans them:
    `critic.py record` appends to `critic-verdicts.md`, and the frozen batch ledger
    (`sprint-review-record.md`, read through `sprint_reviews`) still holds historical batch rows
    naming the unit. Escalation once read the first only, so two batch REJECT rounds on one unit
    escalated nothing.

    Deliberately NOT folded into `unit_review_rounds`, which feeds `seat_verdicts` and the
    coverage predicate. Those ask "which seat holds what verdict on this unit" - a per-unit
    question a batch row cannot answer, because a batch reviewer reviewed a span rather than a
    seat's slice of one unit. Two questions, two readers, and the difference is stated here so
    the next reader does not merge them by tidiness.
    """
    want = sdlc_md.norm_id(unit)
    rows = list(unit_review_rounds(repo_root, unit, phase))
    if phase == "delivery":
        for row in sprint_reviews(repo_root):
            named = {sdlc_md.norm_id(u) for u in str(row.get("units") or "").split()}
            if want in named:
                rows.append({"unit": want, "verdict": row.get("verdict"),
                             "reviewer": row.get("reviewer"), "date": row.get("date"),
                             "ledger": "sprint-review"})
    rows.sort(key=lambda r: str(r.get("date") or ""))
    return rows


def panel_escalation(rounds: list, seat_verdicts: dict) -> tuple[bool, str]:
    """Whether a unit must go to the operator, and why.

    NOTIFIES, never waits. Human-in-the-lead means the decision reaches the operator; it does
    not mean the machine blocks on input that will not arrive. An escalation that waits is
    indistinguishable from a hang, and unattended that is exactly what it becomes.

    Lives here, beside the ledgers it judges, so the command that records a round - `critic
    record`, the one verdict writer - consults one rule rather than a copy of it.

    `sprint.panel_escalation` delegates here and now has no production caller of its own - it is
    kept as a named shim because tests and any consuming project may still reach for it.
    """
    verdicts = [str(v).upper() for v in (rounds or [])]
    # CONVERGENCE ENDS THE ESCALATION, and it is checked before anything else.
    #
    # Both escalations below read the WHOLE history, so once two REJECTs existed they fired on
    # every later record for that unit - including the APPROVE that resolved them. The ordinary
    # reject-fix-approve loop, which is the process working, reported "the repair is not
    # converging" at the moment it demonstrably had. Eight units did this in one run: every one
    # had a round-1 REJECT with substantive findings, a revision, and a round-2 approval.
    #
    # It also explains the sibling defect: a second ROUND is a different context reviewing a
    # revised unit, not a panel SPLIT within one round. Reading the latest verdict tells the two
    # apart without having to reconstruct round boundaries from free-text reviewer names.
    #
    # A notice that fires after it has been answered is one readers learn to scroll past, and
    # then it is not there for the unit that genuinely stalled.
    if verdicts and verdicts[-1] == APPROVE:
        return (False, "")
    rejects = sum(1 for v in verdicts if v == REJECT)
    if rejects >= PANEL_REJECT_LIMIT:
        return (True, f"the panel rejected this unit twice ({rejects} REJECTs) - the repair is "
                      f"not converging. The operator is NOTIFIED and the run continues to its "
                      f"handoff; nothing waits on a reply.")
    seats = {k: str(v).upper() for k, v in (seat_verdicts or {}).items() if v}
    if len(set(seats.values())) > 1:
        # The disagreement IS the signal. Resolving it by majority discards precisely the
        # information the panel was convened to produce, and does so where nobody sees it.
        dissent = sorted(k for k, v in seats.items() if v == REJECT)
        agree = sorted(k for k, v in seats.items() if v != REJECT)
        return (True, f"the panel split: {', '.join(dissent) or 'some seats'} rejected while "
                      f"{', '.join(agree) or 'others'} approved. The disagreement is the "
                      f"finding, so it is not resolved by majority - the operator is NOTIFIED "
                      f"with both sides named.")
    return (False, "")


def escalation_notice(repo_root: Path | str, unit: str, phase: str = "delivery") -> str:
    """The escalation line for one unit, or "" - the whole check in one call.

    Both recording commands call THIS rather than assembling the rounds themselves, because the
    defect being repaired was precisely that the caller assembled them from the wrong ledger.
    """
    rounds = [str(r.get("verdict") or "")
              for r in review_rounds_across_ledgers(repo_root, unit, phase)]
    escalate, why = panel_escalation(rounds, seat_verdicts(repo_root, unit, phase))
    return f"  ESCALATED to the operator - {sdlc_md.norm_id(unit)}: {why}" if escalate else ""


# One reviewer, at most this many rounds per unit: round 1 reviews, round 2 re-checks the fixes.
# A unit still rejected at the cap is carried as a known issue rather than reviewed again.
DEFAULT_REVIEW_CEILING = 2


def review_ceiling(repo_root: Path | str) -> int:
    """The review round cap (`review.max_rounds`), or the shipped default of 2.

    A non-integer or non-positive setting falls back to the default: a cap of 0 would refuse
    the first round and leave no way to review anything."""
    raw = sdlc_md.project_override(repo_root, "review.max_rounds", DEFAULT_REVIEW_CEILING)
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return DEFAULT_REVIEW_CEILING
    return value if value > 0 else DEFAULT_REVIEW_CEILING


def round_refusal(repo_root: Path | str, unit: str, reviewer: str) -> str | None:
    """Why a further delivery verdict on `unit` by `reviewer` must not be written, or None.

    Two rules: no round past the cap, and a round after a REJECT comes from the reviewer who
    rejected, because it re-checks that reviewer's findings. Shared by every command that
    writes a delivery verdict, so the rules cannot differ between them."""
    prior = delivery_rounds(repo_root, unit)
    cap = review_ceiling(repo_root)
    uid = sdlc_md.norm_id(unit)
    if len(prior) >= cap:
        return (f"{uid} has {len(prior)} review round(s) recorded, at the cap of {cap} "
                f"(`review.max_rounds`). A unit still rejected at the cap is carried as a known "
                f"issue, not reviewed again")
    last = prior[-1] if prior else None
    if (last and str(last.get("verdict") or "").upper() == REJECT
            and not same_identity(last.get("reviewer", ""), reviewer or "")):
        return (f"round {len(prior) + 1} of {uid} re-checks the fixes to "
                f"{last.get('reviewer')}'s REJECT, so it must be recorded by "
                f"{last.get('reviewer')}, not {reviewer}")
    return None


CARRIED_REASON = "carried at the review cap"
#: The two ways a standing REJECT ends, named by every refusal that holds one.
REJECT_EXITS = ("a round-2 APPROVE from the reviewer who rejected, or carrying the unit at the "
                "review cap: that reviewer's round-2 REJECT, recorded in the open run, files the "
                "findings as a bug and drops the unit from the batch, so the run closes without "
                "it. A carried unit is still refused Done: it is delivered again in a later run "
                "and reaches Done on an APPROVE from the reviewer who rejected it (the same "
                "reviewer id)")


class CarryFailed(RuntimeError):
    """A REJECT at the cap WAS written, and carrying the unit then failed. Not a refusal: the
    row stands, so no writer may report the verdict as unwritten."""


def carried_notice(unit: str, bug: str) -> str:
    return (f"  {sdlc_md.norm_id(unit)} {CARRIED_REASON}: {bug} holds the findings, and the "
            f"unit leaves the open run's batch so the run continues")


def _carry_if_capped(repo_root: Path | str, unit: str, verdict: str, path: Path,
                     rounds: list[dict] | None = None) -> str | None:
    """Carry `unit` when the delivery verdict just written is a REJECT at the cap: the bug's
    id, or None when nothing is carried. Raises `CarryFailed` naming the written row."""
    if str(verdict or "").upper() != REJECT:
        return None
    rounds = delivery_rounds(repo_root, unit) if rounds is None else rounds
    if not rounds or len(rounds) < review_ceiling(repo_root):
        return None
    try:
        return carry_at_cap(repo_root, unit, rounds[-1])
    except Exception as exc:  # noqa: BLE001 - any failure here follows a written row
        raise CarryFailed(
            f"{sdlc_md.norm_id(unit)}'s round {len(rounds)} REJECT WAS written to {path}, but "
            f"carrying it at the review cap failed: {exc}. The unit stays in the open run's "
            f"batch with that REJECT unanswered: file its findings as a bug and drop it from "
            f"the batch (`sprint batch drop`) by hand") from exc


def carry_at_cap(repo_root: Path | str, unit: str, row: dict) -> str | None:
    """File the findings of a REJECT recorded at the cap as a bug, and drop the unit from the
    open run's batch naming it. Returns the bug id, or None when no open run holds the unit:
    there is then no run to keep going, and the REJECT stands against the unit as it is. The
    run keeps going: the unit becomes a known issue instead of a third round."""
    uid = sdlc_md.norm_id(unit)
    if not run_state.batch_holds(run_state.read(repo_root) or {}, uid):
        return None
    import file_finding  # noqa: PLC0415 - needed only when a unit is carried
    issues = str(row.get("issues") or "").strip(" -") or "(the REJECT itemised no findings)"
    # The fix lands where the unit did, at the unit's own size: the filer refuses a bug that
    # `sprint plan` could not size or place, and a planned unit carries both.
    found = sdlc_md.find_by_id(repo_root, uid)
    text = sdlc_md.read_text_safe(found[0]) if found else ""
    res = file_finding.file_finding(repo_root, "bug", f"{uid} did not converge in review: "
                                    f"round {row.get('round')} REJECT findings", {
        "affects": sdlc_md.extract_field(text, "Affects") or "",
        "points": sdlc_md.extract_field(text, "Points") or "",
        "severity": "Medium",
        "summary": (f"{uid} was rejected at round {row.get('round')}, the review cap, by "
                    f"{row.get('reviewer')}, so it was carried as a known issue rather than "
                    f"reviewed again. The findings still open: {issues}"),
        "steps": f"1. Read the round {row.get('round')} REJECT of {uid} in the verdict ledger.",
        "fix": f"Fix each finding above, then deliver {uid} again in a later run.",
    })
    bug = res["id"]
    run_state.drop_from_batch(repo_root, uid, f"{CARRIED_REASON}: {bug}")
    return bug


def carried_to(repo_root: Path | str, unit: str, reason: str,
               state: dict | None = None) -> str | None:
    """The bug a batch drop of `unit` carried its findings to, or None when the drop is not a
    carry. `carry_at_cap` writes the reason; this is its one reader. A drop counts only when its
    reason is `CARRIED_REASON: <bug>`, the unit's current delivery stands at the cap with a
    REJECT as its last round, and the bug is on disk: a hand drop worded like a carry answers
    no REJECT."""
    prefix = f"{CARRIED_REASON}:"
    reason = str(reason or "")
    if not reason.startswith(prefix):
        return None
    rounds = delivery_rounds(repo_root, unit, state)
    if (len(rounds) < review_ceiling(repo_root)
            or str(rounds[-1].get("verdict") or "").upper() != REJECT):
        return None
    bug = sdlc_md.norm_id(reason[len(prefix):].strip())
    found = sdlc_md.find_by_id(repo_root, bug) if bug else None
    return bug if found and found[1] == "bug" else None


# How a round-N finding relates to round N-1's repair. The distinction is the whole point:
# a FRESH finding says the review is still earning its cost, a REPAIR_REGRESSION says the
# repair loop is manufacturing the defects the review is being paid to catch, and those two
# call for opposite responses. UNCLASSIFIED is neither, and is never quietly folded into
# FRESH - a regression hidden inside the fresh count is the failure this exists to prevent.
# The ORIGIN axis: does this finding predate the run's base ref? A DIFFERENT question from the
# `class` axis below, and deliberately not merged with it. `REPAIR_REGRESSION` means "the repair
# broke it"; `ORIGIN_REGRESSION` means "this unit's diff broke it". The word appears on both and
# means different things, so they carry different names and the coverage gate reads `origin`.
# An independent engineering seat found the collision at goal review; without the separate name
# a second classifier would have been built on top of one CR0510 reports as effectively dead.
ORIGIN_REGRESSION = "regression"      # the diff broke something that worked at the base ref
ORIGIN_NEW = "new"                    # the diff introduced a defect that did not exist
ORIGIN_PRE_EXISTING = "pre-existing"  # already true of the tree at the base ref
ORIGINS = (ORIGIN_REGRESSION, ORIGIN_NEW, ORIGIN_PRE_EXISTING)

#: How a finding declares its origin in an `--issues` string: a leading `[origin]` tag on each
#: semicolon-separated item. The findings channel is free text everywhere it is written, so the
#: tag rides on the text rather than requiring a second parallel field the writers would have to
#: keep in step.
#: The optional `BLOCKING:` prefix is the TOOL's own doing, not the reviewer's: `--from-verdict`
#: folds the block's BLOCKING section into the issues text, so an item that arrived correctly
#: tagged reaches the parser behind that label. Refusing it would refuse a compliant reviewer
#: for something the parser did to their answer.
_ORIGIN_TAG = re.compile(
    r"^\s*(?:BLOCKING\s*:\s*)?\[\s*(regression|new|pre[- ]existing)\s*\]\s*(.*)$",
    re.IGNORECASE | re.DOTALL)

#: What a clean pass says. An APPROVE finding nothing is the common case and must stay legal,
#: or the rule is satisfiable by a gate that refuses every clean review.
_NO_FINDINGS = ("", "-", "none", "none blocking", "no findings", "n/a", "na")


def parse_findings(issues: str) -> list[dict]:
    """Split an `--issues` string into findings, each with its declared `origin`.

    An item with no `[origin]` tag comes back with `origin: None`, which is what
    `unclassified_findings` refuses on. Absent is kept distinct from any real value: guessing
    an origin is exactly the judgement the classification exists to force somebody to make.
    """
    text = (issues or "").strip()
    if text.lower() in _NO_FINDINGS:
        return []
    out = []
    for item in split_items(text):
        m = _ORIGIN_TAG.match(item)
        if m:
            origin = m.group(1).lower().replace(" ", "-")
            out.append({"origin": origin, "text": m.group(2).strip()})
        else:
            out.append({"origin": None, "text": item})
    return out


def unclassified_findings(issues: str) -> list[str]:
    """The findings carrying no origin - the ones a close cannot price against a batch."""
    return [f["text"] for f in parse_findings(issues) if f["origin"] is None]


def blocking_findings(issues: str) -> list[dict]:
    """Only regression and new. A pre-existing finding is reported, never blocking."""
    return [f for f in parse_findings(issues)
            if f["origin"] in (ORIGIN_REGRESSION, ORIGIN_NEW)]


def non_blocking_findings(issues: str) -> list[dict]:
    return [f for f in parse_findings(issues) if f["origin"] == ORIGIN_PRE_EXISTING]


#: A finding that repeats a recorded failure class cites its code anywhere in its text, after
#: the origin tag: `[new] the mutant was never applied [LC-003]`.
LESSON_CITE_RE = re.compile(r"\[\s*(LC-\d{3,})\s*\]", re.IGNORECASE)


def cited_lessons(repo_root: Path | str, state: dict) -> list[tuple[str, str, str]]:
    """`(class code, unit, finding)` for each REJECT the run in `state` recorded whose findings
    cite a lesson class, once per (code, unit); `finding` is the text of every finding that
    cited it, so the class's hits carry the evidence and not only a pointer to it. Only a unit
    the run reviewed counts - its rows past the `REVIEW_BASE` the run fixed - so an APPROVE, or
    a REJECT an earlier run recorded, is never read as this run's repeat."""
    found: dict[tuple[str, str], list[str]] = {}
    for unit in (state or {}).get("batch") or []:
        uid = sdlc_md.norm_id(unit)
        if uid not in ((state or {}).get(run_state.REVIEW_BASE) or {}):
            continue
        for row in delivery_rounds(repo_root, uid, state):
            if str(row.get("verdict") or "").upper() != REJECT:
                continue
            for f in parse_findings(row.get("issues") or ""):
                for code in LESSON_CITE_RE.findall(f["text"]):
                    texts = found.setdefault((code.upper(), uid), [])
                    if f["text"] not in texts:
                        texts.append(f["text"])
    return [(code, uid, "; ".join(texts)) for (code, uid), texts in found.items()]


FRESH = "fresh"
REPAIR_REGRESSION = "repair-regression"
UNCLASSIFIED = "unclassified"


def _spans(entry: dict) -> list[tuple[int, int]]:
    """The (start, end) line spans of one repaired-file entry, malformed pairs dropped."""
    out = []
    for pair in entry.get("lines") or []:
        try:
            start, end = int(pair[0]), int(pair[1])
        except (TypeError, ValueError, IndexError):
            continue
        out.append((start, end) if start <= end else (end, start))
    return out


def classify_finding(repo_root: Path | str, file: str | None = None,
                     line: int | None = None) -> dict:
    """Classify a finding against the PREVIOUS round's repair surface.

    Compared against the latest recorded round only. An earlier round's surface has already
    been re-reviewed by the round after it, so a finding there now is a fresh miss rather
    than a defect the last repair created.

    Matching is file AND line, not file alone: single files here run to thousands of lines,
    and a file-level match would classify nearly every finding as a regression, which would
    make the signal useless in exactly the case it exists for."""
    rounds = run_state.review_rounds(repo_root)
    if not rounds:
        return {"class": FRESH, "round": None, "file": file, "line": line,
                "reason": "no prior round: there is no repair surface to regress against"}
    if not file or line is None:
        return {"class": UNCLASSIFIED, "round": None, "file": file, "line": line,
                "reason": "the finding has no parseable file and line, so it cannot be placed "
                          "inside or outside the previous round's repair surface"}
    try:
        line = int(line)
    except (TypeError, ValueError):
        return {"class": UNCLASSIFIED, "round": None, "file": file, "line": line,
                "reason": f"the finding's line {line!r} is not a number"}
    last = rounds[-1]
    target = Path(str(file)).name
    for entry in last.get("repaired") or []:
        if not isinstance(entry, dict) or Path(str(entry.get("file", ""))).name != target:
            continue
        for start, end in _spans(entry):
            if start <= line <= end:
                return {"class": REPAIR_REGRESSION, "round": last.get("round"),
                        "file": file, "line": line,
                        "reason": f"{target}:{line} lies in the surface round "
                                  f"{last.get('round')}'s repair touched ({start}-{end})"}
    return {"class": FRESH, "round": last.get("round"), "file": file, "line": line,
            "reason": f"{target}:{line} lies outside round {last.get('round')}'s repair surface"}


# An acceptance criterion CORRECTED during delivery is a spec defect, not an ordinary revision.
# Counting it as a normal edit hides the most expensive class of defect this project has found: a
# criterion that specified the WRONG behaviour, which a passing test then defends (US0375 asked the
# sign-off gate to ignore a superseded row - that IS the independence-gate bypass, and the test
# asserted it as a requirement). An absence and a negative result are different facts: a story with
# no AC amendment is not the same as one whose criterion was found wrong and fixed, and folding the
# amendment into the ordinary-revision count erases the distinction the retro then cannot recover.
AC_DEFECT = "ac-defect"
ORDINARY_REVISION = "revision"

# A change is an AC DEFECT when it says a criterion was CORRECTED - not merely touched. Adding,
# rewording, renumbering or clarifying a criterion is an ordinary revision; a criterion that stated
# the wrong behaviour and was amended is a spec failure. Detection needs BOTH a reference to a
# criterion AND a correction-of-wrong-spec verb, so "reworded AC1 for clarity" stays ordinary; an
# explicit `AC-DEFECT` tag an author sets is honoured directly. A trivial correction (a typo) is
# excluded even when it carries a correction verb, so the class stays the expensive one.
_AC_REF = re.compile(r"\b(?:AC\s*\d+|acceptance\s+criteri|criterion|criteria)\b", re.I)
_CORRECTION = re.compile(r"\b(?:correct(?:ed|s|ion)?|amend(?:ed|s|ment)?|wrong|incorrect|"
                         r"mis-?specified|misstated|found\s+wrong|specified\s+the\s+wrong)\b", re.I)
_CLARIFY_ONLY = re.compile(r"\b(?:typo|whitespace|formatting|grammar|spelling|reworded?\s+for\s+"
                           r"clarity|clarif\w*\s+wording)\b", re.I)
_AC_DEFECT_TAG = re.compile(r"\bAC[-\s]?DEFECT\b", re.I)
_REV_HEADING = re.compile(r"^##\s+Revision History\s*$", re.M | re.I)


def classify_revision(change: str) -> str:
    """Classify one Revision History change line as an AC DEFECT or an ordinary revision.

    An explicit `AC-DEFECT` tag is honoured directly. Otherwise the change is an AC defect only
    when it both references a criterion and carries a correction-of-wrong-spec verb, and is not a
    purely cosmetic correction (a typo). Everything else - a clarification, a new criterion, a
    reorder - is an ordinary revision. The point is to keep a wrong-spec correction from being
    counted as a normal edit."""
    text = change or ""
    if _AC_DEFECT_TAG.search(text):
        return AC_DEFECT
    if _AC_REF.search(text) and _CORRECTION.search(text) and not _CLARIFY_ONLY.search(text):
        return AC_DEFECT
    return ORDINARY_REVISION


def ac_defects(source: str | Path) -> list[dict]:
    """The AC-defect rows in a story's Revision History - each an amendment that corrected a wrong
    criterion, classified apart from the ordinary revisions beside it.

    `source` is a story's text or a path to it. Returns one record per AC-defect row, each with its
    date, author and the change text, so a caller (a retro, a close count) can report the AC defects
    a unit carried without re-deriving the rule. Rows outside the Revision History section are
    ignored - only the history table records amendments."""
    text = Path(source).read_text(encoding="utf-8") if isinstance(source, Path) else str(source)
    m = _REV_HEADING.search(text)
    body = text[m.end():] if m else text
    out: list[dict] = []
    for table in sdlc_md.iter_tables(body):
        header = [h.lower() for h in (table["header"] or [])]
        if "change" not in header:
            continue
        ci = header.index("change")
        di = header.index("date") if "date" in header else 0
        ai = header.index("author") if "author" in header else 1
        for _lineno, cells in table["rows"]:
            if len(cells) <= ci:
                continue
            change = cells[ci]
            if classify_revision(change) == AC_DEFECT:
                out.append({
                    "date": cells[di] if di < len(cells) else "",
                    "author": cells[ai] if ai < len(cells) else "",
                    "change": change,
                    "class": AC_DEFECT,
                })
    return out


# What must never reach a reviewer's brief, because it predicts a conclusion rather than
# describing the work: the prior verdict words, severity labels that pre-grade what will be
# found, a round number (which says "others already rejected this"), and any sentence asserting
# what the reviewer is about to conclude. Checked mechanically, so a future edit that
# reintroduces priming fails the suite rather than relying on a reader noticing.
_PRIMING = (
    (re.compile(r"\b(REJECT|APPROVE)\b"), "a prior verdict word"),
    (re.compile(r"\b(MAJOR|MINOR|BLOCKING)\b"), "a severity label that pre-grades the finding"),
    (re.compile(r"(?i)\bround\s*\d+\b"), "a round number"),
    (re.compile(r"(?i)the pattern will continue|you will find|expect to find|"
                r"as in the previous round"), "an asserted conclusion"),
)

# A probe is a thing the reviewer must RE-EXECUTE: a test path or node, or a file:line the
# prior round mutated. These are facts, and they must survive into a re-review - the round-2
# APPROVE this project trusts was earned by a reviewer re-running exactly these. What must not
# survive is the prose around them.
_PROBE = re.compile(r"(?:[\w./-]+\.(?:py|sh|ts|js|go|md)(?::\d+)?"
                    r"(?:::[\w:]+)?|\b(?:pytest|jest|vitest|go test)\s+[\w./:-]+)")


def neutrality_violations(text: str) -> list[str]:
    """Every priming class present in `text`. Empty means the brief is neutral.

    The RETURN CONTRACT is excluded before checking. It necessarily contains both verdict words
    and the BLOCKING label, because it is the reply format the reviewer must follow - offering
    the vocabulary as a required choice is not priming, and stripping it to satisfy this check
    would break the contract. Priming is a prior verdict ASSERTED, which is what remains once
    the contract is removed.

    Mechanical by design: a reviewer's impression of neutrality is exactly the judgement this
    exists to remove from the loop."""
    body = (text or "").replace(_RETURN_CONTRACT, "")
    return [why for rx, why in _PRIMING if rx.search(body)]


def extract_probes(prior_verdict_text: str) -> list[str]:
    """The probes a prior verdict named, as a bare list of things to re-execute.

    Refuses loudly when none can be extracted. A re-review that silently dropped the
    re-execution demand would approve against a brief WEAKER than the one it replaced, which
    is worse than the priming this strips - so absence is an error, never an empty list."""
    found, seen = [], set()
    for m in _PROBE.finditer(prior_verdict_text or ""):
        probe = m.group(0)
        if probe not in seen:
            seen.add(probe)
            found.append(probe)
    if not found:
        raise ValueError(
            "no probe could be extracted from the prior verdict - a re-review must carry the "
            "checks to re-execute, and one that drops them silently is weaker than the review "
            "it replaces. Name the tests and file:line mutants in the verdict, or run a fresh "
            "review rather than a re-review.")
    return found


def neutral_brief(repo_root: Path | str, unit: str, seat: str, tier: str = "full",
                  prior: str | None = None, round_number: int | None = None) -> str:
    """The reviewer's brief, carrying the diff and risk surface but none of the framing that
    predicts a conclusion.

    `round_number` is accepted and deliberately NOT rendered: callers hold it, and silently
    ignoring an argument would be worse than refusing one - this way the caller cannot leak it
    by passing it. When `prior` is given, the probes it named travel as a neutral checklist;
    the verdict prose, severity labels and conclusions around them do not."""
    base = brief(repo_root, unit, seat, tier)
    if prior is None:
        return base
    probes = extract_probes(prior)          # raises rather than dropping the demand
    listed = "\n".join(f"  - {p}" for p in probes)
    return (f"{base}\n\n--- CHECKS TO RE-EXECUTE ---\n\n"
            f"Before concluding, re-execute each of the following and record what you observed. "
            f"Re-apply each named mutant and confirm its killing test fails; re-run each named "
            f"test. Confirm the tree is byte-identical afterwards.\n\n{listed}\n")


def round_cost_report(repo_root: Path | str) -> str:
    """What the close review has cost so far, per round and cumulatively.

    An unmeasured round is NAMED and the total is marked PARTIAL rather than the round being
    summed as zero: a total that quietly absorbs an unmeasured round reads cheaper than the
    run actually was, and this number exists to be weighed against buying another round. A
    measured zero is a different fact from an unmeasured round and reads differently."""
    rounds = run_state.review_rounds(repo_root)
    if not rounds:
        return "no review rounds recorded for this run - no cost to report"
    lines, total, unmeasured = [], 0, 0
    for r in rounds:
        tokens = r.get("tokens", run_state.UNMEASURED)
        if tokens is run_state.UNMEASURED or tokens is None:
            unmeasured += 1
            lines.append(f"  round {r.get('round')}: unmeasured ({r.get('verdict', '?')})")
        else:
            total += int(tokens)
            lines.append(f"  round {r.get('round')}: {int(tokens):,} tokens "
                         f"({r.get('verdict', '?')})")
    if unmeasured:
        tail = (f"  total: {total:,} tokens across {len(rounds) - unmeasured} of "
                f"{len(rounds)} round(s) - PARTIAL, {unmeasured} unmeasured and never "
                f"counted as zero")
    else:
        tail = f"  total: {total:,} tokens across {len(rounds)} round(s)"
    return "\n".join([*lines, tail])


def next_round_offer(repo_root: Path | str, ceiling: int | None = None) -> str:
    """The text put in front of the operator when another round is on the table: what the
    rounds so far cost, how many there have been, and the ceiling they are counting towards.
    'Is the next round worth buying' is then a question asked against a number."""
    limit = review_ceiling(repo_root) if ceiling is None else ceiling
    count = run_state.review_round_count(repo_root)
    return (f"review rounds so far: {count} of a ceiling of {limit}\n"
            f"{round_cost_report(repo_root)}")


# The three ways out of a self-feeding repair loop. Another patch round is deliberately NOT
# among them: on a repair regression the patching is the cause, so offering more of it is the
# one response the evidence rules out. Escalating is a decision someone makes, which is the
# whole point - a round nobody chose is how a loop runs to five.
ESCALATIONS = ("revert", "redesign", "accept-and-file")


def escalation_for(repo_root: Path | str, finding: dict) -> dict:
    """The escalation brief for a repair-regression finding: three named options, each with
    the consequence of taking it, and the round and files that triggered it named so the
    choice is not blind.

    Refuses a finding that is not a repair regression - escalating a fresh finding would spend
    the circuit breaker on the case the review is supposed to handle normally."""
    if (finding or {}).get("class") != REPAIR_REGRESSION:
        raise ValueError(
            f"escalation is for a {REPAIR_REGRESSION} finding; this one is "
            f"{(finding or {}).get('class', 'missing')!r}. A fresh finding is repaired, not "
            f"escalated - the loop is still earning its cost.")
    rounds = run_state.review_rounds(repo_root)
    last = rounds[-1] if rounds else {}
    files = ", ".join(sorted({str(e.get("file")) for e in (last.get("repaired") or [])
                              if isinstance(e, dict) and e.get("file")})) or "(none recorded)"
    rnd = finding.get("round")
    return {
        "finding": finding,
        "round": rnd,
        "options": [
            {"label": "revert",
             "consequence": f"undo round {rnd}'s repair, returning {files} to its state before "
                            f"that round, and re-review from there. The defect the repair "
                            f"targeted comes back and is re-decided with the regression known."},
            {"label": "redesign",
             "consequence": "stop patching this surface and rework the approach. Costs the most "
                            "now and is the only option that addresses a repair loop whose "
                            "successive fixes keep colliding in the same place."},
            {"label": "accept-and-file",
             "consequence": "accept the current state, file the finding as its own tracked "
                            "artefact linked to this run, and close. The defect is recorded "
                            "rather than fixed, and the run closes honestly with it outstanding."},
        ],
    }


def record_escalation(repo_root: Path | str, choice: str, finding: dict, **fields) -> dict:
    """Record the operator's escalation choice against the run, with the regression that
    triggered it. For `accept-and-file`, mints a real linked artefact through the shared filer
    and reports its id - never a prose note claiming something was filed."""
    if choice not in ESCALATIONS:
        raise ValueError(f"unknown escalation {choice!r} - expected one of "
                         f"{', '.join(ESCALATIONS)}")
    filed = None
    if choice == "accept-and-file":
        import file_finding  # noqa: PLC0415 - optional at import time, required only here
        res = file_finding.file_finding(repo_root, "bug", fields.pop("title"), fields)
        filed = res["id"]
    entry = {"choice": choice, "round": finding.get("round"), "finding": finding,
             "filed": filed, "recorded_at": sdlc_md.now_iso8601()}

    def _append(state: dict) -> dict:
        existing = state.get("escalations")
        state["escalations"] = ([e for e in existing if isinstance(e, dict)]
                                if isinstance(existing, list) else []) + [entry]
        return state

    run_state._mutate(repo_root, _append)  # noqa: SLF001 - the module's own mutation path
    return entry


def defer_escalation(repo_root: Path | str, unit: str, finding: dict) -> dict:
    """The autonomous path: record the escalation as a pending operator decision and leave it
    unresolved. It never selects an option - a circuit breaker that picks its own answer is
    not a circuit breaker. Reuses the deferred-decision queue rather than adding a second
    pending-decision mechanism, so the close asks this alongside everything else, once."""
    brief = escalation_for(repo_root, finding)
    entry = {"unit": sdlc_md.norm_id(unit) or unit,
             "question": f"round {brief['round']}'s repair created this finding "
                         f"({finding.get('reason', '')}). Patching again is what produced it - "
                         f"how should the loop exit?",
             "options": brief["options"], "recommend": None,
             "deferred_at": sdlc_md.now_iso8601(), "resolution": None}

    def _append(state: dict) -> dict:
        pending = state.get("pending_decisions")
        state["pending_decisions"] = ([p for p in pending if isinstance(p, dict)]
                                      if isinstance(pending, list) else []) + [entry]
        return state

    run_state._mutate(repo_root, _append)  # noqa: SLF001
    return entry


def review_round_guard(repo_root: Path | str, ceiling: int | None = None,
                       override: bool = False) -> int:
    """Refuse a further close-review round once `ceiling` rounds are recorded, unless the
    operator overrides explicitly. Returns the rounds recorded so far.

    The refusal names the count, the ceiling and the override, because a gate whose remedy is
    not in its message sends the reader round a loop with no exit. An override is RECORDED, so
    the retro can read that the ceiling was passed and at which round."""
    limit = review_ceiling(repo_root) if ceiling is None else ceiling
    count = run_state.review_round_count(repo_root)
    if count < limit:
        return count
    if not override:
        raise ValueError(
            f"the close review has recorded {count} round(s), reaching the ceiling of {limit} "
            f"(review.max_rounds). This project's rounds past three have historically found "
            f"defects its own repairs created, not fresh ones - check the repair-regression "
            f"report before buying another. To proceed deliberately, re-run with the override.")
    run_state.record_ceiling_override(repo_root, at_round=count, ceiling=limit)
    return count


def _covered_ids(row: dict) -> set[str]:
    return {sdlc_md.norm_id(u) for u in re.split(r"[,\s]+", row.get("units", "")) if u.strip()}


def sprint_review_for(repo_root: Path | str, unit: str):
    """The latest frozen sprint-level review (`sprint_reviews`, dated before
    `REPAIR_VERB_RETIRED`) whose covered-units list includes `unit`, or None."""
    target = sdlc_md.norm_id(unit)
    latest = None
    for r in sprint_reviews(repo_root):
        if target in _covered_ids(r):
            latest = r
    return latest


#: The states a unit's independent review can be in. A REJECT is answered only by the rejecting
#: reviewer's round-2 APPROVE, so a rejected unit is `unreviewed` until then: carried at the cap,
#: it leaves the run's batch instead (`REJECT_EXITS`).
COVERAGE_APPROVED = "approved"     # an APPROVE (or a REJECT whose findings are all pre-existing)
COVERAGE_UNREVIEWED = "unreviewed"  # nobody looked, or looked and the answer is still open


def coverage_state(repo_root: Path | str, unit: str, phase: str = "delivery") -> str:
    """Which of the two states this unit's review is in: `approved` by an independent APPROVE
    (or a frozen batch review covering a unit with no verdict of its own), else `unreviewed`. A
    standing REJECT reads `unreviewed` whatever else is recorded beside it."""
    row = verdict_for(repo_root, unit, phase)
    # ONE authority, shared with `conformance.critiqued_unmet`. Answering this through
    # `sprint_covers_independently` alone gave two answers to one question: that predicate
    # refuses the PRE_GATE sentinel while `critiqued_unmet` honours it, so 75-odd grandfathered
    # APPROVEs in this repo's own ledger started reading as REJECTED - a regression introduced
    # by the very row that exists to make coverage honest.
    per_unit_ok = (bool(row) and str(row.get("verdict") or "").upper() == APPROVE
                   and (is_independent(row) or is_pre_gate(row)))
    if per_unit_ok:
        return COVERAGE_APPROVED
    # No per-unit verdict at all: a frozen batch review naming the unit, dated before
    # `REPAIR_VERB_RETIRED`, still covers it - the same licence every batch-ledger reader
    # applies through `sprint_reviews`, so this and `sprint.review_coverage` cannot disagree.
    if not row and sprint_covers_independently(repo_root, unit,
                                               sprint_review_for(repo_root, unit)):
        return COVERAGE_APPROVED
    return COVERAGE_UNREVIEWED


def coverage_counts(repo_root: Path | str, units, phase: str = "delivery") -> dict:
    """`{approved: [...], unreviewed: [...]}` over `units`.

    A PARTITION: every unit falls in exactly one state and the lists sum to the batch, so a unit
    cannot fall through the classification into no count at all.
    """
    out = {COVERAGE_APPROVED: [], COVERAGE_UNREVIEWED: []}
    for unit in units:
        out[coverage_state(repo_root, unit, phase)].append(sdlc_md.norm_id(unit))
    return out


def sprint_covers_independently(repo_root: Path | str, unit: str, review: dict | None) -> bool:
    """True when a sprint-level review covers `unit` with valid INDEPENDENT evidence.

    Two shapes qualify, and the reviewer and author must be recorded and distinct in both:

      - an APPROVE, and
      - a REJECT whose findings are ALL tagged `[pre-existing]`, because only what this unit's
        diff broke may hold its gate (reference-doctrine rule 19). The findings are still
        reported; they are simply the repository's debt rather than this increment's.

    An UNTAGGED finding never qualifies, and a REJECT with no itemised findings never
    qualifies - the safe reading of an unexplained REJECT is that the reviewer had a reason
    they did not write down.

    This is the evidence half of the two-role gate satisfied at sprint scope; the per-unit
    sign-off is still required separately."""
    if not review:
        return False
    if (review.get("verdict") or "").upper() != APPROVE:
        # A REJECT whose findings are ALL pre-existing still covers the unit. Only what this
        # unit's diff broke may hold its gate; anything already true of the tree is the
        # repository's debt, not this increment's, and a gate that no correct change can pass
        # has stopped discriminating (reference-doctrine rule 19).
        #
        # Read through `blocking_findings`, so an UNTAGGED finding is not silently treated as
        # harmless - it counts as neither blocking nor pre-existing here, and `record` refuses
        # it upstream. The safe reading of "no findings at all on a REJECT" is that the
        # reviewer rejected for a reason they did not itemise, so that still does not cover.
        parsed = parse_findings(review.get("issues", ""))
        if not parsed or blocking_findings(review.get("issues", "")):
            return False
        if any(f["origin"] != ORIGIN_PRE_EXISTING for f in parsed):
            return False
    # Through the ONE authority. This predicate used to test only non-empty-and-distinct, so it
    # accepted the PRE_GATE sentinel that `is_independent` refuses; `sprint.review_coverage`
    # compensated by AND-ing the second predicate on and `conformance` did not, which is how the
    # same rule cleared Done in one module and refused it in the other.
    return independence(review.get("reviewer", ""), review.get("author", ""))[0]


def _id(value: str) -> str:
    """Normalise an author/reviewer id for comparison: case-folded, stripped, with the
    markdown escaping that `_clean` adds on write removed, so `Dani\\_Okafor` and
    `dani_okafor` compare equal. The empty-cell placeholder `-` normalises to empty,
    so a missing author is treated as no author, not a real id."""
    out = (value or "").replace("\\_", "_").strip()
    return "" if out == "-" else out.casefold()


def same_identity(a: str, b: str) -> bool:
    """True when two recorded ids name the same identity, under this module's normalisation.

    Public because callers need it for questions that are NOT independence - "is this seat the
    author?" when excluding the author from a goal panel, for instance. Without it those callers
    reached into `_id`, and a caller holding the authority's private parts is a caller one step
    from rebuilding the authority's judgement slightly differently.
    """
    return _id(a) == _id(b)


def independence(reviewer: str, author: str) -> tuple[bool, str]:
    """THE independence test: `(independent, reason)` for a reviewer/author pair.

    One authority, because there were four - `is_independent`, `sprint_covers_independently`,
    a sign-off predicate since retired, and a fourth hand-rolled inline in `sprint.py` reaching
    into this module's private `_id`. Correctness depended on each caller remembering which combination to
    AND, nothing checked that the four agreed, and twice they did not: one required a non-empty
    reviewer and one did not (so an empty reviewer cleared the Done gate, since "" != "alice"),
    and one refused the PRE_GATE sentinel while the module that actually gates Done accepted it.
    A rule living in two implementations is a rule with two answers.

    Every clause fails CLOSED and says which one failed, so a caller can report the reason
    rather than a bare False.
    """
    rev, auth = _id(reviewer or ""), _id(author or "")
    if not auth:
        return False, "no author is recorded, so there is nobody the reviewer had to differ from"
    if not rev:
        # The clause that was missing. An empty reviewer is not equal to a recorded author, so
        # `reviewer != author` alone returned True and the row passed as independently reviewed.
        return False, "no reviewer is recorded, so nothing was independently reviewed"
    if auth == PRE_GATE:
        return False, (f"the author is the {PRE_GATE} migration sentinel, which grandfathers a "
                       f"unit closed before the gate - it is not independence, and is_pre_gate "
                       f"is the separate test for it")
    if rev == auth:
        return False, f"reviewer and author are the same identity ({rev}) - a self-review"
    return True, ""


def is_independent(verdict: dict | None) -> bool:
    """True when a verdict was authored and reviewed by distinct identities.

    Independence is the floor, not a persona feature: it holds for generic workers too. A
    verdict with no recorded reviewer or author, or whose reviewer id equals its author id (a
    self-review), is NOT independent and must not clear the Done gate. PRE_GATE is not real
    independence either - `is_pre_gate` is the separate test for it.

    Delegates to `independence`, which is the one authority.
    """
    if not verdict:
        return False
    return independence(verdict.get("reviewer", ""), verdict.get("author", ""))[0]


# EP0113: the carry-forward review policy lives in its own module; re-exported here so the
# review-policy discipline is reachable through the critic surface the tests and gate use.
try:
    import carry_forward as _carry_forward  # noqa: E402
    review_policy = _carry_forward.review_policy
    validate_carried = _carry_forward.validate_carried
    reject_carries_forward = _carry_forward.reject_carries_forward
    is_narrative_downgrade = _carry_forward.is_narrative_downgrade
    REVIEW_POLICIES = _carry_forward.POLICIES
    PolicyError = _carry_forward.PolicyError
except ImportError:  # pragma: no cover - partial install
    _carry_forward = None


def is_pre_gate(verdict: dict | None) -> bool:
    """True for a unit closed BEFORE the independence gate, under the prior
    risk-scaled policy (which permitted light-tier self-review). Marked by the
    visible PRE_GATE author sentinel from the one-time migration - auditable in the
    ledger, and never producible by the sprint loop (which stamps a real delegation
    id). These are grandfathered as conformant; the gate applies to all work closed
    after it."""
    return bool(verdict) and _id(verdict.get("author", "")) == PRE_GATE


def _declared_reviewers(repo_root: Path | str) -> list[tuple[str, str]]:
    """(role, card person-name) pairs declared under personas/seats and
    personas/amigos - the reviewers the project actually has."""
    import re as _re
    out: list[tuple[str, str]] = []
    role_re = _re.compile(r"<!--\s*role:\s*([a-z][a-z0-9-]*)\s*-->", _re.I)
    name_re = _re.compile(r"^#\s+([^-\n]+)", _re.M)
    for sub in ("seats", "amigos"):
        d = Path(repo_root) / "sdlc-studio" / "personas" / sub
        if not d.is_dir():
            continue
        for card in sorted(d.glob("*.md")):
            try:
                text = card.read_text(encoding="utf-8")
            except OSError:
                continue
            rm = role_re.search(text)
            nm = name_re.search(text)
            if rm:
                out.append((rm.group(1).lower(),
                            (nm.group(1).strip() if nm else card.stem)))
    return out


def seat_for(repo_root: Path | str, reviewer: str) -> str | None:
    """The declared seat ROLE this reviewer id stands in, or None for a seat-less reviewer.

    Whole-word matching only: 'production' must not claim the product seat, while any token of
    the seat holder's name ('sam') is a seat claim. None on a project that declares no
    personas, because there is no seat to stand in - a headless consumer is not seat-less in
    the sense a report should report, so callers distinguish the two by asking whether any seat
    is declared at all.
    """
    import re as _re
    words = set(_re.findall(r"[a-z0-9]+", (reviewer or "").lower()))
    for role, name in _declared_reviewers(repo_root):
        if role in words:
            return role
        if any(tok in words for tok in _re.findall(r"[a-z0-9]+", name.lower())):
            return role
    return None


def _seat_drift_warning(repo_root: Path | str, reviewer: str) -> str | None:
    """Advisory when the reviewer names no declared seat - the persona lens
    drifting out of the critic loop must be visible, never silent. Silent on
    projects that declare no personas (headless consumers still work)."""
    declared = _declared_reviewers(repo_root)
    if not declared:
        return None
    if seat_for(repo_root, reviewer) is not None:
        return None
    opts = ", ".join(f"{name} (role: {role})" for role, name in declared)
    return (f"reviewer '{reviewer}' matches no declared seat - the critic "
            f"should run as a review seat's render (declared: {opts}); see "
            f"reference-workflow-personas.md")


_RETURN_CONTRACT = """Return EXACTLY (raw data, no wrapper):
VERDICT: APPROVE or REJECT
ISSUES: <semicolon-separated findings, each one TAGGED with its origin and carrying
        file:line evidence - or 'none'. Decide the origin by EXECUTION (`git log -S`, or
        re-probe at the base ref), never by impression:
          [regression]   this diff broke something that worked at the base ref
          [new]          this diff introduced a defect that did not exist
          [pre-existing] already true of the tree, or already recorded in an open Bug/CR
                         (cite the id) - reported, and it does NOT hold the gate
        e.g. ISSUES: [regression] verify_ac crashes on empty Affects (verify_ac.py:88);
                     [pre-existing] BG0123 the gate is slow>
BLOCKING: <the subset that must be fixed before Done, or 'none'>"""


# --- Standing review-brief practices ---------------------------------------------------
# The practices that produced this project's highest-value findings, each a STANDING
# instruction carried in every reviewer brief with the reason it exists beside it. Each was
# improvised mid-sprint rather than drawn from anything shipped, so they depended on
# whoever wrote the brief remembering them - the party the review exists to check. Woven into
# every brief so they no longer do. `missing_practices` proves both halves are present: a
# practice named without its reason is the half a fresh reviewer drops first.
_REVIEW_PRACTICES_BLOCK = """--- STANDING REVIEW PRACTICES (each with the reason it exists) ---

On a REPAIR review, rule each previous finding CLOSED, OVER-CLAIMED or MOVED - a general
'review the repair' answer blurs the three into one impression, and a MOVED defect is one that
survived, not one that closed.

Mutate the author's TESTS, not only the code: a shape list drawn from the families where two
implementations agree by construction passes every mutant while proving nothing, and reading
the code never finds that.

When a mutant SURVIVES, re-test its branch in ISOLATION before drawing any conclusion from it:
a sibling guard masked a survivor three separate times in one sprint, and each time the truth
appeared only when the branch was exercised alone - a survivor is evidence about the harness,
not about the test.

A repair that changes behaviour carries a test asserting that behaviour; where it does not,
report the missing regression cover as a finding: an unpinned repair is one a later edit
reverts with the suite still green, and a shipped repair was lost exactly that way.

Mutate in an ISOLATED CHECKOUT of your own, never the author's working tree - in this harness,
`Agent(isolation: 'worktree')`. Do NOT use `git stash` or `git checkout --` to clean up: both
are tree-wide, so either one silently reverts a concurrent reviewer's mutant mid-run and a
result reported SURVIVED may never have been on disk when its test ran. Four reviewers were
once dispatched over one shared tree and a live mutant was left behind in it; it was caught
only because the tree was otherwise clean, and over uncommitted work it would have been
indistinguishable from that work.

If you revert IN PLACE anyway - and the manual oracle is the case where a reviewer is most
tempted to - the obligation is to SNAPSHOT THE BYTES FIRST and restore from that snapshot
unconditionally, in a `finally`, before you report anything. Not `git checkout --`, which
restores the COMMITTED state and destroys whatever was uncommitted: a reviewer following this
procedure took a unit's base revision by hand in the author's working tree and roughly four
hundred uncommitted lines were gone, with nothing able to bring them back. The rule
existed and was broken anyway, so it is stated here, in the brief a reviewer actually reads,
rather than only in the decision that records it."""

# Each practice: (name, instruction-regex, reason-regex). Both must be present in a brief for
# the practice to count as carried; the reason clause is the half worth keeping. Searched over
# the whitespace-normalised brief, and `[^.]*` keeps each match inside one sentence so an
# instruction in one place and a reason in another do not pair by accident.
_BRIEF_PRACTICES = (
    ("per-item repair verdict",
     r"rule each previous finding[^.]*CLOSED[^.]*OVER-CLAIMED[^.]*MOVED",
     r"blurs?[^.]*into one impression"),
    ("mutate the author's tests",
     r"mutate the author'?s TESTS[^.]*not only the code",
     r"agree by construction"),
    ("isolation re-test of a survivor",
     r"re-test[^.]*in ISOLATION[^.]*before drawing any conclusion",
     r"sibling guard[^.]*masked"),
    ("regression cover for a repair",
     r"changes behaviour carries a test[^.]*report the missing regression cover as a finding",
     r"reverts with the suite still green"),
    # The rule existed in reference-review.md and was enforced author-side only: `mutation.py
    # run` refuses a target with uncommitted changes, which protects the AUTHOR, and nothing
    # protected the tree from the REVIEWER. The brief is the one artefact guaranteed to reach a
    # delegated reviewer, so a practice absent from it is held only by the dispatcher's memory.
    ("isolated checkout for mutation",
     r"ISOLATED CHECKOUT[^.]*never the author'?s working tree",
     r"tree-wide[^.]*silently reverts a concurrent reviewer'?s mutant"),
)

# The four prose surfaces the claim-inventory first pass must cover. A pass that omits one
# exempts it, and a Resolution is the artefact no test can fail - the cheapest thing in the
# diff to check and the likeliest to be wrong.
CLAIM_SURFACES = ("Resolutions", "docstrings", "comments", "CHANGELOG")
_CLAIM_INVENTORY_BLOCK = """--- CLAIM INVENTORY (run this FIRST, before the logic review) ---

Before reading the logic, enumerate every assertion the diff's prose makes across all four
surfaces - Resolutions, docstrings, comments and CHANGELOG entries - and mark each TRUE, FALSE
or UNVERIFIABLE against the code. A Resolution is the one artefact no test can fail, so it is
the cheapest thing here to check and the likeliest to be wrong. A claim no command can settle
is UNVERIFIABLE, reported as such and counted on trust, never assumed TRUE."""


def _normalise_brief(text: str) -> str:
    """Collapse whitespace so a practice or surface wrapped across brief lines still matches."""
    return re.sub(r"\s+", " ", (text or "")).strip()


def missing_practices(brief_text: str) -> list[str]:
    """The standing review practices a brief fails to carry, by name. Empty means every one is
    present with its reason. A practice whose instruction is present but whose reason clause
    is not still counts as missing - the reason is what survives into a fresh reviewer's head."""
    body = _normalise_brief(brief_text)
    absent = []
    for name, instruction, reason in _BRIEF_PRACTICES:
        if not (re.search(instruction, body, re.I) and re.search(reason, body, re.I)):
            absent.append(name)
    return absent


def assert_brief_practices(brief_text: str) -> None:
    """Refuse a brief missing any standing practice, naming which. A brief that omits one leaves
    it to whoever wrote the brief to remember, which is how each was improvised rather than
    shipped - so it is refused, never issued.

    The roll-call in the message is DERIVED from `_BRIEF_PRACTICES`, never written beside it: a
    hand-listed roll-call goes stale the first time a practice is added, and then the refusal
    describes a rule set the guard no longer enforces."""
    absent = missing_practices(brief_text)
    if absent:
        every = ", ".join(name for name, _i, _r in _BRIEF_PRACTICES)
        raise ValueError(
            "reviewer brief is missing standing practice(s): " + "; ".join(absent)
            + f" - each of {every} is a standing instruction; a brief that omits one is "
              "refused, not issued")


def missing_claim_surfaces(brief_text: str) -> list[str]:
    """The prose surfaces the claim-inventory pass fails to name, so removing one is detectable.
    All four (Resolutions, docstrings, comments, CHANGELOG) must be named or the omitted one is
    exempted from the pass."""
    body = _normalise_brief(brief_text)
    return [s for s in CLAIM_SURFACES if not re.search(re.escape(s), body, re.I)]


def assert_brief_claim_pass(brief_text: str) -> None:
    """Refuse a brief whose claim-inventory pass omits any of the four prose surfaces or the
    TRUE/FALSE/UNVERIFIABLE vocabulary. A pass that omits a surface silently exempts it."""
    absent = missing_claim_surfaces(brief_text)
    if absent:
        raise ValueError(f"claim-inventory pass omits prose surface(s): {', '.join(absent)} - "
                         f"all four ({', '.join(CLAIM_SURFACES)}) must be enumerated or the "
                         f"omitted one is exempt; refused")
    body = _normalise_brief(brief_text)
    # Only the missing words are named. A roll-call of all three names the present ones as if
    # they were absent too, and the reader repairs a block that was never broken.
    unnamed = [w for w in ("TRUE", "FALSE", "UNVERIFIABLE") if not re.search(rf"\b{w}\b", body)]
    if unnamed:
        raise ValueError(f"claim-inventory pass never names the ruling(s): {', '.join(unnamed)} "
                         f"- a claim the pass cannot mark that way is left unruled; refused")


def tier_for(repo_root: Path | str, unit: str) -> str:
    """The review depth this unit's RISK earns, derived from `route.estimate`'s band.

    `route.py` says it in its own header - "Advisory only - no gate reads a tier" - and that has
    been true since the score was built: a deterministic 0-100 difficulty with bands and a
    confidence, stamped on every unit at plan time. This is its consumer. A unit whose blast
    radius is small stops paying a large unit's review, which is the whole of CR0510's thesis in
    one function.

    Fails towards `full`: an unresolvable band, an unknown band name, an unreadable unit. The
    cost of a needless full pass is tokens; the cost of a needless light one is a defect that
    ships. That asymmetry decides the default, not neatness.
    """
    try:
        import route  # noqa: PLC0415 - deferred; brief() must not pay for it unused
        found = sdlc_md.find_by_id(Path(repo_root), unit)
        if not found:
            return UNKNOWN_BAND_TIER
        band = route.estimate(Path(repo_root), found[0])["difficulty_band"]
    except Exception:  # noqa: BLE001 - a difficulty read must never break a brief
        return UNKNOWN_BAND_TIER
    return BAND_TIER.get(band or "", UNKNOWN_BAND_TIER)


def _lessons_block(root: Path) -> str:
    """The failure classes injected at review (rule plus behaviour, at most five), and how a
    finding that repeats one cites it. The class store is the only lesson source a review brief
    carries: a seat told what has been repeating is the pass most likely to catch the repeat,
    and a cited code is what lets the repeat be counted rather than written up again."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import lessons  # noqa: PLC0415 - sibling; deferred so only a brief pays for it
    digest = lessons.phase_digest(root, "review")
    lines = lessons.render_phase(digest)
    if digest.get("lessons"):
        lines.append("A finding that repeats one of these cites its class code after the origin "
                     "tag, e.g. `[new] the mutant was never applied (x.py:12) [LC-NNN]`, so the "
                     "repeat is counted on the class rather than written up again.")
    return "\n".join(lines)


def _shared_selector_block(path: Path) -> str:
    """One advisory line per Verify selector two or more of this unit's criteria share, or "".

    Advice, not a refusal: two criteria on one run cannot both discriminate, and the seat judging
    them is the one who can say whether they assert one indivisible behaviour or need splitting.
    Judged within this artefact only - a bug sharing its fixing story's selector is correct."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import verify_ac  # noqa: PLC0415 - sibling; the grouping is the lint's own
    lines = []
    for group in verify_ac.duplicate_verifiers([path]):
        acs = [a.split(" ", 1)[-1] for a in group["acs"]]
        names = ", ".join(acs[:-1]) + f" and {acs[-1]}"
        lines.append(f"Advisory: {names} share one Verify selector (`{group['verifier']}`) - "
                     f"two criteria on one run cannot both discriminate; judge whether each is "
                     f"exercised on its own.")
    return "".join(f"{ln}\n" for ln in lines)


def _criteria_from_whole_file(text: str) -> str:
    """The criteria of an artefact with NO `## Acceptance Criteria` section, as the runner reads
    them: every block, wherever it sits. The brief rendered nothing for such an artefact while
    `verify_ac run` executed all of it, so the two readers disagreed by construction; the shape
    itself is refused by `validate check`, and until it is moved the seat sees what runs."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import verify_ac  # noqa: PLC0415 - sibling; the parser is the runner's own
    blocks = verify_ac.parse_story(text)
    if not blocks:
        return ""
    lines = text.splitlines()
    out = []
    for i, b in enumerate(blocks):
        end = blocks[i + 1].heading_line if i + 1 < len(blocks) else len(lines)
        for j in range(b.heading_line + 1, end):
            if lines[j].startswith("## "):
                end = j
                break
        out.append("\n".join(lines[b.heading_line:end]).rstrip())
    return "\n\n".join(out)


def _review_seat_card(root: Path, seat: str) -> Path:
    """The seat's charter, by persona_resolve's one resolver: the project card whose declared
    `role:` is the seat, else the shipped default, so a fresh project briefs its review on the
    shipped team. The brief never judged a card's sections and does not start here; a seat with
    no card anywhere is refused rather than briefed without a charter."""
    import persona_resolve  # noqa: PLC0415 - sibling; one resolver for every seat reader
    card = persona_resolve.resolve_card(root, seat)
    if card is None:
        raise ValueError(f"no seat card for {seat!r} - neither the project nor the skill "
                         f"carries one (seats: {', '.join(persona_resolve.SEATS)})")
    return card


def brief(repo_root: Path | str, unit: str, seat: str, tier: str = "full") -> str:
    """The seat-review prompt, assembled deterministically.

    The judgement stays with the seat; this is only the scaffolding every review
    needs - charter, unit ACs, diff scope, tier, and the exact return contract -
    so no reviewer starts from a hand-typed, drift-prone brief. Refuses an
    unknown unit or seat loudly."""
    root = Path(repo_root)
    found = sdlc_md.find_by_id(root, unit)
    if not found:
        raise ValueError(f"no artefact with id {unit!r} - brief needs a real unit")
    path, _type = found
    text = sdlc_md.read_text_safe(path)
    card = _review_seat_card(root, seat)
    # the SAME heading rule as the runner's `criteria_blocks`: case-insensitive, more words allowed
    m = re.search(r"(?mi)^##\s+acceptance criteria\b[^\n]*\n(.*?)(?=^## |\Z)", text, re.S)
    acs = (m.group(1).strip() if m else _criteria_from_whole_file(text)
           or "(no Acceptance Criteria section - judge the diff against the unit's stated intent)")
    affects = sdlc_md.affects_files(text)
    scope = (", ".join(affects) if affects
             else "(no Affects declared - derive the scope from git status)")
    full_tier = tier == "full"
    depth = ("Full adversarial pass: try to make each test FAIL (mutations), probe "
             "boundaries and silent-failure paths, verify claims by EXECUTION, not reading."
             if full_tier else
             "Lighter independent pass (mechanical/doc-tier unit): check the change does "
             "what its ACs say and nothing else; run the named suite once.")
    # THE BOUNDED BRIEF. The claim-inventory pass reads every Resolution, docstring, comment and
    # CHANGELOG line in scope and rules on each - a finding generator by construction, and the
    # single largest block in this prompt. On a low-band unit it costs more than the unit does.
    #
    # Derived from the SAME `tier` value as the depth line above, deliberately: a brief that
    # announced a lighter pass while carrying the full claim inventory would be two decisions
    # where there is one, and they would disagree the first time either moved.
    inventory = f"{_CLAIM_INVENTORY_BLOCK}\n\n" if full_tier else ""
    shared = _shared_selector_block(path)
    unit_id = sdlc_md.norm_id(sdlc_md.extract_record_id(path.stem) or unit)
    title = sdlc_md.extract_h1_title(text) or unit_id
    # THE FILES' HISTORY: the delivered units that changed them and what their reviews caught,
    # so the seat looks first for a repeat the record already holds.
    import reconcile  # noqa: PLC0415 - sibling; the corpus walk is the already-delivered lane's
    history = reconcile.file_history_section(root, unit_id, affects)
    return f"""You are the {seat} review seat. Read and adopt the charter at
{card} (the review render). You did NOT author this diff; your job is
independent judgement of it against the ACs below - they are law, your stance never
overrides them.

Repo root: {root.resolve()}

Unit under review: {unit_id} - {title}
Artefact: {path}

Diff scope (the unit's declared Affects - inspect with git diff/status on these paths):
{scope}

Acceptance criteria (canonical - judge against THESE, not a paraphrase):
{acs}
{shared}
{history}
Review depth: {depth}

{inventory}{_REVIEW_PRACTICES_BLOCK}

{_lessons_block(root)}

{_RETURN_CONTRACT}"""


def rejoinder_brief(repo_root: Path | str, unit: str, seat: str,
                    prior_verdict_text: str, tier: str = "full") -> str:
    """The re-review brief after a REJECT's repairs: the prior VERDICT/ISSUES/BLOCKING
    quoted verbatim, the base brief refreshed (via the standard brief), the structural demand
    to re-examine what the prior verdict named, and the return contract. A malformed
    prior-verdict block is refused loudly - a rejoinder against a verdict that cannot be parsed
    would re-review against a paraphrase. Validation is well-formedness only: an APPROVE prior
    verdict is accepted too (a legitimate post-approval re-review)."""
    parse_verdict_block(prior_verdict_text)  # validation only; ValueError on malformed
    base = brief(repo_root, unit, seat, tier)
    return f"""{base}

--- RE-REVIEW (rejoinder) ---

This is a RE-REVIEW after repairs to your prior verdict. Your prior verdict, verbatim:

{prior_verdict_text.strip()}

The author's repairs summary (if any) accompanies this brief separately. It is a CLAIM,
not evidence: before you may approve, RE-EXECUTE the probes and mutants your prior
verdict named - re-apply each mutant and watch its killing test FAIL, re-run each live
probe - and confirm the tree is byte-identical after your mutations. A repair whose
killing test cannot fail is vacuous; two such tests have shipped before.

Then return the SAME contract as before:

{_RETURN_CONTRACT}"""


_VERDICT_LINE = re.compile(r"^\s*VERDICT:\s*(\S+)\s*$", re.M | re.I)
_BLOCK_TOKENS = ("VERDICT", "ISSUES", "BLOCKING")


def _block_field(text: str, token: str) -> str:
    """The token's content: from `TOKEN:` to the next KNOWN token line or EOF.
    Case-insensitive both ways, and bounded only by the contract's own tokens -
    a wrapped continuation line starting `NOTE:` (or any other ALL-CAPS word)
    belongs to the field, not to a phantom next one."""
    boundary = "|".join(_BLOCK_TOKENS)
    m = re.search(rf"^\s*{token}:\s*(.*?)(?=^\s*(?:{boundary}):\s|\Z)",
                  text, re.M | re.S | re.I)
    return m.group(1).strip() if m else ""


def parse_verdict_block(text: str) -> tuple[str, str]:
    """(verdict, issues) from a returned VERDICT/ISSUES/BLOCKING block.

    Refuses (ValueError) a missing VERDICT line, a value outside APPROVE/REJECT,
    or MORE THAN ONE verdict line - an ambiguous block must never be recorded as
    a clean approval. An echoed copy of the return contract ("VERDICT: APPROVE or
    REJECT") never matches the single-token verdict line; ISSUES/BLOCKING are read
    from AFTER the verdict line, so an echo above it cannot leak placeholder text
    into the record."""
    matches = list(_VERDICT_LINE.finditer(text))
    if not matches:
        raise ValueError("no 'VERDICT:' line found in the block - the reviewer must "
                         "return the VERDICT/ISSUES/BLOCKING contract")
    if len(matches) > 1:
        raise ValueError(f"{len(matches)} VERDICT lines found - an ambiguous block is "
                         "refused, never resolved in the author's favour")
    m = matches[0]
    verdict = m.group(1).strip().upper()
    if verdict not in ("APPROVE", "REJECT"):
        raise ValueError(f"unknown verdict {verdict!r} - APPROVE or REJECT only")
    after = text[m.end():]
    issues = _block_field(after, "ISSUES")
    blocking = _block_field(after, "BLOCKING")
    if blocking and blocking.lower() != "none":
        issues = (issues + "; " if issues else "") + f"BLOCKING: {blocking}"
    return verdict, issues


# --- Per-item repair verdict -----------------------------------------------------------
# A repair review rules each previous finding individually, so an aggregate 'the repair is
# fine' can never cover findings the reviewer was shown as a set but never item by item.
REPAIR_RULINGS = ("CLOSED", "OVER-CLAIMED", "MOVED")


def enumerate_repair_findings(prior_findings: list[str]) -> str:
    """Render the previous round's findings as a per-item checklist for a repair review, each
    demanding its own CLOSED / OVER-CLAIMED / MOVED ruling. Refuses an empty list - a repair
    review with nothing to rule on is not a repair review, and an aggregate answer about a set
    never shown item by item is exactly what enumerating them forbids."""
    items = [str(f).strip() for f in (prior_findings or []) if str(f).strip()]
    if not items:
        raise ValueError("a repair review needs the previous round's findings to enumerate - "
                         "with none listed the reviewer answers in aggregate; refused")
    lines = ["--- PER-ITEM REPAIR VERDICT (rule EACH previous finding below) ---", "",
             "Rule each of the previous round's findings individually as CLOSED, OVER-CLAIMED "
             "or MOVED. A general 'the repair is fine' answer is not accepted - every finding "
             "carries its own ruling, and MOVED means the defect survived, not that it closed.",
             ""]
    for i, finding in enumerate(items, 1):
        lines.append(f"{i}. {finding}")
        lines.append("   ruling: ( CLOSED | OVER-CLAIMED | MOVED )")
    return "\n".join(lines)


def validate_repair_verdict(prior_findings: list[str], rulings: dict) -> bool:
    """Refuse a repair-round verdict unless EVERY previous finding carries a ruling in
    {CLOSED, OVER-CLAIMED, MOVED}. Raises ValueError naming the first unruled finding, or a
    ruling outside the vocabulary. An unruled finding is never resolved in the repair's favour -
    that is the aggregate answer this exists to refuse."""
    seen = {str(k): str(v).strip().upper() for k, v in (rulings or {}).items()}
    for finding in prior_findings:
        key = str(finding)
        ruling = seen.get(key, "")
        if not ruling:
            raise ValueError(f"finding not ruled: {key!r} - each previous finding carries its "
                             f"own CLOSED/OVER-CLAIMED/MOVED ruling; an unruled finding is "
                             f"refused, never taken as closed")
        if ruling not in REPAIR_RULINGS:
            raise ValueError(f"finding {key!r} has ruling {ruling!r} outside {REPAIR_RULINGS}")
    return True


def repair_open_findings(rulings: dict) -> list[str]:
    """The findings still OPEN after a repair round: everything not CLOSED. A MOVED defect
    survived - it moved, it did not close - and an OVER-CLAIMED repair claimed more than it did;
    counting either as closed is how a repair masks the defect beside it."""
    return [str(f) for f, r in (rulings or {}).items() if str(r).strip().upper() != "CLOSED"]


# --- Claim inventory (prose assertions ruled TRUE / FALSE / UNVERIFIABLE) ---------------
# The first pass of a review: enumerate every assertion the diff's prose makes and rule each,
# before the logic review. A claim silently ruled TRUE because nothing contradicted it is the
# failure this surfaces, so UNVERIFIABLE is its own category and an absent ruling is refused.
CLAIM_RULINGS = ("TRUE", "FALSE", "UNVERIFIABLE")


def validate_claim_inventory(claims: list[str], rulings: dict) -> bool:
    """Refuse a claim inventory unless every enumerated claim carries a ruling in
    {TRUE, FALSE, UNVERIFIABLE}. Raises ValueError naming the first unruled claim, or a ruling
    outside the vocabulary. An absent ruling is refused, never defaulted to TRUE."""
    seen = {str(k): str(v).strip().upper() for k, v in (rulings or {}).items()}
    for claim in claims:
        key = str(claim)
        ruling = seen.get(key, "")
        if not ruling:
            raise ValueError(f"claim not ruled: {key!r} - every enumerated assertion carries a "
                             f"TRUE/FALSE/UNVERIFIABLE ruling; an unruled claim is refused, "
                             f"never assumed true")
        if ruling not in CLAIM_RULINGS:
            raise ValueError(f"claim {key!r} has ruling {ruling!r} outside {CLAIM_RULINGS}")
    return True


def summarise_claim_pass(rulings) -> dict:
    """The claim pass summarised. Counts per category, how many claims rest on TRUST
    (UNVERIFIABLE), how many were actually CHECKED against the code (TRUE or FALSE), and whether
    the pass is VERIFIED. A pass is verified only when at least one claim was settled; a pass
    whose every ruling is UNVERIFIABLE checked nothing, and must not read the same as one that
    looked and found nothing wrong. Accepts a rulings dict or a bare iterable of rulings."""
    values = rulings.values() if isinstance(rulings, dict) else (rulings or [])
    counts = {r: 0 for r in CLAIM_RULINGS}
    for v in values:
        u = str(v).strip().upper()
        if u in counts:
            counts[u] += 1
    checked = counts["TRUE"] + counts["FALSE"]
    on_trust = counts["UNVERIFIABLE"]
    return {"true": counts["TRUE"], "false": counts["FALSE"],
            "unverifiable": on_trust, "on_trust": on_trust,
            "checked": checked, "total": checked + on_trust,
            "verified": checked > 0}


def render_claim_pass(rulings) -> str:
    """One line describing the claim pass, in which a checked round and an all-on-trust round
    read differently. An all-UNVERIFIABLE pass renders NOT VERIFIED - nothing was settled - so
    it cannot be mistaken for a clean pass that looked and found nothing."""
    s = summarise_claim_pass(rulings)
    if s["total"] == 0:
        return "claim pass: no assertions enumerated"
    if not s["verified"]:
        return (f"claim pass: NOT VERIFIED - all {s['total']} claim(s) UNVERIFIABLE, nothing "
                f"settled against the code; this round checked nothing")
    trust = f", {s['on_trust']} on trust (UNVERIFIABLE)" if s["on_trust"] else ""
    return (f"claim pass: {s['checked']} of {s['total']} checked "
            f"(TRUE {s['true']}, FALSE {s['false']}){trust}")


# ---------------------------------------------------------------------------
# The consuming caller: a criterion for a mechanism names what will call it
# ---------------------------------------------------------------------------
# Four mechanisms shipped in one sprint reaching nothing: a hash whose digest could never match,
# a selection computed by one hook and ignored by the one that runs the tests, a consumer whose
# producer did not exist. Every one had passing tests and a green gate, because every criterion
# described the function's own behaviour and none asked what would call it. Reviewing for it
# afterwards costs a round; asking for it while the criterion is being written costs a sentence.
#
# So a criterion for a mechanism declares its consumer, and the declaration must RESOLVE - a
# named caller that is nowhere in the tree is the same defect wearing an answer's clothes.

#: The AC bullet an author writes to name the consumer. Read here and asked for by the shipped
#: story template: a checker reading a different word from the one the template writes is exactly
#: the drift that makes a field look answered and go unchecked.
CALLER_FIELD = "Caller"

#: No criterion names a consumer at all.
CALLER_UNNAMED = "caller-unnamed"
#: A consumer is named but does not resolve to anything in the tree.
CALLER_UNRESOLVED = "caller-unresolved"
#: The unit declares code, but every declared file was subtracted as its own proof, so the
#: mechanism surface came out empty and the check cannot speak for the unit either way. Reported
#: rather than skipped: a silent pass on a unit nothing judged is indistinguishable from a pass
#: the unit earned, and that is how a vacuous criterion survived the check built to catch it.
CALLER_INDETERMINATE = "caller-indeterminate"

_CALLER_RE = re.compile(rf"^\s*[-*]\s*\*\*{CALLER_FIELD}s?:?\*\*:?\s*(.+?)\s*$", re.I)
#: Path-, command- and identifier-shaped runs inside a declaration, so `the commit gate
#: (tools/hooks/pre-commit)` offers `tools/hooks/pre-commit` to the resolver.
_CALLER_TOKEN = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_./-]*")

#: The only directories a tree scan skips, and both are DERIVED content rather than source:
#: git's object store and the interpreter's bytecode cache. Nothing else is excluded, because a
#: list of "uninteresting" directories is a list of places a caller can hide.
_TREE_SKIP = (".git", "__pycache__")


def tree_index(repo_root: Path | str) -> dict:
    """Every TRACKED file, indexed by relative path, file name and stem.

    Tracked, not walked. A filesystem walk pulled in `node_modules` and every vendored artefact,
    which turned the index into a general English vocabulary: against this repo it made
    `unknown`, `nothing at all` and `the main loop` all resolve, while a real relative path did
    not. An index whose failure mode is "everything matches" cannot judge anything, and it is
    worst on exactly the vendored repositories this skill is aimed at.

    Refuses an EMPTY result. A scan that found nothing is not the finding "no caller resolves
    here" - it is a scan that did not answer.
    """
    root = Path(repo_root)
    paths: set[str] = set()
    names: set[str] = set()
    stems: set[str] = set()
    import subprocess as _sp
    try:
        proc = _sp.run(["git", "-C", str(root), "ls-files", "-z"],
                       capture_output=True, text=True, timeout=30)
        listing = [x for x in proc.stdout.split("\0") if x] if proc.returncode == 0 else []
    except (OSError, _sp.SubprocessError):
        listing = []
    if not listing:
        # git could not answer - a tree that is not a repository yet is a legitimate case, and
        # a consuming project may run this before its first commit. Fall back to a walk, but
        # keep the skip list: the vendored directories are what turned this index into an
        # English vocabulary in the first place.
        listing = [str(q.relative_to(root)) for q in root.rglob("*") if q.is_file()]
    symbols: set[str] = set()
    for rel in listing:
        if any(part in _TREE_SKIP for part in Path(rel).parts):
            continue
        paths.add(rel)
        names.add(Path(rel).name)
        stems.add(Path(rel).stem)
        if rel.endswith(".py"):
            symbols |= _defined_symbols(root / rel)
    if not paths:
        raise ValueError(
            f"tree_index of {root} found no tracked files - refusing to report that no caller "
            f"resolves, which is what an unanswered scan would look like")
    return {"paths": paths, "names": names, "stems": stems, "symbols": symbols}


#: A `def` or `class` at any indentation in a tracked source file.
_SYMBOL_DEF = re.compile(r"^\s*(?:async\s+)?(?:def|class)\s+([A-Za-z_]\w*)", re.MULTILINE)


def _defined_symbols(path: Path) -> set[str]:
    """The function and class names a tracked source file defines.

    A caller is very often named as a SYMBOL rather than a path - `cmd_lane -> lane_dispatch`
    is how every lane story names its consumer - and requiring a path-shaped token made those
    declarations unverifiable. They then passed only because an unrelated documentation
    filename sat on the same line, which is the theatre the path rule was added to stop,
    reappearing one step to the left.

    Reads the source rather than importing it: an index that imports every tracked module to
    ask what it defines runs arbitrary code to answer a naming question.
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return set()
    return set(_SYMBOL_DEF.findall(text))


def caller_resolves(index: dict, declaration: str) -> bool:
    """Whether the consumer named by `declaration` resolves to something tracked in the tree.

    A caller is named as a PATH or as a COMMAND, so a token must look like one: it carries a
    separator, or a file extension, or it matches a tracked file's name or stem while being
    more than an ordinary English word. A bare single word matched against every stem in the
    tree is how `unknown` came to satisfy the rule this function exists to enforce.

    Deliberately silent about intent: it proves the named thing EXISTS, never that it calls the
    mechanism. The second question is the reviewer's.
    """
    for token in _CALLER_TOKEN.findall(declaration or ""):
        cleaned = token.strip("./-")
        if len(cleaned) < 3:
            continue
        # A path-shaped or extension-bearing token may match on its full form or its tail.
        path_shaped = "/" in cleaned or "." in cleaned
        if path_shaped:
            if cleaned in index["paths"] or cleaned in index["names"] or cleaned in index["stems"]:
                return True
            tail = Path(cleaned).name
            if tail and (tail in index["names"] or tail in index["stems"]):
                return True
            continue
        # A bare word resolves only against a tracked file NAME (not a stem), and only when it
        # is not a word ordinary prose would produce. `gate` and `review` are stems here; they
        # are also the two most likely words in a sentence about a caller.
        if cleaned in index["names"]:
            return True
        # ...or against a symbol a tracked source file DEFINES, which is how a caller is most
        # often named. Guarded structurally, never by a word list: the token must also be
        # code-shaped - carrying an underscore or an interior capital - so `main`, `run`,
        # `report` and `review` stay unresolvable even though each is a real `def` somewhere.
        # A list of forbidden English words is the enumerated-list defect this repo keeps
        # re-filing; a shape rule cannot forget an entry.
        code_shaped = "_" in cleaned or any(c.isupper() for c in cleaned[1:])
        if code_shaped and cleaned in index.get("symbols", ()):
            return True
    return False


def _ac_blocks_with_bodies(text: str) -> list[tuple[str, list[str]]]:
    """`(AC id, body lines)` per criterion, using `verify_ac.criteria_blocks` for the block
    boundaries - the SAME reader the verifier executes, so a criterion shape the runner
    recognises is a criterion this check reads. A second AC parser here would let a unit be
    judged against criteria the runner cannot see."""
    import verify_ac  # noqa: PLC0415 - sibling; imported lazily so a record never pays for it
    lines = text.splitlines()
    blocks = verify_ac.criteria_blocks(text)
    out: list[tuple[str, list[str]]] = []
    for i, b in enumerate(blocks):
        end = blocks[i + 1].heading_line if i + 1 < len(blocks) else len(lines)
        out.append((b.ac_id, lines[b.heading_line:end]))
    return out


def caller_declarations(text: str) -> list[dict]:
    """The consumers the unit's criteria declare, as `{ac, caller}` in criterion order."""
    found: list[dict] = []
    for ac_id, body in _ac_blocks_with_bodies(text):
        for line in body:
            m = _CALLER_RE.match(line)
            if m:
                found.append({"ac": ac_id, "caller": m.group(1).strip()})
                break
    return found


def _verifier_names(line: str, rel: str) -> bool:
    """Whether a Verify line NAMES this file.

    Matched at path boundaries rather than by substring: a verifier reading
    `tests/test_thing.py` does not name `src/thing.py`, and reading it as though it did
    subtracts the mechanism from the unit and reports nothing about it. Both the declared path
    and its basename count, because a verifier names a path inside a node id
    (`pytest path/test_x.py::Class::test`) and a `./` or `.claude/` prefix must not make the
    same file look like a different one.
    """
    for cand in (rel, Path(rel).name):
        if re.search(rf"(?<![\w./-]){re.escape(cand)}(?![\w-])", line):
            return True
    return False


def mechanism_files(text: str) -> list[str]:
    """The declared files that are the unit's MECHANISM.

    Derived by SUBTRACTION from what the unit itself declares: its `Affects`, less the files its
    own verifiers name (those are its proof, not its mechanism) and less markdown (a document is
    not a mechanism). Never a list of code extensions - such a list exempts the language nobody
    thought of, which is the failure mode this project has paid for repeatedly.

    One known miss, stated rather than hidden: a unit whose verifier reads the mechanism file
    directly (a `grep` over the source it changes) subtracts that file as proof, so it is not
    asked for a consumer. Widening the rule to keep it would have to guess which verbs are
    tests, and a guess about the runner is how the two parsers diverge.
    """
    verify_lines = [line for _ac, body in _ac_blocks_with_bodies(text)
                    for line in body if sdlc_md.VERIFY_RE.match(line)]
    out: list[str] = []
    for raw in sdlc_md.affects_files(text):
        rel = raw.strip().strip("`")
        if not rel or rel.endswith(".md"):
            continue
        if any(_verifier_names(line, rel) for line in verify_lines):
            continue
        out.append(rel)
    return out


def caller_findings(repo_root: Path | str, units: list[str]) -> list[dict]:
    """Units adding a mechanism whose criteria name no consumer, or name one that does not exist.

    A REPORT, not a gate: each finding is `{unit, kind, criteria, detail}` and names the criterion
    it is about, because "this unit needs a caller" sends the author back to read all of them
    while "AC1 describes a function with no consumer" points at the line to fix. A unit whose
    declared surface is documentation, or is only its own tests, adds no mechanism and is not
    asked for one - a check that fires on everything is not a check.
    """
    root = Path(repo_root)
    index = tree_index(root)
    findings: list[dict] = []
    for raw in units or []:
        uid = sdlc_md.norm_id(raw)
        hit = sdlc_md.find_by_id(root, uid)
        if not hit:
            raise ValueError(f"no artefact with id {uid!r} - the caller check needs a real unit; "
                             f"an id that resolves to nothing is not a unit with no findings")
        text = sdlc_md.read_text_safe(Path(hit[0]))
        mech = mechanism_files(text)
        if not mech:
            # A unit whose declared surface is documentation, or only its own tests, adds no
            # mechanism and is legitimately not asked for one. A unit that DECLARED code and
            # had every entry subtracted as its own proof is a different thing entirely: the
            # subtraction emptied the surface, so the check judges nothing and would exit 0
            # however the Caller declaration were written - delete it, or replace it with text
            # naming no consumer, and the verdict is unchanged. That is a vacuous criterion,
            # which is the exact defect this check exists to remove.
            code = [f for f in sdlc_md.affects_files(text)
                    if f.strip().strip("`") and not f.strip().strip("`").endswith(".md")]
            if code:
                findings.append({
                    "unit": uid, "kind": CALLER_INDETERMINATE, "criteria": [],
                    "detail": (f"{uid} declares {', '.join(code)} but every one of those files "
                               f"is named by its own verifiers, so the mechanism surface is "
                               f"empty and this check judges nothing. Point a criterion at the "
                               f"behaviour rather than at the file, or declare the mechanism "
                               f"the unit adds - a check that cannot fail is not evidence."),
                })
            continue
        declared = caller_declarations(text)
        surface = ", ".join(mech)
        if not declared:
            criteria = [ac for ac, _body in _ac_blocks_with_bodies(text)]
            named = ", ".join(criteria) or "no criteria at all"
            findings.append({
                "unit": uid, "kind": CALLER_UNNAMED, "criteria": criteria,
                "detail": (f"{uid} adds a mechanism ({surface}) and no criterion names the "
                           f"caller that consumes it: {named} describe the function's own "
                           f"behaviour only. A mechanism that reaches no caller is inert "
                           f"however green its tests."),
            })
            continue
        for d in declared:
            if caller_resolves(index, d["caller"]):
                continue
            findings.append({
                "unit": uid, "kind": CALLER_UNRESOLVED, "criteria": [d["ac"]],
                "detail": (f"{uid} {d['ac']} names {d['caller']!r} as the consumer of "
                           f"{surface}, and nothing in the tree resolves to it - naming a "
                           f"caller that does not exist is not a way past the check."),
            })
    return findings


def render_caller_findings(findings: list[dict]) -> list[str]:
    """The lines a caller-check prints. An empty result says what it checked FOR rather than
    printing nothing, so a run that found nothing cannot be told apart from one that never
    looked."""
    if not findings:
        return ["caller check: every mechanism unit names a consumer that resolves"]
    return [f"  {f['unit']} [{f['kind']}]: {f['detail']}" for f in findings]


def cmd_caller_check(args: argparse.Namespace) -> int:
    """Report the mechanism units whose criteria name no consumer, or an absent one. Returns 1
    when there is something to report, so a hook or lane can act on it."""
    try:
        units = batch_units(args, "caller-check")
        findings = caller_findings(args.root, units)
    except BatchRefused as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except (OSError, ValueError) as exc:
        print(f"caller check refused: {exc}", file=sys.stderr)
        return 2
    for line in render_caller_findings(findings):
        print(line)
    # The SCOPE, always - a clean result has to name what it is clean over. The false
    # measurement BG0386 records was a clean answer about one unit read as a clean batch, and
    # the count is what would have shown the difference at the moment it was read.
    print(f"caller-check: {len(findings)} finding(s) over {len(units)} unit(s)")
    return 1 if findings else 0


def cmd_brief(args: argparse.Namespace) -> int:
    try:
        if getattr(args, "rejoinder", None):
            src = args.rejoinder
            prior = (sys.stdin.read() if src == "-"
                     else Path(src).read_text(encoding="utf-8"))
            explicit = args.tier is not None
            tier = args.tier or tier_for(args.root, args.unit)
            text = rejoinder_brief(args.root, args.unit, args.seat, prior, tier)
            # The re-review brief carries the same blocks as the first one, so it is refused on
            # the same terms and before anything reaches stdout.
            assert_brief_practices(text)
            if tier == "full":
                assert_brief_claim_pass(text)
            print(text)
            # the footer the delivery rejoinder never printed: a re-review's verdict needs the
            # same provenance as the first one, and a fingerprint the reviewer can quote back
            fp = rejoinder_fingerprint(text)
            how = "chosen" if explicit else "derived from the unit's risk band"
            print(f"\nreview tier: {tier} ({how})\n"
                  f"brief fingerprint: {fp}\n"
                  f"  record the verdict with:  critic.py record --unit "
                  f"{sdlc_md.norm_id(args.unit)} --verdict <APPROVE|REJECT> "
                  f"--brief {fp} --tier {tier}"
                  f"{' --tier-explicit' if explicit else ''} ...", file=sys.stderr)
        else:
            # DERIVED unless the operator named one. `--tier` no longer defaults to `full`
            # in the parser: a default there is indistinguishable from a choice, and the
            # record has to be able to tell them apart to judge whether the derivation works.
            explicit = args.tier is not None
            tier = args.tier or tier_for(args.root, args.unit)
            text = brief(args.root, args.unit, args.seat, tier)
            # The checks run here, in the verb, and never inside `brief()`, which other readers
            # also render through. The practices block reaches every delivery tier; the
            # claim inventory only the full one, so a light brief is not asked for it. Refused
            # before printing, so a deficient brief never reaches a reviewer and never earns a
            # fingerprint.
            assert_brief_practices(text)
            if tier == "full":
                assert_brief_claim_pass(text)
            print(text)
            # On stderr so the brief itself stays pipeable, and stated as the next command so
            # a reviewer does not have to know the flag exists. The tier is carried INTO that
            # command: a tier printed and not recorded is the state this whole flag was in.
            how = "chosen" if explicit else "derived from the unit's risk band"
            print(f"\nreview tier: {tier} ({how})\n"
                  f"brief fingerprint: {brief_fingerprint(text)}\n"
                  f"  record the verdict with:  critic.py record --unit "
                  f"{sdlc_md.norm_id(args.unit)} --verdict <APPROVE|REJECT> "
                  f"--brief {brief_fingerprint(text)} --tier {tier}"
                  f"{' --tier-explicit' if explicit else ''} ...", file=sys.stderr)
    except (OSError, ValueError) as exc:
        print(f"brief refused: {exc}", file=sys.stderr)
        return 2
    return 0


class BatchRefused(ValueError):
    """A batch invocation refused before anything was written."""


def batch_units(args: argparse.Namespace, verb: str) -> list[str]:
    """The units one invocation acts on, from `--unit`, `--units` or the open run.

    Every supplied spelling accumulates and the result keeps its order without repeats. That
    is deliberate and it is BG0386's defect stated as a contract: a repeated flag that keeps
    only its last value answers about one unit while reporting on a batch, and the caller has
    no way to see the difference.

    `--from-run` reads the open run's approved batch. A run that is not open REFUSES; it never
    degrades to the empty batch, because acting on nothing and reporting success is the same
    false clean the count above exists to prevent."""
    supplied: list[str] = []
    for value in (getattr(args, "unit", None) or []):
        supplied.extend(str(value).split(","))
    for value in (getattr(args, "units", None) or []):
        supplied.extend(str(value).split(","))
    if getattr(args, "from_run", False):
        state = run_state.read(args.root) or {}
        batch = [str(u).strip() for u in (state.get("batch") or []) if str(u).strip()]
        if not batch:
            raise BatchRefused(
                f"{verb} refused: --from-run was given but there is no open run with an "
                f"approved batch to read. Name the units with --units, or open a run first")
        supplied.extend(batch)
    seen: set[str] = set()
    units = [u for u in (s.strip() for s in supplied) if u and not (u in seen or seen.add(u))]
    if not units:
        raise BatchRefused(f"{verb} refused: name the unit(s) with --unit/--units, or "
                           f"--from-run to take the open run's batch")
    return units


#: What each batch verb cannot write without. Held here rather than left to argparse alone so
#: the refusal can name EVERY missing argument in one message: a caller who learns one flag per
#: refusal pays a round-trip per flag, which is how one sign-off cost nineteen spawns.
BATCH_REQUIRED: dict = {
    "record": (("author", "--author"),),
}


def missing_arguments(args: argparse.Namespace, verb: str) -> list[str]:
    """Every required argument of `verb` this invocation did not supply, in one list."""
    return [flag for attr, flag in BATCH_REQUIRED.get(verb, ())
            if not str(getattr(args, attr, "") or "").strip()]


def _run_batch(args: argparse.Namespace, verb: str, write) -> int:
    """Resolve the batch, refuse ONCE for anything missing, then write every unit.

    Both refusals happen before the first write, so a bad invocation costs one message rather
    than a half-written batch. After that a per-unit failure is reported and the remaining
    units still run - stopping at the first would leave the caller unable to tell what landed -
    and the exit code is non-zero, because a partially written batch reported as success is a
    gap nobody looks for again."""
    try:
        units = batch_units(args, verb)
    except BatchRefused as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if missing := missing_arguments(args, verb):
        print(f"{verb} refused: missing required argument(s) {', '.join(missing)} - naming "
              f"{len(units)} unit(s). Nothing was written", file=sys.stderr)
        return 2
    # EVERY id must resolve, before anything is written. `caller-check` and `refine seams` both
    # refuse an unresolvable id in this same repo, for the stated reason that a silent skip
    # ships a smaller tranche than approved - and the verb that writes the COMMITTED REVIEW
    # LEDGER did not. `critic record --units US9998,US9999` wrote two verdicts for artefacts
    # that do not exist and reported success.
    # Only where the workspace CAN answer. A root with no artefact tree at all cannot resolve
    # anything, and refusing there would fail on an unanswerable question rather than a wrong
    # one - the same distinction `close_owed` draws between an absent baseline and a corrupt
    # one. Where a tree exists, an id nothing resolves is a typo or a wrong workspace, and
    # neither belongs in a permanent ledger row.
    resolvable = any((Path(args.root) / rel).is_dir()
                     for rel, _prefix in sdlc_md.ARTIFACT_TYPES.values())
    unresolved = [u for u in units
                  if resolvable and not sdlc_md.find_by_id(args.root, u)]
    if unresolved:
        print(f"{verb} refused: {len(unresolved)} id(s) resolve to no artefact on disk: "
              f"{', '.join(unresolved)}. A verdict recorded against an id nothing resolves is "
              f"a permanent row in the review ledger about a unit that does not exist",
              file=sys.stderr)
        return 2
    written, failed = [], []
    for unit in units:
        try:
            write(unit)
        except (ValueError, OSError) as exc:
            failed.append(unit)
            print(f"{verb} refused for {unit}: {exc}", file=sys.stderr)
        else:
            written.append(unit)
    print(f"{verb}: {len(written)} unit(s) written"
          + (f" ({', '.join(written)})" if written else "")
          + (f"; {len(failed)} REFUSED ({', '.join(failed)})" if failed else ""))
    if not failed:
        return 0
    # Two different facts, two different codes. Nothing written is a REFUSAL (2) - the code
    # the single-unit form has always returned for a bad identity, and the
    # one a caller keys on. Something written alongside a refusal is a PARTIAL batch (1),
    # which is neither: the caller has to look at what landed before deciding what to re-run.
    return 2 if not written else 1


def cmd_record(args: argparse.Namespace) -> int:
    if getattr(args, "from_verdict", None):
        if args.verdict or args.issues:
            print("record refused: --from-verdict and an explicit --verdict/--issues are "
                  "mutually exclusive - one source of truth per record", file=sys.stderr)
            return 2
        src = args.from_verdict
        try:
            raw = (sys.stdin.read() if src == "-"
                   else Path(src).read_text(encoding="utf-8"))
            verdict, issues = parse_verdict_block(raw)
        except (OSError, ValueError) as exc:
            print(f"record refused: {exc}", file=sys.stderr)
            return 2
        args.verdict, args.issues = verdict, issues
    elif not args.verdict:
        print("record refused: give --verdict, or --from-verdict FILE|- with the "
              "reviewer's returned block", file=sys.stderr)
        return 2

    brief = (getattr(args, "brief", "") or "").strip()
    if not brief and getattr(args, "brief_file", None):
        try:
            saved = Path(args.brief_file).read_text(encoding="utf-8")
        except OSError as exc:
            print(f"record refused: {exc}", file=sys.stderr)
            return 2
        # Hashed the way the footer that printed it was. A saved REJOINDER's footer carries its
        # base brief plus the phase, never the prior verdict quoted beneath, so hashing the
        # whole file recorded a value no footer printed. A first-round brief is hashed whole,
        # as its footer is.
        brief = (rejoinder_fingerprint(saved) if _REJOINDER_MARK in saved
                 else brief_fingerprint(saved))
    # The origin axis asks what THIS UNIT'S DIFF did - regression, new, or already true of the
    # tree, decided against the base ref.
    if unclassified := unclassified_findings(args.issues):
        listed = "; ".join(f"  - {f[:90]}" for f in unclassified)
        print("record refused: these findings carry no origin, and an unsorted finding is the "
              "one a close cannot price against the batch that caused it:\n"
              f"{listed}\n"
              "  Tag each with what THIS unit's diff did, decided by execution (`git log -S`, "
              "or re-probe at the base ref) rather than by impression:\n"
              "    [regression]   the diff broke something that worked at the base ref\n"
              "    [new]          the diff introduced a defect that did not exist\n"
              "    [pre-existing] already true of the tree - reported, and it does not block\n"
              "  e.g. --issues \"[regression] verify_ac crashes on an empty Affects; "
              "[pre-existing] BG0123 slow gate\"", file=sys.stderr)
        return 2

    carry_failed: list[str] = []

    def write(unit: str) -> None:
        note = ("" if _id(args.author) != _id(args.reviewer)
                else "  (WARNING: self-review - blocked at the gate)")
        try:
            path, n, bug = _record(args.root, unit, args.verdict, args.reviewer, args.author,
                                   args.issues, brief=brief,
                                   tier=getattr(args, "tier", None),
                                   tier_explicit=getattr(args, "tier_explicit", False))
        except CarryFailed as exc:
            carry_failed.append(unit)
            print(f"record: {exc}", file=sys.stderr)
            return
        at = f" round {n}" if n is not None else ""
        print(f"recorded {sdlc_md.norm_id(unit)} {args.verdict.upper()} "
              f"[delivery]{at} -> {path}{note}")
        if bug:
            print(carried_notice(unit, bug))

    rc = _run_batch(args, "record", write)
    if carry_failed and rc == 0:
        rc = 1
    # Escalation is only a notice: the carry above already keeps the run going.
    try:
        recorded = batch_units(args, "record") if rc == 0 else []
    except BatchRefused:
        recorded = []
    for unit in recorded:
        if notice := escalation_notice(args.root, unit):
            print(notice)
    if drift := _seat_drift_warning(args.root, args.reviewer):
        print(f"WARNING: {drift}", file=sys.stderr)
    return rc


#: Statuses that mean "delivered, awaiting the reviewer of record" - the state a sign-off EXISTS
#: to resolve. Matched by name so a project renaming its review status keeps working.
#:
#: PUBLIC, because `sprint._awaits_signoff` reads it across a module boundary. It was reached
#: through the private name behind a broad `except`, so deleting or tightening this predicate
#: changed that caller's behaviour silently - it fell back to its own copy of the old rule.
#: One owner, one name, and a caller that breaks loudly if it ever moves.
def is_awaiting_signoff(status: str) -> bool:
    return "review" in (status or "").strip().lower()


def cmd_show(args: argparse.Namespace) -> int:
    if getattr(args, "format", "text") == "json":
        if args.unit:
            print(json.dumps({"unit": args.unit, "verdict": verdict_for(
                args.root, args.unit)}, indent=2))
        else:
            print(json.dumps(read_verdicts(args.root), indent=2))
        return 0
    if args.unit:
        v = verdict_for(args.root, args.unit)
        print(v if v else f"no verdict for {args.unit}")
    else:
        for v in read_verdicts(args.root):
            print(f"{v['unit']} {v['verdict']} ({v['date']}){_superseded_suffix(v)}")
    return 0


def _superseded_suffix(verdict: dict) -> str:
    """How a retired row reads in the listing: still shown, with why and on whose authority,
    so a reader sees both that it was recorded and that it no longer counts."""
    if not verdict.get("superseded"):
        return ""
    return (f"  SUPERSEDED {verdict.get('superseded_at', '')}: "
            f"{verdict.get('superseded_reason', '')} "
            f"(authorised by {verdict.get('superseded_by', '')})")


def cmd_supersede(args: argparse.Namespace) -> int:
    import file_finding  # noqa: PLC0415 - the shared prose-fields loader, as elsewhere
    try:
        reason = file_finding.resolve_prose_fields(
            getattr(args, "fields_file", None), {"reason": args.reason},
            allowed=("reason",)).get("reason", "")
        path = record_supersession(args.root, args.unit, args.date, reason,
                                   args.authorised_by, args.boundary, reviewer=args.reviewer,
                                   verdict=args.verdict)
    except (OSError, ValueError) as exc:
        print(f"supersede refused: {exc}", file=sys.stderr)
        return 2
    print(f"superseded the delivery verdict row for {sdlc_md.norm_id(args.unit)} "
          f"dated {args.date} -> {path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SDLC Studio critic-verdict record.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("record", help="Record a critic verdict for one unit or a batch.")
    r.add_argument("--unit", action="append", metavar="ID",
                   help="a unit id; repeatable, and a comma-separated list is accepted")
    r.add_argument("--units", action="append", metavar="ID[,ID...]",
                   help="unit ids for a whole batch in one invocation; repeatable")
    r.add_argument("--from-run", dest="from_run", action="store_true",
                   help="take the open run's approved batch as the scope; refused when no run is open")
    r.add_argument("--verdict", choices=("approve", "reject", "APPROVE", "REJECT"),
                   help="the verdict; or use --from-verdict to parse the reviewer's block")
    r.add_argument("--from-verdict", dest="from_verdict", metavar="FILE|-",
                   help="parse VERDICT/ISSUES/BLOCKING from a file (or stdin with -), refusing a malformed block")
    r.add_argument("--reviewer", default="independent-critic")
    r.add_argument("--author",
                   help="Authoring seat / delegation id that produced the diff (must differ from --reviewer).")
    r.add_argument("--issues", default="")
    r.add_argument("--brief", default="",
                   help="optional: the fingerprint `critic.py brief` printed for the prompt this "
                        "seat was given, stored on the row as given")
    r.add_argument("--brief-file", metavar="PATH",
                   help="read the brief TEXT from a file and fingerprint it here, for a "
                        "reviewer who saved the brief rather than its fingerprint")
    r.add_argument("--tier", choices=TIERS, default=None,
                   help="the depth this review was taken at, as `critic.py "
                        "brief` reported it. A light verdict does not cover a unit the risk "
                        "band tiers full; an absent tier is UNKNOWN and covers, so no "
                        "historical verdict is retrospectively downgraded")
    r.add_argument("--tier-explicit", action="store_true",
                   help="mark the tier as an operator's choice rather than a derived one")
    r.add_argument("--root", default=".")
    r.set_defaults(func=cmd_record)
    b = sub.add_parser("brief", help="Print the assembled seat-review prompt for a unit "
                                     "(charter + ACs + scope + return contract).")
    b.add_argument("--unit", required=True)
    b.add_argument("--seat", required=True,
                   help="the seat role: the project card declaring it under "
                        "sdlc-studio/personas/seats/, else the shipped one")
    b.add_argument("--tier", choices=TIERS, default=None,
                   help="override the tier DERIVED from the unit's risk band. Omit it and the "
                        "band decides: a low-band unit gets a bounded brief, a medium-or-worse "
                        "one gets the full adversarial pass. An explicit choice is recorded as "
                        "one, so the derivation can be judged against the reviews it produced")
    b.add_argument("--rejoinder", metavar="FILE|-", default=None,
                   help="emit the RE-REVIEW brief from the prior verdict file (or stdin "
                        "with -): the diff scope re-rendered, the named probes and mutants "
                        "demanded re-executed, and the delivery contract. The prior verdict is "
                        "quoted verbatim, a fingerprint footer is printed on stderr; a "
                        "malformed block is refused")
    b.add_argument("--root", default=".")
    b.set_defaults(func=cmd_brief)
    cc = sub.add_parser("caller-check",
                        help="Report units adding a mechanism whose criteria name no consuming "
                             "caller, or name one that does not resolve in the tree.")
    # `action="extend"` rather than the bare `nargs="+"` this had: with nargs alone a REPEATED
    # `--unit A --unit B` keeps only B and argparse says nothing, so the command answered about
    # one unit while reporting on a batch. That produced a false `caller-unnamed 5 -> 0` in a
    # retro and two commit messages.
    cc.add_argument("--unit", action="extend", nargs="+", metavar="ID",
                    help="the unit ids to check; repeatable, and several may follow one flag")
    cc.add_argument("--units", action="append", metavar="ID[,ID...]",
                    help="unit ids as a comma-separated list; repeatable")
    cc.add_argument("--from-run", dest="from_run", action="store_true",
                    help="check the open run's approved batch; refused when no run is open")
    cc.add_argument("--root", default=".")
    cc.set_defaults(func=cmd_caller_check)
    sp = sub.add_parser("supersede", aliases=["correct"],
                        help="Retire a verdict row that records an event which did not "
                             "happen, by appending a supersession record naming the row, "
                             "the reason and the authoriser. The row itself stays.")
    sp.add_argument("--unit", required=True)
    sp.add_argument("--date", required=True, help="the retired row's Date cell")
    sp.add_argument("--reason", default=None, help="why the row records something untrue")
    sp.add_argument("--fields-file", dest="fields_file", metavar="FIELDS.json",
                    help="read the reason from a JSON object ({\"reason\": \"...\"}) instead of "
                         "--reason, so prose carrying shell metacharacters is stored verbatim "
                         "rather than interpreted by the shell")
    sp.add_argument("--authorised-by", dest="authorised_by", required=True,
                    help="who authorised the correction - a principal independent of the "
                         "author, never the row's own author nor an in-session reviewer")
    sp.add_argument("--boundary", required=True,
                    help="the separate trust boundary the authoriser acted in (operator "
                         "console, another human, CI) - held to the sign-off's own rule")
    sp.add_argument("--reviewer", default=None,
                    help="narrow the match when the unit has several rows that date")
    sp.add_argument("--verdict", default=None, help="narrow the match by the row's verdict")
    sp.add_argument("--root", default=".")
    sp.set_defaults(func=cmd_supersede)
    s = sub.add_parser("show", help="Show the latest verdict for a unit (or all).")
    s.add_argument("--unit", default=None)
    s.add_argument("--root", default=".")
    sdlc_md.add_format_arg(s)
    s.set_defaults(func=cmd_show)
    sdlc_md.add_global_root(parser)
    return parser


#: The verbs that once took `--phase`.
_PHASELESS_VERBS = ("record", "brief", "supersede", "correct", "show")

#: Verbs removed from the parser, each refused BY NAME. Kept out of the parser itself so neither
#: `--help` nor the derived command surface lists them.
RETIRED_VERBS = {
    "signoff": "the operator signs the run once with `sprint.py sign`, and no per-unit "
               "sign-off row is written",
    "signoff-brief": "the operator reads the run's report and signs it once with "
                     "`sprint.py sign`",
    "repair": "the repair ledger is gone, and a REJECT has two exits: " + REJECT_EXITS,
    "evidence": "one verdict ledger says whether a unit was reviewed: record a per-unit "
                "delivery verdict with `critic.py record`",
    "sprint-review": "a batch review covers nothing new: record a per-unit delivery verdict "
                     "with `critic.py record`",
}


def _verb(argv: list[str]) -> str:
    """The subcommand: the first bare word that is not the value of a leading `--root`."""
    return next((a for i, a in enumerate(argv) if not a.startswith("-")
                 and (i == 0 or argv[i - 1] != "--root")), "")


def _plan_phase_retired(argv: list[str]) -> str | None:
    """The refusal for a `--phase` handed to a verdict verb, or None. Plan review is retired, so
    every verdict is a delivery verdict and the flag has nothing left to choose. Named rather
    than left to argparse, whose "unrecognized arguments" would not say why."""
    verb = _verb(argv)
    if verb in _PHASELESS_VERBS and any(a == "--phase" or a.startswith("--phase=")
                                        for a in argv):
        return (f"{verb} refused: plan review is retired - every verdict is a delivery "
                f"verdict, so `--phase` is gone. Drop the flag; nothing was written.")
    return None


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else list(argv)
    if (verb := _verb(argv)) in RETIRED_VERBS:
        print(f"error: `critic.py {verb}` is retired - {RETIRED_VERBS[verb]}. Nothing was "
              f"written.", file=sys.stderr)
        return 2
    if why := _plan_phase_retired(argv):
        print(why, file=sys.stderr)
        return 2
    args = build_parser().parse_args(argv)
    # Resolve the root ONCE and write it back, so every verb below anchors on the tree the
    # run belongs to. The family default `.` means "work it out from here", not "the cwd
    # is the project": otherwise a run from a subdirectory acts on a stray tree and exits 0.
    args.root = str(sdlc_md.resolve_root(args))
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())


# ---------------------------------------------------------------------------
# The plan critic (D0061 / RFC0050 option B)
# ---------------------------------------------------------------------------
# Every adversarial surface in this project runs AFTER code exists: the per-unit critic judges a
# diff, the close runs a full-diff refutation, and every critic subcommand is post-build. The
# planner's own checks are mechanical - shared-file clusters, ordering, capacity, origin drift -
# and none of them asks whether the batch is the RIGHT batch. So the cheapest finding available,
# "this unit does not need to be built", could only be reached by building it.

#: The three lenses, fixed. Named here so a lens that finds nothing is still REPORTED: a lens
#: that is silent because it found nothing and one that never ran are indistinguishable
#: otherwise, which is the reporting failure this project has already repaired once elsewhere.
PLAN_LENSES = ("scope", "risk", "efficiency")

#: What each lens is for, printed with its result so a reader knows what the silence covers.
PLAN_LENS_SUBJECT = {
    "scope": "does each unit need to exist, or is it already served by the codebase, the "
             "stdlib, or an installed dependency",
    "risk": "does the batch's declared proof strategy match what the units actually touch",
    "efficiency": "would refactoring the code or tests this batch touches pay for itself "
                  "WITHIN the sprint, so an accepted cost is chosen rather than absorbed",
}


def plan_intensity(unit_count: int) -> str:
    """How hard the pass works, scaled to batch size.

    The pass spends tokens BEFORE any value is delivered, on a sprint length that is already the
    standing complaint - so a two-unit batch must not pay for a forty-unit review. The rule is
    stated rather than emergent, so a reader can predict it and argue with it.
    """
    if unit_count <= 5:
        return "lite"
    if unit_count <= 20:
        return "full"
    return "ultra"


#: How many units each intensity examines individually. Beyond it the pass still runs, but it
#: says what it did not look at - a bounded pass that reports only what it found reads as
#: complete coverage, and a silent cap is how a partial sweep is mistaken for a full one.
PLAN_INTENSITY_CAP = {"lite": 5, "full": 20, "ultra": 40}


def plan_critique(units: list[str], findings: dict[str, list[dict]] | None = None) -> dict:
    """The plan-critic result over `units`.

    `findings` is what the lenses actually found, supplied by the caller that ran them - this
    function owns the SHAPE of the answer, never the judgement. A lens missing from `findings`
    is reported as NOT RUN; a lens present with an empty list is reported as having found
    nothing. Those are different facts and the difference is the whole point.
    """
    found = findings or {}
    intensity = plan_intensity(len(units))
    cap = PLAN_INTENSITY_CAP[intensity]
    examined = sorted(units)[:cap]
    lenses = {}
    for lens in PLAN_LENSES:
        if lens not in found:
            lenses[lens] = {"ran": False, "findings": []}
        else:
            lenses[lens] = {"ran": True, "findings": list(found[lens])}
    return {
        "intensity": intensity,
        "examined": examined,
        "skipped": sorted(set(units) - set(examined)),
        "lenses": lenses,
        "findings": [f for lens in PLAN_LENSES for f in lenses[lens]["findings"]],
    }


def render_plan_critique(rep: dict) -> list[str]:
    """The block the planner prints. States the cap it worked under and what that cap skipped."""
    lines = [f"  plan critic: intensity {rep['intensity']}, {len(rep['examined'])} unit(s) "
             f"examined individually"]
    if rep["skipped"]:
        shown = ", ".join(rep["skipped"][:8])
        more = f" (+{len(rep['skipped']) - 8} more)" if len(rep["skipped"]) > 8 else ""
        lines.append(f"  plan critic: NOT examined individually under this intensity: "
                     f"{shown}{more}")
    for lens in PLAN_LENSES:
        st = rep["lenses"][lens]
        if not st["ran"]:
            lines.append(f"  plan critic [{lens}]: NOT RUN - {PLAN_LENS_SUBJECT[lens]}")
        elif not st["findings"]:
            lines.append(f"  plan critic [{lens}]: ran, found nothing - "
                         f"{PLAN_LENS_SUBJECT[lens]}")
        else:
            lines.append(f"  plan critic [{lens}]: {len(st['findings'])} finding(s)")
    return lines


def undispositioned_plan_findings(rep: dict) -> list[dict]:
    """Findings with no disposition, or a disposition that records nothing.

    The retro already enforces file-or-decline and silence is not an answer; the plan critic is
    held to the same bar. A decline whose reason is a placeholder records that someone clicked
    past it, which is worse than no record because it looks like a decision.
    """
    out = []
    for f in rep.get("findings") or []:
        disp = (f.get("disposition") or "").strip()
        if not disp:
            out.append(f)
            continue
        if disp.lower().startswith("declined"):
            reason = disp.split(":", 1)[1].strip() if ":" in disp else ""
            if not reason or "{{" in reason:
                out.append(f)
    return out
