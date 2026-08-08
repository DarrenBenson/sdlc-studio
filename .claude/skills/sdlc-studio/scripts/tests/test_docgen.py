"""Unit tests for docgen.py - generated documentation, and the refusal to touch the rest.

Covers US0653 (the verb catalogue), US0656 (the reference index) and US0658 (Reading Guides).

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(DIR))
sys.path.insert(0, str(DIR / "lib"))
import docgen  # noqa: E402
import surface  # noqa: E402

MARKED = f"# Title\n\nprose above\n\n{docgen.BEGIN}\nold body\n{docgen.END}\n\nprose below\n"


class GeneratedRegionTests(unittest.TestCase):
    """US0653: the marker discipline, the drift report, and what the page may not carry."""

    def test_only_the_marked_region_is_rewritten_and_an_unmarked_file_is_refused(self) -> None:
        """AC1. Mutant: write the whole file rather than only the marked region.
        Mutant: generate into an unmarked file rather than refusing it."""
        out = docgen.splice(MARKED, "NEW BODY")
        self.assertIn("NEW BODY", out)
        self.assertNotIn("old body", out)
        for kept in ("# Title", "prose above", "prose below"):
            self.assertIn(kept, out, f"{kept!r} outside the markers was not preserved")

        with self.assertRaises(docgen.MarkerError):
            docgen.splice("# Title\n\njust prose\n", "NEW BODY")

    def test_a_malformed_marker_pair_is_refused(self) -> None:
        """AC1. Each shape is how a generator eats a paragraph.

        Mutant: treat a `BEGIN` with no `END` as running to end-of-file.
        Mutant: accept an `END` that precedes its `BEGIN`.
        Mutant: accept two `BEGIN` markers.
        """
        cases = {
            "BEGIN with no END": f"# T\n{docgen.BEGIN}\nbody\n",
            "END before BEGIN": f"# T\n{docgen.END}\nbody\n{docgen.BEGIN}\n",
            "two BEGINs": f"# T\n{docgen.BEGIN}\na\n{docgen.BEGIN}\nb\n{docgen.END}\n",
        }
        for name, text in cases.items():
            with self.subTest(shape=name), self.assertRaises(docgen.MarkerError):
                docgen.splice(text, "NEW")
        # The positive control: a well-formed pair still writes, or the refusal fires on all.
        self.assertIn("NEW", docgen.splice(MARKED, "NEW"))

    def _fake_surface(self):
        return [surface.ScriptSurface(name="a.py", verbs=["go", "go deep"], flags={"--root"},
                                      has_build_parser=True),
                surface.ScriptSurface(name="b.py", verbs=["go"], flags={"--check"},
                                      has_build_parser=True)]

    def test_the_catalogue_lists_exactly_what_the_surface_enumerates(self) -> None:
        """AC3. The enumerator is PATCHED to a fixed fake and the page compared against that
        literal list. Generating from the live enumeration and comparing against the live
        enumeration is two things agreeing: any mutant inside the shared enumerator survives on
        both sides at once. The repeated verb name exercises the exactly-once half.

        Mutant: emit only the verbs whose script name sorts first, truncating the list.
        """
        real = surface.enumerate_scripts
        try:
            surface.enumerate_scripts = lambda *a, **k: self._fake_surface()  # noqa: ARG005
            body = docgen.render_surface()
        finally:
            surface.enumerate_scripts = real
        for expected in ("`a.py go`", "`a.py go deep`", "`b.py go`"):
            self.assertIn(expected, body, f"{expected} missing from the generated catalogue")
        self.assertEqual(1, body.count("| `a.py go` |"), "a verb appears more than once")

    def test_no_generated_row_carries_a_flag(self) -> None:
        """AC4, asserted against the enumerator's OWN flag set rather than a `--` substring.

        The page's pointer sentence must name `--help`, so a naive substring check would exempt
        exactly the strings that sentence adds and then pass on prose the generator emits.

        Mutant: render each verb's flags into the table beside it.
        """
        flags = surface.all_flags()
        self.assertGreater(len(flags), 100,
                           "the enumerator's flag set is empty or tiny, so a row check against "
                           "it passes vacuously whatever the page contains")
        rows = [ln for ln in docgen.render_surface().splitlines() if ln.startswith("| `")]
        self.assertTrue(rows, "the catalogue rendered no rows")
        for row in rows:
            for flag in flags:
                self.assertNotIn(f"{flag} ", row, f"a generated row carries the flag {flag}")

    def test_format_json_emits_the_flags_the_page_omits(self) -> None:
        """AC5. The page points at this, so it has to be there: a pointer to an entry point
        nobody built is a worse answer than no pointer.

        Mutant: accept `--format json` and emit the same markdown the page carries.
        """
        payload = json.loads(docgen.surface_json())
        self.assertTrue(payload)
        with_flags = [r for r in payload if r["flags"]]
        self.assertTrue(with_flags, "the json carries no flags, which is the one thing it is for")
        self.assertIn("verbs", payload[0])


class ReferenceIndexTests(unittest.TestCase):
    """US0656: the index is walked, both ways, and each row speaks for its own file."""

    def _skill(self, d: Path, names) -> Path:
        for name, body in names.items():
            (d / name).write_text(body, encoding="utf-8")
        return d

    def test_a_reference_the_index_never_named_appears(self) -> None:
        """AC1. Mutant: build the index from the existing rows rather than a directory walk."""
        with tempfile.TemporaryDirectory() as t:
            d = self._skill(Path(t), {
                "reference-new.md": "# New\n\nWhat this new one covers.\n",
                "reference-old.md": "# Old\n\nWhat the old one covers.\n"})
            rows = dict(docgen.reference_rows(d))
            self.assertIn("reference-new.md", rows)
            self.assertIn("reference-old.md", rows)

    def test_a_row_whose_file_has_gone_is_removed(self) -> None:
        """AC2, with its positive control: the live rows must SURVIVE. A test asserting only
        that the stale row went also passes against a generator emitting an empty table.

        Mutant: append missing rows without removing the ones whose file has gone.
        Mutant: emit an empty table.
        """
        with tempfile.TemporaryDirectory() as t:
            d = self._skill(Path(t), {"reference-live.md": "# Live\n\nStill here.\n"})
            body = docgen.render_references(d)
            self.assertIn("reference-live.md", body, "a live row did not survive")
            self.assertNotIn("reference-gone.md", body, "a row for a deleted file survived")

    def test_each_row_carries_the_references_own_description(self) -> None:
        """AC3, including the fallback for a file with no descriptive line - stated, because an
        unspecified one is a thing no test can fail on.

        Mutant: write a fixed description per row rather than reading the file's own.
        Mutant: emit an empty cell for a file with no first descriptive line.
        """
        with tempfile.TemporaryDirectory() as t:
            d = self._skill(Path(t), {
                "reference-described.md": "# D\n\n> **Status:** x\n\nThe thing it covers.\n",
                "reference-bare.md": "# B\n\n| a | b |\n| --- | --- |\n"})
            rows = dict(docgen.reference_rows(d))
            self.assertEqual("The thing it covers", rows["reference-described.md"])
            self.assertEqual("bare", rows["reference-bare.md"],
                             "a file with no descriptive line got an empty cell rather than the "
                             "stated fallback")


class ReadingGuideTests(unittest.TestCase):
    """US0658: a guide with line spans that are TRUE of the file containing them."""

    LONG = "# Doc\n\n" + "".join(f"## Section {i}\n\n" + "filler\n" * 30 for i in range(12))

    def test_each_entry_carries_a_line_span(self) -> None:
        """AC2. Mutant: emit the anchor without the line span."""
        body = docgen.render_guide_text(self.LONG)
        self.assertIn("| Section | Lines |", body)
        self.assertRegex(body, r"\| Section 0 \| \d+-\d+ \|")

    def test_the_spans_are_true_of_the_file_that_contains_them(self) -> None:
        """AC2/AC3, and the reason the generation iterates to a fixed point: the guide reports
        line spans and occupies lines, so one pass emits spans true of the file BEFORE the guide
        existed and wrong the moment it does.

        Mutant: apply the guide once rather than iterating to a fixed point.
        """
        import re
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "reference-long.md"
            p.write_text(self.LONG, encoding="utf-8")
            out = docgen.apply_guide(self.LONG, p)
            lines = out.splitlines()
            for m in re.finditer(r"\| (Section \d+) \| (\d+)-\d+ \|", out):
                title, start = m.group(1), int(m.group(2))
                self.assertTrue(lines[start - 1].startswith(f"## {title}"),
                                f"the guide says {title} is at line {start}, where the file has "
                                f"{lines[start - 1]!r} - a wrong span sends a reader to the "
                                f"wrong place with confidence")

    def test_a_moved_section_is_reported_as_drift_and_a_settled_one_is_not(self) -> None:
        """AC3, with the silent case as the positive control: a checker that always reports
        drift passes the first half.

        Mutant: report no drift when a section has moved.
        Mutant: report drift when nothing has moved.
        """
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "reference-long.md"
            p.write_text(self.LONG, encoding="utf-8")
            settled = docgen.apply_guide(self.LONG, p)
            p.write_text(settled, encoding="utf-8")
            self.assertEqual(settled, docgen.apply_guide(settled, p),
                             "a settled file still reported drift")

            moved = settled.replace("## Section 5", "## Section 5 renamed", 1)
            p.write_text(moved, encoding="utf-8")
            self.assertNotEqual(moved, docgen.apply_guide(moved, p),
                                "a moved section reported no drift")

    def test_every_reference_over_the_threshold_has_one(self) -> None:
        """AC1, over the real tree. The count is DERIVED from the threshold, never typed - and
        pinned by a second assertion that a file which previously had none now has one, because
        a derived count alone cannot catch the mutant that generates only where a guide is
        absent.

        Mutant: generate a guide only where one is absent.
        """
        skill = DIR.parent
        longs = docgen.long_references(skill)
        self.assertGreater(len(longs), 20, "the threshold selected almost nothing")
        for path in longs:
            with self.subTest(reference=path.name):
                self.assertIn(docgen.GUIDE_BEGIN, path.read_text(encoding="utf-8"),
                              f"{path.name} is over {docgen.GUIDE_THRESHOLD} lines and carries "
                              f"no generated Reading Guide")
        # reference-sprint.md had none before this work: its budget justification asserted one
        # twice over a file that did not have it.
        sprint = skill / "reference-sprint.md"
        self.assertIn(docgen.GUIDE_BEGIN, sprint.read_text(encoding="utf-8"))


class CorpusRuleTests(unittest.TestCase):
    """The rule `command_audit.py` imports: strip generated blocks, and nothing else."""

    def test_a_generated_block_is_stripped_wherever_it_appears(self) -> None:
        text = f"prose\n{docgen.BEGIN}\n| `a.py go` |\n{docgen.END}\nmore prose\n"
        out = docgen.strip_generated_blocks(text)
        self.assertNotIn("a.py go", out)
        self.assertIn("prose", out)
        self.assertIn("more prose", out)

    def test_a_hand_written_table_is_not_stripped(self) -> None:
        """A stripper that ate every table would drive a coverage count to 100% undocumented,
        which passes an unchanged-number assertion by measuring nothing."""
        text = "prose\n\n| Command | What |\n| --- | --- |\n| `a.py go` | does a thing |\n"
        self.assertIn("a.py go", docgen.strip_generated_blocks(text))


if __name__ == "__main__":
    unittest.main()
