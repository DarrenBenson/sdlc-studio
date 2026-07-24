#!/usr/bin/env python3
"""SDLC Studio pipeline status.

Deterministic census of the four pillars (Requirements, Code, Tests, Reviews)
and the next-step hint, so Claude renders the dashboard from JSON instead of
reading every artifact in-context. Live metrics that need to run the project's
own toolchain (lint, type-check, coverage) are deliberately left out - the
script reports artifact-derived state; Claude runs the live checks.

Subcommands:
  pillars  Census of artifacts and reviews as JSON/text (default).
  hint     The single next action from the mechanical priority ladder.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402
import digest  # noqa: E402


def _print_update_notice(root: str) -> None:
    """Surface a one-line skill-update notice on status/hint - the skill's
    'on first use' check. Fully guarded: a disabled config / offline / any error is
    silent and never affects the status output."""
    try:
        import version_check as vc  # sibling; lazy so status never hard-depends on it
        enabled = bool(sdlc_md.project_override(root, "version_check.enabled", True))
        ttl = sdlc_md.project_override(root, "version_check.ttl_hours", vc.DEFAULT_TTL_HOURS)
        try:
            ttl = float(ttl)
        except (TypeError, ValueError):
            ttl = vc.DEFAULT_TTL_HOURS
        line = vc.notice(vc.check(ttl_hours=ttl, enabled=enabled))
        if line:
            print(line)
    except Exception:  # noqa: BLE001 - the version check must never break status/hint
        pass


def workspace_advisory(repo_root: Path | str) -> str | None:
    """One-line advisory when the sdlc-studio/ workspace carries uncommitted or
    untracked artifact changes - another session may be mid-flight. Informational
    only: names the artifact ids (or files), guesses no authorship, never blocks,
    and degrades silently when git (or a repo) is absent."""
    import subprocess
    root = Path(repo_root)
    try:
        proc = subprocess.run(["git", "status", "--porcelain", "--", "sdlc-studio/"],
                              cwd=root, capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None  # not a git repo - nothing to say
    names: list[str] = []
    for line in proc.stdout.splitlines():
        # a rename line reads 'R  old -> new': name BOTH ids (the vanished old
        # one is exactly what another session would go looking for)
        for path in line[3:].split(" -> "):
            path = path.strip().strip('"')
            rec = sdlc_md.extract_record_id(Path(path).stem)
            label = sdlc_md.norm_id(rec) if rec else Path(path).name
            if label and label not in names:
                names.append(label)
    if not names:
        return None
    shown = ", ".join(names[:6]) + (f" (+{len(names) - 6} more)" if len(names) > 6 else "")
    return (f"workspace has uncommitted artifact changes: {shown} - "
            f"another session may be mid-flight; check before filing or planning")


def _config_summary(repo_root: Path) -> dict | None:
    """Representative defaults read from config-defaults.yaml.

    Reads the single source via config.py. Lazy + graceful: if PyYAML is absent
    the census still works (the stdlib core has no hard YAML dependency).
    """
    try:
        import config  # sibling script; scripts dir is on sys.path
        return {
            "schema_version": config.get(repo_root, "schema_version"),
            "coverage": config.get(repo_root, "coverage"),
        }
    except Exception:  # pragma: no cover - PyYAML missing or unreadable config
        return None


def count_by_status(type_: str, repo_root: Path) -> dict:
    """Tally a type's files by canonical Status, plus a total.

    Decorated statuses (`Done (v2.66.0)`) collapse to their vocabulary token
    (`Done`) so the tally and done-percentages are correct; consultations files
    are excluded by `artifact_files`.
    """
    vocab = sdlc_md.status_vocab(type_, repo_root)
    # Context tiering: when digests are enabled, a closed artefact's status comes from the
    # digest keyed by filename, so its original is never read - the enumeration skips the
    # is-artifact read for those trusted names. Dormant (empty map) below the threshold, so a
    # small repo reads every original exactly as before.
    dfiles = digest.status_by_file(repo_root)
    counts: dict[str, int] = {}
    total = 0
    for path, text in sdlc_md.iter_artifact_files(type_, repo_root, trust_names=set(dfiles)):
        total += 1
        if text is None and path.name in dfiles:
            raw = dfiles[path.name] or "Unknown"          # from the digest: no read
        else:
            raw = sdlc_md.extract_field(text or "", "Status") or "Unknown"
        status = sdlc_md.canonical_status(raw, vocab) or "Unknown"
        counts[status] = counts.get(status, 0) + 1
    return {"total": total, "by_status": counts}


BACKLOG_TYPES: tuple[str, ...] = ("cr", "story", "epic", "bug", "rfc", "issue")


def backlog(repo_root: Path, types: tuple[str, ...] | None = None) -> dict:
    """Per-type census of the NON-terminal (open) artefacts, grouped by status, from a file
    census. Terminal detection uses the shared vocab's full terminal set via
    `sdlc_md.is_terminal_status`, not a hardcoded Done/Closed subset here, so every terminal
    status is excluded. Returns {type: {count, by_status: {status: [ids]}}}."""
    root = Path(repo_root)
    types = types or BACKLOG_TYPES
    result: dict = {}
    for t in types:
        vocab = sdlc_md.status_vocab(t, root)
        by_status: dict[str, list[str]] = {}
        count = 0
        for path in sdlc_md.artifact_files(t, root):
            raw = sdlc_md.extract_field(sdlc_md.read_text_safe(path), "Status") or "Unknown"
            st = sdlc_md.canonical_status(raw, vocab) or raw
            if sdlc_md.is_terminal_status(t, st):
                continue
            by_status.setdefault(st, []).append(sdlc_md.extract_record_id(path.stem) or path.stem)
            count += 1
        for ids in by_status.values():
            ids.sort(key=sdlc_md.norm_id)
        result[t] = {"count": count, "by_status": by_status}
    return result


def _two_backlog_summary(data: dict) -> dict:
    """Partition the per-type backlog into the two backlogs (G4): the DISCOVERY backlog (the
    options funnel - RFCs, CRs and Issues, discovery items not yet committed as work) and the
    DELIVERY backlog (epics, stories, bugs - sized work ready to deliver). This is dual-track
    agile / upstream Kanban: discovery feeds delivery. Driven by the shared `sdlc_md.is_discovery`,
    so status and the planner agree on which side of the line a type is on. Additive: the per-type
    keys are unchanged; this is a summary beside them."""
    def group(is_disc: bool) -> dict:
        present = {t: v for t, v in data.items()
                   if sdlc_md.is_discovery(t) == is_disc and v.get("count")}
        return {"count": sum(v["count"] for v in present.values()), "types": sorted(present)}
    return {"discovery": group(True), "delivery": group(False)}


# Statuses a Discovery item can sit in without awaiting refinement: parked on purpose (Deferred /
# Blocked on an external dependency / Paused). A Blocked item cannot be refined until unblocked and
# a Deferred one was parked deliberately, so nudging either is a false prompt. NOT terminal (those
# are excluded separately) and NOT the intake states (a Proposed CR / Draft RFC / Open Issue DOES
# await refinement - that is the whole point).
_PARKED_STATUSES = frozenset({"Blocked", "Deferred", "Paused"})


def discovery_awaiting(repo_root: Path | str) -> dict:
    """The Discovery-backlog items still awaiting decomposition: a live, non-parked RFC/CR/Issue
    with NO children yet. This is the depth of the options funnel that is not yet deliverable work
    - a request awaiting `refine`, an Issue awaiting `triage`. Surfaced at the hint so the
    dual-track is visible from the first command an operator reaches for, not only in
    `status backlog`. Returns `{count, ids}` (ids sorted). Excluded: an item already decomposed (In
    Progress, delivered via its children), a terminal item, and a deliberately PARKED item
    (Deferred/Blocked/Paused) - nudging the parked ones is a false prompt."""
    root = Path(repo_root)
    ids: list[str] = []
    for type_ in sdlc_md.DISCOVERY_TYPES:
        vocab = sdlc_md.status_vocab(type_, root)
        for p in sdlc_md.artifact_files(type_, root):
            text = sdlc_md.read_text_safe(p)  # a corrupt artefact must not abort the sweep
            status = sdlc_md.canonical_status(sdlc_md.extract_field(text, "Status"), vocab)
            if (not status or sdlc_md.is_terminal_status(type_, status)
                    or status in _PARKED_STATUSES):
                continue
            rid = sdlc_md.extract_record_id(p.stem) or p.stem
            if not sdlc_md.children_of(root, rid):
                ids.append(rid)
    return {"count": len(ids), "ids": sorted(ids)}


def cmd_backlog(args: argparse.Namespace) -> int:
    """List the non-terminal artefacts, split into the request backlog (intake) and the product
    backlog (deliverable), each grouped by type and status (the deterministic backlog answer)."""
    root = Path(args.root)
    types = (args.type,) if args.type else BACKLOG_TYPES
    data = backlog(root, types)
    if args.format == "json":
        out = dict(data)
        out["backlogs"] = _two_backlog_summary(data)  # additive; per-type keys unchanged
        print(json.dumps(out, indent=2))
        return 0
    total = sum(v["count"] for v in data.values())
    if total == 0:
        print("backlog: empty - no non-terminal artefacts.")
        return 0
    print(f"Backlog: {total} non-terminal artefact(s)")
    # Two backlogs (dual-track): the DISCOVERY backlog is the options funnel - a request is not
    # committed work until it is decomposed; counting it as backlog overstates what is ready to
    # deliver. The DELIVERY backlog is the sized work. Split so the two are never conflated.
    for label, hint, is_disc in (
            ("Discovery backlog", "options - refine requests / triage issues before it is work", True),
            ("Delivery backlog", "sized work, ready to deliver", False)):
        present = [t for t in types
                   if sdlc_md.is_discovery(t) == is_disc and (data.get(t) or {}).get("count")]
        if not present:
            continue
        subtotal = sum(data[t]["count"] for t in present)
        print(f"\n{label} ({hint}): {subtotal}")
        for t in present:
            v = data[t]
            print(f"  {t}: {v['count']}")
            for st, ids in sorted(v["by_status"].items()):
                print(f"    {st}: {', '.join(ids)}")
    return 0


def _pct_done(census: dict, done_states: tuple[str, ...]) -> int:
    """Percentage of a census in any of the done_states (0 if empty)."""
    total = census["total"]
    if not total:
        return 0
    done = sum(census["by_status"].get(s, 0) for s in done_states)
    return round(100 * done / total)


def _verify_lane(repo_root: Path) -> dict:
    """The AC-verification lane: from `verify-report.json`, surface stories with
    unverified ACs (`no`/`stale` failures) and the manual-AC count as their own line - so
    env-bound / manual ACs read as 'deferred', not as silent gaps. Empty when no report."""
    report = sdlc_md.read_json(repo_root / "sdlc-studio" / ".local" / "verify-report.json", {})
    stories = report.get("stories", {})
    entries = stories.values() if isinstance(stories, dict) else stories
    unverified = sum(1 for s in entries if s.get("failed", 0) or s.get("stale", 0))
    manual = sum(s.get("manual", 0) for s in entries)
    return {"has_report": bool(stories), "stories_with_unverified_acs": unverified,
            "manual_acs": manual}


def gather(repo_root: Path) -> dict:
    """Compute all four pillars from the artifact files and review state."""
    base = repo_root / "sdlc-studio"
    epics = count_by_status("epic", repo_root)
    stories = count_by_status("story", repo_root)
    test_specs = count_by_status("test-spec", repo_root)
    bugs = count_by_status("bug", repo_root)
    workflows = count_by_status("workflow", repo_root)

    review_state = sdlc_md.read_json(base / ".local" / "review-state.json", {})
    review_files = sdlc_md.walk_glob(base / "reviews", "RV*.md")

    return {
        "generated_at": sdlc_md.now_iso8601(),
        "config": _config_summary(repo_root),
        "requirements": {
            "prd": (base / "prd.md").exists(),
            "personas": (base / "personas.md").exists(),
            "epics": epics,
            "stories": stories,
            "epics_ready_pct": _pct_done(epics, ("Ready", "Approved", "Done")),
            "stories_done_pct": _pct_done(stories, ("Done",)),
        },
        "code": {
            "trd": (base / "trd.md").exists(),
            "note": "run project lint/type-check/coverage live; not derivable from files",
        },
        "tests": {
            "tsd": (base / "tsd.md").exists(),
            "test_specs": test_specs,
            "verification": _verify_lane(repo_root),
        },
        "bugs": bugs,
        "workflows": workflows,
        "reviews": {
            "has_review_state": bool(review_state),
            "review_files": len(review_files),
            "latest": (base / "reviews" / "LATEST.md").exists(),
        },
        # The two-backlog split (dual-track), surfaced on the main dashboard - not only in
        # `status backlog` - so the Discovery vs Delivery divide is visible from the first command
        # an operator reaches for. `awaiting` is the Discovery depth not yet decomposed.
        "backlogs": {**_two_backlog_summary(backlog(repo_root)),
                     "awaiting": discovery_awaiting(repo_root)},
    }


def cmd_pillars(args: argparse.Namespace) -> int:
    """Print the four-pillar census."""
    data = gather(Path(args.root).resolve())
    if args.format == "json":
        print(json.dumps(data, indent=2))
        return 0
    req = data["requirements"]
    print(f"Requirements: PRD={'yes' if req['prd'] else 'no'} "
          f"personas={'yes' if req['personas'] else 'no'} "
          f"epics={req['epics']['total']} ({req['epics_ready_pct']}% ready+) "
          f"stories={req['stories']['total']} ({req['stories_done_pct']}% done)")
    print(f"Code:         TRD={'yes' if data['code']['trd'] else 'no'}")
    print(f"Tests:        TSD={'yes' if data['tests']['tsd'] else 'no'} "
          f"test-specs={data['tests']['test_specs']['total']}")
    print(f"Bugs:         open={data['bugs']['by_status'].get('Open', 0)} "
          f"fixed={data['bugs']['by_status'].get('Fixed', 0)} total={data['bugs']['total']}")
    print(f"Workflows:    total={data['workflows']['total']}")
    print(f"Reviews:      files={data['reviews']['review_files']} "
          f"latest={'yes' if data['reviews']['latest'] else 'no'}")
    bl = data["backlogs"]
    disc, deliv = bl["discovery"], bl["delivery"]
    awaiting = bl["awaiting"]["count"]
    disc_types = f" ({', '.join(disc['types'])})" if disc["types"] else ""
    deliv_types = f" ({', '.join(deliv['types'])})" if deliv["types"] else ""
    print(f"Backlogs:     Discovery={disc['count']}{disc_types}"
          f"{f', {awaiting} awaiting refine/triage' if awaiting else ''} · "
          f"Delivery={deliv['count']}{deliv_types}")
    adv = workspace_advisory(Path(args.root))
    if adv:
        print(f"advisory: {adv}")
    import persona_gen  # lazy sibling: a provisional label nobody surfaces is never cleared
    prov = persona_gen.provisional_seats(Path(args.root))
    if prov:
        print(f"advisory: {len(prov)} generated persona card(s) still provisional-unverified "
              f"({', '.join(prov[:3])}{'...' if len(prov) > 3 else ''}) - review and accept "
              f"them: persona_gen.py accept (or `persona review`)")
    offer = team_offer_advisory(Path(args.root))
    if offer:
        print(f"advisory: {offer}")
    import gate  # lazy sibling: one shared hook-gap message, so the two surfaces cannot drift
    gap = gate.hook_enablement_gap(args.root)
    if gap:
        print(f"advisory: {gap}")
    owed = close_owed_advisory(Path(args.root))
    if owed:
        print(f"advisory: {owed}")
    tri = backlog_triage_advisory(Path(args.root))
    if tri:
        print(f"advisory: {tri}")
    drift = installed_copy_drift_advisory(sdlc_md.resolve_root(args))
    if drift:
        print(f"advisory: {drift}")
    age = ageing_advisory(Path(args.root))
    if age:
        print(f"advisory: {age}")
    _print_update_notice(args.root)
    return 0


def ageing_advisory(repo_root: Path | str, *, today=None) -> str | None:
    """One line naming aged In Progress and stuck Blocked units - only when the
    project opted in via `flow.ageing_days` (absent = silent, the feature is off)."""
    import flow  # lazy sibling: the measurement lives in flow, status only surfaces it
    rep = flow.ageing_report(repo_root, today=today)
    if not rep or not (rep["flagged"] or rep["blocked"]):
        return None
    bits = []
    if rep["flagged"]:
        bits.append("in progress > " + f"{rep['days']}d: "
                    + ", ".join(f"{rid} ({age}d)" for rid, _s, age in rep["flagged"][:5])
                    + (f" +{len(rep['flagged']) - 5} more" if len(rep["flagged"]) > 5 else ""))
    if rep["blocked"]:
        bits.append("blocked: " + ", ".join(
            f"{rid} ({bd}d stuck)" if bd is not None else f"{rid} (blocked-age unresolvable)"
            for rid, bd, _a in rep["blocked"][:5]))
    return "work-item ageing - " + "; ".join(bits) + " (flow.py compute for the full read)"


def team_offer_advisory(repo_root: Path | str) -> str | None:
    """One-line meet-your-team offer: a PRD exists but no working-team seat card does.
    An offer, never a hint-ladder rung - the operator may happily stay on the shipped
    defaults, so this informs on status/hint and never blocks or nags a step."""
    root = Path(repo_root)
    if not (root / "sdlc-studio" / "prd.md").is_file():
        return None
    seats = root / "sdlc-studio" / "personas" / "seats"
    if seats.is_dir() and any(seats.glob("*.md")):
        return None
    return ("meet your team - `persona generate --team` grows named working seats from "
            "this project's PRD and stack (offer; the shipped defaults keep working)")


def compute_hint(data: dict, repo_root: Path) -> dict:
    """Mechanical next-step ladder. Judgment branches are left to Claude. The result also carries a
    `discovery` summary (how many Discovery items await refinement/triage) - additive, so the
    dual-track shows up at the hint without changing which rung the ladder picks. It REUSES the
    value `gather` already computed (a full-repo scan): `cmd_hint` runs both, so recomputing here
    would double the cost of the most-run command."""
    awaiting = (data.get("backlogs") or {}).get("awaiting")
    return {**_compute_hint_rung(data, repo_root),
            "discovery": awaiting if awaiting is not None else discovery_awaiting(repo_root)}


def _compute_hint_rung(data: dict, repo_root: Path) -> dict:
    req = data["requirements"]
    base = repo_root / "sdlc-studio"
    has_code = any((repo_root / d).exists() for d in ("src", "lib", "app", "cmd"))
    if not req["prd"]:
        return {"next_command": "prd generate" if has_code else "prd create",
                "reason": "no PRD yet"}
    # Lite profile collapses the pipeline to PRD -> story -> implement: the TRD/TSD/
    # persona/epic rungs are skipped, and their absence is never nagged.
    if sdlc_md.profile(repo_root) != "lite":
        if not data["code"]["trd"]:
            return {"next_command": "trd generate" if has_code else "trd create",
                    "reason": "no TRD yet"}
        if not data["tests"]["tsd"]:
            return {"next_command": "tsd", "reason": "no TSD yet"}
        if not req["personas"]:
            return {"next_command": "persona", "reason": "no personas yet"}
        if req["epics"]["total"] == 0:
            return {"next_command": "epic", "reason": "no epics yet"}
    if req["stories"]["total"] == 0:
        return {"next_command": "story", "reason": "no stories yet"}
    if (base / ".local" / "workflow-state.json").exists():
        return {"next_command": "resume workflow",
                "reason": "a workflow-state.json is present (judgment: confirm with the operator)"}
    return {"next_command": "story plan / story implement",
            "reason": "pipeline seeded; pick the next Ready story (judgment)"}


def cmd_hint(args: argparse.Namespace) -> int:
    """Print the single next recommended action."""
    repo_root = Path(args.root).resolve()
    data = gather(repo_root)
    hint = compute_hint(data, repo_root)
    if args.format == "json":
        print(json.dumps(hint, indent=2))
    else:
        print(f"/sdlc-studio {hint['next_command']}  ({hint['reason']})")
        disc = hint.get("discovery") or {}
        if disc.get("count"):
            shown = ", ".join(disc["ids"][:5]) + ("..." if disc["count"] > 5 else "")
            print(f"discovery: {disc['count']} item(s) await refinement/triage ({shown}) - "
                  f"`refine` a request into stories, `triage` an Issue into bugs")
        _print_update_notice(args.root)
    adv = workspace_advisory(Path(args.root))
    if adv and args.format != "json":
        print(f"advisory: {adv}")
    if args.format != "json":
        offer = team_offer_advisory(Path(args.root))
        if offer:
            print(f"advisory: {offer}")
        owed = close_owed_advisory(Path(args.root))
        if owed:
            print(f"advisory: {owed}")
        tri = backlog_triage_advisory(Path(args.root))
        if tri:
            print(f"advisory: {tri}")
        drift = installed_copy_drift_advisory(sdlc_md.resolve_root(args))
        if drift:
            print(f"advisory: {drift}")
        for line in index_bloat_advisories(Path(args.root)):
            print(f"advisory: {line}")
    return 0


def close_owed_advisory(repo_root: Path | str) -> str | None:
    """One line when a sprint close is owed: delivery units reached terminal since the baseline
    with no retro accounting for them. Surfaced on hint and status so a skipped close-down is
    SEEN where operators look, not discovered sprints later when the lessons stopped compounding.
    An unbaselined project (no cutoff stamped) is silent here - it is a soft state, not a nag."""
    try:
        import close_owed  # lazy sibling: no cost when the surface is unused
        report = close_owed.owed(Path(repo_root))
    except Exception:  # noqa: BLE001 - an advisory must never break the hint
        return None
    if report.get("corrupt"):
        # A corrupt baseline silently disarms the close-down: surface it loudly and direct a repair,
        # never the `baseline` re-stamp, which would forgive the units that owe a close.
        return (f"close-owed baseline is CORRUPT ({report.get('error', 'unreadable')}): it silently "
                f"disarms the close-down - repair .close-owed-baseline.json (restore from git); do "
                f"NOT run `close_owed.py baseline`, which would forgive the owed units")
    if not report["baselined"]:
        # The prerequisite is itself skippable and, unnudged, invisible: a project with closed work
        # but no baseline enforces nothing. Nudge it ONCE it has terminal units to judge, so the
        # "un-skippable" close-down does not hinge on an un-surfaced setup step.
        if report["owed"]:
            return (f"close-owed tracking is not initialised: {len(report['owed'])} terminal "
                    f"delivery unit(s) exist with no baseline - run `close_owed.py baseline` once "
                    f"to grandfather them, then a later skipped close is caught")
        return None
    if not report["owed"]:
        return None
    ids = [cid for cid, _ in report["owed"]]
    shown = ", ".join(ids[:5]) + ("..." if len(ids) > 5 else "")
    return (f"a sprint close is owed: {len(ids)} delivery unit(s) reached terminal with no retro "
            f"({shown}) - run the retro, then `gate --require-retro RETROxxxx`")


def backlog_triage_advisory(repo_root: Path | str) -> str | None:
    """One line when the backlog carries triage findings (duplicates, oversized, stale, orphaned
    dependencies) - so a dirty backlog is seen on status, not discovered only when `plan` reads it.
    Names the counts by lens; the detail lives in `backlog_triage.py check` and in the plan."""
    try:
        import backlog_triage  # lazy sibling: no cost when unused
        report = backlog_triage.triage(Path(repo_root))
    except Exception:  # noqa: BLE001 - an advisory must never break the hint
        return None
    findings = report.get("findings") or []
    skipped = report.get("skipped", 0)
    if not findings:
        # Do not imply a clean backlog if some artefacts could not be read - name the gap.
        if skipped:
            return (f"backlog triage: {skipped} artefact(s) unreadable - could not be checked "
                    f"(`backlog_triage.py check`)")
        return None
    by_lens: dict[str, int] = {}
    for f in findings:
        by_lens[f["lens"]] = by_lens.get(f["lens"], 0) + 1
    parts = ", ".join(f"{n} {lens}" for lens, n in sorted(by_lens.items()))
    tail = " (blocks planning)" if report.get("blocked") else ""
    unread = f", {skipped} unreadable" if skipped else ""
    return (f"backlog triage: {len(findings)} item(s) - {parts}{tail}{unread} - "
            f"`backlog_triage.py check` for detail, resolve before planning")


#: The repository's own installed-copy drift check, relative to the project root. Its PRESENCE
#: is what arms this surface: a project that ships no such check - which is every consuming
#: project - is silent here, and no verdict is invented on its behalf.
DRIFT_CHECK = ("tools", "forward-port.sh")
#: The one command that clears the drift, quoted as the remedy on both surfaces.
DRIFT_REMEDY = "bash tools/forward-port.sh --yes"


def installed_copy_drift(repo_root: Path | str, *, timeout: float = 30.0) -> dict | None:
    """`{"count": n, "remedy": ...}` when the installed copy of the skill has drifted from
    this repository's source, else None.

    An installed copy is what every other project on the machine loads, so the window between
    a fix landing in a repo and the mirror running is a window in which a fix believed shipped
    is in force nowhere. The verdict is not computed here: it is delegated wholly to the
    project's own drift check, which already knows what to exclude and which states (no copy,
    a deliberately pinned one) are reported rather than failed. This reads its exit status and
    its count.

    Never raises and never guesses: no check, no shell, a timeout, or an answer carrying no
    count all degrade to None, exactly as every other advisory here does.
    """
    import subprocess
    root = Path(repo_root)
    check = root.joinpath(*DRIFT_CHECK)
    if not check.is_file():
        return None
    try:
        proc = subprocess.run(["bash", str(check), "--check"], cwd=root,
                              capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode == 0:
        return None
    import re
    m = re.search(r"(\d+) file\(s\) differ", proc.stdout)
    if not m:
        # Non-zero for a reason that is not a drift verdict (a refused argument, an
        # unresolvable target). Reporting a drift of unknown size would be a false alarm.
        sdlc_md.debug("status.installed_copy_drift", f"no count in: {proc.stdout.strip()[:200]}")
        return None
    return {"count": int(m.group(1)), "remedy": DRIFT_REMEDY}


def installed_copy_drift_advisory(repo_root: Path | str) -> str | None:
    """One line naming how many files differ and the command that mirrors them."""
    drift = installed_copy_drift(repo_root)
    if not drift:
        return None
    return (f"the installed copy has drifted: {drift['count']} file(s) differ from this "
            f"repository's skill source - every other project on this machine loads that copy, "
            f"so a fix landed here is in force nowhere until it is mirrored: {drift['remedy']}")


def index_bloat_advisories(repo_root: Path) -> list[str]:
    """The per-type archive recommendations (reconcile's index-bloat rule),
    surfaced at the hint so a bloating index is seen where operators look."""
    try:
        import reconcile
    except ImportError:  # pragma: no cover - sibling script always ships
        return []
    out: list[str] = []
    for type_ in sdlc_md.ARTIFACT_TYPES:
        try:
            a = reconcile.index_bloat_advisory(type_, repo_root)
        except Exception:  # noqa: BLE001 - an advisory must never break the hint
            continue
        if a:
            out.append(a)
    return out


def tranche_members(repo_root: Path | str, tranche: str) -> list[dict]:
    """Every artefact carrying `> **Tranche:** <tranche>`, across all types - the answer to
    "what shipped in tranche X" read from the records alone (no scheduler). Record-only: the
    reference is set by an external orchestrator, never allocated by sdlc-studio."""
    root = Path(repo_root)
    want = (tranche or "").strip()
    out: list[dict] = []
    for type_ in sdlc_md.ARTIFACT_TYPES:
        for p in sdlc_md.artifact_files(type_, root):
            text = sdlc_md.read_text_safe(p)  # a corrupt artefact must not abort the sweep
            value = sdlc_md.tranche_ref(text)  # newline-safe: an empty field is not a member
            if value and value == want:
                out.append({"id": sdlc_md.extract_record_id(p.stem) or p.stem, "type": type_,
                            "title": sdlc_md.extract_h1_title(text) or "",
                            "status": sdlc_md.extract_field(text, "Status") or ""})
    return sorted(out, key=lambda r: r["id"])


def cmd_tranche(args: argparse.Namespace) -> int:
    """List every artefact carrying a given tranche reference."""
    members = tranche_members(args.root, args.value)
    if args.format == "json":
        print(json.dumps(members, indent=2))
        return 0
    if not members:
        print(f"tranche {args.value!r}: no artefacts")
        return 0
    print(f"tranche {args.value!r}: {len(members)} artefact(s)")
    for m in members:
        print(f"  {m['id']} ({m['type']}) [{m['status']}] {m['title']}")
    return 0


def cmd_triage_metrics(args: argparse.Namespace) -> int:
    """Print triage-quality metrics (schema v3): false-positive rate + severity inflation."""
    import triage_sampling  # sibling; imported lazily so `status` has no cost when unused
    m = triage_sampling.metrics(args.root)
    if args.format == "json":
        print(json.dumps(m, indent=2))
        return 0
    print(f"triage quality: {m['triaged']} triaged ({m['terminal']} terminal)")
    print(f"  false-positive rate: {m['false_positive_rate']:.0%} "
          f"({m['invalid_closed']} triaged-then-invalid)")
    si = m["severity_inflation"]
    print(f"  severity inflation: {si['inflated']} up, {si['deflated']} down (triager vs raiser)")
    pending = m["sampled_pending_audit"]
    if pending:
        print(f"  sampled, pending audit ({len(pending)}): {', '.join(pending)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Construct the argparse parser for pillars and hint."""
    p = argparse.ArgumentParser(
        prog="status.py",
        description="Deterministic sdlc-studio pipeline status and hint.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    pi = sub.add_parser("pillars", help="Census of the four pillars.")
    pi.add_argument("--root", default=".", help="Repo root (default: .)")
    pi.add_argument("--format", choices=("text", "json"), default="text")
    pi.set_defaults(func=cmd_pillars)

    hi = sub.add_parser("hint", help="The next recommended action.")
    hi.add_argument("--root", default=".", help="Repo root (default: .)")
    hi.add_argument("--format", choices=("text", "json"), default="text")
    hi.set_defaults(func=cmd_hint)

    bl = sub.add_parser("backlog", help="Non-terminal artefacts per type and status (the backlog).")
    bl.add_argument("--type", choices=sorted(BACKLOG_TYPES), help="Restrict to one type")
    bl.add_argument("--root", default=".", help="Repo root (default: .)")
    bl.add_argument("--format", choices=("text", "json"), default="text")
    bl.set_defaults(func=cmd_backlog)

    tr = sub.add_parser("tranche", help="List artefacts carrying a given tranche reference.")
    tr.add_argument("--value", required=True, help="The tranche reference to list members of")
    tr.add_argument("--root", default=".", help="Repo root (default: .)")
    tr.add_argument("--format", choices=("text", "json"), default="text")
    tr.set_defaults(func=cmd_tranche)

    tm = sub.add_parser("triage-metrics",
                        help="Triage-quality metrics (v3): false-positive rate + inflation.")
    tm.add_argument("--root", default=".", help="Repo root (default: .)")
    tm.add_argument("--format", choices=("text", "json"), default="text")
    tm.set_defaults(func=cmd_triage_metrics)

    sdlc_md.add_global_root(p)
    return p


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and dispatch to the chosen subcommand."""
    parser = build_parser()
    args = parser.parse_args(argv)
    # Resolve the root ONCE and write it back, so every verb below anchors on the same
    # tree. Resolving it at only one call site let the two disagree - the resolved value
    # guarded or advised on the real project while other verbs still read a bare
    # `--root .`, so one invocation could report on two different trees.
    args.root = str(sdlc_md.resolve_root(args))
    # A read taken while a mutation run has a mutant applied is degraded evidence, not
    # forbidden: say so loudly on stderr, then answer the question that was asked.
    warning = sdlc_md.inflight_warning(sdlc_md.resolve_root(args))
    if warning:
        print(warning, file=sys.stderr)
    return args.func(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001 - top-level guard
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
