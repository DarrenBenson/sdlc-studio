#!/usr/bin/env python3
"""SDLC Studio sprint - batch selection and ordering.

`sprint plan` selects a batch of work by query (open bugs, proposed CRs, ready
stories) and orders it, so the operator sees the triage plan before the run starts.
Ordering is by priority/severity (Critical first); dependency-topological; and WSJF
(`--order wsjf`): priority stays the dominant axis and the cognitive complexity of the
files a unit will touch (its `Affects`, scored by complexity.py) breaks
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
import complexity  # noqa: E402  (sibling - blast-radius complexity for WSJF)
import reconcile  # noqa: E402  (sibling - reconcile before plan)
import blocker_sweep  # noqa: E402  (sibling - blocker sweep before plan)

PRIORITY_FIELD = {"bug": "Severity", "cr": "Priority", "story": "Priority"}
# One weight scale across types (documented in reference-sprint.md): bug Severity and
# CR/story Priority - including the P1-P4 form - map onto the same rank, so a merged
# bugs + CRs tranche orders on a single documented axis instead of two vocabularies.
PRIORITY_WEIGHT = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3,
                   "P1": 0, "P2": 1, "P3": 2, "P4": 3}
BASE_TOKEN_BUDGET = 50_000        # per-unit floor
TOKENS_PER_COGNITIVE = 5_000      # added per point of blast-radius cognitive complexity


def _weight(pri: str) -> int:
    """Shared cross-type rank of a Severity/Priority value (case-tolerant; decorations
    like `High (gate)` use the leading token). Unknown, blank, or absent values rank
    Medium - a half-filled template field must plan, never crash the planner."""
    toks = (pri or "").strip().split()
    if not toks:
        return 2
    tok = toks[0].rstrip(":,;")
    key = tok.upper() if re.fullmatch(r"[Pp]\d", tok) else tok.title()
    return PRIORITY_WEIGHT.get(key, 2)


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

    Stops at the first non-ID word, so prose like "see US0001 for background" or
    "supersedes US0001" does not become a hard ordering dependency. Handles
    comma/space-separated lists and a trailing parenthetical (`US0003 (note)`).
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


def _rank_key(it: dict):
    """Tiebreak order among ready units: highest WSJF first, else priority then the
    smaller blast-radius job, else priority then id. Shared by topo order + waves."""
    w = _weight(it["priority"])
    if "wsjf" in it:
        return (-it["wsjf"], w, it["id"])
    if "complexity" in it:
        return (w, it["complexity"], it["id"])
    return (w, it["id"])


def _build_dag(items: list[dict], deps: dict[str, set]) -> tuple[dict, dict, dict]:
    """(by_id, adjacency dep->dependents, indegree) over the in-batch dependency graph."""
    by_id = {sdlc_md.norm_id(it["id"]): it for it in items}
    adj: dict[str, set] = {k: set() for k in by_id}
    indeg: dict[str, int] = {k: 0 for k in by_id}
    for k in by_id:
        for dep in deps.get(k, ()):
            if dep in by_id and dep != k and k not in adj[dep]:
                adj[dep].add(k)        # dep must come before k
                indeg[k] += 1
    return by_id, adj, indeg


def _topo_waves(items: list[dict], deps: dict[str, set]) -> list[list[dict]]:
    """Dependency LEVELS: wave 0 = units with no in-batch deps; wave n+1 = units all of
    whose in-batch deps sit in waves <= n. Units in one wave are independent (parallelisable),
    ordered within the wave by `_rank_key`. Raises ValueError naming a dependency cycle."""
    by_id, adj, indeg = _build_dag(items, deps)
    waves: list[list[dict]] = []
    placed = 0
    current = sorted([k for k in by_id if indeg[k] == 0], key=lambda k: _rank_key(by_id[k]))
    while current:
        waves.append([by_id[k] for k in current])
        placed += len(current)
        nxt: list[str] = []
        for k in current:
            for m in adj[k]:
                indeg[m] -= 1
                if indeg[m] == 0:
                    nxt.append(m)
        current = sorted(nxt, key=lambda k: _rank_key(by_id[k]))
    if placed != len(by_id):
        raise ValueError("dependency cycle among: "
                         + ", ".join(sorted(k for k in by_id if indeg[k] > 0)))
    return waves


def _topo_order(items: list[dict], deps: dict[str, set]) -> list[dict]:
    """Dependency-topological order - a unit follows its in-batch deps - with
    priority/severity (then id) as the tiebreak among ready units. A dependency on
    a unit outside the batch is ignored here (the tranche audit reports it as
    unmet-deps). Raises ValueError naming the units in a dependency cycle.
    """
    by_id, adj, indeg = _build_dag(items, deps)

    def rank(k: str):
        return _rank_key(by_id[k])

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


def wsjf_score(value: float, time_criticality: float, risk_reduction: float, size: float) -> float:
    """WSJF = (value + time-criticality + risk-reduction) / job size. Size >= 1."""
    return round((value + time_criticality + risk_reduction) / max(size, 1), 3)


def _wsjf_inputs(root: Path) -> dict:
    """Per-unit value/time-criticality/risk-reduction the review seats scored, written
    to `sdlc-studio/.local/wsjf-inputs.json` by the model after the PO/Eng/QA consult. Keyed by
    normalised id. Absent -> {} -> the planner falls back to priority + complexity."""
    raw = sdlc_md.read_json(root / "sdlc-studio" / ".local" / "wsjf-inputs.json", {})
    return {sdlc_md.norm_id(k): v for k, v in raw.items()} if isinstance(raw, dict) else {}


def _collect(root: Path, kind: str, status: str,
             epic_filter: set | None) -> tuple[list[dict], dict[str, set]]:
    """One kind+status query: (items, in-batch dependency map)."""
    vocab = sdlc_md.status_vocab(kind, root)
    # canonicalise the user-supplied status arg so a lowercase '--crs proposed' (the
    # documented form) matches the title-case vocab token, instead of silently selecting nothing.
    target = sdlc_md.canonical_status(status, vocab) or status
    if vocab and target not in vocab:
        raise ValueError(
            f"status '{status}' is not a {kind} status; valid: {', '.join(vocab)}")
    out: list[dict] = []
    deps: dict[str, set] = {}
    for path in sdlc_md.artifact_files(kind, root):
        text = path.read_text(encoding="utf-8")
        st = sdlc_md.canonical_status(sdlc_md.extract_field(text, "Status"), vocab) or "Unknown"
        if st != target:
            continue
        if epic_filter is not None:  # scope to the named epic(s)
            ef = sdlc_md.extract_field(text, "Epic") or ""
            m = sdlc_md.ID_SEARCH_RE.search(ef)
            if not (m and sdlc_md.norm_id(m.group(0)) in epic_filter):
                continue
        out.append(_unit(kind, path, text, st, deps))
    return out, deps


def _unit(kind: str, path: Path, text: str, st: str, deps: dict[str, set]) -> dict:
    pri = sdlc_md.extract_field(text, PRIORITY_FIELD.get(kind, "Priority")) or "Medium"
    rid = sdlc_md.extract_record_id(path.stem) or path.stem
    dval = sdlc_md.extract_field(text, "Depends on") or sdlc_md.extract_field(text, "Depends On") or ""
    deps[sdlc_md.norm_id(rid)] = _dep_ids(dval)
    return {"id": rid, "type": kind, "status": st, "priority": pri, "path": str(path)}


def _worklist_units(root: Path, worklist: str) -> tuple[list[dict], dict[str, set]]:
    """The documented tranche-file batch source: one unit id per line (markdown
    bullets and `#` comment/heading lines are tolerated). Every id must resolve to
    an artifact on disk - a silent skip would ship a smaller tranche than approved."""
    lines = Path(worklist).read_text(encoding="utf-8").splitlines()
    wanted: list[str] = []
    for ln in lines:
        ln = ln.strip().lstrip("-*").strip()
        if not ln or ln.startswith("#"):
            continue
        m = sdlc_md.ID_SEARCH_RE.search(ln)
        if m:
            wanted.append(sdlc_md.norm_id(m.group(0)))
    wanted = list(dict.fromkeys(wanted))  # a repeated id is one unit, in every order mode
    by_id: dict[str, tuple[Path, str]] = {}
    for kind in sdlc_md.ARTIFACT_TYPES:
        for path in sdlc_md.artifact_files(kind, root):
            rec = sdlc_md.extract_record_id(path.stem)
            if rec and sdlc_md.norm_id(rec) in set(wanted):
                by_id[sdlc_md.norm_id(rec)] = (path, kind)
    missing = [w for w in wanted if w not in by_id]
    if missing:
        raise ValueError(f"worklist ids not found on disk: {', '.join(missing)}")
    out: list[dict] = []
    deps: dict[str, set] = {}
    for w in wanted:
        path, kind = by_id[w]
        text = path.read_text(encoding="utf-8")
        st = sdlc_md.canonical_status(
            sdlc_md.extract_field(text, "Status"),
            sdlc_md.status_vocab(kind, root)) or "Unknown"
        out.append(_unit(kind, path, text, st, deps))
    return out, deps


def _order_batch(root: Path, out: list[dict], deps: dict[str, set], order: str,
                 skip_personas: bool) -> list[dict]:
    """WSJF enrichment + dependency-topological ordering over one (possibly mixed) batch."""
    if order == "wsjf":  # seat-scored WSJF when available, else priority+complexity
        seat_inputs = {} if skip_personas else _wsjf_inputs(root)
        for it in out:
            size = _complexity_size(root, Path(it["path"]).read_text(encoding="utf-8"))
            it["complexity"] = size
            it["token_budget"] = BASE_TOKEN_BUDGET + TOKENS_PER_COGNITIVE * size
            inp = seat_inputs.get(sdlc_md.norm_id(it["id"]))
            if inp:  # the review seats scored this unit (value / time-criticality / risk)
                it["value"] = inp.get("value", 0)
                it["time_criticality"] = inp.get("time_criticality", 0)
                it["risk_reduction"] = inp.get("risk_reduction", 0)
                it["wsjf"] = wsjf_score(it["value"], it["time_criticality"],
                                        it["risk_reduction"], size)
    if order in ("priority", "wsjf"):
        out = _topo_order(out, deps)
    return out


def select_batches(repo_root: Path | str, queries: list[tuple[str, str]],
                   order: str = "priority", skip_personas: bool = False,
                   epics: set[str] | None = None) -> list[dict]:
    """The union of one or more kind+status queries as ONE merged, ordered batch -
    a mixed bugs + CRs tranche is first-class, and a cross-type `Depends on` edge
    (CR depends on BG) orders and waves like any other."""
    root = Path(repo_root)
    epic_filter = {sdlc_md.norm_id(e) for e in epics} if epics else None
    out: list[dict] = []
    deps: dict[str, set] = {}
    for kind, status in queries:
        items, d = _collect(root, kind, status, epic_filter if kind == "story" else None)
        out.extend(items)
        deps.update(d)
    return _order_batch(root, out, deps, order, skip_personas)


def select_batch(repo_root: Path | str, kind: str, status: str, order: str = "priority",
                 skip_personas: bool = False, epics: set[str] | None = None) -> list[dict]:
    """Files of `kind` whose Status matches, with priority, ordered. Single-query
    wrapper over `select_batches` - see there for ordering semantics."""
    return select_batches(repo_root, [(kind, status)], order,
                          skip_personas=skip_personas, epics=epics)


def build_plan(repo_root: Path | str, kind: str | None = None, status: str | None = None,
               order: str = "priority", skip_personas: bool = False,
               epics: set[str] | None = None, queries: list[tuple[str, str]] | None = None,
               worklist: str | None = None) -> dict:
    """The triage plan: the ordered batch, a count, and (for ordered modes) the dependency
    WAVES - the parallelisable levels operators otherwise hand-derive. The batch source is
    a single kind+status, composed `queries`, or a `worklist` file (ids one per line)."""
    root = Path(repo_root)
    if worklist is not None:
        batch, deps = _worklist_units(root, worklist)
        batch = _order_batch(root, batch, deps, order, skip_personas)
        queries = [("worklist", worklist)]
    else:
        if queries is None:
            queries = [(kind, status)]
        batch = select_batches(root, queries, order, skip_personas=skip_personas, epics=epics)
    waves = None
    deps_declared: bool | None = None  # None for manual order (no wave computation)
    if order in ("priority", "wsjf") and batch:
        deps = {}
        for it in batch:
            text = Path(it["path"]).read_text(encoding="utf-8")
            dval = (sdlc_md.extract_field(text, "Depends on")
                    or sdlc_md.extract_field(text, "Depends On") or "")
            deps[sdlc_md.norm_id(it["id"])] = _dep_ids(dval)
        # batch already passed _topo_order above, so the graph is acyclic here.
        waves = [[it["id"] for it in w] for w in _topo_waves(batch, deps)]
        # whether ANY in-batch dependency edge was declared - a flat single wave with no
        # edges is parallel because no one declared a `Depends on:`, not because none exist.
        deps_declared = any(deps[k] & set(deps) for k in deps)
    return {
        "generated_at": sdlc_md.now_iso8601(),
        "kind": "+".join(k for k, _ in queries),
        "status": ", ".join(str(s) for _, s in queries),
        "queries": [{"kind": k, "status": s} for k, s in queries],
        "order": order,
        "batch": batch,
        "count": len(batch),
        "waves": waves,
        "deps_declared": deps_declared,
    }


def build_authoring_plan(repo_root: Path | str, prd_path: str) -> dict:
    """The greenfield authoring plan: the batch source is a PRD, not existing units.
    The planner validates the PRD and signals **authoring mode**; the decomposition itself
    (PRD -> epics -> stories) is the model-instructed phase the loop runs next. It
    cannot enumerate epics/stories here - they do not exist yet."""
    prd = Path(prd_path)
    if not prd.exists():
        raise FileNotFoundError(f"PRD not found: {prd_path}")
    return {
        "generated_at": sdlc_md.now_iso8601(),
        "mode": "authoring",
        "prd": str(prd),
        "next": "decompose the PRD into epics, then Ready stories (the authoring phase); "
                "stop at the epic-cut STOP for approval before authoring stories",
        "count": 0,
    }


def pre_plan_blocker_sweep(repo_root: Path | str) -> dict:
    """Pre-plan step: surface units whose blockers have cleared so newly-unblocked work is
    eligible for the batch, mirroring the reconcile-before-plan gate. Advisory and fail-safe -
    it proposes Blocked -> Ready candidates and never transitions or blocks planning (US0050)."""
    try:
        return blocker_sweep.sweep(repo_root)
    except Exception:  # noqa: BLE001 - the sweep is advisory; never break planning on its failure
        return {"now_unblocked": [], "still_blocked": [], "errors": []}


def cmd_plan(args: argparse.Namespace) -> int:
    """Print the ordered batch the operator approves before a run."""
    if getattr(args, "prd", None):  # greenfield authoring - the batch is a PRD
        try:
            data = build_authoring_plan(args.root, args.prd)
        except FileNotFoundError as exc:
            print(f"{exc}", file=sys.stderr)
            return 2
        print(json.dumps(data, indent=2) if args.format == "json"
              else f"authoring plan: bootstrap from {data['prd']} (PRD -> epics -> stories)")
        return 0
    queries: list[tuple[str, str]] = []
    if args.bugs is not None:
        queries.append(("bug", args.bugs))
    if args.crs is not None:
        queries.append(("cr", args.crs))
    if args.stories is not None:
        queries.append(("story", args.stories))
    worklist = getattr(args, "worklist", None)
    if worklist and queries:
        print("--worklist is a complete batch source; do not combine it with "
              "--bugs/--crs/--stories", file=sys.stderr)
        return 2
    if not worklist and not queries:
        print("specify a batch: --bugs/--crs/--stories (combinable), --worklist, or --prd",
              file=sys.stderr)
        return 2
    # reconcile before plan - a plan must be built on a drift-free census. Mechanical
    # drift only (index vs file); semantic staleness still needs the audit + human grooming.
    kinds = [k for k, _ in queries] if queries else list(sdlc_md.ARTIFACT_TYPES)
    drift = []
    for k in kinds:
        try:
            drift += [(k, d) for d in reconcile.detect_type(k, Path(args.root)).get("drift", [])]
        except Exception:  # noqa: BLE001 - reconcile is advisory here, never block planning on its failure
            pass
    if drift:
        names = ", ".join(sorted({k for k, _ in drift}))
        print(f"reconcile: {len(drift)} drift item(s) in the {names} index(es) - reconcile before "
              f"planning (the plan reads file Status; a stale index misleads selection)",
              file=sys.stderr)
        if getattr(args, "strict", False):
            return 2
    # blocker sweep before plan - newly-unblocked work should be eligible for the batch. Advisory:
    # it proposes Blocked -> Ready candidates; the gated transition stays the actor (never auto).
    sweep = pre_plan_blocker_sweep(Path(args.root))
    if sweep["now_unblocked"]:
        print(f"blocker sweep: {len(sweep['now_unblocked'])} newly-unblocked unit(s) "
              f"({', '.join(sweep['now_unblocked'])}) - propose Blocked -> Ready via the gated "
              f"transition, then re-plan to include them", file=sys.stderr)
    epics = set(getattr(args, "epic", None) or []) or None
    if epics and worklist:  # a worklist names its units; an ignored filter would lie
        print("--epic does not filter a --worklist batch; list the story ids you want",
              file=sys.stderr)
        return 2
    if epics and "story" not in kinds:  # epic-scoping is meaningful for stories only
        print("--epic scopes a story batch; use it with --stories", file=sys.stderr)
        return 2
    try:
        data = build_plan(args.root, order=args.order,
                          skip_personas=getattr(args, "skip_personas", False), epics=epics,
                          queries=queries or None, worklist=worklist)
    except ValueError as exc:  # dependency cycle / bad status / unknown worklist id
        print(f"cannot order the batch: {exc}", file=sys.stderr)
        return 2
    if getattr(args, "write", False):  # persist the sprint-plan artifact for review
        out = Path(args.root) / "sdlc-studio" / ".local" / "sprint-plan.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"wrote sprint plan -> {out}")
    if args.format == "json":
        print(json.dumps(data, indent=2))
    else:
        scope = f", epics {', '.join(sorted(epics))}" if epics else ""
        if worklist:
            src = f"worklist {worklist}"
        else:
            src = " + ".join(f"{k}s {s}" for k, s in queries)
        print(f"batch: {data['count']} unit(s) ({src}){scope}, order={args.order}")
        if data.get("waves"):  # show the parallelisable dependency levels
            for i, wave in enumerate(data["waves"], 1):
                par = " (parallel)" if len(wave) > 1 else ""
                print(f"  wave {i}{par}: {', '.join(wave)}")
            # a flat single wave of >1 unit with no declared deps is not 'no dependencies
            # exist' - it is undeclared. Flag it so the operator grooms `Depends on:` (the
            # --goal design rung) rather than treating the flat list as the real sequence.
            if data.get("deps_declared") is False and data["count"] > 1:
                print("  hint: all units are parallel because no `Depends on:` is declared "
                      "- groom inter-story dependencies (the --goal design rung) for real waves")
        else:
            for b in data["batch"]:
                print(f"  {b['id']} [{b['priority']}]")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SDLC Studio sprint batch selection.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan", help="Select and order a batch of work (the triage plan).")
    p.add_argument("--bugs", metavar="STATUS", help="Bugs with this Status (e.g. Open); "
                   "combinable with --crs/--stories for one merged mixed tranche")
    p.add_argument("--crs", metavar="STATUS", help="CRs with this Status (e.g. Proposed); combinable")
    p.add_argument("--stories", metavar="STATUS", help="Stories with this Status (e.g. Ready); combinable")
    p.add_argument("--worklist", metavar="PATH",
                   help="tranche file: one unit id per line (bullets/comments tolerated); "
                        "a complete batch source, not combinable with status queries")
    p.add_argument("--prd", metavar="PATH", help="Greenfield authoring: bootstrap from a PRD")
    p.add_argument("--epic", action="append", metavar="EPxxxx",
                   help="scope a story batch to one or more epics (repeatable; with --stories)")
    p.add_argument("--order", choices=("priority", "wsjf", "manual"), default="priority")
    p.add_argument("--write", action="store_true",
                   help="persist the sprint plan to sdlc-studio/.local/sprint-plan.json")
    p.add_argument("--strict", action="store_true",
                   help="refuse to plan when the index has drift (reconcile before plan)")
    p.add_argument("--skip-personas", action="store_true", dest="skip_personas",
                   help="ignore review-seat WSJF inputs; order by priority + complexity")
    p.add_argument("--root", default=".", help="Repo root (default: .)")
    p.add_argument("--format", choices=("text", "json"), default="text")
    p.set_defaults(func=cmd_plan)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
