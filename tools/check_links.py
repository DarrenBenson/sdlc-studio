#!/usr/bin/env python3
"""Check that markdown links resolve - anchors AND relative file targets.

A skill-development CI tool (it lives in tools/, not in the runtime scripts/
directory). Four passes:

1. skill tree: every `{#anchor}` (on any line - the skill attaches anchors to
   non-heading lines too) plus implicit heading slugs are indexed, then every
   `path.md#anchor` reference is checked to point at a file and anchor that
   exist. Illustrative examples (e.g. `doc.md#section-name` in the documentation
   style guide) are allowlisted.
2. root docs (README, AGENTS, ...): their `.md` links must name a real file.
3. workspace indexes (`sdlc-studio/**/_index.md`): an index row LINKS an
   artefact file, and that file must exist. Validating anchors alone let a row
   point at a deleted artefact and still pass.
4. workspace artefact BODIES (everything else under `sdlc-studio/`): a
   cross-reference inside an artefact - a test spec's Stories Covered table, a
   Traceability row, a bug's Affects link - must name a real file too.

Why pass 4 is scoped to the workspace and NOT to the skill tree: the skill tree
is PAYLOAD. Its templates and best-practice guides deliberately ship links that
resolve in a CONSUMING project rather than here (`../epics/EP{{epic_id}}-...md`,
`path/to/guide.md`, `../prd.md`) - 56 of them. Flagging those would make the
guard cry wolf on its own product, and a guard that cries wolf is one people
learn to ignore. The workspace, by contrast, is real artefacts whose links a
reader actually clicks on GitHub, so every one of them must resolve.

Usage:
    python3 tools/check_links.py [--root DIR] [--repo-root DIR]
                                 [--workspace DIR] [--allow TARGET ...]
                                 [--allow-body "SRC -> TARGET" ...]

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

# Body links (pass 4) that are deliberately unresolvable, keyed "<src> -> <target>" where
# <src> is the artefact's path relative to the workspace. Empty by default and meant to stay
# that way: a workspace artefact's links are navigation a reader clicks, so the honest remedy
# for a broken one is to fix the link, not to silence the guard. The hook exists only so a
# genuinely illustrative link (a bug report QUOTING the broken link it reports) can be named
# out loud rather than quietly weakening the pass's scope.
DEFAULT_BODY_ALLOW: set[str] = set()

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

    Every row link - live index or `archive/` sub-index - is resolved RELATIVE TO THE FILE
    IT SITS IN, which is what a reader's click does. An archived row therefore has to climb
    to the type directory (`../../x.md`), because archiving moves the ROW into
    `<type>/archive/<release>/` and leaves the FILE in `<type>/`. This pass once read an
    archived row against the type directory as well, which passed the wrong-depth bare
    filenames the archiver used to copy across verbatim - 361 rows that all 404ed. Returns
    [] when the workspace does not exist (a consuming repo need not have one).
    """
    broken: list[str] = []
    if not workspace.is_dir():
        return broken
    for path in sorted(workspace.rglob("*.md")):
        parts = path.relative_to(workspace).parts
        if path.name != "_index.md" and "archive" not in parts:
            continue  # artifact bodies are not index rows; only the indexes are checked
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.lstrip().startswith("|"):
                continue  # a row link, not the index's prose links
            for tgt in _LINK_RE.findall(line):
                if (path.parent / tgt).exists():
                    continue
                rel = path.relative_to(workspace.parent).as_posix()
                broken.append(f"{rel}:{i} -> {tgt} [file missing]")
    return sorted(broken)


_FENCE_RE = re.compile(r"^\s*(```|~~~)")
_SPAN_RE = re.compile(r"`[^`]*`")


def _without_code(text: str) -> list[str]:
    """The document's lines with every fenced block and inline code span blanked out.

    A link inside backticks or a fence is an EXAMPLE, not a reference. Without this, an
    artefact cannot DOCUMENT a broken link - and a bug report about broken links must quote
    the broken link it reports (BG0137 does exactly that, and failed the gate on it).

    Line COUNT is preserved, never collapsed, so a reported line number still points at the
    line the reader will open.
    """
    out: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if _FENCE_RE.match(line):
            in_fence = not in_fence
            out.append("")
            continue
        out.append("" if in_fence else _SPAN_RE.sub("", line))
    return out


def check_body_links(workspace: Path, allow: set[str]) -> list[str]:
    """File-existence for the relative `.md` links inside workspace artefact BODIES.

    The gap this closes: pass 3 reads index ROWS. An artefact's own cross-references - the
    Stories Covered table in a test spec, a Traceability row, an Affects link - were scanned
    by nobody, so an artefact could carry dead references indefinitely. TS0001 did: 13 links
    written `../../stories/...` from `test-specs/`, one level too deep, every one a 404.

    Scope: every `*.md` under the workspace EXCEPT `_index.md` and anything under an
    `archive/` directory - those are pass 3's rows, and double-reporting them would be noise.
    The skill tree is not touched at all (see the module docstring: it is payload).

    Each link is resolved RELATIVE TO THE FILE IT SITS IN, which is what a reader's click
    does. Anchors are ignored; only the file must exist. Returns [] when the workspace does
    not exist (a consuming repo need not have one).
    """
    broken: list[str] = []
    if not workspace.is_dir():
        return broken
    for path in sorted(workspace.rglob("*.md")):
        rel_parts = path.relative_to(workspace).parts
        if path.name == "_index.md" or "archive" in rel_parts:
            continue  # index rows and archived rows belong to check_index_links
        src = path.relative_to(workspace).as_posix()
        for i, line in enumerate(_without_code(path.read_text(encoding="utf-8")), 1):
            for tgt in _LINK_RE.findall(line):
                if f"{src} -> {tgt}" in allow:
                    continue
                if (path.parent / tgt).exists():
                    continue
                rel = path.relative_to(workspace.parent).as_posix()
                broken.append(f"{rel}:{i} -> {tgt} [file missing]")
    return sorted(broken)


def inbound_references(repo_root: Path | str, target_name: str,
                       workspace: Path | str | None = None) -> list[dict]:
    """Every markdown link across the SDLC workspace that resolves to the artefact file
    `target_name` (a bare filename, e.g. `CR0001-foo.md`), for a retitle to rewrite or name.

    Each item: {"path": abspath, "rel": path relative to the repo root, "line": 1-based,
    "target": the link's `.md` target, "immutable": bool}. `immutable` marks a reference the
    retitle must NOT rewrite - a row in an `archive/<release>/` sub-index, which archive.py
    alone owns; the caller refuses the retitle and names it rather than leaving it dangling.

    Two exclusions keep the scan to references a retitle is responsible for: the live
    `_index.md` of a type (the retitle updates the target's own row through reconcile, not
    here) and the target file itself. Fenced and inline-code links are ignored (they are
    examples, not references), matching the body-link pass. Returns [] when the workspace
    does not exist - a consuming repo need not have one."""
    root = Path(repo_root)
    ws = Path(workspace) if workspace else root / "sdlc-studio"
    out: list[dict] = []
    if not ws.is_dir():
        return out
    for path in sorted(ws.rglob("*.md")):
        parts = path.relative_to(ws).parts
        in_archive = "archive" in parts
        if path.name == "_index.md" and not in_archive:
            continue  # the live index is reconcile's domain (the retitle syncs it there)
        if path.name == target_name:
            continue  # the artefact itself
        for i, line in enumerate(_without_code(path.read_text(encoding="utf-8")), 1):
            for tgt in _LINK_RE.findall(line):
                if Path(tgt).name == target_name:
                    out.append({"path": str(path),
                                "rel": path.relative_to(root).as_posix(),
                                "line": i, "target": tgt, "immutable": in_archive})
    return out


_INBOUND_LINK_RE = re.compile(r"(\]\()([\w./-]+\.md)(#[\w-]+)?(\))")


def rewrite_inbound_links(text: str, old_name: str, new_name: str) -> tuple[str, int]:
    """`text` with every markdown link whose target basename is `old_name` repointed to
    `new_name`, preserving each link's directory prefix and anchor. Returns (new_text, n)
    where n counts the lines changed.

    Fenced blocks and inline-code spans are left untouched, so an example link that quotes
    the old filename survives a rename - the same code-blindness `inbound_references` uses to
    find them, so the finder and the rewriter agree about which references are real."""
    def _sub(seg: str) -> str:
        def repl(m: re.Match) -> str:
            inner = m.group(2)
            if Path(inner).name != old_name:
                return m.group(0)
            prefix = inner[: len(inner) - len(old_name)]
            return f"{m.group(1)}{prefix}{new_name}{m.group(3) or ''}{m.group(4)}"
        return _INBOUND_LINK_RE.sub(repl, seg)

    out: list[str] = []
    in_fence = False
    changed = 0
    for line in text.splitlines():
        if _FENCE_RE.match(line):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue
        # rewrite only the segments OUTSIDE inline code spans (odd `-split indices are code)
        segs = line.split("`")
        line_changed = False
        for k in range(0, len(segs), 2):
            new_seg = _sub(segs[k])
            if new_seg != segs[k]:
                segs[k] = new_seg
                line_changed = True
        out.append("`".join(segs))
        if line_changed:
            changed += 1
    new_text = "\n".join(out)
    if text.endswith("\n"):
        new_text += "\n"
    return new_text, changed


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
    p.add_argument("--allow-body", dest="allow_body", action="append", default=[],
                   help="Allowlist a deliberately unresolvable body link, given as "
                        "\"<path-in-workspace> -> <target>\" (repeatable)")
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
    body_allow = set(DEFAULT_BODY_ALLOW) | set(args.allow_body)
    broken = (check(root, allow) + check_root_docs(repo_root)
              + check_index_links(workspace) + check_body_links(workspace, body_allow))
    if broken:
        print(f"Broken markdown links ({len(broken)}):")
        for b in broken:
            print(f"  {b}")
        return 1
    print("All markdown links resolve (anchors, root docs, index rows, artefact bodies).")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001 - top-level guard
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
