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
        """Both gates, and the DOCUMENTED list too. An independent reviewer found `npm run lint`
        had no `lint:spec-claims` at all and AGENTS.md's guard table documented neither new
        checker - in a batch about spec truth, the repo's own record of its gates was incomplete.
        Asserting only that the string appears in the hook missed both."""
        import json as _json
        repo = Path(__file__).resolve().parents[2]
        hook = repo / ".githooks" / "pre-commit"
        self.assertTrue(hook.is_file(), "no pre-commit hook to carry the lane")
        self.assertIn("check_spec_claims.py", hook.read_text(encoding="utf-8"),
                      "the spec-claim check is not run by the gate people actually run")
        pkg = _json.loads((repo / "package.json").read_text(encoding="utf-8"))["scripts"]
        self.assertIn("lint:spec-claims", pkg, "no npm lint script for the checker")
        self.assertIn("lint:spec-claims", pkg["lint"],
                      "the checker is not chained into `npm run lint`")
        self.assertIn("check_spec_claims.py", (repo / "AGENTS.md").read_text(encoding="utf-8"),
                      "AGENTS.md's guard table does not document the checker")

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
        """The whole point, and the distinction the first version got wrong: an unmeasured claim
        must be SAID, and it must not silently read as agreement. It does not FAIL the lane -
        the timing store is machine-local, so failing on its absence made the lane unusable in
        CI and a lane nobody can satisfy gets switched off."""
        import contextlib
        import io
        root = self._repo("Fast. <!-- measured: total <= 300s -->\n", {})
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            errors = check_spec_claims.check(root)
        self.assertEqual([], errors, "an unmeasurable claim failed rather than being reported")
        note = err.getvalue()
        self.assertIn("UNVERIFIABLE", note, "the gap was silent, which IS treating it as a pass")
        self.assertIn("not agreement", note)

    def test_a_missing_timings_file_is_REPORTED_not_failed(self) -> None:
        """An independent reviewer's finding: the timing store is machine-local and gitignored,
        so a fresh clone and CI have none. Failing there made the lane unusable, which means it
        gets switched off - worse than a stated gap. "Never a pass" is honoured by SAYING so."""
        import contextlib
        import io
        root = self._repo("Fast. <!-- measured: total <= 300s -->\n", timings=None)
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            errors = check_spec_claims.check(root)
        self.assertEqual([], errors, "an unmeasurable claim failed a fresh clone")
        self.assertIn("UNVERIFIABLE", err.getvalue(),
                      "the gap was neither failed nor reported - that IS treating it as a pass")

    def test_the_shipped_tsd_markers_parse_and_hold(self) -> None:
        """The reviewer's sharpest point: the timing lane guarded NOTHING, because no marker
        existed anywhere in the repo. Two now do, and they are checked against the live store."""
        repo = Path(__file__).resolve().parents[2]
        text = (repo / "sdlc-studio" / "tsd.md").read_text(encoding="utf-8")
        markers = list(check_spec_claims._TIMING.finditer(text))
        self.assertGreaterEqual(len(markers), 2,
                                "the timing lane still has no shipped marker to check")
        import contextlib
        import io
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual([], check_spec_claims.timing_errors(repo, "tsd.md", text))

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


class PathAwareBandTests(unittest.TestCase):
    """An independent reviewer found FIVE band-shaped claims in the target documents silently
    unchecked, because their noun (`files`, `modules`) is too generic to register - and
    registering `files` would match anything. The row already names its own census; read it
    from there. All five were true, so no active untruth - but all five were unguarded, sitting
    in the same table rows as the one claim that was."""

    def _repo(self, trd: str, help_files: int = 3) -> Path:
        d = Path(tempfile.mkdtemp(prefix="pathband_"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / SKILL / "help").mkdir(parents=True)
        for i in range(help_files):
            (d / SKILL / "help" / f"h{i}.md").write_text("x\n", encoding="utf-8")
        (d / "sdlc-studio").mkdir(parents=True)
        (d / "sdlc-studio" / "trd.md").write_text(trd, encoding="utf-8")
        return d

    def test_a_path_band_the_tree_contradicts_fails(self) -> None:
        root = self._repo("| `help/*.md` (9+ files) | help pages |\n", help_files=3)
        errors = check_spec_claims.path_band_errors(root, "trd.md",
                                                   (root / "sdlc-studio/trd.md").read_text())
        self.assertTrue(errors, "a 9+ claim over 3 files was not reported")
        self.assertIn("3", errors[0], "the counted value was not named")

    def test_an_agreeing_path_band_passes(self) -> None:
        root = self._repo("| `help/*.md` (2+ files) | help pages |\n", help_files=3)
        self.assertEqual([], check_spec_claims.path_band_errors(
            root, "trd.md", (root / "sdlc-studio/trd.md").read_text()))

    def test_a_glob_matching_nothing_is_reported_not_skipped(self) -> None:
        root = self._repo("| `nowhere/*.md` (2+ files) | ghosts |\n")
        errors = check_spec_claims.path_band_errors(
            root, "trd.md", (root / "sdlc-studio/trd.md").read_text())
        self.assertTrue(errors, "a glob matching nothing passed as a clean claim")
        self.assertIn("matches NOTHING", errors[0])

    def test_a_band_inside_a_fenced_block_is_not_a_claim(self) -> None:
        """Four false positives an independent reviewer found: a band in a fenced example, a
        URL, a table row meaning something else, or a historical aside is not a claim about
        the shipped tree."""
        root = self._repo("```text\n| `nowhere/*.md` (99+ files) |\n```\n")
        self.assertEqual([], check_spec_claims.path_band_errors(
            root, "trd.md", (root / "sdlc-studio/trd.md").read_text()),
            "a band inside a fenced example was read as a claim")

    def test_a_band_in_a_url_is_not_a_claim(self) -> None:
        root = self._repo("See https://example.com/`nowhere/*.md`-(99+ files) for detail\n")
        self.assertEqual([], check_spec_claims.path_band_errors(
            root, "trd.md", (root / "sdlc-studio/trd.md").read_text()))

    def test_the_real_trd_path_bands_all_resolve_and_hold(self) -> None:
        """The five the reviewer named, against the live tree."""
        repo = Path(__file__).resolve().parents[2]
        text = (repo / "sdlc-studio" / "trd.md").read_text(encoding="utf-8")
        found = list(check_spec_claims._PATH_BAND.finditer(text))
        self.assertGreaterEqual(len(found), 5,
                                f"only {len(found)} path-aware bands parsed - the five the "
                                f"reviewer named are not all being read")
        self.assertEqual([], check_spec_claims.path_band_errors(repo, "trd.md", text))


if __name__ == "__main__":
    unittest.main()
