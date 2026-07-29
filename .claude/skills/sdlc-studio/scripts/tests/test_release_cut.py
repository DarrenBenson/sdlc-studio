"""US0348 / EP0117: the release cut composes the changelog fragments into a versioned section and
empties [Unreleased], and a tag is refused unless the gate was recorded green on the tagged commit.
"""
from __future__ import annotations

import importlib.util
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
    """BG0311. `--require-close` was documented as enforced "at the push/release moment" and ran
    at neither. The TAG is where it is unambiguously right: a release that ships work no sprint
    closed asserts a record that was never written."""

    def setUp(self) -> None:
        self.mod = _load()

    def _root(self, owed: list[str], *, baselined: bool = True) -> Path:
        d = Path(tempfile.mkdtemp(prefix="tagcheck_"))
        self.addCleanup(__import__("shutil").rmtree, d, ignore_errors=True)
        (d / "sdlc-studio" / ".local").mkdir(parents=True)
        self.mod.record_green(d, "abc123")
        self._patch(owed, baselined=baselined)
        return d

    def _patch(self, owed: list[str], *, baselined: bool = True) -> None:
        real = self.mod._close_owed_units
        self.addCleanup(setattr, self.mod, "_close_owed_units", real)
        self.mod._close_owed_units = lambda _root: list(owed)

    def test_a_tag_is_refused_while_a_close_is_owed(self) -> None:
        allowed, reason = self.mod.tag_check(self._root(["US0001", "BG0002"]), "abc123")
        self.assertFalse(allowed)
        self.assertIn("US0001", reason)
        self.assertIn("no retro", reason)

    def test_a_tag_with_nothing_owed_is_allowed(self) -> None:
        """The discriminating half - a gate that always refuses is not a gate."""
        allowed, reason = self.mod.tag_check(self._root([]), "abc123")
        self.assertTrue(allowed, reason)
        self.assertIn("no close is owed", reason)

    def test_the_commit_mismatch_still_refuses_first(self) -> None:
        """The pre-existing rule keeps its precedence: a green measured on another tree is the
        more fundamental refusal, and its message must not be replaced by this one."""
        allowed, reason = self.mod.tag_check(self._root([]), "different")
        self.assertFalse(allowed)
        self.assertIn("not the commit being tagged", reason)

    def test_an_unbaselined_project_is_not_refused_on_its_history(self) -> None:
        """Without a stamped baseline the report lists every terminal unit ever, which would
        refuse a first tag on history nobody adopted the rule for."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / ".local").mkdir(parents=True)
            self.assertEqual([], self.mod._close_owed_units(root))


if __name__ == "__main__":
    unittest.main()
