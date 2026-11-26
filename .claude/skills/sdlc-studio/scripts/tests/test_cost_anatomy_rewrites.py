"""`sprint.py cost --anatomy` splits each role's cache writes into growth and re-writes after the
cache lifetime.

Every case runs over the harness store of `test_meter_reads_true`: the session's own transcript
and its subagents' `agent-<id>.jsonl` beside it, each record stamped as the harness stamps it. A
call's gap is the time since its transcript's previous call's first usage record; its 5-minute
writes are re-written after a gap longer than 5 minutes, its 1-hour writes after one longer than
60. The expected figures are formed here from the fixture's own writes, never read back from the
code under test.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/cost_anatomy.py
from __future__ import annotations

import contextlib
import io
import json
import sys
import unittest
import unittest.mock
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import test_meter_reads_true as meter  # noqa: E402 - the harness store and workspace

T0 = meter.T0
ROLES = ("orchestrator", "builder", "reviewer", "repair", "other")
SYNTHETIC = "<synthetic>"


def _five(n: int) -> dict:
    return meter._usage(10, 100, n, 0, 1_000)


def _hour(n: int) -> dict:
    return meter._usage(10, 100, 0, n, 1_000)


def _at(minutes: float, base: datetime = T0, ms: int = 0) -> str:
    """The harness's stamp `minutes` (and `ms` milliseconds) after `base`."""
    return (base + timedelta(minutes=minutes, milliseconds=ms)).isoformat(
        timespec="milliseconds").replace("+00:00", "Z")


def _line(msg_id: str | None, usage: dict, at: str | None, model: str = meter.MODEL) -> str:
    """One usage record as the harness writes it; `at` its stamp, or None for none."""
    msg = {"model": model, "role": "assistant", "content": [{"type": "text"}],
           "usage": dict(usage)}
    if msg_id is not None:
        msg["id"] = msg_id
    rec = {"type": "assistant", "cwd": "/work/repo", "message": msg}
    if at is not None:
        rec["timestamp"] = at
    return json.dumps(rec)


def _calls(calls, base: datetime = T0) -> list[str]:
    """One record per `(message id, usage, minute)`."""
    return [_line(m, u, _at(t, base)) for m, u, t in calls]


def _split(growth: int = 0, five: int = 0, hour: int = 0) -> dict:
    return {"growth": growth, "rewrite_5m": five, "rewrite_1h": hour}


#: The session AC1, AC2 and AC4 read: the main thread writes 1-hour cache and its one subagent,
#: the run's builder, 5-minute cache, as this project's transcripts do.
MAIN = (("msg_m1", _hour(2_000), 0), ("msg_m2", _hour(500), 6), ("msg_m3", _hour(9_000), 67))
BUILDER = (("msg_s1", _five(3_000), 1), ("msg_s2", _five(400), 2), ("msg_s3", _five(400), 3),
           ("msg_s4", _five(4_000), 9))


class CacheRewriteTests(meter._Case):
    def _ws(self, name: str, main, agents: dict | None = None):
        """A timed workspace whose main thread makes the `main` calls and whose subagent
        `agent-<id>` writes each of `agents`' lines."""
        ws = self._timed(name)
        ws.tx._append(ws.tx.main, _calls(main))
        for agent, lines in (agents or {}).items():
            ws.tx._append(ws.tx.subagents / f"agent-{agent}.jsonl", lines)
        return ws

    def _session(self):
        ws = self._ws("session", MAIN, {"s1": _calls(BUILDER)})
        ws.open()
        rc, out = ws.lane("return", "--units", "US0101", "--agent", "s1")
        self.assertEqual(0, rc, out)
        return ws

    def _run(self, ws, *argv: str) -> str:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = meter._live("sprint").main(["cost", "--anatomy", *argv, "--transcripts",
                                             str(ws.tx.dir), "--root", str(ws.root)])
        self.assertEqual(0, rc, out.getvalue() + err.getvalue())
        return out.getvalue()

    def _roles(self, ws, *argv: str) -> dict:
        doc = json.loads(self._run(ws, *argv, "--format", "json"))
        return {row["role"]: row for row in doc["roles"]}

    def test_a_five_minute_write_after_a_longer_gap_is_a_rewrite(self) -> None:
        """AC1. MUTANTS: the gap compared with >= (the exactly-5-minute write re-written); the
        5-minute lifetime another figure (3,600: the 6-minute gap reads growth; 301: the gap a
        millisecond over 5 minutes reads growth); a transcript's first call, which has no gap,
        booked as a re-write; the 5-minute write timed against the 1-hour lifetime."""
        got = self._roles(self._session(), "--session")
        self.assertEqual(_split(3_000 + 400 + 400, 4_000, 0), got["builder"]["cache_writes"])
        # a gap of exactly 5 minutes is not longer than the lifetime; one a millisecond over is
        e3 = _line("msg_e3", _five(500), _at(11, ms=1))
        ws = self._ws("exact-five", MAIN[:1], {"e1": _calls(
            (("msg_e1", _five(3_000), 1), ("msg_e2", _five(4_000), 6))) + [e3]})
        self.assertEqual(_split(7_000, 500, 0), self._roles(ws, "--session")["other"]["cache_writes"])

    def test_the_lifetime_comes_from_the_write_kind(self) -> None:
        """AC2. MUTANTS: one lifetime for both kinds (300 s: the 6-minute 500 re-written; 3,600
        s: AC1's 4,000 read as growth); the 1-hour lifetime another figure (3,601: the gap a
        millisecond over an hour reads growth); the 1-hour gap compared with >= (the exactly
        60-minute write re-written); one call timed once against one lifetime, which a call
        writing both kinds after a 6-minute gap shows."""
        got = self._roles(self._session(), "--session")
        self.assertEqual(_split(2_000 + 500, 0, 9_000), got["orchestrator"]["cache_writes"])
        ws = self._ws("exact-hour", (("msg_h1", _hour(2_000), 0), ("msg_h2", _hour(9_000), 60)))
        ws.tx._append(ws.tx.main, [_line("msg_h3", _hour(700), _at(120, ms=1))])
        self.assertEqual(_split(11_000, 0, 700),
                         self._roles(ws, "--session")["orchestrator"]["cache_writes"])
        both = meter._usage(10, 100, 300, 700, 1_000)
        ws = self._ws("both-kinds", (("msg_b1", _hour(2_000), 0), ("msg_b2", both, 6)))
        self.assertEqual(_split(2_000 + 700, 300, 0),
                         self._roles(ws, "--session")["orchestrator"]["cache_writes"])

    def test_a_window_call_measures_its_gap_from_the_call_before_it(self) -> None:
        """AC3. MUTANTS: the gaps measured over the window's records rather than the whole
        transcript (the minute-9 write, first in the window, read as growth); the calls booked
        over the whole transcript rather than the window (the minute-1 write counted)."""
        ws = self._timed("window")
        sdlc_md = meter._live("lib.sdlc_md")
        start = datetime.now(timezone.utc).replace(microsecond=0) - timedelta(minutes=30)
        base = start - timedelta(minutes=5)  # minute 0: the window opens at minute 5
        w1 = ws.tx.subagents / "agent-w1.jsonl"
        ws.tx._append(ws.tx.main, _calls((("msg_m_pre", _hour(1_000), 0),), base))
        ws.tx._append(w1, _calls((("msg_w1", _five(3_000), 1),), base))
        with unittest.mock.patch.object(sdlc_md, "now_iso8601",
                                        return_value=start.strftime("%Y-%m-%dT%H:%M:%SZ")):
            ws.open()
        ws.tx._append(ws.tx.main, _calls((("msg_m_in", _hour(500), 6),), base))
        ws.tx._append(w1, _calls((("msg_w2", _five(4_000), 9),), base))
        doc = json.loads(self._run(ws, "--format", "json"))
        self.assertFalse(doc["window"]["whole_session"], doc["window"])
        got = {row["role"]: row for row in doc["roles"]}
        self.assertEqual(4_000, got["other"]["components"]["cache_write_5m"])
        self.assertEqual(_split(0, 4_000, 0), got["other"]["cache_writes"])
        self.assertEqual(_split(500), got["orchestrator"]["cache_writes"])

    def test_the_printed_split_adds_up_and_an_untimed_record_reads_not_available(self) -> None:
        """AC4. MUTANTS: an untimed record ignored (other reads u2's 600, or u1's timed 900, as
        growth); a role's not available overwritten by a later timed agent of it (u2 sorts
        after u1); the text's not-available branch printing 0; the three figures printed in
        another order or under other labels; the block run on from the line above it; the split
        dropped from a role row."""
        ws = self._session()
        ws.tx._append(ws.tx.subagents / "agent-u1.jsonl",
                      [_line("msg_u1", _five(900), _at(1)), _line("msg_u2", _five(800), None)])
        ws.tx._append(ws.tx.subagents / "agent-u2.jsonl", [_line("msg_u3", _five(600), _at(2))])
        got = self._roles(ws, "--session")
        expected = {"orchestrator": (2_500, 0, 9_000), "builder": (3_800, 4_000, 0),
                    "reviewer": (0, 0, 0), "repair": (0, 0, 0)}
        for role, figures in expected.items():
            split, comps = got[role]["cache_writes"], got[role]["components"]
            self.assertEqual(_split(*figures), split, role)
            self.assertEqual(comps["cache_write_5m"] + comps["cache_write_1h"],
                             sum(split.values()), role)
        self.assertEqual(900 + 800 + 600, got["other"]["components"]["cache_write_5m"])
        self.assertIsNone(got["other"]["cache_writes"])
        lines = self._run(ws, "--session").splitlines()
        head = next(n for n, ln in enumerate(lines) if ln.startswith("Cache writes by role"))
        self.assertEqual("", lines[head - 1], "the block is not set off from the table's lines")
        for role, (g, five, hour) in expected.items():
            line = (f"  {role}: {g:,} growth, {five:,} re-written after 5-minute expiry, "
                    f"{hour:,} re-written after 1-hour expiry")
            self.assertIn(line, lines[head:])
        self.assertIn("  other: not available", lines[head:])
        self.assertEqual([], [ln for ln in lines if ln.startswith("  other:") and "growth" in ln])

    def test_each_gap_runs_from_the_previous_call_in_file_order(self) -> None:
        """MUTANTS: the previous call's moment taken from its latest record (p1's repeat 30 s
        later puts p2 inside 5 minutes); the calls ordered by time rather than file order, or a
        negative gap read as its size (o2 re-written); a synthetic record ending a gap (y2 read
        as growth); a message shared by two transcripts left out of the second one's gaps (z2
        re-written) or timed there rather than on the transcript it is booked to."""
        p = [_line("msg_p1", _five(3_000), _at(0)), _line("msg_p1", _five(3_000), _at(0.5)),
             _line("msg_p2", _five(4_000), _at(5, ms=10_000))]
        o = _calls((("msg_o1", _five(3_000), 10), ("msg_o2", _five(400), 2),
                    ("msg_o3", _five(600), 12)))
        y = [_line("msg_y1", _five(3_000), _at(1)),
             _line("msg_y_syn", meter._usage(0, 0, 0, 0, 0), _at(4), model=SYNTHETIC),
             _line("msg_y_bare", meter._usage(0, 0, 0, 0, 0), None, model=SYNTHETIC),
             _line("msg_y2", _five(4_000), _at(7))]
        for name, lines, split in (("first-record", p, _split(3_000, 4_000)),
                                   ("file-order", o, _split(3_000 + 400, 600)),
                                   ("synthetic", y, _split(3_000, 4_000))):
            ws = self._ws(name, MAIN[:1], {"x1": lines})
            self.assertEqual(split, self._roles(ws, "--session")["other"]["cache_writes"], name)
        # msg_sh is booked to the main thread, where it follows m1 by 10 minutes; on agent-z1 it
        # still sits between z1 and z2, 4 minutes from each
        ws = self._ws("shared", (("msg_m1", _hour(2_000), 0), ("msg_sh", _five(1_000), 10)),
                      {"z1": _calls((("msg_z1", _five(500), 6), ("msg_sh", _five(1_000), 10),
                                     ("msg_z2", _five(700), 14)))})
        got = self._roles(ws, "--session")
        self.assertEqual(_split(2_000, 1_000, 0), got["orchestrator"]["cache_writes"])
        self.assertEqual(_split(500 + 700), got["other"]["cache_writes"])
        self.assertEqual(1_200, got["other"]["components"]["cache_write_5m"])

    def test_an_unmeasurable_record_reads_not_available(self) -> None:
        """MUTANTS: a timestamp present but unparseable read as growth or skipped; a record with
        no message id measured as a call; a harness reading with no per-call record split as
        zeros (its other row's writes are not 0); the text printing figures for a null split."""
        for name, bad in (("unparseable", _line("msg_q2", _five(800), "not a time")),
                          ("naive", _line("msg_q2", _five(800), "2026-10-02T09:03:00")),
                          ("id-less", _line(None, _five(800), _at(3)))):
            ws = self._ws(name, MAIN[:1], {"q1": [_line("msg_q1", _five(900), _at(1)), bad]})
            got = self._roles(ws, "--session")
            self.assertIsNone(got["other"]["cache_writes"], name)
            self.assertEqual(_split(2_000), got["orchestrator"]["cache_writes"], name)
        anatomy = meter._live("lib.cost_anatomy")
        got = anatomy.from_reading({"harness": "cursor", "components": meter._sum(meter.MAIN_1)})
        self.assertEqual({role: None for role in ROLES},
                         {row["role"]: row["cache_writes"] for row in got["roles"]})
        lines = anatomy.render(got).splitlines()
        for role in ROLES:
            self.assertIn(f"  {role}: not available", lines)

    def test_a_call_straddling_the_window_start_is_timed_from_its_first_record(self) -> None:
        """MUTANTS: a call whose first record falls before the window dropped from the split
        while its in-window repeat is booked (the split no longer adds up to its components);
        the call timed from its record inside the window (5 minutes 10 seconds after x1, a
        re-write) rather than from its first record (4 minutes 50 seconds, growth)."""
        ws = self._timed("straddle")
        sdlc_md = meter._live("lib.sdlc_md")
        start = datetime.now(timezone.utc).replace(microsecond=0) - timedelta(minutes=30)
        base = start - timedelta(minutes=6)  # minute 0: the window opens at minute 6
        x1 = ws.tx.subagents / "agent-x1.jsonl"
        ws.tx._append(ws.tx.main, _calls((("msg_m_pre", _hour(1_000), 0),), base))
        ws.tx._append(x1, [_line("msg_x1", _five(3_000), _at(1, base)),
                           _line("msg_x2", _five(4_000), _at(5, base, ms=50_000))])
        with unittest.mock.patch.object(sdlc_md, "now_iso8601",
                                        return_value=start.strftime("%Y-%m-%dT%H:%M:%SZ")):
            ws.open()
        ws.tx._append(x1, [_line("msg_x2", _five(4_000), _at(6, base, ms=10_000))])
        ws.tx._append(ws.tx.main, _calls((("msg_m_in", _hour(500), 7),), base))
        got = self._roles(ws)
        self.assertEqual(4_000, got["other"]["components"]["cache_write_5m"])
        self.assertEqual(_split(4_000), got["other"]["cache_writes"])


if __name__ == "__main__":
    unittest.main()
