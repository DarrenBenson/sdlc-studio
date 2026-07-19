#!/usr/bin/env python3
"""The handoff guide - the remaining-work artefact an agentic run owes a human at its close.

A run that stops (goal reached, budget spent, or blocked) leaves its tail scattered across
hints, the decisions log and the retro, so the person who picks it up has no single "here
is where you start" document. `generate` writes one, and it is a JOIN over evidence that
already exists rather than new instrumentation:

  quarantined units + failure signatures  <- .local/loop-state.json  (loop_guard)
  failing / unproven ACs                  <- .local/verify-report.json (verify_ac)
  per-unit readiness issues               <- audit.audit_unit
  the lifecycle stage a unit stalled at   <- conformance.detect_conformance
  the approved batch and the run's shape  <- .local/run-state.json, .local/sprint-plan.json
  difficulty band (the suitability seed)  <- route.estimate

Two properties are load-bearing:

* **Nothing is omitted.** Every unit that is not terminal is named, with at least one
  pointer (an AC, a check, a blocker, or - always available - its own file). A batch id
  with no file on disk is reported as remaining-and-missing, never dropped; a unit the loop
  quarantined is reported even if it was never in the approved batch. A handoff that
  silently loses an item is worse than no handoff.
* **The tail is machine-readable.** `generate` emits a worklist file, so the next
  `sprint plan --worklist <file>` reads the remaining work back as a batch. No fourth batch
  source; the documented one is reused.

The suitability tag (copilot-tail vs judgement) is seeded deterministically from the
difficulty band, the quarantine reason, the stage the unit stalled at, and the tranche
audit's issues (see the JUDGEMENT_* constants). It is a seed, not a verdict: the closing
model refines it, and every tag carries the reasons it was derived from, so it can be
argued with rather than merely believed.

Subcommands:
  generate   Build the handoff, create it via the artifact machinery, emit the worklist.
  show       Print the join (JSON) without creating anything.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import run_state, sdlc_md  # noqa: E402
import artifact  # noqa: E402  (the meta-artifact creator: id + index row)
import audit  # noqa: E402  (per-unit readiness issues)
import conformance  # noqa: E402  (the stage a unit stalled at)
import critic  # noqa: E402  (delivery evidence: the recorded verdict)
import decisions  # noqa: E402  (the project decisions log)
import loop_guard  # noqa: E402  (quarantine verdicts + failure signatures)
import route  # noqa: E402  (the difficulty band that seeds the suitability tag)

TYPE = "handoff"
WORKLIST_REL = Path("sdlc-studio") / ".local" / "handoff-worklist.txt"


def _heading_title(title: str) -> str:
    """A single-line title for the handoff H1, composed from prose (often the Sprint Goal
    sentence, which ends in a full stop). Trailing punctuation is stripped so the generated
    heading passes markdownlint MD026 in any project that lints its workspace - the same class
    of fix the seeded AC headings carry."""
    return " ".join(str(title).split()).rstrip(" .,;:!?…")

COPILOT_TAIL = "copilot-tail"
JUDGEMENT = "judgement"
TAGS = (COPILOT_TAIL, JUDGEMENT)

# The deterministic seed for the tag. Each constant answers one question: does finishing
# this unit require a DECISION, or only the work? Anything that says a decision is owed
# lands in `judgement`; everything else is the copilot tail. A quarantine of either kind
# (the cap, or a repeated failure signature) is judgement on its own - a unit the loop
# could not turn green is not a typing tail. The estimator's own doctrine is mirrored
# here: unknown difficulty is never treated as minimal, so an item that resolved no signal
# at all reads `judgement`, never a confidently-wrong `copilot-tail`.
JUDGEMENT_BANDS = ("high", "extreme")     # the estimator already says this is not a tail
JUDGEMENT_STAGES = ("specified", "critiqued")   # no AC = a spec decision; review = not self-completable
JUDGEMENT_ISSUES = ("weak-AC", "unmet-deps", "unresolved-deps", "cross-epic-ac",
                    "already-satisfied", "link-integrity", "not-found")

# The statuses that ASSERT the work was done. Terminal is not the same as delivered, and
# the difference is the whole point of the document: `Won't Implement`, `Won't Fix`,
# `Rejected`, `Withdrawn` and `Superseded` are all terminal and none of them is a delivery.
# This is deliberately NOT `audit.MET` - that is a DEPENDENCY-SATISFACTION set (a superseded
# dependency is satisfied; a superseded unit was not delivered), and borrowing it here
# printed a success the run never achieved.
DELIVERED_STATUSES = frozenset({"Done", "Complete", "Fixed", "Verified", "Accepted", "Closed"})


# --------------------------------------------------------------------------- inputs
def _loop_state(root: Path) -> dict:
    return sdlc_md.read_json(root / "sdlc-studio" / ".local" / "loop-state.json", {"units": {}})


def _verify_report(root: Path) -> dict:
    return sdlc_md.read_json(root / "sdlc-studio" / ".local" / "verify-report.json", {})


def _verify_entry(report: dict, rid: str) -> dict | None:
    """The verify-report entry for a unit. The report keys on the story STEM
    (`US0002-story-2`), not the id, so match on the leading record id."""
    stories = report.get("stories")
    if not isinstance(stories, dict):
        return None
    want = sdlc_md.norm_id(rid)
    for stem, entry in stories.items():
        rec = sdlc_md.extract_record_id(stem)
        if rec and sdlc_md.norm_id(rec) == want and isinstance(entry, dict):
            return entry
    return None


def _sprint_plan_batch(root: Path) -> list[str]:
    data = sdlc_md.read_json(root / "sdlc-studio" / ".local" / "sprint-plan.json", {})
    batch = data.get("batch") if isinstance(data, dict) else None
    return [u["id"] for u in batch if isinstance(u, dict) and u.get("id")] \
        if isinstance(batch, list) else []


def _batch_source(root: Path, batch: list[str] | None) -> tuple[list[str], str]:
    """The units this run was approved to do, and where that came from. Explicit ids win,
    then the run state, then the persisted sprint plan. With no source at all the caller
    gets a refusal, not an empty handoff - a document reporting nothing remaining, having
    examined nothing, is the false-assurance class."""
    if batch:
        return [str(b) for b in batch], "argument"
    state = run_state.read(root)
    if state.get("batch"):
        return list(state["batch"]), "run-state.json"
    planned = _sprint_plan_batch(root)
    if planned:
        return planned, "sprint-plan.json"
    raise ValueError(
        "no batch to hand over: pass --id/--ids, or open the run with "
        "`sprint plan --write` (which records the approved batch in "
        f"{run_state.REL}) - a handoff over no batch would report a clean close it "
        "never checked")


# --------------------------------------------------------------------------- the join
def _stalled_stages(root: Path) -> dict[str, list[str]]:
    """{normalised story id: the lifecycle stages it has not reached}. Story-scoped, like
    conformance itself; a bug/CR simply contributes no stage pointer."""
    try:
        report = conformance.detect_conformance(root)
    except Exception as exc:  # noqa: BLE001 - a handoff must still be written when a lane errors
        sdlc_md.debug("handoff._stalled_stages", exc)
        return {}
    return {sdlc_md.norm_id(u["id"]): list(u.get("missing") or [])
            for u in report.get("units", []) if u.get("missing")}


def _quarantine(state: dict, rid: str) -> dict | None:
    """The loop's verdict on a unit, or None when the loop never recorded an attempt.

    Reuses `loop_guard.verdict` so the handoff and the loop agree on what quarantined
    means, instead of re-deriving the rule from the raw counters. The guardrail thresholds
    are CLI flags and loop-state does not record which ones the run used, so this reads at
    the documented defaults - which is why the ATTEMPTS themselves are reported as a
    pointer regardless of whether they tripped a threshold (see `_pointers`): the signature
    is what the next person needs, and it cannot be withheld pending a verdict this file
    cannot fully reconstruct."""
    units = state.get("units") or {}
    key = next((k for k in units if sdlc_md.norm_id(k) == sdlc_md.norm_id(rid)), None)
    if key is None:
        return None
    v = loop_guard.verdict(state, key)
    v["signatures"] = list(units[key].get("signatures") or [])
    return v


def _unproven(entry: dict | None) -> str | None:
    """Why a unit's DECLARED delivery is not backed by its evidence, or None when nothing
    contradicts it.

    A story goes Done green and the code later regresses; its `Status: Done` does not
    change, because the verify report is a snapshot and nothing rewrites the file. Reading
    the status alone therefore prints a green row for a unit whose ACs are currently red -
    and drops its failing verifier out of the document and the worklist entirely, which is
    exactly the work the person picking up needs. `stale` counts the same way: an AC
    verified against code that has since changed is not a passing AC, it is an unrepeated
    one. A unit the run cannot prove it delivered is remaining work."""
    if not entry:
        return None            # no report entry at all is not evidence of failure
    failed, stale = int(entry.get("failed") or 0), int(entry.get("stale") or 0)
    if not failed and not stale:
        return None
    parts = []
    if failed:
        parts.append(f"{failed} red AC(s)")
    if stale:
        parts.append(f"{stale} stale AC(s) (verified against code that has since changed)")
    return "; ".join(parts)


def _delivery_evidence(root: Path, rid: str, report: dict) -> list[str]:
    """What is on record about this unit's delivery: its verified ACs and its critic
    verdict. Only what is actually recorded - an absent verdict is left unsaid, never
    asserted - and a red or stale count is never omitted from the count line, which is how
    a story with 2 stale ACs came to read a flat "2/2 AC(s) verified"."""
    out: list[str] = []
    entry = _verify_entry(report, rid)
    if entry:
        line = f"{entry.get('verified', 0)}/{entry.get('ac_count', 0)} AC(s) verified"
        if entry.get("manual"):
            line += f", {entry['manual']} manual"
        if entry.get("failed"):
            line += f", {entry['failed']} RED"
        if entry.get("stale"):
            line += f", {entry['stale']} STALE"
        out.append(line)
    verdict = critic.verdict_for(root, rid)
    if verdict:
        who = verdict.get("reviewer") or "unrecorded reviewer"
        out.append(f"critic {verdict.get('verdict')} ({who})")
    return out


def _pointers(root: Path, path: Path | None, text: str, unit_audit: dict,
              stages: list[str], quarantine: dict | None, verify: dict | None,
              unproven: str | None = None) -> list[dict]:
    """Every pointer that resolves for one remaining unit: the contradiction between its
    status and its evidence, the failing AC, the check it stalled at, the blocker that
    stopped it, and the files it declared it would touch. The unit's own file is always the
    last resort, so no item is ever listed without a pointer."""
    out: list[dict] = []
    if unproven:
        out.append({"kind": "check", "ref": "verify:unproven",
                    "detail": f"the file says delivered; the evidence says {unproven} "
                              f"- reconcile the two (re-run verify_ac, fix, or reopen)"})
    if verify:
        for f in (verify.get("failures") or []):
            kind = f.get("kind") or "failed"
            out.append({"kind": "ac", "ref": f.get("ac") or "?",
                        "detail": f"{f.get('verifier') or 'no verifier'} ({kind})"})
        if verify.get("stale"):
            out.append({"kind": "ac", "ref": "stale",
                        "detail": f"{verify['stale']} AC(s) verified against changed code "
                                  f"- re-run verify_ac"})
    for stage in stages:
        out.append({"kind": "check", "ref": f"conformance:{stage}",
                    "detail": "lifecycle stage not reached"})
    if quarantine and quarantine.get("attempts"):
        # EVERY recorded attempt is reported, not only a quarantining one: a unit the loop
        # tried and failed once has a failure signature the next person needs, and hiding it
        # until a threshold trips would lose exactly the pointer they came for.
        sigs = quarantine.get("signatures") or []
        ref = (f"quarantine:{quarantine['reason']}" if quarantine.get("quarantine")
               else "failed-attempts")
        out.append({"kind": "blocker", "ref": ref,
                    "detail": f"{quarantine['attempts']} failed attempt(s); "
                              f"signature(s): {', '.join(sigs) or 'none recorded'}"})
    for issue in unit_audit.get("issues", []):
        if issue == "already-terminal":  # a delivered unit is not remaining work
            continue
        out.append({"kind": "issue", "ref": issue, "detail": "tranche audit"})
    for f in sdlc_md.affects_files(text):
        out.append({"kind": "file", "ref": f, "detail": "declared Affects"})
    if path is not None:
        out.append({"kind": "file", "ref": _rel(root, path), "detail": "the unit itself"})
    return out


def _suitability(band: str | None, confidence: str, stages: list[str], issues: list[str],
                 quarantine: dict | None, found: bool, unproven: str | None = None) -> dict:
    """copilot-tail vs judgement, from the deterministic seeds - with the reasons that
    produced it, so the closing model can refine the tag instead of guessing at it."""
    reasons: list[str] = []
    judgement = False
    if not found:
        return {"tag": JUDGEMENT, "reasons": ["not-found"], "confidence": "low"}
    if unproven:
        # the unit's recorded status contradicts its own evidence: whether to fix it
        # forward or reopen it is a decision, and a decision is not a copilot tail
        reasons.append("verify:unproven")
        judgement = True
    if band:
        reasons.append(f"difficulty:{band}")
        judgement |= band in JUDGEMENT_BANDS
    if quarantine and quarantine.get("quarantine"):
        reasons.append(f"quarantine:{quarantine['reason']}")
        judgement = True
    for stage in stages:
        if stage in JUDGEMENT_STAGES:
            reasons.append(f"stage:{stage}")
            judgement = True
    for issue in issues:
        head = issue.split(":")[0].strip()
        if head in JUDGEMENT_ISSUES:
            reasons.append(f"issue:{head}")
            judgement = True
    if not reasons:  # nothing resolved: say so rather than certifying a tail on no evidence
        return {"tag": JUDGEMENT, "reasons": ["no-signal"], "confidence": "low"}
    return {"tag": JUDGEMENT if judgement else COPILOT_TAIL, "reasons": reasons,
            "confidence": confidence}


def _rel(root: Path, path: Path) -> str:
    try:
        return str(Path(path).relative_to(root))
    except ValueError:
        return str(path)


def _estimate(root: Path, path: Path) -> tuple[str | None, str]:
    """(difficulty band, confidence) for a unit, degrading to (None, 'low') when the
    estimator cannot read it - never to a band it did not compute."""
    try:
        est = route.estimate(root, path)
        return est["difficulty_band"], est["confidence"]
    except Exception as exc:  # noqa: BLE001 - the tag degrades; the handoff is still written
        sdlc_md.debug("handoff._estimate", exc)
        return None, "low"


def _unit(root: Path, rid: str, ctx: dict) -> dict:
    """One unit's row in the join: delivered or remaining, with its evidence or its
    pointers. A unit with no file on disk is a REMAINING item whose first problem is that
    nobody can find it."""
    found = sdlc_md.find_by_id(root, rid)
    if found is None:
        return {"id": sdlc_md.norm_id(rid), "type": None, "status": "missing", "path": None,
                "delivered": False, "dropped": False, "terminal": False,
                "pointers": [{"kind": "issue", "ref": "not-found",
                              "detail": f"no artefact file for {rid} - it was in the batch "
                                        f"and is not on disk"}],
                "suitability": _suitability(None, "low", [], [], None, found=False)}
    path, type_ = found
    text = path.read_text(encoding="utf-8")
    status = sdlc_md.canonical_status(sdlc_md.extract_field(text, "Status"),
                                      sdlc_md.status_vocab(type_, root)) or "Unknown"
    rec = sdlc_md.extract_record_id(path.stem) or rid
    verify = _verify_entry(ctx["verify"], rec)
    terminal = status in sdlc_md.terminal_statuses(type_)
    if terminal and status not in DELIVERED_STATUSES:
        # Closed, but not delivered (Won't Implement / Rejected / Withdrawn / Superseded).
        # Not remaining work, and not a success either - it gets its own bucket rather than
        # a row under "Delivered" claiming an outcome the run never reached.
        return {"id": rec, "type": type_, "status": status, "path": _rel(root, path),
                "delivered": False, "dropped": True, "terminal": True,
                "evidence": _delivery_evidence(root, rec, ctx["verify"])}
    unproven = _unproven(verify) if terminal else None
    if terminal and not unproven:
        return {"id": rec, "type": type_, "status": status, "path": _rel(root, path),
                "delivered": True, "dropped": False, "terminal": True,
                "evidence": _delivery_evidence(root, rec, ctx["verify"])}
    # ...everything else is REMAINING - including a unit whose status says Done while its
    # evidence says otherwise. Its failing verifier is the pointer the next person needs.
    try:
        unit_audit = audit.audit_unit(root, rec)
    except Exception as exc:  # noqa: BLE001 - a failing readiness lane must not lose the item
        sdlc_md.debug("handoff.audit_unit", exc)
        unit_audit = {"issues": []}
    stages = ctx["stages"].get(sdlc_md.norm_id(rec), [])
    quarantine = _quarantine(ctx["loop"], rec)
    band, confidence = _estimate(root, path)
    return {
        "id": rec, "type": type_, "status": status, "path": _rel(root, path),
        "delivered": False, "dropped": False, "terminal": False, "unproven": unproven,
        "pointers": _pointers(root, path, text, unit_audit, stages, quarantine, verify,
                              unproven),
        "suitability": _suitability(band, confidence, stages, unit_audit.get("issues", []),
                                    quarantine, found=True, unproven=unproven),
    }


def _open_decisions(root: Path, ids: list[str]) -> list[dict]:
    """The decisions still owed. Two deterministic sources: an `Open` row in a batch
    artefact's Open Decisions table (the RFC shape), and any project decision the log marks
    `revisited` (settled once, re-opened since)."""
    out: list[dict] = []
    for rid in ids:
        found = sdlc_md.find_by_id(root, rid)
        if found is None:
            continue
        path, _type = found
        text = path.read_text(encoding="utf-8")
        if "## Open Decisions" not in text:
            continue
        block = text.split("## Open Decisions", 1)[1].split("\n## ", 1)[0]
        for _ln, cells in _rows(block):
            if len(cells) >= 3 and cells[-1].strip().lower() == "open":
                out.append({"source": sdlc_md.extract_record_id(path.stem) or path.stem,
                            "ref": cells[0].strip(), "decision": cells[1].strip(),
                            "path": _rel(root, path)})
    try:
        for d in decisions.list_decisions(root, status="revisited"):
            out.append({"source": "decisions.md", "ref": d["id"], "decision": d["decision"],
                        "path": decisions.LOG_REL})
    except Exception as exc:  # noqa: BLE001 - an unreadable log must not lose the rest
        sdlc_md.debug("handoff._open_decisions", exc)
    return out


def _rows(block: str):
    for tbl in sdlc_md.iter_tables(block):
        yield from tbl["rows"]


def _appetite(root: Path, state: dict, ids: list[str], delivered: int) -> dict | None:
    """The run's appetite line for the close: declared vs spent vs delivered, plus the token
    forecast. None when no appetite was declared and no forecast was recorded - a run opened
    without the breaker owes no appetite report. `spent` is measured, not self-reported:
    wall-clock from the run's `started_at`, units from those now terminal (loop_guard). Token
    is a FORECAST (recorded at plan time), labelled so and never a spend or a gate."""
    appetite = state.get("appetite")
    forecast = state.get("token_forecast")
    if not appetite and forecast is None:
        return None
    appetite = appetite or {}
    return {
        "declared": {"minutes": appetite.get("minutes") or 0,
                     "units": appetite.get("units") or 0},
        "spent": {"minutes": round(loop_guard.elapsed_minutes(state.get("started_at")), 1),
                  "units": loop_guard.units_consumed(root, ids)},
        "delivered": delivered,
        "token_forecast": forecast,
    }


def build(repo_root: Path | str, batch: list[str] | None = None,
          outcome: str | None = None) -> dict:
    """The JOIN: what was delivered, what remains, and what decisions are still owed.

    Read-only. Raises ValueError when there is no batch to hand over."""
    root = Path(repo_root)
    ids, source = _batch_source(root, batch)
    loop = _loop_state(root)
    ctx = {"loop": loop, "verify": _verify_report(root), "stages": _stalled_stages(root)}
    seen = {sdlc_md.norm_id(i) for i in ids}
    # a unit the loop quarantined is remaining work even when it was never in the approved
    # batch (an escalation pulled it in, or the batch was re-cut mid-run) - never dropped
    extra = sorted(u for u in (loop.get("units") or {})
                   if sdlc_md.norm_id(u) not in seen)
    units = [_unit(root, i, ctx) for i in ids] + [_unit(root, u, ctx) for u in extra]
    delivered = [u for u in units if u["delivered"]]
    dropped = [u for u in units if u["dropped"]]
    remaining = [u for u in units if not u["terminal"]]
    state = run_state.read(root)
    tags = {t: sum(1 for u in remaining if u["suitability"]["tag"] == t) for t in TAGS}
    return {
        "generated_at": sdlc_md.now_iso8601(),
        "run": state or None,
        "outcome": outcome or state.get("outcome") or None,
        "batch_source": source,
        "batch": [sdlc_md.norm_id(i) for i in ids],
        "delivered": delivered,
        "dropped": dropped,
        "remaining": remaining,
        "open_decisions": _open_decisions(root, ids),
        "appetite": _appetite(root, state, ids, len(delivered)),
        "summary": {"total": len(units), "delivered": len(delivered),
                    "dropped": len(dropped), "remaining": len(remaining), **tags},
        "worklist": str(WORKLIST_REL),
    }


# --------------------------------------------------------------------------- render
def _plannable(report: dict) -> list[str]:
    """The remaining ids `sprint plan --worklist` can actually resolve. A missing unit is
    NOT written - the planner refuses a worklist id with no file, and a worklist that
    aborts the next plan helps nobody. It stays named in the document, which is the durable
    record."""
    return [u["id"] for u in report["remaining"] if u["path"]]


def _worklist_text(report: dict, disp: str) -> str:
    lines = [f"# {disp}: the remaining work from the last run "
             f"({report['summary']['remaining']} item(s))",
             "# plan it: sprint.py plan --worklist sdlc-studio/.local/handoff-worklist.txt"]
    missing = [u["id"] for u in report["remaining"] if not u["path"]]
    if missing:
        lines.append(f"# not planned (no artefact file on disk): {', '.join(missing)}")
    lines += _plannable(report)
    return "\n".join(lines) + "\n"


def _unit_table(units: list[dict], empty: str) -> str:
    if not units:
        return f"{empty}\n"
    rows = ["| Unit | Type | Status | Evidence |", "| --- | --- | --- | --- |"]
    for u in units:
        link = f"[{u['id']}](../../{u['path']})" if u["path"] else u["id"]
        evidence = "; ".join(u.get("evidence") or []) or "no verifier or verdict on record"
        rows.append(sdlc_md.join_row([link, u["type"] or "?", u["status"], evidence]))
    return "\n".join(rows) + "\n"


def _remaining_body(report: dict) -> str:
    if not report["remaining"]:
        return "_Nothing remains: every unit in the batch reached a terminal status._\n"
    out: list[str] = []
    for u in report["remaining"]:
        s = u["suitability"]
        head = f"### {u['id']} ({u['type'] or 'unknown type'}, {u['status']}) - {s['tag']}"
        out.append(head)
        out.append("")
        for p in u["pointers"]:
            detail = f" - {p['detail']}" if p.get("detail") else ""
            out.append(f"- **{p['kind']}:** `{p['ref']}`{detail}")
        out.append(f"- **Suitability:** {s['tag']} (confidence {s['confidence']}) "
                   f"- seeded by {', '.join(s['reasons'])}")
        out.append("")
    return "\n".join(out)


def _decisions_body(report: dict) -> str:
    if not report["open_decisions"]:
        return ("_None recorded._ Rulings made during the run live in the tranche ledger "
                "(`sdlc-studio/decisions/`); settled decisions belong in "
                "`sdlc-studio/decisions.md`.\n")
    out = ["| Ref | Decision | Where |", "| --- | --- | --- |"]
    for d in report["open_decisions"]:
        out.append(sdlc_md.join_row([d["ref"], d["decision"],
                                     f"{d['source']} (`{d['path']}`)"]))
    return "\n".join(out) + "\n"


def _pickup_body(report: dict) -> str:
    s = report["summary"]
    if not report["remaining"]:
        return ("Every unit in the batch is terminal. There is no tail: close the run and "
                "plan the next batch normally.\n")
    lines = [
        f"{s['remaining']} of {s['total']} unit(s) remain "
        f"({s[COPILOT_TAIL]} suit copilot-assisted completion, {s[JUDGEMENT]} need human "
        f"judgement). Plan them straight back in:",
        "",
        "```bash",
        'python3 "$CLAUDE_SKILL_DIR/scripts/sprint.py" plan \\',
        f"  --worklist {report['worklist']} --order wsjf",
        "```",
        "",
        "Each item below names the pointer to start from: the failing AC, the check it "
        "stalled at, the blocker that stopped it, or the file it was to touch.",
    ]
    return "\n".join(lines) + "\n"


def _appetite_body(report: dict) -> str:
    """The appetite line, rendered only when the run declared one (or carried a forecast):
    what was budgeted, what it spent, what it delivered. The token line is a forecast,
    labelled so - a run's appetite is wall-clock and units, never a token gate."""
    ap = report.get("appetite")
    if not ap:
        return ""
    d, sp = ap["declared"], ap["spent"]
    mins = f"{d['minutes']:g} min" if d["minutes"] else "unbounded"
    units = f"{d['units']} unit(s)" if d["units"] else "unbounded"
    out = ["\n## Appetite\n",
           f"- **Declared:** wall-clock {mins}, units {units}",
           f"- **Spent:** {sp['minutes']:g} min, {sp['units']} unit(s) terminal",
           f"- **Delivered:** {ap['delivered']} unit(s)"]
    if ap.get("token_forecast"):
        out.append(f"- **Token forecast:** ~{ap['token_forecast']:,} tokens - a plan-time "
                   f"estimate, never a gate (a script cannot observe token spend)")
    return "\n".join(out) + "\n"


def render_body(report: dict) -> str:
    """The generated body. Every section is filled from the join - there is no authoring
    scaffold here, and so no `{{placeholder}}` that a renderer could fail to substitute.

    `Closed without delivery` is rendered only when there IS one: a unit dropped
    (Won't Implement / Rejected / Withdrawn) is neither remaining work nor a success, and
    folding it into Delivered would be the tool claiming an outcome it did not reach."""
    s = report["summary"]
    dropped = (f"\n## Closed without delivery ({s['dropped']})\n\n"
               + _unit_table(report["dropped"], "")) if s["dropped"] else ""
    return (
        "## Where to pick up\n\n" + _pickup_body(report) + _appetite_body(report) +
        f"\n## Delivered ({s['delivered']})\n\n"
        + _unit_table(report["delivered"], "_Nothing was delivered in this run._")
        + dropped +
        f"\n## Remaining ({s['remaining']})\n\n" + _remaining_body(report) +
        "\n## Open decisions\n\n" + _decisions_body(report)
    )


def _meta_lines(report: dict) -> list[tuple[str, str]]:
    """The head fields: the run's identity and how it ended. An unopened run says so rather
    than wearing a start time nobody recorded."""
    run = report.get("run") or {}
    run_id = run.get("run_id")
    started = run.get("started_at")
    if run_id:
        ident = f"{run_id} (started {started})" if started else run_id
    else:
        ident = "not recorded - the run was not opened via `sprint plan --write`"
    lines = [("Run", ident), ("Outcome", report.get("outcome") or "not recorded")]
    if run.get("goal"):
        lines.append(("Goal", run["goal"]))
    lines.append(("Batch source", report["batch_source"]))
    return lines


# --------------------------------------------------------------------------- retro link
def _find_retro(root: Path, retro_id: str) -> Path:
    """The retro file for an id in either spelling (`RETRO0021` / `RETRO-0021`). Raises when
    it does not exist - a handoff must never claim a link it did not make, so this is
    checked BEFORE anything is written."""
    stem = str(retro_id).replace("-", "").upper()
    d = root / "sdlc-studio" / "retros"
    hits = sorted(d.glob(f"{stem}*.md")) if d.is_dir() else []
    if not hits:
        raise ValueError(f"retro {retro_id} not found under sdlc-studio/retros/ - create it "
                         f"first (`artifact new --type retro`), then link the handoff to it")
    return hits[0]


def _link_from_retro(retro_path: Path, disp: str, file_name: str, report: dict) -> None:
    """Write the handoff link into the retro's `## Handoff` section (replacing it when one
    is already there, so a re-generated handoff never stacks a second)."""
    s = report["summary"]
    body = (f"- [{disp}](../handoffs/{file_name}) - {s['remaining']} remaining item(s): "
            f"{s[COPILOT_TAIL]} copilot-tail, {s[JUDGEMENT]} judgement. Pick up with "
            f"`sprint plan --worklist {report['worklist']}`.\n")
    text = retro_path.read_text(encoding="utf-8")
    sdlc_md.atomic_write(retro_path, artifact._put_section(text, ("Handoff",), body))


# --------------------------------------------------------------------------- generate
def _ensure_index(root: Path, today: str) -> bool:
    """Create `sdlc-studio/handoffs/_index.md` from the shipped template when it is missing,
    so the first handoff in a project is INDEXED rather than becoming reconcile drift the
    operator then has to clear by hand. Idempotent; never clobbers an existing index."""
    import re
    idx = root / "sdlc-studio" / "handoffs" / "_index.md"
    if idx.exists():
        return False
    tmpl = Path(__file__).resolve().parent.parent / "templates" / "indexes" / f"{TYPE}.md"
    if not tmpl.exists():
        return False
    text = re.sub(r"^<!--.*?-->\n+", "", tmpl.read_text(encoding="utf-8"),
                  count=1, flags=re.DOTALL)
    text = text.replace("{{last_updated}}", today)
    lines = [ln for ln in text.splitlines() if "{{" not in ln]  # drop the sample row
    idx.parent.mkdir(parents=True, exist_ok=True)
    sdlc_md.atomic_write(idx, "\n".join(lines).rstrip() + "\n")
    return True


def generate(repo_root: Path | str, title: str, batch: list[str] | None = None,
             outcome: str | None = None, retro: str | None = None,
             dry_run: bool = False) -> dict:
    """Build the join, create the handoff through the artifact machinery (tool-allocated id,
    index row), emit the worklist the next plan reads, link it from the retro, and close the
    run state with its outcome."""
    root = Path(repo_root)
    title = _heading_title(title)   # strip trailing punctuation so the H1 passes MD026
    report = build(root, batch=batch, outcome=outcome)
    retro_path = _find_retro(root, retro) if retro else None  # refuse before any write
    if dry_run:
        return {"id": None, "path": None, "dry_run": True, "indexed": None,
                "retro_linked": bool(retro_path), "worklist": str(root / WORKLIST_REL),
                "report": report}
    _ensure_index(root, sdlc_md.now_date())
    res = artifact.meta_new(root, TYPE, title,
                            {"body": render_body(report), "meta": _meta_lines(report)})
    worklist = root / WORKLIST_REL
    worklist.parent.mkdir(parents=True, exist_ok=True)
    sdlc_md.atomic_write(worklist, _worklist_text(report, res["id"]))
    if retro_path is not None:
        _link_from_retro(retro_path, res["id"], Path(res["path"]).name, report)
    run_state.update(root, handoff_worklist=str(WORKLIST_REL),
                     handoff_remaining=report["summary"]["remaining"])
    if outcome:
        run_state.close_run(root, outcome, handoff=res["id"])
    else:
        run_state.update(root, handoff=res["id"])
    return {**res, "dry_run": False, "retro_linked": retro_path is not None,
            "worklist": str(worklist), "report": report}


def _recorded_run_id(text: str) -> str:
    """The run id a handoff document already claims, or "" when it records none.

    The head renders `> **Run:** RUN-XXXX (started ...)`, and an unopened run renders a
    sentence instead - so only a leading token that looks like a run id counts.
    """
    for line in text.splitlines():
        if line.startswith("> **Run:**"):
            token = line.split("**Run:**", 1)[1].strip().split()[0] if line.split(
                "**Run:**", 1)[1].strip() else ""
            return token if token.upper().startswith("RUN-") else ""
    return ""


def refresh(repo_root: Path | str, handoff_id: str, batch: list[str] | None = None) -> dict | None:
    """Re-render an EXISTING handoff after the close cascade moved units terminal.

    The close chain writes the handoff at step 5, but `--apply-signoff` transitions the run's
    units to Done at the tail, one step later. The document was therefore a snapshot taken
    just before the work it describes finished: units the close was about to complete were
    listed as remaining, and the worklist the next `sprint plan --worklist` reads carried
    them forward as outstanding work.

    Rewrites the same artefact in place - same id, same index row, same retro link, same RUN -
    so the handoff describes the state the close actually left behind. Returns None when the id
    has no file, so a caller can report the gap instead of assuming a refresh happened.

    A handoff belongs to a run. The re-render draws the unit list from `batch` but everything
    else from ambient run state, so refreshing one run's handoff while a DIFFERENT run is open
    would re-stamp it with the other run's identity and overwrite the shared worklist. That is
    refused rather than done quietly: the caller is refreshing the wrong document, and a
    handoff wearing another run's id misdirects whoever picks the work up.
    """
    root = Path(repo_root)
    norm = sdlc_md.norm_id(handoff_id)
    path = next((p for p in sorted((root / "sdlc-studio" / "handoffs").glob("*.md"))
                 if p.is_file() and sdlc_md.norm_id(p.stem.split("-")[0]) == norm), None)
    if path is None:
        return None
    existing = path.read_text(encoding="utf-8")
    doc_run = _recorded_run_id(existing)
    open_run_id = ((run_state.read(root) or {}).get("run_id") or "").strip()
    if doc_run and open_run_id and doc_run != open_run_id:
        raise ValueError(
            f"{handoff_id} belongs to {doc_run} but the open run is {open_run_id} - refusing to "
            f"re-stamp it with another run's identity; close or clear the open run first")
    report = build(root, batch=batch)
    lines = path.read_text(encoding="utf-8").splitlines()
    # Keep the H1 and the Revision History; regenerate everything the join owns.
    head = lines[0] if lines and lines[0].startswith("# ") else f"# {handoff_id}"
    tail_at = next((i for i, ln in enumerate(lines)
                    if ln.strip().lower().startswith("## revision history")), None)
    tail = "\n".join(lines[tail_at:]) if tail_at is not None else ""
    meta = "\n".join(f"> **{k}:** {v}" for k, v in _meta_lines(report))
    date = next((ln for ln in lines if ln.startswith("> **Date:**")), "")
    created = next((ln for ln in lines if ln.startswith("> **Created-by:**")), "")
    head_block = "\n".join(x for x in (date, created, meta) if x)
    body = f"{head}\n\n{head_block}\n\n{render_body(report)}\n"
    if tail:
        body += f"\n{tail}\n"
    # `render_body` already terminates its last section, so joining the kept tail onto it
    # produced two blank lines and the markdown gate (MD012) refused the commit. Collapse any
    # run of blank lines to one - a generated document must not need hand-fixing after every
    # refresh.
    body = re.sub(r"\n{3,}", "\n\n", body)
    sdlc_md.atomic_write(path, body)
    sdlc_md.atomic_write(root / WORKLIST_REL, _worklist_text(report, handoff_id))
    run_state.update(root, handoff_remaining=report["summary"]["remaining"])
    return report


# --------------------------------------------------------------------------- CLI
def cmd_generate(args: argparse.Namespace) -> int:
    ids = sdlc_md.resolve_ids(args)
    try:
        r = generate(args.root, args.title, batch=ids or None, outcome=args.outcome,
                     retro=args.retro, dry_run=args.dry_run)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(r, indent=2))
    else:
        s = r["report"]["summary"]
        verb = "would generate" if r["dry_run"] else "generated"
        print(f"{verb} handoff {r['id'] or '(dry run)'}: {s['delivered']} delivered, "
              f"{s['remaining']} remaining ({s[COPILOT_TAIL]} {COPILOT_TAIL}, "
              f"{s[JUDGEMENT]} {JUDGEMENT})")
        if not r["dry_run"]:
            print(f"  {r['path']}")
            print(f"  worklist -> {r['worklist']} (sprint plan --worklist)")
    if not r["retro_linked"]:
        print("warning: this handoff is not linked from a retro - pass --retro RETROxxxx; "
              "`gate --require-handoff` fails until a retro links it", file=sys.stderr)
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    ids = sdlc_md.resolve_ids(args)
    try:
        report = build(args.root, batch=ids or None)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(report, indent=2))
        return 0
    s = report["summary"]
    print(f"handoff (not written): {s['delivered']} delivered, {s['remaining']} remaining "
          f"({s[COPILOT_TAIL]} {COPILOT_TAIL}, {s[JUDGEMENT]} {JUDGEMENT})")
    for u in report["remaining"]:
        first = u["pointers"][0]
        print(f"  {u['id']} [{u['suitability']['tag']}] {first['kind']}: {first['ref']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="The run-close handoff guide (remaining work).")
    sub = p.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("generate", help="Create the handoff artefact + the worklist "
                                        "the next sprint plan reads.")
    g.add_argument("--title", required=True, help="what this run was")
    g.add_argument("--outcome", choices=run_state.CLOSED,
                   help="how the run ended; closes the run state")
    g.add_argument("--retro", metavar="RETROxxxx",
                   help="link the handoff from this retro (the close gate requires it)")
    sdlc_md.add_ids_argument(g, help_="the batch this run was approved to do; defaults to "
                                      "the recorded run state, then the persisted sprint plan")
    g.add_argument("--root", default=".")
    g.add_argument("--dry-run", action="store_true", dest="dry_run",
                   help="preview; write nothing")
    sdlc_md.add_format_arg(g)
    g.set_defaults(func=cmd_generate)
    s = sub.add_parser("show", help="Print the join without creating anything.")
    sdlc_md.add_ids_argument(s, help_="the batch to join over (default: the run state)")
    s.add_argument("--root", default=".")
    sdlc_md.add_format_arg(s)
    s.set_defaults(func=cmd_show)
    sdlc_md.add_global_root(p)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
