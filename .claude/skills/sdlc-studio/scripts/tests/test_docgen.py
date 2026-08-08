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


class CheckExitsZeroTests(unittest.TestCase):
    """AC2, driven through `main()`. The claim that `--check` reports and never blocks was true
    by hand and pinned nowhere, so a revert to a blocking guard ships green - and this whole CR
    exists under an operator decision that documentation guards REPORT."""

    def _target(self, d: Path, name: str, sub: str) -> Path:
        skill = d / ".claude/skills/sdlc-studio"
        (skill / "help").mkdir(parents=True, exist_ok=True)
        (skill / "SKILL.md").write_text("# S\n", encoding="utf-8")
        target = skill / name
        target.write_text(f"# T\n\n{docgen.BEGIN}\nSEEDED DRIFT\n{docgen.END}\n",
                          encoding="utf-8")
        return target

    def test_check_reports_drift_and_still_exits_zero(self) -> None:
        """Mutant: return 1 from `--check` when the regeneration differs.
        Mutant: WRITE the file under `--check`, so the guard is a rewrite in disguise."""
        import io, contextlib
        for name, sub in (("reference-scripts-surface.md", "surface"),
                          ("help/references.md", "references")):
            with self.subTest(verb=sub), tempfile.TemporaryDirectory() as t:
                d = Path(t)
                target = self._target(d, name, sub)
                before = target.read_text(encoding="utf-8")
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    code = docgen.main([sub, "--root", str(d), "--check"])
                self.assertEqual(0, code,
                                 f"`docgen.py {sub} --check` exited {code} on a seeded drift - a "
                                 f"documentation guard that blocks is the thing the operator "
                                 f"decided against")
                self.assertIn("drift item(s)", buf.getvalue(),
                              "`--check` exited 0 without reporting anything, which is silence "
                              "rather than a report")
                self.assertNotIn("0 drift", buf.getvalue(), "the seeded drift was not detected")
                self.assertEqual(before, target.read_text(encoding="utf-8"),
                                 "`--check` WROTE the file - it is a rewrite in disguise")

    def test_a_settled_target_reports_zero_and_exits_zero(self) -> None:
        """The positive control: a `--check` hard-wired to report drift passes the test above."""
        import io, contextlib
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            target = self._target(d, "help/references.md", "references")
            docgen.main(["references", "--root", str(d)])       # settle it
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = docgen.main(["references", "--root", str(d), "--check"])
            self.assertEqual(0, code)
            self.assertIn("0 drift item(s)", buf.getvalue(),
                          "a settled target still reported drift, so the count is hard-wired")


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

    def test_every_real_row_reads_as_prose_about_its_own_file(self) -> None:
        """AC3 OVER THE REAL TREE. A two-file synthetic fixture cannot see what the corpus
        actually contains - seven rows shipped a comment tail, a marker line or a table
        fragment as their description and the fixture was green throughout.

        Mutant: take the first non-blank line, whatever it is.
        Mutant: read through a generated block, an HTML comment or a fenced example.
        """
        skill = DIR.parent
        rows = dict(docgen.reference_rows(skill))
        self.assertGreater(len(rows), 40, "the walk found almost no references")
        bad = {"-->", "<!--", "```", "|", "#", docgen.BEGIN, docgen.GUIDE_BEGIN}
        for name, desc in rows.items():
            with self.subTest(reference=name):
                self.assertTrue(desc, f"{name} got an empty description")
                for token in bad:
                    self.assertNotIn(token, desc,
                                     f"{name}'s row reads {desc!r} - markup rather than a "
                                     f"sentence about the file")
                self.assertGreater(len(desc), 14,
                                   f"{name}'s row reads {desc!r}, which tells a reader choosing "
                                   f"between 50 references nothing")


class GenerationThroughTheCliTests(unittest.TestCase):
    """The claims driven through `docgen.py` itself. A library test cannot see the wiring: the
    splice, the marker refusal and the write are three functions the CLI has to compose, and
    `brief_fingerprint(brief(...))` passed in-process for a whole sprint while the command
    printed nothing."""

    def test_references_is_generated_from_the_filesystem_through_the_cli(self) -> None:
        """US0656 AC1. Mutant: build the index from the rows already in the file.
        Mutant: leave `cmd_references` unwired, so the library is right and nothing calls it."""
        import io, contextlib
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            skill = d / ".claude/skills/sdlc-studio"
            (skill / "help").mkdir(parents=True)
            (skill / "SKILL.md").write_text("# S\n", encoding="utf-8")
            (skill / "reference-invented.md").write_text(
                "# Invented\n\nA reference nothing has ever listed anywhere.\n", encoding="utf-8")
            index = skill / "help/references.md"
            index.write_text(f"# R\n\n{docgen.BEGIN}\n{docgen.END}\n", encoding="utf-8")

            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                self.assertEqual(0, docgen.main(["references", "--root", str(d)]))
            body = index.read_text(encoding="utf-8")
            self.assertIn("reference-invented.md", body,
                          "a reference the index never named did not appear after running the "
                          "command - the walk is in the library and nothing calls it")
            self.assertIn("A reference nothing has ever listed anywhere", body)

    def test_a_target_without_markers_is_refused_by_the_cli(self) -> None:
        """US0653 AC1 through the entry point: the refusal is what stops a generator eating a
        hand-written page, and a library that raises into a `main` which swallows it refuses
        nothing. Mutant: catch MarkerError in `main` and write anyway."""
        import io, contextlib
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            skill = d / ".claude/skills/sdlc-studio"
            (skill / "help").mkdir(parents=True)
            (skill / "SKILL.md").write_text("# S\n", encoding="utf-8")
            index = skill / "help/references.md"
            index.write_text("# R\n\nhand-written prose nobody generated\n", encoding="utf-8")
            before = index.read_text(encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()) as err:
                code = docgen.main(["references", "--root", str(d)])
            self.assertEqual(2, code, "an unmarked target was not refused")
            self.assertIn("marker", err.getvalue().lower())
            self.assertEqual(before, index.read_text(encoding="utf-8"),
                             "the unmarked hand-written page was OVERWRITTEN")

    def test_reading_guides_are_generated_through_the_cli(self) -> None:
        """US0658 AC1. Mutant: leave `cmd_reading_guides` unwired."""
        import io, contextlib
        with tempfile.TemporaryDirectory() as t:
            d = Path(t)
            skill = d / ".claude/skills/sdlc-studio"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("# S\n", encoding="utf-8")
            long = skill / "reference-long.md"
            # Comfortably PAST the threshold, computed from it rather than typed: a fixture
            # sized by hand sits under the bar the moment the bar moves, and the test then
            # reports "no guide generated" about a file that was never eligible for one.
            long.write_text("# Doc\n\n" + "".join(
                f"## Section {i}\n\n" + "filler\n" * 30
                for i in range(docgen.GUIDE_THRESHOLD // 20)), encoding="utf-8")
            self.assertGreater(len(long.read_text(encoding="utf-8").splitlines()),
                               docgen.GUIDE_THRESHOLD, "the fixture is under the threshold")
            short = skill / "reference-short.md"
            short.write_text("# Short\n\n## A\n\nbody\n", encoding="utf-8")

            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                self.assertEqual(0, docgen.main(["reading-guides", "--root", str(d)]))
            self.assertIn(docgen.GUIDE_BEGIN, long.read_text(encoding="utf-8"),
                          f"a reference over {docgen.GUIDE_THRESHOLD} lines got no guide from "
                          f"the command")
            self.assertNotIn(docgen.GUIDE_BEGIN, short.read_text(encoding="utf-8"),
                             "a SHORT reference got a guide, so the threshold is not applied")
            self.assertIn("1 of 1 reference(s) rewritten", buf.getvalue())


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

    def test_the_generated_guide_REPLACES_a_hand_written_one(self) -> None:
        """AC1's second clause. Asserting a guide is PRESENT is satisfied by a file with two,
        which is what shipped: three references carried a hand-written guide and a generated one
        underneath it, and the generated table listed its own rival as a section row.

        Mutant: append the generated guide without removing the hand-written one.
        """
        skill = DIR.parent
        for path in docgen.long_references(skill):
            body = path.read_text(encoding="utf-8")
            with self.subTest(reference=path.name):
                self.assertEqual(1, body.count(docgen.GUIDE_BEGIN),
                                 f"{path.name} carries {body.count(docgen.GUIDE_BEGIN)} generated "
                                 f"guides")
                self.assertEqual([], docgen.HAND_GUIDE.findall(body),
                                 f"{path.name} still carries a HAND-WRITTEN Reading Guide beside "
                                 f"the generated one, so a reader gets two answers about where a "
                                 f"section starts - and the generated table lists its rival as a "
                                 f"section row")
        # ...and the stripper is what enforces it, over a file that HAS a hand-written one.
        hand = "# T\n\n## Reading Guide\n\n| a | b |\n\nbody\n"
        self.assertNotIn("Reading Guide", docgen.strip_hand_written_guide(hand))
        self.assertIn("body", docgen.strip_hand_written_guide(hand),
                      "the stripper ate prose past the guide it removed")


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
