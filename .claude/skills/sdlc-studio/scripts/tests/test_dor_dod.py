"""DoR/DoD documents + check-id registry (RED first).

The two editable documents are the single source of the project's ready and done
bars; an enforceable criterion carries a [check: <id>] tag resolving through ONE
registered vocabulary. An unknown id is a loud validation error - a tag nothing
enforces would be human intent silently unenforced.
"""
from __future__ import annotations

import contextlib
import io
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import loader  # noqa: E402

SCRIPTS = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
from lib import sdlc_md  # noqa: E402

TEMPLATES = SCRIPTS.parent / "templates" / "core"


class RegistryTests(unittest.TestCase):
    """One authority module holds the check-id vocabulary; the shipped templates
    tag only registered ids and cover every level."""

    def test_registry_lives_in_one_authority_module(self):
        reg = sdlc_md.DOR_DOD_CHECK_IDS
        self.assertIsInstance(reg, dict)
        self.assertGreaterEqual(len(reg), 8)
        for cid, desc in reg.items():
            self.assertRegex(cid, r"^[a-z0-9]+(\.[a-z0-9-]+)+$")
            self.assertTrue(desc.strip(), f"{cid} has no description")

    def test_registry_names_the_existing_gates(self):
        # The bar maps to checks that EXIST - grooming, verify-ac, critic, close, release.
        for expected in ("grooming.affects", "grooming.points", "story.verify-ac",
                         "review.critic-approve", "close.retro", "release.gate"):
            self.assertIn(expected, sdlc_md.DOR_DOD_CHECK_IDS)

    def test_check_tags_parse(self):
        text = ("- [ ] Affects declared [check: grooming.affects]\n"
                "- [ ] judged by a human, untagged\n"
                "- [ ] ACs pass [check: story.verify-ac]\n")
        self.assertEqual(sdlc_md.check_tags(text),
                         ["grooming.affects", "story.verify-ac"])

    def test_shipped_templates_exist_tag_registered_ids_and_cover_levels(self):
        for name in ("definition-of-ready.md", "definition-of-done.md"):
            path = TEMPLATES / name
            self.assertTrue(path.is_file(), f"{name} not shipped")
            text = path.read_text(encoding="utf-8")
            tags = sdlc_md.check_tags(text)
            self.assertGreaterEqual(len(tags), 3, f"{name} has too few enforceable criteria")
            self.assertEqual(sdlc_md.unknown_check_ids(text), [],
                             f"{name} tags an unregistered id")
            for level in ("Story", "Sprint", "Release"):
                self.assertIn(f"## {level}", text, f"{name} missing the {level} level")

    def test_templates_state_the_never_weaken_rule(self):
        for name in ("definition-of-ready.md", "definition-of-done.md"):
            text = (TEMPLATES / name).read_text(encoding="utf-8")
            self.assertIn("never weaken the bar", text)


class UnknownCheckIdTests(unittest.TestCase):
    """An unknown check id is a loud validation error, never silently unenforced."""

    def test_unknown_ids_are_listed(self):
        text = ("- [ ] real [check: grooming.affects]\n"
                "- [ ] typo [check: groomin.affects]\n"
                "- [ ] invented [check: vibes.good]\n")
        self.assertEqual(sdlc_md.unknown_check_ids(text),
                         ["groomin.affects", "vibes.good"])

    def test_validate_flags_unknown_id_in_project_document(self):
        validate = loader.load_script("validate")
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            (root / "sdlc-studio").mkdir(parents=True)
            (root / "sdlc-studio" / "definition-of-done.md").write_text(
                "# Definition of Done\n\n## Story\n\n"
                "- [ ] ACs pass [check: story.verify-ac]\n"
                "- [ ] good vibes [check: vibes.good]\n", encoding="utf-8")
            args = validate.build_parser().parse_args(["check", "--root", str(root)])
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = args.func(args)
            self.assertEqual(rc, 1)   # loud: the run FAILS
            self.assertIn("vibes.good", out.getvalue())
            self.assertIn("ERROR", out.getvalue())

    def test_validate_passes_registered_only_document(self):
        validate = loader.load_script("validate")
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            (root / "sdlc-studio").mkdir(parents=True)
            (root / "sdlc-studio" / "definition-of-ready.md").write_text(
                "# Definition of Ready\n\n## Story\n\n"
                "- [ ] Affects declared [check: grooming.affects]\n"
                "- [ ] a human-judged criterion, untagged\n", encoding="utf-8")
            args = validate.build_parser().parse_args(["check", "--root", str(root)])
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(args.func(args), 0)

    def test_untagged_criteria_are_not_errors(self):
        # Untagged = explicitly human-judged; only a BAD tag errors.
        self.assertEqual(sdlc_md.unknown_check_ids("- [ ] judged by the operator\n"), [])


class CheckTagNearMissTests(unittest.TestCase):
    """BG0185: a mis-cased/mis-spaced check tag must ERROR loudly, never parse as no-tag.

    A tag the strict parser silently ignores is a criterion the DoR/DoD bar no longer enforces -
    exactly the silent-control class the tag registry exists to close.
    """

    def test_near_miss_is_detected(self):
        # wrong case, wrong spacing, and a missing colon - none parse strictly.
        for token, text in (
            ("[Check: grooming.affects]", "- [ ] x [Check: grooming.affects]\n"),
            ("[check:GROOMING]", "- [ ] x [check:GROOMING]\n"),
            ("[ check: grooming.affects ]", "- [ ] x [ check: grooming.affects ]\n"),
            ("[check grooming.affects]", "- [ ] x [check grooming.affects]\n"),
        ):
            self.assertIn(token, sdlc_md.check_tag_near_misses(text))
            self.assertEqual(sdlc_md.check_tags(text), [])   # strict parser sees nothing

    def test_valid_tag_is_not_a_near_miss(self):
        text = "- [ ] x [check: grooming.affects]\n- [ ] y [check: story.verify-ac]\n"
        self.assertEqual(sdlc_md.check_tag_near_misses(text), [])

    def test_unrelated_bracket_word_is_not_a_near_miss(self):
        # "checkpoint" shares a prefix but is not the tag word - no false positive.
        self.assertEqual(
            sdlc_md.check_tag_near_misses("- [ ] see [checkpoint: 3] later\n"), [])

    def test_validate_flags_a_near_miss_tag(self):
        validate = loader.load_script("validate")
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            (root / "sdlc-studio").mkdir(parents=True)
            (root / "sdlc-studio" / "definition-of-done.md").write_text(
                "# Definition of Done\n\n## Story\n\n"
                "- [ ] ACs pass [Check: story.verify-ac]\n", encoding="utf-8")
            args = validate.build_parser().parse_args(["check", "--root", str(root)])
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = args.func(args)
            self.assertEqual(rc, 1)                      # loud: the run FAILS
            self.assertIn("ERROR", out.getvalue())
            self.assertIn("[Check: story.verify-ac]", out.getvalue())


def _write_doc(root: pathlib.Path, kind: str, body: str) -> None:
    (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
    (root / "sdlc-studio" / f"definition-of-{kind}.md").write_text(body, encoding="utf-8")


def _grooming_unit(root: pathlib.Path, *, points: bool) -> list[dict]:
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    (root / "real.py").write_text("x = 1\n", encoding="utf-8")
    body = ("# US0001: sample\n\n> **Status:** Ready\n> **Epic:** EP0001\n"
            "> **Affects:** real.py\n")
    if points:
        body += "> **Points:** 3\n"
    body += "\n## Acceptance Criteria\n\n### AC1: works\n- **Verify:** shell echo ok\n"
    p = d / "US0001-sample.md"
    p.write_text(body, encoding="utf-8")
    return [{"id": "US0001", "type": "story", "path": str(p)}]


class GateResolveTests(unittest.TestCase):
    """RFC0043 slice 2: each gate resolves its level's tagged criteria from the
    project documents; absent documents keep today's behaviour byte-for-byte."""

    def test_absent_documents_resolve_to_none(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            self.assertIsNone(sdlc_md.dor_dod_level_checks(root, "ready", "story"))
            self.assertIsNone(sdlc_md.dor_dod_level_checks(root, "done", "sprint"))

    def test_level_checks_parse_per_section(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            _write_doc(root, "ready",
                       "# Definition of Ready\n\n## Story\n\n"
                       "- [ ] a [check: grooming.affects]\n"
                       "- [ ] b [check: grooming.points]\n\n"
                       "## Sprint\n\n- [ ] c\n")
            self.assertEqual(sdlc_md.dor_dod_level_checks(root, "ready", "story"),
                             {"grooming.affects", "grooming.points"})
            self.assertEqual(sdlc_md.dor_dod_level_checks(root, "ready", "sprint"), set())
            self.assertIsNone(sdlc_md.dor_dod_level_checks(root, "ready", "release"))

    def test_grooming_refuses_unsized_by_default(self):
        sprint = loader.load_script("sprint")
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            bd = sprint.breakdown(root, _grooming_unit(root, points=False))
            self.assertFalse(bd["ok"])
            self.assertEqual(bd["ungroomed"][0]["missing"], ["Points"])

    def test_grooming_reads_the_story_dor(self):
        # A project whose DoR does not tag grooming.points has downgraded sizing to
        # human judgement: the gate no longer refuses, and says so visibly.
        sprint = loader.load_script("sprint")
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            _write_doc(root, "ready",
                       "# DoR\n\n## Story\n\n- [ ] files [check: grooming.affects]\n")
            bd = sprint.breakdown(root, _grooming_unit(root, points=False))
            self.assertTrue(bd["ok"])
            self.assertIn("grooming.points", bd["downgraded"])

    def test_prefix_colliding_heading_does_not_redefine_a_level(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            _write_doc(root, "ready",
                       "# DoR\n\n## Storyboard notes\n\n- [ ] x [check: grooming.points]\n")
            self.assertIsNone(sdlc_md.dor_dod_level_checks(root, "ready", "story"))

    def test_dod_with_the_tag_still_blocks_done(self):
        # The nastiest silent-disarm regression: adopting a DoD that TAGS
        # story.verify-ac must leave the AC-verify Done gate fully armed.
        transition = loader.load_script("transition")
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            story_dir = root / "sdlc-studio" / "stories"
            story_dir.mkdir(parents=True)
            p = story_dir / "US0001-sample.md"
            text = ("# US0001: sample\n\n> **Status:** Review\n\n## Acceptance Criteria\n\n"
                    "### AC1: works\n- **Verify:** shell echo ok\n")
            p.write_text(text, encoding="utf-8")
            _write_doc(root, "done",
                       "# DoD\n\n## Story\n\n- [ ] acs pass [check: story.verify-ac]\n")
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                self.assertIsNotNone(transition._done_verify_gate(root, p, text))
            self.assertEqual(err.getvalue(), "")   # armed, and no stand-down noise

    def test_stand_down_note_not_emitted_for_manual_only_story(self):
        transition = loader.load_script("transition")
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            story_dir = root / "sdlc-studio" / "stories"
            story_dir.mkdir(parents=True)
            p = story_dir / "US0001-sample.md"
            text = ("# US0001: sample\n\n> **Status:** Review\n\n## Acceptance Criteria\n\n"
                    "### AC1: works\n- **Verify:** manual check by the operator\n")
            p.write_text(text, encoding="utf-8")
            _write_doc(root, "done", "# DoD\n\n## Story\n\n- [ ] human judged\n")
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                self.assertIsNone(transition._done_verify_gate(root, p, text))
            self.assertEqual(err.getvalue(), "")   # nothing executable = nothing stood down

    def test_plan_render_prints_the_downgrade(self):
        # AC2 says VISIBLY IN GATE OUTPUT - the dict field alone is not visibility.
        sprint = loader.load_script("sprint")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            sprint._render_downgrades({"breakdown": {"downgraded": ["grooming.points"]}})
        self.assertIn("grooming.points", out.getvalue())
        self.assertIn("human-judged", out.getvalue())

    def test_conformance_output_prints_the_downgrade(self):
        conformance = loader.load_script("conformance")
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            (sd / "US0001-s.md").write_text(
                "# US0001: s\n\n> **Status:** Done\n> **Epic:** EP0001\n\n"
                "## Acceptance Criteria\n\n### AC1: works\n- **Given** x\n"
                "- **Verify:** shell echo ok\n- **Verified:** yes (2026-01-01)\n",
                encoding="utf-8")
            _write_doc(root, "done", "# DoD\n\n## Story\n\n- [ ] acs [check: story.verify-ac]\n")
            args = conformance.build_parser().parse_args(["check", "--root", str(root)])
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                args.func(args)
            self.assertIn("review.critic-approve", out.getvalue())
            self.assertIn("human-judged", out.getvalue())

    def test_transition_done_reads_the_story_dod(self):
        transition = loader.load_script("transition")
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            story_dir = root / "sdlc-studio" / "stories"
            story_dir.mkdir(parents=True)
            p = story_dir / "US0001-sample.md"
            text = ("# US0001: sample\n\n> **Status:** Review\n\n## Acceptance Criteria\n\n"
                    "### AC1: works\n- **Verify:** shell echo ok\n")
            p.write_text(text, encoding="utf-8")
            # default: executable ACs never verified -> blocked
            self.assertIsNotNone(transition._done_verify_gate(root, p, text))
            # DoD downgrades story.verify-ac -> the deterministic gate stands down, noting it
            _write_doc(root, "done", "# DoD\n\n## Story\n\n- [ ] reviewed by a human\n")
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                self.assertIsNone(transition._done_verify_gate(root, p, text))
            self.assertIn("human-judged", err.getvalue())   # the stand-down is visible

    def test_conformance_critiqued_reads_the_story_dod(self):
        conformance = loader.load_script("conformance")
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            (sd / "US0001-s.md").write_text(
                "# US0001: s\n\n> **Status:** Done\n> **Epic:** EP0001\n\n"
                "## Acceptance Criteria\n\n### AC1: works\n- **Given** x\n"
                "- **Verify:** shell echo ok\n- **Verified:** yes (2026-01-01)\n",
                encoding="utf-8")
            units = {u["id"]: u for u in conformance.detect_conformance(root)["units"]}
            self.assertIn("critiqued", units["US0001"]["missing"])   # default: required
            _write_doc(root, "done", "# DoD\n\n## Story\n\n- [ ] acs [check: story.verify-ac]\n")
            units = {u["id"]: u for u in conformance.detect_conformance(root)["units"]}
            self.assertNotIn("critiqued", units["US0001"]["missing"])  # downgraded
            self.assertIn("review.critic-approve", units["US0001"].get("downgraded", []))

    def test_two_role_tag_alone_still_enforces(self):
        # Cross-unit hole (closing critic, RUN-01KXPJG9): a story DoD tagging
        # review.two-role but NOT review.critic-approve must keep the two-role
        # requirement armed - dropping the critic tag must never disarm BOTH.
        try:
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest("two_role_after reads .config.yaml (needs PyYAML)")
        conformance = loader.load_script("conformance")
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            (root / "sdlc-studio").mkdir(parents=True)
            (root / "sdlc-studio" / ".config.yaml").write_text(
                "review:\n  two_role_after: US0100\n", encoding="utf-8")
            _write_doc(root, "done",
                       "# DoD\n\n## Story\n\n- [ ] signed [check: review.two-role]\n")
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir()
            (sd / "US0101-s.md").write_text(
                "# US0101: s\n\n> **Status:** Done\n> **Epic:** EP0001\n\n"
                "## Acceptance Criteria\n\n### AC1: works\n- **Given** x\n"
                "- **Verify:** shell echo ok\n- **Verified:** yes (2026-01-01)\n",
                encoding="utf-8")
            units = {u["id"]: u for u in conformance.detect_conformance(root)["units"]}
            u = units["US0101"]
            # no evidence and no sign-off recorded: the two-role tag must BLOCK
            self.assertIn("critiqued", u["missing"])
            self.assertFalse(u["conformant"])
            # and only the critic-approve criterion reads as downgraded
            self.assertEqual(u["downgraded"], ["review.critic-approve"])

    def test_close_gate_reads_the_sprint_dod(self):
        gate = loader.load_script("gate")
        ok = lambda r: (0, "fine")  # noqa: E731
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            (root / "sdlc-studio").mkdir(parents=True)
            # default: --require-retro binds the retro AND lessons lanes
            res = gate.run_gate(root=str(root), checks={"noop": ok},
                                require_retro="RETRO0001")
            names = [c["check"] for c in res["checks"]]
            self.assertIn("retro", names)
            self.assertTrue(any(n.startswith("lessons") or "lessons" in n for n in names))
            # a sprint DoD without close.lessons downgrades those lanes, visibly
            _write_doc(root, "done",
                       "# DoD\n\n## Sprint\n\n- [ ] retro [check: close.retro]\n")
            res = gate.run_gate(root=str(root), checks={"noop": ok},
                                require_retro="RETRO0001")
            names = [c["check"] for c in res["checks"]]
            self.assertIn("retro", names)
            self.assertFalse(any("lessons" in n for n in names if n != "dod-downgrades"))
            note = next(c for c in res["checks"] if c["check"] == "dod-downgrades")
            self.assertIn("close.lessons", note["detail"])
            self.assertIn("human-judged", note["detail"])


class TagEditTests(unittest.TestCase):
    """RFC0043 slice 2: editing a tagged criterion changes gate behaviour without
    code changes; removing a tag downgrades it to human-judged visibly."""

    def test_document_edit_flips_the_gate_without_code_change(self):
        sprint = loader.load_script("sprint")
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            batch = _grooming_unit(root, points=False)
            _write_doc(root, "ready",
                       "# DoR\n\n## Story\n\n- [ ] sized [check: grooming.points]\n")
            self.assertFalse(sprint.breakdown(root, batch)["ok"])   # enforced
            _write_doc(root, "ready", "# DoR\n\n## Story\n\n- [ ] sized by a human\n")
            bd = sprint.breakdown(root, batch)                      # tag removed
            self.assertTrue(bd["ok"])
            self.assertIn("grooming.points", bd["downgraded"])      # visible, never silent

    def test_shipped_default_document_matches_no_document(self):
        # Adopting the shipped defaults must not change behaviour: the template's
        # story-level DoR tags are exactly the checks the gate enforces bare.
        sprint = loader.load_script("sprint")
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            batch = _grooming_unit(root, points=False)
            bare = sprint.breakdown(root, batch)
            (root / "sdlc-studio").mkdir(exist_ok=True)
            template = (TEMPLATES / "definition-of-ready.md").read_text(encoding="utf-8")
            (root / "sdlc-studio" / "definition-of-ready.md").write_text(template,
                                                                         encoding="utf-8")
            with_doc = sprint.breakdown(root, batch)
            self.assertEqual(bare["ok"], with_doc["ok"])
            self.assertEqual(bare["ungroomed"], with_doc["ungroomed"])
            self.assertEqual(with_doc.get("downgraded", []), [])


if __name__ == "__main__":
    unittest.main()
