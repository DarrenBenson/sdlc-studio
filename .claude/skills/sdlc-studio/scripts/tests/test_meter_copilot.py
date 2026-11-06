"""US0987 (CR0611): a Copilot CLI run records its token actual from the session's own events.

A Copilot CLI sprint wrote no Claude transcript, so its run published no figure.
`lib/meter_copilot.py` reads the events file the CLI keeps per session,
`$COPILOT_HOME/session-state/<id>/events.jsonl`, and every test here reaches it through the
shipped selector, `run_state.session_tokens`, against a store built in a temporary directory.

The fixtures are derived from real Copilot CLI 1.0.106 sessions on 2026-11-06: one trivial print
session, and one resumed once, whose second `session.shutdown` aggregate covered both calls.
They keep only the events and fields the reader uses, under synthetic session ids, with the
request and account identifiers dropped. The counts are the captures' own, except where a
test alters one so a mutant or a malformed value is seen.

Pinned here:

* `tokens` is the uncached input + output + cache write from the shutdown aggregate, where
  `inputTokens` already holds the cached tokens; cache reads are apart, reasoning is not
  added to output, the model is named, and a session recording another repo is never read (AC1);
* a live session sums its per-call records, and a resumed one reads its last aggregate plus the
  records after it, never the records the aggregate already folded (AC2);
* the running-total checkpoints are never added, and two models read as the mixed marker (AC3);
* `~/.copilot` is the default store, and a missing store, an empty session or a malformed value
  reads tokens None with the reason, never zero and never a quietly short total (AC4);
* `sprint.py plan --write` stamps a baseline naming copilot and the events file (AC5).

Run from the repo root:
    python3 -m pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_copilot.py
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/meter_copilot.py
from __future__ import annotations

import contextlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib import meter_copilot, run_state, token_meters  # noqa: E402

SPRINT = Path(__file__).resolve().parents[1] / "sprint.py"
MODEL = "claude-sonnet-5.5"
OTHER_MODEL = "gpt-5.5"
SESSION = "5d0c0987-0000-4000-8000-00000000a001"
#: Every variable the selection reads, scrubbed so the suite's own harness never reaches a test.
SCRUB = (token_meters.HARNESS_ENV, run_state.TRANSCRIPTS_ENV, meter_copilot.HOME_ENV,
         *(v for vs in token_meters.SIGNALS.values() for v in vs))

#: The resumed capture's two calls, as each `session.usage_record` carried them: `inputTokens`
#: is the uncached input (4) plus the cache read plus the cache write.
CALL_1 = {"model": MODEL, "inputTokens": 40_046, "outputTokens": 4, "cacheReadTokens": 0,
          "cacheWriteTokens": 40_042, "reasoningTokens": 0, "cacheTtlSeconds": 300}
CALL_2 = {"model": MODEL, "inputTokens": 40_096, "outputTokens": 4, "cacheReadTokens": 40_042,
          "cacheWriteTokens": 50, "reasoningTokens": 0, "cacheTtlSeconds": 300}
FIELDS = ("inputTokens", "outputTokens", "cacheReadTokens", "cacheWriteTokens", "reasoningTokens")


def aggregate(*calls: dict) -> dict:
    """The `modelMetrics.<model>.usage` the CLI folds `calls` into: their counts summed."""
    return {f: sum(c[f] for c in calls) for f in FIELDS}


def split(*calls: dict) -> tuple[int, int]:
    """(tokens, cache reads) of `calls`: uncached input + output + cache write, and reads."""
    reads = sum(c["cacheReadTokens"] for c in calls)
    writes = sum(c["cacheWriteTokens"] for c in calls)
    uncached = sum(c["inputTokens"] for c in calls) - reads - writes
    return uncached + sum(c["outputTokens"] for c in calls) + writes, reads


def start(root: Path | str, session: str = SESSION) -> dict:
    """The `session.start` the CLI writes first, recording the directory it ran in."""
    return {"type": "session.start", "data": {
        "sessionId": session, "version": 1, "producer": "copilot-agent",
        "copilotVersion": "1.0.106", "context": {"cwd": str(root), "gitRoot": str(root),
                                                 "branch": "main"}}}


def record(usage: dict, seq: int, session: str = SESSION) -> dict:
    return {"type": "session.usage_record", "data": {"usage": {
        **usage, "accounting": {"sourceSessionId": session, "sequence": seq}}}}


def checkpoint(models: dict, seq: int, session: str = SESSION) -> dict:
    """A `session.usage_checkpoint`: the session's running totals, never a spend of its own."""
    return {"type": "session.usage_checkpoint", "data": {
        "totalPremiumRequests": seq, "usageAccountingWatermarks": {session: seq},
        "accountingSnapshot": {"modelMetrics": {
            m: {"requests": {"count": seq}, "usage": u} for m, u in models.items()}}}}


def shutdown(models: dict, seq: int, session: str = SESSION) -> dict:
    """A `session.shutdown`: `modelMetrics` covers every call of the session so far."""
    return {"type": "session.shutdown", "data": {
        "shutdownType": "routine", "totalPremiumRequests": seq,
        "usageAccountingWatermarks": {session: seq} if seq else None,
        "currentModel": next(iter(models), MODEL),
        "modelMetrics": {m: {"requests": {"count": seq}, "usage": u} for m, u in models.items()}}}


RESUME = {"type": "session.resume", "data": {"context": {}}}


def write_lines(path: Path, lines: list[str], mtime: float | None = None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(f"{line}\n" for line in lines), encoding="utf-8")
    if mtime is not None:
        os.utime(path, (mtime, mtime))
    return path


class _Fixture(unittest.TestCase):

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(os.path.realpath(tmp.name))
        self.root = self.tmp / "repo"
        self.root.mkdir()
        (self.tmp / "home").mkdir()
        self.store = self.tmp / "copilot"

    def events(self, events: list[dict], session: str = SESSION, home: Path | None = None,
               mtime: float | None = None) -> Path:
        """Write `events` as session `session`'s events file under `home` (the store)."""
        path = (home or self.store) / "session-state" / session / "events.jsonl"
        return write_lines(path, [json.dumps(e) for e in events], mtime)

    def environment(self, **values) -> dict:
        env = {k: v for k, v in os.environ.items() if k not in SCRUB}
        env.update({"HOME": str(self.tmp / "home"),
                    run_state.TRANSCRIPTS_ENV: str(self.tmp / "home" / "none"),
                    token_meters.HARNESS_ENV: "copilot",
                    meter_copilot.HOME_ENV: str(self.store)})
        env.update(values)
        return {k: v for k, v in env.items() if v is not None}

    @contextlib.contextmanager
    def env(self, **values):
        """os.environ as `environment` gives it; a value of None drops that variable."""
        with mock.patch.dict(os.environ, clear=True):
            os.environ.update(self.environment(**values))
            yield

    def reading(self, **values) -> dict:
        with self.env(**values):
            return run_state.session_tokens(self.root)

    def assertSplit(self, got: dict, calls: tuple[dict, ...]) -> None:  # noqa: N802
        self.assertEqual((got.get("tokens"), got.get(token_meters.CACHE_READ)), split(*calls),
                         got.get("reason"))


class CopilotReaderTests(_Fixture):

    def test_shutdown_aggregate_counts_one_basis(self) -> None:
        """AC1. Mutants: reasoning added to output; cache reads counted in `tokens`;
        `inputTokens` taken as uncached input, so the cache write is counted twice; the per-call
        records read in place of the aggregate; another repo's newer session read; this repo's
        older session read in place of its latest."""
        # The capture's aggregate of both calls, its reasoning and output each raised by 3 from
        # the capture's 0 and 4, so a reader adding reasoning to output is seen. The per-call
        # records are trimmed out: the aggregate alone is what an ended session is read from.
        calls = (CALL_1, {**CALL_2, "outputTokens": 7, "reasoningTokens": 3})
        events = self.events([start(self.root), checkpoint({MODEL: aggregate(*calls)}, 2),
                              shutdown({MODEL: aggregate(*calls)}, 2)], mtime=1_000)
        other = self.tmp / "other-repo"
        self.events([start(other, "other"), record(CALL_1, 1, "other"),
                     shutdown({MODEL: aggregate(CALL_1, CALL_1)}, 2, "other")],
                    session="other", mtime=2_000)
        older = self.events([start(self.root, "older"), record(CALL_1, 1, "older")],
                            session="older", mtime=500)
        got = self.reading()
        self.assertEqual(got[token_meters.HARNESS], "copilot")
        self.assertSplit(got, calls)
        self.assertEqual((got["tokens"], got[token_meters.CACHE_READ]), (4 + 4 + 11 + 40_092,
                                                                          40_042))
        self.assertEqual(got["model"], MODEL)
        self.assertIn(str(events), got["source"])
        comps = got["components"]
        self.assertEqual((comps["input"], comps["output"], comps["cache_write_5m"],
                          comps["cache_read"]), (8, 11, 40_092, 40_042))
        self.assertEqual(got["priced"], run_state.price(comps))
        self.assertIs(got["includes_subagents"], False)
        # Another repo's session alone is never read, newest though it is.
        events.unlink()
        older.unlink()
        none = self.reading()
        self.assertIsNone(none["tokens"])
        self.assertIn(str(self.root), none["reason"])
        with self.env():
            self.assertIsNone(meter_copilot.store(self.root, os.environ))
            self.assertIsNotNone(meter_copilot.store(other, os.environ))

    def test_live_and_ended_sessions_are_never_double_counted(self) -> None:
        """AC2. Mutants: the records summed and the aggregate added for the same span; every
        shutdown summed, though each covers the session so far; the records after the last
        shutdown dropped. Each stage is the resumed capture's file as it stood then."""
        stages = [
            ([start(self.root), record(CALL_1, 1)], (CALL_1,), "live"),
            ([shutdown({MODEL: aggregate(CALL_1)}, 1)], (CALL_1,), "ended"),
            ([RESUME, record(CALL_2, 2)], (CALL_1, CALL_2), "live"),
            ([shutdown({MODEL: aggregate(CALL_1, CALL_2)}, 2)], (CALL_1, CALL_2), "ended"),
        ]
        so_far: list[dict] = []
        for added, calls, state in stages:
            so_far += added
            with self.subTest(events=[e["type"] for e in so_far]):
                self.events(so_far)
                got = self.reading()
                self.assertSplit(got, calls)
                self.assertEqual(got["ended"], state == "ended")
                self.assertEqual(got["model"], MODEL)
        # The resumed capture's figures: 8 uncached + 8 output + 40,092 written; 40,042 read.
        self.assertEqual((got["tokens"], got[token_meters.CACHE_READ]), (40_108, 40_042))

    def test_occupancy_is_not_spend_and_two_models_read_mixed(self) -> None:
        """AC3. Mutants: a checkpoint's running total added to the records it totals; the first
        model named in place of the mixed marker; one model's usage read and the other's
        dropped."""
        other = {**CALL_2, "model": OTHER_MODEL}
        live = [start(self.root), record(CALL_1, 1), checkpoint({MODEL: aggregate(CALL_1)}, 1),
                record(other, 2), checkpoint({MODEL: aggregate(CALL_1),
                                              OTHER_MODEL: aggregate(other)}, 2)]
        self.events(live)
        got = self.reading()
        self.assertSplit(got, (CALL_1, other))
        self.assertEqual(got["model"], run_state.SESSION_MODEL_MIXED)
        self.events([*live, shutdown({MODEL: aggregate(CALL_1),
                                      OTHER_MODEL: aggregate(other)}, 2)])
        got = self.reading()
        self.assertTrue(got["ended"])
        self.assertSplit(got, (CALL_1, other))
        self.assertEqual(got["model"], run_state.SESSION_MODEL_MIXED)

    def test_missing_or_malformed_store_is_not_attributable(self) -> None:
        """AC4. Mutants: the default store read from the process's own home, not `HOME`; a
        malformed record skipped so the total is quietly short; an empty session read as 0."""
        home_store = self.tmp / "home" / ".copilot"
        found = self.events([start(self.root), record(CALL_1, 1)], home=home_store)
        for unset in (None, "  "):
            with self.subTest(copilot_home=unset):
                got = self.reading(**{meter_copilot.HOME_ENV: unset})
                self.assertSplit(got, (CALL_1,))
                self.assertIn(str(found), got["source"])
        # The home is the one in the environment the selection read, not the process's own.
        with mock.patch.dict(os.environ, {"HOME": str(self.tmp / "elsewhere")}):
            got = meter_copilot.read(self.root, {"HOME": str(self.tmp / "home")})
        self.assertSplit(got, (CALL_1,))

        missing = self.tmp / "absent"
        got = self.reading(**{meter_copilot.HOME_ENV: str(missing)})
        self.assertIsNone(got["tokens"])
        self.assertIn(str(missing / "session-state"), got["reason"])

        cases = {
            "empty": ([start(self.root), shutdown({}, 0)], "records no usage"),
            "started only": ([start(self.root)], "records no usage"),
            "a count as text": ([start(self.root), record(CALL_1, 1),
                                 record({**CALL_2, "outputTokens": "4"}, 2)], "outputTokens"),
            "a negative count": ([start(self.root), record(CALL_1, 1),
                                  record({**CALL_2, "cacheWriteTokens": -1}, 2)],
                                 "cacheWriteTokens"),
            "a count as a bool": ([start(self.root), record({**CALL_1, "inputTokens": True}, 1)],
                                  "inputTokens"),
            "no usage object": ([start(self.root), record(CALL_1, 1),
                                 {"type": "session.usage_record", "data": {"usage": None}}],
                                "usage"),
            "input short of the cache": ([start(self.root),
                                          record({**CALL_2, "inputTokens": 40_000}, 1)],
                                         "inputTokens"),
            "an aggregate value": ([start(self.root), shutdown(
                {MODEL: {**aggregate(CALL_1), "cacheReadTokens": None}}, 1)], "cacheReadTokens"),
        }
        for name, (events, named) in cases.items():
            with self.subTest(case=name):
                path = self.events(events)
                got = self.reading()
                self.assertIsNone(got["tokens"], got)
                self.assertIn(named, got["reason"])
                self.assertIn(str(path), got["reason"])
        # A line that is not JSON may have been any event, a shutdown among them.
        path = self.events([start(self.root), record(CALL_1, 1)])
        with path.open("a", encoding="utf-8") as fh:
            fh.write('{"type": "session.usage_record", "data": {"usage": {"inputTok\n')
        got = self.reading()
        self.assertIsNone(got["tokens"])
        self.assertIn("line 3", got["reason"])


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


class CopilotLaneTests(_Fixture):

    def test_plan_write_stamps_a_copilot_baseline(self) -> None:
        """AC5. Mutant: the reader passing its unit tests while the plan path never reaches it
        (`open_run` stamping the Claude reading, or none), so the baseline names no copilot."""
        _bug(self.root)
        events = self.events([start(self.root), record(CALL_1, 1), record(CALL_2, 2)])
        proc = subprocess.run(
            [sys.executable, str(SPRINT), "plan", "--bugs", "Open", "--write", "--no-fetch",
             "--root", str(self.root)],
            env=self.environment(), capture_output=True, text=True, timeout=300, check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr[-2000:])
        base = run_state.read(self.root)[run_state.TOKEN_BASELINE]
        self.assertEqual(base[token_meters.HARNESS], "copilot")
        self.assertIn(str(events), base["source"])
        self.assertEqual((base["tokens"], base[token_meters.CACHE_READ]), split(CALL_1, CALL_2))
        self.assertEqual(base["priced"], run_state.price(base["components"]))


if __name__ == "__main__":
    unittest.main()
