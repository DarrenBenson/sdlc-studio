#!/usr/bin/env python3
"""OpenCode's token reader, the module `token_meters` loads for the OpenCode harness.

OpenCode keeps every session and message in one SQLite database, `opencode.db` in its data
directory: `DB_ENV` when set (an absolute path, or one relative to the data directory, as
OpenCode resolves it), else `$XDG_DATA_HOME/opencode/opencode.db` when `XDG_ENV` is not blank,
else `~/.local/share/opencode/opencode.db`. Its `session` table carries each session's
`directory` and `parent_id`, and each assistant message's `data` is JSON whose `tokens` holds
`input`, `output`, `reasoning`, `cache.read` and `cache.write`. Builds before the database kept
the same messages as a JSON tree under the data directory's `storage/`:
`session/<project>/<id>.json` with the session's `directory` and `parentID`, and
`message/<session>/<id>.json`. With no database file, that tree is read on the same basis.

The figure is folded from the messages, never from the session's own `tokens_*` columns, which
rows migrated from the JSON tree carry as zero. The sessions read are those whose directory is
this repo and every session descending from one through its parent, which is where OpenCode
records a subagent's spend, so the reading includes it. OpenCode's `input` excludes the cache,
and it reports reasoning beside output, not inside it: a message's `total` is input + output +
reasoning + cache read + cache write. So `tokens` is input + output + reasoning + cache write,
reasoning added once; a message whose `total` is input + output + the cache, reasoning inside
output, adds it no second time, and one whose `total` fits neither is refused, since its counts
would then overlap. Cache reads are `cache_read`, apart. OpenCode does not split a cache write
by duration, so each is booked at five minutes, and reasoning is priced as output.

The database is opened with a `mode=ro` URI and `PRAGMA query_only` (`connect`), so a read
never writes the database's own bytes. As for any reader of a WAL database, the read-only open
may create the write-ahead log (`-wal`) and shared-memory index (`-shm`) files beside it. No
`opencode` process is started: `opencode stats` is never run. No store, a store holding no
session for this repo or no count above zero, a store that cannot be read, or a message whose
`tokens` is malformed gives tokens None with the reason, never zero and never a figure with that
message left out. The store probe, `store`, raises on a database present that SQLite cannot
read, so `token_meters` reports OpenCode as a candidate rather than leaving it out.
"""
from __future__ import annotations

import json
import sqlite3
from collections.abc import Mapping
from pathlib import Path

from .token_meters import CACHE_READ

#: OpenCode's own variable naming its database; it also signals OpenCode to `token_meters`.
DB_ENV = "OPENCODE_DB"
XDG_ENV = "XDG_DATA_HOME"
DB_NAME = "opencode.db"
#: The legacy JSON tree, under the data directory.
STORAGE = "storage"
#: The `tokens` counts every message must carry, and the two under `cache`.
COUNTS = ("input", "output", "reasoning")
CACHE = ("read", "write")

#: Every session in this repo's directory and every one descending from those, each once (a
#: recursive UNION keeps distinct rows), whether it is a child, and its messages.
SQL = """WITH RECURSIVE ours(id) AS (
  SELECT id FROM session WHERE directory IN ({dirs})
  UNION SELECT s.id FROM session s JOIN ours o ON s.parent_id = o.id)
SELECT s.id, s.parent_id IS NOT NULL, m.id, m.data FROM session s
  JOIN ours o ON o.id = s.id LEFT JOIN message m ON m.session_id = s.id"""


class Malformed(ValueError):
    """A message whose `tokens` cannot be counted."""


def data_dir(env: Mapping) -> Path:
    """OpenCode's data directory: `$XDG_DATA_HOME/opencode`, else `~/.local/share/opencode`."""
    xdg = (env.get(XDG_ENV) or "").strip()
    if xdg:
        return Path(xdg) / "opencode"
    home = env.get("HOME") or str(Path.home())
    return Path(home) / ".local" / "share" / "opencode"


def db_path(env: Mapping) -> Path | None:
    """The database OpenCode reads, as it resolves it, or None for an in-memory one."""
    named = env.get(DB_ENV) or ""
    if named == ":memory:":
        return None
    if named:
        return Path(named) if Path(named).is_absolute() else data_dir(env) / named
    return data_dir(env) / DB_NAME


def connect(db: Path) -> sqlite3.Connection:
    """`db` opened read-only: a `mode=ro` URI, then `PRAGMA query_only`."""
    con = sqlite3.connect(f"{db.absolute().as_uri()}?mode=ro", uri=True)
    con.execute("PRAGMA query_only = ON")
    return con


def _dirs(repo_root: Path) -> list[str]:
    """The spellings of this repo's directory a session can carry, resolved and as given."""
    return list(dict.fromkeys([str(Path(repo_root).resolve()), str(Path(repo_root).absolute())]))


def _count(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool) and v >= 0


def _fold(toks) -> dict:
    """One message's components. RAISES Malformed naming what is wrong."""
    if not isinstance(toks, dict):
        raise Malformed(f"tokens is {type(toks).__name__}, not an object")
    cache = toks.get("cache")
    if not isinstance(cache, dict):
        raise Malformed("tokens.cache is missing or not an object")
    got = {k: toks.get(k) for k in COUNTS} | {f"cache.{k}": cache.get(k) for k in CACHE}
    bad = [f"{k} {v!r}" for k, v in got.items() if not _count(v)]
    if bad:
        raise Malformed(f"tokens.{', tokens.'.join(bad)} is not a count")
    inp, out, why = got["input"], got["output"], got["reasoning"]
    cached = got["cache.read"] + got["cache.write"]
    total = toks.get("total")
    if total is None or total == inp + out + why + cached:
        out += why
    elif total != inp + out + cached:
        raise Malformed(f"tokens.total {total!r} is neither input + output + reasoning + cache "
                        f"nor input + output + cache, so its counts overlap")
    return {"input": inp, "output": out, "cache_write_5m": got["cache.write"],
            "cache_write_1h": 0, "cache_read": got["cache.read"]}


def _reading(messages, ours: dict[str, bool], where: str, repo: str) -> dict:
    """The reading folded from `messages`, `(message id, data text)` pairs of the sessions in
    `ours` (id to whether it is a child), or tokens None naming why."""
    from . import run_state  # noqa: PLC0415 - lazy: run_state loads this reader

    def none(why: str) -> dict:
        return {"tokens": None, "reason": f"{where} {why}, so this run's tokens cannot be read"}
    if not ours:
        return none(f"holds no session in {repo}")
    comps = dict.fromkeys(("input", "output", "cache_write_5m", "cache_write_1h", "cache_read"), 0)
    counted = 0
    for mid, text in messages:
        try:
            data = json.loads(text)
        except (TypeError, ValueError):
            return none(f"holds message {mid}, whose data is not JSON")
        if not isinstance(data, dict):
            return none(f"holds message {mid}, whose data is not an object")
        if "tokens" not in data:
            continue
        try:
            one = _fold(data["tokens"])
        except Malformed as exc:
            return none(f"holds message {mid}, whose {exc}")
        counted += 1
        for k, v in one.items():
            comps[k] += v
    tokens = comps["input"] + comps["output"] + comps["cache_write_5m"]
    if not tokens:
        return none(f"holds {len(ours)} session(s) in {repo} but no token count above zero yet")
    children = sum(ours.values())
    basis = (f"{where}, {counted} assistant message(s) across {len(ours)} session(s) in {repo}, "
             f"{children} of them child session(s), so subagent spend is included: tokens is "
             f"input + output + reasoning + cache write, reasoning added once since OpenCode "
             f"reports it beside output, cache reads apart; each message's own counts are "
             f"folded, never the session totals, and each cache write is priced at five minutes")
    return {"tokens": tokens, CACHE_READ: comps["cache_read"], "components": comps,
            "priced": run_state.price(comps), "sessions": len(ours), "child_sessions": children,
            "messages": counted, "source": f"{where}, sessions in {repo}", "basis": basis,
            "includes_subagents": True}


def read_db(db: Path, repo_root: Path) -> dict:
    """The reading the database `db` holds for `repo_root`'s sessions."""
    dirs = _dirs(repo_root)
    where = f"the OpenCode database {db}"
    try:
        con = connect(db)
        try:
            got = con.execute(SQL.format(dirs=", ".join("?" * len(dirs))), dirs).fetchall()
        finally:
            con.close()
    except sqlite3.Error as exc:
        return {"tokens": None, "reason": f"{where} could not be read ({type(exc).__name__}), "
                                          f"so this run's tokens cannot be read"}
    ours = {sid: bool(child) for sid, child, _mid, _data in got}
    return _reading([(m, d) for _s, _c, m, d in got if m is not None], ours, where, dirs[0])


def _legacy_sessions(storage: Path) -> list[dict]:
    """Every session record in the legacy tree. RAISES Malformed on one that is not JSON."""
    found = []
    for f in sorted((storage / "session").glob("*/*.json")):
        try:
            info = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise Malformed(f"holds session record {f}, which could not be read "
                            f"({type(exc).__name__})") from None
        if isinstance(info, dict):
            found.append({"id": info.get("id") or f.stem, "directory": info.get("directory"),
                          "parent": info.get("parentID")})
    return found


def read_legacy(storage: Path, repo_root: Path) -> dict:
    """The reading the legacy JSON tree `storage` holds for `repo_root`'s sessions."""
    dirs = _dirs(repo_root)
    where = f"the OpenCode legacy JSON store {storage}"
    try:
        records = _legacy_sessions(storage)
    except Malformed as exc:
        return {"tokens": None, "reason": f"{where} {exc}, so this run's tokens cannot be read"}
    child = {r["id"]: bool(r["parent"]) for r in records}
    ours = {r["id"]: child[r["id"]] for r in records if r["directory"] in dirs}
    grew = True
    while grew:
        grew = False
        for r in records:
            if r["id"] not in ours and r["parent"] in ours:
                ours[r["id"]], grew = child[r["id"]], True

    def messages():
        for sid in ours:
            for f in sorted((storage / "message" / sid).glob("*.json")):
                try:
                    yield f.stem, f.read_text(encoding="utf-8")
                except OSError:
                    yield f.stem, None
    return _reading(messages(), ours, where, dirs[0])


def store(repo_root: Path, env: Mapping) -> str | None:
    """This repo's OpenCode store, or None: the database, else the legacy tree, when it holds a
    session in this repo's directory. A store of other directories' sessions is not this
    repo's, so it does not make OpenCode a candidate. RAISES the `sqlite3.Error` that opening
    or querying a database file present raises: a store present but unreadable may be this
    run's, so `token_meters` reports it as a candidate."""
    db = db_path(env)
    if db is not None and db.is_file():
        dirs = _dirs(repo_root)
        con = connect(db)
        try:
            # Only `?` placeholders are interpolated; every directory is a bound parameter.
            hit = con.execute(f"SELECT 1 FROM session WHERE directory IN "  # nosec B608
                              f"({', '.join('?' * len(dirs))}) LIMIT 1", dirs).fetchone()
        finally:
            con.close()
        return str(db) if hit else None
    storage = data_dir(env) / STORAGE
    if not (storage / "message").is_dir():
        return None
    try:
        records = _legacy_sessions(storage)
    except Malformed:
        return None
    dirs = _dirs(repo_root)
    return str(storage) if any(r["directory"] in dirs for r in records) else None


def read(repo_root: Path, env: Mapping) -> dict:
    """One reading of OpenCode's store for `repo_root`: the database when its file is present,
    else the legacy JSON tree, else tokens None naming both."""
    db = db_path(env)
    if db is None:
        return {"tokens": None, "reason": f"{DB_ENV} names an in-memory database, which no "
                                          f"other process can read, so this run's tokens "
                                          f"cannot be read"}
    if db.is_file():
        return read_db(db, Path(repo_root))
    storage = data_dir(env) / STORAGE
    if (storage / "message").is_dir():
        return read_legacy(storage, Path(repo_root))
    return {"tokens": None, "reason": f"there is no OpenCode database at {db} and no legacy "
                                      f"JSON store at {storage / 'message'}, so this run's "
                                      f"tokens cannot be read"}
