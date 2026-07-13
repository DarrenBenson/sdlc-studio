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
    "disclosure": _disclosure,
    "doc-freshness": _doc_freshness,
    "mutation": _mutation,
    "hook-enabled": _hook_enabled,
}


def _retro_present(root: str, retro_id: str) -> dict:
    """Blocking close-gate check: the batch's retro file must exist before a sprint/review
    close reports success. Fail-loud per LL0008 - 'unconditional' retro is doctrine until it is
    a gate. The sprint-close orchestration passes the next retro id via --require-retro."""
    retros = Path(root) / "sdlc-studio" / "retros"
    present = bool(list(retros.glob(f"{retro_id}*.md"))) if retros.is_dir() else False
    return {"count": 0 if present else 1, "blocking": True,
            "detail": (f"batch retro {retro_id} present" if present
                       else f"missing batch retro {retro_id} - write it before closing the sprint")}


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
    * NOTHING TO PROVE IS NOT PROOF, at either level: an empty story set fails (a wrong --root,
      a moved directory), and so does a story set with zero executable verifiers - otherwise
      DELETING a rotted `Verify:` line would be the way to turn the release gate green.
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
    acs = manual = 0
    for path in stories:
        report = verify_ac.verify_story(path, dry_run=True, timeout=timeout, repo_root=rr,
                                        jest_cache=jest_cache, allow_external=allow_external)
        story_id = sdlc_md.extract_record_id(path.stem) or path.stem
        acs += report.ac_count
        manual += report.manual
        for f in report.failures:
            name = f"{story_id}::{f['ac']} ({f['verifier']})"
            (blocked if f.get("kind") == "blocked" else red).append(name)
    executable = acs - manual
    if not executable:
        return {"count": 1, "blocking": True,
                "detail": f"no executable Verify: expression across {len(stories)} "
                          f"story/stories ({acs} AC(s), {manual} manual) - the verify lane "
                          f"proved nothing about the AC layer; author a Verify: line per AC"}
    if not red and not blocked:
        return {"count": 0, "blocking": True,
                "detail": f"{executable}/{acs} executable AC(s) green across "
                          f"{len(stories)} story/stories ({manual} manual)"}
    parts = []
    if red:
        parts.append(f"{len(red)} red AC(s): {_elide(red)}")
    if blocked:
        parts.append(f"{len(blocked)} unproven AC(s) - verifier BLOCKED unrun by the "
                     f"trust boundary (story stamped Provenance: external): {_elide(blocked)}; "
                     f"pass --allow-external to run them once you trust the content")
    return {"count": len(red) + len(blocked), "blocking": True, "detail": "; ".join(parts)}


def run_gate(root: str = ".", only: list[str] | None = None,
             skip: list[str] | None = None, checks: dict | None = None,
             require_retro: str | None = None, release: bool = False,
             allow_external: bool = False, verify_batch: bool = False) -> dict:
    """Run the selected checks and report. `ok` is False only when a BLOCKING check
    fails; a non-blocking failure is reported but does not fail the gate. `require_retro`
    adds a blocking close-gate check that the named batch retro exists (the sprint close).
    `release` adds the blocking `verify` lane - the pre-tag gate is then ONE command with
    ONE exit code, not a gate plus a separate verify run whose exit code can be dropped;
    deselecting that lane under `release` is refused, not honoured (see below)."""
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
    if require_retro:  # close-gate: bind the expected retro id into a blocking check
        registry["retro"] = lambda r, _rid=require_retro: _retro_present(r, _rid)
    if release:  # pre-tag: the executing AC-verify lane joins the standard gate
        registry["verify"] = (lambda r, _x=allow_external, _b=verify_batch:
                              _verify_acs(r, allow_external=_x, batch=_b))
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
    # The verify lane is what MAKES this a release gate. Honouring a --skip/--only that
    # deselects it would print a release verdict over an unexamined AC layer - the
    # passing-looking command the release mode exists to abolish. Refuse instead: a caller
    # who does not want the AC layer examined wants the standard gate, and should say so.
    if release and "verify" not in selected:
        return {"ok": False, "checks": [{
            "check": "selection", "count": 1, "blocking": True, "status": "fail",
            "detail": "--release with the `verify` lane deselected proves nothing about the "
                      "AC layer - a release verdict will not be printed over it. Drop the "
                      "--skip/--only that excludes `verify`, or drop --release and run the "
                      "standard gate"}]}
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
                      verify_batch=getattr(args, "verify_batch", False))
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
                   help="Close-gate: fail unless this batch retro exists in sdlc-studio/retros/")
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
