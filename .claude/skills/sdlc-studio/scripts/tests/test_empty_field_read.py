"""extract_field and metadata_fields read an empty metadata field the same way."""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib import sdlc_md  # noqa: E402

HEADER = "> **Affects:**\n> **Next:** x\n> **Affects:** later.py\n"


class EmptyFieldReadTests(unittest.TestCase):
    def test_an_empty_field_reads_as_empty_in_both_readers(self):
        self.assertIsNone(sdlc_md.extract_field("> **Affects:**\n> **Next:** x", "Affects"))
        self.assertNotIn("affects", sdlc_md.metadata_fields("> **Affects:**\n> **Next:** x"))
        self.assertEqual(sdlc_md.extract_field("> **Affects:**\n> **Next:** x", "Next"), "x")

    def test_an_empty_field_that_recurs_later_gives_the_same_answer_in_both(self):
        # the first occurrence wins in both readers, so a later one cannot fill it
        self.assertIsNone(sdlc_md.extract_field(HEADER, "Affects"))
        self.assertNotIn("affects", sdlc_md.metadata_fields(HEADER))
        self.assertEqual(sdlc_md.metadata_fields(HEADER), {"next": "x"})

    def test_an_empty_field_before_a_plain_line_or_a_run_reads_as_empty(self):
        self.assertIsNone(sdlc_md.extract_field("**Affects:**\n**Next:** x", "Affects"))
        self.assertIsNone(sdlc_md.extract_field("> **Status:** · **Epic:** E1", "Status"))
        self.assertIsNone(sdlc_md.extract_field("> **Affects:**   \n", "Affects"))
        self.assertIsNone(sdlc_md.extract_field("> **Affects:**", "Affects"))

    def test_the_first_occurrence_of_a_name_wins_whatever_its_case(self):
        self.assertEqual(sdlc_md.metadata_fields("> **Next:** a\n> **next:** b\n"), {"next": "a"})
        # ...whichever case comes first
        self.assertEqual(sdlc_md.metadata_fields("> **next:** a\n> **Next:** b\n"), {"next": "a"})
        self.assertEqual(sdlc_md.metadata_fields("> **next:**\n> **Next:** b\n"), {})
        # an empty first occurrence is not filled by a later one spelt in another case
        self.assertEqual(sdlc_md.metadata_fields("> **Next:**\n> **next:** b\n"), {})

    def test_a_filled_field_is_unchanged(self):
        text = "> **Status:** Done · **Epic:** EP0088 · **Points:** 3\n> **Owner:**   me  \n"
        self.assertEqual(sdlc_md.extract_field(text, "Epic"), "EP0088")
        self.assertEqual(sdlc_md.extract_field(text, "Owner"), "me")
        self.assertEqual(sdlc_md.metadata_fields(text),
                         {"status": "Done", "epic": "EP0088", "points": "3", "owner": "me"})

    def test_a_field_with_a_regex_metacharacter_in_its_name_is_read_literally(self):
        self.assertEqual(sdlc_md.extract_field("> **A.B:** v\n> **AxB:** w\n", "AxB"), "w")
        self.assertEqual(sdlc_md.extract_field("> **AxB:** w\n> **A.B:** v\n", "A.B"), "v")


class SwallowedRunTests(unittest.TestCase):
    def test_a_value_with_regex_metacharacters_is_matched_literally(self):
        self.assertTrue(sdlc_md.is_swallowed_run("a+b · next", "a+b"))
        self.assertFalse(sdlc_md.is_swallowed_run("aab · next", "a+b"))
        self.assertTrue(sdlc_md.is_swallowed_run("x(1) **Next:** y", "x(1)"))

    def test_the_value_must_open_the_cell(self):
        self.assertTrue(sdlc_md.is_swallowed_run("v · rest", "v"))
        self.assertFalse(sdlc_md.is_swallowed_run("see v · rest", "v"))
        self.assertFalse(sdlc_md.is_swallowed_run("v alone", "v"))
        self.assertFalse(sdlc_md.is_swallowed_run("v · rest", ""))


if __name__ == "__main__":
    unittest.main()
