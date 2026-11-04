"""BG1122: a meter reading parses only the transcript bytes appended since the last reading.

Since US1091 the meter reads the main transcript and every `<session>/subagents/agent-*.jsonl`
once per message, and every reading parsed every one of them from the first byte: on a long
session a lane, transition or report command spent about 36 s in the meter, and more under load.
Each reading now leaves a memo under the workspace's `.local/`: per transcript, its identity,
the bytes it parsed, a digest of the bytes at either end of them, and the usage records they
held. The next reading parses only what follows.

Pinned here, through `run_state.session_tokens`, the reader every stamp-taking command calls:

* a second reading parses only the appended lines, and equals a reading of a root that keeps
  no memo, which parses every file whole (AC1);
* a transcript that shrank, was replaced by another file, or was rewritten in place with
  other bytes at either end of what was parsed, is parsed whole (AC2);
* a last line with no newline is counted in the reading that finds it, and parsed again in the
  next, so a line the harness is still writing is neither lost nor counted twice;
* the memo holds the files of the last reading and no other, is not rewritten when nothing was
  appended, is discarded when another version of the reader wrote it or it is malformed, and
  a memo that cannot be written leaves the reading standing;
* a root with no `sdlc-studio/` directory is read whole, and no directory is made in it.

Run from the repo root:
    pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_incremental_read.py
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/run_state.py
from __future__ import annotations

import contextlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib import run_state, sdlc_md, token_meters  # noqa: E402

#: No harness named or signalled for the module, for a run under `python3 -m unittest`, which
#: loads no conftest; each test then names Claude itself (US0986).
_NO_HARNESS = mock.patch.dict(os.environ)

#: One message's usage as the harness writes it: it counts input + output + cache write, ONE.
USAGE = {"input_tokens": 1_200, "output_tokens": 300, "cache_creation_input_tokens": 4_500,
         "cache_read_input_tokens": 90_000}
ONE = 6_000
#: A line carrying no usage, long enough that a probe window sits wholly inside it.
PAD = json.dumps({"type": "user", "message": {"role": "user", "content": "x" * 5_000}})


def setUpModule() -> None:
    _NO_HARNESS.start()
    for name in token_meters.selection_variables():
        os.environ.pop(name, None)


def tearDownModule() -> None:
    _NO_HARNESS.stop()


def _record(msg_id: str | None, block: str, usage: dict = USAGE) -> str:
    """One transcript record for one content block of an assistant message."""
    message = {"model": "claude-opus-5-5", "role": "assistant", "content": [{"type": block}],
               "usage": dict(usage)}
    if msg_id is not None:
        message["id"] = msg_id
    return json.dumps({"type": "assistant", "timestamp": "2026-11-04T10:00:00Z",
                       "message": message})


def _message(msg_id: str, usage: dict = USAGE) -> list[str]:
    """One message as the harness writes it: a record per content block, each with its usage."""
    return [_record(msg_id, block, usage) for block in ("thinking", "text", "tool_use")]


def _text(lines: list[str]) -> str:
    return "".join(line + "\n" for line in lines)


@contextlib.contextmanager
def _parsed():
    """Every transcript line the meter parses inside the block, newline stripped."""
    seen: list[str] = []
    real = run_state._line_record

    def spy(line, path):
        seen.append(line.rstrip("\n"))
        return real(line, path)

    with mock.patch.object(run_state, "_line_record", side_effect=spy):
        yield seen


class _Workspace:
    """A workspace that keeps a memo, a root that keeps none, and one session's transcripts."""

    def __init__(self, base: Path) -> None:
        self.root = base / "repo"
        (self.root / "sdlc-studio" / ".local").mkdir(parents=True)
        self.bare = base / "bare"
        self.transcripts = base / "transcripts"
        self.main = self.transcripts / "s1.jsonl"
        (self.transcripts / "s1" / run_state.SUBAGENTS_DIR).mkdir(parents=True)
        self.memo = self.root / run_state.METER_MEMO_REL

    def agent(self, name: str) -> Path:
        return self.transcripts / "s1" / run_state.SUBAGENTS_DIR / f"agent-{name}.jsonl"

    @staticmethod
    def add(path: Path, text: str) -> None:
        with path.open("a", encoding="utf-8") as fh:
            fh.write(text)

    def read(self, root: Path | None = None) -> tuple[dict, list[str]]:
        """A reading of `root` (the memo-keeping one by default), and every line it parsed."""
        with _parsed() as seen:
            got = run_state.session_tokens(root or self.root, self.transcripts)
        return got, seen

    def whole(self) -> dict:
        """The reading a root with no memo gives: every file parsed from its first byte."""
        return run_state.session_tokens(self.bare, self.transcripts)


class _Case(unittest.TestCase):

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = Path(tmp.name)
        env = mock.patch.dict(os.environ, {token_meters.HARNESS_ENV: "claude"})
        env.start()
        self.addCleanup(env.stop)
        self.count = 0

    def workspace(self) -> _Workspace:
        self.count += 1
        return _Workspace(self.base / str(self.count))

    def session(self) -> _Workspace:
        """A session whose main thread ran m1 and whose two subagents ran a1 and b1."""
        ws = self.workspace()
        ws.add(ws.main, _text(_message("m1")))
        ws.add(ws.agent("a"), _text(_message("a1")))
        ws.add(ws.agent("b"), _text(_message("b1")))
        return ws

    def assert_whole(self, ws: _Workspace, got: dict, seen: list[str], *files: Path) -> None:
        """`got` equals a memo-free reading, and parsed exactly the lines of `files`."""
        self.assertIsNotNone(got.get("tokens"), got.get("reason"))
        self.assertEqual(got, ws.whole())
        lines = [line for f in files for line in f.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(seen, lines)


class IncrementalReadTests(_Case):

    def test_a_second_reading_parses_only_appended_bytes(self) -> None:
        """AC1. Mutants: each file parsed from its first byte whatever the memo holds (the
        reading parses the old lines again), or the held records dropped when a file grows (the
        reading is a1's message short of a full re-read)."""
        ws = self.session()
        first, seen = ws.read()
        self.assertEqual(first["tokens"], 3 * ONE)
        self.assertEqual(len(seen), 9, "the first reading did not parse every file whole")
        appended = _message("a2")
        ws.add(ws.agent("a"), _text(appended))
        second, seen = ws.read()
        self.assertEqual(seen, appended, "the second reading parsed more than the appended bytes")
        self.assertEqual(second, ws.whole())
        self.assertEqual(second["tokens"], 4 * ONE)
        self.assertEqual(second["subagents"]["input"], 3 * USAGE["input_tokens"])

    def test_a_shrunk_or_replaced_transcript_is_read_whole(self) -> None:
        """AC2, one case per way the memo's span stops describing the file. Mutants: no size
        check (the case that drops only an unfinished last line resumes), no device and inode
        check (the replacement with the same bytes at both ends resumes), no probe, or a probe
        of the first or the last bytes alone (an in-place rewrite resumes over stale records)."""
        cut_to = len(_text(_message("a1")))

        def truncated(ws):
            with ws.agent("a").open("r+b") as fh:
                fh.truncate(cut_to)

        def replaced(ws):
            other = ws.agent("a").with_suffix(".new")
            other.write_text(_text([PAD, *_message("a1", {**USAGE, "input_tokens": 3_400}), PAD,
                                    *_message("a2")]), encoding="utf-8")
            os.replace(other, ws.agent("a"))

        def rewritten(lines):
            def act(ws):
                with ws.agent("a").open("w", encoding="utf-8") as fh:
                    fh.write(_text(lines))
            return act

        changed = _message("a1", {**USAGE, "input_tokens": 3_400})
        cases = {
            "shrunk": ([*_message("a1"), *_message("a2")], "", truncated),
            "an unfinished last line dropped": (_message("a1"), _record("a2", "text")[:40],
                                                truncated),
            "replaced, the same bytes at both ends": ([PAD, *_message("a1"), PAD], "", replaced),
            "rewritten in place, its first bytes changed": (
                [*_message("a1"), PAD], "", rewritten([*changed, PAD, *_message("a2")])),
            "rewritten in place, its last bytes changed": (
                [PAD, *_message("a1")], "", rewritten([PAD, *changed, *_message("a2")])),
        }
        for name, (lines, tail, act) in cases.items():
            with self.subTest(name):
                ws = self.workspace()
                ws.add(ws.main, _text(_message("m1")))
                ws.add(ws.agent("a"), _text(lines) + tail)
                ino = ws.agent("a").stat().st_ino
                first, _ = ws.read()
                self.assertIsNotNone(first.get("tokens"), first.get("reason"))
                act(ws)
                same = ws.agent("a").stat().st_ino == ino
                self.assertEqual(same, not name.startswith("replaced"), "not the case named")
                got, seen = ws.read()
                self.assert_whole(ws, got, seen, ws.agent("a"))

    def test_a_message_split_across_two_readings_is_counted_once_at_its_largest(self) -> None:
        """A message's last block appended after a reading, with a larger output than its first
        two. Mutant: the held records and the appended ones aggregated apart and summed (the
        message is counted twice)."""
        ws = self.workspace()
        ws.add(ws.main, _text([_record("m1", "thinking"), _record("m1", "text")]))
        ws.read()
        ws.add(ws.main, _text([_record("m1", "tool_use", {**USAGE, "output_tokens": 900})]))
        got, seen = ws.read()
        self.assertEqual(len(seen), 1)
        self.assertEqual(got, ws.whole())
        self.assertEqual(got["tokens"], ONE + 600)

    def test_a_line_still_being_written_is_read_once_it_is_whole(self) -> None:
        """Mutant: the memo's offset taken past an unfinished last line (its first half is
        never parsed again, so the message it opens is lost)."""
        ws = self.workspace()
        line = _record("m2", "text")
        ws.add(ws.main, _text(_message("m1")) + line[:50])
        first, _ = ws.read()
        self.assertEqual(first, ws.whole())
        self.assertEqual(first["tokens"], ONE)
        ws.add(ws.main, line[50:] + "\n")
        got, seen = ws.read()
        self.assertEqual(seen, [line])
        self.assertEqual(got, ws.whole())
        self.assertEqual(got["tokens"], 2 * ONE)

    def test_a_last_line_with_no_newline_is_counted_once(self) -> None:
        """Records with no message id, which nothing dedupes. Mutant: the records of a last line
        with no newline kept in the memo (it is parsed again next time and counted twice)."""
        ws = self.workspace()
        ws.add(ws.main, _text(_message("m1")) + _record(None, "text"))
        first, _ = ws.read()
        self.assertEqual(first, ws.whole())
        self.assertEqual(first["tokens"], 2 * ONE)
        ws.add(ws.main, "\n" + _text([_record(None, "text")]))
        got, _ = ws.read()
        self.assertEqual(got, ws.whole())
        self.assertEqual(got["tokens"], 3 * ONE)

    def test_a_stamp_after_the_plan_parses_only_what_the_plan_did_not(self) -> None:
        """The path every stamp-taking command takes: `open_run` reads the baseline, and
        `stamp_tokens` the next reading. Mutant: the memo dropped on that path."""
        ws = self.session()
        with mock.patch.dict(os.environ, {run_state.TRANSCRIPTS_ENV: str(ws.transcripts)}):
            rec = run_state.open_run(ws.root, batch=["BG0001"], goal="g")
            self.assertEqual(rec[run_state.TOKEN_BASELINE]["tokens"], 3 * ONE)
            appended = _message("m2")
            ws.add(ws.main, _text(appended))
            with _parsed() as seen:
                stamp = run_state.stamp_tokens(ws.root, "report")
        self.assertEqual(seen, appended)
        self.assertEqual(stamp["tokens"], ws.whole()["tokens"])
        self.assertEqual(stamp["tokens"], 4 * ONE)


class MemoTests(_Case):

    def test_the_memo_holds_the_files_of_the_last_reading_and_no_other(self) -> None:
        """Mutant: the new entries merged over the old memo, which then grows with every session
        the workspace has read."""
        ws = self.session()
        ws.read()
        held = json.loads(ws.memo.read_text(encoding="utf-8"))["files"]
        self.assertEqual(set(held), {str(ws.main), str(ws.agent("a")), str(ws.agent("b"))})
        later = ws.transcripts / "s2.jsonl"
        later.write_text(_text(_message("n1")), encoding="utf-8")
        os.utime(later, (ws.main.stat().st_mtime + 60,) * 2)
        got, _ = ws.read()
        self.assertEqual(got["source"], str(later))
        self.assertEqual(set(json.loads(ws.memo.read_text(encoding="utf-8"))["files"]),
                         {str(later)})

    def test_a_reading_with_nothing_appended_rewrites_no_memo(self) -> None:
        """Mutant: the memo written on every reading."""
        ws = self.session()
        ws.read()
        with mock.patch.object(sdlc_md, "atomic_write", wraps=sdlc_md.atomic_write) as wrote:
            got, seen = ws.read()
        self.assertEqual(seen, [])
        self.assertEqual(got, ws.whole())
        self.assertFalse(wrote.called, "an unchanged memo was rewritten")

    def test_a_memo_another_reader_wrote_is_discarded(self) -> None:
        """A memo binds the reader's source digest. Mutant: the digest not compared (a reader
        that reads a line differently resumes over records the earlier one kept)."""
        ws = self.session()
        ws.read()
        with mock.patch.object(run_state, "_reader_key", return_value="another reader"):
            got, seen = ws.read()
        self.assert_whole(ws, got, seen, ws.main, ws.agent("a"), ws.agent("b"))

    def test_a_malformed_memo_is_read_whole(self) -> None:
        """Mutants: a malformed entry raised rather than read as absent, or a held row short of a
        component taken as it is (either way the reading refuses)."""
        for name, damage in {
                "not JSON": lambda doc: "{",
                "records of the wrong shape": lambda doc: json.dumps(
                    {**doc, "files": {k: {**v, "records": [["x"]]}
                                      for k, v in doc["files"].items()}}),
                "a row short of a component": lambda doc: json.dumps(
                    {**doc, "files": {k: {**v, "records": [[r[0], r[1], r[2][:-1]]
                                                           for r in v["records"]]}
                                      for k, v in doc["files"].items()}}),
                "an offset that is not a count": lambda doc: json.dumps(
                    {**doc, "files": {k: {**v, "offset": "x"} for k, v in doc["files"].items()}}),
        }.items():
            with self.subTest(name):
                ws = self.session()
                ws.read()
                doc = json.loads(ws.memo.read_text(encoding="utf-8"))
                ws.memo.write_text(damage(doc), encoding="utf-8")
                got, seen = ws.read()
                self.assert_whole(ws, got, seen, ws.main, ws.agent("a"), ws.agent("b"))

    def test_a_memo_that_cannot_be_written_leaves_the_reading_standing(self) -> None:
        """Mutant: the write's OSError not caught (the reading raises)."""
        ws = self.session()
        with mock.patch.object(sdlc_md, "atomic_write", side_effect=OSError("read-only")):
            got, _ = ws.read()
        self.assertEqual(got, ws.whole())
        self.assertFalse(ws.memo.exists())

    def test_a_root_with_no_workspace_is_read_whole_and_written_nothing(self) -> None:
        """Mutant: the memo written under any root (a reading makes `sdlc-studio/.local/` in a
        directory that never had one)."""
        ws = self.session()
        ws.bare.mkdir()
        for _ in range(2):
            got, seen = ws.read(ws.bare)
            self.assertEqual(len(seen), 9)
            self.assertEqual(got["tokens"], 3 * ONE)
        self.assertEqual(list(ws.bare.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
