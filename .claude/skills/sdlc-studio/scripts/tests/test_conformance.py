"""Unit tests for conformance.py (RED first - the script does not exist yet).

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import shutil
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
            # `global_failures` (US0217) counts repo-wide failures attributed once rather
            # than charged to every unit; the gate adds it to `nonconformant` so that
            # reporting a failure differently never enforces less.
            self.assertEqual(set(data["summary"]),
                             {"total", "conformant", "nonconformant", "exempt", "ungroomed",
                              "global_failures"})


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


class GlobalAttributionTests(unittest.TestCase):
    """US0217: a repo-GLOBAL failure is one fact about the repo, not a defect in each unit.

    The `documented` stage is a repo-wide floor: one uncatalogued command failed it for
    every Done unit, so a single doc gap rendered as 118 non-conformant units - a true
    count of a misleading thing, which buried every genuine per-unit finding (L-0084).

    The report must attribute it once WITHOUT enforcing less: the gate still blocks, and
    the CLI still exits non-zero. Reporting better must never mean gating weaker."""

    def _conformant_done_repo(self, root, n=3, doc_ok=False):
        """n Done stories that are conformant except for the repo-wide doc floor.

        `doc_coverage` is a shared module object in sys.modules, so stubbing its `check`
        leaks into every later test in the process unless it is restored - patch and
        register the undo together so the two can never drift apart.
        """
        mod = _load()
        original = mod.doc_coverage.check
        self.addCleanup(setattr, mod.doc_coverage, "check", original)
        rows = []
        for i in range(1, n + 1):
            _story(root, i, status="Done", verified="yes")
            _record_verdict(root, f"US{i:04d}", "approve")
            rows.append(f"| [US{i:04d}](US{i:04d}-sample.md) | sample | Done |")
        (root / "sdlc-studio" / "stories" / "_index.md").write_text(
            "# Stories\n\n| ID | Title | Status |\n|---|---|---|\n" + "\n".join(rows) + "\n",
            encoding="utf-8")
        mod.doc_coverage.check = lambda _r: {"ok": doc_ok}
        return mod

    def test_global_failure_reported_once(self) -> None:
        """AC1: one entry in `globals`, and no unit charged with it."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = self._conformant_done_repo(root, n=3, doc_ok=False)
            result = mod.detect_conformance(root)
            docs = [g for g in result["globals"] if g["stage"] == "documented"]
            self.assertEqual(len(docs), 1)
            self.assertTrue(docs[0]["remedy"])
            for u in result["units"]:
                self.assertNotIn("documented", u["missing"])
            self.assertEqual(result["summary"]["nonconformant"], 0)

    def test_unit_records_global_separately(self) -> None:
        """AC2: nothing is hidden - it moves to `missing_global`."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = self._conformant_done_repo(root, n=2, doc_ok=False)
            for u in mod.detect_conformance(root)["units"]:
                self.assertIn("documented", u["missing_global"])
                self.assertFalse(u["stages"]["documented"])

    def test_global_failure_still_blocks(self) -> None:
        """AC3: the gate lane counts it and the CLI exits non-zero."""
        import io
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = self._conformant_done_repo(root, n=3, doc_ok=False)
            result = mod.detect_conformance(root)
            self.assertEqual(result["summary"]["global_failures"], 1)
            # the gate's own arithmetic: per-unit + global, so it still fails
            self.assertGreater(
                result["summary"]["nonconformant"] + result["summary"]["global_failures"], 0)
            with redirect_stdout(io.StringIO()) as buf:
                rc = mod.main(["check", "--root", str(root)])
            self.assertEqual(rc, 1)
            self.assertIn("REPO-WIDE documented", buf.getvalue())

    def test_per_unit_gaps_unaffected(self) -> None:
        """AC4: with no repo-wide failure, per-unit reporting is exactly as before."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = self._conformant_done_repo(root, n=1, doc_ok=True)
            _story(root, 9, status="Done", verified="no")   # a genuine per-unit gap
            result = mod.detect_conformance(root)
            self.assertEqual(result["globals"], [])
            self.assertEqual(result["summary"]["global_failures"], 0)
            u9 = next(u for u in result["units"] if u["id"] == "US0009")
            self.assertIn("verified", u9["missing"])
            self.assertEqual(u9["missing_global"], [])


class StampResolutionTests(unittest.TestCase):
    """BG0256: conformance must not count a Done story verified on a dead pointer."""

    def test_a_done_story_stamped_against_a_selector_that_resolves_to_nothing_is_not_verified(self) -> None:
        """The two calls differ in ONE argument. Everything else - the stamps, the index, the
        drift set - is held identical, so the assertion cannot pass on some other stage's
        behaviour. Without that, a fixture with unrelated conformance gaps would report
        `verified: False` either way and the test would prove nothing."""
        conformance = _load()
        dead = conformance._done_stages(".", "US9001", ["yes", "yes"], False, set(), True,
                                        dead_stamps=1)
        live = conformance._done_stages(".", "US9001", ["yes", "yes"], False, set(), True,
                                        dead_stamps=0)
        self.assertFalse(dead[0], "a green resting on a selector that selects nothing counted as verified")
        self.assertTrue(live[0], "a live stamp stopped counting as verified - the sign is flipped")


class ReviewPolicyTests(unittest.TestCase):
    """US0332 AC2: under carry-forward a REJECT does not block the close."""

    def _mods(self):
        import importlib.util, sys
        from pathlib import Path
        base = Path(__file__).resolve().parent.parent
        for name in ("carry_forward", "critic", "conformance"):
            spec = importlib.util.spec_from_file_location(name, base / f"{name}.py")
            m = importlib.util.module_from_spec(spec); sys.modules[name] = m
            spec.loader.exec_module(m)
        return sys.modules["conformance"], sys.modules["critic"]

    def _root(self, policy):
        d = Path(tempfile.mkdtemp(prefix="cf_conf_"))
        (d / "sdlc-studio").mkdir(parents=True)
        (d / "sdlc-studio" / ".config.yaml").write_text(f"review:\n  policy: {policy}\n")
        b = d / "sdlc-studio" / "bugs"; b.mkdir()
        (b / "BG9001-x.md").write_text("# BG9001: c\n\n> **Status:** Open\n> **Found-against:** US0001\n")
        return d

    def test_a_reject_under_carry_forward_does_not_block_the_close(self) -> None:
        conf, critic = self._mods()
        review = {"verdict": "REJECT", "reviewer": "qa", "author": "dev"}
        findings = [{"ref": "BG9001", "units": ["US0001"]}]
        d_cf = self._root("carry-forward")
        d_block = self._root("block")
        try:
            self.assertTrue(conf.carry_forward_covers(d_cf, review, findings))
            # under block, the same REJECT does NOT carry - the close still blocks
            self.assertFalse(conf.carry_forward_covers(d_block, review, findings))
            # an APPROVE is not a carry-forward case at all
            self.assertFalse(conf.carry_forward_covers(
                d_cf, {"verdict": "APPROVE", "reviewer": "qa", "author": "dev"}, findings))
        finally:
            shutil.rmtree(d_cf, ignore_errors=True); shutil.rmtree(d_block, ignore_errors=True)


class CarriedFindingLinkTests(unittest.TestCase):
    """US0335: a carried finding names the units it was found against, and the link survives
    the close of the sprint that produced it."""

    def _cf(self):
        import importlib.util, sys
        from pathlib import Path
        spec = importlib.util.spec_from_file_location(
            "carry_forward", Path(__file__).resolve().parent.parent / "carry_forward.py")
        m = importlib.util.module_from_spec(spec); sys.modules["carry_forward"] = m
        spec.loader.exec_module(m); return m

    def _root(self):
        d = Path(tempfile.mkdtemp(prefix="cf_link_"))
        (d / "sdlc-studio").mkdir(parents=True)
        (d / "sdlc-studio" / ".config.yaml").write_text("review:\n  policy: carry-forward\n")
        return d

    def test_a_carried_finding_naming_no_unit_is_refused(self) -> None:
        cf = self._cf(); d = self._root()
        try:
            b = d / "sdlc-studio" / "bugs"; b.mkdir(parents=True)
            (b / "BG9002-x.md").write_text("# BG9002: c\n\n> **Status:** Open\n")  # no Found-against
            with self.assertRaises(cf.PolicyError):
                cf.validate_carried(d, [{"ref": "BG9002", "units": []}])
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_a_carried_finding_still_resolves_after_its_sprint_closes(self) -> None:
        cf = self._cf(); d = self._root()
        try:
            b = d / "sdlc-studio" / "bugs"; b.mkdir(parents=True)
            # the finding names its units on its OWN file, so closing the run cannot strand it
            (b / "BG9003-x.md").write_text(
                "# BG9003: c\n\n> **Status:** Fixed\n> **Found-against:** US0007, US0008\n")
            self.assertEqual(cf.carried_finding_units(d, "BG9003"), ["US0007", "US0008"])
        finally:
            shutil.rmtree(d, ignore_errors=True)


def _ungroomed_story(root, num) -> None:
    """A refine-minted ungroomed story: its Acceptance Criteria are the placeholder marker
    (`sdlc_md.UNGROOMED_AC_MARKER`) rather than authored criteria."""
    marker = _load().sdlc_md.UNGROOMED_AC_MARKER
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"US{num:04d}-sample.md").write_text(
        f"# US{num:04d}: sample\n\n> **Status:** Draft\n"
        "> **Epic:** [EP0001: x](../epics/EP0001-x.md)\n\n"
        f"## Acceptance Criteria\n\n{marker}\n", encoding="utf-8")


class UngroomedMarkerTests(unittest.TestCase):
    """US0411: the count of ungroomed stories is machine-visible - conformance counts them by the
    marker, so an operator sees a refined backlog's grooming debt rather than meeting it at plan."""

    def test_ungroomed_stories_are_counted_by_their_marker(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            # Deliberately UNEQUAL groomed (3) and ungroomed (2), so a count that measured the
            # wrong set (the groomed ones) would read 3, not 2.
            _story(root, 1)                 # groomed (real ACs)
            _story(root, 2)                 # groomed
            _story(root, 5)                 # groomed
            _ungroomed_story(root, 3)       # ungroomed marker
            _ungroomed_story(root, 4)       # ungroomed marker
            result = _load().detect_conformance(root)
            self.assertEqual(result["summary"]["ungroomed"], 2)
            flagged = {u["id"] for u in result["units"] if u["ungroomed"]}
            self.assertEqual(flagged, {"US0003", "US0004"})
            # a groomed story is not miscounted, and the marker does not read as a specified AC
            self.assertFalse(_units(root)["US0003"]["stages"]["specified"])


if __name__ == "__main__":
    unittest.main()
