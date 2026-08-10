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
import re
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
        agents = (repo / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("check_spec_claims.py", agents,
                      "AGENTS.md's guard table does not document the checker")
        # EVERY blocking lane, derived from the hook rather than restated here - AGENTS.md says
        # extend the pinning when you add a lane, or the list silently exempts what it forgot
        # (LL0013). Two lanes reached this roster late: `runbook.py` was filed as BG0500, and
        # `validate.py`'s warning ratchet shipped in the same batch and was missed until an
        # independent seat named it.
        hook = (repo / ".githooks" / "pre-commit").read_text(encoding="utf-8")
        import re as _re
        for key, script in _re.findall(
                r'run\s+"([^"]+)"(?:[^\n]*\n){1,4}?\s*--\s+\S+\s+(\S+)', hook):
            name = script.rsplit("/", 1)[-1]
            if not name.endswith((".py", ".sh")):
                continue
            with self.subTest(lane=key):
                self.assertIn(name, agents,
                              f"the `{key}` lane runs {name} and AGENTS.md's roster does not "
                              f"name it - a guard nobody has written down is one nobody "
                              f"notices losing")

    def test_the_lane_roster_names_the_release_rehearsal(self) -> None:
        """US0666: a lane bound at a BOUNDARY is invisible to the hook-derived sweep above, which
        reads the pre-commit hook - so the one lane that deliberately does not run per commit is
        the one that roster cannot see. It is pinned here by name, with the boundary it binds at,
        because a lane nobody has written down is one nobody notices losing (LL0013)."""
        repo = Path(__file__).resolve().parents[2]
        agents = (repo / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("release-rehearsal", agents,
                      "AGENTS.md's roster does not name the release-rehearsal lane")
        self.assertIn("rehearse-release.sh", agents,
                      "the roster names the lane but not the harness it runs")
        self.assertRegex(agents, r"release-rehearsal[^.]*boundar",
                         "the roster does not say the lane binds at a boundary rather than per "
                         "commit, which is the only thing a reader needs to know about it")
        gate = (repo / ".claude" / "skills" / "sdlc-studio" / "scripts"
                / "gate.py").read_text(encoding="utf-8")
        self.assertIn('"release-rehearsal"', gate,
                      "AGENTS.md names a lane the gate does not register")

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


class LintAggregateTests(unittest.TestCase):
    """US0655 AC2: the `lint` CHAIN calls `lint:disclosure`, which it did not."""

    def test_the_lint_chain_calls_disclosure(self) -> None:
        """`lint:disclosure` has existed as a script KEY all along; only the aggregate omitted
        it, so a checker with 28 advisory findings was one line from being read and was not.
        Asserting the key exists is green today with nothing changed, which is a criterion that
        cannot fail.

        Mutant: leave `lint:disclosure` defined as a key but absent from the `lint` chain.
        """
        import json
        pkg = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))["scripts"]
        self.assertIn("lint:disclosure", pkg, "the disclosure lane is not defined at all")
        self.assertIn("lint:disclosure", pkg["lint"],
                      "the `lint` chain does not call `lint:disclosure`, so the checker runs "
                      "nowhere and reports nothing however good it is")




class SkillSectionTests(unittest.TestCase):
    """US0659 AC1/AC2: SKILL.md carries the sections its own checklist requires."""

    def test_skill_md_carries_the_sections_its_own_checklist_requires(self) -> None:
        """`best-practices/claude-skill.md` requires a "See Also" section and gives a single
        vague sentence as its BAD trigger example - labelled "Too vague, no trigger keywords",
        so the fault it names is VAGUENESS. The assertion is on trigger phrases being present,
        which is the rule, rather than on the shape of a list, which is a proxy that would
        outlive the reason for it.

        Mutant: remove the `## See Also` section.
        Mutant: revert `When to Use` to a single vague sentence with no trigger phrases.
        """
        skill = (ROOT / ".claude/skills/sdlc-studio/SKILL.md").read_text(encoding="utf-8")
        checklist = (ROOT / ".claude/skills/sdlc-studio/best-practices/claude-skill.md"
                     ).read_text(encoding="utf-8")
        self.assertIn("See Also", checklist, "the checklist no longer requires this section")
        self.assertIn("## See Also", skill,
                      "SKILL.md fails the checklist it ships - the cheapest possible finding "
                      "and the most embarrassing to leave")
        when = skill[skill.index("## When to Use"):]
        when = when[:when.index("\n## ", 5)]
        phrases = [ln for ln in when.splitlines() if ln.strip().startswith("- ")]
        self.assertGreaterEqual(len(phrases), 5,
                                "`When to Use` names no trigger phrases, which is the shape "
                                "the skill's own guidance gives as its bad example")

    def test_the_four_top_level_documents_are_in_the_loading_guide(self) -> None:
        """The doctrine calls the PRD, TRD, TSD and story the top-level human levers, and an
        agent following the Progressive Loading Guide was told about none of them.

        Mutant: drop one of the four rows.
        """
        skill = (ROOT / ".claude/skills/sdlc-studio/SKILL.md").read_text(encoding="utf-8")
        guide = skill[skill.index("## Progressive Loading Guide"):]
        guide = guide[:guide.index("\n## ", 5)]
        for ref in ("reference-prd.md", "reference-trd.md", "reference-tsd.md",
                    "reference-story.md"):
            with self.subTest(reference=ref):
                self.assertIn(ref, guide,
                              f"{ref} is a top-level document the loading guide never names")



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

    def test_a_bare_filename_naming_a_changed_file_is_not_flagged(self) -> None:
        """BG0505. MUTANT: revert `_names_a_touched_file` to `any(s in touched ...)`. This must go
        red.

        `touched` holds repo-relative paths, so a bare name could never be a member of it, and
        `unittest -p` takes a PATTERN rather than a path - which makes the shipped way to name a
        Python test the one form that could not pass. It fired on BG0504's own criterion over a
        file the same diff changed by 76 lines.
        """
        diff = self._diff(
            ("sdlc-studio/bugs/BG0001-x.md", [
                "- [x] both guards read the archive union",
                '- **Verify:** python3 -m unittest discover -s tools/tests -p "test_touched.py"',
            ]),
            ("tools/tests/test_touched.py", ["    def test_a(self): pass"]),
        )
        self.assertEqual([], check_spec_claims.ticked_over_untouched(diff))

    def test_a_bare_filename_matching_nothing_in_the_diff_is_still_flagged(self) -> None:
        """The half that keeps the widening honest. MUTANT: make `_names_a_touched_file` return
        True whenever a bare name appears - the check would then pass every basename-only Verify
        line, which is most of them, and the lane would detect nothing it was built for."""
        diff = self._diff(
            ("sdlc-studio/bugs/BG0001-x.md", [
                "- [x] both guards read the archive union",
                '- **Verify:** python3 -m unittest discover -s tools/tests -p "test_absent.py"',
            ]),
            ("tools/tests/test_touched.py", ["    def test_a(self): pass"]),
        )
        found = check_spec_claims.ticked_over_untouched(diff)
        self.assertEqual(1, len(found))
        self.assertEqual("test_absent.py", found[0]["surface"])

    def test_a_path_qualified_name_still_compares_by_path(self) -> None:
        """MUTANT: drop the `"/" in s` branch and match every surface by basename. A criterion
        naming `scripts/gate.py` would then be satisfied by a change to `tools/gate.py`, which is
        a different file - the looseness must stay confined to the form carrying no directory to
        be wrong about."""
        diff = self._diff(
            ("sdlc-studio/bugs/BG0001-x.md", [
                "- [x] scripts/gate.py refuses a stale verdict",
            ]),
            ("tools/gate.py", ["    return 1"]),
        )
        found = check_spec_claims.ticked_over_untouched(diff)
        self.assertEqual(1, len(found))
        self.assertEqual("scripts/gate.py", found[0]["surface"])

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


# --- US0567: the doctrine's repair-evidence rule -------------------------------------------
# Lifted here rather than shipped as its own file: `tools/tests/test_doctrine_repair_evidence.py`
# could never be attributed by the test census, whose sibling-module rule only sees `tools/*.py`,
# and the census baseline is explicit that it is lowered when a file gains a home and NEVER
# raised to accommodate a new one. A guard that a shipped document's claim is true is a
# spec-claim check, so this is where it belongs.

ROOT = Path(__file__).resolve().parents[2]
DOCTRINE = ROOT / ".claude/skills/sdlc-studio/reference-doctrine.md"
DOD = ROOT / ".claude/skills/sdlc-studio/templates/core/definition-of-done.md"
LESSONS = ROOT / ".claude/skills/sdlc-studio/reference-agentic-lessons.md"


def _states_the_rule(text: str) -> bool:
    """Does THIS text state rule 21 and name its enforcing mechanism?

    Takes the text rather than reading the file, so the discrimination below can put a
    doctored corpus through the identical predicate. Asserting a length comparison instead
    proved too weak: a mutant that pointed the rule test at the whole file survived it,
    because the length check computed its own slice and never saw the sibling stop
    discriminating. The property has to be exercised, not inferred.
    """
    passage = _slice_rule(text)
    if not passage:
        return False
    low = passage.lower()
    return "author" in low and "mutant" in low and "transition.py" in passage


def _slice_rule(text: str) -> str:
    """Rule 21's own text, from its numbered heading to the next top-level heading or rule.

    Sliced rather than searched, so the assertions below cannot be satisfied by any other
    part of the file - a Revision History row included.
    """
    m = re.search(r"^21\. \*\*(.+?)\*\*.*?$", text, re.M)
    if not m:
        return ""
    rest = text[m.start():]
    end = re.search(r"^(?:## |\d+\. \*\*)", rest[len(m.group(0)):], re.M)
    return rest[: len(m.group(0)) + end.start()] if end else rest


def _defined_functions(source: str) -> set:
    """Every function `source` DEFINES, by AST."""
    import ast
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set()
    return {n.name for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}


def _doctrine_lane_names(doctrine: str, source: str) -> set:
    """The mechanisms rule 21 NAMES that `source` actually DEFINES.

    Two independent sources, and neither is the property under test. The doctrine supplies the
    claim; the module supplies which of the backticked tokens in it are functions rather than
    mode values (`report`, `block`, `off`), config keys or filenames. What the guard then asks
    is whether each is REACHED - and defining a function and reaching it are different
    properties, which is the entire content of BG0541: `repair_mutation_gate` was defined,
    tested and called by nothing while the doctrine said it refused.

    So this is not the circularity round 2 rejected. That was a set derived from the predicate's
    own reachability walk, which narrows exactly when the predicate narrows. This one does not
    move when the ladder changes; it moves only when the doctrine stops naming a mechanism or
    the module stops defining one, and the cardinality floor beside it catches both.
    """
    passage = _slice_rule(doctrine)
    named = set(re.findall(r"`([A-Za-z_][A-Za-z0-9_]*)`", passage))
    return named & _defined_functions(source)


def _calls_within(source: str, func: str) -> set:
    """Every name called inside `func`'s body, by AST rather than by substring.

    A substring search over a function's text cannot tell a call from a mention in a docstring,
    and every one of these names appears in prose somewhere in the module.
    """
    import ast
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func:
            out = set()
            for sub in ast.walk(node):
                if isinstance(sub, ast.Call):
                    fn = sub.func
                    if isinstance(fn, ast.Name):
                        out.add(fn.id)
                    elif isinstance(fn, ast.Attribute):
                        out.add(fn.attr)
            return out
    return set()


def _lanes_are_reachable(source: str, lanes: set) -> bool:
    """Is every named lane reached from `_pre_write_gates`, directly or through one hop?

    One hop, because the composition is the design: `_pre_write_gates` calls
    `mutation_evidence_lane`, which calls the gates beneath it. A predicate demanding a direct
    call would force the ladder to inline the composition to stay green, which is the guard
    dictating the shape rather than checking the claim.
    """
    entry = _calls_within(source, "_pre_write_gates")
    reached = set(entry)
    for name in entry:
        reached |= _calls_within(source, name)
    return lanes <= reached


def _drop_call(source: str, name: str) -> str:
    """`source` with every statement calling `name` removed, for the doctored corpus.

    Line-wise and deliberately crude: it only has to produce a source in which the call is
    absent, and it asserts nothing about what else survives - the predicate re-parses it.
    """
    kept = [ln for ln in source.splitlines(keepends=True)
            if f"{name}(" not in ln or ln.lstrip().startswith(("#", '"', "'", "def "))]
    return "".join(kept)


class DoctrineTests(unittest.TestCase):
    def test_doctrine_states_the_rule_and_names_the_enforcing_gate(self) -> None:
        """A reader must arrive at a MECHANISM, not at advice.

        Mutant: delete the passage and leave every other line intact, Revision History
        included - this reddens. Mutant: state the rule and drop the sentence naming
        `transition.py` - a rule with no mechanism behind it is one this doctrine is
        explicit about distrusting, and the enforcement assertion catches it alone.
        """
        text = DOCTRINE.read_text(encoding="utf-8")
        self.assertTrue(_states_the_rule(text), "rule 21 is absent, or states no mechanism")
        passage = _slice_rule(text)
        low = passage.lower()
        self.assertIn("author", low, "the rule does not name whose evidence is insufficient")
        self.assertIn("mutant", low, "the rule does not name the evidence it demands")
        self.assertIn("transition.py", passage,
                      "the rule states no enforcing mechanism, so it is advice")

    def test_deleting_the_stating_passage_reddens_the_guard(self) -> None:
        """THE DISCRIMINATION, exercised rather than inferred.

        The predicate is run over a doctored corpus: rule 21 removed, and a Revision History
        row describing the change that added it left in place. That row contains every word
        the assertions look for. A guard anchored on the whole file passes it; one anchored on
        the rule's own passage does not. BG0457 records exactly this defect - four guards
        comparing a document against a projection of itself - and a guard shipped in the same
        change as the prose it checks is the easiest place to repeat it.

        Mutant: point `_states_the_rule` at the whole text instead of the slice - this reddens,
        and the earlier length-comparison version did not.
        """
        real = DOCTRINE.read_text(encoding="utf-8")
        self.assertTrue(_states_the_rule(real), "the positive control does not hold")
        doctored = real.replace(_slice_rule(real), "") + (
            "\n| 2026-08-06 | sdlc | Added the repair-evidence rule: a fix's author is not "
            "sufficient evidence, held by a mutant and enforced by transition.py |\n")
        self.assertFalse(_states_the_rule(doctored),
                         "the guard is satisfied by a Revision History row describing the "
                         "rule rather than by the rule itself")

    def test_the_definition_of_done_carries_a_consistent_clause(self) -> None:
        """A consuming project copies this file as its own Done contract.

        Mutant: drop the clause from the template - the doctrine states a rule the shipped
        contract does not carry, and a consuming project inherits the prose without the bar.

        Second mutant: write the clause with an internal provenance tag (`(US0567)`) or an
        em dash. The style guard would catch either, but only while somebody runs it over
        this file; asserting it HERE is what makes the criterion's own selector answer for
        the whole criterion rather than for half of it. This criterion previously pointed at
        `bash tools/lint-style.sh`, a whole-repo selector it shared with US0111 AC3 - two
        criteria that a regression in either would fail together, neither saying which.
        """
        dod = DOD.read_text(encoding="utf-8")
        story = dod[dod.index("## Story"): dod.index("## Delivery batch")]
        # Anchored on the CLAUSE, not on the section: `repair` and `mutant` both appear
        # elsewhere in the Story contract, so a whole-section substring check survived a mutant
        # that gutted the clause itself. Found by applying that mutant rather than by reading.
        clause = next((ln for ln in story.splitlines() if "REPAIR" in ln), "")
        self.assertTrue(clause, "the Story contract carries no repair clause")
        tail = story[story.index(clause):] if clause else ""
        tail = tail[:tail.index("- [ ]", len(clause))] if "- [ ]" in tail[len(clause):] else tail
        self.assertIn("mutant was applied", tail,
                      "the clause does not demand the evidence the gate reads - it names the "
                      "repair class and asks for nothing")
        self.assertIn("changed lines", tail,
                      "the clause does not scope the evidence to the repair's own change")
        self.assertIn("block", tail,
                      "the clause states a bar without naming the setting that makes it one, "
                      "so a project cannot tell what it is being held to")
        # Tool-neutral and untagged: a consuming project copies this file, so an id that means
        # something only in THIS repo is noise there, and the house style refuses it.
        tags = re.findall(r"\((?:US|CR|BG|RFC|EP|RV)\d{3,4}[^)]*\)", story)
        self.assertEqual([], tags, f"the clause carries an internal provenance tag: {tags}")
        self.assertNotIn("—", story, "the clause carries an em dash")


    def test_the_named_gate_actually_exists(self) -> None:
        """The doctrine names `transition.py` as what enforces this rule. If that file does not
        carry a repair-evidence gate, the doctrine names a mechanism that is not there - which
        is the failure this repo files as INERT, and the one thing worse than advice is advice
        wearing a mechanism's name.

        This also gives the guard a HOME in the test census: it now references the module it
        checks rather than only markdown, so the attribution convention can place it. Raising
        the unattributed baseline to accommodate a new file is explicitly forbidden, and the
        first remedy the ratchet offers is the right one - give the new file a home.

        Mutant: point the doctrine at a verb that carries no such gate - this reddens.
        """
        transition = (ROOT / ".claude/skills/sdlc-studio/scripts/transition.py").read_text(
            encoding="utf-8")
        self.assertIn("_plan_gate_active", transition,
                      "transition.py carries no repair/test-plan gate, so the doctrine names a "
                      "mechanism that does not exist")
        self.assertIn("review.test_plan_after", transition,
                      "the gate the doctrine names is not the one transition.py reads")

    def test_removing_any_lane_the_doctrine_names_reddens_the_guard(self) -> None:
        """Every mechanism rule 21 NAMES must be reachable from the gate ladder, not merely
        defined. The whole of BG0541 is that `repair_mutation_gate` was defined, tested, and
        called by nothing, while the doctrine told consuming projects it refused.

        Three properties, and the second is the one that took three review rounds to get right:

          1. the real source is wired - the positive control;
          2. removing ANY ONE named lane's call reddens the predicate. The removal set comes
             from the DOCTRINE, never from the predicate's own derived set: a set the predicate
             computes narrows when the predicate narrows, so the mutant `pin this to one lane`
             would leave the loop still red and survive. The doctrine is the text making the
             claim, so checking the claim against the code is what this guard is for;
          3. a floor of THREE lanes, so a doctrine passage edited down to one mechanism cannot
             quietly satisfy the loop either. Both ends have to be pinned or the pair can be
             satisfied by shrinking whichever end is not.

        Mutant: narrow `_wired_lanes` to a single hard-coded name - this reddens on the floor.
        Mutant: delete the `mutation_evidence_lane` call from `_pre_write_gates` - this reddens
        on the loop, and it is the state of the tree BG0541 was filed against.
        """
        transition = (ROOT / ".claude/skills/sdlc-studio/scripts/transition.py").read_text(
            encoding="utf-8")
        lanes = _doctrine_lane_names(DOCTRINE.read_text(encoding="utf-8"), transition)
        self.assertGreaterEqual(
            len(lanes), 3,
            f"rule 21 names {len(lanes)} mechanism(s) - {sorted(lanes)}. The floor is three: a "
            f"passage edited down to one satisfies the reachability loop below without any "
            f"mechanism being reached")
        self.assertTrue(_lanes_are_reachable(transition, lanes),
                        f"the positive control fails: {sorted(lanes)} are named by rule 21 and "
                        f"not all reachable from _pre_write_gates")
        for lane in sorted(lanes):
            doctored = _drop_call(transition, lane)
            self.assertNotEqual(doctored, transition,
                                f"no call to {lane} was found to remove, so the mutant cannot "
                                f"be applied and the loop proves nothing about it")
            self.assertFalse(
                _lanes_are_reachable(doctored, lanes),
                f"removing every call to {lane} leaves the guard green - a mechanism the "
                f"doctrine names can be unreached without this test noticing, which is "
                f"precisely the state BG0541 was filed against")

    def test_the_doctrine_names_the_mode_that_restores_refusal(self) -> None:
        """US0567 AC5: a project that read this rule as a refusal is owed the sentence saying
        the default changed.

        A documented block quietly becoming a documented report lowers a bar on somebody else's
        project without their knowing. The passage therefore has to state which of the three
        modes an unset project gets, and name the one that restores what it used to promise.

        Mutant: state the three modes without marking which is the default - a reader then has
        to guess whether their existing project still refuses.
        Mutant: drop `review.mutation_evidence` from the passage - the rule changes direction
        with no way to change it back.
        """
        passage = _slice_rule(DOCTRINE.read_text(encoding="utf-8"))
        self.assertIn("review.mutation_evidence", passage,
                      "the rule states no setting, so a project cannot choose its consequence")
        for mode in ("report", "block", "off"):
            with self.subTest(mode=mode):
                self.assertIn(f"`{mode}`", passage, f"the rule does not name the {mode} mode")
        self.assertRegex(passage, r"`report`[^\n]*default|default[^\n]*`report`",
                         "the rule names three modes without saying which one a project that "
                         "sets nothing gets, so an existing reader cannot tell whether their "
                         "bar moved")
        # The upgrade sentence itself, not an ordering accident: a reader who installed an
        # earlier version must be told, in one place, that the default moved and what to set to
        # move it back. Asserted on the two things that sentence has to carry.
        upgrade = next((ln for ln in passage.splitlines()
                        if "no longer" in ln or "earlier version" in ln), "")
        self.assertTrue(upgrade,
                        "the rule states three modes but never tells a project that installed "
                        "an earlier version that the default changed under it")
        after = passage[passage.index(upgrade):]
        self.assertIn("`review.mutation_evidence: block`", after,
                      "the upgrade note does not name the setting that restores the refusal "
                      "this rule used to describe")

    def test_the_carried_lesson_cites_the_gate(self) -> None:
        """The lesson must POINT at the doctrine and the enforcing verb, not restate their terms.

        Two documents stating the same rule in their own words drift, and the second is edited
        by whoever did not know the first existed. Citing is what makes them one rule.

        Mutant: restate the rule in the lesson without the `reference-doctrine.md#repair-evidence`
        anchor or the `transition.py` reference - this reddens, and a reader is left with advice
        that has no destination.
        """
        lessons = LESSONS.read_text(encoding="utf-8")
        self.assertIn("repair-evidence", lessons,
                      "the lesson does not cite the doctrine passage")
        self.assertIn("transition.py", lessons,
                      "the lesson does not name the verb that enforces it")
