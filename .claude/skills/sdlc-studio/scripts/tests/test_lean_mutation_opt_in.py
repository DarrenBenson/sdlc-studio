"""US0921: the gate carries no mutation lane.

Mutation testing is an instrument an operator picks up with `mutation.py run`, not a lane the
gate reads. AC1 drives `gate.py --only mutation` through the CLI in a throwaway workspace and
checks the `window` lane, which shares the `mutation` module's window record, still refuses a
staged path an open rewrite window claims. AC2 asks the upgrade digest what arrived in the
version gap that brought the lane. Nothing reads this repository's own state.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/gate.py
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(SCRIPTS))
import gitutil  # noqa: E402 - confined git for the fixture repos
import gate  # noqa: E402
import project_upgrade  # noqa: E402


def _repo(tmp: str) -> Path:
    """A committed git repository holding an empty workspace and one source file."""
    root = Path(tmp)
    (root / "sdlc-studio" / ".local").mkdir(parents=True)
    (root / "tools").mkdir()
    (root / "tools" / "thing.py").write_text("VALUE = 1\n", encoding="utf-8")
    gitutil.git(["init", "-q"], cwd=root)
    gitutil.git(["add", "-A"], cwd=root)
    gitutil.git(["commit", "-qm", "fixture"], cwd=root)
    return root


class MutationOptInTests(unittest.TestCase):

    def test_no_mutation_lane_and_the_window_still_guards(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = _repo(t)
            proc = subprocess.run(
                [sys.executable, str(SCRIPTS / "gate.py"), "--root", str(root),
                 "--only", "mutation", "--format", "json"],
                capture_output=True, text=True, env=gitutil.git_env(), timeout=300)
            self.assertNotEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            rows = json.loads(proc.stdout)["checks"]
            self.assertEqual([r["check"] for r in rows], ["selection"], rows)
            self.assertIn("unknown check name(s): mutation", rows[0]["detail"])

            self.assertNotIn("mutation", gate.ON_DEMAND_CHECKS)
            self.assertNotIn("mutation", gate.ADVISORY_WHEN_ABSENT)
            self.assertFalse(hasattr(gate, "_mutation_coverage"))

            # the window lane stays, and still refuses a staged path an open window claims
            (root / "sdlc-studio" / ".local" / "mutation-window.json").write_text(json.dumps(
                {"owner": "the reviewer", "opened_at": "2026-09-25T10:00:00Z",
                 "paths": ["tools/thing.py"]}), encoding="utf-8")
            (root / "tools" / "thing.py").write_text("VALUE = 999\n", encoding="utf-8")
            gitutil.git(["add", "tools/thing.py"], cwd=root)
            report = gate.run_gate(str(root), only=["window"])
            self.assertFalse(report["ok"], report)
            lane = report["checks"][0]
            self.assertEqual((lane["check"], lane["status"]), ("window", "fail"), lane)
            self.assertTrue(lane["blocking"], lane)
            self.assertIn("tools/thing.py", lane["detail"])

    def test_an_upgrade_announces_no_mutation_lane(self) -> None:
        # 2.5.0 -> 3.4.0 is the gap in which the mutation lane arrived
        lanes = project_upgrade.new_advisory_lanes("2.5.0", "3.4.0")
        self.assertNotIn("mutation", [x["lane"] for x in lanes])
        for lane in lanes:
            self.assertNotIn("mutation", lane["baseline"], lane)


if __name__ == "__main__":
    unittest.main()
