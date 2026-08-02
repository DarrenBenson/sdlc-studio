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



class LedgerExemptionTests(unittest.TestCase):
    """What claim-drift is allowed to STOP reading, and what it must keep reading.

    A ledger row states that somebody judged something on a date - no diff can contradict it.
    A review document, or `LATEST.md`, is prose making claims about the change, which is
    exactly what this lane exists to read. The exemption once matched the whole
    `sdlc-studio/reviews/` path and silently took both with it.
    """

    def test_the_append_only_ledgers_are_exempt(self) -> None:
        """The control. MUTANT: exempt nothing.

        A lane that reads the verdict log as prose fires on every recorded review, which is
        noise on rows that cannot make a claim - and noise is how a lane gets switched off.
        """
        for name in ("critic-verdicts.md", "signoff-record.md", "sprint-review-record.md"):
            self.assertTrue(check_spec_claims._is_ledger(f"sdlc-studio/reviews/{name}"),
                            f"{name} is an append-only ledger and should be exempt")

    def test_prose_under_reviews_is_not_exempt(self) -> None:
        """MUTANT: exempt by DIRECTORY (`_LEDGER_DIRS = ("sdlc-studio/reviews/",)`).

        That was the shipped defect and it is invisible to a test that only checks the
        ledgers: `critic-verdicts.md` is exempt by name too, so the directory clause could be
        removed OR added without either existing criterion noticing. These two files are the
        ones a directory prefix takes with it.
        """
        for path in ("sdlc-studio/reviews/LATEST.md",
                     "sdlc-studio/reviews/RV0025-the-review-learned-to-discriminate.md"):
            self.assertFalse(
                check_spec_claims._is_ledger(path),
                f"{path} is prose making claims, not an append-only ledger - a directory-wide "
                f"exemption removed the whole reviews tree from the lane")

    def test_the_exemption_is_by_name_not_by_path_segment(self) -> None:
        """MUTANT: match on `in norm` rather than on the file name.

        A substring match exempts `notes/critic-verdicts.md.bak` and anything whose path merely
        CONTAINS a ledger name. The exemption is a statement about one file, so it is decided
        on the file name.
        """
        self.assertFalse(check_spec_claims._is_ledger("docs/about-critic-verdicts.md"),
                         "a file whose name merely contains a ledger name was exempted")
        self.assertTrue(check_spec_claims._is_ledger("anywhere/else/critic-verdicts.md"),
                        "the ledger is exempt wherever it lives - the name is the fact")

if __name__ == "__main__":
    unittest.main()


class ClaimDriftTests(unittest.TestCase):
    """US0583: a diff whose code and whose own prose disagree, caught at delivery.

    Every blocking finding of RUN-01KYX375's corrected review loop was this shape - a changelog
    or docstring stating a value the code in the same diff had moved past. Each was decidable
    from the diff alone in seconds and instead cost an adversarial review round. BG0471 is the
    specimen: the collapse signal moved from exit 2 to exit 3 and two prose sites kept saying 2,
    one of them the docstring of the very test asserting 3.

    The mutant each test must fail on is named in its own docstring, per LL0050.
    """

    def _diff(self, code_before: str, code_after: str, prose: str) -> str:
        """A unified diff touching one code file and one prose file, as `git diff` emits it."""
        return (
            "diff --git a/tools/thing.py b/tools/thing.py\n"
            "--- a/tools/thing.py\n+++ b/tools/thing.py\n@@ -1,2 +1,2 @@\n"
            # The CONTEXT line a real `git diff` emits. It is where the subject is NAMED:
            # `-    return 2` / `+    return 3` identifies nothing on its own, and a finding
            # now needs the prose to name something the changed code names rather than merely
            # sharing a digit (BG0479).
            " def collapse():\n"
            f"-{code_before}\n+{code_after}\n"
            "diff --git a/changelog.d/BG0001.md b/changelog.d/BG0001.md\n"
            "--- a/changelog.d/BG0001.md\n+++ b/changelog.d/BG0001.md\n@@ -0,0 +1,1 @@\n"
            f"+{prose}\n")

    def test_a_changed_literal_contradicting_its_prose_is_flagged(self) -> None:
        """MUTANT: make `claim_drift` return [] unconditionally. This must go red.

        BG0471's shape, reduced: the code moves to 3 and the prose still says 2."""
        diff = self._diff("    return 2", "    return 3",
                          "- the check now exits 2 when the suite collapses")
        found = check_spec_claims.claim_drift(diff)
        self.assertEqual(1, len(found), f"expected one drift finding, got {found}")
        self.assertIn("3", found[0]["code"], "the finding does not name the code value")
        self.assertIn("2", found[0]["prose"], "the finding does not name the prose value")
        self.assertIn("changelog.d/BG0001.md", found[0]["prose_file"])
        self.assertIn("tools/thing.py", found[0]["code_file"])

    def test_a_literal_the_diff_KEPT_is_not_treated_as_replaced(self) -> None:
        """MUTANT: compute the replaced set as `old_nums` rather than `old_nums - new_nums`.
        This must go red.

        A hunk that rewrites a line while keeping a number has not moved away from it, so prose
        naming that number is still true. Without this case the detector flags every number the
        diff touches at all, which is the noise that gets a lane switched off."""
        diff = ("diff --git a/tools/thing.py b/tools/thing.py\n"
                "--- a/tools/thing.py\n+++ b/tools/thing.py\n@@ -1,1 +1,1 @@\n"
                "-    if x: return 2\n+    if y: return 2\n"
                "diff --git a/changelog.d/BG0001.md b/changelog.d/BG0001.md\n"
                "--- a/changelog.d/BG0001.md\n+++ b/changelog.d/BG0001.md\n@@ -0,0 +1,1 @@\n"
                "+- it still exits 2 on collapse\n")
        self.assertEqual([], check_spec_claims.claim_drift(diff),
                         "a number the diff kept was reported as one it moved away from")

    def test_agreeing_prose_produces_no_finding(self) -> None:
        """The control. MUTANT: make `claim_drift` return a finding unconditionally - this must
        go red, so the lane cannot be satisfied by one that always fires."""
        diff = self._diff("    return 2", "    return 3",
                          "- the check now exits 3 when the suite collapses")
        self.assertEqual([], check_spec_claims.claim_drift(diff))

    def test_only_the_staged_diff_is_judged(self) -> None:
        """MUTANT: widen the scan from the diff to the whole repository. This must go red.

        The lane is a DELIVERY check. A repo-wide scan would find a contradiction somewhere on
        every commit, which is how a guard becomes noise and then gets switched off."""
        diff = ("diff --git a/tools/thing.py b/tools/thing.py\n"
                "--- a/tools/thing.py\n+++ b/tools/thing.py\n@@ -1,1 +1,1 @@\n"
                "-    return 2\n+    return 3\n")
        self.assertEqual([], check_spec_claims.claim_drift(diff),
                         "a diff touching no prose produced a finding")

    def test_an_unchanged_prose_line_is_not_judged(self) -> None:
        """MUTANT: read context lines as prose. This must go red.

        Only lines the diff ADDS are this unit's claims. A context line is prose the commit did
        not write, and judging it turns a delivery check into an audit of the file's history."""
        diff = ("diff --git a/tools/thing.py b/tools/thing.py\n"
                "--- a/tools/thing.py\n+++ b/tools/thing.py\n@@ -1,2 +1,2 @@\n"
                "-    return 2\n+    return 3\n"
                "diff --git a/changelog.d/BG0001.md b/changelog.d/BG0001.md\n"
                "--- a/changelog.d/BG0001.md\n+++ b/changelog.d/BG0001.md\n@@ -1,2 +1,2 @@\n"
                " - an older note saying it exits 2\n"
                "+- an added note that names no number\n")
        self.assertEqual([], check_spec_claims.claim_drift(diff))

    def test_a_drift_finding_alone_does_not_fail_the_command(self) -> None:
        """The exit-code contract (D0105). MUTANT: fold drift findings into `errors`. This must
        go red - the drift lane is ADVISORY while its yield is measured, and the existing
        spec-claim errors keep the blocking contract they have today."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir(parents=True)
            diff = self._diff("    return 2", "    return 3",
                              "- the check now exits 2 when the suite collapses")
            buf_out, buf_err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
                rc = check_spec_claims.main(["--root", str(root), "--claim-drift", "-"],
                                            stdin_text=diff)
            self.assertEqual(0, rc, "an advisory drift finding blocked the command")
            self.assertIn("CLAIM-DRIFT", buf_out.getvalue() + buf_err.getvalue(),
                          "the finding was not reported at all")


class ClaimTickTests(unittest.TestCase):
    """US0584: a criterion ticked in a diff whose named surface that diff never touches.

    BG0472 is the specimen. Two of BG0460's criteria were recorded met and were not: AC2 required
    a claim retired from a story that was byte-identical to the base ref, and AC3 required two
    verifiers to call `close_dry_run` while both still asserted over a hand-built list. Both were
    ticked, the close accepted them, and an independent seat found them by reading `git diff`.

    Each test names the mutant it must fail on, per LL0050.
    """

    def _diff(self, *files: tuple[str, list[str]]) -> str:
        out = []
        for path, added in files:
            out.append(f"diff --git a/{path} b/{path}\n--- a/{path}\n+++ b/{path}\n@@ -0,0 +1,1 @@\n")
            out.extend(f"+{line}\n" for line in added)
        return "".join(out)

    def test_a_tick_over_an_untouched_surface_is_flagged(self) -> None:
        """MUTANT: make `ticked_over_untouched` return [] unconditionally. This must go red.

        BG0472's shape: a criterion ticked whose named verifier lives in a file the diff does
        not contain."""
        diff = self._diff(
            ("sdlc-studio/stories/US0001-x.md", [
                "- [x] the close reports every step",
                "- **Verify:** pytest tools/tests/test_untouched.py::T::test_a",
            ]),
            ("tools/other.py", ["    return 1"]),
        )
        found = check_spec_claims.ticked_over_untouched(diff)
        self.assertEqual(1, len(found), f"expected one finding, got {found}")
        self.assertIn("test_untouched.py", found[0]["surface"])
        self.assertIn("US0001", found[0]["unit"])

    def test_a_tick_over_a_changed_surface_passes(self) -> None:
        """The control. MUTANT: flag every ticked criterion. This must go red, or the check
        cannot tell a met criterion from an asserted one and would fire on every honest tick."""
        diff = self._diff(
            ("sdlc-studio/stories/US0001-x.md", [
                "- [x] the close reports every step",
                "- **Verify:** pytest tools/tests/test_touched.py::T::test_a",
            ]),
            ("tools/tests/test_touched.py", ["    def test_a(self): pass"]),
        )
        self.assertEqual([], check_spec_claims.ticked_over_untouched(diff))

    def test_a_surface_named_INSIDE_the_criterion_is_honoured(self) -> None:
        """The second control, and the one mutation demanded. A criterion can name its surface in
        its own text rather than in a Verify line, and that branch needs its own touched case -
        without it, a mutant flagging every criterion-text surface survives, because the other
        control only exercises the Verify-line branch."""
        diff = self._diff(
            ("sdlc-studio/stories/US0001-x.md", [
                "- [x] tools/check_spec_claims.py refuses a contradiction",
            ]),
            ("tools/check_spec_claims.py", ["    return 1"]),
        )
        self.assertEqual([], check_spec_claims.ticked_over_untouched(diff))

    def test_a_surface_named_inside_an_UNTOUCHED_criterion_is_flagged(self) -> None:
        """Its positive half: the same shape where the named file is absent from the diff."""
        diff = self._diff(
            ("sdlc-studio/stories/US0001-x.md", [
                "- [x] tools/absent.py refuses a contradiction",
            ]),
            ("tools/other.py", ["    return 1"]),
        )
        found = check_spec_claims.ticked_over_untouched(diff)
        self.assertEqual(1, len(found))
        self.assertEqual("untouched", found[0]["kind"])

    def test_an_unjudgeable_criterion_is_named_not_passed(self) -> None:
        """MUTANT: treat a criterion naming no surface as passing (drop it silently). This must
        go red - an unanswerable check must never read the same as a satisfied one, which is the
        rule this whole batch exists to enforce."""
        diff = self._diff(
            ("sdlc-studio/stories/US0001-x.md", [
                "- [x] the operator is happier than before",
            ]),
            ("tools/other.py", ["    return 1"]),
        )
        found = check_spec_claims.ticked_over_untouched(diff)
        self.assertEqual(1, len(found), f"expected the criterion to be named, got {found}")
        self.assertEqual("unjudgeable", found[0]["kind"],
                         "a criterion naming no surface was reported as an ordinary pass")

    def test_an_unticked_criterion_is_not_judged(self) -> None:
        """MUTANT: judge unticked criteria too. This must go red.

        An unticked criterion claims nothing, so there is nothing to contradict. Judging it
        would flag every story that declares work it has not done yet."""
        diff = self._diff(
            ("sdlc-studio/stories/US0001-x.md", [
                "- [ ] the close reports every step",
                "- **Verify:** pytest tools/tests/test_untouched.py::T::test_a",
            ]),
            ("tools/other.py", ["    return 1"]),
        )
        self.assertEqual([], check_spec_claims.ticked_over_untouched(diff))
