"""US0988 (CR0611): an OpenCode run records its token actual from the read-only OpenCode
database, child sessions included.

`lib/meter_opencode.py` folds each assistant message's `tokens` from OpenCode's store, reached
here through the shipped selector, `run_state.session_tokens`, and `sprint.py plan --write`.

The fixture is derived from the development machine's OpenCode 1.18.34 database
(`~/.local/share/opencode/opencode.db`, read with a `mode=ro` URI on 2026-11-06): the `session`
and `message` DDL is that build's, and the token values are those of two free-model sessions it
recorded, a parent that delegated through the task tool and the child session it created, which
carries `parent_id` and the parent's directory. Two changes are synthetic: one message's cache
write is 2,048 (every real one was 0), so that the write is seen to count, and every session's
aggregate `tokens_*` columns are 0, as rows migrated from the legacy JSON store are left, so a
reader of those columns reads nothing. Paths are this test's temporary directories.

Pinned here:

* `tokens` is input + output + reasoning + cache write folded from each message's JSON, cache
  reads apart, a child session included, the basis saying so (AC1);
* the database is opened with a `mode=ro` URI and `PRAGMA query_only`, a session in another
  directory is excluded, and no `opencode` process is started (AC2);
* with no database, the legacy JSON tree under `storage/` reads the same basis (AC3);
* no store, an empty store or a malformed token value is tokens None with a reason (AC4);
* `sprint.py plan --write` stamps a baseline naming opencode and the database (AC5).

BG1240 adds:

* a database present at the default path that SQLite cannot read (not a database, or mode 000)
  is a candidate at the store step, never left out so Claude is chosen by default (AC1);
* a readable database holding only other directories' sessions is still not a candidate (AC2);
* `read_db` on a cleanly closed WAL database leaves its bytes unchanged, through a read-only
  open, and the module docstring says so without claiming the write-ahead log is untouched (AC3).

Run from the repo root:
    python3 -m pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_opencode.py
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/meter_opencode.py
from __future__ import annotations

import contextlib
import json
import os
import sqlite3
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib import meter_opencode, run_state, token_meters  # noqa: E402

SPRINT = Path(__file__).resolve().parents[1] / "sprint.py"

#: OpenCode 1.18.34's own DDL for the two tables the reader reads, as its database holds it.
DDL = """CREATE TABLE `session` (
  `id` text PRIMARY KEY, `project_id` text NOT NULL, `workspace_id` text, `parent_id` text,
  `slug` text NOT NULL, `directory` text NOT NULL, `path` text, `title` text NOT NULL,
  `version` text NOT NULL, `share_url` text, `summary_additions` integer,
  `summary_deletions` integer, `summary_files` integer, `summary_diffs` text, `metadata` text,
  `cost` real DEFAULT 0 NOT NULL, `tokens_input` integer DEFAULT 0 NOT NULL,
  `tokens_output` integer DEFAULT 0 NOT NULL, `tokens_reasoning` integer DEFAULT 0 NOT NULL,
  `tokens_cache_read` integer DEFAULT 0 NOT NULL, `tokens_cache_write` integer DEFAULT 0 NOT NULL,
  `revert` text, `permission` text, `agent` text, `model` text,
  `time_created` integer NOT NULL, `time_updated` integer NOT NULL, `time_compacting` integer,
  `time_archived` integer);
CREATE TABLE `message` (
  `id` text PRIMARY KEY, `session_id` text NOT NULL, `time_created` integer NOT NULL,
  `time_updated` integer NOT NULL, `data` text NOT NULL,
  CONSTRAINT `fk_message_session_id_session_id_fk` FOREIGN KEY (`session_id`)
  REFERENCES `session`(`id`) ON DELETE CASCADE);"""

PARENT, CHILD, OTHER = ("ses_e4f427a52ffeRgqnlfA1bDfBf1", "ses_e4f42432effeDn1OzeOQrfZci1",
                        "ses_e4f70696affemjSa99Fu7ITrM9")


def tokens(inp: int, out: int, reasoning: int, write: int, read: int, total=True) -> dict:
    """A message's `tokens`, its `total` as OpenCode forms it: every count, reasoning beside
    output. `total` False leaves it out; an int gives that total."""
    got = {"input": inp, "output": out, "reasoning": reasoning,
           "cache": {"write": write, "read": read}}
    if total is True:
        got["total"] = inp + out + reasoning + write + read
    elif total is not False:
        got["total"] = total
    return got


def assistant(cwd: str, toks: dict) -> dict:
    """An assistant message's `data`, in the shape 1.18.34 wrote it, trimmed."""
    return {"parentID": "msg_user", "role": "assistant", "mode": "build", "agent": "build",
            "path": {"cwd": cwd, "root": cwd}, "cost": 0, "tokens": toks,
            "modelID": "deepseek-v4.1-flash-free", "providerID": "opencode",
            "time": {"created": 1793963564074, "completed": 1793963567382}, "finish": "stop"}


USER = {"role": "user", "time": {"created": 1793963562903}, "agent": "build",
        "model": {"providerID": "opencode", "modelID": "deepseek-v4.1-flash-free"},
        "summary": {"diffs": []}}

#: input 13,950 + 410 + 12,409 = 26,769; output 78 + 3 + 3 = 84; reasoning 28 (beside output);
#: cache write 2,048; so tokens 28,929; cache reads 1,792 + 15,488 + 1,792 = 19,072.
TOKENS, CACHE_READS = 28_929, 19_072
COMPONENTS = {"input": 26_769, "output": 112, "cache_write_5m": 2_048, "cache_write_1h": 0,
              "cache_read": 19_072}


def rows(repo: str, other: str) -> list[tuple[str, str, dict]]:
    """`(session, message id, data)` for every message the fixture holds."""
    return [
        (PARENT, "msg_1b08fb0YhgIKw6", USER),
        (PARENT, "msg_1b08fbxciNwHmz", assistant(repo, tokens(13_950, 78, 28, 0, 1_792))),
        (PARENT, "msg_1b08fbZRVdp7pK", assistant(repo, tokens(410, 3, 0, 2_048, 15_488))),
        (CHILD, "msg_1b08fcGOUu6Hl8", USER),
        (CHILD, "msg_1b08fcqWPMw7Ik", assistant(repo, tokens(12_409, 3, 0, 0, 1_792))),
        (OTHER, "msg_1b08f9yaoxIo2Q", assistant(other, tokens(9_896, 3, 0, 0, 1_792))),
    ]


def sessions(repo: str, other: str) -> list[tuple[str, str | None, str]]:
    return [(PARENT, None, repo), (CHILD, PARENT, repo), (OTHER, None, other)]


def make_db(path: Path, repo: str, other: str, extra=()) -> Path:
    """The fixture database at `path`, in WAL mode as OpenCode opens it, closed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    try:
        con.execute("PRAGMA journal_mode = WAL")
        con.executescript(DDL)
        with con:
            for sid, parent, directory in sessions(repo, other):
                con.execute("INSERT INTO session (id, project_id, parent_id, slug, directory, "
                            "title, version, time_created, time_updated) "
                            "VALUES (?, 'global', ?, 's', ?, 't', '1.18.34', 1, 2)",
                            (sid, parent, directory))
            for n, (sid, mid, data) in enumerate([*rows(repo, other), *extra]):
                con.execute("INSERT INTO message VALUES (?, ?, ?, ?, ?)",
                            (mid, sid, n, n, data if isinstance(data, str) else json.dumps(data)))
    finally:
        con.close()
    return path


def make_legacy(storage: Path, repo: str, other: str) -> Path:
    """The same sessions and messages as the legacy JSON tree: `session/<project>/<id>.json`
    holding `id`, `directory` and `parentID`, and `message/<session>/<id>.json` the message with
    its `id` and `sessionID`, the layout OpenCode's own storage migrations read."""
    for sid, parent, directory in sessions(repo, other):
        info = {"id": sid, "projectID": "global", "directory": directory, "title": "t",
                "version": "1.18.34", "time": {"created": 1, "updated": 2}}
        if parent:
            info["parentID"] = parent
        f = storage / "session" / "global" / f"{sid}.json"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps(info), encoding="utf-8")
    for sid, mid, data in rows(repo, other):
        f = storage / "message" / sid / f"{mid}.json"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps({"id": mid, "sessionID": sid, **data}), encoding="utf-8")
    return storage


class _Fixture(unittest.TestCase):

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        base = Path(tmp.name).resolve()
        self.root, self.home, self.other = base / "repo", base / "home", base / "elsewhere"
        for d in (self.root, self.home, self.other):
            d.mkdir()
        self.data = self.home / ".local" / "share" / "opencode"
        self.db = self.data / "opencode.db"
        # A stand-in `opencode` on PATH that leaves a mark when anything runs it.
        self.bin, self.mark = base / "bin", base / "opencode-ran"
        self.bin.mkdir()
        fake = self.bin / "opencode"
        fake.write_text(f"#!/bin/sh\necho \"$@\" > '{self.mark}'\necho '{{}}'\n", "utf-8")
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)

    def environment(self, **values) -> dict:
        scrub = {*token_meters.selection_variables(), run_state.TRANSCRIPTS_ENV,
                 meter_opencode.DB_ENV, meter_opencode.XDG_ENV}
        env = {k: v for k, v in os.environ.items() if k not in scrub}
        env.update({"HOME": str(self.home), token_meters.HARNESS_ENV: "opencode",
                    run_state.TRANSCRIPTS_ENV: str(self.home / "none"),
                    "PATH": f"{self.bin}{os.pathsep}{os.environ.get('PATH', '')}"})
        env.update(values)
        return {k: v for k, v in env.items() if v is not None}

    @contextlib.contextmanager
    def env(self, **values):
        with mock.patch.dict(os.environ, clear=True):
            os.environ.update(self.environment(**values))
            yield

    def reading(self, **values) -> dict:
        with self.env(**values):
            return run_state.session_tokens(self.root)

    def assert_folded(self, got: dict, source: str) -> None:
        self.assertEqual(got[token_meters.HARNESS], "opencode", got.get("reason"))
        self.assertEqual((got["tokens"], got[token_meters.CACHE_READ]), (TOKENS, CACHE_READS),
                         got.get("reason"))
        self.assertEqual(got["components"], COMPONENTS)
        self.assertEqual(got["priced"], run_state.price(COMPONENTS))
        self.assertIs(got["includes_subagents"], True)
        self.assertEqual((got["sessions"], got["child_sessions"]), (2, 1))
        self.assertIn(source, got["source"])
        self.assertIn("child session", got["basis"])
        self.assertIn("subagent", got["basis"])


class OpenCodeReaderTests(_Fixture):

    def test_messages_fold_one_basis_with_child_sessions(self) -> None:
        """AC1. Mutants: reading the session aggregate columns (0 here, as migrated rows leave
        them), dropping the child session (by `parent_id IS NULL`, or by matching the directory
        alone once the child's differs), leaving reasoning out, adding it twice where the total
        shows it inside output, or counting cache reads into `tokens`."""
        make_db(self.db, str(self.root), str(self.other))
        self.assert_folded(self.reading(), str(self.db))
        # The child is the parent's by `parent_id`, wherever it ran.
        con = sqlite3.connect(self.db)
        with con:
            con.execute("UPDATE session SET directory = ? WHERE id = ?", (str(self.other), CHILD))
        con.close()
        self.assert_folded(self.reading(), str(self.db))
        # A total showing reasoning inside output adds it no second time.
        inside = assistant(str(self.root), tokens(100, 50, 20, 0, 0, total=150))
        make_db(self.data / "inside.db", str(self.root), str(self.other),
                extra=[(PARENT, "msg_inside", inside)])
        got = self.reading(OPENCODE_DB=str(self.data / "inside.db"))
        self.assertEqual(got["tokens"], TOKENS + 150, got.get("reason"))
        self.assertEqual(got["components"]["output"], COMPONENTS["output"] + 50)

    @contextlib.contextmanager
    def opens(self):
        """Every database opened while the block runs, seen at `sqlite3.connect` itself, so an
        open that bypasses the module's read-only helper is seen too. Each is (database, the
        `uri` flag, whether a write on the bare open was refused, `PRAGMA query_only` at each
        statement other than a PRAGMA run on it)."""
        real, opens = sqlite3.connect, []

        class Probe(sqlite3.Connection):
            def execute(self, sql, *args):
                if not sql.lstrip().upper().startswith("PRAGMA"):
                    self.ran.append(super().execute("PRAGMA query_only").fetchone()[0])
                return super().execute(sql, *args)

        def spy(database, *args, **kwargs):
            con = real(database, *args, factory=Probe, **kwargs)
            con.ran = []
            try:
                sqlite3.Connection.execute(con, "CREATE TABLE written_by_the_reader (x)")
                refused = False
            except sqlite3.OperationalError:
                refused = True
            opens.append((str(database), kwargs.get("uri", False), refused, con.ran))
            return con
        with mock.patch.object(sqlite3, "connect", spy):
            yield opens

    def assert_read_only(self, opens: list, what: str) -> None:
        self.assertTrue(opens, f"{what} answered without opening the database")
        for database, uri, refused, ran in opens:
            self.assertIn("mode=ro", database, f"{what} opened {database} without mode=ro")
            self.assertTrue(uri, f"{what} opened {database} without uri=True")
            self.assertTrue(refused, f"{what} opened {database} for writing")
            self.assertTrue(ran, f"{what} ran no statement on {database}")
            self.assertEqual(set(ran), {1}, f"{what} queried {database} without query_only")

    def test_read_only_this_repo_and_no_binary(self) -> None:
        """AC2. Mutants: a plain read-write open in `read_db` or in the `store()` probe, the
        `mode=ro` URI or `PRAGMA query_only` dropped, the other directory's session counted, or
        `opencode stats` run."""
        make_db(self.db, str(self.root), str(self.other))
        before = self.db.read_bytes()
        with self.opens() as opened:
            got = self.reading()
        self.assert_read_only(opened, "the reading")
        self.assertEqual(got["tokens"], TOKENS, "the other directory's 11,691 is left out")
        self.assertEqual(self.db.read_bytes(), before)
        self.assertFalse(self.mark.exists(), "no opencode process is started")
        with self.env(), self.opens() as opened:
            self.assertIn(str(self.db), meter_opencode.store(self.root, os.environ))
            self.assertIsNone(meter_opencode.store(self.home, os.environ),
                              "a store holding no session for that directory is not its store")
        self.assert_read_only(opened, "the store() probe")
        self.assertEqual(len(opened), 2, "each store() call opens the database once")
        self.assertEqual(self.db.read_bytes(), before)
        self.assertFalse(self.mark.exists())

    def test_the_store_probe_binds_its_directories(self) -> None:
        """BG1259 AC2. Mutant: the `store()` probe writing each directory into its SQL as a
        quoted literal instead of binding it as a parameter, which its `# nosec B608` keeps
        bandit from refusing. Every statement is seen at the connection's `execute`, as `opens`
        sees each open at `sqlite3.connect`; the repo is reached through a symlink, so both of
        its spellings are probed."""
        make_db(self.db, str(self.root), str(self.other))
        link = self.home / "repo-link"
        link.symlink_to(self.root, target_is_directory=True)
        dirs = [str(self.root), str(link)]
        real, ran = sqlite3.connect, []

        class Recorder(sqlite3.Connection):
            def execute(self, sql, *args):
                ran.append((sql, tuple(args[0]) if args else ()))
                return super().execute(sql, *args)

        def spy(database, *args, **kwargs):
            return real(database, *args, factory=Recorder, **kwargs)
        faked = {meter_opencode.XDG_ENV: str(self.home / ".local" / "share"),
                 meter_opencode.DB_ENV: str(self.db)}
        with self.env(**faked), mock.patch.object(sqlite3, "connect", spy):
            found = meter_opencode.store(link, os.environ)
        self.assertEqual(found, str(self.db), "the workspace directory's session is found")
        probes = [(sql, params) for sql, params in ran if "FROM session" in sql]
        self.assertEqual(len(probes), 1, ran)
        sql, params = probes[0]
        for d in dirs:
            self.assertNotIn(d, sql, "a directory is written into the probe's SQL")
        self.assertNotIn("'", sql, "the probe's SQL carries a quoted literal")
        listed = sql.partition(" IN (")[2].partition(")")[0]
        self.assertEqual([p.strip() for p in listed.split(",")], ["?"] * len(dirs), sql)
        self.assertEqual(params, tuple(dirs), "each directory arrives as a bound parameter")

    def unsignalled(self, claude: bool) -> dict:
        """The selection's environment with no harness named or signalled, and a Claude
        transcript for this repo when `claude` is set."""
        transcripts = self.home / ("claude" if claude else "none")
        if claude:
            transcripts.mkdir(exist_ok=True)
            (transcripts / "session.jsonl").write_text("{}\n", "utf-8")
        return {token_meters.HARNESS_ENV: None, run_state.TRANSCRIPTS_ENV: str(transcripts)}

    def test_an_unreadable_store_is_a_candidate(self) -> None:
        """BG1240 AC1. Mutant: `store()` keeping `except sqlite3.Error: return None` for a file
        that exists, so the selection falls to Claude by default with no warning."""
        def junk() -> None:
            self.db.parent.mkdir(parents=True, exist_ok=True)
            self.db.write_bytes(b"not a database at all" * 100)

        def sealed() -> None:
            make_db(self.db, str(self.root), str(self.other))
            self.db.chmod(0)
            self.addCleanup(self.db.chmod, stat.S_IRUSR | stat.S_IWUSR)
        cases = {"bytes that are not a database": junk, "mode 000": sealed}
        for label, unreadable in cases.items():
            with self.subTest(store=label):
                if label == "mode 000" and os.geteuid() == 0:
                    self.skipTest("root reads a mode 000 file, so it is not unreadable")
                for leftover in self.data.glob("opencode.db*"):
                    leftover.chmod(stat.S_IRUSR | stat.S_IWUSR)
                    leftover.unlink()
                unreadable()
                with self.env(**self.unsignalled(claude=False)):
                    alone = run_state.session_tokens(self.root)
                self.assertEqual(alone[token_meters.HARNESS], "opencode", alone)
                self.assertIn("could not be", alone["selected_by"])
                self.assertIsNone(alone["tokens"])
                self.assertIn(str(self.db), alone["reason"])
                self.assertIn("could not be read", alone["reason"])
                with self.env(**self.unsignalled(claude=True)):
                    both = run_state.session_tokens(self.root)
                self.assertIsNone(both["tokens"])
                self.assertIsNone(both[token_meters.HARNESS], both)
                self.assertEqual(both["candidates"], ["claude", "opencode"])
                self.assertIn("opencode (its store could not be", both["reason"])
        self.assertFalse(self.mark.exists())

    def test_a_readable_store_of_other_directories_is_not_a_candidate(self) -> None:
        """BG1240 AC2. Mutant: a fix that raises, or reports a candidate, for every database that
        exists, readable or not."""
        make_db(self.db, str(self.other), str(self.other))
        with self.env(**self.unsignalled(claude=False)):
            self.assertIsNone(meter_opencode.store(self.root, os.environ))
            alone = run_state.session_tokens(self.root)
        self.assertEqual(alone[token_meters.HARNESS], "claude", alone)
        self.assertIn("the default", alone["selected_by"])
        with self.env(**self.unsignalled(claude=True)):
            both = run_state.session_tokens(self.root)
        self.assertEqual(both[token_meters.HARNESS], "claude", both)
        self.assertNotIn("candidates", both)
        self.assertIn(str(self.home / "claude"), both["selected_by"])
        self.assertNotIn(str(self.db), both["selected_by"])

    def test_a_read_leaves_the_database_bytes_unchanged(self) -> None:
        """BG1240 AC3. Mutants: the docstring keeping that the write-ahead log is not written, or
        `connect` dropping `mode=ro` or `PRAGMA query_only`. A read-write open that only reads
        leaves a closed WAL database's bytes as they were too, so the open itself is pinned: the
        spy writes on every open that permits it, so the bytes then change as well."""
        make_db(self.db, str(self.root), str(self.other))
        self.assertFalse(Path(f"{self.db}-wal").exists(), "the fixture is closed cleanly")
        before = self.db.read_bytes()
        with self.opens() as opened:
            got = meter_opencode.read_db(self.db, self.root)
        self.assertEqual(got["tokens"], TOKENS, got.get("reason"))
        self.assert_read_only(opened, "read_db")
        self.assertEqual(self.db.read_bytes(), before, "the database's own bytes are unchanged")
        doc = " ".join(meter_opencode.__doc__.split())
        self.assertNotIn("nor its write-ahead log", doc)
        for said in ("never writes the database", "`-wal`", "`-shm`"):
            self.assertIn(said, doc)

    def test_legacy_json_store_reads_the_same_basis(self) -> None:
        """AC3. Mutant: returning not attributable whenever the database is absent, or reading
        the legacy tree on another basis than the database's."""
        storage = make_legacy(self.data / "storage", str(self.root), str(self.other))
        got = self.reading()
        self.assert_folded(got, str(storage))
        # The child is the parent's by `parentID`, wherever it ran.
        info = storage / "session" / "global" / f"{CHILD}.json"
        info.write_text(json.dumps({**json.loads(info.read_text("utf-8")),
                                    "directory": str(self.other)}), encoding="utf-8")
        self.assert_folded(self.reading(), str(storage))
        with self.env():
            self.assertIn(str(storage), meter_opencode.store(self.root, os.environ))
        # Under XDG_DATA_HOME, as OpenCode resolves its data directory.
        xdg = self.home / "xdg"
        make_legacy(xdg / "opencode" / "storage", str(self.root), str(self.other))
        self.assert_folded(self.reading(XDG_DATA_HOME=str(xdg)), str(xdg / "opencode"))
        # A database present is the store, and the tree beside it is not added to it.
        make_db(self.db, str(self.root), str(self.other))
        got = self.reading()
        self.assertEqual(got["tokens"], TOKENS)
        self.assertIn(str(self.db), got["source"])
        self.assertFalse(self.mark.exists())

    def test_missing_or_malformed_store_is_not_attributable(self) -> None:
        """AC4. Mutants: a missing store, an empty one or a malformed count becoming zero, or a
        malformed message skipped so a partial figure is published."""
        def none(got: dict, *needles: str) -> None:
            self.assertIsNone(got["tokens"], got)
            self.assertEqual(got[token_meters.HARNESS], "opencode")
            for n in needles:
                self.assertIn(n, got["reason"])
        for on_path in (True, False):
            path = os.environ.get("PATH", "") if on_path else str(self.home / "nobin")
            with self.subTest(binary_on_path=on_path):
                none(self.reading(PATH=f"{self.bin}{os.pathsep}{path}" if on_path else path),
                     str(self.db), "storage")
        self.assertFalse(self.mark.exists())
        none(self.reading(OPENCODE_DB=":memory:"), "in-memory")
        # Relative OPENCODE_DB names a file in the data directory, as OpenCode resolves it.
        make_db(self.data / "other.db", str(self.other), str(self.other))
        none(self.reading(OPENCODE_DB="other.db"), str(self.data / "other.db"), "no session")
        con = sqlite3.connect(self.data / "empty.db")
        con.executescript(DDL)
        con.close()
        none(self.reading(OPENCODE_DB=str(self.data / "empty.db")), "no session")
        (self.data / "junk.db").write_bytes(b"not a database at all" * 100)
        none(self.reading(OPENCODE_DB=str(self.data / "junk.db")), "could not be read")
        zero = assistant(str(self.root), tokens(0, 0, 0, 0, 0))
        con = sqlite3.connect(self.data / "zero.db")
        con.executescript(DDL)
        with con:
            con.execute("INSERT INTO session (id, project_id, slug, directory, title, version, "
                        "time_created, time_updated) VALUES (?, 'g', 's', ?, 't', 'v', 1, 2)",
                        (PARENT, str(self.root)))
            con.execute("INSERT INTO message VALUES ('m', ?, 1, 1, ?)", (PARENT, json.dumps(zero)))
        con.close()
        none(self.reading(OPENCODE_DB=str(self.data / "zero.db")), "no token")
        bad = {"string": tokens("12", 1, 0, 0, 0, total=False),
               "negative": tokens(-1, 1, 0, 0, 0, total=False),
               "boolean": tokens(True, 1, 0, 0, 0, total=False),
               "no cache": {"input": 1, "output": 1, "reasoning": 0, "total": 2},
               "a total matching neither shape": tokens(1, 1, 1, 0, 0, total=99)}
        for n, (label, toks) in enumerate(bad.items()):
            with self.subTest(malformed=label):
                db = make_db(self.data / f"bad{n}.db", str(self.root), str(self.other),
                             extra=[(CHILD, "msg_bad", assistant(str(self.root), toks))])
                none(self.reading(OPENCODE_DB=str(db)), "msg_bad")
        db = make_db(self.data / "notjson.db", str(self.root), str(self.other),
                     extra=[(PARENT, "msg_bad", "{not json")])
        none(self.reading(OPENCODE_DB=str(db)), "msg_bad")
        # The legacy tree too: a message file that is not JSON is refused, not skipped.
        storage = make_legacy(self.data / "storage", str(self.root), str(self.other))
        (storage / "message" / PARENT / "msg_bad.json").write_text("{not json", "utf-8")
        none(self.reading(), "msg_bad")
        self.assertFalse(self.mark.exists())


class OpenCodeLaneTests(_Fixture):

    def test_plan_write_stamps_an_opencode_baseline(self) -> None:
        """AC5. Mutant: the reader passing its unit tests while the plan path never reaches it
        (`open_run` stamping the Claude reading, or none), so the baseline names no opencode."""
        make_db(self.db, str(self.root), str(self.other))
        (self.root / "src").mkdir()
        (self.root / "src" / "bg0001.py").write_text("", encoding="utf-8")
        bugs = self.root / "sdlc-studio" / "bugs"
        bugs.mkdir(parents=True)
        (bugs / "BG0001-x.md").write_text(
            "# BG0001: b\n\n> **Status:** Open\n> **Severity:** Medium\n"
            "> **Affects:** src/bg0001.py\n> **Points:** 2\n\n## Acceptance Criteria\n\n"
            "### AC1: it behaves as recorded\n\n- **Given** the recorded state\n"
            "- **Verify:** shell true\n", encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(SPRINT), "plan", "--bugs", "Open", "--write", "--no-fetch",
             "--root", str(self.root)],
            env=self.environment(), capture_output=True, text=True, timeout=300,
            check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr[-2000:])
        base = run_state.read(self.root)[run_state.TOKEN_BASELINE]
        self.assertEqual(base[token_meters.HARNESS], "opencode")
        self.assertIn(str(self.db), base["source"])
        self.assertEqual((base["tokens"], base[token_meters.CACHE_READ]), (TOKENS, CACHE_READS))
        self.assertEqual(base["components"], COMPONENTS)
        self.assertFalse(self.mark.exists(), "no opencode process is started")


if __name__ == "__main__":
    unittest.main()
