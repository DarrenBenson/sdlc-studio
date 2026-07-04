#!/usr/bin/env python3
"""SDLC Studio tranche audit - sprint pre-flight readiness.

Runs between `sprint plan` and the triage STOP, so the operator approves a
clean, verifiable batch. Per unit it flags, deterministically:

- **weak-AC**       - no checkable AC, or the tautology placeholder (the
                      vacuous-pass class the downstream verify/conformance miss),
- **unmet-deps**    - a `Depends on` referent that is not yet delivered,
- **already-terminal** - already Complete/Superseded/Done (close, do not re-work),
- **missing-regression-test** - a Fixed/Done bug whose recorded tests carry no
                      integration/regression-level case (name-signal only; the seam
                      judgement stays with review - see best-practices/testing.md),
- **link-integrity** - reuses `integrity.py`'s error findings for the unit.

Emits a JSON readiness report; exits non-zero when any unit is not ready. The
adversarial "is the problem still real" lens stays model-instructed (delegates to
the adversarial audit when built). Read-only; pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402
import integrity  # noqa: E402  (sibling script; scripts dir is on sys.path)
import sprint  # noqa: E402
import verify_ac  # noqa: E402  (reuse the Verify-line lint)
import ac_scope  # noqa: E402  (reuse the cross-epic AC check)

TAUTOLOGY = "lint and tests green"
# A dependency counts as met once it has been delivered (or replaced).
MET = {"Done", "Complete", "Verified", "Fixed", "Accepted", "Superseded", "Closed"}
# Terminal-but-not-delivered: the dependency is dead, surfaced distinctly.
DEAD = {"Rejected", "Withdrawn", "Won't Implement", "Won't Fix", "Deferred"}
_AC_CHECKBOX = re.compile(r"^\s*- \[[ xX]\] ")


def find_artifact(root: Path, rec_id: str):
    """Locate an artifact file by id across all types; return (path, type) or None."""
    target = sdlc_md.norm_id(rec_id)
    for type_ in sdlc_md.ARTIFACT_TYPES:
        for path in sdlc_md.artifact_files(type_, root):
            rec = sdlc_md.extract_record_id(path.stem)
            if rec and sdlc_md.norm_id(rec) == target:
                return path, type_
    return None


def _weak_ac(text: str) -> bool:
    """True when the unit has no checkable AC, or only the tautology placeholder."""
    items: list[str] = []
    in_ac = False
    for line in text.splitlines():
        if line.startswith("## "):
            in_ac = "acceptance criteria" in line.lower()
            continue
        if not in_ac:  # only AC inside the Acceptance Criteria section count
            continue
        if (_AC_CHECKBOX.match(line) or sdlc_md.AC_HEADING_RE.match(line)
                or sdlc_md.AC_BULLET_RE.match(line)):
            items.append(line)
    if not items:
        return True
    return any(TAUTOLOGY in i.lower() for i in items)


def _bug_underspecified(text: str) -> bool:
    """A bug is ready when it documents how to reproduce AND a proposed fix.

    Bugs have no Acceptance Criteria section - judging them by `_weak_ac` would
    always flag them. Readiness for a bug is repro + fix presence instead.
    Both heading vocabularies count: released projects already carry bugs
    authored from template revisions using "Reproduction Steps" / "Fix
    Description", and those must not flag forever.
    """
    low = text.lower()
    has_repro = "## steps to reproduce" in low or "## reproduction steps" in low
    has_fix = "## proposed fix" in low or "## fix description" in low
    return not (has_repro and has_fix)


def _unmet_deps(root: Path, text: str) -> list[str]:
    """Referents of `Depends on` that are not yet delivered."""
    val = sdlc_md.extract_field(text, "Depends on") or sdlc_md.extract_field(text, "Depends On")
    if not val or integrity._is_blank(val):
        return []
    unmet: list[str] = []
    for ref in sorted({sdlc_md.norm_id(r) for r in sdlc_md.ID_SEARCH_RE.findall(val)}):
        found = find_artifact(root, ref)
        if found is None:
            unmet.append(f"{ref}:missing")
            continue
        path, type_ = found
        st = sdlc_md.canonical_status(
            sdlc_md.extract_field(path.read_text(encoding="utf-8"), "Status"),
            sdlc_md.status_vocab(type_, root),
        ) or "Unknown"
        if st in DEAD:
            unmet.append(f"{ref}:{st}(dead)")
        elif st not in MET:
            unmet.append(f"{ref}:{st}")
    return unmet


def _already_satisfied(root: Path, rid: str) -> bool:
    """True if the unit's executable ACs all pass in the verify-report: verified > 0,
    no failures, no stale. Such a Ready unit is already delivered (the audit cannot see a feature
    shipped under a different artifact, but a green verifier set is the deterministic signal) -
    surface it as a close-candidate, not work to build. Manual-only / AC-less units never match."""
    report = sdlc_md.read_json(root / "sdlc-studio" / ".local" / "verify-report.json", {})
    stories = report.get("stories", {})
    items = stories.items() if isinstance(stories, dict) else []
    for stem, e in items:
        if sdlc_md.norm_id(stem.split("-")[0]) == sdlc_md.norm_id(rid):
            return e.get("verified", 0) > 0 and not e.get("failed", 0) and not e.get("stale", 0)
    return False


def _weak_verify(text: str) -> bool:
    """True if a story has a non-executable / mis-written Verify line: reuses
    verify_ac.lint_verifier, so the breakdown flags prose-curl verifiers at design time instead
    of discovering them 0/7 at verify time."""
    for line in text.splitlines():
        m = verify_ac.VERIFY_RE.match(line)
        if m and verify_ac.lint_verifier(m.group(2).strip()):
            return True
    return False


_REGRESSION_RE = re.compile(r"regression|integration|\be2e\b|end[- ]to[- ]end", re.I)


def _missing_regression_test(text: str) -> bool:
    """CR0128 heuristic 2: a Fixed/Done bug should carry an integration- or regression-level test
    (the bug lived in the seams), not only a unit test on the root-cause file. This mechanises the
    NAME signal - a `Verify` line or a 'regression/integration/e2e' marker - and returns True for a
    bug that records tests but none at that level. It deliberately does NOT try to prove a test
    truly exercises the seams: that stays a review judgement (the advisory boundary recorded in
    CR0128). A bug with no test info at all is left to `underspecified`, not double-flagged here."""
    lines = text.splitlines()
    mentions_test = any("**verify:**" in low or "test" in low
                        for low in (line.lower() for line in lines))
    if not mentions_test:
        return False
    return not any(_REGRESSION_RE.search(line) for line in lines)


def audit_unit(root: Path | str, rec_id: str, integrity_errors: set[str] | None = None,
               cross_epic_ids: set[str] | None = None) -> dict:
    """Readiness verdict for a single unit."""
    root = Path(root)
    found = find_artifact(root, rec_id)
    if found is None:
        return {"id": sdlc_md.norm_id(rec_id), "status": "missing", "issues": ["not-found"], "ready": False}
    path, type_ = found
    text = path.read_text(encoding="utf-8")
    rid = sdlc_md.extract_record_id(path.stem) or path.stem
    status = sdlc_md.canonical_status(sdlc_md.extract_field(text, "Status"),
                                      sdlc_md.status_vocab(type_, root)) or "Unknown"
    issues: list[str] = []
    if type_ == "bug":
        if _bug_underspecified(text):
            issues.append("underspecified")
        if status in integrity.TERMINAL and _missing_regression_test(text):
            issues.append("missing-regression-test")
    elif _weak_ac(text):
        issues.append("weak-AC")
    if type_ == "story" and _weak_verify(text):  # non-executable Verify line
        issues.append("weak-verify")
    if cross_epic_ids and sdlc_md.norm_id(rid) in cross_epic_ids:  # cross-epic AC leakage
        issues.append("cross-epic-ac")
    unmet = _unmet_deps(root, text)
    if unmet:
        issues.append("unmet-deps: " + ", ".join(unmet))
    if status in integrity.TERMINAL:
        issues.append("already-terminal")
    if integrity_errors and rid in integrity_errors:
        issues.append("link-integrity")
    if status not in integrity.TERMINAL and _already_satisfied(root, rid):
        issues.append("already-satisfied")  # verifiers pass -> close-candidate, don't build
    return {"id": rid, "type": type_, "status": status, "issues": issues, "ready": not issues}


def audit_batch(repo_root: Path | str, ids: list[str]) -> dict:
    """Readiness report over a batch of unit ids."""
    root = Path(repo_root)
    ierr = {f["id"] for f in integrity.detect_integrity(root)["findings"] if f["severity"] == "error"}
    # cross-epic AC leakage, computed once for the batch (ac_scope is repo-wide)
    try:
        cross = {sdlc_md.norm_id(f["story"]) for f in ac_scope.check(root) if f.get("story")}
    except Exception:  # noqa: BLE001 - advisory readiness check, never break the audit
        cross = set()
    units = [audit_unit(root, i, ierr, cross) for i in ids]
    ready = sum(1 for u in units if u["ready"])
    return {
        "generated_at": sdlc_md.now_iso8601(),
        "units": units,
        "summary": {"total": len(units), "ready": ready, "not_ready": len(units) - ready},
    }


def cmd_check(args: argparse.Namespace) -> int:
    """Audit a batch (by ids or a status query); exit non-zero if any unit is not ready."""
    if args.ids:
        ids = [s.strip() for s in args.ids.split(",") if s.strip()]
    else:
        kind, status = (("cr", args.crs) if args.crs is not None
                        else ("bug", args.bugs) if args.bugs is not None
                        else ("story", args.stories))
        ids = [b["id"] for b in sprint.select_batch(args.root, kind, status)]
    res = audit_batch(args.root, ids)
    if args.format == "json":
        print(json.dumps(res, indent=2))
    else:
        s = res["summary"]
        print(f"tranche audit: {s['ready']}/{s['total']} ready, {s['not_ready']} not")
        kinds = set()
        for u in res["units"]:
            if not u["ready"]:
                print(f"  NOT READY {u['id']} ({u['status']}): {'; '.join(u['issues'])}")
                kinds.update(i.split(":")[0].strip() for i in u["issues"])  # issue may carry a suffix
        hints = sdlc_md.remediation_lines("audit", kinds)
        if hints:
            print("Guidance:")
            for h in hints:
                print(f"  - {h}")
    return 1 if res["summary"]["not_ready"] else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SDLC Studio tranche audit (sprint pre-flight).")
    sub = parser.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="Audit a batch for readiness before the triage STOP.")
    g = c.add_mutually_exclusive_group(required=True)
    g.add_argument("--ids", help="Comma-separated unit ids (e.g. CR0003,CR0004)")
    g.add_argument("--crs", metavar="STATUS", help="CRs with this Status")
    g.add_argument("--bugs", metavar="STATUS", help="Bugs with this Status")
    g.add_argument("--stories", metavar="STATUS", help="Stories with this Status")
    c.add_argument("--root", default=".", help="Repo root (default: .)")
    c.add_argument("--format", choices=("text", "json"), default="text")
    c.set_defaults(func=cmd_check)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
