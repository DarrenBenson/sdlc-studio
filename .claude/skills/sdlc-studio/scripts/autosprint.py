#!/usr/bin/env python3
"""SDLC Studio autosprint - batch selection and ordering (RFC0001 WS2).

`autosprint plan` selects a batch of work by query (open bugs, proposed CRs, ready
stories) and orders it, so the operator sees the triage plan before the run starts.
Ordering is by priority/severity (Critical first); dependency-topological; and WSJF
(`--order wsjf`): priority stays the dominant axis and the cognitive complexity of the
files a unit will touch (its `Affects`, scored by complexity.py - RFC0009 WS3) breaks
ties within a priority, so the smaller blast-radius job goes first. Complexity never
overrides priority, and the order degrades to plain priority when no complexity is
known. The plan also carries a complexity-weighted per-unit token budget. Read-only;
pure stdlib (complexity is a sibling helper).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402
import complexity  # noqa: E402  (sibling - blast-radius complexity for WSJF, RFC0009 WS3)

PRIORITY_FIELD = {"bug": "Severity", "cr": "Priority", "story": "Priority"}
PRIORITY_WEIGHT = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
BASE_TOKEN_BUDGET = 50_000        # per-unit floor (RFC0009 WS3)
TOKENS_PER_COGNITIVE = 5_000      # added per point of blast-radius cognitive complexity


def _affects_files(text: str) -> list[str]:
    """File paths a unit declares it will touch (its `Affects` field)."""
    val = sdlc_md.extract_field(text, "Affects") or ""
    files = []
    for tok in val.split(","):
        tok = re.sub(r"\s*\(.*\)\s*$", "", tok.strip()).strip().strip("`").strip()
        if tok and ("/" in tok or tok.endswith((".py", ".md", ".yaml", ".yml", ".sh"))):
            files.append(tok)
    return files


def _resolve(root: Path, p: str) -> Path | None:
    """Resolve an Affects path against the repo root or the installed skill dir."""
    for base in (root, root / ".claude" / "skills" / "sdlc-studio"):
        cand = base / p
        if cand.exists():
            return cand
    return None


def _complexity_size(root: Path, text: str) -> int:
    """Max cognitive complexity across the files a unit will touch (0 if none resolve)."""
    paths = [str(r) for p in _affects_files(text) if (r := _resolve(root, p))]
    if not paths:
        return 0
    try:
        return complexity.assess(root, paths)["max_cognitive"]
    except Exception:  # noqa: BLE001 - WSJF must degrade to priority, never break planning
        return 0


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
        it = by_id[k]
        w = PRIORITY_WEIGHT.get(it["priority"], 2)
        if "complexity" in it:  # wsjf: priority first, then the smaller blast-radius job
            return (w, it["complexity"], it["id"])
        return (w, it["id"])

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
    if order == "wsjf":  # priority-primary; smaller blast-radius job as the tiebreak (RFC0009 WS3)
        for it in out:
            size = _complexity_size(root, Path(it["path"]).read_text(encoding="utf-8"))
            it["complexity"] = size
            it["token_budget"] = BASE_TOKEN_BUDGET + TOKENS_PER_COGNITIVE * size
    if order in ("priority", "wsjf"):
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
