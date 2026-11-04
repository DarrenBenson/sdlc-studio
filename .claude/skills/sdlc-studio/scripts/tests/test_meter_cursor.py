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
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

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
         meter_cursor.AGENT_ENV, meter_cursor.API_ENV,
         *(v for vs in token_meters.SIGNALS.values() for v in vs),
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
        """AC2. Mutants: the key or agent-id check dropped (a request goes out), the worker
        joined with no timeout (the dribbling stub holds it for seconds), the socket timeout
        dropped (the held worker outlives the deadline), a socket timeout read as anything but
        the deadline, an empty usage read as 0, or an HTTP error, a malformed field, a broken
        status line or an oversized answer passed on as a figure."""
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
                began = time.monotonic()
                got = self.reading(stub)
                self.assertLess(time.monotonic() - began, 2.0, reply.__name__)
                self.assertIsNone(got["tokens"])
                self.assertIn("did not answer within 0.3 seconds", got["reason"])
                if reply is hold:
                    self.assertTrue(worker_ends(2.0), "a held socket times out the worker too")
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


if __name__ == "__main__":
    unittest.main()
