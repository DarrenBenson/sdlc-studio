#!/usr/bin/env python3
"""Advisory check: does `sdlc-studio/reviews/LATEST.md` still tell the truth?

LATEST.md is the project's state anchor - read first after every reset. It drifts silently: it once
claimed 606 tests (was 622), ~66 disclosure advisories (was 0), and a workstream "deferred" (was
shipped), and nothing caught it. This check compares the facts LATEST.md *claims* against reality and flags the
mismatches. Advisory (never blocks) and skill-only (no-op where there is no SKILL.md). It only checks
a fact LATEST.md actually states - it never demands one.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402


def _skill_dir(root: Path) -> Path:
    return root / ".claude" / "skills" / "sdlc-studio"


def _read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _true_version(skill_dir: Path) -> str | None:
    m = re.search(r'^\s*version:\s*"([\d.]+)"', _read(skill_dir / "SKILL.md"), re.M)
    return m.group(1) if m else None


def _true_test_count(skill_dir: Path) -> int:
    tdir = skill_dir / "scripts" / "tests"
    return sum(len(re.findall(r"^\s*def test_", _read(f), re.M))
               for f in sorted(tdir.glob("test_*.py"))) if tdir.is_dir() else 0


def _true_disclosure_count(root: Path) -> int | None:
    try:
        import disclosure
        r = disclosure.check(root)
        return len(r["findings"]) if r["applicable"] else None
    except Exception:  # noqa: BLE001 - the freshness check must never crash the gate
        return None


def check(repo_root: Path | str = ".") -> dict:
    """Findings (all advisory). {findings, ok, applicable}. Applicable only on the skill repo with a
    LATEST.md present; only facts LATEST.md states are checked."""
    root = Path(repo_root)
    skill_dir = _skill_dir(root)
    latest = root / "sdlc-studio" / "reviews" / "LATEST.md"
    if not (skill_dir / "SKILL.md").exists() or not latest.exists():
        return {"findings": [], "ok": True, "applicable": False}
    text = _read(latest)
    findings: list[dict] = []

    def claim(pattern: str):
        m = re.search(pattern, text, re.I)
        return m.group(1) if m else None

    # version
    cv, tv = claim(r"project version:\**\s*([\d.]+)"), _true_version(skill_dir)
    if cv and tv and cv != tv:
        findings.append({"kind": "version-drift",
                         "detail": f"LATEST.md says version {cv}; SKILL.md is {tv}"})
    # test count
    ct = claim(r"([\d,]+)\s+script tests")
    if ct:
        ct_n, tt = int(ct.replace(",", "")), _true_test_count(skill_dir)
        if ct_n != tt:
            findings.append({"kind": "test-count-drift",
                             "detail": (f"LATEST.md says {ct_n} tests; {tt} test functions "
                                        f"counted statically in scripts/tests (the runner may "
                                        f"report fewer for skips/subclasses - claim this number)")})
    # disclosure count
    cd = claim(r"disclosure[^\d]{0,8}(\d+)")
    if cd is not None:
        td = _true_disclosure_count(root)
        if td is not None and int(cd) != td:
            findings.append({"kind": "disclosure-drift",
                             "detail": f"LATEST.md says disclosure {cd}; actual is {td}"})
    # anchor-window ceiling: the anchor is re-read at every session start, so
    # it must stay a WINDOW (current state + one-line history), not a ledger
    # of full past-sprint paragraphs duplicating the retros
    from lib import sdlc_md
    try:
        ceiling = int(sdlc_md.project_override(root, "docs.latest_max_lines", 80))
    except (TypeError, ValueError):
        ceiling = 80
    n_lines = len(text.splitlines())
    if n_lines > ceiling:
        findings.append({"kind": "anchor-ledger",
                         "detail": (f"LATEST.md is {n_lines} lines (> {ceiling}, "
                                    f"docs.latest_max_lines) and is re-read every session "
                                    f"start - move past-sprint paragraphs to their retros "
                                    f"and keep one History line each")})
    return {"findings": findings, "ok": not findings, "applicable": True}


def main(argv: list[str] | None = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Flag stale facts in LATEST.md (advisory).")
    ap.add_argument("--root", default=".")
    sdlc_md.add_format_arg(ap)
    args = ap.parse_args(argv)
    r = check(args.root)
    if args.format == "json":
        print(json.dumps(r, indent=2))
        return 0  # advisory: report, never fail
    if not r["applicable"]:
        print("doc-freshness: N/A (not the skill repo, or no LATEST.md)")
        return 0
    if r["ok"]:
        print("doc-freshness: LATEST.md is fresh")
        return 0
    print(f"doc-freshness: {len(r['findings'])} stale claim(s) in LATEST.md:")
    for f in r["findings"]:
        print(f"  [{f['kind']}] {f['detail']}")
    return 0  # advisory: report, never fail


if __name__ == "__main__":
    raise SystemExit(main())
