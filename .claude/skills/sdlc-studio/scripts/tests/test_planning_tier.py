"""The `planning` template tier: a lean pre-implementation scaffold that cannot
silently reach implementation.

The full story template's structural floor is ~171 lines once every mandated heading
survives, so a dense planning story cannot get under it however economically it is
written. The `planning` tier sits between `minimal` and `full`: metadata, user story,
ACs with Verify and Verification-target lines, scope, technical notes - and no
inherited-constraint tables or module views until implementation.

The contract that keeps the tier honest: a planning-tier story is STAMPED
(`> **Template:** planning`), the stamp is validated against the known tiers (a typo'd
tier would silently switch the gate off), the transition gate refuses entry to an
implementation-facing status until the story is promoted, and conformance backstops the
hand-edited status. A lean lane must not read as a finished one.
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCR))
from lib import sdlc_md  # noqa: E402
import conformance  # noqa: E402
import transition  # noqa: E402
import validate  # noqa: E402


def _load():
    spec = importlib.util.spec_from_file_location("artifact", SCR / "artifact.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["artifact"] = mod
    spec.loader.exec_module(mod)
    return mod


artifact = _load()

ACS = ["the CLI exits 0 for a known id", "an unknown id exits 2 with a named reason"]
VERIFIES = ["pytest -k known_id", "pytest -k unknown_id"]


def _project(root: Path) -> str:
    """A bare workspace with one epic; returns the epic id."""
    (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
    return artifact.new(root, "epic", "parent epic", {"summary": "the group"})["id"]


def _story(root: Path, template: str = "planning", **extra) -> Path:
    epic = extra.pop("epic", None) or _project(root)
    fields = {"epic": epic, "template": template, "acs": ACS, "verify": VERIFIES,
              "target": "functional", **extra}
    res = artifact.new(root, "story", "a planning story", fields)
    return Path(res["path"])


def _scaffold(root: Path, template: str = "planning") -> Path:
    """A content-less story: the `skeleton` the CR's first AC is about."""
    res = artifact.new(root, "story", "a bare planning story",
                       {"epic": _project(root), "template": template})
    return Path(res["path"])


def _errors(root: Path, path: Path, type_: str = "story") -> list[dict]:
    return [v for v in validate.validate_file(path, type_, root) if v["severity"] == "error"]


class PlanningStoryShapeTests(unittest.TestCase):
    """AC1: a planning skeleton under 60 lines with ACs, scope and Verify targets intact."""

    def test_the_skeleton_is_under_sixty_lines_with_its_verify_targets_intact(self) -> None:
        """The CR's AC1, read literally: the SKELETON (what `new` writes before an agent
        fills it) must be under 60 lines and still carry AC, scope and Verify-target slots."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            text = _scaffold(root).read_text(encoding="utf-8")
            n = len(text.splitlines())
            self.assertLess(n, 60, f"planning skeleton rendered {n} lines:\n{text}")
            for want in ("## Acceptance Criteria", "### AC1:", "- **Verify:**",
                         "- **Verification target:**", "## Scope", "### In Scope",
                         "### Out of Scope", "## Technical Notes", "## Revision History"):
                self.assertIn(want, text, f"planning skeleton lost {want!r}")
            for gone in ("## Inherited Constraints", "## Rollback Envelope", "## Estimation",
                         "## Edge Cases", "## Test Scenarios"):
                self.assertNotIn(gone, text, f"{gone!r} is implementation furniture")

    def test_a_filled_planning_story_keeps_its_acs_verifies_and_scope(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            text = _story(root).read_text(encoding="utf-8")
            n = len(text.splitlines())
            self.assertLess(n, 60, f"planning story rendered {n} lines:\n{text}")
            for ac in ACS:
                self.assertIn(ac, text, "the supplied ACs must land in the planning tier too")
            for v in VERIFIES:
                self.assertIn(f"- **Verify:** {v}", text, "the executable check must land")
            self.assertIn("- **Verification target:** functional", text)
            self.assertIn("## Scope", text)

    def test_a_supplied_ac_with_no_verify_gets_no_invented_one(self) -> None:
        """There is no honest default for a Verify line: a placeholder fails the validator
        and `manual` asserts a proof nobody ran. The gap is reported, never filled."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            res = artifact.new(root, "story", "no verify",
                               {"epic": _project(root), "template": "planning", "acs": ACS})
            text = Path(res["path"]).read_text(encoding="utf-8")
            self.assertNotIn("**Verify:**", text)
            self.assertNotIn("manual", text.lower())
            self.assertEqual(_errors(root, Path(res["path"])), [])

    def test_the_tier_is_stamped(self) -> None:
        """The gate reads a stamp, so the render must write one."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            text = _story(Path(d)).read_text(encoding="utf-8")
            self.assertEqual(sdlc_md.extract_field(text, "Template"), "planning")
            self.assertEqual(_errors(root, _story(root, "full")), [])

    def test_full_and_minimal_are_unstamped(self) -> None:
        """Only the NEW tier carries the promotion contract: gating `minimal` retroactively
        would refuse every story in every existing project."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            epic = _project(root)
            for tier in ("minimal", "full"):
                text = _story(root, tier, epic=epic).read_text(encoding="utf-8")
                self.assertIsNone(sdlc_md.extract_field(text, "Template"), tier)

    def test_batch_renders_the_planning_tier(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            epic = _project(root)
            res = artifact.new_batch(root, "story",
                                     [{"title": "batched", "epic": epic, "acs": ACS}],
                                     template="planning")
            text = Path(res["created"][0]["path"]).read_text(encoding="utf-8")
            self.assertEqual(sdlc_md.extract_field(text, "Template"), "planning")
            self.assertLess(len(text.splitlines()), 60)

    def test_planning_epic_is_lean_too(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir(parents=True)
            res = artifact.new(root, "epic", "a planning epic",
                               {"template": "planning", "summary": "what it groups",
                                "acs": ["every story is Done"]})
            text = Path(res["path"]).read_text(encoding="utf-8")
            self.assertLess(len(text.splitlines()), 60)
            self.assertIn("## Story Breakdown", text)
            self.assertIn("## Scope", text)
            self.assertNotIn("## Inherited Constraints", text)
            self.assertEqual(_errors(root, Path(res["path"]), "epic"), [])


class SuppliedVerifyTests(unittest.TestCase):
    """A Verify line is a command the verifier reads back and RUNS - so it is written
    verbatim, and anything that cannot be trusted to run is refused rather than written."""

    def test_a_verify_expression_is_not_markdown_mangled(self) -> None:
        """`pytest -k known_id` markdown-safed becomes ``pytest -k `known_id` `` - and those
        backticks are command substitution by the time verify_ac hands it to a shell."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            text = _story(root).read_text(encoding="utf-8")
            self.assertIn("- **Verify:** pytest -k known_id", text)
            self.assertNotIn("`known_id`", text)

    def test_the_supplied_verify_is_the_one_the_verifier_parses_back(self) -> None:
        """The round trip that matters: what the creator wrote is what verify_ac reads."""
        import verify_ac
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            blocks = verify_ac.parse_story(_story(root).read_text(encoding="utf-8"))
            self.assertEqual([b.verifier for b in blocks], VERIFIES)

    def test_an_unknown_verification_target_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            with self.assertRaises(ValueError):
                _story(root, target="thorough")

    def test_a_multiline_verify_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            with self.assertRaises(ValueError):
                _story(root, verify=["pytest -k x\n- **Verify:** true"])

    def test_a_bad_item_aborts_the_batch_before_any_write(self) -> None:
        """new_batch is all-or-nothing: item 2's bad target must not leave item 1 on disk."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            epic = _project(root)
            items = [{"title": "good", "epic": epic, "acs": ACS},
                     {"title": "bad", "epic": epic, "acs": ACS, "target": "thorough"}]
            with self.assertRaises(ValueError):
                artifact.new_batch(root, "story", items, template="planning")
            self.assertEqual(list((root / "sdlc-studio" / "stories").glob("US*.md")), [])


class PlanningValidationTests(unittest.TestCase):
    """AC2, first leg: validate.py accepts the tier - and refuses a tier it cannot trust."""

    def test_a_filled_planning_story_is_validator_clean(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path = _story(root)
            errs = _errors(root, path)
            self.assertEqual(errs, [], "; ".join(f"[{e['rule']}] {e['message']}" for e in errs))

    def test_a_contentless_planning_scaffold_still_reports_its_placeholders(self) -> None:
        """The carve-out holds: a scaffold is not a specified story, and the lean tier does
        not paper over its unfilled slots to look clean."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            epic = _project(root)
            res = artifact.new(root, "story", "bare", {"epic": epic, "template": "planning"})
            errs = _errors(root, Path(res["path"]))
            self.assertTrue([e for e in errs if e["rule"] == "placeholder"],
                            "an unfilled planning scaffold must still report its slots")
            owned = [e for e in errs if e["rule"] in
                     {"id-format", "no-title", "no-status", "status-vocab", "template-tier"}]
            self.assertEqual(owned, [], "no CREATOR-owned rule may fire on a scaffold")

    def test_an_unknown_tier_stamp_is_refused(self) -> None:
        """A typo'd tier (`plannning`) would read as not-planning and switch the promotion
        gate silently off - a lane with nothing to prove reading as proof."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path = _story(root)
            path.write_text(path.read_text(encoding="utf-8").replace(
                "> **Template:** planning", "> **Template:** plannning"), encoding="utf-8")
            errs = _errors(root, path)
            self.assertTrue([e for e in errs if e["rule"] == "template-tier"],
                            "an unknown Template tier must be an error, not a silent pass")


class PlanningPromotionGateTests(unittest.TestCase):
    """AC2, second leg: implementation-facing statuses require promotion to full."""

    def _ready(self, root: Path) -> str:
        path = _story(root)
        return sdlc_md.extract_record_id(path.stem)

    def test_every_implementation_target_is_refused(self) -> None:
        for status in ("In Progress", "Review", "Done"):
            with self.subTest(status=status), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                sid = self._ready(root)
                with self.assertRaises(ValueError) as ctx:
                    transition.transition(root, sid, status)
                self.assertIn("promote", str(ctx.exception).lower(),
                              "the refusal must name the remedy")

    def test_the_gate_is_not_force_bypassable(self) -> None:
        """The sanctioned skip is promotion (one deterministic command), never a documented
        skip that prints green over the missing sections."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sid = self._ready(root)
            with self.assertRaises(ValueError):
                transition.transition(root, sid, "Done", force=True)

    def test_dry_run_refuses_too(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sid = self._ready(root)
            with self.assertRaises(ValueError):
                transition.transition(root, sid, "In Progress", dry_run=True)

    def test_non_implementation_statuses_pass(self) -> None:
        """Planning IS the point of the tier: Ready/Blocked and the rest stay open."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sid = self._ready(root)
            res = transition.transition(root, sid, "Ready")
            self.assertEqual(res["to"], "Ready")

    def test_a_full_tier_story_is_never_gated(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path = _story(root, "full")
            sid = sdlc_md.extract_record_id(path.stem)
            self.assertEqual(transition.transition(root, sid, "In Progress")["to"], "In Progress")


class PromoteTests(unittest.TestCase):
    """`artifact.py promote` is the remedy the refusal names: it must actually work."""

    def test_promote_adds_the_missing_sections_and_keeps_the_content(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path = _story(root)
            before = path.read_text(encoding="utf-8")
            res = artifact.promote(root, sdlc_md.extract_record_id(path.stem))
            self.assertTrue(res["promoted"])
            after = path.read_text(encoding="utf-8")
            self.assertEqual(sdlc_md.extract_field(after, "Template"), "full")
            for want in ("## Inherited Constraints", "## Edge Cases", "## Test Scenarios",
                         "## Dependencies", "## Rollback Envelope"):
                self.assertIn(want, after, f"promote must add {want!r}")
            for ac in ACS:  # nothing the planning tier held may be lost
                self.assertIn(ac, after)
            self.assertIn("## User Story", after)
            self.assertEqual(before.count("## Acceptance Criteria"),
                             after.count("## Acceptance Criteria"),
                             "promote must not duplicate a section the story already has")
            self.assertEqual(after.count("## Revision History"), 1)

    def test_promote_unblocks_the_transition(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path = _story(root)
            sid = sdlc_md.extract_record_id(path.stem)
            artifact.promote(root, sid)
            self.assertEqual(transition.transition(root, sid, "In Progress")["to"], "In Progress")

    def test_promote_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path = _story(root)
            sid = sdlc_md.extract_record_id(path.stem)
            artifact.promote(root, sid)
            once = path.read_text(encoding="utf-8")
            res = artifact.promote(root, sid)
            self.assertFalse(res["promoted"], "a full-tier story is already promoted")
            self.assertEqual(path.read_text(encoding="utf-8"), once)

    def test_a_promoted_story_still_validates(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path = _story(root)
            artifact.promote(root, sdlc_md.extract_record_id(path.stem))
            errs = _errors(root, path)
            self.assertEqual(errs, [], "; ".join(f"[{e['rule']}] {e['message']}" for e in errs))


class ConformanceBackstopTests(unittest.TestCase):
    """The transition gate guards the tool path; a hand-edited `Status: Done` bypasses it.
    Conformance is the backstop - the same doubling the AC-verify gate already has."""

    def test_a_done_planning_story_is_nonconformant(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path = _story(root)
            path.write_text(path.read_text(encoding="utf-8").replace(
                "> **Status:** Draft", "> **Status:** Done"), encoding="utf-8")
            unit = next(u for u in conformance.detect_conformance(root)["units"])
            self.assertFalse(unit["stages"]["promoted"])
            self.assertIn("promoted", unit["missing"])

    def test_an_ordinary_story_is_promoted_by_definition(self) -> None:
        """An unstamped story (every artefact in every existing project) is never flagged."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path = _story(root, "full")
            path.write_text(path.read_text(encoding="utf-8").replace(
                "> **Status:** Draft", "> **Status:** Done"), encoding="utf-8")
            unit = next(u for u in conformance.detect_conformance(root)["units"])
            self.assertTrue(unit["stages"]["promoted"])
            self.assertNotIn("promoted", unit["missing"])


class GateDefeatTests(unittest.TestCase):
    """The gate is the tier's whole justification. These are the routes that defeated it.

    The structural lesson: stop trusting a marker the subject can rewrite, and check the
    thing actually cared about - the deferred sections. Where a route ends in an artefact
    CLAIMING to be full while lacking them, that claim is checkable and the route closes.
    """

    def _planning_story(self, root: Path) -> tuple[str, Path]:
        path = _story(root)
        return sdlc_md.extract_record_id(path.stem), path

    def _retag(self, path: Path, value: str | None) -> None:
        """Rewrite (or delete) the tier stamp by hand."""
        line = "> **Template:** planning"
        text = path.read_text(encoding="utf-8")
        new = text.replace(line + "\n", "") if value is None \
            else text.replace(line, f"> **Template:** {value}")
        path.write_text(new, encoding="utf-8")

    # F1 -----------------------------------------------------------------
    def test_annotate_refuses_the_tier_field(self) -> None:
        """`annotate --field Template --value full` cleared the gate AND the backstop, with
        no waiver and no record - the documented skip I claimed did not exist. `Template` is
        a gate-protected field; the denylist is the project's own precedent for exactly this."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sid, _ = self._planning_story(root)
            with self.assertRaises(ValueError) as ctx:
                transition.annotate(root, sid, "Template", "full")
            self.assertIn("promote", str(ctx.exception).lower())

    def test_a_forged_full_stamp_does_not_clear_the_gate(self) -> None:
        """Belt and braces for F1: even with a `full` stamp written by hand, the sections are
        not there - and a stamp is only a claim. Nothing legitimately carries a `full` stamp
        except an artefact `promote` built, so checking the claim costs no legacy story."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sid, path = self._planning_story(root)
            self._retag(path, "full")
            with self.assertRaises(ValueError) as ctx:
                transition.transition(root, sid, "Done", force=True)
            self.assertIn("section", str(ctx.exception).lower())

    def test_a_forged_full_stamp_is_not_conformant(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _, path = self._planning_story(root)
            self._retag(path, "full")
            path.write_text(path.read_text(encoding="utf-8").replace(
                "> **Status:** Draft", "> **Status:** Done"), encoding="utf-8")
            unit = next(iter(conformance.detect_conformance(root)["units"]))
            self.assertFalse(unit["stages"]["promoted"])

    # F2 -----------------------------------------------------------------
    def test_an_unknown_tier_fails_closed_at_the_gate(self) -> None:
        """I wrote the rationale and then hardened only the validator. A typo'd tier read as
        'not planning' and switched off the gate AND the backstop it was meant to protect."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sid, path = self._planning_story(root)
            self._retag(path, "plannning")
            with self.assertRaises(ValueError):
                transition.transition(root, sid, "Done", force=True)

    def test_an_unknown_tier_fails_closed_at_the_backstop(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _, path = self._planning_story(root)
            self._retag(path, "plannning")
            path.write_text(path.read_text(encoding="utf-8").replace(
                "> **Status:** Draft", "> **Status:** Done"), encoding="utf-8")
            unit = next(iter(conformance.detect_conformance(root)["units"]))
            self.assertFalse(unit["stages"]["promoted"])

    # F3 -----------------------------------------------------------------
    def test_a_stripped_stamp_leaves_a_legacy_shaped_story(self) -> None:
        """The honest boundary, asserted so it cannot drift silently.

        Delete the stamp and the artefact is byte-for-byte the shape of the 103 of 119
        existing stories that carry none of the deferred sections and reach Done today. It is
        not a forgery the tool can detect - it IS a legacy story. Refusing it by default would
        refuse them too. The close is a project-wide decision, not a default (below)."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sid, path = self._planning_story(root)
            self._retag(path, None)
            self.assertIsNone(sdlc_md.extract_field(path.read_text(encoding="utf-8"), "Template"))
            self.assertEqual(transition.transition(root, sid, "In Progress")["to"], "In Progress")

    def test_require_full_sections_closes_it_project_wide(self) -> None:
        """`quality.require_full_sections: true` is the structural close: the gate stops
        consulting the stamp at all and checks only the sections, so a stripped stamp buys
        nothing. Opt-in, because ON by default would refuse 103 of this repo's 119 stories."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sid, path = self._planning_story(root)
            self._retag(path, None)
            (root / "sdlc-studio" / ".config.yaml").write_text(
                "quality:\n  require_full_sections: true\n", encoding="utf-8")
            with self.assertRaises(ValueError) as ctx:
                transition.transition(root, sid, "Done", force=True)
            self.assertIn("section", str(ctx.exception).lower())
            artifact.promote(root, sid)
            self.assertEqual(transition.transition(root, sid, "In Progress")["to"], "In Progress")

    def test_require_full_sections_does_not_fire_on_a_promoted_story(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sid, _ = self._planning_story(root)
            artifact.promote(root, sid)
            (root / "sdlc-studio" / ".config.yaml").write_text(
                "quality:\n  require_full_sections: true\n", encoding="utf-8")
            self.assertEqual(transition.transition(root, sid, "Done", force=True)["to"], "Done")

    # F4 -----------------------------------------------------------------
    def test_a_planning_epic_is_gated_too(self) -> None:
        """The epic template asserts its constraint chain, success metrics and risk register
        'arrive with promotion'. An ungated epic made that assertion false."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir(parents=True)
            res = artifact.new(root, "epic", "a planning epic",
                               {"template": "planning", "summary": "s",
                                "acs": ["every story is Done"]})
            for status in ("In Progress", "Done"):
                with self.subTest(status=status), self.assertRaises(ValueError) as ctx:
                    transition.transition(root, res["id"], status)
                self.assertIn("promote", str(ctx.exception).lower())
            artifact.promote(root, res["id"])
            self.assertEqual(transition.transition(root, res["id"], "Done")["to"], "Done")

    # no over-fire ---------------------------------------------------------
    def test_an_unstamped_legacy_story_is_never_gated(self) -> None:
        """The floor Sam confirmed and I must not break: 119 existing stories carry no stamp,
        103 of them carry none of the deferred sections, and none may be newly refused."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path = _story(root, "minimal")
            sid = sdlc_md.extract_record_id(path.stem)
            self.assertIsNone(sdlc_md.extract_field(path.read_text(encoding="utf-8"), "Template"))
            self.assertEqual(transition.transition(root, sid, "Done", force=True)["to"], "Done")
            unit = next(iter(conformance.detect_conformance(root)["units"]))
            self.assertTrue(unit["stages"]["promoted"])


if __name__ == "__main__":
    unittest.main()
