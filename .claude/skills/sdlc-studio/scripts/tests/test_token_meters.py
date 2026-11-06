"""US0986 (CR0611): the token meter reads the store of the harness that is running, chosen by
`SDLC_STUDIO_HARNESS` or the environment, and never forms a reading from two.

A Cursor cloud run once stamped no baseline and published no token figure, because the only
meter was the Claude Code transcript. The fix is a reader per harness, chosen for the process
that is running, and the rule that a leftover store of another harness is never booked onto it.

Pinned here:

* Claude's reading is the transcript reading it always was, under an explicit choice, a
  signal or no selection at all, and a malformed record still refuses it (AC1);
* a chosen harness is the only one read: no reader, or a reader with nothing to report, is
  tokens None naming it, and the Claude transcript is never opened (AC2);
* exactly one signal chooses, over any store on disk; two signals, or two stores and no
  signal, name every candidate and read nothing (AC3);
* every reading and every stamp names its harness and carries cache reads apart from `tokens`,
  and a run total never pairs readings of two harnesses (AC4);
* the close's CLI path inherits the selection through `retro.harness_tokens` (AC5).

Each harness other than Claude is stubbed by a module placed at `lib.meter_<harness>` in
`sys.modules`, or forced absent by a None there, so these tests hold whichever readers are
installed.

Run from the repo root:
    python3 -m pytest .claude/skills/sdlc-studio/scripts/tests/test_token_meters.py
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/token_meters.py
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib import run_state, token_meters  # noqa: E402
import retro  # noqa: E402

#: Every variable the selection reads, scrubbed from each test's environment so the harness the
#: suite itself runs under never chooses for it.
SCRUB = ("STUB_CURSOR_RUN_ID", run_state.TRANSCRIPTS_ENV, *token_meters.selection_variables())
#: Two messages: tokens 1,000 + 200 + 3,000 + 500 + 100 = 4,800, and 57,000 cache reads beside.
USAGES = ({"input_tokens": 1_000, "output_tokens": 200, "cache_creation_input_tokens": 3_000,
           "cache_read_input_tokens": 50_000},
          {"input_tokens": 500, "output_tokens": 100, "cache_read_input_tokens": 7_000})
TOKENS, CACHE_READS = 4_800, 57_000
OTHERS = (token_meters.CURSOR, token_meters.COPILOT, token_meters.OPENCODE, token_meters.CODEX)


def stub(reading=None, store=None, signals=None, raises=None) -> types.ModuleType:
    """A reader module: `read` returns `reading` (or raises `raises`), `store` returns `store`,
    and each call is logged on `calls`."""
    mod = types.ModuleType("stub_meter")
    mod.calls = []

    def read(repo_root, env):
        mod.calls.append("read")
        if raises is not None:
            raise raises
        return reading

    mod.read = read
    if store is not None:
        def probe(repo_root, env):
            mod.calls.append("store")
            if isinstance(store, Exception):
                raise store
            return store
        mod.store = probe
    if signals is not None:
        mod.SIGNALS = signals
    return mod


def cursor_reading(**over) -> dict:
    """A well-formed reading as a Cursor reader would return it."""
    return {"tokens": 900, "cache_read": 4_000, "source": "cursor agent bc-1",
            "basis": "cursor usage: input + output + cache write", "includes_subagents": False,
            "model": "m", **over}


def installed(**readers) -> mock._patch:
    """`lib.meter_<harness>` set to each given module, or None for "not installed"."""
    return mock.patch.dict(sys.modules, {f"lib.meter_{h}": m for h, m in readers.items()})


class _Fixture(unittest.TestCase):
    """A repo, a Claude transcript of `USAGES` and a scrubbed environment."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.transcripts = self.root / "transcripts"
        self.transcripts.mkdir()
        self.home = self.root / "home"
        self.home.mkdir()
        self.transcript = self._write("s1.jsonl", *USAGES)

    def _write(self, name: str, *usages: dict, raw: str = "") -> Path:
        p = self.transcripts / name
        p.write_text("".join(json.dumps({"message": {"id": f"m{i}", "usage": u}}) + "\n"
                             for i, u in enumerate(usages)) + raw, encoding="utf-8")
        return p

    @contextlib.contextmanager
    def env(self, transcripts: Path | None = None, **values: str):
        """The environment for one reading: no harness variable but `values`, HOME in the
        fixture, and the Claude transcripts at `transcripts` (the fixture's by default)."""
        with mock.patch.dict(os.environ):
            for v in SCRUB:
                os.environ.pop(v, None)
            os.environ.update({"HOME": str(self.home), "XDG_DATA_HOME": str(self.home),
                               run_state.TRANSCRIPTS_ENV: str(transcripts or self.transcripts),
                               **values})
            yield

    @contextlib.contextmanager
    def claude_spy(self):
        """Spies on every way the Claude store is reached: its reader, its transcript read and
        its directory listing."""
        with mock.patch.object(run_state, "claude_tokens", wraps=run_state.claude_tokens) as rd, \
                mock.patch.object(run_state, "_collect", wraps=run_state._collect) as col, \
                mock.patch.object(run_state, "_newest_transcript",
                                  wraps=run_state._newest_transcript) as ls:
            yield types.SimpleNamespace(read=rd, collect=col, listing=ls)

    def assert_claude_untouched(self, spy) -> None:
        self.assertFalse(spy.read.called, "the Claude reader was consulted")
        self.assertFalse(spy.collect.called, "the Claude transcript was opened")


class HarnessSelectionTests(_Fixture):

    def test_claude_reading_is_unchanged(self) -> None:
        """AC1. Mutants: the dispatcher summing the transcript itself with cache reads counted
        (61,800), or a malformed record skipped so a short total is read."""
        with self.env():
            expected = run_state.claude_tokens(self.root)
        self.assertEqual((expected["tokens"], expected["cache_read"]), (TOKENS, CACHE_READS))
        self.assertIn("MAIN THREAD only", expected["basis"])
        for values in ({"SDLC_STUDIO_HARNESS": "claude"}, {"SDLC_STUDIO_HARNESS": " Claude "},
                       {"CLAUDECODE": "1"}, {}):
            with self.subTest(values=values), self.env(**values):
                got = run_state.session_tokens(self.root)
                self.assertEqual(got["tokens"], TOKENS)
                self.assertEqual(got[token_meters.HARNESS], token_meters.CLAUDE)
                self.assertEqual({k: v for k, v in got.items()
                                  if k not in (token_meters.HARNESS, "selected_by")}, expected,
                                 "the reading is the Claude reader's, field for field")
        self._write("s1.jsonl", *USAGES, raw=json.dumps(
            {"message": {"id": "m9", "usage": {"input_tokens": "lots"}}}) + "\n")
        with self.env():
            refused = run_state.claude_tokens(self.root)
        self.assertIsNone(refused["tokens"])
        self.assertIn("malformed usage record", refused["reason"])
        for values in ({"SDLC_STUDIO_HARNESS": "claude"}, {"CLAUDECODE": "1"}, {}):
            with self.subTest(malformed=values), self.env(**values):
                got = run_state.session_tokens(self.root)
                self.assertIsNone(got["tokens"])
                self.assertEqual(got["reason"], refused["reason"],
                                 "Claude's reason is passed on as written")

    def test_a_chosen_harness_never_reads_another_store(self) -> None:
        """AC2. Mutant: falling back to the Claude transcript when the chosen reader is absent
        or returns nothing, with CLAUDECODE set and the transcript readable beside it."""
        for h in OTHERS:
            with self.subTest(absent=h), installed(**{h: None}), \
                    self.env(SDLC_STUDIO_HARNESS=h, CLAUDECODE="1"), self.claude_spy() as spy:
                got = run_state.session_tokens(self.root)
                self.assertIsNone(got["tokens"], "no reader is no reading, never zero")
                self.assertEqual(got[token_meters.HARNESS], h)
                self.assertIn(f"no {h} token reader is installed", got["reason"])
                self.assert_claude_untouched(spy)
                self.assertFalse(spy.listing.called, "a choice by name probes no store")
            empty = stub({"tokens": None, "reason": "no usage is stored for this run yet"})
            with self.subTest(empty=h), installed(**{h: empty}), \
                    self.env(SDLC_STUDIO_HARNESS=h, CLAUDECODE="1"), self.claude_spy() as spy:
                got = run_state.session_tokens(self.root)
                self.assertIsNone(got["tokens"])
                self.assertEqual(got["reason"],
                                 f"the {h} reader: no usage is stored for this run yet")
                self.assertEqual(empty.calls, ["read"])
                self.assert_claude_untouched(spy)
            full = stub(cursor_reading())
            with self.subTest(read=h), installed(**{h: full}), \
                    self.env(SDLC_STUDIO_HARNESS=h.upper()), self.claude_spy() as spy:
                got = run_state.session_tokens(self.root)
                self.assertEqual((got["tokens"], got[token_meters.HARNESS]), (900, h))
                self.assertEqual(got["selected_by"], token_meters.HARNESS_ENV)
                self.assert_claude_untouched(spy)

    def test_two_unselected_harnesses_name_the_candidates(self) -> None:
        """AC3. Mutants: a fixed precedence picking the first signalled or first stored
        harness, a store on disk outranking a signal, or the two readings added."""
        cursor = stub(cursor_reading(), signals=("STUB_CURSOR_RUN_ID",))
        with installed(cursor=cursor):
            named = token_meters.selection_variables()
        self.assertEqual(named[:2], [token_meters.HARNESS_ENV, "CLAUDECODE"])
        for v in ("CURSOR_AGENT", "STUB_CURSOR_RUN_ID", "COPILOT_HOME", "OPENCODE", "OPENCODE_DB",
                  "CODEX_THREAD_ID"):
            self.assertIn(v, named, "a test's scrub must clear every selection variable")
        for values in ({"CURSOR_AGENT": "1"}, {"STUB_CURSOR_RUN_ID": "bc-1"}):
            with self.subTest(signal=values), installed(cursor=cursor), self.env(**values), \
                    self.claude_spy() as spy:
                got = run_state.session_tokens(self.root)
                self.assertEqual((got["tokens"], got[token_meters.HARNESS]), (900, "cursor"),
                                 "one signal chooses over the Claude store on disk")
                self.assertIn(next(iter(values)), got["selected_by"])
                self.assert_claude_untouched(spy)
        with self.env(CURSOR_AGENT=""):
            self.assertEqual(run_state.session_tokens(self.root)["tokens"], TOKENS,
                             "an empty variable signals nothing")
        with installed(copilot=None, opencode=None), self.env(OPENCODE_DB="/x/opencode.db"):
            got = run_state.session_tokens(self.root)
            self.assertEqual((got["tokens"], got[token_meters.HARNESS]), (None, "opencode"))
        pairs = ({"CLAUDECODE": "1", "CURSOR_AGENT": "1"},
                 {"COPILOT_HOME": "/x/copilot", "OPENCODE": "1"},
                 {"CLAUDECODE": "1", "OPENCODE": "1"})
        for values in pairs:
            both = stub(cursor_reading())
            with self.subTest(signals=values), installed(cursor=both, copilot=both,
                                                         opencode=both), \
                    self.env(**values), self.claude_spy() as spy:
                got = run_state.session_tokens(self.root)
                self.assertIsNone(got["tokens"], "no total is formed")
                self.assertIsNone(got[token_meters.HARNESS])
                named = [h for h in token_meters.HARNESSES
                         if any(v in values for v in token_meters.SIGNALS[h])]
                self.assertEqual(got["candidates"], named)
                for h in named:
                    self.assertIn(h, got["reason"])
                for v in values:
                    self.assertIn(v, got["reason"])
                self.assertNotIn("read", both.calls)
                self.assert_claude_untouched(spy)
        stored = stub(cursor_reading(), store="/x/cursor/projects/repo")
        with installed(cursor=stored), self.env(), self.claude_spy() as spy:
            got = run_state.session_tokens(self.root)
        self.assertIsNone(got["tokens"])
        self.assertEqual(got["candidates"], ["claude", "cursor"])
        self.assertIn(str(self.transcripts), got["reason"])
        self.assertIn("/x/cursor/projects/repo", got["reason"])
        self.assertEqual(stored.calls, ["store"], "a candidate's reader is never read")
        self.assert_claude_untouched(spy)
        with installed(cursor=stub(cursor_reading(), store="/x/c")), \
                self.env(transcripts=self.root / "none"):
            got = run_state.session_tokens(self.root)
        self.assertEqual((got["tokens"], got[token_meters.HARNESS]), (900, "cursor"),
                         "the only store present chooses")
        self.assertIn("/x/c", got["selected_by"])
        with installed(cursor=stub(cursor_reading(), store=OSError("denied"))), self.env():
            got = run_state.session_tokens(self.root)
        self.assertEqual(got["candidates"], ["claude", "cursor"],
                         "a store that cannot be probed may be present")
        self.assertIn("could not be probed (OSError)", got["reason"])

    def test_readings_and_stamps_name_the_harness(self) -> None:
        """AC4. Mutants: a stamp without its harness, cache reads folded into `tokens`, a run
        total pairing readings by source alone, or a legacy baseline folded into another
        harness's session of the same source."""
        with self.env(SDLC_STUDIO_HARNESS="claude"):
            got = run_state.session_tokens(self.root)
            run_state.open_run(self.root, batch=["BG0001"], goal="g")
            stamped = run_state.stamp_tokens(self.root, "report")
        state = run_state.read(self.root)
        rows = [state[run_state.TOKEN_BASELINE], *state[run_state.TOKEN_STAMPS], stamped]
        for row in [got, *rows]:
            self.assertEqual(row[token_meters.HARNESS], "claude")
            self.assertEqual((row["tokens"], row[token_meters.CACHE_READ]), (TOKENS, CACHE_READS))
        other = self.root / "other"
        other.mkdir()
        with installed(cursor=stub(cursor_reading())), self.env(SDLC_STUDIO_HARNESS="cursor"):
            run_state.open_run(other, batch=["BG0001"], goal="g")
            stamped = run_state.stamp_tokens(other, "report")
        state = run_state.read(other)
        rows = [state[run_state.TOKEN_BASELINE], *state[run_state.TOKEN_STAMPS], stamped]
        for row in rows:
            self.assertEqual(row[token_meters.HARNESS], "cursor")
            self.assertEqual((row["tokens"], row[token_meters.CACHE_READ], row["source"]),
                             (900, 4_000, "cursor agent bc-1"))

        def at(n: int, **row) -> dict:
            return {"at": f"2026-11-04T10:0{n}:00Z", "source": "S", **row}
        mixed = {run_state.TOKEN_STAMPS: [at(1, tokens=100, kind="open", harness="claude"),
                                          at(2, tokens=500, kind="report", harness="cursor")]}
        total = run_state.run_token_total(mixed)
        self.assertIsNone(total["tokens"], "a claude and a cursor reading of one source")
        self.assertEqual(total["uncovered"], ["S", "S (cursor)"])
        legacy = {run_state.TOKEN_STAMPS: [at(1, tokens=100, kind="open"),
                                           at(2, tokens=500, kind="report", harness="claude")]}
        self.assertEqual(run_state.run_token_total(legacy)["tokens"], 400,
                         "a stamp naming no harness is Claude's, and pairs with Claude's")
        # The legacy baseline folds only into its own harness's session of the same source.
        for named in ({"harness": "claude"}, {}):
            folded = {run_state.TOKEN_BASELINE: at(1, tokens=100, **named),
                      run_state.TOKEN_STAMPS: [at(2, tokens=500, kind="report",
                                                  harness="cursor")]}
            self.assertIsNone(run_state.run_token_total(folded)["tokens"],
                              f"a Claude legacy baseline {named} folded into a Cursor session")
        folded[run_state.TOKEN_STAMPS][0]["harness"] = "claude"
        self.assertEqual(run_state.run_token_total(folded)["tokens"], 400,
                         "a Claude legacy baseline folds into Claude's session of its source")
        base = {run_state.TOKEN_BASELINE: at(1, tokens=100, harness="claude")}
        self.assertIsNone(run_state.run_token_total(
            base, current=at(2, tokens=500, harness="cursor"))["tokens"])
        self.assertEqual(run_state.run_token_total(
            base, current=at(2, tokens=500, harness="claude"))["tokens"], 400)

    def test_a_harness_name_is_matched_loosely_and_an_unknown_one_reads_nothing(self) -> None:
        """Mutants: an unknown name falling through to detection (the Claude reading), a blank
        one refused, or the default choosing anything but Claude's own reason."""
        with self.env(SDLC_STUDIO_HARNESS="gemini", CLAUDECODE="1"), self.claude_spy() as spy:
            got = run_state.session_tokens(self.root)
        self.assertIsNone(got["tokens"])
        self.assertIn("'gemini'", got["reason"])
        self.assertIn("claude, cursor, copilot, opencode, codex", got["reason"])
        self.assert_claude_untouched(spy)
        with self.env(SDLC_STUDIO_HARNESS="  "):
            self.assertEqual(run_state.session_tokens(self.root)["tokens"], TOKENS)
        empty = self.root / "empty"
        empty.mkdir()
        with self.env(transcripts=empty):
            got = run_state.session_tokens(self.root)
            own = run_state.claude_tokens(self.root)
        self.assertEqual((got[token_meters.HARNESS], got["reason"]), ("claude", own["reason"]))
        self.assertTrue(got["selected_by"].startswith("the default"))

    def test_a_broken_reader_is_reported_by_its_type_never_its_message(self) -> None:
        """Mutants: a reader's exception propagating, its message (which may carry a key)
        echoed, or a reader that fails to load read as one not installed."""
        secret = RuntimeError("Authorization: Bearer sk-secret")
        with installed(cursor=stub(raises=secret)), self.env(SDLC_STUDIO_HARNESS="cursor"):
            got = run_state.session_tokens(self.root)
        self.assertIsNone(got["tokens"])
        self.assertIn("raised RuntimeError", got["reason"])
        self.assertNotIn("sk-secret", json.dumps(got))

        def broken(h: str):
            if h == "cursor":
                raise SyntaxError("bad reader")
            return None
        with mock.patch.object(token_meters, "load_reader", side_effect=broken):
            with self.env(SDLC_STUDIO_HARNESS="cursor"):
                got = run_state.session_tokens(self.root)
            self.assertIn("could not be loaded (SyntaxError)", got["reason"])
            with self.env():
                got = run_state.session_tokens(self.root)
            self.assertEqual(got["candidates"], ["claude", "cursor"])
        with mock.patch.object(token_meters.importlib, "import_module",
                               side_effect=ModuleNotFoundError("x", name="requests")):
            with self.assertRaises(ModuleNotFoundError):
                token_meters.load_reader("cursor")
        with installed(cursor=None):
            self.assertIsNone(token_meters.load_reader("cursor"))

    def test_a_reading_that_breaks_the_contract_is_refused(self) -> None:
        """Mutant: any one check of `_fault` dropped, so a reading with no count, no cache-read
        figure, no source, no basis or no subagent flag reaches a stamp."""
        bad = ({"tokens": -1}, {"tokens": True}, {"tokens": "900"}, {"tokens": 900.0},
               {"cache_read": -1}, {"cache_read": True}, {"source": ""}, {"basis": "  "},
               {"includes_subagents": "no"})
        cases = [cursor_reading(**b) for b in bad]
        cases += [{k: v for k, v in cursor_reading().items() if k != key}
                  for key in ("cache_read", "source", "basis", "includes_subagents")]
        for reading in [*cases, ["not", "a", "dict"]]:
            with self.subTest(reading=reading), installed(cursor=stub(reading)), \
                    self.env(SDLC_STUDIO_HARNESS="cursor"):
                got = run_state.session_tokens(self.root)
                self.assertIsNone(got["tokens"])
                self.assertIn("the cursor reader returned", got["reason"])
        for good in (cursor_reading(), cursor_reading(cache_read=None), cursor_reading(tokens=0)):
            with self.subTest(good=good), installed(cursor=stub(good)), \
                    self.env(SDLC_STUDIO_HARNESS="cursor"):
                self.assertEqual(run_state.session_tokens(self.root)["tokens"], good["tokens"])


RETRO = """# RETRO-9002: a measured sprint

> **Date:** 2026-11-04
> **Batch:** BG0001, BG0002
> **Goal:** close the loop

## Delivered
- BG0001 - fixed it
## What went well
- it was measured
## What was hard / what stalled
- nothing
## Lessons
- measure the units
## Actions raised
| Finding | Disposition |
| --- | --- |
| nothing to raise | declined: clean sprint |
"""


class HarnessLaneTests(_Fixture):

    def test_accuracy_names_the_harness_it_could_not_read(self) -> None:
        """AC5. Mutant: `retro.harness_tokens` bound to the Claude reader rather than the
        dispatcher, so the close books the Claude transcript's growth onto an OpenCode run."""
        for d in ("retros", "bugs", ".local"):
            (self.root / "sdlc-studio" / d).mkdir(parents=True)
        (self.root / "sdlc-studio" / "retros" / "RETRO9002-t.md").write_text(RETRO)
        for num, pts in (("0001", 3), ("0002", 5)):
            (self.root / "sdlc-studio" / "bugs" / f"BG{num}-a.md").write_text(
                f"# BG{num}: a bug\n\n> **Status:** Fixed\n> **Severity:** Low\n"
                f"> **Points:** {pts}\n")
        with self.env():
            run_state.open_run(self.root, batch=["BG0001", "BG0002"], goal="a goal")
        self.assertEqual(run_state.read(self.root)[run_state.TOKEN_BASELINE]["tokens"], TOKENS)
        self._write("s1.jsonl", *USAGES, {"input_tokens": 70_000})   # the meter runs on
        buf = io.StringIO()
        with self.env(SDLC_STUDIO_HARNESS="opencode"), self.claude_spy() as spy, \
                mock.patch.object(sys, "argv", ["retro.py", "--root", str(self.root), "accuracy",
                                                "--id", "RETRO9002", "--write",
                                                "--tokens-from-harness"]), \
                contextlib.redirect_stdout(buf):
            rc = retro.main()
        out = buf.getvalue()
        self.assertEqual(rc, 0, out)
        line = next((ln for ln in out.splitlines() if "NOT ATTRIBUTABLE" in ln), "")
        self.assertIn("opencode", line, out)
        # The reason, whichever it is: no reader installed, or the installed reader's own.
        self.assertRegex(line, r"no opencode token reader is installed|the opencode reader: ")
        self.assertNotIn("70,000", out)
        self.assert_claude_untouched(spy)
        row = retro.velocity_history(str(self.root))[0]
        self.assertFalse(row["actual_tokens"], "no token figure is recorded")


if __name__ == "__main__":
    unittest.main()
