"""Unit tests for conformance.py (RED first - the script does not exist yet).

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "conformance.py"


def _load():
    spec = importlib.util.spec_from_file_location("conformance", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["conformance"] = mod
    spec.loader.exec_module(mod)
    return mod


def _story(root, num, *, epic=True, ac=True, verify=True, status="Ready", verified="yes"):
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    lines = [f"# US{num:04d}: sample", "", f"> **Status:** {status}"]
    if epic:
        lines.append("> **Epic:** [EP0001: x](../epics/EP0001-x.md)")
    lines.append("")
    if ac:
        lines += ["## Acceptance Criteria", "", "### AC1: works", "- **Given** a thing"]
        if verify:
            lines.append("- **Verify:** shell echo ok")
        if status == "Done":
            lines.append(f"- **Verified:** {verified} (2026-01-01)")
    (d / f"US{num:04d}-sample.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _units(root):
    return {u["id"]: u for u in _load().detect_conformance(root)["units"]}


class StageTests(unittest.TestCase):
    def test_full_story_all_stages_true(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1)
            u = _units(root)["US0001"]
            self.assertTrue(u["conformant"])
            self.assertEqual(u["missing"], [])
            self.assertTrue(all(u["stages"][s] for s in ("decomposed", "specified", "verifiable")))

    def test_missing_stage_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, epic=False)
            u = _units(root)["US0001"]
            self.assertFalse(u["conformant"])
            self.assertIn("decomposed", u["missing"])

    def test_draft_story_is_conformant_on_decomposed_alone(self) -> None:
        # CR0342: an ungroomed Draft story (a fresh refine output with placeholder ACs) needs only
        # `decomposed` - specified/verifiable are the Definition-of-Ready bar, required once it is
        # Ready+. So a large refined backlog does not read as non-conformant before it is groomed.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, status="Draft", ac=False, verify=False)
            u = _units(root)["US0001"]
            self.assertTrue(u["conformant"], u["missing"])
            self.assertEqual(u["missing"], [])

    def test_ready_story_still_requires_specified_and_verifiable(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, status="Ready", verify=False)
            u = _units(root)["US0001"]
            self.assertFalse(u["conformant"])
            self.assertIn("verifiable", u["missing"])

    def test_done_must_be_verified(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, status="Done", verified="no")
            u = _units(root)["US0001"]
            self.assertFalse(u["conformant"])
            self.assertIn("verified", u["missing"])


def _record_verdict(root, unit, verdict="approve", reviewer="independent-critic", author="builder"):
    spec = importlib.util.spec_from_file_location("critic", SCRIPT.parent / "critic.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["critic"] = m
    spec.loader.exec_module(m)
    # Independence floor (CR0117): the critic stage needs author != reviewer, so the helper
    # records distinct ids by default; self-review/missing-author cases are covered in test_critic.
    m.record_verdict(root, unit, verdict, reviewer=reviewer, author=author)


class SpecifiedStageTests(unittest.TestCase):
    def test_prose_bullet_ac_section_is_specified(self) -> None:
        # An AC section of prose bullets (no ACn id) still counts as specified.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            (sd / "US0001-x.md").write_text(
                "# US0001: s\n\n> **Status:** Ready\n> **Epic:** [EP0001](../epics/EP0001-x.md)\n\n"
                "## Acceptance Criteria\n\n- New byModel strategy in group.ts\n- Unit-tested: counts match\n\n"
                "## Notes\n\nx\n", encoding="utf-8")
            u = _units(root)["US0001"]
            self.assertTrue(u["stages"]["specified"])

    def test_empty_ac_section_not_specified(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            (sd / "US0001-x.md").write_text(
                "# US0001: s\n\n> **Status:** Ready\n> **Epic:** [EP0001](../epics/EP0001-x.md)\n\n"
                "## Acceptance Criteria\n\n## Notes\n\nx\n", encoding="utf-8")
            u = _units(root)["US0001"]
            self.assertFalse(u["stages"]["specified"])

    def test_placeholder_only_ac_not_specified_or_verifiable(self) -> None:
        # CR0056: a fresh scaffold whose AC/Verify slots are still {{...}} is NOT specified
        # and NOT verifiable - it cannot reach Done.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            (sd / "US0001-x.md").write_text(
                "# US0001: s\n\n> **Status:** Draft\n> **Epic:** [EP0001](../epics/EP0001-x.md)\n\n"
                "## Acceptance Criteria\n\n### AC1: {{define}}\n\n- **Given** {{context}}\n"
                "- **When** {{action}}\n- **Then** {{outcome}}\n- **Verify:** {{check}}\n", encoding="utf-8")
            u = _units(root)["US0001"]
            self.assertFalse(u["stages"]["specified"])
            self.assertFalse(u["stages"]["verifiable"])

    def test_one_real_ac_among_placeholders_is_specified(self) -> None:
        # A real Verify/AC line still counts even if a sibling slot is a placeholder.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            (sd / "US0001-x.md").write_text(
                "# US0001: s\n\n> **Status:** Ready\n> **Epic:** [EP0001](../epics/EP0001-x.md)\n\n"
                "## Acceptance Criteria\n\n### AC1: login works\n\n- **Given** a real precondition\n"
                "- **Verify:** pytest tests/test_login.py\n", encoding="utf-8")
            u = _units(root)["US0001"]
            self.assertTrue(u["stages"]["specified"])
            self.assertTrue(u["stages"]["verifiable"])


    def test_placeholder_with_trailing_punct_not_specified(self) -> None:
        # CR0056 (critic): `{{x}}.` is not real content - conformance must agree with validate.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "stories"; sd.mkdir(parents=True)
            (sd / "US0001-x.md").write_text(
                "# US0001: s\n\n> **Status:** Draft\n> **Epic:** [EP0001](../epics/EP0001-x.md)\n\n"
                "## Acceptance Criteria\n\n### AC1: {{define}}.\n\n- **Verify:** {{check}}.\n", encoding="utf-8")
            u = _units(root)["US0001"]
            self.assertFalse(u["stages"]["specified"])
            self.assertFalse(u["stages"]["verifiable"])


class CritiqueStageTests(unittest.TestCase):
    def test_done_without_verdict_not_conformant(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, status="Done", verified="yes")  # no critic verdict
            u = _units(root)["US0001"]
            self.assertFalse(u["conformant"])
            self.assertIn("critiqued", u["missing"])

    def test_done_with_approve_verdict_conformant(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, status="Done", verified="yes")
            _record_verdict(root, "US0001", "approve")
            u = _units(root)["US0001"]
            self.assertNotIn("critiqued", u["missing"])
            self.assertTrue(u["stages"]["critiqued"])

    def test_done_with_reject_verdict_not_conformant(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, status="Done", verified="yes")
            _record_verdict(root, "US0001", "reject")
            u = _units(root)["US0001"]
            self.assertIn("critiqued", u["missing"])  # unresolved REJECT

    def test_new_self_review_not_conformant(self) -> None:
        # CR0117: a NEW self-review (reviewer == author, no grandfather) never clears.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, status="Done", verified="yes")
            _record_verdict(root, "US0001", "approve", reviewer="dani", author="dani")
            u = _units(root)["US0001"]
            self.assertIn("critiqued", u["missing"])  # self-review blocked

    def test_pre_gate_unit_is_grandfathered(self) -> None:
        # A unit closed before the gate (PRE_GATE marker, prior risk-scaled policy)
        # is grandfathered conformant even though it is not real independence.
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "critic", Path(__file__).resolve().parent.parent / "critic.py")
        critic = importlib.util.module_from_spec(spec); spec.loader.exec_module(critic)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, status="Done", verified="yes")
            _record_verdict(root, "US0001", "approve",
                            reviewer="self-review (light, docs)", author=critic.PRE_GATE)
            u = _units(root)["US0001"]
            self.assertNotIn("critiqued", u["missing"])  # grandfathered
            self.assertTrue(u["stages"]["critiqued"])


class ReconciledStageTests(unittest.TestCase):
    def test_done_with_index_drift_not_reconciled(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, status="Done", verified="yes")
            _record_verdict(root, "US0001", "approve")  # isolate the reconciled stage
            # index says Ready while the file says Done -> status-mismatch
            (root / "sdlc-studio" / "stories" / "_index.md").write_text(
                "# Stories\n\n| ID | Title | Status |\n|---|---|---|\n"
                "| [US0001](US0001-sample.md) | sample | Ready |\n", encoding="utf-8")
            u = _units(root)["US0001"]
            self.assertIn("reconciled", u["missing"])
            self.assertFalse(u["stages"]["reconciled"])

    def test_done_absent_from_index_not_reconciled(self) -> None:
        # A Done story missing from the index (missing-row) is not reconciled.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, status="Done", verified="yes")
            _record_verdict(root, "US0001", "approve")
            (root / "sdlc-studio" / "stories" / "_index.md").write_text(
                "# Stories\n\n| ID | Title | Status |\n|---|---|---|\n", encoding="utf-8")
            u = _units(root)["US0001"]
            self.assertIn("reconciled", u["missing"])


class GuidanceTests(unittest.TestCase):
    def test_guidance_printed_for_missing_stage(self) -> None:
        import io
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, epic=False)  # missing decomposed
            buf = io.StringIO()
            with redirect_stdout(buf):
                _load().main(["check", "--root", str(root)])
            out = buf.getvalue()
            self.assertIn("Guidance:", out)
            self.assertIn("decomposed ->", out)


class CliTests(unittest.TestCase):
    def test_exit_and_shape(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1)
            _story(root, 2, epic=False)
            mod = _load()
            rc = mod.main(["check", "--root", str(root), "--format", "json"])
            self.assertEqual(rc, 1)  # US0002 is non-conformant
            data = mod.detect_conformance(root)
            self.assertIn("units", data)
            self.assertEqual(set(data["summary"]), {"total", "conformant", "nonconformant", "exempt"})


try:
    import yaml as _yaml  # noqa: F401
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


@unittest.skipUnless(HAS_YAML, "adopt_after reads .config.yaml (needs PyYAML)")
class AdoptCutoffTests(unittest.TestCase):
    """conformance.adopt_after exempts pre-adoption stories (CR0027)."""

    def _config(self, root: Path, body: str) -> None:
        (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
        (root / "sdlc-studio" / ".config.yaml").write_text(body, encoding="utf-8")

    def test_pre_cutoff_story_is_exempt(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, epic=False, ac=False)   # would be non-conformant
            _story(root, 10, epic=False, ac=False)  # non-conformant, judged
            self._config(root, "conformance:\n  adopt_after: US0005\n")
            units = _units(root)
            self.assertTrue(units["US0001"]["exempt"])
            self.assertTrue(units["US0001"]["conformant"])   # exempt -> not failing
            self.assertEqual(units["US0001"]["missing"], [])
            self.assertFalse(units["US0010"]["exempt"])
            self.assertFalse(units["US0010"]["conformant"])  # still judged + failing
            summ = _load().detect_conformance(root)["summary"]
            self.assertEqual(summ["exempt"], 1)
            self.assertEqual(summ["nonconformant"], 1)

    def test_no_cutoff_judges_all(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, epic=False, ac=False)
            self.assertFalse(_units(root)["US0001"]["exempt"])
            self.assertFalse(_units(root)["US0001"]["conformant"])

    def test_cmd_check_exits_zero_when_all_nonconformant_are_exempt(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, epic=False, ac=False)   # would fail, but exempt
            self._config(root, "conformance:\n  adopt_after: US0005\n")
            mod = _load()
            args = mod.build_parser().parse_args(["check", "--root", str(root)])
            self.assertEqual(args.func(args), 0)  # nothing judged-and-failing

    def test_bare_int_cutoff_now_exempts(self) -> None:
        # BG0039: a bare integer cutoff was silently dropped (id_number("5") -> None);
        # it must now exempt pre-cutoff stories exactly as the prefixed form does.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, epic=False, ac=False)
            _story(root, 10, epic=False, ac=False)
            self._config(root, "conformance:\n  adopt_after: 5\n")  # bare int
            units = _units(root)
            self.assertTrue(units["US0001"]["exempt"])
            self.assertFalse(units["US0010"]["exempt"])

    def test_boundary_id_itself_is_exempt(self) -> None:
        # BG0039: <= alignment - the cutoff id itself is grandfathered, not judged.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 5, epic=False, ac=False)
            self._config(root, "conformance:\n  adopt_after: 5\n")
            self.assertTrue(_units(root)["US0005"]["exempt"])

    def test_unparseable_cutoff_raises_not_silent(self) -> None:
        # LL0008: a typo'd cutoff must fail loud, NOT silently judge everything.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, epic=False, ac=False)
            self._config(root, "conformance:\n  adopt_after: oops\n")
            with self.assertRaises(ValueError):
                _load().detect_conformance(root)


def _critic_mod():
    spec = importlib.util.spec_from_file_location("critic", SCRIPT.parent / "critic.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["critic"] = m
    spec.loader.exec_module(m)
    return m


@unittest.skipUnless(HAS_YAML, "review.two_role_after reads .config.yaml (needs PyYAML)")
class TwoRoleCritiquedTests(unittest.TestCase):
    """CR0323 / RFC0044: with review.two_role_after set, a Done unit past the cutoff
    clears `critiqued` only with adversarial EVIDENCE plus an independent SIGN-OFF -
    forward-only, so existing projects and pre-cutoff units keep today's behaviour."""

    def _config(self, root: Path) -> None:
        (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
        (root / "sdlc-studio" / ".config.yaml").write_text(
            "review:\n  two_role_after: US0100\n", encoding="utf-8")

    def test_verdict_alone_no_longer_clears_critiqued(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._config(root)
            _story(root, 101, status="Done")
            _record_verdict(root, "US0101")           # independent APPROVE, old-style
            u = _units(root)["US0101"]
            self.assertFalse(u["stages"]["critiqued"])
            self.assertIn("critiqued", u["missing"])

    def test_evidence_plus_signoff_clears_critiqued(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._config(root)
            _story(root, 101, status="Done")
            _record_verdict(root, "US0101")
            c = _critic_mod()
            c.record_evidence(root, "US0101", reviewer="qa-seat", author="builder",
                              findings="adversarial pass done")
            c.record_signoff(root, "US0101", principal="Darren Benson (operator)",
                             author="builder")
            u = _units(root)["US0101"]
            self.assertTrue(u["stages"]["critiqued"])

    def test_hand_edited_self_signoff_is_backstopped(self) -> None:
        # record_signoff refuses a self-sign-off; a hand-appended row walks round the
        # tool, so conformance re-checks independence from the recorded rows.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._config(root)
            _story(root, 101, status="Done")
            _record_verdict(root, "US0101")
            c = _critic_mod()
            c.record_evidence(root, "US0101", reviewer="qa-seat", author="builder",
                              findings="adversarial pass done")
            path = c.signoff_path(root)
            path.parent.mkdir(parents=True, exist_ok=True)
            c.record_signoff(root, "US0101", principal="operator", author="builder")
            text = path.read_text(encoding="utf-8").replace("| operator |", "| builder |")
            path.write_text(text, encoding="utf-8")   # hand-edit: principal == author
            u = _units(root)["US0101"]
            self.assertFalse(u["stages"]["critiqued"])

    def test_signoff_by_session_subagent_is_backstopped(self) -> None:
        # A sign-off whose principal is a recorded authoring-session reviewer id
        # (the seat subagent) must not clear the gate even if hand-recorded.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._config(root)
            _story(root, 101, status="Done")
            _record_verdict(root, "US0101", reviewer="qa-seat")
            c = _critic_mod()
            c.record_evidence(root, "US0101", reviewer="qa-seat", author="builder",
                              findings="adversarial pass done")
            c.record_signoff(root, "US0101", principal="operator", author="builder")
            path = c.signoff_path(root)
            text = path.read_text(encoding="utf-8").replace("| operator |", "| qa-seat |")
            path.write_text(text, encoding="utf-8")
            u = _units(root)["US0101"]
            self.assertFalse(u["stages"]["critiqued"])

    def test_signoff_without_evidence_not_critiqued(self) -> None:
        # "critiqued requires BOTH": an independent sign-off with no adversarial
        # evidence row must not clear the stage (kills the drop-evidence mutant).
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._config(root)
            _story(root, 101, status="Done")
            _record_verdict(root, "US0101")
            c = _critic_mod()
            c.record_signoff(root, "US0101", principal="Darren Benson (operator)",
                             author="builder")
            u = _units(root)["US0101"]
            self.assertFalse(u["stages"]["critiqued"])
            self.assertIn("critiqued", u["missing"])

    def test_cutoff_boundary_unit_keeps_old_rule(self) -> None:
        # The cutoff id itself is grandfathered (<= exempt, > judged) - a `>` -> `>=`
        # regression would retroactively gate the boundary unit.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._config(root)
            _story(root, 100, status="Done")          # == US0100 cutoff
            _record_verdict(root, "US0100")           # verdict alone suffices
            u = _units(root)["US0100"]
            self.assertTrue(u["stages"]["critiqued"])

    def test_pre_cutoff_done_unit_keeps_old_rule(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._config(root)
            _story(root, 99, status="Done")           # <= US0100 cutoff
            _record_verdict(root, "US0099")           # verdict alone suffices
            u = _units(root)["US0099"]
            self.assertTrue(u["stages"]["critiqued"])

    def test_no_config_keeps_old_rule_everywhere(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 101, status="Done")
            _record_verdict(root, "US0101")
            u = _units(root)["US0101"]
            self.assertTrue(u["stages"]["critiqued"])


@unittest.skipUnless(HAS_YAML, "review.two_role_after reads .config.yaml (needs PyYAML)")
class SprintReviewCritiquedTests(unittest.TestCase):
    """US0247 / RFC0046 option B: a recorded sprint-level adversarial full-diff review satisfies
    the per-unit `critiqued` gate for the units in its range - both the verdict half (a covered
    unit needs no individual APPROVE) and the two-role evidence half - while a per-unit REJECT is
    still repaired per unit and the per-unit sign-off stays required."""

    def _config(self, root: Path) -> None:
        (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
        (root / "sdlc-studio" / ".config.yaml").write_text(
            "review:\n  two_role_after: US0100\n", encoding="utf-8")

    def test_sprint_review_clears_critiqued_for_covered_unit(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._config(root)
            _story(root, 101, status="Done")           # NO per-unit verdict
            c = _critic_mod()
            c.record_sprint_review(root, ["US0101"], reviewer="qa-seat", author="builder",
                                   verdict="APPROVE", findings="full-diff pass; none blocking")
            c.record_signoff(root, "US0101", principal="Darren Benson (operator)", author="builder")
            u = _units(root)["US0101"]
            self.assertTrue(u["stages"]["critiqued"])

    def test_SprintReview_does_not_override_a_per_unit_reject(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._config(root)
            _story(root, 101, status="Done")
            _record_verdict(root, "US0101", "reject")  # latest per-unit verdict is REJECT
            c = _critic_mod()
            c.record_sprint_review(root, ["US0101"], reviewer="qa-seat", author="builder",
                                   verdict="APPROVE", findings="range looks fine overall")
            c.record_signoff(root, "US0101", principal="operator", author="builder")
            u = _units(root)["US0101"]
            self.assertFalse(u["stages"]["critiqued"])   # REJECT repairs per unit
            self.assertIn("critiqued", u["missing"])

    def test_SprintReview_still_needs_the_per_unit_signoff(self) -> None:
        # The sprint pass is EVIDENCE, not the reviewer-of-record sign-off: a covered unit with no
        # sign-off does not clear the two-role gate.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._config(root)
            _story(root, 101, status="Done")
            c = _critic_mod()
            c.record_sprint_review(root, ["US0101"], reviewer="qa-seat", author="builder",
                                   verdict="APPROVE", findings="full-diff pass; none blocking")
            u = _units(root)["US0101"]
            self.assertFalse(u["stages"]["critiqued"])

    def test_SprintReview_refuses_self_review_and_empty(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            c = _critic_mod()
            with self.assertRaises(ValueError):        # reviewer == author
                c.record_sprint_review(root, ["US0101"], reviewer="bob", author="bob",
                                       verdict="APPROVE", findings="x")
            with self.assertRaises(ValueError):        # empty findings
                c.record_sprint_review(root, ["US0101"], reviewer="qa", author="bob",
                                       verdict="APPROVE", findings="")
            with self.assertRaises(ValueError):        # no covered units
                c.record_sprint_review(root, [], reviewer="qa", author="bob",
                                       verdict="APPROVE", findings="x")


if __name__ == "__main__":
    unittest.main()
