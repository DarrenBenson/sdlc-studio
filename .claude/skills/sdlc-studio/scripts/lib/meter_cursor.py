#!/usr/bin/env python3
"""Cursor's token reader, the module `token_meters` loads for the Cursor harness.

A Cursor cloud agent writes no Claude transcript, so its spend is read from Cursor's cloud usage
API, `GET /v1/agents/{id}/usage`, whose `totalUsage` holds `inputTokens`, `outputTokens`,
`cacheWriteTokens`, `cacheReadTokens` and `totalTokens`. The call is opt-in: it is made only
when a Cursor API key (`KEY_ENV`) and the agent's id (`AGENT_ENV`) are both set, and otherwise
no request is made and the reading names the variable that is missing.

`tokens` is input + output + cache write, the basis every reader counts on; the cache reads are
`cache_read`, apart from it, and `totalTokens`, which holds them, is never the figure. An answer
carrying a `totalTokens` that is not the sum of the four is refused, since the four would then
overlap.

The call never holds the close: it runs on a worker thread joined for at most
`TIMEOUT_SECONDS`, and an HTTP error, a timeout, an unreachable API, a malformed answer or a
run with no usage recorded yet is tokens None with the reason, never zero. A redirect is
refused, not followed, so the key is never sent where a redirect points. The key is sent in one
request header and nowhere else: no reason quotes an exception's message, an error's body or
its headers, and `source` is built from the agent id, never from the URL. A URL that is not
https is refused before any request, unless it is http on a loopback address, as a test's
local stub is, so an http override does not send the key in cleartext to the host it names;
the reason names `API_ENV`, never its value.

`read` decides which surface a reading comes from, and takes it from one alone: the cloud API
when both variables are set, else the Cursor CLI's chat store for this workspace. The CLI's
2026.10.22 build keeps that store at `chats/<md5 of the workspace's absolute path>/<chat id>/`
under its config directory, each chat a `store.db` (SQLite, tables `blobs` and `meta`), a
`meta.json` or both, and records no usage in it; a print run reports its usage on its stdout.
So the CLI's figure comes from the ledger `LEDGER_REL` under the workspace, a line per response
that `cursor_usage_hook.py`, run as the CLI's `HOOK_EVENT` hook, appends from the counts its
payload carries (`LEDGER_FIELDS`). A ledger is read as measured: each line's four counts are
summed and priced (`read_ledger`), and a line that is not a JSON object carrying the four as
counts is skipped and counted, never fatal. With no ledger, a CLI reading is tokens None with
the reason, never zero; only the chat directory's listing and each `store.db`'s table names
are read, and no terminal output. The store is never written:
a `store.db` whose `-wal` is empty or absent is read in place with SQLite's immutable read-only
open, and one with a `-wal` (a chat whose tables may sit in the WAL alone) through a copy of the
two in a temporary directory, since a read-only open of the store itself writes its `-shm`.
"""
from __future__ import annotations

import hashlib
import ipaddress
import json
import os
import shutil
import sqlite3
import tempfile
import threading
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Mapping
from pathlib import Path

from .token_meters import CACHE_READ

#: The Cursor API key. It is sent as the request's bearer token and is never written into a
#: reading, a reason or a source.
KEY_ENV = "CURSOR_API_KEY"
#: The Cursor cloud agent's id, the usage API's path parameter.
AGENT_ENV = "SDLC_STUDIO_CURSOR_AGENT_ID"
#: The API's base URL, overridable so a test reaches a local stub and never the network: an
#: https URL, or an http one on a loopback address, and any other is refused.
API_ENV = "SDLC_STUDIO_CURSOR_API"
API_BASE = "https://api.cursor.com"
#: The longest the close waits for the usage API, connect and answer together.
TIMEOUT_SECONDS = 5.0
#: The largest answer read; a longer one is refused rather than parsed.
MAX_BYTES = 1 << 20
#: The agent id signals Cursor to `token_meters`. The key does not: a key exported in another
#: harness's shell is not a Cursor run.
SIGNALS = (AGENT_ENV,)
#: The `totalUsage` fields `tokens` sums, and the cache reads it leaves out.
COUNTED = ("inputTokens", "outputTokens", "cacheWriteTokens")
CACHE_READS = "cacheReadTokens"
TOTAL = "totalTokens"
#: The Cursor CLI's config directory, as its 2026.10.22 build resolves it: `CONFIG_ENV` when not
#: blank, else `$XDG_CONFIG_HOME/cursor` when `XDG_ENV` is not blank, else `~/.cursor`.
CONFIG_ENV = "CURSOR_CONFIG_DIR"
XDG_ENV = "XDG_CONFIG_HOME"
#: The tables of the chat store that build wrote, neither holding usage: `meta`, the chat's
#: settings, and `blobs`, its messages and conversation state. A store with other tables is not
#: read as one keeping no usage.
STORE_TABLES = ("blobs", "meta")
#: The ledger the CLI's hook appends to and this reader sums, relative to the workspace root.
LEDGER_REL = Path("sdlc-studio") / ".local" / "cursor-usage.jsonl"
#: The CLI hook entry whose payload carries each response's usage.
HOOK_EVENT = "afterAgentResponse"
#: That payload's counts, as the 2026.10.22-27dcf5f build names them, and each line keeps them.
LEDGER_FIELDS = ("input_tokens", "output_tokens", "cache_read_tokens", "cache_write_tokens")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Refuses every redirect, which then surfaces as its HTTP status: a followed redirect
    carries the request's headers, the key among them, to wherever it points."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ARG002
        return None


_OPENER = urllib.request.build_opener(_NoRedirect)


def read(repo_root: Path, env: Mapping) -> dict:
    """This Cursor run's reading from one surface, never the two added: the cloud usage API's
    when `KEY_ENV` and `AGENT_ENV` are both set, and the CLI's store is then not opened; else
    the CLI's, with no request made and the reason naming the variable or variables unset."""
    key = (env.get(KEY_ENV) or "").strip()
    agent = (env.get(AGENT_ENV) or "").strip()
    missing = [name for name, value in ((KEY_ENV, key), (AGENT_ENV, agent)) if not value]
    if not missing:
        base = (env.get(API_ENV) or "").strip() or API_BASE
        return read_cloud(key, agent, base)
    got = read_cli(repo_root, env)
    if got.get("tokens") is not None:
        return got
    unset = (f"{' and '.join(missing)} {'is' if len(missing) == 1 else 'are'} not set, so the "
             f"Cursor cloud usage API is not called")
    return {**got, "reason": f"{unset}, and {got['reason']}"}


def cli_chats(repo_root: Path, env: Mapping) -> Path:
    """The directory the Cursor CLI keeps the workspace `repo_root`'s chats in."""
    config = env.get(CONFIG_ENV) or ""
    if not config.strip():
        xdg = env.get(XDG_ENV) or ""
        home = env.get("HOME") or str(Path.home())
        config = os.path.join(xdg, "cursor") if xdg.strip() else os.path.join(home, ".cursor")
    workspace = os.path.abspath(os.fspath(repo_root))
    name = hashlib.md5(workspace.encode(), usedforsecurity=False).hexdigest()
    return Path(config) / "chats" / name


def read_cli(repo_root: Path, env: Mapping) -> dict:
    """The Cursor CLI's reading for the workspace `repo_root`: tokens None, since its chat store
    records no usage, unless the hook ledger `LEDGER_REL` is there, which is then the reading
    (`read_ledger`). The reason names the store, or says none is there, or that a `store.db`
    holds other tables than the pinned build's, and is then not read as keeping no usage."""
    ledger = ledger_path(repo_root)
    if ledger.is_file():
        return read_ledger(ledger)
    chats = cli_chats(repo_root, env)

    def none(why: str) -> dict:
        return {"tokens": None, "reason": f"{why}, so this run's tokens cannot be read"}
    try:
        found = sorted(d for d in chats.iterdir()
                       if (d / "store.db").is_file() or (d / "meta.json").is_file())
    except FileNotFoundError:
        found = []
    except OSError as exc:
        return none(f"the Cursor CLI chat store {chats} could not be listed "
                    f"({type(exc).__name__})")
    if not found:
        return none(f"no Cursor CLI chat store sits at {chats}")
    for db in (d / "store.db" for d in found):
        if db.is_file() and _tables(db) != set(STORE_TABLES):
            return none(f"the Cursor CLI chat store {db} does not hold exactly the tables "
                        f"{' and '.join(STORE_TABLES)}, the shape this reader was pinned "
                        f"against, so whether it records usage is not known")
    return none(f"the Cursor CLI kept no usage record: its chat store for this workspace, "
                f"{chats}, holds {len(found)} chat{'' if len(found) == 1 else 's'} and records "
                f"no tokens spent, and the usage a print run reports on its stdout is not read")


def ledger_path(repo_root: Path) -> Path:
    """Where the hook appends the workspace `repo_root`'s ledger, and this reader reads it."""
    return Path(repo_root) / LEDGER_REL


def read_ledger(ledger: Path) -> dict:
    """The reading the hook ledger `ledger` holds: every line's counts summed, or tokens None
    with the reason when no line can be read. A line that is not a JSON object whose
    `LEDGER_FIELDS` are each a count is skipped and counted as `skipped`; the figure is then a
    lower bound, and the basis says so. The payload's `input_tokens` holds the response's cache
    reads and writes, so its uncached input is `input_tokens` less both, never below zero, as
    the CLI's own print-mode usage line forms it. The payload does not split a cache write by
    duration, so each is booked at five minutes, as an unsplit Claude write is, and priced from
    `run_state.TOKEN_WEIGHTS` as the figure is formed."""
    from . import run_state  # noqa: PLC0415 - lazy: run_state loads this reader

    sums = dict.fromkeys(LEDGER_FIELDS, 0)
    read = skipped = uncached = 0
    try:
        with ledger.open("rb") as fh:
            for raw in fh:
                if not raw.strip():
                    continue
                try:
                    row = json.loads(raw)
                except ValueError:
                    row = None
                if not (isinstance(row, dict) and all(_count(row.get(f)) for f in LEDGER_FIELDS)):
                    skipped += 1
                    continue
                read += 1
                for f in LEDGER_FIELDS:
                    sums[f] += row[f]
                uncached += max(row["input_tokens"] - row["cache_read_tokens"]
                                - row["cache_write_tokens"], 0)
    except OSError as exc:
        return {"tokens": None, "reason": f"the Cursor CLI hook ledger {ledger} could not be "
                                          f"read ({type(exc).__name__}), so this run's tokens "
                                          f"cannot be read"}
    lines = f"{skipped} malformed line{'' if skipped == 1 else 's'} skipped"
    if not read:
        return {"tokens": None, "reason": f"the Cursor CLI hook ledger {ledger} holds no line "
                                          f"that can be read ({lines}), so this run's tokens "
                                          f"cannot be read"}
    comps = {"input": uncached, "output": sums["output_tokens"],
             "cache_write_5m": sums["cache_write_tokens"], "cache_write_1h": 0,
             "cache_read": sums["cache_read_tokens"]}
    basis = (f"the Cursor CLI {HOOK_EVENT} hook ledger {ledger}, {read} "
             f"response{'' if read == 1 else 's'} summed: input is each response's input_tokens "
             f"less its cache reads and writes, never below zero; tokens is input + output + "
             f"cache write, cache reads apart, and the priced figure weighs every component, "
             f"each cache write at the five-minute weight since the payload does not split it")
    if skipped:
        basis += f"; {lines}, so it is a LOWER BOUND on what the run cost"
    return {"tokens": comps["input"] + comps["output"] + comps["cache_write_5m"],
            CACHE_READ: comps["cache_read"], "components": comps,
            "priced": run_state.price(comps), "responses": read, "skipped": skipped,
            "source": f"the Cursor CLI hook ledger {ledger}", "basis": basis,
            "includes_subagents": False}


def _tables(db: Path) -> set[str] | None:
    """The table names in the SQLite store `db`, WAL included, or None when it cannot be read
    as SQLite. The CLI opens its store in WAL mode before creating its tables, so a chat not yet
    checkpointed holds them in its `-wal` alone, which an immutable open ignores; that store is
    read from a copy, and `db`, its `-wal` and its `-shm` are never written."""
    wal = db.with_name(db.name + "-wal")
    try:
        if not (wal.is_file() and wal.stat().st_size):
            return _schema(f"{db.absolute().as_uri()}?mode=ro&immutable=1")
        with tempfile.TemporaryDirectory(prefix="sdlc-cursor-") as tmp:
            copy = Path(tmp).absolute() / db.name
            shutil.copyfile(db, copy)
            shutil.copyfile(wal, copy.with_name(wal.name))
            return _schema(f"{copy.as_uri()}?mode=ro")
    except (sqlite3.Error, OSError):
        return None


def _schema(uri: str) -> set[str]:
    """The table names of the SQLite database at `uri`."""
    con = sqlite3.connect(uri, uri=True)
    try:
        return {row[0] for row in con.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'")}
    finally:
        con.close()


def read_cloud(key: str, agent: str, base: str = API_BASE) -> dict:
    """Agent `agent`'s reading from the usage API at `base`, or tokens None with the reason. A
    URL neither https nor http on a loopback address is refused before any request is made."""
    url = f"{base.rstrip('/')}/v1/agents/{urllib.parse.quote(agent, safe='')}/usage"
    if not _private(url):
        return {"tokens": None, "reason": (
            f"the Cursor cloud usage API, for agent {agent}: {API_ENV} is neither an https URL "
            f"nor an http one on a loopback address, so no request is made")}
    got = _get(url, key)
    if isinstance(got, str):
        return {"tokens": None, "reason": f"the Cursor cloud usage API, for agent {agent}: {got}"}
    return _reading(got, agent)


def _private(url: str) -> bool:
    """Whether `url` may carry the key: its scheme is https, or it is http and its host is a
    loopback IP address. A host name, `localhost` among them, is refused rather than resolved,
    since what a name resolves to is not this check's to know, and so is a URL `urlsplit`
    cannot parse."""
    try:
        parts = urllib.parse.urlsplit(url)
        host = parts.hostname
    except ValueError:
        return False
    if parts.scheme == "https":
        return True
    if parts.scheme != "http" or not host:
        return False
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def _get(url: str, key: str) -> bytes | str:
    """The answer's body, or the reason there is none, built from the HTTP status or the
    exception's type alone: a message, a body or a header may echo the key."""
    req = urllib.request.Request(url, headers={"Accept": "application/json",
                                               "Authorization": f"Bearer {key}"})
    box: dict = {}

    def call() -> None:
        try:
            with _OPENER.open(req, timeout=TIMEOUT_SECONDS) as resp:
                box["body"] = resp.read(MAX_BYTES + 1)
        except urllib.error.HTTPError as exc:
            exc.close()
            box["error"] = exc
        except Exception as exc:  # noqa: BLE001 - every failure is a reason, never a raise
            box["error"] = exc

    worker = threading.Thread(target=call, name="cursor-usage", daemon=True)
    worker.start()
    worker.join(TIMEOUT_SECONDS)
    if worker.is_alive():
        return f"it did not answer within {TIMEOUT_SECONDS:g} seconds"
    exc = box.get("error")
    if exc is None:
        body = box["body"]
        return body if len(body) <= MAX_BYTES else f"its answer exceeds {MAX_BYTES} bytes"
    if isinstance(exc, urllib.error.HTTPError):
        return f"it answered HTTP {exc.code}"
    cause = exc.reason if isinstance(exc, urllib.error.URLError) else exc
    if isinstance(cause, TimeoutError):
        return f"it did not answer within {TIMEOUT_SECONDS:g} seconds"
    if isinstance(exc, urllib.error.URLError):
        named = type(cause).__name__ if isinstance(cause, BaseException) else "URLError"
        return f"it could not be reached ({named})"
    return f"the call failed ({type(exc).__name__})"


def _count(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _reading(body: bytes, agent: str) -> dict:
    """The reading in the usage API's answer `body`, or tokens None with the reason."""
    def none(why: str) -> dict:
        return {"tokens": None, "reason": f"the Cursor cloud usage API, for agent {agent}: {why}"}
    try:
        doc = json.loads(body)
    except ValueError:
        return none("its answer is not JSON")
    usage = doc.get("totalUsage") if isinstance(doc, dict) else None
    if usage is None:
        return none("it records no usage for this agent yet")
    if not isinstance(usage, dict):
        return none("its totalUsage is not an object")
    for field in (*COUNTED, CACHE_READS):
        if not _count(usage.get(field)):
            return none(f"its totalUsage {field} is {usage.get(field)!r}, not a count")
    tokens = sum(usage[f] for f in COUNTED)
    total = usage.get(TOTAL)
    if total is not None and total != tokens + usage[CACHE_READS]:
        return none(f"its totalTokens {total!r} is not the sum of the four counts, so they "
                    f"overlap and no figure is formed")
    if tokens == 0:
        return none("it records no usage for this agent yet")
    return {"tokens": tokens, CACHE_READ: usage[CACHE_READS], "agent_id": agent,
            "source": f"the Cursor cloud usage API, agent {agent}",
            "basis": ("Cursor cloud usage API totalUsage for the agent, every run of it: input "
                      "+ output + cache write, cache reads apart; totalTokens, which holds "
                      "them, is not used"),
            "includes_subagents": True}

