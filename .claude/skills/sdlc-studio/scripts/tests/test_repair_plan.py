"""EP0106: the repair-plan gate. Every test names the AC it verifies."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _load(name):
    spec = importlib.util.spec_from_file_location(
        name, Path(__file__).resolve().parent.parent / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


repair_plan = _load("repair_plan")
critic = _load("critic")


def _entry(finding, change="rewrite the branch", approach="derive from the runner",
           risk="a false refusal costs one manual", design=None):
    e = {"finding": finding, "change": change, "approach": approach, "risk": risk}
    if design:
        e["design"] = design
    return e


class _Root:
    def __init__(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="repair_plan_test_"))
        (self.tmp / "sdlc-studio" / ".local").mkdir(parents=True)

    def cleanup(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)


class RepairPlanTests(unittest.TestCase):
    """US0311: a REJECT verdict produces a written repair plan, one entry per finding."""

    def setUp(self):
        self.r = _Root()

    def tearDown(self):
        self.r.cleanup()

    def test_a_plan_missing_an_entry_for_any_finding_is_refused(self) -> None:
        # AC1: a plan with fewer entries than the verdict has findings leaves a defect
        # silently unanswered.
        with self.assertRaises(ValueError) as cm:
            repair_plan.record_repair_plan(
                self.r.tmp, "RP1", "REJECT", ["F1", "F2"], [_entry("F1")], "author-a")
        self.assertIn("F2", str(cm.exception))
        # the complete plan is accepted
        p = repair_plan.record_repair_plan(
            self.r.tmp, "RP1", "REJECT", ["F1", "F2"],
            [_entry("F1"), _entry("F2")], "author-a")
        self.assertTrue(p.exists())

    def test_an_entry_without_an_approach_or_a_risk_is_refused(self) -> None:
        # AC2: an entry without an approach is a restatement; without a risk it asserts the
        # repair is free.
        with self.assertRaises(ValueError) as cm:
            repair_plan.record_repair_plan(
                self.r.tmp, "RP1", "REJECT", ["F1"],
                [_entry("F1", approach="")], "author-a")
        self.assertIn("approach", str(cm.exception))
        with self.assertRaises(ValueError) as cm:
            repair_plan.record_repair_plan(
                self.r.tmp, "RP2", "REJECT", ["F1"],
                [_entry("F1", risk="")], "author-a")
        self.assertIn("risk", str(cm.exception))

    def test_a_repair_plan_against_a_non_reject_verdict_is_refused(self) -> None:
        # AC3: a plan cannot be manufactured to launder a change nobody rejected.
        for verdict in ("APPROVE", "approve", ""):
            with self.subTest(verdict=verdict):
                with self.assertRaises(ValueError):
                    repair_plan.record_repair_plan(
                        self.r.tmp, "RP1", verdict, ["F1"], [_entry("F1")], "author-a")


class RepairPlanReviewTests(unittest.TestCase):
    """US0312: the plan is attacked by an independent pass before any code is written."""

    def setUp(self):
        self.r = _Root()

    def tearDown(self):
        self.r.cleanup()

    def _plan(self):
        return repair_plan.record_repair_plan(
            self.r.tmp, "RP1", "REJECT", ["F1"], [_entry("F1")], "author-a")

    def test_a_repair_without_a_plan_verdict_is_refused(self) -> None:
        # AC1: with the gate on, a repair naming no reviewed plan is refused.
        _write_config(self.r.tmp, "on")
        self._plan()
        with self.assertRaises(ValueError):
            repair_plan.repair_gate(self.r.tmp, "RP1")  # planned but unreviewed

    def test_the_plan_author_cannot_record_its_own_verdict(self) -> None:
        # AC2: self-approval refused, on the story-plan gate's rule.
        self._plan()
        with self.assertRaises(ValueError):
            repair_plan.review_repair_plan(self.r.tmp, "RP1", "APPROVE", "author-a", "author-a")

    def test_a_brief_missing_any_of_the_four_questions_is_refused(self) -> None:
        # AC3: the brief carries the four questions this loop keeps failing.
        good = repair_plan.build_brief()
        repair_plan.validate_brief(good)  # does not raise
        self.assertEqual(len(repair_plan.FOUR_QUESTIONS), 4)
        for i in range(4):
            bad = {"questions": [q for j, q in enumerate(repair_plan.FOUR_QUESTIONS) if j != i]}
            with self.subTest(dropped=i):
                with self.assertRaises(ValueError):
                    repair_plan.validate_brief(bad)

    def test_a_verdict_recorded_after_the_repair_does_not_satisfy_the_gate(self) -> None:
        # AC4: a review that followed the work describes it rather than attacking it.
        _write_config(self.r.tmp, "on")
        self._plan()
        repair_plan.review_repair_plan(self.r.tmp, "RP1", "APPROVE", "reviewer-b", "author-a")
        with self.assertRaises(ValueError):
            repair_plan.repair_gate(self.r.tmp, "RP1",
                                    repaired_at="2026-07-22T10:00:00Z",
                                    plan_reviewed_at="2026-07-22T11:00:00Z")
        # a review BEFORE the repair is fine
        res = repair_plan.repair_gate(self.r.tmp, "RP1",
                                      repaired_at="2026-07-22T11:00:00Z",
                                      plan_reviewed_at="2026-07-22T10:00:00Z")
        self.assertTrue(res["ok"])


class RepairPlanPinTests(unittest.TestCase):
    """US0313: a verdict is pinned to the findings it answered."""

    def setUp(self):
        self.r = _Root()

    def tearDown(self):
        self.r.cleanup()

    def test_a_verdict_stores_a_fingerprint_of_the_findings_it_answered(self) -> None:
        # AC1
        repair_plan.record_repair_plan(
            self.r.tmp, "RP1", "REJECT", ["F1", "F2"],
            [_entry("F1"), _entry("F2")], "author-a")
        repair_plan.review_repair_plan(self.r.tmp, "RP1", "APPROVE", "reviewer-b", "author-a")
        v = critic.verdict_for(self.r.tmp, "RP1", phase="plan-review")
        self.assertIn("findings-hash=", v["issues"])

    def test_a_finding_added_after_the_verdict_invalidates_it(self) -> None:
        # AC2
        p = repair_plan.record_repair_plan(
            self.r.tmp, "RP1", "REJECT", ["F1"], [_entry("F1")], "author-a")
        repair_plan.review_repair_plan(self.r.tmp, "RP1", "APPROVE", "reviewer-b", "author-a")
        self.assertTrue(repair_plan.plan_reviewed(self.r.tmp, "RP1")["ok"])
        # a later round adds a finding
        import json
        plan = json.loads(p.read_text())
        plan["findings"].append("F2")
        plan["entries"].append(_entry("F2"))
        p.write_text(json.dumps(plan))
        self.assertFalse(repair_plan.plan_reviewed(self.r.tmp, "RP1")["ok"])

    def test_reordering_and_whitespace_do_not_invalidate_a_verdict(self) -> None:
        # AC3
        a = repair_plan.findings_fingerprint(["F1", "F2  extra", "F3"])
        b = repair_plan.findings_fingerprint(["F3", "F1", "F2 extra"])
        self.assertEqual(a, b)
        c = repair_plan.findings_fingerprint(["F1", "F2", "F3", "F4"])
        self.assertNotEqual(a, c)


class RepairPlanConfigTests(unittest.TestCase):
    """US0315: the gate is opt-in per project and OFF by default."""

    def setUp(self):
        self.r = _Root()

    def tearDown(self):
        self.r.cleanup()

    def test_an_absent_config_leaves_the_close_unchanged(self) -> None:
        # AC1: no config -> nothing refused, an upgrading project sees no change.
        res = repair_plan.repair_gate(self.r.tmp, None)
        self.assertTrue(res["ok"])

    def test_enabling_the_gate_refuses_an_unplanned_repair(self) -> None:
        # AC2
        _write_config(self.r.tmp, "on")
        with self.assertRaises(ValueError) as cm:
            repair_plan.repair_gate(self.r.tmp, None)
        self.assertIn(repair_plan.GATE_KEY, str(cm.exception))

    def test_the_documented_key_is_the_key_the_code_reads(self) -> None:
        # AC3: the key the reference names is the key the code reads - taken from the docs,
        # not restated here. BG0250 shipped a key four documents claimed was read and no code
        # read; a hand-copied constant in a test would reproduce it.
        ref = (Path(__file__).resolve().parents[2] / "reference-config.md").read_text()
        self.assertIn(repair_plan.GATE_KEY, ref,
                      "the gate key the code reads is not documented in reference-config.md")


class DesignDecisionTests(unittest.TestCase):
    """US0343: a repeat-class repair must decide retain-or-change, not propose a better
    instance forever."""

    def setUp(self):
        self.r = _Root()

    def tearDown(self):
        self.r.cleanup()

    def _round(self, plan_id, design=None):
        return repair_plan.record_repair_plan(
            self.r.tmp, plan_id, "REJECT", ["class:enumerate"],
            [_entry("class:enumerate", design=design)], "author-a")

    def test_a_repeat_class_plan_without_a_retain_or_change_statement_is_refused(self) -> None:
        self._round("RP1")  # first time: no declaration needed
        with self.assertRaises(ValueError) as cm:
            self._round("RP2")  # second: same class, no design declared
        self.assertIn("RETAINED or CHANGED", str(cm.exception))

    def test_past_the_threshold_a_retained_design_is_refused_and_names_the_failed_rounds(self) -> None:
        self._round("RP1")
        self._round("RP2", design="change")
        # now the class has 2 prior rounds; threshold is 2, so a RETAIN is refused
        with self.assertRaises(ValueError) as cm:
            self._round("RP3", design="retain")
        self.assertIn("2 round", str(cm.exception))

    def test_a_reasoned_retain_below_the_threshold_is_accepted_and_its_reason_stored(self) -> None:
        self._round("RP1")
        p = self._round("RP2", design="retain")  # 1 prior round, below threshold 2
        import json
        self.assertEqual(json.loads(p.read_text())["entries"][0]["design"], "retain")

    def test_the_default_threshold_carries_its_basis_and_a_project_value_overrides_it(self) -> None:
        thr = repair_plan.design_threshold(self.r.tmp)
        self.assertEqual(thr["value"], 2)
        self.assertTrue(thr["basis"].strip())
        _write_config(self.r.tmp, "on", extra="  repair_design_threshold: 4\n")
        self.assertEqual(repair_plan.design_threshold(self.r.tmp)["value"], 4)


class ApproachQuestionBriefTests(unittest.TestCase):
    """US0344: the reviewer is asked whether the approach itself is the defect."""

    def setUp(self):
        self.r = _Root()

    def tearDown(self):
        self.r.cleanup()

    def test_a_repeat_class_brief_missing_the_approach_question_is_refused(self) -> None:
        brief = repair_plan.build_brief(prior_findings=["v1: enumerate spellings"])
        self.assertIn(repair_plan.APPROACH_QUESTION, brief["questions"])
        repair_plan.validate_brief(brief)  # ok
        brief["questions"] = [q for q in brief["questions"]
                              if q != repair_plan.APPROACH_QUESTION]
        with self.assertRaises(ValueError):
            repair_plan.validate_brief(brief)

    def test_the_brief_enumerates_the_previous_approaches_and_their_failures(self) -> None:
        prior = ["v1: enumerate spellings, beaten by a glob",
                 "v2: flag-aware split, beaten by a bare directory"]
        brief = repair_plan.build_brief(prior_findings=prior)
        self.assertEqual(brief["prior_approaches"], prior)
        # a first-round brief carries no prior approaches and no approach question
        first = repair_plan.build_brief()
        self.assertEqual(first["prior_approaches"], [])
        self.assertNotIn(repair_plan.APPROACH_QUESTION, first["questions"])


def _write_config(root: Path, gate: str, extra: str = "") -> None:
    cfg = root / "sdlc-studio" / ".config.yaml"
    cfg.write_text(f"review:\n  repair_plan_gate: {gate}\n{extra}", encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
