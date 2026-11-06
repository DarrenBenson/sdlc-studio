#!/usr/bin/env python3
"""Copilot CLI's token reader, the module `token_meters` loads for the Copilot harness.

The Copilot CLI keeps one events file per session, `session-state/<id>/events.jsonl` under its
home (`HOME_ENV` when not blank, else `~/.copilot`), one JSON event a line. The 1.0.106 build
this reader is pinned against writes `session.start` first, whose `context` records the
directory the session ran in (`gitRoot`, else `cwd`), then per call a `session.usage_record`
whose `data.usage` holds `inputTokens`, `outputTokens`, `cacheReadTokens`, `cacheWriteTokens`
and `reasoningTokens`, a `session.usage_checkpoint` holding the session's running totals, and
on exit a `session.shutdown` whose `data.modelMetrics.<model>.usage` holds the same five counts
summed over every call of the session so far. A resumed session appends to the same file, and
its next shutdown's aggregate covers the calls before the resume as well as after it.

So a session is read from one place for each span, never two: the last shutdown's aggregate,
plus the per-call records written after it, which no aggregate has folded yet. A live session
that has not shut down is its records alone. A checkpoint is a running total, never a spend, and
is never read. A session recording another directory than this repo's is never read; of this
repo's sessions, the one whose events file changed last is the reading.

`inputTokens` already holds the cache reads and writes, so the uncached input is `inputTokens`
less both, and a count where it would fall below zero is refused rather than clamped, since the
counts then overlap in a way this reader was not pinned against. `reasoningTokens` is never
added to `outputTokens`: the CLI's own priced `tokenDetails` carry input, cache read, cache
write and output, and no reasoning line. `tokens` is the uncached input + output + cache
write, and the cache reads are `cache_read`, apart from it. The aggregate does not split a cache
write by duration, so every write, a per-call record's included, is booked at five minutes, as
an unsplit Claude write is, and the components are priced from `run_state.TOKEN_WEIGHTS` as the
figure is formed. One model reads as itself; more than one reads as `run_state`'s mixed marker.

A missing store, a session recording no usage, a line that is not JSON or a counted usage value
that is not a count reads tokens None with the reason, never zero and never a total quietly
short of a skipped record. The store is only read, never written.
"""
from __future__ import annotations

import json
import os
from collections.abc import Mapping
from pathlib import Path

from .token_meters import CACHE_READ

#: The Copilot CLI's home directory, which also signals Copilot to `token_meters`.
HOME_ENV = "COPILOT_HOME"
#: Where the sessions sit under that home, and each session's events file.
STATE_DIR = "session-state"
EVENTS_FILE = "events.jsonl"
#: The event types this reader reads. A checkpoint is named so the docstring's rule has a
#: name, and is never read.
START, RECORD, CHECKPOINT, SHUTDOWN = ("session.start", "session.usage_record",
                                       "session.usage_checkpoint", "session.shutdown")
#: The usage counts a reading is formed from. `reasoningTokens` is not one of them.
INPUT, OUTPUT, CACHE_READS, CACHE_WRITES = ("inputTokens", "outputTokens", "cacheReadTokens",
                                            "cacheWriteTokens")
COUNTED = (INPUT, OUTPUT, CACHE_READS, CACHE_WRITES)


class _Malformed(ValueError):
    """A counted value or a line this reader cannot read; its message is the reason."""


def copilot_home(env: Mapping) -> Path:
    """The Copilot CLI's home: `HOME_ENV` when not blank, else `~/.copilot` under `HOME`."""
    home = env.get(HOME_ENV) or ""
    if home.strip():
        return Path(home)
    return Path(env.get("HOME") or str(Path.home())) / ".copilot"


def _directory(events: Path) -> str | None:
    """The directory session `events` recorded at its start (`gitRoot`, else `cwd`), from its
    first line alone, or None when that line is not a `session.start` naming one."""
    try:
        with events.open("rb") as fh:
            first = json.loads(fh.readline())
    except (OSError, ValueError):
        return None
    if not (isinstance(first, dict) and first.get("type") == START):
        return None
    data = first.get("data")
    context = data.get("context") if isinstance(data, dict) else None
    if not isinstance(context, dict):
        return None
    named = context.get("gitRoot") or context.get("cwd")
    return named if isinstance(named, str) and named.strip() else None


def sessions(repo_root: Path | str, env: Mapping) -> list[Path]:
    """The events files of the sessions recording `repo_root`, the latest changed first."""
    state = copilot_home(env) / STATE_DIR
    want = os.path.realpath(os.fspath(repo_root))
    try:
        found = [d / EVENTS_FILE for d in state.iterdir() if (d / EVENTS_FILE).is_file()]
    except OSError:
        return []
    mine = []
    for path in found:
        named = _directory(path)
        if named and os.path.realpath(named) == want:
            try:
                mine.append((path.stat().st_mtime_ns, str(path), path))
            except OSError:
                continue
    return [path for *_, path in sorted(mine, reverse=True)]


def store(repo_root: Path | str, env: Mapping) -> str | None:
    """The events file this repo's reading would be taken from, or None."""
    mine = sessions(repo_root, env)
    return str(mine[0]) if mine else None


def read(repo_root: Path | str, env: Mapping) -> dict:
    """This repo's latest Copilot CLI session's reading, or tokens None with the reason."""
    state = copilot_home(env) / STATE_DIR
    if not state.is_dir():
        return {"tokens": None, "reason": f"no Copilot CLI session store sits at {state}, so "
                                          f"this run's tokens cannot be read"}
    mine = sessions(repo_root, env)
    if not mine:
        return {"tokens": None, "reason": (
            f"no Copilot CLI session under {state} records {os.fspath(repo_root)} as its "
            f"directory, so this run's tokens cannot be read")}
    return read_events(mine[0])


def _count(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _components(usage, where: str) -> dict:
    """One usage object's components. RAISES `_Malformed` naming the value that is not a count,
    or an `inputTokens` short of the cache reads and writes it holds."""
    if not isinstance(usage, dict):
        raise _Malformed(f"{where} carries no usage object")
    for field in COUNTED:
        if not _count(usage.get(field)):
            raise _Malformed(f"{where} has {field} {usage.get(field)!r}, not a count")
    uncached = usage[INPUT] - usage[CACHE_READS] - usage[CACHE_WRITES]
    if uncached < 0:
        raise _Malformed(f"{where} has {INPUT} {usage[INPUT]} short of its cache reads and "
                         f"writes ({usage[CACHE_READS] + usage[CACHE_WRITES]}), which it holds")
    return {"input": uncached, "output": usage[OUTPUT], "cache_write_5m": usage[CACHE_WRITES],
            "cache_write_1h": 0, "cache_read": usage[CACHE_READS]}


def _add(total: dict, comps: dict) -> None:
    for key, value in comps.items():
        total[key] = total.get(key, 0) + value


def _scan(events: Path) -> tuple[tuple[int, dict] | None, list[tuple[int, dict]]]:
    """The last shutdown's line and data, and the per-call records after it. RAISES `_Malformed`
    on a line that is not a JSON object, since it may have been any event, a shutdown included."""
    last, after = None, []
    with events.open("rb") as fh:
        for lineno, raw in enumerate(fh, 1):
            if not raw.strip():
                continue
            try:
                event = json.loads(raw)
            except ValueError:
                event = None
            if not isinstance(event, dict):
                raise _Malformed(f"line {lineno} is not a JSON object")
            data = event.get("data")
            if event.get("type") == SHUTDOWN:
                last, after = (lineno, data), []
            elif event.get("type") == RECORD:
                after.append((lineno, data))
    return last, after


def read_events(events: Path) -> dict:
    """The reading session `events` holds: its last shutdown's aggregate plus the records after
    it, or tokens None with the reason when none can be formed."""
    from . import run_state  # noqa: PLC0415 - lazy: run_state loads this reader

    def none(why: str) -> dict:
        return {"tokens": None, "reason": f"the Copilot CLI session events {events} {why}, so "
                                          f"this run's tokens cannot be read"}
    total = dict.fromkeys(run_state.TOKEN_COMPONENTS, 0)
    models: set[str] = set()
    try:
        last, after = _scan(events)
        if last is not None:
            lineno, data = last
            metrics = data.get("modelMetrics") if isinstance(data, dict) else None
            if not isinstance(metrics, dict):
                raise _Malformed(f"the shutdown on line {lineno} carries no modelMetrics object")
            for model, entry in metrics.items():
                usage = entry.get("usage") if isinstance(entry, dict) else None
                _add(total, _components(usage, f"the shutdown on line {lineno}, model {model},"))
                models.add(model)
        for lineno, data in after:
            usage = data.get("usage") if isinstance(data, dict) else None
            _add(total, _components(usage, f"the usage record on line {lineno}"))
            if isinstance(usage.get("model"), str) and usage["model"]:
                models.add(usage["model"])
    except _Malformed as exc:
        return none(f"cannot be read: {exc}")
    except OSError as exc:
        return none(f"could not be read ({type(exc).__name__})")
    tokens = total["input"] + total["output"] + total["cache_write_5m"]
    if not tokens:
        return none("records no usage yet")
    ended = last is not None and not after
    if last is None:
        read_as = f"{len(after)} per-call usage record{'' if len(after) == 1 else 's'} summed"
    else:
        read_as = (f"the session.shutdown aggregate on line {last[0]}"
                   + (f" plus the {len(after)} per-call usage record"
                      f"{'' if len(after) == 1 else 's'} after it" if after else ""))
    basis = (f"the Copilot CLI session events {events}: {read_as}, the running-total checkpoints "
             f"not read; input is inputTokens less its cache reads and writes, reasoningTokens is "
             f"not added to output, tokens is input + output + cache write, cache reads apart, and the "
             f"priced figure weighs every component, each cache write at the five-minute weight "
             f"since the aggregate does not split it")
    model = (next(iter(models)) if len(models) == 1
             else run_state.SESSION_MODEL_MIXED if models else None)
    return {"tokens": tokens, CACHE_READ: total["cache_read"], "components": total,
            "priced": run_state.price(total), "model": model, "ended": ended,
            "calls_after_shutdown": len(after), "basis": basis, "includes_subagents": False,
            "source": f"the Copilot CLI session events {events}"}
