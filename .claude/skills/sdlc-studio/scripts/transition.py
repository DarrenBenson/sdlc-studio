#!/usr/bin/env python3
"""SDLC Studio status transition.

`transition --id <ID> --status <new>` performs the one mechanical write-side cascade
that was still hand-driven: set an artifact's `Status` field, sync its index row and the
summary counts, and (for a story) tick/untick its checkbox in the parent epic's Story
Breakdown. Deterministic once the new status is chosen - it reuses the validated
`reconcile.apply_type` to bring the index into line with the file, so there is no
bespoke index-row editing.

Subcommand:
  set  Transition one artifact to a new status and cascade the index/epic updates.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402
import reconcile  # noqa: E402  (sibling - reuse the tested index-row + count sync)

# Statuses that mean "complete" for the epic-breakdown checkbox (a story is ticked).
_STORY_TICKED = {"Done", "Won't Implement", "Deferred", "Superseded"}
_REPORT_REL = "sdlc-studio/.local/verify-report.json"

# Verification-depth tiers, weakest first (reference-test-best-practices.md).
_TIERS = {"smoke": 0, "functional": 1, "conversational": 2, "soak": 3, "live": 4}
_TARGET_RE = re.compile(r"^\s*-\s*\*\*Verification target:\*\*\s*`?(\w+)`?", re.M)


def _depth_token(text: str) -> str | None:
    """The leading tier token of the `Verification depth` field (decorations like
    `functional (unit)` are fine), or None when the field is absent/unparseable."""
    raw = (sdlc_md.extract_field(text, "Verification depth") or "").strip()
    token = raw.split()[0].lower().strip("`") if raw else ""
    return token if token in _TIERS else None


def _bug_depth_gate(text: str, target_canon: str | None) -> str | None:
    """Block reason when a bug transition under-shoots its verification-depth tier.

    Fixed requires `functional`+; Verified claims the higher-tier proof landed,
    so it requires a tier ABOVE functional (conversational/soak/live); Closed
    on a production-affecting bug requires `soak`+. A missing/unparseable depth
    on a gated transition is refused, never treated as satisfied (fail loud).
    The non-production Close path is unchanged, and a project that never
    promotes to Verified is unaffected."""
    if target_canon not in ("Fixed", "Verified", "Closed"):
        return None
    if target_canon == "Closed":
        prod_raw = (sdlc_md.extract_field(text, "Production-affecting") or "").strip()
        # leading-token match, mirroring the depth field: `yes (checkout path)` is
        # still yes - a decorated flag must never silently switch the soak gate OFF.
        prod_tok = prod_raw.split()[0].rstrip(":,;-").lower() if prod_raw else ""
        if prod_tok not in ("yes", "true"):
            return None
    required = {"Fixed": "functional", "Verified": "conversational",
                "Closed": "soak"}[target_canon]
    token = _depth_token(text)
    if token is None:
        return (f"no parseable `Verification depth` field; {target_canon} requires "
                f"`{required}`+ - record the verified tier "
                f"(see reference-test-best-practices.md#verification-depth-tiers)")
    if _TIERS[token] < _TIERS[required]:
        if target_canon == "Verified":
            return (f"depth is `{token}`; Verified claims a proof ABOVE the "
                    f"functional tier (conversational/soak/live) - run that "
                    f"verification, then set the depth, or stay at Fixed")
        return (f"depth is `{token}`; {target_canon} requires `{required}`+ - run the "
                f"verification that tier demands, then set the depth")
    return None


def _story_target_parity(text: str) -> str | None:
    """Advisory: Done should not out-run a declared AC `Verification target` above
    `functional` unless a story-level depth at/above it is recorded."""
    targets = [t.lower() for t in _TARGET_RE.findall(text) if t.lower() in _TIERS]
    if not targets:
        return None
    top = max(targets, key=lambda t: _TIERS[t])
    if _TIERS[top] <= _TIERS["functional"]:
        return None
    token = _depth_token(text)
    if token and _TIERS[token] >= _TIERS[top]:
        return None
    return (f"an AC declares Verification target `{top}` but the recorded depth is "
            f"`{token or 'unrecorded'}` - Done should not out-run the target")


def _iso_to_epoch(value) -> float | None:
    """Parse a `YYYY-MM-DDTHH:MM:SSZ` verify-report timestamp to a UTC epoch, or None."""
    if not value:
        return None
    from datetime import datetime, timezone
    try:
        return datetime.strptime(str(value), "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc).timestamp()
    except (ValueError, TypeError):
        return None


def _story_has_executable_acs(text: str) -> bool:
    """True if the story declares any non-manual `Verify:` line (an executable AC). A story
    with only `manual` ACs (or none) has nothing the deterministic gate can check."""
    for line in text.splitlines():
        m = sdlc_md.VERIFY_RE.match(line)
        if m and m.group(2).strip().split(None, 1)[0].lower() not in ("manual", "manually"):
            return True
    return False


def _done_verify_gate(root: Path, path: Path, text: str) -> str | None:
    """Definition-of-Done safety net on the hand-driven path. A story may not reach
    Done with executable ACs that are red or never run - the 0/7 a hand-driving agent shipped.
    Returns a block reason, or None to allow. Manual-only / AC-less stories are never blocked;
    a green report passes. The hard gate is the one deterministic fact - the verifier result;
    critic semantic findings stay advisory (handled elsewhere)."""
    if not _story_has_executable_acs(text):
        return None  # nothing executable to verify
    report_path = root / _REPORT_REL
    if not report_path.exists():
        return "this story declares executable ACs but they were never verified - run `verify_ac`"
    try:
        entry = (json.loads(report_path.read_text(encoding="utf-8")).get("stories", {}) or {}).get(path.stem)
    except (ValueError, OSError):
        entry = None
    if entry is None:
        return "this story is not in the verify-report - run `verify_ac` before Done"
    if entry.get("failed", 0) or entry.get("stale", 0):
        fails = ", ".join(f.get("ac", "?") for f in entry.get("failures", [])) or "stale AC(s)"
        return f"AC verification is red ({fails}) - fix or re-verify before Done"
    # A green entry can still be STALE: the story may have been edited since it was verified
    # (a changed Verify line, or a new AC). A merged report carries the old green forever, so
    # the entry alone is not proof the CURRENT story passes.
    verified_at = _iso_to_epoch(entry.get("verified_at"))
    try:
        story_mtime = path.stat().st_mtime
    except OSError:
        story_mtime = None
    if verified_at is not None and story_mtime is not None and story_mtime > verified_at + 2:
        return "this story was edited after it was last verified - re-run `verify_ac` before Done"
    reported_acs = entry.get("ac_count")
    if reported_acs is not None:
        try:
            import verify_ac  # sibling; imports only sdlc_md, no cycle
            current_acs = len(verify_ac.parse_story(text))
        except Exception:  # noqa: BLE001 - a parse hiccup must not mask the gate; skip this leg
            current_acs = None
        if current_acs is not None and current_acs != reported_acs:
            return (f"the story now has {current_acs} AC(s) but the verify-report covers "
                    f"{reported_acs} - re-run `verify_ac` before Done")
    return None


def _find(repo_root: Path, artifact_id: str):
    """(path, type) of the artifact with this id, or (None, None). Delegates to the shared
    alias-aware `sdlc_md.find_by_id`; normalises its None to the (None, None) this call site
    unpacks."""
    return sdlc_md.find_by_id(repo_root, artifact_id) or (None, None)


def _set_field(text: str, name: str, value: str) -> tuple[str, bool]:
    """Replace a `**Name:** value` field's value in place (blockquote or inline `·`
    form), preserving the surrounding format. Returns (new_text, changed)."""
    pat = re.compile(
        rf"((?:^>?\s*|·\s*)\*\*{re.escape(name)}:\*\*\s*)(.+?)(\s*(?=·|\s\*\*[^*\n]+:\*\*|$))",
        re.M)
    new_text, n = pat.subn(lambda m: m.group(1) + value + m.group(3), text, count=1)
    return new_text, n > 0


def _insert_after_status(text: str, line: str) -> str:
    """Insert `line` immediately after the `> **Status:**` metadata line (used to add a
    field that does not yet exist, e.g. a first-time `Triaged-by`). No-op if no Status line."""
    lines = text.splitlines(keepends=True)
    for i, ln in enumerate(lines):
        if re.match(r">?\s*\*\*Status:\*\*", ln):
            lines.insert(i + 1, line if line.endswith("\n") else line + "\n")
            return "".join(lines)
    return text


def _upsert_field(text: str, name: str, value: str) -> str:
    """Set `**Name:** value` in place, or insert it after Status when the field is absent."""
    new_text, changed = _set_field(text, name, value)
    return new_text if changed else _insert_after_status(text, f"> **{name}:** {value}")


def _triage_gate(root: Path, type_: str, text: str, from_canon: str | None,
                 target_canon: str | None, triaged_by: str | None) -> str | None:
    """Block reason when a v3 finding is leaving the `inbox` triage lane without a valid,
    separated `triaged_by`; None when the transition is not a triage or the gate is satisfied.
    Leaving `inbox` by ANY exit is the triage act (accept into the workflow, or reject the
    finding), so every such transition is gated - not only the canonical accept target - or an
    agent could sidestep triage by moving a finding straight to another state. Enforces CR0169
    (structured triaged_by, recorded at transition time) and CR0170 (separation of duties: the
    triager must not be the raiser). A solo human self-triage is not blocked (a lone operator
    must not deadlock) - it is left to the caller to warn, mirroring validate.py."""
    if not (type_ in sdlc_md.FINDING_TYPES and sdlc_md.is_schema_v3(root)):
        return None
    if from_canon != sdlc_md.INBOX_STATUS:  # only transitions leaving the inbox lane are triage
        return None
    raw = triaged_by or sdlc_md.extract_field(text, "Triaged-by")
    tb = sdlc_md.parse_authorship_value(raw)
    if not tb or not tb["name"]:
        return ('triage requires a structured `--triaged-by "Name; type; version"` '
                "(type is human|persona|agent) - the triaging seat must be recorded")
    if tb["type"] not in ("human", "persona", "agent"):
        return f"triaged_by type {tb['type']!r} must be one of human|persona|agent"
    raiser = sdlc_md.parse_authorship(text, "Raised-by")
    if raiser and raiser["name"]:
        same = (sdlc_md.norm_id(raiser["name"]) == sdlc_md.norm_id(tb["name"])
                and raiser["type"] == tb["type"])
        if same and tb["type"] != "human":
            return (f"triaged_by {tb['name']!r} is the raiser - a different seat must triage "
                    "(separation of duties, CR0170)")
    return None


def _cascade_epic(repo_root: Path, story_id: str, ticked: bool) -> str | None:
    """Tick/untick the story's line in its parent epic's Story Breakdown (called only on
    a real write). Returns the epic id touched, or None."""
    spath, _ = _find(repo_root, story_id)
    if spath is None:
        return None
    epic_field = sdlc_md.extract_field(spath.read_text(encoding="utf-8"), "Epic") or ""
    m = sdlc_md.ID_SEARCH_RE.search(epic_field)
    if not m:
        return None
    epath, _ = _find(repo_root, m.group(0))
    if epath is None:
        return None
    norm = sdlc_md.norm_id(story_id)
    lines = epath.read_text(encoding="utf-8").splitlines()
    changed = False
    box = "[x]" if ticked else "[ ]"
    for i, ln in enumerate(lines):
        s = ln.lstrip()
        if s.startswith(("- [ ]", "- [x]", "- [X]")) and sdlc_md.ID_SEARCH_RE.search(ln) \
                and sdlc_md.norm_id(sdlc_md.ID_SEARCH_RE.search(ln).group(0)) == norm:
            new = re.sub(r"\[[ xX]\]", box, ln, count=1)
            if new != ln:
                lines[i] = new
                changed = True
            break
    if changed:
        epath.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return m.group(0) if changed else None


def transition(repo_root: Path | str, artifact_id: str, new_status: str,
               dry_run: bool = False, force: bool = False,
               metrics: dict | None = None, triaged_by: str | None = None,
               triage_severity: str | None = None) -> dict:
    """Set `artifact_id`'s status to `new_status`, sync its index, and cascade the epic
    breakdown for a story. Returns {id, type, from, to, index_synced, epic}.

    A story moving to Done is gated on its AC-verify result: red or never-run
    executable ACs block the transition unless `force=True`. Scoped to stories - CR/epic/bug
    closures are unaffected. Manual-only / AC-less stories are never blocked."""
    root = Path(repo_root)
    if re.match(r"^(RETRO|RV)-?\d+", artifact_id.strip(), re.IGNORECASE):
        raise ValueError(
            f"{artifact_id} is a meta-artifact (retro/review) outside the status "
            f"machinery by design - edit the file directly; there is no status to cascade")
    path, type_ = _find(root, artifact_id)
    if path is None:
        raise ValueError(f"no artifact found for id {artifact_id!r}")
    vocab = sdlc_md.status_vocab(type_, root)
    if sdlc_md.canonical_status(new_status, vocab) is None:
        raise ValueError(f"{new_status!r} is not a valid {type_} status ({', '.join(vocab)})")
    text = path.read_text(encoding="utf-8")
    gate_warn = None
    target_canon = sdlc_md.canonical_status(new_status, vocab)
    if type_ == "bug" and not force and not dry_run:
        block = _bug_depth_gate(text, target_canon)
        if block:
            raise ValueError(
                f"{artifact_id} -> {new_status} blocked: {block}. Override with --force.")
    if type_ == "story" and not dry_run and target_canon == "Done":
        parity = _story_target_parity(text)
        if parity:
            # advisory by default (existing projects unaffected); a project opts
            # into refusal via `quality.depth_parity_gate: true`. Read via the
            # gracefully-degrading project_override so a PyYAML-less machine gets the
            # gate decision, not a config-loading crash.
            if sdlc_md.project_override(root, "quality.depth_parity_gate", False) and not force:
                raise ValueError(
                    f"{artifact_id} -> Done blocked: {parity}. Override with --force.")
            gate_warn = f"depth-parity advisory: {parity}"
    if (type_ == "story" and not force and not dry_run
            and target_canon == "Done"):
        block = _done_verify_gate(root, path, text)
        if block:
            # the gate is hard by default; `quality.done_requires_verified: false`
            # downgrades it to advisory-warn (the project sets the policy in .config.yaml).
            # project_override degrades to the default without PyYAML, so the block message
            # is produced rather than a config RuntimeError.
            if sdlc_md.project_override(root, "quality.done_requires_verified", True):
                raise ValueError(f"{artifact_id} -> Done blocked: {block}. Override with --force.")
            verify_warn = f"AC-verify advisory (quality.done_requires_verified=false): {block}"
            gate_warn = f"{gate_warn}; {verify_warn}" if gate_warn else verify_warn
    current = sdlc_md.extract_field(text, "Status")
    from_canon = sdlc_md.canonical_status(current, vocab)
    triage_fields: dict[str, str] = {}
    # The triage gate fires on any exit from `inbox` for a v3 finding, dry-run included: an
    # honest preflight must surface the same refusal a real run would (never a false green).
    block = _triage_gate(root, type_, text, from_canon, target_canon, triaged_by)
    if block:
        raise ValueError(f"{artifact_id} -> {new_status} blocked: {block}.")
    # Plan-review gate (US0090): a story with spec-derived ACs cannot REACH implementation
    # without a recorded independent plan-review verdict. Fires on entry to any state that
    # implies the plan was built - In Progress, Review, or Done - so a direct Ready->Done
    # close cannot smuggle an unreviewed plan into the terminal state. Dry-run included
    # (honest preflight); a no-op on v2 or when the deterministic trigger is not tripped.
    # Not bypassed by --force - the sanctioned skip is the recorded override field, so a
    # skip is always auditable. Idempotent for a forward walk: once reviewed/overridden,
    # In Progress -> Review -> Done all pass.
    _IMPL_TARGETS = {"In Progress", "Review", "Done"}
    if type_ == "story" and target_canon in _IMPL_TARGETS and from_canon not in _IMPL_TARGETS:
        import plan_review  # local import: plan_review pulls route/critic; keep them off cold paths
        pr_res = plan_review.gate(root, artifact_id, path)
        if not pr_res["ok"]:
            raise ValueError(f"{artifact_id} -> {new_status} blocked: {pr_res['reason']}.")
    if (not dry_run and type_ in sdlc_md.FINDING_TYPES and sdlc_md.is_schema_v3(root)
            and from_canon == sdlc_md.INBOX_STATUS):
        # A satisfied triage transition records the triaging seat (and, when given, the
        # triager's severity) at the moment of transition, alongside the raiser's Severity.
        raw_tb = triaged_by or sdlc_md.extract_field(text, "Triaged-by")
        if raw_tb:
            triage_fields["Triaged-by"] = raw_tb
        tb = sdlc_md.parse_authorship_value(raw_tb)
        raiser = sdlc_md.parse_authorship(text, "Raised-by")
        if (tb and raiser and raiser["name"] and tb["type"] == "human"
                and sdlc_md.norm_id(raiser["name"]) == sdlc_md.norm_id(tb["name"])):
            gate_warn = (f"{gate_warn}; solo-human self-triage: {tb['name']}"
                         if gate_warn else f"solo-human self-triage: {tb['name']}")
        if triage_severity:
            triage_fields["Triage-severity"] = triage_severity
    new_text, ok = _set_field(text, "Status", new_status)
    if not ok:
        raise ValueError(f"{path.name} has no `Status` field to transition")
    for fname, fval in triage_fields.items():
        new_text = _upsert_field(new_text, fname, fval)
    result = {"id": sdlc_md.extract_record_id(path.stem), "type": type_,
              "from": current, "to": new_status, "index_synced": False, "epic": None,
              "warning": gate_warn}
    if dry_run:
        return result
    path.write_text(new_text, encoding="utf-8")
    reconcile.apply_type(type_, root)  # sync the index row + counts
    # index_synced is the TRUTH after the sync, not "apply did something": an archived
    # row (apply only edits the live index) or a target status with no summary row both
    # leave residual drift, which we must report honestly rather than claim success.
    norm = sdlc_md.norm_id(result["id"])
    residual = [d for d in reconcile.detect_type(type_, root)["drift"]
                if (d.get("id") and sdlc_md.norm_id(d["id"]) == norm) or d["kind"] == "count-mismatch"]
    result["index_synced"] = not residual
    if residual:
        sync_warn = ("index not fully synced (the artifact may be archived, or its "
                     "new status has no summary row) - run reconcile")
        result["warning"] = f"{gate_warn}; {sync_warn}" if gate_warn else sync_warn
    if type_ == "story":
        result["epic"] = _cascade_epic(root, result["id"],
                                       sdlc_md.canonical_status(new_status, vocab) in _STORY_TICKED)
    from_canon = sdlc_md.canonical_status(current, vocab)
    to_canon = sdlc_md.canonical_status(new_status, vocab)
    if (to_canon in sdlc_md.terminal_statuses(type_)
            and from_canon not in sdlc_md.terminal_statuses(type_)):
        # record on ENTERING the terminal set only: Fixed -> Verified -> Closed is
        # one close (one event), an idempotent re-close is none, and a
        # reopen-then-reclose is honestly a second cycle
        import telemetry  # sibling; record() is best-effort and never raises
        telemetry.record(root, {"id": result["id"], "type": type_, **(metrics or {})})
        result["telemetry"] = True
    return result


def _print_result(res: dict, dry_run: bool) -> None:
    verb = "would set" if dry_run else "set"
    extra = f"; epic {res['epic']} breakdown updated" if res.get("epic") else ""
    print(f"{verb} {res['id']} {res['from']} -> {res['to']}"
          + ("" if dry_run else f" (index synced={res['index_synced']}{extra})"))
    if res.get("warning"):
        print(f"  warning: {res['warning']}")


def _num(v):
    """int when whole, float otherwise (fractional seconds are a natural unit);
    None only when absent or unparseable - a typo'd metric is dropped visibly by
    the telemetry record simply lacking the field."""
    if v is None:
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return int(f) if f == int(f) else f


def cmd_set(args: argparse.Namespace) -> int:
    if bool(args.id) == bool(args.ids):
        print("specify exactly one of --id or --ids", file=sys.stderr)
        return 2
    ids = [args.id] if args.id else [s.strip() for s in args.ids.split(",") if s.strip()]
    results = []
    refused = 0
    for aid in ids:
        try:
            metrics = {k: v for k, v in {"iterations": _num(args.iterations),
                                         "wall_time_s": _num(args.wall_time_s),
                                         "critic_verdict": args.verdict}.items() if v is not None}
            res = transition(args.root, aid, args.status, dry_run=args.dry_run,
                             force=args.force, metrics=metrics,
                             triaged_by=args.triaged_by, triage_severity=args.triage_severity)
            results.append(res)
            if args.format != "json":
                _print_result(res, args.dry_run)
        except (ValueError, FileNotFoundError) as exc:
            # one refusal never aborts the rest - each id is individually gated
            refused += 1
            results.append({"id": aid, "blocked": str(exc)})
            if args.format != "json":
                print(f"  blocked  {aid}: {exc}")
    if args.format == "json":
        print(json.dumps(results if args.ids else results[0], indent=2))
    if len(ids) > 1:
        out = sys.stderr if args.format == "json" else sys.stdout
        print(f"batch: {len(ids) - refused}/{len(ids)} transitioned, {refused} blocked", file=out)
    return 1 if refused else 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Transition an artifact's status + cascade.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("set", help="Set an artifact's status and sync index + epic breakdown.")
    s.add_argument("--id", help="Artifact id, e.g. CR0042 / US0023")
    s.add_argument("--ids", help="comma-separated ids for a same-target batch; each is "
                                 "individually gated and one refusal never aborts the rest")
    s.add_argument("--status", required=True, help="New status (must be in the type vocabulary)")
    s.add_argument("--root", default=".")
    s.add_argument("--iterations", help="run metric passed to the terminal-close telemetry event")
    s.add_argument("--wall-time-s", dest="wall_time_s", help="run metric for the telemetry event")
    s.add_argument("--verdict", help="critic verdict recorded on the telemetry event")
    s.add_argument("--force", action="store_true",
                   help="bypass the story->Done AC-verify gate; recorded as an override")
    s.add_argument("--triaged-by", dest="triaged_by",
                   help="v3 triage: the triaging seat as `Name; type; version` (type is "
                        "human|persona|agent); required and recorded on an inbox->triaged "
                        "transition, must differ from the raiser (separation of duties)")
    s.add_argument("--triage-severity", dest="triage_severity",
                   help="v3 triage: the triager's severity, recorded alongside the raiser's")
    s.add_argument("--dry-run", action="store_true")
    s.add_argument("--format", choices=("text", "json"), default="text")
    s.set_defaults(func=cmd_set)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001 - top-level guard
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
