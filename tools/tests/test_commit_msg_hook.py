"""Repo-only test for the tracked .githooks/commit-msg gate.

The hook's DECISION logic is unit-tested in the shipped engagement_floor suite
(CommitMsgCheckTests). This test exercises the bash gate end-to-end, the way git invokes
it (a message file path as $1): a multi-id subject with no `Refs:` trailer is REFUSED
(non-zero, the commit does not land), the same subject with the trailers passes, and the
things it deliberately still lets through keep passing - a solo id, a merge, a revert, a
fixup/squash, and every honest-degrade case (no script / unreadable message).
"""
# test-selection: sweep HookInvocationHermeticityTests 0.2s
from __future__ import annotations

import json
import os
import pathlib
import re
import subprocess
import tempfile
import unittest
import unittest.mock
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
#: A passing hook prints one summary line unless SDLC_GATE_VERBOSE=1, and this module reads the
#: per-lane list a pass prints, so every hook it runs inherits SDLC_GATE_VERBOSE=1. The quiet pass
#: and the replay of a refusal are pinned in tools/tests/test_quiet_hooks.py.
_VERBOSE = unittest.mock.patch.dict(os.environ, {"SDLC_GATE_VERBOSE": "1"})


def setUpModule() -> None:
    _VERBOSE.start()


def tearDownModule() -> None:
    _VERBOSE.stop()

HOOK = REPO / ".githooks" / "commit-msg"


def _run(message: str, *, path: str | None = None, cwd: str | None = None,
         env_extra: dict[str, str] | None = None, mid_operation: str | None = None,
         no_argument: bool = False, plant_handoff: bool = False,
         strip_caller_identity: bool = False):
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
        if strip_caller_identity:
            # BG0595 AC3: the paired leg. A probe on a caller-identity variable is green under
            # the identity leg alone, because this fixture's own env carries PYTEST_CURRENT_TEST
            # through - it is `{**os.environ}` minus three GIT_* keys. Only the stripped leg
            # tells such a probe apart from an honest message-absent exit.
            for name in ("PYTEST_CURRENT_TEST", "PYTEST_VERSION", "TOX_ENV_NAME", "CI"):
                env.pop(name, None)
        if plant_handoff:
            # The record `pre-commit` leaves for the suite lanes. The hook CONSUMES it (`rm -f`)
            # at the point it enters those lanes, so its survival is the observable for "did
            # this invocation enter the suite block" - no output parsing, no timing.
            (repo / ".git" / "sdlc-gate-suites").write_text(
                "precommit_seconds=1\n", encoding="utf-8")
        argv = ["bash", str(HOOK)]
        if not no_argument:
            argv.append(path if path is not None else str(msg))
        r = subprocess.run(argv, capture_output=True, text=True, env=env,
                           cwd=cwd if cwd is not None else str(repo))
        if plant_handoff:
            # Stashed on the result so the caller can assert it without reaching into the
            # tempdir after it is gone.
            r.entered_suite_block = not (repo / ".git" / "sdlc-gate-suites").exists()
        return r


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
        # The message rule is a `run` lane (US0901): its verdict line and nothing else.
        self.assertEqual((r.stdout + r.stderr).strip(), "ok   message-refs")

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
        # BG0595 AC4: an explicit cwd and a git-scrubbed env, like every other invocation in
        # this file. Without them this ran the hook against the REAL repository, consumed the
        # `sdlc-gate-suites` record a commit was going to use, and started a full skill suite
        # inside a unit test. One exemption in twenty-five was the whole defect.
        r = _run("", path=None, no_argument=True)
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
            # ... and a clean run prints only the message lane's verdict (US0901)
            self.assertEqual(out.strip(), "ok   message-refs", out)


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

    WITHOUT_PYTEST = "(runs only without pytest"

    @staticmethod
    def _lanes_by_path() -> tuple[set, set]:
        """The lanes the hook's source calls on the pytest path and on the path taken only when
        the selected run did not use pytest: the `else` of the pytest test, and the block guarded
        by `ran_pytest` being 0. Read from the hook itself, so a lane moved between the two
        moves its expected marking with it."""
        on_pytest, without = set(), set()
        region = None
        for line in HOOK.read_text(encoding="utf-8").splitlines():
            if line.startswith("if [ -n \"$selectors\" ] && python3 -c 'import pytest'"):
                region = "pytest"
            elif line.startswith('if [ "$ran_pytest" -eq 0 ]'):
                region = "without"
            elif line == "else" and region == "pytest":
                region = "without"
            elif line == "fi" and region:
                region = None
            m = re.match(r'\s*run "([^"]+)"', line)
            if m:
                (without if region == "without" else on_pytest).add(m.group(1))
        return on_pytest, without

    def test_the_lane_list_marks_lanes_that_run_only_without_pytest(self):
        """BG1519 AC4. MUTANTS: drop the marking from one of the three lanes; mark a lane that
        runs on the pytest path; move a lane into the no-pytest branch without marking it; a TSD
        `full-suite` row silent on the count floor."""
        listed = subprocess.run(["bash", str(HOOK), "--list"], cwd=REPO, capture_output=True,
                                text=True, timeout=60,
                                env={k: v for k, v in os.environ.items() if not k.startswith("GIT_")})
        self.assertEqual(0, listed.returncode, listed.stderr)
        rules = dict(line.split("\t", 1) for line in listed.stdout.splitlines() if "\t" in line)
        on_pytest, without = self._lanes_by_path()
        self.assertEqual({"suite-collapse", "skill-tests", "tool-tests"}, without,
                         "the lanes the hook runs only without pytest are not the three named today")
        self.assertIn("unit-tests", on_pytest, "the reader did not find the pytest path's lane")
        for key, rule in rules.items():
            with self.subTest(lane=key):
                if key in without:
                    self.assertIn(self.WITHOUT_PYTEST, rule,
                                  f"{key} runs only without pytest and its listed rule does not say so")
                else:
                    self.assertIn(key, on_pytest, f"{key} is listed but not called by the hook")
                    self.assertNotIn(self.WITHOUT_PYTEST, rule,
                                     f"{key} runs on the pytest path and is marked as not")
        for key in without:
            self.assertIn(key, rules, f"{key} is called by the hook but not listed")
        tsd = (REPO / "sdlc-studio" / "tsd.md").read_text(encoding="utf-8")
        row = next((ln for ln in tsd.splitlines() if ln.startswith("| `full-suite` |")), "")
        for phrase in ("count floor", "nothing was collected", "every test was skipped",
                       "`gate.py --run-tests`"):
            self.assertIn(phrase, row, f"the TSD full-suite row does not state the floor: {row}")


class MessageAbsentTests(unittest.TestCase):
    """BG0595. An invocation with no message file has no commit to gate.

    The observable throughout is the `sdlc-gate-suites` record: the hook `rm -f`s it at the
    point it enters the suite lanes, so its SURVIVAL means the lanes were not entered. That is
    a byte on disk rather than a timing or an output match, and it cannot be satisfied by the
    hook merely being slow or quiet.
    """

    def test_no_message_file_does_not_enter_the_suite_block(self):
        """MUTANT: in `commit-msg`, remove the early exit for an invocation carrying no
        message file. Without it the hook falls through to the handoff block, consumes the
        record and runs the lanes."""
        r = _run("", no_argument=True, plant_handoff=True)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertFalse(r.entered_suite_block,
                         "an invocation with no message file entered the suite-running block "
                         "and consumed the handoff record")

    def test_a_present_message_still_reaches_the_suite_block(self):
        """MUTANT: in `commit-msg`, make the message-absent exit unconditional.

        The CONTROL. Without it the criterion above is satisfied by a hook that never enters the
        suite block at all, which would disable the lanes rather than scope them.

        The mutant is the OVER-REACH, not a failure-when-no-record: this fixture PLANTS the
        record, so any mutant conditioned on its absence is pre-empted and survives. Two earlier
        cuts of this row named exactly that, and both were measured surviving by independent
        review.
        """
        r = _run("fix(BG0489): probe", plant_handoff=True)
        self.assertTrue(r.entered_suite_block,
                        "a real commit message did not reach the suite block - the exit is "
                        "over-reaching, and the lanes are now off for everybody:\n"
                        + r.stdout + r.stderr)

    def test_the_exit_is_the_absent_message_not_the_caller(self):
        """MUTANT: in `commit-msg`, gate the early exit on the caller being a test, via a
        `PYTEST_CURRENT_TEST` probe.

        THE PAIRED INVOCATION, and it is the whole criterion. The identity leg ALONE is green
        under that mutant, because this file's own fixture carries `PYTEST_CURRENT_TEST`
        through - `clean` is `{**os.environ}` minus three GIT_* keys. Only running the same
        invocation with the caller-identity signals stripped tells an honest message-absent
        exit apart from a probe for who is calling. A caller probe is also the second bypass
        this repo forbids by name.
        """
        with_identity = _run("", no_argument=True, plant_handoff=True)
        without_identity = _run("", no_argument=True, plant_handoff=True,
                                strip_caller_identity=True)
        self.assertEqual(with_identity.returncode, without_identity.returncode,
                         "the hook behaved differently depending on caller-identity "
                         "environment variables, which is a bypass rather than a gate")
        self.assertFalse(with_identity.entered_suite_block, with_identity.stdout)
        self.assertFalse(without_identity.entered_suite_block,
                         "with caller-identity signals stripped the hook entered the suite "
                         "block - the exit is keyed on WHO is calling, not on the absent "
                         "message:\n" + without_identity.stdout + without_identity.stderr)


def _load_gitutil():
    """The shipped git-fixture helper, loaded rather than re-implemented, so every fixture git
    call below is confined to its fixture by the same list the skill's own tests use."""
    import importlib.util
    import sys
    path = REPO / ".claude/skills/sdlc-studio/scripts/tests/gitutil.py"
    spec = importlib.util.spec_from_file_location("_commit_msg_hook_gitutil", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


gitutil = _load_gitutil()


class DerivedTrailerTests(unittest.TestCase):
    """US1133: the hook WRITES the trailers the staged files' `Affects` already attribute, so a
    multi-id commit lands at its first attempt, and still refuses a `Refs:` line that contradicts
    them. The BG1213 landing is the replay: a subject naming two units, each owning a staged file,
    refused once for a trailer the units' own declarations could have written."""

    def _fixture(self, d: str, *, stage: tuple[str, ...],
                 units: tuple[tuple[str, str, str], ...] = (("stories", "US0001", "src/a.py"),
                                                            ("bugs", "BG0002", "bin/gate")),
                 files: tuple[str, ...] = ("src/a.py", "bin/gate")) -> Path:
        """US0001 owns src/a.py and BG0002 owns bin/gate, each by its Affects; the files in
        `stage` are modified and staged, and the hook is installed the way git runs it. The
        extension-less `bin/gate` is the shape of `.githooks/commit-msg`, which the footprint
        counter does not count as a file and which a unit still owns by declaring it."""
        repo = Path(d)
        gitutil.git(["init", "-q"], cwd=repo)
        skill = repo / ".claude" / "skills" / "sdlc-studio"
        skill.mkdir(parents=True)
        (skill / "scripts").symlink_to(REPO / ".claude" / "skills" / "sdlc-studio" / "scripts")
        for rel, rid, owned in units:
            folder = repo / "sdlc-studio" / rel
            folder.mkdir(parents=True, exist_ok=True)
            (folder / f"{rid}-sample.md").write_text(
                f"# {rid}: sample\n\n> **Status:** In Progress\n> **Affects:** {owned}\n",
                encoding="utf-8")
        for rel in files:
            (repo / rel).parent.mkdir(parents=True, exist_ok=True)
            (repo / rel).write_text("x = 1\n", encoding="utf-8")
        gitutil.git(["add", "-A"], cwd=repo)
        gitutil.git(["commit", "-q", "-m", "seed"], cwd=repo)
        for rel in stage:
            (repo / rel).write_text("x = 2\n", encoding="utf-8")
        gitutil.git(["add", "-A"], cwd=repo)
        hooks = repo / "hooks"
        hooks.mkdir()
        (hooks / "commit-msg").symlink_to(HOOK)
        gitutil.git(["config", "core.hooksPath", str(hooks)], cwd=repo)
        return repo

    def _hook(self, repo: Path, message: str):
        msg = repo / "COMMIT_EDITMSG"
        msg.write_text(message, encoding="utf-8")
        env = gitutil.git_env()
        r = subprocess.run(["bash", str(HOOK), str(msg)], capture_output=True, text=True,
                           cwd=repo, env=env, timeout=120)
        return r, msg.read_text(encoding="utf-8")

    def test_owning_ids_get_refs_written_and_the_commit_lands(self):
        # AC1. Must fail on: `message-refs` still refusing a message the staged-file map can
        # attribute, or the trailers written outside the message's own trailer block.
        with tempfile.TemporaryDirectory() as d:
            repo = self._fixture(d, stage=("src/a.py", "bin/gate"))
            message = "fix(US0001, BG0002): the pair\n\nCo-Authored-By: t <t@t>\n"
            r = gitutil.git(["commit", "-q", "-m", message], cwd=repo, check=False, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            body = gitutil.git(["log", "-1", "--format=%B"], cwd=repo, text=True).stdout
            self.assertEqual(body.count("Refs: US0001"), 1, body)
            self.assertEqual(body.count("Refs: BG0002"), 1, body)
            self.assertNotIn("Mentions:", body)
            # git reads them as trailers, in the block the message already carried
            refs = gitutil.git(["log", "-1", "--format=%(trailers:key=Refs,valueonly)"],
                               cwd=repo, text=True).stdout.split()
            self.assertEqual(sorted(refs), ["BG0002", "US0001"], body)
            self.assertIn("Co-Authored-By: t <t@t>\nRefs: ", body)

    def test_a_trailer_that_contradicts_ownership_is_refused(self):
        # AC3. Must fail on: the lane deleted outright, or a correct trailer written twice.
        with tempfile.TemporaryDirectory() as d:
            repo = self._fixture(d, stage=("src/a.py",))
            subject = "fix(US0001, BG0002): only a.py moved"
            wrong = f"{subject}\n\nRefs: US0001\nRefs: BG0002\n"
            r, after = self._hook(repo, wrong)
            out = r.stdout + r.stderr
            self.assertNotEqual(r.returncode, 0, out)
            self.assertIn("FAIL message-refs", re.sub(r"\s+", " ", out))
            self.assertRegex(out, r"Refs: BG0002[^\n]*owns none of the staged files", out)
            self.assertNotRegex(out, r"Refs: US0001[^\n]*owns none", out)
            self.assertEqual(after, wrong, "a refused message is not rewritten")
            # A trailer that matches ownership passes unchanged ...
            right = f"{subject}\n\nRefs: US0001\nMentions: BG0002\n"
            r, after = self._hook(repo, right)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual(after, right)
            self.assertEqual((r.stdout + r.stderr).strip(), "ok   message-refs")
            # ... and is never written a second time beside the one derived for the other id.
            r, after = self._hook(repo, f"{subject}\n\nRefs: US0001\n")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual(after, f"{subject}\n\nRefs: US0001\nMentions: BG0002\n")

    def test_a_directory_or_glob_declaration_owns_the_files_under_it(self):
        # Round-1 REJECT of US1133. `Affects` declares a DIRECTORY (`src/`) or a GLOB
        # (`lib/*.py`) as often as a file; the base hook accepted the owner's `Refs:` line, and
        # the close's own guard (`sprint.batch_repair_in_tree`) already reads such a token as
        # covering what sits under it. Must fail on: ownership judged by the exact path only, so
        # the owner is refused its correct `Refs:` and is written `Mentions:`; or a glob under a
        # dot-directory (`.ci/*.sh`) mangled to `ci/*.sh` by a leading-character strip.
        units = (("stories", "US0001", "src/"), ("stories", "US0003", "lib/*.py"),
                 ("bugs", "BG0004", ".ci/*.sh"), ("bugs", "BG0002", "bin/gate"),
                 ("stories", "US0005", "docs/x.md"))
        files = ("src/a.py", "lib/b.py", ".ci/run.sh", "bin/gate", "docs/x.md")
        owners = ("US0001", "US0003", "BG0004", "BG0002")
        subject = "fix(US0001, US0003, BG0004, BG0002, US0005): under a declaration"
        with tempfile.TemporaryDirectory() as d:
            repo = self._fixture(d, stage=files[:4], units=units, files=files)
            # Derivation: one `Refs:` per owner, `Mentions:` for the control, never the reverse.
            r, after = self._hook(repo, f"{subject}\n")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            for rid in owners:
                with self.subTest(owner=rid):
                    self.assertEqual(after.count(f"Refs: {rid}\n"), 1, after)
                    self.assertNotIn(f"Mentions: {rid}", after)
            self.assertEqual(after.count("Mentions: US0005\n"), 1, after)
            self.assertNotIn("Refs: US0005", after)
            # The owners' correct `Refs:` lines pass unchanged, as the base hook passed them ...
            right = (f"{subject}\n\n" + "".join(f"Refs: {i}\n" for i in owners)
                     + "Mentions: US0005\n")
            r, after = self._hook(repo, right)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual(after, right)
            # ... and the non-owning control's `Refs:` is still refused, naming only it.
            wrong = f"{subject}\n\n" + "".join(f"Refs: {i}\n" for i in (*owners, "US0005"))
            r, after = self._hook(repo, wrong)
            out = r.stdout + r.stderr
            self.assertNotEqual(r.returncode, 0, out)
            self.assertRegex(out, r"Refs: US0005[^\n]*owns none of the staged files", out)
            for rid in owners:
                self.assertNotRegex(out, rf"Refs: {rid}[^\n]*owns none", out)
            self.assertEqual(after, wrong)


    def test_a_bracketed_note_or_a_dotdot_path_owns_its_file_as_the_close_reads_it(self):
        # Round-2 REJECT of US1133 (BG1274). Two declaration shapes this tree's own units carry,
        # which the close guard credits and the base hook passed: CR0155's bracketed note
        # holding a comma (`scripts/audit.py (`_bug_underspecified`, lines ~72-83)`) and
        # US0483's path through a `..` segment (`.claude/skills/sdlc-studio/scripts/../x.md`).
        # A commit naming both with their own `Refs:` lines must land. Must fail on: the hook
        # splitting the note on its comma, or keying the `..` path unresolved, so a true owner's
        # `Refs:` is refused as owning none of the staged files.
        skill = ".claude/skills/sdlc-studio"
        units = (("change-requests", "CR0155", "tool/audit.py (`_bug_underspecified`, "
                  "lines ~72-83)"),
                 ("stories", "US0483", f"{skill}/templates/../reference-config.md"))
        files = ("tool/audit.py", f"{skill}/reference-config.md", f"{skill}/templates/t.md")
        subject = "fix(US0483, CR0155): the note and the dot-dot path"
        with tempfile.TemporaryDirectory() as d:
            repo = self._fixture(d, stage=files[:2], units=units, files=files)
            right = f"{subject}\n\nRefs: US0483\nRefs: CR0155\n"
            r, after = self._hook(repo, right)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual(after, right)
            # Derived, each owner gets `Refs:` and neither is written `Mentions:`.
            r, after = self._hook(repo, f"{subject}\n")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            for rid in ("US0483", "CR0155"):
                with self.subTest(owner=rid):
                    self.assertEqual(after.count(f"Refs: {rid}\n"), 1, after)
                    self.assertNotIn(f"Mentions: {rid}", after)

    def test_a_verbose_diff_below_the_scissors_is_neither_read_nor_written_into(self):
        # Round-1 REJECT of US1133 (BG1263). `git commit -v` puts the staged diff below git's
        # scissors line, and git drops everything below it. A diff context line reading
        # ` Refs: US0005` is git's text, not the author's, so it states no ownership; and the
        # derived trailers go into the author's text above git's scaffolding, never after the
        # diff where git would drop them. Must fail on: the derivation reading a `Refs:` line
        # below the scissors (refused as contradicting ownership), or the trailers written
        # below the diff.
        units = (("stories", "US0001", "src/a.py"), ("bugs", "BG0002", "bin/gate"),
                 ("stories", "US0005", "docs/x.md"))
        files = ("src/a.py", "bin/gate", "docs/x.md")
        subject = "fix(US0001, BG0002): verbose"
        scaffold = ("\n# Please enter the commit message for your changes.\n"
                    "# ------------------------ >8 ------------------------\n"
                    "# Do not modify or remove the line above.\n"
                    "# Everything below it will be ignored.\n"
                    "diff --git a/src/a.py b/src/a.py\n"
                    " Refs: US0005\n"
                    "-x = 1\n"
                    "+x = 2\n")
        with tempfile.TemporaryDirectory() as d:
            repo = self._fixture(d, stage=("src/a.py",), units=units, files=files)
            r, after = self._hook(repo, f"{subject}\n{scaffold}")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(after, f"{subject}\n\nRefs: US0001\nMentions: BG0002\n{scaffold}")

    def test_the_scissors_line_is_found_under_a_non_default_comment_character(self):
        # BG1323 AC1. With `core.commentChar=;` git writes `; ---- >8 ----`. The hook reads
        # nothing below it (a diff context ` Refs: US0005` is git's text) and writes its trailers
        # above it. Fails on a scissors pattern fixed to `#`.
        units = (("stories", "US0001", "src/a.py"), ("bugs", "BG0002", "bin/gate"),
                 ("stories", "US0005", "docs/x.md"))
        files = ("src/a.py", "bin/gate", "docs/x.md")
        subject = "fix(US0001, BG0002): verbose"
        scaffold = ("\n; Please enter the commit message for your changes.\n"
                    "; ------------------------ >8 ------------------------\n"
                    "; Do not modify or remove the line above.\n"
                    "diff --git a/src/a.py b/src/a.py\n"
                    " Refs: US0005\n"
                    "-x = 1\n"
                    "+x = 2\n")
        with tempfile.TemporaryDirectory() as d:
            repo = self._fixture(d, stage=("src/a.py",), units=units, files=files)
            gitutil.git(["config", "core.commentChar", ";"], cwd=repo)
            r, after = self._hook(repo, f"{subject}\n{scaffold}")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(after, f"{subject}\n\nRefs: US0001\nMentions: BG0002\n{scaffold}")

class ChangelogFragmentRequiredTests(unittest.TestCase):
    """BG1574: a commit that names a unit and stages code is refused until the unit's
    `changelog.d/<ID>.md` is staged or tracked, so the paperwork rule is a gate and not a habit."""

    def _fixture(self, d: str, *, keep_dir: bool = True, tracked: tuple[str, ...] = (),
                 stage: tuple[str, ...] = (".claude/skills/x/scripts/a.py",),
                 units: tuple[tuple[str, str], ...] = (("BG9001", ".claude/skills/x/scripts/a.py"),
                                                      ("BG9002", "src/b.py")),
                 changelog_py: str = "real") -> Path:
        """BG9001 owns a skill script and BG9002 owns src/b.py, by their Affects; `tracked`
        fragments are committed in the seed, and every path in `stage` is modified and staged.
        `changelog_py` is "real" (the scripts directory itself), "absent" (every script but
        changelog.py), or the source of a changelog.py to put in its place."""
        repo = Path(d)
        gitutil.git(["init", "-q"], cwd=repo)
        skill = repo / ".claude" / "skills" / "sdlc-studio"
        skill.mkdir(parents=True)
        real = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"
        if changelog_py == "real":
            (skill / "scripts").symlink_to(real)
        else:
            (skill / "scripts").mkdir()
            for entry in real.iterdir():
                if entry.name not in ("changelog.py", "__pycache__"):
                    (skill / "scripts" / entry.name).symlink_to(entry)
            if changelog_py != "absent":
                (skill / "scripts" / "changelog.py").write_text(changelog_py, encoding="utf-8")
        for rid, owned in units:
            folder = repo / "sdlc-studio" / "bugs"
            folder.mkdir(parents=True, exist_ok=True)
            (folder / f"{rid}-sample.md").write_text(
                f"# {rid}: sample\n\n> **Status:** In Progress\n> **Affects:** {owned}\n",
                encoding="utf-8")
            (repo / owned).parent.mkdir(parents=True, exist_ok=True)
            (repo / owned).write_text("x = 1\n", encoding="utf-8")
        if keep_dir:
            (repo / "changelog.d").mkdir()
            (repo / "changelog.d" / ".gitkeep").write_text("", encoding="utf-8")
        for rid in tracked:
            (repo / "changelog.d" / f"{rid}.md").write_text(
                "<!-- section: Fixed -->\n\nA fragment.\n", encoding="utf-8")
        gitutil.git(["add", "-A"], cwd=repo)
        gitutil.git(["commit", "-q", "-m", "seed"], cwd=repo)
        for rel in stage:
            (repo / rel).parent.mkdir(parents=True, exist_ok=True)
            (repo / rel).write_text("x = 2\n", encoding="utf-8")
        gitutil.git(["add", "-A"], cwd=repo)
        return repo

    def _stage_fragment(self, repo: Path, rid: str) -> None:
        (repo / "changelog.d" / f"{rid}.md").write_text(
            "<!-- section: Fixed -->\n\nA fragment.\n", encoding="utf-8")
        gitutil.git(["add", "--", f"changelog.d/{rid}.md"], cwd=repo)

    def _hook(self, repo: Path, message: str):
        msg = repo / "COMMIT_EDITMSG"
        msg.write_text(message, encoding="utf-8")
        r = subprocess.run(["bash", str(HOOK), str(msg)], capture_output=True, text=True,
                           cwd=repo, env=gitutil.git_env(), timeout=120)
        return r, r.stdout + r.stderr

    def test_a_unit_commit_with_a_code_change_and_no_fragment_is_refused(self):
        # AC1. Must fail on: HEAD, where the same commit exits 0 with every lane green.
        with tempfile.TemporaryDirectory() as d:
            repo = self._fixture(d)
            r, out = self._hook(repo, "fix(BG9001): change a script with no fragment\n")
        self.assertNotEqual(r.returncode, 0, out)
        flat = re.sub(r"\s+", " ", out)
        self.assertIn("FAIL message-refs", flat)
        self.assertIn("BG9001", flat)
        self.assertIn("changelog.d/BG9001.md", flat)
        # no exemption was attempted, so the refusal does not talk about one
        self.assertNotIn("a reason", flat)

    def test_a_staged_or_tracked_fragment_or_a_paperwork_commit_passes(self):
        # AC2. Each leg is paired with a refusing control on the same fixture shape.
        subject = "fix(BG9001): change a script\n"
        with tempfile.TemporaryDirectory() as d:
            repo = self._fixture(d)
            self._stage_fragment(repo, "BG9001")
            r, out = self._hook(repo, subject)
            self.assertEqual(r.returncode, 0, out)
            self.assertIn("ok   message-refs", out)
        with tempfile.TemporaryDirectory() as d:
            # a repair round: the fragment landed in the unit's earlier commit
            repo = self._fixture(d, tracked=("BG9001",))
            r, out = self._hook(repo, subject)
            self.assertEqual(r.returncode, 0, out)
        with tempfile.TemporaryDirectory() as d:
            # an untracked draft on disk is not a staged fragment
            repo = self._fixture(d)
            (repo / "changelog.d" / "BG9001.md").write_text(
                "<!-- section: Fixed -->\n\nA draft.\n", encoding="utf-8")
            r, out = self._hook(repo, subject)
            self.assertNotEqual(r.returncode, 0, out)
        with tempfile.TemporaryDirectory() as d:
            # a fragment staged for DELETION is no fragment
            repo = self._fixture(d, tracked=("BG9001",))
            gitutil.git(["rm", "-q", "--", "changelog.d/BG9001.md"], cwd=repo)
            r, out = self._hook(repo, subject)
            self.assertNotEqual(r.returncode, 0, out)
        with tempfile.TemporaryDirectory() as d:
            # a paperwork commit: only files under sdlc-studio/ and changelog.d/
            repo = self._fixture(d, stage=("sdlc-studio/bugs/BG9001-sample.md",))
            self._stage_fragment(repo, "BG9002")
            r, out = self._hook(repo, subject)
            self.assertEqual(r.returncode, 0, out)
            self.assertIn("ok   message-refs", out)
        with tempfile.TemporaryDirectory() as d:
            # code beside a paperwork file is still code: the paperwork does not excuse it
            repo = self._fixture(d, stage=("sdlc-studio/bugs/BG9001-sample.md",
                                           ".claude/skills/x/scripts/a.py"))
            r, out = self._hook(repo, subject)
            self.assertNotEqual(r.returncode, 0, out)
            self.assertIn("changelog.d/BG9001.md", out)
        with tempfile.TemporaryDirectory() as d:
            # a merge or revert git wrote is not judged: the work was gated on its own commit
            repo = self._fixture(d)
            (repo / ".git" / "MERGE_HEAD").write_text("x\n", encoding="utf-8")
            r, out = self._hook(repo, subject)
            self.assertEqual(r.returncode, 0, out)
        with tempfile.TemporaryDirectory() as d:
            # a refusal by the message rules is answered alone, not doubled by this lane
            repo = self._fixture(d, stage=("src/other.py",))
            r, out = self._hook(repo, "fix(BG9001, BG9002): owns no staged file\n")
            self.assertNotEqual(r.returncode, 0, out)
            self.assertIn("FAIL message-refs", out)
            self.assertNotIn("stages code but not", out)
        with tempfile.TemporaryDirectory() as d:
            # a subject naming no unit
            repo = self._fixture(d)
            r, out = self._hook(repo, "chore: tidy a script\n")
            self.assertEqual(r.returncode, 0, out)
        with tempfile.TemporaryDirectory() as d:
            # a project that keeps no changelog.d/ has no fragment rule
            repo = self._fixture(d, keep_dir=False)
            r, out = self._hook(repo, "fix(BG9001): change a script\n")
            self.assertEqual(r.returncode, 0, out)

    def test_each_owning_id_needs_its_fragment_and_an_exemption_needs_a_reason(self):
        # AC3. Must fail on: HEAD, a first-id-only read, and an exemption with no reason.
        stage = (".claude/skills/x/scripts/a.py", "src/b.py")
        shared = "fix(BG9001, BG9002): two units in one commit\n"
        with tempfile.TemporaryDirectory() as d:
            repo = self._fixture(d, stage=stage)
            self._stage_fragment(repo, "BG9001")
            r, out = self._hook(repo, shared)
            self.assertNotEqual(r.returncode, 0, out)
            self.assertIn("changelog.d/BG9002.md", out)
            self.assertNotIn("changelog.d/BG9001.md", out)
            # the other order: only the second id's fragment is staged
            gitutil.git(["rm", "-q", "--cached", "--", "changelog.d/BG9001.md"], cwd=repo)
            self._stage_fragment(repo, "BG9002")
            r, out = self._hook(repo, shared)
            self.assertNotEqual(r.returncode, 0, out)
            self.assertIn("changelog.d/BG9001.md", out)
            self.assertNotIn("changelog.d/BG9002.md", out)
            # both staged
            self._stage_fragment(repo, "BG9001")
            r, out = self._hook(repo, shared)
            self.assertEqual(r.returncode, 0, out)
        with tempfile.TemporaryDirectory() as d:
            # a Mentions: id owns no file and needs no fragment
            repo = self._fixture(d)
            r, out = self._hook(repo, "fix(BG9001, BG9002): one owns the file\n")
            self.assertNotEqual(r.returncode, 0, out)
            self.assertIn("changelog.d/BG9001.md", out)
            self.assertNotIn("changelog.d/BG9002.md", out)
            self._stage_fragment(repo, "BG9001")
            r, out = self._hook(repo, "fix(BG9001, BG9002): one owns the file\n")
            self.assertEqual(r.returncode, 0, out)
        for trailer, passes in (("Changelog: none - a revert of a doc typo", True),
                                ("changelog: NONE - lower case is read the same", True),
                                ("Changelog: none", False),
                                ("Changelog: none -", False),
                                ("Changelog: none -   ", False),
                                ("Changelog: none- x", False),
                                ("Changelog: none because I said so", False)):
            with self.subTest(trailer=trailer):
                with tempfile.TemporaryDirectory() as d:
                    repo = self._fixture(d)
                    r, out = self._hook(repo, f"fix(BG9001): no fragment\n\n{trailer}\n")
                self.assertEqual(r.returncode == 0, passes, out)
                if not passes:
                    self.assertIn("a reason", re.sub(r"\s+", " ", out))
        for trailers in ("Changelog: none\nChangelog: none - the second line says why",
                         "Changelog: none - the first line says why\nChangelog: none"):
            with self.subTest(trailers=trailers):
                with tempfile.TemporaryDirectory() as d:
                    repo = self._fixture(d)
                    r, out = self._hook(repo, f"fix(BG9001): no fragment\n\n{trailers}\n")
                self.assertEqual(r.returncode, 0, out)
        with tempfile.TemporaryDirectory() as d:
            # a word that merely begins with "none" is no exemption, and no bare-exemption hint
            repo = self._fixture(d)
            r, out = self._hook(repo, "fix(BG9001): x\n\nChangelog: nonetheless - but why\n")
            self.assertNotEqual(r.returncode, 0, out)
            self.assertNotIn("a reason", out)
        with tempfile.TemporaryDirectory() as d:
            # the git scaffold (# lines) is not the message: not a trailer, and not the subject
            repo = self._fixture(d)
            r, out = self._hook(repo, "fix(BG9001): none\n\n# Changelog: none - scaffold\n")
            self.assertNotEqual(r.returncode, 0, out)
            r, out = self._hook(repo, "# Please enter the message\n\nfix(BG9001): x\n")
            self.assertNotEqual(r.returncode, 0, out)
            self.assertIn("changelog.d/BG9001.md", out)

    def _check(self, root: Path, message: Path | None, text: bytes | None = None):
        if message is not None and text is not None:
            message.write_bytes(text)
        script = REPO / ".claude/skills/sdlc-studio/scripts/changelog.py"
        argv = ["python3", str(script), "required", "--root", str(root),
                str(message if message is not None else root / "absent-message")]
        return subprocess.run(argv, capture_output=True, text=True, cwd=root,
                              env=gitutil.git_env(), timeout=60)

    def test_the_check_itself_degrades_on_a_bad_message_and_a_broken_index(self):
        with tempfile.TemporaryDirectory() as d:
            repo = self._fixture(d)
            for label, text in (("not UTF-8", b"fix(BG9001): \xff\xfe\n"), ):
                r = self._check(repo, repo / "MSG", text)
                self.assertEqual(r.returncode, 0, label + r.stderr)
                self.assertIn("required skipped", r.stderr)
            r = self._check(repo, None)                      # a missing message file
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("required skipped", r.stderr)
            # control: the same repo and a readable message is refused
            r = self._check(repo, repo / "MSG", b"fix(BG9001): x\n")
            self.assertEqual(r.returncode, 1, r.stderr)
            r = self._check(repo, repo / "MSG", b"")         # an empty message names no unit
            self.assertEqual(r.returncode, 0, r.stderr)
        with tempfile.TemporaryDirectory() as d:
            # no repository at all: git cannot answer, which is refused and named, not passed
            (Path(d) / "changelog.d").mkdir()
            r = self._check(Path(d), Path(d) / "MSG", b"fix(BG9001): x\n")
            self.assertEqual(r.returncode, 2, r.stderr)
            self.assertIn("required refused", r.stderr)
            # control: a message naming no unit never asks git, so it passes where that cannot
            r = self._check(Path(d), Path(d) / "MSG", b"chore: tidy\n")
            self.assertEqual(r.returncode, 0, r.stderr)
        with tempfile.TemporaryDirectory() as d:
            # a project that keeps no changelog.d/ is never asked, even with code staged
            repo = self._fixture(d, keep_dir=False)
            r = self._check(repo, repo / "MSG", b"fix(BG9001): x\n")
            self.assertEqual(r.returncode, 0, r.stderr)

    def test_a_version_three_id_is_read_from_the_subject(self):
        # control for the id grammar: a schema 3 id names its fragment as the hook reads it
        with tempfile.TemporaryDirectory() as d:
            repo = self._fixture(d)
            r = self._check(repo, repo / "MSG", b"fix(BG-01JQK3F8): x\n")
            self.assertEqual(r.returncode, 1, r.stderr)
            self.assertIn("changelog.d/BG-01JQK3F8.md", r.stderr)
            # either spelling of the fragment's name satisfies the id
            for name in ("BG-01JQK3F8", "BG01JQK3F8"):
                (repo / "changelog.d" / f"{name}.md").write_text(
                    "<!-- section: Fixed -->\n\nA fragment.\n", encoding="utf-8")
                gitutil.git(["add", "--", f"changelog.d/{name}.md"], cwd=repo)
                r = self._check(repo, repo / "MSG", b"fix(BG-01JQK3F8): x\n")
                self.assertEqual(r.returncode, 0, name + r.stderr)
                gitutil.git(["rm", "-q", "--cached", "--", f"changelog.d/{name}.md"], cwd=repo)

    def test_a_shared_commit_asks_no_fragment_of_an_id_that_owns_no_staged_code(self):
        # A Refs: id whose only staged file is its own record owns no code: the hook writes its
        # Refs: line from the record's name, and the fragment rule must not then refuse it.
        record = "sdlc-studio/bugs/BG9001-sample.md"
        subject = "docs(BG9001, BG9002): record verdicts\n"
        with tempfile.TemporaryDirectory() as d:
            repo = self._fixture(d, stage=(record, "src/b.py"))
            self._stage_fragment(repo, "BG9002")
            r, out = self._hook(repo, subject)
            self.assertEqual(r.returncode, 0, out)
            written = (repo / "COMMIT_EDITMSG").read_text(encoding="utf-8")
            self.assertIn("Refs: BG9001", written)
            self.assertIn("Refs: BG9002", written)
        with tempfile.TemporaryDirectory() as d:
            # control: the id that owns the code is still asked, and only it
            repo = self._fixture(d, stage=(record, "src/b.py"))
            r, out = self._hook(repo, subject)
            self.assertNotEqual(r.returncode, 0, out)
            self.assertIn("changelog.d/BG9002.md", out)
            self.assertNotIn("changelog.d/BG9001.md", out)
        with tempfile.TemporaryDirectory() as d:
            # a code file carrying an id in its name is that unit's code, as the trailers read it
            repo = self._fixture(d, stage=(".claude/skills/x/scripts/a.py", "src/BG9002-tool.py"))
            self._stage_fragment(repo, "BG9001")
            r, out = self._hook(repo, "fix(BG9001, BG9002): a tool named for its unit\n")
            self.assertNotEqual(r.returncode, 0, out)
            self.assertIn("changelog.d/BG9002.md", out)
            self._stage_fragment(repo, "BG9002")
            r, out = self._hook(repo, "fix(BG9001, BG9002): a tool named for its unit\n")
            self.assertEqual(r.returncode, 0, out)
        with tempfile.TemporaryDirectory() as d:
            # a written Refs: id with no artefact in the workspace declares nothing and owns no code
            repo = self._fixture(d)
            self._stage_fragment(repo, "BG9001")
            r, out = self._hook(repo, "fix(BG9001, BG9005): x\n\nRefs: BG9005\n")
            self.assertEqual(r.returncode, 0, out)
        with tempfile.TemporaryDirectory() as d:
            # a single-id subject owns everything it stages, declared in its Affects or not
            repo = self._fixture(d, stage=("src/b.py",))
            r, out = self._hook(repo, "fix(BG9001): a file another unit declares\n")
            self.assertNotEqual(r.returncode, 0, out)
            self.assertIn("changelog.d/BG9001.md", out)
        units = (("BG9001", ".claude/skills/x/scripts/a.py"), ("BG9002", "src/b.py"),
                 ("BG9003", "src/c.py"))
        stage = (".claude/skills/x/scripts/a.py", "src/b.py", "src/c.py")
        with tempfile.TemporaryDirectory() as d:
            # a Refs: id the subject does not name is not the commit's unit and is not asked
            repo = self._fixture(d, stage=stage, units=units)
            self._stage_fragment(repo, "BG9001")
            self._stage_fragment(repo, "BG9002")
            r, out = self._hook(repo, "fix(BG9001, BG9002): x\n\nRefs: BG9003\n")
            self.assertEqual(r.returncode, 0, out)
        with tempfile.TemporaryDirectory() as d:
            # a written `refs:` line is read whatever its case, as the trailer check reads it
            repo = self._fixture(d, stage=stage[:2])
            self._stage_fragment(repo, "BG9001")
            r, out = self._hook(repo, "fix(BG9001, BG9002): x\n\nRefs: BG9001\nrefs: BG9002\n")
            self.assertNotEqual(r.returncode, 0, out)
            self.assertIn("changelog.d/BG9002.md", out)

    def test_a_dashed_sequential_id_and_a_dashed_fragment_name_are_one_unit(self):
        # The subject's `BG-9001` is BG9001, and a fragment in either spelling is its fragment.
        for subject in ("fix(BG-9001): change a script\n", "fix(BG9001): change a script\n"):
            with self.subTest(subject=subject):
                with tempfile.TemporaryDirectory() as d:
                    repo = self._fixture(d)
                    r, out = self._hook(repo, subject)
                    self.assertNotEqual(r.returncode, 0, out)
                    self.assertIn("changelog.d/BG9001.md", out)
                    for name in ("BG-9001", "BG9001"):
                        self._stage_fragment(repo, name)
                        r, out = self._hook(repo, subject)
                        self.assertEqual(r.returncode, 0, name + out)
                        gitutil.git(["rm", "-q", "--cached", "--", f"changelog.d/{name}.md"],
                                    cwd=repo)

    def test_a_refusal_names_each_unit_as_its_artefacts_spell_it(self):
        # A schema 3 id is printed dashed, as its record and its fragment spell it, never as the
        # dashless comparison key the rule matches on, even with no record in the workspace; a
        # sequential id keeps its dashless spelling, whichever way the subject wrote it.
        v3 = "BG-01JQK3F8"
        units = ((v3, "src/v3.py"), ("BG9002", "src/b.py"))
        both = ("src/v3.py", "src/b.py")
        for subject, owners, stage, refused in (
                (f"fix({v3}, BG9002): two\n", units, both, (v3, "BG9002")),
                (f"fix({v3}): one\n", units, both, (v3,)),
                (f"fix({v3}): no record\n", units[1:], ("src/b.py",), (v3,)),
                ("fix(BG-9002): one\n", units, ("src/b.py",), ("BG9002",)),
                ("fix(BG9002): one\n", units, ("src/b.py",), ("BG9002",))):
            with self.subTest(subject=subject):
                with tempfile.TemporaryDirectory() as d:
                    repo = self._fixture(d, stage=stage, units=owners)
                    self.assertEqual(owners == units,
                                     (repo / f"sdlc-studio/bugs/{v3}-sample.md").is_file())
                    r, out = self._hook(repo, subject)
                self.assertNotEqual(r.returncode, 0, out)
                faults = [ln.strip() for ln in out.splitlines() if "stages code but not" in ln]
                self.assertEqual(
                    [f"{rid}: the commit stages code but not changelog.d/{rid}.md"
                     for rid in refused], faults, out)
                self.assertNotIn("BG01JQK3F8", out)
                self.assertNotIn("BG-9002:", out)

    def test_a_story_and_a_request_id_are_read_from_the_subject(self):
        # The grammar's US and CR branches are live: each id is asked for its own fragment.
        for rid in ("US9003", "CR9004"):
            with self.subTest(rid=rid):
                with tempfile.TemporaryDirectory() as d:
                    repo = self._fixture(d, stage=("tools/c.py",))
                    r, out = self._hook(repo, f"feat({rid}): a tool\n")
                    self.assertNotEqual(r.returncode, 0, out)
                    self.assertIn(f"changelog.d/{rid}.md", out)
                    self._stage_fragment(repo, rid)
                    r, out = self._hook(repo, f"feat({rid}): a tool\n")
                    self.assertEqual(r.returncode, 0, out)

    def test_a_scripts_dir_without_the_verb_or_the_script_skips_the_rule(self):
        # The clone's hooks path is shared by its linked worktrees, each running this hook over
        # its own scripts: one from before `required`, or with no changelog.py, is not refused.
        before = ("import argparse\n"
                  "p = argparse.ArgumentParser(prog='changelog')\n"
                  "sub = p.add_subparsers(dest='cmd', required=True)\n"
                  "for verb in ('compose', 'check', 'structure', 'shape'):\n"
                  "    sub.add_parser(verb)\n"
                  "p.parse_args()\n")
        for label, source in (("no required verb", before), ("no changelog.py", "absent")):
            for subject in ("chore: tidy\n", "fix(BG9001): change a script\n"):
                with self.subTest(scripts=label, subject=subject):
                    with tempfile.TemporaryDirectory() as d:
                        repo = self._fixture(d, changelog_py=source)
                        r, out = self._hook(repo, subject)
                    self.assertEqual(r.returncode, 0, out)
                    self.assertIn("ok   message-refs", out)
                    # the probe of a missing script is silent, not an attribution note
                    self.assertNotIn("No such file", out)
        with tempfile.TemporaryDirectory() as d:
            # control: the same copied layout with the real script refuses the unit's commit
            real = REPO / ".claude/skills/sdlc-studio/scripts/changelog.py"
            repo = self._fixture(d, changelog_py=real.read_text(encoding="utf-8"))
            r, out = self._hook(repo, "fix(BG9001): change a script\n")
        self.assertNotEqual(r.returncode, 0, out)
        self.assertIn("changelog.d/BG9001.md", out)


class HookInvocationHermeticityTests(unittest.TestCase):
    """BG0595 AC4/AC5. No test may invoke the hook against the repository under development."""

    #: Every hook invocation must supply both, or it resolves to whatever repo the test process
    #: happens to be sitting in. `_run` supplies them for the whole file; a bare call does not.
    #: Assembled from parts so the pattern cannot match its own source line - a self-match made
    #: the census report this class as its own offender, which is the shape where a detector
    #: measures the detector.
    _BARE = re.compile(r"subprocess" + r"\.run\(\s*\[[^]]*HOOK[^]]*\][^)]*\)", re.S)

    def _offenders(self, path: pathlib.Path) -> list:
        out = []
        for m in self._BARE.finditer(path.read_text(encoding="utf-8")):
            call = m.group(0)
            if "cwd=" in call and "env=" in call:
                continue
            out.append(f"{path.name}:{path.read_text(encoding='utf-8')[:m.start()].count(chr(10)) + 1}")
        return out

    def test_every_invocation_in_this_file_supplies_a_cwd_and_an_env(self):
        """MUTANT: in `test_commit_msg_hook.py`, change `GIT_DIR` to the live repository.

        Named as a census rather than as one test, because one exemption in twenty-five was
        the entire defect and a check that names the file it already knows about would not
        have found it.
        """
        here = pathlib.Path(__file__)
        self.assertEqual([], self._offenders(here),
                         "these invocations resolve to whatever repository the test process "
                         "runs in, so they can consume the developer's gate handoff")

    def test_no_other_test_file_invokes_the_hook_bare(self):
        """The sweep AC5 names: any OTHER test carrying the same coupling is reported by name
        rather than left behind the one test this bug happened to catch."""
        roots = [REPO / "tools" / "tests",
                 REPO / ".claude" / "skills" / "sdlc-studio" / "scripts" / "tests"]
        seen, offenders = 0, []
        for root in roots:
            if not root.is_dir():
                continue
            for f in sorted(root.glob("test_*.py")):
                seen += 1
                offenders += self._offenders(f)
        self.assertGreater(seen, 20, f"only {seen} test files were scanned - the sweep "
                                     f"resolved the wrong root and measured nothing")
        self.assertEqual([], offenders,
                         "hook invocations that resolve to the repository under development")


if __name__ == "__main__":
    unittest.main()
