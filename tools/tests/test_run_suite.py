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
        """
        with tempfile.TemporaryDirectory() as d:
            root = _fixture(Path(d))
            _run(root, "scripts", cmd="exit 0")
            r = _run(root, "--check")
        self.assertEqual(0, r.returncode,
                         f"a current green verdict was refused:\n{r.stdout}{r.stderr}")


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


if __name__ == "__main__":
    unittest.main()
