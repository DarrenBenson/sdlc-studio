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


class UntokenedVerdictPinTests(unittest.TestCase):
    """BG0267: a plan verdict carrying NO findings-hash token was passing the pin check
    vacuously, because `if m and m.group(1) != current` short-circuits on the missing match.

    The untokened case is now decided deliberately: nothing pins the verdict to a finding set,
    so it is NOT pinned and does not satisfy the gate. Unreachable through
    `review_repair_plan` (which always writes the token), which is exactly the case a guard
    exists for: a verdict recorded straight through `critic.record_verdict`, or hand-edited.
    """

    def setUp(self):
        self.r = _Root()

    def tearDown(self):
        self.r.cleanup()

    def _plan(self, findings=("F1",)):
        return repair_plan.record_repair_plan(
            self.r.tmp, "RP1", "REJECT", list(findings),
            [_entry(f) for f in findings], "author-a")

    def test_an_untokened_verdict_is_not_treated_as_pinned(self) -> None:
        # AC1: an APPROVE recorded with an issues field that carries no `plan-hash=`, the pin.
        # Under the repair plan's own kind, the only kind `plan_reviewed` reads: recorded under
        # the default kind it would be refused as no APPROVE at all, and the assertion on the
        # REASON below is what keeps this test about the missing pin. The findings-only token
        # an earlier build wrote is not a pin either: it answers the finding set, not the plan.
        import json
        plan = json.loads(self._plan().read_text(encoding="utf-8"))
        issues = ("plan=RP1", f"plan=RP1; findings-hash={plan['fingerprint']}")
        for n, cell in enumerate(issues):
            with self.subTest(issues=cell):
                root = self.r.tmp
                if n:
                    other = _Root()
                    self.addCleanup(other.cleanup)
                    root = other.tmp
                    repair_plan.record_repair_plan(root, "RP1", "REJECT", ["F1"],
                                                   [_entry("F1")], "author-a")
                critic.record_verdict(root, "RP1", "APPROVE", "reviewer-b", "author-a",
                                      cell, phase="plan-review",
                                      kind=critic.REPAIR_PLAN_KIND)
                res = repair_plan.plan_reviewed(root, "RP1")
                self.assertFalse(res["ok"], f"an unpinned verdict was honoured: {res}")
                # the REASON must name the missing pin, not some other refusal (independence,
                # no APPROVE) - otherwise this would pass while the hole stayed open behind it
                self.assertIn("plan-hash", res["reason"])
                # and the gate built on it refuses the repair
                _write_config(root, "on")
                with self.assertRaises(ValueError) as cm:
                    repair_plan.repair_gate(root, "RP1")
                self.assertIn("plan-hash", str(cm.exception))

    def test_a_correctly_pinned_verdict_still_passes(self) -> None:
        # AC2: the positive control - the fix narrows only the untokened hole. A blanket
        # refusal would kill the shipped path and pass AC1 on its own.
        plan = self._plan()
        repair_plan.review_repair_plan(self.r.tmp, "RP1", "APPROVE", "reviewer-b", "author-a")
        v = critic.verdict_for(self.r.tmp, "RP1", phase="plan-review")
        import json
        stored = json.loads(plan.read_text())
        self.assertIn(f"findings-hash={stored['fingerprint']}",
                      v["issues"])                       # records THIS finding set
        self.assertIn(f"plan-hash={repair_plan.plan_fingerprint(stored)}",
                      v["issues"])                       # and is pinned to THIS plan
        res = repair_plan.plan_reviewed(self.r.tmp, "RP1")
        self.assertTrue(res["ok"], res["reason"])
        _write_config(self.r.tmp, "on")
        self.assertTrue(repair_plan.repair_gate(self.r.tmp, "RP1")["ok"])


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


_SCRIPTS = Path(__file__).resolve().parent.parent

_BUG = ("# BG0001: b\n\n> **Status:** In Progress\n> **Severity:** medium\n"
        "> **Verification depth:** functional\n\n## Summary\n\nx\n\n## Steps to Reproduce\n\n"
        "1. x\n\n## Proposed Fix\n\ny\n\n## Acceptance Criteria\n\n"
        "- [x] the defect no longer reproduces\n")


def _story_text(sid: str, provenance: str) -> str:
    # Review, one manual criterion stamped verified: the story passes the AC-verify gate, and
    # with neither `review.two_role_after` nor `review.test_plan_after` set no other Done gate
    # applies - so the only thing that can refuse it is the gate under test.
    return (f"# {sid}: s\n\n> **Status:** Review\n> {provenance}\n\n## Acceptance Criteria\n\n"
            f"### AC1\n- **Verify:** manual a human looked\n- **Verified:** yes (2026-01-01)\n")


def _run(root: Path, script: str, *argv: str) -> tuple[int, str]:
    """Drive a script through its SHIPPED ENTRY POINT, stdout and stderr merged: the wiring
    between the command and the library is the thing these criteria are about."""
    import subprocess
    p = subprocess.run([sys.executable, str(_SCRIPTS / script), "--root", str(root), *argv],
                       capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


class RepairGateIsReachableTests(unittest.TestCase):
    """BG0673: the repair-plan gate shipped with a library check nothing called. No command
    recorded a plan or its verdict, and turning `review.repair_plan_gate` on refused nothing a
    delivery command ran. Every test here goes in through the commands."""

    def setUp(self):
        self.r = _Root()
        self.root = self.r.tmp

    def tearDown(self):
        self.r.cleanup()

    def _fresh(self) -> Path:
        r = _Root()
        self.addCleanup(r.cleanup)
        return r.tmp

    def _bug(self, root: Path, gate: str | None, bid: str = "BG0001") -> Path:
        bugs = root / "sdlc-studio" / "bugs"
        bugs.mkdir(parents=True, exist_ok=True)
        path = bugs / f"{bid}-x.md"
        path.write_text(_BUG.replace("BG0001", bid), encoding="utf-8")
        if gate is not None:
            _write_config(root, gate)
        return path

    def _story(self, root: Path, sid: str, provenance: str) -> Path:
        stories = root / "sdlc-studio" / "stories"
        stories.mkdir(parents=True, exist_ok=True)
        path = stories / f"{sid}-x.md"
        path.write_text(_story_text(sid, provenance), encoding="utf-8")
        return path

    @staticmethod
    def _status(path: Path) -> str:
        import re
        return re.search(r"\*\*Status:\*\*\s*(.+)", path.read_text(encoding="utf-8")).group(1)

    def _record_plan(self, root: Path, unit: str = "BG0001", author: str = "author-a"):
        import json
        doc = root / "plan.json"
        doc.write_text(json.dumps({"verdict": "REJECT", "findings": ["F1"],
                                   "entries": [_entry("F1")]}), encoding="utf-8")
        return _run(root, "repair_plan.py", "record", "--unit", unit, "--author", author,
                    "--plan-file", str(doc))

    def _plan_rows(self, root: Path, unit: str = "BG0001") -> list[dict]:
        return [v for v in critic.read_verdicts(root, "plan-review") if v["unit"] == unit]

    def _test_plan_reject(self, root: Path, unit: str = "BG0001") -> None:
        rc, out = _run(root, "critic.py", "record", "--unit", unit, "--phase", "plan-review",
                       "--kind", "test-plan", "--verdict", "REJECT",
                       "--issues", "the fixture cannot reach the branch",
                       "--reviewer", "qa-seat", "--author", "author-a",
                       "--brief", "0123456789ab")
        self.assertEqual(rc, 0, out)

    def test_the_gate_refuses_at_the_terminal_transition(self) -> None:
        """AC1. Must fail on: the gate's ValueError returned as the advisory `gate_warn` so the
        write proceeds; or the gate asked only at Done, so a bug reaching Fixed is never
        checked. Either leaves the bug Fixed and the exit 0."""
        bug = self._bug(self.root, "on")
        rc, out = _run(self.root, "transition.py", "set", "BG0001", "Fixed")
        self.assertNotEqual(rc, 0, out)
        # THIS gate's key, not a refusal: other gates also refuse a bug going to Fixed
        self.assertIn(repair_plan.GATE_KEY, out)
        self.assertIn("blocked", out)
        self.assertEqual(self._status(bug), "In Progress", "the refused transition was written")

    def test_a_plan_and_verdict_record_through_the_cli(self) -> None:
        """AC2. Must fail on: a `record` verb with no `review` verb; or a `review` verb that
        writes through `critic.record_verdict` directly, skipping the independence check
        against the plan's recorded author."""
        import json
        self._bug(self.root, None)
        rc, out = self._record_plan(self.root)
        self.assertEqual(rc, 0, out)
        stored = json.loads((self.root / "sdlc-studio" / ".local" / "repair-plans"
                             / "BG0001.json").read_text(encoding="utf-8"))
        self.assertEqual((stored["plan_id"], stored["author"]), ("BG0001", "author-a"),
                         "the plan is keyed to the unit it repairs")
        # keyed to a unit that EXISTS: an id nothing carries is one no transition asks for
        rc, out = self._record_plan(self.root, unit="BG0999")
        self.assertNotEqual(rc, 0, out)
        self.assertIn("names no artefact", out)
        # a plan file that is not a JSON object is refused, naming the shape, and nothing stored
        bad = self.root / "list.json"
        bad.write_text(json.dumps(["F1"]), encoding="utf-8")
        rc, out = _run(self.root, "repair_plan.py", "record", "--unit", "BG0001",
                       "--author", "author-b", "--plan-file", str(bad))
        self.assertNotEqual(rc, 0, out)
        self.assertIn("must be a JSON object", out)
        kept = json.loads((self.root / "sdlc-studio" / ".local" / "repair-plans"
                           / "BG0001.json").read_text(encoding="utf-8"))
        self.assertEqual(kept["author"], "author-a", "a refused plan file overwrote the plan")
        # the plan's own author as reviewer: refused, naming independence, and nothing written
        rc, out = _run(self.root, "repair_plan.py", "review", "--unit", "BG0001",
                       "--verdict", "APPROVE", "--reviewer", "author-a")
        self.assertNotEqual(rc, 0, out)
        self.assertIn("not independent", out)
        self.assertEqual(self._plan_rows(self.root), [], "a self-review wrote a verdict row")
        # the positive case: a different reviewer's verdict is written
        rc, out = _run(self.root, "repair_plan.py", "review", "--unit", "BG0001",
                       "--verdict", "APPROVE", "--reviewer", "reviewer-b")
        self.assertEqual(rc, 0, out)
        rows = self._plan_rows(self.root)
        self.assertEqual([(v["verdict"], v["reviewer"], v["author"]) for v in rows],
                         [("APPROVE", "reviewer-b", "author-a")])

    def test_the_gate_off_changes_nothing(self) -> None:
        """AC3. Must fail on: the transition calling `plan_reviewed` directly, bypassing the
        `gate_enabled` check `repair_gate` makes; or echoing the gate-off reason, which names
        the key, as a warning."""
        for gate in ("off", None):                       # set off, and never set at all
            with self.subTest(gate=gate):
                root = self._fresh()
                bug = self._bug(root, gate)
                rc, out = _run(root, "transition.py", "set", "BG0001", "Fixed")
                self.assertEqual(rc, 0, out)
                self.assertEqual(self._status(bug), "Fixed")
                self.assertNotIn(repair_plan.GATE_KEY, out)
        # the pair: the SAME fixture with the setting on is refused, so the leg above is the
        # setting's doing and not a transition that never asks the gate at all
        bug = self._bug(self.root, "on")
        rc, out = _run(self.root, "transition.py", "set", "BG0001", "Fixed")
        self.assertNotEqual(rc, 0, out)
        self.assertIn(repair_plan.GATE_KEY, out)
        self.assertEqual(self._status(bug), "In Progress")

    def test_a_repair_plan_approval_is_not_a_spec_plan_review(self) -> None:
        """AC4. Must fail on: `review_repair_plan` writing without the kind, so the approval
        lands under the default `spec` kind; or writing twice, once under each."""
        self._bug(self.root, None)
        self.assertEqual(self._record_plan(self.root)[0], 0)
        rc, out = _run(self.root, "repair_plan.py", "review", "--unit", "BG0001",
                       "--verdict", "APPROVE", "--reviewer", "reviewer-b")
        self.assertEqual(rc, 0, out)
        self.assertIn(critic.REPAIR_PLAN_KIND, critic.PLAN_REVIEW_KINDS)
        self.assertEqual([v["kind"] for v in self._plan_rows(self.root)],
                         [critic.REPAIR_PLAN_KIND], "exactly one row, of the repair plan's kind")
        for kind in ("spec", "test-plan"):
            with self.subTest(kind=kind):
                self.assertIsNone(critic.verdict_for(self.root, "BG0001", phase="plan-review",
                                                     kind=kind),
                                  f"a repair-plan approval answered the {kind} lookup")
        v = critic.verdict_for(self.root, "BG0001", phase="plan-review",
                               kind=critic.REPAIR_PLAN_KIND)
        self.assertIsNotNone(v)
        self.assertEqual(v["verdict"], "APPROVE")

    def test_the_gate_holds_repair_stories_and_spares_decision_terminals(self) -> None:
        """AC5. Must fail on: the gate asked of bugs only; asked at every terminal status
        rather than Done and Fixed; asked of every unit reaching Done; or reading a story's
        `Parent` and never its `Delivers`."""
        repair_stories = (("US0001", "**Parent:** BG0002"), ("US0002", "**Delivers:** RV0001"))
        root = self.root
        _write_config(root, "on")
        for sid, prov in repair_stories:
            with self.subTest(story=sid, gate="on"):
                path = self._story(root, sid, prov)
                rc, out = _run(root, "transition.py", "set", sid, "Done")
                self.assertNotEqual(rc, 0, out)
                self.assertIn(repair_plan.GATE_KEY, out)
                self.assertEqual(self._status(path), "Review")
        with self.subTest(spared="a bug set to Won't Fix"):
            self._bug(root, None)
            rc, out = _run(root, "transition.py", "set", "BG0001", "Won't Fix")
            self.assertNotIn(repair_plan.GATE_KEY, out)
        with self.subTest(spared="a story whose Parent names an epic"):
            path = self._story(root, "US0003", "**Parent:** EP0001")
            rc, out = _run(root, "transition.py", "set", "US0003", "Done")
            self.assertNotIn(repair_plan.GATE_KEY, out)
            self.assertEqual((rc, self._status(path)), (0, "Done"), out)
        # the same two repair stories reach Done with the setting off: each passes every other
        # Done gate, so the refusals above are this gate's and nothing else's
        off = self._fresh()
        _write_config(off, "off")
        for sid, prov in repair_stories:
            with self.subTest(story=sid, gate="off"):
                path = self._story(off, sid, prov)
                rc, out = _run(off, "transition.py", "set", sid, "Done")
                self.assertEqual((rc, self._status(path)), (0, "Done"), out)

    def test_a_repair_plan_reject_does_not_hold_the_test_plan_repair_clause(self) -> None:
        """AC6. Must fail on: `repair_state` reading every plan-review row, so the repair plan's
        `plan=` and `findings-hash=` cells count as outstanding findings; or `record_repair`
        looking up the live REJECT with no kind, so a closure is accepted against a repair-plan
        rejection."""
        for gate in ("on", "off"):
            with self.subTest(gate=gate):
                root = self._fresh()
                self._bug(root, gate)
                self._test_plan_reject(root)
                rc, out = _run(root, "critic.py", "repair", "--unit", "BG0001",
                               "--phase", "plan-review", "--author", "author-a",
                               "--closed", "the fixture cannot reach the branch -> rewrote "
                                           "the fixture so the branch is reached")
                self.assertEqual(rc, 0, out)
                self.assertEqual(critic.plan_review_repair_clears(root, "BG0001"), (True, ""))
                self.assertEqual(self._record_plan(root)[0], 0)
                rc, out = _run(root, "repair_plan.py", "review", "--unit", "BG0001",
                               "--verdict", "REJECT", "--reviewer", "reviewer-b")
                self.assertEqual(rc, 0, out)
                self.assertEqual([v["kind"] for v in self._plan_rows(root)
                                  if v["verdict"] == "REJECT"],
                                 ["test-plan", critic.REPAIR_PLAN_KIND])
                self.assertEqual(critic.plan_review_repair_clears(root, "BG0001"), (True, ""))
        # a unit whose ONLY plan-review REJECT is a repair plan's: nothing for `repair` to answer
        closure = ("--closed", "#1 -> revised the plan")
        only = self._fresh()
        self._bug(only, None)
        self.assertEqual(self._record_plan(only)[0], 0)
        self.assertEqual(_run(only, "repair_plan.py", "review", "--unit", "BG0001",
                              "--verdict", "REJECT", "--reviewer", "reviewer-b")[0], 0)
        rc, out = _run(only, "critic.py", "repair", "--unit", "BG0001", "--phase",
                       "plan-review", "--author", "author-a", *closure)
        self.assertNotEqual(rc, 0, out)
        self.assertIn("no live REJECT", out)
        self.assertEqual(critic.repairs_for(only, "BG0001"), [], "a repair row was appended")
        # the same command on a unit carrying a test-plan REJECT is accepted
        tp = self._fresh()
        self._bug(tp, None)
        self._test_plan_reject(tp)
        rc, out = _run(tp, "critic.py", "repair", "--unit", "BG0001", "--phase",
                       "plan-review", "--author", "author-a", *closure)
        self.assertEqual(rc, 0, out)
        self.assertEqual(len(critic.repairs_for(tp, "BG0001")), 1)

    def test_the_gate_on_lets_an_independently_approved_plan_reach_fixed(self) -> None:
        """AC7, the gate-on positive control. Must fail on: the transition handing
        `repair_gate` None, or an `RP-` id derived from the unit id, rather than the unit's own
        id; or `plan_reviewed` reading kind `spec`, or no kind at all, rather than the repair
        plan's. The earlier test-plan REJECT on the bug is what a kind-blind read trips on."""
        bug = self._bug(self.root, "on")
        self._test_plan_reject(self.root)
        rc, out = self._record_plan(self.root, author="author-a")
        self.assertEqual(rc, 0, out)
        rc, out = _run(self.root, "repair_plan.py", "review", "--unit", "BG0001",
                       "--verdict", "APPROVE", "--reviewer", "reviewer-b")
        self.assertEqual(rc, 0, out)
        # the shipped gate verb answers the same question the transition asks, by unit id and
        # through its --plan alias
        for flag in ("--unit", "--plan"):
            rc, out = _run(self.root, "repair_plan.py", "gate", flag, "bg0001")
            self.assertEqual(rc, 0, f"{flag}: {out}")
        rc, out = _run(self.root, "transition.py", "set", "BG0001", "Fixed")
        self.assertEqual(rc, 0, out)
        self.assertEqual(self._status(bug), "Fixed")
        self.assertNotIn(repair_plan.GATE_KEY, out)

    # --- BG0678: rounds, the brief key, the whole-plan pin and plan-author independence -------

    def _round(self, root: Path, findings, entries, unit: str = "BG0001",
               author: str = "author-a") -> tuple[int, str]:
        """Record one round of `unit`'s plan through the shipped `record` verb."""
        import json
        doc = root / "plan.json"
        doc.write_text(json.dumps({"verdict": "REJECT", "findings": list(findings),
                                   "entries": list(entries)}), encoding="utf-8")
        return _run(root, "repair_plan.py", "record", "--unit", unit, "--author", author,
                    "--plan-file", str(doc))

    def _ok_round(self, root: Path, findings, entries, **kw) -> None:
        rc, out = self._round(root, findings, entries, **kw)
        self.assertEqual(rc, 0, out)

    def _review(self, root: Path, verdict: str, reviewer: str, unit: str = "BG0001") -> None:
        rc, out = _run(root, "repair_plan.py", "review", "--unit", unit, "--verdict", verdict,
                       "--reviewer", reviewer)
        self.assertEqual(rc, 0, out)

    def _gate(self, root: Path, unit: str = "BG0001") -> tuple[int, str]:
        return _run(root, "repair_plan.py", "gate", "--unit", unit)

    @staticmethod
    def _key(findings) -> str:
        """The Brief cell `repair_plan.py review` writes: the first 12 hex characters of the
        findings fingerprint, the length `critic.py record --brief` accepts."""
        return repair_plan.findings_fingerprint(findings)[:12]

    def _repair_rows(self, root: Path, unit: str = "BG0001") -> list[dict]:
        return [v for v in self._plan_rows(root, unit) if v["kind"] == critic.REPAIR_PLAN_KIND]

    def _stored_rounds(self, root: Path) -> list[Path]:
        """The round files on disk, counted straight off the directory rather than through
        the module under test, so a counter that miscounts cannot also mis-report."""
        return sorted((root / "sdlc-studio" / ".local" / "repair-plans").glob("*.json"))

    def _critic_approve(self, root: Path, reviewer: str, author: str,
                        unit: str = "BG0001") -> None:
        """An APPROVE written through `critic.py record`, not `repair_plan.py review`, carrying
        exactly the brief and pin `review` would write for the current round - so the only
        thing that can refuse it is who reviewed it."""
        plan = repair_plan.load_plan(root, unit)
        fp = repair_plan.findings_fingerprint(plan["findings"])
        rc, out = _run(root, "critic.py", "record", "--unit", unit, "--phase", "plan-review",
                       "--kind", critic.REPAIR_PLAN_KIND, "--verdict", "APPROVE",
                       "--reviewer", reviewer, "--author", author, "--brief", fp[:12],
                       "--issues", f"plan={unit}; findings-hash={fp}; "
                                   f"plan-hash={repair_plan.plan_fingerprint(plan)}")
        self.assertEqual(rc, 0, out)
        row = self._repair_rows(root, unit)[-1]
        self.assertEqual((row["reviewer"], row["author"], row["brief"]),
                         (reviewer, author, fp[:12]), "the row did not read back as written")

    def _refused_at_fixed(self, root: Path, why: str) -> str:
        bug = root / "sdlc-studio" / "bugs" / "BG0001-x.md"
        rc, out = _run(root, "transition.py", "set", "BG0001", "Fixed")
        self.assertNotEqual(rc, 0, out)
        self.assertIn(repair_plan.GATE_KEY, out)
        self.assertIn(why, out)
        self.assertEqual(self._status(bug), "In Progress", "the refused transition was written")
        return out

    def test_each_missing_plan_state_is_refused_by_unit_id(self) -> None:
        """BG0678 AC1. Must fail on: the no-plan refusal worded as the unreviewed one, so the
        two causes are not named apart; the transition asking for the most recently written
        plan rather than the unit's own; `plan_reviewed` dropping `critic.is_independent`
        (case 4, whose reviewer is the row's Author but not the plan's); dropping the stored
        plan author, or reading only the newest round's (case 5, whose reviewer wrote round
        one and whose row names round two's author)."""
        no_plan, no_verdict = "no repair plan is recorded for BG0001", "has no verdict"
        with self.subTest(case="1: nothing recorded for the unit"):
            root = self._fresh()
            self._bug(root, "on")
            self.assertNotIn(no_verdict, self._refused_at_fixed(root, no_plan))
        with self.subTest(case="2: only an approved plan for a DIFFERENT unit, written last"):
            root = self._fresh()
            self._bug(root, "on")
            self._bug(root, None, "BG0002")
            self._ok_round(root, ["F1"], [_entry("F1")], unit="BG0002")
            self._review(root, "APPROVE", "reviewer-b", unit="BG0002")
            self.assertTrue(repair_plan.plan_reviewed(root, "BG0002")["ok"],
                            "the other unit's plan must be approved, or this proves nothing")
            self._refused_at_fixed(root, no_plan)
        with self.subTest(case="3: a plan with no verdict"):
            root = self._fresh()
            self._bug(root, "on")
            self._ok_round(root, ["F1"], [_entry("F1")])
            self.assertNotIn(no_plan, self._refused_at_fixed(root, no_verdict))
        with self.subTest(case="4: reviewer = the row's Author, the plan's author a third"):
            root = self._fresh()
            bug = self._bug(root, "on")
            self._ok_round(root, ["F1"], [_entry("F1")], author="author-a")
            self._critic_approve(root, reviewer="bob", author="bob")
            self._refused_at_fixed(root, "not independent")
            # the same record naming a third identity, on the same plan: it passes
            self._critic_approve(root, reviewer="zed", author="bob")
            self.assertTrue(repair_plan.plan_reviewed(root, "BG0001")["ok"])
            rc, out = _run(root, "transition.py", "set", "BG0001", "Fixed")
            self.assertEqual((rc, self._status(bug)), (0, "Fixed"), out)
        with self.subTest(case="5: reviewer wrote round one, the row names round two's author"):
            root = self._fresh()
            bug = self._bug(root, "on")
            self._ok_round(root, ["F1"], [_entry("F1")], author="alice")
            self._ok_round(root, ["F1"], [_entry("F1", design="retain")], author="erin")
            self.assertEqual(repair_plan.plan_authors(root, "BG0001"), ["alice", "erin"])
            self._critic_approve(root, reviewer="alice", author="erin")
            self._refused_at_fixed(root, "not independent")
            self._critic_approve(root, reviewer="zed", author="erin")
            self.assertTrue(repair_plan.plan_reviewed(root, "BG0001")["ok"])
            rc, out = _run(root, "transition.py", "set", "BG0001", "Fixed")
            self.assertEqual((rc, self._status(bug)), (0, "Fixed"), out)

    def test_an_approved_plan_passes_despite_an_earlier_test_plan_reject(self) -> None:
        """BG0678 AC2. Must fail on: `plan_reviewed` reading every plan-review row (no kind),
        or both verbs using kind `test-plan`, so the test-plan REJECT answers for the plan;
        `review` writing no brief, the whole-plan hash as the brief, or the unsliced 16-hex
        fingerprint - the first two leave the round-one REJECT standing, and all three fail the
        read-back of the Brief cell."""
        key = self._key(["F1"])
        with self.subTest(fixture="an approved plan beside a standing test-plan REJECT"):
            root = self._fresh()
            bug = self._bug(root, "on")
            self._test_plan_reject(root)
            # beside it, the same fixture with no plan: refused, naming the gate
            self._refused_at_fixed(root, "no repair plan is recorded for BG0001")
            self._ok_round(root, ["F1"], [_entry("F1")])
            self._review(root, "APPROVE", "reviewer-b")
            self.assertEqual(critic.verdict_for(root, "BG0001", phase="plan-review",
                                                kind="test-plan")["verdict"], "REJECT",
                             "the test-plan REJECT must still stand, or this proves nothing")
            self.assertEqual([r["brief"] for r in self._repair_rows(root)], [key])
            rc, out = _run(root, "transition.py", "set", "BG0001", "Fixed")
            self.assertEqual((rc, self._status(bug)), (0, "Fixed"), out)
        with self.subTest(fixture="round one REJECTed, the revised round APPROVEd"):
            root = self._fresh()
            bug = self._bug(root, "on")
            self._ok_round(root, ["F1"], [_entry("F1")])
            self._review(root, "REJECT", "reviewer-b")
            self._ok_round(root, ["F1"], [_entry("F1", change="rewrite the reader instead",
                                                 design="retain")])
            self._review(root, "APPROVE", "reviewer-b")
            self.assertEqual([(r["verdict"], r["brief"]) for r in self._repair_rows(root)],
                             [("REJECT", key), ("APPROVE", key)])
            rc, out = _run(root, "transition.py", "set", "BG0001", "Fixed")
            self.assertEqual((rc, self._status(bug)), (0, "Fixed"), out)

    def test_every_round_is_kept_so_the_design_threshold_binds_on_one_unit(self) -> None:
        """BG0678 AC3. Must fail on: `record` writing each round to `<unit>.json` in place;
        `repeat_rounds` counting distinct unit ids rather than rounds; or the round file written
        before the design-threshold check, so a refused round is left on disk."""
        self._bug(self.root, None)
        cls = "class:enumerate"
        self._ok_round(self.root, [cls], [_entry(cls, approach="v1: enumerate spellings")])
        first = self._stored_rounds(self.root)
        self.assertEqual(len(first), 1)
        round_one = first[0].read_bytes()
        self._ok_round(self.root, [cls], [_entry(cls, approach="v2: a flag-aware split",
                                                 design="retain")])
        self.assertEqual(len(self._stored_rounds(self.root)), 2)
        rc, out = self._round(self.root, [cls], [_entry(cls, approach="v3: a longer list",
                                                        design="retain")])
        self.assertNotEqual(rc, 0, out)
        self.assertIn("failed 2 round", out)
        self.assertEqual(len(self._stored_rounds(self.root)), 2, "the refused round was written")
        # beside it, the same third round changing the design: accepted, and kept as a third
        self._ok_round(self.root, [cls], [_entry(cls, approach="v3: derive from the runner",
                                                 design="change")])
        rounds = self._stored_rounds(self.root)
        self.assertEqual(len(rounds), 3)
        self.assertEqual(first[0].read_bytes(), round_one, "round one was written over")
        self.assertEqual(repair_plan.load_plan(self.root, "BG0001")["entries"][0]["approach"],
                         "v3: derive from the runner", "the current round is the latest")

    def test_a_re_record_after_approval_invalidates_the_approval(self) -> None:
        """BG0678 AC4. Must fail on: the pin made the findings fingerprint alone, or findings
        plus `design` without `approach`; or `load_plan` returning the first round, so the
        gate judges the round that was approved rather than the current one."""
        _write_config(self.root, "on")
        self._bug(self.root, None)
        entry = dict(finding="F1", change="rewrite the branch", risk="one manual",
                     design="retain")
        self._ok_round(self.root, ["F1"], [_entry(approach="derive from the runner", **entry)])
        self._review(self.root, "APPROVE", "reviewer-b")
        rc, out = self._gate(self.root)
        self.assertEqual(rc, 0, out)
        # the same findings, design, change and risk: ONLY the approach differs
        self._ok_round(self.root, ["F1"], [_entry(approach="enumerate the spellings", **entry)])
        self.assertEqual(critic.verdict_for(self.root, "BG0001", phase="plan-review",
                                            kind=critic.REPAIR_PLAN_KIND)["verdict"], "APPROVE",
                         "the round-one approval is still the latest verdict")
        rc, out = self._gate(self.root)
        self.assertNotEqual(rc, 0, out)
        self.assertIn("answered a different plan", out)
        # a fresh independent approval of the new round passes it again
        self._review(self.root, "APPROVE", "reviewer-b")
        rc, out = self._gate(self.root)
        self.assertEqual(rc, 0, out)

    def test_a_reject_is_retired_only_by_an_approval_of_the_same_finding_set(self) -> None:
        """BG0678 AC5. Must fail on: a Brief key every round of a unit shares whatever its
        finding set (a hash of the unit id); `plan_reviewed` judging only the latest row's pin
        and ignoring earlier REJECTs; or its REJECT scan counting a principal-superseded row."""
        waived = "F2 waived under D0001: out of scope for this repair"
        # unit A: F2 waived by DROPPING it from round two - the key changes, the REJECT stands
        a = self._fresh()
        self._bug(a, "on")
        self._ok_round(a, ["F1", "F2"], [_entry("F1"), _entry("F2")])
        self._review(a, "REJECT", "carol")
        self._ok_round(a, ["F1"], [_entry("F1", change="rewrite the reader", design="retain")])
        self._review(a, "APPROVE", "carol")
        rc, out = self._gate(a)
        self.assertNotEqual(rc, 0, out)
        self.assertIn("carol's REJECT", out)
        self.assertIn("unanswered", out)
        # unit B: the same path, F2 kept in the set with an entry naming the waiver - passes
        b = self._fresh()
        self._bug(b, "on")
        self._ok_round(b, ["F1", "F2"], [_entry("F1"), _entry("F2")])
        self._review(b, "REJECT", "carol")
        self._ok_round(b, ["F1", "F2"], [
            _entry("F1", change="rewrite the reader", design="retain"),
            _entry("F2", change=f"none: {waived}", approach="answered by the waiver, no code",
                   risk="the waived defect ships disclosed", design="retain")])
        self._review(b, "APPROVE", "carol")
        rc, out = self._gate(b)
        self.assertEqual(rc, 0, out)
        # the remedy for A: a principal supersession of the round-one REJECT
        reject = next(r for r in self._repair_rows(a) if r["verdict"] == "REJECT")
        rc, out = _run(a, "critic.py", "supersede", "--phase", "plan-review", "--unit", "BG0001",
                       "--date", reject["date"], "--reason", "the finding set changed: F2 waived",
                       "--reviewer", "carol", "--verdict", "REJECT", "--authorised-by", "pat",
                       "--boundary", "operator terminal, outside the authoring session")
        self.assertEqual(rc, 0, out)
        rc, out = self._gate(a)
        self.assertEqual(rc, 0, out)

    def _carol_rejects_then(self, approver: str) -> Path:
        """Round one REJECTed by carol, round two re-recorded against the same finding set and
        APPROVEd by `approver`, all through `repair_plan.py`."""
        root = self._fresh()
        self._bug(root, "on")
        self._ok_round(root, ["F1"], [_entry("F1")])
        self._review(root, "REJECT", "carol")
        self._ok_round(root, ["F1"], [_entry("F1", change="rewrite the reader", design="retain")])
        self._review(root, "APPROVE", approver)
        return root

    def _carols_reject(self, root: Path) -> dict:
        return next(r for r in self._repair_rows(root)
                    if r["verdict"] == "REJECT" and r["reviewer"] == "carol")

    def test_another_reviewers_approval_does_not_retire_a_reject(self) -> None:
        """BG0678 AC6. Must fail on: the reviewer-identity comparison deleted from
        `plan_reviewed`'s REJECT scan; the scan's retired-row filter removed; or that filter
        widened to `critic.is_superseded`, or the scan replaced by `critic.unit_review_rounds`
        - both drop a REJECT the plan's own author retired by hand."""
        refused = "carol's REJECT"
        with self.subTest(case="dave approves carol's rejected plan"):
            root = self._carol_rejects_then("dave")
            v = critic.verdict_for(root, "BG0001", phase="plan-review",
                                   kind=critic.REPAIR_PLAN_KIND)
            self.assertEqual((v["reviewer"], v["verdict"]), ("dave", "APPROVE"),
                             "verdict_for must read dave's APPROVE as retiring carol's REJECT, "
                             "or this proves nothing about plan_reviewed's own scan")
            rc, out = self._gate(root)
            self.assertNotEqual(rc, 0, out)
            self.assertIn(refused, out)
            self.assertIn("unanswered", out)
            # the remedy: a principal supersession of carol's REJECT; the raw row still reads it
            rc, out = _run(root, "critic.py", "supersede", "--phase", "plan-review",
                           "--unit", "BG0001", "--date", self._carols_reject(root)["date"],
                           "--reason", "carol's seat was renamed between rounds",
                           "--reviewer", "carol", "--verdict", "REJECT",
                           "--authorised-by", "pat", "--boundary", "operator terminal")
            self.assertEqual(rc, 0, out)
            row = self._carols_reject(root)
            self.assertEqual((row["verdict"], row["superseded"]), ("REJECT", True))
            rc, out = self._gate(root)
            self.assertEqual(rc, 0, out)
        with self.subTest(case="carol approves her own rejected plan"):
            rc, out = self._gate(self._carol_rejects_then("carol"))
            self.assertEqual(rc, 0, out)
        with self.subTest(case="carol's REJECT retired by the plan's author, by hand"):
            root = self._carol_rejects_then("dave")
            row = self._carols_reject(root)
            self.assertEqual(row["author"], repair_plan.load_plan(root, "BG0001")["author"],
                             "the REJECT's Author cell must be the plan's author")
            path = critic.verdicts_path(root, "plan-review")
            path.write_text(
                path.read_text(encoding="utf-8") + "\n" + critic.SUPERSEDE_HEADING + "\n\n"
                + critic._SUPERSEDE_PREFIX
                + f"unit=BG0001 row-date={row['date']} row-verdict=REJECT row-reviewer=carol "
                  f"row-author={row['author']} authorised-by={row['author']} boundary=- "
                  "reason=inconvenient recorded=2026-09-15\n", encoding="utf-8")
            row = self._carols_reject(root)
            self.assertTrue(critic.is_superseded(row), "the hand append did not parse")
            self.assertFalse(critic._is_principal_superseded(root, "BG0001", row),
                             "an author-authorised correction must read non-principal")
            v = critic.verdict_for(root, "BG0001", phase="plan-review",
                                   kind=critic.REPAIR_PLAN_KIND)
            self.assertEqual((v["reviewer"], v["verdict"]), ("dave", "APPROVE"))
            rc, out = self._gate(root)
            self.assertNotEqual(rc, 0, out)
            self.assertIn(refused, out)
        with self.subTest(case="carol and erin reject, erin alone approves"):
            root = self._fresh()
            self._bug(root, "on")
            self._ok_round(root, ["F1"], [_entry("F1")])
            self._review(root, "REJECT", "carol")
            self._review(root, "REJECT", "erin")
            self._ok_round(root, ["F1"], [_entry("F1", change="rewrite the reader",
                                                 design="retain")])
            self._review(root, "APPROVE", "erin")
            rc, out = self._gate(root)
            self.assertNotEqual(rc, 0, out)
            self.assertIn(refused, out)
            self.assertNotIn("erin's REJECT", out)
            # and once carol approves too, the gate passes
            self._review(root, "APPROVE", "carol")
            rc, out = self._gate(root)
            self.assertEqual(rc, 0, out)


def _write_config(root: Path, gate: str, extra: str = "") -> None:
    cfg = root / "sdlc-studio" / ".config.yaml"
    cfg.write_text(f"review:\n  repair_plan_gate: {gate}\n{extra}", encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
