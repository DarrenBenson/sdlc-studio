"""Edge-case battery for the SHARED markdown-table primitives in lib/sdlc_md.py (CR0069).

The reconcile fault history (multi-schema columns, count blocks, orphan-row safety) all flowed
through one shared splitter (`table_cells`), one shared writer (`join_row`), and one shared status
reducer (`canonical_status`). Every index parser/writer in the skill uses these. This module isolates
their edge cases and the join/split round-trip so the whole fault class stays closed.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS_DIR / rel)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


sdlc_md = _load("sdlc_md", "lib/sdlc_md.py")
tc = sdlc_md.table_cells
jr = sdlc_md.join_row
cs = sdlc_md.canonical_status
VOCAB = ["Proposed", "In Progress", "Done", "Complete", "Superseded"]


class TableCellsTests(unittest.TestCase):
    def test_plain_row(self):
        self.assertEqual(tc("| a | b | c |"), ["a", "b", "c"])

    def test_non_table_line_is_none(self):
        self.assertIsNone(tc("not a table row"))
        self.assertIsNone(tc("a | b | c"))           # no leading pipe

    def test_separator_variants_are_none(self):
        for sep in ("|---|---|", "| --- | --- |", "| :--- | ---: | :-: |", "|:-:|:-:|"):
            self.assertIsNone(tc(sep), sep)

    def test_trailing_pipe_optional(self):
        self.assertEqual(tc("| a | b |"), ["a", "b"])
        self.assertEqual(tc("| a | b"), ["a", "b"])

    def test_empty_cells_preserved(self):
        self.assertEqual(tc("| a |  | c |"), ["a", "", "c"])
        self.assertEqual(tc("|  |  |"), ["", ""])

    def test_per_cell_whitespace_trimmed(self):
        self.assertEqual(tc("|   a   |\tb\t| c |"), ["a", "b", "c"])

    def test_escaped_pipe_does_not_shift_columns(self):
        self.assertEqual(tc(r"| US0161 | `string \| string[]` | Done |"),
                         ["US0161", "`string | string[]`", "Done"])

    def test_multiple_escaped_pipes_in_one_cell(self):
        self.assertEqual(tc(r"| a \| b \| c | x |"), ["a | b | c", "x"])

    def test_unicode_content(self):
        self.assertEqual(tc("| café | déjà | Done |"), ["café", "déjà", "Done"])

    def test_ragged_rows_do_not_crash(self):
        self.assertEqual(tc("| a |"), ["a"])
        self.assertEqual(tc("| a | b | c | d | e |"), ["a", "b", "c", "d", "e"])

    def test_single_dash_cell_in_real_row_is_not_a_separator(self):
        # only a row whose EVERY cell is dashes/colons is a separator
        self.assertEqual(tc("| - | x |"), ["-", "x"])
        self.assertEqual(tc("| Done | - |"), ["Done", "-"])


class JoinRoundTripTests(unittest.TestCase):
    def test_join_escapes_pipe(self):
        self.assertEqual(jr(["a | b", "c"]), r"| a \| b | c |")

    def test_round_trip_preserves_cells(self):
        for cells in (["a", "b", "c"], ["a | b", "c"], [r"x \| y", "z"],
                      ["café", ""], ["a | b | c", "d", "e | f"]):
            self.assertEqual(tc(jr(cells)), cells, cells)


class CanonicalStatusTests(unittest.TestCase):
    def test_exact_match(self):
        self.assertEqual(cs("Done", VOCAB), "Done")

    def test_decorated_status_reduces_to_token(self):
        self.assertEqual(cs("Done (v2.83.0) · **CR:** CR-0088 · **Points:** 8", VOCAB), "Done")

    def test_bold_stripped(self):
        self.assertEqual(cs("**Done**", VOCAB), "Done")

    def test_longest_term_wins(self):
        self.assertEqual(cs("In Progress", VOCAB), "In Progress")

    def test_title_starting_with_status_word_is_not_a_status(self):
        # the BG0018 guard: an alnum continuation means it's prose, not the status
        self.assertIsNone(cs("Doneness review", VOCAB))
        self.assertIsNone(cs("Completeness audit", VOCAB))

    def test_non_alnum_boundary_still_matches(self):
        self.assertEqual(cs("Done.", VOCAB), "Done")
        self.assertEqual(cs("Done - shipped", VOCAB), "Done")

    def test_unrecognised_and_empty(self):
        self.assertIsNone(cs("TBD", VOCAB))
        self.assertIsNone(cs("", VOCAB))
        self.assertIsNone(cs(None, VOCAB))


if __name__ == "__main__":
    unittest.main()
