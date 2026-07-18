#!/usr/bin/env python3
"""Authoring lint: a story's ACs should be satisfiable within its own epic.

When stories are fanned out per epic, an agent authoring epic E can write an acceptance
criterion that quietly depends on epic F's capability (e.g. an EP0001 auth story asserting
"a valid *account* token resolves a userId" - accounts are EP0006). Such a story is
structurally un-Done-able in its own epic. This flags, advisory and heuristic, any AC that
mentions a distinctive capability keyword owned by a *different* epic's title - so it can be
split or re-scoped at authoring time, before it becomes an un-passable AC (the symptom
the Done-gate catches downstream). A keyword owned only by a *terminal* epic is exempt - a
closed epic no longer owns live scope, so reusing its keyword in a new extension story is not a
leak. Never auto-edits; false positives are expected (it is a keyword heuristic) - the operator
decides. Pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402

# Generic words that are not a distinctive capability (drop so they never flag).
_STOP = {"and", "the", "for", "with", "management", "system", "foundation", "platform",
         "support", "feature", "features", "power", "core", "experience", "client",
         "service", "services", "data", "user", "users", "from", "into", "this", "that"}

# A distinctive title keyword that turns up in the ACs of stories across this many or more
# distinct epics is shared domain vocabulary (e.g. "list", "item"), not epic-specific leakage,
# so it is suppressed - it would otherwise cry wolf on every story that mentions it. CR0113.
_SHARED_EPIC_THRESHOLD = 3

# A story-count ("document frequency") suppression was tried here and REMOVED. It counted the
# owning epic's own stories, and an epic's backlog is exactly where its title vocabulary
# appears - so three sibling stories were enough to drop the keyword from `distinctive`
# entirely, deleting a genuine multi-keyword leak before its strength was ever computed. It
# also demoted nothing this repo did not already demote: 11 findings before, the same 11
# after. `_SHARED_EPIC_THRESHOLD` counts DISTINCT EPICS, which discounts the owner, and it is
# the only frequency signal here for that reason.

# How many DISTINCT owner keywords a story must name before the hit is treated as evidence
# rather than a coincidence. One shared English word is the false-positive case this heuristic
# generates constantly; two or more independent keywords from the same epic title is a pattern.
_BLOCKING_STRENGTH = 2


def _keywords(title: str) -> set[str]:
    return {w for w in re.findall(r"[a-z]+", title.lower()) if len(w) > 3 and w not in _STOP}


def _ac_block(text: str) -> str:
    """The Acceptance Criteria section body (where a cross-epic reference is a real defect)."""
    lines = text.splitlines()
    start = next((i for i, ln in enumerate(lines)
                  if ln.strip().lower().startswith("## acceptance criteria")), None)
    if start is None:
        return ""
    end = next((j for j in range(start + 1, len(lines)) if lines[j].startswith("## ")), len(lines))
    return "\n".join(lines[start + 1:end]).lower()


def _mentions(block: str, kw: str) -> bool:
    """Whether the AC block names the keyword, matching singular/plural (account[s])."""
    stem = kw[:-1] if kw.endswith("s") else kw
    return bool(re.search(rf"\b{re.escape(stem)}s?\b", block))


def check(repo_root: Path | str) -> list[dict]:
    root = Path(repo_root)
    # epic id -> distinctive keywords (owned by exactly one epic)
    epic_kw: dict[str, set[str]] = {}
    titles: dict[str, str] = {}
    terminal_epics: set[str] = set()  # closed epics own no live scope
    epic_vocab = sdlc_md.status_vocab("epic", root)
    for path in sdlc_md.artifact_files("epic", root):
        rec = sdlc_md.extract_record_id(path.stem)
        if not rec:
            continue
        text = path.read_text(encoding="utf-8")
        m = re.search(r"^#\s+\S+:\s*(.+?)\s*$", text, re.M)
        title = m.group(1) if m else ""
        eid = sdlc_md.norm_id(rec)
        titles[eid] = title
        epic_kw[eid] = _keywords(title)
        status = sdlc_md.canonical_status(sdlc_md.extract_field(text, "Status"), epic_vocab)
        if status and sdlc_md.is_terminal_status("epic", status):
            terminal_epics.add(eid)
    owners: dict[str, set[str]] = {}
    for eid, kws in epic_kw.items():
        for kw in kws:
            owners.setdefault(kw, set()).add(eid)
    # A keyword whose SOLE owning epic is terminal is exempt: a closed epic no longer owns
    # live scope, so reusing its keyword in a new extension story is not a cross-epic leak.
    distinctive = {kw: next(iter(es)) for kw, es in owners.items()
                   if len(es) == 1 and next(iter(es)) not in terminal_epics}

    # First pass: read each story's AC block once, keyed by its own epic.
    stories: list[tuple[str | None, str, str | None]] = []  # (own_eid, ac_block, record_id)
    for path in sdlc_md.artifact_files("story", root):
        text = path.read_text(encoding="utf-8")
        own = sdlc_md.extract_field(text, "Epic") or ""
        m = sdlc_md.ID_SEARCH_RE.search(own)
        own_eid = sdlc_md.norm_id(m.group(0)) if m else None
        block = _ac_block(text)
        if not block:
            continue
        stories.append((own_eid, block, sdlc_md.extract_record_id(path.stem)))

    # Document frequency: how many distinct epics own a story whose AC names the keyword.
    # A distinctive title keyword spread across many epics is shared domain vocabulary - drop it.
    epics_mentioning: dict[str, set[str | None]] = {}
    for own_eid, block, _ in stories:
        for kw in distinctive:
            if _mentions(block, kw):
                epics_mentioning.setdefault(kw, set()).add(own_eid)
    distinctive = {kw: owner for kw, owner in distinctive.items()
                   if len(epics_mentioning.get(kw, set())) < _SHARED_EPIC_THRESHOLD}

    findings: list[dict] = []
    for own_eid, block, rec_id in stories:
        hits = set()
        for kw, owner_eid in distinctive.items():
            if owner_eid == own_eid:
                continue
            if _mentions(block, kw):
                hits.add((kw, owner_eid))
        # Strength is per (story, owner epic): how many independent keywords from the SAME
        # epic title this story names. One is a word in common; several is a pattern.
        strength: dict[str, int] = {}
        for kw, owner_eid in hits:
            strength[owner_eid] = strength.get(owner_eid, 0) + 1
        for kw, owner_eid in sorted(hits):
            n = strength[owner_eid]
            findings.append({"story": rec_id, "keyword": kw,
                             "owner_epic": owner_eid, "owner_title": titles.get(owner_eid, ""),
                             "strength": n, "advisory": n < _BLOCKING_STRENGTH})
    return findings


def cmd_check(args: argparse.Namespace) -> int:
    findings = check(args.root)
    if args.format == "json":
        print(json.dumps(findings, indent=2))
        return 0  # advisory: never fail the build
    for f in findings:
        print(f"  {f['story']}: AC references '{f['keyword']}' owned by {f['owner_epic']}"
              f" ({f['owner_title']}) - split or re-scope to the owning epic")
    print(f"ac-scope: {len(findings)} cross-epic AC reference(s) (advisory, heuristic)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Cross-epic AC scope lint (advisory).")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="Flag ACs referencing a capability owned by another epic.")
    c.add_argument("--root", default=".")
    c.add_argument("--format", choices=("text", "json"), default="text")
    c.set_defaults(func=cmd_check)
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
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
