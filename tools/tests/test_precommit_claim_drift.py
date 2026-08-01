"""US0585: the claim-drift lane runs in the real commit gate, and does not block.

The lane reports a contradiction between a diff's code and its own prose. It ships ADVISORY
(D0105): a new blocking check on a gate already ~40% over its declared ceiling has to earn its
place on measured yield, not on assertion. These tests drive the REAL tracked hook in a hermetic
repo, because a lane whose only evidence is a unit test is one end of a contract with the other
end free - the shape BG0413 shipped and an independent seat then found.

Each test names the mutant it must fail on, per LL0050.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Importable under BOTH runners. The sibling fixture module is found via PYTHONPATH
# under `unittest discover`, but pytest - which `verify_ac` invokes to check a
# criterion - does not put this directory on the path, so the import failed there and
# the story's own verifier could not run.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import test_precommit_window_guard as _wg

_git = _wg._git
REPO = Path(__file__).resolve().parents[2]

#: A staged change whose code moves to 3 while its own changelog fragment still says 2 -
#: BG0471's shape, which cost an adversarial review round to find.
DRIFTING_CODE = "def collapse():\n    return 3\n"
DRIFTING_PROSE = "<!-- section: Fixed -->\n- the check now exits 2 when the suite collapses\n"
AGREEING_PROSE = "<!-- section: Fixed -->\n- the check now exits 3 when the suite collapses\n"


class LaneTests(unittest.TestCase):
    """Borrows the hermetic fixture without inheriting its cases."""

    def setUp(self) -> None:
        self._fixture = _wg.WindowGuardTests("run")

    def _commit_with(self, prose: str) -> tuple[int, str]:
        """A commit that MODIFIES a literal, which is the shape the lane detects.

        A first version created `tools/thing.py` new. A new file has no removed lines, so there
        is no replaced literal and the lane correctly found nothing - the fixture was modelling
        a shape BG0471 never had. The base state carries `return 2`; the commit under test
        moves it to 3 while the prose keeps saying 2.
        """
        with tempfile.TemporaryDirectory() as d:
            root = self._fixture._repo(Path(d))
            # the REAL checker, not a stub: this test is about the lane's verdict reaching the
            # gate, and a stubbed checker would prove only that the hook can call something.
            (root / "tools" / "check_spec_claims.py").write_text(
                (REPO / "tools" / "check_spec_claims.py").read_text(encoding="utf-8"),
                encoding="utf-8")
            (root / "tools" / "thing.py").write_text("def collapse():\n    return 2\n",
                                                     encoding="utf-8")
            _git(root, "add", "-A")
            _git(root, "commit", "-q", "--no-verify", "-m", "base: thing returns 2")
            (root / "changelog.d").mkdir(parents=True, exist_ok=True)
            (root / "changelog.d" / "BG0001.md").write_text(prose, encoding="utf-8")
            _git(root, "add", "-A")
            return self._fixture._commit(root, "tools/thing.py", DRIFTING_CODE)

    def test_the_lane_reports_and_does_not_block(self) -> None:
        """MUTANT: fold the drift findings into the checker's exit code. This must go red.

        The finding must reach the operator AND the commit must land, or an advisory lane has
        silently become a blocking one on a gate already over its ceiling."""
        rc, out = self._commit_with(DRIFTING_PROSE)
        self.assertEqual(0, rc, f"an advisory drift finding blocked a legitimate commit:\n{out}")
        self.assertIn("gate green.", out)
        # ...and the finding REACHED the operator. Asserting only that the commit lands is
        # satisfied by a hook that drops the finding silently - mutation proved exactly that,
        # so the report is now half the contract rather than an implied one.
        self.assertIn("CLAIM-DRIFT", out,
                      "the commit landed but the finding never reached the operator")

    def test_a_diff_whose_prose_agrees_is_silent(self) -> None:
        """The control. MUTANT: report unconditionally. This must go red, or the lane is noise
        on every commit and gets switched off, which is the failure it exists to avoid."""
        rc, out = self._commit_with(AGREEING_PROSE)
        self.assertEqual(0, rc, out)
        self.assertNotIn("CLAIM-DRIFT", out)

    def test_the_lane_is_named_in_the_gate_roster(self) -> None:
        """MUTANT: remove the lane from AGENTS.md's roster. This must go red.

        A guard nobody has written down is one nobody notices losing - the contract a reviewer
        added after finding this repo's own account of its gates incomplete."""
        agents = (REPO / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("claim-drift", agents,
                      "AGENTS.md's lane roster does not name the claim-drift lane")

    def test_the_yield_is_recorded(self) -> None:
        """MUTANT: stop recording the count. This must go red.

        The decision to make this lane blocking is explicitly OUT of this sprint - the lane
        ships here, so a sprint's worth of yield cannot exist yet. What must exist is the
        number, so that later decision has something to read rather than an impression."""
        import json
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / "retros" / "evidence").mkdir(parents=True)
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "csc", REPO / "tools" / "check_spec_claims.py")
            csc = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(csc)
            diff = ("diff --git a/tools/thing.py b/tools/thing.py\n"
                    "--- a/tools/thing.py\n+++ b/tools/thing.py\n@@ -1,1 +1,1 @@\n"
                    "-    return 2\n+    return 3\n"
                    "diff --git a/changelog.d/BG0001.md b/changelog.d/BG0001.md\n"
                    "--- a/changelog.d/BG0001.md\n+++ b/changelog.d/BG0001.md\n@@ -0,0 +1,1 @@\n"
                    "+- it exits 2 on collapse\n")
            csc.record_yield(root, diff)
            rec = json.loads(
                (root / "sdlc-studio" / "retros" / "evidence" / "claim-drift-yield.json")
                .read_text(encoding="utf-8"))
        self.assertGreaterEqual(rec["findings"], 1, "the yield record counts no findings")
        self.assertIn("runs", rec, "the record cannot say how many runs produced that count")


if __name__ == "__main__":
    unittest.main()
