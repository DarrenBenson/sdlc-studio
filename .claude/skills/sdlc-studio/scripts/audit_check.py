#!/usr/bin/env python3
"""SDLC Studio team-schema audit check - one CI-runnable command over the schema-v3 rules.

Runs the enforceable team-schema rules with STABLE rule ids so the output is a reference
implementation the wider crew audit linter can consume: structured authorship present and
resolvable, per-type evidence present, raiser and triager distinct, indexes derived (not
hand-edited), and id format valid. Any error-severity finding exits non-zero; a clean repo
exits 0. The rules are era-gated (schema v3), so a v2 project reports nothing.

    audit_check.py check                 # human summary, exit 1 on any violation
    audit_check.py check --format json   # stable machine output for the crew linter
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402
import validate  # noqa: E402
import reconcile  # noqa: E402

# The stable rule-id set this command owns (a subset validate/reconcile also surface).
RULE_IDS = (
    "authorship-structured", "authorship-type", "authorship-unresolved",
    "evidence-present", "duties-separated", "id-format", "index-derived",
)


def run(repo_root: Path | str) -> list[dict]:
    """Every team-schema violation as {rule, file, message}. Empty = the repo is conformant."""
    root = Path(repo_root)
    findings: list[dict] = []
    for type_ in sdlc_md.ARTIFACT_TYPES:
        for p in sdlc_md.artifact_files(type_, root):
            for v in validate.validate_file(p, type_, root):
                if v["rule"] in RULE_IDS and v["severity"] == "error":
                    findings.append({"rule": v["rule"], "file": str(p.relative_to(root)),
                                     "message": v["message"]})
    for issue in reconcile.index_derived_issues(root):
        findings.append({"rule": "index-derived", "file": "sdlc-studio", "message": issue})
    return findings


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="audit_check.py", description="Run the team-schema audit rules.")
    p.add_argument("cmd", choices=["check"])
    p.add_argument("--root", default=".")
    p.add_argument("--format", choices=["text", "json"], default="text")
    args = p.parse_args(argv)
    findings = run(args.root)
    if args.format == "json":
        print(json.dumps({"ok": not findings, "rules": list(RULE_IDS), "findings": findings}, indent=2))
    else:
        if not findings:
            print("audit-check: clean (all team-schema rules pass)")
        else:
            print(f"audit-check: {len(findings)} violation(s)")
            for f in findings:
                print(f"  [{f['rule']}] {f['file']}: {f['message']}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
