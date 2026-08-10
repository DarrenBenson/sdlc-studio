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


def _repo(root: Path, v3: bool = True, cfg_extra: str = "", *, retros: int = 1) -> Path:
    sd = root / "sdlc-studio"
    (sd / "stories").mkdir(parents=True, exist_ok=True)
    (sd / "reviews").mkdir(parents=True, exist_ok=True)
    if v3:
        (sd / ".config.yaml").write_text("schema_version: 3\n" + cfg_extra, encoding="utf-8")
    # US0662: the gate REPORTS rather than refuses on a project that has closed no sprint, and
    # every fixture in this file means "an established project" - they exist to test the refusal.
    # One retro arms them. Pass `retros=0` for the first-run case, which is its own test class.
    rd = sd / "retros"
    rd.mkdir(parents=True, exist_ok=True)
    for i in range(retros):
        (rd / f"RETRO{i:04d}-x.md").write_text(f"# RETRO{i:04d}\n", encoding="utf-8")
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


class EnablementKeyTests(unittest.TestCase):
    """US0640: `plan_review.gate` hard-returned `dormant (schema v2)` with no config key at all.

    So the one hard, deterministic, risk-proportional gate this codebase has - the model the
    rest of the ceremony work copies, and the one `--force` cannot bypass - was reachable only
    by adopting the v3 id format, the inbox status and spec-guard across every artefact a
    project holds. It is a REVIEW POLICY and has nothing to do with the shape of artefacts.
    `triage_noise` was given exactly this knob for exactly this reason; this does the same, and
    shares the one resolution rather than copying it.
    """

    def _cfg(self, root: Path, body: str) -> None:
        (root / "sdlc-studio" / ".config.yaml").write_text(body, encoding="utf-8")

    def test_the_knob_switches_the_gate_on_under_schema_v2(self) -> None:
        """Mutant: read the schema version alone - the gate stays dormant and the whole slice is
        inert, which is the state it has been in since it was built."""
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), v3=False)
            _story(root, sid="US0002", affects="docs/prd.md")
            # ONE `plan_review:` mapping - a second one would silently replace the first in YAML.
            self._cfg(root, "schema_version: 2\nplan_review:\n  enabled: true\n"
                            "  affects_files_threshold: 99\n  min_difficulty: extreme\n")
            res = pr.gate(root, "US0002")
            self.assertTrue(res["fired"], res)
            self.assertFalse(res["ok"], res)

    def test_the_knob_switches_the_gate_off_under_schema_v3(self) -> None:
        """Mutant: honour the knob only in the permissive direction - a project that
        deliberately turned it off gets it anyway. And the reason must name the KNOB, because a
        reader sent to a schema migration they do not need cannot act on it."""
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), v3=True)
            _story(root, sid="US0002", affects="docs/prd.md")
            self._cfg(root, "schema_version: 3\nplan_review:\n  enabled: false\n"
                            "  affects_files_threshold: 99\n  min_difficulty: extreme\n")
            res = pr.gate(root, "US0002")
            self.assertTrue(res["ok"], res)
            self.assertFalse(res["fired"], res)
            self.assertIn("plan_review.enabled", res["reason"])
            self.assertNotIn("schema", res["reason"])

    def test_an_unset_knob_preserves_the_schema_gated_behaviour(self) -> None:
        """Mutant: default the knob to true - every v2 project acquires a gate nobody adopted,
        and the upgrade moves the bar under them."""
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), v3=False, cfg_extra=_ISOLATE)
            _story(root, sid="US0002", affects="docs/prd.md")
            res = pr.gate(root, "US0002")
            self.assertTrue(res["ok"], res)
            self.assertEqual(res["reason"], "dormant (schema v2)")
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), v3=True, cfg_extra=_ISOLATE)
            _story(root, sid="US0002", affects="docs/prd.md")
            self.assertTrue(pr.gate(root, "US0002")["fired"], "v3 with no knob must still fire")

    def test_one_shared_enablement_predicate_serves_both_adopters(self) -> None:
        """LL0016. Mutant: give `plan_review` its own copy of the knob-then-schema resolution -
        two answers to one question, and they drift the moment either is touched. Proved by
        MOVING the shared predicate: if either adopter carries its own copy, one of them keeps
        answering while the shared one is broken."""
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), v3=False)
            self._cfg(root, "schema_version: 2\nplan_review:\n  enabled: true\n"
                            "triage:\n  enabled: true\n")
            # Patch the config module EACH ADOPTER ACTUALLY IMPORTED, not `import config` in
            # this test. Under the full suite the sibling test modules load their subjects via
            # importlib under distinct names, so `import config` here can resolve to a different
            # module object than `plan_review.config` - and the patch then lands on nothing while
            # the test still passes in isolation. Found by the full suite doing exactly that.
            import triage_noise as tn_mod
            for holder in (pr, tn_mod):
                self.addCleanup(setattr, holder.config, "feature_enabled",
                                holder.config.feature_enabled)
                holder.config.feature_enabled = lambda r, f: False
            self.assertFalse(pr.active(root), "plan_review does not ask the shared predicate")
            self.assertFalse(tn_mod.active(root), "triage_noise does not ask it either")


class PlanReviewKindTests(unittest.TestCase):
    """BG0510, the consumer half: the one live gate asks for ITS artefact's approval."""

    def test_the_gate_asks_for_the_spec_kind_and_its_behaviour_is_unchanged(self) -> None:
        """Every case this gate passes and refuses today it still passes and refuses, AND a
        test-plan approval no longer discharges it. Mutant: leave the gate asking for any kind -
        the column exists and nothing reads it, which is the state `critic brief --tier` is
        already in and the reason this bug is worth fixing rather than noting."""
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), cfg_extra=_ISOLATE)
            _story(root, sid="US0002", affects="docs/prd.md")
            self.assertFalse(pr.gate(root, "US0002")["ok"], "the trigger must fire, or this "
                                                            "test proves nothing about kinds")
            # a TEST-PLAN approval must not clear the SPEC gate
            critic.record_verdict(root, "US0002", "APPROVE", reviewer="qa", author="dev",
                                  phase="plan-review", kind="test-plan")
            self.assertFalse(pr.gate(root, "US0002")["ok"],
                             "a test-plan approval discharged the AC-vs-spec gate")
            # ...and the SPEC approval does
            critic.record_verdict(root, "US0002", "APPROVE", reviewer="qa", author="dev",
                                  phase="plan-review", kind="spec")
            self.assertTrue(pr.gate(root, "US0002")["ok"], pr.gate(root, "US0002"))

    def test_an_approval_recorded_before_the_column_existed_still_clears_the_gate(self) -> None:
        """The back-compatibility control, at the gate rather than at the reader. Mutant: read
        an absent kind as unknown - `transition` starts refusing units it passes today, across
        the whole corpus, for a latent defect that costs nothing."""
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), cfg_extra=_ISOLATE)
            _story(root, sid="US0002", affects="docs/prd.md")
            critic.record_verdict(root, "US0002", "APPROVE", reviewer="qa", author="dev",
                                  phase="plan-review")        # no kind named, as before
            self.assertTrue(pr.gate(root, "US0002")["ok"], pr.gate(root, "US0002"))


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


class ResolutionAndFailLoudTests(unittest.TestCase):
    """BG0094: lowercase stories must resolve (shared find_by_id, not a case-sensitive
    glob); an unresolved story must fail LOUD in record and gate, never a null fingerprint
    or a vacuous skip."""

    def _v3(self, root: Path) -> None:
        (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
        (root / "sdlc-studio" / ".config.yaml").write_text("schema_version: 3\n",
                                                           encoding="utf-8")

    def _story(self, root: Path, name: str) -> Path:
        d = root / "sdlc-studio" / "stories"
        d.mkdir(parents=True, exist_ok=True)
        p = d / name
        p.write_text("# US0101: lower\n\n> **Status:** Draft\n\n## Acceptance Criteria\n\n"
                     "### AC1: x\n\n- **Given** a\n- **When** b\n- **Then** c\n",
                     encoding="utf-8")
        return p

    def test_lowercase_story_file_resolves(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._v3(root)
            p = self._story(root, "us0101-lower.md")
            self.assertEqual(pr._resolve_story(root, "US0101"), p)

    def test_record_refuses_an_unresolvable_story(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._v3(root)
            with self.assertRaises(FileNotFoundError):
                pr.record_review(root, "US9999", "APPROVE", "rev", "auth")

    def test_gate_not_found_is_non_ok(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._v3(root)
            res = pr.gate(root, "US9999")
            self.assertFalse(res["ok"])
            self.assertIn("not found", res["reason"])


class RunHistoryArmsTheGateTests(unittest.TestCase):
    """US0662/US0663 under D0134: the gate is a report on a project that has closed no sprint,
    and a refusal on every project that has. The arming fact is the COMMITTED retros."""

    _STORY = ("# US0001: s\n\n> **Status:** Ready\n> **Epic:** EP0001\n"
              "> **Affects:** src/a.py, src/b.py, src/c.py, src/d.py, src/e.py, src/f.py\n"
              "> **Points:** 3\n\n## Acceptance Criteria\n\n### AC1: it works\n\n"
              "- **Given** x\n- **When** y\n- **Then** z\n- **Verify:** shell true\n")

    def _proj(self, root: Path, *, retros: int = 0) -> Path:
        _repo(root, retros=0)
        (root / "sdlc-studio" / "stories" / "US0001-x.md").write_text(self._STORY,
                                                                     encoding="utf-8")
        d = root / "sdlc-studio" / "retros"
        d.mkdir(parents=True, exist_ok=True)
        for i in range(retros):
            (d / f"RETRO{i:04d}-x.md").write_text(f"# RETRO{i:04d}\n", encoding="utf-8")
        return root

    def test_a_project_with_no_retro_reports_the_plan_review_requirement(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._proj(Path(d), retros=0)
            res = pr.gate(root, "US0001")
            self.assertTrue(res["ok"], "a project with no closed sprint was refused")
            self.assertTrue(res["fired"], "the trigger did not trip, so nothing was softened")
            self.assertIn("retros", res["reason"],
                          "the report does not name the condition that arms the gate")

    def test_an_armed_project_still_refuses(self) -> None:
        # Pinned HERE, not only in the sibling unit: every criterion of the first plan passed on
        # an implementation that deleted the gate outright, which would have put a commit on main
        # with the flagship gate off and nothing in this unit able to notice.
        with tempfile.TemporaryDirectory() as d:
            root = self._proj(Path(d), retros=1)
            res = pr.gate(root, "US0001")
            self.assertFalse(res["ok"], "one retro on disk and the gate still did not refuse")
            self.assertIn("plan-review required", res["reason"])

    def test_the_softening_expires_on_the_first_retro(self) -> None:
        # US0663 AC1: both halves in ONE test, so it cannot pass on the pre-epic tree where every
        # project refuses.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._proj(root, retros=0)
            self.assertTrue(pr.gate(root, "US0001")["ok"])
            (root / "sdlc-studio" / "retros" / "RETRO0001-x.md").write_text("# RETRO0001\n",
                                                                           encoding="utf-8")
            self.assertFalse(pr.gate(root, "US0001")["ok"],
                             "the concession survived the first retro, so it does not expire")

    def test_an_unreadable_history_counts_as_armed(self) -> None:
        # US0662 AC4. The direction this must not fail in is a long-lived project being silently
        # softened, so anything the predicate cannot read counts as history rather than absence.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._proj(root, retros=0)
            real = pr.Path
            try:
                class _Boom(type(root)):
                    def is_dir(self):
                        raise OSError("unreadable")
                pr.Path = lambda *a, **k: _Boom(*a, **k)  # noqa: ARG005
                self.assertTrue(pr.has_run_history(root),
                                "an unreadable retro directory read as 'no history', which "
                                "softens the gate on every project it cannot inspect")
            finally:
                pr.Path = real

    def test_no_configuration_key_can_hold_the_softening_open(self) -> None:
        # US0663 AC3, replacing a verifier that asserted the PRESENCE of two strings while its
        # own mutant was an ADDITION - so adding the forbidden key made it pass harder. This is
        # an ABSENCE assertion over both files, with a positive control below it.
        forbidden = "first_run"
        for rel in ("reference-config.md", "templates/config-defaults.yaml"):
            text = (DIR.parent / rel).read_text(encoding="utf-8")
            self.assertNotIn(f"plan_review.{forbidden}", text, f"{rel} names a knob that could "
                             "hold the first-run softening open")
            self.assertNotIn(f"{forbidden}:", text.split("plan_review:")[-1][:400],
                             f"{rel} adds a first_run key under plan_review")

    def test_the_absence_check_reddens_when_such_a_key_is_added(self) -> None:
        # The positive control for the test above: without it, a check that can never fail
        # passes for the wrong reason, which is exactly the defect it replaced.
        sample = "plan_review:\n  affects_files_threshold: 5\n  first_run: report\n"
        self.assertIn("first_run:", sample.split("plan_review:")[-1][:400],
                      "the absence assertion cannot detect an added key, so it proves nothing")


if __name__ == "__main__":
    unittest.main()
