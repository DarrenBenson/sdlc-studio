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
            # Carries the CONTEXT line a real `git diff` emits. Without it the only tie
            # between the code and the prose is the digit 2, which is no longer a finding
            # on its own (BG0479) - so a fixture lacking it would be asserting that the
            # yield counts noise.
            diff = ("diff --git a/tools/thing.py b/tools/thing.py\n"
                    "--- a/tools/thing.py\n+++ b/tools/thing.py\n@@ -1,2 +1,2 @@\n"
                    " def collapse():\n"
                    "-    return 2\n+    return 3\n"
                    "diff --git a/changelog.d/BG0001.md b/changelog.d/BG0001.md\n"
                    "--- a/changelog.d/BG0001.md\n+++ b/changelog.d/BG0001.md\n@@ -0,0 +1,1 @@\n"
                    "+- it exits 2 on collapse\n")
            csc.record_yield(root, diff)
            rec = json.loads(
                (root / "sdlc-studio" / ".local" / "claim-drift-yield.json")
                .read_text(encoding="utf-8"))
        self.assertGreaterEqual(rec["findings"], 1, "the yield record counts no findings")
        self.assertIn("runs", rec, "the record cannot say how many runs produced that count")


class DiscriminationTests(unittest.TestCase):
    """The two faults a corpus replay found: 81% of findings named no code, and a shared
    digit was treated as a shared subject (BG0479).

    Both are pinned by asserting on the OUTPUT SET rather than on a count, because a lane
    that simply stopped firing would satisfy a count assertion while being just as useless.
    Each case therefore carries its own positive control: the same diff, altered only in the
    way that should make it fire, must still fire.
    """

    def _drift(self, diff: str):
        sys.path.insert(0, str(REPO / "tools"))
        import check_spec_claims as csc
        return csc.claim_drift(diff)

    #: The added side carries no integer at all, so every number on the removed side used to
    #: read as "replaced" - by nothing. This is the `-RETRIES = 2` / `+RETRIES = LIMIT` shape.
    NO_INT_ADDED = (
        "diff --git a/tools/retry.py b/tools/retry.py\n"
        "--- a/tools/retry.py\n+++ b/tools/retry.py\n@@ -1,1 +1,1 @@\n"
        "-DEFAULT_RETRIES = 2\n+DEFAULT_RETRIES = RETRY_LIMIT\n"
        "diff --git a/changelog.d/BG0001.md b/changelog.d/BG0001.md\n"
        "--- a/changelog.d/BG0001.md\n+++ b/changelog.d/BG0001.md\n@@ -0,0 +1,1 @@\n"
        "+- default_retries stays at 2 for now\n")

    def test_a_finding_never_names_an_empty_code_anchor(self) -> None:
        """Mutant: delete the `if not new_nums: continue` guard in claim_drift.

        Without it this diff yields a finding whose `code` is the empty string, printing as
        `... while tools/retry.py in this diff carries ''`. That was 191 of 235 findings over
        the 40-commit replay - a report naming nothing the reader can act on.
        """
        findings = self._drift(self.NO_INT_ADDED)
        empty = [f for f in findings if not f["code"]]
        self.assertEqual(
            empty, [],
            "a finding was emitted whose code anchor is empty - it names no code to act on")

    def test_a_replacement_that_does_name_a_new_value_still_fires(self) -> None:
        """Positive control for the guard above: the ONLY change from NO_INT_ADDED is that the
        added line carries an integer, so there is a real replacement to reason about."""
        diff = self.NO_INT_ADDED.replace(
            "+DEFAULT_RETRIES = RETRY_LIMIT", "+DEFAULT_RETRIES = 5")
        self.assertTrue(
            self._drift(diff),
            "a genuine literal replacement stopped being reported - the guard is too broad")

    #: A column-count condition moving 6 -> 7, beside prose about an unrelated subject that
    #: merely contains the digit 6. This is what fired against changelog.d/BG0467.md.
    DIGIT_ONLY = (
        "diff --git a/scripts/critic.py b/scripts/critic.py\n"
        "--- a/scripts/critic.py\n+++ b/scripts/critic.py\n@@ -1,1 +1,1 @@\n"
        "-        if len(cells) == 6:\n+        if len(cells) == 7:\n"
        "diff --git a/changelog.d/BG0002.md b/changelog.d/BG0002.md\n"
        "--- a/changelog.d/BG0002.md\n+++ b/changelog.d/BG0002.md\n@@ -0,0 +1,1 @@\n"
        "+- the commit gate left main red for 6 commits\n")

    def test_a_shared_digit_alone_is_not_a_finding(self) -> None:
        """Mutant: delete the `if not (context & _prose_tokens(prose_line)): continue` clause.

        Without it, prose is flagged for containing the replaced digit even when it names
        nothing the changed code names. Here the prose is about commits on main and the code
        is about a table's column count; they share only the character 6.
        """
        self.assertEqual(
            self._drift(self.DIGIT_ONLY), [],
            "prose sharing only a digit with the changed code was reported as drift")

    def test_prose_naming_the_changed_code_still_fires(self) -> None:
        """Positive control for the token requirement: same diff, but the prose now names the
        subject (`cells`), so it is genuinely asserting the old value of this thing."""
        diff = self.DIGIT_ONLY.replace(
            "+- the commit gate left main red for 6 commits",
            "+- a verdict row carries 6 cells")
        self.assertTrue(
            self._drift(diff),
            "prose asserting the old value of the changed symbol stopped being reported")


if __name__ == "__main__":
    unittest.main()
