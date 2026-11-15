"""Inbound markdown references to a workspace artefact: finding them and repointing them.

A retitle renames an artefact's file, so every relative `.md` link that resolves to the old
filename must be found first and rewritten after. Both halves live here, in the shipped
runtime, so an installed skill with no repository around it can rename an artefact without
leaving a link dangling. The skill's own source repository runs its link checker on these
same functions, so the checker and the retitle agree about which links are references.

A link inside a fenced block or an inline code span is an example, not a reference: the
finder skips it and the rewriter leaves it alone. Fences are read with `sdlc_md.fence_step`,
the CommonMark fence rule `lib/sdlc_md.py` owns.

Pure functions: this module reads the workspace and returns text; it writes nothing. Usage:

    from lib import link_refs
    refs = link_refs.inbound_references(repo_root, "CR0001-old-title.md")
    new_text, n = link_refs.rewrite_inbound_links(text, "CR0001-old-title.md", "CR0001-new.md")
"""
from __future__ import annotations

import re
from pathlib import Path

from . import sdlc_md

# Any markdown link to a `.md` file, anchored or not; group 1 is the target without its anchor.
LINK_RE = re.compile(r"\]\(([\w./-]+\.md)(?:#[\w-]+)?\)")

# The same link split into the parts a rewrite keeps: `](`, the target, the anchor, `)`.
_INBOUND_LINK_RE = re.compile(r"(\]\()([\w./-]+\.md)(#[\w-]+)?(\))")

_SPAN_RE = re.compile(r"`[^`]*`")


def without_code(text: str) -> list[str]:
    """The document's lines with every fenced block and inline code span blanked out.

    A link inside backticks or a fence is an example, not a reference, so a document can
    quote a broken link without being reported for it. The line count is preserved, so a
    line number taken from the result still points at the line a reader opens."""
    out: list[str] = []
    fence = None
    for line in text.splitlines():
        fence, is_fence_line = sdlc_md.fence_step(line.lstrip(), fence)
        if is_fence_line or fence is not None:
            out.append("")
            continue
        out.append(_SPAN_RE.sub("", line))
    return out


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
    examples, not references). Returns [] when the workspace does not exist - a consuming
    repo need not have one."""
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
        for i, line in enumerate(without_code(path.read_text(encoding="utf-8")), 1):
            for tgt in LINK_RE.findall(line):
                if Path(tgt).name == target_name:
                    out.append({"path": str(path),
                                "rel": path.relative_to(root).as_posix(),
                                "line": i, "target": tgt, "immutable": in_archive})
    return out


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
    fence = None
    changed = 0
    for line in text.splitlines():
        fence, is_fence_line = sdlc_md.fence_step(line.lstrip(), fence)
        if is_fence_line or fence is not None:
            out.append(line)   # illustration: a rename never rewrites an example
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
