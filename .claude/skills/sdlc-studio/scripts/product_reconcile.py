#!/usr/bin/env python3
"""Cross-repo feature-map traceability.

Verify the PVD's master feature inventory against the child repos: every product feature
`PF####` must map to a real feature in its owning repo's PRD. Reads sibling repos via the
product manifest; **degrades** (advisory) when a repo is absent rather than crashing - it is
a coordination check, not a hard dependency. Exits non-zero on a blocking inconsistency.

Findings:
  orphan-feature   PF maps to <repo>:<feat> but that feature is not in the child PRD (BLOCKING)
  unknown-repo     PF references a repo id not in the manifest (BLOCKING)
  repo-absent      the child repo / its PRD is not reachable (advisory - degrade)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402
import pvd  # noqa: E402  (sibling: read_manifest)

_PF = re.compile(r"^PF\d+$")
# <repo-id>:<prd-feature-id> - the feature side must contain a digit, which excludes prose
# like "see:later" and the template placeholder "{{repo}}:{{prd_feature_id}}".
_REF = re.compile(r"^[\w.-]+:[\w.-]*\d[\w.-]*$")


def parse_feature_map(pvd_text: str) -> list[dict]:
    """Extract {pf_id, repo, feature} from the PVD's feature-inventory table rows."""
    out: list[dict] = []
    for line in pvd_text.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = sdlc_md.table_cells(line)
        if not cells or not _PF.match(cells[0].strip()):
            continue
        ref = next((c.strip() for c in cells if _REF.match(c.strip())), None)
        if ref:
            repo, _, feat = ref.partition(":")
            out.append({"pf_id": cells[0].strip(), "repo": repo, "feature": feat})
    return out


def prd_has_feature(repo_root: Path, feature_id: str) -> bool | None:
    """True/False if the child PRD DECLARES the feature; None if the PRD is unreachable.
    Anchored to a declaration site - the id as a standalone table cell or in a heading -
    so a free-text mention (changelog, "F0007 removed", prose) does NOT count."""
    prd = Path(repo_root) / "sdlc-studio" / "prd.md"
    try:
        text = prd.read_text(encoding="utf-8")
    except OSError:
        return None
    fid = feature_id.strip()
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("#") and re.search(rf"\b{re.escape(fid)}\b", s):
            return True
        cells = sdlc_md.table_cells(line) if s.startswith("|") else None
        if cells and fid in [c.strip() for c in cells]:
            return True
    return False


def product_reconcile(pvd_path: Path | str, manifest_path: Path | str) -> dict:
    pvd_path, manifest_path = Path(pvd_path), Path(manifest_path)
    features = parse_feature_map(pvd_path.read_text(encoding="utf-8"))
    manifest = pvd.read_manifest(manifest_path)
    repo_by_id = {r["id"]: r for r in manifest.get("repos", []) if r.get("id")}
    base = manifest_path.resolve().parent
    findings: list[dict] = []
    if not features:
        findings.append({"kind": "empty-feature-map", "blocking": False, "pf": None,
                         "detail": "no PF feature rows parsed - empty PVD or the §3 table was renamed?"})
    for f in features:
        repo = repo_by_id.get(f["repo"])
        if repo is None:
            findings.append({"kind": "unknown-repo", "blocking": True, "pf": f["pf_id"],
                             "detail": f"{f['pf_id']} references repo '{f['repo']}' not in the manifest"})
            continue
        if not repo.get("path"):  # never silently fall back to the manifest dir
            findings.append({"kind": "missing-path", "blocking": True, "pf": f["pf_id"],
                             "detail": f"manifest repo '{f['repo']}' has no path"})
            continue
        repo_root = (base / repo["path"]).resolve()
        has = prd_has_feature(repo_root, f["feature"])
        if has is None:
            findings.append({"kind": "repo-absent", "blocking": False, "pf": f["pf_id"],
                             "detail": f"{f['pf_id']}: {f['repo']} PRD unreachable at {repo_root}"})
        elif not has:
            findings.append({"kind": "orphan-feature", "blocking": True, "pf": f["pf_id"],
                             "detail": f"{f['pf_id']} maps to {f['repo']}:{f['feature']} but it is not in that PRD"})
    unverified = sum(1 for x in findings if x["kind"] == "repo-absent")
    return {"features": len(features), "unverified": unverified, "findings": findings,
            "ok": not any(x["blocking"] for x in findings)}


def cmd_reconcile(args: argparse.Namespace) -> int:
    r = product_reconcile(args.pvd, args.manifest)
    if args.format == "json":
        print(json.dumps(r, indent=2))
    else:
        for x in r["findings"]:
            print(f"  [{'FAIL' if x['blocking'] else 'warn'}] {x['kind']}: {x['detail']}")
        unv = f", {r['unverified']} un-verified (repos absent)" if r.get("unverified") else ""
        print(f"product reconcile: {r['features']} feature(s){unv}, "
              f"{'OK' if r['ok'] else 'DRIFT'}")
    return 0 if r["ok"] else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Cross-repo PVD feature-map traceability.")
    p.add_argument("--pvd", required=True, help="The master PVD")
    p.add_argument("--manifest", required=True, help="The product manifest")
    p.add_argument("--format", choices=("text", "json"), default="text")
    p.set_defaults(func=cmd_reconcile)
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
