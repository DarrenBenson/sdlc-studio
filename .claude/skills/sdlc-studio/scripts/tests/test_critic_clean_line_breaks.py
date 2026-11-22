"""BG1050: a verdict cell carrying any character `str.splitlines` breaks on stays on its row.

`critic._clean` folded only the newline, while the ledger is read back with universal newlines
and `splitlines`, which also break on a carriage return, a vertical tab, a form feed, the file,
group and record separators, the next-line control and the Unicode line and paragraph
separators. A reviewer id carrying one tore its own row: `read_verdicts` warned of a malformed
row and skipped it, and the unit's delivery verdict vanished from every gate.

The first case records through `critic.record_verdict`, the writer every recording command
calls, and reads the ledger back through `critic.read_verdicts`. The second derives the set of
breaking characters from `str.splitlines` itself over every code point, so a character the
fold leaves out is named here rather than found in a torn ledger.
"""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

critic = loader.load_script("critic")


def _breaks(ch: str) -> bool:
    """True when `str.splitlines` ends a line at `ch`."""
    return len(f"a{ch}b".splitlines()) == 2


class CleanLineBreakTests(unittest.TestCase):

    def test_a_reviewer_id_with_every_splitlines_break_reads_back_whole(self) -> None:
        """AC1. Mutants: `_clean` folding only the newline (the carriage return tears the row);
        a fold that drops a break rather than spacing it (the reviewer reads `qaseat`)."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            reviewer = "qa\rseat\x0cone\u2028two"
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                critic.record_verdict(root, "US0001", "APPROVE", reviewer=reviewer,
                                      author="builder", issues="none")
                critic.record_verdict(root, "US0002", "APPROVE", reviewer="qa-seat",
                                      author="builder", issues="none")
                rows = critic.read_verdicts(root)
            self.assertNotIn("malformed row", err.getvalue())
            self.assertEqual(["US0001", "US0002"], [r["unit"] for r in rows],
                             "the torn row was skipped, or tore the row after it")
            self.assertEqual("qa seat one two", rows[0]["reviewer"])
            self.assertEqual("builder", rows[0]["author"])
            self.assertEqual("APPROVE", rows[0]["verdict"])

    def test_every_character_splitlines_breaks_on_is_folded_to_a_space(self) -> None:
        """Mutant: any one break left out of the fold. Derived from `str.splitlines` over every
        code point, never from a list beside the code, and the negative control holds a
        character that is not a break (a tab) as it was written."""
        breaks = [chr(c) for c in range(sys.maxunicode + 1)
                  if not 0xD800 <= c <= 0xDFFF and _breaks(chr(c))]
        self.assertIn("\r", breaks, "premise: the derivation finds the carriage return")
        for ch in breaks:
            self.assertEqual("a b", critic._clean(f"a{ch}b"), f"{ch!r} was not folded")
        self.assertEqual("a\tb", critic._clean("a\tb"), "a tab is not a line break")


if __name__ == "__main__":
    unittest.main()
