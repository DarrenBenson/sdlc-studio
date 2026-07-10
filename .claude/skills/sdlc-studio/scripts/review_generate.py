#!/usr/bin/env python3
"""Deterministic spine of the `review generate` on-ramp.

`review generate` lets a developer point sdlc-studio at an existing repo, get a
dated review report plus triaged findings, and decide whether to adopt the full
pipeline - with no prior workspace. The review itself is model-driven (three legs:
architecture, code quality, defensive security), but three things must be
deterministic and testable:

  * bootstrap  - create the workspace folders the review writes into, on a repo
                 that has never run sdlc-studio, idempotently;
  * the policy - the remediation-only security posture, embedded verbatim in the
                 prompt template so a reviewing agent cannot paraphrase it away;
  * scan_secret - a guard that proves no secret value leaked into a produced
                 artefact (location plus rotation only, never the value).

Pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402
import file_finding  # noqa: E402  (reuse ensure_index)

SKILL = Path(__file__).resolve().parent.parent
SDLC = "sdlc-studio"

# The remediation-only security posture. This is the single source of truth; the
# prompt template embeds it verbatim (guarded by test_review_generate) so a
# reviewing agent is handed the exact wording, never a paraphrase.
SECURITY_POLICY = (
    "Security findings are remediation-only by design: report location, weakness "
    "class, realistic impact, and a concrete fix. Do not include proof-of-concept "
    "exploits or payloads. Never copy a secret value into any artefact; report a "
    "committed secret by its location plus rotation instructions, and leave the "
    "value where it is."
)

# Folders the review writes into: the report and the two finding types.
_BOOTSTRAP_DIRS = ("reviews", "bugs", "change-requests")
_BOOTSTRAP_INDEXES = ("bug", "cr")


def bootstrap(repo_root: Path | str, dry_run: bool = False) -> dict:
    """Create the workspace folders a review needs, idempotently. Returns the list
    of paths created (empty on a repo that already has them)."""
    root = Path(repo_root)
    today = date.today().isoformat()
    created: list[str] = []
    for d in _BOOTSTRAP_DIRS:
        rel = f"{SDLC}/{d}"
        if not (root / rel).is_dir():
            created.append(rel + "/")
            if not dry_run:
                (root / rel).mkdir(parents=True, exist_ok=True)
    for t in _BOOTSTRAP_INDEXES:
        idx_rel = f"{sdlc_md.ARTIFACT_TYPES[t][0]}/_index.md"
        if (root / idx_rel).exists():
            continue
        if dry_run:
            created.append(idx_rel)
        elif file_finding.ensure_index(root, t, today):
            created.append(idx_rel)
    return {"created": created, "dry_run": dry_run}


def render_prompt() -> str:
    """The review-workflow prompt template, with the security policy embedded."""
    return (SKILL / "templates" / "workflows" / "repo-review.md").read_text(encoding="utf-8")


def scan_secret(repo_root: Path | str, secret: str) -> list[tuple[str, int]]:
    """Return (relative-path, line-number) for every produced artefact line that
    contains the literal `secret`. A clean remediation-only report returns [].
    An empty/whitespace secret matches nothing (never treat it as a wildcard)."""
    if not secret or not secret.strip():
        return []
    root = Path(repo_root)
    hits: list[tuple[str, int]] = []
    for d in _BOOTSTRAP_DIRS:
        base = root / SDLC / d
        if not base.is_dir():
            continue
        for md in sorted(base.glob("*.md")):
            for lineno, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
                if secret in line:
                    hits.append((str(md.relative_to(root)), lineno))
    return hits


def cmd_bootstrap(args: argparse.Namespace) -> int:
    r = bootstrap(args.root, dry_run=args.dry_run)
    if args.format == "json":
        print(json.dumps(r, indent=2))
    else:
        verb = "would create" if r["dry_run"] else "created"
        print(f"bootstrap: {verb} {len(r['created'])}")
        for c in r["created"]:
            print(f"  + {c}")
    return 0


def cmd_policy(args: argparse.Namespace) -> int:
    print(SECURITY_POLICY)
    return 0


def cmd_prompt(args: argparse.Namespace) -> int:
    print(render_prompt())
    return 0


def cmd_scan(args: argparse.Namespace) -> int:
    hits = scan_secret(args.root, args.secret)
    if hits:
        for rel, lineno in hits:
            print(f"{rel}:{lineno}: secret value present - must be location + rotation only")
        return 1
    print("scan: no secret value found in produced artefacts")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Deterministic spine of `review generate`.")
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("bootstrap", help="Create the workspace folders a review writes into.")
    b.add_argument("--root", default=".")
    b.add_argument("--dry-run", action="store_true", dest="dry_run")
    b.add_argument("--format", choices=("text", "json"), default="text")
    b.set_defaults(func=cmd_bootstrap)

    pol = sub.add_parser("policy", help="Print the verbatim remediation-only security policy.")
    pol.set_defaults(func=cmd_policy)

    pr = sub.add_parser("prompt", help="Print the review-workflow prompt template.")
    pr.set_defaults(func=cmd_prompt)

    sc = sub.add_parser("scan", help="Fail if a secret value leaked into a produced artefact.")
    sc.add_argument("--root", default=".")
    sc.add_argument("--secret", required=True)
    sc.set_defaults(func=cmd_scan)
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
