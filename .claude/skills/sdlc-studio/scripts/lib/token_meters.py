#!/usr/bin/env python3
"""The token meters: which agent harness's store a reading is taken from, and the rule that no
reading is ever formed from two.

A sprint's token cost is read off the store the running harness keeps: Claude Code writes a
transcript per session, and Cursor, Copilot CLI, OpenCode and Codex CLI each persist usage
elsewhere.
A leftover store of another harness is not this run's meter, and booking it onto the run is
worse than reporting no figure. So one harness is chosen, and only its reader is consulted:

1. `SDLC_STUDIO_HARNESS` names it, matched without regard to case or surrounding whitespace.
   It wins outright, over every signal and every store; a value naming no harness in
   `HARNESSES` reads nothing, and an empty or blank one counts as unset.
2. Otherwise the environment: a harness is signalled when one of its `SIGNALS` is set to a
   non-empty value. Exactly one signalled harness is chosen, whatever stores sit on disk.
3. Otherwise the stores on disk: exactly one harness whose store is present, by its reader's
   `store` probe (Claude's: a transcript in its transcript directory).
4. Otherwise Claude, whose reader then names the directory it found no transcript in.

Two or more candidates at step 2, or at step 3, give tokens None with a reason naming every
candidate, and no reader's `read` is called, so no total is formed. Nothing falls back to a
second harness: a chosen reader that returns no reading is the reading.

Claude's reader is built in, because its body shares the transcript code `run_state` re-derives
earlier readings with; the caller passes it in as `claude`. Every other harness's reader is its
own module, `lib/meter_<harness>.py`, loaded by name, so a reader is added without editing this
module or `run_state`. A module provides:

* `read(repo_root, env) -> dict` - required. A reading, or `{"tokens": None, "reason"}`.
* `store(repo_root, env) -> str | None` - optional. Where this repo's store sits, or None. A
  reader without it is chosen only by name or by signal, never by a store on disk.
* `SIGNALS` - optional. A tuple of further environment variable names that signal the
  harness, beside the ones `SIGNALS` here names.

`env` is the environment mapping the selection read; a reader reads its variables from it.

A reading is `{"tokens", "cache_read", "source", "basis", "includes_subagents", ...}`:
`tokens` is input + output + cache write, cache reads excluded; `cache_read` is the cache reads,
apart from it, or None where the store does not separate them; `source` names the store read;
`basis` is the sentence saying what was counted; `includes_subagents` says whether delegated
agents' spend is in it. A reading breaking that contract is refused here, never passed on. Every
result of `read`, a refusal included, carries `harness` and `selected_by`.
"""
from __future__ import annotations

import importlib
import os
from collections.abc import Mapping
from pathlib import Path

#: The environment variable that names the harness outright.
HARNESS_ENV = "SDLC_STUDIO_HARNESS"
CLAUDE, CURSOR, COPILOT, OPENCODE, CODEX = "claude", "cursor", "copilot", "opencode", "codex"
#: Every harness a reading can be taken for, in the order a refusal names them.
HARNESSES = (CLAUDE, CURSOR, COPILOT, OPENCODE, CODEX)
#: The environment variables that signal each harness is the one running this process. A
#: reader module adds to its own harness's with a `SIGNALS` tuple. Codex's is the thread id a
#: codex-cli 0.160.0 session set in the shell its command ran in, read from a captured session.
SIGNALS = {CLAUDE: ("CLAUDECODE",), CURSOR: ("CURSOR_AGENT",), COPILOT: ("COPILOT_HOME",),
           OPENCODE: ("OPENCODE", "OPENCODE_DB"), CODEX: ("CODEX_THREAD_ID",)}
#: The key a reading, and each stamp taken from one, names its harness under.
HARNESS = "harness"
#: The key a reading and a stamp carry the cache reads under, outside `tokens`.
CACHE_READ = "cache_read"


def harness_of(row) -> str:
    """The harness a reading or stamp names. One naming none is Claude's: every reading taken
    before readings named a harness was, and a re-derived row is read from a Claude transcript."""
    named = row.get(HARNESS) if isinstance(row, dict) else None
    return named if isinstance(named, str) and named else CLAUDE


def load_reader(harness: str):
    """The reader module for `harness`, `lib/meter_<harness>.py`, or None when none is installed.

    RAISES whatever importing an installed module raises: a reader that is present but broken
    is not one that is absent, and the caller reports the difference."""
    name = f"{__package__}.meter_{harness}"
    try:
        return importlib.import_module(name)
    except ModuleNotFoundError as exc:
        if exc.name == name:
            return None
        raise


class _Readers:
    """Each harness's reader, loaded at most once per reading: Claude's as passed in, the rest by
    name. A module that fails to load is held as its exception."""

    def __init__(self, claude) -> None:
        self._got: dict = {CLAUDE: claude}

    def get(self, harness: str):
        if harness not in self._got:
            try:
                self._got[harness] = load_reader(harness)
            except Exception as exc:  # noqa: BLE001 - a reader is a plug-in; reported, not raised
                self._got[harness] = exc
        return self._got[harness]


def _signals(harness: str, reader) -> list[str]:
    """`harness`'s signal variables: this module's, then any its reader module adds."""
    extra = getattr(reader, "SIGNALS", ()) if not isinstance(reader, Exception) else ()
    extra = extra if isinstance(extra, (tuple, list)) else ()
    return list(dict.fromkeys([*SIGNALS[harness], *(v for v in extra if isinstance(v, str))]))


def _store(harness: str, reader, repo_root: Path, env: Mapping) -> str | None:
    """Where `harness`'s store for this repo sits, or None. A reader that cannot be loaded, or
    whose probe raises, may have a store present, so it is reported as a candidate."""
    if isinstance(reader, Exception):
        return f"its reader could not be loaded ({type(reader).__name__})"
    probe = getattr(reader, "store", None)
    if probe is None:
        return None
    try:
        where = probe(repo_root, env)
    except Exception as exc:  # noqa: BLE001 - a reader is a plug-in; reported, not raised
        return f"its store could not be probed ({type(exc).__name__})"
    return str(where) if where else None


def _refusal(why: str, candidates: list[str], named: dict) -> dict:
    listed = ", ".join(f"{h} ({named[h]})" for h in candidates)
    return {HARNESS: None, "candidates": candidates, "reason": (
        f"{why}: {listed}. No reading is taken and no total is formed from two harnesses; set "
        f"{HARNESS_ENV} to the harness running this session")}


def selection_variables() -> list[str]:
    """Every environment variable that signals or names a harness: `HARNESS_ENV`, each harness's
    `SIGNALS`, and the further signals each installed reader module names. A test that must not
    inherit the harness running it clears these."""
    readers = _Readers(None)
    names = [HARNESS_ENV]
    for h in HARNESSES:
        names += _signals(h, readers.get(h) if h != CLAUDE else None)
    return list(dict.fromkeys(names))


def select(repo_root: Path | str, claude, env: Mapping | None = None) -> dict:
    """The harness to read, `{"harness", "selected_by"}`, or `{"harness": None, "candidates",
    "reason"}` when none can be chosen. The order is this module's docstring's."""
    env = os.environ if env is None else env
    return _select(Path(repo_root), _Readers(claude), env)


def _select(repo_root: Path, readers: _Readers, env: Mapping) -> dict:
    named = (env.get(HARNESS_ENV) or "").strip().lower()
    if named:
        if named not in HARNESSES:
            return {HARNESS: None, "candidates": [], "reason": (
                f"{HARNESS_ENV} is {env.get(HARNESS_ENV)!r}, which names none of the harnesses "
                f"this meter reads ({', '.join(HARNESSES)}), so no store is read")}
        return {HARNESS: named, "selected_by": HARNESS_ENV}
    signalled = {}
    for h in HARNESSES:
        hits = [v for v in _signals(h, readers.get(h) if h != CLAUDE else None) if env.get(v)]
        if hits:
            signalled[h] = ", ".join(hits)
    if len(signalled) == 1:
        (h, hits), = signalled.items()
        return {HARNESS: h, "selected_by": f"the environment ({hits})"}
    if signalled:
        return _refusal(f"{HARNESS_ENV} is not set and the environment signals "
                        f"{len(signalled)} harnesses", list(signalled), signalled)
    stores = {}
    for h in HARNESSES:
        where = _store(h, readers.get(h), repo_root, env)
        if where:
            stores[h] = where
    if len(stores) == 1:
        (h, where), = stores.items()
        return {HARNESS: h, "selected_by": f"the only harness store present ({where})"}
    if stores:
        return _refusal(f"{HARNESS_ENV} is not set, no harness is signalled, and "
                        f"{len(stores)} harness stores are present", list(stores), stores)
    return {HARNESS: CLAUDE,
            "selected_by": "the default: no harness is signalled and no harness store is present"}


def _fault(got: dict) -> str | None:
    """What a reading with a figure breaks of the reading contract, or None."""
    def count(v) -> bool:
        return isinstance(v, int) and not isinstance(v, bool) and v >= 0
    if not count(got.get("tokens")):
        return f"tokens {got.get('tokens')!r} is not a count"
    if CACHE_READ not in got or not (got[CACHE_READ] is None or count(got[CACHE_READ])):
        return f"{CACHE_READ} {got.get(CACHE_READ)!r} is neither a count nor None"
    for key in ("source", "basis"):
        if not isinstance(got.get(key), str) or not got[key].strip():
            return f"it names no {key}"
    if not isinstance(got.get("includes_subagents"), bool):
        return "it does not say whether delegated agents' spend is in it (includes_subagents)"
    return None


def _checked(harness: str, got) -> dict:
    """A reader's result under the reading contract, its harness named. Claude's own reasons are
    passed on as written; every other reader's is prefixed with its harness."""
    if not isinstance(got, dict):
        return {"tokens": None, "reason": f"the {harness} reader returned "
                                          f"{type(got).__name__}, not a reading"}
    if got.get("tokens") is None:
        reason = got.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            reason = "it gave no reading and no reason"
        return {**got, "tokens": None,
                "reason": reason if harness == CLAUDE else f"the {harness} reader: {reason}"}
    fault = _fault(got)
    if fault:
        return {"tokens": None, "reason": f"the {harness} reader returned a reading that breaks "
                                          f"the reading contract, so it is refused: {fault}"}
    return dict(got)


def read(repo_root: Path | str, claude, env: Mapping | None = None) -> dict:
    """One reading of the running harness's meter, or tokens None with the reason. Whatever a
    reader's import, `store` or `read` raises is reported by its type, never by its message,
    which may carry a request's credentials."""
    env = os.environ if env is None else env
    root = Path(repo_root)
    readers = _Readers(claude)
    choice = _select(root, readers, env)
    harness = choice[HARNESS]
    if harness is None:
        return {"tokens": None, HARNESS: None, "selected_by": None,
                "candidates": choice["candidates"], "reason": choice["reason"]}
    reader = readers.get(harness)
    if reader is None:
        got = {"tokens": None, "reason": (
            f"no {harness} token reader is installed (lib/meter_{harness}.py), so this "
            f"{harness} run's tokens cannot be read, and no other harness's store is read in "
            f"their place")}
    elif isinstance(reader, Exception):
        got = {"tokens": None, "reason": (
            f"the {harness} reader could not be loaded ({type(reader).__name__}), so no "
            f"reading is taken")}
    else:
        try:
            got = _checked(harness, reader.read(root, env))
        except Exception as exc:  # noqa: BLE001 - a reader is a plug-in; reported, not raised
            got = {"tokens": None, "reason": (
                f"the {harness} reader raised {type(exc).__name__} rather than returning a "
                f"reason, so no reading is taken")}
    return {**got, HARNESS: harness, "selected_by": choice["selected_by"]}
