"""Unit tests for sprint.py (RED first - the script does not exist yet)."""
from __future__ import annotations

import argparse
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ dir, for the shared gitutil helper
import gitutil  # noqa: E402

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


class SeatProvenanceTests(unittest.TestCase):
    """wsjf-inputs.json is a cross-sprint side-channel: the plan must say which
    units carry seat inputs, which fell back, and how fresh the file is."""

    def _inputs(self, root, mapping, age_days=0):
        import json as _json
        import os
        import time
        p = root / "sdlc-studio" / ".local" / "wsjf-inputs.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(_json.dumps(mapping), encoding="utf-8")
        if age_days:
            t = time.time() - age_days * 86400
            os.utime(p, (t, t))
        return p

    def test_plan_records_scored_and_unscored(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1)
            _cr(root, 2)
            self._inputs(root, {"CR0001": {"value": 5, "time_criticality": 1,
                                           "risk_reduction": 1, "size": 2}})
            data = _load().build_plan(root, "cr", "Proposed", order="wsjf")
            prov = data["seat_provenance"]
            self.assertEqual(prov["scored"], ["CR0001"])
            self.assertEqual(prov["unscored"], ["CR0002"])
            self.assertIsNotNone(prov["written_at"])
            self.assertFalse(prov["stale"])

    def test_fresh_inputs_not_stale_old_inputs_advisory(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1)
            self._inputs(root, {"CR0001": {"value": 5, "time_criticality": 1,
                                           "risk_reduction": 1, "size": 2}},
                         age_days=10)
            data = _load().build_plan(root, "cr", "Proposed", order="wsjf")
            prov = data["seat_provenance"]
            self.assertTrue(prov["stale"])            # 10 days > default 7
            self.assertGreater(prov["age_days"], 9)
            self.assertEqual(prov["stale_after_days"], 7)

    def test_no_inputs_file_names_everyone_unscored(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1)
            data = _load().build_plan(root, "cr", "Proposed", order="wsjf")
            prov = data["seat_provenance"]
            self.assertEqual(prov["scored"], [])
            self.assertEqual(prov["unscored"], ["CR0001"])
            self.assertIsNone(prov["written_at"])
            self.assertFalse(prov["stale"])           # nothing to be stale about

    def test_priority_order_has_no_seat_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1)
            data = _load().build_plan(root, "cr", "Proposed", order="priority")
            self.assertIsNone(data.get("seat_provenance"))


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


class RepeatedStatusFilterTests(unittest.TestCase):
    """A status filter is a set: `--crs Proposed --crs Deferred` must select BOTH,
    never silently drop the first (the argparse `store` overwrite that produced a
    plan quietly missing two CRs)."""

    def test_repeated_crs_merges_both_statuses(self) -> None:
        sprint = _load()
        args = sprint.build_parser().parse_args(
            ["plan", "--crs", "Proposed", "--crs", "Deferred"])
        queries, worklist, rc = sprint._plan_batch_source(args)
        self.assertIsNone(rc)
        self.assertEqual(queries, [("cr", "Proposed"), ("cr", "Deferred")])

    def test_repeated_crs_reaches_both_units_in_the_plan(self) -> None:
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1, status="Proposed")
            _cr(root, 2, status="Deferred")
            plan = sprint.build_plan(
                root, queries=[("cr", "Proposed"), ("cr", "Deferred")])
            self.assertEqual(sorted(b["id"] for b in plan["batch"]), ["CR0001", "CR0002"])

    def test_mixed_repeated_filters_merge(self) -> None:
        sprint = _load()
        args = sprint.build_parser().parse_args(
            ["plan", "--crs", "Proposed", "--bugs", "Open", "--crs", "Deferred"])
        queries, _worklist, rc = sprint._plan_batch_source(args)
        self.assertIsNone(rc)
        self.assertEqual(
            queries, [("bug", "Open"), ("cr", "Proposed"), ("cr", "Deferred")])


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


class FallbackSizeTests(unittest.TestCase):
    """CR0149: without a seat size, the complexity seed never stands in as the
    WSJF denominator - a one-line fix in a complex file must not sink."""

    def test_small_fix_in_complex_file_ranks_by_default_not_file_complexity(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            # a complex existing file the "small fix" CR touches
            (root / "big.py").write_text(
                "def f(x):\n" + "".join(f"    if x > {i}:\n        x -= {i}\n"
                                         for i in range(12)) + "    return x\n",
                encoding="utf-8")
            dd = root / "sdlc-studio" / "change-requests"
            dd.mkdir(parents=True, exist_ok=True)
            (dd / "CR0001-x.md").write_text(
                "# CR-0001: small fix\n\n> **Status:** Proposed\n> **Priority:** Medium\n"
                "> **Affects:** big.py\n", encoding="utf-8")
            (dd / "CR0002-x.md").write_text(
                "# CR-0002: peer\n\n> **Status:** Proposed\n> **Priority:** Medium\n",
                encoding="utf-8")
            local = root / "sdlc-studio" / ".local"
            local.mkdir(parents=True, exist_ok=True)
            import json as _json
            (local / "wsjf-inputs.json").write_text(_json.dumps({
                "CR0001": {"value": 9, "time_criticality": 9, "risk_reduction": 9},
                "CR0002": {"value": 3, "time_criticality": 3, "risk_reduction": 3}}),
                encoding="utf-8")
            batch = sp.select_batch(root, "cr", "Proposed", order="wsjf")
            by_id = {b["id"]: b for b in batch}
            # denominator is the neutral default for BOTH (no seat size anywhere);
            # the higher-scored small fix ranks first instead of sinking on
            # big.py's cognitive complexity
            self.assertEqual(by_id["CR0001"]["size"], sp.DEFAULT_UNKNOWN_SIZE)
            self.assertEqual(by_id["CR0001"]["wsjf"], round(27 / sp.DEFAULT_UNKNOWN_SIZE, 3))
            self.assertEqual([b["id"] for b in batch][0], "CR0001")
            # the seed survives as tiebreak input, not as size
            self.assertGreater(by_id["CR0001"]["complexity"], 0)


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


class RoutingEnrichmentTests(unittest.TestCase):
    """RFC0026 / CR0190: the plan carries difficulty (always) and tier/model (only
    when routing.enabled)."""

    def _routed_config(self, root, enabled=True):
        d = root / "sdlc-studio"
        d.mkdir(parents=True, exist_ok=True)
        (d / ".config.yaml").write_text(
            "routing:\n"
            f"  enabled: {'true' if enabled else 'false'}\n"
            "  models:\n"
            "    small: model-s\n"
            "    large: model-l\n", encoding="utf-8")

    def test_difficulty_emitted_under_both_orders(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1)
            for order in ("priority", "wsjf"):
                batch = _load().select_batch(root, "cr", "Proposed", order=order)
                self.assertIn("difficulty", batch[0], f"order={order}")
                self.assertIn("band", batch[0]["difficulty"])

    def test_tier_and_model_only_when_routing_enabled(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1)
            self._routed_config(root, enabled=False)
            batch = _load().select_batch(root, "cr", "Proposed")
            self.assertNotIn("tier", batch[0])
            self.assertNotIn("model", batch[0])
            self._routed_config(root, enabled=True)
            batch = _load().select_batch(root, "cr", "Proposed")
            self.assertIn("tier", batch[0])
            self.assertIn(batch[0]["tier"], ("small", "large"))
            self.assertIn(batch[0]["model"], ("model-s", "model-l"))

    def test_estimator_failure_degrades_that_unit_only(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1)
            _cr(root, 2)
            sprint = _load()
            import route as route_mod
            real = route_mod.estimate
            calls = {"n": 0}

            def flaky(r, p):
                calls["n"] += 1
                if "CR0001" in str(p):
                    raise RuntimeError("boom")
                return real(r, p)
            route_mod.estimate = flaky
            try:
                batch = sprint.select_batch(root, "cr", "Proposed")
            finally:
                route_mod.estimate = real
            by_id = {b["id"]: b for b in batch}
            self.assertNotIn("difficulty", by_id["CR0001"])  # degraded, not crashed
            self.assertIn("difficulty", by_id["CR0002"])


import subprocess as _sp

sprint = _load()


def _run(cwd, *args):
    return _sp.run(["git", "-C", str(cwd), *args], capture_output=True, text=True,
                   env=gitutil.git_env())  # host config neutralised (gpgsign-safe)


def _behind_repo(d):
    """A work repo one commit behind its origin (a teammate pushed a CR)."""
    origin = Path(d) / "origin.git"
    _sp.run(["git", "init", "-q", "--bare", str(origin)])
    _sp.run(["git", "-C", str(origin), "symbolic-ref", "HEAD", "refs/heads/main"])
    work = Path(d) / "work"; work.mkdir()
    _run(work, "init", "-q"); _run(work, "checkout", "-q", "-b", "main")
    _run(work, "config", "user.email", "t@t"); _run(work, "config", "user.name", "t")
    _run(work, "remote", "add", "origin", str(origin))
    (work / "README.md").write_text("base\n", encoding="utf-8")
    _run(work, "add", "-A"); _run(work, "commit", "-qm", "base")
    _run(work, "push", "-q", "origin", "main")
    other = Path(d) / "other"
    _sp.run(["git", "clone", "-q", str(origin), str(other)])
    _run(other, "config", "user.email", "o@o"); _run(other, "config", "user.name", "o")
    crd = other / "sdlc-studio" / "change-requests"; crd.mkdir(parents=True)
    (crd / "CR0001-remote.md").write_text("# CR-0001: remote\n", encoding="utf-8")
    _run(other, "add", "-A"); _run(other, "commit", "-qm", "remote cr")
    _run(other, "push", "-q", "origin", "main")
    return work


def _up_to_date_repo(d):
    """A work clone that is level with origin (no divergence)."""
    origin = Path(d) / "origin.git"
    _sp.run(["git", "init", "-q", "--bare", str(origin)])
    _sp.run(["git", "-C", str(origin), "symbolic-ref", "HEAD", "refs/heads/main"])
    work = Path(d) / "work"; work.mkdir()
    _run(work, "init", "-q"); _run(work, "checkout", "-q", "-b", "main")
    _run(work, "config", "user.email", "t@t"); _run(work, "config", "user.name", "t")
    _run(work, "remote", "add", "origin", str(origin))
    (work / "README.md").write_text("base\n", encoding="utf-8")
    _run(work, "add", "-A"); _run(work, "commit", "-qm", "base")
    _run(work, "push", "-q", "origin", "main")
    _run(work, "fetch", "-q", "origin")
    return work


def _remote_id_repo(d, branch):
    """A work repo whose origin default branch (`branch`) holds CR0005 that local deleted."""
    origin = Path(d) / "origin.git"
    _sp.run(["git", "init", "-q", "--bare", str(origin)])
    _sp.run(["git", "-C", str(origin), "symbolic-ref", "HEAD", f"refs/heads/{branch}"])
    seed = Path(d) / "seed"; seed.mkdir()
    _run(seed, "init", "-q"); _run(seed, "checkout", "-q", "-b", branch)
    _run(seed, "config", "user.email", "s@s"); _run(seed, "config", "user.name", "s")
    _run(seed, "remote", "add", "origin", str(origin))
    crd = seed / "sdlc-studio" / "change-requests"; crd.mkdir(parents=True)
    (crd / "CR0005-remote.md").write_text("# CR-0005: r\n", encoding="utf-8")
    _run(seed, "add", "-A"); _run(seed, "commit", "-qm", "cr5")
    _run(seed, "push", "-q", "origin", branch)
    work = Path(d) / "work"
    _sp.run(["git", "clone", "-q", str(origin), str(work)])
    _run(work, "config", "user.email", "w@w"); _run(work, "config", "user.name", "w")
    _run(work, "rm", "-q", "sdlc-studio/change-requests/CR0005-remote.md")
    _run(work, "commit", "-qm", "remove locally")   # gone from disk, still on origin/<branch>
    return work


class OriginDriftTests(unittest.TestCase):
    """US0099/CR0188: sprint plan compares local HEAD to origin; warns when behind."""

    def test_origin_drift_detects_behind(self):
        with tempfile.TemporaryDirectory() as d:
            work = _behind_repo(d)
            drift = sprint.origin_drift(work, do_fetch=True)   # fetch from the LOCAL origin (offline)
            self.assertTrue(drift["remote"])
            self.assertEqual(drift["behind"], 1)
            self.assertIn("sdlc-studio/change-requests/CR0001-remote.md", drift["paths"])


class OriginDriftNoFalsePositiveTests(unittest.TestCase):
    """US0099/CR0188 AC2: no remote / non-git / up-to-date-with-origin all stay silent."""

    def test_no_remote_is_silent(self):
        with tempfile.TemporaryDirectory() as d:
            work = Path(d) / "w"; work.mkdir()
            _run(work, "init", "-q")
            drift = sprint.origin_drift(work, do_fetch=False)
            self.assertFalse(drift["remote"])
            self.assertEqual(drift["behind"], 0)

    def test_non_git_dir_is_silent(self):
        with tempfile.TemporaryDirectory() as d:
            drift = sprint.origin_drift(Path(d), do_fetch=False)
            self.assertFalse(drift["remote"])
            self.assertEqual(drift["behind"], 0)

    def test_up_to_date_with_origin_is_silent(self):
        with tempfile.TemporaryDirectory() as d:
            work = _up_to_date_repo(d)
            drift = sprint.origin_drift(work, do_fetch=True)
            self.assertTrue(drift["remote"])
            self.assertEqual(drift["behind"], 0)                 # level with origin
            self.assertIsNone(sprint._drift_warning(drift, set()))  # no warning


class OriginDriftWarningTests(unittest.TestCase):
    def test_up_to_date_no_warning(self):
        self.assertIsNone(sprint._drift_warning({"behind": 0}, set()))

    def test_behind_warns_and_names_overlap(self):
        drift = {"behind": 2, "branch": "main",
                 "paths": ["sdlc-studio/change-requests/CR0001-x.md", "README.md"]}
        w = sprint._drift_warning(drift, {"sdlc-studio/change-requests/CR0001-x.md"})
        self.assertIn("2 commit(s) behind", w)
        self.assertIn("CR0001-x.md", w)

    def test_behind_without_overlap_still_warns(self):
        w = sprint._drift_warning({"behind": 1, "branch": "main", "paths": ["README.md"]}, set())
        self.assertIn("behind", w)
        self.assertNotIn("touch batch artifacts", w)


class RemoteIdAllocationTests(unittest.TestCase):
    """US0099/CR0188 AC3: id allocation is remote-aware - it will not re-mint an id the remote
    already holds (the collision the incident hit)."""

    def _next_id(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("next_id", Path(SCRIPT).parent / "next_id.py")
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        return m

    def test_allocation_skips_a_remote_only_id_on_main(self):
        next_id = self._next_id()
        with tempfile.TemporaryDirectory() as d:
            work = _remote_id_repo(d, "main")
            self.assertEqual(next_id.allocate_number("cr", work, remote=True), 6)   # remote-aware
            self.assertEqual(next_id.allocate_number("cr", work, remote=False), 1)  # local-only

    def test_allocation_remote_aware_on_non_main_default(self):
        # the MAJOR: on a master/develop-default repo, remote_ids must resolve the actual default
        # branch, not hardcode origin/main - else the anti-collision protection silently no-ops.
        next_id = self._next_id()
        with tempfile.TemporaryDirectory() as d:
            work = _remote_id_repo(d, "master")
            self.assertEqual(next_id.allocate_number("cr", work, remote=True), 6)   # not 1


class OriginDriftCollisionTests(unittest.TestCase):
    """US0099/CR0188 AC5: sprint plan warns before an id-collision would occur."""

    def _clean_bug_batch(self, work):
        """A reconcile-clean single-bug batch, so the origin-drift path is not masked by the
        reconcile-before-plan strict gate."""
        _bug(work, 1, status="Open")
        (work / "sdlc-studio" / "bugs" / "_index.md").write_text(
            "# Bugs\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Open | 1 |\n"
            "| **Total** | **1** |\n\n## All\n\n| ID | Title | Status | Severity | Created | Updated |\n"
            "| --- | --- | --- | --- | --- | --- |\n"
            "| [BG0001](BG0001-x.md) | b | Open | Medium | 2026-07-09 | 2026-07-09 |\n",
            encoding="utf-8")

    def _args(self, work, strict):
        import argparse
        return argparse.Namespace(
            prd=None, bugs=["Open"], crs=None, stories=None, worklist=None, epic=None,
            order="priority", write=False, strict=strict, no_fetch=False,
            skip_personas=False, root=str(work), format="json")

    def test_cmd_plan_warns_when_behind_a_remote_with_same_numbered_file(self):
        import contextlib, io
        with tempfile.TemporaryDirectory() as d:
            work = _behind_repo(d)
            self._clean_bug_batch(work)
            err = io.StringIO()
            with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
                rc = sprint.cmd_plan(self._args(work, strict=False))
            self.assertEqual(rc, 0)                  # advisory: warns but does not fail
            self.assertIn("origin drift", err.getvalue())
            self.assertIn("behind", err.getvalue())

    def test_cmd_plan_strict_refuses_when_behind(self):
        import contextlib, io
        with tempfile.TemporaryDirectory() as d:
            work = _behind_repo(d)
            self._clean_bug_batch(work)
            err = io.StringIO()
            with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
                rc = sprint.cmd_plan(self._args(work, strict=True))
            self.assertEqual(rc, 2)                  # --strict refuses the stale plan
            self.assertIn("behind", err.getvalue())


class PreflightSurvivesAllOrdersTests(unittest.TestCase):
    """BG0085: waves=None (manual order, empty batch) killed the preflight via a swallowed
    TypeError - the --strict refusal must fire for EVERY order on a behind-origin clone."""

    def _seed_cr(self, work):
        crd = work / "sdlc-studio" / "change-requests"
        crd.mkdir(parents=True, exist_ok=True)
        (crd / "CR0002-local.md").write_text(
            "# CR-0002: local\n\n> **Status:** Proposed\n> **Priority:** Medium\n",
            encoding="utf-8")
        (crd / "_index.md").write_text(
            "# CRs\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Proposed | 1 |\n"
            "| **Total** | **1** |\n\n## All\n\n| ID | Title | Status | Priority | Type | Date | Linked Epics |\n"
            "| --- | --- | --- | --- | --- | --- | --- |\n"
            "| [CR-0002](CR0002-local.md) | local | Proposed | Medium | X | 2026-07-10 | -- |\n",
            encoding="utf-8")

    def test_manual_order_strict_refuses_when_behind(self):
        import io
        from contextlib import redirect_stderr, redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            work = _behind_repo(d)
            self._seed_cr(work)
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                rc = sprint.main(["plan", "--crs", "Proposed", "--order", "manual",
                                  "--strict", "--root", str(work)])
            self.assertEqual(rc, 2, err.getvalue() + out.getvalue())
            self.assertIn("behind", err.getvalue())

    def test_empty_batch_strict_still_refuses_when_behind(self):
        import io
        from contextlib import redirect_stderr, redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            work = _behind_repo(d)  # no plannable units in work at all
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                rc = sprint.main(["plan", "--crs", "Proposed", "--order", "priority",
                                  "--strict", "--root", str(work)])
            self.assertEqual(rc, 2, err.getvalue() + out.getvalue())


class PlanLessonsDigestTests(unittest.TestCase):
    """CR0236 AC2: the plan an agent reads at sprint start CONTAINS the still-valid lessons -
    it does not point at a file the agent may not open."""

    LOG = ("# Project Lessons\n\n## L-0002: Read every creation path\n\n"
           "- **Rule:** grep for every code path that does the thing\n\n"
           "## L-0001: Closed one\n\n- **Status:** Closed - obsolete\n")

    def _seed(self, root: Path) -> None:
        _cr(root, 1, status="Proposed")
        p = root / "sdlc-studio" / ".local" / "lessons.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(self.LOG, encoding="utf-8")

    def test_build_plan_carries_the_open_lessons(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._seed(root)
            plan = _load().build_plan(root, "cr", "Proposed")
            ids = [x["id"] for x in plan["lessons"]["lessons"]]
            self.assertEqual(ids, ["L-0002"])  # the closed one is not in force

    def test_plan_output_prints_the_lessons(self) -> None:
        import io
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._seed(root)
            out = io.StringIO()
            with redirect_stdout(out):
                rc = _load().main(["plan", "--crs", "Proposed", "--root", str(root),
                                   "--no-fetch"])
            self.assertEqual(rc, 0)
            text = out.getvalue()
            self.assertIn("L-0002", text)
            self.assertIn("Read every creation path", text)
            self.assertNotIn("L-0001", text)  # closed lessons are not in force


class EffortSizingTests(unittest.TestCase):
    """The human `Effort:` S/M/L captured at filing is a real WSJF size input.

    It was recorded on every CR and read by nothing: with no seat score and no `Affects`, WSJF
    collapsed to plain priority and every unit forecast the same flat base. These tests assert
    the BEHAVIOUR changes (size and forecast move with the estimate), never that the string
    'effort' appears in the source - `rg -qi effort sprint.py` passed while the field was
    entirely unread, which is exactly the false-green this replaces.
    """

    def _cr(self, root, num, effort=None, priority="Medium", affects=None):
        d = root / "sdlc-studio" / "change-requests"
        d.mkdir(parents=True, exist_ok=True)
        body = f"# CR-{num:04d}: c\n\n> **Status:** Proposed\n> **Priority:** {priority}\n"
        if affects:
            body += f"> **Affects:** {affects}\n"
        body += "\n## Impact\n\nSomething.\n"
        if effort:
            body += f"\n**Effort:** {effort}\n"
        (d / f"CR{num:04d}-x.md").write_text(body, encoding="utf-8")

    def _bug(self, root, num, effort=None, severity="Medium"):
        d = root / "sdlc-studio" / "bugs"
        d.mkdir(parents=True, exist_ok=True)
        body = f"# BG{num:04d}: b\n\n> **Status:** Open\n> **Severity:** {severity}\n"
        if effort:
            body += f"> **Effort:** {effort}\n"
        (d / f"BG{num:04d}-x.md").write_text(body, encoding="utf-8")

    def test_small_and_large_effort_produce_different_sizes_without_seats_or_affects(self) -> None:
        # The headline gap: no seat score, no Affects. Today both units size identically.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            self._cr(root, 1, effort="S")
            self._cr(root, 2, effort="L")
            by_id = {b["id"]: b for b in sp.select_batch(root, "cr", "Proposed", order="wsjf")}
            self.assertLess(by_id["CR0001"]["size"], by_id["CR0002"]["size"])
            self.assertEqual(by_id["CR0001"]["size"], sp.EFFORT_SIZE["S"])
            self.assertEqual(by_id["CR0002"]["size"], sp.EFFORT_SIZE["L"])

    def test_undeclared_effort_keeps_the_neutral_default(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            self._cr(root, 1)
            batch = sp.select_batch(root, "cr", "Proposed", order="wsjf")
            self.assertEqual(batch[0]["size"], sp.DEFAULT_UNKNOWN_SIZE)
            self.assertNotIn("effort", batch[0])

    def test_seat_size_still_beats_the_declared_effort(self) -> None:
        # The seats scored it: their estimate is the authority, effort is the fallback.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            self._cr(root, 1, effort="S")
            local = root / "sdlc-studio" / ".local"
            local.mkdir(parents=True, exist_ok=True)
            import json as _json
            (local / "wsjf-inputs.json").write_text(_json.dumps({
                "CR0001": {"value": 9, "time_criticality": 9, "risk_reduction": 9, "size": 9}}),
                encoding="utf-8")
            batch = sp.select_batch(root, "cr", "Proposed", order="wsjf")
            self.assertEqual(batch[0]["size"], 9)          # seat estimate, not EFFORT_SIZE['S']
            self.assertEqual(batch[0]["wsjf"], 3.0)

    def test_effort_divides_the_wsjf_score_when_seats_scored_no_size(self) -> None:
        # Seats scored value/urgency/risk but left size out: the human estimate fills it.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            self._cr(root, 1, effort="L")
            local = root / "sdlc-studio" / ".local"
            local.mkdir(parents=True, exist_ok=True)
            import json as _json
            (local / "wsjf-inputs.json").write_text(_json.dumps({
                "CR0001": {"value": 9, "time_criticality": 9, "risk_reduction": 9}}),
                encoding="utf-8")
            batch = sp.select_batch(root, "cr", "Proposed", order="wsjf")
            self.assertEqual(batch[0]["size"], sp.EFFORT_SIZE["L"])
            self.assertEqual(batch[0]["wsjf"], round(27 / sp.EFFORT_SIZE["L"], 3))

    def test_a_bug_can_be_sized_too(self) -> None:
        # A bug's Severity is urgency; its Effort is size. Until now it had no size at all.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            self._bug(root, 1, effort="S")
            self._bug(root, 2, effort="L")
            by_id = {b["id"]: b for b in sp.select_batch(root, "bug", "Open", order="wsjf")}
            self.assertEqual(by_id["BG0001"]["size"], sp.EFFORT_SIZE["S"])
            self.assertEqual(by_id["BG0002"]["size"], sp.EFFORT_SIZE["L"])

    def test_decorated_and_worded_values_parse_and_junk_is_undeclared(self) -> None:
        sp = _load()
        self.assertEqual(sp._effort_code("**Effort:** M - two files\n"), "M")
        self.assertEqual(sp._effort_code("> **Effort:** large\n"), "L")
        self.assertIsNone(sp._effort_code("> **Effort:** unknown\n"))
        self.assertIsNone(sp._effort_code("# no field here\n"))
        self.assertIsNone(sp._effort_code("an agent under effort pressure skips it\n"))


class EffortForecastTests(unittest.TestCase):
    """The token forecast reflects the declared effort when no `Affects` is declared.

    A unit with no file list forecast the flat `BASE_TOKEN_BUDGET` whatever its size, which is
    how a batch of ten paperwork-light units forecast exactly 10 x 50,000.
    """

    def _cr(self, root, num, effort=None, affects=None):
        d = root / "sdlc-studio" / "change-requests"
        d.mkdir(parents=True, exist_ok=True)
        body = f"# CR-{num:04d}: c\n\n> **Status:** Proposed\n> **Priority:** Medium\n"
        if affects:
            body += f"> **Affects:** {affects}\n"
        if effort:
            body += f"\n**Effort:** {effort}\n"
        (d / f"CR{num:04d}-x.md").write_text(body, encoding="utf-8")

    def test_large_forecasts_more_than_small_when_no_files_are_named(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            self._cr(root, 1, effort="S")
            self._cr(root, 2, effort="L")
            fc = sp.build_plan(root, "cr", "Proposed", order="wsjf")["token_forecast"]["per_unit"]
            self.assertLess(fc["CR0001"], fc["CR0002"])
            self.assertEqual(fc["CR0001"], sp.BASE_TOKEN_BUDGET)  # S keeps the measured floor

    def test_effort_reaches_the_forecast_in_priority_order_too(self) -> None:
        # priority/manual order never stamps a token_budget - the forecast derives it, and must
        # read the effort there as well, or the same batch forecasts differently per order mode.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            self._cr(root, 1, effort="L")
            pri = sp.build_plan(root, "cr", "Proposed", order="priority")["token_forecast"]
            wsjf = sp.build_plan(root, "cr", "Proposed", order="wsjf")["token_forecast"]
            self.assertEqual(pri["tokens"], wsjf["tokens"])
            self.assertGreater(pri["tokens"], sp.BASE_TOKEN_BUDGET)

    def test_declared_complexity_is_never_inflated_by_effort(self) -> None:
        # The constants are fitted to measured actuals: a unit whose files resolve keeps the
        # measured model exactly. Effort only fills the gap where complexity is absent.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            (root / "real.py").write_text(
                "def f(x):\n    if x:\n        return 1\n    return 0\n", encoding="utf-8")
            self._cr(root, 1, effort="L", affects="real.py")
            batch = sp.select_batch(root, "cr", "Proposed", order="wsjf")
            cx = batch[0]["complexity"]
            self.assertGreater(cx, 0)
            self.assertEqual(batch[0]["token_budget"],
                             sp.BASE_TOKEN_BUDGET + sp.TOKENS_PER_COGNITIVE * cx)


try:
    import yaml  # noqa: F401
    HAVE_YAML = True
except ImportError:  # pragma: no cover - the config override needs PyYAML
    HAVE_YAML = False


def _load_loop_guard():
    path = SCRIPT.parent / "loop_guard.py"
    spec = importlib.util.spec_from_file_location("loop_guard", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["loop_guard"] = mod
    spec.loader.exec_module(mod)
    return mod


def _config(root: Path, body: str) -> None:
    d = root / "sdlc-studio"
    d.mkdir(parents=True, exist_ok=True)
    (d / ".config.yaml").write_text(body, encoding="utf-8")


def _drift_free_crs(root: Path, n: int) -> None:
    """n Proposed CRs plus the matching index, so `--strict` has nothing else to refuse on."""
    crd = root / "sdlc-studio" / "change-requests"
    crd.mkdir(parents=True, exist_ok=True)
    rows = []
    for i in range(1, n + 1):
        _cr(root, i)
        rows.append(f"| [CR-{i:04d}](CR{i:04d}-x.md) | c | Proposed | Medium | X "
                    f"| 2026-07-14 | -- |")
    (crd / "_index.md").write_text(
        f"# CRs\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Proposed | {n} |\n"
        f"| **Total** | **{n}** |\n\n## All\n\n"
        "| ID | Title | Status | Priority | Type | Date | Linked Epics |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n" + "\n".join(rows) + "\n",
        encoding="utf-8")


class CapacityBudgetTests(unittest.TestCase):
    """CR0259: the batch is sized against the sprint capacity AT PLAN TIME.

    Behaviour only - these assert what the planner REPORTS, never that a word appears in the
    source. The over-budget signal is a warning: the plan is still produced, and still exits 0.
    """

    def test_a_batch_within_capacity_reports_within_budget(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1)
            cap = _load().build_plan(root, "cr", "Proposed")["capacity"]
            self.assertEqual(cap["over"], [])
            self.assertFalse(cap["over_budget"])

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_a_batch_over_the_token_budget_is_flagged_with_the_numbers(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _config(root, "capacity:\n  tokens: 60000\n")  # one unit's floor is 50,000
            _cr(root, 1)
            _cr(root, 2)
            cap = _load().build_plan(root, "cr", "Proposed")["capacity"]
            self.assertIn("tokens", cap["over"])
            self.assertTrue(cap["over_budget"])
            # the numbers are reported, not just the verdict
            self.assertEqual(cap["budget"]["tokens"], 60_000)
            self.assertGreater(cap["forecast"]["tokens"], 60_000)

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_a_batch_over_the_unit_budget_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _config(root, "capacity:\n  units: 2\n")
            for n in (1, 2, 3):
                _cr(root, n)
            cap = _load().build_plan(root, "cr", "Proposed")["capacity"]
            self.assertIn("units", cap["over"])
            self.assertEqual(cap["units"], 3)
            self.assertEqual(cap["budget"]["units"], 2)

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_zero_on_an_axis_is_unbounded(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _config(root, "capacity:\n  tokens: 0\n  units: 0\n")
            for n in range(1, 6):
                _cr(root, n)
            cap = _load().build_plan(root, "cr", "Proposed")["capacity"]
            self.assertEqual(cap["over"], [])

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_over_budget_warns_but_never_refuses_to_plan(self) -> None:
        """The estimate is not authoritative enough to refuse to plan on. Even under --strict -
        which DOES refuse on index drift and origin drift - an over-budget batch exits 0."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _config(root, "capacity:\n  tokens: 1\n  units: 1\n")
            _drift_free_crs(root, 2)          # nothing else can refuse: the census is clean
            sp = _load()
            data = sp.build_plan(root, "cr", "Proposed")
            self.assertEqual(sorted(data["capacity"]["over"]), ["tokens", "units"])
            rc = sp.main(["plan", "--crs", "Proposed", "--root", str(root),
                          "--no-fetch", "--strict"])
            self.assertEqual(rc, 0)

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_the_over_budget_verdict_reaches_the_operator_output(self) -> None:
        import io
        import contextlib
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _config(root, "capacity:\n  units: 1\n")
            _cr(root, 1)
            _cr(root, 2)
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                _load().main(["plan", "--crs", "Proposed", "--root", str(root), "--no-fetch"])
            printed = out.getvalue() + err.getvalue()
            self.assertIn("OVER BUDGET", printed)
            self.assertIn("units 2/1", printed)          # the numbers, not just a label
            self.assertIn("WARNING, not a gate", printed)


class CapacityHonestyTests(unittest.TestCase):
    """The report must state its own uncertainty. The forecast is mis-calibrated out-of-sample
    by ~30%, so a bare point estimate would read as a fact it is not."""

    def test_the_forecast_is_quoted_as_a_range_around_the_point_estimate(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1)
            fc = _load().build_plan(root, "cr", "Proposed")["capacity"]["forecast"]
            self.assertLess(fc["low"], fc["tokens"])
            self.assertGreater(fc["high"], fc["tokens"])

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_a_batch_under_budget_but_over_it_at_the_top_of_the_band_says_so(self) -> None:
        # The honest middle case: the point estimate fits, the plausible high end does not.
        # Reporting only the point estimate would hide it.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _config(root, "capacity:\n  tokens: 55000\n")
            _cr(root, 1)  # forecast 50,000; high end 65,000
            cap = _load().build_plan(root, "cr", "Proposed")["capacity"]
            self.assertEqual(cap["over"], [])
            self.assertTrue(cap["tokens_may_exceed"])

    def test_nothing_is_recalibrated_from_the_velocity_history(self) -> None:
        """The constants are pinned to the actuals they were fitted to (see
        test_token_calibration). A plan built against a repo WITH velocity history must not
        move them - the history is reported, and a human decides."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            retros = root / "sdlc-studio" / "retros"
            retros.mkdir(parents=True)
            (retros / "VELOCITY.md").write_text(
                "| Retro | Date | Units | Measured | Estimate | Actual | Ratio | Wall |\n"
                "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
                "| RETRO0001 | 2026-07-14 | 6 | 6 | 418,800 | 384,278 | 1.09x | 1,848 |\n",
                encoding="utf-8")
            _cr(root, 1)
            sp = _load()
            base, slope = sp.BASE_TOKEN_BUDGET, sp.TOKENS_PER_COGNITIVE
            cal = sp.build_plan(root, "cr", "Proposed")["capacity"]["calibration"]
            self.assertEqual((sp.BASE_TOKEN_BUDGET, sp.TOKENS_PER_COGNITIVE), (base, slope))
            self.assertEqual(cal["sprints"], 1)
            self.assertFalse(cal["enough_history"])  # one sprint is not a calibration

    def test_an_observed_under_forecast_widens_the_band_it_never_narrows_it(self) -> None:
        """A sprint that came in 0.7x (the estimator under-forecasting) must widen the upper
        end. A sprint that agreed with the model must NOT shrink the band - agreeing once is
        not evidence of precision."""
        sp = _load()

        def band(rows: str) -> tuple:
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                retros = root / "sdlc-studio" / "retros"
                retros.mkdir(parents=True)
                (retros / "VELOCITY.md").write_text(
                    "| Retro | Date | Units | Measured | Estimate | Actual | Ratio | Wall |\n"
                    "| --- | --- | --- | --- | --- | --- | --- | --- |\n" + rows, encoding="utf-8")
                cal = sp.calibration(root)
                return cal["low"], cal["high"]

        agreeing = band("| RETRO0001 | d | 6 | 6 | 400 | 400 | 1.0x | 10 |\n")
        self.assertEqual(agreeing, (round(1 - sp.FORECAST_BAND, 2),
                                    round(1 + sp.FORECAST_BAND, 2)))
        under = band("| RETRO0001 | d | 6 | 6 | 280 | 400 | 0.7x | 10 |\n")
        self.assertGreater(under[1], agreeing[1])  # 1/0.7 = 1.43 - the band widened


class CapacityFeedsTheAppetiteTests(unittest.TestCase):
    """One configured source, two consumers: the plan-time check and the run-time breaker."""

    def test_the_appetite_defaults_to_the_configured_capacity(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            sp = _load()
            app = sp.resolve_appetite(Path(d))
            self.assertEqual(app["minutes"], float(sp.DEFAULT_CAPACITY["minutes"]))
            self.assertEqual(app["units"], sp.DEFAULT_CAPACITY["units"])

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_capacity_units_become_the_run_breakers_ceiling(self) -> None:
        """The whole point of the CR: the number the plan flags the batch against is the number
        the run breaker later stops on. Plan a 2-unit batch under a capacity of 1 unit; the plan
        says over-budget, and `loop_guard budget` - reading the run state the plan opened -
        halts the run at exactly that unit."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _config(root, "capacity:\n  units: 1\n")
            _cr(root, 1)
            _cr(root, 2)
            sp = _load()
            data = sp.build_plan(root, "cr", "Proposed")
            self.assertIn("units", data["capacity"]["over"])          # flagged at PLAN time
            rc = sp.main(["plan", "--crs", "Proposed", "--root", str(root),
                          "--no-fetch", "--write"])
            self.assertEqual(rc, 0)

            guard = _load_loop_guard()
            # the breaker resolves the SAME ceiling, from the run state the plan stamped
            args = argparse.Namespace(appetite_minutes=None, appetite_units=None)
            minutes, units = guard._resolve_appetite(root, args)
            self.assertEqual(units, 1)
            self.assertEqual(minutes, float(sp.DEFAULT_CAPACITY["minutes"]))

            # ...and it FIRES there: one unit terminal is the whole appetite.
            (root / "sdlc-studio" / "change-requests" / "CR0001-x.md").write_text(
                "# CR-0001: c\n\n> **Status:** Complete\n> **Priority:** Medium\n",
                encoding="utf-8")
            rc = guard.main(["budget", "--root", str(root)])
            self.assertEqual(rc, guard.BUDGET_EXIT)

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_an_explicit_appetite_flag_overrides_capacity_on_both_consumers(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _config(root, "capacity:\n  units: 8\n")
            for n in (1, 2, 3):
                _cr(root, n)
            sp = _load()
            # the plan sizes the batch against the ceiling the RUN will use, not the config one
            cap = sp.build_plan(root, "cr", "Proposed", appetite_units=2)["capacity"]
            self.assertIn("units", cap["over"])
            self.assertEqual(cap["appetite"]["units"], 2)
            self.assertEqual(cap["budget"]["units"], 2)

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_an_explicitly_configured_appetite_still_wins_over_capacity(self) -> None:
        # Back-compat: a project that pinned appetite.* before capacity existed keeps its pin.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _config(root, "capacity:\n  units: 8\n  minutes: 240\nappetite:\n  units: 3\n")
            app = _load().resolve_appetite(root)
            self.assertEqual(app["units"], 3)
            self.assertEqual(app["units_source"], "config appetite.units")
            self.assertEqual(app["minutes"], 240.0)          # unpinned axis inherits capacity
            self.assertEqual(app["minutes_source"], "config capacity.minutes")


if __name__ == "__main__":
    unittest.main()
