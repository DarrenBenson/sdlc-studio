"""Unit tests for the v3 plan-review gate (US0090/CR0194): a deterministic trigger and an
independent-verdict gate that blocks implementation of a spec-derived plan until reviewed.
Dormant under schema_version 2.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, DIR / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


pr = _load("plan_review", "plan_review.py")
critic = _load("critic", "critic.py")
telemetry = _load("telemetry", "telemetry.py")


def _repo(root: Path, v3: bool = True, cfg_extra: str = "") -> Path:
    sd = root / "sdlc-studio"
    (sd / "stories").mkdir(parents=True, exist_ok=True)
    (sd / "reviews").mkdir(parents=True, exist_ok=True)
    if v3:
        (sd / ".config.yaml").write_text("schema_version: 3\n" + cfg_extra, encoding="utf-8")
    return root


def _story(root: Path, sid: str = "US0001", affects: str = "", override: str | None = None,
           body_extra: str = "") -> Path:
    lines = [f"# {sid}: Test story", "", "> **Status:** Ready", "> **Epic:** EP0001"]
    if affects:
        lines.append(f"> **Affects:** {affects}")
    if override is not None:
        lines.append(f"> **Plan-Review-Override:** {override}")
    lines += ["", "## Acceptance Criteria", "", "### AC1: a thing",
              "- **Given** x", "- **When** y", "- **Then** z", body_extra]
    p = root / "sdlc-studio" / "stories" / f"{sid}-test.md"
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p


# A config that isolates one signal at a time: threshold high, difficulty ceiling high,
# so only an explicit spec citation trips the gate unless a test opts a signal in.
_ISOLATE = ("plan_review:\n  affects_files_threshold: 99\n  min_difficulty: extreme\n")


class TriggerTests(unittest.TestCase):
    """AC1: the trigger fires deterministically on any of the three checkable signals."""

    def test_spec_citation_in_affects_fires(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), cfg_extra=_ISOLATE)
            t = pr.triggers(_story(root, affects="docs/prd.md").read_text(encoding="utf-8"), root)
            self.assertTrue(t["fired"])
            self.assertTrue(t["spec_citation"])
            self.assertIn("spec-citation", t["signals"])

    def test_spec_citation_in_ac_body_fires(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), cfg_extra=_ISOLATE)
            p = _story(root, body_extra="- **Verify:** grep rule docs/requirements.md")
            self.assertTrue(pr.triggers(p.read_text(encoding="utf-8"), root)["spec_citation"])

    def test_affects_over_threshold_fires(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), cfg_extra="plan_review:\n  affects_files_threshold: 5\n"
                                            "  min_difficulty: extreme\n")
            aff = "a.py, b.py, c.py, d.py, e.py"      # 5 files, none a spec
            t = pr.triggers(_story(root, affects=aff).read_text(encoding="utf-8"), root)
            self.assertTrue(t["fired"])
            self.assertTrue(t["affects_over"])
            self.assertFalse(t["spec_citation"])

    def test_difficulty_over_min_fires(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            # min_difficulty trivial => every unit's band (>= trivial) trips the signal
            root = _repo(Path(d), cfg_extra="plan_review:\n  affects_files_threshold: 99\n"
                                            "  min_difficulty: trivial\n")
            t = pr.triggers(_story(root, affects="a.py").read_text(encoding="utf-8"), root)
            self.assertTrue(t["difficulty_over"])
            self.assertTrue(t["fired"])

    def test_extensionless_spec_dir_reference_fires(self) -> None:
        # A spec section referenced without a file extension (requirements/r5, specs/design)
        # must still trip the gate - missing it would under-fire (the dangerous direction).
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), cfg_extra=_ISOLATE)
            self.assertTrue(pr.cites_spec("invert the rule from requirements/r5 here", root))
            self.assertTrue(pr.cites_spec("see specs/design for the constraint", root))
            self.assertFalse(pr.cites_spec("a normal sentence with no path", root))

    def test_root_spec_file_citation_fires(self) -> None:
        # The plan-review spec boundary must agree with spec_guard's: a root SPEC.md counts.
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), cfg_extra=_ISOLATE)
            self.assertTrue(pr.cites_spec("this reworks the rule in SPEC.md", root))
            self.assertTrue(pr.cites_spec("see product.spec.md for the constraint", root))

    def test_no_signal_does_not_fire(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), cfg_extra=_ISOLATE)   # threshold 99, difficulty extreme
            t = pr.triggers(_story(root, affects="a.py").read_text(encoding="utf-8"), root)
            self.assertFalse(t["fired"])
            self.assertEqual(t["signals"], [])

    def test_trigger_is_pure_no_side_effects(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), cfg_extra=_ISOLATE)
            text = _story(root, affects="docs/prd.md").read_text(encoding="utf-8")
            a = pr.triggers(text, root)
            b = pr.triggers(text, root)
            self.assertEqual(a, b)                       # deterministic


class GateTests(unittest.TestCase):
    """AC2: a triggered story cannot enter implementation without an independent verdict."""

    def _triggered(self, root):
        return _story(root, sid="US0002", affects="docs/prd.md")

    def test_triggered_without_verdict_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), cfg_extra=_ISOLATE)
            self._triggered(root)
            res = pr.gate(root, "US0002")
            self.assertFalse(res["ok"])
            self.assertIn("plan-review", res["reason"].lower())

    def test_independent_approve_unblocks(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), cfg_extra=_ISOLATE)
            self._triggered(root)
            critic.record_verdict(root, "US0002", "APPROVE", reviewer="qa", author="dev",
                                  phase="plan-review")
            self.assertTrue(pr.gate(root, "US0002")["ok"])

    def test_self_review_does_not_unblock(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), cfg_extra=_ISOLATE)
            self._triggered(root)
            critic.record_verdict(root, "US0002", "APPROVE", reviewer="dev", author="dev",
                                  phase="plan-review")
            self.assertFalse(pr.gate(root, "US0002")["ok"])   # reviewer == author

    def test_reject_does_not_unblock(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), cfg_extra=_ISOLATE)
            self._triggered(root)
            critic.record_verdict(root, "US0002", "REJECT", reviewer="qa", author="dev",
                                  phase="plan-review")
            self.assertFalse(pr.gate(root, "US0002")["ok"])

    def test_untriggered_story_passes_without_verdict(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), cfg_extra=_ISOLATE)
            _story(root, sid="US0003", affects="a.py")        # no signal
            self.assertTrue(pr.gate(root, "US0003")["ok"])

    def test_dormant_under_v2(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), v3=False)
            _story(root, sid="US0002", affects="docs/prd.md")
            res = pr.gate(root, "US0002")
            self.assertTrue(res["ok"])                         # gate is a no-op on v2


class OverrideTests(unittest.TestCase):
    """AC3: a skip is possible only through a recorded operator override."""

    def test_recorded_override_unblocks_and_is_named(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), cfg_extra=_ISOLATE)
            _story(root, sid="US0002", affects="docs/prd.md",
                   override="ops: hotfix, spec unchanged")
            res = pr.gate(root, "US0002")
            self.assertTrue(res["ok"])
            self.assertIn("override", res["reason"].lower())

    def test_no_override_no_verdict_stays_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), cfg_extra=_ISOLATE)
            _story(root, sid="US0002", affects="docs/prd.md")   # no override field
            self.assertFalse(pr.gate(root, "US0002")["ok"])

    def test_empty_override_does_not_count(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), cfg_extra=_ISOLATE)
            _story(root, sid="US0002", affects="docs/prd.md", override="")
            self.assertFalse(pr.gate(root, "US0002")["ok"])     # blank is not an override

    def test_dash_sentinel_override_does_not_count(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), cfg_extra=_ISOLATE)
            _story(root, sid="US0002", affects="docs/prd.md", override="-")
            self.assertFalse(pr.gate(root, "US0002")["ok"])     # `-` is the empty sentinel


class StaleApprovalTests(unittest.TestCase):
    """A plan-review approval pins the reviewed ACs; editing them after approval must not
    ride the stale verdict (the mis-pinned-AC attack CR0194 targets)."""

    def test_pinned_approval_holds_when_acs_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), cfg_extra=_ISOLATE)
            _story(root, sid="US0002", affects="docs/prd.md")
            pr.record_review(root, "US0002", "APPROVE", "qa", "dev")
            self.assertTrue(pr.gate(root, "US0002")["ok"])

    def test_ac_edit_after_approval_invalidates_the_verdict(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), cfg_extra=_ISOLATE)
            p = _story(root, sid="US0002", affects="docs/prd.md")
            pr.record_review(root, "US0002", "APPROVE", "qa", "dev")
            # invert the AC after the benign plan was approved
            p.write_text(p.read_text(encoding="utf-8").replace(
                "### AC1: a thing", "### AC1: the INVERSE of the spec rule"),
                encoding="utf-8")
            self.assertFalse(pr.gate(root, "US0002")["ok"])     # stale approval rejected

    def test_hashless_verdict_still_honoured(self) -> None:
        # back-compat: a bare `critic record --phase plan-review` (no pinned hash) counts
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), cfg_extra=_ISOLATE)
            _story(root, sid="US0002", affects="docs/prd.md")
            critic.record_verdict(root, "US0002", "APPROVE", reviewer="qa", author="dev",
                                  phase="plan-review")
            self.assertTrue(pr.gate(root, "US0002")["ok"])

    def test_record_cli_pins_and_unblocks(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), cfg_extra=_ISOLATE)
            _story(root, sid="US0002", affects="docs/prd.md")
            pr.main(["record", "--id", "US0002", "--verdict", "approve",
                     "--reviewer", "qa", "--author", "dev", "--root", str(root)])
            self.assertTrue(pr.gate(root, "US0002")["ok"])     # pinned + independent


class PhaseRecordTests(unittest.TestCase):
    """AC4: plan-review verdicts are written distinctly and read only by phase."""

    def test_plan_review_verdict_in_its_own_log(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            critic.record_verdict(root, "US0009", "APPROVE", reviewer="qa", author="dev",
                                  phase="plan-review")
            self.assertTrue(critic.verdicts_path(root, "plan-review").exists())
            self.assertFalse(critic.verdicts_path(root, "delivery").exists())

    def test_delivery_verdict_invisible_to_plan_review_and_vice_versa(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            critic.record_verdict(root, "US0009", "APPROVE", reviewer="qa", author="dev",
                                  phase="delivery")
            self.assertIsNone(critic.verdict_for(root, "US0009", phase="plan-review"))
            self.assertIsNotNone(critic.verdict_for(root, "US0009", phase="delivery"))

    def test_delivery_approve_does_not_satisfy_plan_gate(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), cfg_extra=_ISOLATE)
            _story(root, sid="US0002", affects="docs/prd.md")
            critic.record_verdict(root, "US0002", "APPROVE", reviewer="qa", author="dev",
                                  phase="delivery")          # delivery, not plan-review
            self.assertFalse(pr.gate(root, "US0002")["ok"])


class TelemetryTests(unittest.TestCase):
    """US0091 AC3: a plan-review verdict emits a telemetry event (id, verdict, independence)."""

    def test_record_review_emits_plan_review_event(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), cfg_extra=_ISOLATE)
            _story(root, sid="US0002", affects="docs/prd.md")
            pr.record_review(root, "US0002", "APPROVE", "qa", "dev")
            events = [e for e in telemetry.read_all(root) if e.get("event") == "plan-review"]
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0]["verdict"], "APPROVE")
            self.assertEqual(events[0]["id"], "US0002")
            self.assertTrue(events[0]["independent"])

    def test_self_review_event_marked_not_independent(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), cfg_extra=_ISOLATE)
            _story(root, sid="US0002", affects="docs/prd.md")
            pr.record_review(root, "US0002", "APPROVE", "dev", "dev")
            events = [e for e in telemetry.read_all(root) if e.get("event") == "plan-review"]
            self.assertFalse(events[0]["independent"])


if __name__ == "__main__":
    unittest.main()
