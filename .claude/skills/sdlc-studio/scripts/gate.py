#!/usr/bin/env python3
"""Portable, ecosystem-neutral CI quality gate.

One command that runs the deterministic checks (conformance, reconcile drift, validate,
constitution, integrity) over the artifact graph, prints a consolidated pass/fail, and
exits non-zero only when a *blocking* check fails. No network, no CI/cloud assumption -
runnable as a bare shell step in any CI (GitHub Actions, GitLab, Jenkins, a pre-commit
hook). `--only` / `--skip` select checks. `--release` is the pre-tag form: the same gate plus
an EXECUTING acceptance-criteria verify pass, as one exit code.

Each check is a callable `fn(root) -> {"count": int, "blocking": bool, "detail": str}`;
the registry is injectable so the aggregation logic is testable without a full repo.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402


def _conformance(root: str) -> dict:
    import conformance
    result = conformance.detect_conformance(root)
    n = result["summary"]["nonconformant"]
    # Name the remedies inline (the adopt_after cutoff + the verify_ac backfill) and flag
    # whether the shape reads as pre-existing forward-only debt vs a fresh regression, so a
    # grown-but-accepted count does not read as a new breakage.
    return {"count": n, "blocking": True, "detail": conformance.remedy_detail(result)}


def _reconcile(root: str) -> dict:
    import reconcile
    rr = Path(root).resolve()
    # detect_type returns a dict; the drift items live under "drift" (not len(dict)).
    total = sum(len(reconcile.detect_type(t, rr)["drift"]) for t in reconcile.DEFAULT_TYPES)
    return {"count": total, "blocking": True, "detail": f"{total} drift item(s)"}


def _index_derived(root: str) -> dict:
    import reconcile
    issues = reconcile.index_derived_issues(Path(root).resolve())
    return {"count": len(issues), "blocking": True,
            "detail": "; ".join(issues) if issues else "indexes are derived output"}


def _validate(root: str) -> dict:
    import validate
    rr = Path(root).resolve()
    errors = 0
    for type_ in sdlc_md.ARTIFACT_TYPES:
        for path in sdlc_md.artifact_files(type_, rr):
            errors += sum(1 for v in validate.validate_file(path, type_, rr)
                          if v["severity"] == "error")
    return {"count": errors, "blocking": True, "detail": f"{errors} validation error(s)"}


def _constitution(root: str) -> dict:
    import constitution
    rep = constitution.check_constitution(root)
    v = len(rep["violations"])
    # Only blocking when the project opts in (constitution.enforce: true).
    return {"count": v, "blocking": bool(rep["enforced"]),
            "detail": (f"{v} violation(s)" + ("" if rep["enforced"] else " (advisory)"))
            if rep["exists"] else "no constitution"}


def _integrity(root: str) -> dict:
    import integrity
    e = integrity.detect_integrity(root)["summary"]["errors"]
    return {"count": e, "blocking": True, "detail": f"{e} integrity error(s)"}


def _duplicate_id(root: str) -> dict:
    import next_id
    import reconcile
    files = next_id.detect_collisions(root)["count"]      # two files claim one id
    rows = reconcile.detect_duplicate_rows(root)["count"]  # one index lists an id twice
    total = files + rows
    detail = f"{total} duplicate id(s)" + (f" ({files} file, {rows} index-row)" if total else "")
    return {"count": total, "blocking": True, "detail": detail}


def _provenance(root: str) -> dict:
    import provenance
    r = provenance.check(root)  # blocking only when provenance.enforce (the constitution pattern)
    n = len(r["findings"])
    return {"count": n, "blocking": r["enforced"],
            "detail": f"{n} unstamped artifact(s) ({'enforced' if r['enforced'] else 'advisory'})"}


def _disclosure(root: str) -> dict:
    import disclosure
    r = disclosure.check(root)
    n = len(r["findings"])
    detail = "N/A (not the skill repo)" if not r["applicable"] else f"{n} advisory finding(s)"
    return {"count": n, "blocking": False, "detail": detail}  # advisory: never blocks


def _doc_freshness(root: str) -> dict:
    import doc_freshness
    r = doc_freshness.check(root)
    n = len(r["findings"])
    detail = "N/A (not the skill repo)" if not r["applicable"] else (
        f"{n} stale LATEST.md claim(s)" if n else "LATEST.md fresh")
    return {"count": n, "blocking": False, "detail": detail}  # advisory: never blocks


def _doc_coverage(root: str) -> dict:
    import doc_coverage
    r = doc_coverage.check(root)
    blocking = sum(1 for f in r["findings"] if f["blocking"])
    advisory = len(r["findings"]) - blocking
    detail = ("N/A (not the skill repo)" if not r["applicable"]
              else f"{blocking} undocumented" + (f" (+{advisory} advisory)" if advisory else ""))
    return {"count": blocking, "blocking": True, "detail": detail}


def _engagement_floor(root: str) -> dict:
    """Blocking standard-gate lane: no shipped multi-file unit may reach a done outcome with no
    planning artefact (an AC, a Verify line, or a linked plan). Deterministic - a source-file
    count (declared Affects UNION the git cross-check) and a presence check, no model judgement.

    Advisory, never blocking, when the project sets `engagement_floor: judgement` - the documented
    project-global opt-out. A per-unit or project waiver, or the `adopt_after` cutoff, are the
    other auditable ways past; a plain --skip deselects the lane visibly, it does not pass it.
    """
    import engagement_floor
    result = engagement_floor.detect(root)
    s = result["summary"]
    # A forward cutoff (adopt_after above the highest existing id) silently disarms the whole
    # floor - it must FAIL loudly, even in judgement mode, because it is a config error, not the
    # sanctioned opt-out (that is judgement mode, which stays visible).
    if s["cutoff_forward"]:
        return {"count": 1, "blocking": True, "detail": engagement_floor.remedy_detail(result)}
    blocking = result["mode"] != "judgement"
    return {"count": s["violations"], "blocking": blocking,
            "detail": engagement_floor.remedy_detail(result)}


def _mutation(root: str) -> dict:
    """Advisory v1 lane: surface the mutation-check report's survivors. An absent
    report reads NOT-RUN (advisory) - never PASS: silence is not assertion integrity."""
    report_path = Path(root) / "sdlc-studio" / ".local" / "mutation-report.json"
    if not report_path.exists():
        return {"count": 1, "blocking": False,
                "detail": "mutation gate not run (no mutation-report.json) - advisory; "
                          "run scripts/mutation.py over the changed surface"}
    try:
        data = json.loads(report_path.read_text(encoding="utf-8"))
        s = data.get("summary", {})
    except (ValueError, OSError) as exc:
        return {"count": 1, "blocking": False, "detail": f"mutation-report unreadable: {exc}"}
    # staleness: a report from another rev is about some other change - it must
    # not render this diff's lane as PASS
    report_rev = data.get("git_rev")
    if report_rev:
        try:
            import subprocess
            head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root,
                                  capture_output=True, text=True, timeout=10).stdout.strip()
        except Exception:  # noqa: BLE001 - staleness must not break the gate (Exception covers OSError)
            head = None
        if head and head != report_rev:
            return {"count": 1, "blocking": False,
                    "detail": f"mutation-report is STALE (run at {report_rev[:9]}, tree at "
                              f"{head[:9]}) - re-run scripts/mutation.py (advisory)"}
    # content-hash staleness: same rev but an edited/missing target is still
    # evidence about code that no longer exists (the dirty-tree pre-commit flow)
    hashes = data.get("target_hashes") or {}
    if hashes:
        import hashlib
        for fp, recorded in hashes.items():
            fpath = Path(fp) if Path(fp).is_absolute() else Path(root) / fp
            try:
                current = hashlib.sha256(fpath.read_bytes()).hexdigest()
            except OSError:
                current = None
            if current != recorded:
                return {"count": 1, "blocking": False,
                        "detail": f"mutation-report is STALE ({Path(fp).name} changed since "
                                  f"the run) - re-run scripts/mutation.py (advisory)"}
    n = int(s.get("survived", 0)) + int(s.get("errors", 0))
    detail = (f"{s.get('survived', 0)} survived, {s.get('errors', 0)} error(s) of "
              f"{s.get('applied', 0)} applied ({s.get('truncated', 0)} truncated) - advisory"
              if n else
              f"{s.get('killed', 0)}/{s.get('applied', 0)} mutations killed "
              f"({s.get('truncated', 0)} truncated) (advisory)")
    # a truncated green lane must state its coverage: 12/12 killed reads as
    # whole-surface assurance when it sampled under 1% of the enumerable sites
    applied, enumerated = int(s.get("applied", 0)), int(s.get("enumerated", 0))
    if int(s.get("truncated", 0)) and enumerated:
        pct = f"{100.0 * applied / enumerated:.1f}%"
        detail += f" - {applied}/{enumerated} enumerated sampled ({pct})"
    return {"count": n, "blocking": False, "detail": detail}


# Lanes that read NOT-RUN (advisory) when their evidence file is absent. The
# upgrade capability digest names these when they arrive in a version gap, so
# a new integrity check cannot land silently as a benign-looking warn - a
# registry test asserts every advisory-when-absent lane is declared here.
ADVISORY_WHEN_ABSENT = {
    "mutation": {
        "since": "3.4.0",
        "baseline": ("run scripts/mutation.py over your changed surface to "
                     "create sdlc-studio/.local/mutation-report.json"),
    },
}

def hook_enablement_gap(root) -> str | None:
    """The one-line warning when a tree SHIPS a tracked pre-commit gate that this clone has
    not enabled - or None when there is nothing to say. Fires only where it means something:
    a git work tree containing `.githooks/pre-commit` (never a consuming project, which has
    no .githooks; never a non-git directory). Shared by the gate lane and the status
    dashboard so the two surfaces cannot drift."""
    import os
    import subprocess
    hook = Path(root) / ".githooks" / "pre-commit"
    if not hook.is_file():
        return None
    # Scrub repo-redirecting env: gate/status may run from inside ANOTHER repo's hook, and an
    # inherited GIT_DIR/GIT_WORK_TREE would silently make git answer for that repo, not root.
    env = {k: v for k, v in os.environ.items()
           if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")}
    try:
        inside = subprocess.run(["git", "-C", str(root), "rev-parse", "--is-inside-work-tree"],
                                capture_output=True, text=True, timeout=10, env=env)
        if inside.returncode != 0 or inside.stdout.strip() != "true":
            return None
        cfg = subprocess.run(["git", "-C", str(root), "config", "core.hooksPath"],
                             capture_output=True, text=True, timeout=10, env=env)
    except (OSError, subprocess.SubprocessError):
        return None  # git unavailable: nothing checkable, never a false alarm
    val = cfg.stdout.strip() if cfg.returncode == 0 else ""
    if val:
        # Equivalent enabled spellings must read enabled: ".githooks", ".githooks/", or an
        # absolute path to the same directory - git runs the hook under all of them.
        if val.rstrip("/") == ".githooks":
            return None
        try:
            if (Path(val).is_absolute()
                    and Path(val).resolve() == (Path(root) / ".githooks").resolve()):
                return None
        except OSError:
            pass
    return ("tracked .githooks/pre-commit is NOT enabled in this clone (core.hooksPath "
            "unset or elsewhere) - the commit gate is not running; fix: bash tools/enable-hooks.sh")


def _hook_enabled(root: str) -> dict:
    gap = hook_enablement_gap(root)
    return {"count": 0 if gap is None else 1, "blocking": False,
            "detail": gap or "hook enabled (or no tracked hook in this tree)"}


# Lanes whose FAILURES block must also block when they CRASH: a raised exception in
# (say) validate or reconcile means the gate proved nothing about that lane, and a
# green gate over an unproven blocking lane is the false-assurance class (LL0008).
# Custom/injected checks not declared here stay contained (advisory-on-error), so one
# buggy experimental check cannot brick the gate.
BLOCKING_ON_ERROR = {
    "conformance", "reconcile", "index-derived", "validate",
    "integrity", "duplicate-id", "doc-coverage", "retro", "verify",
    "lessons-summary", "lessons-validity", "handoff", "review-legs",
    "engagement-floor", "review-current",
}

DEFAULT_CHECKS = {
    "conformance": _conformance,
    "reconcile": _reconcile,
    "index-derived": _index_derived,
    "validate": _validate,
    "constitution": _constitution,
    "integrity": _integrity,
    "duplicate-id": _duplicate_id,
    "provenance": _provenance,
    "doc-coverage": _doc_coverage,
    "engagement-floor": _engagement_floor,
    "disclosure": _disclosure,
    "doc-freshness": _doc_freshness,
    "mutation": _mutation,
    "hook-enabled": _hook_enabled,
}


def _retro_present(root: str, retro_id: str) -> dict:
    """Blocking close-gate check: the batch's retro must exist AND say something before a
    sprint/review close reports success. Fail-loud per LL0008 - 'unconditional' retro is
    doctrine until it is a gate. The sprint-close orchestration passes the next retro id
    via --require-retro.

    This leg used to glob for a filename, so a 0-byte file named RETRO9999.md passed it:
    the one gate that made the retrospective un-skippable was the one an agent could
    satisfy with `touch`. Existence is not evidence - so the check is now
    delegated to `retro.py validate`, which interrogates the CONTENT: the required
    sections, at least one real lesson, and a disposition for every finding.
    """
    import config
    import retro
    # The documented opt-out (`lessons.loop: judgement`), mirroring the engagement floor: the
    # lane still REPORTS, it just does not block. An opt-out that is documented but unread
    # would be the very disease this loop exists to cure.
    mode = str(config.get(root, "lessons.loop", "enforce") or "enforce").strip().lower()
    blocking = mode != "judgement"
    res = retro.validate(root, retro_id)
    if res["ok"]:
        n_l, n_f = len(res["lessons"]), len(res["findings"])
        return {"count": 0, "blocking": blocking,
                "detail": (f"batch retro {retro_id}: {n_l} lesson(s), {n_f} finding(s) all "
                           f"dispositioned ({len(res['filed'])} filed, "
                           f"{len(res['declined'])} declined)")}
    # Every error names its own remedy; surface them all rather than only the first, so one
    # close tells you everything it wants instead of a queue of one-at-a-time refusals.
    suffix = "" if blocking else " (advisory: lessons.loop is judgement)"
    return {"count": len(res["errors"]), "blocking": blocking,
            "detail": f"batch retro {retro_id} incomplete{suffix} - " + "; ".join(res["errors"])}


def _review_current(root: str) -> dict:
    """Blocking close-gate check: the unified-review anchor (reviews/LATEST.md) must be at least
    as new as every artefact. If any artefact changed since the last review, LATEST.md is stale
    and a fresh session orients on an out-of-date claim.

    The sprint close is reconcile + review + retro. Reconcile blocks on drift and retro is a
    hard gate; this is the review leg, which was only advisory before (doc_freshness) - so a
    stale review reached a close, and did. Presence is not currency: the review-legs lane checks
    the doc legs EXIST; this checks the review was actually re-RUN. The estimate machinery is
    reused from review_prep (git commit time, mtime fallback).
    """
    import review_prep
    rr = Path(root)
    latest = rr / "sdlc-studio" / "reviews" / "LATEST.md"
    if not latest.is_file():
        return {"count": 1, "blocking": True,
                "detail": "no reviews/LATEST.md - run `review` before closing the sprint"}
    latest_dt = review_prep._parse_dt(review_prep._modified_iso(latest, rr)[0])
    stale = []
    for key, rec in review_prep.staleness(rr).items():
        m = review_prep._parse_dt(rec.get("last_modified"))
        if m and latest_dt and m > latest_dt:
            stale.append(key)
    if stale:
        return {"count": len(stale), "blocking": True,
                "detail": (f"reviews/LATEST.md is stale - {len(stale)} artefact(s) changed since "
                           f"the last review ({_elide(sorted(stale))}); run `review` before closing")}
    return {"count": 0, "blocking": True, "detail": "reviews/LATEST.md is current with all artefacts"}


def _handoff_present(root: str, handoff_id: str) -> dict:
    """Blocking close-gate check: a run that stopped short of its goal must leave the
    handoff, and a retro must LINK it.

    Both halves are the check. A handoff nobody links is a document nobody opens - the
    person picking the work up reads the retro, and the retro is where the pointer belongs.
    Presence alone would let the gate certify a handoff that is, in practice, invisible.
    """
    rr = Path(root)
    stem = str(handoff_id).replace("-", "").upper()
    d = rr / "sdlc-studio" / "handoffs"
    hits = sorted(d.glob(f"{stem}*.md")) if d.is_dir() else []
    if not hits:
        return {"count": 1, "blocking": True,
                "detail": f"missing handoff {handoff_id} - a run that stopped short of its "
                          f"goal owes one (`handoff generate --outcome <how it ended>`)"}
    retros = rr / "sdlc-studio" / "retros"
    disp = f"{stem[:2]}-{stem[2:]}" if stem.startswith("HO") else stem
    # A LINK, not a mention. A substring scan for the id passes on a retro whose prose
    # DENIES the handoff exists ("we never wrote HO-0001") - it would certify the very
    # absence it is meant to catch. The check is the markdown link shape the writer emits
    # and a reader can actually follow: a link whose target is the handoff file.
    import re
    link_re = re.compile(rf"\[[^\]]*\]\([^)]*{re.escape(stem)}[^)]*\.md\)", re.IGNORECASE)
    linked = [p.name for p in (sorted(retros.glob("RETRO*.md")) if retros.is_dir() else [])
              if link_re.search(p.read_text(encoding="utf-8"))]
    if not linked:
        return {"count": 1, "blocking": True,
                "detail": f"handoff {disp} exists but no retro links it (a markdown link to "
                          f"the handoff file - a bare mention of the id is not a link a "
                          f"reader can follow) - regenerate with `handoff generate --retro "
                          f"RETROxxxx`, so the person picking the work up finds it from the "
                          f"retro they read"}
    return {"count": 0, "blocking": True,
            "detail": f"handoff {disp} present, linked from {', '.join(linked)}"}


def _lessons_summary(root: str) -> dict:
    """Blocking close-gate lane: the committed LESSONS-SUMMARY.md must be the digest of the
    CURRENT lessons log. Summarising the sprint's lessons was doctrine - prose four steps long,
    of which only the retro was enforced - so an agent under effort pressure skipped it and the
    next sprint read a summary that predated the last one's learning.

    The verdict is recomputed, never trusted: `lessons.summary_status` regenerates the digest
    from the log and compares it with what the file says, so a lesson CLOSED since the last
    regeneration fails it exactly as an added one does. Nothing is stamped, so there is nothing
    to forge; the only way to green is for the file to say what the log implies.
    """
    import lessons
    status = lessons.summary_status(root)
    if not status["applicable"]:
        return {"count": 0, "blocking": True, "detail": status["reason"]}
    if not status["stale"]:
        return {"count": 0, "blocking": True, "detail": status["reason"]}
    n = len(status["added"]) + len(status["removed"]) or 1
    return {"count": n, "blocking": True, "detail": status["reason"]}


def _lessons_validity(root: str) -> dict:
    """Blocking close-gate lane: no open lesson may sit past its validity horizon unclosed and
    unextended, and none may carry no horizon at all. The re-validation step, made mechanical.

    An unstamped lesson counts. A lane that reported only EXPIRED entries would pass every
    legacy log vacuously - a check that catches only the total case is not a check.
    """
    import lessons
    status = lessons.validity_status(root)
    if not status["applicable"]:
        return {"count": 0, "blocking": True, "detail": status["reason"]}
    n = len(status["expired"]) + len(status["unstamped"])
    return {"count": n, "blocking": True, "detail": status["reason"]}


# The close-gate lanes, bound as one set: the sprint close is a single obligation (write the
# retro, re-validate the lessons, regenerate the digest the next sprint reads), so the command
# the doctrine already prescribes - `gate --require-retro RETROxxxx` - carries all of it. A
# separate flag per step is a step an agent under effort pressure forgets.
LESSONS_CLOSE_CHECKS = {
    "lessons-summary": _lessons_summary,
    "lessons-validity": _lessons_validity,
}


VERIFY_TIMEOUT = 120  # per-verifier seconds; matches the verify_ac default
_MAX_NAMED = 10       # failing ACs listed by name before the detail is elided


def _elide(names: list[str]) -> str:
    """`a, b, c (+2 more)` - name the failures, bound the line."""
    more = f" (+{len(names) - _MAX_NAMED} more)" if len(names) > _MAX_NAMED else ""
    return ", ".join(names[:_MAX_NAMED]) + more


def _verify_acs(root: str, timeout: int = VERIFY_TIMEOUT, allow_external: bool = False,
                batch: bool = False) -> dict:
    """Blocking release-gate lane: EXECUTE every story's `Verify:` expression now, and fail
    on any AC that is red OR unproven, naming each one.

    Properties this lane must hold at once, and how it holds them:

    * It EXECUTES rather than reading the stored verify-report. A merged report carries a
      story's last green forward until something re-runs it, so a rotted verifier keeps
      reading PASS - the stale green that reaches a tag. Silence is not assertion integrity.
    * It does NOT write. `verify_ac run` in its normal mode rewrites each AC's
      `- **Verified:**` back-annotation and overwrites `.local/verify-report.json`; the gate
      is read-only (a pre-commit hook runs it), and a gate that edits tracked files while
      judging them is not a gate. So the lane calls `verify_story(dry_run=True)` per story:
      the verifiers run for real, nothing is written back, and the verdict is this run's.
    * A verifier the trust boundary REFUSED TO RUN is reported as BLOCKED, never as red. On a
      story stamped `Provenance: external`, a shell-backed verb is not executed (see
      `verify_ac`), so its result is not evidence about the code: reporting it as a failing AC
      sends the operator to debug a verifier that works. It still fails the lane - unproven is
      not proof - and `allow_external` is the deliberate way to run it and reach a green.
    * NOTHING TO PROVE IS NOT PROOF, and the guard is PER-STORY, not repo-wide. An empty story
      set fails (a wrong --root, a moved directory). A story with an UNSPECIFIED AC - one
      carrying no `Verify:` line at all - fails and is NAMED, because an omitted verifier is
      not a passed one. This is per-story on purpose: a repo-wide "some executable verifier
      exists" test let one green AC anywhere carry every verifier-less story along, so DELETING
      a rotted `Verify:` line reached a green gate. A story whose ACs are ALL declared
      `Verify: manual` is honestly declaring human verification and PASSES - the guard fires on
      omission, never on a declared judgement call.
    """
    import verify_ac
    rr = Path(root).resolve()
    stories = list(verify_ac.walk_stories(rr / "sdlc-studio" / "stories"))
    if not stories:
        return {"count": 1, "blocking": True,
                "detail": "no stories under sdlc-studio/stories - the verify lane proved "
                          "nothing about the AC layer (wrong --root?)"}
    jest_cache = verify_ac.jest_batch_cache(rr, timeout) if batch else None
    red: list[str] = []
    blocked: list[str] = []
    unspecified: list[str] = []
    acs = manual = unspec = 0
    for path in stories:
        report = verify_ac.verify_story(path, dry_run=True, timeout=timeout, repo_root=rr,
                                        jest_cache=jest_cache, allow_external=allow_external)
        story_id = sdlc_md.extract_record_id(path.stem) or path.stem
        acs += report.ac_count
        manual += report.manual
        unspec += report.unspecified
        if report.unspecified:
            unspecified.append(f"{story_id} ({report.unspecified} AC(s) with no Verify: line)")
        for f in report.failures:
            name = f"{story_id}::{f['ac']} ({f['verifier']})"
            (blocked if f.get("kind") == "blocked" else red).append(name)
    executable = acs - manual - unspec
    parts = []
    if unspecified:
        parts.append(f"{len(unspecified)} story/stories with an unspecified AC (no Verify: line "
                     f"- an omitted verifier is not a passed one; author one or mark it "
                     f"`Verify: manual`): {_elide(unspecified)}")
    if red:
        parts.append(f"{len(red)} red AC(s): {_elide(red)}")
    if blocked:
        parts.append(f"{len(blocked)} unproven AC(s) - verifier BLOCKED unrun by the "
                     f"trust boundary (story stamped Provenance: external): {_elide(blocked)}; "
                     f"pass --allow-external to run them once you trust the content")
    if parts:
        return {"count": len(unspecified) + len(red) + len(blocked), "blocking": True,
                "detail": "; ".join(parts)}
    if acs == 0:
        return {"count": 1, "blocking": True,
                "detail": f"no acceptance criteria across {len(stories)} story/stories - the "
                          f"verify lane proved nothing about the AC layer (wrong --root?)"}
    return {"count": 0, "blocking": True,
            "detail": f"{executable}/{acs} executable AC(s) green across "
                      f"{len(stories)} story/stories ({manual} manual)"}


def _review_legs(root: str) -> dict:
    """Blocking release-gate lane: every required DOCUMENT leg (PRD/TRD/TSD/Persona) must be
    PRESENT or explicitly WAIVED against a recorded decision id. A required leg that is absent
    and unwaived FAILS - the review cannot reclassify a missing leg as 'optional' in prose,
    because a waiver is a decisions-log row (`decisions.py waive --leg <leg>`), not narrative.

    The CODE leg is out of scope: it has no single artefact whose presence can be tested, so this
    lane makes no claim about it (decision D0022) - it states that exclusion in every verdict, so a
    green lane is never misread as certifying the code leg too.
    """
    import review_prep
    legs = review_prep.required_legs(Path(root).resolve())
    absent = sorted(k for k, v in legs.items() if not v["present"] and not v["waiver"])
    waived = sorted(f"{k} ({v['waiver']})" for k, v in legs.items()
                    if not v["present"] and v["waiver"])
    if absent:
        detail = (f"{len(absent)} required leg(s) absent and unwaived: {', '.join(absent)} - "
                  f"add the artefact, or record a waiver (`decisions.py waive --leg <leg> "
                  f"--rationale ...`); CODE leg out of scope (D0022)")
    else:
        present = sorted(k for k, v in legs.items() if v["present"])
        detail = (f"{len(present)} required leg(s) present"
                  + (f"; waived: {', '.join(waived)}" if waived else "")
                  + " (CODE leg out of scope, D0022)")
    return {"count": len(absent), "blocking": True, "detail": detail}


# What each bound lane is FOR, named in the refusal so an operator who deselects one is
# told what the verdict would have been printed over. A lane with no entry falls back to
# the generic phrase.
BOUND_LANE_SUBJECT = {
    "verify": "the AC layer",
    "review-legs": "the required document legs (present or waived)",
    "retro": "the sprint close's learning loop",
    "lessons-summary": "the sprint close's learning loop",
    "lessons-validity": "the sprint close's learning loop",
    "handoff": "the remaining-work handoff",
    "review-current": "the sprint close's review currency",
}


def run_gate(root: str = ".", only: list[str] | None = None,
             skip: list[str] | None = None, checks: dict | None = None,
             require_retro: str | None = None, release: bool = False,
             allow_external: bool = False, verify_batch: bool = False,
             require_lessons: bool = False, require_handoff: str | None = None,
             require_review: bool = False) -> dict:
    """Run the selected checks and report. `ok` is False only when a BLOCKING check
    fails; a non-blocking failure is reported but does not fail the gate. `require_retro`
    is the SPRINT-CLOSE gate: it binds a blocking check that the named batch retro exists,
    plus the lessons lanes (`require_lessons` binds those alone) - the close's learning loop
    is one obligation, so one command carries it. `release` adds the blocking `verify` lane -
    the pre-tag gate is then ONE command with ONE exit code, not a gate plus a separate verify
    run whose exit code can be dropped. A BOUND lane cannot be deselected: a mode's verdict
    printed over the lane that defines it is the false-assurance class this gate exists to
    refuse."""
    # Guard against a vacuous PASS on a wrong/missing root (a CI step pointed at the wrong
    # dir, or a failed checkout). "No project found" must FAIL, not look all-green. Only
    # applies to real runs; injected check registries (logic tests) skip it.
    if checks is None:
        rr = Path(root)
        if not rr.exists() or not (rr / "sdlc-studio").is_dir():
            return {"ok": False, "checks": [{
                "check": "scope", "count": 0, "blocking": True, "status": "fail",
                "detail": f"no SDLC project under {root} (no sdlc-studio/ dir) - wrong --root?"}]}
    registry = dict(checks) if checks is not None else dict(DEFAULT_CHECKS)
    bound: list[str] = []  # lanes a mode bound in: deselecting one is refused, not honoured
    if require_retro:  # close-gate: bind the expected retro id into a blocking check
        registry["retro"] = lambda r, _rid=require_retro: _retro_present(r, _rid)
        bound.append("retro")
    if require_retro or require_lessons:  # ...and the rest of the close's learning loop
        registry.update(LESSONS_CLOSE_CHECKS)
        bound.extend(LESSONS_CLOSE_CHECKS)
    if require_handoff:  # a run that stopped short: the handoff must exist AND be linked
        registry["handoff"] = lambda r, _hid=require_handoff: _handoff_present(r, _hid)
        bound.append("handoff")
    if require_review:  # close-gate review leg: LATEST.md must be current with the artefacts
        registry["review-current"] = _review_current
        bound.append("review-current")
    if release:  # pre-tag: the executing AC-verify lane joins the standard gate...
        registry["verify"] = (lambda r, _x=allow_external, _b=verify_batch:
                              _verify_acs(r, allow_external=_x, batch=_b))
        bound.append("verify")
        # ...and every required document leg must be present or explicitly waived: a tag over a
        # silently-missing required artefact is the BG0110 hole this refuses to leave open.
        registry["review-legs"] = _review_legs
        bound.append("review-legs")
    # A wrong/typo'd --only/--skip (or a renamed check) must FAIL, not silently select
    # nothing and report a vacuous PASS - the false-assurance class LL0008 warns against.
    unknown = sorted({n for n in (list(only or []) + list(skip or [])) if n not in registry})
    if unknown:
        return {"ok": False, "checks": [{
            "check": "selection", "count": len(unknown), "blocking": True, "status": "fail",
            "detail": f"unknown check name(s): {', '.join(unknown)} - "
                      f"valid: {', '.join(sorted(registry))}"}]}
    selected = [n for n in registry
                if (not only or n in only) and (not skip or n not in skip)]
    if not selected:
        return {"ok": False, "checks": [{
            "check": "selection", "count": 0, "blocking": True, "status": "fail",
            "detail": "no checks selected - the gate proved nothing (check --only/--skip)"}]}
    # A bound lane is what MAKES the mode that bound it: `verify` a release gate, `retro` and
    # the lessons lanes a sprint close. Honouring a --skip/--only that deselects one would
    # print that mode's verdict over the very thing it claims to have examined - the
    # passing-looking command these modes exist to abolish. Refuse instead: a caller who does
    # not want the lane examined wants the standard gate, and should say so.
    dropped = [n for n in bound if n not in selected]
    if dropped:
        subjects = sorted({BOUND_LANE_SUBJECT.get(n, "what it claims to gate")
                           for n in dropped})
        what = " and ".join(subjects)
        return {"ok": False, "checks": [{
            "check": "selection", "count": len(dropped), "blocking": True, "status": "fail",
            "detail": f"deselecting the bound lane(s) {', '.join(dropped)} proves nothing "
                      f"about {what} - that verdict will not be printed over them. Drop the "
                      f"--skip/--only that excludes them, or drop the mode flag "
                      f"(--release/--require-retro/--require-lessons/--require-handoff) and "
                      f"run the standard gate"}]}
    results = []
    for name in selected:
        try:
            r = registry[name](root)
            results.append({"check": name, "count": r["count"], "blocking": r["blocking"],
                            "status": "pass" if r["count"] == 0 else "fail",
                            "detail": r.get("detail", "")})
        except Exception as exc:  # noqa: BLE001 - one buggy check must not abort the whole gate
            # A conventions shape error is the operator's config, not a buggy
            # check: it silently disables whichever lane read it (reconcile's
            # drift detection, most damagingly), so it must BLOCK - a green
            # gate over a disabled lane is the false assurance class.
            from lib.conventions import ConventionsError
            blocking = isinstance(exc, ConventionsError) or name in BLOCKING_ON_ERROR
            results.append({"check": name, "count": 1, "blocking": blocking, "status": "error",
                            "detail": f"check raised{'' if blocking else ', skipped'}: {exc}"})
    ok = all(r["status"] == "pass" for r in results if r["blocking"])
    return {"ok": ok, "checks": results}


def _split(v: str | None) -> list[str] | None:
    return [x.strip() for x in v.split(",") if x.strip()] if v else None


def cmd_gate(args: argparse.Namespace) -> int:
    release = getattr(args, "release", False)
    report = run_gate(args.root, only=_split(args.only), skip=_split(args.skip),
                      require_retro=getattr(args, "require_retro", None), release=release,
                      allow_external=getattr(args, "allow_external", False),
                      verify_batch=getattr(args, "verify_batch", False),
                      require_lessons=getattr(args, "require_lessons", False),
                      require_handoff=getattr(args, "require_handoff", None),
                      require_review=getattr(args, "require_review", False))
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        for c in report["checks"]:
            mark = "PASS" if c["status"] == "pass" else ("FAIL" if c["blocking"] else "warn")
            print(f"  [{mark}] {c['check']}: {c['detail']}")
        # The release banner is printed only when the release gate actually RAN - i.e. the
        # verify lane is in the results. Anything else prints the plain gate verdict, so a
        # deselected AC layer can never wear a release PASS.
        ran_release = release and any(c["check"] == "verify" for c in report["checks"])
        print(f"gate{' --release' if ran_release else ''}: "
              f"{'PASS' if report['ok'] else 'FAIL'}")
        if ran_release and report["ok"]:
            # A green mechanical gate is not the whole pre-tag ritual; say so, so a PASS here
            # is never read as the checklist's judgement items being done.
            print("  the checklist's judgement items remain: "
                  "templates/workflows/release-gate.md")
    return 0 if report["ok"] else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Portable CI quality gate.")
    p.add_argument("--root", default=".", help="Repo root (default: .)")
    p.add_argument("--only", help="Comma-separated checks to run (default: all)")
    p.add_argument("--skip", help="Comma-separated checks to skip")
    p.add_argument("--require-retro", metavar="RETROxxxx",
                   help="Sprint-close gate: fail unless this batch retro exists in "
                        "sdlc-studio/retros/, the committed LESSONS-SUMMARY.md is the digest of "
                        "the current lessons log, and every open lesson is inside its validity "
                        "horizon (it implies --require-lessons - the close is one obligation)")
    p.add_argument("--require-lessons", dest="require_lessons", action="store_true",
                   help="The lessons half of the close gate on its own: fail on a stale "
                        "LESSONS-SUMMARY.md (regenerate it with `lessons summary`) or on an open "
                        "lesson past its validity horizon (`lessons revalidate`)")
    p.add_argument("--require-handoff", dest="require_handoff", metavar="HOxxxx",
                   help="Run-close gate for a run that stopped SHORT of its goal: fail "
                        "unless this handoff exists in sdlc-studio/handoffs/ and a retro "
                        "links it (`handoff generate --outcome <how it ended> --retro "
                        "RETROxxxx`). Deselecting the `handoff` lane under it is refused")
    p.add_argument("--require-review", dest="require_review", action="store_true",
                   help="The review half of the sprint close: fail unless reviews/LATEST.md is at "
                        "least as new as every artefact (run `review` to refresh it). Currency, "
                        "not presence - a stale review anchor is a fresh session's first read")
    p.add_argument("--release", action="store_true",
                   help="Pre-tag gate: also EXECUTE every story's Verify: expression and fail "
                        "on any red or unproven AC (read-only - no Verified: back-annotation, "
                        "no report rewrite). One command, one exit code, before you tag. "
                        "Deselecting the `verify` lane under --release is refused")
    p.add_argument("--allow-external", dest="allow_external", action="store_true",
                   help="--release: run shell-backed verifiers on stories stamped "
                        "`Provenance: external` too (off by default - the trust boundary; "
                        "those verifiers are otherwise reported BLOCKED, never green)")
    p.add_argument("--verify-batch", dest="verify_batch", action="store_true",
                   help="--release: run jest once and resolve jest verifiers from the cached "
                        "result, instead of a cold start per AC")
    p.add_argument("--format", choices=("text", "json"), default="text")
    p.set_defaults(func=cmd_gate)
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
