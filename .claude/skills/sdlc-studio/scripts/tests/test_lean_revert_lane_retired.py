"""US0784: the advisory `revert-check` gate lane is retired; the per-unit CLI stays.

The release boundary re-ran every batch unit's verifiers with its change reverted IN THE LIVE
TREE, rewriting tracked production files while the gate ran (CR0552), and the lane never
blocked. Its last measured yield, from the gitignored accumulator it alone wrote, was 71 runs,
730 units examined and 18 that would have been refused. The lane, its accumulator and every
mention of them in the shipped gate, hook and help are deleted. `verify_ac.py revert-check
--unit`, which an author runs deliberately on one unit, stays.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/gate.py
from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
REPO = SCRIPTS.parents[3]

#: The shipped files that named the lane, each read whole.
SHIPPED = (SCRIPTS / "gate.py", REPO / ".githooks" / "pre-push", REPO / "tools" / "enable-hooks.sh",
           SCRIPTS.parent / "help" / "gate.md")


def _env() -> dict:
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def _cli(script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPTS / script), *args], cwd=REPO,
                          capture_output=True, text=True, timeout=300, check=False, env=_env())


class RevertLaneRetiredTests(unittest.TestCase):
    """AC1-AC2."""

    def test_the_release_boundary_registers_no_revert_check_lane(self) -> None:
        """AC1. MUTANTS: (1) keep `registry["revert-check"]` at the release boundary - the
        valid-lane list names it; (2) delete the `revert-check` subcommand from `verify_ac.py`
        with the lane - its `--help` no longer exits 0."""
        r = _cli("gate.py", "--boundary", "release", "--only", "no-such-lane", "--root", str(REPO))
        out = r.stdout + r.stderr
        listed = next((ln for ln in out.splitlines() if "valid:" in ln), "")
        self.assertTrue(listed, "premise: the refusal printed no valid-lane list:\n" + out)
        lanes = [x.strip() for x in listed.split("valid:", 1)[1].split(",")]
        self.assertIn("release-rehearsal", lanes, "premise: the release lanes are listed:\n" + out)
        self.assertNotIn("revert-check", lanes,
                         "the release boundary still registers the revert-check lane:\n" + out)
        cli = _cli("verify_ac.py", "revert-check", "--help")
        self.assertEqual(0, cli.returncode,
                         "the per-unit `verify_ac.py revert-check` went with the lane:\n"
                         + cli.stdout + cli.stderr)
        self.assertIn("--unit", cli.stdout, "the per-unit command lost its --unit argument")

    def test_no_shipped_file_names_the_lane_or_its_yield_file(self) -> None:
        """AC2. MUTANTS: (1) keep `_REVERT_YIELD_REL` in gate.py; (2) keep the lane in the
        pre-push release cost note; (3) keep it in enable-hooks.sh's hook summary; (4) keep the
        lane's paragraph in help/gate.md. Each is a mention the per-unit CLI does not account
        for: a mention of `verify_ac.py revert-check` itself is allowed."""
        for path in SHIPPED:
            with self.subTest(file=str(path.relative_to(REPO))):
                text = path.read_text(encoding="utf-8").replace("verify_ac.py revert-check", "")
                self.assertNotIn("revert-check-yield.json", text)
                self.assertNotIn("revert-check", text,
                                 f"{path.relative_to(REPO)} still names the revert-check lane")


if __name__ == "__main__":
    unittest.main()
