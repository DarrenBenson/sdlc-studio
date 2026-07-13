#!/usr/bin/env python3
"""SDLC Studio blocker sweep: find units whose blockers have cleared (read-only).

The skill tracks what is blocked but never re-checks whether a blocker has cleared.
`audit.py` flags the forward direction (`unmet-deps`); this is the inverse: a unit sits at
Status `Blocked`, carries a `Depends on:` field, or an epic `Blocked By` row long after the
thing it waited on reached a terminal state, and nothing surfaces it as now-eligible.

The sweep collects every blocker signal across the artefacts, resolves each referent's
current status - in-repo by the file census (LL0001), cross-repo across the sibling repos
named in `product-manifest.yaml`, both through the shared `lib/xrepo` resolver - and
classifies each genuinely-blocked unit as now-unblocked (every referent terminal/delivered)
or still-blocked (with the outstanding referent named).

Per LL0008 it fails loud and never false-clears: a referent that is missing, unreadable, or
in an unknown status is reported still-blocked / as an error, never silently cleared.
Detection and reporting only - it mutates nothing; the gated `transition` call stays the
actor for `Blocked -> Ready`.

Subcommand:
  sweep  Blocker census + now-unblocked / still-blocked report as JSON/text.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md, xrepo  # noqa: E402  (xrepo: in-repo + cross-repo id resolution)

_BLOCKED = "Blocked"


def _referents(text: str) -> list[str]:
    """Normalised ids this unit waits on: the union of `Depends on` and `Blocked By` fields."""
    refs: set[str] = set()
    for field in ("Depends on", "Depends On", "Blocked By", "Blocked by"):
        val = sdlc_md.extract_field(text, field)
        if not val:
            continue
        for rid in sdlc_md.ID_SEARCH_RE.findall(val):
            refs.add(sdlc_md.norm_id(rid))
    return sorted(refs)


def sweep(root: Path | str, manifest: Path | str | None = None) -> dict:
    """Census every blocker signal and classify each genuinely-blocked unit.

    A unit is *genuinely blocked* when its Status is `Blocked` or it carries a `Blocked By`
    referent; such a unit with every referent cleared (and at least one referent) is a
    now-unblocked candidate, otherwise still-blocked. A non-blocked unit that merely carries
    a `Depends on:` is reported as `dependent` (the signal is collected per AC1) but is never
    a Blocked->Ready candidate.
    """
    rr = Path(root).resolve()
    repos = xrepo.manifest_repos(rr, manifest)
    units: list[dict] = []
    now_unblocked: list[str] = []
    still_blocked: list[str] = []
    errors: list[str] = []
    for type_ in sdlc_md.ARTIFACT_TYPES:
        vocab = sdlc_md.status_vocab(type_, rr)
        for path in sdlc_md.artifact_files(type_, rr):
            rec = sdlc_md.extract_record_id(path.stem)
            if not rec:
                continue
            text = path.read_text(encoding="utf-8")
            status = sdlc_md.canonical_status(sdlc_md.extract_field(text, "Status"), vocab)
            blocked_by = bool(sdlc_md.extract_field(text, "Blocked By")
                              or sdlc_md.extract_field(text, "Blocked by"))
            refs = _referents(text)
            signals = []
            if status == _BLOCKED:
                signals.append("blocked-status")
            if blocked_by:
                signals.append("blocked-by")
            if sdlc_md.extract_field(text, "Depends on") or sdlc_md.extract_field(text, "Depends On"):
                signals.append("depends-on")
            if not signals:
                continue
            resolved = [xrepo.resolve(r, rr, repos) for r in refs]
            genuinely_blocked = status == _BLOCKED or blocked_by
            unit = {"id": rec, "type": type_, "status": status or "Unknown",
                    "signals": signals, "referents": resolved}
            for r in resolved:
                if r["error"]:
                    errors.append(f"{rec} -> {r['id']}: {r['error']}")
            if not genuinely_blocked:
                unit["state"] = "dependent"
            elif resolved and all(r["cleared"] for r in resolved):
                unit["state"] = "now-unblocked"
                now_unblocked.append(rec)
            else:
                unit["state"] = "still-blocked"
                unit["outstanding"] = [f"{r['id']}:{r['status'] or r['error']}"
                                       for r in resolved if not r["cleared"]] or ["no referent"]
                still_blocked.append(rec)
            units.append(unit)
    return {"now_unblocked": sorted(now_unblocked), "still_blocked": sorted(still_blocked),
            "errors": errors, "units": units}


def cmd_sweep(args: argparse.Namespace) -> int:
    report = sweep(args.root, args.manifest)
    if args.format == "json":
        print(json.dumps(report, indent=2))
        return 0
    nu, sb = report["now_unblocked"], report["still_blocked"]
    if nu:
        print("Now unblocked (every blocker cleared - candidates for Blocked -> Ready):")
        for uid in nu:
            print(f"  {uid}")
    if sb:
        print("Still blocked:")
        for u in report["units"]:
            if u["state"] == "still-blocked":
                print(f"  {u['id']}: waiting on {', '.join(u['outstanding'])}")
    if report["errors"]:
        print("Unresolved referents (reported still-blocked, never cleared):")
        for e in report["errors"]:
            print(f"  {e}")
    if not (nu or sb):
        print("No blocked units found.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Find units whose blockers have cleared.")
    sub = p.add_subparsers(dest="cmd", required=True)
    sw = sub.add_parser("sweep", help="Census blocker signals; report now-unblocked units.")
    sw.add_argument("--root", default=".", help="Repo root (default: .)")
    sw.add_argument("--manifest", help="PVD manifest path (default: <root>/product-manifest.yaml)")
    sw.add_argument("--format", choices=("text", "json"), default="text")
    sw.set_defaults(func=cmd_sweep)
    sdlc_md.add_global_root(p)
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
