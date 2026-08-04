"""Repo-only test for the tracked .githooks/commit-msg gate.

The hook's DECISION logic is unit-tested in the shipped engagement_floor suite
(CommitMsgCheckTests). This test exercises the bash gate end-to-end, the way git invokes
it (a message file path as $1): a multi-id subject with no `Refs:` trailer is REFUSED
(non-zero, the commit does not land), the same subject with the trailers passes, and the
things it deliberately still lets through keep passing - a solo id, a merge, a revert, a
fixup/squash, and every honest-degrade case (no script / unreadable message).
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / ".githooks" / "commit-msg"


def _run(message: str, *, path: str | None = None, cwd: str | None = None,
         env_extra: dict[str, str] | None = None, mid_operation: str | None = None):
    """Run the commit-msg hook against `message` in a HERMETIC fixture repo.

    The hook resolves its repo root and git dir from wherever it runs; run in the OUTER repo it
    reads the outer repo's state, and while THAT repo is mid-merge (which happens whenever the
    pre-commit suite runs during a merge commit) its in-progress-operation guard exits the hook
    early and every refusal test passes vacuously, or - worse - fails because the refusal never
    ran (BG0281). So each call builds its own throwaway git repo and runs the hook there.

    The checker (`engagement_floor.py` and its `lib/`) is made present via a symlinked `scripts`
    dir at the path the hook resolves, so the refusal actually executes - the isolation does not
    make the test vacuous (AC2). `mid_operation` writes the named in-progress marker into the
    FIXTURE's git dir, so the mid-merge behaviour is exercised deliberately rather than inherited.
    """
    with tempfile.TemporaryDirectory() as d:
        repo = Path(d)
        clean = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull,
                 "GIT_CONFIG_SYSTEM": os.devnull}
        for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
            clean.pop(name, None)
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True, env=clean)
        scripts = repo / ".claude" / "skills" / "sdlc-studio"
        scripts.mkdir(parents=True)
        (scripts / "scripts").symlink_to(
            REPO / ".claude" / "skills" / "sdlc-studio" / "scripts")
        if mid_operation:
            (repo / ".git" / mid_operation).write_text("x\n", encoding="utf-8")
        msg = repo / "COMMIT_EDITMSG"
        msg.write_text(message, encoding="utf-8")
        env = dict(clean)
        env.update(env_extra or {})
        target = path if path is not None else str(msg)
        return subprocess.run(["bash", str(HOOK), target], capture_output=True,
                              text=True, env=env, cwd=cwd if cwd is not None else str(repo))


class CommitMsgGateTests(unittest.TestCase):
    """The load-bearing pair: refuse the bare multi-id subject, pass the trailered one."""

    def test_multi_id_without_refs_is_refused(self):
        r = _run("feat(CR0257, CR0258): batch fix")
        self.assertNotEqual(r.returncode, 0,
                            "a multi-id subject with no Refs: trailer must REFUSE the commit")
        out = r.stdout + r.stderr
        # The refusal has to be cheap to satisfy: the exact trailer lines, ready to paste.
        self.assertIn("Refs: CR0257", out)
        self.assertIn("Refs: CR0258", out)
        self.assertIn("--no-verify", out)  # the one escape, named

    def test_multi_id_with_refs_trailers_passes(self):
        r = _run("feat(CR0257, CR0258): batch fix\n\nRefs: CR0257\nRefs: CR0258\n")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual((r.stdout + r.stderr).strip(), "")

    def test_multi_id_with_comma_list_trailer_passes(self):
        r = _run("feat(CR0257, CR0258): batch fix\n\nRefs: CR0257, CR0258\n")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_partially_covered_multi_id_is_refused_naming_the_gap(self):
        r = _run("feat(CR0257, CR0258): batch fix\n\nRefs: CR0257\n")
        self.assertNotEqual(r.returncode, 0)
        out = r.stdout + r.stderr
        self.assertIn("Refs: CR0258", out)


class DeliberatelyAllowedTests(unittest.TestCase):
    """What the gate lets through on purpose. Each of these must keep passing."""

    def test_solo_id_without_a_trailer_passes(self):
        # One id: attribution is unambiguous, the floor's git leg already handles it.
        r = _run("fix(BG0134): the hook now refuses")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_no_id_passes(self):
        r = _run("docs: tidy the README")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_merge_subject_passes(self):
        # git wrote this message; the author cannot restructure it.
        r = _run("Merge pull request #7 from x (CR0257, CR0258)")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_revert_subject_passes(self):
        r = _run('Revert "feat(CR0257, CR0258): batch fix"\n\nThis reverts commit deadbeef.\n')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_fixup_and_squash_subjects_pass(self):
        for prefix in ("fixup! ", "squash! ", "amend! "):
            with self.subTest(prefix=prefix):
                r = _run(prefix + "feat(CR0257, CR0258): batch fix")
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_commented_scaffolding_is_ignored(self):
        # git's scaffolding (# lines, and in verbose mode the diff) is not the subject.
        msg = ("# Please enter the commit message...\n"
               "# On branch main\n"
               "fix(BG0134): solo\n")
        r = _run(msg)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


class HonestDegradeTests(unittest.TestCase):
    def test_missing_message_file_does_not_block(self):
        r = _run("", path="/nonexistent/COMMIT_EDITMSG")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_no_argument_does_not_block(self):
        r = subprocess.run(["bash", str(HOOK)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_outside_a_repo_carrying_the_script_degrades_to_pass(self):
        with tempfile.TemporaryDirectory() as elsewhere:
            r = _run("feat(CR0257, CR0258): batch fix", cwd=elsewhere)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


class InProgressOperationTests(unittest.TestCase):
    """A replayed/machine-written message (merge, revert, cherry-pick, rebase) is exempt:
    the author did not type it, and the work it records was gated on its original commit.
    Exercised in a throwaway git repo that symlinks this repo's skill scripts, so the
    real repo's .git is never touched."""

    def _sandbox(self, d: str) -> Path:
        root = Path(d)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        os.symlink(REPO / ".claude", root / ".claude")
        return root

    def test_multi_id_is_refused_in_the_sandbox_without_a_marker(self):
        # The negative control: proves the sandbox itself is not what lets the next
        # test's commit through - the marker is.
        with tempfile.TemporaryDirectory() as d:
            root = self._sandbox(d)
            r = _run("feat(CR0257, CR0258): batch fix", cwd=str(root))
            self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_in_progress_markers_exempt_the_commit(self):
        for marker in ("MERGE_HEAD", "REVERT_HEAD", "CHERRY_PICK_HEAD", "rebase-merge"):
            with self.subTest(marker=marker), tempfile.TemporaryDirectory() as d:
                root = self._sandbox(d)
                target = root / ".git" / marker
                if marker == "rebase-merge":
                    target.mkdir()
                else:
                    target.write_text("deadbeef\n", encoding="utf-8")
                r = _run("feat(CR0257, CR0258): batch fix", cwd=str(root))
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


class NoSecondBypassTests(unittest.TestCase):
    def test_the_old_strict_env_var_is_not_a_bypass(self):
        # SDLC_ENGAGEMENT_STRICT used to be the opt-in to block. Blocking is now the
        # behaviour; no env var may turn the gate back off (--no-verify is the one escape).
        for value in ("0", "", "1"):
            with self.subTest(value=value):
                r = _run("feat(CR0257, CR0258): batch fix",
                         env_extra={"SDLC_ENGAGEMENT_STRICT": value})
                self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)


class MidMergeIsolationTests(unittest.TestCase):
    """BG0281: a conflicted merge could not be committed through the gate, because these very
    tests failed while the outer repo was mid-merge - they inherited its MERGE_HEAD and saw the
    hook's correct early exit. The fixture is now hermetic, so the outer state cannot leak in."""

    def test_the_refusal_still_fires_while_the_OUTER_repo_is_mid_merge(self):
        # The regression proof: even if the outer repo carries MERGE_HEAD right now, a bare
        # multi-id subject is still refused, because the hook reads the fixture's state.
        r = _run("feat(CR0257, CR0258): batch fix")
        self.assertNotEqual(r.returncode, 0,
                            "the hook read the outer repo's merge state instead of the fixture's")
        self.assertIn("Refs: CR0258", r.stdout + r.stderr)

    def test_the_fixture_is_not_vacuous_the_checker_actually_ran(self):
        # AC2: a passing trailered commit must be the CHECKER passing, not the checker being
        # absent. The refusal test above already proves the checker fires; this proves the
        # symlinked checker resolves (a bad symlink would make the hook exit 0 on a bare subject).
        r = _run("feat(CR0257, CR0258): batch fix\n\nRefs: CR0257\nRefs: CR0258\n")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_a_marker_in_the_fixture_itself_exits_early_as_designed(self):
        # AC3, the intended behaviour isolated: with the fixture ITSELF mid-merge, the hook
        # exits 0 on a multi-id subject - so a real merge commit is never blocked by the gate.
        r = _run("feat(CR0257, CR0258): merge two branches", mid_operation="MERGE_HEAD")
        self.assertEqual(r.returncode, 0,
                         "the hook must not block a commit while a merge is genuinely in progress")


class UnnamedUnitAttributionTests(unittest.TestCase):
    """US0417/CR0416, through the bash hook rather than the library: a commit whose staged files
    belong to a unit the message never names gets an advisory NOTE and still lands. The refusal
    path stays the multi-id rule's alone - ownership here is read from a declaration, and a gate
    that blocked on an inference would be switched off within a week."""

    SUBJECT = "fix(BG0276): the ungroomed count sees the legacy scaffold"

    def _fixture(self, d: str, *, second_owner: bool = False) -> Path:
        """A repo carrying two bugs and one staged MODIFICATION to a source file.

        `second_owner` makes BG0276 declare the same file, so it has two owners - the ambiguous
        case that must not be reported.
        """
        repo = Path(d)
        clean = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull,
                 "GIT_CONFIG_SYSTEM": os.devnull}
        for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
            clean.pop(name, None)
        self._env = clean
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True, env=clean)
        scripts = repo / ".claude" / "skills" / "sdlc-studio"
        scripts.mkdir(parents=True)
        (scripts / "scripts").symlink_to(
            REPO / ".claude" / "skills" / "sdlc-studio" / "scripts")
        bugs = repo / "sdlc-studio" / "bugs"
        bugs.mkdir(parents=True)
        owned = "src/sprint.py" if second_owner else "src/conformance.py"
        (bugs / "BG0276-sample.md").write_text(
            f"# BG0276: sample\n\n> **Status:** Fixed\n> **Affects:** {owned}\n", encoding="utf-8")
        (bugs / "BG0268-sample.md").write_text(
            "# BG0268: sample\n\n> **Status:** Fixed\n> **Affects:** src/sprint.py\n",
            encoding="utf-8")
        (repo / "src").mkdir()
        (repo / "src" / "sprint.py").write_text("x = 1\n", encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=repo, check=True, env=clean)
        subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q",
                        "-m", "seed"], cwd=repo, check=True, env=clean)
        # ... then MODIFY it, which is what the lane reads (an addition is a filing, not an
        # attribution).
        (repo / "src" / "sprint.py").write_text("x = 2\n", encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=repo, check=True, env=clean)
        return repo

    def _hook(self, repo: Path, message: str):
        msg = repo / "COMMIT_EDITMSG"
        msg.write_text(message, encoding="utf-8")
        return subprocess.run(["bash", str(HOOK), str(msg)], capture_output=True, text=True,
                              env=self._env, cwd=str(repo))

    def test_a_file_owned_by_an_unnamed_unit_is_reported(self):
        with tempfile.TemporaryDirectory() as d:
            repo = self._fixture(d)
            r = self._hook(repo, self.SUBJECT + "\n")
            out = r.stdout + r.stderr
            self.assertEqual(r.returncode, 0, out)   # advisory: the commit is NOT blocked
            self.assertIn("BG0268", out)
            self.assertIn("Refs: BG0268", out)       # the remedy, ready to paste
            self.assertIn("advisory", out)

    def test_a_shared_or_unowned_file_does_not_refuse(self):
        with tempfile.TemporaryDirectory() as d:
            repo = self._fixture(d, second_owner=True)
            r = self._hook(repo, self.SUBJECT + "\n")
            out = r.stdout + r.stderr
            self.assertEqual(r.returncode, 0, out)
            self.assertNotIn("BG0268", out)          # two owners: no claim about whose work it is
            self.assertEqual(out.strip(), "", out)   # ... and a clean run stays silent


class _VerdictPlacementFixture:
    """The executing fixture shared by the verdict-placement classes below.

    Deliberately NOT a `TestCase`. Subclassing one to reuse its fixture also inherits its
    tests, and they would re-run under the subclass's `collapse` setting - where a blocked
    commit is the correct outcome, so the inherited control failed while the hook was right.
    A fixture is not a test, and mixing the two is how a suite starts asserting the wrong
    thing about itself.

    Reaching the suite section needs the handoff `pre-commit` leaves at
    `$git_dir/sdlc-gate-suites`; without it the hook exits before the lanes, and a test that
    forgot it would pass vacuously on every mutant.
    """

    #: When set, the fixture ships a `tools/gate_timing.py` whose `scope` subcommand exits 3
    #: with a note - the COLLAPSE verdict (BG0507). Absent, no such file exists and the hook's
    #: honest-degrade path takes the silent `else` branch, which is the shape every other test
    #: in this class runs under.
    collapse: bool = False

    def _fixture(self, d: str, *, tool_lane_passes: bool) -> tuple[Path, dict]:
        """A repo whose skill lane always passes and whose tool lane is the parameter.

        The skill lane is a stub script printing a plausible `Ran N tests` line, because the hook
        parses that for the budget lane. The tool lane is a REAL unittest module discovered the
        way the hook discovers it, so the failure travels the same path a genuine red test does
        rather than through a stub's exit code.
        """
        repo = Path(d)
        clean = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull,
                 "GIT_CONFIG_SYSTEM": os.devnull}
        for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
            clean.pop(name, None)
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True, env=clean)
        scripts = repo / ".claude" / "skills" / "sdlc-studio"
        scripts.mkdir(parents=True)
        (scripts / "scripts").symlink_to(
            REPO / ".claude" / "skills" / "sdlc-studio" / "scripts")
        tools = repo / "tools"
        tools.mkdir()
        (tools / "skill-tests.sh").write_text(
            '#!/bin/sh\necho "Ran 3 tests in 0.100s"\nexit 0\n', encoding="utf-8")
        tests = tools / "tests"
        tests.mkdir()
        (tests / "test_probe.py").write_text(
            "import unittest\n\n\nclass T(unittest.TestCase):\n"
            f"    def test_probe(self):\n        self.assertTrue({tool_lane_passes})\n",
            encoding="utf-8")
        if self.collapse:
            # `scope` exits 3 with a note - the collapse verdict. Every other subcommand exits 0
            # silently, so `record` and `budget` behave as they do in a normal run and the only
            # thing this stub changes is the one branch under test.
            (tools / "gate_timing.py").write_text(
                "import sys\n"
                "if len(sys.argv) > 1 and sys.argv[1] == 'scope':\n"
                "    print('COLLAPSE: 3 tests ran where the surface demands far more')\n"
                "    sys.exit(3)\n"
                "sys.exit(0)\n", encoding="utf-8")
        # The handoff pre-commit leaves behind; without it the hook exits before the lanes.
        (repo / ".git" / "sdlc-gate-suites").write_text("precommit_seconds=1\n", encoding="utf-8")
        return repo, clean

    def _run(self, *, tool_lane_passes: bool):
        with tempfile.TemporaryDirectory() as d:
            repo, env = self._fixture(d, tool_lane_passes=tool_lane_passes)
            msg = repo / "COMMIT_EDITMSG"
            msg.write_text("fix(BG0489): probe\n", encoding="utf-8")
            r = subprocess.run(["bash", str(HOOK), str(msg)], capture_output=True, text=True,
                               env=env, cwd=str(repo))
            verdict = repo / "sdlc-studio" / ".local" / "gate-suite-verdict.json"
            return r, (json.loads(verdict.read_text(encoding="utf-8"))
                       if verdict.is_file() else None)

class SuiteVerdictIsEarnedByBothLanesTests(_VerdictPlacementFixture, unittest.TestCase):
    """A green suite verdict is written only when BOTH lanes actually passed - proven by RUNNING
    the hook, not by reading it.

    `SuiteVerdictFailOpenTests` in `test_precommit_lane_order.py` already asserts the placement
    and the guard, and every one of those assertions is a `text.index` over the hook's source.
    That is precisely why this defect survived its own repair twice: the verdict write moved out
    from under the failing lane, then moved to sit BETWEEN the lanes, and a grep for
    `if [ "$fail" -eq 0 ]` was green on both shapes. A source-order assertion also cannot see a
    refactor that keeps the text order and changes when the write executes - hoisting it into a
    function called earlier, say.

    So this class executes the hook against a fixture repo whose two lanes are controlled
    independently, and asserts on the verdict FILE the next commit would read.
    `test_the_control_case_records_a_green_verdict` is what makes a vacuous pass impossible to
    miss: it fails if the lanes never ran.
    """

    def test_a_failing_tool_lane_writes_no_green_verdict(self):
        """MUTANT: move the `--record-suite-verdict` call above `run "tool-tests"`.

        That is the exact shape BG0423's repair left behind and BG0489 was filed on: the skill
        lane passes, `$fail` is still 0, a green verdict is written, and then the tool lane fails
        and blocks the commit. The byte-identical retry reads that green and runs no tests at all.
        """
        r, verdict = self._run(tool_lane_passes=False)
        out = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0, "a failing tool lane must block the commit")
        # The lane must actually have RUN and FAILED. Without this the criterion is satisfied
        # by a hook that exits 1 before reaching any lane - review demonstrated it, replacing
        # the hook with `exit 1` and watching this test pass in 4ms. AC2 catches that case, but
        # AC1's Verify line is a standalone `-k` invocation, so anybody running the criterion
        # as written would get a green from a hook that reached nothing.
        self.assertIn("FAIL tool-tests", out,
                      f"the tool lane never ran, so this proves nothing:\n{out}")
        self.assertIsNone(
            verdict,
            "the hook recorded a suite verdict though the tool-tests lane FAILED - the next "
            f"byte-identical attempt would reuse it and skip both suites. Verdict: {verdict}")

    def test_the_control_case_records_a_green_verdict(self):
        """MUTANT: delete the `--record-suite-verdict` call entirely.

        Without this the refusal above is satisfied by a hook that never records anything, and
        the reuse path the verdict exists for would be unreachable in production however well it
        is tested. It is also what proves the fixture reaches the lanes at all.
        """
        r, verdict = self._run(tool_lane_passes=True)
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, out)
        self.assertIn("ok   tool-tests", out, "the fixture never reached the tool lane")
        self.assertIsNotNone(verdict, "two passing lanes recorded no verdict")
        self.assertEqual(verdict["status"], "green", verdict)


class ACollapsedSuiteLeavesNoReusableGreenTests(_VerdictPlacementFixture, unittest.TestCase):
    """BG0507: the third door into the same fail-open.

    BG0423 wrote the verdict unconditionally; BG0489 moved it under `$fail` but left it between
    the lanes. Both are closed. This one is reached through the SCOPE check: the guard that sets
    `fail=1` on a collapsed suite - far fewer tests run than the surface demands - executed
    AFTER the verdict had already been written. So the commit was blocked and `status green`
    was left at that HEAD, and since `pre-commit` skips the suites when a current green verdict
    covers the surface, the byte-identical retry landed the collapsed suite.

    Inherits the executing fixture deliberately. The two tests above are the controls for this
    one: they prove the lanes are reached and that a green run still records, so a refusal here
    cannot be satisfied by a hook that reached nothing.
    """

    collapse = True

    def test_a_collapsed_suite_writes_no_green_verdict(self):
        """MUTANT: move the `--record-suite-verdict` block back above the scope check.

        Both lanes PASS here - that is what makes this the third door rather than a restatement
        of BG0489. `fail` is 0 when the scope check runs, so the pre-fix hook wrote green and
        only then set `fail=1`. Asserting on the verdict FILE rather than on the exit code is
        what separates the two: the exit code was already correct before the fix.
        """
        r, verdict = self._run(tool_lane_passes=True)
        out = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0, f"a collapsed suite must block the commit:\n{out}")
        self.assertIn("COLLAPSE", out, f"the scope lane never ran, so this proves nothing:\n{out}")
        self.assertIsNone(
            verdict,
            "the hook recorded a green suite verdict though the suite COLLAPSED - pre-commit "
            "reuses it over an unchanged surface, so the byte-identical retry lands the "
            f"collapsed suite having run no tests at all. Verdict: {verdict}")

    def test_both_lanes_still_passed(self):
        """The premise, asserted rather than assumed.

        If the collapse stub also broke a lane, the refusal above would be BG0489's shape
        wearing this one's name and would pass against the unfixed hook. This is the assertion
        that makes the class honest about which door it is testing.
        """
        r, _ = self._run(tool_lane_passes=True)
        out = r.stdout + r.stderr
        self.assertIn("ok   tool-tests", out, f"the tool lane did not pass:\n{out}")
        self.assertIn("ok   skill-tests", out, f"the skill lane did not pass:\n{out}")


if __name__ == "__main__":
    unittest.main()
