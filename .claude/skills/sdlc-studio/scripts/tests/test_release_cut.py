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


class ForgeCiTests(unittest.TestCase):
    """BG0576. Both v5 tags were cut over a CI that had been red for two days, because the tag
    guard read a locally recorded green and never asked the runner. These pin that a tag now
    turns on what the FORGE says, and that every way of not getting an answer refuses."""

    def setUp(self) -> None:
        self.mod = _load()

    def _forge(self, *, remote=True, gh=True, rc=0, stdout="[]", stderr="", boom=None):
        """Drive `forge_ci_state` against a scripted forge, with no network and no gh."""
        mod = self.mod

        class _P:
            def __init__(self, returncode, stdout, stderr):
                self.returncode, self.stdout, self.stderr = returncode, stdout, stderr

        def fake_run(cmd, *a, **k):
            if cmd[:2] == ["git", "remote"]:
                return _P(0, "origin\n" if remote else "", "")
            if boom is not None:
                raise boom
            return _P(rc, stdout, stderr)

        self.mod_patches = [
            (mod, "subprocess", type("S", (), {
                "run": staticmethod(fake_run),
                "SubprocessError": mod.subprocess.SubprocessError})),
            (mod.shutil, "which", (lambda n: "/usr/bin/gh" if gh else None)),
        ]
        for obj, name, val in self.mod_patches:
            self.addCleanup(setattr, obj, name, getattr(obj, name))
            setattr(obj, name, val)
        return mod

    @staticmethod
    def _runs(*pairs) -> str:
        import json as _j
        return _j.dumps([{"workflowName": w, "status": "completed", "conclusion": c}
                         for w, c in pairs])

    def test_a_failed_ci_conclusion_refuses_the_tag(self) -> None:
        """AC1. The exact state main was in when both v5 tags were cut: a run finished, and it
        finished red. MUTANT: report `failure` as `success` - this must then pass."""
        mod = self._forge(stdout=self._runs(("ci", "failure")))
        state, detail = mod.forge_ci_state(Path("."), "deadbee")
        self.assertEqual("failed", state)
        self.assertIn("ci: failure", detail)

    def test_a_commit_the_forge_has_never_run_refuses(self) -> None:
        """AC2. No run at all is not a green. MUTANT: return `success` for an empty run list."""
        mod = self._forge(stdout="[]")
        state, detail = mod.forge_ci_state(Path("."), "deadbee")
        self.assertEqual("none", state)
        self.assertIn("no CI run", detail)

    def test_a_forge_that_cannot_be_asked_refuses(self) -> None:
        """AC3. `gh` missing, unauthenticated or unparseable must not borrow the no-forge pass -
        "I could not look" is not "there is nothing wrong". MUTANT: return `no-forge` here."""
        for label, kwargs in (("no gh", {"gh": False}),
                              ("gh failed", {"rc": 1, "stderr": "not authenticated"}),
                              ("not json", {"stdout": "<html>"}),
                              ("gh raised", {"boom": OSError("boom")})):
            with self.subTest(label):
                mod = self._forge(**kwargs)
                state, _ = mod.forge_ci_state(Path("."), "deadbee")
                self.assertEqual("unknown", state, f"{label} was not refused")

    def test_an_unfinished_run_refuses_the_tag(self) -> None:
        """A tag cut while CI is still running asserts an outcome that has not happened."""
        mod = self._forge(stdout='[{"workflowName":"ci","status":"in_progress",'
                                 '"conclusion":null}]')
        state, detail = mod.forge_ci_state(Path("."), "deadbee")
        self.assertEqual("pending", state)
        self.assertIn("has not finished", detail)

    def test_a_green_forge_passes_and_a_skipped_run_does_not_block_it(self) -> None:
        """The positive control. A guard that always refuses is not a guard, and a path-filtered
        workflow reporting `skipped` beside a real success must stay taggable."""
        mod = self._forge(stdout=self._runs(("ci", "success"), ("release", "skipped")))
        state, _ = mod.forge_ci_state(Path("."), "deadbee")
        self.assertEqual("success", state)

    def test_all_skipped_is_not_a_green(self) -> None:
        """Nothing judged the tree, so there is nothing to assert."""
        mod = self._forge(stdout=self._runs(("ci", "skipped")))
        self.assertEqual("none", mod.forge_ci_state(Path("."), "deadbee")[0])

    def test_no_remote_is_the_one_honest_pass(self) -> None:
        """AC4 / the control that keeps `unknown` honest: there is genuinely no CI to ask about,
        which is why a missing `gh` had to be told apart from it. MUTANT: return `unknown`."""
        mod = self._forge(remote=False, gh=False)
        state, detail = mod.forge_ci_state(Path("."), "deadbee")
        self.assertEqual("no-forge", state)
        self.assertIn("no git remote", detail)

    def test_an_abbreviated_sha_is_resolved_before_the_forge_is_asked(self) -> None:
        """Found by the positive control, not by reasoning: `gh run list --commit` matches the
        FULL sha and answers nothing for an abbreviated one, so a green commit named short would
        have been refused as "never run". MUTANT: pass `commit` through unresolved."""
        mod = self.mod
        seen: list[str] = []

        class _P:
            def __init__(self, rc, out):
                self.returncode, self.stdout, self.stderr = rc, out, ""

        def fake_run(cmd, *a, **k):
            if cmd[:2] == ["git", "remote"]:
                return _P(0, "origin\n")
            if cmd[:2] == ["git", "rev-parse"]:
                return _P(0, "f" * 40 + "\n")
            seen.append(cmd[cmd.index("--commit") + 1])
            return _P(0, self._runs(("ci", "success")))

        self.addCleanup(setattr, mod, "subprocess", mod.subprocess)
        mod.subprocess = type("S", (), {"run": staticmethod(fake_run),
                                        "SubprocessError": mod.subprocess.SubprocessError})
        self.addCleanup(setattr, mod.shutil, "which", mod.shutil.which)
        mod.shutil.which = lambda n: "/usr/bin/gh"
        mod.forge_ci_state(Path("."), "f" * 8)
        self.assertEqual(["f" * 40], seen, "the forge was asked about an abbreviated sha")

    def test_tag_check_refuses_on_a_red_forge_and_says_why(self) -> None:
        """The wiring, not the helper: a locally green tree with a red runner must not tag."""
        mod = self.mod
        d = Path(tempfile.mkdtemp(prefix="forgetag_"))
        self.addCleanup(lambda: __import__("shutil").rmtree(d, ignore_errors=True))
        mod.record_green(d, "abc123")
        self.addCleanup(setattr, mod, "forge_ci_state", mod.forge_ci_state)
        mod.forge_ci_state = lambda root, commit: ("failed", "CI on abc123 did not pass (ci: failure)")
        allowed, reason = mod.tag_check(d, "abc123")
        self.assertFalse(allowed, "a tag was allowed over a red forge CI")
        self.assertIn("did not pass", reason)
        mod.forge_ci_state = lambda root, commit: ("success", "CI passed")
        allowed, reason = mod.tag_check(d, "abc123")
        self.assertTrue(allowed, reason)
        self.assertIn("CI green on the forge", reason)


if __name__ == "__main__":
    unittest.main()
