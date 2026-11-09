"""Where an open run stands and its next step, read from disk alone, and a resume brief of it.

A session that resumes a run, after a compaction or in a fresh context, needs four facts: which
lanes are building, which landed units owe a review or a repair, which wave is next, and whether
the run is ready to close. Each is already on disk, so this module derives them from the tree and
`sdlc-studio/.local/` and from nothing a process holds; two calls on one tree return one answer.

A batch unit's lane state is read from what the shipped tools write:

- `terminal`: the unit's artefact carries a terminal status for its type (`sdlc_md`).
- `in flight`: `sprint.py lane brief` recorded the unit under the run state's `lanes_in_flight`,
  and no QA brief of this lane is on disk yet.
- `landed awaiting a verdict`: `sprint lane land` wrote the unit's QA brief under
  `sdlc-studio/.local/briefs/` at or after the lane's `started_at`, and the delivery verdict
  ledger holds no verdict against that brief's fingerprint.
- `rejected`: the latest verdict against that brief is a REJECT, so a repair is owed.
- `accepted`: the latest verdict against that brief is an APPROVE and the unit is not
  terminal, as when `sprint lane accept` recorded the APPROVE and a red criterion or a refused
  transition left the unit where it was.
- `unbriefed`: none of the above.

A QA brief dated before the lane's `started_at` was written by an earlier landing, so a repair
lane briefed again after a REJECT reads `in flight`, not `rejected`.

`next_action` climbs a fixed ladder and stops at the first rung that holds: 1 await the in-flight
lanes; 2 review each landed unit, repair each rejected one, finish each accepted one; 3 brief the
first wave in the sprint plan that holds an unbriefed unit; 4 run `sprint.py close` in its own
fresh session, named only when every batch unit is terminal.

`build` renders the brief and refuses one over `BUDGET_TOKENS`, estimated as the characters
divided by four, rounded up (`estimate_tokens`); it never returns a truncated brief. `parse` reads
a brief back, keying each unit by `sdlc_md.norm_id`, so `US-01M6XQJF` and `US01M6XQJF` are one.
"""
from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from lib import lanes, run_state, sdlc_md

#: The most a resume brief may cost a fresh session, in estimated tokens.
BUDGET_TOKENS = 8000
#: Where `sprint.py plan` writes the plan when the run state names none.
PLAN_REL = Path("sdlc-studio") / ".local" / "sprint-plan.json"
#: The suffix `sprint lane land` gives a unit's QA brief under `lanes.BRIEFS`.
QA_SUFFIX = "-qa.txt"

UNBRIEFED = "unbriefed"
IN_FLIGHT = "in flight"
LANDED = "landed awaiting a verdict"
REJECTED = "rejected"
ACCEPTED = "accepted"
TERMINAL = "terminal"
#: The states that hold a lane open, so the run is not at a wave boundary.
OPEN = (IN_FLIGHT, LANDED, REJECTED)
_BLOCKS = {IN_FLIGHT: "is in flight", LANDED: "is landed awaiting a verdict",
           REJECTED: "is rejected and owes a repair"}


class ResumeError(Exception):
    """No open run to read, a lane state no rung of the ladder catches, or a text that is not
    a resume brief."""


class BriefTooLong(ResumeError):
    """A brief whose estimate exceeds the budget; it is refused whole, never cut."""

    def __init__(self, estimate: int, budget: int):
        self.estimate, self.budget = estimate, budget
        super().__init__(f"the resume brief is an estimated {estimate:,} tokens (characters "
                         f"divided by four, rounded up), over the budget of {budget:,}; it was "
                         f"not returned, and nothing was cut from it")


@dataclass(frozen=True)
class Step:
    """One rung of the ladder: its number, its kind, the units it names and the step to take."""
    rung: int
    kind: str
    units: tuple[str, ...]
    text: str


@dataclass(frozen=True)
class Boundary:
    """Whether the run stands at a wave boundary; false names the first unit holding a lane open."""
    holds: bool
    blocking: str | None
    reason: str

    def __bool__(self) -> bool:
        return self.holds


@dataclass(frozen=True)
class Lane:
    unit: str
    wave: int
    state: str
    brief: str | None
    title: str


def estimate_tokens(text: str) -> int:
    """The brief's cost in tokens: its characters divided by four, rounded up."""
    return math.ceil(len(text) / 4)


def _open_state(root: Path) -> dict:
    state = run_state.read(root)
    if not state.get("run_id") or state.get("outcome") != run_state.RUNNING:
        raise ResumeError(f"no open run at {run_state.path(root)}: a resume brief reads an open "
                          f"run's state")
    return state


def _batch(state: dict) -> list[str]:
    out, seen = [], set()
    for uid in state.get("batch") or []:
        key = sdlc_md.norm_id(str(uid or ""))
        if key and key not in seen:
            seen.add(key)
            out.append(str(uid).strip())
    return out


def _waves(root: Path, state: dict) -> list[list[str]]:
    """The plan's waves as normalised ids, or [] when the plan is absent, unreadable or names
    none."""
    rel = Path(str(state.get("plan") or PLAN_REL))
    try:
        plan = json.loads((rel if rel.is_absolute() else root / rel).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    waves = plan.get("waves") if isinstance(plan, dict) else None
    return [[sdlc_md.norm_id(str(u)) for u in w] for w in waves or [] if isinstance(w, list)]


def _briefs(root: Path) -> dict[str, Path]:
    """Each unit's QA brief by normalised id; of two spellings, the later landing's."""
    found: dict[str, Path] = {}
    folder = root / lanes.BRIEFS
    for p in sorted(folder.glob(f"*{QA_SUFFIX}")) if folder.is_dir() else []:
        key = sdlc_md.norm_id(p.name[:-len(QA_SUFFIX)])
        if key not in found or p.stat().st_mtime > found[key].stat().st_mtime:
            found[key] = p
    return found


def _landed_since(brief: Path, started_at) -> bool:
    """True when the brief was written at or after the lane's start, so this lane landed it,
    or when the lane record carries no start to compare it with."""
    started = sdlc_md.parse_iso8601(started_at) if started_at else None
    if started is None:
        return True
    return datetime.fromtimestamp(brief.stat().st_mtime, timezone.utc) >= started


def _approved(root: Path, unit: str, brief: Path) -> bool | None:
    """Whether the latest live verdict against this brief's fingerprint is an APPROVE; None
    when no verdict is recorded against it."""
    import critic  # noqa: PLC0415 - sibling script that owns the verdict ledger
    fp = critic.brief_fingerprint(brief.read_text(encoding="utf-8", errors="replace"))
    rows = [r for r in critic.unit_review_rounds(root, unit) if r.get("brief") == fp]
    if not rows:
        return None
    return str(rows[-1].get("verdict") or "").strip().upper().startswith(critic.APPROVE)


def _artefact(root: Path, uid: str) -> tuple[bool, str]:
    """(terminal, title) of the unit's artefact; an artefact not found is not terminal."""
    found = sdlc_md.find_by_id(root, uid)
    if not found:
        return False, ""
    path, type_ = found
    text = sdlc_md.read_text_safe(path)
    raw = sdlc_md.extract_field(text, "Status") or ""
    status = sdlc_md.canonical_status(raw, sdlc_md.status_vocab(type_, root)) or raw
    title = sdlc_md.extract_h1_title(text) or ""
    title = re.sub(r"^\S+:\s*", "", title) if sdlc_md.ID_RE.match(title) else title
    return sdlc_md.is_terminal_status(type_, status), title


def _lanes(root: Path, state: dict) -> list[Lane]:
    """Each batch unit's lane, in plan order: wave by wave, then any unit no wave names."""
    batch = _batch(state)
    keyed = {sdlc_md.norm_id(u): u for u in batch}
    placed: dict[str, int] = {}
    for n, wave in enumerate(_waves(root, state), 1):
        for k in wave:
            if k in keyed:
                placed.setdefault(keyed[k], n)
    last = max(placed.values(), default=0) + 1
    order = list(placed.items()) + [(u, last) for u in batch if u not in placed]
    flying = {sdlc_md.norm_id(str(r.get("unit") or "")): r.get("started_at")
              for r in state.get(run_state.IN_FLIGHT) or [] if isinstance(r, dict)}
    briefs = _briefs(root)
    out = []
    with sdlc_md.corpus_cache():
        for uid, wave in order:
            key = sdlc_md.norm_id(uid)
            terminal, title = _artefact(root, uid)
            brief = briefs.get(key)
            state_, shown = UNBRIEFED, None
            if terminal:
                state_ = TERMINAL
            elif key in flying:
                state_ = IN_FLIGHT
                if brief is not None and _landed_since(brief, flying[key]):
                    shown = brief.relative_to(root).as_posix()
                    said = _approved(root, uid, brief)
                    state_ = LANDED if said is None else ACCEPTED if said else REJECTED
            out.append(Lane(uid, wave, state_, shown, title))
    return out


def _ladder(rows: list[Lane]) -> Step:
    flying = tuple(r.unit for r in rows if r.state == IN_FLIGHT)
    if flying:
        lane = "lane" if len(flying) == 1 else "lanes"
        return Step(1, "await", flying, f"await the in-flight {lane}: {', '.join(flying)}")
    parts: list[tuple[str, str, str]] = []
    for r in rows:
        if r.state == LANDED:
            parts.append(("review", r.unit, f"review {r.unit}: hand `{r.brief}` to an independent "
                          f"reviewer, then record the verdict with `sprint.py lane accept --unit "
                          f"{r.unit} --verdict <file> --reviewer <name>`"))
    for r in rows:
        if r.state == REJECTED:
            parts.append(("repair", r.unit, f"repair {r.unit} after its REJECT: `sprint.py lane "
                                            f"brief --units {r.unit}`"))
    for r in rows:
        if r.state == ACCEPTED:
            parts.append(("finish", r.unit, f"finish {r.unit}: its APPROVE is recorded and it is "
                                            f"not terminal, so make its criteria green "
                                            f"(`verify_ac.py run --id {r.unit}`) and move it"))
    if parts:
        return Step(2, parts[0][0], tuple(p[1] for p in parts), "; ".join(p[2] for p in parts))
    waiting = [r for r in rows if r.state == UNBRIEFED]
    if waiting:
        wave = waiting[0].wave
        ids = tuple(r.unit for r in waiting if r.wave == wave)
        return Step(3, "brief", ids, f"brief wave {wave}: `sprint.py lane brief --units "
                                     f"{' '.join(ids)}`")
    left = [r.unit for r in rows if r.state != TERMINAL]
    if left:  # every state above is caught by a lower rung; a new one must not reach the close
        raise ResumeError(f"no rung of the ladder holds and {', '.join(left)} is not terminal")
    return Step(4, "close", (), "every batch unit is terminal: run `sprint.py close` in its own "
                                "fresh session")


def _boundary(rows: list[Lane]) -> Boundary:
    for r in rows:
        if r.state in OPEN:
            return Boundary(False, r.unit, f"{r.unit} {_BLOCKS[r.state]}")
    return Boundary(True, None, "no lane is in flight and every briefed lane is accepted")


def next_action(root: Path | str) -> Step:
    """The open run's next step, by the ladder the module docstring states."""
    root = Path(root)
    return _ladder(_lanes(root, _open_state(root)))


def at_wave_boundary(root: Path | str) -> Boundary:
    """True only when no lane of the open run is in flight, landed awaiting a verdict or
    rejected; false names the first such unit in plan order."""
    root = Path(root)
    return _boundary(_lanes(root, _open_state(root)))


def _cell(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").strip() or "-"


def _ruling(value) -> str:
    if isinstance(value, dict):
        return "; ".join(f"{k}: {v}" for k, v in value.items())
    return str(value)


def _findings(root: Path, run_id: str) -> list[str]:
    """Each open bug or CR whose `Raised-in-batch` stamp names the run."""
    named = re.compile(rf"(?<![\w-]){re.escape(run_id)}(?![\w-])")
    out = []
    with sdlc_md.corpus_cache():
        for type_ in ("bug", "cr"):
            for path, text in sdlc_md.iter_artifact_files(type_, root):
                text = text if text is not None else sdlc_md.read_text_safe(path)
                if not named.search(sdlc_md.extract_field(text, "Raised-in-batch") or ""):
                    continue
                raw = sdlc_md.extract_field(text, "Status") or ""
                status = sdlc_md.canonical_status(raw, sdlc_md.status_vocab(type_, root)) or raw
                if sdlc_md.is_terminal_status(type_, status):
                    continue
                rid = sdlc_md.extract_record_id(path.stem) or path.stem
                out.append(f"{sdlc_md.extract_h1_title(text) or rid} ({status})")
    return out


def build(root: Path | str, agents: dict | None = None, issues: list | None = None) -> str:
    """The open run's resume brief as markdown, or `BriefTooLong` when over `BUDGET_TOKENS`.

    `agents` maps a unit (any spelling) to the agent id of its lane; `issues` are the caller's
    known issues, listed before the open findings raised in the run."""
    root = Path(root)
    state = _open_state(root)
    run_id = str(state["run_id"])
    rows = _lanes(root, state)
    step, boundary = _ladder(rows), _boundary(rows)
    agent = {sdlc_md.norm_id(str(k)): str(v) for k, v in (agents or {}).items() if str(v).strip()}
    lines = [f"# Resume brief: {run_id}", "",
             f"- Sprint Goal: {state.get('sprint_goal') or 'none recorded'}",
             f"- Wave boundary: {'yes' if boundary else 'no'} ({boundary.reason})",
             f"- Next action (rung {step.rung}, {step.kind}): {step.text}", "",
             "## Units", "", "| Unit | Wave | Lane state | Agent | QA brief | Title |",
             "| --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        lines.append(f"| {_cell(r.unit)} | {r.wave} | {r.state} | "
                     f"{_cell(agent.get(sdlc_md.norm_id(r.unit), ''))} | {_cell(r.brief or '')} "
                     f"| {_cell(r.title)} |")
    pending = []
    for r in rows:
        if r.state == LANDED:
            pending += [f"- QA brief for {r.unit}: `{r.brief}`",
                        f"- Verdict owed on {r.unit}: `sprint.py lane accept --unit {r.unit} "
                        f"--verdict <file> --reviewer <name>`"]
        elif r.state == REJECTED:
            pending.append(f"- Repair owed on {r.unit} after its REJECT")
    lines += ["", "## Pending", "", *(pending or ["- none"])]
    rulings = [f"- {_ruling(v)}" for v in state.get("rulings") or []]
    lines += ["", "## Rulings", "", *(rulings or ["- none"])]
    known = [f"- {i}" for i in issues or []] + [f"- {f}" for f in _findings(root, run_id)]
    lines += ["", "## Known issues", "", *(known or ["- none"])]
    text = "\n".join(lines) + "\n"
    estimate = estimate_tokens(text)
    if estimate > BUDGET_TOKENS:
        raise BriefTooLong(estimate, BUDGET_TOKENS)
    return text


_RUN_RE = re.compile(r"^# Resume brief: (\S+)\s*$", re.M)
_NEXT_RE = re.compile(r"^- Next action \(rung (\d+), ([a-z]+)\): (.*)$", re.M)
_BOUNDARY_RE = re.compile(r"^- Wave boundary: (yes|no)\b", re.M)
_GOAL_RE = re.compile(r"^- Sprint Goal: (.*)$", re.M)


def parse(text: str) -> dict:
    """A built brief read back: its run id, goal, next action, rung and kind, wave boundary, and
    each unit's lane state and agent, keyed by `sdlc_md.norm_id`."""
    run, nxt = _RUN_RE.search(text), _NEXT_RE.search(text)
    if not run or not nxt:
        raise ResumeError("not a resume brief: no `# Resume brief:` heading or no next action")
    units, agents = {}, {}
    for line in text.splitlines():
        cells = sdlc_md.table_cells(line)
        hit = sdlc_md.ID_RE.match(cells[0]) if cells and len(cells) >= 4 else None
        if not hit or hit.group(1) != cells[0]:
            continue
        key = sdlc_md.norm_id(cells[0])
        units[key] = cells[2]
        if cells[3] not in ("", "-"):
            agents[key] = cells[3]
    goal, boundary = _GOAL_RE.search(text), _BOUNDARY_RE.search(text)
    return {"run_id": run.group(1), "sprint_goal": goal.group(1) if goal else None,
            "next_action": nxt.group(3), "rung": int(nxt.group(1)), "kind": nxt.group(2),
            "at_wave_boundary": bool(boundary) and boundary.group(1) == "yes",
            "units": units, "agents": agents}
