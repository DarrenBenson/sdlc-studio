"""US1127 (CR0668): a Codex CLI run records its token actual from the store Codex keeps.

`lib/meter_codex.py` reads Codex CLI 0.160.0's state store, `~/.codex/state_5.sqlite`, for the
threads whose working directory is the workspace, and each thread's figure from the last
`token_count` its rollout records. Every test reaches it through the shipped selector,
`run_state.session_tokens`, against a fixture store under a temporary HOME: no test touches the
real `~/.codex`, and `CODEX_HOME` is scrubbed unless a test sets it.

The fixture is built from a session captured on 2026-11-06 (`codex exec --json`, codex-cli
0.160.0), scrubbed of its account identifiers: the `threads` columns the reader reads, as the
build created them, and the rollout's `token_count` event as Codex wrote it.

Pinned here:

* the cached input is split out of `input_tokens`, which includes it, and carried as
  `cache_read`; `tokens` is input + output + cache write (AC1);
* with no `SDLC_STUDIO_HARNESS`, `CODEX_THREAD_ID`, which a real session set in the shell its
  command ran in, chooses Codex, and `codex` is in `token_meters.HARNESSES` (AC2);
* a missing, locked or unreadable store is tokens None with the reason, never zero, and every
  open of the store is read-only (AC3);
* BG1246: `CODEX_HOME` names the store when set, a sibling directory sharing the workspace's
  name as a prefix is not the workspace, a locked store is abandoned within `TIMEOUT_SECONDS` by
  the wall clock, and a read leaves the store's bytes unchanged.

Run from the repo root:
    python3 -m pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_codex.py
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/meter_codex.py
from __future__ import annotations

import contextlib
import json
import os
import sqlite3
import sys

import pytest
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib import meter_codex, run_state, token_meters  # noqa: E402

SCRUB = (run_state.TRANSCRIPTS_ENV, *token_meters.selection_variables())
#: The CODEX_ variables a real codex-cli 0.160.0 session set in the shell it ran
#: `env | cut -d= -f1 | sort` in, captured 2026-11-06. A Codex signal must be one of these.
CAPTURED_SESSION_VARIABLES = ("CODEX_CI", "CODEX_PERMISSION_PROFILE",
                              "CODEX_SANDBOX_NETWORK_DISABLED", "CODEX_SESSION_ID",
                              "CODEX_THREAD_ID", "CODEX_VERSION")
#: The captured session's final `token_count`, its `info.total_token_usage` as written.
CAPTURED_USAGE = {"input_tokens": 14524, "cached_input_tokens": 12288,
                  "cache_write_input_tokens": 0, "output_tokens": 5,
                  "reasoning_output_tokens": 0, "total_tokens": 14529}
#: Its `threads.tokens_used`: input + output, the cached input inside it.
CAPTURED_TOKENS_USED = 14529
#: The captured `threads` columns the reader reads, and the spawn edges table, as codex-cli
#: 0.160.0 created them (the account columns `creator_user_id` and `creator_account_id` dropped).
THREADS_DDL = """CREATE TABLE threads (
    id TEXT PRIMARY KEY,
    rollout_path TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL,
    source TEXT NOT NULL,
    model_provider TEXT NOT NULL,
    cwd TEXT NOT NULL,
    title TEXT NOT NULL,
    tokens_used INTEGER NOT NULL DEFAULT 0,
    cli_version TEXT NOT NULL DEFAULT '',
    model TEXT)"""
EDGES_DDL = """CREATE TABLE thread_spawn_edges (
    parent_thread_id TEXT NOT NULL,
    child_thread_id TEXT NOT NULL PRIMARY KEY,
    status TEXT NOT NULL)"""
THREAD = "01a1b08f-6aa6-7db1-93e7-b71b8ab17ef6"
#: input 14524 less 12288 cached = 2236 uncached, + 5 output + 0 cache write.
TOKENS, CACHED = 2236 + 5 + 0, 12288
#: Slack over `TIMEOUT_SECONDS` for a read of a locked store; SQLite's default wait is 5 s.
MARGIN = 1.5
#: The page that documents each reader's store.
REFERENCE = Path(__file__).resolve().parents[2] / "reference-sprint.md"


def codex_bullet() -> str:
    """The Codex CLI bullet of `reference-sprint.md`, its lines joined."""
    lines = REFERENCE.read_text(encoding="utf-8").splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("- **Codex CLI"))
    end = next((i for i in range(start + 1, len(lines)) if not lines[i].startswith("  ")),
               len(lines))
    return " ".join(" ".join(lines[start:end]).split())


def token_count(usage: dict) -> dict:
    """A rollout `token_count` event as the captured session wrote it, rate limits dropped."""
    return {"timestamp": "2026-11-06T11:12:34.856Z", "ordinal": 13, "type": "event_msg",
            "payload": {"type": "token_count", "info": {
                "total_token_usage": usage, "last_token_usage": usage,
                "model_context_window": 475000}}}


class CodexMeterTests(unittest.TestCase):
    """A workspace, a fixture Codex home under a temporary HOME and a scrubbed environment."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        base = Path(tmp.name)
        self.root = base / "repo"
        self.root.mkdir()
        self.home = base / "home"
        self.codex = self.home / ".codex"
        self.codex.mkdir(parents=True)
        self.db = self.codex / meter_codex.STATE_DB
        self.transcripts = base / "transcripts"
        self.transcripts.mkdir()

    def store(self, *threads: tuple, edges: tuple = (), codex: Path | None = None) -> None:
        """The state store in `codex`, by default `~/.codex`, WAL as Codex keeps it, with one
        row per (id, cwd, usage or None, tokens_used) and its rollout holding a `session_meta`
        line and, unless usage is None, the `token_count` event."""
        codex = self.codex if codex is None else codex
        codex.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(codex / meter_codex.STATE_DB)
        con.execute("PRAGMA journal_mode=WAL")
        con.execute(THREADS_DDL)
        con.execute(EDGES_DDL)
        for n, (tid, cwd, usage, used) in enumerate(threads):
            rollout = codex / "sessions" / f"rollout-{tid}.jsonl"
            rollout.parent.mkdir(exist_ok=True)
            lines = [{"type": "session_meta", "payload": {"id": tid, "cwd": str(cwd),
                                                          "cli_version": "0.160.0"}}]
            lines += [token_count(usage)] if usage is not None else []
            rollout.write_text("".join(json.dumps(x) + "\n" for x in lines), encoding="utf-8")
            con.execute("INSERT INTO threads VALUES (?, ?, ?, ?, 'exec', 'openai', ?, 'OK', ?, "
                        "'0.160.0', 'gpt-6.1-sol')",
                        (tid, str(rollout), 1793963551 + n, 1793963554 + n, str(cwd), used))
        con.executemany("INSERT INTO thread_spawn_edges VALUES (?, ?, 'completed')", edges)
        con.commit()
        con.close()

    @contextlib.contextmanager
    def env(self, **values: str):
        """No harness variable and no `CODEX_HOME` but `values`, HOME at the fixture, no Claude
        transcript."""
        with mock.patch.dict(os.environ):
            for v in (*SCRUB, "CODEX_HOME"):
                os.environ.pop(v, None)
            os.environ.update({"HOME": str(self.home), "XDG_DATA_HOME": str(self.home),
                               run_state.TRANSCRIPTS_ENV: str(self.transcripts), **values})
            yield

    def test_reads_the_captured_session(self) -> None:
        """AC1. Mutants: `input_tokens` booked whole beside the cached input (the cached input
        counted twice), the cached input dropped, `tokens_used` read as the figure, or a thread
        outside the workspace counted."""
        self.store((THREAD, self.root, CAPTURED_USAGE, CAPTURED_TOKENS_USED),
                   ("other", self.root.parent / "elsewhere", CAPTURED_USAGE, 14529))
        with self.env(SDLC_STUDIO_HARNESS="codex"):
            got = run_state.session_tokens(self.root)
        self.assertEqual((got["tokens"], got[token_meters.CACHE_READ]), (TOKENS, CACHED),
                         got.get("reason"))
        comps = {"input": 2236, "output": 5, "cache_write_5m": 0, "cache_write_1h": 0,
                 "cache_read": 12288}
        self.assertEqual(got["components"], comps)
        self.assertEqual(got["priced"], run_state.price(comps))
        self.assertEqual((got[token_meters.HARNESS], got["selected_by"]),
                         ("codex", token_meters.HARNESS_ENV))
        self.assertEqual((got["threads"], got["model"]), (1, "gpt-6.1-sol"))
        self.assertIn(str(self.db), got["source"])
        self.assertIs(got["includes_subagents"], False)
        self.assertIn("cached", got["basis"])

    def test_a_spawned_thread_and_a_cache_write_are_each_counted_once(self) -> None:
        """AC1. Mutants: a cache write counted inside input and again beside it, a spawned
        thread in the workspace dropped, or a thread that has spent nothing refused."""
        child = {"input_tokens": 3000, "cached_input_tokens": 1000,
                 "cache_write_input_tokens": 500, "output_tokens": 40,
                 "reasoning_output_tokens": 10, "total_tokens": 3040}
        lane = self.root / ".claude" / "worktrees" / "lane"
        self.store((THREAD, self.root, CAPTURED_USAGE, CAPTURED_TOKENS_USED),
                   ("child", lane, child, 3040), ("idle", self.root, None, 0),
                   edges=((THREAD, "child"),))
        with self.env(SDLC_STUDIO_HARNESS="codex"):
            got = run_state.session_tokens(self.root)
        self.assertEqual(got["components"], {"input": 2236 + 1500, "output": 45,
                                             "cache_write_5m": 500, "cache_write_1h": 0,
                                             "cache_read": 13288}, got.get("reason"))
        self.assertEqual(got["tokens"], 3736 + 45 + 500)
        self.assertEqual(got["threads"], 3)
        self.assertIs(got["includes_subagents"], True)

    def test_selected_by_the_codex_session_signal(self) -> None:
        """AC2. Mutants: a signal no captured session set (`CODEX_HOME`, say), `codex` left out
        of HARNESSES, or the signal not reaching the scrub list."""
        self.assertIn(token_meters.CODEX, token_meters.HARNESSES)
        self.assertEqual(token_meters.CODEX, "codex")
        signals = token_meters.SIGNALS[token_meters.CODEX]
        self.assertTrue(signals)
        for v in signals:
            self.assertIn(v, CAPTURED_SESSION_VARIABLES, "a signal a real session does not set")
            self.assertIn(v, token_meters.selection_variables())
        self.store((THREAD, self.root, CAPTURED_USAGE, CAPTURED_TOKENS_USED))
        with self.env(CODEX_THREAD_ID=THREAD):
            got = run_state.session_tokens(self.root)
        self.assertEqual((got["tokens"], got[token_meters.HARNESS]), (TOKENS, "codex"),
                         got.get("reason"))
        self.assertEqual(got["selected_by"], "the environment (CODEX_THREAD_ID)")
        with self.env(CODEX_HOME=str(self.codex)):
            got = run_state.session_tokens(self.root)
        self.assertEqual(got[token_meters.HARNESS], "codex")
        self.assertIn("the only harness store present", got["selected_by"],
                      "CODEX_HOME signals nothing; the store on disk chose")
        self.db.unlink()
        with self.env(CODEX_HOME=str(self.codex)):
            self.assertEqual(run_state.session_tokens(self.root)[token_meters.HARNESS], "claude")
        with self.env(CODEX_THREAD_ID=THREAD, CLAUDECODE="1"):
            got = run_state.session_tokens(self.root)
        self.assertEqual((got["tokens"], got["candidates"]), (None, ["claude", "codex"]))

    def test_missing_or_unreadable_store_is_named_and_read_only(self) -> None:
        """AC3. Mutants: a read-write open, a missing store, a locked one or a thread whose
        usage cannot be read booked as zero. How long a lock is waited on is BG1246 AC3's, timed
        by the clock in `test_a_locked_store_is_abandoned_within_the_bound`."""
        with self.env(SDLC_STUDIO_HARNESS="codex"):
            got = run_state.session_tokens(self.root)
        self.assertIsNone(got["tokens"], "a missing store is no reading, never zero")
        self.assertIn(f"no Codex state store sits at {self.db}", got["reason"])

        self.db.write_bytes(b"not a database, " * 64)
        with self.env(SDLC_STUDIO_HARNESS="codex"):
            got = run_state.session_tokens(self.root)
        self.assertIsNone(got["tokens"])
        self.assertIn(f"the Codex state store {self.db} could not be read (DatabaseError)",
                      got["reason"])
        self.db.unlink()

        self.store((THREAD, self.root, CAPTURED_USAGE, CAPTURED_TOKENS_USED))
        before = self.db.read_bytes()
        real, opens = sqlite3.connect, []

        def spy(database, *args, **kwargs):
            con = real(database, *args, **kwargs)
            try:
                con.execute("CREATE TABLE written_by_the_reader (x)")
                opens.append((str(database), "read-write"))
            except sqlite3.OperationalError:
                opens.append((str(database), "read-only"))
            return con
        with self.env(SDLC_STUDIO_HARNESS="codex"), mock.patch.object(sqlite3, "connect", spy):
            got = run_state.session_tokens(self.root)
        self.assertEqual(got["tokens"], TOKENS, got.get("reason"))
        self.assertTrue(opens, "the store was read without being opened")
        for where, how in opens:
            self.assertEqual(how, "read-only", f"{where} was opened for writing")
            self.assertIn("mode=ro", where)
        self.assertEqual(self.db.read_bytes(), before, "the store's bytes changed")

        rollout = self.codex / "sessions" / f"rollout-{THREAD}.jsonl"
        rollout.unlink()
        with self.env(SDLC_STUDIO_HARNESS="codex"):
            got = run_state.session_tokens(self.root)
        self.assertIsNone(got["tokens"], "a thread that spent tokens is never read as zero")
        self.assertIn(f"Codex thread {THREAD}'s rollout {rollout} is missing", got["reason"])
        overlap = {**CAPTURED_USAGE, "total_tokens": 14529 + 12288}
        rollout.write_text(json.dumps(token_count(overlap)) + "\n", encoding="utf-8")
        with self.env(SDLC_STUDIO_HARNESS="codex"):
            got = run_state.session_tokens(self.root)
        self.assertIsNone(got["tokens"], "a total whose parts may overlap is refused")
        self.assertIn("records a total_tokens that is not input_tokens + output_tokens",
                      got["reason"])

        holder = sqlite3.connect(self.db)
        self.addCleanup(holder.close)
        holder.execute("PRAGMA locking_mode=EXCLUSIVE")
        holder.execute("BEGIN EXCLUSIVE")
        with self.env(SDLC_STUDIO_HARNESS="codex"), \
                mock.patch.object(meter_codex, "TIMEOUT_SECONDS", 0.05):
            got = run_state.session_tokens(self.root)
        self.assertIsNone(got["tokens"], "a locked store is no reading, never zero")
        self.assertIn(f"the Codex state store {self.db} could not be read (OperationalError)",
                      got["reason"])
        self.assertLessEqual(meter_codex.TIMEOUT_SECONDS, 2)
        holder.rollback()
        holder.close()

        with self.env(SDLC_STUDIO_HARNESS="codex"):
            got = run_state.session_tokens(self.home)
        self.assertIsNone(got["tokens"])
        self.assertIn("holds no thread whose working directory is", got["reason"])


    def test_codex_home_names_the_store(self) -> None:
        """BG1246 AC1. Mutants: `codex_home` reading only HOME, `CODEX_HOME` honoured by the
        reading but not by the store the selection looks for, HOME's store preferred when both
        exist, or an empty `CODEX_HOME` taken for a directory."""
        relocated = self.home.parent / "relocated-codex"
        moved = {**CAPTURED_USAGE, "input_tokens": 20000, "total_tokens": 20005}
        self.store((THREAD, self.root, moved, 20005), codex=relocated)
        self.codex.rmdir()
        with self.env(SDLC_STUDIO_HARNESS="codex", CODEX_HOME=str(relocated)):
            got = run_state.session_tokens(self.root)
        self.assertEqual(got["tokens"], 20000 - CACHED + 5, got.get("reason"))
        self.assertIn(str(relocated / meter_codex.STATE_DB), got["source"])
        with self.env(CODEX_HOME=str(relocated)):
            got = run_state.session_tokens(self.root)
        self.assertEqual((got["tokens"], got[token_meters.HARNESS]),
                         (20000 - CACHED + 5, "codex"), got.get("reason"))
        self.assertIn("the only harness store present", got["selected_by"])

        self.store((THREAD, self.root, CAPTURED_USAGE, CAPTURED_TOKENS_USED))
        with self.env(SDLC_STUDIO_HARNESS="codex", CODEX_HOME=str(relocated)):
            got = run_state.session_tokens(self.root)
        self.assertEqual(got["tokens"], 20000 - CACHED + 5, "a stale ~/.codex was read instead")
        for unset in ({}, {"CODEX_HOME": ""}):
            with self.env(SDLC_STUDIO_HARNESS="codex", **unset):
                got = run_state.session_tokens(self.root)
            self.assertEqual(got["tokens"], TOKENS, (unset, got.get("reason")))
            self.assertIn(str(self.db), got["source"])
        self.assertIn("`CODEX_HOME`, else `~/.codex`", codex_bullet())

    def test_a_sibling_prefix_workspace_is_not_this_repo_s(self) -> None:
        """BG1246 AC2. Mutant: the workspace boundary read as a bare prefix,
        `startswith(workspace)`, which books `<base>/repo-old`'s thread to `<base>/repo`."""
        sibling = self.root.parent / f"{self.root.name}-old"
        sibling.mkdir()
        other = {**CAPTURED_USAGE, "input_tokens": 30000, "total_tokens": 30005}
        self.store((THREAD, self.root, CAPTURED_USAGE, CAPTURED_TOKENS_USED),
                   ("sibling", sibling, other, 30005))
        with self.env(SDLC_STUDIO_HARNESS="codex"):
            got = run_state.session_tokens(self.root)
        self.assertEqual((got["tokens"], got["threads"]), (TOKENS, 1), got.get("reason"))
        with self.env(SDLC_STUDIO_HARNESS="codex"):
            got = run_state.session_tokens(sibling)
        self.assertEqual((got["tokens"], got["threads"]), (30000 - CACHED + 5, 1),
                         "the sibling's own thread is readable, so only the boundary kept it out")

    @pytest.mark.serial_only
    @pytest.mark.boundary_only
    def test_a_locked_store_is_abandoned_within_the_bound(self) -> None:
        """BG1246 AC3. Mutants: `timeout=TIMEOUT_SECONDS` dropped from the store's open, so a
        locked store is waited on for SQLite's default 5 s, or `timeout=0`, so a lock Codex holds
        for a moment is not waited on at all. The wait is timed, never read off the constant."""
        self.store((THREAD, self.root, CAPTURED_USAGE, CAPTURED_TOKENS_USED))
        holder = sqlite3.connect(self.db)
        self.addCleanup(holder.close)
        holder.execute("PRAGMA locking_mode=EXCLUSIVE")
        holder.execute("BEGIN EXCLUSIVE")
        bound = 0.2
        with self.env(SDLC_STUDIO_HARNESS="codex"), \
                mock.patch.object(meter_codex, "TIMEOUT_SECONDS", bound):
            began = time.monotonic()
            got = run_state.session_tokens(self.root)
            waited = time.monotonic() - began
        self.assertIsNone(got["tokens"], "a locked store is no reading, never zero")
        self.assertIn(f"the Codex state store {self.db} could not be read (OperationalError)",
                      got["reason"])
        self.assertLess(waited, bound + MARGIN, f"a lock bounded at {bound} s held {waited:.2f} s")
        self.assertGreaterEqual(waited, bound / 2, "the lock was not waited on at all")

    def test_a_read_leaves_the_store_s_bytes_unchanged(self) -> None:
        """BG1246 AC4. Mutants: the store's open losing `mode=ro`, so the write this test tries
        through each connection the reader opens lands in the store, or the module docstring or
        `reference-sprint.md` keeping 'never opened for writing' with nothing said of the files
        a read creates."""
        self.store((THREAD, self.root, CAPTURED_USAGE, CAPTURED_TOKENS_USED))
        for suffix in ("-wal", "-shm"):
            self.assertFalse(Path(f"{self.db}{suffix}").exists(), "the store was not closed")
        before, listed = self.db.read_bytes(), set(os.listdir(self.codex))
        real, opened = sqlite3.connect, []

        def writer(database, *args, **kwargs):
            con = real(database, *args, **kwargs)
            opened.append(str(database))
            with contextlib.suppress(sqlite3.OperationalError):
                con.execute("CREATE TABLE written_by_the_reader (x)")
            return con
        with self.env(SDLC_STUDIO_HARNESS="codex"), mock.patch.object(sqlite3, "connect", writer):
            got = run_state.session_tokens(self.root)
        self.assertEqual(got["tokens"], TOKENS, got.get("reason"))
        self.assertTrue(opened, "the store was read without being opened")
        self.assertEqual(self.db.read_bytes(), before, "a read changed the store's bytes")
        self.assertLessEqual(set(os.listdir(self.codex)) - listed,
                             {f"{meter_codex.STATE_DB}-wal", f"{meter_codex.STATE_DB}-shm"},
                             "a read left a file beside the store other than SQLite's own")
        for where, text in (("the module docstring", " ".join(meter_codex.__doc__.split())),
                            ("reference-sprint.md", codex_bullet())):
            self.assertNotIn("never opened for writing", text, where)
            for said in ("never written", "`-wal`", "`-shm`"):
                self.assertIn(said, text, f"{where} does not say {said!r}")


if __name__ == "__main__":
    unittest.main()
