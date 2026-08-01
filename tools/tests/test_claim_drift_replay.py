"""US0597: the premise, replayed against the real commit rather than asserted.

An engineering seat refused the plan until this existed, on the grounds that both epics'
measurement criteria were owned by no story - so the sprint would ship a mechanism on a claim
nobody had checked. The replay then disproved the claim it was written to confirm, three times,
and each correction is pinned here.

Every test names the mutant it must fail on, per LL0050.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("csc", REPO / "tools" / "check_spec_claims.py")
csc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(csc)

#: The commit that moved the collapse signal from 2 to 3 in tools/gate_timing.py. The stale
#: claim it left behind was written in an EARLIER commit (10b6fd54) and this one never reopened
#: it - which is why no single-diff check could have caught BG0471, and why the lane reads the
#: unit's standing changelog.d paperwork as well as the diff.
DRIFT_COMMIT = "67fc683f"


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True).stdout


class ReplayTests(unittest.TestCase):

    def setUp(self) -> None:
        if not _git("cat-file", "-t", DRIFT_COMMIT).strip():
            self.skipTest(f"{DRIFT_COMMIT} is not in this clone")

    def _historical_tree(self, tmp: Path) -> Path:
        """The changelog.d fragment as it stood BEFORE the drifting commit."""
        root = tmp / "hist"
        (root / "changelog.d").mkdir(parents=True)
        frag = _git("show", f"{DRIFT_COMMIT}^:changelog.d/BG0413.md")
        (root / "changelog.d" / "BG0413.md").write_text(frag, encoding="utf-8")
        return root

    def test_the_lane_names_the_prose_drift_finding(self) -> None:
        """MUTANT: drop the standing-paperwork read, or compare per file instead of per hunk.
        Either must go red.

        Both were real states of this code. Per-file comparison returned ZERO on this commit,
        because gate_timing.py's own repair mentions 2 in a dozen places so `2` appeared on both
        sides and never read as replaced."""
        with tempfile.TemporaryDirectory() as d:
            root = self._historical_tree(Path(d))
            self.assertIn("exits 2", (root / "changelog.d" / "BG0413.md").read_text("utf-8"),
                          "the fixture is not the pre-drift state, so it proves nothing")
            diff = _git("show", DRIFT_COMMIT, "--format=", "-U0")
            found = csc.claim_drift(diff, root)
        named = {f["prose_file"] for f in found}
        self.assertIn("changelog.d/BG0413.md", named,
                      "the lane misses the exact stale claim BG0471 was filed for")

    def test_a_clean_diff_replays_silent(self) -> None:
        """The control. MUTANT: report unconditionally - this must go red, or the replay proves
        only that the lane fires, which is what a lane that always fires also does."""
        with tempfile.TemporaryDirectory() as d:
            root = self._historical_tree(Path(d))
            # a commit touching prose only: no hunk replaces a literal, so nothing can be stale
            diff = _git("show", DRIFT_COMMIT, "--format=", "-U0", "--", "changelog.d")
            self.assertEqual([], csc.claim_drift(diff, root))

    def test_prose_narrating_the_change_is_not_flagged(self) -> None:
        """MUTANT: drop the `prose_nums & new_nums` guard. This must go red.

        Prose saying "the exit code was 2 ... it is now 3" names both values and is current.
        The first firing replay's loudest hits were all honest narration of this shape, and a
        lane that flags them is the noise that gets a lane switched off."""
        diff = ("diff --git a/tools/thing.py b/tools/thing.py\n"
                "--- a/tools/thing.py\n+++ b/tools/thing.py\n@@ -1 +1 @@\n"
                "-    return 2\n+    return 3\n"
                "diff --git a/changelog.d/BG0001.md b/changelog.d/BG0001.md\n"
                "--- a/changelog.d/BG0001.md\n+++ b/changelog.d/BG0001.md\n@@ -0,0 +1 @@\n"
                "+- the exit code was 2 and is now 3\n")
        self.assertEqual([], csc.claim_drift(diff))

    #: The evidence the criterion names. Asserted against the SHIPPED file, not a temp-dir
    #: accumulator: the previous version of this test built its own record in a
    #: TemporaryDirectory and asserted `runs == 1` on it, which is true of any record the test
    #: itself just wrote and says nothing about whether the replay was ever run. That is a
    #: verifier that cannot fail on its subject, and it stood over a criterion ticked
    #: `Verified: yes` whose named file did not exist (BG0482).
    REPLAY = Path(__file__).resolve().parents[2] / "sdlc-studio" / "retros" / "evidence" \
        / "claim-drift-replay.json"

    def test_the_before_and_after_is_recorded(self) -> None:
        """MUTANT: delete either arm of the replay record, or the units it covers.

        The criterion requires the blocking-finding count BEFORE and AFTER the scoping rule,
        written to the evidence directory, with the units it covers. Each of those three is
        asserted separately, because a record carrying two of them satisfies no criterion."""
        self.assertTrue(self.REPLAY.exists(),
                        f"the criterion names {self.REPLAY.name} and it does not exist")
        rec = json.loads(self.REPLAY.read_text(encoding="utf-8"))
        for arm in ("before", "after"):
            self.assertIn(arm, rec, f"the record has no {arm!r} arm to compare")
            self.assertIsInstance(rec[arm].get("findings_total"), int,
                                  f"the {arm!r} arm carries no finding count")
        self.assertTrue(rec.get("units_covered"),
                        "the record does not say which units it covers")
        self.assertGreaterEqual(rec["corpus"]["commits"], 2,
                                "a single-commit replay is the premise, not a test of it")
        # The direction is the claim being made. A record whose 'after' is no better than its
        # 'before' would satisfy every assertion above while showing the repair did nothing.
        self.assertLess(rec["after"]["findings_total"], rec["before"]["findings_total"],
                        "the recorded after-count is not below the before-count")

    def test_the_after_arm_records_no_empty_anchors(self) -> None:
        """MUTANT: let a finding with an empty `code` through claim_drift again.

        Held apart from the before-and-after test above so each criterion discriminates: that
        one asks whether the measurement was TAKEN, this one asks what it SAYS. A single
        selector covering both means a regression in either fails both and neither names which
        (the verify-ratchet rule).

        This is the class the repair eliminates outright rather than reduces, so zero is the
        assertion - anything above it means a report naming no code survived.
        """
        rec = json.loads(self.REPLAY.read_text(encoding="utf-8"))
        self.assertEqual(
            0, rec["after"]["findings_with_empty_code_anchor"],
            "findings naming no code survive in the after arm")
        self.assertGreater(
            rec["before"]["findings_with_empty_code_anchor"], 0,
            "the before arm records no empty anchors, so it is not measuring the defect")

    def test_the_yield_accumulator_still_counts(self) -> None:
        """MUTANT: stop accumulating in record_yield. This must go red.

        Separate from the replay record above: this pins the per-run counter the later
        blocking decision reads, and it is the assertion the old test was actually making."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / ".local").mkdir(parents=True)
            (root / "changelog.d").mkdir(parents=True)
            (root / "changelog.d" / "BG0001.md").write_text(
                "- it exits 2 on collapse\n", encoding="utf-8")
            diff = ("diff --git a/tools/thing.py b/tools/thing.py\n"
                    "--- a/tools/thing.py\n+++ b/tools/thing.py\n@@ -1,2 +1,2 @@\n"
                    " def collapse():\n"
                    "-    return 2\n+    return 3\n")
            csc.record_yield(root, diff)
            rec = json.loads((root / "sdlc-studio" / ".local"
                              / "claim-drift-yield.json").read_text(encoding="utf-8"))
        self.assertEqual(1, rec["runs"])
        self.assertGreaterEqual(rec["findings"], 1,
                                "the replay recorded a run but counted no findings")


if __name__ == "__main__":
    unittest.main()
