"""Unit tests for validate.py.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import re
import sys
import tempfile
import pathlib
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ dir, for the sibling helper
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # scripts/, for lib + siblings
import gitutil  # noqa: E402 - confined git for the fixture repos below
import loader  # noqa: E402 - the canonical way to import a script under test
import workspace  # noqa: E402 - the dev-repo-only skip authority
from lib import sdlc_md  # noqa: E402

refine = loader.load_script("refine")   # BG0290: validate must accept what refine mints

SCRIPT_PATH = Path(__file__).resolve().parent.parent / "validate.py"
_spec = importlib.util.spec_from_file_location("validate", SCRIPT_PATH)
assert _spec and _spec.loader
validate = importlib.util.module_from_spec(_spec)
sys.modules["validate"] = validate
_spec.loader.exec_module(validate)

GOOD_STORY = "# Login\n\n> **Status:** Done\n\n### AC1: Happy\n- **Verify:** file a.py\n"


def _write(root: Path, rel: str, text: str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


class ValidateFileTests(unittest.TestCase):
    def test_good_story_has_no_violations(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = _write(Path(d), "sdlc-studio/stories/US0001-login.md", GOOD_STORY)
            self.assertEqual(validate.validate_file(p, "story"), [])

    def test_bad_status_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = _write(Path(d), "sdlc-studio/stories/US0002-x.md",
                       "# X\n\n> **Status:** Frozen\n\n### AC1: y\n- **Verify:** file b\n")
            rules = {v["rule"] for v in validate.validate_file(p, "story")}
            self.assertIn("status-vocab", rules)

    def test_status_vocab_error_names_extension_mechanism(self) -> None:
        # The error carries the sanctioned remedy: declare an established project
        # status via config, not rewrite historical artifacts.
        with tempfile.TemporaryDirectory() as d:
            p = _write(Path(d), "sdlc-studio/stories/US0002-x.md",
                       "# X\n\n> **Status:** Frozen\n\n### AC1: y\n- **Verify:** file b\n")
            msgs = [v["message"] for v in validate.validate_file(p, "story")
                    if v["rule"] == "status-vocab"]
            self.assertEqual(len(msgs), 1)
            self.assertIn("status_vocab.story", msgs[0])
            self.assertIn(".config.yaml", msgs[0])
            self.assertIn("reference-config.md", msgs[0])

    def test_missing_status_and_title(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = _write(Path(d), "sdlc-studio/stories/US0003-x.md", "no heading, no status\n")
            rules = {v["rule"] for v in validate.validate_file(p, "story")}
            self.assertIn("no-status", rules)
            self.assertIn("no-title", rules)

    def test_story_without_ac_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = _write(Path(d), "sdlc-studio/stories/US0004-x.md",
                       "# X\n\n> **Status:** Draft\n")
            rules = {v["rule"] for v in validate.validate_file(p, "story")}
            self.assertIn("no-ac", rules)

    def test_a_stated_absence_is_not_criteria_at_a_terminal_status(self) -> None:
        """`file_finding` writes this paragraph AUTOMATICALLY when a finding's evidence is too
        thin to derive a criterion, so it is the DEFAULT for a thin finding, not a deliberate
        act. `sdlc_md.count_acs` correctly reads it as zero criteria; `_has_criteria` read the
        populated section as criteria present, and the floor consults the second one - so a bug
        carrying no criterion at all reached Fixed with nothing to refuse it. Verified live on
        a fresh project before this test was written.

        One question, two answers, and the looser one runs: the same defect as the lane's two
        parsers, one file away.
        """
        import file_finding
        with tempfile.TemporaryDirectory() as d:
            body = (f"# X\n\n> **Status:** Fixed\n\n## Acceptance Criteria\n\n"
                    f"{file_finding.THIN_EVIDENCE_MARK}: `summary` carries fewer than 5 words "
                    f"of substance, so nothing here states what fixed would look like.\n")
            p = _write(Path(d), "sdlc-studio/bugs/BG0009-x.md", body)
            rules = {v["rule"] for v in validate.validate_file(p, "bug")}
            self.assertIn("no-ac", rules,
                          "a stated absence states that there is no criterion - counting it as "
                          "one lets a bug reach terminal with nothing verifiable")

    def test_the_two_criteria_predicates_agree(self) -> None:
        """The differential. Each predicate was individually correct and they disagreed on the
        same bytes, which no test of either alone could see."""
        import file_finding
        absence = (f"# X\n\n> **Status:** Fixed\n\n## Acceptance Criteria\n\n"
                   f"{file_finding.THIN_EVIDENCE_MARK}: too thin to derive anything.\n")
        real = ("# X\n\n> **Status:** Fixed\n\n## Acceptance Criteria\n\n"
                "### AC1: it holds\n\n- **Given** a thing\n- **Verify:** file b\n")
        for text, expect in ((absence, False), (real, True)):
            self.assertEqual(validate._has_criteria(text), expect)
            self.assertEqual(sdlc_md.count_acs(text) > 0, expect)
            self.assertEqual(validate._has_criteria(text), sdlc_md.count_acs(text) > 0,
                             "the floor and the counter must give one answer, not two")

    def test_quoting_the_absence_marker_elsewhere_does_not_erase_real_criteria(self) -> None:
        """The first version of this predicate scanned the whole document, so an artefact that
        merely QUOTED the filer's sentence - a bug filed ABOUT the filer is the obvious case -
        was judged to carry no criteria even with a populated section. Prose criteria are the
        shape that breaks: with no `### ACn` id to find, the marker decided alone."""
        import file_finding
        prose = ("# X\n\n> **Status:** Fixed\n\n## Summary\n\n"
                 f'This bug is about the filer writing "{file_finding.THIN_EVIDENCE_MARK}".\n\n'
                 "## Acceptance Criteria\n\nThe waiver is refused at record time when it names "
                 "no reason, and the refusal names the rule it could not resolve.\n")
        self.assertTrue(validate._has_criteria(prose),
                        "a populated criteria section is criteria, whatever the body quotes")
        labelled = prose.replace(
            "The waiver is refused at record time when it names no reason, and the refusal "
            "names the rule it could not resolve.",
            "### AC1: it holds\n\n- **Given** a thing\n- **Verify:** file b")
        self.assertTrue(validate._has_criteria(labelled))
        absent = ("# X\n\n> **Status:** Fixed\n\n## Acceptance Criteria\n\n"
                  f"{file_finding.THIN_EVIDENCE_MARK}: too thin to derive anything.\n")
        self.assertFalse(validate._has_criteria(absent),
                         "the marker IN the section is still an absence")

    def test_no_ac_grandfathered_below_adopt_after(self) -> None:
        # A pre-cutoff story is exempt from no-ac; a story at/after the cutoff is not.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "sdlc-studio/.config.yaml",
                   "conformance:\n  adopt_after: US0682\n")
            old = _write(root, "sdlc-studio/stories/US0100-x.md",
                         "# X\n\n> **Status:** Draft\n")
            new = _write(root, "sdlc-studio/stories/US0700-y.md",
                         "# Y\n\n> **Status:** Draft\n")
            old_rules = {v["rule"] for v in validate.validate_file(old, "story", root)}
            new_rules = {v["rule"] for v in validate.validate_file(new, "story", root)}
            self.assertNotIn("no-ac", old_rules)  # grandfathered
            self.assertIn("no-ac", new_rules)      # judged

    def test_no_ac_still_flagged_without_cutoff(self) -> None:
        # No .config.yaml cutoff -> the discipline applies to every story.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = _write(root, "sdlc-studio/stories/US0100-x.md",
                       "# X\n\n> **Status:** Draft\n")
            rules = {v["rule"] for v in validate.validate_file(p, "story", root)}
            self.assertIn("no-ac", rules)

    def test_no_ac_still_flagged_with_malformed_config(self) -> None:
        # Fail-safe: a broken .config.yaml must NOT silently exempt - no-ac fires.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "sdlc-studio/.config.yaml", ": : not yaml :")
            p = _write(root, "sdlc-studio/stories/US0001-x.md",
                       "# X\n\n> **Status:** Draft\n")
            rules = {v["rule"] for v in validate.validate_file(p, "story", root)}
            self.assertIn("no-ac", rules)

    def test_no_ac_at_cutoff_is_exempt(self) -> None:
        # The cutoff is inclusive (<=): the cutoff story itself is grandfathered, matching
        # conformance/provenance ("this id and earlier are exempt").
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "sdlc-studio/.config.yaml",
                   "conformance:\n  adopt_after: US0100\n")
            p = _write(root, "sdlc-studio/stories/US0100-x.md",
                       "# X\n\n> **Status:** Draft\n")
            rules = {v["rule"] for v in validate.validate_file(p, "story", root)}
            self.assertNotIn("no-ac", rules)  # boundary id exempt

    def test_no_ac_bare_int_cutoff_exempts_at_boundary(self) -> None:
        # BG0039: a bare-integer cutoff used to silently fail here (id_number("103") -> None),
        # so a pre-cutoff story was wrongly flagged. It must now exempt ids <= the cutoff.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "sdlc-studio/.config.yaml",
                   "conformance:\n  adopt_after: 103\n")  # bare int
            at = _write(root, "sdlc-studio/stories/US0103-x.md",
                        "# X\n\n> **Status:** Draft\n")     # 103 <= 103 -> exempt
            below = _write(root, "sdlc-studio/stories/US0050-y.md",
                           "# Y\n\n> **Status:** Draft\n")  # 50 <= 103 -> exempt
            above = _write(root, "sdlc-studio/stories/US0200-z.md",
                           "# Z\n\n> **Status:** Draft\n")  # 200 > 103 -> judged
            self.assertNotIn("no-ac", {v["rule"] for v in validate.validate_file(at, "story", root)})
            self.assertNotIn("no-ac", {v["rule"] for v in validate.validate_file(below, "story", root)})
            self.assertIn("no-ac", {v["rule"] for v in validate.validate_file(above, "story", root)})

    def test_bad_id_format(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = _write(Path(d), "sdlc-studio/stories/login.md", GOOD_STORY)
            rules = {v["rule"] for v in validate.validate_file(p, "story")}
            self.assertIn("id-format", rules)

    def test_decorated_status_accepted(self) -> None:
        # `Done (v2.66.0)` canonicalises to `Done` — not a status-vocab error.
        with tempfile.TemporaryDirectory() as d:
            p = _write(Path(d), "sdlc-studio/stories/US0005-x.md",
                       "# X\n\n> **Status:** Done (v2.66.0)\n\n### AC1: y\n- **Verify:** file b\n")
            rules = {v["rule"] for v in validate.validate_file(p, "story")}
            self.assertNotIn("status-vocab", rules)

    def test_bold_bullet_ac_accepted(self) -> None:
        # `- **AC1:**` compact bullet style satisfies the AC requirement.
        with tempfile.TemporaryDirectory() as d:
            p = _write(Path(d), "sdlc-studio/stories/US0006-x.md",
                       "# X\n\n> **Status:** Draft\n\n- **AC1:** login works\n")
            rules = {v["rule"] for v in validate.validate_file(p, "story")}
            self.assertNotIn("no-ac", rules)

    def test_plain_ac_section_accepted(self) -> None:
        # A populated `## Acceptance Criteria` section (plain bullets, no ACn
        # ids) satisfies the AC requirement.
        with tempfile.TemporaryDirectory() as d:
            p = _write(Path(d), "sdlc-studio/stories/US0007-x.md",
                       "# X\n\n> **Status:** Draft\n\n## Acceptance Criteria\n\n- user can log in\n")
            rules = {v["rule"] for v in validate.validate_file(p, "story")}
            self.assertNotIn("no-ac", rules)

    def test_empty_ac_section_still_flagged(self) -> None:
        # An AC heading with no content before the next heading is still no-ac.
        with tempfile.TemporaryDirectory() as d:
            p = _write(Path(d), "sdlc-studio/stories/US0008-x.md",
                       "# X\n\n> **Status:** Draft\n\n## Acceptance Criteria\n\n## Notes\n- something\n")
            rules = {v["rule"] for v in validate.validate_file(p, "story")}
            self.assertIn("no-ac", rules)


class UngroomedMarkerTests(unittest.TestCase):
    """BG0290: `refine` mints an ungroomed story whose AC section holds only the grooming
    marker, `conformance` reads that as a legitimate pre-Ready state, and `validate` called
    the same bytes `no-ac`. Both run in the same pre-commit gate, so the refine that created
    the backlog could not be committed and there was no groom-before-commit path (the story
    must exist to be groomed).

    The marker is a blockquote and `_has_ac_section` skips blockquotes, which is why the split
    looked like `--epic-title` versus `--into` and was neither: the real trigger is whether the
    REQUEST carries `- [ ]` criteria to seed from. A CR does, an RFC does not, so refining any
    accepted RFC produced uncommittable stories.
    """

    def _story(self, root: Path, ac_body: str, name: str = "US0900-x.md") -> Path:
        return _write(root, f"sdlc-studio/stories/{name}",
                      "# US0900: A refined story\n\n> **Status:** Draft\n> **Epic:** EP0001\n\n"
                      "## User Story\n\n**As a** x\n**I want** y\n**So that** z\n\n"
                      f"## Acceptance Criteria\n\n{ac_body}"
                      "## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n")

    def test_the_ungroomed_marker_is_not_a_no_ac_error(self) -> None:
        # BG0290 AC1, both halves: the MARKED story is a known pre-Ready state; an AC section
        # that is merely empty declares nothing and stays the error it always was.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            marked = self._story(root, sdlc_md.UNGROOMED_AC_MARKER + "\n\n")
            rules = {v["rule"] for v in validate.validate_file(marked, "story")}
            self.assertNotIn("no-ac", rules)
            empty = self._story(root, "", name="US0901-x.md")
            rules = {v["rule"] for v in validate.validate_file(empty, "story")}
            self.assertIn("no-ac", rules)

    def test_a_story_refine_just_minted_passes_validate(self) -> None:
        """The end-to-end pin, on refine's real output rather than a copied marker: a
        multi-story breakdown of a request with NO criteria to seed from is the shape that
        blocked the commit."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "src").mkdir(parents=True, exist_ok=True)
            (root / "src" / "a.py").write_text("", encoding="utf-8")
            _write(root, "sdlc-studio/rfcs/RFC0001-x.md",
                   "# RFC-0001: A design\n\n> **Status:** Accepted\n> **Affects:** src/a.py\n\n"
                   "## Summary\n\ns\n\n## Design Options\n\no\n")
            res = refine.refine(root, "RFC0001", "The epic",
                                [("First slice", 2, None), ("Second slice", 3, None)],
                                skip_personas=True)
            for sid in res["stories"]:
                spath = sdlc_md.find_by_id(root, sid)[0]
                with self.subTest(story=sid):
                    errs = [v for v in validate.validate_file(spath, "story")
                            if v["severity"] == "error"]
                    self.assertEqual(errs, [], f"refine minted a story validate refuses: {errs}")

    def test_validate_and_conformance_agree_on_every_shipped_story(self) -> None:
        """BG0290 AC2: one definition of ungroomed, read by both guards.

        The corpus half alone would be vacuous the moment the backlog is fully groomed (it is,
        today: 0 of 431 stories are ungroomed), so the canonical shapes are checked beside it -
        and the delegation itself is proved by moving conformance's answer and watching
        validate follow, which no restated copy of the rule could do.
        """
        import conformance  # the predicate's owner - validate must be reading THIS one
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cases = {"marker": self._story(root, sdlc_md.UNGROOMED_AC_MARKER + "\n\n"),
                     "legacy scaffold": self._story(root, "### AC1: {{define}}\n\n",
                                                    name="US0902-x.md"),
                     "empty": self._story(root, "", name="US0903-x.md")}
            for label, path in cases.items():
                text = path.read_text(encoding="utf-8")
                flagged = any(v["rule"] == "no-ac" for v in validate.validate_file(path, "story"))
                with self.subTest(case=label):
                    self.assertFalse(conformance.story_is_ungroomed(text) and flagged,
                                     f"{label}: conformance says ungroomed, validate says no-ac")
            # The delegation, not a coincidence of two agreeing implementations: with
            # conformance's answer moved, validate's verdict on the EMPTY story moves with it.
            empty = cases["empty"]
            original = conformance.story_is_ungroomed
            conformance.story_is_ungroomed = lambda text: True
            try:
                rules = {v["rule"] for v in validate.validate_file(empty, "story")}
            finally:
                conformance.story_is_ungroomed = original
            self.assertNotIn("no-ac", rules,
                             "validate holds its own copy of the ungroomed rule - two copies drift")
        if not workspace.in_dev_repo():
            self.skipTest(workspace.SKIP_REASON)   # the corpus half is dev-repo-only
        stories = sorted((workspace.REPO / "sdlc-studio" / "stories").glob("US*.md"))
        self.assertTrue(stories, "no shipped stories to check")
        for path in stories:
            text = path.read_text(encoding="utf-8")
            if not conformance.story_is_ungroomed(text):
                continue
            flagged = [v for v in validate.validate_file(path, "story") if v["rule"] == "no-ac"]
            self.assertEqual(flagged, [], f"{path.name}: ungroomed to conformance, malformed to "
                                          f"validate - the two guards disagree")


class ContradictedAffectsTests(unittest.TestCase):
    """US0292 AC4. `validate` and the planner must reach the same verdict on one artefact,
    because they read the same field for different purposes - the planner to cluster parallel
    work, the engagement floor to judge a declared footprint. Two implementations of
    "contradicted" is how the same bytes come to pass one check and fail the other.

    The fixtures are TERMINAL (US0528): the predicate is still the planner's and still shared,
    but validate reports the `unresolvable` half only once the unit is closed, because
    declaring the file you are about to create is what an open unit is for. What the two
    readers must agree on is what is unresolvable, which is what these tests assert."""

    def _story(self, root: Path, affects: str, verify: str, status: str = "Done") -> Path:
        return _write(root, "sdlc-studio/stories/US0001-x.md",
                      f"# US0001: s\n\n> **Status:** {status}\n> **Affects:** {affects}\n"
                      f"> **Points:** 2\n\n## Acceptance Criteria\n\n### AC1: a\n\n"
                      f"- **Given** x\n- **Verify:** {verify}\n")

    def test_validate_reports_an_affects_the_story_contradicts(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "src/real.py", "x = 1\n")
            _write(root, "tests/test_p.py", "def test_x(): pass\n")
            p = self._story(root, "src/real.py,src/typo.py", "pytest tests/test_p.py -k test_x")
            rules = {v["rule"] for v in validate.validate_file(p, "story", repo_root=root)}
            self.assertIn("affects-unresolvable", rules)
            self.assertIn("affects-undeclared", rules)

    def test_a_clean_affects_is_reported_by_neither_rule(self) -> None:
        """The negative control: without it, a function reporting every story unconditionally
        would satisfy the test above."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "src/real.py", "x = 1\n")
            _write(root, "tests/test_p.py", "def test_x(): pass\n")
            p = self._story(root, "src/real.py,tests/test_p.py",
                            "pytest tests/test_p.py -k test_x")
            rules = {v["rule"] for v in validate.validate_file(p, "story", repo_root=root)}
            self.assertNotIn("affects-unresolvable", rules)
            self.assertNotIn("affects-undeclared", rules)

    def test_both_readers_agree_on_the_same_artefact(self) -> None:
        """The point of the shared predicate, asserted directly rather than assumed."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "src/real.py", "x = 1\n")
            _write(root, "tests/test_p.py", "def test_x(): pass\n")
            p = self._story(root, "src/real.py,src/typo.py", "pytest tests/test_p.py -k test_x")
            sys.path.insert(0, str(Path(validate.__file__).parent))
            import sprint
            mism = sprint.affects_mismatch(root, p.read_text(encoding="utf-8"))
            msgs = " ".join(v["message"] for v in validate.validate_file(p, "story",
                                                                        repo_root=root))
            for path in mism["unresolvable"] + mism["undeclared"]:
                self.assertIn(path, msgs, "validate names exactly what the planner found")

    def test_the_severity_is_a_warning_not_an_error(self) -> None:
        """A path to a file the unit will CREATE is legitimate, so an error would fail the
        ordinary case and the rule would be turned off."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "src/real.py", "x = 1\n")
            p = self._story(root, "src/real.py,src/not-yet.py", "file src/real.py")
            sev = {v["severity"] for v in validate.validate_file(p, "story", repo_root=root)
                   if v["rule"].startswith("affects-")}
            self.assertEqual(sev, {validate.SEVERITY_WARNING})


class InferTypeTests(unittest.TestCase):
    def test_infer_from_dir(self) -> None:
        self.assertEqual(validate.infer_type(Path("sdlc-studio/epics/EP0001-x.md")), "epic")

    def test_infer_from_id_prefix(self) -> None:
        self.assertEqual(validate.infer_type(Path("/tmp/CR-0001-x.md")), "cr")


class CheckCmdTests(unittest.TestCase):
    """A PASSING suite must be silent.

    These tests feed the validator a deliberately-broken story and assert it complains. The
    complaint is the thing under test - but it was being written straight to the console, so a
    fully green run printed `ERROR` lines and the tail of a 2000-test pass read like a failure.
    Worse, it trains everyone (human and agent) to skim past `ERROR`, which is exactly the
    reflex that lets a real one through: a signal indistinguishable from noise is not a signal.

    So the diagnostics are captured, and asserted ON, rather than leaked. The assertions are
    stronger for it - previously these tests checked only the exit code and never looked at
    what the validator actually said.
    """

    def _check(self, root: str) -> tuple[int, str]:
        """Run the validator, capturing what it says instead of spilling it to the console."""
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            rc = validate.main(["check", "--type", "story", "--root", root])
        return rc, buf.getvalue()

    def test_check_exit_nonzero_on_error(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            _write(Path(d), "sdlc-studio/stories/US0001-bad.md", "# X\n\n> **Status:** Frozen\n")
            rc, out = self._check(d)
            self.assertEqual(rc, 1)
            # Assert on the diagnostics now that we hold them: the exit code alone does not
            # prove the validator objected for the RIGHT reason.
            self.assertIn("status-vocab", out)
            self.assertIn("no-ac", out)

    def test_check_exit_zero_when_clean(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            _write(Path(d), "sdlc-studio/stories/US0001-login.md", GOOD_STORY)
            rc, out = self._check(d)
            self.assertEqual(rc, 0)
            self.assertNotIn("ERROR", out)


# The pointer half: the four cross-reference rules and nothing else. This is the fixture
# CR0353 was raised about - it passes every rule the check had while saying nothing about how
# the project is developed.
POINTERS_ONLY_AGENTS = (
    "# Proj\n\n"
    "Read `reference-doctrine.md`. Read `sdlc-studio/reviews/LATEST.md` first.\n"
    "IMPORTANT pre-release gate: `/sdlc-studio reconcile --verify` + the review legs.\n"
    "After `/compact` or a reset, re-read LATEST.md and run status.\n"
)

# A sound file: the pointers PLUS the working model the pointers used to stand in for.
GOOD_AGENTS = POINTERS_ONLY_AGENTS + (
    "Every substantive change flows through the skill: CR -> Epic -> Story -> plan ->\n"
    "implement -> verify. No ad-hoc coding.\n"
    "Never hand-allocate ids or hand-author `_index.md` - the index is derived.\n"
    "A story reaches Done only when its executable ACs pass.\n"
    "Review is independent of the author: the reviewer of record never wrote the change.\n"
)


def _shipped_template() -> str:
    """The shipped agent-instructions template as a project would save it - guidance
    comment stripped. The exemplar the check tells people to copy."""
    text = (SCRIPT_PATH.parent.parent / "templates" / "agent-instructions.md").read_text(
        encoding="utf-8")
    return re.sub(r"^<!--.*?-->\n+", "", text, count=1, flags=re.DOTALL)


def _template_headings() -> set[str]:
    return set(re.findall(r"^#{2,}\s+(.*)$", _shipped_template(), re.M))


class InstructionsTests(unittest.TestCase):
    def test_missing_agents_is_error(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            v = validate.check_instructions(Path(d))
            self.assertIn("no-agents", {x["rule"] for x in v})
            self.assertTrue(any(x["severity"] == "error" for x in v))

    def test_good_agents_clean(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "AGENTS.md").write_text(GOOD_AGENTS, encoding="utf-8")
            (root / "CLAUDE.md").write_text("@AGENTS.md\n", encoding="utf-8")
            self.assertEqual(validate.check_instructions(root), [])

    def test_claude_not_pointer_warns(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "AGENTS.md").write_text(GOOD_AGENTS, encoding="utf-8")
            (root / "CLAUDE.md").write_text("# full instructions inline\n", encoding="utf-8")
            self.assertIn("claude-not-pointer", {x["rule"] for x in validate.check_instructions(root)})

    def test_missing_elements_warn(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "AGENTS.md").write_text("# Proj\n\nNothing useful here.\n", encoding="utf-8")
            rules = {x["rule"] for x in validate.check_instructions(root)}
            self.assertIn("no-doctrine-pointer", rules)
            self.assertIn("no-latest-pointer", rules)
            self.assertIn("no-release-gate", rules)
            self.assertIn("no-compaction-rule", rules)

    def test_no_agents_finding_is_marked_seedable(self) -> None:
        # US0294: the one rule whose remedy is fully deterministic carries a machine-readable
        # remedy, so the caller acts on the structure and never parses the prose.
        with tempfile.TemporaryDirectory() as d:
            f = next(x for x in validate.check_instructions(Path(d)) if x["rule"] == "no-agents")
            self.assertTrue(f.get("seedable"))
            self.assertEqual(f.get("template"), "templates/agent-instructions.md")
            self.assertEqual(f.get("target"), "AGENTS.md")
            # D0052: severity stays `error` even once seeding is possible - CI reads the exit code.
            self.assertEqual(f["severity"], validate.SEVERITY_ERROR)

    def test_only_the_absent_file_case_is_seedable(self) -> None:
        # A caller acting on the marker can never overwrite a file that exists.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "AGENTS.md").write_text("# Proj\n\nNothing useful here.\n", encoding="utf-8")
            (root / "CLAUDE.md").write_text("# full instructions inline\n", encoding="utf-8")
            findings = validate.check_instructions(root)
            self.assertTrue(findings, "the fixture must fail rules for this to mean anything")
            self.assertEqual([f["rule"] for f in findings if f.get("seedable")], [])

    def test_no_agents_message_names_the_seeding_command(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            f = next(x for x in validate.check_instructions(Path(d)) if x["rule"] == "no-agents")
            self.assertIn("migrate --apply", f["message"])

    def test_cmd_exit_nonzero_when_no_agents(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            with contextlib.redirect_stdout(io.StringIO()):
                rc = validate.main(["instructions", "--root", d])
            self.assertEqual(rc, 1)

    def test_cmd_exit_zero_when_clean(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "AGENTS.md").write_text(GOOD_AGENTS, encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                rc = validate.main(["instructions", "--root", d])
            self.assertEqual(rc, 0)


class WorkingModelTests(unittest.TestCase):
    """US0295/US0296: the check tests that the file establishes how the project is developed,
    not only that it cross-references four other documents. A file can hold every pointer and
    never say work is done this way; the check used to call that good."""

    def _root(self, d, agents: str, *, claude: str = "@AGENTS.md\n") -> Path:
        root = Path(d)
        (root / "AGENTS.md").write_text(agents, encoding="utf-8")
        (root / "CLAUDE.md").write_text(claude, encoding="utf-8")
        return root

    def _working_model(self, findings: list[dict]) -> list[dict]:
        keys = {s["key"] for s in validate.WORKING_MODEL_RULES}
        return [f for f in findings if f.get("element") in keys]

    def test_working_model_rules_fire_per_missing_element(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d, POINTERS_ONLY_AGENTS)
            rules = {f["rule"] for f in validate.check_instructions(root)}
            for spec in validate.WORKING_MODEL_RULES:
                self.assertIn("no-" + spec["key"], rules)
            # one distinct rule per element, not one lumped finding
            self.assertEqual(len(self._working_model(validate.check_instructions(root))),
                             len(validate.WORKING_MODEL_RULES))

    def test_shipped_template_satisfies_the_working_model_rules(self) -> None:
        # The exemplar the check tells people to copy must clear the bar the check sets.
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d, _shipped_template())
            findings = validate.check_instructions(root)
            self.assertEqual(self._working_model(findings), [],
                             "the shipped template fails its own working-model rules")
            self.assertEqual(findings, [], "the shipped template fails the hygiene check")

    def test_a_recorded_opt_out_is_reported_as_such(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d, POINTERS_ONLY_AGENTS)
            cfg = root / "sdlc-studio"
            cfg.mkdir(parents=True, exist_ok=True)
            (cfg / ".config.yaml").write_text(
                "instructions:\n  working_model_opt_out:\n    - independent-review\n",
                encoding="utf-8")
            findings = validate.check_instructions(root)
            rules = {f["rule"] for f in findings}
            self.assertIn("independent-review-opted-out", rules)   # its own rule id
            self.assertNotIn("no-independent-review", rules)       # not counted as a defect
            opt = next(f for f in findings if f["rule"] == "independent-review-opted-out")
            self.assertEqual(opt["severity"], validate.SEVERITY_INFO)
            self.assertTrue(opt.get("opted_out"))
            # the other three still apply, unchanged
            for key in ("delivery-flow", "tool-allocated-ids", "executable-ac-gate"):
                self.assertIn("no-" + key, rules)

    def test_pointer_perfect_fixture_fails_only_the_working_model_rules(self) -> None:
        # The proof obligation: if the fixture failed the six existing rules too, the new
        # rules would only be restating them.
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d, POINTERS_ONLY_AGENTS)
            findings = validate.check_instructions(root)
            existing = {"no-agents", "claude-not-pointer", "no-doctrine-pointer",
                        "no-latest-pointer", "no-release-gate", "no-compaction-rule"}
            self.assertEqual({f["rule"] for f in findings} & existing, set())
            self.assertEqual(len(self._working_model(findings)),
                             len(validate.WORKING_MODEL_RULES))

    def test_each_working_model_finding_cites_a_template_section(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d, POINTERS_ONLY_AGENTS)
            for f in self._working_model(validate.check_instructions(root)):
                spec = next(s for s in validate.WORKING_MODEL_RULES if s["key"] == f["element"])
                self.assertIn(spec["element"], f["message"])          # the missing element
                self.assertIn(f["template_section"], f["message"])    # and where it comes from
                self.assertIn("templates/agent-instructions.md", f["message"])

    def test_cited_template_sections_exist_in_the_shipped_template(self) -> None:
        # Renaming or removing a cited section must fail here, not leave the messages
        # pointing at nothing.
        headings = _template_headings()
        body = _shipped_template()
        for spec in validate.WORKING_MODEL_RULES:
            self.assertIn(spec["section"], headings,
                          f"{spec['key']} cites a section the template does not have")
            self.assertIn(spec["anchor"], body,
                          f"{spec['key']} cites an anchor the template does not carry")

    def test_report_never_calls_a_working_model_less_file_good(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self._root(d, POINTERS_ONLY_AGENTS)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                validate.main(["instructions", "--root", d])
            out = buf.getvalue()
            self.assertNotIn("agent-instructions files look good.", out)
            for spec in validate.WORKING_MODEL_RULES:
                self.assertIn("no-" + spec["key"], out)


class PlaceholderTests(unittest.TestCase):
    def _story(self, body):
        import tempfile
        d = tempfile.mkdtemp()
        f = pathlib.Path(d) / "US0001-x.md"
        f.write_text(body, encoding="utf-8")
        return f

    def test_placeholder_ac_flagged(self):
        # A GROOMED (Ready+) story with a placeholder AC is an ERROR - a story that claims Ready
        # must have executable ACs.
        f = self._story("# US0001: x\n\n> **Status:** Ready\n\n## Acceptance Criteria\n\n"
                        "### AC1: {{define}}\n\n- **Given** {{context}}\n- **Verify:** {{check}}\n")
        rules = [v["rule"] for v in validate.validate_file(f, "story") if v["severity"] == "error"]
        self.assertIn("placeholder", rules)

    def test_draft_story_placeholder_ac_is_a_warning_not_error(self):
        # CR0342: an ungroomed Draft story's AC placeholders are a WARNING, so the refine commit
        # that creates the Draft backlog lands; the placeholder still keeps it out of Ready/Done.
        f = self._story("# US0001: x\n\n> **Status:** Draft\n\n## Acceptance Criteria\n\n"
                        "### AC1: {{define}}\n\n- **Given** {{context}}\n- **Verify:** {{check}}\n")
        findings = [v for v in validate.validate_file(f, "story") if v["rule"] == "placeholder"]
        self.assertTrue(findings, "the placeholder is still reported")
        self.assertTrue(all(v["severity"] == validate.SEVERITY_WARNING for v in findings),
                        "an ungroomed Draft story's placeholder is a warning, not an error")

    def test_placeholder_metadata_flagged(self):
        f = self._story("# US0001: x\n\n> **Status:** {{status}}\n\n## Acceptance Criteria\n\n"
                        "- some real criterion\n")
        self.assertIn("placeholder", [v["rule"] for v in validate.validate_file(f, "story")])

    def test_prose_placeholder_not_flagged(self):
        # meta-artifact discussing {{placeholder}} syntax in prose must NOT be flagged
        f = self._story("# US0001: x\n\n> **Status:** Draft\n\n## Description\n\n"
                        "Templates use {{placeholder}} syntax for fields.\n\n"
                        "## Acceptance Criteria\n\n- a real filled criterion\n")
        self.assertNotIn("placeholder", [v["rule"] for v in validate.validate_file(f, "story")])

    def test_checkbox_placeholder_flagged(self):
        # CR/story AC checklist `- [ ] {{criterion}}` is a structural AC line (CR0056 critic gap).
        f = self._story("# US0001: x\n\n> **Status:** Draft\n\n## Acceptance Criteria\n\n"
                        "- [ ] {{criterion}}\n")
        self.assertIn("placeholder", [v["rule"] for v in validate.validate_file(f, "story")])

    def test_checkbox_real_text_not_flagged(self):
        f = self._story("# US0001: x\n\n> **Status:** Draft\n\n## Acceptance Criteria\n\n"
                        "- [ ] a genuine filled criterion\n")
        self.assertNotIn("placeholder", [v["rule"] for v in validate.validate_file(f, "story")])

    def test_user_story_block_placeholder_flagged(self):
        # BG0304: the `**As a** {{role}}` scaffold artifact.py mints lives in the body, outside
        # both metadata and the AC section - 39 stories reached Done carrying it unfilled while
        # the check reported nothing. A Done story's unfilled body slot is an error.
        f = self._story("# US0001: x\n\n> **Status:** Done\n\n## User Story\n\n"
                        "**As a** {{role}}\n**I want** {{capability}}\n**So that** {{benefit}}\n\n"
                        "## Acceptance Criteria\n\n- a real filled criterion\n")
        findings = [v for v in validate.validate_file(f, "story") if v["rule"] == "placeholder"]
        self.assertTrue(findings, "the unfilled user-story block is reported")
        self.assertTrue(any(v["severity"] == "error" for v in findings),
                        "a Done story's unfilled body slot is an error")

    def test_draft_story_body_placeholder_is_a_warning_not_error(self):
        # Same grandfather as the AC path: a fresh refine output is all scaffold, so its body
        # placeholders must not block the refine commit that creates it.
        f = self._story("# US0001: x\n\n> **Status:** Draft\n\n## User Story\n\n"
                        "**As a** {{role}}\n\n## Acceptance Criteria\n\n- a real filled criterion\n")
        findings = [v for v in validate.validate_file(f, "story") if v["rule"] == "placeholder"]
        self.assertTrue(findings, "the placeholder is still reported")
        self.assertTrue(all(v["severity"] == validate.SEVERITY_WARNING for v in findings),
                        "an ungroomed Draft story's body placeholder is a warning, not an error")

    def test_terminal_non_story_body_placeholder_is_an_error(self):
        # The same hole in every other type: a bug that reached Fixed with its Summary still
        # `{{symptom}}` is a finished record with a blank where its content should be. The
        # terminal set is derived from the type's own vocabulary, not enumerated here.
        import tempfile
        f = pathlib.Path(tempfile.mkdtemp()) / "BG0001-x.md"
        f.write_text("# BG0001: x\n\n> **Status:** Fixed\n> **Severity:** Medium\n\n"
                     "## Summary\n\n{{symptom}}\n\n## Steps to Reproduce\n\nrun the tool\n",
                     encoding="utf-8")
        findings = [v for v in validate.validate_file(f, "bug") if v["rule"] == "placeholder"]
        self.assertTrue(any(v["severity"] == "error" for v in findings),
                        "a terminal bug's unfilled body slot is an error")

    def test_in_flight_non_story_body_placeholder_is_a_warning(self):
        # A freshly minted artefact is scaffolded by design, so creation must not error - the
        # create/validate round trip depends on it. It is still reported.
        import tempfile
        f = pathlib.Path(tempfile.mkdtemp()) / "BG0001-x.md"
        f.write_text("# BG0001: x\n\n> **Status:** Open\n> **Severity:** Medium\n\n"
                     "## Summary\n\n{{symptom}}\n\n## Steps to Reproduce\n\nrun the tool\n",
                     encoding="utf-8")
        findings = [v for v in validate.validate_file(f, "bug") if v["rule"] == "placeholder"]
        self.assertTrue(findings, "the placeholder is still reported")
        self.assertTrue(all(v["severity"] == validate.SEVERITY_WARNING for v in findings),
                        "an in-flight artefact's body placeholder is a warning, not an error")

    def test_body_placeholder_inside_code_fence_not_flagged(self):
        # A fenced block is sample text - a story documenting the scaffold it generates is not
        # a story carrying an unfilled scaffold.
        f = self._story("# US0001: x\n\n> **Status:** Done\n\n## Description\n\n"
                        "The template emits:\n\n```markdown\n**As a** {{role}}\n```\n\n"
                        "## Acceptance Criteria\n\n- a real filled criterion\n")
        self.assertNotIn("placeholder", [v["rule"] for v in validate.validate_file(f, "story")])

    def test_embedded_token_in_real_ac_not_flagged(self):
        # A real, filled AC that references a {{...}} token in its text (this repo's own
        # meta-CRs) must NOT be flagged - only placeholder-ONLY values are (CR0056 critic).
        f = self._story("# US0001: x\n\n> **Status:** Draft\n\n## Acceptance Criteria\n\n"
                        "- [ ] validate flags unresolved {{...}} placeholders as an error\n"
                        "- [x] All three use `{{placeholder}}` syntax and pass lint\n")
        self.assertNotIn("placeholder", [v["rule"] for v in validate.validate_file(f, "story")])


class SeverityVocabularyTests(unittest.TestCase):
    """BG0217: the summary counters must count every severity the checks emit.

    A per-line WARN that the tail then reports as `warnings=0` is a summary contradicting the
    output above it - the same false-completeness class as a dry run disagreeing with its real
    run. These tests pin both halves: the vocabulary is closed, and the count equals the lines.
    """

    def _draft_story_with_placeholder_acs(self, root: Path) -> Path:
        return _write(root, "sdlc-studio/stories/US0001-x.md",
                      "# US0001: x\n\n> **Status:** Draft\n\n## Acceptance Criteria\n\n"
                      "### AC1: {{define}}\n\n- **Given** {{context}}\n- **Verify:** {{check}}\n")

    def test_every_emitted_severity_is_a_known_spelling(self) -> None:
        # A severity outside the closed vocabulary is invisible to the counters. Pinning the
        # set is what stops a third spelling being introduced later.
        with tempfile.TemporaryDirectory() as d:
            f = self._draft_story_with_placeholder_acs(Path(d))
            findings = validate.validate_file(f, "story")
            self.assertTrue(findings, "the fixture must produce findings for this to mean anything")
            unknown = sorted({v["severity"] for v in findings} - set(validate.SEVERITIES))
            self.assertEqual(unknown, [], f"severities the counters cannot count: {unknown}")

    def test_summary_warning_count_equals_the_warning_lines_printed(self) -> None:
        # The reported count and the printed output must agree. Three WARNING lines and a
        # `warnings=0` tail is the defect.
        with tempfile.TemporaryDirectory() as d:
            self._draft_story_with_placeholder_acs(Path(d))
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                validate.main(["check", "--type", "story", "--root", d])
            out = buf.getvalue()
            lines = [ln for ln in out.splitlines()
                     if ln.startswith(validate.SEVERITY_WARNING.upper())]
            self.assertGreaterEqual(len(lines), 3, f"expected the placeholder warnings:\n{out}")
            self.assertIn(f"warnings={len(lines)}", out,
                          f"summary count disagrees with the {len(lines)} lines printed:\n{out}")


class PersonaWellFormedTests(unittest.TestCase):
    def _persona(self, repo, name, role, *, sections):
        d = repo / "sdlc-studio" / "personas"; d.mkdir(parents=True, exist_ok=True)
        body = (f"# {name}\n\n## Quick Reference\n\n| Attribute | Value |\n| --- | --- |\n"
                f"| **Cast role** | {role} |\n\n")
        body += "".join(f"## {s}\n\nx\n\n" for s in sections)
        (d / f"{name}.md").write_text(body, encoding="utf-8")

    STD = ["Who They Are", "End Goals", "Experience Goals", "Behaviours & Context",
           "Frustrations", "Scenario"]
    NEG = ["Who They Are", "End Goals (stated to exclude)", "Why We Are Not Designing For Them",
           "Behaviours & Context", "Frustrations", "Scenario"]

    def test_well_formed_primary_no_findings(self):
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d); self._persona(repo, "maya", "Primary", sections=self.STD)
            self.assertEqual(validate.check_personas(repo), [])

    def test_primary_missing_scenario_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d)
            self._persona(repo, "maya", "Primary", sections=[s for s in self.STD if s != "Scenario"])
            msgs = [v["message"] for v in validate.check_personas(repo)]
            self.assertTrue(any("Scenario" in m for m in msgs))

    def test_negative_variant_well_formed_no_findings(self):
        # the Negative persona has no Experience Goals - the cast-role-aware check must accept it
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d); self._persona(repo, "trevor", "Negative", sections=self.NEG)
            self.assertEqual(validate.check_personas(repo), [])

    def test_negative_missing_whynot_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d)
            self._persona(repo, "trevor", "Negative",
                          sections=[s for s in self.NEG if "Why" not in s])
            msgs = [v["message"] for v in validate.check_personas(repo)]
            self.assertTrue(any("Why" in m for m in msgs))

    def test_customer_experience_and_scenario_optional(self):
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d)
            self._persona(repo, "buyer", "Customer",
                          sections=["Who They Are", "End Goals", "Behaviours & Context", "Frustrations"])
            self.assertEqual(validate.check_personas(repo), [])

    def _persona_iface(self, repo, name, role, interface=None):
        d = repo / "sdlc-studio" / "personas"; d.mkdir(parents=True, exist_ok=True)
        iface = f"| **Interface** | {interface} |\n" if interface else ""
        body = (f"# {name}\n\n## Quick Reference\n\n| Attribute | Value |\n| --- | --- |\n"
                f"| **Cast role** | {role} |\n{iface}\n")
        body += "".join(f"## {s}\n\nx\n\n" for s in self.STD)
        (d / f"{name}.md").write_text(body, encoding="utf-8")

    def test_two_primaries_is_a_warning(self):
        # Cooper: exactly one Primary per interface; two Primaries = two interfaces.
        # A warning by default - the cast MAY legitimately target two interfaces.
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d)
            self._persona_iface(repo, "maya", "Primary")
            self._persona_iface(repo, "omar", "Primary")
            found = [v for v in validate.check_personas(repo)
                     if v["rule"] == "persona-one-primary"]
            self.assertEqual(len(found), 1)
            self.assertEqual(found[0]["severity"], "warning")

    def test_two_primaries_same_interface_is_an_error(self):
        # ...but two Primaries DECLARING the same Interface: is the elastic user reborn
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d)
            self._persona_iface(repo, "maya", "Primary", interface="operator console")
            self._persona_iface(repo, "omar", "Primary", interface="Operator Console")
            found = [v for v in validate.check_personas(repo)
                     if v["rule"] == "persona-one-primary"]
            self.assertEqual(len(found), 1)
            self.assertEqual(found[0]["severity"], "error")

    def test_two_primaries_distinct_interfaces_no_finding(self):
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d)
            self._persona_iface(repo, "maya", "Primary", interface="operator console")
            self._persona_iface(repo, "omar", "Primary", interface="mobile app")
            rules = {v["rule"] for v in validate.check_personas(repo)}
            self.assertNotIn("persona-one-primary", rules)

    STAKE = ("<!-- stakeholder: compliance -->\n# Ines Ferreira - DPO\n\n"
             "> **Cast:** Customer\n\n## Who They Are\n\nx\n\n## What They Want\n\n1. x\n\n"
             "## Veto Lines\n\n- x\n\n## Evidence They Read\n\n- x\n")

    def _stakeholder(self, repo, name, body):
        d = repo / "sdlc-studio" / "personas" / "stakeholders"
        d.mkdir(parents=True, exist_ok=True)
        (d / name).write_text(body, encoding="utf-8")

    def test_well_formed_stakeholder_no_findings(self):
        # AC: check_personas learns the stakeholder schema - a generated panel produces
        # no permanent layout/section warnings
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d)
            self._stakeholder(repo, "ines.md", self.STAKE)
            self.assertEqual(validate.check_personas(repo), [])

    def test_stakeholder_missing_type_and_sections_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d)
            self._stakeholder(repo, "bare.md", "# Someone\n\n## Who They Are\n\nx\n")
            rules = {v["rule"] for v in validate.check_personas(repo)}
            self.assertIn("stakeholder-type", rules)
            self.assertIn("stakeholder-section", rules)
            self.assertIn("stakeholder-cast", rules)

    def test_stakeholder_unknown_type_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d)
            self._stakeholder(repo, "ines.md",
                              self.STAKE.replace("stakeholder: compliance",
                                                 "stakeholder: shareholder"))
            self.assertIn("stakeholder-type",
                          {v["rule"] for v in validate.check_personas(repo)})

    def test_stakeholder_check_is_advisory_only(self):
        # check_personas' contract: never errors, never in the hard gate
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d)
            self._stakeholder(repo, "bare.md", "# Someone\n")
            sev = {v["severity"] for v in validate.check_personas(repo)}
            self.assertEqual(sev, {"warning"})

    def test_missing_cast_role_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d)
            dd = repo / "sdlc-studio" / "personas"; dd.mkdir(parents=True)
            (dd / "x.md").write_text("# X\n\n## Who They Are\n\nx\n", encoding="utf-8")
            rules = [v["rule"] for v in validate.check_personas(repo)]
            self.assertIn("persona-cast-role", rules)


    def test_collision_headings_do_not_false_pass(self):
        # prefix matching: unrelated headings that merely contain the keywords must NOT satisfy
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d)
            self._persona(repo, "junk", "Primary",
                          sections=["Why End Goals Matter", "Some Context We Discuss",
                                    "Frustrations Of Other People", "Scenario Planning Theory"])
            rules = [v["rule"] for v in validate.check_personas(repo)]
            self.assertIn("persona-section", rules)  # flagged, not a clean pass

    def test_negative_loose_why_flagged(self):
        # "## Why This Matters" must NOT satisfy the Negative why-not rationale
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d)
            self._persona(repo, "t", "Negative",
                          sections=["Who They Are", "End Goals (stated to exclude)",
                                    "Why This Matters", "Behaviours & Context", "Frustrations", "Scenario"])
            msgs = [v["message"] for v in validate.check_personas(repo)]
            self.assertTrue(any("Why we are not" in m for m in msgs))

    def test_empty_bodies_still_well_formed(self):
        # well-formed is structural (headings present); bodies are not content-checked (RFC0017)
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d); self._persona(repo, "maya", "Primary", sections=self.STD)
            self.assertEqual(validate.check_personas(repo), [])

    def test_unknown_role_held_to_standard(self):
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d)
            dd = repo / "sdlc-studio" / "personas"; dd.mkdir(parents=True)
            # no Cast role; has the common sections but not Experience Goals / Scenario
            (dd / "x.md").write_text(
                "# X\n\n## Who They Are\n\nx\n## End Goals\n\nx\n"
                "## Behaviours & Context\n\nx\n## Frustrations\n\nx\n", encoding="utf-8")
            out = validate.check_personas(repo)
            rules = [v["rule"] for v in out]; msgs = [v["message"] for v in out]
            self.assertIn("persona-cast-role", rules)               # role missing
            self.assertTrue(any("Experience Goals" in m for m in msgs))  # held to standard
            self.assertTrue(any("Scenario" in m for m in msgs))

    def test_shipped_personas_are_well_formed(self):
        # pin the two shipped personas (Maya Primary + Trevor Negative) - a future edit must not break them
        repo_root = pathlib.Path(__file__).resolve().parents[5]
        src = repo_root / "sdlc-studio" / "personas"
        if not (src / "maya-okafor-founder-engineer.md").exists():
            self.skipTest("shipped personas not present")
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d); dd = repo / "sdlc-studio" / "personas"; dd.mkdir(parents=True)
            for f in src.glob("*.md"):
                (dd / f.name).write_text(f.read_text(encoding="utf-8"), encoding="utf-8")
            self.assertEqual(validate.check_personas(repo), [])

    def test_no_personas_dir_is_noop(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(validate.check_personas(pathlib.Path(d)), [])

    def test_index_md_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d)
            dd = repo / "sdlc-studio" / "personas"; dd.mkdir(parents=True)
            (dd / "index.md").write_text("# Index\n\nstuff\n", encoding="utf-8")
            self.assertEqual(validate.check_personas(repo), [])

    def test_consult_guide_and_readme_not_flagged(self):
        # BG0027: non-design-persona files in personas/ are not checked for the Cooper schema
        import tempfile, pathlib as _pl
        d = tempfile.mkdtemp(); pd = _pl.Path(d) / "sdlc-studio" / "personas"; pd.mkdir(parents=True)
        (pd / "consult-guide.md").write_text("# Consult guide\n\nrun consult team\n", encoding="utf-8")
        (pd / "README.md").write_text("# Personas\n\noverview\n", encoding="utf-8")
        self.assertEqual([f["file"] for f in validate.check_personas(_pl.Path(d))], [])

    def test_nested_only_personas_get_advisory_not_clean_pass(self):
        # BG0040: a project whose personas are nested (no flat design personas) must NOT read as a
        # clean pass - the flat glob finds nothing, so the check must say so, not pass vacuously.
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d)
            nested = repo / "sdlc-studio" / "personas" / "team"
            nested.mkdir(parents=True)
            body = ("# Maya\n\n## Quick Reference\n\n| Attribute | Value |\n| --- | --- |\n"
                    "| **Cast role** | Primary |\n\n## Who They Are\n\nx\n")
            (nested / "maya.md").write_text(body, encoding="utf-8")
            out = validate.check_personas(repo)
            rules = [v["rule"] for v in out]
            self.assertIn("persona-layout", rules)
            self.assertTrue(any("not validated" in v["message"] for v in out))

    def test_nested_count_reported_in_advisory(self):
        # the advisory names how many nested files were found (so the operator can act).
        # team/ is a genuinely-legacy nesting; seats/ and stakeholders/ are the generator's
        # canonical homes and are excluded from this advisory by design (CR0218).
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d)
            pdir = repo / "sdlc-studio" / "personas" / "team"
            pdir.mkdir(parents=True)
            (pdir / "a.md").write_text("# A\n\n## Who They Are\n\nx\n", encoding="utf-8")
            (pdir / "b.md").write_text("# B\n\n## Who They Are\n\nx\n", encoding="utf-8")
            out = validate.check_personas(repo)
            self.assertEqual(len(out), 1)
            self.assertEqual(out[0]["rule"], "persona-layout")
            self.assertIn("2", out[0]["message"])

    def test_seats_and_stakeholders_are_canonical_not_nested(self):
        # the generator's own output homes never trip the layout advisory (stakeholder
        # cards get their own schema warnings instead - a different rule family)
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d)
            for sub in ("seats", "stakeholders"):
                pdir = repo / "sdlc-studio" / "personas" / sub
                pdir.mkdir(parents=True)
                (pdir / "x.md").write_text("# X\n", encoding="utf-8")
            rules = {v["rule"] for v in validate.check_personas(repo)}
            self.assertNotIn("persona-layout", rules)

    def test_flat_personas_present_no_layout_advisory(self):
        # when flat design personas ARE found, nested files do not trigger the advisory
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d)
            self._persona(repo, "maya", "Primary", sections=self.STD)
            nested = repo / "sdlc-studio" / "personas" / "team"
            nested.mkdir(parents=True)
            (nested / "x.md").write_text("# X\n\n## Who They Are\n\nx\n", encoding="utf-8")
            rules = [v["rule"] for v in validate.check_personas(repo)]
            self.assertNotIn("persona-layout", rules)

    def test_seats_only_is_not_a_layout_advisory(self):
        # seats/ holds review-seat charters (a different schema), not nested design personas;
        # a personas/ dir with only seats/ is genuinely empty of personas, not a nested layout
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d)
            seats = repo / "sdlc-studio" / "personas" / "seats"
            seats.mkdir(parents=True)
            (seats / "engineer.md").write_text("# Engineer seat\n\ncharter\n", encoding="utf-8")
            self.assertEqual(validate.check_personas(repo), [])


class LegacyPersonasMdTests(unittest.TestCase):
    """The personas.md-only layout (the legacy flat file the story pipeline reads) must
    get a layout advisory plus a light structural check, never a vacuous clean pass."""

    POPULATED = ("# User Personas\n\nPersonas for this project.\n\n---\n\n"
                 "## Alex Dev\n\n**Role:** developer\n**Primary Goal:** ship\n\n"
                 "### Background\n\nA real background.\n")

    def _flat(self, repo, body):
        d = repo / "sdlc-studio"; d.mkdir(parents=True, exist_ok=True)
        (d / "personas.md").write_text(body, encoding="utf-8")

    def test_personas_md_only_emits_layout_advisory(self):
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d); self._flat(repo, self.POPULATED)
            found = validate.check_personas(repo)
            self.assertEqual([v["rule"] for v in found], ["persona-layout"])
            self.assertEqual(found[0]["severity"], "warning")
            self.assertIn("legacy", found[0]["message"])

    def test_boilerplate_personas_md_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d)
            self._flat(repo, "# User Personas\n\n## {{persona_name}}\n\n"
                             "**Role:** {{role}}\n")
            rules = [v["rule"] for v in validate.check_personas(repo)]
            self.assertIn("persona-legacy", rules)

    def test_empty_personas_md_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d); self._flat(repo, "# User Personas\n\nNothing yet.\n")
            found = [v for v in validate.check_personas(repo) if v["rule"] == "persona-legacy"]
            self.assertEqual(len(found), 1)
            self.assertIn("empty", found[0]["message"])

    def test_registry_present_no_legacy_advisory(self):
        # a registry with design cards is the checked source; personas.md alongside is not flagged
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d); self._flat(repo, self.POPULATED)
            pd = repo / "sdlc-studio" / "personas"; pd.mkdir(parents=True)
            body = ("# Maya\n\n## Quick Reference\n\n| Attribute | Value |\n| --- | --- |\n"
                    "| **Cast role** | Primary |\n\n")
            body += "".join(f"## {s}\n\nx\n\n" for s in PersonaWellFormedTests.STD)
            (pd / "maya.md").write_text(body, encoding="utf-8")
            self.assertEqual(validate.check_personas(repo), [])

    def test_seats_only_registry_falls_back_to_legacy_check(self):
        # personas/ holding only seats/ has no design cards - the story pipeline falls
        # back to personas.md, so the legacy advisory must still fire (LL0008)
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d); self._flat(repo, self.POPULATED)
            seats = repo / "sdlc-studio" / "personas" / "seats"; seats.mkdir(parents=True)
            (seats / "engineer.md").write_text("# Engineer seat\n\ncharter\n", encoding="utf-8")
            self.assertIn("persona-layout", [v["rule"] for v in validate.check_personas(repo)])

    def test_no_personas_anywhere_no_findings(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(validate.check_personas(pathlib.Path(d)), [])


class NotAnArtifactSweepTests(unittest.TestCase):
    """An id-named file the census excludes (no artifact header) must be NAMED,
    never silently invisible - the operator either fixes the header or declares
    the suffix as a companion. Warning severity: a declared companion is fine."""

    def _run(self, root):
        import argparse
        ns = argparse.Namespace(root=str(root), type=None, file=None, format="json")
        import contextlib, io, json as _json
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            validate.cmd_check(ns)
        return _json.loads(buf.getvalue())

    def test_off_template_artifact_named_as_warning(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "sdlc-studio/stories/US0001-login.md",
                   "# US0001 - Login\n\nStatus: Draft\n")   # off-template: excluded
            out = self._run(root)
            rules = [v["rule"] for v in out["violations"]]
            self.assertIn("not-an-artifact", rules)
            v = next(x for x in out["violations"] if x["rule"] == "not-an-artifact")
            self.assertEqual(v["severity"], "warning")
            self.assertIn("companion", v["message"])        # both remedies named

    def test_declared_companion_suffix_not_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "sdlc-studio/epics/EP0001-x.md",
                   "# EP0001: x\n\n> **Status:** Draft\n")
            _write(root, "sdlc-studio/epics/EP0001-x-consultations.md", "notes\n")
            out = self._run(root)
            self.assertEqual([v for v in out["violations"]
                              if v["rule"] == "not-an-artifact"], [])


class StructuredAuthorshipTests(unittest.TestCase):
    """US0060/CR0169: schema-v3 artefacts carry a typed, resolvable raised_by; v2 is exempt."""

    def _v3(self, root: Path) -> None:
        (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
        (root / "sdlc-studio" / ".config.yaml").write_text("schema_version: 3\n", encoding="utf-8")

    def _bug(self, root: Path, meta: str) -> Path:
        return _write(root, "sdlc-studio/bugs/BG0001-x.md",
                      f"# BG0001: x\n\n> **Status:** Open\n> **Severity:** Low\n{meta}\n")

    def test_v3_missing_authorship_fails(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self._v3(root)
            p = self._bug(root, "")
            rules = [v["rule"] for v in validate.validate_file(p, "bug", root)]
            self.assertIn("authorship-structured", rules)

    def test_v3_unresolvable_persona_fails(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self._v3(root)
            p = self._bug(root, "> **Raised-by:** Nobody Here; persona; v1")
            rules = [v["rule"] for v in validate.validate_file(p, "bug", root)]
            self.assertIn("authorship-unresolved", rules)

    def test_v3_resolvable_persona_passes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self._v3(root)
            pd = root / "sdlc-studio" / "personas"
            pd.mkdir(parents=True, exist_ok=True)
            (pd / "sam.md").write_text("# Sam Eriksson - QA amigo\n", encoding="utf-8")
            p = self._bug(root, "> **Raised-by:** Sam Eriksson; persona; v1")
            rules = [v["rule"] for v in validate.validate_file(p, "bug", root)]
            self.assertNotIn("authorship-structured", rules)
            self.assertNotIn("authorship-unresolved", rules)

    def test_v2_exempt(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)  # no .config.yaml -> v2
            p = self._bug(root, "")
            rules = [v["rule"] for v in validate.validate_file(p, "bug", root)]
            self.assertNotIn("authorship-structured", rules)


class SeparationOfDutiesTests(unittest.TestCase):
    """US0061/CR0170: a triager may not be the raiser (v3). Solo-human self-triage warns."""

    def _v3_persona(self, root: Path) -> None:
        (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
        (root / "sdlc-studio" / ".config.yaml").write_text("schema_version: 3\n", encoding="utf-8")
        pd = root / "sdlc-studio" / "personas"; pd.mkdir(parents=True, exist_ok=True)
        (pd / "sam.md").write_text("# Sam Eriksson - QA amigo\n", encoding="utf-8")
        (pd / "dani.md").write_text("# Dani Okafor - Engineering amigo\n", encoding="utf-8")

    def _bug(self, root: Path, raised: str, triaged: str) -> Path:
        return _write(root, "sdlc-studio/bugs/BG0001-x.md",
                      f"# BG0001: x\n\n> **Status:** Open\n> **Severity:** Low\n"
                      f"> **Raised-by:** {raised}\n> **Triaged-by:** {triaged}\n")

    def test_same_persona_raiser_and_triager_fails(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self._v3_persona(root)
            p = self._bug(root, "Sam Eriksson; persona; v1", "Sam Eriksson; persona; v1")
            errs = [v for v in validate.validate_file(p, "bug", root)
                    if v["rule"] == "duties-separated" and v["severity"] == "error"]
            self.assertTrue(errs)

    def test_distinct_personas_pass(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self._v3_persona(root)
            p = self._bug(root, "Sam Eriksson; persona; v1", "Dani Okafor; persona; v1")
            self.assertEqual([v for v in validate.validate_file(p, "bug", root)
                              if v["rule"] == "duties-separated"], [])

    def test_solo_human_self_triage_warns_not_errors(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self._v3_persona(root)
            p = self._bug(root, "Darren; human; v1", "Darren; human; v1")
            rows = [v for v in validate.validate_file(p, "bug", root) if v["rule"] == "duties-separated"]
            self.assertTrue(rows)
            self.assertTrue(all(v["severity"] == "warning" for v in rows))


class EvidenceSchemaTests(unittest.TestCase):
    """US0062/CR0171: v3 bugs need evidence; v3 CRs need impact + a size. v2 exempt.

    The size is `Points` on the modified Fibonacci scale. The retired `Effort` S/M/L still
    passes HERE, and only here: this is a read over artefacts already on disk, and turning
    every CR filed before the vocabulary changed into an error would report a fact about
    history rather than a defect anyone can fix. Nothing writes an Effort any more."""

    def _v3(self, root: Path) -> None:
        (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
        (root / "sdlc-studio" / ".config.yaml").write_text("schema_version: 3\n", encoding="utf-8")
        pd = root / "sdlc-studio" / "personas"; pd.mkdir(parents=True, exist_ok=True)
        (pd / "sam.md").write_text("# Sam Eriksson - QA\n", encoding="utf-8")

    _AUTH = "> **Raised-by:** Sam Eriksson; persona; v1\n"

    def test_bug_without_evidence_fails(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self._v3(root)
            p = _write(root, "sdlc-studio/bugs/BG0001-x.md",
                       f"# BG0001: x\n\n> **Status:** Open\n> **Severity:** Low\n{self._AUTH}\n"
                       "## Summary\n\nsomething is wrong\n")
            rules = [v["rule"] for v in validate.validate_file(p, "bug", root)]
            self.assertIn("evidence-present", rules)

    def test_bug_with_file_line_passes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self._v3(root)
            p = _write(root, "sdlc-studio/bugs/BG0001-x.md",
                       f"# BG0001: x\n\n> **Status:** Open\n> **Severity:** Low\n{self._AUTH}\n"
                       "## Evidence\n\n`scripts/foo.py:42` returns the wrong value\n")
            self.assertNotIn("evidence-present",
                             [v["rule"] for v in validate.validate_file(p, "bug", root)])

    def _cr(self, root: Path, tail: str) -> Path:
        return _write(root, "sdlc-studio/change-requests/CR0001-x.md",
                      f"# CR-0001: x\n\n> **Status:** Proposed\n> **Priority:** Low\n"
                      f"> **Type:** X\n{self._AUTH}\n{tail}")

    def test_cr_without_a_size_fails(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self._v3(root)
            p = self._cr(root, "## Impact\n\nusers are affected\n")
            self.assertIn("evidence-present",
                          [v["rule"] for v in validate.validate_file(p, "cr", root)])

    def test_cr_with_impact_and_points_passes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self._v3(root)
            p = self._cr(root, "## Impact\n\nusers are affected and blocked\n\n**Points:** 5\n")
            self.assertNotIn("evidence-present",
                             [v["rule"] for v in validate.validate_file(p, "cr", root)])

    def test_a_cr_sized_off_the_scale_is_not_sized_at_all(self) -> None:
        # A 7 is not a size the tool will write, and it is not one it will accept as a size on
        # read either - otherwise a hand-edited artefact re-admits the precision the scale exists
        # to refuse, and the validator becomes the hole in the gate.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self._v3(root)
            p = self._cr(root, "## Impact\n\nusers are affected and blocked\n\n**Points:** 7\n")
            self.assertIn("evidence-present",
                          [v["rule"] for v in validate.validate_file(p, "cr", root)])

    def test_a_legacy_effort_cr_already_on_disk_still_passes(self) -> None:
        # The backlog carries hundreds of these. They are re-estimated by a planning pass, not
        # by a validator turning red on history nobody can change.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self._v3(root)
            p = self._cr(root, "## Impact\n\nusers are affected and blocked\n\n"
                               "## Effort\n\n**M.** moderate\n")
            self.assertNotIn("evidence-present",
                             [v["rule"] for v in validate.validate_file(p, "cr", root)])

    def test_v2_bug_exempt(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)  # v2
            p = _write(root, "sdlc-studio/bugs/BG0001-x.md",
                       "# BG0001: x\n\n> **Status:** Open\n> **Severity:** Low\n\n## Summary\n\nx\n")
            self.assertNotIn("evidence-present",
                             [v["rule"] for v in validate.validate_file(p, "bug", root)])


def _v3_cr(root: Path, tranche_line: str = "") -> Path:
    """A schema-v3 repo with one CR; `tranche_line` is an optional `> **Tranche:** ...` line."""
    (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
    (root / "sdlc-studio" / ".config.yaml").write_text("schema_version: 3\n", encoding="utf-8")
    body = f"# CR-0001: c\n\n> **Status:** Proposed\n{tranche_line}\n## Summary\n\ns\n"
    return _write(root, "sdlc-studio/change-requests/CR0001-c.md", body)


class TrancheShapeTests(unittest.TestCase):
    """US0068 AC1: a record-only tranche reference - absent or valued is fine; present-but-empty
    is a malformed record. Era-gated to schema v3."""

    def _rules(self, p: Path, root: Path) -> set:
        return {v["rule"] for v in validate.validate_file(p, "cr", root)}

    def test_tranche_shape_empty_value_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = _v3_cr(root, "> **Tranche:**\n")
            self.assertIn("tranche-shape", self._rules(p, root))

    def test_tranche_shape_whitespace_value_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = _v3_cr(root, "> **Tranche:**    \n")
            self.assertIn("tranche-shape", self._rules(p, root))

    def test_tranche_shape_present_value_ok(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = _v3_cr(root, "> **Tranche:** sprint-12\n")
            self.assertNotIn("tranche-shape", self._rules(p, root))

    def test_tranche_shape_absent_ok(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = _v3_cr(root, "")
            self.assertNotIn("tranche-shape", self._rules(p, root))

    def test_tranche_shape_dormant_under_v2(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)  # v2: no .config.yaml
            p = _write(root, "sdlc-studio/change-requests/CR0001-c.md",
                       "# CR-0001: c\n\n> **Status:** Proposed\n> **Tranche:**\n\n## Summary\n\ns\n")
            self.assertNotIn("tranche-shape",
                             {v["rule"] for v in validate.validate_file(p, "cr", root)})


class UlidIdFormatTests(unittest.TestCase):
    """US0112/CR0198: validate must accept a v3 ULID id (BG-01JQK3F8), not flag it id-format."""

    def test_v3_ulid_id_not_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = _write(Path(d), "sdlc-studio/bugs/BG-01JQK3F8-x.md",
                       "# BG-01JQK3F8: x\n\n> **Status:** Open\n> **Severity:** Low\n")
            rules = {v["rule"] for v in validate.validate_file(p, "bug")}
            self.assertNotIn("id-format", rules)

    def test_v2_sequential_still_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = _write(Path(d), "sdlc-studio/bugs/BG0001-x.md",
                       "# BG0001: x\n\n> **Status:** Open\n> **Severity:** Low\n")
            rules = {v["rule"] for v in validate.validate_file(p, "bug")}
            self.assertNotIn("id-format", rules)

    def test_garbage_id_still_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = _write(Path(d), "sdlc-studio/bugs/notanid-x.md",
                       "# x\n\n> **Status:** Open\n")
            rules = {v["rule"] for v in validate.validate_file(p, "bug")}
            self.assertIn("id-format", rules)

class ServesCoverageTests(unittest.TestCase):
    """Persona-tagged requirements coverage - DORMANT until the project carries >=1
    Serves: tag or opts in via config; advisory, never gated."""

    def _repo(self, d, *, stories=(), personas=(), config=""):
        repo = pathlib.Path(d)
        sdir = repo / "sdlc-studio" / "stories"; sdir.mkdir(parents=True)
        for i, (name, body) in enumerate(stories):
            (sdir / name).write_text(body, encoding="utf-8")
        pdir = repo / "sdlc-studio" / "personas"; pdir.mkdir(parents=True, exist_ok=True)
        for name, h1 in personas:
            (pdir / name).write_text(f"# {h1}\n\n## Who They Are\n\nx\n", encoding="utf-8")
        if config:
            (repo / "sdlc-studio" / ".config.yaml").write_text(config, encoding="utf-8")
        return repo

    STORY = "# US0001: x\n\n> **Status:** Draft\n> **Serves:** Maya Chen\n\n## Acceptance Criteria\n\n- **AC1:** x\n"

    def test_dormant_with_no_tags_and_no_opt_in(self):
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d, stories=[("US0001-x.md", self.STORY.replace(
                "> **Serves:** Maya Chen\n", ""))])
            res = validate.check_serves(repo)
            self.assertFalse(res["active"])
            self.assertEqual(res["findings"], [])

    def test_one_tag_activates_and_resolves(self):
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d, stories=[("US0001-x.md", self.STORY)],
                              personas=[("maya-chen.md", "Maya Chen - Dispatcher")])
            res = validate.check_serves(repo)
            self.assertTrue(res["active"])
            self.assertEqual(res["findings"], [])
            self.assertEqual(res["coverage"].get("maya-chen.md"), 1)

    def test_case_variants_never_fragment_coverage(self):
        # coverage keys on the resolved file, not the tag's raw spelling
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d, stories=[
                ("US0001-x.md", self.STORY),
                ("US0002-y.md", self.STORY.replace("US0001", "US0002").replace(
                    "Maya Chen", "MAYA CHEN"))],
                personas=[("maya-chen.md", "Maya Chen - Dispatcher")])
            res = validate.check_serves(repo)
            self.assertEqual(res["coverage"], {"maya-chen.md": 2})

    def test_fenced_code_block_never_activates(self):
        # a story QUOTING the convention in a code block must not activate the check
        with tempfile.TemporaryDirectory() as d:
            quoted = ("# US0001: x\n\n> **Status:** Draft\n\n"
                      "```markdown\n**Serves:** Nobody Real\n```\n\n"
                      "## Acceptance Criteria\n\n- **AC1:** x\n")
            repo = self._repo(d, stories=[("US0001-x.md", quoted)])
            self.assertFalse(validate.check_serves(repo)["active"])

    def test_unresolved_persona_name_is_flagged(self):
        # Sam's blocking condition: a named persona MUST resolve to a persona file -
        # a tag pointing nowhere is worse than no tag (it reads as covered)
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d, stories=[("US0001-x.md", self.STORY)])
            rules = {v["rule"] for v in validate.check_serves(repo)["findings"]}
            self.assertIn("serves-unresolved", rules)

    def test_config_opt_in_activates_without_tags(self):
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d, stories=[("US0001-x.md", self.STORY.replace(
                "> **Serves:** Maya Chen\n", ""))],
                config="serves_coverage: true\n")
            res = validate.check_serves(repo)
            self.assertTrue(res["active"])
            rules = {v["rule"] for v in res["findings"]}
            self.assertIn("serves-nobody", rules)

    def test_advisory_only_never_errors(self):
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d, stories=[("US0001-x.md", self.STORY)])
            sev = {v["severity"] for v in validate.check_serves(repo)["findings"]}
            self.assertLessEqual(sev, {"warning"})


class SeatCheckTests(unittest.TestCase):
    """The error-level generation floor: role declared+allowed, review render present,
    demographic denylist clean, one card per role, cast capped at 5."""

    GOOD = ("<!-- role: qa -->\n# Priya - QA seat\n\n## Lens\n\nx\n"
            "## Pushes Back When\n\nx\n## Shadow\n\nx\n")

    def _seat(self, root: Path, name: str, body: str) -> None:
        d = root / "sdlc-studio" / "personas" / "seats"
        d.mkdir(parents=True, exist_ok=True)
        (d / name).write_text(body, encoding="utf-8")

    def _rules(self, root: Path) -> set:
        return {v["rule"] for v in validate.check_seats(root)}

    def test_good_seat_is_clean(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self._seat(Path(d), "priya.md", self.GOOD)
            errs = [v for v in validate.check_seats(Path(d)) if v["severity"] == "error"]
            self.assertEqual(errs, [])

    def test_missing_role_and_render_are_errors(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self._seat(Path(d), "bad.md", "# Someone\n\n## Who They Are\n\nx\n")
            rules = self._rules(Path(d))
            self.assertIn("seat-no-role", rules)
            self.assertIn("seat-no-review-render", rules)

    def test_duplicate_role_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self._seat(Path(d), "a.md", self.GOOD)
            self._seat(Path(d), "b.md", self.GOOD)
            self.assertIn("seat-duplicate-role", self._rules(Path(d)))

    def test_demographic_fluff_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self._seat(Path(d), "p.md", self.GOOD.replace(
                "# Priya - QA seat", "# Priya - QA seat\n\n34 years old, married"))
            self.assertIn("seat-demographic-fluff", self._rules(Path(d)))

    def test_cast_over_five_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            roles = ["engineering", "qa", "product", "security", "sre", "data"]
            for i, r in enumerate(roles):
                self._seat(Path(d), f"s{i}.md", self.GOOD.replace("role: qa", f"role: {r}"))
            self.assertIn("seat-cast-size", self._rules(Path(d)))

    def test_require_stamp_flags_an_unstamped_named_card(self) -> None:
        # The critic's defect: AC3 promises "provenance stamp present on generated cards"
        # but nothing enforced it. The flow names the files it just wrote; each must carry
        # a valid generation stamp or reviewed marker.
        with tempfile.TemporaryDirectory() as d:
            self._seat(Path(d), "priya.md", self.GOOD)
            card = Path(d) / "sdlc-studio" / "personas" / "seats" / "priya.md"
            rules = {v["rule"] for v in validate.check_seats(Path(d), require_stamp=[card])}
            self.assertIn("seat-no-stamp", rules)

    def test_require_stamp_accepts_stamped_and_reviewed_cards(self) -> None:
        stamp = ("<!-- provenance: generated provisional-unverified "
                 "hash=sha256:0123456789abcdef -->\n")
        reviewed = "<!-- provenance: reviewed 2026-07-10 -->\n"
        for marker in (stamp, reviewed):
            with tempfile.TemporaryDirectory() as d:
                self._seat(Path(d), "priya.md",
                           self.GOOD.replace("<!-- role: qa -->\n",
                                             "<!-- role: qa -->\n" + marker))
                card = Path(d) / "sdlc-studio" / "personas" / "seats" / "priya.md"
                errs = [v for v in validate.check_seats(Path(d), require_stamp=[card])
                        if v["severity"] == "error"]
                self.assertEqual(errs, [])

    def test_malformed_stamp_is_always_an_error(self) -> None:
        # A line that claims to be a provenance comment but parses as neither the
        # generation stamp nor the reviewed marker would silently classify as authored -
        # dropping out of the provisional advisory with no signal.
        with tempfile.TemporaryDirectory() as d:
            self._seat(Path(d), "priya.md",
                       self.GOOD.replace(
                           "<!-- role: qa -->\n",
                           "<!-- role: qa -->\n<!-- provenance: generated "
                           "provisional-unverified hash=sha256:ABCDEF -->\n"))
            self.assertIn("seat-malformed-stamp", self._rules(Path(d)))

    def test_require_stamp_covers_stakeholder_cards(self) -> None:
        # The stakeholder flow reuses the same gate: a named stakeholders/ card is
        # stamp-verified (not schema-checked as a seat), so --stakeholders shares the
        # loud floor instead of growing a parallel one.
        stamp = ("<!-- provenance: generated provisional-unverified "
                 "hash=sha256:0123456789abcdef -->\n")
        with tempfile.TemporaryDirectory() as d:
            self._seat(Path(d), "priya.md", self.GOOD)
            sdir = Path(d) / "sdlc-studio" / "personas" / "stakeholders"
            sdir.mkdir(parents=True)
            (sdir / "omar.md").write_text("# Omar - buyer\n", encoding="utf-8")
            rules = {v["rule"] for v in validate.check_seats(
                Path(d), require_stamp=[sdir / "omar.md"])}
            self.assertIn("seat-no-stamp", rules)
            self.assertNotIn("seat-require-miss", rules)
            (sdir / "omar.md").write_text(stamp + "# Omar - buyer\n", encoding="utf-8")
            errs = [v for v in validate.check_seats(Path(d),
                                                    require_stamp=[sdir / "omar.md"])
                    if v["severity"] == "error"]
            self.assertEqual(errs, [])

    def test_malformed_stamp_on_a_stakeholder_card_is_an_error(self) -> None:
        # Same failure mode as seats: a mangled provenance line silently classifies as
        # authored and drops from the provisional advisory - caught here even with no
        # --require-stamp (post-gate mangling has an owner).
        with tempfile.TemporaryDirectory() as d:
            self._seat(Path(d), "priya.md", self.GOOD)
            sdir = Path(d) / "sdlc-studio" / "personas" / "stakeholders"
            sdir.mkdir(parents=True)
            (sdir / "omar.md").write_text(
                "<!-- provenance: generated provisional-unverified hash=sha256:ABCDEF -->\n"
                "# Omar - buyer\n", encoding="utf-8")
            self.assertIn("seat-malformed-stamp", self._rules(Path(d)))

    def test_require_stamp_fails_loudly_on_an_unmatched_path(self) -> None:
        # The critic's round-2 defect: a guard must fail loudly on input it cannot
        # verify, never vacuously pass. A typo'd, relative-from-elsewhere, or
        # outside-seats/ required path matches no scanned card and MUST error.
        with tempfile.TemporaryDirectory() as d:
            self._seat(Path(d), "priya.md", self.GOOD.replace(
                "<!-- role: qa -->\n",
                "<!-- role: qa -->\n<!-- provenance: reviewed 2026-07-10 -->\n"))
            seats = Path(d) / "sdlc-studio" / "personas" / "seats"
            for bad in (seats / "pirya.md",                       # typo
                        Path("sdlc-studio/personas/seats/priya.md"),  # cwd-relative
                        Path(d) / "sdlc-studio" / "personas" / "stakeholders" / "omar.md"):
                rules = {v["rule"]
                         for v in validate.check_seats(Path(d), require_stamp=[bad])}
                self.assertIn("seat-require-miss", rules, msg=str(bad))

    def test_cli_require_stamp(self) -> None:
        import contextlib, io
        with tempfile.TemporaryDirectory() as d:
            self._seat(Path(d), "priya.md", self.GOOD)
            card = str(Path(d) / "sdlc-studio" / "personas" / "seats" / "priya.md")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(
                    validate.main(["seats", "--root", d, "--require-stamp", card]), 1)

    def test_cli_exits_1_on_errors_0_clean(self) -> None:
        import contextlib, io
        with tempfile.TemporaryDirectory() as d:
            self._seat(Path(d), "bad.md", "# no role\n")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(validate.main(["seats", "--root", d]), 1)
        with tempfile.TemporaryDirectory() as d:
            self._seat(Path(d), "priya.md", self.GOOD)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(validate.main(["seats", "--root", d]), 0)


def _rfc(status: str, rows: str, override: str = "") -> str:
    head = f"# RFC0001: r\n\n> **Status:** {status}\n"
    if override:
        head += f"> **Decision-Override:** {override}\n"
    return (head + "\n## Summary\n\nx\n\n## Open Decisions\n\n"
            "| # | Decision | Status |\n| --- | --- | --- |\n" + rows)


class AcceptedRfcOpenDecisionTests(unittest.TestCase):
    """US0244 AC3: the transition gate cannot reach files that predate it.

    Six RFCs were already Accepted carrying nothing but the boilerplate Open row. A gate
    on the transition alone would leave every one of them untouched and still call the
    workspace clean, so the standing check has to cover the state as well as the change.
    """

    def test_accepted_rfc_with_an_open_decision_is_a_violation(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = _write(Path(d), "sdlc-studio/rfcs/RFC0001-r.md",
                       _rfc("Accepted", "| D1 | act or not | Open |\n"))
            out = validate.validate_file(p, "rfc")
            hits = [v for v in out if v["rule"] == "accepted-open-decision"]
            self.assertTrue(hits, out)
            self.assertIn("D1", hits[0]["message"])
            self.assertEqual(hits[0]["severity"], "error")

    def test_every_open_row_is_named(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = _write(Path(d), "sdlc-studio/rfcs/RFC0001-r.md",
                       _rfc("Accepted",
                            "| D1 | a | Open |\n| D2 | b | Closed |\n| D3 | c | Open |\n"))
            msg = [v for v in validate.validate_file(p, "rfc")
                   if v["rule"] == "accepted-open-decision"][0]["message"]
            self.assertIn("D1", msg)
            self.assertIn("D3", msg)
            self.assertNotIn("D2", msg)

    def test_accepted_rfc_with_all_rows_closed_is_clean(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = _write(Path(d), "sdlc-studio/rfcs/RFC0001-r.md",
                       _rfc("Accepted", "| D1 | settled | Closed |\n"))
            self.assertEqual(
                [v for v in validate.validate_file(p, "rfc")
                 if v["rule"] == "accepted-open-decision"], [])

    def test_a_non_terminal_rfc_with_an_open_row_is_not_flagged(self) -> None:
        """An Open decision on an In Review RFC is the normal state, not a defect."""
        with tempfile.TemporaryDirectory() as d:
            p = _write(Path(d), "sdlc-studio/rfcs/RFC0001-r.md",
                       _rfc("In Review", "| D1 | still deciding | Open |\n"))
            self.assertEqual(
                [v for v in validate.validate_file(p, "rfc")
                 if v["rule"] == "accepted-open-decision"], [])

    def test_a_recorded_override_downgrades_it_to_a_warning(self) -> None:
        """The transition's sanctioned skip must not read as a permanent error here."""
        with tempfile.TemporaryDirectory() as d:
            p = _write(Path(d), "sdlc-studio/rfcs/RFC0001-r.md",
                       _rfc("Accepted", "| D1 | a | Open |\n", override="settled at review"))
            hits = [v for v in validate.validate_file(p, "rfc")
                    if v["rule"] == "accepted-open-decision"]
            self.assertTrue(hits)
            self.assertEqual(hits[0]["severity"], "warning")


_BAD_STATUS_STORY = ("# Bad\n\n> **Status:** Bananas\n\n### AC1: x\n"
                     "- **Verify:** file a.py\n")


class DiffScopedCheckTests(unittest.TestCase):
    """US0354 AC1: `check --changed` judges only the artefacts in the diff, while the repo-wide
    sweeps (`excluded_id_files`, `check_dor_dod`) keep running over the whole tree. An untouched
    error is PRINTED as advisory - a scope that swallowed it would be worse than a slow check.

    Real git repos throughout: the behaviour under test is "what changed".
    """

    def _repo(self, t) -> Path:
        root = Path(t)
        _write(root, "sdlc-studio/stories/US0001-good.md", GOOD_STORY)
        _write(root, "sdlc-studio/stories/US0002-bad.md", _BAD_STATUS_STORY)
        # id-named, no artifact header: the whole-tree census must still report it
        _write(root, "sdlc-studio/stories/US0009-notes.md", "plain notes\n")
        gitutil.git(["init", "-q"], cwd=root)
        gitutil.git(["add", "-A"], cwd=root)
        gitutil.git(["commit", "-qm", "baseline"], cwd=root)
        return root

    def _json(self, root: Path, *extra: str):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = validate.main(["check", "--root", str(root), "--format", "json", *extra])
        return rc, json.loads(buf.getvalue())

    def _text(self, root: Path, *extra: str) -> str:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            validate.main(["check", "--root", str(root), *extra])
        return buf.getvalue()

    @staticmethod
    def _facts(data: dict, name: str):
        return sorted((v["rule"], v["severity"]) for v in data["violations"]
                      if v["file"].endswith(name))

    def test_untouched_error_is_advisory_while_global_sweeps_still_run(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = self._repo(t)
            p = root / "sdlc-studio" / "stories" / "US0001-good.md"
            p.write_text(GOOD_STORY + "\n<!-- edited -->\n", encoding="utf-8")

            rc, data = self._json(root, "--changed")
            self.assertEqual(rc, 0)                                # the diff is clean
            self.assertEqual(data["summary"]["errors"], 0)
            self.assertEqual(data["summary"]["advisory_errors"], 1)

            bad = [v for v in data["violations"] if v["file"].endswith("US0002-bad.md")]
            self.assertEqual([v["rule"] for v in bad if v["severity"] == "error"],
                             ["status-vocab"])
            # EVERY finding on the untouched file is marked, not just the counted ones ...
            self.assertTrue(all(v["scoped_out"] for v in bad))
            # ... and the severity is the FACT and does not move; only the counting does
            self.assertEqual([v["severity"] for v in bad if v["rule"] == "status-vocab"],
                             ["error"])

            # the whole-tree census still ran over the untouched tree
            self.assertTrue(any(v["rule"] == "not-an-artifact" for v in data["violations"]))

            # the untouched error is PRINTED, marked advisory, not swallowed
            out = self._text(root, "--changed")
            self.assertIn("US0002-bad.md", out)
            self.assertIn("ADVISORY", out)

            # the scoped run and the full run AGREE on the file both judged ...
            rc_full, full = self._json(root)
            self.assertEqual(self._facts(data, "US0001-good.md"),
                             self._facts(full, "US0001-good.md"))
            # ... and the full run charges the untouched error, so the scope is what moved it
            self.assertEqual(rc_full, 1)
            self.assertEqual(full["summary"]["errors"], 1)

            # the DoR/DoD sweep is NOT scoped away: an unresolvable check tag still fails
            _write(root, "sdlc-studio/definition-of-ready.md",
                   "- a criterion [check: no-such-check]\n")
            rc2, data2 = self._json(root, "--changed")
            self.assertEqual(rc2, 1)
            self.assertTrue(any(v["rule"] == "unknown-check-id" for v in data2["violations"]))

    def test_a_degraded_probe_judges_the_whole_workspace(self) -> None:
        """No git, no diff: unknown must mean judge EVERYTHING. A scope derived from an
        unanswered probe would be an empty scope wearing a green exit code."""
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)                                  # deliberately NOT a git repo
            _write(root, "sdlc-studio/stories/US0001-good.md", GOOD_STORY)
            _write(root, "sdlc-studio/stories/US0002-bad.md", _BAD_STATUS_STORY)
            rc, data = self._json(root, "--changed")
            self.assertEqual(rc, 1)
            self.assertEqual(data["summary"]["errors"], 1)
            self.assertEqual(data["summary"]["advisory_errors"], 0)
            self.assertTrue(data["scope"]["degraded"])
            self.assertFalse(any(v.get("scoped_out") for v in data["violations"]))




class PlaceholderBaselineTests(unittest.TestCase):
    """The widened body sweep records pre-existing findings so it does not block on the backlog it
    revealed. Every case here must DIE if the waiver is removed or made unconditional - the first
    version of these tests passed with the feature patched out, which is the defect this project
    files under vacuous verifiers."""

    def _story(self, repo, sid, token="{{what changes and why}}", status="Done"):
        d = repo / "sdlc-studio" / "stories"
        d.mkdir(parents=True, exist_ok=True)
        p = d / f"{sid}-x.md"
        p.write_text(f"# {sid}: x\n\n> **Status:** {status}\n\n## Summary\n\n{token}\n",
                     encoding="utf-8")
        return p

    def _sev(self, path, repo):
        validate._baseline_cache.clear()
        return [f["severity"] for f in validate.validate_file(path, "story", repo_root=repo)
                if f.get("rule") == "placeholder"]

    def _baseline(self, repo, *entries):
        (repo / "sdlc-studio").mkdir(parents=True, exist_ok=True)
        (repo / "sdlc-studio" / ".placeholder-baseline.txt").write_text(
            "\n".join(entries) + "\n", encoding="utf-8")

    def test_a_baselined_finding_is_downgraded_to_a_warning(self):
        """Dies if the waiver is removed: without it this is an error."""
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            self._baseline(repo, "US9999:{{what changes and why}}")
            sev = self._sev(self._story(repo, "US9999"), repo)
            self.assertEqual(sev, ["warning"],
                             "a recorded pre-existing finding must not block; got %r" % sev)

    def test_a_different_token_in_a_baselined_artefact_still_errors(self):
        """The waiver is per FINDING. Dies if it is keyed on the artefact instead."""
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            self._baseline(repo, "US9999:{{what changes and why}}")
            sev = self._sev(self._story(repo, "US9999", token="{{a brand new blank}}"), repo)
            self.assertIn("error", sev,
                          "a NEW blank in an already-listed record must still error - otherwise "
                          "listing an artefact waives it for ever")

    def test_an_artefact_absent_from_the_baseline_errors(self):
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            self._baseline(repo, "US9998:{{what changes and why}}")
            self.assertIn("error", self._sev(self._story(repo, "US9999"), repo))

    def test_an_absent_baseline_file_quietens_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            (repo / "sdlc-studio").mkdir(parents=True, exist_ok=True)
            self.assertIn("error", self._sev(self._story(repo, "US9999"), repo))

    def test_one_root_s_baseline_does_not_leak_into_another(self):
        """Dies if the cache is a bare module global keyed on nothing."""
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            ra, rb = Path(a), Path(b)
            self._baseline(ra, "US9999:{{what changes and why}}")
            (rb / "sdlc-studio").mkdir(parents=True, exist_ok=True)   # no baseline at all
            pa, pb = self._story(ra, "US9999"), self._story(rb, "US9999")
            validate._baseline_cache.clear()
            sa = [f["severity"] for f in validate.validate_file(pa, "story", repo_root=ra)
                  if f.get("rule") == "placeholder"]
            sb = [f["severity"] for f in validate.validate_file(pb, "story", repo_root=rb)
                  if f.get("rule") == "placeholder"]   # same id, different root, no clear()
            self.assertEqual(sa, ["warning"])
            self.assertIn("error", sb, "the first root's baseline leaked into the second")

    def test_a_non_terminal_artefact_is_unaffected_by_the_baseline(self):
        """The waiver only applies where the body sweep errors, which is at terminal status."""
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            self._baseline(repo, "US9999:{{what changes and why}}")
            sev = self._sev(self._story(repo, "US9999", status="Draft"), repo)
            self.assertNotIn("error", sev)

    def test_repo_root_none_does_not_crash_the_checker(self):
        """Path(None) raised TypeError past an OSError-only handler."""
        with tempfile.TemporaryDirectory() as d:
            p = self._story(Path(d), "US9999")
            validate._baseline_cache.clear()
            validate.validate_file(p, "story")   # no repo_root at all


class PlaceholderFenceTests(unittest.TestCase):
    """The body sweep tracked fences with the naive toggle the same commit replaced in the
    acceptance-criteria parser. Restoring the toggle survived the whole 4,300-test suite, so the
    repair was correct and unpinned. It fails in BOTH directions: a false positive inside the
    fence, and a real placeholder MISSED after it."""

    def _body(self, repo, body):
        d = repo / "sdlc-studio" / "stories"
        d.mkdir(parents=True, exist_ok=True)
        p = d / "US9999-x.md"
        p.write_text(f"# US9999: x\n\n> **Status:** Done\n\n## Summary\n\n{body}\n",
                     encoding="utf-8")
        return p

    def _findings(self, path, repo):
        validate._baseline_cache.clear()
        return [f["message"] for f in validate.validate_file(path, "story", repo_root=repo)
                if f.get("rule") == "placeholder"]

    def test_a_placeholder_inside_a_fence_is_not_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            body = "```\nexample:\n```markdown\n{{not a real slot}}\n```\n"
            self.assertEqual(self._findings(self._body(repo, body), repo), [],
                             "sample text inside a fenced block is an illustration, not a slot")

    def test_a_real_placeholder_after_the_fence_is_still_found(self):
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            body = "```\nexample:\n```markdown\n{{illustration}}\n```\n\n{{a real blank}}\n"
            found = self._findings(self._body(repo, body), repo)
            self.assertTrue(any("a real blank" in f for f in found),
                            "the naive toggle left the fence state inverted and MISSED this")
            self.assertFalse(any("illustration" in f for f in found))


class PartialCapabilityTests(unittest.TestCase):
    """US0513: a unit that ships half a capability may say so, and saying so is only an
    answer when it names the unit that ships the other half.

    The declaration is read from an EXPLICIT place - the `> **Partial:**` metadata line or a
    `## Scope note` section (the shape US0507 established at review) - never from prose that
    happens to contain the words. CR0461, EP0178 and US0513 itself all discuss `consumer-only`
    in their acceptance criteria; a phrase sweep over the whole body would refuse every one of
    them, which is the lint-fires-on-the-text-describing-the-lint trap.
    """

    HEAD = "# {sid}: x\n\n> **Status:** {status}\n{extra}\n### AC1: y\n- **Verify:** file a.py\n"

    def _unit(self, root, *, extra="", body="", sid="US9990", status="Done"):
        return _write(root, f"sdlc-studio/stories/{sid}-x.md",
                      self.HEAD.format(sid=sid, status=status, extra=extra) + body)

    def _rules(self, path, root):
        return [f["rule"] for f in validate.validate_file(path, "story", repo_root=root)]

    def test_a_declared_partial_capability_is_accepted(self):
        """Both declaration shapes pass when the follow-up is named."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            meta = self._unit(root, sid="US9990",
                              extra="> **Partial:** consumer-only; follow-up BG0357\n")
            self.assertEqual([r for r in self._rules(meta, root) if r.startswith("partial")], [],
                             "a declaration that names its follow-up is a recorded gap, not a defect")

            note = self._unit(root, sid="US9991", body=(
                "\n## Scope note (added at review)\n\n"
                "**This unit ships the CONSUMER only.** The producer half is filed as BG0357.\n"))
            self.assertEqual([r for r in self._rules(note, root) if r.startswith("partial")], [],
                             "the scope-note shape US0507 established must pass too")

    def test_a_partial_capability_must_name_its_follow_up(self):
        """No follow-up named -> refused. An acknowledged gap nobody owns is the same as an
        unacknowledged one."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            meta = self._unit(root, sid="US9992", extra="> **Partial:** consumer-only\n")
            self.assertIn("partial-no-followup", self._rules(meta, root))

            note = self._unit(root, sid="US9993", body=(
                "\n## Scope note\n\n**This unit ships the producer only.** The consumer is "
                "not built yet.\n"))
            self.assertIn("partial-no-followup", self._rules(note, root))

            # the unit's OWN id is not a follow-up - it names nobody else
            own = self._unit(root, sid="US9994",
                             extra="> **Partial:** producer-only; see US9994\n")
            self.assertIn("partial-no-followup", self._rules(own, root))

            # and a `Partial:` value naming neither half is refused rather than read as
            # "no declaration", which would silently exempt the unit
            odd = self._unit(root, sid="US9995", extra="> **Partial:** half of it; BG0357\n")
            self.assertIn("partial-scope", self._rules(odd, root))

    def test_prose_discussing_the_rule_is_not_a_declaration(self):
        """CR0461/EP0178/US0513 quote the phrase in their criteria. A body sweep would refuse
        every artefact that describes this rule."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = self._unit(root, sid="US9996", body=(
                "\n## Notes\n\nA unit whose mechanism has no caller states that as "
                "consumer-only or producer-only.\n"))
            self.assertEqual([r for r in self._rules(p, root) if r.startswith("partial")], [])


class BugCriteriaTests(unittest.TestCase):
    """US0514/US0515: a bug reaching a terminal status with no acceptance criteria is refused,
    as a story reaching Done already is - and the corpus that already breaks the rule is
    baselined from the checker's OWN output so the new rule blocks a new instance without
    blocking on the backlog it reveals.
    """

    def _bug(self, root, bid="BG9990", status="Fixed", ac=""):
        return _write(root, f"sdlc-studio/bugs/{bid}-x.md",
                      f"# {bid}: x\n\n> **Status:** {status}\n\n## Summary\n\nsomething broke "
                      f"at a.py:12\n{ac}")

    def _findings(self, path, root, rule="no-ac"):
        validate._baseline_cache.clear()
        return [f for f in validate.validate_file(path, "bug", repo_root=root)
                if f["rule"] == rule]

    def _baseline(self, root, *entries):
        (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
        (root / "sdlc-studio" / validate._CRITERIA_BASELINE.split("/")[-1]).write_text(
            "\n".join(entries) + "\n", encoding="utf-8")

    # --- US0514 ---------------------------------------------------------------------------
    def test_a_terminal_bug_with_no_criteria_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            found = self._findings(self._bug(root), root)
            self.assertEqual([f["severity"] for f in found], ["error"],
                             "a bug at a terminal status with no criteria must be refused")
            self.assertIn("acceptance criteria", found[0]["message"])

            # ... and a bug that carries criteria is not
            ok = self._bug(root, "BG9991", ac="\n## Acceptance Criteria\n\n- the crash is gone\n")
            self.assertEqual(self._findings(ok, root), [])

            # ... and a bug still in flight is not: the criteria are owed at the terminal
            # status, which is where the record starts speaking for shipped code
            live = self._bug(root, "BG9992", status="Open")
            self.assertEqual(self._findings(live, root), [])

    def test_the_terminal_set_is_derived_not_enumerated(self):
        """A project whose bug vocabulary gains a terminal status is covered with no edit here.
        Dies if the checker enumerates Fixed/Verified/Closed instead of asking the vocabulary."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            novel = self._bug(root, "BG9993", status="Retired")
            self.assertEqual(self._findings(novel, root), [],
                             "precondition: Retired is not a bug status yet")
            vocab = sdlc_md.STATUS_VOCAB["bug"]
            terminal = sdlc_md.TERMINAL_STATUS["bug"]
            sdlc_md.STATUS_VOCAB["bug"] = [*vocab, "Retired"]
            sdlc_md.TERMINAL_STATUS["bug"] = {*terminal, "Retired"}
            try:
                found = self._findings(novel, root)
            finally:
                sdlc_md.STATUS_VOCAB["bug"] = vocab
                sdlc_md.TERMINAL_STATUS["bug"] = terminal
            self.assertEqual([f["severity"] for f in found], ["error"],
                             "the rule must follow the type's own terminal set")

    # --- US0515 ---------------------------------------------------------------------------
    def test_a_baselined_unit_reports_as_debt(self):
        """The record is CAPTURED from the checker's own output, not hand-written: the emitter
        and the reader are pinned to each other here, so a format drift fails this test rather
        than silently quietening nothing."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._bug(root, "BG9990")
            self._bug(root, "BG9991")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = validate.main(["check", "--root", str(root), "--type", "bug",
                                    "--emit-baseline"])
            self.assertEqual(rc, 0, "emitting the baseline is a report, not a verdict")
            emitted = buf.getvalue()
            self.assertIn("BG9990", emitted)
            self.assertIn("BG9991", emitted)

            (root / "sdlc-studio" / validate._CRITERIA_BASELINE.split("/")[-1]).write_text(
                emitted, encoding="utf-8")
            found = self._findings(root / "sdlc-studio/bugs/BG9990-x.md", root)
            self.assertEqual([f["severity"] for f in found], ["warning"],
                             "a recorded pre-existing instance is known debt, not a block")
            self.assertIn("baseline", found[0]["message"])

            # and the run as a whole now passes: the rule does not block on the backlog it revealed
            validate._baseline_cache.clear()
            buf2 = io.StringIO()
            with contextlib.redirect_stdout(buf2):
                rc2 = validate.main(["check", "--root", str(root), "--type", "bug"])
            self.assertEqual(rc2, 0, buf2.getvalue())

    def test_a_new_instance_still_fails(self):
        """Not in the baseline -> error. And removal is one-way: an id taken out errors from
        then on, so the recorded count can only fall."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._baseline(root, "BG9990")
            listed = self._bug(root, "BG9990")
            fresh = self._bug(root, "BG9994")
            self.assertEqual([f["severity"] for f in self._findings(listed, root)], ["warning"])
            self.assertEqual([f["severity"] for f in self._findings(fresh, root)], ["error"],
                             "a NEW criteria-less unit must still be refused")

            self._baseline(root, "# nothing left")     # the id removed from the record
            self.assertEqual([f["severity"] for f in self._findings(listed, root)], ["error"],
                             "removal is one-way - the check errors on it from then on")

    def test_an_absent_baseline_quietens_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
            self.assertEqual([f["severity"] for f in self._findings(self._bug(root), root)],
                             ["error"])


class ScopedCheckTests(unittest.TestCase):
    """US0527: validate can be pointed at one artefact, and a scoped run SAYS it was scoped.
    US0528: the contradicted-`Affects` warning fires where a missing file is a real signal.
    """

    def _workspace(self, root):
        _write(root, "sdlc-studio/stories/US0001-good.md", GOOD_STORY)
        _write(root, "sdlc-studio/stories/US0002-bad.md",
               "# X\n\n> **Status:** Frozen\n\n### AC1: y\n- **Verify:** file b\n")
        _write(root, "sdlc-studio/stories/US0009-notes.md", "plain notes\n")  # census bait
        _write(root, "sdlc-studio/definition-of-ready.md",
               "- a criterion [check: no-such-check]\n")                      # DoR bait
        return root / "sdlc-studio" / "stories" / "US0001-good.md"

    def _json(self, root, *extra):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = validate.main(["check", "--root", str(root), "--format", "json", *extra])
        return rc, json.loads(buf.getvalue())

    def _text(self, root, *extra):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            validate.main(["check", "--root", str(root), *extra])
        return buf.getvalue()

    # --- US0527 ---------------------------------------------------------------------------
    def test_a_single_artefact_can_be_checked(self):
        """Points at one artefact in a workspace of many: its findings, and only what reading
        it required. The read COUNT is asserted, not just the output - a scope that still swept
        the tree and filtered the report afterwards would pass an output-only test."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            one = self._workspace(root)
            real = validate.validate_file
            read: list[str] = []

            def counting(path, type_, repo_root=None):
                read.append(Path(path).name)
                return real(path, type_, repo_root)

            validate.validate_file = counting
            try:
                rc, data = self._json(root, "--file", str(one))
            finally:
                validate.validate_file = real

            self.assertEqual(read, ["US0001-good.md"], "the whole workspace was read")
            self.assertEqual(data["checked"], 1)
            self.assertEqual(rc, 0)
            self.assertEqual({v["file"] for v in data["violations"]} - {str(one)}, set(),
                             "only the named artefact's findings belong in a scoped report")
            self.assertFalse(any(v["rule"] == "unknown-check-id" for v in data["violations"]),
                             "the DoR sweep is not this artefact's business")

    def test_a_scoped_run_states_its_scope(self):
        """'no findings here' and 'no findings anywhere' are different claims. A clean scoped
        run that does not say what it covered is read as the second."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            one = self._workspace(root)
            out = self._text(root, "--file", str(one))
            self.assertIn("scope:", out)
            self.assertIn("US0001-good.md", out)
            self.assertNotIn("US0002-bad.md", out)      # genuinely scoped, not merely narrated
            _, data = self._json(root, "--file", str(one))
            self.assertEqual(data["scope"]["file"], str(one))
            self.assertEqual(data["scope"]["judged"], 1)

            # the unscoped run makes the wider claim and does NOT carry the narrower one
            full = self._text(root)
            self.assertNotIn("scope:", full)

    # --- US0528 ---------------------------------------------------------------------------
    def _affects(self, root, sid, status, path):
        return _write(root, f"sdlc-studio/stories/{sid}-x.md",
                      f"# {sid}: x\n\n> **Status:** {status}\n> **Affects:** {path}\n\n"
                      f"### AC1: y\n- **Verify:** file {path}\n")

    def _rules(self, path, root):
        return [f["rule"] for f in validate.validate_file(path, "story", repo_root=root)]

    def test_a_draft_declaring_a_new_file_is_not_warned(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = self._affects(root, "US9970", "Draft", "src/not_written_yet.py")
            self.assertNotIn("affects-unresolvable", self._rules(p, root),
                             "declaring what you will create is the normal case for new work")

    def test_a_terminal_unit_with_a_missing_path_is_still_warned(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = self._affects(root, "US9971", "Done", "src/never_existed.py")
            self.assertIn("affects-unresolvable", self._rules(p, root),
                          "at a terminal status the file should exist and its absence is real")
            # and the file existing clears it, so the warning tracks the tree, not the status
            _write(root, "src/never_existed.py", "x = 1\n")
            self.assertNotIn("affects-unresolvable", self._rules(p, root))


class VerifierAuthorityAgreementTests(unittest.TestCase):
    """BG0356. The validator called a bug's command-shaped `Verify:` "executed by nothing"
    while `verify_ac` was about to execute it, so an author was told opposite things about
    one line and a fixed bug had no agreed closure path. One rule held in two places
    diverges, and the looser copy is the one that runs."""

    LINE = "- **Verify:** pytest tests/test_thing.py::Thing::test_it\n"

    def _artefact(self, root: Path, type_: str, ident: str) -> Path:
        d = root / "sdlc-studio" / {"bug": "bugs", "cr": "change-requests"}[type_]
        d.mkdir(parents=True, exist_ok=True)
        p = d / f"{ident}-x.md"
        p.write_text(f"# {ident}: a thing\n\n> **Status:** Open\n\n"
                     f"## Acceptance Criteria\n\n- [ ] it works\n{self.LINE}",
                     encoding="utf-8")
        return p

    def _pseudo(self, path: Path, type_: str, root: Path) -> list:
        return [v for v in validate.validate_file(path, type_, root)
                if v["rule"] == "pseudo-verify"]

    def test_a_bug_s_verify_line_is_not_reported_as_executed_by_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = self._artefact(root, "bug", "BG0001")
            self.assertEqual(self._pseudo(p, "bug", root), [],
                             "the runner executes a bug's verifiers; the validator must agree")

    def test_a_request_s_verify_line_still_is(self) -> None:
        """The carve-out is a bug/story rule, not the deletion of the warning. A CR is
        decomposed rather than delivered, so a command on one gates nothing."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = self._artefact(root, "cr", "CR0001")
            self.assertTrue(self._pseudo(p, "cr", root))

    def test_the_three_sites_read_one_authority(self) -> None:
        """The runner, the validator's warning and the creators' refusal each decided this
        independently. They now read `sdlc_md.executes_verifiers`, and this asserts the
        AGREEMENT rather than three separate expected answers - so a future edit to one
        cannot pass while the others disagree."""
        import file_finding
        import verify_ac
        for type_, prefix in (("story", "US"), ("bug", "BG"), ("cr", "CR"), ("rfc", "RFC")):
            executes = sdlc_md.executes_verifiers(type_)
            with self.subTest(type=type_):
                # the runner walks exactly the executing types
                self.assertEqual(prefix in verify_ac.VERIFIABLE_PREFIXES, executes)
                # the creators refuse a command-shaped Verify on exactly the others
                refused = False
                try:
                    file_finding.check_prose_acs(
                        type_, {"acs": ["it works\n  - **Verify:** pytest a.py::B::c"]})
                except Exception:  # noqa: BLE001 - the refusal type is the filer's business
                    refused = True
                if type_ in sdlc_md.FINDING_TYPES:
                    self.assertEqual(refused, not executes)


class OpenQuestionsTests(unittest.TestCase):
    """US0465. Sixteen artefacts reached a terminal status still asking questions nobody had
    answered, and every one read as settled work. The rule is one helper in `lib/sdlc_md.py`,
    called by BOTH `validate` and the transition gate, because two readings of one rule is two
    rules and the looser one wins."""

    def _story(self, root, status, body):
        d = root / "sdlc-studio" / "stories"
        d.mkdir(parents=True, exist_ok=True)
        p = d / "US0001-x.md"
        p.write_text(f"# US0001: x\n\n> **Status:** {status}\n\n"
                     f"## Acceptance Criteria\n\n- [ ] something\n\n{body}", encoding="utf-8")
        return p

    #: Type -> (directory, id) for the non-story types whose terminal status is not `Done`.
    _TYPES = {"bug": ("bugs", "BG0001"), "cr": ("change-requests", "CR0001")}

    def _artifact(self, root, type_, status, body):
        """A minimal artefact of `type_`, so the gate can be driven for a type whose terminal
        status is not Done. Returns its id."""
        folder, uid = self._TYPES[type_]
        d = root / "sdlc-studio" / folder
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{uid}-x.md").write_text(
            f"# {uid}: x\n\n> **Status:** {status}\n\n"
            f"## Acceptance Criteria\n\n- [ ] something\n\n{body}", encoding="utf-8")
        return uid

    def _transition(self, transition, root, uid, status):
        """Drive the real transition command. Returns (moved, combined output)."""
        import contextlib
        import io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            try:
                rc = transition.main(["--root", str(root), "set", uid, status])
            except SystemExit as exc:  # argparse-style exit is still a refusal
                rc = exc.code if isinstance(exc.code, int) else 1
        return rc == 0, buf.getvalue()

    def test_a_terminal_artefact_with_unchecked_questions_is_flagged(self) -> None:
        from lib import sdlc_md
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        p = self._story(root, "Done",
                        "## Open Questions\n\n- [ ] should we do X?\n- [ ] and Y?\n")
        items = sdlc_md.unresolved_questions(p.read_text(encoding="utf-8"), root)
        self.assertEqual(2, len(items), f"the items themselves were not reported: {items}")
        self.assertIn("should we do X?", items[0],
                      "the finding quotes no question text - it reports a heading, not an item")
        # ...and a clean story passes, so the finding is the ITEM and not the heading.
        p2 = self._story(root, "Done", "## Open Questions\n\n- [x] X, ruled by D0001\n")
        self.assertEqual([], sdlc_md.unresolved_questions(p2.read_text(encoding="utf-8"), root))

    def test_a_none_placeholder_is_not_a_question(self) -> None:
        """`- [ ] None - behaviour fully extracted from scripts/x.py` is the template saying
        there ARE none. Reading it as unanswered flagged nine already-correct artefacts, which
        is a guard manufacturing work."""
        from lib import sdlc_md
        for wording in ("None", "None - behaviour fully extracted from `scripts/x.py`", "n/a"):
            self.assertEqual([], sdlc_md.unresolved_questions(
                f"## Open Questions\n\n- [ ] {wording}\n", None), f"flagged: {wording!r}")

    def test_an_unfilled_template_placeholder_is_not_a_question(self) -> None:
        """`- [ ] {{question}}` is an unfilled template, and validate's placeholder rule already
        owns it. Reporting it here double-reports it and refuses a transition for the wrong
        reason, naming two routes out that neither apply. Found by the full suite, not by a
        mutant: a scaffolded epic fixture reddened three directories away."""
        from lib import sdlc_md
        self.assertEqual([], sdlc_md.unresolved_questions(
            "## Open Questions\n\n- [ ] {{question}} - Owner: {{question_owner}}\n", None))

    def test_a_ruling_on_the_item_resolves_it(self) -> None:
        """A ruling recorded ON the item is the same fact as one moved under a heading.
        Demanding the heading would be demanding a layout, not an answer."""
        from lib import sdlc_md
        for wording in ("Ruled by D0052: the seed lands in apply()",
                        "Settled in the build: each finding cites a heading",
                        "Resolved by delivery: the flag is read at plan time"):
            self.assertEqual([], sdlc_md.unresolved_questions(
                f"## Open Questions\n\n- [x] {wording}\n", None), f"flagged: {wording!r}")

    def test_a_tick_with_no_destination_is_refused(self) -> None:
        """The escape hatch cannot be a tick pointing at nothing - that is how a question stops
        being visible without being answered."""
        from lib import sdlc_md
        items = sdlc_md.unresolved_questions("## Open Questions\n\n- [x] should we do X?\n", None)
        self.assertEqual(1, len(items))
        self.assertIn("no ruling and no follow-up id", items[0])

    def test_validate_and_the_gate_agree_across_every_type_and_terminal_status(self) -> None:
        """ONE helper, so the two callers cannot disagree. Every type in the terminal-status map,
        in each of its terminal statuses - a CR reaching Superseded is held like a story
        reaching Done, because the status set is DERIVED from the map."""
        from lib import sdlc_md
        body = "## Open Questions\n\n- [ ] unanswered\n"
        checked = 0
        for type_, statuses in sdlc_md.TERMINAL_STATUS.items():
            for status in statuses:
                self.assertTrue(sdlc_md.is_terminal_status(type_, status),
                                f"{type_}/{status} is not read as terminal by its own map")
                self.assertEqual(["unanswered"], sdlc_md.unresolved_questions(body, None),
                                 f"the helper answered differently for {type_}/{status}")
                checked += 1
        self.assertGreater(checked, 8, "the map yielded almost nothing to check")

    def test_a_heading_with_a_suffix_still_hides_nothing(self) -> None:
        """BG0450, escape 1. `^#+\\s*Open Questions\\s*$` anchored the heading to end-of-line,
        so `## Open Questions (deferred)` was a different heading and the whole section went
        unscanned. One token of author edit turned the gate off, and the artefact read CLEAN
        rather than refused - which is the direction that matters."""
        from lib import sdlc_md
        text = ("# US0001: x\n\n> **Status:** Done\n\n"
                "## Open Questions (deferred)\n\n- [ ] should the retry budget be per-run?\n")
        items = sdlc_md.unresolved_questions(text, None)
        self.assertEqual(["should the retry budget be per-run?"], items,
                         "a suffix on the heading hid the section from the detector")

    def test_a_second_open_questions_section_is_scanned_too(self) -> None:
        """BG0450, escape 2. `search` reads ONE section. An artefact whose first section is
        fully resolved and whose second carries the live question passed the gate, because the
        second was never read. Independently found by the QA seat with a positive control."""
        from lib import sdlc_md
        text = ("# US0001: x\n\n> **Status:** Done\n\n"
                "## Open Questions\n\n- [x] settled - ruled by D0001\n\n"
                "## Notes\n\nprose\n\n"
                "## Open Questions\n\n- [ ] should the census rewrite archived indexes?\n")
        items = sdlc_md.unresolved_questions(text, None)
        self.assertEqual(["should the census rewrite archived indexes?"], items,
                         "only the first Open Questions section was scanned")

    def test_a_tick_citing_only_itself_is_not_a_follow_up(self) -> None:
        """BG0450, escape 3. `find_by_id` proves an id RESOLVES, and an artefact always
        resolves to itself, so self-citation satisfied the follow-up route in full - the exact
        'tick pointing at nothing' the docstring promises cannot happen. The control matters as
        much as the case: citing a DIFFERENT artefact must still be accepted, or this fix has
        merely broken the escape hatch."""
        from lib import sdlc_md
        head = "# US0001: x\n\n> **Status:** Done\n\n## Open Questions\n\n"
        items = sdlc_md.unresolved_questions(head + "- [x] deferred? See US0001.\n", None)
        self.assertEqual(1, len(items), "an artefact citing itself passed as resolved")
        self.assertIn("citing only itself", items[0])
        self.assertEqual([], sdlc_md.unresolved_questions(
            head + "- [x] deferred, filed as BG0450\n", None),
            "a genuine follow-up elsewhere was refused - the escape hatch is broken")

    def test_the_GATE_refuses_every_terminal_status_not_only_Done(self) -> None:
        """What the test above only appears to prove, and the mutant it could not catch.

        Its loop body is `unresolved_questions(body, None)` - arguments that depend on neither
        `type_` nor `status` - so it is ONE call repeated two dozen times, and it never invokes
        the gate. Reducing the gate to `target_canon == "Done"` therefore survived all 5489
        tests while being a live CLI escape: a bug reached Fixed and a CR reached Superseded
        carrying unanswered questions, which is the one thing this story's title forbids.

        So drive the gate itself, for a type whose terminal status is NOT Done.
        """
        from lib import sdlc_md
        import transition
        for type_, status, other in (("bug", "Fixed", "Open"),
                                     ("cr", "Superseded", "Proposed")):
            with self.subTest(type_=type_, status=status):
                self.assertTrue(sdlc_md.is_terminal_status(type_, status))
                self.assertNotEqual(status, "Done",
                                    "this test is pointless unless the status is not Done")
                td = tempfile.TemporaryDirectory()
                self.addCleanup(td.cleanup)
                root = Path(td.name)
                uid = self._artifact(root, type_, other,
                                     "## Open Questions\n\n- [ ] should we do X?\n")
                ok, msg = self._transition(transition, root, uid, status)
                self.assertFalse(ok, f"{type_} reached {status} carrying an open question")
                self.assertIn("should we do X?", msg,
                              "the refusal does not quote the question that caused it")

    def test_validate_ITSELF_reports_the_finding_not_only_the_helper(self) -> None:
        """Through `validate`, because the sibling tests call the helper directly and so
        survived a mutant that removed validate's reporting entirely. A rule nothing invokes
        is a rule nothing enforces."""
        import contextlib
        import io
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        self._story(root, "Done", "## Open Questions\n\n- [ ] should we do X?\n")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            validate.main(["--root", str(root), "check"])
        out = buf.getvalue()
        self.assertIn("open-question", out,
                      f"validate did not report the finding at all:\n{out}")
        self.assertIn("should we do X?", out, "the reported finding quotes no question text")

    def test_no_terminal_artefact_in_the_workspace_carries_an_unresolved_question(self) -> None:
        """The sweep, over the REAL workspace, with the directories derived from the type map
        rather than a list of filenames - so an offender in a type nobody thought about is
        still caught."""
        from lib import sdlc_md
        repo = Path(__file__).resolve().parents[5]
        offenders = {}
        swept = 0
        for type_ in sdlc_md.TERMINAL_STATUS:
            entry = sdlc_md.ARTIFACT_TYPES.get(type_)
            if not entry:
                continue
            for path in (repo / entry[0]).glob("*.md"):
                if path.name.startswith("_"):
                    continue
                text = path.read_text(encoding="utf-8")
                status = (sdlc_md.extract_field(text, "Status") or "").strip()
                if not sdlc_md.is_terminal_status(type_, status):
                    continue
                swept += 1
                items = sdlc_md.unresolved_questions(text, repo)
                if items:
                    offenders[path.name] = items
        self.assertGreater(swept, 100, "the sweep read almost nothing - it proves nothing")
        self.assertEqual({}, offenders,
                         f"terminal artefacts still carry unresolved questions: "
                         f"{sorted(offenders)}")
        # POSITIVE CONTROL. Without it a clean sweep is equally consistent with a detector that
        # scans nothing, and it was: `return offending` -> `return []` and a heading regex
        # changed to `Open Queries` BOTH survived this test. `swept` counts terminal ARTEFACTS,
        # not questions found, so it cannot tell the two apart. Plant an offender in each of
        # the three escape shapes and require the detector to find every one.
        planted = {
            "a plain unchecked question": "## Open Questions\n\n- [ ] planted, unanswered?\n",
            "a heading carrying a suffix":
                "## Open Questions (deferred)\n\n- [ ] planted, unanswered?\n",
            "a SECOND Open Questions section":
                "## Open Questions\n\n- [x] answered - ruled by D0001\n\n## Notes\n\ntext\n\n"
                "## Open Questions\n\n- [ ] planted, unanswered?\n",
            "a tick citing only the artefact itself":
                "## Open Questions\n\n- [x] planted? See US0001.\n",
        }
        for label, body in planted.items():
            with self.subTest(shape=label):
                text = f"# US0001: x\n\n> **Status:** Done\n\n{body}"
                self.assertTrue(sdlc_md.unresolved_questions(text, repo),
                                f"the sweep is blind to {label} - a clean corpus proves nothing")


class FreshArtefactPlaceholderTests(unittest.TestCase):
    """A freshly-minted artefact's criteria scaffold is not-yet-written, not an error.

    A Draft story's placeholder was a WARNING while a freshly-minted CR's was an ERROR - so
    `artifact.py new --type cr`, the path the docs call recommended, produced an artefact that
    blocked the very next commit, and the author had to hand-edit what the tool had just
    written. That is the hand-authoring the deterministic path exists to avoid, induced by it.
    """

    def _artefact(self, root, folder, name, body):
        d = root / "sdlc-studio" / folder
        d.mkdir(parents=True, exist_ok=True)
        (d / name).write_text(body, encoding="utf-8")

    def test_the_warning_is_printed_by_the_shipped_command(self) -> None:
        """MUTANT: make the NOT FINISHED print unreachable.

        Driven through `artifact.py new` and asserted on its OUTPUT. AC3's first verifier was
        `grep -q "NOT FINISHED" artifact.py`, which a dead branch satisfies: making the
        condition `if False:` left the grep at exit 0 and 145 tests green. A grep over source
        text is not a test of what the source does.
        """
        import importlib.util, io, contextlib, sys  # noqa: PLC0415
        spec = importlib.util.spec_from_file_location(
            "artifact", Path(__file__).resolve().parent.parent / "artifact.py")
        artifact = importlib.util.module_from_spec(spec)
        sys.modules["artifact"] = artifact
        spec.loader.exec_module(artifact)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / "change-requests").mkdir(parents=True)
            (root / "src").mkdir()
            (root / "src" / "a.py").write_text("x = 1\n", encoding="utf-8")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
                rc = artifact.main(["new", "--type", "cr", "--title", "a fresh request",
                                    "--summary", "a summary", "--impact", "an impact",
                                    "--priority", "High", "--size", "S",
                                    "--affects", "src/a.py", "--root", str(root)])
            out = buf.getvalue()
        self.assertEqual(0, rc, f"artifact.py new did not run:\n{out}")
        self.assertIn("NOT FINISHED", out,
                      "the shipped command reported plain success over an artefact whose "
                      "criteria are still the scaffold placeholder")

    def test_a_fresh_request_placeholder_is_a_warning(self) -> None:
        """MUTANT: restore the story-only condition.

        A CR at its opening status is 'not written yet' for exactly the same reason a Draft
        story is.
        """
        mod = validate
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._artefact(root, "change-requests", "CR0001-x.md",
                           "# CR-0001: a request\n\n> **Status:** Proposed\n"
                           "> **Priority:** High\n> **Type:** Improvement\n"
                           "> **Size:** S\n> **Affects:** src/a.py\n\n"
                           "## Summary\n\ns\n\n## Impact\n\ni\n\n"
                           "## Acceptance Criteria\n\n- [ ] {{criterion}}\n")
            findings = mod.validate_file(
                root / "sdlc-studio" / "change-requests" / "CR0001-x.md", "cr", root)
        errors = [f for f in findings
                  if f.get("severity") == mod.SEVERITY_ERROR and "placeholder" in str(f)]
        self.assertEqual([], errors,
                         f"a freshly-minted request's scaffold placeholder errored: {errors}")

    def test_a_request_past_its_opening_status_still_errors(self) -> None:
        """The positive control. MUTANT: warn on every placeholder regardless of status.

        Once a request is being acted on, an unfilled criterion is real debt - and a rule that
        never errors is not a rule.
        """
        mod = validate
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._artefact(root, "change-requests", "CR0002-y.md",
                           "# CR-0002: a request\n\n> **Status:** In Progress\n"
                           "> **Priority:** High\n> **Type:** Improvement\n"
                           "> **Size:** S\n> **Affects:** src/a.py\n\n"
                           "## Summary\n\ns\n\n## Impact\n\ni\n\n"
                           "## Acceptance Criteria\n\n- [ ] {{criterion}}\n")
            findings = mod.validate_file(
                root / "sdlc-studio" / "change-requests" / "CR0002-y.md", "cr", root)
        errors = [f for f in findings
                  if f.get("severity") == mod.SEVERITY_ERROR and "placeholder" in str(f)]
        self.assertTrue(errors,
                        "a request past its opening status kept an unfilled criterion without "
                        "erroring")


class RepeatedFieldTests(unittest.TestCase):
    """BG0506. `extract_field` matches with `re.search`, so a repeated `> **Name:** value` line
    is read FIRST-WINS, and `transition._set_field` substitutes with `count=1`, so a correction
    rewrites the first and leaves the rest standing. Nothing refused the shape: a fixture with
    two `Verification depth` lines validated with `errors=0`, while the transition gate read one
    of them and a human read the other.

    `Parent` is plural BY DESIGN - a shared batch epic delivers more than one request - so the
    rule needs a DECLARED exempt set rather than a blanket no-duplicates.

    MUTANTS:
      1. drop the `PLURAL_FIELDS` skip -> multi-parent epics become errors.
      2. scan the whole file instead of stopping at the first `##` -> body prose reads as
         metadata.
      3. drop the rule entirely -> the two-depth fixture passes again.
    """

    def _art(self, d: Path, name: str, body: str) -> Path:
        p = d / "sdlc-studio" / "change-requests" / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
        return p

    def test_a_repeated_single_valued_field_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = self._art(root, "CR9001-x.md",
                          "# CR-9001: x\n\n> **Status:** Complete\n"
                          "> **Verification depth:** smoke\n"
                          "> **Verification depth:** soak\n\n## Summary\n\nx\n")
            found = validate.validate_file(p, "cr")
            hits = [f for f in found if f["rule"] == "repeated-field"]
            self.assertEqual(len(hits), 1, found)
            self.assertEqual(hits[0]["severity"], "error")
            self.assertIn("Verification depth", hits[0]["message"])
            self.assertIn("4", hits[0]["message"])
            self.assertIn("5", hits[0]["message"])

    def test_the_plural_set_is_declared_and_exempts_multi_parent_epics(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            parents = "".join(f"> **Parent:** CR{n:04d}\n" for n in range(1, 13))
            p = self._art(root, "CR9002-x.md",
                          f"# CR-9002: x\n\n> **Status:** Complete\n{parents}\n## Summary\n\nx\n")
            hits = [f for f in validate.validate_file(p, "cr") if f["rule"] == "repeated-field"]
            self.assertEqual(hits, [], "a plural field was flagged")
        self.assertIn(sdlc_md.PARENT_FIELD, sdlc_md.PLURAL_FIELDS)
        self.assertNotIn("Verification depth", sdlc_md.PLURAL_FIELDS)

    def test_a_repeated_shape_in_the_BODY_is_prose_not_metadata(self) -> None:
        """The metadata block ends at the first `##`. A `**Field:**` shape quoted in the body -
        a template excerpt, a worked example - is prose, and flagging it would make documenting
        the rule an error."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = self._art(root, "CR9003-x.md",
                          "# CR-9003: x\n\n> **Status:** Complete\n\n## Summary\n\n"
                          "**Points:** 3\n\n**Points:** 5\n")
            hits = [f for f in validate.validate_file(p, "cr") if f["rule"] == "repeated-field"]
            self.assertEqual(hits, [], "body prose was read as metadata")

    def test_the_live_corpus_holds_no_repeated_single_valued_field(self) -> None:
        """AC3. The guard landing and the debt being paid are proven separately: this asserts
        the CORPUS is clean, which the fixture tests above cannot see."""
        repo = Path(__file__).resolve().parents[4]
        hits = []
        for sub, type_ in (("change-requests", "cr"), ("bugs", "bug"), ("stories", "story"),
                           ("epics", "epic"), ("rfcs", "rfc")):
            for f in sorted((repo / "sdlc-studio" / sub).glob("*.md")):
                if f.name.startswith("_"):
                    continue
                hits += [(f.name, x["message"]) for x in validate.validate_file(f, type_)
                         if x["rule"] == "repeated-field"]
        self.assertEqual(hits, [], f"{len(hits)} repeated single-valued field(s) in the corpus")


if __name__ == "__main__":
    unittest.main()
