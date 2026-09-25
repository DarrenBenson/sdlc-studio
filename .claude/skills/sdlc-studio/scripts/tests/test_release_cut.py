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

    def test_a_git_that_cannot_answer_does_not_borrow_the_no_forge_pass(self) -> None:
        """BG0576 round 2, and the finding an independent review had to make because no test
        here could. `_has_forge_remote` returned a bare bool, so EVERY way git can fail - absent
        from PATH, a dubious-ownership refusal, a timeout, an unreadable `.git` - collapsed into
        `False`, which read as "no forge to ask" and PASSED the tag. That is the exact defect
        this unit exists to remove, re-created inside its own fix: a question that could not be
        asked, answered in the reassuring direction. The old test scripted only success-with-
        empty-output, so the failure path was untested in both directions.

        MUTANT: return `no-forge` for any git failure.
        """
        mod = self.mod

        class _P:
            def __init__(self, rc, out, err):
                self.returncode, self.stdout, self.stderr = rc, out, err

        for label, outcome in (
                ("git refuses for dubious ownership",
                 _P(128, "", "fatal: detected dubious ownership in repository")),
                ("git exits non-zero with no message", _P(128, "", "")),
                ("git is absent", OSError("No such file or directory: 'git'")),
                ("git times out", mod.subprocess.SubprocessError("timed out")),
        ):
            with self.subTest(label):
                def fake_run(cmd, *a, _o=outcome, **k):
                    if isinstance(_o, Exception):
                        raise _o
                    return _o
                self.addCleanup(setattr, mod, "subprocess", mod.subprocess)
                mod.subprocess = type("S", (), {
                    "run": staticmethod(fake_run),
                    "SubprocessError": mod.subprocess.SubprocessError})
                state, _ = mod.forge_ci_state(Path("."), "deadbee")
                self.assertEqual("unknown", state,
                                 f"{label}: an unanswered question passed the tag")

    def test_an_unreadable_repository_is_not_a_repository_without_a_remote(self) -> None:
        """The sharp edge of the same finding, and the reason the first repair was not enough:
        git prints `not a git repository` VERBATIM for a repository it cannot read. `chmod 000
        .git` produces it. Believing the message alone re-opened the defect one branch along, so
        it is now believed only when the filesystem agrees there is no `.git`.

        MUTANT: drop the `_git_dir_exists` corroboration.
        """
        d = Path(tempfile.mkdtemp(prefix="unreadable_"))
        self.addCleanup(lambda: __import__("shutil").rmtree(d, ignore_errors=True))
        (d / ".git").mkdir()
        (d / ".git" / "config").write_text("[remote \"origin\"]\n", encoding="utf-8")
        (d / ".git").chmod(0o000)
        self.addCleanup(lambda: (d / ".git").chmod(0o755))
        state, detail = self.mod.forge_ci_state(d, "deadbee")
        self.assertEqual("unknown", state,
                         f"an unreadable repository passed as having no forge: {detail}")
        # The positive control: a directory that genuinely holds no repository still passes.
        plain = Path(tempfile.mkdtemp(prefix="norepo_"))
        self.addCleanup(lambda: __import__("shutil").rmtree(plain, ignore_errors=True))
        self.assertEqual("no-forge", self.mod.forge_ci_state(plain, "deadbee")[0])

    def test_a_forge_gh_cannot_query_is_not_refused(self) -> None:
        """BG0576 round 2, second blocking finding. `release_cut.py` is SHIPPED, and the fix made
        every non-GitHub consumer permanently un-taggable with no override - while the shipped
        gate documentation states that nothing in it is GitHub-specific and carries a GitLab CI
        section. A bug fix may not invent a hard GitHub requirement the tool never had.

        `unsupported` is not `unknown`: a forge this code does not know HOW to ask is not a forge
        that would not answer, and the tag says out loud that CI was not consulted.

        MUTANT: fold `unsupported` back into `unknown`, or drop it from the allowed states.
        """
        mod = self._forge(rc=1, stderr="failed to determine base repo: none of the git remotes "
                                       "configured for this repository point to a known GitHub "
                                       "host. Try selecting a repository with --repo")
        state, detail = mod.forge_ci_state(Path("."), "deadbee")
        self.assertEqual("unsupported", state)
        self.assertIn("cannot be read from here", detail)
        d = Path(tempfile.mkdtemp(prefix="gitlab_"))
        self.addCleanup(lambda: __import__("shutil").rmtree(d, ignore_errors=True))
        mod.record_green(d, "abc123")
        self.addCleanup(setattr, mod, "forge_ci_state", mod.forge_ci_state)
        mod.forge_ci_state = lambda root, commit: ("unsupported", detail)
        allowed, reason = mod.tag_check(d, "abc123")
        self.assertTrue(allowed, f"a GitLab-hosted project could not tag at all: {reason}")
        self.assertIn("NOT consulted", reason,
                      "the tag passed without saying that CI was never read")

    def test_an_empty_commit_is_never_asked_about(self) -> None:
        """`gh run list --commit ""` IGNORES the filter and returns whatever ran most recently,
        so an empty commit would report success on another tree's evidence. Unreachable through
        `tag_check` today - the green stamp is compared first - but a guard that is safe only
        because of its caller is safe by luck. MUTANT: drop the empty-commit guard."""
        self.assertEqual("unknown", self.mod.forge_ci_state(Path("."), "")[0])
        self.assertEqual("unknown", self.mod.forge_ci_state(Path("."), "   ")[0])

    def test_a_flag_shaped_ref_is_not_resolved_as_a_flag(self) -> None:
        """`git rev-parse` echoes an argument-shaped value back with rc 0, so the resolve-to-a-
        full-sha contract was unenforced: `--output=/tmp/x` came back unchanged. It failed safe
        only because the bogus token then reached `gh` as a flag, which is safety by accident.
        MUTANT: drop `--verify --end-of-options`."""
        for bogus in ("--output=/tmp/pwn", "--since=2020-01-01", "-n1"):
            with self.subTest(bogus):
                self.assertEqual(bogus, self.mod._full_sha(Path("."), bogus),
                                 "a flag-shaped ref was resolved rather than passed through")

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

    def test_tag_check_refuses_every_forge_state_that_is_not_an_answer(self) -> None:
        """No run, an unfinished run and an unaskable forge are refusals at the TAG, not only in
        the helper. MUTANT: add any of the three to the states `tag_check` lets through."""
        mod = self.mod
        d = Path(tempfile.mkdtemp(prefix="forgetag_"))
        self.addCleanup(lambda: __import__("shutil").rmtree(d, ignore_errors=True))
        mod.record_green(d, "abc123")
        self.addCleanup(setattr, mod, "forge_ci_state", mod.forge_ci_state)
        for state in ("none", "pending", "unknown"):
            with self.subTest(state):
                detail = f"the forge said {state}"
                mod.forge_ci_state = lambda root, commit, _s=state, _d=detail: (_s, _d)
                allowed, reason = mod.tag_check(d, "abc123")
                self.assertFalse(allowed, f"a tag was allowed over a forge state of {state}")
                self.assertIn(detail, reason)


if __name__ == "__main__":
    unittest.main()
