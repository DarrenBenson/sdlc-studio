#!/usr/bin/env python3
"""A suite verdict is a FACT READ FROM A FILE, never a stream an agent interprets.

`npm test 2>&1 | tail -15` reports **tail's** exit status. The repo's runners set
`set -uo pipefail`; the ad-hoc invoking shell does not. That cost two false claims in one
session - a commit reported as landed when the hook had refused it, and a suite reported green
with a real failure inside it.

It is not fixable by resolving to be careful: the pipe exists because a six-minute suite's
output does not fit in one read, so the incentive recurs on every run. `run-suite.sh` removes
the incentive by printing one line and writing the verdict where it can be read as data.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "tools" / "run-suite.sh"
VERDICT_REL = "sdlc-studio/.local/suite-verdict.json"


def _run(root: Path, *args: str, cmd: str | None = None):
    """Run the wrapper against `root`, overriding the suite command when given.

    `SUITE_CMD_OVERRIDE` exists FOR THIS TEST and is documented in the script: a test that
    shelled out to the real 6-minute suite to check the wrapper's bookkeeping would be
    untestable in practice, and one that mocked the whole script would test nothing.
    """
    env = dict(os.environ)
    if cmd is not None:
        env["SUITE_CMD_OVERRIDE"] = cmd
    return subprocess.run([str(SCRIPT), *args], cwd=root, env=env,
                          capture_output=True, text=True)


def _fixture(tmp: Path) -> Path:
    root = tmp / "repo"
    (root / "sdlc-studio" / ".local").mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=root, check=True)
    (root / "a.txt").write_text("x", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "base"], cwd=root, check=True)
    return root


class VerdictFileTests(unittest.TestCase):

    def test_the_wrapper_writes_the_verdict(self) -> None:
        """MUTANT: stop writing the file, or drop any recorded field.

        Every field is asserted by NAME, because a verdict missing `exit_code` is exactly as
        useless as no verdict and would otherwise pass a shape-only check.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            r = _run(root, "scripts", cmd="exit 0")
            rec = json.loads((root / VERDICT_REL).read_text(encoding="utf-8"))
        self.assertEqual(0, r.returncode, r.stderr)
        for field in ("suite", "exit_code", "passed", "failed", "duration", "head_sha"):
            self.assertIn(field, rec, f"the verdict records no {field!r}")
        self.assertEqual("scripts", rec["suite"])
        self.assertEqual(0, rec["exit_code"])

    def test_only_the_verdict_line_is_printed(self) -> None:
        """MUTANT: let the suite's own output through to stdout.

        The whole point is that there is nothing worth piping to `tail`. If the wrapper streams
        the suite's output, the incentive that caused the original defect is back.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            r = _run(root, "scripts", cmd="echo LINE1; echo LINE2; echo LINE3; exit 0")
        self.assertNotIn("LINE2", r.stdout,
                         "the suite's own output reached stdout - there is now something to pipe")
        self.assertLessEqual(len(r.stdout.strip().splitlines()), 2,
                             f"more than a verdict line was printed:\n{r.stdout}")
        self.assertIn("scripts", r.stdout)

    def test_a_red_run_writes_a_red_verdict(self) -> None:
        """MUTANT: hardcode `exit_code: 0`, or write the verdict only on success.

        A wrapper that always records green reproduces the defect it replaces, and one that
        writes nothing on failure leaves the PREVIOUS green verdict in place - which is worse,
        because it is stale and looks current.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            r = _run(root, "scripts", cmd="echo boom; exit 1")
            rec = json.loads((root / VERDICT_REL).read_text(encoding="utf-8"))
        self.assertNotEqual(0, rec["exit_code"], "a failing suite recorded a green verdict")
        self.assertNotEqual(0, r.returncode, "the wrapper swallowed the suite's failure")

    def test_a_red_run_overwrites_an_earlier_green_verdict(self) -> None:
        """The stale-green case, which is the dangerous one. MUTANT: skip the write on failure."""
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            _run(root, "scripts", cmd="exit 0")
            _run(root, "scripts", cmd="exit 1")
            rec = json.loads((root / VERDICT_REL).read_text(encoding="utf-8"))
        self.assertNotEqual(
            0, rec["exit_code"],
            "an earlier GREEN verdict survived a red run - the file now lies about HEAD")

    def test_the_verdict_records_its_head(self) -> None:
        """MUTANT: drop `head_sha`, or record a constant.

        Without it a verdict taken three commits ago is indistinguishable from one taken now,
        which is the whole basis of the staleness check in US0611.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            _run(root, "scripts", cmd="exit 0")
            first = json.loads((root / VERDICT_REL).read_text(encoding="utf-8"))["head_sha"]
            (root / "b.txt").write_text("y", encoding="utf-8")
            subprocess.run(["git", "add", "-A"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "second"], cwd=root, check=True)
            head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root,
                                  capture_output=True, text=True).stdout.strip()
        self.assertTrue(first, "no head_sha was recorded")
        self.assertNotEqual(first, head,
                            "the recorded sha did not move with HEAD, so it cannot detect "
                            "staleness")

    def test_an_unknown_suite_is_refused(self) -> None:
        """MUTANT: fall through to a default suite on an unrecognised name.

        Running the wrong suite and reporting it under the requested name is a false green of
        exactly the kind this script exists to prevent.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            r = _run(root, "nonsense")
        self.assertNotEqual(0, r.returncode, "an unknown suite name was accepted")
        self.assertFalse((root / VERDICT_REL).exists(),
                         "a refused invocation still wrote a verdict")


class GateTests(unittest.TestCase):
    """`run-suite.sh --check` is what makes the verdict load-bearing.

    Writing a verdict nobody reads changes nothing. The check is the half that turns "I ran the
    suite" from a claim into a fact the gate can refuse.
    """

    def test_an_absent_verdict_is_refused(self) -> None:
        """MUTANT: treat a missing verdict as green.

        Absent must never read as pass: that is the fail-open shape, and it is indistinguishable
        from a suite that was never run - which is exactly the state being guarded against.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            r = _run(root, "--check")
        self.assertNotEqual(0, r.returncode, "a missing verdict was accepted as green")
        self.assertIn("no suite verdict", (r.stdout + r.stderr).lower())

    def test_a_stale_verdict_is_refused(self) -> None:
        """MUTANT: drop the head_sha comparison.

        A verdict from three commits ago is the dangerous case, because it exists and looks
        current. Without the sha check it passes forever.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            _run(root, "scripts", cmd="exit 0")
            (root / "c.txt").write_text("z", encoding="utf-8")
            subprocess.run(["git", "add", "-A"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "moved on"], cwd=root, check=True)
            r = _run(root, "--check")
        self.assertNotEqual(0, r.returncode, "a verdict taken at an older commit was accepted")
        self.assertIn("stale", (r.stdout + r.stderr).lower())

    def test_a_red_verdict_is_refused(self) -> None:
        """MUTANT: check only freshness, not the recorded exit code."""
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            _run(root, "scripts", cmd="exit 1")
            r = _run(root, "--check")
        self.assertNotEqual(0, r.returncode, "a RED verdict at the right sha was accepted")

    def test_a_current_green_verdict_passes(self) -> None:
        """The control. MUTANT: refuse unconditionally.

        A check that refuses every commit discriminates no better than one that refuses none,
        and would simply be switched off.

        Asks for `scripts` explicitly. It used to pass a bare `--check` against a `scripts`
        verdict and expect green, which was the second half of BG0492: a bare check now means
        "the whole tree is green" and only an `all` verdict establishes that. The assertion is
        narrower than it was, not weaker - it pins that a narrower REQUEST is still satisfiable.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            _run(root, "scripts", cmd="exit 0")
            r = _run(root, "--check", "scripts")
        self.assertEqual(0, r.returncode,
                         f"a current green verdict was refused:\n{r.stdout}{r.stderr}")


class VerdictBindsToTheTreeTests(unittest.TestCase):
    """BG0492: the verdict authorised the COMMIT, not the working tree, and `--check` never read
    which suite had run.

    A verdict is necessarily taken at its parent commit, so binding staleness to `head_sha` alone
    made every subsequent edit covered by it. With a green verdict at HEAD, staging a syntactically
    broken file and claiming "Both suites green." passed. An uncommitted working tree is the normal
    state mid-session, which is what makes this the dangerous half.
    """

    def test_an_edit_after_the_verdict_makes_it_stale(self) -> None:
        """MUTANT: drop the tree-hash comparison from --check.

        The commit sha is unchanged here - only the tree moved - so the existing head_sha check
        is green on this fixture and cannot catch it. That is why this is a separate test rather
        than an extra assertion on the staleness one.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            _run(root, "all", cmd="exit 0")
            self.assertEqual(0, _run(root, "--check").returncode, "fixture starts green")
            (root / "a.txt").write_text("edited after the suite ran", encoding="utf-8")
            r = _run(root, "--check")
        out = (r.stdout + r.stderr).lower()
        self.assertNotEqual(0, r.returncode,
                            "an edit made after the verdict was taken was accepted as green")
        self.assertIn("tree", out, out)

    def test_a_staged_edit_after_the_verdict_makes_it_stale(self) -> None:
        """MUTANT: hash only the unstaged diff.

        BG0492's own reproduction stages the broken file, so a hash reading `git diff` without
        `HEAD` would compare a clean-looking worktree against the index and see nothing.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            _run(root, "all", cmd="exit 0")
            (root / "a.txt").write_text("broken", encoding="utf-8")
            subprocess.run(["git", "add", "-A"], cwd=root, check=True)
            r = _run(root, "--check")
        self.assertNotEqual(0, r.returncode, "a STAGED edit after the verdict was accepted")

    def test_a_new_untracked_file_makes_it_stale(self) -> None:
        """MUTANT: hash the tracked diff only.

        A new module is the commonest mid-session change and is untracked until it is added, so a
        hash blind to untracked files answers "unchanged" for the case where the most new code
        arrived at once. Ignored files must not count, or the verdict expires on its own output.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            _run(root, "all", cmd="exit 0")
            (root / "new_module.py").write_text("def f():\n    return 1\n", encoding="utf-8")
            r = _run(root, "--check")
        self.assertNotEqual(0, r.returncode, "a new untracked module was accepted as covered")

    def test_the_verdicts_own_output_does_not_expire_it(self) -> None:
        """MUTANT: drop the `:(exclude)sdlc-studio/.local` pathspec.

        The verdict is written INTO the tree it describes, so a digest that counted it would
        differ the instant it was recorded and every check would refuse - a guard that refuses
        always is switched off, and this is the shape that would do it.

        NO .gitignore here, deliberately. The first version of this test wrote one naming the
        very path the exclusion also covers, so the two masked each other and the mutant the
        docstring named SURVIVED - review caught it. With no .gitignore, only the pathspec can
        make this pass.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            _run(root, "all", cmd="exit 0")
            r = _run(root, "--check")
        self.assertEqual(0, r.returncode,
                         f"the verdict expired itself:\n{r.stdout}{r.stderr}")

    def test_an_ignored_file_does_not_invalidate_the_verdict(self) -> None:
        """MUTANT: stage with `git add -A -f`, ignoring .gitignore.

        Ignore handling is git's own here rather than a flag this script passes, which is the
        point - a second ignore rule drifts from the first. This repo ignores `__pycache__/`,
        `node_modules/` and `.pytest_cache/`, all of which appear during an ordinary suite run,
        so a digest blind to .gitignore would expire the verdict its own suite had just earned.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            (root / ".gitignore").write_text("build/\n", encoding="utf-8")
            subprocess.run(["git", "add", "-A"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "ignore build"], cwd=root, check=True)
            _run(root, "all", cmd="exit 0")
            (root / "build").mkdir()
            (root / "build" / "generated.py").write_text("x = 1\n", encoding="utf-8")
            r = _run(root, "--check")
        self.assertEqual(0, r.returncode,
                         f"an ignored file expired the verdict:\n{r.stdout}{r.stderr}")

    def test_staging_an_unchanged_tree_does_not_invalidate_the_verdict(self) -> None:
        """MUTANT: return to hashing `git diff HEAD` plus untracked file hashes.

        REVIEW FINDING, and the reason the digest is a git tree object. That shape mixed two
        representations of the same bytes - an untracked file contributed `sha256  path`, the
        same file staged contributed a new-file patch - so `git add` alone moved the digest
        with no edit at all. On the shipped commit-msg lane that refused the ordinary sequence
        (write a module, run the suite, `git add -A`, commit) and told the author to re-run a
        nine-minute suite for no information.

        Both directions are staged here: a NEW file added, and a MODIFIED tracked file added.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            (root / "new_module.py").write_text("def f():\n    return 1\n", encoding="utf-8")
            (root / "a.txt").write_text("modified", encoding="utf-8")
            _run(root, "all", cmd="exit 0")
            self.assertEqual(0, _run(root, "--check").returncode, "fixture starts green")
            subprocess.run(["git", "add", "-A"], cwd=root, check=True)
            r = _run(root, "--check")
        self.assertEqual(0, r.returncode,
                         "`git add` alone invalidated a byte-identical tree:\n"
                         f"{r.stdout}{r.stderr}")

    def test_the_digest_is_recorded_when_the_verdict_dir_is_itself_gitignored(self) -> None:
        """MUTANT: exclude `.local` with an `add -- ':(exclude)<p>'` pathspec.

        THE SHAPE THIS REPOSITORY ACTUALLY HAS, and the one every other fixture here lacks.
        `git add -- ':(exclude)<p>'` FAILS when <p> is also gitignored - "the following paths
        are ignored by one of your .gitignore files" - so the digest came back empty on the real
        repo while all six fixtures passed, because none of them ignores `.local`. The verdict
        then recorded `tree_hash: ""` and `--check` refused every claim as unbindable: the fix
        was inert exactly where it ships.

        Asserts a NON-EMPTY digest, which is the assertion the other tests cannot make - they
        compare digests to each other, and two empty strings compare equal.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            (root / ".gitignore").write_text("sdlc-studio/.local/\n", encoding="utf-8")
            subprocess.run(["git", "add", "-A"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "ignore local"], cwd=root, check=True)
            _run(root, "all", cmd="exit 0")
            verdict = json.loads((root / VERDICT_REL).read_text(encoding="utf-8"))
            self.assertTrue(verdict["tree_hash"],
                            "the verdict recorded an EMPTY tree_hash, so nothing binds it to "
                            "the tree - the check degrades to refusing everything")
            self.assertEqual(0, _run(root, "--check").returncode,
                             "a verdict with a real digest was still refused")

    def test_an_unknown_suite_is_refused_rather_than_defaulted(self) -> None:
        """MUTANT: accept any `--check <word>`.

        `WANT` was unvalidated and the coverage test short-circuits on an `all` verdict, so
        `--check nonsense`, `--check ALL` and `--check --help` all printed GREEN. The run path
        already refuses an unknown suite, with a comment reading "REFUSED, never defaulted";
        this is the second entry point applying the same rule.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            _run(root, "all", cmd="exit 0")
            self.assertEqual(0, _run(root, "--check", "all").returncode, "control")
            for bad in ("nonsense", "ALL", "scripts tools"):
                with self.subTest(bad):
                    r = _run(root, "--check", bad)
                    self.assertNotEqual(0, r.returncode,
                                        f"--check {bad!r} was accepted as a checked assertion")

    def test_a_narrower_suite_does_not_satisfy_a_whole_tree_claim(self) -> None:
        """MUTANT: stop reading the `suite` field in --check.

        The commit-msg lane matches "Both suites green." and calls a bare `--check`, which never
        read which suite had run - so a verdict from `run-suite.sh scripts` satisfied a claim
        about both.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            _run(root, "scripts", cmd="exit 0")
            r = _run(root, "--check")
        out = (r.stdout + r.stderr).lower()
        self.assertNotEqual(0, r.returncode,
                            "a scripts-only verdict satisfied an unqualified greenness check")
        self.assertIn("scripts", out, out)

    def test_an_all_verdict_satisfies_a_narrower_request(self) -> None:
        """MUTANT: compare the suite names for equality instead of coverage.

        `all` ran the scripts suite, so it answers a request for `scripts`. Equality would refuse
        a verdict that genuinely covers the question asked, which teaches people to re-run a
        six-minute suite for no information.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            _run(root, "all", cmd="exit 0")
            r = _run(root, "--check", "scripts")
        self.assertEqual(0, r.returncode,
                         f"an `all` verdict was refused for a `scripts` request:\n{r.stderr}")


class CommitClaimLaneTests(unittest.TestCase):
    """The commit-msg lane: a message that CLAIMS greenness is checked against the verdict.

    Scoped to messages making the claim rather than to every commit. A gate demanding a
    six-minute suite before every commit is one people bypass, and a bypassed gate protects
    nothing - the claim is the thing worth holding to account.
    """

    HOOK = REPO / ".githooks" / "commit-msg"

    def test_the_lane_is_wired_into_the_hook(self) -> None:
        """MUTANT: delete the lane from .githooks/commit-msg.

        Pinned on the hook's text because the lane living only in `run-suite.sh` is exactly the
        library-not-lane defect this sprint exists to stop (LL0040): `--check` passing in
        isolation says nothing about whether any commit ever runs it.
        """
        text = self.HOOK.read_text(encoding="utf-8")
        self.assertIn("run-suite.sh", text,
                      "the commit-msg hook never invokes the verdict check, so the claim is "
                      "held to account by nothing")
        self.assertIn("--check", text, "the hook invokes run-suite.sh but not its check mode")
        # The lane must END the hook, not set a flag: `fail=0` in section 2 would wipe it, and
        # with no pre-commit handover the hook exits before section 2 is ever reached.
        lane = text.split("suite-claim")[1][:1200]
        self.assertIn("exit 1", lane,
                      "the lane sets a flag instead of refusing - section 2 resets it")
        self.assertIn("suite-claim", text, "the lane has no name in the hook's output")

    def test_the_claim_pattern_matches_how_these_messages_are_actually_written(self) -> None:
        """MUTANT: narrow the pattern to one exact phrase.

        The phrasings are taken from THIS repo's own log - the commits that made the false
        claim. A pattern that misses them guards nothing, which is LL0013's shape: an
        enumeration silently exempts what it forgot.
        """
        import re
        pattern = re.compile(
            r'(both )?suites? (are |were |is )?green|suite green|tests? (are |were |is )?green',
            re.IGNORECASE)
        for claim in ("Both suites green, exit codes checked directly rather than",
                      "both full suites green",
                      "Both suites are green with the working tree byte-identical",
                      "the suite is green"):
            self.assertRegex(claim, pattern, f"the lane would not fire on {claim!r}")
        for innocent in ("the green lane ordering was corrected",
                         "greenfield init now refuses an unreadable PRD"):
            self.assertNotRegex(innocent, pattern,
                                f"the lane would fire on unrelated prose: {innocent!r}")


class RedRunNamesItsFailureTests(unittest.TestCase):
    """BG0513: a red leg reported a COUNT and never a NAME, so an intermittent failure in the
    full runner went unnamed across five invocations.

    The output was captured to a `mktemp` file and removed by an EXIT trap; only `tail -25`
    reached stderr, and unittest prints its `FAIL:` headers well above the closing
    `FAILED (failures=1)` line. The evidence existed on every run and was deleted every time.
    """

    def test_a_red_run_prints_the_failing_test_name(self) -> None:
        """MUTANT: drop the `FAIL:`/`FAILED ` grep and print only the tail.

        The stub puts the header far enough above the summary that a 25-line tail cannot
        reach it - which is the real shape, not a contrived one: the header is separated from
        the summary by the traceback and by every later test's output. Asserting on the NAME
        rather than on the word "FAIL" is what makes the mutant fail, because the tail still
        contains `FAILED (failures=1)`.
        """
        filler = "; ".join(f"echo pad{i}" for i in range(40))
        cmd = ("echo 'FAIL: test_the_named_one (mod.Case)'; "
               f"{filler}; echo 'FAILED (failures=1)'; exit 1")
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            r = _run(root, "tools", cmd=cmd)
        self.assertEqual(1, r.returncode)
        self.assertNotIn("test_the_named_one", r.stdout,
                         "stdout must stay the single verdict line")
        self.assertIn("test_the_named_one", r.stderr,
                      "the red run does not name the test that failed - only its count")

    def test_a_pytest_style_failure_is_named_too(self) -> None:
        """MUTANT: match only unittest's `FAIL:` and drop `^FAILED `.

        The batch runs both runners, so a red can come from either. pytest's short summary
        uses a different prefix, and a pattern that knows only one silently exempts the other
        (LL0013).
        """
        filler = "; ".join(f"echo pad{i}" for i in range(40))
        cmd = ("echo 'FAILED tools/tests/test_x.py::Case::test_pytest_one - AssertionError'; "
               f"{filler}; exit 1")
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            r = _run(root, "tools", cmd=cmd)
        self.assertIn("test_pytest_one", r.stderr,
                      "a pytest-style failure is not named")

    def test_the_verdict_records_a_log_that_holds_the_full_output(self) -> None:
        """MUTANT: stop recording `log`, or keep writing the output to a mktemp path.

        Asserts the recorded path RESOLVES and holds a line the 25-line tail could not have
        carried. A test that only checked the field's presence would survive a `log` pointing
        at a file the EXIT trap had already removed.
        """
        filler = "; ".join(f"echo pad{i}" for i in range(40))
        cmd = f"echo FIRST_LINE_MARKER; {filler}; exit 1"
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            _run(root, "tools", cmd=cmd)
            rec = json.loads((root / VERDICT_REL).read_text(encoding="utf-8"))
            self.assertIn("log", rec, "the verdict records no log path")
            log = root / rec["log"]
            self.assertTrue(log.is_file(), f"the recorded log {rec['log']} does not exist")
            self.assertIn("FIRST_LINE_MARKER", log.read_text(encoding="utf-8"),
                          "the log does not hold output from above the tail window")

    def test_a_later_run_does_not_overwrite_an_earlier_run_s_log(self) -> None:
        """MUTANT: write to one rolling `suite-last.log` instead of a per-run path.

        This is the criterion that decides the design, and the one the shipped rolling log
        fails. The moment you read a red run's log is precisely the moment a later run has
        already happened, so a log tied to "most recent" describes the wrong run exactly when
        it matters.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            _run(root, "tools", cmd="echo RUN_ONE_MARKER; exit 1")
            first = json.loads((root / VERDICT_REL).read_text(encoding="utf-8"))["log"]
            _run(root, "tools", cmd="echo RUN_TWO_MARKER; exit 1")
            second = json.loads((root / VERDICT_REL).read_text(encoding="utf-8"))["log"]
            self.assertNotEqual(first, second, "both runs wrote to one rolling log path")
            self.assertIn("RUN_ONE_MARKER", (root / first).read_text(encoding="utf-8"),
                          "the first run's log was overwritten by the second")

    def test_the_log_directory_is_bounded(self) -> None:
        """MUTANT: remove the prune, or raise the cap without bound.

        A directory of full-suite logs grows on every invocation. Asserts the cap holds after
        exceeding it, rather than asserting the exact keep count, so tightening the cap later
        does not redden a test about boundedness.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            for i in range(14):
                _run(root, "tools", cmd=f"echo run{i}; exit 0")
            logs = list((root / "sdlc-studio" / ".local" / "suite-logs").glob("*.log"))
        self.assertLessEqual(len(logs), 10,
                             f"the log directory is unbounded - {len(logs)} logs kept")

    def test_a_green_run_still_prints_only_the_verdict_line(self) -> None:
        """MUTANT: print the log path unconditionally rather than on red.

        The control. The single-line stdout contract is what makes the verdict readable, and
        a fix for the red path must not spend it.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            r = _run(root, "tools", cmd="echo noise; exit 0")
        self.assertEqual(1, len([ln for ln in r.stdout.splitlines() if ln.strip()]),
                         f"stdout is no longer one line: {r.stdout!r}")


if __name__ == "__main__":
    unittest.main()
