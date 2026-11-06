"""`sprint cost --anatomy`: where a session's tokens went, by role and by tool output.

It reads the transcripts the token meter reads (`run_state`): the session's own file and each
subagent's `agent-<id>.jsonl` beside it, through the meter's own reader, so each message is
counted once at its largest usage record and each component is priced from `TOKEN_WEIGHTS`.

A subagent's role comes from the run's own records and from nothing else: an agent `sprint lane
return --agent` recorded against a unit is that unit's builder, or its repair when the unit's
first verdict names another agent as the author (the first agent returned for it when no verdict
names one); an agent a recorded verdict names as its reviewer, which is the record `sprint lane
accept` writes, is a reviewer. An agent no record names is `other`. Its prompt text is never read
for a role: wording is not a record.

A context figure (the first call's, and the average per call) is the prompt a call was billed
for: input + cache write + cache read. It is None, printed `not available`, wherever no per-call
record exists: a harness reading that gives only a session total, a transcript whose usage records
carry no message id, or a role with no calls. It is never 0. The main thread's start context is its
first call's context, which the header names: what the session paid before any tool output.
A subagent whose first call's context exceeds `cost.agent_start_budget` is flagged with its start
and the budget: the first call, not the largest, because the start is what its definition and
brief cost before it did any work. The first call is its transcript's first, whatever the window;
the window decides only which subagents are judged. One whose records give no per-call start is
named `not available`, and the whole check is when none can be judged. The main thread is not
judged against it.

A tool output is costed as its size in characters times the later calls of its own transcript,
each of which re-reads it as context. The transcript records no token count per tool output, so
the size is stated in characters rather than converted at a guessed ratio.

The anatomy is the open run's (`run_window`): only the records timestamped after its `started_at`
count, each message, tool output and later call among them, and a subagent with no call in that
window is not one of its agents. It is the whole session under `--session`, when no run is open,
and when a usage record carries no timestamp, since such a record cannot be placed against the
start and a window that dropped it would understate the run. The header names which, and why.
The start context alone is read over the whole session: it is what the session paid first.
"""
from __future__ import annotations

import bisect
import json
import os
import re
from pathlib import Path

from lib import run_state, sdlc_md

ORCHESTRATOR, BUILDER, REVIEWER, REPAIR, OTHER = (
    "orchestrator", "builder", "reviewer", "repair", "other")
ROLES = (ORCHESTRATOR, BUILDER, REVIEWER, REPAIR, OTHER)
TOP_OUTPUTS = 10
NOT_AVAILABLE = "not available"
#: the tool input fields that name what produced an output, the first present one wins
PRODUCER_FIELDS = ("command", "file_path", "notebook_path", "path", "pattern", "url", "query",
                   "description")
PRODUCER_WIDTH = 100
_PLAIN = re.compile(r"[A-Za-z0-9_-]+")
_WRITES = ("cache_write_5m", "cache_write_1h")
START_BUDGET_KEY = "cost.agent_start_budget"


class AnatomyError(Exception):
    """Why no anatomy can be had. `store` is False when no session transcript was found."""

    def __init__(self, message: str, store: bool = True) -> None:
        super().__init__(message)
        self.store = store


def agent_key(name) -> str | None:
    """The agent id `name` carries, with or without its `agent-` prefix; None when it is not a
    plain id (letters, digits, `_` and `-`), as `build lane` or a seat name is not."""
    s = str(name or "").strip()
    s = s[len("agent-"):] if s.startswith("agent-") else s
    return s if _PLAIN.fullmatch(s) else None


def agent_roles(state: dict, verdicts: list[dict]) -> dict[str, str]:
    """`{agent id: role}` from the run's delegated records and the recorded verdicts.

    Per unit, the agents `lane return --agent` recorded, in the order they landed: the one its
    first verdict names as the author is the builder, else the first; every other is a repair.
    An agent a verdict names as its reviewer is a reviewer, whatever else names it."""
    by_unit: dict[str, list[str]] = {}
    for r in run_state.delegated_records(state):
        key = agent_key(r.get("agent")) or agent_key(Path(str(r.get("transcript") or "")).stem)
        unit = sdlc_md.norm_id(str(r.get("unit") or ""))
        if key and unit and key not in by_unit.setdefault(unit, []):
            by_unit[unit].append(key)
    first_author: dict[str, str | None] = {}
    for v in verdicts:
        first_author.setdefault(sdlc_md.norm_id(str(v.get("unit") or "")),
                                agent_key(v.get("author")))
    roles: dict[str, str] = {}
    for unit, agents in by_unit.items():
        named = first_author.get(unit)
        builder = named if named in agents else agents[0]
        for a in agents:
            roles.setdefault(a, BUILDER if a == builder else REPAIR)
    for v in verdicts:
        key = agent_key(v.get("reviewer"))
        if key:
            roles[key] = REVIEWER
    return roles


def _context(parts: dict) -> int:
    return parts["input"] + parts["cache_write_5m"] + parts["cache_write_1h"] + parts["cache_read"]


def _records_of(path: Path, side: str) -> list:
    """One transcript's usage records through the meter's reader (`run_state._file_records`), a
    whole read, so each record keeps its timestamp for the window (`_after`); `_largest` and
    `_aggregate` read a message's repeats once, at its largest. RAISES `AnatomyError` on a
    malformed or unreadable transcript, as the meter refuses one."""
    out: list = []
    try:
        run_state._file_records(path, side, out)
    except run_state._MeterError as exc:
        raise AnatomyError(str(exc)) from exc
    return out


def _whole(reason: str | None) -> dict:
    return {"run_id": None, "since": None, "whole_session": True, "reason": reason}


def run_window(state: dict, session: bool = False) -> dict:
    """The window the anatomy reads: the open run's, every record after its `started_at`, or the
    whole session, with the reason, under `session` (`--session`) or when no run is open (a
    closed run, or none recorded)."""
    if session:
        return _whole("--session names the whole session")
    if (state or {}).get("outcome") == run_state.RUNNING and state.get("started_at"):
        return {"run_id": state.get("run_id"), "since": state["started_at"],
                "whole_session": False, "reason": None}
    return _whole("no run is open")


def _after(readings: list[list], since) -> list[list] | None:
    """Each transcript's records timestamped after `since` (a datetime), as the meter's opening
    reading holds the ones at or before it; None when any record carries no timestamp, which no
    window can place."""
    out = []
    for records in readings:
        kept = []
        for rec in records:
            moment = sdlc_md.parse_iso8601(rec[2]) if rec[2] else None
            if moment is None:
                return None
            if moment > since:
                kept.append(rec)
        out.append(kept)
    return out


def _largest(readings: list[list]) -> dict:
    """`{message id: components}`, each component at its largest over every transcript's records,
    as `run_state._aggregate` reads a message read on more than one transcript."""
    largest: dict = {}
    for records in readings:
        for _side, msg_id, _at, parts, _model in records:
            if msg_id is not None:
                held = largest.get(msg_id)
                largest[msg_id] = parts if held is None else {
                    c: max(held[c], parts[c]) for c in run_state.TOKEN_COMPONENTS}
    return largest


def _usage_of(path: Path, records: list, seen: set,
              largest: dict) -> tuple[dict, list[int] | None]:
    """`(components, contexts)` of one transcript's `records`: its components once per message
    at the message's largest usage over every transcript (`largest`, then `_aggregate`), and each
    call's context in the order the calls first appear, None when a usage record carries no
    message id. A message id already read on an earlier transcript stays booked there, at that
    largest usage, as the meter books it to the side it was first read on."""
    kept = [(side, msg_id, at, parts if msg_id is None else largest[msg_id], model)
            for side, msg_id, at, parts, model in records
            if msg_id is None or msg_id not in seen]
    seen.update(rec[1] for rec in kept if rec[1] is not None)
    calls: dict = {}
    for _side, msg_id, _at, parts, model in kept:
        if msg_id is not None:
            # the collapse leaves a repeat only for a last line still being written
            held = calls.get((msg_id, model))
            calls[(msg_id, model)] = parts if held is None else {
                c: max(held[c], parts[c]) for c in run_state.TOKEN_COMPONENTS}
    try:
        comps = run_state._aggregate({"source": path, "records": kept, "files": 0,
                                      "note": None})["components"] if kept else None
    except run_state._MeterError:
        comps = None  # no usage, or none that counts: the transcript adds nothing
    comps = dict(comps) if comps else run_state._zero()
    per_call = all(rec[1] is not None for rec in kept)
    return comps, [_context(p) for p in calls.values()] if per_call else None


def _producer(block: dict) -> str:
    """What a tool call ran or read: its tool's name and the first `PRODUCER_FIELDS` input."""
    name = str(block.get("name") or "tool")
    inp = block.get("input") if isinstance(block.get("input"), dict) else {}
    value = next((inp[f] for f in PRODUCER_FIELDS if isinstance(inp.get(f), str) and inp[f]), "")
    text = f"{name}: {' '.join(value.split())}" if value else name
    return text if len(text) <= PRODUCER_WIDTH else text[:PRODUCER_WIDTH - 3] + "..."


def _size(content) -> int:
    """A tool result's size in characters: its text, or the text of its text blocks."""
    if isinstance(content, str):
        return len(content)
    if isinstance(content, list):
        return sum(len(b["text"]) for b in content
                   if isinstance(b, dict) and isinstance(b.get("text"), str))
    return 0


def _outputs_of(path: Path, role: str, agent: str, since=None) -> list[dict]:
    """Every tool output of one transcript, each with the later calls of that transcript; given
    `since` (a datetime), only the records timestamped after it, a record with none outside."""
    producers: dict[str, str] = {}
    call_lines: list[int] = []
    ids: set = set()
    results: list[tuple[int, str, int]] = []
    try:
        with path.open(encoding="utf-8") as fh:
            for n, line in enumerate(fh):
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                msg = rec.get("message") if isinstance(rec, dict) else None
                if not isinstance(msg, dict):
                    continue
                if since is not None:
                    at = rec.get("timestamp")
                    moment = sdlc_md.parse_iso8601(at) if isinstance(at, str) else None
                    if moment is None or moment <= since:
                        continue
                if isinstance(msg.get("usage") or rec.get("usage"), dict):
                    msg_id = msg.get("id")
                    if not (isinstance(msg_id, str) and msg_id) or msg_id not in ids:
                        call_lines.append(n)
                        ids.add(msg_id)
                blocks = msg.get("content")
                for b in blocks if isinstance(blocks, list) else []:
                    if not isinstance(b, dict):
                        continue
                    if b.get("type") == "tool_use" and isinstance(b.get("id"), str):
                        producers[b["id"]] = _producer(b)
                    elif b.get("type") == "tool_result":
                        results.append((n, str(b.get("tool_use_id") or ""), _size(b.get("content"))))
    except (OSError, UnicodeDecodeError) as exc:
        raise AnatomyError(f"transcript {path} unreadable ({type(exc).__name__}: {exc})") from exc
    out = []
    for n, tid, size in results:
        later = len(call_lines) - bisect.bisect_right(call_lines, n)
        out.append({"producer": producers.get(tid, "tool (its call is not in the transcript)"),
                    "size": size, "later_calls": later, "cost": size * later,
                    "role": role, "agent": agent})
    return out


def _row(role: str) -> dict:
    return {"role": role, "agents": 0, "agent_ids": [], "calls": 0,
            "components": run_state._zero(), "contexts": [], "firsts": [], "per_call": True}


def _finish(rows: dict) -> list[dict]:
    """The rows as the anatomy reports them: priced, shared, split and their contexts."""
    weights = run_state.TOKEN_WEIGHTS
    priced = {r: run_state.price(row["components"]) for r, row in rows.items()}
    whole = sum(priced.values())
    out = []
    for role in ROLES:
        row = rows[role]
        comps = row["components"]
        weighed = {c: comps[c] * weights[c] for c in run_state.TOKEN_COMPONENTS}
        spend = sum(weighed.values())
        per_call = row["per_call"] and bool(row["contexts"])
        out.append({
            "role": role, "agents": row["agents"], "agent_ids": row["agent_ids"],
            "calls": row["calls"] if row["per_call"] else None,
            "priced": priced[role], "share": priced[role] / whole if whole else None,
            "components": comps,
            "split": ({"cache_read": weighed["cache_read"] / spend,
                       "cache_write": sum(weighed[c] for c in _WRITES) / spend,
                       "output": weighed["output"] / spend} if spend else None),
            "first_context": sum(row["firsts"]) / len(row["firsts"]) if per_call else None,
            "avg_context": sum(row["contexts"]) / len(row["contexts"]) if per_call else None})
    return out


def start_budget(repo_root) -> int | None:
    """`cost.agent_start_budget` as a whole number of tokens, or None when it is off, unset or
    not one, which flags no agent."""
    import config  # noqa: PLC0415 - sibling script; only the start budget reads the config
    raw = config.get(repo_root, START_BUDGET_KEY)
    return raw if isinstance(raw, int) and not isinstance(raw, bool) and raw > 0 else None


def build(main: Path, subagents: list[Path], roles: dict[str, str],
          window: dict | None = None, budget: int | None = None) -> dict:
    """The anatomy of the session whose transcript is `main`, its subagents' transcripts
    `subagents`, each subagent's role read from `roles` (`agent_roles`) and `other` when absent,
    over `window` (`run_window`; the whole session when None). Each subagent the window counts
    (one with a call inside it) whose start, the context of its transcript's first call whatever
    the window, exceeds `budget` (`start_budget`) is named in `over_start_budget`, and each whose
    records give no per-call start in `start_not_available`; `over_start_budget` is None with no
    budget, or when no subagent the window counts can be judged. RAISES `AnatomyError` on a
    transcript the meter would refuse."""
    rows = {r: _row(r) for r in ROLES}
    seen: set = set()
    over: list[dict] | None = [] if budget is not None else None
    outputs: list[dict] = []
    sources = [(main, "main")] + [(f, "subagents") for f in subagents]
    whole = [_records_of(path, side) for path, side in sources]
    # each transcript's first call, whatever the window: in the order the calls first appear
    largest_whole = _largest(whole)
    starts = [_usage_of(path, records, set(), largest_whole)[1]
              for (path, _side), records in zip(sources, whole)]
    start = starts[0][0] if starts[0] else None
    unjudged: list[dict] = []
    judged = 0
    window, since, readings = dict(window or _whole(None)), None, whole
    if window["since"] is not None:
        since = sdlc_md.parse_iso8601(window["since"])
        cut = _after(whole, since) if since is not None else None
        if cut is None:
            why = ("a usage record carries no timestamp" if since is not None
                   else f"its start {window['since']!r} does not parse")
            window, since = _whole(f"the open run {window['run_id']}'s window cannot be applied: "
                                   f"{why}"), None
        else:
            readings = cut
    largest = _largest(readings)
    for (path, side), records, firsts in zip(sources, readings, starts):
        if since is not None and side == "subagents" and not records:
            continue  # no call in the run's window: not one of its agents
        key = agent_key(path.stem) if side == "subagents" else None
        role = ORCHESTRATOR if side == "main" else roles.get(key or "", OTHER)
        agent = path.stem if side == "subagents" else "session"
        comps, contexts = _usage_of(path, records, seen, largest)
        if side == "subagents" and over is not None:
            if not firsts:  # no message id, or no call: neither flagged nor cleared
                unjudged.append({"agent": agent, "role": role, "reason": (
                    "a usage record carries no message id" if firsts is None
                    else "its transcript carries no call")})
            else:
                judged += 1
                if firsts[0] > budget:
                    over.append({"agent": agent, "role": role, "start": firsts[0]})
        row = rows[role]
        row["agents"] += 1
        row["agent_ids"].append(agent)
        for c in run_state.TOKEN_COMPONENTS:
            row["components"][c] += comps[c]
        if contexts is None:
            row["per_call"] = False
        else:
            row["calls"] += len(contexts)
            row["contexts"].extend(contexts)
            row["firsts"].extend(contexts[:1])
        outputs.extend(_outputs_of(path, role, agent, since))
    outputs.sort(key=lambda o: (-o["cost"], -o["size"]))
    total = run_state._zero()
    for row in rows.values():
        for c in run_state.TOKEN_COMPONENTS:
            total[c] += row["components"][c]
    finished = _finish(rows)
    if over is not None and unjudged and not judged:
        over = None  # no subagent the window counts gives a start: the check cannot be read
    return {"source": str(main), "subagent_files": len(subagents), "start_context": start,
            "start_budget": budget, "over_start_budget": over,
            "start_not_available": unjudged if budget is not None else None, "window": window,
            "roles": finished, "total": _total(finished, total),
            "outputs": outputs[:TOP_OUTPUTS], "note": None}


def _total(finished: list[dict], comps: dict) -> dict:
    calls = [r["calls"] for r in finished]
    agents = [r["agents"] for r in finished]
    return {"agents": None if None in agents else sum(agents),
            "calls": None if None in calls else sum(calls),
            "priced": run_state.price(comps), "components": comps}


def from_reading(reading: dict) -> dict:
    """The anatomy a harness reading with no per-call records gives: its whole under `other`, no
    role attributed and every count and context not available, never 0."""
    comps = {c: int((reading.get("components") or {}).get(c) or 0)
             for c in run_state.TOKEN_COMPONENTS}
    rows = {r: _row(r) for r in ROLES}
    rows[OTHER]["components"] = dict(comps)
    finished = _finish(rows)
    for row in finished:
        row["calls"] = None
        if row["role"] != OTHER:
            row.update(agents=None, priced=None, share=None, split=None)
        else:
            row["agents"] = None
            if isinstance(reading.get("priced"), int):
                row["priced"] = reading["priced"]
    harness = reading.get("harness") or "harness"
    return {"source": harness, "subagent_files": None, "start_context": None,
            "start_budget": None, "over_start_budget": None, "start_not_available": None,
            "start_check": "no per-call record exists",
            "window": _whole(f"the {harness} reading is one session total, which no window "
                             f"divides"), "roles": finished,
            "total": _total(finished, comps) | {"priced": finished[-1]["priced"]},
            "outputs": [],
            "note": f"the {harness} reading is one session total with no per-call records, so no "
                    f"role is attributed: it is counted under other"}


def anatomy(repo_root: Path | str, transcripts_dir: Path | str | None = None,
            env=None, session: bool = False) -> dict:
    """The CURRENT session's anatomy, from the directory the meter reads (`transcripts_dir`,
    else `run_state.TRANSCRIPTS_ENV`, else the harness's folder for this repo), over the open
    run's window (`run_window`; the whole session under `session`), with roles from the open
    run's records and the recorded verdicts. RAISES `AnatomyError`, `store` False when that
    directory holds no session transcript."""
    import critic  # noqa: PLC0415 - sibling script; only the roles need its verdict reader
    env = os.environ if env is None else env
    d = Path(transcripts_dir or env.get(run_state.TRANSCRIPTS_ENV)
             or run_state._harness_transcript_dir(repo_root))
    main = run_state._newest_transcript(d) if d.is_dir() else None
    if main is None:
        raise AnatomyError(f"no session transcript (*.jsonl) in {d}", store=False)
    folder = main.parent / main.stem / run_state.SUBAGENTS_DIR
    files = sorted(folder.glob(run_state.SUBAGENT_GLOB)) if folder.is_dir() else []
    state = run_state.read(repo_root)
    roles = agent_roles(state, critic.read_verdicts(repo_root))
    return build(main, files, roles, window=run_window(state, session),
                 budget=start_budget(repo_root))


def _cell(value, kind: str = "int") -> str:
    if value is None:
        return NOT_AVAILABLE
    if kind == "pct":
        return f"{100 * value:.1f}%"
    return f"{round(value):,}"


def _window_text(window: dict) -> str:
    if not window["whole_session"]:
        return (f"the open run {window['run_id']}, the records after its start "
                f"{window['since']}; --session reads the whole session")
    return "the whole session" + (f" ({window['reason']})" if window["reason"] else "")


def render(got: dict) -> str:
    """The anatomy as `sprint cost --anatomy` prints it."""
    w = len(NOT_AVAILABLE)
    head = ("role", "agents", "calls", "priced", "share", "cache read", "cache write", "output",
            "first context", "avg context")
    lines = [f"Cost anatomy of {Path(got['source']).stem}"
             + (f" ({got['subagent_files']} subagent transcript(s))"
                if got.get("subagent_files") is not None else ""),
             "  priced in input-equivalent tokens (TOKEN_WEIGHTS), each message counted once at "
             "its largest usage record; split is each part's share of the role's priced cost; "
             "context is input + cache write + cache read per call",
             "  roles from the open run's lane returns and the recorded verdicts; an agent no "
             "record names is other",
             "  window: " + _window_text(got.get("window") or _whole(None)),
             "  main thread start context: "
             + (f"{got['start_context']:,} tokens (its first call's input + cache write + cache "
                "read: what the session paid before any tool output)"
                if got.get("start_context") is not None else NOT_AVAILABLE)]
    if got.get("note"):
        lines.append(f"  {got['note']}")
    lines += ["", f"{head[0]:<12}" + "".join(f"  {h:>{w}}" for h in head[1:])]
    for row in got["roles"]:
        split = row["split"] or {}
        cells = (_cell(row["agents"]), _cell(row["calls"]), _cell(row["priced"]),
                 _cell(row["share"], "pct"), _cell(split.get("cache_read"), "pct"),
                 _cell(split.get("cache_write"), "pct"), _cell(split.get("output"), "pct"),
                 _cell(row["first_context"]), _cell(row["avg_context"]))
        lines.append(f"{row['role']:<12}" + "".join(f"  {c:>{w}}" for c in cells))
    t = got["total"]
    lines.append(f"{'total':<12}" + "".join(f"  {c:>{w}}" for c in (
        _cell(t["agents"]), _cell(t["calls"]), _cell(t["priced"]))))
    lines += ["", f"Subagent starts (each one's first call's context) against "
                  f"`{START_BUDGET_KEY}`:"]
    budget, over = got.get("start_budget"), got.get("over_start_budget")
    unjudged = got.get("start_not_available") or []
    if budget is None:
        lines.append(f"  not available: {got.get('start_check') or 'no budget is configured'}")
    elif over is None:
        lines.append("  not available: no subagent's transcript gives a per-call start")
    else:
        for o in over:
            lines.append(f"  {o['agent']} ({o['role']}) started at {o['start']:,} tokens, over "
                         f"the start budget of {budget:,} tokens")
        for o in unjudged:
            lines.append(f"  {o['agent']} ({o['role']}): not available, {o['reason']}")
        if not over:
            lines.append(f"  none {'of the others ' if unjudged else ''}started over the start "
                         f"budget of {budget:,} tokens")
    lines += ["", "Heaviest tool outputs (size in characters x the later calls of its own "
                  "transcript that re-read it):"]
    if not got["outputs"]:
        lines.append("  none: no tool output in the session's transcripts")
    for n, o in enumerate(got["outputs"], 1):
        lines.append(f"  {n:>2}. {o['cost']:>13,} = {o['size']:,} x {o['later_calls']}  "
                     f"{o['role']} {o['agent']}  {o['producer']}")
    return "\n".join(lines)
