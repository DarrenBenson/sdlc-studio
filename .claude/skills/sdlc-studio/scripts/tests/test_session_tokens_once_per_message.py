"""BG1111: the session token meter counts each assistant message once, keyed on `message.id`.

The harness writes one transcript record per content block of an assistant message (thinking,
text, each tool call), and every one of them carries that message's full usage under the same
`message.id`. `run_state.session_tokens` summed every record carrying usage, so a message with
four content blocks was billed four times. Measured on transcript acd73b30 on 2026-10-22: 8,130
usage records for 3,488 distinct ids, 51.1M tokens summed per record against 20.2M once per
message, and no usage record without an id. Every reading taken from the meter - the open
stamp, the report stamp and the run total formed from them - carried the larger sum.

Pinned here:

* a message repeated on several records is counted once, and two distinct messages with the
  same usage are counted twice (AC1);
* a record carrying no `message.id` is counted once, by itself, as every record was before:
  there is nothing to tell two of them apart by, so none is merged with another;
* a message whose repeats disagree is counted at its largest reading: an earlier record can
  carry a smaller output count than the message's last;
* a malformed value on a REPEATED record still refuses the read, as on any other record;
* the run total, which is what a close reports, inherits the rule.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -k once_per_message
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/run_state.py
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib import run_state  # noqa: E402

#: One message's usage, in the shape the harness writes: cache reads are carried and excluded.
USAGE = {"input_tokens": 1_200, "output_tokens": 300, "cache_creation_input_tokens": 4_500,
         "cache_read_input_tokens": 90_000}
#: input + output + cache creation of USAGE - what one message counts for.
ONE = 6_000


def _record(msg_id: str | None, block: str, usage: dict, model: str = "claude-opus-5-5") -> str:
    """One transcript record for one content block, as the harness writes it."""
    message = {"model": model, "role": "assistant", "type": "message",
               "content": [{"type": block}], "usage": dict(usage)}
    if msg_id is not None:
        message["id"] = msg_id
    return json.dumps({"type": "assistant", "message": message})


def _blocks(msg_id: str | None, usage: dict = USAGE) -> list[str]:
    """One message written as three records - thinking, text and a tool call - each carrying
    the message's full usage, which is the shape the harness produces."""
    return [_record(msg_id, block, usage) for block in ("thinking", "text", "tool_use")]


class SessionTokensOncePerMessageTests(unittest.TestCase):

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "sdlc-studio" / ".local").mkdir(parents=True)
        self.transcripts = self.root / "transcripts"
        self.transcripts.mkdir()
        env = mock.patch.dict(os.environ, {run_state.TRANSCRIPTS_ENV: str(self.transcripts)})
        env.start()
        self.addCleanup(env.stop)
        self.addCleanup(self.tmp.cleanup)
        self.src = self.transcripts / "s1.jsonl"

    def _write(self, *records: str) -> None:
        with self.src.open("a", encoding="utf-8") as fh:
            fh.write("".join(r + "\n" for r in records))

    def test_a_repeated_message_is_counted_once(self) -> None:
        """AC1. MUTANTS: sum every record carrying usage (the defect), which reads 6 x ONE; key
        the de-duplication on the usage itself rather than on `message.id`, which merges the two
        distinct messages below because their usage is identical, and reads ONE."""
        self._write(*_blocks("msg_A"), *_blocks("msg_B"))
        cap = run_state.session_tokens(str(self.root))
        self.assertEqual(cap.get("tokens"), 2 * ONE,
                         f"two messages, each repeated on three records, must count twice: {cap}")
        self.assertEqual(cap.get("source"), str(self.src))
        self.assertEqual(cap.get("model"), "claude-opus-5-5")

    def test_a_record_with_no_message_id_is_counted_once_by_itself(self) -> None:
        """MUTANTS: key a record with no id on None, which merges every such record into one and
        reads ONE for the two below; drop it, which reads no figure at all. Two id-less records
        are two records, as they were before the fix: nothing tells them apart, so neither is
        assumed to repeat the other."""
        self._write(_record(None, "text", USAGE), _record(None, "text", USAGE))
        self.assertEqual(run_state.session_tokens(str(self.root)).get("tokens"), 2 * ONE)
        # Beside a repeated message the two rules hold together: three records of msg_A count
        # once, and each id-less record counts once.
        self._write(*_blocks("msg_A"))
        self.assertEqual(run_state.session_tokens(str(self.root)).get("tokens"), 3 * ONE)

    def test_a_message_whose_repeats_disagree_is_counted_at_its_largest_reading(self) -> None:
        """MUTANT: keep the first record's reading of a message. An earlier record can carry a
        smaller output count than the message's last: measured over this project's 90
        transcripts on 2026-10-22, 307 repeats disagreed on a counted value, always
        `output_tokens`, and the later reading was the larger every time. Keeping the first
        reads the smaller, and the meter is short."""
        early = dict(USAGE, output_tokens=12)
        self._write(_record("msg_A", "thinking", early), _record("msg_A", "text", early),
                    _record("msg_A", "tool_use", USAGE))
        self.assertEqual(run_state.session_tokens(str(self.root)).get("tokens"), ONE)

    def test_a_malformed_value_on_a_repeated_record_still_refuses_the_read(self) -> None:
        """MUTANT: skip a record whose `message.id` has been seen before parsing its usage. The
        malformed value is then never read and a figure is returned; the module's rule is that a
        malformed usage value refuses the whole read rather than yielding a total nobody can
        trust, and a repeat is no exception."""
        self._write(_record("msg_A", "thinking", USAGE),
                    _record("msg_A", "text", dict(USAGE, output_tokens=["oops"])))
        cap = run_state.session_tokens(str(self.root))
        self.assertIsNone(cap.get("tokens"), f"a malformed repeat produced a figure: {cap}")
        self.assertIn("malformed", cap.get("reason") or "")

    def test_the_run_total_counts_a_repeated_message_once(self) -> None:
        """The surface a close reports from: `open_run` stamps the meter, the report stamps it
        again, and `run_token_total` takes the delta. MUTANT: sum every record (the defect),
        which reports the one message spent between the stamps as 3 x ONE."""
        self._write(*_blocks("msg_A"))
        run_state.open_run(str(self.root), batch=["BG0001"], goal="g")
        self._write(*_blocks("msg_B"))
        self.assertIsNotNone(run_state.stamp_tokens(str(self.root), "report"))
        total = run_state.run_token_total(run_state.read(str(self.root)))
        self.assertEqual(total.get("tokens"), ONE, f"the run total misread the meter: {total}")
        self.assertEqual(total.get("sessions"), [str(self.src)])


if __name__ == "__main__":
    unittest.main()
