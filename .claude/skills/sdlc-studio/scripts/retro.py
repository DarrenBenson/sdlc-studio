#!/usr/bin/env python3
"""The deterministic retro spine: parse a retro, extract its lessons, and prove every
finding was dispositioned.

The retro was the only enforced ceremony with no script behind it. `gate.py` therefore
had nothing to interrogate but the filesystem - a glob for the filename - so an
empty file with the right name passed it. A gate is only as good as the thing it
can interrogate; this is that thing.

Everything here is mechanical, because everything here CAN be. Parsing a `## Lessons`
heading is parsing. Checking each finding is filed or declined is a set difference.
Judgement is reserved for what a lesson MEANS, never for whether the plumbing ran.

Subcommands:

  validate  content check - required sections, at least one real lesson, and every
            finding dispositioned. This is what the gate calls instead of a glob.
  extract   lift the `## Lessons` bullets into the project lessons log (`lessons add`),
            so a lesson written in a retro reaches the store that the next sprint reads.
  dispose   report every finding and its disposition; non-zero while any is undecided.
            The read-only half of `validate`, for a human deciding what to file.
  accuracy  estimate vs actual for the units in the retro's `Batch`: the plan's forecast
            against what telemetry measured, per unit and per batch, IN POINTS and in tokens.
            Flags any unit delivered above the split threshold. `--write` records it in the
            retro and appends the sprint's row to the velocity history.
  velocity  print the accumulated velocity history - POINTS DELIVERED PER SPRINT, and the
            tokens-per-point rate derived from it - so the next plan can see how the estimator
            has actually performed rather than trusting a constant.

The disposition rule. A finding is dispositioned when it is either filed as
an artefact (`CR0123` / `BG0045`) or DECLINED WITH A REASON. Declining is a first-class
answer and is equally green, so honesty costs exactly what noise costs and there is
nothing to game. What does not pass is silence: a finding written down and left to rot.

The measurement rule (the same rule, applied to numbers). A unit with no PER-UNIT telemetry
record has its per-unit ratio reported UNMEASURED and excluded from every ratio - never skipped,
never counted as accurate: a silent skip would let a batch of ten units with two measurements
report as a clean forecast. Silence is not a measurement, and the report says how many of the
batch it is actually speaking for. But UNMEASURED means NOT-YET-CAPTURED, not unmeasurable: the
harness tracks the token count deterministically. An interactive sprint (no runner) records no
per-unit actual, so its sprint total is supplied with `accuracy --tokens N` to yield a real,
DESCRIPTIVE sprint tokens-per-point over the delivered points - the number the velocity loop needs.
Never call an interactive sprint's tokens unknowable.

The velocity rule. VELOCITY IS POINTS DELIVERED PER SPRINT, and the tokens-per-point rate is
DERIVED from that history - actual tokens over points delivered, recomputed on every read.
Nothing hardcodes it. A rate written down as a constant is an article of faith within two
sprints, and this project has twice had to delete one; a rate that is a quotient of two things
the history records is re-measured every sprint, by construction. A unit delivered above the
split threshold is FLAGGED with its own tokens-per-point against the rest, so the rule that
says to decompose it is answerable from evidence each sprint rather than believed.

The forecast rule (the same rule again, on the other side of the ratio). The estimate is the
one the PLANNER RECORDED when it planned the sprint. It is read back verbatim and is never
re-derived from the constants in force - there is no such path, not even as a fallback. A
number recomputed at judgement time, by the model being judged, is not a prediction: change the
constants and every past sprint is retroactively deemed to have forecast something else, so the
ratio drifts to 1.0x and the loop can never falsify its own estimator. A unit with no recorded
plan-time forecast is UNFORECAST, named, and excluded from both sides - silence on the estimate
side is not evidence either, and it is not an invitation to invent one.

And the fit is not the test. A sprint whose actuals the constants were FITTED to is labelled
IN-SAMPLE: its ratio is training error, near 1.0x by construction, and it is excluded from any
accuracy figure shown as evidence. Only a sprint forecast by the constants in force, which they
were not fitted to, tells you anything.

What this does NOT do is recalibrate. It reports the accuracy and stops. The forecast
constants are a hypothesis fitted to a handful of units; auto-fitting them to the next
handful would fit noise and dress it as evidence. A human reads the history and decides.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import run_state, sdlc_md  # noqa: E402  (run_state: the run a close's tokens belong to)
import lessons  # noqa: E402  (sibling - the store a retro's lessons are extracted into)
import telemetry  # noqa: E402  (sibling - the measured actuals an estimate is judged against)

RETRO_DIR = "sdlc-studio/retros"
# The velocity history: one row per sprint, committed alongside the retros (a gitignored
# `.local/` file would not survive a fresh clone, and history the team cannot read is not
# history). LESSONS-SUMMARY.md is the precedent - a derived, committed sibling of the retros.
VELOCITY_FILE = "sdlc-studio/retros/VELOCITY.md"

# The sections a retro must carry. Absence is a structural failure, not a style note:
# each is a question the ceremony exists to ask, and a retro that skips one did not
# hold the ceremony.
REQUIRED_SECTIONS = (
    "Delivered",
    "What went well",
    "What was hard / what stalled",
    "Lessons",
    "Actions raised",
)

# `## Heading` -> body, to the next `##` of the same level.
SECTION_RE = re.compile(r"^##\s+(.+?)\s*$")

# A bullet that carries content. `{{placeholder}}` is a scaffold, not an answer - the
# template ships with them and a retro that still has them was never filled in.
BULLET_RE = re.compile(r"^\s*[-*]\s+(.*\S)\s*$")
PLACEHOLDER_RE = re.compile(r"\{\{.*?\}\}")

# A disposition is an artefact id, or an explicit decline carrying a reason.
#
# `LL` counts. Some findings are not tickets: the right outcome is a habit, and a habit's
# durable form is a recorded lesson. Refusing to accept one would push those findings toward a
# decline, which loses the lesson, or toward a make-work CR, which is the noise the decline path
# exists to prevent. It is no cheaper to game than declining, which is already free.
ARTEFACT_ID_RE = re.compile(r"\b((?:CR|BG|US|RFC|EP|LL)-?\d{4})\b", re.IGNORECASE)
DECLINED_RE = re.compile(r"^\s*declined\s*:\s*(.+\S)\s*$", re.IGNORECASE)

# A row in the `## Actions raised` table: | finding | disposition |
ROW_RE = re.compile(r"^\s*\|(?!\s*[-:]+\s*\|)([^|]+)\|([^|]+)\|\s*$")


# The leading id of a retro filename stem: `RETRO0049-slug` / `RETRO-0049-slug`.
# Three digits are accepted as well as four: `next_id` treats a 3-digit meta id as
# taken, so a legacy `RETRO001-x.md` holds its number and must also be findable -
# two readers of one id space that disagree on width lose the file between them.
# The width is a floor, not the match: the digits are still consumed greedily, so
# `RETRO001` does not resolve a `RETRO0012` file.
_STEM_ID_RE = re.compile(r"^([A-Za-z]+-?\d{3,})")


def find_retro(root, retro_id: str) -> Path | None:
    """The retro file for an id. One resolver, shared, so the gate and this script cannot
    disagree about which file they are talking about.

    Matched on the NORMALISED id, not by prefix-globbing the raw string: files are named
    `RETRO0049-...` while indexes, run state and prose all write `RETRO-0049`, and a literal
    glob silently found nothing for the dashed form. The close tail passed exactly that, so
    the velocity row went unrecorded for two consecutive sprints while the close still
    reported success.
    """
    d = Path(root) / RETRO_DIR
    if not d.is_dir():
        return None
    want = sdlc_md.norm_id(retro_id)
    if not want:
        return None
    hits = []
    for p in sorted(d.glob("*.md")):
        if not p.is_file():
            continue
        m = _STEM_ID_RE.match(p.stem)
        if m and sdlc_md.norm_id(m.group(1)) == want:
            hits.append(p)
    return hits[0] if hits else None


def sections(text: str) -> dict[str, list[str]]:
    """Map `## Heading` -> its body lines. Headings are matched on their exact text, so a
    renamed section reads as a MISSING section rather than silently passing - a retro
    that quietly dropped `Lessons` is the thing this is here to catch."""
    out: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        m = SECTION_RE.match(line)
        if m:
            current = m.group(1).strip()
            out[current] = []
            continue
        if current is not None:
            out[current].append(line)
    return out


def _fold_bullets(body: list[str]) -> list[str]:
    """The section's bullets, each with its WRAPPED CONTINUATION LINES folded back on.

    A bullet an author wrapped across three lines is ONE bullet. Read line by line it became
    one-third of a lesson, cut wherever the author's editor happened to break the line - so the
    store held a fragment and the headline stopped mid-clause. Where the text wraps is a
    typographic accident, and nothing downstream may depend on it.

    A blank line closes a bullet, so the paragraph after a list is not swallowed into it.
    """
    out: list[str] = []
    open_bullet = False
    for line in body:
        m = BULLET_RE.match(line)
        if m:
            out.append(m.group(1).strip())
            open_bullet = True
            continue
        if not line.strip():                      # a blank line ends the bullet
            open_bullet = False
            continue
        if open_bullet and not line.lstrip().startswith(("#", "|", ">")):
            out[-1] = f"{out[-1]} {line.strip()}"  # a wrapped continuation of the bullet above
        else:
            open_bullet = False
    return out


def _real_bullets(body: list[str]) -> list[str]:
    """Bullets with content in them, unwrapped. A `{{placeholder}}` bullet is the template
    talking, not the author, and counts as nothing."""
    found = []
    for text in _fold_bullets(body):
        if not text or PLACEHOLDER_RE.search(text):
            continue
        # An HTML comment is template guidance, not an answer.
        text = re.sub(r"<!--.*?-->", "", text).strip()
        if text:
            found.append(" ".join(text.split()))
    return found


# The headline a lesson is filed under - and the one line `sprint plan` prints in the lessons
# digest at the top of every plan. That digest is the surface the whole learning loop exists to
# serve, and the one an agent under effort pressure reads INSTEAD of opening the file. A headline
# that stops mid-clause is a lesson that will be skimmed past.
#
# So the title is the lesson's first SENTENCE, taken from the wrap-normalised text. Not its first
# line: where a line ends is where somebody's editor wrapped it.
LESSON_TITLE_MAX = 140
#: Abbreviations whose full stop does not end a sentence. Without this, "e.g. the seed" titles a
#: lesson "e.g." A single-character token (an initial, or the `r` of `r = 0.42.`) is excluded by
#: length rather than by listing every one.
_ABBREV = frozenset({"e.g", "i.e", "cf", "vs", "etc", "fig", "approx", "no", "cr", "bg", "us"})
_SENTENCE_END_RE = re.compile(r"[.!?]\s")


def lesson_title(text: str) -> str:
    """A lesson's headline: its first complete SENTENCE, from the wrap-normalised text.

    Independent of where the author broke the line, which is the whole defect. A lesson that is
    already one short sentence is its own title (so the store's existing entries do not churn);
    a very long first sentence is elided at a word boundary rather than cut mid-word."""
    flat = " ".join(str(text or "").split())
    if not flat:
        return ""
    first = flat
    for m in _SENTENCE_END_RE.finditer(flat):
        end = m.start()
        prev = re.split(r"[\s(\[]", flat[:end])[-1].lower()
        if len(prev) <= 1 or prev in _ABBREV:   # an initial, a decimal, or a known abbreviation
            continue
        first = flat[:end + 1]
        break
    if len(first) <= LESSON_TITLE_MAX:
        return first
    cut = first[:LESSON_TITLE_MAX].rsplit(" ", 1)[0].rstrip(" ,;:")
    return f"{cut}..."


def lessons_in(text: str) -> list[str]:
    """The retro's lessons, as written. This is the input `extract` lifts into the store."""
    return _real_bullets(sections(text).get("Lessons", []))


def dispositions_in(text: str) -> list[dict]:
    """Every row of `## Actions raised`, with its disposition classified.

    Returns one dict per finding: {finding, raw, state, detail}, where state is
    'filed' (an artefact id), 'declined' (with a reason) or 'undecided' (anything
    else - blank, a placeholder, or a bare 'declined' with no reason).
    """
    rows = []
    for line in sections(text).get("Actions raised", []):
        m = ROW_RE.match(line)
        if not m:
            continue
        finding, disp = m.group(1).strip(), m.group(2).strip()
        # The template's own header row is not a finding.
        if finding.lower() in {"finding", "issue"} or not finding:
            continue
        state, detail = "undecided", ""
        # Order matters. An explicit `declined:` prefix WINS over an artefact id in its
        # reason - a decline routinely cites the work it defers to ("declined: belongs to
        # RFC0034"), and reading that id as a filing would report the finding as ticketed
        # when it was deliberately not. A bare `declined` with no reason stays undecided:
        # silence wearing a decision's clothes.
        if PLACEHOLDER_RE.search(disp) or not disp:
            state = "undecided"
        elif (d := DECLINED_RE.match(disp)) and not PLACEHOLDER_RE.search(d.group(1)):
            state, detail = "declined", d.group(1).strip()
        elif ARTEFACT_ID_RE.search(disp):
            state, detail = "filed", ARTEFACT_ID_RE.search(disp).group(1).upper()
        rows.append({"finding": finding, "raw": disp, "state": state, "detail": detail})
    return rows


def validate(root, retro_id: str) -> dict:
    """The content check the gate calls. Errors are blocking; each names its own remedy.

    This is deliberately NOT a glob. A 0-byte file called RETRO9999.md satisfied
    the old leg, so the one gate that made the retrospective un-skippable was the one an
    agent could satisfy with `touch`. Existence is not evidence.
    """
    path = find_retro(root, retro_id)
    if path is None:
        return {"ok": False, "id": retro_id, "path": None, "errors": [
            f"no retro file for {retro_id} in {RETRO_DIR}/ - write it before closing "
            f"the sprint (artifact.py new --type retro)"]}

    text = path.read_text(encoding="utf-8")
    errors: list[str] = []

    present = sections(text)
    for want in REQUIRED_SECTIONS:
        if want not in present:
            errors.append(
                f"missing section '## {want}' - a retro that skips it did not ask the "
                f"question the section exists to ask")

    if "Lessons" in present and not lessons_in(text):
        errors.append(
            "no lesson recorded - '## Lessons' is empty or still holds its "
            "{{placeholder}}. A sprint that taught nothing is a claim, not a default; "
            "if it truly taught nothing, say so in a bullet")

    rows = dispositions_in(text)
    if "Actions raised" in present and not rows:
        errors.append(
            "'## Actions raised' has no rows - answer the question: are there any CRs or "
            "Bugs to raise for the issues found? To say no, record a row declining it "
            "with a reason. Silence is not an answer")
    undecided = [r for r in rows if r["state"] == "undecided"]
    for r in undecided:
        errors.append(
            f"finding not dispositioned: {r['finding'][:60]!r} - file it (BG/CR id) or "
            f"decline it with a reason ('declined: <why>')")

    return {
        "ok": not errors,
        "id": retro_id,
        "path": str(path),
        "errors": errors,
        "lessons": lessons_in(text),
        "findings": rows,
        "filed": [r["detail"] for r in rows if r["state"] == "filed"],
        "declined": [r["finding"] for r in rows if r["state"] == "declined"],
    }


# ---------------------------------------------------------------------------
# Estimate vs actual: the plan's forecast, judged against what the sprint cost.
# ---------------------------------------------------------------------------

# `> **Batch:** BG0126, BG0127, CR0248` - the units the sprint set out to deliver.
BATCH_RE = re.compile(r"(?m)^>?\s*\*\*Batch:\*\*\s*(.+)$")
DATE_RE = re.compile(r"(?m)^>?\s*\*\*Date:\*\*\s*(.+?)\s*$")
# `> **Delivered:** 5 / 5` - the retro's OWN declared unit count. The second number is the
# total the sprint set out to deliver, which is what the Batch field enumerates.
DELIVERED_RE = re.compile(r"(?m)^>?\s*\*\*Delivered:\*\*\s*(\d+)\s*/\s*(\d+)")


class BatchCountMismatch(ValueError):
    """The retro's Batch field parses to a different unit count than the retro itself declares
    in its `Delivered: N / M` header. A range like `BG0247-BG0256` reads naturally but the
    parser expands no ranges, so it matches only the bare endpoints and a whole-sprint token
    numerator lands over a partial points denominator - a velocity row wrong by orders of
    magnitude in the one file the planner re-measures its rate from. Refused BEFORE
    `record_velocity` writes: a partial denominator must never reach the record, and CR0391's
    fixed-term fit reads the same columns."""


def declared_unit_count(text: str) -> int | None:
    """The unit count the retro declares in its `Delivered: N / M` header (the total, M), or
    None when the header is absent or still a `{{placeholder}}`. None means "nothing to
    cross-check against" and never a mismatch: a retro predating the header is unaffected."""
    m = DELIVERED_RE.search(PLACEHOLDER_RE.sub("", text))
    return int(m.group(2)) if m else None


def batch_count_check(text: str) -> dict:
    """Cross-check the parsed Batch against the retro's own declared unit count.

    `{"parsed", "declared", "parsed_ids", "ok"}`. `ok` is True when the counts agree, or when
    the retro declares no count to check against (an older retro, or an unfilled header). A
    disagreement is the range-in-the-Batch-field defect: the writer named its units as a range
    the parser could not expand, so half the batch was silently dropped."""
    parsed_ids = batch_ids(text)
    declared = declared_unit_count(text)
    parsed = len(parsed_ids)
    ok = declared is None or parsed == declared
    return {"parsed": parsed, "declared": declared, "parsed_ids": parsed_ids, "ok": ok}


def _batch_mismatch_message(check: dict, retro_id: str) -> str:
    """The actionable refusal: it says what to do (name the units individually), not merely
    that a count disagreed."""
    return (f"retro {retro_id}: the Batch field parses to {check['parsed']} unit(s) "
            f"({', '.join(check['parsed_ids']) or 'none'}) but the retro declares "
            f"{check['declared']} in its `Delivered: N / M` header. The parser expands no "
            f"ranges, so a Batch written as a range (`BG0247-BG0256`) drops all but its "
            f"endpoints, and a partial points denominator must never reach VELOCITY.md. Name "
            f"the delivered units individually in the Batch field, then re-run.")

# The generated block inside `## Estimate vs actual`. Markers, not a whole-section
# rewrite: the section also carries the author's reading of the numbers, and a tool that
# ate the analysis every time it refreshed the table would teach people not to run it.
ACCURACY_BEGIN = "<!-- accuracy:begin (generated by retro.py accuracy --write) -->"
ACCURACY_END = "<!-- accuracy:end -->"
ACCURACY_SECTION = "Estimate vs actual"
ACCURACY_HEADING_RE = re.compile(r"(?im)^##\s+estimate\s+vs\.?\s+actual\b.*$")

VELOCITY_HEADER = """<!--
Generated by `retro.py accuracy --write`. One row per sprint retro: how many POINTS the sprint
delivered, what the plan forecast the batch would cost, and what it actually cost.

VELOCITY IS THE POINTS COLUMN. It is the number an agile team plans with, and the reason it is
here rather than a token total is that the tokens-per-point RATE is DERIVED from it - actual
tokens over points delivered, re-measured every sprint from this file. A rate that is written
down as a constant instead is an article of faith within two sprints, and this project has
twice had to delete one. Nothing may hardcode it: read it back with `retro.py velocity`.

The Points are the sizes the PLAN recorded, never the sizes on the artefacts today. A size
revised once the outcome was known is not an estimate, and the whole point of the column is
that it was written down before anyone knew.

The Estimate column is the forecast AS RECORDED AT PLAN TIME, and the Constants column names
the estimator that produced it. Neither is ever recomputed. A row re-derived from whatever the
constants say today is not a record of a prediction, and a history of those cannot falsify the
estimator that wrote it: recalibrate, and every past sprint is retroactively deemed to have
forecast something else.

Read the Sample column before the Ratio. IN-SAMPLE means the constants in force were fitted to
that sprint's actuals: its ratio is training error, it lands near 1.0x by construction, and it
is evidence of nothing. Only an OUT-OF-SAMPLE row - forecast by the constants in force, on a
sprint they were not fitted to - tells you whether the estimator works. The planner quotes only
those.

Read the Oversized column before trusting a row's Tokens/pt. It counts the units the sprint
delivered ABOVE the split threshold, and a point stops being a stable unit of cost up there:
measured, the 13s ran 1.9x cheaper per point than every band below, so a row with an oversized
unit in it has a rate dragged downward by a unit that should have been decomposed.

This is a RECORD, not a calibration. Nothing here re-fits the forecast constants
automatically - a fit to a handful of sprints would fit noise. A human reads the trend
and decides whether the constants have earned a change.

Read the coverage columns too. A ratio computed over 2 rated units of 10 is a ratio about
2 units, and the row says so.

Read the MODEL column before comparing any two rows. Cost per unit is meaningless without
knowing which model paid it: a sprint delivered by a smaller model must not land in the same
average as one delivered by a larger, and the mean of the two would describe neither. A sprint
that MIXED models records `mixed` and NO ratio at all, rather than an averaged number that is
about no run that ever happened.

An EMPTY Actual (tokens) cell means the sprint's token cost was not measured, and the NOTE
column says why. It never means the sprint cost nothing: a sprint that spent no tokens does
not exist, so a `0` there could only ever have been a sum over an empty set of measured units
published as though it were a measurement. Rows written before that was fixed carried exactly
that, and the reader treats such a `0` as the absence it is - it is not a data point, and no
rate is derived from it.

Read the SOURCE column before quoting an Actual as evidence. `per-unit` is a sum of per-unit
telemetry and `harness` is read off the harness meter; both are machine reads. `supplied` is a
figure an operator TYPED, which is a claim about what a sprint cost, not a measurement of it.
`harness+supplied` is the meter read PLUS the totals delegated agents reported for themselves.
An empty Source is unrecorded - the rows written before the column existed - and unrecorded is
what it stays, because back-filling provenance would invent the very thing the column records.

A `harness` figure is a LOWER BOUND, never an equality. The meter is the session transcript,
and the transcript records no subagent usage at all: measured on one live session, 6,624,813
tokens of usage carried ZERO sidechain records. So a sprint that delegated work to agents cost
MORE than its harness row says - one published 439,982 while its cluster agents had reported
787,834 between them. Their totals reach a row only when somebody supplies them, which is what
`harness+supplied` marks, and even that sum bounds the sprint from below rather than measuring
it. Compare a fan-out sprint's rate with a single-thread sprint's only with that in mind.
-->
# Velocity history

| Retro | Date | Units | Measured | Forecast | Points | Estimate (tokens, plan-time) | Actual (tokens) | Ratio (est/actual) | Tokens/pt | Oversized | Wall (s) | Constants | Sample | Model | Note | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
"""

# The history is parsed by COLUMN NAME, not position, so a row written before the plan-time
# forecast was recorded (which has no Constants and no Sample) still reads - and reads as what
# it is: a row carrying no record of any forecast, and therefore no evidence. A row written
# before the model was recorded reads the same way: `model` is None, and None is reported as
# unrecorded rather than assumed to be whatever is in use today. The same property is what lets
# the Points columns be ADDED without rewriting a single historical row: an older row simply
# records no points, which is exactly what happened.
#
# `Tokens/pt` is deliberately NOT parsed. It is a quotient of two columns that are, and a
# derived number read back as though it were a measurement is how a rate escapes its evidence.
VELOCITY_COLUMNS = (
    ("retro", "id"), ("date", "date"), ("units", "units"), ("measured", "measured"),
    ("forecast", "forecast"), ("points", "points"), ("estimate", "estimate"),
    ("actual", "actual_tokens"), ("ratio", "ratio"), ("oversized", "oversized"),
    ("wall", "wall_time_s"), ("constants", "constants"), ("sample", "sample"),
    ("model", "model"), ("note", "note"), ("source", "source"),
)
#: A sprint whose rated units were delivered by more than one model. Its ratio is not recorded.
MODEL_MIXED = "mixed"
#: A sprint recorded before the model was captured. Not "the model we use now".
MODEL_UNRECORDED = "unrecorded"


def batch_ids(text: str) -> list[str]:
    """The unit ids named in the retro's `> **Batch:**` field, in order, de-duplicated.

    An unfilled `{{batch}}` yields nothing, which reads downstream as a batch with no
    units - correct, since a retro that never said what it delivered has nothing to measure.
    """
    m = BATCH_RE.search(text)
    if not m:
        return []
    line = PLACEHOLDER_RE.sub("", m.group(1))
    # The batch line names delivery units interleaved with `(...)` provenance parentheticals -
    # `(EPxxxx-EPyyyy, from CR.../RFC...)`, `(absorbing CR0139)`, `(RFC-first)` - which epic
    # decomposed them or which request they came from. Those ids are context, NOT delivery units,
    # and only delivery units carry a plan-time forecast, so counting them padded the UNFORECAST
    # list with noise. Strip each parenthetical IN PLACE (not truncate at the first `(`, which
    # would silently drop every real unit listed AFTER an inline parenthetical); a line with none
    # is unaffected.
    line = re.sub(r"\([^)]*\)", "", line)
    out: list[str] = []
    for hit in ARTEFACT_ID_RE.finditer(line):
        rid = sdlc_md.norm_id(hit.group(1))
        if rid.startswith("LL"):  # a lesson is not a unit of delivery
            continue
        if rid not in out:
            out.append(rid)
    return out


def _sample_of(retro_id: str, constants) -> str:
    """Where this sprint stands relative to the estimator in force (sprint.sample_class).

    The import is deferred - `validate` is on the gate's path and must not pay for the
    planner's import graph - and it reads a DECLARATION (which sprints the constants were
    fitted to), never a formula. Nothing here recomputes an estimate."""
    try:
        import sprint  # noqa: PLC0415
        return sprint.sample_class(retro_id, constants)
    except Exception as exc:  # noqa: BLE001 - an unclassifiable row is reported, never fatal
        sdlc_md.debug("retro._sample_of", exc)
        return "unknown"


#: How far a unit's tokens-per-point may sit from its sprint's own rate before the SIZE is
#: called wrong rather than the run unusual. The band the RFC set before the data was seen
#: (0.75x-1.25x), reused here so a sprint is judged by the same bar the model was.
SIZE_BAND = 0.25


def _rate(tokens: int | float, points: int | float):
    """Tokens per point, or None when there are no points to divide by. Never 0: a unit with no
    recorded size has no rate, and a rate of nothing is not a rate."""
    return round(tokens / points) if points else None


def _delivered_points(root, unit_ids) -> int:
    """Summed `Points` of the DELIVERED units, read from their ARTEFACTS. The descriptive-velocity
    denominator - available even when no plan-time forecast was recorded (an interactive sprint
    reports UNFORECAST), unlike the forecast telemetry the estimate-vs-actual ratio reads. Only a
    unit in a TERMINAL state counts: a batch may name a unit that slipped (still In Progress), and
    counting its points as delivered would inflate the denominator and understate the real rate -
    the exact over-claim a sprint about honest measurement must not make."""
    total = 0
    for uid in unit_ids:
        hit = sdlc_md.find_by_id(root, uid)
        if not hit:
            continue
        path, type_ = hit
        text = sdlc_md.read_text_safe(path)  # a bad artefact must not crash the velocity read
        status = sdlc_md.canonical_status(sdlc_md.extract_field(text, "Status"),
                                          sdlc_md.status_vocab(type_, root))
        if not sdlc_md.is_terminal_status(type_, status or ""):
            continue   # not delivered - do not count it toward the delivered points
        pts = sdlc_md.read_points(text)
        if isinstance(pts, int) and pts > 0:
            total += pts
    return total


def _worker_hours(root, unit_ids) -> float | None:
    """Summed runner worker-time (`wall_time_s`) over the batch's measured units, in hours - the
    SECONDARY velocity's denominator. None when NO unit carries a wall-time record: an interactive
    sprint has no runner worker time, so points-per-worker-hour honestly reads UNMEASURED rather
    than dividing by a fabricated zero. Ceremony is EXCLUDED here (this is worker time, for tuning
    the tool), which is exactly why it is not the planning number."""
    import telemetry
    actuals = telemetry.latest_actuals(telemetry.read_all(root))
    want = {sdlc_md.norm_id(u) for u in unit_ids}
    secs, seen = 0.0, False
    for uid, rec in actuals.items():
        if sdlc_md.norm_id(uid) in want and isinstance(rec.get("wall_time_s"), (int, float)):
            secs += rec["wall_time_s"]
            seen = True
    return round(secs / 3600, 3) if seen else None


def _run_covers(state: dict, unit_ids) -> bool:
    """Does this run-state's batch speak for these units?

    A strict MAJORITY of the units must be in the batch, not merely one in common. Run-state
    batches are CUMULATIVE, so a previous sprint's state can share a single carried-over
    (failed-then-redelivered) unit with this one, and a one-unit intersection would then lend
    that other run's whole elapsed - and its whole spend - to this sprint. The majority rule
    still accepts a cumulative superset that covers the sprint, which is the common case: the
    current run's own state carries earlier ids too.

    ONE rule, shared by both quantities read off a run: the hours it was open and the tokens
    it spent. Either one taken from a run that is not this sprint's is the same error.
    """
    run_batch = {sdlc_md.norm_id(x) for x in (state.get("batch") or [])}
    retro_units = {sdlc_md.norm_id(u) for u in unit_ids}
    if not retro_units:
        return False   # a retro naming no units gives nothing for a run to cover
    return len(run_batch & retro_units) * 2 > len(retro_units)


def retro_units(root, retro_id: str) -> list[str]:
    """The delivery units a retro records, or an empty list when there is no such retro."""
    path = find_retro(root, retro_id)
    return batch_ids(path.read_text(encoding="utf-8")) if path else []


def _elapsed_hours(root, unit_ids) -> tuple[float | None, str | None]:
    """Wall-clock hours the run was OPEN - the PRIMARY velocity's denominator, ceremony included -
    read from the run-state (`started_at` -> `ended_at`, or now if still open). Returns
    `(hours, source)`.

    Trusted ONLY when the run-state's batch COVERS this sprint's units (`_run_covers`, the same
    rule the token capture obeys). A one-unit intersection with an older cumulative batch would
    otherwise report that run's full age (observed live: 43h) as this sprint's elapsed - the
    exact confounding CR0273 warns about. When it does not cover, or no run was opened (an
    interactive sprint, whose wall-clock would count operator-away gaps as sprint time), this
    returns None and the primary reads UNMEASURED unless the operator supplies a real figure
    with `--elapsed-hours`."""
    try:
        from lib import run_state
        st = run_state.read(root)
    except Exception:  # noqa: BLE001 - a velocity read must never break the retro
        return None, None
    if not _run_covers(st, unit_ids):
        return None, None  # the run-state does not cover this sprint - its elapsed is not ours
    # The idle deduction is `telemetry`'s, CALLED rather than re-derived (D0052). Two copies of
    # a duration rule is how one sprint comes to have two elapsed figures, and the published
    # points-per-hour is then set by whichever reader the close happens to ask. `hours` is None
    # for an OPEN run (no `ended_at`): extending it to `now` would report the run's own age,
    # including any operator-away gap since it opened, as sprint time - the confounder CR0273
    # warns about. It reads UNMEASURED until the operator supplies a real figure.
    span = telemetry.elapsed_excluding_idle(st.get("started_at"), st.get("ended_at"), st)
    hours = span.get("hours")
    return (hours, "run-state") if hours else (None, None)


def accuracy(root, retro_id: str, sprint_tokens: int | None = None,
             elapsed_hours: float | None = None) -> dict:
    """Estimate vs actual for every unit in the retro's batch - IN POINTS, and in tokens.

    `sprint_tokens` is the SPRINT-level actual token spend: the harness tracks the token
    count deterministically, but the runner-only telemetry captures a per-unit `actual` only for a
    runner-driven sprint, so an INTERACTIVE sprint's per-unit rows stay UNMEASURED. Supplying the
    sprint total (from the harness / operator) lets the batch report a real
    tokens-per-point - `sprint_tokens / points delivered` - instead of nothing. It does NOT invent
    per-unit actuals (those honestly stay unmeasured); it records the batch-level figure the
    velocity loop needs. A batch-level count, so it is not attributed to any single unit.

    The estimate is the forecast the planner RECORDED when it planned the sprint
    (`telemetry.forecasts`), read back verbatim. It is never re-derived from the constants in
    force - there is no such path, not even as a fallback. An estimate recomputed at judgement
    time, from the model it is meant to be judging, is not a prediction: recalibrate and every
    past sprint is retroactively deemed to have forecast something else, the ratio drifts to
    1.0x, and the loop can never falsify its own estimator. A recorded 5.2x miss - the entire
    evidence for one recalibration - was erased that way by the recalibration it caused.

    THE POINTS ARE READ BACK THE SAME WAY, from the same record, for the same reason. A size
    read off the artefact today may have been revised once the outcome was known, and a size
    revised with hindsight is not an estimate. So a unit whose plan recorded no points is
    UNSIZED: it is named, it contributes no points to the velocity, and nothing invents a
    number for it.

    Per unit: the recorded size, the recorded forecast, the measured actual, the ratio
    (estimate / actual, so >1 means the plan over-forecast) and the tokens it cost per point -
    which is the number that says whether the SIZE was right, not merely whether a token number
    was. Per batch: the same, summed over the RATED units - those with BOTH a recorded forecast
    and a measurement - plus the points delivered, the sprint's measured rate, and any unit
    delivered above the split threshold.

    Both silences are named, and both are excluded from both sides of the ratio:
      UNMEASURED - forecast, but no telemetry record. Silence is not a measurement.
      UNFORECAST - measured, but no plan-time forecast was recorded. Silence on the estimate
                   side is not evidence either, and it is not an invitation to invent one.
    """
    path = find_retro(root, retro_id)
    if path is None:
        return {"ok": False, "id": retro_id, "path": None, "units": [],
                "errors": [f"no retro file for {retro_id} in {RETRO_DIR}/"]}

    text = path.read_text(encoding="utf-8")
    measured_by_id = telemetry.actuals(root)
    forecast_by_id = telemetry.forecasts(root)

    units: list[dict] = []
    for uid in batch_ids(text):
        fc = forecast_by_id.get(uid) or {}
        rec = measured_by_id.get(uid, {})
        est = fc.get("tokens")
        # Actual tokens reconcile with the SPEND report: a per-attempt record (an escalation) may
        # carry no flat `tokens`, only an `attempts` list. Reading flat-only would report that unit
        # UNMEASURED here while the report priced its summed tokens - the two honest subsystems
        # contradicting. So fall back to the summed attempts (and the delivering model = the last
        # attempt), exactly the tokens `unit_cost` prices. A legacy record keeps its flat value.
        _attempts = telemetry.attempts_of(rec)
        # ATTEMPTS-FIRST, matching unit_cost and the spend report - the two must never disagree
        #. latest_actuals aggregates a unit's records into one attempts list (rework
        # summed), so reading the attempts here IS reading the whole cost.
        if _attempts:
            _token_vals = [a.get("tokens") for a in _attempts if a.get("tokens") is not None]
            tokens = sum(_token_vals) if _token_vals else None
        else:
            tokens = rec.get("tokens")
        # The unit's model SET across ALL its attempts. A unit delivered across more than one
        # model is ITSELF mixed: its tokens cannot be booked to a single model's rate, so
        # it marks the batch mixed and is kept out of the per-model rows. Single-model and legacy
        # flat records read as exactly one model, unchanged.
        _unit_models = sorted({a.get("model") for a in _attempts if a.get("model")})
        if len(_unit_models) == 1:
            _model = _unit_models[0]
        elif len(_unit_models) > 1:
            _model = MODEL_MIXED
        else:
            _model = rec.get("model")
        points = fc.get("points")
        points = points if isinstance(points, int) and points > 0 else None
        has_est = isinstance(est, (int, float)) and est > 0
        has_act = isinstance(tokens, (int, float)) and tokens > 0
        u = {"id": uid, "type": rec.get("type"),
             "complexity": fc.get("complexity", fc.get("seed")),
             "seed": fc.get("seed"), "estimate": est if has_est else None,
             "constants": fc.get("constants"), "planned_at": fc.get("planned_at"),
             # WHO sized it, WHAT SIZE they called, and WHAT delivered it. All read back from
             # the record, never inferred: an unrecorded model is `None` and reports as
             # unrecorded, not as "presumably the one we use now".
             "estimator": fc.get("estimator"), "points": points,
             "model": _model, "unit_models": _unit_models,
             "actual_tokens": tokens if has_act else None,
             "wall_time_s": rec.get("wall_time_s"), "ratio": None,
             "tokens_per_point": None,
             "oversized": bool(points and points > sdlc_md.POINTS_SPLIT_ABOVE),
             "state": "measured", "reason": ""}
        if not has_est:
            why = ["no plan-time forecast recorded"]
            if not has_act:
                why.append("no telemetry token record")
            u["state"], u["reason"] = "unforecast", "; ".join(why)
        elif not has_act:
            u["state"], u["reason"] = "unmeasured", "no telemetry token record"
        else:
            u["ratio"] = round(est / tokens, 2)
            u["tokens_per_point"] = _rate(tokens, points)
        units.append(u)

    rated = [u for u in units if u["state"] == "measured"]
    # The sprint's DELIVERED points: the points of the units this batch delivered, read from their
    # ARTEFACTS - the denominator for a sprint-level tokens-per-point when `sprint_tokens` is
    # supplied. Deliberately NOT the forecast telemetry: an interactive sprint records no plan-time
    # forecast (it reports UNFORECAST), but the delivered stories/bugs carry real Points. This is a
    # DESCRIPTIVE velocity number about what shipped, distinct from the forecast-vs-actual ratio
    # above (which must stay on the plan-time recorded points, never the artefact's revisable size).
    delivered_points = _delivered_points(root, [u["id"] for u in units])
    # WHETHER a sprint total was supplied is a separate fact from what it was worth, and no
    # truthiness test can carry it: an explicit 0 is the operator retracting a wrongly recorded
    # actual, an absent value is a plain re-run that must preserve one. Both read as falsy, so
    # the intent travels to the writer as its own flag.
    sprint_tokens_supplied = (isinstance(sprint_tokens, (int, float))
                              and not isinstance(sprint_tokens, bool))
    sprint_tokens = (int(sprint_tokens)
                     if sprint_tokens_supplied and sprint_tokens > 0 else None)
    est_sum = sum(u["estimate"] for u in rated)
    act_sum = sum(u["actual_tokens"] for u in rated)
    # THE PLAN'S FORECAST FOR THE WHOLE BATCH, over every unit that HAS one - not only the
    # rated units. `est_sum` above is the ratio's numerator and must describe exactly the units
    # `act_sum` does, but the published plan-time estimate is a fact about the PLAN, knowable
    # whether or not anything was later measured. Summed over the rated units it read 0 for
    # every sprint that measured nothing, which the history then published in a column named
    # `Estimate (tokens, plan-time)` - a prediction of zero tokens, next to a forecast that had
    # been recorded and simply was not read. None when no unit was forecast: that is an
    # absence, and the writer renders it blank rather than as a prediction nobody made.
    forecast_est = [u["estimate"] for u in units if u["estimate"]]
    plan_est = sum(forecast_est) if forecast_est else None
    walls = [u["wall_time_s"] for u in rated if isinstance(u["wall_time_s"], (int, float))]
    # THE SPRINT'S VELOCITY: the points its rated units carried, as the PLAN recorded them.
    # A rated unit with no recorded size is unsized - counted nowhere, invented nowhere.
    sized = [u for u in rated if u["points"]]
    pts_sum = sum(u["points"] for u in sized)
    # A unit above the split threshold is FLAGGED, not disqualified. It counts toward the
    # velocity (the team did deliver it), and it is named with its own tokens-per-point beside
    # the rate of everything at or below the threshold - because that comparison is the whole
    # evidence for the decomposition rule, and it must be re-answerable every sprint rather
    # than taken on faith. In the blind re-estimation the 13s ran at 14,144 tokens per point
    # against ~25,000 for every band below: systematically OVER-estimated, exactly where the
    # literature says estimator consistency collapses.
    within = [u for u in sized if not u["oversized"]]
    over = [u for u in sized if u["oversized"]]
    rate_within = _rate(sum(u["actual_tokens"] for u in within),
                        sum(u["points"] for u in within))
    # The estimator that produced this batch's forecasts. More than one means the batch was
    # planned across a constants change and judges no single model - it is not evidence.
    #
    # Read from every FORECAST unit, not only the rated ones. Which estimator made a forecast is
    # a property of the forecast, knowable whether or not that unit was ever measured. Sourcing
    # it from `rated` meant a sprint with no token telemetry - every interactive sprint, until
    # CR0278 lands - collected nothing, fell through to SAMPLE_NONE, and printed "no plan-time
    # forecast was recorded" directly beneath its own "9 of 9 forecast at plan time". The
    # forecasts were on disk and their estimates were printed on every line above it.
    seen = {json.dumps(u["constants"], sort_keys=True) for u in units if u["constants"]}
    constants = json.loads(seen.pop()) if len(seen) == 1 else ("mixed-constants" if seen else None)
    # THE MODELS THAT DELIVERED THE RATED UNITS. A ratio pooled across two of them is a
    # statement about neither: a sprint half-delivered by a smaller model and half by a larger
    # would land in one mean, and the mean would describe no run that ever happened. So when the
    # batch is mixed the pooled ratio is REFUSED and the per-model figures are given instead.
    # Refusing to average is not refusing to report.
    # The distinct models across ALL attempts of the rated units - NOT just each unit's last
    # attempt. A single unit that escalated across models therefore makes the batch mixed,
    # so the pooled ratio is refused exactly as a two-unit two-model batch is; the escalation can
    # no longer hide as a single-model 'opus' batch.
    models = sorted({m for u in rated for m in u.get("unit_models", []) if m})
    mixed = len(models) > 1
    refused = (f"REFUSED: this batch was delivered by more than one model "
               f"({', '.join(models)}). One ratio across two models describes neither of them - "
               f"read the per-model rows instead." if mixed else None)
    # VELOCITY: the PRIMARY planning read is points delivered / elapsed sprint hours,
    # CEREMONY INCLUDED - what a session actually delivers. Elapsed comes from the run-state; an
    # interactive sprint has none (and its wall-clock counts operator-away gaps), so it reads
    # UNMEASURED unless the operator supplies a real figure. The SECONDARY is points-per-worker-hour
    # (runner wall-time, ceremony removed) for tuning the tool, UNMEASURED interactive. Both are
    # DESCRIPTIVE ONLY - fed to no gate, never auto-refitted (see the module doctrine).
    # An explicit --elapsed-hours is an operator OVERRIDE and wins outright: a matched
    # run-state must never silently override the figure the operator supplied. Only when none is
    # supplied does the run-state provide the elapsed.
    if isinstance(elapsed_hours, (int, float)) and elapsed_hours > 0:
        elapsed, elapsed_source = round(float(elapsed_hours), 3), "supplied"
    else:
        elapsed, elapsed_source = _elapsed_hours(root, [u["id"] for u in units])
    worker_hours = _worker_hours(root, [u["id"] for u in units])
    ppeh = round(delivered_points / elapsed, 2) if elapsed and delivered_points else None
    ppwh = round(delivered_points / worker_hours, 2) if worker_hours and delivered_points else None
    return {
        "ok": True,
        "id": retro_id,
        "path": str(path),
        "date": (m.group(1).strip() if (m := DATE_RE.search(text)) else ""),
        # The Batch field cross-checked against the retro's own declared unit count. A
        # disagreement is refused at the write path (cmd_accuracy) and, belt-and-braces, by
        # record_velocity itself, so a partially-parsed batch never reaches VELOCITY.md.
        "batch_check": batch_count_check(text),
        "units": units,
        "n_units": len(units),
        "n_measured": len(rated),
        "n_forecast": sum(1 for u in units if u["state"] != "unforecast"),
        "n_unmeasured": sum(1 for u in units if u["state"] == "unmeasured"),
        "n_unforecast": sum(1 for u in units if u["state"] == "unforecast"),
        "n_sized": len(sized),
        "unmeasured": [u["id"] for u in units if u["state"] == "unmeasured"],
        "unforecast": [u["id"] for u in units if u["state"] == "unforecast"],
        "unsized": [u["id"] for u in rated if not u["points"]],
        "constants": constants,
        "sample": _sample_of(retro_id, constants),
        "models": models,
        "mixed_models": mixed,
        "by_model": _by_model(rated),
        "batch": {
            "estimate": est_sum,
            # The forecast the PLAN made for this batch, over every forecast unit. The history's
            # Estimate column reads this one; `estimate` above stays the ratio's numerator.
            "plan_estimate": plan_est,
            "actual_tokens": act_sum,
            "ratio": None if mixed else (round(est_sum / act_sum, 2) if act_sum else None),
            "refused": refused,
            "wall_time_s": sum(walls) if walls else None,
            # The velocity, and the rate it implies. Both derived here from what was recorded;
            # neither is a constant anybody wrote down.
            "points": pts_sum,
            "tokens_per_point": None if mixed else _rate(act_sum, pts_sum),
            "tokens_per_point_within": None if mixed else rate_within,
            # CR0278: the sprint-level actual (harness-tracked) and the tokens-per-point it implies
            # over the DELIVERED points - the honest figure for an interactive sprint that has no
            # per-unit actuals. None until the sprint total is supplied (not unmeasurable, just
            # not-yet-captured).
            "sprint_actual_tokens": sprint_tokens,
            # Was a sprint total supplied at all? The writer needs the distinction between
            # "no --tokens" (preserve what is recorded) and "--tokens 0" (clear it).
            "sprint_tokens_supplied": sprint_tokens_supplied,
            "delivered_points": delivered_points,
            "sprint_tokens_per_point": _rate(sprint_tokens, delivered_points) if sprint_tokens else None,
            # Velocity: PRIMARY = points/elapsed-hour (ceremony included, the planning
            # number); SECONDARY = points/worker-hour (runner time, tool-tuning). Both descriptive,
            # never a target, fed to no gate. None reads as UNMEASURED (interactive sprint).
            "sprint_elapsed_hours": elapsed,
            "elapsed_source": elapsed_source,
            "points_per_elapsed_hour": ppeh,
            "worker_hours": worker_hours,
            "points_per_worker_hour": ppwh,
            "split_above": sdlc_md.POINTS_SPLIT_ABOVE,
            "oversized": [{"id": u["id"], "points": u["points"],
                           "tokens_per_point": u["tokens_per_point"],
                           "actual_tokens": u["actual_tokens"]} for u in over],
            "basis": "units with BOTH a recorded plan-time forecast and a measurement; an "
                     "unmeasured or unforecast unit is excluded from both sides. A batch "
                     "delivered by more than one model reports NO pooled ratio - it is "
                     "segmented per model. Points are the sizes the PLAN recorded; a rated "
                     "unit the plan did not size contributes none, and none is invented",
        },
        "errors": [],
    }


def _by_model(rated: list[dict]) -> dict:
    """The rated units grouped by the model that delivered them, each with its own ratio.

    This is what a refusal to average hands back. A model with no recorded name groups under
    `unrecorded` - it is not silently merged with the model in use today."""
    out: dict[str, dict] = {}
    for u in rated:
        # A unit delivered across more than one model belongs to NO single model's row -
        # booking its summed tokens into one would poison that model's calibration. It is left out
        # of the per-model breakdown (the batch-level ratio is already refused as mixed).
        if u["model"] == MODEL_MIXED:
            continue
        b = out.setdefault(u["model"] or "unrecorded",
                           {"units": [], "estimate": 0, "actual_tokens": 0})
        b["units"].append(u["id"])
        b["estimate"] += u["estimate"]
        b["actual_tokens"] += u["actual_tokens"]
    for b in out.values():
        b["n"] = len(b["units"])
        b["ratio"] = (round(b["estimate"] / b["actual_tokens"], 2)
                      if b["actual_tokens"] else None)
    return out


def _fmt(n) -> str:
    return f"{n:,}" if isinstance(n, (int, float)) else "-"


#: The estimator's SHAPE is not fixed, and the history must survive it changing. It has changed
#: twice already (a complexity-weighted budget, then a flat per-unit rate, now a rate per point),
#: and a cell that only knew how to render the estimator of the day would make every older row
#: unreadable the moment it moved - which would quietly delete the only evidence that the older
#: model was wrong. So a cell is `KEY=INT` pairs, whatever the keys are, and the two names the
#: history already carries in short form are read back into the keys they stood for.
LEGACY_CONSTANT_KEYS = {"base": "BASE_TOKEN_BUDGET", "tpc": "TOKENS_PER_COGNITIVE"}
LEGACY_CONSTANT_SHORT = {v: k for k, v in LEGACY_CONSTANT_KEYS.items()}
CONSTANTS_PAIR_RE = re.compile(r"([A-Za-z_][\w]*)\s*=\s*(-?\d+)")


def constants_cell(c) -> str:
    """The estimator that produced a forecast, as one table cell. Recorded, not assumed: a row
    must say which model it is judging, or it says nothing.

    The two keys the existing history was written with keep their short spelling, so the rows
    already on disk round-trip byte-for-byte rather than being rewritten under a new schema."""
    if not isinstance(c, dict) or not c:
        return "mixed" if c == "mixed-constants" else "-"
    return " ".join(f"{LEGACY_CONSTANT_SHORT.get(k, k)}={v}" for k, v in c.items())


def parse_constants(cell: str):
    """A `Constants` cell back into the estimator it names, or None when the row records none
    (a legacy row, whose estimate was re-derived and therefore is not a forecast at all)."""
    pairs = CONSTANTS_PAIR_RE.findall(cell or "")
    if not pairs:
        return "mixed-constants" if (cell or "").strip().lower() == "mixed" else None
    return {LEGACY_CONSTANT_KEYS.get(k.lower(), k): int(v) for k, v in pairs}


#: What each sample class means, in the retro and in the history. Written next to the number so
#: nobody has to know the convention to read the row correctly.
SAMPLE_NOTE = {
    "in-sample": "IN-SAMPLE: the constants in force were FITTED to these actuals. This ratio "
                 "is TRAINING ERROR - it lands near 1.0x by construction and is not evidence "
                 "the estimator works. It is excluded from the accuracy the planner reports.",
    "out-of-sample": "OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were "
                     "not fitted to. This is the only kind of row that tells you anything.",
    "stale-constants": "STALE CONSTANTS: forecast by a DIFFERENT estimator from the one now in "
                       "force. It judges that one, not this one, and is excluded.",
    "mixed-constants": "MIXED CONSTANTS: this batch was forecast across a change of estimator, "
                       "so it judges no single model. Excluded.",
    "unforecast": "UNFORECAST: no plan-time forecast was recorded, so there is no prediction to "
                  "judge. Nothing is re-derived to fill the gap.",
}


def _points_lines(res: dict) -> list[str]:
    """The velocity, the rate it implies, and the decomposition rule ANSWERED - one paragraph
    each, and none of them printed when there is nothing measured to say it about.

    This is the half of the report that asks whether the SIZES were right. A token ratio only
    ever said whether one number matched another; a rate per point says whether the team's
    estimate of how big the work was survived contact with the work.
    """
    b = res["batch"]
    out: list[str] = []
    # CR0278: the SPRINT-level tokens-per-point (harness-tracked actual over the delivered points).
    # Printed first and unconditionally when supplied, so an INTERACTIVE sprint - which has no
    # per-unit actuals and would otherwise fall into the "no velocity" branch below - still gets a
    # real, deterministic velocity number. Descriptive, never a target.
    if b.get("sprint_tokens_per_point"):
        out.append(
            f"**Sprint tokens/point: {b['sprint_tokens_per_point']:,}** "
            f"({b['sprint_actual_tokens']:,} tokens over {b['delivered_points']} delivered points, "
            f"harness-tracked). The token count is deterministic (supply it with `accuracy "
            f"--tokens N`) - not UNMEASURED. A descriptive velocity, never a target.")
    elif b.get("sprint_actual_tokens") and not b.get("delivered_points"):
        out.append(
            f"**{b['sprint_actual_tokens']:,} tokens supplied, but no rate:** the batch has no "
            f"delivered unit carrying Points, so there is no denominator. Size the delivered "
            f"stories/bugs, or the rate stays uncomputable.")
    # VELOCITY: the PRIMARY planning read - points delivered / elapsed sprint hours,
    # ceremony INCLUDED - and the SECONDARY worker-time figure. Both DESCRIPTIVE, never a target.
    dp = b.get("delivered_points")
    if dp:
        if b.get("points_per_elapsed_hour"):
            src = "run-state" if b.get("elapsed_source") == "run-state" else "operator-supplied"
            out.append(
                f"**Velocity: {b['points_per_elapsed_hour']} points/elapsed-hour** "
                f"({dp} points over {b['sprint_elapsed_hours']}h, {src}, ceremony included). This is "
                f"the planning number - points per SESSION within the observed single-session "
                f"envelope; it is NOT a linear per-point rate to extrapolate to a 1-point or "
                f"100-point sprint, and it is descriptive, never a target.")
        else:
            out.append(
                f"**Velocity (points/elapsed-hour): UNMEASURED.** No run-state elapsed for this "
                f"sprint (an interactive sprint's wall-clock would count operator-away gaps as "
                f"sprint time). Supply a real elapsed with `accuracy --elapsed-hours H` to record it "
                f"- descriptive, never a target.")
        if b.get("points_per_worker_hour"):
            out.append(
                f"  secondary (tool-tuning): {b['points_per_worker_hour']} points/worker-hour over "
                f"{b['worker_hours']}h of runner worker time, ceremony removed - NOT the planning "
                f"number, distinct from the elapsed velocity above.")
        else:
            out.append("  secondary (points/worker-hour): UNMEASURED - no runner worker-time "
                       "records (an interactive sprint has none).")
    if not b["points"]:
        if res["n_measured"]:
            out.append(
                f"**No points recorded at plan time** for the rated units, so this sprint "
                f"records NO velocity. It is not zero and it is not assumed: a size the plan "
                f"never wrote down is a size nobody predicted, and it is not reconstructed "
                f"from the artefacts as they stand today.")
        return out

    rate = b["tokens_per_point"]
    if rate:
        out.append(
            f"**Velocity: {b['points']} points delivered**, at **{rate:,} tokens per point** "
            f"({_fmt(b['actual_tokens'])} tokens over {res['n_sized']} sized unit(s)). That "
            f"rate is MEASURED here and derived from the history in VELOCITY.md - it is never "
            f"a constant, so the next plan forecasts with what this project actually costs.")
    elif b.get("refused"):
        out.append(
            f"**Velocity: {b['points']} points delivered.** No tokens-per-point rate is "
            f"reported: this batch was delivered by more than one model, and a rate pooled "
            f"across two models describes neither.")
    if res.get("unsized"):
        out.append(
            f"Unsized: {', '.join(res['unsized'])}. Measured and forecast, but the plan "
            f"recorded no Points, so they add nothing to the velocity and nothing to the rate.")

    over, within = b["oversized"], b["tokens_per_point_within"]
    if over:
        detail = ", ".join(
            f"**{u['id']}** ({u['points']} points, {_fmt(u['tokens_per_point'])} tokens/pt)"
            for u in over)
        against = (f"against **{within:,} tokens/pt** for the units at or below "
                   f"{b['split_above']}" if within else
                   "and there is no unit at or below the threshold to price it against")
        out.append(
            f"**Above {b['split_above']} points, and SHOULD HAVE BEEN SPLIT: {detail}** - "
            f"{against}. This is the decomposition rule answered with THIS sprint's evidence "
            f"rather than taken on faith: above the threshold the estimate stops being worth "
            f"having (in the blind re-estimation the 13s ran 1.9x cheaper per point than every "
            f"band below - systematically over-estimated), so a unit this size is a triage "
            f"failure, not an estimation problem. Split it next time and the rate holds.")
    elif b["points"]:
        out.append(
            f"Every sized unit came in at or below {b['split_above']} points, so the "
            f"decomposition rule held and the rate above is uncontaminated by an over-sized "
            f"unit.")
    return out


def size_verdict(u: dict, rate) -> str:
    """Was the SIZE right? A unit whose tokens-per-point sits inside the band around its own
    sprint's rate was sized correctly RELATIVE to the rest of the batch - which is the only
    claim a relative estimate ever makes. Outside it, the call was too big or too small, and
    the report says which. With no rate (nothing sized) there is nothing to compare against,
    and it says that instead of guessing."""
    if not u.get("tokens_per_point") or not rate:
        return "-"
    ratio = u["tokens_per_point"] / rate
    if ratio > 1 + SIZE_BAND:
        return f"under-sized ({ratio:.2f}x)"    # it cost MORE per point than the batch did
    if ratio < 1 - SIZE_BAND:
        return f"over-sized ({ratio:.2f}x)"
    return "sized right"


def accuracy_block(res: dict) -> str:
    """The generated markdown the retro carries: the table, the coverage, and the caveat."""
    b = res["batch"]
    rate = b.get("tokens_per_point")
    rows = ["| Unit | Points | Estimate (plan-time) | Actual | Ratio (est/actual) | Tokens/pt | "
            "Size | Wall | Model |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for u in res["units"]:
        model = u.get("model") or "-"
        pts = _fmt(u["points"])
        if u["state"] == "measured":
            wall = f"{u['wall_time_s']}s" if u["wall_time_s"] is not None else "-"
            size = ("**SHOULD HAVE BEEN SPLIT**" if u["oversized"]
                    else size_verdict(u, rate))
            rows.append(f"| {u['id']} | {pts} | {_fmt(u['estimate'])} | "
                        f"{_fmt(u['actual_tokens'])} | {u['ratio']}x | "
                        f"{_fmt(u['tokens_per_point'])} | {size} | {wall} | {model} |")
        elif u["state"] == "unmeasured":
            rows.append(f"| {u['id']} | {pts} | {_fmt(u['estimate'])} | - | "
                        f"**UNMEASURED** ({u['reason']}) | - | - | - | {model} |")
        else:
            rows.append(f"| {u['id']} | - | - | {_fmt(u['actual_tokens'])} | "
                        f"**UNFORECAST** ({u['reason']}) | - | - | - | {model} |")
    wall = f"{b['wall_time_s']}s" if b["wall_time_s"] is not None else "-"
    ratio = f"**{b['ratio']}x**" if b["ratio"] is not None else (
        "**REFUSED**" if b.get("refused") else "-")
    models = ", ".join(res.get("models") or []) or "-"
    rows.append(f"| **Batch (rated units only)** | **{_fmt(b['points'])}** | "
                f"**{_fmt(b['estimate'])}** | **{_fmt(b['actual_tokens'])}** | {ratio} | "
                f"**{_fmt(rate)}** | | **{wall}** | {models} |")

    n, m, f = res["n_units"], res["n_measured"], res["n_forecast"]
    lines = [ACCURACY_BEGIN, "", *rows, "",
             f"**{m} of {n} unit(s) measured; {f} of {n} forecast at plan time.**"]
    for para in _points_lines(res):
        lines += ["", para]
    if b.get("refused"):
        lines += ["", b["refused"], ""]
        lines.append("| Model | Units | Estimate | Actual | Ratio |")
        lines.append("| --- | --- | --- | --- | --- |")
        for model, seg in sorted((res.get("by_model") or {}).items()):
            r = f"{seg['ratio']}x" if seg["ratio"] is not None else "-"
            lines.append(f"| {model} | {', '.join(seg['units'])} | {_fmt(seg['estimate'])} | "
                         f"{_fmt(seg['actual_tokens'])} | {r} |")
    if res["unmeasured"]:
        lines.append(
            f"Unmeasured: {', '.join(res['unmeasured'])}. They are excluded from the batch "
            f"ratio - an unmeasured unit is not evidence that the estimate was right.")
    if res["unforecast"]:
        lines.append(
            f"Unforecast: {', '.join(res['unforecast'])}. No plan-time forecast was recorded "
            f"for them, so they are excluded too. The estimate is NOT re-derived from today's "
            f"constants: a number computed at judgement time, by the model being judged, is "
            f"not a prediction.")
    if m == 0:
        lines.append("No unit in this batch is rated, so this sprint says nothing about the "
                     "estimator's accuracy.")
    note = SAMPLE_NOTE.get(res.get("sample"), "")
    lines += ["",
              f"Forecast by `{constants_cell(res.get('constants'))}`, recorded at plan time. "
              f"{note}".strip(),
              "",
              "Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it "
              "under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across "
              "sprints, and change the constants only on evidence a human has looked at.",
              ACCURACY_END]
    return "\n".join(lines)


def write_accuracy(root, res: dict) -> Path:
    """Record the block in the retro. Idempotent: refreshing replaces the generated block
    between its markers and leaves everything the author wrote around it untouched."""
    path = Path(res["path"])
    text = path.read_text(encoding="utf-8")
    block = accuracy_block(res)

    if ACCURACY_BEGIN in text and ACCURACY_END in text:
        head, rest = text.split(ACCURACY_BEGIN, 1)
        _old, tail = rest.split(ACCURACY_END, 1)
        new = head + block + tail
    elif (m := ACCURACY_HEADING_RE.search(text)):
        # The section exists but was written by hand: keep the heading and the prose, and
        # insert the generated block directly under the heading.
        at = m.end()
        new = text[:at] + "\n\n" + block + "\n\n" + text[at:].lstrip("\n")
    else:
        heading = f"\n## {ACCURACY_SECTION}\n\n{block}\n"
        anchor = re.search(r"(?m)^##\s+Actions raised\s*$", text)
        new = (text[:anchor.start()] + heading.lstrip("\n") + "\n" + text[anchor.start():]
               if anchor else text.rstrip("\n") + "\n" + heading)

    sdlc_md.atomic_write(path, new)
    return path


# ---------------------------------------------------------------------------
# The velocity history: what the estimator has actually done, sprint by sprint.
# ---------------------------------------------------------------------------

#: Where the harness keeps its per-session transcripts, overridable for tests and
#: non-standard installs. Defined beside the reader in `lib.run_state` (which stamps the
#: run's opening baseline from the same meter) and re-exported here.
TRANSCRIPTS_ENV = run_state.TRANSCRIPTS_ENV

#: The CURRENT session's harness-tracked token total. The ONE reader, shared with the
#: baseline `open_run` stamps - see `run_state.session_tokens`. It is a per-SESSION total,
#: which is why the close does not record it directly: `run_attributed_tokens` below narrows
#: it to a LOWER BOUND on what this run cost. Never to what the run actually spent: the
#: transcript records no subagent usage at all, so delegated work is missing from the figure.
harness_tokens = run_state.session_tokens


def run_attributed_tokens(root, retro_id: str, transcripts_dir=None) -> dict:
    """The tokens the open run is known to have spent AT LEAST, for the retro that is being
    recorded - or a stated reason there is no such number. Never the run's cost: the session
    transcript records no subagent usage, so any delegated work nobody supplied a total for is
    absent from it, and the figure bounds the run from below. Same shape as `harness_tokens`:
    {"tokens", "source", "basis"} or {"tokens": None, "reason"}.

    `retro_id` is REQUIRED, and the units are read from that retro, because the delta is only
    this retro's spend if the open run is the run that delivered it. Reading the open run and
    trusting the caller to have asked about the right one is how a number correct about one
    sprint gets stamped on another.

    The harness meter is cumulative per SESSION, not per sprint. Closing a second sprint in
    one session against the raw meter books the first sprint's spend - and the conversation
    around it - as the second sprint's own: it published 341,450 then 472,691 tokens/point
    against a measured ~25,000/pt rate, and both had to be blanked by hand afterwards. So
    the run's opening reading is subtracted from the current one.

    NOT ATTRIBUTABLE, never a fallback to the raw total, when:

    * no run is open, or the open run carries no baseline (it was opened before the baseline
      existed - the live case at this fix's own sprint);
    * the open run's batch does not COVER the units the retro records, so the run that is open
      is not the run that delivered this sprint;
    * the current session is not the one the baseline was taken in, so the two readings are
      of different meters;
    * the meter reads at or below the baseline, which is the same statement by other means.

    The failure mode this closes is a published number that LOOKS measured, so every one of
    those returns no number at all rather than a plausible one.
    """
    try:
        state = run_state.read(root)
    except run_state.RunStateError as exc:
        return {"tokens": None, "reason": f"not attributable: the run state is unreadable ({exc})"}
    rid = state.get("run_id") or "the current run"
    base = state.get(run_state.TOKEN_BASELINE)
    baseline = base.get("tokens") if isinstance(base, dict) else None
    if not isinstance(baseline, int) or isinstance(baseline, bool) or baseline < 0:
        return {"tokens": None, "reason": (
            f"not attributable: {rid} carries no session-token baseline, so the session total "
            f"cannot be separated from any earlier sprint's in the same session. A run opened "
            f"before the baseline existed reports no token figure rather than a session-wide "
            f"one")}
    # WHOSE spend is it? The meter says what the open run cost; only the batch says whether the
    # open run is the one this retro records. `sprint close` always works on the open run, but
    # `accuracy --id <an older retro> --tokens-from-harness` after a later `sprint plan --write`
    # does not, and the delta would land on the older sprint's row with nothing saying so.
    units = retro_units(root, retro_id)
    if not _run_covers(state, units):
        named = ", ".join(units) if units else "no units at all"
        return {"tokens": None, "reason": (
            f"not attributable: {rid}'s batch does not cover the units {retro_id} records "
            f"({named}), so its spend is a different sprint's. Record {retro_id} from the run "
            f"that delivered it, or supply the figure with `accuracy --tokens N`")}
    cap = harness_tokens(root, transcripts_dir)
    if not cap.get("tokens"):
        return {"tokens": None, "reason": f"not attributable: {cap.get('reason')}"}
    # The source is half the record, so a MISSING source refuses rather than waves through. The
    # earlier `base.get("source") and cap.get("source") and ...` form disabled the guard entirely
    # whenever either side lacked one, which is the failure mode the guard exists to prevent: an
    # unsourced baseline is precisely the one that cannot be shown to be this meter's.
    if not base.get("source") or not cap.get("source"):
        return {"tokens": None, "reason": (
            f"not attributable: {rid}'s baseline does not name the session it was read from, so "
            f"it cannot be shown to be a reading of this meter. A delta between two meters that "
            f"may not be the same one is not a spend")}
    if base["source"] != cap["source"]:
        return {"tokens": None, "reason": (
            f"not attributable: {rid} took its baseline in session {Path(base['source']).name} "
            f"but this close is running in {Path(cap['source']).name} - two different meters, "
            f"so their difference is not a spend")}
    delta = cap["tokens"] - baseline
    if delta <= 0:
        return {"tokens": None, "reason": (
            f"not attributable: the session meter reads {cap['tokens']:,}, at or below {rid}'s "
            f"opening baseline of {baseline:,} - no spend can be derived from that")}
    # MEASURED (main thread) + SUPPLIED (delegated), and the sum is a LOWER BOUND. The two halves
    # are different evidence and stay separately named: the delta is a meter reading, a delegated
    # total is a figure an agent reported. Neither the label nor the arithmetic may imply that
    # the transcript saw the delegated work - it never does.
    delegated = run_state.delegated_records(state)
    supplied = run_state.delegated_total(state)
    total = delta + supplied
    meter = (f"the current-session total {cap['tokens']:,} less the {baseline:,} on the meter "
             f"when the run opened (input + output + cache creation; cache reads excluded)")
    bound = (f"a LOWER BOUND, not the run's cost: the session transcript records no subagent "
             f"usage at all, so any delegated work no one supplied a total for is missing from "
             f"it")
    if supplied:
        basis = (f"{rid} cost AT LEAST {total:,}: {delta:,} MEASURED on the main thread "
                 f"({meter}), plus {supplied:,} SUPPLIED by {len(delegated)} delegated "
                 f"agent(s), which is a figure they reported rather than one measured here. "
                 f"{bound}")
    else:
        basis = (f"{rid} cost AT LEAST {delta:,}, its MAIN-THREAD spend: {meter}. No delegated "
                 f"total was supplied, and {bound}. Record one with "
                 f"`accuracy --delegated-tokens N --delegated-agent NAME`")
    return {"tokens": total, "measured_tokens": delta, "delegated_tokens": supplied,
            "delegated_records": len(delegated), "lower_bound": True,
            "source": cap["source"], "basis": basis}


def _tokens_cover_points(row: dict) -> bool:
    """True when a history row's Actual tokens describe the same units as its Points.

    Two honest shapes: every unit measured (the Actual is the full per-unit sum), or none
    measured with an Actual present (the Actual is the sprint-level harness total, which by
    definition covers the whole batch). A partly measured row pairs a partial numerator
    with a full denominator, so it carries no rate."""
    measured, units = row.get("measured"), row.get("units")
    if measured is None or units is None:
        return False
    if measured == units:
        return True
    return measured == 0 and bool(row.get("actual_tokens"))


def velocity_path(root) -> Path:
    return Path(root) / VELOCITY_FILE


def _velocity_num(cell: str):
    raw = (cell or "").replace(",", "").replace("*", "").rstrip("x").strip()
    try:
        return float(raw) if "." in raw else int(raw)
    except ValueError:
        return None


def _velocity_index(line: str) -> dict[str, int] | None:
    """Column name -> position, from the table's header row. None when the line is not one."""
    cells = sdlc_md.table_cells(line)
    if not cells or cells[0].strip().lower() != "retro":
        return None
    idx: dict[str, int] = {}
    for pos, cell in enumerate(cells):
        name = cell.strip().lower()
        for prefix, key in VELOCITY_COLUMNS:
            if name.startswith(prefix) and key not in idx:
                idx[key] = pos
    return idx


def velocity_history(root) -> list[dict]:
    """The accumulated history, oldest first. The read a plan makes: how the estimator has
    performed on real sprints, next to the constants it is about to forecast with.

    Every row carries the estimator that produced its forecast, so the reader can tell whether
    the row is evidence about the model in force or its own training error. A row with no
    recorded constants recorded no forecast, and `sprint.sample_class` reads it as exactly
    that - it is never assumed to have been forecast by whatever is in force today."""
    path = velocity_path(root)
    if not path.is_file():
        return []
    idx: dict[str, int] | None = None
    out: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if idx is None:
            idx = _velocity_index(line)
            continue
        cells = sdlc_md.table_cells(line)
        if not cells or len(cells) < 2:
            continue
        rid = cells[0].strip()
        # EITHER FORM reads, and both report the canonical one. The writer normalises now, but a
        # row minted dashed before it did must not stay invisible - it holds a real measurement,
        # and the next upsert rewrites it clean only if this read can see it first.
        if not re.fullmatch(r"RETRO-?\d{4}", rid, re.IGNORECASE):
            continue
        rid = sdlc_md.norm_id(rid)

        def cell(key: str, pos_map=idx, row=cells):
            pos = pos_map.get(key)
            return row[pos].strip() if pos is not None and pos < len(row) else ""

        model = cell("model").strip()
        note = cell("note").strip()
        # A model id is ONE token (`claude-opus-4-8`, `mixed`, `unrecorded`). A Model cell
        # holding a sentence is a row somebody corrected by hand before the Note column
        # existed, when the last cell was the only place a reason could go. Read it as the
        # note it is: a sentence must never reach the per-model segmentation as a model, and
        # the next rewrite then puts it in the column that now exists for it.
        if " " in model:
            note, model = note if note and note != "-" else model, "-"
        out.append({"id": rid.upper(), "date": cell("date"),
                    "units": _velocity_num(cell("units")),
                    "measured": _velocity_num(cell("measured")),
                    "forecast": _velocity_num(cell("forecast")),
                    # The velocity. Absent on a row written before points were recorded, and
                    # absent is what it stays: an unsized sprint delivered no measurable points,
                    # and back-filling one from the artefacts as they stand today would be
                    # inventing a prediction after the fact.
                    "points": _velocity_num(cell("points")),
                    "oversized": _velocity_num(cell("oversized")),
                    # A recorded 0 reads as ABSENT, for the same reason the Actual cell beside
                    # it does: it can only be the empty rated-unit sum the old writer published,
                    # and read as a number it is a plan-time prediction of zero tokens. 12 of
                    # the 17 rows on disk when this was fixed carried one.
                    "estimate": _velocity_num(cell("estimate")) or None,
                    # A recorded 0 reads as ABSENT, not as a spend of nothing. No sprint costs
                    # zero tokens, so a 0 in this column can only be the empty rated-unit sum
                    # the old writer published, and rows carrying one are on disk. Read as 0 it
                    # would be a data point about a sprint's cost; read as absent it is what it
                    # is, and the next rewrite republishes it as a blank rather than a figure.
                    "actual_tokens": _velocity_num(cell("actual_tokens")) or None,
                    "ratio": _velocity_num(cell("ratio")),
                    "wall_time_s": _velocity_num(cell("wall_time_s")),
                    "constants": parse_constants(cell("constants")),
                    "sample": cell("sample") or None,
                    "model": model if model and model != "-" else None,
                    "note": note if note and note != "-" else None,
                    # Absent on every row written before the column existed, and absent is what
                    # it stays. None reads as UNRECORDED downstream, never as a measurement.
                    "source": cell("source").strip() or None})
    return sorted(out, key=lambda r: r["id"])


def _retro_index(rid: str) -> int:
    """The numeric part of a retro id, for bounding a window. 0 when it has none."""
    m = re.search(r"(\d+)\s*$", sdlc_md.norm_id(rid) or "")
    return int(m.group(1)) if m else 0


def velocity_gaps(root, since: str | None = None) -> dict:
    """Every retro on disk with NO row in the velocity record, oldest first.

    Nothing else detects this. `velocity_history` reads the rows that are there and the report
    prints them, so a retro that never reached the file is invisible to both: the record can rot
    with no command saying so, and a skipped accuracy write cannot be told from a sprint that
    never happened. The rows are read with the same reader the planner uses, so a row the reader
    cannot parse counts as the gap it effectively is.

    `since` bounds the window at a retro id, by the same doctrine the close-owed baseline obeys:
    a project adopting this must not be handed a tail of history nothing can ever clear.
    """
    have = {r["id"] for r in velocity_history(root)}
    floor = _retro_index(since) if since else 0
    d = Path(root) / RETRO_DIR
    gaps: list[dict] = []
    total = 0
    if d.is_dir():
        for p in sorted(d.glob("RETRO*.md")):
            m = _STEM_ID_RE.match(p.stem)
            if not m:
                continue
            rid = sdlc_md.norm_id(m.group(1))
            if _retro_index(rid) < floor:
                continue
            total += 1
            if rid in have:
                continue
            text = sdlc_md.read_text_safe(p)
            dm = DATE_RE.search(text)
            gaps.append({"id": rid, "date": dm.group(1).strip() if dm else "",
                         "path": str(p)})
    gaps.sort(key=lambda g: g["id"])
    return {"gaps": gaps, "since": sdlc_md.norm_id(since) if since else None,
            "retros": total, "rows": len(have),
            "basis": "a retro with no row in the velocity record. The row is the demand, not a "
                     "token total: a row with a blank Actual and the reason it is blank records "
                     "that the sprint's cost was not recoverable, which no row at all does"}


def measured_rate(root) -> dict:
    """THE TOKENS-PER-POINT RATE, DERIVED FROM THE HISTORY. Never a constant.

    Actual tokens over points delivered, across every sprint that recorded both. That is the
    whole definition, and it is why it can be re-measured every sprint instead of decaying into
    an unvalidated number nobody dares touch - which is the fate of both estimators this project
    has already had to delete.

    The rate is a per-(PROJECT, MODEL) quantity. This reads ONE project's committed VELOCITY.md,
    so the project is constant across its rows and resolved once from the repo; it is stamped on
    the result and on every cell, so a figure lifted out of here is never mistaken for a different
    project's. SEGMENTED PER MODEL, and REFUSED across them, by the same rule the ratio already
    obeys: a rate averaged over a sprint delivered by a smaller model and one delivered by a
    larger describes neither, and a plan that forecast with it would be pricing work in a currency
    no run ever paid in. The CROSS-project pooling, and its refusal, lives in `collate_rate`,
    which reads the project off each record rather than off the repo it is reading.

    With no sprint that recorded points, there is NO rate - `None`, and the caller must say so.
    A project's first sprint cannot forecast from its own history, and the honest answer to that
    is to say it has none, not to hand back a number borrowed from somebody else's project.
    """
    project = telemetry.project_name(root)
    # Only sprints whose tokens and points describe the SAME units: the Points column is the
    # DELIVERED series, so a partial per-unit token sum divided by the full points would
    # quietly understate the rate. Excluded, not averaged in.
    rows = [r for r in velocity_history(root)
            if r.get("points") and isinstance(r.get("actual_tokens"), (int, float))
            and _tokens_cover_points(r)]
    by_model: dict[str, dict] = {}
    mixed: list[str] = []
    for r in rows:
        model = r.get("model") or MODEL_UNRECORDED
        if model == MODEL_MIXED:
            # A sprint delivered by more than one model already records no ratio, for the same
            # reason it can carry no rate: its tokens were paid by two payers. It is named and
            # excluded, never averaged.
            mixed.append(r["id"])
            continue
        b = by_model.setdefault(model,
                                {"sprints": [], "points": 0, "actual_tokens": 0, "oversized": 0})
        b["sprints"].append(r["id"])
        b["points"] += r["points"]
        b["actual_tokens"] += r["actual_tokens"]
        b["oversized"] += int(r.get("oversized") or 0)
    for b in by_model.values():
        b["n"] = len(b["sprints"])
        b["tokens_per_point"] = _rate(b["actual_tokens"], b["points"])
    why: list[str] = []
    if len(by_model) > 1:
        why.append(f"the history spans {len(by_model)} models ({', '.join(sorted(by_model))}). "
                   f"One rate across two models is a rate for neither - forecast with the row "
                   f"for the model that will do the work")
    if mixed:
        why.append(f"{', '.join(mixed)} was delivered by more than one model, so its tokens "
                   f"were paid by two payers and it carries no rate at all")
    refused = f"REFUSED: {'; and '.join(why)}." if why else None
    for b in by_model.values():
        b["project"] = project           # the cell is (project, model), not model alone
    only = next(iter(by_model.values())) if len(by_model) == 1 else None
    return {
        "project": project,
        "tokens_per_point": only["tokens_per_point"] if only else None,
        "model": next(iter(by_model)) if only else None,
        "points": only["points"] if only else None,
        "actual_tokens": only["actual_tokens"] if only else None,
        "sprints": only["sprints"] if only else [],
        "oversized": only["oversized"] if only else 0,
        "mixed_sprints": mixed,
        "by_model": by_model,
        "refused": refused,
        "basis": "actual tokens over points delivered, across the sprints in VELOCITY.md that "
                 "recorded both. Derived from the record every time it is read; never stored, "
                 "never fitted, and never assumed from a project that is not this one. It is a "
                 "rate for ONE (project, model) cell; pooling across projects is refused in "
                 "collate_rate, not here",
    }


#: Below this many qualifying whole-sprint rows the fixed per-sprint term is UNMEASURED: a fit
#: to one point cannot separate a fixed cost from a marginal one at all, and there is nothing to
#: fit. The APPLICATION threshold - how many rows before the fit may enter a forecast total - is
#: higher and lives with the planner (a line through two points is exact and proves nothing).
FIXED_MIN_QUALIFYING = 2


def _fit_fixed_marginal(points: list[float], actuals: list[float]) -> "tuple[float, float] | None":
    """Least-squares fit of `actual = fixed + marginal * points`, returning (fixed, marginal), or
    None when the points do not vary (a vertical spread cannot separate the two terms)."""
    n = len(points)
    sx, sy = sum(points), sum(actuals)
    sxx = sum(p * p for p in points)
    sxy = sum(p * a for p, a in zip(points, actuals))
    denom = n * sxx - sx * sx
    if denom == 0:
        return None
    marginal = (n * sxy - sx * sy) / denom
    fixed = (sy - marginal * sx) / n
    return fixed, marginal


def fixed_sprint_cost(root) -> dict:
    """THE FIXED PER-SPRINT COST, MEASURED from this project's own whole-sprint actuals.

    The token forecast prices the BUILD (points x a marginal rate). Two measured sprints showed
    the model has no parameter at all for the rest - the ceremony, the review rounds, the repairs
    and the close - and at real batch sizes that omission dwarfs the term the model does have.
    This fits it: `actual = fixed + marginal x points` across the record's WHOLE-SPRINT rows.

    A qualifying row carries recorded Points and a whole-sprint Actual - a sprint-level total that
    INCLUDES the ceremony (Measured is 0: the Actual is the harness meter over the whole session,
    not a per-unit build sum). A per-unit build sum (Measured equals Units) is EXCLUDED and named:
    it omits the very ceremony the fixed term exists to price, so fitting against it would fit the
    fixed cost to data that never contained it.

    UNMEASURED, with no figure at all - not the seed, not zero, not a scaled default - when fewer
    than `FIXED_MIN_QUALIFYING` rows qualify. It states how many it found, and the fit names the
    retro ids it rests on, so the number is traceable to the rows that produced it. This measures;
    whether a fit may be APPLIED to a forecast total is the planner's separate decision.

    Read-only and fail-safe: an unreadable record yields UNMEASURED, never an exception.
    """
    try:
        rows = velocity_history(root)
    except Exception as exc:  # noqa: BLE001 - no record must never break a plan
        sdlc_md.debug("retro.fixed_sprint_cost", exc)
        rows = []
    qualifying: list[dict] = []
    excluded: list[dict] = []
    for r in rows:
        pts = r.get("points")
        actual = r.get("actual_tokens")
        if not pts or not isinstance(actual, (int, float)) or actual <= 0:
            continue
        measured, units = r.get("measured"), r.get("units")
        if measured == 0:
            qualifying.append(r)                     # whole-sprint total, ceremony included
        elif isinstance(measured, (int, float)) and measured and measured == units:
            excluded.append({"id": r.get("id"), "reason": (
                "a per-unit build sum (Measured equals Units) omits the ceremony the fixed term "
                "exists to price, so counting it would fit the fixed cost against data that never "
                "contained it")})
    n = len(qualifying)
    base = {"fixed": None, "marginal": None, "sprints": [q.get("id") for q in qualifying],
            "n": n, "min": FIXED_MIN_QUALIFYING, "excluded": excluded, "unmeasured": True}
    if n < FIXED_MIN_QUALIFYING:
        base["reason"] = (
            f"UNMEASURED: {n} of the {FIXED_MIN_QUALIFYING} whole-sprint rows needed to fit a "
            f"fixed per-sprint term were found in VELOCITY.md"
            + (f", and {len(excluded)} per-unit build-sum row(s) were excluded (they omit the "
               f"ceremony the term prices)" if excluded else "")
            + ". No figure is supplied - not the seed, not zero, not a default")
        return base
    fit = _fit_fixed_marginal([float(q["points"]) for q in qualifying],
                              [float(q["actual_tokens"]) for q in qualifying])
    if fit is None:
        base["reason"] = (f"UNMEASURED: the {n} qualifying whole-sprint rows all carry the same "
                          f"point count, so a fixed term cannot be separated from a marginal one")
        return base
    fixed, marginal = fit
    return {"fixed": int(round(fixed)), "marginal": int(round(marginal)),
            "sprints": [q.get("id") for q in qualifying], "n": n, "min": FIXED_MIN_QUALIFYING,
            "excluded": excluded, "unmeasured": False,
            "reason": (f"fitted from {n} whole-sprint row(s) "
                       f"({', '.join(q.get('id') or '?' for q in qualifying)}) as "
                       f"actual = {int(round(fixed)):,} + {int(round(marginal)):,} x points")}


def collate_rate(roots) -> dict:
    """THE CROSS-PROJECT TOKENS-PER-POINT RATE, per (PROJECT, MODEL) CELL. Never a pooled figure.

    This is the reader for the multi-project tuning run: the operator forward-ports the skill onto
    several repos, each stamps its own project on every record, and their evidence is pooled here.
    The cell is read off the RECORD's own `project` and `model` - never off the directory it was
    read from - so records physically copied into one place stay attributable, which is the whole
    reason the project is stamped on the row and not inferred at read time.

    SEGMENT OR REFUSE, never silently average - the same rule `measured_rate` and the accuracy
    ratio already obey, now on the project axis too. A rate is computed WITHIN each (project,
    model) cell; NO number is ever summed across two cells. A points-vs-cost figure pooled across
    a fast project and a slow one, or across two models, describes neither - this project has twice
    withdrawn a finding to exactly that confound (a field that flipped sign between cohorts, and a
    field whose mere presence became a calendar artefact). So the pooled total is REFUSED and the
    per-cell rows are handed back instead. A record with no project reads as `unknown`; it is its
    own cell, never folded into a named project.

    A unit is rated only with BOTH a plan-time forecast carrying points AND a measured actual
    carrying tokens - the same bar every other rate obeys. Everything else is excluded, not
    invented.
    """
    if isinstance(roots, (str, Path)):
        roots = [roots]
    cells: dict[tuple, dict] = {}
    for root in roots:
        forecasts = telemetry.forecasts(root)
        actuals = telemetry.actuals(root)
        for uid, fc in forecasts.items():
            rec = actuals.get(uid, {})
            points = fc.get("points")
            tokens = rec.get("tokens")
            if not (isinstance(points, int) and points > 0
                    and isinstance(tokens, (int, float)) and tokens > 0):
                continue
            # The project and model are the RECORD's own - the actual's if it carries them, else
            # the forecast's - never the directory's. `unknown`/`unrecorded` are their own cells.
            project = rec.get("project") or fc.get("project") or telemetry.PROJECT_UNKNOWN
            model = rec.get("model") or "unrecorded"
            cell = cells.setdefault((project, model),
                                    {"project": project, "model": model, "units": [],
                                     "points": 0, "actual_tokens": 0})
            cell["units"].append(uid)
            cell["points"] += points
            cell["actual_tokens"] += tokens
    out = []
    for (project, model), c in sorted(cells.items()):
        c["n"] = len(c["units"])
        c["tokens_per_point"] = _rate(c["actual_tokens"], c["points"])
        out.append(c)
    projects = sorted({c["project"] for c in out})
    models = sorted({c["model"] for c in out})
    refused = None
    if len(out) > 1:
        why = []
        if len(projects) > 1:
            why.append(f"{len(projects)} projects ({', '.join(projects)})")
        if len(models) > 1:
            why.append(f"{len(models)} models ({', '.join(models)})")
        refused = (f"REFUSED: the pooled evidence spans {' and '.join(why) or 'more than one cell'}. "
                   f"A tokens-per-point rate across two cells describes neither - read the "
                   f"per-(project, model) rows. Pooling them is the cohort confound this project "
                   f"has twice withdrawn a finding to.")
    return {
        "cells": out,
        "projects": projects,
        "models": models,
        "refused": refused,
        "basis": "actual tokens over points delivered, WITHIN each (project, model) cell, read "
                 "from the record's own project and model. Never summed across cells; a record "
                 "with no project is its own `unknown` cell, never folded into a named one",
    }


def model_cell(res: dict) -> str:
    """The model a sprint's rated units were delivered by, as one history cell.

    `mixed` when more than one delivered it - and a mixed row records NO ratio, because a ratio
    across two models is a statement about neither."""
    models = res.get("models") or []
    if len(models) > 1:
        return MODEL_MIXED
    return models[0] if models else "-"


def _note_cell(text) -> str:
    """One table cell from a reason written for a human: single line, no pipe, or `-`."""
    flat = " ".join(str(text or "").split()).replace("|", "/")
    return flat or "-"


def _actual_note(res: dict, actual, existing=None) -> str | None:
    """WHY this row's Actual (tokens) cell is blank, or None when it is not blank.

    A blank with no reason beside it is indistinguishable from an oversight, and this project
    has already published the alternative: a `0` that read as a measurement.

    THIS RUN'S OWN STATEMENT FIRST, then what the row already carries, then the generic fact:

    - the close's not-attributable reason, which names the run, the meter, or the baseline that
      was missing;
    - an explicit `--tokens 0`, which is an operator RETRACTING a figure they know to be wrong.
      A total was supplied, deliberately, and the generic sentence below says the opposite;
    - the reason already recorded against this row. The column was added to stop a hand-written
      reason being lost, and regenerating it unconditionally lost it on the row's own next
      write - a rescued figure beside an overwritten reason for it. A recorded reason for a
      cell that is still blank is still the reason it is blank;
    - the generic statement, for a row that has never carried one.
    """
    if actual is not None:
        return None
    capture = (res.get("token_capture") or "").strip()
    if capture:
        return capture
    if (res.get("batch") or {}).get("sprint_tokens_supplied"):
        return ("retracted: a sprint total WAS supplied, as 0, withdrawing a figure recorded "
                "here in error. The cell is blank by instruction, not for want of a look")
    recorded = " ".join(str(existing or "").split())
    return recorded or (
        "not attributable: no unit carries per-unit telemetry and no sprint total was "
        "supplied, so the sprint's token cost is unrecorded rather than 0")


#: WHERE a row's Actual (tokens) figure came from. Two of the three are machine reads; the
#: third is an operator's typed claim, and a plan that cannot tell them apart quotes a typed
#: number as evidence of what a sprint cost. Absent is its own value: a row written before the
#: column existed records no provenance, and nothing back-fills one for it.
SOURCE_PER_UNIT = "per-unit"    # summed from per-unit telemetry - only a runner writes it
SOURCE_HARNESS = "harness"      # read off the harness transcript meter by --tokens-from-harness
SOURCE_SUPPLIED = "supplied"    # typed by an operator into `accuracy --tokens N`
#: The harness meter read PLUS delegated totals the agents themselves reported. Part machine
#: read, part claim, and the whole is a LOWER BOUND: the transcript carries no subagent usage,
#: so a delegated agent nobody supplied a total for is still missing from it.
SOURCE_HARNESS_SUPPLIED = "harness+supplied"
#: Not a recorded value: cmd_accuracy's signal that it re-used the figure already on the row,
#: so whatever provenance that row holds is the provenance of the figure it still holds.
SOURCE_UNCHANGED = "unchanged"


def _actual_source(res: dict, actual, existing=None) -> str | None:
    """The provenance mark for this row's Actual cell, or None when there is nothing to mark.

    A per-unit sum outranks everything: every unit carried its own record. Otherwise the figure
    is sprint-level, and the two ways one arrives are not the same evidence."""
    if actual is None:
        return None
    if res.get("n_measured"):
        return SOURCE_PER_UNIT
    declared = (res.get("token_source") or "").strip()
    if declared == SOURCE_UNCHANGED:
        return existing or None
    if declared in (SOURCE_HARNESS, SOURCE_SUPPLIED, SOURCE_HARNESS_SUPPLIED):
        return declared
    if (res.get("batch") or {}).get("sprint_tokens_supplied"):
        return SOURCE_SUPPLIED
    return existing or None


def record_velocity(root, res: dict) -> Path:
    """Upsert this retro's row into the history. Keyed by retro id, so re-running a sprint's
    accuracy report corrects its row rather than double-counting the sprint.

    The row records the plan-time estimate and the constants that produced it. The Sample cell
    is written for a human reading the file; the planner re-derives it at read time from those
    two facts, so a later refit reclassifies the row instead of leaving it quoted as validation
    for a model it helped fit.

    REFUSED, never written, when the batch failed its own count cross-check: a partially-parsed
    batch pairs a whole-sprint token numerator with a partial points denominator, and a row that
    wrong in the file the planner re-measures from is worse than no row. The write path refuses
    first; this is the second guard, so no future caller can reach the file around it."""
    check = res.get("batch_check")
    if isinstance(check, dict) and check.get("ok") is False:
        raise BatchCountMismatch(_batch_mismatch_message(check, res.get("id", "?")))
    b = res["batch"]
    # `ratio` is already None for a mixed-model sprint (accuracy refuses to pool it), so the
    # history inherits the refusal rather than re-deciding it in a second place.
    # NORMALISED, never verbatim: the id arrives in whichever form the caller held it - the
    # close scaffolds `RETRO-0060`, the files are named `RETRO0060` - and a dashed row is one
    # this file's own reader never parses. The row lands on disk and every consumer is blind to
    # it, which is the same failure `find_retro` was fixed for.
    row = {"id": sdlc_md.norm_id(res["id"]) or res["id"].upper(),
           "date": res.get("date") or "", "units": res["n_units"],
           "measured": res["n_measured"], "forecast": res.get("n_forecast"),
           # THE VELOCITY, and the count of units that were too big to be worth sizing. Both
           # recorded, so the rate can be derived from this file and its contamination seen.
           # Points-per-sprint is the PRIMARY series this file exists to hold, and it is
           # independent of whether anyone forecast the units: DELIVERED points (artefact-read)
           # first, the plan-recorded rated sum as the fallback for a batch whose artefacts
           # carry no points. The ratio columns keep their forecast gate - an unforecast unit
           # says nothing about the estimator, but its points were still delivered.
           "points": b.get("delivered_points") or b.get("points") or None,
           "oversized": len(b.get("oversized") or []),
           # The Actual cell: the per-unit sum for a measured (runner) sprint; the sprint-level
           # harness total for an interactive one that has no per-unit actuals. Never both
           # blended - which one a row carries is decidable from its own Measured cell.
           # The plan-time forecast over every unit that carried one, NOT the sum over the rated
           # units: a sprint that measured nothing rated nothing, so that sum was over an empty
           # set and published 0 as a prediction. Falsy is an absence here, exactly as it is in
           # the Actual cell below, and the preservation rule is the same.
           #
           # ONE limb, deliberately. A fallback to `b["estimate"]` - the rated-unit sum - read
           # as a live alternative and was dead code: the rated units are a subset of the
           # forecast ones and no estimate is negative, so `estimate <= plan_estimate` always,
           # and `plan_estimate` is absent only when NO unit was forecast, which makes the
           # rated sum 0 too. Restoring that limb would restore the exact 0-as-a-prediction
           # this column was fixed to stop publishing.
           "estimate": b.get("plan_estimate") or None,
           "actual_tokens": (b["actual_tokens"] if res["n_measured"]
                             else (b.get("sprint_actual_tokens") or b["actual_tokens"])),
           "ratio": b["ratio"], "wall_time_s": b["wall_time_s"],
           "constants": res.get("constants"), "sample": res.get("sample"),
           "model": model_cell(res)}
    history = velocity_history(root)
    # A rewrite must never replace a recorded number with the absence of one: an interactive
    # sprint's harness-captured actual would otherwise be erased by ANY later plain re-run,
    # whose per-unit sum is 0. Preserved here, in the writer itself, so every caller is
    # covered; a truthy new actual (per-unit sums, an explicit --tokens) still overrides.
    #
    # An explicit `--tokens 0` is the one falsy value that is an INSTRUCTION, not an absence:
    # the operator retracting a wrongly recorded actual. It reaches here as
    # `sprint_tokens_supplied` because zero cannot be told from absent by truthiness, and it
    # clears the cell rather than re-quoting the figure being retracted.
    #
    # The row as it already stands, read ONCE: the figure, the reason, and the provenance are
    # three facts about the same cell, and each is preserved by the same rule - this run's own
    # statement wins, and what is already recorded is never discarded for want of one.
    existing = next((r for r in history if r["id"] == row["id"]), None)
    # The forecast log lives in `.local/`, which is not committed, so a re-record on another
    # clone - or after a prune - sees no forecast at all. A recorded prediction is never
    # replaced by the absence of one; only a fresh forecast overrides it.
    if not row["estimate"] and existing and existing.get("estimate"):
        row["estimate"] = existing["estimate"]
    if not row["actual_tokens"]:
        if b.get("sprint_tokens_supplied"):
            row["actual_tokens"] = None
        elif existing and existing.get("actual_tokens"):
            row["actual_tokens"] = existing["actual_tokens"]
    # Whatever is left falsy here is an ABSENCE, and the cell says so. `b["actual_tokens"]` is
    # a sum over the RATED units, so a sprint that rated none - every interactive sprint -
    # summed an empty set to 0 and published it in a column named Actual (tokens). The
    # Tokens/pt cell beside it already refused, so the row contradicted itself; three rows were
    # corrected by hand, and the third correction was overwritten by the next close.
    if not row["actual_tokens"]:
        row["actual_tokens"] = None
    row["note"] = _actual_note(res, row["actual_tokens"], (existing or {}).get("note"))
    row["source"] = _actual_source(res, row["actual_tokens"], (existing or {}).get("source"))
    rows = [r for r in history if r["id"] != row["id"]] + [row]
    rows.sort(key=lambda r: r["id"])

    lines = [VELOCITY_HEADER.rstrip("\n")]
    for r in rows:
        ratio = f"{r['ratio']}x" if r["ratio"] is not None else "-"
        sample = r.get("sample") or _sample_of(r["id"], r.get("constants"))
        # Derived at write time from the two columns beside it, and never read back as though it
        # were a measurement. It is here for a human reading the file, not for a tool.
        # Only when tokens and points describe the SAME set of units: a fully measured sprint
        # (per-unit sums cover everything) or a wholly unmeasured one whose Actual is the
        # sprint-level harness total. A partial per-unit sum over the full delivered points
        # would understate the real rate, so it gets no cell.
        rate = (_rate(r["actual_tokens"] or 0, r.get("points") or 0)
                if _tokens_cover_points(r) else None)
        # An EMPTY cell is not a value, and a `|  |` in a markdown table is a lint failure as
        # well as an ambiguity: a retro that records no Date renders `-`, like every other
        # absent cell in the row.
        lines.append(f"| {r['id']} | {r['date'] or '-'} | {_fmt(r['units'])} | "
                     f"{_fmt(r['measured'])} | "
                     f"{_fmt(r.get('forecast'))} | {_fmt(r.get('points'))} | "
                     f"{_fmt(r['estimate'])} | "
                     f"{_fmt(r['actual_tokens'])} | {ratio} | {_fmt(rate)} | "
                     f"{_fmt(r.get('oversized'))} | {_fmt(r['wall_time_s'])} | "
                     f"{constants_cell(r.get('constants'))} | {sample} | "
                     f"{r.get('model') or '-'} | {_note_cell(r.get('note'))} | "
                     f"{r.get('source') or '-'} |")
    path = velocity_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    sdlc_md.atomic_write(path, "\n".join(lines) + "\n")
    return path


# ---------------------------------------------------------------------------
# MEASURE THE ESTIMATOR: per estimator, per model, and the coercion answer.
# ---------------------------------------------------------------------------
# The loop could quote what estimation is like IN GENERAL - a population average from a study of
# other people - and could not tell an operator whether THEIR judgement was any good. Those are
# different questions and only the second is actionable: a population figure measures, to an
# unknown degree, how much people CARE rather than how well they could estimate if they did, and
# no study can separate the two. A per-person figure against measured actuals can.
#
# THE RULE, applied on all three axes: SEGMENT OR REFUSE, never silently average.
#   - per MODEL: a figure spanning two models is refused. Cost per unit means nothing without
#     knowing which model paid it.
#   - per ESTIMATOR: never pooled, and never INFERRED. An unclaimed estimate belongs to nobody.
#   - per ERA: a size given freely and a size extracted by a gate are different data.
#
# And what a unit is RATED on is the SIZE THE PLAN RECORDED, not the size on the artefact today.
# Same rule as the token forecast: a size revised after the outcome is not a prediction, and this
# project has already seen one revised (M at filing, L by the time it closed).

#: Units below which a cohort says nothing. A correlation off two points is a line through two
#: points; a direction off one is an anecdote.
MIN_FOR_CORRELATION = 3
MIN_FOR_DIRECTION = 2
#: Rated units per era before the coercion comparison is allowed to claim an answer.
MIN_FOR_COERCION = 5
#: How far a class must sit from an estimator's own scale before the miss is called directional
#: rather than noise.
BIAS_BAND = 0.15


def _pearson(xs: list, ys: list) -> float | None:
    """Correlation, or None when there is nothing to correlate (too few points, or no variance
    on one axis - an estimator who called everything M has told us nothing about ordering)."""
    n = len(xs)
    if n < MIN_FOR_CORRELATION:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if not sxx or not syy:
        return None
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    return round(sxy / (sxx * syy) ** 0.5, 3)


def _bias(units: list[dict]) -> list[dict]:
    """The CLASSES of unit an estimator systematically under- or over-calls.

    A correlation tells you whether someone ranks work correctly. It does not tell them what to
    DO differently, and a bare r is not correctable. A direction is: "your 3s cost three times
    what your own scale implies" is an instruction. So each class (the size called, and the kind
    of unit) is priced against the estimator's OWN per-point rate - not against an absolute -
    because the question is whether they are internally consistent, not whether their points mean
    what someone else's points mean.
    """
    pts = [u["points"] for u in units]
    act = [u["actual_tokens"] for u in units]
    rate = sum(act) / sum(pts) if sum(pts) else 0
    classes: dict[str, list[dict]] = {}
    for u in units:
        classes.setdefault(f"{u['points']}-point", []).append(u)
        if u.get("type"):
            classes.setdefault(f"type {u['type']}", []).append(u)
    out: list[dict] = []
    for name, members in sorted(classes.items()):
        observed = sum(m["actual_tokens"] for m in members) / len(members)
        expected = rate * (sum(m["points"] for m in members) / len(members))
        ratio = round(observed / expected, 2) if expected else None
        if len(members) < MIN_FOR_DIRECTION or ratio is None:
            direction = "not enough units"
        elif ratio > 1 + BIAS_BAND:
            direction = "under-calls"     # it cost MORE than their own scale implies
        elif ratio < 1 - BIAS_BAND:
            direction = "over-calls"
        else:
            direction = "calibrated"
        out.append({"class": name, "n": len(members), "ratio": ratio,
                    "direction": direction,
                    "units": sorted(m["id"] for m in members)})
    return out


def _estimator_segments(units: list[dict]) -> dict:
    """Per-estimator figures within ONE model. Never across two - the caller has already
    grouped by model, because that is the only way this figure means anything."""
    by: dict[str, list[dict]] = {}
    for u in units:
        by.setdefault(u["estimator"], []).append(u)
    out: dict[str, dict] = {}
    for name, members in by.items():
        r = _pearson([m["points"] for m in members], [m["actual_tokens"] for m in members])
        out[name] = {
            "n": len(members),
            "units": sorted(m["id"] for m in members),
            "r": r,
            "mean_actual": round(sum(m["actual_tokens"] for m in members) / len(members)),
            "bias": _bias(members),
        }
    return out


def _coercion(units: list[dict]) -> dict:
    """THE COERCION HAZARD, answered with evidence rather than opinion.

    The grooming gate makes a SIZE COMPULSORY at filing. If sizing is a chore an engineer
    resents, a compulsory estimate is a CARELESS estimate - and a careless number is strictly
    worse than none, because it looks like data and is averaged in as though it were an estimate.
    The gate may be manufacturing precisely the noise it exists to remove.

    So: compare the sizes recorded when they were freely given against the sizes recorded once
    they were demanded, and report what comes out.

    AND CARRY THE CONFOUND. Before/after IS a cohort split. Everything else about a project moves
    over the same period - the work gets bigger, the units get harder, the team learns - and a
    difference between the eras is a difference between two cohorts, not proof of an effect of
    the gate. This project has already been bitten by exactly this shape once: a size field that
    only EXISTED on the later, larger units made itself look predictive purely by being present.
    A small cohort here says NOTHING, and the report says so rather than quoting an r it cannot
    support.
    """
    eras = {"voluntary": [], "compulsory": [], "unknown": []}
    for u in units:
        eras.setdefault(u["era"], []).append(u)
    by_era = {
        era: {"n": len(members),
              "units": sorted(m["id"] for m in members),
              "r": _pearson([m["points"] for m in members],
                            [m["actual_tokens"] for m in members]),
              "mean_actual": (round(sum(m["actual_tokens"] for m in members) / len(members))
                              if members else None)}
        for era, members in eras.items()
    }
    vol, comp = by_era["voluntary"], by_era["compulsory"]
    answerable = (vol["n"] >= MIN_FOR_COERCION and comp["n"] >= MIN_FOR_COERCION
                  and vol["r"] is not None and comp["r"] is not None)
    caveat = (
        "Before/after IS a cohort split: everything else moved over the same period, so a "
        "difference between the eras is confounded with the calendar and is NOT proof that the "
        "gate caused it. Read it as a signal to look harder, never as a finding.")
    if answerable:
        delta = comp["r"] - vol["r"]
        if delta < -0.15:
            verdict = (f"the compulsory size is WORSE ({comp['r']:+.2f} against "
                       f"{vol['r']:+.2f} freely given) - consistent with the coercion hazard, "
                       f"and the gate may be manufacturing the noise it exists to remove")
        elif delta > 0.15:
            verdict = (f"the compulsory size is BETTER ({comp['r']:+.2f} against "
                       f"{vol['r']:+.2f} freely given) - the hazard is not visible here")
        else:
            verdict = (f"the two eras are indistinguishable ({comp['r']:+.2f} against "
                       f"{vol['r']:+.2f}) - compulsion has not measurably degraded the estimate")
        answer = f"{verdict}. {caveat}"
    else:
        answer = (
            f"NOT ANSWERABLE from the evidence held: {vol['n']} rated unit(s) recorded freely "
            f"and {comp['n']} under compulsion, against a floor of {MIN_FOR_COERCION} each. The "
            f"data CANNOT separate the effect of the gate from the effect of the calendar, and "
            f"nothing here should be read as evidence either way - that is itself the result, "
            f"not a gap to be filled with an r off a handful of units. {caveat}")
    return {"by_era": by_era, "answered": answerable, "answer": answer, "caveat": caveat,
            "min_per_era": MIN_FOR_COERCION,
            "unknown_era": by_era["unknown"]["n"],
            "basis": "the Points AS RECORDED AT PLAN TIME, and the compulsion in force when the "
                     "plan read them. A size on the artefact today may have been revised after "
                     "the outcome, and a value revised with hindsight is not a prediction"}


ESTIMATOR_UNATTRIBUTED = "unattributed"
ERA_UNKNOWN = "unknown"


def _era_of(root, uid: str, stamped) -> str:
    """The compulsion a size was recorded under. The STAMP on the forecast record wins; the
    planner's declared cutoffs answer for evidence recorded before the stamp existed.

    Deferred and guarded, exactly like `_sample_of`: the gate's path must not pay for the
    planner's import graph, and a planner that cannot answer leaves the era UNKNOWN - which is
    reported as its own cohort, never quietly filed on one side of the split."""
    try:
        import sprint  # noqa: PLC0415
        era = getattr(sprint, "size_gate_era", None) or getattr(sprint, "effort_gate_era", None)
        if era:
            return era(root, uid, stamped)
    except Exception as exc:  # noqa: BLE001 - an unclassifiable unit is reported, never fatal
        sdlc_md.debug("retro._era_of", exc)
    return stamped if stamped in ("compulsory", "voluntary") else ERA_UNKNOWN


def estimator_report(root) -> dict:
    """Estimate vs actual, ACROSS SPRINTS, segmented per estimator and per model.

    Rates a unit on the POINTS THE PLAN RECORDED (`telemetry.forecasts`) against what the run
    actually cost (`telemetry.actuals`). That is the question the loop exists to answer and the
    only one worth asking: does this estimator's sense of how big a job is track what the job
    costs? Blind, on 21 delivered units, points scored r = +0.68 against measured cost where
    every computed metric managed +0.03 - so this is the axis that carries the signal, and it is
    the axis the report measures.

    Three states, and only the first is rated - the other two are named, counted, and excluded
    from every figure:

      rated        Points recorded at plan time, and a measured actual
      unsized      no Points were recorded at plan time. The artefact may carry a size now, but
                   there is no record of what it said when the plan was made, and a size read
                   back with hindsight is not an estimate
      unmeasured   no actual. Silence is not a measurement
    """
    forecasts = telemetry.forecasts(root)
    actuals = telemetry.actuals(root)

    units: list[dict] = []
    for uid, fc in forecasts.items():
        rec = actuals.get(uid, {})
        tokens = rec.get("tokens")
        points = fc.get("points")
        points = points if isinstance(points, int) and points > 0 else None
        u = {"id": uid, "type": rec.get("type"), "model": rec.get("model") or "unrecorded",
             "estimator": fc.get("estimator") or ESTIMATOR_UNATTRIBUTED,
             "points": points,
             "era": _era_of(root, uid, fc.get("size_gate") or fc.get("effort_gate")),
             "actual_tokens": tokens if isinstance(tokens, (int, float)) and tokens > 0 else None}
        if u["actual_tokens"] is None:
            u["state"] = "unmeasured"
        elif points is None:
            u["state"] = "unsized"
        else:
            u["state"] = "rated"
        units.append(u)
    units.sort(key=lambda u: u["id"])

    rated = [u for u in units if u["state"] == "rated"]
    models = sorted({u["model"] for u in rated})
    by_model = {
        model: {
            "n": len([u for u in rated if u["model"] == model]),
            "mean_actual": round(sum(u["actual_tokens"] for u in rated if u["model"] == model)
                                 / max(1, len([u for u in rated if u["model"] == model]))),
            "estimators": _estimator_segments([u for u in rated if u["model"] == model]),
        }
        for model in models
    }
    for seg in by_model.values():
        # Who to TRUST, named: the estimator whose calls track cost best within this model. It is
        # only a ranking, over the units each was given - and a ranking of ONE is not a ranking,
        # so with a single estimator there is nobody to prefer and the report says nothing.
        ranked = [(name, s["r"]) for name, s in seg["estimators"].items() if s["r"] is not None]
        seg["best_estimator"] = max(ranked, key=lambda p: p[1])[0] if len(ranked) > 1 else None

    refused = (f"REFUSED: the rated units were delivered by {len(models)} different models "
               f"({', '.join(models)}). One accuracy figure across two models describes neither, "
               f"so it is segmented per model and never pooled." if len(models) > 1 else None)
    pooled = None
    if len(models) == 1 and rated:
        pooled = _pearson([u["points"] for u in rated], [u["actual_tokens"] for u in rated])
    return {
        "units": units,
        "n_units": len(units),
        "n_rated": len(rated),
        "unsized": [u["id"] for u in units if u["state"] == "unsized"],
        "unmeasured": [u["id"] for u in units if u["state"] == "unmeasured"],
        "models": models,
        "by_model": by_model,
        "pooled": pooled,
        "refused": refused,
        "coercion": _coercion(rated),
        "basis": "the Points recorded at PLAN TIME against the measured actual. A unit the plan "
                 "did not size, and a unit nobody measured, are each named and excluded - "
                 "neither is coerced into a number",
    }


def _render_estimator(rep: dict) -> None:
    """The report an operator reads: whose judgement to weight, and what to correct."""
    print(f"estimator accuracy: {rep['n_rated']} of {rep['n_units']} unit(s) rated "
          f"(Points recorded at plan time, and a measured actual)")
    for tag, ids in (("unsized (no Points recorded when the plan was made - and a size read "
                      "off the artefact today is not a prediction)", rep["unsized"]),
                     ("unmeasured (no actual - silence is not a measurement)",
                      rep["unmeasured"])):
        if ids:
            print(f"  excluded, {tag}: {', '.join(ids)}")
    if rep["refused"]:
        print(f"\n  {rep['refused']}")
    for model, seg in sorted(rep["by_model"].items()):
        print(f"\n  model {model}: {seg['n']} rated unit(s), mean {seg['mean_actual']:,} tokens")
        for name, s in sorted(seg["estimators"].items()):
            r = f"r = {s['r']:+.2f}" if s["r"] is not None else "r = n/a (too few units, or " \
                                                                "every call the same size)"
            print(f"    {name}: {s['n']} unit(s), {r}, mean {s['mean_actual']:,} tokens")
            for b in s["bias"]:
                if b["direction"] in ("under-calls", "over-calls"):
                    print(f"      {b['direction']} {b['class']} by {b['ratio']}x "
                          f"({b['n']} unit(s): {', '.join(b['units'])})")
        if seg["best_estimator"]:
            print(f"    trust: {seg['best_estimator']} - their calls track cost best on this "
                  f"model. It ranks the estimators over the units each was given; it is not a "
                  f"licence to price a unit by their number")
    c = rep["coercion"]
    print("\n  coercion check (is a COMPULSORY size a CARELESS size?):")
    for era in ("voluntary", "compulsory", "unknown"):
        e = c["by_era"][era]
        r = f"r = {e['r']:+.2f}" if e["r"] is not None else "r = n/a"
        print(f"    {era:11} {e['n']} rated unit(s), {r}")
    print(f"    {c['answer']}")


def cmd_estimator(args) -> int:
    rep = estimator_report(args.root)
    if args.format == "json":
        print(json.dumps(rep, indent=2))
        return 0
    _render_estimator(rep)
    return 0


def cmd_accuracy(args) -> int:
    tokens = getattr(args, "tokens", None)
    capture_note = None
    # A delegated agent's own reported total, recorded against the open run BEFORE the capture
    # below reads it. The harness transcript never sees a subagent, so this is the only way a
    # fan-out sprint's delegated spend reaches the record at all - and it is a claim, so it is
    # recorded as `supplied` and published as part of a lower bound.
    delegated = getattr(args, "delegated_tokens", None)
    if delegated is not None:
        try:
            rec = run_state.record_delegated_tokens(
                args.root, delegated, agent=getattr(args, "delegated_agent", "") or "")
        except ValueError as exc:
            print(f"delegated total refused: {exc}", file=sys.stderr)
            return 1
        if rec is None:
            print("no run is open, so the delegated total was not recorded against one - "
                  "supply the sprint's whole figure with `--tokens N` instead")
        else:
            print(f"delegated total recorded (supplied, not measured): {rec['tokens']:,}"
                  + (f" for {rec['agent']}" if rec["agent"] else ""))
    # WHERE the figure below came from, decided where it is fetched rather than inferred later.
    # An explicit `--tokens N` is an operator's typed claim; the branches below overwrite this
    # with what they actually did.
    token_source = SOURCE_SUPPLIED if tokens is not None else None
    if tokens is None and getattr(args, "tokens_from_harness", False):
        # The close's path: capture the harness-tracked total itself. An actual already on
        # the sprint's row is NEVER re-stamped from a (possibly different) session - the
        # explicit --tokens above remains the operator's override for corrections.
        existing = next((r for r in velocity_history(args.root)
                         if r["id"] == args.id.upper().replace("-", "")
                         or r["id"] == args.id.upper()), None)
        if existing and existing.get("actual_tokens"):
            # Reused, not merely skipped: the upsert rewrites the whole row, so dropping the
            # figure here would erase the recorded actual while claiming to protect it.
            tokens = existing["actual_tokens"]
            # The figure is the one already on the row, so its provenance is too. Re-stamping
            # it from this path would relabel a harness capture as an operator's typed claim.
            token_source = SOURCE_UNCHANGED
            capture_note = (f"token actual already recorded for {args.id} "
                            f"({existing['actual_tokens']:,}) - reused, not re-captured; "
                            f"correct it with an explicit `--tokens N`")
        else:
            # THIS RUN's spend, not the session's. The meter is cumulative per session, so a
            # second sprint closed in one session would otherwise book the first sprint's
            # tokens too. No baseline, no number - never a session-wide fallback.
            cap = run_attributed_tokens(args.root, args.id)
            if cap["tokens"]:
                tokens = cap["tokens"]
                # Part meter read, part reported claim: the row must say so, or a figure half
                # of which nobody measured would be published under a machine read's provenance.
                token_source = (SOURCE_HARNESS_SUPPLIED if cap.get("delegated_tokens")
                                else SOURCE_HARNESS)
                capture_note = (f"token actual captured from the harness transcript: "
                                f"AT LEAST {tokens:,} ({cap['basis']}; {cap['source']})")
            else:
                capture_note = (f"token actual NOT ATTRIBUTABLE: {cap['reason']}. The sprint's "
                                f"token cost is left unrecorded rather than filled with a "
                                f"session-wide total; supply a real figure with "
                                f"`accuracy --tokens N` if you have one")
    res = accuracy(args.root, args.id, sprint_tokens=tokens,
                   elapsed_hours=getattr(args, "elapsed_hours", None))
    if token_source:
        res["token_source"] = token_source
    if capture_note:
        res["token_capture"] = capture_note
        if args.format != "json":
            print(capture_note)
    if not res["ok"]:
        print(f"retro {args.id}: {res['errors'][0]}", file=sys.stderr)
        return 1
    # THE BATCH CROSS-CHECK. Before ANY write: a Batch field that parses to a different count
    # than the retro's own `Delivered: N / M` header is refused, so neither the retro's accuracy
    # block nor a VELOCITY.md row is written and nothing already recorded is disturbed. This is
    # the range-in-the-Batch defect - the parser expands no ranges, so a partial denominator
    # would otherwise reach the file the planner re-measures its rate from.
    check = res.get("batch_check") or {}
    if check.get("ok") is False:
        print(_batch_mismatch_message(check, res["id"]), file=sys.stderr)
        return 1
    if args.write:
        write_accuracy(args.root, res)
        record_velocity(args.root, res)

    if args.format == "json":
        print(json.dumps(res, indent=2))
        return 0

    if not res["units"]:
        print(f"retro {res['id']}: no units named in '> **Batch:**' - nothing to measure")
        return 1
    for u in res["units"]:
        model = f"  model={u['model']}" if u.get("model") else ""
        if u["state"] == "measured":
            wall = f"{u['wall_time_s']}s" if u["wall_time_s"] is not None else "-"
            split = "  SHOULD HAVE BEEN SPLIT" if u["oversized"] else ""
            print(f"  [measured  ] {u['id']:8} pts={_fmt(u['points']):>3}  "
                  f"est={_fmt(u['estimate']):>9}  actual={_fmt(u['actual_tokens']):>9}  "
                  f"{u['ratio']}x  {_fmt(u['tokens_per_point']):>7}/pt  "
                  f"wall={wall}{model}{split}")
        elif u["state"] == "unmeasured":
            print(f"  [UNMEASURED] {u['id']:8} pts={_fmt(u['points']):>3}  "
                  f"est={_fmt(u['estimate']):>9}  actual=        -  ({u['reason']})")
        else:
            print(f"  [UNFORECAST] {u['id']:8} pts=  -  est=        -  "
                  f"actual={_fmt(u['actual_tokens']):>9}  ({u['reason']})")
    b = res["batch"]
    ratio = f"{b['ratio']}x" if b["ratio"] is not None else "n/a"
    print(f"\nbatch (rated units only): est={_fmt(b['estimate'])} actual="
          f"{_fmt(b['actual_tokens'])} -> {ratio}")
    for para in _points_lines(res):     # the velocity, the rate, and the decomposition answer
        print(para.replace("**", ""))
    if b.get("refused"):
        print(b["refused"])
        for model, seg in sorted((res.get("by_model") or {}).items()):
            r = f"{seg['ratio']}x" if seg["ratio"] is not None else "n/a"
            print(f"  {model:24} {seg['n']} unit(s)  est={_fmt(seg['estimate']):>9}  "
                  f"actual={_fmt(seg['actual_tokens']):>9}  {r}")
    elif res.get("models"):
        print(f"delivered by {', '.join(res['models'])}")
    print(f"{res['n_measured']} of {res['n_units']} unit(s) measured; "
          f"{res['n_forecast']} of {res['n_units']} forecast at plan time")
    if res["unmeasured"]:
        print(f"UNMEASURED: {', '.join(res['unmeasured'])}")
    if res["unforecast"]:
        print(f"UNFORECAST: {', '.join(res['unforecast'])} - no plan-time forecast was "
              f"recorded, and none is re-derived. They are excluded from both sides")
    print(f"forecast by {constants_cell(res.get('constants'))} - "
          f"{SAMPLE_NOTE.get(res.get('sample'), res.get('sample'))}")
    if res["n_measured"] == 0:
        print("no unit is rated - this sprint says nothing about accuracy")
    if args.write:
        print(f"recorded in {res['path']} and {velocity_path(args.root)}")
    else:
        print("--write records it in the retro and appends the sprint's row to VELOCITY.md")
    return 0


def _report_gaps(args) -> int:
    """`velocity --gaps`: the retros the record never recorded. Non-zero when there are any, so
    a gate or a close can branch on it rather than a human noticing a missing line."""
    rep = velocity_gaps(args.root, since=getattr(args, "since", None))
    if args.format == "json":
        print(json.dumps(rep, indent=2))
        return 1 if rep["gaps"] else 0
    window = f" since {rep['since']}" if rep["since"] else ""
    if not rep["gaps"]:
        print(f"velocity record: no gap{window} - all {rep['retros']} retro(s) in the window "
              f"carry a row in {VELOCITY_FILE}.")
        return 0
    print(f"velocity record: {len(rep['gaps'])} of {rep['retros']} retro(s){window} have NO row "
          f"in {VELOCITY_FILE}. Each is a close whose accuracy write did not run, so the "
          f"tokens-per-point rate the plans quote was never measured against it:")
    for g in rep["gaps"]:
        print(f"  {g['id']}  {g['date'] or '(no date recorded)'}")
    print("Record one with `retro.py accuracy --id RETROxxxx --write`. A sprint whose token "
          "cost cannot be recovered still gets a row: a blank Actual with the reason stated is "
          "a fact about that sprint, and no row at all is indistinguishable from an oversight.")
    return 1


def cmd_velocity(args) -> int:
    """The history the next plan reads: the points delivered per sprint, the tokens-per-point
    rate DERIVED from them, and how the forecast has actually performed."""
    rows = velocity_history(args.root)
    if getattr(args, "gaps", False):
        return _report_gaps(args)
    rate = measured_rate(args.root)
    if args.format == "json":
        print(json.dumps({"history": rows, "rate": rate}, indent=2))
        return 0
    if not rows:
        print(f"no velocity history yet ({VELOCITY_FILE}) - record one with "
              f"'retro.py accuracy --id RETROxxxx --write'")
        return 0
    for r in rows:
        ratio = f"{r['ratio']}x" if r["ratio"] is not None else "n/a"
        sample = _sample_of(r["id"], r.get("constants"))
        model = r.get("model") or MODEL_UNRECORDED
        pts = _fmt(r.get("points"))
        # The SAME rule the file's own Tokens/pt column obeys: a rate only where the tokens and
        # the points describe the same units. Dividing an absent Actual by the points printed
        # `0/pt` beside an `actual= -` on the same line.
        tpp = _fmt(_rate(r["actual_tokens"] or 0, r.get("points") or 0)
                   if _tokens_cover_points(r) else None)
        over = f"  ({r['oversized']} over {sdlc_md.POINTS_SPLIT_ABOVE}pt)" if r.get(
            "oversized") else ""
        print(f"  {r['id']}  {r['date']:12} {r['measured']}/{r['units']} measured  "
              f"pts={pts:>4}  est={_fmt(r['estimate']):>9} actual={_fmt(r['actual_tokens']):>9}  "
              f"{ratio:>6}  {tpp:>7}/pt  [{sample}]  {model}{over}")

    # THE RATE, DERIVED. Not a constant, not stored - a quotient of the two columns above,
    # recomputed on every read, so it cannot drift away from the evidence that produced it.
    print()
    if rate["refused"]:
        print(rate["refused"])
        for model, seg in sorted(rate["by_model"].items()):
            print(f"  {model:24} {seg['points']} point(s) over {seg['n']} sprint(s) -> "
                  f"{_fmt(seg['tokens_per_point'])} tokens/pt")
    elif rate["tokens_per_point"]:
        print(f"MEASURED RATE: {rate['tokens_per_point']:,} tokens per point "
              f"({rate['points']} points over {len(rate['sprints'])} sprint(s) on "
              f"{rate['model']}: {', '.join(rate['sprints'])}).")
        print("Derived from this history every time it is read - never stored and never fitted, "
              "so it is re-measured each sprint instead of decaying into a constant nobody "
              "dares touch.")
        if rate["oversized"]:
            print(f"CAVEAT: {rate['oversized']} unit(s) in that history were delivered above "
                  f"{sdlc_md.POINTS_SPLIT_ABOVE} points, and a point stops being a stable unit "
                  f"of cost up there. The rate is dragged downward by them - split those units "
                  f"and it will rise.")
    else:
        print("NO MEASURED RATE: no sprint has recorded the points it delivered, so there is "
              "nothing to divide the tokens by. Nothing is assumed in its place - a rate "
              "borrowed from another project is not a measurement of this one.")

    oos = [r for r in rows if _sample_of(r["id"], r.get("constants")) == "out-of-sample"
           and isinstance(r["ratio"], (int, float))]
    # PER MODEL, never pooled. A mean over a sprint delivered by a smaller model and one
    # delivered by a larger describes neither of them, and the moment a second model is used the
    # history would silently mix them into one meaningless figure. So the mean is quoted for each
    # model separately, and a mixed-model sprint (whose ratio was refused at record time) carries
    # no ratio to pool in the first place.
    by_model: dict[str, list[dict]] = {}
    for r in oos:
        by_model.setdefault(r.get("model") or MODEL_UNRECORDED, []).append(r)
    if oos:
        if len(by_model) > 1:
            print("\nOUT-OF-SAMPLE accuracy, SEGMENTED PER MODEL - it is never pooled, because a "
                  "mean across two models is a statement about neither:")
        for model, group in sorted(by_model.items()):
            mean = sum(r["ratio"] for r in group) / len(group)
            print(f"\n{len(group)} OUT-OF-SAMPLE sprint(s) on {model}, mean {mean:.2f}x "
                  f"(estimate / actual; above 1 the plan over-forecasts)")
    else:
        print("\nno out-of-sample sprint yet - nothing here is evidence that the estimator in "
              "force works")
    excluded = len(rows) - len(oos)
    if excluded:
        print(f"{excluded} row(s) excluded from that figure: a sprint whose actuals the "
              f"constants were fitted to is training error, a sprint forecast by a different "
              f"estimator judges that one, not this one, and a sprint that MIXED models records "
              f"no ratio at all")
    print("A trend, not a calibration. The forecast constants are changed by a human "
          "reading this, never automatically - a fit to a few sprints fits noise.")
    return 0


def cmd_collate(args) -> int:
    """The multi-project rate reader: the tokens-per-point rate per (project, model) cell, pooled
    across several project evidence directories and never summed across cells."""
    roots = args.roots or [args.root]
    rep = collate_rate(roots)
    if args.format == "json":
        print(json.dumps(rep, indent=2))
        return 0
    if not rep["cells"]:
        print("no rated units across those projects - a unit needs both a plan-time forecast "
              "with points and a measured actual")
        return 0
    if rep["refused"]:
        print(rep["refused"])
        print()
    for c in rep["cells"]:
        print(f"  {c['project']:20} {c['model']:20} {c['n']:>3} unit(s)  "
              f"{c['points']:>4} pt  {c['actual_tokens']:>10,} tok  -> "
              f"{_fmt(c['tokens_per_point'])}/pt")
    print("\nEach row is one (project, model) cell. No rate is pooled across cells - a figure "
          "spanning two projects or two models describes neither.")
    return 0


def cmd_validate(args) -> int:
    res = validate(args.root, args.id)
    if args.format == "json":
        print(json.dumps(res, indent=2))
    else:
        if res["ok"]:
            n_l, n_f = len(res["lessons"]), len(res["findings"])
            print(f"retro {res['id']}: ok - {n_l} lesson(s), {n_f} finding(s) all dispositioned "
                  f"({len(res['filed'])} filed, {len(res['declined'])} declined)")
        else:
            print(f"retro {res['id']}: FAIL")
            for e in res["errors"]:
                print(f"  - {e}")
    return 0 if res["ok"] else 1


def cmd_dispose(args) -> int:
    """Read-only: what has been decided, and what still needs deciding."""
    res = validate(args.root, args.id)
    if res["path"] is None:
        print(f"retro {args.id}: not found", file=sys.stderr)
        return 1
    rows = res["findings"]
    if args.format == "json":
        print(json.dumps({"id": res["id"], "findings": rows}, indent=2))
        return 0 if all(r["state"] != "undecided" for r in rows) else 1
    if not rows:
        print(f"retro {res['id']}: no findings recorded under '## Actions raised'")
        return 1
    for r in rows:
        mark = {"filed": "filed   ", "declined": "declined", "undecided": "UNDECIDED"}[r["state"]]
        extra = f" -> {r['detail']}" if r["detail"] else ""
        print(f"  [{mark}] {r['finding'][:64]}{extra}")
    left = sum(1 for r in rows if r["state"] == "undecided")
    print(f"\n{len(rows)} finding(s), {left} undecided")
    if left:
        print("file each with scripts/file_finding.py, or decline it with a reason "
              "('declined: <why>') - both are green, silence is not")
    return 1 if left else 0


def cmd_extract(args) -> int:
    """Lift the retro's lessons into the project store, so a lesson written in a retro
    reaches the digest the next sprint plan prints. Without this the retro is a diary.

    The lesson is TITLED from its first sentence and BODIED with its full text. Titling from the
    first physical line cut the headline wherever the author happened to wrap it, and those
    headlines are exactly what `sprint plan` prints as the lessons digest - a lesson whose
    headline stops mid-clause is one the next sprint skims past.

    Idempotent by content: a lesson already in the store is not added twice, so running
    extract on the same retro repeatedly converges rather than duplicating.
    """
    res = validate(args.root, args.id)
    if res["path"] is None:
        print(f"retro {args.id}: not found", file=sys.stderr)
        return 1
    found = res["lessons"]
    if not found:
        print(f"retro {args.id}: no lessons to extract")
        return 0

    log = lessons.default_project_file(args.root)
    existing_text = log.read_text(encoding="utf-8") if log.is_file() else lessons.PROJECT_HEADER
    existing = lessons.parse_project_lessons(existing_text)
    have = {e.get("title", "").strip().lower() for e in existing}

    added, skipped = [], []
    for text in found:
        title = lesson_title(text)
        if title.strip().lower() in have:
            skipped.append(title)
            continue
        added.append((title, text))

    if args.dry_run:
        for title, _text in added:
            print(f"  + would add: {title[:70]}")
        for t in skipped:
            print(f"  = already recorded: {t[:70]}")
        print(f"\n{len(added)} to add, {len(skipped)} already present")
        return 0

    log.parent.mkdir(parents=True, exist_ok=True)
    for title, text in added:
        # The body keeps the WHOLE lesson - the title is a headline, never a truncation of the
        # record. Only when the lesson is a single sentence are the two the same thing.
        body = (f"{text}\n\nRecorded from retro {res['id']}." if text != title
                else f"Recorded from retro {res['id']}.")
        rc = lessons.cmd_add(argparse.Namespace(
            title=title, body=body, root=args.root,
            tags="", origin=res["id"], epic=None, wave=None,
            validity_days=lessons.DEFAULT_VALIDITY_DAYS, global_=False,
            project_file=str(log), lessons_dir=None, format="text"))
        if rc != 0:
            print(f"failed to record: {title[:60]}", file=sys.stderr)
            return rc

    print(f"retro {res['id']}: {len(added)} lesson(s) extracted, {len(skipped)} already present")
    if added:
        print("regenerate the summary so the next sprint reads them: lessons.py summary")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=".")
    sub = ap.add_subparsers(dest="cmd", required=True)

    for name, fn, helptext in (
        ("validate", cmd_validate, "content check: sections, lessons, dispositions (the gate's leg)"),
        ("dispose", cmd_dispose, "report each finding and whether it is filed, declined or undecided"),
        ("extract", cmd_extract, "lift the retro's lessons into the project lessons log"),
        ("accuracy", cmd_accuracy, "estimate vs actual for the batch, in points and tokens: the "
                                   "plan's forecast against telemetry, and any unit that should "
                                   "have been split"),
        ("velocity", cmd_velocity, "points delivered per sprint, and the tokens-per-point rate "
                                   "derived from that history"),
        ("estimator", cmd_estimator, "measure the ESTIMATOR: per-estimator and per-model accuracy "
                                     "of the recorded Points, the classes each systematically "
                                     "under- or over-calls, and the coercion check"),
        ("collate", cmd_collate, "the tokens-per-point rate per (project, model) cell, pooled "
                                 "across several project evidence dirs and never summed across "
                                 "cells - the multi-project tuning read"),
    ):
        p = sub.add_parser(name, help=helptext)
        if name not in ("velocity", "estimator", "collate"):  # these span sprints, not one
            p.add_argument("--id", required=True, help="retro id, e.g. RETRO0022")
        if name == "collate":
            p.add_argument("--roots", nargs="+", metavar="DIR",
                           help="the project evidence roots to pool (default: --root). Each "
                                "record names its own project, so they may be separate dirs or "
                                "one pooled dir")
        p.add_argument("--format", choices=("text", "json"), default="text")
        if name == "velocity":
            p.add_argument("--gaps", action="store_true",
                           help="report every retro on disk with NO row in the velocity record "
                                "and exit non-zero, so a skipped accuracy write is visible "
                                "instead of looking like a sprint that never happened")
            p.add_argument("--since", metavar="RETROxxxx",
                           help="bound the gap report at a retro id, so adopting it creates no "
                                "tail of history nothing can clear")
        if name == "extract":
            p.add_argument("--dry-run", action="store_true")
        if name == "accuracy":
            p.add_argument("--write", action="store_true",
                           help="record the report in the retro and append the sprint's row "
                                "to the velocity history (default: read-only)")
            p.add_argument("--tokens", type=int, default=None, metavar="N",
                           help="the sprint's ACTUAL token spend (harness-tracked). Supply it for "
                                "an interactive sprint - which records no per-unit actual - to get "
                                "a real tokens-per-point over the delivered points")
            p.add_argument("--tokens-from-harness", dest="tokens_from_harness",
                           action="store_true",
                           help="capture the sprint's actual token spend from the harness's "
                                "current-session transcript instead of supplying --tokens by "
                                "hand. The close passes this; a re-read of an old retro must "
                                "not, because the current session is not that sprint. An "
                                "already-recorded actual is never overwritten (an explicit "
                                "--tokens still is the override), and a failed capture states "
                                "plainly why. Best-effort ATTRIBUTION: the most recently "
                                "modified transcript is taken as this session, so a close run "
                                "beside a concurrent session can capture the wrong one - the "
                                "recorded basis says exactly what was read")
            p.add_argument("--delegated-tokens", dest="delegated_tokens", type=int,
                           default=None, metavar="N",
                           help="one delegated agent's OWN reported token total, recorded "
                                "against the open run. The harness transcript carries no "
                                "subagent usage, so a fan-out sprint's delegated spend can only "
                                "be supplied - it is recorded as a claim, and the captured "
                                "figure is published as a lower bound on what the run cost. "
                                "Repeat the command once per agent")
            p.add_argument("--delegated-agent", dest="delegated_agent", default="",
                           metavar="NAME",
                           help="which agent reported the --delegated-tokens figure")
            p.add_argument("--elapsed-hours", dest="elapsed_hours", type=float, default=None,
                           metavar="H",
                           help="the sprint's real elapsed hours (start to close), for the PRIMARY "
                                "points-per-elapsed-hour velocity. Supply it for an interactive "
                                "sprint whose run-state has no clean elapsed; descriptive, never a "
                                "target")
        p.set_defaults(func=fn)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
