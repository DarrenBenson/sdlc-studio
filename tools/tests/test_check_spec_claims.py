"""Unit tests for tools/check_spec_claims.py (US0453, US0454).

Run from the repo root:
    python3 -m unittest discover -s tools/tests
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import shutil
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "check_spec_claims.py"
_spec = importlib.util.spec_from_file_location("check_spec_claims", TOOLS)
assert _spec and _spec.loader
check_spec_claims = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_spec_claims)

SKILL = check_spec_claims.SKILL_DIR


class CountableClaimTests(unittest.TestCase):
    """US0453. The TRD and TSD make claims a reader takes as fact - "60+ scripts" - and those
    were exact numbers once, which went stale by about a fifth before anyone noticed. A band
    still rots; it just rots downward and silently, because nothing counted the tree."""

    def _repo(self, trd: str, scripts: int = 3) -> Path:
        d = Path(tempfile.mkdtemp(prefix="claims_"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / SKILL / "scripts").mkdir(parents=True)
        for i in range(scripts):
            (d / SKILL / "scripts" / f"s{i}.py").write_text("x = 1\n", encoding="utf-8")
        (d / "sdlc-studio").mkdir(parents=True)
        (d / "sdlc-studio" / "trd.md").write_text(trd, encoding="utf-8")
        return d

    def test_a_claim_disagreeing_with_the_census_fails(self) -> None:
        root = self._repo("The skill ships 10+ scripts.\n", scripts=3)
        errors = check_spec_claims.check(root)
        self.assertTrue(errors, "a claim of 10+ over a tree of 3 was not reported")
        self.assertIn("10", errors[0])
        self.assertIn("3", errors[0], "the counted value was not named beside the claimed one")

    def test_an_agreeing_claim_passes(self) -> None:
        """The positive control. Without it a checker that reports everything looks correct."""
        self.assertEqual([], check_spec_claims.check(
            self._repo("The skill ships 2+ scripts.\n", scripts=3)))

    def test_the_expected_count_is_derived_from_the_tree_not_stored(self) -> None:
        """Add a script and the SAME claim becomes true, with no edit to the checker. A guard
        carrying its own copy of the answer is a second place for the answer to be wrong."""
        root = self._repo("The skill ships 4+ scripts.\n", scripts=3)
        self.assertTrue(check_spec_claims.check(root), "3 scripts satisfied a 4+ claim")
        (root / SKILL / "scripts" / "extra.py").write_text("y = 2\n", encoding="utf-8")
        self.assertEqual([], check_spec_claims.check(root),
                         "the expected count did not move with the repo")

    def test_an_unparseable_marked_claim_is_reported_not_skipped(self) -> None:
        """A claim nobody can check is the finding. A silent skip is indistinguishable from a
        pass, which is the failure mode this whole tool exists to remove."""
        root = self._repo("Lots of things. <!-- derived: mumble mumble -->\n", scripts=3)
        errors = check_spec_claims.check(root)
        self.assertTrue(errors, "an unparseable marked claim passed in silence")
        self.assertIn("cannot be checked", errors[0])

    def test_a_marked_claim_naming_an_unknown_census_is_reported(self) -> None:
        root = self._repo("Many. <!-- derived: unicorns >= 5 -->\n", scripts=3)
        errors = check_spec_claims.check(root)
        self.assertTrue(errors, "a claim naming a census nothing counts passed")
        self.assertIn("cannot be checked", errors[0])

    def test_a_marked_claim_that_is_checkable_is_checked(self) -> None:
        """The positive control for the marker path: it must be able to PASS, or "reported"
        above would be true of every marker and prove nothing."""
        self.assertEqual([], check_spec_claims.check(
            self._repo("Some. <!-- derived: scripts >= 2 -->\n", scripts=3)))
        self.assertTrue(check_spec_claims.check(
            self._repo("Some. <!-- derived: scripts >= 9 -->\n", scripts=3)))

    def test_an_absent_spec_is_not_a_failure(self) -> None:
        """A consuming project need not carry every spec, and holding it to one it never
        adopted would make the guard unusable outside this repo."""
        d = Path(tempfile.mkdtemp(prefix="claims_"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.assertEqual([], check_spec_claims.check(d))

    def test_the_real_repo_specs_agree_with_their_census(self) -> None:
        """Against the live tree, because this guard's whole value is that it runs here."""
        repo = Path(__file__).resolve().parents[2]
        self.assertEqual([], check_spec_claims.check(repo),
                         "this repository's own specs contradict its census")


class GateLaneTests(unittest.TestCase):
    """US0453 AC4: drift is caught at the commit that causes it, not at the next audit."""

    def test_the_spec_claim_check_is_a_gate_lane(self) -> None:
        hook = Path(__file__).resolve().parents[2] / ".githooks" / "pre-commit"
        self.assertTrue(hook.is_file(), "no pre-commit hook to carry the lane")
        self.assertIn("check_spec_claims.py", hook.read_text(encoding="utf-8"),
                      "the spec-claim check is not run by the gate people actually run")

    def test_the_checker_exits_non_zero_on_a_contradiction(self) -> None:
        """The lane is only a lane if the command it runs can fail."""
        d = Path(tempfile.mkdtemp(prefix="claims_"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / SKILL / "scripts").mkdir(parents=True)
        (d / "sdlc-studio").mkdir(parents=True)
        (d / "sdlc-studio" / "trd.md").write_text("99+ scripts.\n", encoding="utf-8")
        with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(1, check_spec_claims.main(["--root", str(d)]))


class TimingClaimTests(unittest.TestCase):
    """US0454. A timing claim is the easiest kind to write and the hardest to keep true, and
    this project has already had to correct one performance figure built from a cherry-picked
    pair. Claims are checked against the RECORDED series, at its median - a bound justified by
    the fastest run ever taken is a bound nobody experiences."""

    def _repo(self, tsd: str, timings: dict | None = None) -> Path:
        import json
        d = Path(tempfile.mkdtemp(prefix="timing_"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / "sdlc-studio" / ".local").mkdir(parents=True)
        (d / "sdlc-studio" / "tsd.md").write_text(tsd, encoding="utf-8")
        if timings is not None:
            (d / check_spec_claims.TIMINGS_REL).write_text(json.dumps(timings), encoding="utf-8")
        return d

    def test_a_timing_claim_contradicted_by_measurement_fails(self) -> None:
        root = self._repo("The gate runs fast. <!-- measured: total <= 300s -->\n",
                          {"total": [400.0, 420.0, 410.0]})
        errors = check_spec_claims.check(root)
        self.assertTrue(errors, "a 300s bound against a 410s median was not reported")
        self.assertIn("300", errors[0], "the asserted bound was not named")
        self.assertIn("410", errors[0], "the measured value was not named")

    def test_a_satisfied_timing_claim_passes(self) -> None:
        """The positive control: a checker that fails every timing claim would pass the test
        above while being useless."""
        self.assertEqual([], check_spec_claims.check(
            self._repo("Fast. <!-- measured: total <= 500s -->\n", {"total": [400.0, 420.0]})))

    def test_absent_measurement_is_unverifiable_not_a_pass(self) -> None:
        """The whole point. Treating a missing measurement as agreement is how a timing claim
        survives every run that never took the measurement it asserts."""
        root = self._repo("Fast. <!-- measured: total <= 300s -->\n", {})
        errors = check_spec_claims.check(root)
        self.assertTrue(errors, "an unmeasured claim was treated as agreement")
        self.assertIn("UNVERIFIABLE", errors[0])
        self.assertIn("not agreement", errors[0])

    def test_a_missing_timings_file_is_also_unverifiable(self) -> None:
        root = self._repo("Fast. <!-- measured: total <= 300s -->\n", timings=None)
        self.assertTrue(check_spec_claims.check(root),
                        "with no timings file at all the claim silently passed")

    def test_the_median_is_used_not_the_best_run(self) -> None:
        """A bound justified by the fastest measurement ever taken is a bound nobody
        experiences - the exact shape of the over-claim this project already corrected once."""
        root = self._repo("Fast. <!-- measured: total <= 310s -->\n",
                          {"total": [300.0, 400.0, 420.0]})
        self.assertTrue(check_spec_claims.check(root),
                        "the fastest run was used to justify the bound")

    def test_a_lower_bound_claim_is_supported(self) -> None:
        self.assertEqual([], check_spec_claims.check(
            self._repo("Slow. <!-- measured: total >= 100s -->\n", {"total": [400.0]})))
        self.assertTrue(check_spec_claims.check(
            self._repo("Slow. <!-- measured: total >= 900s -->\n", {"total": [400.0]})))


if __name__ == "__main__":
    unittest.main()
