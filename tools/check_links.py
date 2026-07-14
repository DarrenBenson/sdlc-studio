#!/usr/bin/env python3
"""Check that markdown links resolve - anchors AND relative file targets.

A skill-development CI tool (it lives in tools/, not in the runtime scripts/
directory). Three passes:

1. skill tree: every `{#anchor}` (on any line - the skill attaches anchors to
   non-heading lines too) plus implicit heading slugs are indexed, then every
   `path.md#anchor` reference is checked to point at a file and anchor that
   exist. Illustrative examples (e.g. `doc.md#section-name` in the documentation
   style guide) are allowlisted.
2. root docs (README, AGENTS, ...): their `.md` links must name a real file.
3. workspace indexes (`sdlc-studio/**/_index.md`): an index row LINKS an
   artefact file, and that file must exist. Validating anchors alone let a row
   point at a deleted artefact and still pass.

Usage:
    python3 tools/check_links.py [--root DIR] [--repo-root DIR]
                                 [--workspace DIR] [--allow TARGET ...]

Exits non-zero when any real broken reference is found.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

DEFAULT_ROOT = ".claude/skills/sdlc-studio"

# Illustrative link examples that are not real references.
DEFAULT_ALLOW = {"doc.md#section-name"}

_ID_RE = re.compile(r"\{#([\w-]+)\}")
_HEADING_RE = re.compile(r"^#{1,6}\s+(.*)")
_REF_RE = re.compile(r"([\w./-]+\.md)#([\w-]+)")
# Any markdown link to a `.md` file (anchored or not) - used by the root-docs file pass.
# The skill tree is NOT scanned this way: its templates and doc examples carry many legitimate
# non-resolving bare links (`../prd.md`, `path/to/guide.md`), so only anchored intra-skill
# references are checked there. Root docs (README, AGENTS, ...) link to real files.
_LINK_RE = re.compile(r"\]\(([\w./-]+\.md)(?:#[\w-]+)?\)")

# Repo-root docs that link into the skill (and each other) but sit outside the skill tree,
# so the skill-scoped scan never saw them.
ROOT_DOCS = ("README.md", "AGENTS.md", "CLAUDE.md", "CONTRIBUTING.md",
             "SECURITY.md", "INSTALL.md", "CHANGELOG.md")


def slug(text: str) -> str:
    """GitHub-style heading slug (after stripping any explicit {#id})."""
    text = _ID_RE.sub("", text).strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"\s+", "-", text)


def index_anchors(root: Path) -> tuple[dict[str, set[str]], set[str]]:
    """Map each markdown file (relpath) to its anchors; return (anchors, files)."""
    anchors: dict[str, set[str]] = {}
    files: set[str] = set()
    for path in root.rglob("*.md"):
        rel = str(path.relative_to(root))
        files.add(rel)
        found: set[str] = set()
        for line in path.read_text(encoding="utf-8").splitlines():
            found.update(_ID_RE.findall(line))
            m = _HEADING_RE.match(line)
            if m:
                found.add(slug(m.group(1)))
        anchors[rel] = found
    return anchors, files


def _candidates(src: str, tgt: str) -> list[str]:
    """Root-relative paths a reference might mean: file-relative, then root-relative.

    The skill mixes conventions: a `help/x.md` file may link `../reference-y.md`
    (relative to itself) or `reference-y.md` (relative to the skill root). A
    reference resolves if either reading lands on a real file. Candidates that
    normalise above the root are dropped (out of skill scope, not our concern).
    """
    out: list[str] = []
    for cand in (os.path.normpath(os.path.join(os.path.dirname(src), tgt)),
                 os.path.normpath(tgt)):
        cand = cand.replace(os.sep, "/")
        if not cand.startswith("..") and cand not in out:
            out.append(cand)
    return out


def check(root: Path, allow: set[str]) -> list[str]:
    """Return a list of human-readable broken-reference messages."""
    anchors, files = index_anchors(root)
    broken: list[str] = []
    seen: set[tuple[str, int, str, str]] = set()
    for path in root.rglob("*.md"):
        src = str(path.relative_to(root))
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for tgt, anc in _REF_RE.findall(line):
                if f"{tgt}#{anc}" in allow or f"{os.path.normpath(tgt)}#{anc}" in allow:
                    continue
                key = (src, i, tgt, anc)
                if key in seen:
                    continue
                seen.add(key)
                cands = _candidates(src, tgt)
                if not cands:
                    continue  # resolves outside the skill root; out of scope
                existing = [c for c in cands if c in files]
                if not existing:
                    broken.append(f"{src}:{i} -> {tgt}#{anc} [file missing]")
                elif not any(anc in anchors[c] for c in existing):
                    broken.append(f"{src}:{i} -> {tgt}#{anc} [anchor missing]")
    return sorted(broken)


def check_index_links(workspace: Path) -> list[str]:
    """File-existence for the workspace indexes' row links (`sdlc-studio/**/_index.md`
    plus the `archive/` sub-indexes).

    The gap this closes: an index row is a link to an artefact file, and nothing checked
    that the file was there. The skill scan sees only the skill tree and the root-docs
    scan only the root docs, so a row pointing at a deleted artefact resolved nowhere and
    was reported by nobody - the index went on advertising an artefact that is not there.

    An `archive/` sub-index row is read against the type directory as well as its own:
    archiving moves the ROW into `<type>/archive/<release>/` and leaves the FILE in
    `<type>/`, so the row carries the live index's bare filename. Returns [] when the
    workspace does not exist (a consuming repo need not have one).
    """
    broken: list[str] = []
    if not workspace.is_dir():
        return broken
    for path in sorted(workspace.rglob("*.md")):
        parts = path.relative_to(workspace).parts
        if path.name != "_index.md" and "archive" not in parts:
            continue  # artifact bodies are not index rows; only the indexes are checked
        type_dir = workspace / parts[0] if len(parts) > 1 else path.parent
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.lstrip().startswith("|"):
                continue  # a row link, not the index's prose links
            for tgt in _LINK_RE.findall(line):
                if (path.parent / tgt).exists():
                    continue
                if "archive" in parts and (type_dir / tgt).exists():
                    continue  # the row was archived; the file stayed in the type dir
                rel = path.relative_to(workspace.parent).as_posix()
                broken.append(f"{rel}:{i} -> {tgt} [file missing]")
    return sorted(broken)


def check_root_docs(repo_root: Path) -> list[str]:
    """File-existence for the repo-root docs' markdown links (README, AGENTS, CLAUDE, ...).
    These sit outside the skill tree, so the skill scan never saw them; a link is checked
    against the linking file's own directory (root-relative), anchors ignored (root docs
    rarely target a cross-file anchor)."""
    broken: list[str] = []
    for name in ROOT_DOCS:
        path = repo_root / name
        if not path.exists():
            continue
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for tgt in _LINK_RE.findall(line):
                if not (path.parent / tgt).exists():
                    broken.append(f"{name}:{i} -> {tgt} [file missing]")
    return sorted(broken)


def main(argv: list[str] | None = None) -> int:
    """Parse arguments, run the check, and report."""
    p = argparse.ArgumentParser(
        prog="check_links.py",
        description="Verify intra-skill markdown anchor links resolve.",
    )
    p.add_argument("--root", default=DEFAULT_ROOT, help=f"Skill root (default: {DEFAULT_ROOT})")
    p.add_argument("--repo-root", dest="repo_root", default=None,
                   help="Repo root for the root-docs pass (default: inferred from --root)")
    p.add_argument("--workspace", default=None,
                   help="SDLC workspace whose index-row links are file-checked "
                        "(default: <repo-root>/sdlc-studio; skipped when absent)")
    p.add_argument("--allow", action="append", default=[],
                   help="Additional allowlisted `file.md#anchor` target (repeatable)")
    args = p.parse_args(argv)

    root = Path(args.root)
    if not root.exists():
        print(f"error: root does not exist: {root}", file=sys.stderr)
        return 2
    # The repo root is where the root docs live: given explicitly, or inferred by walking up
    # from the skill root past `.claude/skills/<name>` (three levels) when that shape holds.
    if args.repo_root is not None:
        repo_root = Path(args.repo_root)
    elif root.name == "sdlc-studio" and root.parent.name == "skills":
        repo_root = root.parents[2]
    else:
        repo_root = Path(".")
    workspace = Path(args.workspace) if args.workspace else repo_root / "sdlc-studio"
    allow = set(DEFAULT_ALLOW) | set(args.allow)
    broken = check(root, allow) + check_root_docs(repo_root) + check_index_links(workspace)
    if broken:
        print(f"Broken markdown links ({len(broken)}):")
        for b in broken:
            print(f"  {b}")
        return 1
    print("All markdown links resolve (anchors, root docs, index rows).")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001 - top-level guard
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
