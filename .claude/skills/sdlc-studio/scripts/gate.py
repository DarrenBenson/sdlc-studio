#!/usr/bin/env python3
"""Portable, ecosystem-neutral CI quality gate.

One command that runs the deterministic checks (conformance, reconcile drift, validate,
constitution, integrity) over the artifact graph, prints a consolidated pass/fail, and
exits non-zero only when a *blocking* check fails. No network, no CI/cloud assumption -
runnable as a bare shell step in any CI (GitHub Actions, GitLab, Jenkins, a pre-commit
hook). `--only` / `--skip` select checks.

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
    total = sum(len(reconcile.detect_type(t, rr)["drift"]) for t in reconcile._DEFAULT_TYPES)
    return {"count": total, "blocking": True, "detail": f"{total} drift item(s)"}


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
        except (OSError, Exception):  # noqa: BLE001 - staleness must not break the gate
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

DEFAULT_CHECKS = {
    "conformance": _conformance,
    "reconcile": _reconcile,
    "validate": _validate,
    "constitution": _constitution,
    "integrity": _integrity,
    "duplicate-id": _duplicate_id,
    "provenance": _provenance,
    "doc-coverage": _doc_coverage,
    "disclosure": _disclosure,
    "doc-freshness": _doc_freshness,
    "mutation": _mutation,
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


def run_gate(root: str = ".", only: list[str] | None = None,
             skip: list[str] | None = None, checks: dict | None = None,
             require_retro: str | None = None) -> dict:
    """Run the selected checks and report. `ok` is False only when a BLOCKING check
    fails; a non-blocking failure is reported but does not fail the gate. `require_retro`
    adds a blocking close-gate check that the named batch retro exists (the sprint close)."""
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
            blocking = isinstance(exc, ConventionsError)
            results.append({"check": name, "count": 1, "blocking": blocking, "status": "error",
                            "detail": f"check raised, skipped: {exc}"})
    ok = all(r["status"] == "pass" for r in results if r["blocking"])
    return {"ok": ok, "checks": results}


def _split(v: str | None) -> list[str] | None:
    return [x.strip() for x in v.split(",") if x.strip()] if v else None


def cmd_gate(args: argparse.Namespace) -> int:
    report = run_gate(args.root, only=_split(args.only), skip=_split(args.skip),
                      require_retro=getattr(args, "require_retro", None))
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        for c in report["checks"]:
            mark = "PASS" if c["status"] == "pass" else ("FAIL" if c["blocking"] else "warn")
            print(f"  [{mark}] {c['check']}: {c['detail']}")
        print(f"gate: {'PASS' if report['ok'] else 'FAIL'}")
    return 0 if report["ok"] else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Portable CI quality gate.")
    p.add_argument("--root", default=".", help="Repo root (default: .)")
    p.add_argument("--only", help="Comma-separated checks to run (default: all)")
    p.add_argument("--skip", help="Comma-separated checks to skip")
    p.add_argument("--require-retro", metavar="RETROxxxx",
                   help="Close-gate: fail unless this batch retro exists in sdlc-studio/retros/")
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
