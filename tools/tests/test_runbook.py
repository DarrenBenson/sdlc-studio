#!/usr/bin/env python3
"""The sprint toolchain runbook: ordered by step, and unable to rot silently."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))

import runbook  # noqa: E402

RUNBOOK = REPO / runbook.RUNBOOK_REL


class RunbookTests(unittest.TestCase):

    def test_every_step_names_its_command(self) -> None:
        """MUTANT: drop a step section, or a step's command column.

        Ordered by STEP, not by script: `reference-scripts.md` already answers "what does X
        do", and nobody planning a sprint has that question. The one they have is "what is
        next, and which command performs it".
        """
        text = RUNBOOK.read_text(encoding="utf-8")
        self.assertEqual([], runbook.missing_steps(text),
                         "the runbook has no section for a step of the cycle")
        self.assertEqual([], runbook.missing(REPO, text),
                         "the runbook names a command that does not exist")
        # PER STEP, not a global total. `len(commands(text)) >= 15` is satisfied by one rich
        # step carrying the tally for an empty one - and the empty step is precisely the one an
        # agent answers from memory. Blanking a whole step's table left the old assertion green.
        self.assertEqual([], runbook.steps_without_a_command(text),
                         "a step of the cycle names no command of its own")
        # ORDER, which membership cannot see. The runbook's whole claim over `reference-scripts`
        # is that it is ordered by step; reversing every section passed the old test.
        self.assertEqual([], runbook.out_of_order_steps(text),
                         "the steps are not in sprint order, which is the runbook's only claim")
        self.assertEqual([], runbook.missing_verbs(REPO, text),
                         "the runbook names a subcommand its script no longer offers")

    def test_each_step_names_what_it_replaces(self) -> None:
        """MUTANT: drop the `Instead of` column.

        The entry has to be findable from the WRONG instinct - the hand-rolled shape an agent
        is about to reach for - or it is only useful to somebody who already knows the tool
        exists, which is not who needs it.
        """
        text = RUNBOOK.read_text(encoding="utf-8")
        # The CELLS, not the header rows. `count("| Instead of |")` counts headers, so blanking
        # every "Instead of" cell in the shipped runbook - deleting the entire feature the
        # criterion is about - left this green.
        rows = [ln for ln in text.splitlines()
                if ln.startswith("|") and ln.count("|") >= 4
                and "Instead of" not in ln and not set(ln) <= set("|- :")]
        filled = [ln for ln in rows if ln.split("|")[-2].strip() not in ("", "-")]
        self.assertGreaterEqual(
            len(filled), 5,
            f"the `Instead of` column is empty on every row - the entry can then only be found "
            f"by somebody who already knows the tool exists, which is not who needs it "
            f"({len(filled)} filled of {len(rows)} rows)")

    def test_a_missing_command_fails_the_guard(self) -> None:
        """MUTANT: report a rotted runbook without failing.

        Built adversarially: a runbook naming a command that was renamed away must go red, or
        the guard pins nothing.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            target = root / runbook.RUNBOOK_REL
            target.parent.mkdir(parents=True, exist_ok=True)
            body = "\n".join(f"## {s}\n\n| Do | Command | Instead of |\n| --- | --- | --- |\n"
                             f"| x | `renamed_away.py verb` | y |\n"
                             for s in runbook.REQUIRED_STEPS)
            target.write_text(body, encoding="utf-8")
            self.assertEqual(1, runbook.main(["--root", str(root)]),
                             "a runbook naming a command that does not exist passed")

    def test_the_shipped_runbook_passes_its_own_guard(self) -> None:
        """The control. MUTANT: fail unconditionally."""
        self.assertEqual(0, runbook.main(["--root", str(REPO)]),
                         "the shipped runbook is refused by its own guard")


class RunbookGuardRunsInTheGateTests(unittest.TestCase):
    """BG0500: the guard existed and ran in no lane.

    `test_a_missing_command_fails_the_guard` above already proves the guard REFUSES. It said
    nothing about whether anything invokes it, and nothing did: the guard appeared in neither
    `.githooks/pre-commit` nor `package.json`, so it ran only when the whole tools suite ran.
    A gate belongs in the command people actually run, not in the step they are told to run
    (LL0027) - and the runbook is the document every agent is told to read before each sprint
    step, so it is exactly the file that rots quietly between suite runs.
    """

    HOOK = REPO / ".githooks" / "pre-commit"

    def test_the_guard_is_invoked_by_the_pre_commit_lane(self) -> None:
        """MUTANT: delete the `run "runbook"` lane from the hook."""
        hook = self.HOOK.read_text(encoding="utf-8")
        self.assertIn('run "runbook"', hook, "the runbook guard runs in no pre-commit lane")
        i = hook.index('run "runbook"')
        self.assertIn("tools/runbook.py", hook[i:i + 700],
                      "the lane is declared but invokes something other than the guard")

    def test_the_npm_chain_checks_what_the_hook_checks(self) -> None:
        """MUTANT: add the hook lane and leave `npm run lint` behind.

        The two drifting apart is how a contributor without the hooks enabled - or CI - stops
        checking something the hook checks, silently.
        """
        import json
        pkg = json.loads((REPO / "package.json").read_text(encoding="utf-8"))
        self.assertIn("lint:runbook", pkg["scripts"], "no npm script for the runbook guard")
        self.assertIn("runbook.py", pkg["scripts"]["lint:runbook"])
        self.assertIn("lint:runbook", pkg["scripts"]["lint"],
                      "the script exists but the `lint` chain never runs it")

    def test_the_repo_s_own_lane_roster_names_the_guard(self) -> None:
        """MUTANT: wire the lane and leave AGENTS.md's roster stale.

        That roster is the repo's written account of its own gates, and a guard nobody has
        written down is one nobody notices losing - which is why AGENTS.md keeps the list at
        all. This is the half of the AC that is about the document rather than the hook.
        """
        agents = (REPO / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("runbook.py", agents,
                      "AGENTS.md's pre-commit lane roster does not name the runbook guard")



if __name__ == "__main__":
    unittest.main()
