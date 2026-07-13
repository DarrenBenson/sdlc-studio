#!/usr/bin/env python3
"""Cross-repo artefact resolution over the PVD product manifest.

A multi-repo product declares its repos in `product-manifest.yaml`, so an artefact in one
repo can legitimately name a referent that lives in another (service A's story waits on
service B's API). This is the single resolver for that lookup, shared by every checker that
follows a `Depends on:` / `Blocked By:` edge: in-repo first (the file census, alias-aware via
`sdlc_md.find_by_id`), then across the sibling repos the manifest names.

It degrades honestly. An absent sibling checkout is reported with a named `error`
("manifest repo X not found at <path>") and never resolves - a caller can therefore
distinguish three states and must never collapse them: resolved (a status), unresolvable
(an error, the checkout is not on disk), and genuinely missing (no such id anywhere).

Pure stdlib; no PyYAML dependency (the manifest is parsed line-wise).
"""
from __future__ import annotations

import re
from pathlib import Path

from . import sdlc_md

MANIFEST_NAME = "product-manifest.yaml"
MISSING = "missing"  # `error` when the id resolves in no repo at all
_MASTER_RE = re.compile(r"master_pvd:\s*(\S+)")


def read_manifest(path: Path) -> dict:
    """Best-effort parse of product-manifest.yaml (master_pvd + repos[].path) without a
    hard PyYAML dependency."""
    text = Path(path).read_text(encoding="utf-8")
    master = None
    repos: list[dict] = []
    cur: dict | None = None
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("#") or not s:
            continue
        m = _MASTER_RE.match(s)
        if m:
            master = m.group(1)
            continue
        if s.startswith("- id:"):
            cur = {"id": s.split(":", 1)[1].partition("#")[0].strip()}  # strip inline comment
            repos.append(cur)
        elif cur is not None and ":" in s:
            k, _, v = s.partition(":")
            cur[k.strip()] = v.partition("#")[0].strip()  # strip inline comment
    return {"master_pvd": master, "repos": repos}


def manifest_repos(root: Path | str, manifest: Path | str | None = None) -> list[tuple[str, Path]]:
    """(label, repo-root) for each sibling repo in the PVD manifest, paths resolved relative
    to the manifest. Returns [] when there is no manifest (an in-repo-only run)."""
    mpath = Path(manifest) if manifest else Path(root) / MANIFEST_NAME
    if not mpath.is_file():
        return []
    base = mpath.resolve().parent
    out: list[tuple[str, Path]] = []
    for repo in read_manifest(mpath).get("repos", []):
        rel = repo.get("path")
        if not rel:
            continue
        out.append((repo.get("id") or rel, (base / rel).resolve()))
    return out


def status_in(root: Path, ref: str) -> dict | None:
    """Resolve a referent by the file census in ONE repo: {type, status} or None if absent.
    A file with no readable Status yields `Unknown` rather than being treated as resolved."""
    found = sdlc_md.find_by_id(root, ref)
    if found is None:
        return None
    path, type_ = found
    raw = sdlc_md.extract_field(path.read_text(encoding="utf-8"), "Status")
    st = sdlc_md.canonical_status(raw, sdlc_md.status_vocab(type_, root))
    return {"type": type_, "status": st or (raw.strip() if raw else "Unknown")}


def resolve(ref: str, root: Path, repos: list[tuple[str, Path]]) -> dict:
    """Resolve a referent in-repo first, then across EVERY manifest repo that is on disk.

    An absent sibling checkout never stops the search: it is recorded and the remaining repos
    are still searched, so a referent delivered in a repo the operator HAS cloned resolves
    whatever order the manifest lists the repos in. The verdict is therefore a function of
    the disk state, not of manifest ordering. Only when no repo resolves the id do the
    recorded absences become the `error` - the honest report is then "one or more repos could
    not be searched", not "this id does not exist".

    The returned dict always carries `cleared` and `error` so a caller never has to guess:
    an unresolved or unknown-status referent is `cleared=False` with `error` set, never
    silently cleared. `cleared` is the terminal-status judgement (an absorbing state for the
    referent's type); a caller wanting a different policy (delivered vs dead, say) reads
    `status` and applies its own.
    """
    hit = status_in(root, ref)
    if hit is not None:
        return _hit(ref, ".", hit)
    unsearched: list[str] = []
    for label, rp in repos:
        if not rp.exists():
            unsearched.append(f"manifest repo {label} not found at {rp}")
            continue
        hit = status_in(rp, ref)
        if hit is not None:
            return _hit(ref, label, hit)
    if unsearched:  # a repo went unsearched, so `missing` would be a claim we cannot make
        return {"id": ref, "repo": None, "status": None, "cleared": False,
                "error": "; ".join(unsearched)}
    return {"id": ref, "repo": None, "status": None, "cleared": False, "error": MISSING}


def _hit(ref: str, repo: str, hit: dict) -> dict:
    """The resolution record for a referent found in `repo`."""
    cleared = sdlc_md.is_terminal_status(hit["type"], hit["status"])
    return {"id": ref, "repo": repo, "status": hit["status"], "cleared": cleared,
            "error": None if cleared or hit["status"] != "Unknown" else "unknown status"}
