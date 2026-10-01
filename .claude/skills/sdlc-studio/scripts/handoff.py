#!/usr/bin/env python3
"""The remaining-work join a run's handoff guide was built from, read-only.

No command writes a handoff any more: the signed sprint report hands over the open findings
and carried units, and the next `sprint plan` reads them from it (`--worklist RPTxxxx`). The
HO files already written stay on disk and in `handoffs/_index.md`, resolvable and reconciled.
What remains here is the JOIN over evidence that already exists, which `show` prints and
`status.py` reads through `remaining_count`:

  quarantined units + failure signatures  <- .local/loop-state.json  (loop_guard)
  failing / unproven ACs                  <- .local/verify-report.json (verify_ac)
  per-unit readiness issues               <- readiness.audit_unit
  the lifecycle stage a unit stalled at   <- conformance.detect_conformance
  the approved batch and the run's shape  <- .local/run-state.json, .local/sprint-plan.json
  difficulty band (the suitability seed)  <- route.estimate
  units the run cannot end over           <- sprint.unanswered_units (the close's predicate)

Two properties are load-bearing:

* **Nothing is omitted.** Every unit that is not terminal is named, with at least one
  pointer (an AC, a check, a blocker, or - always available - its own file). A batch id
  with no file on disk is reported as remaining-and-missing, never dropped; a unit the loop
  quarantined is reported even if it was never in the approved batch. A handoff that
  silently loses an item is worse than no handoff.

The suitability tag (copilot-tail vs judgement) is seeded deterministically from the
difficulty band, the quarantine reason, the stage the unit stalled at, and the tranche
audit's issues (see the JUDGEMENT_* constants). It is a seed, not a verdict: the closing
model refines it, and every tag carries the reasons it was derived from, so it can be
argued with rather than merely believed.

Subcommands:
  show       Print the join without creating anything.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import run_state, sdlc_md  # noqa: E402
import readiness  # noqa: E402  (per-unit readiness issues)
import conformance  # noqa: E402  (the stage a unit stalled at)
import critic  # noqa: E402  (delivery evidence: the recorded verdict)
import decisions  # noqa: E402  (the project decisions log)
import loop_guard  # noqa: E402  (quarantine verdicts + failure signatures)
import route  # noqa: E402  (the difficulty band that seeds the suitability tag)

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
# This is deliberately NOT `readiness.MET` - that is a DEPENDENCY-SATISFACTION set (a superseded
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


def _classify(root: Path, rid: str, verify_report: dict) -> dict:
    """THE terminal-versus-dropped predicate, in one place. `build` reads it for every row of
    the join and the dashboard's `Run:` line reads it through `remaining_count`, so the two
    cannot answer "how many remain" differently (a second copy of it was found once, and a
    review found the copy's uncovered branches).

    Four outcomes. A unit with no file on disk is REMAINING (`found` False). A terminal
    status outside `DELIVERED_STATUSES` (Won't Implement / Rejected / Withdrawn / Superseded)
    is DROPPED - not remaining work, and not a success either. A terminal status whose verify
    report carries no red or stale criterion is DELIVERED. Everything else - open, or terminal
    with evidence that contradicts the status - is REMAINING, with `unproven` saying why."""
    found = sdlc_md.find_by_id(root, rid)
    if found is None:
        return {"found": False, "rec": sdlc_md.norm_id(rid), "path": None, "type": None,
                "text": "", "status": "missing", "verify": None, "terminal": False,
                "dropped": False, "delivered": False, "unproven": None}
    path, type_ = found
    # `read_text_safe`, not `Path.read_text`: inside a `corpus_cache` sweep the walk has already
    # read this file and serves it, so the dashboard's census and its run line read each unit
    # once. An unreadable file classifies as Unknown status - remaining - and is recorded in the
    # degradation log, where the base ref raised out of the whole join.
    text = sdlc_md.read_text_safe(path)
    status = sdlc_md.canonical_status(sdlc_md.extract_field(text, "Status"),
                                      sdlc_md.status_vocab(type_, root)) or "Unknown"
    rec = sdlc_md.extract_record_id(path.stem) or rid
    verify = _verify_entry(verify_report, rec)
    terminal = status in sdlc_md.terminal_statuses(type_)
    base = {"found": True, "rec": rec, "path": path, "type": type_, "text": text,
            "status": status, "verify": verify}
    if terminal and status not in DELIVERED_STATUSES:
        return {**base, "terminal": True, "dropped": True, "delivered": False, "unproven": None}
    unproven = _unproven(verify) if terminal else None
    if terminal and not unproven:
        return {**base, "terminal": True, "dropped": False, "delivered": True, "unproven": None}
    return {**base, "terminal": False, "dropped": False, "delivered": False,
            "unproven": unproven}


def _unit(root: Path, rid: str, ctx: dict) -> dict:
    """One unit's row in the join: delivered or remaining, with its evidence or its
    pointers. A unit with no file on disk is a REMAINING item whose first problem is that
    nobody can find it. The verdict itself is `_classify`'s; this adds the evidence or the
    pointers the row carries."""
    c = _classify(root, rid, ctx["verify"])
    if not c["found"]:
        return {"id": c["rec"], "type": None, "status": "missing", "path": None,
                "delivered": False, "dropped": False, "terminal": False,
                "pointers": [{"kind": "issue", "ref": "not-found",
                              "detail": f"no artefact file for {rid} - it was in the batch "
                                        f"and is not on disk"}],
                "suitability": _suitability(None, "low", [], [], None, found=False)}
    path, type_, text, status, rec, verify = (c["path"], c["type"], c["text"], c["status"],
                                              c["rec"], c["verify"])
    if c["dropped"]:
        # Closed, but not delivered. Its own bucket rather than a row under "Delivered"
        # claiming an outcome the run never reached.
        return {"id": rec, "type": type_, "status": status, "path": _rel(root, path),
                "delivered": False, "dropped": True, "terminal": True,
                "evidence": _delivery_evidence(root, rec, ctx["verify"])}
    if c["delivered"]:
        return {"id": rec, "type": type_, "status": status, "path": _rel(root, path),
                "delivered": True, "dropped": False, "terminal": True,
                "evidence": _delivery_evidence(root, rec, ctx["verify"])}
    unproven = c["unproven"]
    # ...everything else is REMAINING - including a unit whose status says Done while its
    # evidence says otherwise. Its failing verifier is the pointer the next person needs.
    try:
        unit_audit = readiness.audit_unit(root, rec)
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


def remaining_count(repo_root: Path | str, batch: list[str] | None = None) -> int:
    """How many of the batch's units remain, by `_classify` - the SAME predicate `build` reads
    - and nothing else of `build`'s weight. `build` also asks conformance for the
    stage each unit stalled at and readiness for its pointers - 62 seconds on this corpus -
    which the dashboard's `Run:` line never shows. The batch is read the way `build` reads
    it, including a unit the loop quarantined outside it."""
    root = Path(repo_root)
    ids, _source = _batch_source(root, batch)
    loop = _loop_state(root)
    verify = _verify_report(root)
    seen = {sdlc_md.norm_id(i) for i in ids}
    extra = sorted(u for u in (loop.get("units") or {}) if sdlc_md.norm_id(u) not in seen)
    return sum(1 for rid in list(ids) + extra if not _classify(root, rid, verify)["terminal"])


def build(repo_root: Path | str, batch: list[str] | None = None,
          outcome: str | None = None, retro: str | None = None) -> dict:
    """The JOIN: what was delivered, what remains, and what decisions are still owed.

    `retro` names the retro whose carried table answers the unanswered-unit predicate, as the
    close names it to its checklist step; None reads the latest retro carrying the run id.
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
    # The units the run cannot end over, by the close's own predicate - never by `remaining`,
    # which cannot see a ruling, a standing REJECT or an owed adversarial pass. Computed here so
    # `generate` and `refresh` render the same section, and walked over THIS document's batch:
    # a refresh scoped to the run being closed must not name the units of whichever run is open.
    # None when it cannot be computed: the handoff is still written, and says so, rather than
    # reporting an empty set it never read.
    import sprint  # noqa: PLC0415 - deferred sibling; sprint imports this module lazily too
    ua, ua_error = None, ""
    try:
        ua = sprint.unanswered_units(root, {**state, "batch": list(ids)}, retro)
    except Exception as exc:  # noqa: BLE001 - the join degrades and says so; it never dies
        ua_error = f"{type(exc).__name__}: {exc}"
    unanswered = ua["unanswered"] if ua else None
    return {
        "generated_at": sdlc_md.now_iso8601(),
        "run": state or None,
        "outcome": outcome or state.get("outcome") or None,
        "batch_source": source,
        "batch": [sdlc_md.norm_id(i) for i in ids],
        "delivered": delivered,
        "dropped": dropped,
        "remaining": remaining,
        "unanswered": unanswered,
        "unanswered_error": ua_error,
        "unanswered_rulings_from": ua["rulings_from"] if ua else None,
        "unanswered_ways_out": (sprint.unanswered_ways_out(unanswered, ua["rulings_from"],
                                                           state.get("run_id"))
                                if unanswered else ""),
        "open_decisions": _open_decisions(root, ids),
        "appetite": _appetite(root, state, ids, len(delivered)),
        "summary": {"total": len(units), "delivered": len(delivered),
                    "dropped": len(dropped), "remaining": len(remaining), **tags},
    }


# --------------------------------------------------------------------------- CLI
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
    p = argparse.ArgumentParser(description="The remaining-work join a handoff guide was "
                                            "built from, printed without writing anything. "
                                            "No command writes a handoff: the signed sprint "
                                            "report hands over the remaining work.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("show", help="Print the join without creating anything.")
    sdlc_md.add_ids_argument(s, help_="the batch to join over (default: the run state)")
    s.add_argument("--root", default=".")
    sdlc_md.add_format_arg(s)
    s.set_defaults(func=cmd_show)
    sdlc_md.add_global_root(p)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    # Resolve the root ONCE and write it back, so every verb below anchors on the tree the
    # run belongs to. The family default `.` means "work it out from here", not "the cwd
    # is the project": otherwise a run from a subdirectory acts on a stray tree and exits 0.
    args.root = str(sdlc_md.resolve_root(args))
    return args.func(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
