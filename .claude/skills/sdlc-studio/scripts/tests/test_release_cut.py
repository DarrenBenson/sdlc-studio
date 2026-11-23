"""US0348 / EP0117: the release cut composes the changelog fragments into a versioned section and
empties [Unreleased], and a tag is refused unless the gate was recorded green on the tagged commit.
"""
from __future__ import annotations

import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import test_evidence_pack_build as epb  # noqa: E402 - its signed-report project, shared

SCRIPT = Path(__file__).resolve().parent.parent / "release_cut.py"
SPRINT_REPORT = SCRIPT.parent / "sprint_report.py"
TEMPLATE = SCRIPT.parent.parent / "templates" / "workflows" / "release-gate.md"


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


def _git(root: Path, *argv: str) -> str:
    return gitutil.git(list(argv), root, text=True).stdout.strip()


def _commit(root: Path, message: str = "c") -> str:
    """Commit everything under `root` (an empty commit when nothing changed); the new full sha."""
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "--allow-empty", "-m", message)
    return _git(root, "rev-parse", "HEAD")


def _git_repo(case: unittest.TestCase, commits: int = 1) -> tuple[Path, list[str]]:
    """A throwaway repository with no remote and `commits` empty commits; (root, full shas)."""
    d = tempfile.TemporaryDirectory(prefix="release_cut_")
    case.addCleanup(d.cleanup)
    root = Path(d.name)
    _git(root, "init", "-q")
    return root, [_commit(root, f"c{i}") for i in range(commits)]


def _cli(script: Path, root: Path, *argv: str) -> subprocess.CompletedProcess:
    """A shipped entry point run as a subprocess, confined to the fixture's repository."""
    return subprocess.run([sys.executable, "-B", str(script), "--root", str(root), *argv],
                          capture_output=True, text=True, env=gitutil.git_env(), timeout=300,
                          check=False)


def _confine(case: unittest.TestCase) -> None:
    """The in-process git calls read the fixture's repository and never one an inherited
    GIT_DIR names."""
    patch = mock.patch.dict(os.environ, gitutil.git_env(), clear=True)
    patch.start()
    case.addCleanup(patch.stop)


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
        _confine(self)
        root, (a, b) = _git_repo(self, commits=2)
        mod.record_green(root, a)
        allowed, reason = mod.tag_check(root, b)
        self.assertFalse(allowed)
        self.assertIn(a, reason)                             # names what was actually judged
        self.assertIn(b, reason)
        # the matching commit IS allowed
        ok, _ = mod.tag_check(root, a)
        self.assertTrue(ok)

    def test_a_tag_with_no_recorded_green_is_refused(self) -> None:
        """No stamp at all is refused - a tag may not be cut on an unmeasured tree."""
        mod = _load()
        _confine(self)
        root, (a,) = _git_repo(self)
        allowed, reason = mod.tag_check(root, a)
        self.assertFalse(allowed)
        self.assertIn("no release gate", reason)

    @staticmethod
    def _cut_fixture(root: Path, changelog: str) -> tuple[Path, Path]:
        """CHANGELOG.md as given and one pending Fixed fragment; (changelog, fragment)."""
        (root / "CHANGELOG.md").write_text(changelog, encoding="utf-8")
        (root / "changelog.d").mkdir()
        frag = root / "changelog.d" / "BG0001.md"
        frag.write_text("<!-- section: Fixed -->\n\n- **A pending fix (BG0001).**\n",
                        encoding="utf-8")
        return root / "CHANGELOG.md", frag

    CUT_ONCE = "# Changelog\n\n## [Unreleased]\n\n## [1.0.0] - 2026-01-01\n\n- first\n"

    def _cut(self, root: Path, version: str) -> tuple[int, str]:
        err = io.StringIO()
        with mock.patch("sys.stderr", err), mock.patch("sys.stdout", io.StringIO()):
            code = _load().main(["--root", str(root), "changelog-cut", "--version", version])
        return code, err.getvalue()

    def test_a_refused_second_cut_leaves_the_changelog_and_fragments_untouched(self) -> None:
        """BG1544 AC1. A version that already has a section is refused BEFORE the fragments are
        composed: the refusal says nothing was cut, so nothing may have been. MUTANT: compose
        ahead of the duplicate-section check - the fragment is folded and deleted."""
        with tempfile.TemporaryDirectory() as d:
            clog, frag = self._cut_fixture(Path(d), self.CUT_ONCE)
            before = (clog.read_bytes(), frag.read_bytes())
            code, err = self._cut(Path(d), "1.0.0")
            self.assertEqual(2, code, err)
            self.assertIn("already carries a ## [1.0.0] section", err)
            self.assertTrue(frag.is_file(), "the refused cut consumed the pending fragment")
            self.assertEqual(before, (clog.read_bytes(), frag.read_bytes()))

    def test_a_cut_with_no_unreleased_section_consumes_no_fragment(self) -> None:
        """BG1544 AC2. No [Unreleased] section is refused before anything is composed, and with
        no fragment pending the cut itself names the missing section rather than failing on
        it. MUTANT: drop the cut's own [Unreleased] check."""
        with tempfile.TemporaryDirectory() as d:
            clog, frag = self._cut_fixture(Path(d), "# Changelog\n\n## [1.0.0] - 2026-01-01\n")
            before = (clog.read_bytes(), frag.read_bytes())
            code, err = self._cut(Path(d), "1.1.0")
            self.assertEqual(2, code, err)
            self.assertIn("no '## [Unreleased]' section", err)
            self.assertEqual(before, (clog.read_bytes(), frag.read_bytes()))
            frag.unlink()
            code, err = self._cut(Path(d), "1.1.0")
            self.assertEqual(2, code, err)
            self.assertIn("no '## [Unreleased]' section to cut from", err)
            self.assertEqual(before[0], clog.read_bytes())

    def test_a_new_version_still_folds_the_pending_fragment(self) -> None:
        """BG1544 AC3. The positive control: the reordered checks still let a new version
        through, folding the fragment into its section and consuming the file."""
        with tempfile.TemporaryDirectory() as d:
            clog, frag = self._cut_fixture(Path(d), self.CUT_ONCE)
            code, err = self._cut(Path(d), "1.1.0")
            self.assertEqual(0, code, err)
            self.assertFalse(frag.exists(), "the cut left the folded fragment behind")
            text = clog.read_text(encoding="utf-8")
            section = text.split("## [1.1.0] - ", 1)[1].split("## [1.0.0]", 1)[0]
            self.assertIn("A pending fix (BG0001)", section)
            self.assertNotIn("A pending fix", text.split("## [1.1.0]", 1)[0])


class EvidencePackVerbTests(unittest.TestCase):
    """The `evidence-pack` verb parses its own arguments and hands them to `evidence_pack.py`,
    which holds the logic; `test_evidence_pack_build.py` drives the pack end to end."""

    def test_the_verb_delegates_to_the_pack_builder(self) -> None:
        rc = _load()
        sys.path.insert(0, str(SCRIPT.parent))
        import evidence_pack  # noqa: PLC0415
        seen = []
        real = evidence_pack.write_pack
        evidence_pack.write_pack = lambda *a: seen.append(a) or Path(a[0])
        try:
            with tempfile.TemporaryDirectory() as d:
                code = rc.main(["--root", d, "evidence-pack", "--version", "6.4.0",
                                "--reports", " rpt0001, RPT0002,RPT0001"])
        finally:
            evidence_pack.write_pack = real
        self.assertEqual(code, 0)
        self.assertEqual(len(seen), 1)
        self.assertEqual(seen[0][1:], ("6.4.0", ["RPT0001", "RPT0002"], "HEAD"))

    def test_a_refusal_exits_non_zero_with_the_reason(self) -> None:
        rc = _load()
        with tempfile.TemporaryDirectory() as d, \
                mock.patch("sys.stderr", new_callable=io.StringIO) as err:
            code = rc.main(["--root", d, "evidence-pack", "--version", "../6.4.0",
                            "--reports", "RPT0001"])
        self.assertEqual(code, 2)
        self.assertIn("evidence-pack refused", err.getvalue())
        self.assertIn("../6.4.0", err.getvalue())


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
        real = (self.mod.subprocess, self.mod.shutil.which)
        mod = self._forge(rc=1, stderr="failed to determine base repo: none of the git remotes "
                                       "configured for this repository point to a known GitHub "
                                       "host. Try selecting a repository with --repo")
        state, detail = mod.forge_ci_state(Path("."), "deadbee")
        self.assertEqual("unsupported", state)
        self.assertIn("cannot be read from here", detail)
        # The tag half resolves its commits with the real git, so the scripted forge is lifted.
        mod.subprocess, mod.shutil.which = real
        _confine(self)
        d, (sha,) = _git_repo(self)
        mod.record_green(d, sha)
        self.addCleanup(setattr, mod, "forge_ci_state", mod.forge_ci_state)
        mod.forge_ci_state = lambda root, commit: ("unsupported", detail)
        allowed, reason = mod.tag_check(d, sha)
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
        _confine(self)
        d, (sha,) = _git_repo(self)
        mod.record_green(d, sha)
        self.addCleanup(setattr, mod, "forge_ci_state", mod.forge_ci_state)
        mod.forge_ci_state = lambda root, commit: ("failed", "CI on abc123 did not pass (ci: failure)")
        allowed, reason = mod.tag_check(d, sha)
        self.assertFalse(allowed, "a tag was allowed over a red forge CI")
        self.assertIn("did not pass", reason)
        mod.forge_ci_state = lambda root, commit: ("success", "CI passed")
        allowed, reason = mod.tag_check(d, sha)
        self.assertTrue(allowed, reason)
        self.assertIn("CI green on the forge", reason)

    def test_tag_check_refuses_every_forge_state_that_is_not_an_answer(self) -> None:
        """No run, an unfinished run and an unaskable forge are refusals at the TAG, not only in
        the helper. MUTANT: add any of the three to the states `tag_check` lets through."""
        mod = self.mod
        _confine(self)
        d, (sha,) = _git_repo(self)
        mod.record_green(d, sha)
        self.addCleanup(setattr, mod, "forge_ci_state", mod.forge_ci_state)
        for state in ("none", "pending", "unknown"):
            with self.subTest(state):
                detail = f"the forge said {state}"
                mod.forge_ci_state = lambda root, commit, _s=state, _d=detail: (_s, _d)
                allowed, reason = mod.tag_check(d, sha)
                self.assertFalse(allowed, f"a tag was allowed over a forge state of {state}")
                self.assertIn(detail, reason)



class TagCheckResolvesCommitsTests(unittest.TestCase):
    """BG1542. The stamp and the tagged commit were compared as the strings typed, so green
    recorded on HEAD matched HEAD after another commit, a tree the gate never ran on. Both sides
    are now full shas, through the shipped verbs, in a repository with no remote."""

    def test_a_symbolic_ref_recorded_at_one_commit_is_refused_at_another(self) -> None:
        """AC1. MUTANT: store the `--commit` argument unresolved - the stamp holds HEAD and the
        second commit passes."""
        root, (first,) = _git_repo(self)
        r = _cli(SCRIPT, root, "record-green", "--commit", "HEAD")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn(first, r.stdout)
        second = _commit(root, "after the gate")
        r = _cli(SCRIPT, root, "tag-check", "--commit", "HEAD")
        self.assertEqual(2, r.returncode, r.stdout + r.stderr)
        self.assertIn(f"recorded green on {first}", r.stderr)
        self.assertIn(second, r.stderr)
        # The positive control from the report: full shas on both sides, refused the same way.
        _cli(SCRIPT, root, "record-green", "--commit", first)
        r = _cli(SCRIPT, root, "tag-check", "--commit", second)
        self.assertEqual(2, r.returncode, r.stdout + r.stderr)
        self.assertIn(first, r.stderr)

    def test_both_sides_are_compared_as_full_shas(self) -> None:
        """AC2. A symbolic ref and an abbreviated sha are each stamped as the full sha, and an
        abbreviated sha of the stamped commit is allowed. MUTANT: compare the `--commit`
        argument unresolved - the short spelling is refused."""
        root, (first,) = _git_repo(self)
        _git(root, "branch", "release")
        stamp = root / "sdlc-studio" / ".local" / "release-gate-green.json"
        # A name typed with surrounding whitespace is the name, as the stamp always took it.
        for spelling in ("HEAD", "release", first[:9], f" {first[:9]}\n"):
            with self.subTest(spelling):
                r = _cli(SCRIPT, root, "record-green", "--commit", spelling)
                self.assertEqual(0, r.returncode, r.stdout + r.stderr)
                self.assertEqual({"commit": first}, json.loads(stamp.read_text(encoding="utf-8")))
        r = _cli(SCRIPT, root, "tag-check", "--commit", first[:8])
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn(f"gate green on {first} matches the tagged commit", r.stdout)

    def test_an_unresolvable_commit_is_refused_and_stamps_nothing(self) -> None:
        """AC3. A name git cannot resolve to a commit is refused by both verbs, naming it, and
        `record-green` writes no stamp - nor replaces one already there. MUTANT: write the stamp
        before resolving, or pass an unresolved name through."""
        root, (first,) = _git_repo(self)
        tree = _git(root, "rev-parse", "HEAD^{tree}")
        stamp = root / "sdlc-studio" / ".local" / "release-gate-green.json"
        for bogus in ("no-such-ref", "0" * 40, tree, "--output=x"):
            with self.subTest(bogus):
                r = _cli(SCRIPT, root, "record-green", f"--commit={bogus}")
                self.assertEqual(2, r.returncode, r.stdout + r.stderr)
                self.assertIn(f"`{bogus}` does not resolve to a commit", r.stderr)
                self.assertFalse(stamp.exists(), f"{bogus} was stamped")
                r = _cli(SCRIPT, root, "tag-check", f"--commit={bogus}")
                self.assertEqual(2, r.returncode, r.stdout + r.stderr)
                self.assertIn(f"`{bogus}` does not resolve to a commit", r.stderr)
        _cli(SCRIPT, root, "record-green", "--commit", first)
        held = stamp.read_bytes()
        r = _cli(SCRIPT, root, "record-green", "--commit", "no-such-ref")
        self.assertEqual(2, r.returncode, r.stdout + r.stderr)
        self.assertEqual(held, stamp.read_bytes(), "a refused record-green replaced the stamp")

    def test_a_stamp_written_before_the_fix_is_read_safely(self) -> None:
        """A stamp an older record-green left holds whatever was typed. An abbreviated sha still
        names one commit, so it is resolved and matched; a name such as HEAD moves with every
        commit, so it is refused rather than resolved to whatever it names today. MUTANT:
        resolve every stored name - an old HEAD stamp passes any commit."""
        root, (first,) = _git_repo(self)
        stamp = root / "sdlc-studio" / ".local" / "release-gate-green.json"
        stamp.parent.mkdir(parents=True)
        stamp.write_text(json.dumps({"commit": first[:10]}) + "\n", encoding="utf-8")
        r = _cli(SCRIPT, root, "tag-check", "--commit", first)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        _git(root, "branch", "release")
        # A name (upper or lower case), an abbreviated and a full sha no commit here holds.
        for held in ("HEAD", "release", "0" * 12, "1" * 40):
            with self.subTest(held):
                stamp.write_text(json.dumps({"commit": held}) + "\n", encoding="utf-8")
                r = _cli(SCRIPT, root, "tag-check", "--commit", first)
                self.assertEqual(2, r.returncode, r.stdout + r.stderr)
                self.assertIn(f"the release gate stamp holds `{held}`", r.stderr)


EVIDENCE_SHELL = ("# Evidence\n\nHand-written prose above the table.\n\n"
                  "<!-- BEGIN GENERATED -->\n<!-- END GENERATED -->\n\nProse below it.\n")
CUT_CHANGELOG = "# Changelog\n\n## [Unreleased]\n\n## [6.4.0] - 2026-11-12\n\n- shipped\n"
PACK = "sdlc-studio/reports/evidence-pack-6.4.0.md"
PAGE = "docs/evidence.md"


class GeneratedPagesFreshTests(unittest.TestCase):
    """BG1510. The evidence page and the evidence pack are generated at the cut, but reports are
    signed and records change after it, so a tag shipped pages naming an older last report and,
    for 6.4, no pack at all. `tag-check` now compares both with the records at the tagged
    commit, once the commit holds a generated page, or a cut version with a signed report."""

    def _release(self, *, pack: bool = True) -> Path:
        """A committed project with signed reports RPT0001, RPT0002 and RPT0004, a cut 6.4.0,
        and the evidence page (and, unless told not to, the pack) generated from them."""
        d = tempfile.TemporaryDirectory(prefix="release_pages_")
        self.addCleanup(d.cleanup)
        root = Path(d.name)
        epb.project(root)
        epb.write(root, "CHANGELOG.md", CUT_CHANGELOG)
        epb.write(root, PAGE, EVIDENCE_SHELL)
        self._regenerate(root, page=True, pack=pack)
        return root

    def _regenerate(self, root: Path, *, page: bool, pack: bool) -> None:
        """Run the shipped generators over the records, then commit what they wrote."""
        if page:
            r = _cli(SPRINT_REPORT, root, "evidence", "--out", PAGE)
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        if pack:
            r = _cli(SCRIPT, root, "evidence-pack", "--version", "6.4.0",
                     "--reports", "RPT0001,RPT0002")
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        _commit(root, "regenerated")

    def _tag(self, root: Path) -> subprocess.CompletedProcess:
        """Record the gate green on HEAD and ask whether HEAD may be tagged."""
        sha = _git(root, "rev-parse", "HEAD")
        r = _cli(SCRIPT, root, "record-green", "--commit", sha)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        return _cli(SCRIPT, root, "tag-check", "--commit", sha)

    def test_tag_check_refuses_an_evidence_page_that_lags_a_later_signature(self) -> None:
        """AC1. A report signed after the page was written is named, with the page and the
        command that regenerates it; a page regenerated but left uncommitted is not the page
        the commit holds. MUTANT: read the page or the reports from the working tree."""
        root = self._release()
        epb.seal(root, epb.report("RPT0005", [("US0002", epb.S2, 1, "delivered")],
                                  epb.signature("RPT0005", "Lee Operator", "2026-11-20T10:00:00Z")))
        _commit(root, "a later signature")
        r = self._tag(root)
        self.assertEqual(2, r.returncode, r.stdout + r.stderr)
        self.assertIn(f"{PAGE} does not carry RPT0005", r.stderr)
        self.assertIn(f"`sprint_report.py evidence --out {PAGE}`", r.stderr)
        self.assertNotIn(PACK, r.stderr, "the pack names RPT0001 and RPT0002, still current")
        r = _cli(SPRINT_REPORT, root, "evidence", "--out", PAGE)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        r = self._tag(root)
        self.assertEqual(2, r.returncode, "a page regenerated but not committed passed")
        self.assertIn(f"{PAGE} does not carry RPT0005", r.stderr)
        _commit(root, "the page regenerated")
        r = self._tag(root)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        # Every report is there, but the generated table was edited by hand.
        page = root / PAGE
        page.write_text(page.read_text(encoding="utf-8").replace(
            "<!-- END GENERATED -->", "A line typed into the table.\n<!-- END GENERATED -->"),
            encoding="utf-8")
        _commit(root, "the generated region edited by hand")
        r = self._tag(root)
        self.assertEqual(2, r.returncode, r.stdout + r.stderr)
        self.assertIn(f"{PAGE} differs from what the signed reports at the tagged commit render",
                      r.stderr)

    def test_tag_check_refuses_a_missing_or_stale_evidence_pack(self) -> None:
        """AC2. No pack for the cut version, then a pack built before a record it summarises
        changed, are each refused naming the pack and the `evidence-pack` command. MUTANT:
        accept any pack that exists, or skip the pack when the page is current."""
        root = self._release(pack=False)
        r = self._tag(root)
        self.assertEqual(2, r.returncode, r.stdout + r.stderr)
        self.assertIn(f"release 6.4.0 has no evidence pack at {PACK}", r.stderr)
        self.assertIn("`release_cut.py evidence-pack --version 6.4.0 --reports", r.stderr)
        self._regenerate(root, page=False, pack=True)
        fresh = _git(root, "rev-parse", "HEAD")
        self.assertEqual(0, self._tag(root).returncode)
        story = root / epb.S1
        story.write_text(story.read_text(encoding="utf-8").replace(
            "# US0001: Widgets carry a colour", "# US0001: Widgets carry a colour and a size"),
            encoding="utf-8")
        _commit(root, "a summarised record changes after the pack")
        r = self._tag(root)
        self.assertEqual(2, r.returncode, r.stdout + r.stderr)
        self.assertIn(f"{PACK} was built before the records it summarises last changed",
                      r.stderr)
        self.assertIn("`release_cut.py evidence-pack --version 6.4.0 --reports "
                      "RPT0001,RPT0002`", r.stderr)
        self.assertNotIn(f"{PAGE} ", r.stderr, "the page is current: only the pack is stale")
        # The commit named is the one judged, not HEAD: the earlier commit's pack was current.
        _cli(SCRIPT, root, "record-green", "--commit", fresh)
        r = _cli(SCRIPT, root, "tag-check", "--commit", fresh)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        # A pre-release cut is the version that owes the pack, not the release below it.
        epb.write(root, "CHANGELOG.md", CUT_CHANGELOG.replace(
            "## [6.4.0]", "## [6.5.0-rc.1] - 2026-11-22\n\n- next\n\n## [6.4.0]"))
        _commit(root, "a pre-release cut")
        r = self._tag(root)
        self.assertEqual(2, r.returncode, r.stdout + r.stderr)
        self.assertIn("release 6.5.0-rc.1 has no evidence pack", r.stderr)
        self.assertNotIn("6.4.0", r.stderr)

    def test_tag_check_passes_once_the_pages_and_pack_are_regenerated(self) -> None:
        """AC3. Regenerated from the records at the commit, with the gate green on it, the tag
        passes. MUTANT: compare the pack with its build commit left in, so every pack built
        before the commit that carries it reads stale."""
        root = self._release()
        # Only the reports are read from the reports directory: a binary file beside them is
        # not a record the tag waits on.
        (root / "sdlc-studio" / "reports" / "burndown.png").write_bytes(b"\x89PNG\r\n\xff\xfe")
        _commit(root, "a chart beside the reports")
        built_at = (root / PACK).read_text(encoding="utf-8")
        self.assertNotIn(_git(root, "rev-parse", "HEAD")[:12], built_at,
                         "the fixture's pack must be built on an earlier commit than it is tagged at")
        r = self._tag(root)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("matches the tagged commit", r.stdout)

    def test_the_release_gate_workflow_names_the_pre_tag_regeneration_step(self) -> None:
        """AC4. The shipped checklist tells the operator when to regenerate: after the last
        signature and filing, before the tag, with `tag-check` named as what refuses."""
        text = TEMPLATE.read_text(encoding="utf-8")
        item = next((block for block in text.split("\n- [ ] ")
                     if "Regenerate the generated release pages" in block), "")
        self.assertTrue(item, "no pre-tag regeneration step in the release-gate workflow")
        for needed in ("after the last signature", "filing", "sprint_report.py\" evidence --out",
                       "known_issues.py write --release", "release_cut.py\" evidence-pack",
                       "release_cut.py\" tag-check", "refuses"):
            self.assertIn(needed, item, needed)
        self.assertLess(text.index("Regenerate the generated release pages"),
                        text.index("## 6. Post-tag"), "the step must come before the tag")

    def test_the_gate_help_names_every_question_the_tag_asks(self) -> None:
        """help/gate.md said the tag asked only about the gate and CI; it now asks about the
        generated release records too, and the page says so."""
        text = " ".join((SCRIPT.parent.parent / "help" / "gate.md").read_text(
            encoding="utf-8").split())
        self.assertNotIn("the release tag asks only whether", text)
        self.assertIn("the generated evidence page and the evidence pack for the version "
                      "CHANGELOG.md last cut are current with the signed reports it holds", text)

    def test_no_cut_version_or_no_signed_report_owes_no_pack(self) -> None:
        """The scope: a pack is owed only for a cut version whose project has a signed report,
        and a page is judged only when it carries the generation markers, so a project that
        adopted neither tags as before. MUTANT: owe the pack on either condition alone, or
        judge a page with no markers."""
        d = tempfile.TemporaryDirectory(prefix="release_scope_")
        self.addCleanup(d.cleanup)
        signed = Path(d.name) / "signed"
        signed.mkdir()
        epb.project(signed)                          # signed reports, no CHANGELOG cut, no page
        # With neither a page nor a cut version the reports are not read at all, so not even
        # one that cannot be parsed stands in the way of a project that adopted neither.
        broken = signed / "sdlc-studio" / "reports" / "RPT0009.json"
        broken.write_text("{not json", encoding="utf-8")
        _commit(signed, "a report that is not JSON")
        r = self._tag(signed)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        broken.unlink()
        epb.write(signed, PAGE, "# Evidence\n\nWritten by hand, no generated table.\n")
        _commit(signed, "a hand-written page")
        r = self._tag(signed)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        # Each record is judged on its own condition: a generated page with no cut version...
        epb.write(signed, PAGE, EVIDENCE_SHELL)
        _commit(signed, "a generated page, never generated, and no cut")
        r = self._tag(signed)
        self.assertEqual(2, r.returncode, r.stdout + r.stderr)
        self.assertIn(f"{PAGE} does not carry RPT0001, RPT0002", r.stderr)
        self.assertNotIn("evidence pack", r.stderr)
        # ...and a cut version with signed reports and no page at all.
        (signed / PAGE).unlink()
        epb.write(signed, "CHANGELOG.md", CUT_CHANGELOG)
        _commit(signed, "a cut, and no page")
        r = self._tag(signed)
        self.assertEqual(2, r.returncode, r.stdout + r.stderr)
        self.assertIn(f"release 6.4.0 has no evidence pack at {PACK}", r.stderr)
        self.assertNotIn(PAGE, r.stderr)
        cut = Path(d.name) / "cut"
        cut.mkdir()
        _git(cut, "init", "-q")
        epb.write(cut, "CHANGELOG.md", CUT_CHANGELOG)  # a cut version, no signed report
        _commit(cut, "cut")
        r = self._tag(cut)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)

    def test_a_project_below_the_repository_root_is_read_at_its_own_paths(self) -> None:
        """The records are read relative to the project root, which need not be the
        repository's: a project in a subdirectory tags once its pages are current, and is
        refused once they lag. MUTANT: read each record at the repository root's path."""
        d = tempfile.TemporaryDirectory(prefix="release_subdir_")
        self.addCleanup(d.cleanup)
        top = Path(d.name)
        root = top / "project"
        root.mkdir()
        epb.project(root)
        shutil.move(str(root / ".git"), str(top / ".git"))
        _commit(top, "the project moved below the repository root")
        epb.write(root, "CHANGELOG.md", CUT_CHANGELOG)
        epb.write(root, PAGE, EVIDENCE_SHELL)
        self._regenerate(root, page=True, pack=True)
        self.assertEqual("project", _git(top, "ls-tree", "--name-only", "HEAD"))
        r = self._tag(root)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        epb.seal(root, epb.report("RPT0005", [("US0002", epb.S2, 1, "delivered")],
                                  epb.signature("RPT0005", "Lee Operator", "2026-11-20T10:00:00Z")))
        _commit(root, "a later signature")
        r = self._tag(root)
        self.assertEqual(2, r.returncode, r.stdout + r.stderr)
        self.assertIn(f"{PAGE} does not carry RPT0005", r.stderr)

    def test_a_record_that_cannot_be_read_refuses_and_says_which(self) -> None:
        """A generated page with broken markers, a pack that is not UTF-8 and a report that is
        not JSON each refuse naming the file, never a traceback and never a pass."""
        root = self._release()
        page = root / PAGE
        good_page = page.read_bytes()
        page.write_text(page.read_text(encoding="utf-8").replace("<!-- END GENERATED -->", ""),
                        encoding="utf-8")
        _commit(root, "markers broken")
        r = self._tag(root)
        self.assertEqual(2, r.returncode, r.stdout + r.stderr)
        self.assertIn(f"{PAGE}: 1 BEGIN and 0 END marker(s)", r.stderr)
        page.write_bytes(good_page)
        pack = (root / PACK).read_text(encoding="utf-8")
        (root / PACK).write_text(pack.replace("over the signed reports RPT0001, RPT0002.",
                                              "over some reports."), encoding="utf-8")
        _commit(root, "a pack whose header names no report")
        r = self._tag(root)
        self.assertEqual(2, r.returncode, r.stdout + r.stderr)
        self.assertIn(f"{PACK} names no signed reports in its header", r.stderr)
        (root / PACK).write_text(pack.replace("RPT0001, RPT0002.", "RPT0001, RPT0003."),
                                 encoding="utf-8")
        _commit(root, "a pack naming an unsigned report")
        r = self._tag(root)
        self.assertEqual(2, r.returncode, r.stdout + r.stderr)
        self.assertIn(f"{PACK} cannot be rebuilt from the records committed at", r.stderr)
        self.assertIn("RPT0003", r.stderr)
        (root / PACK).write_bytes(b"# Evidence pack: release 6.4.0\n\n\xff\xfe\n")
        _commit(root, "a pack that is not UTF-8")
        r = self._tag(root)
        self.assertEqual(2, r.returncode, r.stdout + r.stderr)
        self.assertIn(f"{PACK} at ", r.stderr)
        self.assertIn("is not UTF-8 text", r.stderr)
        self.assertNotIn("Traceback", r.stderr)
        (root / "sdlc-studio" / "reports" / "RPT0009.json").write_text("{not json",
                                                                         encoding="utf-8")
        _commit(root, "a report that is not JSON")
        r = self._tag(root)
        self.assertEqual(2, r.returncode, r.stdout + r.stderr)
        self.assertIn("sdlc-studio/reports/RPT0009.json could not be read", r.stderr)
        self.assertNotIn("Traceback", r.stderr)

    def test_a_git_that_cannot_answer_refuses_rather_than_passes(self) -> None:
        """git failing or absent while the records are read is an unanswered question, so the
        tag is refused as UNKNOWN, and `record-green` stamps nothing it could not resolve.
        MUTANT: read a failed git's empty output as "the commit holds no such file"."""
        mod = _load()
        _confine(self)
        root = self._release()
        sha = _git(root, "rev-parse", "HEAD")
        mod.record_green(root, sha)
        real = subprocess.run

        def failing(answer, stderr=b""):
            def run(cmd, *a, **k):
                if cmd[:2] == ["git", "ls-tree"]:
                    if isinstance(answer, Exception):
                        raise answer
                    return subprocess.CompletedProcess(cmd, answer, b"", stderr)
                return real(cmd, *a, **k)
            return run

        # Each refusal says why git failed: its own words, else its exit status.
        for label, answer, stderr, why in (
                ("git refuses", 128, b"fatal: bad object\n", ": fatal: bad object"),
                ("git refuses silently", 128, b"", ": exit 128"),
                ("git is absent", OSError("no git"), b"", "OSError('no git')")):
            with self.subTest(label), \
                    mock.patch.object(mod.subprocess, "run", failing(answer, stderr)):
                allowed, reason = mod.tag_check(root, sha)
                self.assertFalse(allowed, f"{label}: an unread record passed the tag")
                self.assertIn("could not be read, so whether it is current is UNKNOWN", reason)
                self.assertIn(f"git could not read {PAGE} at {sha[:12]}", reason)
                self.assertIn(why, reason)
        with mock.patch.object(mod.subprocess, "run", side_effect=OSError("no git")):
            with self.assertRaises(ValueError):
                mod.record_green(root, sha)

        def failed_with_output(cmd, *a, **k):
            if cmd[:2] == ["git", "rev-parse"]:
                return subprocess.CompletedProcess(cmd, 128, sha + "\n", "fatal: bad revision")
            return real(cmd, *a, **k)

        # A rev-parse that exits non-zero is never an answer, whatever it printed.
        with mock.patch.object(mod.subprocess, "run", failed_with_output):
            with self.assertRaises(ValueError):
                mod.record_green(root, sha)

if __name__ == "__main__":
    unittest.main()
