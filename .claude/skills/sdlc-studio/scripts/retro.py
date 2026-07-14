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
            against what telemetry measured, per unit and per batch. `--write` records it
            in the retro and appends the sprint's row to the velocity history.
  velocity  print the accumulated velocity history, so the next plan can see how the
            estimator has actually performed rather than trusting its constants.

The disposition rule. A finding is dispositioned when it is either filed as
an artefact (`CR0123` / `BG0045`) or DECLINED WITH A REASON. Declining is a first-class
answer and is equally green, so honesty costs exactly what noise costs and there is
nothing to game. What does not pass is silence: a finding written down and left to rot.

The measurement rule (the same rule, applied to numbers). A unit with no telemetry record
is reported UNMEASURED and is excluded from every ratio. It is never skipped and never
counted as accurate: a silent skip would let a batch of ten units with two measurements
report as a clean forecast. Silence is not a measurement, and the report says how many of
the batch it is actually speaking for.

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
from lib import sdlc_md  # noqa: E402
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


def find_retro(root, retro_id: str) -> Path | None:
    """The retro file for an id. One glob, shared, so the gate and this script cannot
    disagree about which file they are talking about."""
    d = Path(root) / RETRO_DIR
    if not d.is_dir():
        return None
    hits = sorted(p for p in d.glob(f"{retro_id}*.md") if p.is_file())
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


def _real_bullets(body: list[str]) -> list[str]:
    """Bullets with content in them. A `{{placeholder}}` bullet is the template talking,
    not the author, and counts as nothing."""
    found = []
    for line in body:
        m = BULLET_RE.match(line)
        if not m:
            continue
        text = m.group(1).strip()
        if not text or PLACEHOLDER_RE.search(text):
            continue
        # An HTML comment is template guidance, not an answer.
        text = re.sub(r"<!--.*?-->", "", text).strip()
        if text:
            found.append(text)
    return found


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

# The generated block inside `## Estimate vs actual`. Markers, not a whole-section
# rewrite: the section also carries the author's reading of the numbers, and a tool that
# ate the analysis every time it refreshed the table would teach people not to run it.
ACCURACY_BEGIN = "<!-- accuracy:begin (generated by retro.py accuracy --write) -->"
ACCURACY_END = "<!-- accuracy:end -->"
ACCURACY_SECTION = "Estimate vs actual"
ACCURACY_HEADING_RE = re.compile(r"(?im)^##\s+estimate\s+vs\.?\s+actual\b.*$")

VELOCITY_HEADER = """<!--
Generated by `retro.py accuracy --write`. One row per sprint retro: what the plan
forecast the batch would cost, and what it actually cost.

This is a RECORD, not a calibration. Nothing here re-fits the forecast constants
automatically - a fit to a handful of sprints would fit noise. A human reads the trend
and decides whether the constants have earned a change.

Read the coverage column first. A ratio computed over 2 measured units of 10 is a ratio
about 2 units, and the row says so.
-->
# Velocity history

| Retro | Date | Units | Measured | Estimate (tokens) | Actual (tokens) | Ratio (est/actual) | Wall (s) |
| --- | --- | --- | --- | --- | --- | --- | --- |
"""


def batch_ids(text: str) -> list[str]:
    """The unit ids named in the retro's `> **Batch:**` field, in order, de-duplicated.

    An unfilled `{{batch}}` yields nothing, which reads downstream as a batch with no
    units - correct, since a retro that never said what it delivered has nothing to measure.
    """
    m = BATCH_RE.search(text)
    if not m:
        return []
    line = PLACEHOLDER_RE.sub("", m.group(1))
    out: list[str] = []
    for hit in ARTEFACT_ID_RE.finditer(line):
        rid = sdlc_md.norm_id(hit.group(1))
        if rid.startswith("LL"):  # a lesson is not a unit of delivery
            continue
        if rid not in out:
            out.append(rid)
    return out


def estimate_tokens(root, unit_id: str) -> tuple[int | None, int | None, str]:
    """The plan's forecast for one unit: (estimate, complexity, note).

    The SAME model the plan used, imported from sprint rather than restated here - a second
    copy of the formula would let the report and the plan drift apart and neither would be
    wrong on its own terms. Import is deferred: `validate` is on the gate's path and must not
    pay for the planner's import graph.
    """
    hit = sdlc_md.find_by_id(root, unit_id)
    if hit is None:
        return None, None, "no artefact file"
    path, _type = hit
    try:
        import sprint  # noqa: PLC0415 - deferred: the gate's path must not import the planner
        cx = sprint._complexity_size(Path(root), path.read_text(encoding="utf-8"))
        return sprint.BASE_TOKEN_BUDGET + sprint.TOKENS_PER_COGNITIVE * cx, cx, ""
    except Exception as exc:  # noqa: BLE001 - an unestimable unit is reported, never fatal
        sdlc_md.debug("retro.estimate_tokens", exc)
        return None, None, "estimate unavailable"


def accuracy(root, retro_id: str) -> dict:
    """Estimate vs actual for every unit in the retro's batch.

    Per unit: the plan's forecast, the measured actual, and the ratio (estimate / actual, so
    >1 means the plan over-forecast). Per batch: the same, summed over the MEASURED units only.

    The batch ratio deliberately excludes unmeasured units from BOTH sides. Adding an
    unmeasured unit's estimate to the numerator with nothing in the denominator would inflate
    the apparent over-forecast; dropping it silently from both would hide that the batch was
    only partly measured. So it is excluded, counted, and named.
    """
    path = find_retro(root, retro_id)
    if path is None:
        return {"ok": False, "id": retro_id, "path": None, "units": [],
                "errors": [f"no retro file for {retro_id} in {RETRO_DIR}/"]}

    text = path.read_text(encoding="utf-8")
    measured_by_id = telemetry.actuals(root)

    units: list[dict] = []
    for uid in batch_ids(text):
        est, cx, note = estimate_tokens(root, uid)
        rec = measured_by_id.get(uid, {})
        tokens = rec.get("tokens")
        wall = rec.get("wall_time_s")
        u = {"id": uid, "type": rec.get("type"), "complexity": cx, "estimate": est,
             "actual_tokens": tokens, "wall_time_s": wall, "ratio": None,
             "state": "measured", "reason": ""}
        if not isinstance(tokens, (int, float)) or tokens <= 0:
            u["state"], u["reason"] = "unmeasured", "no telemetry token record"
        elif est is None:
            u["state"], u["reason"] = "unmeasured", note or "no estimate"
        else:
            u["ratio"] = round(est / tokens, 2)
        units.append(u)

    done = [u for u in units if u["state"] == "measured"]
    est_sum = sum(u["estimate"] for u in done)
    act_sum = sum(u["actual_tokens"] for u in done)
    walls = [u["wall_time_s"] for u in done if isinstance(u["wall_time_s"], (int, float))]
    return {
        "ok": True,
        "id": retro_id,
        "path": str(path),
        "date": (m.group(1).strip() if (m := DATE_RE.search(text)) else ""),
        "units": units,
        "n_units": len(units),
        "n_measured": len(done),
        "n_unmeasured": len(units) - len(done),
        "unmeasured": [u["id"] for u in units if u["state"] == "unmeasured"],
        "batch": {
            "estimate": est_sum,
            "actual_tokens": act_sum,
            "ratio": round(est_sum / act_sum, 2) if act_sum else None,
            "wall_time_s": sum(walls) if walls else None,
            "basis": "measured units only; unmeasured units are excluded from both sides",
        },
        "errors": [],
    }


def _fmt(n) -> str:
    return f"{n:,}" if isinstance(n, (int, float)) else "-"


def accuracy_block(res: dict) -> str:
    """The generated markdown the retro carries: the table, the coverage, and the caveat."""
    rows = ["| Unit | Complexity | Estimate | Actual | Ratio (est/actual) | Wall |",
            "| --- | --- | --- | --- | --- | --- |"]
    for u in res["units"]:
        if u["state"] == "measured":
            wall = f"{u['wall_time_s']}s" if u["wall_time_s"] is not None else "-"
            rows.append(f"| {u['id']} | {_fmt(u['complexity'])} | {_fmt(u['estimate'])} | "
                        f"{_fmt(u['actual_tokens'])} | {u['ratio']}x | {wall} |")
        else:
            rows.append(f"| {u['id']} | {_fmt(u['complexity'])} | {_fmt(u['estimate'])} | - | "
                        f"**UNMEASURED** ({u['reason']}) | - |")
    b = res["batch"]
    wall = f"{b['wall_time_s']}s" if b["wall_time_s"] is not None else "-"
    ratio = f"**{b['ratio']}x**" if b["ratio"] is not None else "-"
    rows.append(f"| **Batch (measured only)** | | **{_fmt(b['estimate'])}** | "
                f"**{_fmt(b['actual_tokens'])}** | {ratio} | **{wall}** |")

    n, m = res["n_units"], res["n_measured"]
    lines = [ACCURACY_BEGIN, "", *rows, "",
             f"**{m} of {n} unit(s) measured.**"]
    if res["unmeasured"]:
        lines.append(
            f"Unmeasured: {', '.join(res['unmeasured'])}. They are excluded from the batch "
            f"ratio - an unmeasured unit is not evidence that the estimate was right.")
    if m == 0:
        lines.append("No unit in this batch carries a telemetry record, so this sprint says "
                     "nothing about the estimator's accuracy.")
    lines += ["",
              "Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it "
              "under-forecast. The forecast is a HYPOTHESIS fitted to a small sample and is "
              "not re-fitted here - see VELOCITY.md for the trend across sprints, and change "
              "the constants only on evidence a human has looked at.",
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

def velocity_path(root) -> Path:
    return Path(root) / VELOCITY_FILE


def velocity_history(root) -> list[dict]:
    """The accumulated history, oldest first. The read a plan makes: how the estimator has
    performed on real sprints, next to the constants it is about to forecast with."""
    path = velocity_path(root)
    if not path.is_file():
        return []
    out: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = sdlc_md.table_cells(line)
        if not cells or len(cells) < 8:
            continue
        rid = cells[0].strip()
        if not re.fullmatch(r"RETRO\d{4}", rid, re.IGNORECASE):
            continue

        def _num(cell: str):
            raw = cell.replace(",", "").replace("*", "").rstrip("x").strip()
            try:
                return float(raw) if "." in raw else int(raw)
            except ValueError:
                return None

        out.append({"id": rid.upper(), "date": cells[1].strip(),
                    "units": _num(cells[2]), "measured": _num(cells[3]),
                    "estimate": _num(cells[4]), "actual_tokens": _num(cells[5]),
                    "ratio": _num(cells[6]), "wall_time_s": _num(cells[7])})
    return sorted(out, key=lambda r: r["id"])


def record_velocity(root, res: dict) -> Path:
    """Upsert this retro's row into the history. Keyed by retro id, so re-running a sprint's
    accuracy report corrects its row rather than double-counting the sprint."""
    b = res["batch"]
    row = {"id": res["id"].upper(), "date": res.get("date") or "", "units": res["n_units"],
           "measured": res["n_measured"], "estimate": b["estimate"],
           "actual_tokens": b["actual_tokens"], "ratio": b["ratio"],
           "wall_time_s": b["wall_time_s"]}
    rows = [r for r in velocity_history(root) if r["id"] != row["id"]] + [row]
    rows.sort(key=lambda r: r["id"])

    lines = [VELOCITY_HEADER.rstrip("\n")]
    for r in rows:
        ratio = f"{r['ratio']}x" if r["ratio"] is not None else "-"
        lines.append(f"| {r['id']} | {r['date']} | {_fmt(r['units'])} | {_fmt(r['measured'])} | "
                     f"{_fmt(r['estimate'])} | {_fmt(r['actual_tokens'])} | {ratio} | "
                     f"{_fmt(r['wall_time_s'])} |")
    path = velocity_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    sdlc_md.atomic_write(path, "\n".join(lines) + "\n")
    return path


def cmd_accuracy(args) -> int:
    res = accuracy(args.root, args.id)
    if not res["ok"]:
        print(f"retro {args.id}: {res['errors'][0]}", file=sys.stderr)
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
        if u["state"] == "measured":
            wall = f"{u['wall_time_s']}s" if u["wall_time_s"] is not None else "-"
            print(f"  [measured  ] {u['id']:8} cx={_fmt(u['complexity']):>4}  "
                  f"est={_fmt(u['estimate']):>9}  actual={_fmt(u['actual_tokens']):>9}  "
                  f"{u['ratio']}x  wall={wall}")
        else:
            print(f"  [UNMEASURED] {u['id']:8} cx={_fmt(u['complexity']):>4}  "
                  f"est={_fmt(u['estimate']):>9}  actual=        -  ({u['reason']})")
    b = res["batch"]
    ratio = f"{b['ratio']}x" if b["ratio"] is not None else "n/a"
    print(f"\nbatch (measured only): est={_fmt(b['estimate'])} actual="
          f"{_fmt(b['actual_tokens'])} -> {ratio}")
    print(f"{res['n_measured']} of {res['n_units']} unit(s) measured", end="")
    print(f"; UNMEASURED: {', '.join(res['unmeasured'])}" if res["unmeasured"] else "")
    if res["n_measured"] == 0:
        print("no unit carries a telemetry record - this sprint says nothing about accuracy")
    if args.write:
        print(f"recorded in {res['path']} and {velocity_path(args.root)}")
    else:
        print("--write records it in the retro and appends the sprint's row to VELOCITY.md")
    return 0


def cmd_velocity(args) -> int:
    """The history the next plan reads: how the forecast has actually performed."""
    rows = velocity_history(args.root)
    if args.format == "json":
        print(json.dumps(rows, indent=2))
        return 0
    if not rows:
        print(f"no velocity history yet ({VELOCITY_FILE}) - record one with "
              f"'retro.py accuracy --id RETROxxxx --write'")
        return 0
    for r in rows:
        ratio = f"{r['ratio']}x" if r["ratio"] is not None else "n/a"
        print(f"  {r['id']}  {r['date']:12} {r['measured']}/{r['units']} measured  "
              f"est={_fmt(r['estimate']):>9} actual={_fmt(r['actual_tokens']):>9}  {ratio}")
    rated = [r for r in rows if isinstance(r["ratio"], (int, float))]
    if rated:
        mean = sum(r["ratio"] for r in rated) / len(rated)
        print(f"\n{len(rated)} sprint(s) with a ratio, mean {mean:.2f}x "
              f"(estimate / actual; above 1 the plan over-forecasts)")
    print("A trend, not a calibration. The forecast constants are changed by a human "
          "reading this, never automatically - a fit to a few sprints fits noise.")
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
        if text.strip().lower() in have:
            skipped.append(text)
            continue
        added.append(text)

    if args.dry_run:
        for t in added:
            print(f"  + would add: {t[:70]}")
        for t in skipped:
            print(f"  = already recorded: {t[:70]}")
        print(f"\n{len(added)} to add, {len(skipped)} already present")
        return 0

    log.parent.mkdir(parents=True, exist_ok=True)
    for text in added:
        rc = lessons.cmd_add(argparse.Namespace(
            title=text, body=f"Recorded from retro {res['id']}.", root=args.root,
            tags="", origin=res["id"], epic=None, wave=None,
            validity_days=lessons.DEFAULT_VALIDITY_DAYS, global_=False,
            project_file=str(log), lessons_dir=None, format="text"))
        if rc != 0:
            print(f"failed to record: {text[:60]}", file=sys.stderr)
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
        ("accuracy", cmd_accuracy, "estimate vs actual for the batch: plan forecast against telemetry"),
        ("velocity", cmd_velocity, "print the accumulated estimate-vs-actual history across retros"),
    ):
        p = sub.add_parser(name, help=helptext)
        if name != "velocity":  # the history spans sprints; it is not about one retro
            p.add_argument("--id", required=True, help="retro id, e.g. RETRO0022")
        p.add_argument("--format", choices=("text", "json"), default="text")
        if name == "extract":
            p.add_argument("--dry-run", action="store_true")
        if name == "accuracy":
            p.add_argument("--write", action="store_true",
                           help="record the report in the retro and append the sprint's row "
                                "to the velocity history (default: read-only)")
        p.set_defaults(func=fn)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
