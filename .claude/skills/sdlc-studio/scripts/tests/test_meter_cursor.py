"""US0989 (CR0611): a Cursor cloud run records its token actual from the usage API when a key is
present.

A Cursor cloud sprint once published NOT MEASURED, because the only meter was the Claude Code
transcript. `lib/meter_cursor.py` reads the agent's `totalUsage` from Cursor's cloud usage API,
and every test here reaches it through the shipped selector, `run_state.session_tokens`, against
a local stub server: no test touches the network.

Pinned here:

* `tokens` is input + output + cache write, cache reads apart, never `totalTokens`, and the
  source names the agent id; the agent id alone signals Cursor (AC1);
* no key or no agent id makes no request, and an HTTP error, a timeout, an unreachable API or
  an empty usage is tokens None with a reason, never zero, within the timeout (AC2);
* the key reaches neither the reading, the run state, a stamp nor the run total (AC3);
* `sprint.py plan --write` stamps a baseline naming cursor and the agent id (AC4).

US0990 adds the Cursor CLI's surface, pinned in `CursorCliTests`: the chat store is found where
the CLI writes it, records no usage, so reads tokens None naming it, never zero, and the cloud
and CLI surfaces are never added together.

BG1213: a base that would send the key in cleartext, one neither https nor http on a loopback
address, is refused before any request, the reason naming `SDLC_STUDIO_CURSOR_API`.

US1121 (CR0662), pinned in `CursorHookLedgerTests`: `cursor_usage_hook.py`, run as the CLI's
`afterAgentResponse` hook, appends each response's counts to a ledger the CLI reading sums and
prices as measured; with no ledger the reading is the store's, as before, and a malformed line
is skipped and counted.

Run from the repo root:
    python3 -m pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_cursor.py
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/meter_cursor.py
from __future__ import annotations

import contextlib
import http.server
import json
import os
import socket
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib import meter_cursor, run_state, token_meters  # noqa: E402

SPRINT = Path(__file__).resolve().parents[1] / "sprint.py"
KEY = "key-7f3a-DO-NOT-RECORD"
AGENT = "bc-5e1d-4c2a"
#: 1,000 input + 200 output + 3,000 cache write = 4,200; 50,000 cache reads; 54,200 in all.
USAGE = {"inputTokens": 1_000, "outputTokens": 200, "cacheWriteTokens": 3_000,
         "cacheReadTokens": 50_000, "totalTokens": 54_200}
TOKENS, CACHE_READS = 4_200, 50_000
#: Every variable the selection or the call reads, scrubbed so the suite's own harness and any
#: proxy never reach a test.
SCRUB = (token_meters.HARNESS_ENV, run_state.TRANSCRIPTS_ENV, meter_cursor.KEY_ENV,
         meter_cursor.AGENT_ENV, meter_cursor.API_ENV, meter_cursor.CONFIG_ENV,
         meter_cursor.XDG_ENV, *(v for vs in token_meters.SIGNALS.values() for v in vs),
         "http_proxy", "https_proxy", "all_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY")


def worker_ends(within: float) -> bool:
    """Whether every usage-call worker thread has ended within `within` seconds."""
    deadline = time.monotonic() + within
    while any(t.name == "cursor-usage" for t in threading.enumerate()):
        if time.monotonic() > deadline:
            return False
        time.sleep(0.05)
    return True


def answer(status: int = 200, doc=None, raw: bytes | None = None):
    """A stub reply: `status` with `doc` as JSON, or the bytes `raw`."""
    body = raw if raw is not None else json.dumps(doc).encode()

    def reply(h: http.server.BaseHTTPRequestHandler) -> None:
        h.send_response(status)
        h.send_header("Content-Type", "application/json")
        h.send_header("Content-Length", str(len(body)))
        h.end_headers()
        h.wfile.write(body)
    return reply


def usage(**over) -> dict:
    return {"totalUsage": {**USAGE, **over},
            "runs": [{"id": "run-1", "usageUuid": "u-1", "usage": {**USAGE, **over}}]}


class Stub:
    """A local server standing in for Cursor's API. Each request's path and headers are logged
    on `requests`, and `reply` (a function of the handler) answers it."""

    def __init__(self, test: unittest.TestCase, reply=None) -> None:
        self.requests: list[tuple[str, dict]] = []
        self.reply = reply or answer(doc=usage())
        self.release = threading.Event()
        stub = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802 - the http.server interface
                stub.requests.append((self.path, dict(self.headers)))
                stub.reply(self)

            def log_message(self, *args) -> None:
                pass

        self.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        test.addCleanup(self.server.server_close)
        test.addCleanup(self.server.shutdown)
        test.addCleanup(self.release.set)
        self.base = f"http://127.0.0.1:{self.server.server_address[1]}"


class _Fixture(unittest.TestCase):

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        (self.root / "home").mkdir()
        # The module the selector loads, which is the one a test patches.
        self.reader = token_meters.load_reader(token_meters.CURSOR)

    def environment(self, stub: Stub | None, **values: str) -> dict:
        env = {k: v for k, v in os.environ.items() if k not in SCRUB}
        env.update({"HOME": str(self.root / "home"),
                    run_state.TRANSCRIPTS_ENV: str(self.root / "home" / "none"),
                    token_meters.HARNESS_ENV: "cursor", meter_cursor.KEY_ENV: KEY,
                    meter_cursor.AGENT_ENV: AGENT})
        if stub is not None:
            env[meter_cursor.API_ENV] = stub.base
        env.update(values)
        return {k: v for k, v in env.items() if v is not None}

    @contextlib.contextmanager
    def env(self, stub: Stub | None, **values):
        """os.environ as `environment` gives it; a value of None drops that variable."""
        with mock.patch.dict(os.environ, clear=True):
            os.environ.update(self.environment(stub, **values))
            yield

    def reading(self, stub: Stub | None, **values) -> dict:
        with self.env(stub, **values):
            return run_state.session_tokens(self.root)


class CursorCloudTests(_Fixture):

    def test_usage_payload_counts_one_basis(self) -> None:
        """AC1. Mutants: `tokens` taken from `totalTokens` (54,200, cache reads in it), cache
        reads folded into `tokens`, a source naming no agent, or `SIGNALS` dropped so the agent
        id no longer signals Cursor and the default reads Claude instead."""
        stub = Stub(self)
        got = self.reading(stub)
        self.assertEqual((got["tokens"], got[token_meters.CACHE_READ]), (TOKENS, CACHE_READS))
        self.assertEqual(got[token_meters.HARNESS], "cursor")
        self.assertIn(AGENT, got["source"])
        self.assertIn("cache reads apart", got["basis"])
        path, headers = stub.requests[-1]
        self.assertEqual(path, f"/v1/agents/{AGENT}/usage")
        self.assertEqual(headers.get("Authorization"), f"Bearer {KEY}")

        by_signal = self.reading(stub, SDLC_STUDIO_HARNESS=None)
        self.assertEqual((by_signal["tokens"], by_signal[token_meters.HARNESS]),
                         (TOKENS, "cursor"), by_signal.get("reason"))
        self.assertIn(meter_cursor.AGENT_ENV, by_signal["selected_by"])
        self.assertEqual(len(stub.requests), 2)

        stub.reply = answer(doc=usage(totalTokens=55_000))
        got = self.reading(stub)
        self.assertIsNone(got["tokens"], "four counts that do not sum to totalTokens overlap")
        self.assertIn("totalTokens 55000 is not the sum", got["reason"])
        stub.reply = answer(doc={"totalUsage": {k: v for k, v in USAGE.items()
                                                if k != "totalTokens"}})
        self.assertEqual(self.reading(stub)["tokens"], TOKENS, "totalTokens absent is no fault")

    def test_no_key_no_call_and_failures_not_attributable(self) -> None:
        """AC2. Mutants: the key or agent-id check dropped (a request goes out), a socket timeout
        read as anything but the deadline, an empty usage read as 0, or an HTTP error, a
        malformed field, a broken status line or an oversized answer passed on as a figure. The
        two that only a clock can see, the worker joined with no timeout and the socket timeout
        dropped, are pinned by `test_a_held_or_dribbling_answer_is_cut_off_at_the_deadline`,
        which bounds wall time and so runs serially at the boundary."""
        self.assertLessEqual(meter_cursor.TIMEOUT_SECONDS, 10, "the timeout is short")
        stub = Stub(self)
        for drop, blank in ((meter_cursor.KEY_ENV, None), (meter_cursor.KEY_ENV, "  "),
                            (meter_cursor.AGENT_ENV, None), (meter_cursor.AGENT_ENV, "")):
            got = self.reading(stub, **{drop: blank})
            self.assertIsNone(got["tokens"])
            self.assertIn(f"{drop} is not set", got["reason"])
        got = self.reading(stub, **{meter_cursor.KEY_ENV: None, meter_cursor.AGENT_ENV: None,
                                    token_meters.HARNESS_ENV: "cursor"})
        self.assertIn(f"{meter_cursor.KEY_ENV} and {meter_cursor.AGENT_ENV} are not set",
                      got["reason"])
        self.assertEqual(stub.requests, [], "no request without both a key and an agent id")
        self.assertEqual(self.reading(stub)["tokens"], TOKENS, "the positive control")

        def hold(h) -> None:
            stub.release.wait(5)

        def dribble(h) -> None:
            for ch in b"HTTP/1.1 200 OK\r\nX-Slow: " + b"a" * 40:
                if stub.release.wait(0.1):
                    return
                h.wfile.write(bytes([ch]))

        cases = {
            "it answered HTTP 500": answer(500, {"error": {"code": "internal_error"}}),
            "it answered HTTP 404": answer(404, {"error": {"code": "run_not_found"}}),
            "it records no usage for this agent yet": answer(doc=usage(
                inputTokens=0, outputTokens=0, cacheWriteTokens=0, cacheReadTokens=0,
                totalTokens=0)),
            "records no usage for this agent yet": answer(doc={"runs": [{"id": "run-1"}]}),
            "its answer is not JSON": answer(raw=b"<html>gateway</html>"),
            "its totalUsage outputTokens is '200', not a count": answer(doc=usage(
                outputTokens="200")),
            "its totalUsage cacheReadTokens is True, not a count": answer(doc=usage(
                cacheReadTokens=True)),
            "its totalUsage is not an object": answer(doc={"totalUsage": [1, 2]}),
            "the call failed (BadStatusLine)": lambda h: h.wfile.write(b"NOT HTTP\r\n\r\n"),
        }
        for why, reply in cases.items():
            stub.reply = reply
            got = self.reading(stub)
            self.assertIsNone(got["tokens"], why)
            self.assertIn(why, got["reason"])
            self.assertIn(AGENT, got["reason"])
        stub.reply = answer(doc=usage())
        with mock.patch.object(self.reader, "MAX_BYTES", 10):
            got = self.reading(stub)
        self.assertIsNone(got["tokens"])
        self.assertIn("its answer exceeds 10 bytes", got["reason"])
        with mock.patch.object(self.reader, "TIMEOUT_SECONDS", 0.3):
            for reply in (hold, dribble):
                stub.reply = reply
                got = self.reading(stub)
                self.assertIsNone(got["tokens"])
                self.assertIn("did not answer within 0.3 seconds", got["reason"])
        for raised in (TimeoutError("timed out"), urllib.error.URLError(TimeoutError("t"))):
            with mock.patch.object(self.reader._OPENER, "open", side_effect=raised):
                got = self.reading(stub)
            self.assertIsNone(got["tokens"])
            self.assertIn(f"did not answer within {meter_cursor.TIMEOUT_SECONDS:g} seconds",
                          got["reason"], "a socket timeout reads as the deadline does")
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            closed = f"http://127.0.0.1:{s.getsockname()[1]}"
        got = self.reading(None, **{meter_cursor.API_ENV: closed})
        self.assertIsNone(got["tokens"])
        self.assertIn("could not be reached (ConnectionRefusedError)", got["reason"])

    @pytest.mark.serial_only
    @pytest.mark.boundary_only
    def test_a_held_or_dribbling_answer_is_cut_off_at_the_deadline(self) -> None:
        """AC2's clock half, kept out of a parallel commit run because it bounds a duration its
        own process measures (BG1212). Mutants: the worker joined with no timeout (the dribbling
        stub holds it for seconds), the socket timeout dropped (the held worker outlives the
        deadline)."""
        stub = Stub(self)

        def hold(h) -> None:
            stub.release.wait(5)

        def dribble(h) -> None:
            for ch in b"HTTP/1.1 200 OK\r\nX-Slow: " + b"a" * 40:
                if stub.release.wait(0.1):
                    return
                h.wfile.write(bytes([ch]))

        with mock.patch.object(self.reader, "TIMEOUT_SECONDS", 0.3):
            for reply in (hold, dribble):
                stub.reply = reply
                began = time.monotonic()
                got = self.reading(stub)
                self.assertLess(time.monotonic() - began, 2.0, reply.__name__)
                self.assertIsNone(got["tokens"])
                if reply is hold:
                    self.assertTrue(worker_ends(2.0), "a held socket times out the worker too")

    def test_the_key_is_never_recorded(self) -> None:
        """AC3. Mutants: a reason built from the error's message (its reason phrase echoes the
        key, as a refused header's ValueError quotes it), its body or its headers; a redirect
        followed with the key on it; a source built from the request URL or headers."""
        stub = Stub(self)

        def echo(h) -> None:
            seen = h.headers.get("Authorization", "")
            body = json.dumps({"error": {"message": f"bad credentials {seen}"}}).encode()
            h.send_response(401, f"Unauthorized {seen}")
            h.send_header("WWW-Authenticate", seen)
            h.send_header("Content-Length", str(len(body)))
            h.end_headers()
            h.wfile.write(body)

        def redirect(h) -> None:
            if h.path.startswith("/elsewhere"):
                return answer(doc=usage())(h)
            h.send_response(302)
            h.send_header("Location", f"{stub.base}/elsewhere")
            h.send_header("Content-Length", "0")
            h.end_headers()

        for reply, why in ((echo, "it answered HTTP 401"), (redirect, "it answered HTTP 302")):
            stub.reply = reply
            got = self.reading(stub)
            self.assertIsNone(got["tokens"])
            self.assertIn(why, got["reason"])
            self.assertNotIn(KEY, json.dumps(got))
        self.assertFalse([p for p, _ in stub.requests if p.startswith("/elsewhere")],
                         "a redirect is refused, not followed with the key")
        self.assertTrue(any(KEY in json.dumps(h) for _, h in stub.requests), "the key was sent")
        # A key no header can carry: http.client's refusal quotes the header value it refused.
        got = self.reading(stub, **{meter_cursor.KEY_ENV: f"{KEY}\nX-Injected: 1"})
        self.assertIn("the call failed (ValueError)", got["reason"])
        self.assertNotIn(KEY, json.dumps(got))

        stub.reply = answer(doc=usage())
        with self.env(stub):
            got = run_state.session_tokens(self.root)
            run_state.open_run(self.root, batch=["BG0001"], goal="g")
            stamped = run_state.stamp_tokens(self.root, "report")
        self.assertEqual(stamped["tokens"], TOKENS)
        state = run_state.read(self.root)
        total = run_state.run_token_total(state)
        for what, row in (("reading", got), ("stamp", stamped), ("run total", total),
                          ("run state", (self.root / run_state.REL).read_text("utf-8"))):
            self.assertNotIn(KEY, row if isinstance(row, str) else json.dumps(row), what)

    def test_a_cleartext_base_is_refused_before_any_request(self) -> None:
        """BG1213 AC1. Mutants: the scheme check dropped, or made after the request (an http
        base on a remote host is called with the key on it); the loopback exemption granted by a
        text match on the base (`127.0.0.1.example.net`, a userinfo of `127.0.0.1@`), to a host
        name (`localhost`), to a private address (`10.0.0.7`) or to any scheme (a loopback
        `ftp://`); the exemption dropped (the local stub and its IPv6 and 127/8 neighbours are
        refused); a base urlsplit cannot parse raised rather than refused; and the reason
        quoting the base, whose userinfo may hold a secret, or not naming the variable."""
        stub = Stub(self)
        self.assertEqual(self.reading(stub)["tokens"], TOKENS, "the loopback stub is read")
        port = stub.base.rsplit(":", 1)[1]
        refused = ("http://api.cursor.com", "http://10.0.0.7:8080",
                   f"http://127.0.0.1.example.net:{port}", f"http://127.0.0.1@example.net:{port}",
                   "http://user:s3cret@example.net", f"http://localhost:{port}",
                   f"ftp://127.0.0.1:{port}", "api.cursor.com", "http://[::1")
        allowed = (None, "https://api.example.net", f"http://[::1]:{port}",
                   f"http://127.0.0.2:{port}")
        why = (f"{meter_cursor.API_ENV} is neither an https URL nor an http one on a loopback "
               f"address, so no request is made")
        unreachable = urllib.error.URLError(ConnectionRefusedError())
        for base in refused + allowed:
            with mock.patch.object(self.reader._OPENER, "open", side_effect=unreachable) as call:
                got = self.reading(None, **{meter_cursor.API_ENV: base})
            self.assertIsNone(got["tokens"], base)
            if base in refused:
                call.assert_not_called()
                self.assertIn("SDLC_STUDIO_CURSOR_API", got["reason"], base)
                self.assertIn(why, got["reason"], base)
                self.assertNotIn(base, got["reason"])
                self.assertNotIn("s3cret", got["reason"])
            else:
                self.assertEqual(call.call_count, 1, base)
                self.assertTrue(call.call_args.args[0].full_url.startswith(
                    base or meter_cursor.API_BASE), base)
                self.assertIn("could not be reached (ConnectionRefusedError)", got["reason"])
                self.assertNotIn(meter_cursor.API_ENV, got["reason"], base)
        self.assertEqual(len(stub.requests), 1, "only the positive control reached the stub")


def _bug(root: Path) -> None:
    """One Open bug a plan can batch: sized, with an Affects that resolves and a criterion."""
    (root / "src").mkdir()
    (root / "src" / "bg0001.py").write_text("", encoding="utf-8")
    bugs = root / "sdlc-studio" / "bugs"
    bugs.mkdir(parents=True)
    (bugs / "BG0001-x.md").write_text(
        "# BG0001: b\n\n> **Status:** Open\n> **Severity:** Medium\n"
        "> **Affects:** src/bg0001.py\n> **Points:** 2\n\n## Acceptance Criteria\n\n"
        "### AC1: it behaves as recorded\n\n- **Given** the recorded state\n"
        "- **Verify:** shell true\n", encoding="utf-8")


class CursorCloudLaneTests(_Fixture):

    def test_plan_write_stamps_a_cursor_baseline(self) -> None:
        """AC4. Mutant: the reader passing its unit tests while the plan path never reaches it
        (`open_run` stamping the Claude reading, or none), so the baseline names no cursor."""
        _bug(self.root)
        stub = Stub(self)
        proc = subprocess.run(
            [sys.executable, str(SPRINT), "plan", "--bugs", "Open", "--write", "--no-fetch",
             "--root", str(self.root)],
            env=self.environment(stub), capture_output=True, text=True, timeout=300)
        self.assertEqual(proc.returncode, 0, proc.stderr[-2000:])
        base = run_state.read(self.root)[run_state.TOKEN_BASELINE]
        self.assertEqual(base[token_meters.HARNESS], "cursor")
        self.assertIn(AGENT, base["source"])
        self.assertEqual((base["tokens"], base[token_meters.CACHE_READ]), (TOKENS, CACHE_READS))
        self.assertIn(f"/v1/agents/{AGENT}/usage", [p for p, _ in stub.requests])
        self.assertNotIn(KEY, (self.root / run_state.REL).read_text("utf-8"))


#: This repository's checkout on the development machine, and the chats directory names the
#: Cursor CLI's 2026.10.22-27dcf5f build wrote there for it and for a sibling checkout.
DEV_REPO = "/home/darren/code/DarrenBenson/sdlc-studio"
DEV_CHATS = {DEV_REPO: "6e276e3188a9dbcce0e0ec6cbd9afdc1",
             f"{DEV_REPO}-lens": "ef6664fffe2e4dc1c8c6faedd4d2c614"}
#: A print run's last stdout line, in the shape that build writes, usage and all.
PRINT_RESULT = json.dumps({
    "type": "result", "subtype": "success", "is_error": False, "duration_ms": 9,
    "duration_api_ms": 9, "result": "done", "session_id": "chat-run", "request_id": "r-1",
    "usage": {"inputTokens": 1_000, "outputTokens": 200, "cacheReadTokens": 50_000,
              "cacheWriteTokens": 3_000}})


#: What that build runs on opening a chat store (`initializeDriver`): WAL first, then the tables.
CLI_INIT = """PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA busy_timeout = 5000;
PRAGMA user_version = 1;
CREATE TABLE IF NOT EXISTS blobs (id TEXT PRIMARY KEY, data BLOB);
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);"""


def cli_store(chats: Path, chat: str, conversation: bool = True, tables=(),
              live: unittest.TestCase | None = None) -> Path:
    """One chat in the shape the Cursor CLI's 2026.10.22-27dcf5f build wrote on the development
    machine, every value synthetic: a `meta.json`, and for a chat with a conversation a
    `store.db` opened as that build opens it, whose `meta` row is hex-encoded JSON and whose
    `blobs` hold a message. `tables` adds further tables, a store of some other build. Closed,
    the store is checkpointed into a WAL-mode `store.db` alone. Given a test as `live`, its
    connection stays open until that test's cleanup, as a chat the CLI holds open: the `-wal`
    and `-shm` sit beside it, and the tables are in the `-wal` alone."""
    chat_dir = chats / chat
    chat_dir.mkdir(parents=True)
    (chat_dir / "meta.json").write_text(json.dumps({
        "schemaVersion": 1, "createdAtMs": 1, "hasConversation": conversation,
        "updatedAtMs": 2, "cwd": "/workspace"}), encoding="utf-8")
    if conversation:
        con = sqlite3.connect(chat_dir / "store.db")
        con.executescript(CLI_INIT)
        with con:
            meta = {"agentId": chat, "latestRootBlobId": "0" * 64, "name": "New Agent",
                    "mode": "default", "isRunEverything": False, "createdAt": 1,
                    "lastUsedModel": "auto", "blobEncryptionKey": "0" * 64}
            con.execute("INSERT INTO meta VALUES ('0', ?)", (json.dumps(meta).encode().hex(),))
            message = {"id": "m-1", "role": "assistant", "providerOptions": {"cursor": {}},
                       "content": [{"type": "text", "text": "done"}]}
            con.execute("INSERT INTO blobs VALUES (?, ?)", ("1" * 64, json.dumps(message)))
            for table in tables:
                con.execute(f"CREATE TABLE {table} (k TEXT)")
        if live is None:
            con.close()
        else:
            live.addCleanup(con.close)
    return chat_dir


def snapshot(chat_dir: Path) -> tuple:
    """The chat directory's own mtime and each file's name and bytes, which a file written,
    created or removed, even one removed again, changes."""
    return (chat_dir.stat().st_mtime_ns,
            sorted((p.name, p.read_bytes()) for p in chat_dir.iterdir()))


class CursorCliTests(_Fixture):

    def setUp(self) -> None:
        super().setUp()
        self.chats = meter_cursor.cli_chats(self.root, {"HOME": str(self.root / "home")})

    def cli_reading(self, stub: Stub, **values) -> dict:
        """The selector's reading with no API key, so the CLI's surface is the one read."""
        return self.reading(stub, **{meter_cursor.KEY_ENV: None, **values})

    def test_the_store_is_found_where_the_cli_writes_it(self) -> None:
        """The CLI's own location rule. Mutants: a hard-coded path, `CURSOR_CONFIG_DIR` or
        `XDG_CONFIG_HOME` ignored or taken when blank, the workspace path hashed unnormalised
        (the trailing slash), or `realpath` (the symlink) where the CLI takes the path as
        given; the store looked for in `~/.cursor/projects/<slug>/`, the guess the story's
        notes made, where the CLI keeps transcripts and terminal output instead. The open is
        read-only: a plain `sqlite3.connect`, or a `mode=ro` open without `immutable=1`, of a
        closed WAL store or of one held open with its `-wal` and `-shm` changes the chat
        directory's bytes or mtime."""
        for repo, name in DEV_CHATS.items():
            self.assertEqual(meter_cursor.cli_chats(repo, {"HOME": "/h"}),
                             Path("/h/.cursor/chats", name))
        name = DEV_CHATS[DEV_REPO]
        for env, want in (({"XDG_CONFIG_HOME": "/x"}, "/x/cursor"),
                          ({"XDG_CONFIG_HOME": " "}, "/h/.cursor"),
                          ({"XDG_CONFIG_HOME": "/x", "CURSOR_CONFIG_DIR": "/c"}, "/c"),
                          ({"XDG_CONFIG_HOME": "/x", "CURSOR_CONFIG_DIR": " "}, "/x/cursor")):
            self.assertEqual(meter_cursor.cli_chats(Path(DEV_REPO), {"HOME": "/h", **env}),
                             Path(want, "chats", name), env)
        self.assertEqual(meter_cursor.cli_chats(DEV_REPO + "/", {"HOME": "/h"}).name, name)
        link = self.root / "link"
        link.symlink_to(self.root / "home")
        self.assertEqual(meter_cursor.cli_chats(link, {"HOME": "/h"}).name,
                         meter_cursor.cli_chats(str(link), {"HOME": "/h"}).name)
        self.assertNotEqual(meter_cursor.cli_chats(link, {"HOME": "/h"}).name,
                            meter_cursor.cli_chats(self.root / "home", {"HOME": "/h"}).name)

        stub = Stub(self)
        slug = os.path.abspath(self.root).strip("/").replace("/", "-")
        guessed = self.root / "home" / ".cursor" / "projects" / slug
        cli_store(guessed, "chat-run")
        got = self.cli_reading(stub)
        self.assertIn(f"no Cursor CLI chat store sits at {self.chats}", got["reason"])
        xdg = self.root / "xdg"
        cli_store(meter_cursor.cli_chats(self.root, {"XDG_CONFIG_HOME": str(xdg)}), "chat-run")
        got = self.cli_reading(stub, XDG_CONFIG_HOME=str(xdg))
        self.assertIn(f"its chat store for this workspace, {xdg / 'cursor' / 'chats'}",
                      got["reason"])

        closed = cli_store(self.chats, "chat-closed")
        live = cli_store(self.chats, "chat-live", live=self)
        self.assertEqual((closed / "store.db").read_bytes()[18:20], b"\x02\x02", "WAL mode")
        self.assertFalse((closed / "store.db-wal").exists())
        self.assertTrue((live / "store.db-wal").stat().st_size, "a -wal holding the tables")
        self.assertTrue((live / "store.db-shm").is_file())
        before = [snapshot(d) for d in (closed, live)]
        got = self.cli_reading(stub)
        self.assertIn("the Cursor CLI kept no usage record", got["reason"])
        self.assertEqual([snapshot(d) for d in (closed, live)], before, "never written")

    def test_no_persisted_usage_is_not_attributable(self) -> None:
        """AC2. Mutants: a store keeping no usage read as 0 tokens, or with a reason not saying
        the CLI kept no usage record; a print run's result line, usage and all, taken from the
        CLI's terminal or transcript files; a request made with no key; the store written to;
        the table check dropped or made a subset test, so a store with a usage table, or one
        that is not SQLite, reads as keeping none; the `-wal` ignored, so a chat held open
        before its first checkpoint reads as a store of unknown shape."""
        stub = Stub(self)
        got = self.cli_reading(stub)
        self.assertIsNone(got["tokens"], "the control: no store at all")
        self.assertIn(f"no Cursor CLI chat store sits at {self.chats}", got["reason"])

        # An interactive session left before its first prompt: the CLI's chat for this repo on
        # the development machine held a meta.json alone.
        cli_store(self.chats, "chat-idle", conversation=False)
        got = self.cli_reading(stub)
        self.assertIsNone(got["tokens"])
        self.assertIn(f"the Cursor CLI kept no usage record: its chat store for this "
                      f"workspace, {self.chats}, holds 1 chat and", got["reason"])
        self.assertIn(f"{meter_cursor.KEY_ENV} is not set", got["reason"])

        # A print run whose stdout has gone, though its result line sits in the files the CLI
        # keeps beside the store.
        db = cli_store(self.chats, "chat-run") / "store.db"
        project = self.root / "home" / ".cursor" / "projects" / os.path.abspath(
            self.root).strip("/").replace("/", "-")
        for rel in ("terminals/1.txt", "agent-transcripts/chat-run/chat-run.jsonl"):
            (project / rel).parent.mkdir(parents=True, exist_ok=True)
            (project / rel).write_text(PRINT_RESULT + "\n", encoding="utf-8")
        (db.parent / "stdout.jsonl").write_text(PRINT_RESULT + "\n", encoding="utf-8")
        before = sorted((p.name, p.read_bytes()) for p in db.parent.iterdir())
        got = self.cli_reading(stub)
        self.assertIsNone(got["tokens"], "never zero, never the scraped figure")
        self.assertIn("the Cursor CLI kept no usage record", got["reason"])
        self.assertIn("holds 2 chats and", got["reason"])
        self.assertEqual(sorted((p.name, p.read_bytes()) for p in db.parent.iterdir()), before)
        self.assertEqual(stub.requests, [], "no key, no request")

        # An interactive session still open and not yet checkpointed: its tables sit in its
        # -wal alone, which an immutable open of store.db does not see.
        live = cli_store(self.chats, "chat-live", live=self) / "store.db"
        con = sqlite3.connect(f"{live.as_uri()}?mode=ro&immutable=1", uri=True)
        self.addCleanup(con.close)
        self.assertEqual(con.execute("SELECT count(*) FROM sqlite_master").fetchone(), (0,))
        got = self.cli_reading(stub)
        self.assertIsNone(got["tokens"])
        self.assertIn("the Cursor CLI kept no usage record", got["reason"])
        self.assertIn("holds 3 chats and", got["reason"])

        cli_store(self.chats, "chat-other", tables=("usage",))
        bad = self.chats / "chat-other" / "store.db"
        for why in ("a further table", "not SQLite"):
            got = self.cli_reading(stub)
            self.assertIsNone(got["tokens"], why)
            self.assertIn(f"the Cursor CLI chat store {bad} does not hold exactly the tables "
                          f"blobs and meta", got["reason"], why)
            self.assertNotIn("kept no usage record", got["reason"], why)
            bad.write_bytes(b"not a database")

    def test_cloud_and_cli_surfaces_are_never_mixed(self) -> None:
        """AC3. Mutants: the CLI's reading added to the cloud's; the CLI store read, or
        preferred, when the key and agent id are set; a failed cloud call falling back to the
        CLI store; the cloud called with the key unset. A CLI reading carrying a figure stands
        in for one, since the store the CLI writes has none."""
        stub = Stub(self)
        cli_store(self.chats, "chat-run")
        cli = {"tokens": 999, token_meters.CACHE_READ: 1, "basis": "a CLI reading",
               "source": f"the Cursor CLI chat store {self.chats}", "includes_subagents": False}
        with mock.patch.object(self.reader, "read_cli", return_value=dict(cli)) as read_cli:
            both = self.reading(stub)
            self.assertEqual((both["tokens"], both[token_meters.CACHE_READ]),
                             (TOKENS, CACHE_READS), "the cloud reading alone")
            self.assertIn(AGENT, both["source"])
            stub.reply = answer(500, {"error": {"code": "internal_error"}})
            failed = self.reading(stub)
            self.assertIsNone(failed["tokens"], "a failed cloud call is not the CLI's figure")
            self.assertIn("it answered HTTP 500", failed["reason"])
            read_cli.assert_not_called()
            calls = len(stub.requests)
            alone = self.cli_reading(stub)
            self.assertEqual((alone["tokens"], alone[token_meters.CACHE_READ], alone["source"]),
                             (999, 1, cli["source"]), "the CLI reading alone")
            self.assertEqual(len(stub.requests), calls, "no cloud call without the key")
            read_cli.assert_called_once()
        got = self.cli_reading(stub)
        self.assertIsNone(got["tokens"])
        self.assertIn("the Cursor CLI kept no usage record", got["reason"])


HOOK = Path(__file__).resolve().parents[1] / "cursor_usage_hook.py"
REFERENCE = Path(__file__).resolve().parents[2] / "reference-sprint.md"


def response(n: int, inp, out, read, write, **over) -> dict:
    """An `afterAgentResponse` payload in the shape the CLI's 2026.10.22-27dcf5f build sends:
    its ids, model and text, and the four counts, a None one left out as the CLI leaves an
    undefined one out of the JSON. `inp` is the payload's `input_tokens`, which holds the
    response's cache reads and writes, so a response of that build has it at least their sum."""
    doc = {"conversation_id": "conv-1", "generation_id": f"gen-{n}", "model": "gpt-5",
           "text": f"RESPONSE-TEXT-{n}", "hook_event_name": "afterAgentResponse",
           "input_tokens": inp, "output_tokens": out, "cache_read_tokens": read,
           "cache_write_tokens": write, **over}
    return {k: v for k, v in doc.items() if v is not None}


class CursorHookLedgerTests(_Fixture):

    def setUp(self) -> None:
        super().setUp()
        (self.root / "sdlc-studio").mkdir()
        self.ledger = self.root / "sdlc-studio" / ".local" / "cursor-usage.jsonl"

    def hook(self, payload, root: Path | None = None, cwd: Path | None = None):
        """The hook as the CLI runs it: the payload on stdin, from the workspace's root, under
        the fixture's own environment rather than whatever the test process inherited."""
        raw = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
        named = ["--root", str(root)] if root else []
        return subprocess.run([sys.executable, str(HOOK), *named], cwd=cwd or self.root,
                              env=self.environment(None), input=raw, capture_output=True,
                              timeout=60, check=False)

    def cli_reading(self, root: Path | None = None) -> dict:
        with self.env(None, **{meter_cursor.KEY_ENV: None}):
            return run_state.session_tokens(root or self.root)

    def test_a_hook_fired_below_the_workspace_appends_to_the_workspace_ledger(self) -> None:
        """BG1236. Mutants: the `--root` default parsed as `Path(".")`, which `resolve_root`
        honours as a named root, or the anchor dropped; either way the subdirectory is read as
        the root, and the hook keeps no ledger and says so on stderr."""
        (self.root / "sdlc-studio" / "stories").mkdir()
        below = self.root / "deep" / "sub"
        below.mkdir(parents=True)
        done = self.hook(response(1, 54_000, 200, 50_000, 3_000), cwd=below)
        self.assertEqual((done.returncode, done.stdout, done.stderr), (0, b"", b""))
        self.assertEqual(len(self.ledger.read_text(encoding="utf-8").splitlines()), 1)
        self.assertFalse((below / "sdlc-studio").exists(), "a stray workspace beside the cwd")

    def test_the_ledger_is_read_as_measured(self) -> None:
        """AC1. Mutants: the ledger not read, so the reading stays None; a count dropped from
        the sum, the cache reads summed into `tokens`, the cache writes left out of it, one
        line read rather than every line; the priced figure formed from `tokens` alone or with
        the cache writes at the one-hour weight; a basis or source not naming the ledger; the
        hook and the meter on different paths; `--root` ignored; the response's text written
        to the ledger; a reading that is not cumulative, so the run window's delta between the
        open stamp and the close is not the window's lines summed. Round 2: `input_tokens`
        booked as uncached input, though it holds the cache reads and writes, or less them
        without the CLI's clamp at zero; a stamp of a Cursor reading keeping no price or
        components (`_priced_fields` for Claude alone), so the window's priced cost is None."""
        # One realistic response: 1,000 uncached input, 200 output, 50,000 cache reads and
        # 3,000 cache writes, which the payload carries as input_tokens 54,000.
        self.assertEqual(self.hook(response(0, 54_000, 200, 50_000, 3_000)).returncode, 0)
        got = self.cli_reading()
        one = {"input": 1_000, "output": 200, "cache_write_5m": 3_000, "cache_write_1h": 0,
               "cache_read": 50_000}
        self.assertEqual((got["tokens"], got["components"]), (4_200, one))
        # 1,000 + 200 x 5 + 3,000 x 1.25 + 50,000 x 0.1.
        self.assertEqual((got["priced"], run_state.price(one)), (10_750, 10_750))
        with self.env(None, **{meter_cursor.KEY_ENV: None}):
            run_state.open_run(self.root, batch=["BG0001"], goal="g")
        opening = run_state.read(self.root)[run_state.TOKEN_STAMPS][0]
        self.assertEqual((opening["priced"], opening["components"]), (10_750, one))
        # The run window: a realistic response, then one whose input_tokens falls short of its
        # cache counts, which the CLI's own usage line clamps at zero.
        elsewhere = self.root / "elsewhere"
        elsewhere.mkdir()
        done = [self.hook(response(1, 76_000, 300, 70_000, 4_000)),
                self.hook(response(2, 100, 50, 600, 400), root=self.root, cwd=elsewhere)]
        self.assertEqual([(p.returncode, p.stdout) for p in done], [(0, b"")] * 2)
        self.assertFalse((elsewhere / "sdlc-studio").exists(), "--root, not the cwd")
        text = self.ledger.read_text(encoding="utf-8")
        self.assertEqual(len(text.splitlines()), 3)
        self.assertNotIn("RESPONSE-TEXT", text)

        got = self.cli_reading()
        comps = {"input": 3_000, "output": 550, "cache_write_5m": 7_400, "cache_write_1h": 0,
                 "cache_read": 120_600}
        self.assertEqual((got["harness"], got["tokens"], got[token_meters.CACHE_READ]),
                         ("cursor", 10_950, 120_600))
        self.assertEqual(got["components"], comps)
        # 3,000 + 550 x 5 + 7,400 x 1.25 + 120,600 x 0.1.
        self.assertEqual(got["priced"], 27_060)
        self.assertEqual(got["priced"], run_state.price(comps))
        self.assertEqual((got["responses"], got["skipped"]), (3, 0))
        self.assertEqual(got["source"], f"the Cursor CLI hook ledger {self.ledger}")
        self.assertIn(f"afterAgentResponse hook ledger {self.ledger}, 3 responses summed",
                      got["basis"])
        self.assertNotIn("LOWER BOUND", got["basis"])

        with self.env(None, **{meter_cursor.KEY_ENV: None}):
            closing = run_state.stamp_tokens(self.root, "report")
        self.assertEqual((closing["tokens"], closing["priced"]), (10_950, 27_060))
        total = run_state.run_token_total(run_state.read(self.root))
        window = {"input": 2_000, "output": 350, "cache_write_5m": 4_400, "cache_write_1h": 0,
                  "cache_read": 70_600}
        self.assertEqual(total["tokens"], 2_000 + 350 + 4_400, "the window's lines alone")
        self.assertEqual(total["components"], window)
        # 2,000 + 350 x 5 + 4,400 x 1.25 + 70,600 x 0.1.
        self.assertEqual((total["priced"], total["priced_reason"]), (16_310, None))
        self.assertEqual([m["harness"] for m in total["meters"]], ["cursor"])
        self.assertIn(str(self.ledger), total["meters"][0]["basis"])

    def test_no_ledger_stays_unattributable_and_a_bad_line_is_counted(self) -> None:
        """AC2. Mutants: no ledger read as zero, or with a reason other than the store's as
        before; a malformed line raising, so the reading is lost; a malformed line not counted,
        counted as read, or partly summed (its other counts added); a negative, absent or
        truncated count read as a count; a ledger of malformed lines alone read as zero; the
        hook raising, or writing, on a payload that is not a JSON object, or creating a ledger
        in a root with no `sdlc-studio/`."""
        chats = meter_cursor.cli_chats(self.root, {"HOME": str(self.root / "home")})
        unset = (f"the cursor reader: {meter_cursor.KEY_ENV} is not set, so the Cursor cloud "
                 f"usage API is not called, and ")
        got = self.cli_reading()
        self.assertEqual((got["tokens"], got["reason"]), (None, (
            f"{unset}no Cursor CLI chat store sits at {chats}, so this run's tokens cannot be "
            f"read")))
        cli_store(chats, "chat-run")
        got = self.cli_reading()
        self.assertEqual((got["tokens"], got["reason"]), (None, (
            f"{unset}the Cursor CLI kept no usage record: its chat store for this workspace, "
            f"{chats}, holds 1 chat and records no tokens spent, and the usage a print run "
            f"reports on its stdout is not read, so this run's tokens cannot be read")))

        for bad in (b"not json", b"[1, 2]"):
            done = self.hook(bad)
            self.assertEqual((done.returncode, done.stdout), (0, b""), bad)
            self.assertIn(b"not a JSON object", done.stderr, bad)
        self.assertFalse(self.ledger.exists(), "nothing appended for a payload not an object")
        bare = self.root / "bare"
        bare.mkdir()
        done = self.hook(response(0, 1, 1, 1, 1), cwd=bare)
        self.assertEqual(done.returncode, 0)
        self.assertIn(b"holds no sdlc-studio/ directory", done.stderr)
        self.assertEqual(list(bare.iterdir()), [])

        self.hook(response(1, 54_000, 200, 50_000, 3_000))
        self.hook(response(2, 900_000, 900_000, 900_000, None))     # the CLI left one undefined
        self.hook(response(3, -5, 900_000, 900_000, 900_000))
        with self.ledger.open("ab") as fh:                           # a write cut short
            fh.write(b'{"input_tokens": 900000, "output_tok\n')
        self.hook(response(4, 76_000, 300, 70_000, 4_000))
        got = self.cli_reading()
        self.assertEqual((got["tokens"], got[token_meters.CACHE_READ]),
                         (3_000 + 500 + 7_000, 120_000), "the two good lines alone")
        self.assertEqual((got["responses"], got["skipped"]), (2, 3))
        self.assertIn("2 responses summed", got["basis"])
        self.assertIn("; 3 malformed lines skipped, so it is a LOWER BOUND", got["basis"])

        other = self.root / "other"
        (other / "sdlc-studio").mkdir(parents=True)
        self.hook(response(5, 1, 1, 1, None), root=other)
        got = self.cli_reading(other)
        ledger = other / "sdlc-studio" / ".local" / "cursor-usage.jsonl"
        self.assertIsNone(got["tokens"], "never zero")
        self.assertIn(f"the Cursor CLI hook ledger {ledger} holds no line that can be read "
                      f"(1 malformed line skipped)", got["reason"])

    def test_the_reference_names_the_hook_and_ledger(self) -> None:
        """AC3. Mutants: the hook, its `afterAgentResponse` entry, `.cursor/hooks.json` or the
        ledger's path left out of the paragraph that registers the hook, or named only
        elsewhere in the file; a ledger path in the reference that is not `LEDGER_REL`; a hook
        named that the skill does not ship; the BG1213 rule on `SDLC_STUDIO_CURSOR_API` left
        out of the paragraph naming the override."""
        paras = REFERENCE.read_text(encoding="utf-8").split("\n\n")
        hook = [p for p in paras if "cursor_usage_hook.py" in p]
        self.assertEqual(len(hook), 1, "one paragraph registers the hook")
        para = " ".join(hook[0].split())
        for want in (f"python3 <skill>/scripts/{HOOK.name}",
                     f"`{meter_cursor.HOOK_EVENT}` entry of the project's `.cursor/hooks.json`",
                     f"`{meter_cursor.LEDGER_REL.as_posix()}`"):
            self.assertIn(want, para)
        # BG1236: the hook resolves the workspace, so the page must not say it writes under
        # its working directory
        flat = " ".join(para.split())
        self.assertIn("under the workspace it resolves", flat)
        self.assertNotIn("under its working directory", flat)
        self.assertTrue(HOOK.is_file())
        override = [" ".join(p.split()) for p in paras if f"`{meter_cursor.API_ENV}`" in p]
        self.assertEqual(len(override), 1)
        self.assertIn(f"`{meter_cursor.API_ENV}` overrides the base URL, and must be https or "
                      f"http on a loopback IP address, else no request is made", override[0])


if __name__ == "__main__":
    unittest.main()
