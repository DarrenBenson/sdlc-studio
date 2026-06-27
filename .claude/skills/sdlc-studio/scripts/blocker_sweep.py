#!/usr/bin/env python3
"""SDLC Studio blocker sweep: find units whose blockers have cleared (read-only).

The skill tracks what is blocked but never re-checks whether a blocker has cleared.
`audit.py` flags the forward direction (`unmet-deps`); this is the inverse: a unit sits at
Status `Blocked`, carries a `Depends on:` field, or an epic `Blocked By` row long after the
thing it waited on reached a terminal state, and nothing surfaces it as now-eligible.

The sweep collects every blocker signal across the artefacts, resolves each referent's
current status - in-repo by the file census (LL0001), cross-repo by reading the sibling
repos named in `product-manifest.yaml` (reusing pvd.read_manifest) - and classifies each
genuinely-blocked unit as now-unblocked (every referent terminal/delivered) or
still-blocked (with the outstanding referent named).

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
import pvd  # noqa: E402  (manifest read, no PyYAML dependency)
from lib import sdlc_md  # noqa: E402

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


def _status_in(root: Path, ref: str) -> dict | None:
    """Resolve a referent by the file census in one repo: {type, status} or None if absent."""
    target = sdlc_md.norm_id(ref)
    for type_ in sdlc_md.ARTIFACT_TYPES:
        for path in sdlc_md.artifact_files(type_, root):
            rec = sdlc_md.extract_record_id(path.stem)
            if rec and sdlc_md.norm_id(rec) == target:
                raw = sdlc_md.extract_field(path.read_text(encoding="utf-8"), "Status")
                st = sdlc_md.canonical_status(raw, sdlc_md.status_vocab(type_, root))
                return {"type": type_, "status": st or (raw.strip() if raw else "Unknown")}
    return None


def _manifest_repos(root: Path, manifest: Path | None) -> list[tuple[str, Path]]:
    """(label, repo-root) for each sibling repo in the PVD manifest, paths resolved relative
    to the manifest. Returns [] when there is no manifest (in-repo-only run)."""
    mpath = manifest or (root / "product-manifest.yaml")
    if not Path(mpath).is_file():
        return []
    base = Path(mpath).resolve().parent
    out: list[tuple[str, Path]] = []
    for repo in pvd.read_manifest(Path(mpath)).get("repos", []):
        rel = repo.get("path")
        if not rel:
            continue
        rp = (base / rel).resolve()
        out.append((repo.get("id") or rel, rp))
    return out


def _resolve(ref: str, root: Path, repos: list[tuple[str, Path]]) -> dict:
    """Resolve a referent in-repo first, then across the manifest repos. The returned dict
    always carries `cleared` and `error` so a caller never has to guess: an unresolved or
    unknown-status referent is `cleared=False` with `error` set - never silently cleared."""
    hit = _status_in(root, ref)
    if hit is not None:
        cleared = sdlc_md.is_terminal_status(hit["type"], hit["status"])
        return {"id": ref, "repo": ".", "status": hit["status"], "cleared": cleared,
                "error": None if cleared or hit["status"] != "Unknown"
                else "unknown status"}
    for label, rp in repos:
        if not rp.exists():
            return {"id": ref, "repo": label, "status": None, "cleared": False,
                    "error": f"manifest repo {label} not found at {rp}"}
        hit = _status_in(rp, ref)
        if hit is not None:
            cleared = sdlc_md.is_terminal_status(hit["type"], hit["status"])
            return {"id": ref, "repo": label, "status": hit["status"], "cleared": cleared,
                    "error": None if cleared or hit["status"] != "Unknown" else "unknown status"}
    return {"id": ref, "repo": None, "status": None, "cleared": False, "error": "missing"}


def sweep(root: Path | str, manifest: Path | str | None = None) -> dict:
    """Census every blocker signal and classify each genuinely-blocked unit.

    A unit is *genuinely blocked* when its Status is `Blocked` or it carries a `Blocked By`
    referent; such a unit with every referent cleared (and at least one referent) is a
    now-unblocked candidate, otherwise still-blocked. A non-blocked unit that merely carries
    a `Depends on:` is reported as `dependent` (the signal is collected per AC1) but is never
    a Blocked->Ready candidate.
    """
    rr = Path(root).resolve()
    repos = _manifest_repos(rr, Path(manifest) if manifest else None)
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
            resolved = [_resolve(r, rr, repos) for r in refs]
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
