#!/usr/bin/env python3
"""SDLC Studio autosprint - batch selection and ordering (RFC0001 WS2).

`autosprint plan` selects a batch of work by query (open bugs, proposed CRs, ready
stories) and orders it, so the operator sees the triage plan before the run starts.
Ordering is by priority/severity (Critical first); dependency-topological and WSJF
(priority over RFC0009 complexity) are layered later - `--order wsjf` currently
falls back to priority until the complexity signal exists. Read-only; pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402

PRIORITY_FIELD = {"bug": "Severity", "cr": "Priority", "story": "Priority"}
PRIORITY_WEIGHT = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}


def _dep_ids(value: str) -> set:
    """The leading artifact-ID tokens of a `Depends on` field, normalised.

    Stops at the first non-ID word, so prose like "see CR0001 for background" or
    "supersedes CR0001" does not become a hard ordering dependency. Handles
    comma/space-separated lists and a trailing parenthetical (`CR0003 (note)`).
    """
    ids: set = set()
    for tok in re.split(r"[,\s]+", value.strip()):
        if not tok:
            continue
        m = sdlc_md.ID_RE.match(tok)  # anchored at the start of the token
        if not m:
            break  # first non-ID token ends the dependency list
        ids.add(sdlc_md.norm_id(m.group(0)))
    return ids


def _topo_order(items: list[dict], deps: dict[str, set]) -> list[dict]:
    """Dependency-topological order - a unit follows its in-batch deps - with
    priority/severity (then id) as the tiebreak among ready units. A dependency on
    a unit outside the batch is ignored here (the tranche audit reports it as
    unmet-deps). Raises ValueError naming the units in a dependency cycle.
    """
    by_id = {sdlc_md.norm_id(it["id"]): it for it in items}
    adj: dict[str, set] = {k: set() for k in by_id}
    indeg: dict[str, int] = {k: 0 for k in by_id}
    for k in by_id:
        for dep in deps.get(k, ()):
            if dep in by_id and dep != k and k not in adj[dep]:
                adj[dep].add(k)        # dep must come before k
                indeg[k] += 1

    def rank(k: str):
        return (PRIORITY_WEIGHT.get(by_id[k]["priority"], 2), by_id[k]["id"])

    ready = sorted([k for k in by_id if indeg[k] == 0], key=rank)
    order: list[dict] = []
    while ready:
        k = ready.pop(0)
        order.append(by_id[k])
        for m in adj[k]:
            indeg[m] -= 1
            if indeg[m] == 0:
                ready.append(m)
        ready.sort(key=rank)
    if len(order) != len(by_id):
        raise ValueError("dependency cycle among: " + ", ".join(sorted(k for k in by_id if indeg[k] > 0)))
    return order


def select_batch(repo_root: Path | str, kind: str, status: str, order: str = "priority") -> list[dict]:
    """Files of `kind` whose Status matches, with priority, ordered.

    `priority`/`wsjf` order deps-first (topological) with priority as the tiebreak;
    `manual` preserves discovery order.
    """
    root = Path(repo_root)
    vocab = sdlc_md.status_vocab(kind, root)
    out: list[dict] = []
    deps: dict[str, set] = {}
    for path in sdlc_md.artifact_files(kind, root):
        text = path.read_text(encoding="utf-8")
        st = sdlc_md.canonical_status(sdlc_md.extract_field(text, "Status"), vocab) or "Unknown"
        if st != status:
            continue
        pri = sdlc_md.extract_field(text, PRIORITY_FIELD.get(kind, "Priority")) or "Medium"
        rid = sdlc_md.extract_record_id(path.stem) or path.stem
        dval = sdlc_md.extract_field(text, "Depends on") or sdlc_md.extract_field(text, "Depends On") or ""
        deps[sdlc_md.norm_id(rid)] = _dep_ids(dval)
        out.append({"id": rid, "type": kind, "status": st, "priority": pri, "path": str(path)})
    if order in ("priority", "wsjf"):  # wsjf falls back to priority until RFC0009 ships complexity
        out = _topo_order(out, deps)
    return out


def build_plan(repo_root: Path | str, kind: str, status: str, order: str = "priority") -> dict:
    """The triage plan: the ordered batch plus a count."""
    batch = select_batch(repo_root, kind, status, order)
    return {
        "generated_at": sdlc_md.now_iso8601(),
        "kind": kind,
        "status": status,
        "order": order,
        "batch": batch,
        "count": len(batch),
    }


def cmd_plan(args: argparse.Namespace) -> int:
    """Print the ordered batch the operator approves before a run."""
    if args.bugs is not None:
        kind, status = "bug", args.bugs
    elif args.crs is not None:
        kind, status = "cr", args.crs
    elif args.stories is not None:
        kind, status = "story", args.stories
    else:  # pragma: no cover - argparse marks the group required
        print("specify one of --bugs/--crs/--stories <STATUS>", file=sys.stderr)
        return 2
    try:
        data = build_plan(args.root, kind, status, args.order)
    except ValueError as exc:  # dependency cycle
        print(f"cannot order the batch: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(data, indent=2))
    else:
        print(f"batch: {data['count']} {kind}(s) with Status {status}, order={args.order}")
        for b in data["batch"]:
            print(f"  {b['id']} [{b['priority']}]")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SDLC Studio autosprint batch selection.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan", help="Select and order a batch of work (the triage plan).")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--bugs", metavar="STATUS", help="Bugs with this Status (e.g. Open)")
    g.add_argument("--crs", metavar="STATUS", help="CRs with this Status (e.g. Proposed)")
    g.add_argument("--stories", metavar="STATUS", help="Stories with this Status (e.g. Ready)")
    p.add_argument("--order", choices=("priority", "wsjf", "manual"), default="priority")
    p.add_argument("--root", default=".", help="Repo root (default: .)")
    p.add_argument("--format", choices=("text", "json"), default="text")
    p.set_defaults(func=cmd_plan)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
