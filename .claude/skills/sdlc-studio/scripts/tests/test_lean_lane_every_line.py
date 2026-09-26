"""BG0777: the sprint lane runner and the revert check run every `Verify:` line of a criterion.

BG0687 made `verify_ac.py run` execute every line; the lane runner and the revert check still
read only the first, so a stacked criterion was red to one command and green to the other.
Each test drives a shipped command as a subprocess against a throwaway workspace (a real git
repository for the revert check). Nothing reads this repository's own artefacts or state.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/, for the sibling helper
import gitutil  # noqa: E402 - the confined git runner every fixture repo goes through

_PASS = "shell test -d /"
_FAIL = "shell test -d /nonexistent-bg0777"

_BUG = ("# BG0001: a bug\n\n> **Status:** In Progress\n> **Severity:** medium\n"
        "> **Affects:** scripts/prod.py\n> **Points:** 1\n\n"
        "## Acceptance Criteria\n\n- [ ] **AC1** Given a, when b, then c in both environments\n"
        "  - **Verify:** {first}\n  - **Verify:** {second}\n")


def _cli(script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(SCRIPTS / script), *args],
                          capture_output=True, text=True, check=False, timeout=300)


def _workspace(root: Path, first: str, second: str) -> None:
    (root / "sdlc-studio" / "stories").mkdir(parents=True)
    (root / "sdlc-studio" / "bugs").mkdir(parents=True)
    (root / "scripts").mkdir()
    (root / "scripts" / "prod.py").write_text("BASE_ONLY = 1\n", encoding="utf-8")
    (root / "sdlc-studio" / "bugs" / "BG0001-a-bug.md").write_text(
        _BUG.format(first=first, second=second), encoding="utf-8")


class LaneEveryLineTests(unittest.TestCase):
    def test_a_red_second_line_is_not_fixed_on_lane_return(self) -> None:
        """AC1. MUTANT: `lane_verify` running only `block.verifier` (HEAD before the fix), which
        returns `fixed` with the first line's green and never names the red one."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _workspace(root, _PASS, _FAIL)
            ran = _cli("verify_ac.py", "run", "--id", "BG0001", "--dry-run", "--root", str(root))
            ran_out = ran.stdout + ran.stderr
            self.assertIn(f"FAIL AC1: {_FAIL}", ran_out, ran_out)
            lane = _cli("sprint.py", "lane", "return", "--units", "BG0001", "--format", "json",
                        "--root", str(root))
            self.assertEqual(1, lane.returncode, lane.stdout + lane.stderr)
            res = json.loads(lane.stdout)[0]
            self.assertNotEqual("fixed", res["outcome"], res)
            self.assertEqual("blocked", res["outcome"], res)
            crit = res["verification"]["criteria"][0]
            self.assertEqual(("AC1", "failed"), (crit["ac"], crit["state"]), crit)
            # the SAME line `verify_ac run` names, not the first line of the block
            self.assertEqual(_FAIL, crit["verifier"], crit)
            self.assertEqual(["AC1"], res["verification"]["blocking"])
            # the positive control: both lines green returns what the lane claimed
            (root / "sdlc-studio" / "bugs" / "BG0001-a-bug.md").write_text(
                _BUG.format(first=_PASS, second="shell test -e /"), encoding="utf-8")
            green = _cli("sprint.py", "lane", "return", "--units", "BG0001", "--format", "json",
                         "--root", str(root))
            self.assertEqual(0, green.returncode, green.stdout + green.stderr)
            self.assertEqual("fixed", json.loads(green.stdout)[0]["outcome"])

    def test_the_revert_check_runs_every_line(self) -> None:
        """AC2. MUTANT: the revert check reading only the first line. Two fixtures:

        * line 1 stays green without the change and line 2 goes red. First-line-only reads the
          criterion green and REFUSES a unit whose second line does reach the change.
        * line 1 goes red and line 2 stays green at base as well. First-line-only never runs
          line 2, so the line that does not reach the change is never named.
        """
        stays_green = "grep BASE_ONLY scripts/prod.py"
        goes_red = "grep SHIPPED_MARKER scripts/prod.py"
        for first, second in ((stays_green, goes_red), (goes_red, stays_green)):
            with self.subTest(first=first), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _workspace(root, first, second)
                for args in (("init", "-q"), ("config", "user.email", "t@example.com"),
                             ("config", "user.name", "t"), ("add", "-A"),
                             ("commit", "-qm", "base")):
                    gitutil.git(list(args), root)
                base = gitutil.git(["rev-parse", "HEAD"], root).stdout.decode().strip()
                (root / "scripts" / "prod.py").write_text(
                    'BASE_ONLY = 1\nSHIPPED_MARKER = "SHIPPED_MARKER"\n', encoding="utf-8")
                gitutil.git(["commit", "-qam", "ship"], root)
                proc = _cli("verify_ac.py", "revert-check", "--unit", "BG0001", "--base", base,
                            "--format", "json", "--root", str(root))
                self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
                res = json.loads(proc.stdout)
                self.assertEqual("pass", res["status"], res)
                self.assertEqual(["AC1"], res["red"], res)
                lines = res["criteria"][0]["lines"]
                self.assertEqual([(first, "red" if first == goes_red else "green"),
                                  (second, "red" if second == goes_red else "green")],
                                 [(ln["verifier"], ln["state"]) for ln in lines], res)
                # the line that passes at base as well is caught, and named in the text report
                text = _cli("verify_ac.py", "revert-check", "--unit", "BG0001", "--base", base,
                            "--root", str(root)).stdout
                self.assertRegex(text, rf"green\s+{stays_green}", text)
                self.assertEqual("", gitutil.git(["status", "--porcelain"], root)
                                 .stdout.decode(), "the revert was not restored")


if __name__ == "__main__":
    unittest.main()
