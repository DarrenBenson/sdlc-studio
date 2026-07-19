#!/usr/bin/env python3
"""The run-state object - a sprint/epic run's identity, in one place.

The loop is executed by the MODEL calling discrete scripts, so until now a run had no
identity at all: no id, no start time, no recorded outcome. What a run did was scattered
across seven files nothing joined (`loop-state.json`, `epic-state.json`,
`sprint-plan.json`, `telemetry.jsonl`, `verify-report.json`, `reconcile-report.json`,
`wsjf-inputs.json`), so nothing could say "this run started here, aimed at that, and
stopped for this reason". The handoff needs exactly that sentence, and so does anything
later that must bound a run's appetite.

This is the object: run-local (`sdlc-studio/.local/run-state.json`, gitignored like the
rest of `.local/`), opened when the batch is approved (`sprint plan --write`) and closed
when the run stops (`handoff generate`).

Three properties are load-bearing, and each exists because breaking it loses work:

* **The batch is CUMULATIVE.** Re-planning mid-run (a re-cut tranche, a blocker sweep
  pulling work in) must never DISCARD an approved unit: the handoff joins over this batch,
  so a unit dropped from a narrowed re-cut - and never attempted, so absent from the loop
  state too - would land in no bucket at all and vanish from the handover. `open_run` on an
  open run takes the UNION, in first-approval order. Only a CLOSED run resets it.
* **Every mutation is LOCKED.** `update` is a read-modify-write; unlocked, concurrent
  writers silently lose each other's keys. The lock is taken here rather than left to each
  caller, because the callers that will hurt (a spend counter incremented per unit) have a
  wider window than any caller in this module does.
* **A corrupt file FAILS LOUD.** `read` raises rather than degrading a truncated file to
  "no run was ever opened" - which would let a close overwrite a real run's identity with a
  blank record, and print in the handover that the run was never opened. A silently dropped
  field is a lie the next reader inherits.

Extensible by contract: `update()` MERGES, and nothing here drops a key it does not
recognise. A later capability adds its own fields (an appetite ceiling, a spend counter)
without touching this module, and a close preserves them.

A library, not a command: the writers are `sprint.py` and `handoff.py`.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import sdlc_md

REL = Path("sdlc-studio") / ".local" / "run-state.json"
SCHEMA = 1

# Where a CLOSED run's record is kept once the next one opens. The live file holds exactly
# one run and every new run overwrites it, so before this a closed cycle's forecast, goal,
# batch and verdict were gone the moment the next cycle started - which makes an N-cycle
# rolling run unauditable: N sprints happened and one record survived. The archive is a copy
# taken at close, keyed by `run_id`, and the live file's shape is deliberately UNCHANGED so
# every existing reader sees exactly what it saw before.
ARCHIVE_REL = Path("sdlc-studio") / ".local" / "run-archive"

# The outcome vocabulary. A run is RUNNING until something says otherwise; the three ways
# it stops are the three the handoff exists for (goal reached, budget spent, blocked), plus
# the honest catch-all for an operator stop. An unknown value is REFUSED, never written: a
# free-text outcome is a field no gate can read, and this one is read.
RUNNING = "running"
GOAL_REACHED = "goal-reached"
BUDGET_SPENT = "budget-spent"
BLOCKED = "blocked"
STOPPED = "stopped"
OUTCOMES = (RUNNING, GOAL_REACHED, BUDGET_SPENT, BLOCKED, STOPPED)
CLOSED = tuple(o for o in OUTCOMES if o != RUNNING)

# The fields this module owns. Anything else a caller writes is preserved verbatim - see
# the module docstring: this list documents, it does not gate.
FIELDS = ("schema", "run_id", "started_at", "ended_at", "outcome", "goal", "batch",
          "plan", "handoff")


class RunStateError(RuntimeError):
    """The run state exists but cannot be read. Never degraded to "there is no run": that
    reading would let a close write a blank record over a real run's identity."""


def path(repo_root: Path | str) -> Path:
    return Path(repo_root) / REL


def read(repo_root: Path | str) -> dict:
    """The current run state, or `{}` when there is none.

    Never fabricated: a run that was not opened has no start time, and this returns nothing
    rather than inventing one. A file that EXISTS but does not parse RAISES - "unreadable"
    is not the same fact as "absent", and reporting it as absent destroys the run it failed
    to read."""
    p = path(repo_root)
    try:
        text = p.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {}
    except OSError as exc:
        raise RunStateError(f"cannot read the run state at {p}: {exc}") from exc
    if not text.strip():
        return {}
    try:
        state = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RunStateError(
            f"the run state at {p} is not valid JSON ({exc}) - it holds the run's id, start "
            f"time, approved batch and outcome, and nothing may overwrite it blind. Repair "
            f"it, or delete it to start a fresh run (the run it described is then "
            f"unrecoverable, which is the point of saying so out loud)") from exc
    if not isinstance(state, dict):
        raise RunStateError(
            f"the run state at {p} is not an object (got {type(state).__name__})")
    return state


def write(repo_root: Path | str, state: dict) -> dict:
    """Persist the state atomically (a crash mid-write must not truncate a run's identity).
    Anything mutating an EXISTING state goes through `_mutate`, which holds the lock."""
    p = path(repo_root)
    p.parent.mkdir(parents=True, exist_ok=True)
    sdlc_md.atomic_write(p, json.dumps(state, indent=2))
    return state


def archive_dir(repo_root: Path | str) -> Path:
    return Path(repo_root) / ARCHIVE_REL


def archive_path(repo_root: Path | str, run_id: str) -> Path:
    return archive_dir(repo_root) / f"{run_id}.json"


def archive(repo_root: Path | str, state: dict | None = None) -> Path | None:
    """Copy a run's record to its own file, so a closed run stays readable after the next
    one opens. Returns the path written, or None when there is no run to archive.

    Keyed by `run_id` and rewritten in place, so archiving the same run twice leaves one
    record, not two - the boundary archives at close and the next open archives again as a
    safety net, and neither may double-count. A run with no `run_id` (nobody opened it) is
    NOT archived: a record with no identity cannot be joined to anything later."""
    state = read(repo_root) if state is None else state
    run_id = state.get("run_id")
    if not run_id:
        return None
    p = archive_path(repo_root, run_id)
    p.parent.mkdir(parents=True, exist_ok=True)
    sdlc_md.atomic_write(p, json.dumps(state, indent=2))
    return p


def archived(repo_root: Path | str) -> list[dict]:
    """Every archived run, oldest first. An unreadable record is SKIPPED rather than raising:
    unlike the live file, a damaged archive entry cannot cause a close to overwrite a real
    run's identity, so failing the whole read would lose the intact records for nothing."""
    d = archive_dir(repo_root)
    if not d.is_dir():
        return []
    out = []
    for p in sorted(d.glob("*.json")):
        try:
            rec = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(rec, dict) and rec.get("run_id"):
            out.append(rec)
    # Chronological, and the CYCLE INDEX breaks a tie before the run id does. Two cycles of a
    # fast run start inside the same second, and `short_ulid` is not monotonic within one - so
    # ordering on the id alone reads a rolling run's cycles back out of order, which is exactly
    # the sequence the archive exists to preserve.
    out.sort(key=lambda r: (r.get("started_at") or "",
                            int((r.get("cycle") or {}).get("index") or 0),
                            r.get("run_id") or ""))
    return out


def read_archived(repo_root: Path | str, run_id: str) -> dict:
    """One archived run by id, or `{}` when it was never archived."""
    p = archive_path(repo_root, run_id)
    try:
        rec = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return rec if isinstance(rec, dict) else {}


def is_open(repo_root: Path | str) -> bool:
    """True when a run is open (recorded and not yet closed)."""
    return read(repo_root).get("outcome") == RUNNING


def _blank() -> dict:
    """The record for a run nobody opened. `run_id` and `started_at` are None, and stay
    None: a close that invented a start time would put a false fact in the one file the
    next reader trusts. An unopened run says so."""
    return {"schema": SCHEMA, "run_id": None, "started_at": None, "ended_at": None,
            "outcome": RUNNING, "goal": None, "batch": [], "plan": None, "handoff": None}


def _mutate(repo_root: Path | str, fn) -> dict:
    """Read-modify-write the run state under the shared advisory lock.

    The single mutation path. Every writer goes through it, so a writer cannot read the
    state, be overtaken, and then write its stale copy back over the other's keys. It is
    the same advisory lock the id allocator and the finding filer take, for the same
    reason."""
    with sdlc_md.allocation_lock(repo_root):
        state = read(repo_root)          # inside the lock; a corrupt file still raises
        return write(repo_root, fn(state))


def _union(existing, incoming) -> list[str]:
    """The approved batch, accumulated: first-approval order, no duplicates. An approved
    unit is never removed by a later, narrower plan."""
    out = [sdlc_md.norm_id(b) for b in (existing or [])]
    seen = set(out)
    for b in incoming:
        n = sdlc_md.norm_id(b)
        if n not in seen:
            out.append(n)
            seen.add(n)
    return out


# The close artefacts a finalised run carries. A run holding ANY of them has been judged or
# closed - it is history - even if its `outcome` string was never moved off `running`: a close
# chain that records the goal-verdict but stops before the handoff leaves exactly that
# inconsistent state. `open_run` treats such a run as CLOSED so the next plan mints a fresh run
# rather than accumulating the new batch onto - and clobbering the verdict of - the judged one.
_CLOSE_ARTEFACTS = ("sprint_goal_verdict", "ended_at", "handoff")


def _is_spent(state: dict) -> bool:
    """True when the run is finalised: a terminal outcome, or a close artefact recorded while
    the outcome string still says `running`. A judged run is history regardless of the string."""
    if state.get("outcome") != RUNNING or not state.get("run_id"):
        return True
    return any(state.get(k) for k in _CLOSE_ARTEFACTS)


def open_run(repo_root: Path | str, batch: list[str] | None = None, goal: str | None = None,
             plan: str | None = None) -> dict:
    """Open a run, or re-plan the OPEN one.

    Re-running `sprint plan --write` must not restart the clock: an already-open run keeps
    its `run_id` and `started_at`, and its batch ACCUMULATES (see the module docstring - a
    narrowing re-cut must not silently discard work the run was approved to do). A run that
    has been CLOSED - or judged but left `running`, an inconsistent state - is history: the
    next open mints a fresh run with a fresh batch, so a handoff can never be re-attributed
    to the run after it.
    """
    def apply(state: dict) -> dict:
        if _is_spent(state):
            # ARCHIVE BEFORE BLANKING. This is the last moment the finished run exists: the
            # next statement replaces it. `close_run` normally archived it already and this
            # rewrites the same key, but a run judged and left `running` never reached a
            # close, and without this its record would be destroyed here unrecorded.
            archive(repo_root, state)
            state = {**_blank(), "run_id": f"RUN-{sdlc_md.short_ulid()}",
                     "started_at": sdlc_md.now_iso8601()}
        if batch is not None:
            state["batch"] = _union(state.get("batch"), batch)
        if goal is not None:
            state["goal"] = goal
        if plan is not None:
            state["plan"] = plan
        return state

    return _mutate(repo_root, apply)


def update(repo_root: Path | str, **fields) -> dict:
    """Merge fields into the run state. Unknown keys are kept: this is the extension point,
    and a silently-dropped field is a lie the next reader inherits. With no run open the
    fields land on a blank record (no fabricated start time). Locked: see `_mutate`."""
    if "outcome" in fields:
        _check_outcome(fields["outcome"])

    def apply(state: dict) -> dict:
        state = state or _blank()
        state.update(fields)
        return state

    return _mutate(repo_root, apply)


def _check_outcome(outcome: str) -> None:
    if outcome not in OUTCOMES:
        raise ValueError(f"unknown run outcome {outcome!r} - expected one of "
                         f"{', '.join(OUTCOMES)}")


def close_run(repo_root: Path | str, outcome: str, handoff: str | None = None) -> dict:
    """Close the run with its outcome (and the handoff that documents it). Idempotent - a
    second close re-stamps the outcome rather than raising. Every field an earlier caller
    added survives, and a run nobody opened closes onto a blank record rather than a
    fabricated one."""
    _check_outcome(outcome)
    if outcome == RUNNING:
        raise ValueError(f"{RUNNING!r} is not a close outcome - expected one of "
                         f"{', '.join(CLOSED)}")

    def apply(state: dict) -> dict:
        state = state or _blank()
        state["outcome"] = outcome
        state["ended_at"] = sdlc_md.now_iso8601()
        if handoff is not None:
            state["handoff"] = handoff
        return state

    state = _mutate(repo_root, apply)
    # The record is final here, so keep it: the next `open_run` overwrites the live file, and
    # a closed run that only ever existed there is a sprint whose evidence expires.
    archive(repo_root, state)
    return state
