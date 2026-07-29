"""US0348 / EP0117: the release cut composes the changelog fragments into a versioned section and
empties [Unreleased], and a tag is refused unless the gate was recorded green on the tagged commit.
"""
from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "release_cut.py"


def _load():
    spec = importlib.util.spec_from_file_location("release_cut", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["release_cut"] = mod
    spec.loader.exec_module(mod)
    return mod


BASE_CHANGELOG = (
    "# Changelog\n\n## [Unreleased]\n\n### Added\n\n- an existing unreleased line\n\n"
    "## [4.1.0] - 2026-07-14\n\n- old\n")


def _repo(root: Path, fragments=()) -> None:
    (root / "CHANGELOG.md").write_text(BASE_CHANGELOG, encoding="utf-8")
    d = root / "changelog.d"
    d.mkdir(parents=True, exist_ok=True)
    for name, body in fragments:
        (d / name).write_text(body, encoding="utf-8")


class ChangelogCutTests(unittest.TestCase):
    def test_the_section_is_cut_from_fragments_and_unreleased_is_emptied(self) -> None:
        """AC2. A pending fragment ends up in the new [5.0.0] section, [Unreleased] is emptied of
        it, and the fragment file is consumed (the release-time fold)."""
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _repo(root, fragments=[("US0001.md",
                                    "<!-- section: Added -->\n- **A shipped thing (US0001).**\n")])
            header = mod.cut_changelog(root, "5.0.0")
            text = (root / "CHANGELOG.md").read_text(encoding="utf-8")
            self.assertTrue(header.startswith("## [5.0.0] - "))
            # the fragment's line is in the 5.0.0 section...
            after_50 = text.split("## [5.0.0]", 1)[1]
            self.assertIn("A shipped thing (US0001)", after_50.split("## [4.1.0]", 1)[0])
            # ...and NOT left in [Unreleased]
            unreleased = text.split("## [Unreleased]", 1)[1].split("## [5.0.0]", 1)[0]
            self.assertNotIn("A shipped thing", unreleased)
            self.assertNotIn("existing unreleased line", unreleased)   # the whole body moved
            # the fragment was consumed
            self.assertFalse((root / "changelog.d" / "US0001.md").exists())
            # the fragments lane is clean afterwards (nothing stray)
            self.assertEqual(mod.changelog.check(root), [])

    def test_a_second_cut_of_the_same_version_is_refused(self) -> None:
        """The cut is not idempotent-by-accident: a repeat would duplicate the section."""
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _repo(root)
            mod.cut_changelog(root, "5.0.0")
            with self.assertRaises(ValueError):
                mod.cut_changelog(root, "5.0.0")

    def test_a_tag_is_refused_when_the_green_was_measured_elsewhere(self) -> None:
        """AC3. A tag of commit B is refused when the gate was recorded green on commit A, and the
        message names the commit that was actually judged."""
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / ".local").mkdir(parents=True, exist_ok=True)
            mod.record_green(root, "aaaaaaa")
            allowed, reason = mod.tag_check(root, "bbbbbbb")
            self.assertFalse(allowed)
            self.assertIn("aaaaaaa", reason)                 # names what was actually judged
            self.assertIn("bbbbbbb", reason)
            # the matching commit IS allowed
            ok, _ = mod.tag_check(root, "aaaaaaa")
            self.assertTrue(ok)

    def test_a_tag_with_no_recorded_green_is_refused(self) -> None:
        """No stamp at all is refused - a tag may not be cut on an unmeasured tree."""
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            allowed, reason = mod.tag_check(Path(d), "aaaaaaa")
            self.assertFalse(allowed)
            self.assertIn("no release gate", reason)


class TagRefusesAnOwedCloseTests(unittest.TestCase):
    """A tag is refused while any delivery unit owes a close, and the guard FAILS CLOSED.

    The first version of these tests replaced `_close_owed_units` with a lambda, so the
    function under test never ran and its exception-swallowing `return []` was invisible: the
    closing review showed that deleting or truncating one tracked baseline file turned the
    release guard off and made the tag report "no close is owed". These tests now drive the
    REAL function against a real workspace, and each of the three states it must tell apart is
    asserted separately."""

    def setUp(self) -> None:
        self.mod = _load()

    def _root(self, *, terminal: bool = True, baseline: str | None = "stamp") -> Path:
        """A workspace with one terminal, retro-less story and a baseline in a chosen state."""
        d = Path(tempfile.mkdtemp(prefix="tagcheck_"))
        self.addCleanup(__import__("shutil").rmtree, d, ignore_errors=True)
        ws = d / "sdlc-studio"
        (ws / "stories").mkdir(parents=True)
        (ws / ".local").mkdir(parents=True)
        # Written non-terminal when a baseline will be stamped, so the stamp cannot
        # grandfather the unit this fixture exists to catch.
        status = "In Progress" if (baseline == "stamp" or not terminal) else "Done"
        (ws / "stories" / "US0001-a-story.md").write_text(
            f"# US0001: a story\n\n> **Status:** {status}\n> **Epic:** EP0001\n",
            encoding="utf-8")
        (ws / "stories" / "_index.md").write_text(
            "# Story Index\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            f"| [US0001](US0001-a-story.md) | a story | {status} |\n", encoding="utf-8")
        marker = ws / ".close-owed-baseline.json"
        if baseline == "stamp":
            # Stamped while the unit is NOT yet terminal, then flipped - otherwise the baseline
            # grandfathers the very unit under test and the fixture asserts nothing. The
            # baseline forgives what was terminal at adoption; work that closes AFTER is owed.
            import close_owed
            close_owed.stamp_baseline(d)
            if terminal:
                for f in ((ws / "stories" / "US0001-a-story.md"),
                          (ws / "stories" / "_index.md")):
                    f.write_text(f.read_text(encoding="utf-8").replace("In Progress", "Done"),
                                 encoding="utf-8")
        elif baseline == "corrupt":
            marker.write_text("{ not json", encoding="utf-8")
        self.mod.record_green(d, "abc123")
        return d

    def test_a_tag_is_refused_while_a_close_is_owed(self) -> None:
        units, unknown = self.mod._close_owed_units(self._root())
        self.assertIsNone(unknown)
        self.assertIn("US0001", units, "a terminal unit with no retro is not owed?")
        allowed, reason = self.mod.tag_check(self._root(), "abc123")
        self.assertFalse(allowed)
        self.assertIn("no retro", reason)

    def test_a_corrupt_baseline_refuses_rather_than_reporting_clean(self) -> None:
        """THE finding. `gate._close_owed` calls this state a loud blocking refusal; the tag
        path read it as clean, so `git rm` on one tracked file disarmed the release guard."""
        root = self._root(baseline="corrupt")
        units, unknown = self.mod._close_owed_units(root)
        self.assertEqual([], units)
        self.assertIsNotNone(unknown, "an unreadable baseline read as clean")
        self.assertIn("unreadable", unknown)
        allowed, reason = self.mod.tag_check(root, "abc123")
        self.assertFalse(allowed, "a tag was allowed over an unreadable close-owed baseline")
        self.assertIn("refusing the tag", reason)

    def test_a_raising_helper_refuses_rather_than_reporting_clean(self) -> None:
        """The other swallowed state: nothing was judged, reported as though all was well.

        The helper is made to RAISE, not merely pointed at a path hoped to raise. The first
        version of this test called the real function against `/nonexistent/...`, which does not
        raise - it returns `{'baselined': False, ...}` - so the test exercised the no-baseline
        branch, never asserted `unknown`, and the mutant restoring `except: return [], None`
        survived the full suite."""
        import close_owed
        real_owed = close_owed.owed
        self.addCleanup(setattr, close_owed, "owed", real_owed)

        def boom(_root):
            raise RuntimeError("the report could not be produced")

        close_owed.owed = boom
        units, unknown = self.mod._close_owed_units(self._root())
        self.assertEqual([], units)
        self.assertIsNotNone(unknown, "a raising helper reported a clean close-owed answer")
        self.assertIn("UNKNOWN", unknown)
        self.assertIn("could not be produced", unknown)

    def test_an_unreadable_delivery_tree_refuses_rather_than_reporting_clean(self) -> None:
        """The fourth state, and the one the previous repair missed.

        `read_text_safe` and `walk_glob` swallow their own I/O errors, so `owed()` never raised
        and the new `except` never fired: an unreadable tree returned an empty unit list, which
        is indistinguishable from a clean one. `chmod 000 sdlc-studio/stories` turned a correct
        refusal into "no close is owed" - the same fail-open, one frame down the stack."""
        root = self._root()
        units, unknown = self.mod._close_owed_units(root)
        self.assertIn("US0001", units, "the fixture is not owed a close - nothing is asserted")

        stories = root / "sdlc-studio" / "stories"
        os.chmod(stories, 0o000)
        self.addCleanup(os.chmod, stories, 0o755)
        if os.access(stories, os.R_OK):        # running as root: the mode cannot be enforced
            self.skipTest("cannot make a directory unreadable for this user")

        units, unknown = self.mod._close_owed_units(root)
        self.assertEqual([], units)
        self.assertIsNotNone(unknown, "an unreadable delivery tree read as a clean one")
        self.assertIn("could not be read", unknown)
        allowed, reason = self.mod.tag_check(root, "abc123")
        self.assertFalse(allowed, "a tag was allowed over a delivery tree nobody could scan")
        self.assertIn("refusing the tag", reason)

    def test_an_unbaselined_project_is_not_refused_on_its_history(self) -> None:
        """The one state that legitimately passes, and the reason `corrupt` had to be told
        apart from it: without a baseline there is no adopted rule to hold this project to."""
        root = self._root(baseline=None)
        units, unknown = self.mod._close_owed_units(root)
        self.assertEqual(([], None), (units, unknown))

    def test_a_tag_with_nothing_owed_is_allowed(self) -> None:
        """A gate that always refuses is not a gate."""
        allowed, reason = self.mod.tag_check(self._root(terminal=False, baseline=None), "abc123")
        self.assertTrue(allowed, reason)
        self.assertIn("no close is owed", reason)

    def test_the_commit_mismatch_still_refuses_first(self) -> None:
        allowed, reason = self.mod.tag_check(self._root(baseline=None), "different")
        self.assertFalse(allowed)
        self.assertIn("not the commit being tagged", reason)


if __name__ == "__main__":
    unittest.main()
