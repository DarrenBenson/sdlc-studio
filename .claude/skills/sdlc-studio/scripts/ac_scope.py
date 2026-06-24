#!/usr/bin/env python3
"""Authoring lint: a story's ACs should be satisfiable within its own epic (CR0086).

When stories are fanned out per epic, an agent authoring epic E can write an acceptance
criterion that quietly depends on epic F's capability (e.g. an EP0001 auth story asserting
"a valid *account* token resolves a userId" - accounts are EP0006). Such a story is
structurally un-Done-able in its own epic. This flags, advisory and heuristic, any AC that
mentions a distinctive capability keyword owned by a *different* epic's title - so it can be
split or re-scoped at authoring time, before it becomes an un-passable AC (the symptom
CR0084 catches downstream). Never auto-edits; false positives are expected (it is a keyword
heuristic) - the operator decides. Pure stdlib.
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


def check(repo_root: Path | str) -> list[dict]:
    root = Path(repo_root)
    # epic id -> distinctive keywords (owned by exactly one epic)
    epic_kw: dict[str, set[str]] = {}
    titles: dict[str, str] = {}
    for path in sdlc_md.artifact_files("epic", root):
        rec = sdlc_md.extract_record_id(path.stem)
        if not rec:
            continue
        m = re.search(r"^#\s+\S+:\s*(.+?)\s*$", path.read_text(encoding="utf-8"), re.M)
        title = m.group(1) if m else ""
        titles[sdlc_md.norm_id(rec)] = title
        epic_kw[sdlc_md.norm_id(rec)] = _keywords(title)
    owners: dict[str, set[str]] = {}
    for eid, kws in epic_kw.items():
        for kw in kws:
            owners.setdefault(kw, set()).add(eid)
    distinctive = {kw: next(iter(es)) for kw, es in owners.items() if len(es) == 1}

    findings: list[dict] = []
    for path in sdlc_md.artifact_files("story", root):
        text = path.read_text(encoding="utf-8")
        own = sdlc_md.extract_field(text, "Epic") or ""
        m = sdlc_md.ID_SEARCH_RE.search(own)
        own_eid = sdlc_md.norm_id(m.group(0)) if m else None
        block = _ac_block(text)
        if not block:
            continue
        hits = set()
        for kw, owner_eid in distinctive.items():
            if owner_eid == own_eid:
                continue
            root = kw[:-1] if kw.endswith("s") else kw   # match singular/plural (account[s])
            if re.search(rf"\b{re.escape(root)}s?\b", block):
                hits.add((kw, owner_eid))
        for kw, owner_eid in sorted(hits):
            findings.append({"story": sdlc_md.extract_record_id(path.stem), "keyword": kw,
                             "owner_epic": owner_eid, "owner_title": titles.get(owner_eid, "")})
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
    p = argparse.ArgumentParser(description="Cross-epic AC scope lint (CR0086, advisory).")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="Flag ACs referencing a capability owned by another epic.")
    c.add_argument("--root", default=".")
    c.add_argument("--format", choices=("text", "json"), default="text")
    c.set_defaults(func=cmd_check)
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
