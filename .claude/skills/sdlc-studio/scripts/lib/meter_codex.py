#!/usr/bin/env python3
"""Codex CLI's token reader, the module `token_meters` loads for the Codex harness.

Codex CLI 0.160.0 keeps its state in `HOME_ENV` when it is set and not empty, else under
`HOME_REL` in the user's home. Its state store,
`STATE_DB` (SQLite, in WAL mode), holds a `threads` row per session: the session's working
directory `cwd`, the `rollout_path` of the JSONL rollout the session appends its events to, its
`model`, and `tokens_used`, the session's input + output with the cached input inside it. Spawned
agent threads are listed in its `thread_spawn_edges`. `tokens_used` does not split the cached
input out, so each thread's figure is read from its rollout instead: the last `event_msg` of type
`token_count`, whose `info.total_token_usage` is the thread's running total, `USAGE_FIELDS`.

That total's `input_tokens` includes its `cached_input_tokens` (a captured session recorded
14524 input with 12288 of it cached), so the uncached input is `input_tokens` less the cached
input and the cache write, never below zero, and the cached input is `cache_read`, apart from
`tokens`. The cache write is taken to sit inside `input_tokens` as the cached input does; no
captured session recorded one. `output_tokens` holds the reasoning tokens, since the pinned build
writes `total_tokens` as `input_tokens` + `output_tokens`; a total that is not that sum is refused,
since its parts could then overlap. A cache write is not split by duration, so each is booked at
five minutes and priced from `run_state.TOKEN_WEIGHTS` as the figure is formed. Each thread's
components are also summed under its own `model` (`run_state.BY_MODEL`, "" for a thread naming
none), so a dollar figure prices each model at its own rate; a reading over one model is named
as it, and one over more than one as `run_state.SESSION_MODEL_MIXED`, never a name joined from
the set.

A reading sums every thread whose `cwd` is the workspace or a directory under it, and a spawned
thread there is counted with the rest, except a thread whose `cwd` is under the lane worktrees,
`lanes.RUN_WORKTREES`, where `sprint lane run --harness codex` runs `codex exec`: it is left
out, since a lane's spend reaches the run once, through its delegated record. A reading says
delegated spend is in it (`includes_subagents`) only when it counts a thread a spawn edge names
as a child. A missing, locked or unreadable store, a store with no thread for the workspace
outside its lane worktrees, or a thread that has spent tokens whose rollout holds no usable
count, is tokens None with the reason, never zero; a thread whose `tokens_used` is 0 and whose
rollout holds no usable count has spent nothing, and adds nothing.
The store is never written: every open is a `mode=ro` URI, though SQLite may create the store's
`-wal` and `-shm` files beside it, as any reader of a WAL database may, and leave them. A store
another process has locked is waited on for `TIMEOUT_SECONDS` at most. Reasons name an error by its type, never by its message.
"""
from __future__ import annotations

import json
import os
import sqlite3
from collections.abc import Mapping
from pathlib import Path

from .token_meters import CACHE_READ

#: The variable that names Codex's home, as codex-cli reads it.
HOME_ENV = "CODEX_HOME"
#: Codex's home under the user's HOME, when `HOME_ENV` is unset or empty.
HOME_REL = ".codex"
#: The state store codex-cli 0.160.0 writes in its home.
STATE_DB = "state_5.sqlite"
#: The counts a rollout's `token_count` total carries that the reading is formed from.
USAGE_FIELDS = ("input_tokens", "cached_input_tokens", "cache_write_input_tokens",
                "output_tokens")
#: The longest a reading waits on a store another process holds locked, in seconds.
TIMEOUT_SECONDS = 1.0


def codex_home(env: Mapping) -> Path:
    """Where Codex keeps its state: `HOME_ENV` when `env` sets it and it is not empty, else
    `HOME_REL` under the HOME `env` names."""
    named = env.get(HOME_ENV)
    if named:
        return Path(named)
    return Path(env.get("HOME") or str(Path.home())) / HOME_REL


def store(repo_root: Path, env: Mapping) -> str | None:
    """The state store, when it holds a thread for the workspace `repo_root`, else None. RAISES
    what reading the store raises: a store present but unreadable may be this run's."""
    db = codex_home(env) / STATE_DB
    if not db.is_file():
        return None
    threads, _ = _threads(db, repo_root)
    return str(db) if threads else None


def read(repo_root: Path, env: Mapping) -> dict:
    """The workspace `repo_root`'s reading from Codex's state store and the rollouts its threads
    name, or tokens None with the reason."""
    from . import run_state  # noqa: PLC0415 - lazy: run_state loads this reader

    db = codex_home(env) / STATE_DB
    workspace = os.path.realpath(repo_root)

    def none(why: str) -> dict:
        return {"tokens": None, "reason": f"{why}, so this run's tokens cannot be read"}
    if not db.is_file():
        return none(f"no Codex state store sits at {db}")
    try:
        threads, spawned = _threads(db, repo_root)
    except (sqlite3.Error, OSError) as exc:
        return none(f"the Codex state store {db} could not be read ({type(exc).__name__})")
    if not threads:
        return none(f"the Codex state store {db} holds no thread whose working directory is "
                    f"{workspace} or under it outside its lane worktrees")
    comps = {"input": 0, "output": 0, "cache_write_5m": 0, "cache_write_1h": 0, "cache_read": 0}
    split: dict[str, dict] = {}
    models = set()
    for thread_id, rollout, used, model in threads:
        usage = _usage(rollout)
        if isinstance(usage, str):
            if not used:
                continue
            return none(f"Codex thread {thread_id}'s rollout {rollout} {usage}")
        cached, write = usage["cached_input_tokens"], usage["cache_write_input_tokens"]
        part = {"input": max(usage["input_tokens"] - cached - write, 0),
                "output": usage["output_tokens"], "cache_write_5m": write, "cache_write_1h": 0,
                "cache_read": cached}
        # The thread's spend under its own model, so the split sums to the reading.
        held = split.setdefault(model or "", dict.fromkeys(comps, 0))
        for c, v in part.items():
            comps[c] += v
            held[c] += v
        if model:
            models.add(model)
    n = len(threads)
    basis = (f"Codex state store {db}, the last token_count total of each of its {n} "
             f"thread{'' if n == 1 else 's'} for {workspace}, summed: input is input_tokens less "
             f"its cached input and cache write, never below zero; the cached input is the cache "
             f"read, apart from tokens; tokens is input + output + cache write, and the priced "
             f"figure weighs every component, each cache write at the five-minute weight")
    return {"tokens": comps["input"] + comps["output"] + comps["cache_write_5m"],
            CACHE_READ: comps["cache_read"], "components": comps,
            "priced": run_state.price(comps), "threads": n,
            "model": (next(iter(models)) if len(models) == 1 else
                      run_state.SESSION_MODEL_MIXED if models else None),
            run_state.BY_MODEL: split,
            "source": f"the Codex state store {db} and the rollouts it names", "basis": basis,
            "includes_subagents": bool(spawned)}


def _threads(db: Path, repo_root: Path) -> tuple[list[tuple], set[str]]:
    """Each thread of the store `db` whose working directory is the workspace `repo_root` or under
    it but not under its lane worktrees, as (id, rollout path, tokens_used, model), and which of
    them were spawned. The store is opened read-only; RAISES what SQLite raises."""
    from . import lanes  # noqa: PLC0415 - lazy: only a reading needs the lane worktrees
    con = sqlite3.connect(f"{db.absolute().as_uri()}?mode=ro", uri=True, timeout=TIMEOUT_SECONDS)
    try:
        rows = con.execute("SELECT id, cwd, rollout_path, tokens_used, model FROM threads "
                           "ORDER BY created_at, id").fetchall()
        children = {row[0] for row in con.execute("SELECT child_thread_id FROM thread_spawn_edges")}
    finally:
        con.close()
    workspace = os.path.realpath(repo_root)
    worktrees = os.path.realpath(Path(repo_root) / lanes.RUN_WORKTREES)
    mine = [(tid, db.parent / path, used, model) for tid, cwd, path, used, model in rows
            if isinstance(cwd, str) and _within(cwd, workspace) and not _within(cwd, worktrees)]
    return mine, children & {row[0] for row in mine}


def _within(cwd: str, workspace: str) -> bool:
    here = os.path.realpath(cwd)
    return here == workspace or here.startswith(workspace.rstrip(os.sep) + os.sep)


def _count(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _usage(rollout: Path) -> dict | str:
    """The last `token_count` total the rollout records, or what is wrong with it."""
    last = None
    try:
        with rollout.open("rb") as fh:
            for raw in fh:
                if b'"token_count"' not in raw:
                    continue
                try:
                    event = json.loads(raw)
                except ValueError:
                    continue
                payload = event.get("payload") if isinstance(event, dict) else None
                info = payload.get("info") if isinstance(payload, dict) else None
                if (isinstance(info, dict) and payload.get("type") == "token_count"
                        and isinstance(info.get("total_token_usage"), dict)):
                    last = info["total_token_usage"]
    except FileNotFoundError:
        return "is missing"
    except OSError as exc:
        return f"could not be read ({type(exc).__name__})"
    if last is None:
        return "records no token count"
    usage = {f: last.get(f, 0 if f == "cache_write_input_tokens" else None) for f in USAGE_FIELDS}
    bad = [f for f, v in usage.items() if not _count(v)]
    if bad:
        return f"records a token count whose {', '.join(bad)} is not a count"
    total = last.get("total_tokens")
    if total is not None and total != usage["input_tokens"] + usage["output_tokens"]:
        return ("records a total_tokens that is not input_tokens + output_tokens, the relation "
                "the pinned build keeps, so its parts may overlap")
    return usage
