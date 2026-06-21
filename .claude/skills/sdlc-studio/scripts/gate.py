#!/usr/bin/env python3
"""Portable, ecosystem-neutral CI quality gate (CR0046).

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
    n = conformance.detect_conformance(root)["summary"]["nonconformant"]
    return {"count": n, "blocking": True, "detail": f"{n} non-conformant unit(s)"}


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


DEFAULT_CHECKS = {
    "conformance": _conformance,
    "reconcile": _reconcile,
    "validate": _validate,
    "constitution": _constitution,
    "integrity": _integrity,
}


def run_gate(root: str = ".", only: list[str] | None = None,
             skip: list[str] | None = None, checks: dict | None = None) -> dict:
    """Run the selected checks and report. `ok` is False only when a BLOCKING check
    fails; a non-blocking failure is reported but does not fail the gate."""
    # Guard against a vacuous PASS on a wrong/missing root (a CI step pointed at the wrong
    # dir, or a failed checkout). "No project found" must FAIL, not look all-green. Only
    # applies to real runs; injected check registries (logic tests) skip it.
    if checks is None:
        rr = Path(root)
        if not rr.exists() or not (rr / "sdlc-studio").is_dir():
            return {"ok": False, "checks": [{
                "check": "scope", "count": 0, "blocking": True, "status": "fail",
                "detail": f"no SDLC project under {root} (no sdlc-studio/ dir) - wrong --root?"}]}
    registry = checks if checks is not None else DEFAULT_CHECKS
    selected = [n for n in registry
                if (not only or n in only) and (not skip or n not in skip)]
    results = []
    for name in selected:
        r = registry[name](root)
        results.append({"check": name, "count": r["count"], "blocking": r["blocking"],
                        "status": "pass" if r["count"] == 0 else "fail",
                        "detail": r.get("detail", "")})
    ok = all(r["status"] == "pass" for r in results if r["blocking"])
    return {"ok": ok, "checks": results}


def _split(v: str | None) -> list[str] | None:
    return [x.strip() for x in v.split(",") if x.strip()] if v else None


def cmd_gate(args: argparse.Namespace) -> int:
    report = run_gate(args.root, only=_split(args.only), skip=_split(args.skip))
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        for c in report["checks"]:
            mark = "PASS" if c["status"] == "pass" else ("FAIL" if c["blocking"] else "warn")
            print(f"  [{mark}] {c['check']}: {c['detail']}")
        print(f"gate: {'PASS' if report['ok'] else 'FAIL'}")
    return 0 if report["ok"] else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Portable CI quality gate (CR0046).")
    p.add_argument("--root", default=".", help="Repo root (default: .)")
    p.add_argument("--only", help="Comma-separated checks to run (default: all)")
    p.add_argument("--skip", help="Comma-separated checks to skip")
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
