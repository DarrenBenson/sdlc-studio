"""changelog.py - per-unit fragments composed deterministically (US0188/CR0315).

The honesty properties: compose is idempotent (fragments are consumed), a
malformed fragment is refused naming the file, a stray fragment fails a release
(never silently dropped from a cut), and a fragment satisfies the
changelog-empty documentation check.
"""
import pathlib
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


if __name__ == "__main__":
    unittest.main()
