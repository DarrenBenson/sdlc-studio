"""Unit tests for sprint.py (RED first - the script does not exist yet)."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "sprint.py"


def _load():
    spec = importlib.util.spec_from_file_location("sprint", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["sprint"] = mod
    spec.loader.exec_module(mod)
    return mod


def _bug(root, num, status="Open", severity="Medium"):
    d = root / "sdlc-studio" / "bugs"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"BG{num:04d}-x.md").write_text(
        f"# BG{num:04d}: b\n\n> **Status:** {status}\n> **Severity:** {severity}\n", encoding="utf-8")


def _cr(root, num, status="Proposed", priority="Medium"):
    d = root / "sdlc-studio" / "change-requests"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"CR{num:04d}-x.md").write_text(
        f"# CR-{num:04d}: c\n\n> **Status:** {status}\n> **Priority:** {priority}\n", encoding="utf-8")


class StatusArgCanonicalisationTests(unittest.TestCase):
    """BG0034: a lowercase status arg (the documented form) must match the title-case vocab."""

    def test_lowercase_status_selects_same_as_titlecase(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1, status="Proposed")
            _cr(root, 2, status="Complete")
            lower = [b["id"] for b in _load().select_batch(root, "cr", "proposed")]
            title = [b["id"] for b in _load().select_batch(root, "cr", "Proposed")]
            self.assertEqual(lower, ["CR0001"])
            self.assertEqual(lower, title)

    def test_unknown_status_raises(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1, status="Proposed")
            with self.assertRaises(ValueError):
                _load().select_batch(root, "cr", "notastatus")


class EpicScopeTests(unittest.TestCase):
    """CR0106: sprint plan can scope a story batch to one or more epics."""

    def _story(self, root, num, epic, status="Draft"):
        d = root / "sdlc-studio" / "stories"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"US{num:04d}-x.md").write_text(
            f"# US{num:04d}: s\n\n> **Status:** {status}\n> **Epic:** [{epic}: t](../epics/{epic}-t.md)\n",
            encoding="utf-8")

    def test_epic_scopes_the_batch(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, 1, "EP0002"); self._story(root, 2, "EP0002")
            self._story(root, 3, "EP0003")
            all_ids = [b["id"] for b in _load().select_batch(root, "story", "Draft")]
            ep2 = [b["id"] for b in _load().select_batch(root, "story", "Draft", epics={"EP0002"})]
            self.assertEqual(len(all_ids), 3)
            self.assertEqual(sorted(ep2), ["US0001", "US0002"])

    def test_multiple_epics_union(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, 1, "EP0002"); self._story(root, 3, "EP0003")
            self._story(root, 5, "EP0009")
            got = [b["id"] for b in _load().select_batch(
                root, "story", "Draft", epics={"EP0002", "EP0003"})]
            self.assertEqual(sorted(got), ["US0001", "US0003"])


class WaveTests(unittest.TestCase):
    """CR0107: build_plan emits dependency waves (parallelisable levels)."""

    def _story(self, root, num, depends=None, status="Draft"):
        d = root / "sdlc-studio" / "stories"
        d.mkdir(parents=True, exist_ok=True)
        dep = f"> **Depends on:** {depends}\n" if depends else ""
        (d / f"US{num:04d}-x.md").write_text(
            f"# US{num:04d}: s\n\n> **Status:** {status}\n{dep}", encoding="utf-8")

    def test_waves_are_dependency_levels(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, 1)                       # wave 1
            self._story(root, 2, depends="US0001")     # wave 2
            self._story(root, 3, depends="US0001")     # wave 2 (parallel with US0002)
            self._story(root, 4, depends="US0002")     # wave 3
            waves = _load().build_plan(root, "story", "Draft")["waves"]
            self.assertEqual(waves[0], ["US0001"])
            self.assertEqual(sorted(waves[1]), ["US0002", "US0003"])
            self.assertEqual(waves[2], ["US0004"])

    def test_manual_order_has_no_waves(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, 1)
            self.assertIsNone(_load().build_plan(root, "story", "Draft", order="manual")["waves"])


class NoDepsHintTests(unittest.TestCase):
    """CR0114: a flat single wave with no declared deps must be flagged, not mistaken
    for 'no dependencies exist'."""

    def _story(self, root, num, depends=None, status="Draft"):
        d = root / "sdlc-studio" / "stories"
        d.mkdir(parents=True, exist_ok=True)
        dep = f"> **Depends on:** {depends}\n" if depends else ""
        (d / f"US{num:04d}-x.md").write_text(
            f"# US{num:04d}: s\n\n> **Status:** {status}\n{dep}", encoding="utf-8")

    def test_plan_flags_no_declared_deps(self) -> None:
        # >1 unit, no Depends on anywhere -> deps_declared False, one flat parallel wave.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, 1); self._story(root, 2); self._story(root, 3)
            plan = _load().build_plan(root, "story", "Draft")
            self.assertFalse(plan["deps_declared"])
            self.assertEqual(len(plan["waves"]), 1)            # everything in one flat wave
            self.assertEqual(len(plan["waves"][0]), 3)

    def test_declared_deps_not_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, 1); self._story(root, 2, depends="US0001")
            plan = _load().build_plan(root, "story", "Draft")
            self.assertTrue(plan["deps_declared"])
            self.assertEqual(len(plan["waves"]), 2)            # real levels

    def test_single_unit_not_flagged(self) -> None:
        # A lone unit is genuinely parallel-by-default; no hint needed.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, 1)
            self.assertFalse(_load().build_plan(root, "story", "Draft")["deps_declared"])

    def test_manual_order_omits_deps_signal(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, 1); self._story(root, 2)
            plan = _load().build_plan(root, "story", "Draft", order="manual")
            self.assertIsNone(plan["deps_declared"])

    def test_cli_prints_no_deps_hint(self) -> None:
        import io
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, 1); self._story(root, 2)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = _load().main(["plan", "--stories", "Draft", "--root", str(root)])
            self.assertEqual(rc, 0)
            out = buf.getvalue()
            self.assertIn("Depends on", out)        # the hint names the missing field
            self.assertIn("parallel", out.lower())

    def test_cli_no_hint_for_single_unit(self) -> None:
        # A lone unit is parallel-by-default; the hint targets a >1-unit flat batch only
        # (AC2: "a batch of >1 story ... a flat single wave"). The CLI must suppress it here.
        import io
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, 1)
            buf = io.StringIO()
            with redirect_stdout(buf):
                _load().main(["plan", "--stories", "Draft", "--root", str(root)])
            self.assertNotIn("no `Depends on:` is declared", buf.getvalue())

    def test_cli_no_hint_when_deps_declared(self) -> None:
        import io
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, 1); self._story(root, 2, depends="US0001")
            buf = io.StringIO()
            with redirect_stdout(buf):
                _load().main(["plan", "--stories", "Draft", "--root", str(root)])
            self.assertNotIn("no `Depends on:` is declared", buf.getvalue())


class SelectTests(unittest.TestCase):
    def test_selects_by_status(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1, status="Open")
            _bug(root, 2, status="Fixed")
            batch = _load().select_batch(root, "bug", "Open")
            ids = [b["id"] for b in batch]
            self.assertEqual(ids, ["BG0001"])
            self.assertEqual(batch[0]["status"], "Open")


class OrderTests(unittest.TestCase):
    def test_priority_order(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1, severity="Low")
            _bug(root, 2, severity="Critical")
            _bug(root, 3, severity="Medium")
            batch = _load().select_batch(root, "bug", "Open", order="priority")
            self.assertEqual([b["priority"] for b in batch], ["Critical", "Medium", "Low"])


def _cr_dep(root, num, priority="Medium", depends=None, status="Proposed"):
    d = root / "sdlc-studio" / "change-requests"
    d.mkdir(parents=True, exist_ok=True)
    body = f"# CR-{num:04d}: c\n\n> **Status:** {status}\n> **Priority:** {priority}\n"
    if depends:
        body += f"> **Depends on:** {depends}\n"
    (d / f"CR{num:04d}-x.md").write_text(body, encoding="utf-8")


class DepsOrderTests(unittest.TestCase):
    def test_deps_first_overrides_priority(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr_dep(root, 1, priority="Low")                      # A (Low)
            _cr_dep(root, 2, priority="High", depends="CR0001")   # B (High) needs A
            ids = [b["id"] for b in _load().select_batch(root, "cr", "Proposed")]
            self.assertLess(ids.index("CR0001"), ids.index("CR0002"))  # A before B

    def test_cycle_raises(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr_dep(root, 1, depends="CR0002")
            _cr_dep(root, 2, depends="CR0001")
            with self.assertRaises(ValueError):
                _load().select_batch(root, "cr", "Proposed")

    def test_out_of_batch_dep_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr_dep(root, 2, priority="High", depends="CR9099")  # dep not in batch
            ids = [b["id"] for b in _load().select_batch(root, "cr", "Proposed")]
            self.assertEqual(ids, ["CR0002"])  # ordered by priority, no error

    def test_prose_id_is_not_a_dependency(self) -> None:
        # "see CR0001 for background" must NOT create a phantom ordering edge.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr_dep(root, 1, priority="Low")
            _cr_dep(root, 2, priority="High", depends="see CR0001 for background")
            ids = [b["id"] for b in _load().select_batch(root, "cr", "Proposed")]
            self.assertEqual(ids, ["CR0002", "CR0001"])  # priority order, no phantom dep

    def test_parenthetical_dep_parsed(self) -> None:
        # "CR0001 (referential integrity)" IS a dependency (leading ID token).
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr_dep(root, 1, priority="Low")
            _cr_dep(root, 2, priority="High", depends="CR0001 (referential integrity)")
            ids = [b["id"] for b in _load().select_batch(root, "cr", "Proposed")]
            self.assertLess(ids.index("CR0001"), ids.index("CR0002"))

    def test_transitive_chain_and_diamond(self) -> None:
        mod = _load()
        chain = mod._topo_order(
            [{"id": "C", "priority": "High"}, {"id": "B", "priority": "High"}, {"id": "A", "priority": "High"}],
            {"C": {"B"}, "B": {"A"}, "A": set()})
        self.assertEqual([i["id"] for i in chain], ["A", "B", "C"])
        diamond = mod._topo_order(
            [{"id": "D", "priority": "High"}, {"id": "B", "priority": "High"},
             {"id": "C", "priority": "High"}, {"id": "A", "priority": "High"}],
            {"D": {"B", "C"}, "B": {"A"}, "C": {"A"}, "A": set()})
        order = [i["id"] for i in diamond]
        self.assertEqual(order[0], "A")
        self.assertEqual(order[-1], "D")

    def test_cmd_plan_returns_nonzero_on_cycle(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr_dep(root, 1, depends="CR0002")
            _cr_dep(root, 2, depends="CR0001")
            rc = _load().main(["plan", "--crs", "Proposed", "--root", str(root)])
            self.assertEqual(rc, 2)


class CliTests(unittest.TestCase):
    def test_plan_json(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1, priority="High")
            mod = _load()
            rc = mod.main(["plan", "--crs", "Proposed", "--root", str(root), "--format", "json"])
            self.assertEqual(rc, 0)
            data = mod.build_plan(root, "cr", "Proposed", "priority")
            self.assertIn("batch", data)
            self.assertEqual(data["count"], 1)


class WsjfTests(unittest.TestCase):
    """--order wsjf weights priority against touched-code complexity (RFC0009 WS3)."""

    def _cr_aff(self, root, num, priority, affects, depends=None):
        d = root / "sdlc-studio" / "change-requests"
        d.mkdir(parents=True, exist_ok=True)
        body = (f"# CR-{num:04d}: c\n\n> **Status:** Proposed\n> **Priority:** {priority}\n"
                f"> **Affects:** {affects}\n")
        if depends:
            body += f"> **Depends on:** {depends}\n"
        (d / f"CR{num:04d}-x.md").write_text(body, encoding="utf-8")

    _DEEP = ("def deep(a, b, c, d):\n    if a:\n        if b:\n            if c:\n"
             "                if d:\n                    return 1\n")

    def test_wsjf_prefers_smaller_job_at_equal_priority(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "simple.py").write_text("def s(a):\n    return a\n", encoding="utf-8")
            (root / "complex.py").write_text(
                "def deep(a, b, c, d):\n    if a:\n        if b:\n            if c:\n"
                "                if d:\n                    return 1\n", encoding="utf-8")
            self._cr_aff(root, 1, "High", "complex.py")
            self._cr_aff(root, 2, "High", "simple.py")
            batch = _load().select_batch(root, "cr", "Proposed", order="wsjf")
            byid = {b["id"]: b for b in batch}
            self.assertEqual([b["id"] for b in batch], ["CR0002", "CR0001"])  # smaller job first
            self.assertGreater(byid["CR0001"]["complexity"], byid["CR0002"]["complexity"])
            self.assertGreater(byid["CR0001"]["token_budget"], byid["CR0002"]["token_budget"])

    def test_wsjf_falls_back_to_priority_without_affects(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr_aff(root, 1, "Low", "")
            self._cr_aff(root, 2, "High", "")
            batch = _load().select_batch(root, "cr", "Proposed", order="wsjf")
            self.assertEqual([b["id"] for b in batch], ["CR0002", "CR0001"])  # High first

    def test_wsjf_degrades_when_affects_unresolvable(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr_aff(root, 1, "High", "nonexistent/foo.py")
            batch = _load().select_batch(root, "cr", "Proposed", order="wsjf")
            self.assertEqual(batch[0]["complexity"], 0)  # unresolved path -> 0, no crash

    def test_priority_dominates_complexity(self) -> None:
        # A degraded (size-0) lower-priority unit must NOT outrank an assessed higher one.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "complex.py").write_text(self._DEEP, encoding="utf-8")
            self._cr_aff(root, 1, "Critical", "complex.py")     # assessed, big job
            self._cr_aff(root, 2, "Medium", "nonexistent.py")   # degraded, size 0
            ids = [b["id"] for b in _load().select_batch(root, "cr", "Proposed", order="wsjf")]
            self.assertEqual(ids, ["CR0001", "CR0002"])         # Critical first regardless

    def test_deps_win_over_complexity_tiebreak(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "complex.py").write_text(self._DEEP, encoding="utf-8")
            self._cr_aff(root, 1, "High", "complex.py")            # big job
            self._cr_aff(root, 2, "High", "", depends="CR0001")    # tiny job, needs CR0001
            ids = [b["id"] for b in _load().select_batch(root, "cr", "Proposed", order="wsjf")]
            self.assertLess(ids.index("CR0001"), ids.index("CR0002"))  # dep before dependent

    def test_degrades_when_assess_raises(self) -> None:
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "x.py").write_text("def f():\n    return 1\n", encoding="utf-8")
            self._cr_aff(root, 1, "High", "x.py")
            orig = mod.complexity.assess
            mod.complexity.assess = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom"))
            try:
                batch = mod.select_batch(root, "cr", "Proposed", order="wsjf")
            finally:
                mod.complexity.assess = orig
            self.assertEqual(batch[0]["complexity"], 0)  # exception swallowed, no crash

    def test_affects_parse_backtick_and_paren(self) -> None:
        files = _load()._affects_files(
            "> **Affects:** `scripts/x.py` (deleted), reference-y.md, scripts/z.py")
        self.assertEqual(files, ["scripts/x.py", "reference-y.md", "scripts/z.py"])


class AuthoringPlanTests(unittest.TestCase):
    """CR0088: the sprint planner accepts a PRD input (greenfield authoring bootstrap)."""

    def test_prd_input_signals_authoring_mode(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            prd = root / "sdlc-studio" / "prd.md"
            prd.parent.mkdir(parents=True)
            prd.write_text("# PRD\n", encoding="utf-8")
            plan = _load().build_authoring_plan(root, str(prd))
            self.assertEqual(plan["mode"], "authoring")
            self.assertEqual(plan["prd"], str(prd))
            self.assertEqual(plan["count"], 0)   # epics/stories don't exist yet

    def test_missing_prd_errors(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError):
                _load().build_authoring_plan(Path(d), str(Path(d) / "nope.md"))

    def test_prd_cli_path(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            prd = root / "prd.md"
            prd.write_text("# PRD\n", encoding="utf-8")
            rc = _load().main(["plan", "--prd", str(prd), "--root", str(root)])
            self.assertEqual(rc, 0)

    def test_plan_write_persists_artifact(self) -> None:  # CR0091
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1, status="Proposed")
            rc = _load().main(["plan", "--crs", "Proposed", "--write", "--root", str(root)])
            self.assertEqual(rc, 0)
            self.assertTrue((root / "sdlc-studio" / ".local" / "sprint-plan.json").exists())


class SeatWsjfTests(unittest.TestCase):
    """CR0099: seat-scored WSJF ordering, with graceful fallback."""

    def test_wsjf_score_math(self) -> None:
        # (value + tc + rr) / size
        self.assertEqual(_load().wsjf_score(8, 2, 3, 4), round(13 / 4, 3))
        self.assertEqual(_load().wsjf_score(5, 0, 0, 0), 5.0)   # size floored to 1

    def _inputs(self, root, mapping):
        import json
        p = root / "sdlc-studio" / ".local" / "wsjf-inputs.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(mapping), encoding="utf-8")

    def test_orders_by_wsjf_when_seats_scored(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1, priority="Low")     # low priority but high seat value
            _cr(root, 2, priority="High")    # high priority but low seat value
            self._inputs(root, {"CR0001": {"value": 20, "time_criticality": 0, "risk_reduction": 0},
                                "CR0002": {"value": 1, "time_criticality": 0, "risk_reduction": 0}})
            batch = _load().select_batch(root, "cr", "Proposed", order="wsjf")
            self.assertEqual([b["id"] for b in batch][0], "CR0001")  # WSJF beat raw priority
            self.assertIn("wsjf", batch[0])

    def test_falls_back_without_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1, priority="Low")
            _cr(root, 2, priority="High")
            batch = _load().select_batch(root, "cr", "Proposed", order="wsjf")   # no inputs
            self.assertEqual([b["id"] for b in batch][0], "CR0002")  # priority wins
            self.assertNotIn("wsjf", batch[0])

    def test_skip_personas_ignores_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1, priority="Low")
            _cr(root, 2, priority="High")
            self._inputs(root, {"CR0001": {"value": 20}})
            batch = _load().select_batch(root, "cr", "Proposed", order="wsjf", skip_personas=True)
            self.assertEqual([b["id"] for b in batch][0], "CR0002")  # inputs ignored -> priority
            self.assertNotIn("wsjf", batch[0])


class ReconcileBeforePlanTests(unittest.TestCase):
    """CR0094: the planner surfaces index drift before selecting; --strict refuses."""

    def test_strict_refuses_on_drift(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1, status="Proposed")   # a CR file but no _index.md -> missing-index drift
            rc = _load().main(["plan", "--crs", "Proposed", "--strict", "--root", str(root)])
            self.assertEqual(rc, 2)            # refused

    def test_warns_but_proceeds_without_strict(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1, status="Proposed")
            rc = _load().main(["plan", "--crs", "Proposed", "--root", str(root)])
            self.assertEqual(rc, 0)            # warns, still plans


def _bug_dep(root, num, severity="Medium", depends=None, status="Open"):
    d = root / "sdlc-studio" / "bugs"
    d.mkdir(parents=True, exist_ok=True)
    body = f"# BG{num:04d}: b\n\n> **Status:** {status}\n> **Severity:** {severity}\n"
    if depends:
        body += f"> **Depends on:** {depends}\n"
    (d / f"BG{num:04d}-x.md").write_text(body, encoding="utf-8")


class MixedBatchTests(unittest.TestCase):
    """A bugs + CRs tranche is first-class: combined queries, one merged
    dependency-waved plan, cross-type edges honoured."""

    def test_combined_queries_merge_into_one_plan(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1)
            _cr(root, 2)
            plan = _load().build_plan(root, queries=[("bug", "Open"), ("cr", "Proposed")])
            ids = [b["id"] for b in plan["batch"]]
            self.assertEqual(sorted(ids), ["BG0001", "CR0002"])
            self.assertEqual(plan["count"], 2)

    def test_cross_type_dependency_waves(self) -> None:
        # CR depends on a bug in the same tranche: the CR lands in a later wave.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug_dep(root, 1)
            dd = root / "sdlc-studio" / "change-requests"
            dd.mkdir(parents=True, exist_ok=True)
            (dd / "CR0002-x.md").write_text(
                "# CR-0002: c\n\n> **Status:** Proposed\n> **Priority:** High\n"
                "> **Depends on:** BG0001\n", encoding="utf-8")
            plan = _load().build_plan(root, queries=[("bug", "Open"), ("cr", "Proposed")])
            self.assertEqual(plan["waves"], [["BG0001"], ["CR0002"]])
            self.assertTrue(plan["deps_declared"])

    def test_shared_weight_scale_across_types(self) -> None:
        # Critical bug and P1 CR outrank a Medium bug and P3 CR: one documented scale.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1, severity="Critical")
            _bug(root, 2, severity="medium")            # lowercase in the field is fine
            _cr(root, 3, priority="P1")
            _cr(root, 4, priority="P3")
            plan = _load().build_plan(root, queries=[("bug", "Open"), ("cr", "Proposed")])
            ids = [b["id"] for b in plan["batch"]]
            self.assertEqual(set(ids[:2]), {"BG0001", "CR0003"})  # weight-0/1 first
            self.assertEqual(set(ids[2:]), {"BG0002", "CR0004"})

    def test_single_kind_wrapper_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1)
            batch = _load().select_batch(root, "cr", "Proposed")
            self.assertEqual([b["id"] for b in batch], ["CR0001"])

    def test_cli_accepts_combined_flags(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1)
            _cr(root, 2)
            rc = _load().main(["plan", "--bugs", "Open", "--crs", "Proposed",
                               "--root", str(root)])
            self.assertEqual(rc, 0)


class WeightRobustnessTests(unittest.TestCase):
    def test_blank_but_present_severity_ranks_medium(self) -> None:
        # A half-filled template ('> **Severity:**   ') must plan, not crash.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            dd = root / "sdlc-studio" / "bugs"; dd.mkdir(parents=True)
            (dd / "BG0001-x.md").write_text(
                "# BG0001: b\n\n> **Status:** Open\n> **Severity:**   \n", encoding="utf-8")
            plan = _load().build_plan(root, "bug", "Open")
            self.assertEqual(plan["count"], 1)

    def test_weight_blank_and_decorated(self) -> None:
        sp = _load()
        self.assertEqual(sp._weight("  "), 2)          # blank -> Medium, no crash
        self.assertEqual(sp._weight("High (gate)"), 1)
        self.assertEqual(sp._weight("p1"), 0)


class SeatSizeTests(unittest.TestCase):
    """The Engineering seat can supply size in wsjf-inputs.json; an unresolvable
    Affects (new-file work) is UNKNOWN size, never minimal."""

    def _inputs(self, root, data):
        d = root / "sdlc-studio" / ".local"
        d.mkdir(parents=True, exist_ok=True)
        import json as _json
        (d / "wsjf-inputs.json").write_text(_json.dumps(data), encoding="utf-8")

    def test_seat_size_preferred_over_complexity_seed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1)
            self._inputs(root, {"CR0001": {"value": 9, "time_criticality": 9,
                                           "risk_reduction": 9, "size": 9}})
            batch = _load().select_batch(root, "cr", "Proposed", order="wsjf")
            self.assertEqual(batch[0]["size"], 9)
            self.assertEqual(batch[0]["wsjf"], 3.0)  # 27 / seat size 9, not /1

    def test_unresolvable_affects_uses_declared_default_not_minimal(self) -> None:
        # New-file work with no seat size is UNKNOWN effort: the declared neutral
        # default divides the score, instead of size 0 -> cheapest job in the batch.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            dd = root / "sdlc-studio" / "change-requests"
            dd.mkdir(parents=True, exist_ok=True)
            (dd / "CR0001-x.md").write_text(
                "# CR-0001: c\n\n> **Status:** Proposed\n> **Priority:** Medium\n"
                "> **Affects:** scripts/does-not-exist-yet.py\n", encoding="utf-8")
            self._inputs(root, {"CR0001": {"value": 9, "time_criticality": 9,
                                           "risk_reduction": 9}})
            batch = sp.select_batch(root, "cr", "Proposed", order="wsjf")
            self.assertEqual(batch[0]["size"], sp.DEFAULT_UNKNOWN_SIZE)
            self.assertEqual(batch[0]["wsjf"],
                             round(27 / sp.DEFAULT_UNKNOWN_SIZE, 3))  # never /1

    def test_resolvable_affects_still_seeds_from_complexity(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "real.py").write_text("def f(x):\n    if x:\n        return 1\n    return 0\n",
                                          encoding="utf-8")
            dd = root / "sdlc-studio" / "change-requests"
            dd.mkdir(parents=True, exist_ok=True)
            (dd / "CR0001-x.md").write_text(
                "# CR-0001: c\n\n> **Status:** Proposed\n> **Priority:** Medium\n"
                "> **Affects:** real.py\n", encoding="utf-8")
            self._inputs(root, {"CR0001": {"value": 6, "time_criticality": 0,
                                           "risk_reduction": 0}})
            batch = _load().select_batch(root, "cr", "Proposed", order="wsjf")
            self.assertIn("wsjf", batch[0])   # complexity seed still works when files resolve


class WorklistTests(unittest.TestCase):
    """The documented worklist file (ids one per line) is a real batch source."""

    def test_worklist_selects_listed_units(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1)
            _cr(root, 2)
            _cr(root, 3)  # not listed - stays out
            wl = root / "tranche.md"
            wl.write_text("# tranche\n\n- BG0001\nCR-0002\n", encoding="utf-8")
            plan = _load().build_plan(root, worklist=str(wl))
            self.assertEqual(sorted(b["id"] for b in plan["batch"]), ["BG0001", "CR0002"])

    def test_worklist_unknown_id_errors(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            wl = root / "tranche.md"
            wl.write_text("BG0042\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                _load().build_plan(root, worklist=str(wl))

    def test_cli_worklist(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1)
            wl = root / "wl.md"
            wl.write_text("BG0001\n", encoding="utf-8")
            rc = _load().main(["plan", "--worklist", str(wl), "--root", str(root)])
            self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
