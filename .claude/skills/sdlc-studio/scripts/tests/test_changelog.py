"""changelog.py - per-unit fragments composed deterministically (US0188/CR0315).

The honesty properties: compose is idempotent (fragments are consumed), a
malformed fragment is refused naming the file, a stray fragment fails a release
(never silently dropped from a cut), and a fragment satisfies the
changelog-empty documentation check.
"""
import pathlib
import re
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import loader  # noqa: E402

changelog = loader.load_script("changelog")

BASE = """# Changelog

## [Unreleased]

### Added

- an existing entry

## [4.1.0] - 2026-07-14

### Fixed

- old release content
"""


def _repo(tmp, changelog_text=BASE, fragments=()):
    root = pathlib.Path(tmp)
    (root / "CHANGELOG.md").write_text(changelog_text, encoding="utf-8")
    d = root / "changelog.d"
    d.mkdir(exist_ok=True)
    for name, body in fragments:
        (d / name).write_text(body, encoding="utf-8")
    return root


FRAG_ADDED = "<!-- section: Added -->\n- **New thing (US0001).** It does a thing.\n"
FRAG_CHANGED = "<!-- section: Changed -->\n- **Altered thing (US0002).** Different now.\n"


class ComposeTests(unittest.TestCase):
    def test_compose_groups_into_existing_and_new_sections(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(tmp, fragments=[("US0001.md", FRAG_ADDED),
                                         ("US0002.md", FRAG_CHANGED)])
            r = changelog.compose(root)
            self.assertEqual(r["composed"], 2)
            text = (root / "CHANGELOG.md").read_text(encoding="utf-8")
            unreleased = text.split("## [4.1.0]")[0]
            self.assertIn("- **New thing (US0001).**", unreleased)
            self.assertIn("### Changed", unreleased)          # section created
            self.assertIn("- **Altered thing (US0002).**", unreleased)
            self.assertIn("- an existing entry", unreleased)  # never clobbered
            self.assertNotIn("US0001", text.split("## [4.1.0]")[1])  # not in old releases

    def test_entry_lands_under_its_declared_preexisting_section(self):
        # kills the bottom-of-[Unreleased] append mutant: the fragment declares the
        # FIRST section (Added), so a bottom-append would land it in the LAST block -
        # the assertions distinguish insert-under-heading from append (the first
        # version of this test targeted the last section and was vacuous: the
        # critic ran the mutant and 11/11 stayed green)
        two_sections = ("# Changelog\n\n## [Unreleased]\n\n### Added\n\n- existing added\n\n"
                        "### Fixed\n\n- existing fixed\n\n## [4.1.0] - 2026-07-14\n\n- x\n")
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(tmp, changelog_text=two_sections,
                         fragments=[("f.md", "<!-- section: Added -->\n- **the addition.**\n")])
            changelog.compose(root)
            text = (root / "CHANGELOG.md").read_text(encoding="utf-8")
            added_block = text.split("### Added", 1)[1].split("### Fixed", 1)[0]
            self.assertIn("- **the addition.**", added_block)
            fixed_block = text.split("### Fixed", 1)[1].split("## [4.1.0]", 1)[0]
            self.assertNotIn("the addition", fixed_block)

    def test_mixed_good_and_bad_fragments_all_survive_refusal(self):
        # kills the consume-before-validate mutant: the good sibling must NOT be
        # destroyed (or composed) when a bad fragment refuses the run
        with tempfile.TemporaryDirectory() as tmp:
            # the good fragment SORTS FIRST (a- < z-): an interleaved parse+unlink
            # mutant consumes it before hitting the bad one - the ordering is the test
            root = _repo(tmp, fragments=[("a-good.md", FRAG_ADDED),
                                         ("z-bad.md", "no marker here\n")])
            with self.assertRaises(changelog.FragmentError):
                changelog.compose(root)
            self.assertEqual((root / "CHANGELOG.md").read_text(encoding="utf-8"), BASE)
            self.assertTrue((root / "changelog.d" / "a-good.md").exists())
            self.assertTrue((root / "changelog.d" / "z-bad.md").exists())

    def test_compose_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(tmp, fragments=[("US0001.md", FRAG_ADDED)])
            changelog.compose(root)
            first = (root / "CHANGELOG.md").read_text(encoding="utf-8")
            r2 = changelog.compose(root)
            self.assertEqual(r2["composed"], 0)
            self.assertEqual((root / "CHANGELOG.md").read_text(encoding="utf-8"), first)

    def test_fragments_are_consumed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(tmp, fragments=[("US0001.md", FRAG_ADDED)])
            changelog.compose(root)
            self.assertEqual(list((root / "changelog.d").glob("*.md")), [])

    def test_malformed_fragment_refused_naming_the_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(tmp, fragments=[("bad.md", "- entry with no section marker\n")])
            with self.assertRaises(changelog.FragmentError) as ctx:
                changelog.compose(root)
            self.assertIn("bad.md", str(ctx.exception))
            # nothing was written or consumed on refusal
            self.assertEqual((root / "CHANGELOG.md").read_text(encoding="utf-8"), BASE)
            self.assertTrue((root / "changelog.d" / "bad.md").exists())

    def test_unknown_section_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(tmp, fragments=[
                ("odd.md", "<!-- section: Sparkles -->\n- glitter\n")])
            with self.assertRaises(changelog.FragmentError) as ctx:
                changelog.compose(root)
            self.assertIn("Sparkles", str(ctx.exception))


class StrayFragmentTests(unittest.TestCase):
    def test_check_lists_stray_fragments(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(tmp, fragments=[("US0001.md", FRAG_ADDED)])
            strays = changelog.check(root)
            self.assertEqual([p.name for p in strays], ["US0001.md"])

    def test_release_gate_lane_blocks_on_strays(self):
        gate = loader.load_script("gate")
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(tmp, fragments=[("US0001.md", FRAG_ADDED)])
            r = gate._changelog_fragments(str(root))
            self.assertEqual(r["count"], 1)
            self.assertTrue(r["blocking"])
            self.assertIn("US0001.md", r["detail"])
            (root / "changelog.d" / "US0001.md").unlink()
            r = gate._changelog_fragments(str(root))
            self.assertEqual(r["count"], 0)


class FragmentCoverageTests(unittest.TestCase):
    def test_fragment_satisfies_changelog_empty_check(self):
        dc = loader.load_script("doc_coverage")
        empty_changelog = "# Changelog\n\n## [Unreleased]\n\n## [4.1.0] - 2026-07-14\n\n- x\n"
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(tmp, changelog_text=empty_changelog,
                         fragments=[("US0001.md", FRAG_ADDED)])
            self.assertFalse(dc._changelog_unreleased_empty(root))

    def test_empty_with_no_fragments_still_fails(self):
        dc = loader.load_script("doc_coverage")
        empty_changelog = "# Changelog\n\n## [Unreleased]\n\n## [4.1.0] - 2026-07-14\n\n- x\n"
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(tmp, changelog_text=empty_changelog)
            self.assertTrue(dc._changelog_unreleased_empty(root))


class StructureCheckTests(unittest.TestCase):
    """US0330: a structural check over CHANGELOG.md's OWN [Unreleased] headings catches the
    shapes a bad hand-insert produces - out of canonical order, repeated inside the release,
    or empty - and passes a well-formed file. Scoped to [Unreleased]: released history is
    frozen and hand-editable, so it is not policed."""

    def _errs(self, tmp, changelog_text):
        root = pathlib.Path(tmp)
        (root / "CHANGELOG.md").write_text(changelog_text, encoding="utf-8")
        return changelog.structure_errors(root)

    def test_subsections_out_of_canonical_order_fail(self):
        # Fixed above Added: the canonical order is Added(1) before Fixed(5), so Added is the
        # heading out of place. The message names the release, the out-of-order heading and
        # the expected order.
        text = ("# Changelog\n\n## [Unreleased]\n\n"
                "### Fixed\n\n- a fix\n\n"
                "### Added\n\n- an addition\n\n"
                "## [4.1.0] - 2026-07-14\n\n### Fixed\n\n- old\n")
        with tempfile.TemporaryDirectory() as tmp:
            errs = self._errs(tmp, text)
            self.assertTrue(any("out of canonical order" in e for e in errs), errs)
            joined = " ".join(errs)
            self.assertIn("### Added", joined)          # the out-of-place heading
            self.assertIn("### Fixed", joined)          # what it follows
            self.assertIn("[Unreleased]", joined)       # the release named
            self.assertIn("Added, Changed", joined)     # the expected order spelled out
        # the same release with the headings the right way round is clean (the fault is the
        # order, not the presence of two headings)
        ok_text = ("# Changelog\n\n## [Unreleased]\n\n"
                   "### Added\n\n- an addition\n\n"
                   "### Fixed\n\n- a fix\n\n"
                   "## [4.1.0] - 2026-07-14\n\n### Fixed\n\n- old\n")
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(self._errs(tmp, ok_text), [])

    def test_a_repeated_subsection_in_one_release_fails_naming_both_lines(self):
        # two `### Added` headings inside [Unreleased] - the exact incident shape, under which
        # every entry after the second heading reads as belonging to it.
        text = ("# Changelog\n\n## [Unreleased]\n\n"      # lines 1-3
                "### Added\n\n- first entry\n\n"          # ### Added at line 5
                "### Added\n\n- second entry\n\n"         # ### Added at line 9
                "## [4.1.0] - 2026-07-14\n\n### Fixed\n\n- old\n")
        with tempfile.TemporaryDirectory() as tmp:
            errs = self._errs(tmp, text)
            self.assertEqual(len(errs), 1, errs)         # ONLY the repeat, not a spurious order fault
            self.assertIn("repeated", errs[0])
            self.assertIn("5 and 9", errs[0])            # both occurrences, by file line number
            self.assertIn("[Unreleased]", errs[0])

    def test_an_empty_subsection_fails_and_a_well_formed_release_passes(self):
        # a `### Added` heading carrying no entry before the next heading -> empty.
        empty = ("# Changelog\n\n## [Unreleased]\n\n"
                 "### Added\n\n"                          # no entry before the next heading
                 "### Fixed\n\n- a fix\n\n"
                 "## [4.1.0] - 2026-07-14\n\n### Fixed\n\n- old\n")
        well_formed = ("# Changelog\n\n## [Unreleased]\n\n"
                       "### Added\n\n- an addition\n\n"
                       "### Fixed\n\n- a fix\n\n"
                       "## [4.1.0] - 2026-07-14\n\n### Fixed\n\n- old\n")
        with tempfile.TemporaryDirectory() as tmp:
            errs = self._errs(tmp, empty)
            self.assertTrue(any("empty" in e for e in errs), errs)
            self.assertIn("### Added", " ".join(errs))
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(self._errs(tmp, well_formed), [])   # discriminates, never blanket-refuses

    def test_compose_output_still_passes_the_structural_check(self):
        # compose CREATES a missing heading; the ordering rule must bind the writer too, or
        # compose and its own check end in a standoff. Two created sections exercise both
        # directions: Security must land AFTER Fixed (kills a head-insert), Breaking must land
        # BEFORE Added (kills an end-append).
        base = ("# Changelog\n\n## [Unreleased]\n\n"
                "### Added\n\n- existing added\n\n"
                "### Fixed\n\n- existing fixed\n\n"
                "## [4.1.0] - 2026-07-14\n\n- x\n")
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(tmp, changelog_text=base, fragments=[
                ("a-security.md", "<!-- section: Security -->\n- **a security fix.**\n"),
                ("b-breaking.md", "<!-- section: Breaking -->\n- **a breaking change.**\n")])
            self.assertEqual(changelog.structure_errors(root), [])   # sound before compose
            changelog.compose(root)
            self.assertEqual(changelog.structure_errors(root), [])   # and still sound after
            text = (root / "CHANGELOG.md").read_text(encoding="utf-8")
            unreleased = text.split("## [4.1.0]")[0]
            order = re.findall(r"^### ([A-Za-z]+)\s*$", unreleased, re.M)
            self.assertEqual(order, ["Breaking", "Added", "Fixed", "Security"])


if __name__ == "__main__":
    unittest.main()
