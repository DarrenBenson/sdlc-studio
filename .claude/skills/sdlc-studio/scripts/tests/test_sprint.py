"""Unit tests for sprint.py (RED first - the script does not exist yet)."""
from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
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


# The default fixtures are GROOMED - they declare the files they touch and their Points - because
# `sprint plan` refuses a batch that is not, and a fixture that could not be planned would be
# testing the gate rather than the behaviour under test. Each declares its OWN file (no
# shared-file cluster) and 2 points, so a default unit's forecast is 2 x the rate.
# `groomed=False` is the deliberate ungroomed shape the gate's own tests need.
FIXTURE_POINTS = 2


def _affect(root, rel):
    """Create the file an Affects line names, so a groomed fixture's path RESOLVES (BG0144:
    grooming refuses a unit whose declared paths all fail to resolve)."""
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("", encoding="utf-8")


def _bug(root, num, status="Open", severity="Medium", groomed=True, points=FIXTURE_POINTS):
    d = root / "sdlc-studio" / "bugs"
    d.mkdir(parents=True, exist_ok=True)
    meta = ""
    if groomed:
        _affect(root, f"src/bg{num:04d}.py")
        meta = f"> **Affects:** src/bg{num:04d}.py\n> **Points:** {points}\n"
    (d / f"BG{num:04d}-x.md").write_text(
        f"# BG{num:04d}: b\n\n> **Status:** {status}\n> **Severity:** {severity}\n{meta}",
        encoding="utf-8")


def _cr(root, num, status="Proposed", priority="Medium", groomed=True, points=FIXTURE_POINTS):
    d = root / "sdlc-studio" / "change-requests"
    d.mkdir(parents=True, exist_ok=True)
    meta = ""
    if groomed:
        _affect(root, f"src/cr{num:04d}.py")
        meta = f"> **Affects:** src/cr{num:04d}.py\n> **Points:** {points}\n"
    (d / f"CR{num:04d}-x.md").write_text(
        f"# CR-{num:04d}: c\n\n> **Status:** {status}\n> **Priority:** {priority}\n{meta}",
        encoding="utf-8")


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
        # groomed (own file, declared points): the missing-`Depends on` hint is the subject
        # here, and the breakdown gate would otherwise refuse the batch before it is reached.
        _affect(root, f"src/us{num:04d}.py")  # BG0144: the Affects path must resolve on disk
        (d / f"US{num:04d}-x.md").write_text(
            f"# US{num:04d}: s\n\n> **Status:** {status}\n{dep}"
            f"> **Affects:** src/us{num:04d}.py\n> **Points:** 3\n", encoding="utf-8")

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
            _bug(root, 1, severity="High")
            mod = _load()
            rc = mod.main(["plan", "--bugs", "Open", "--root", str(root), "--format", "json"])
            self.assertEqual(rc, 0)
            data = mod.build_plan(root, "bug", "Open", "priority")
            self.assertIn("batch", data)
            self.assertEqual(data["count"], 1)


class WsjfTests(unittest.TestCase):
    """--order wsjf ranks Cost of Delay (from Priority) against Points. No seat scores needed.

    It used to rank priority against the cognitive complexity of the files a unit's `Affects`
    named - a signal that scores r = +0.03 against measured cost (BG0147). These tests replace
    the ones that pinned that ordering, and assert the size that decides the order is the size
    somebody actually estimated.
    """

    def _cr_pts(self, root, num, priority, points, affects=None, depends=None):
        d = root / "sdlc-studio" / "change-requests"
        d.mkdir(parents=True, exist_ok=True)
        aff = affects if affects is not None else f"src/cr{num:04d}.py"
        body = (f"# CR-{num:04d}: c\n\n> **Status:** Proposed\n> **Priority:** {priority}\n"
                f"> **Affects:** {aff}\n> **Points:** {points}\n")
        if depends:
            body += f"> **Depends on:** {depends}\n"
        (d / f"CR{num:04d}-x.md").write_text(body, encoding="utf-8")

    def test_wsjf_prefers_the_smaller_job_at_equal_priority(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr_pts(root, 1, "High", 8)
            self._cr_pts(root, 2, "High", 2)
            batch = _load().select_batch(root, "cr", "Proposed", order="wsjf")
            byid = {b["id"]: b for b in batch}
            self.assertEqual([b["id"] for b in batch], ["CR0002", "CR0001"])  # smaller job first
            self.assertGreater(byid["CR0002"]["wsjf"], byid["CR0001"]["wsjf"])
            self.assertNotIn("token_budget", byid["CR0001"])   # no per-unit budget field

    def test_the_file_a_unit_touches_does_not_decide_the_order(self) -> None:
        """The blast radius of the FILE is not the size of the JOB - the mistake BG0147 names.
        Two 3-point units, one in a deeply nested module: neither outranks the other."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "simple.py").write_text("def s(a):\n    return a\n", encoding="utf-8")
            (root / "complex.py").write_text(
                "def deep(a, b, c, d):\n    if a:\n        if b:\n            if c:\n"
                "                if d:\n                    return 1\n", encoding="utf-8")
            self._cr_pts(root, 1, "High", 3, affects="complex.py")
            self._cr_pts(root, 2, "High", 3, affects="simple.py")
            batch = _load().select_batch(root, "cr", "Proposed", order="wsjf")
            self.assertEqual(batch[0]["wsjf"], batch[1]["wsjf"])              # identical WSJF
            self.assertEqual([b["id"] for b in batch], ["CR0001", "CR0002"])  # falls to id

    def test_wsjf_still_ranks_when_no_affects_path_resolves(self) -> None:
        """New-file work (the biggest jobs) used to score complexity 0 and rank as the cheapest
        possible unit. Its size is now what its author said it was."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr_pts(root, 1, "High", 8, affects="does/not/exist.py")
            self._cr_pts(root, 2, "High", 2, affects="also/missing.py")
            batch = _load().select_batch(root, "cr", "Proposed", order="wsjf")
            self.assertEqual([b["id"] for b in batch], ["CR0002", "CR0001"])
            self.assertEqual(batch[1]["points"], 8)   # the new-file unit is BIG, not free

    def test_priority_still_decides_between_units_of_equal_size(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr_pts(root, 1, "Medium", 3)
            self._cr_pts(root, 2, "Critical", 3)
            ids = [b["id"] for b in _load().select_batch(root, "cr", "Proposed", order="wsjf")]
            self.assertEqual(ids, ["CR0002", "CR0001"])

    def test_deps_win_over_the_wsjf_order(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr_pts(root, 1, "High", 8)                       # big job
            self._cr_pts(root, 2, "High", 1, depends="CR0001")     # tiny job, needs CR0001
            ids = [b["id"] for b in _load().select_batch(root, "cr", "Proposed", order="wsjf")]
            self.assertLess(ids.index("CR0001"), ids.index("CR0002"))  # dep before dependent

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
            _bug(root, 1, status="Open")
            rc = _load().main(["plan", "--bugs", "Open", "--write", "--root", str(root)])
            self.assertEqual(rc, 0)
            self.assertTrue((root / "sdlc-studio" / ".local" / "sprint-plan.json").exists())


class SeatWsjfTests(unittest.TestCase):
    """CR0099: seat-scored WSJF ordering, with graceful fallback."""

    def test_wsjf_score_math(self) -> None:
        # Cost of Delay / Points
        self.assertEqual(_load().wsjf_score(13, 4), round(13 / 4, 3))
        self.assertEqual(_load().wsjf_score(5, 0), 5.0)   # points floored to 1, never /0

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

    def test_wsjf_runs_without_any_seat_inputs(self) -> None:
        # The whole point of the rewrite: WSJF runs on the priority-derived CoD, so a groomed
        # backlog with no seat consult still gets a real WSJF - not a fall to bare priority.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1, priority="Low")
            _cr(root, 2, priority="High")
            batch = _load().select_batch(root, "cr", "Proposed", order="wsjf")   # no inputs
            self.assertEqual([b["id"] for b in batch][0], "CR0002")  # higher CoD, equal points
            self.assertIn("wsjf", batch[0])
            self.assertEqual(batch[0]["cod_source"], "priority")

    def test_skip_personas_still_ranks_by_the_derived_cost_of_delay(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1, priority="Low")
            _cr(root, 2, priority="High")
            self._inputs(root, {"CR0001": {"value": 20}})
            batch = _load().select_batch(root, "cr", "Proposed", order="wsjf", skip_personas=True)
            self.assertEqual([b["id"] for b in batch][0], "CR0002")  # seat input ignored
            self.assertEqual(batch[0]["cod_source"], "priority")


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
            _bug(root, 1, status="Open")   # a bug file but no _index.md -> missing-index drift
            rc = _load().main(["plan", "--bugs", "Open", "--strict", "--root", str(root)])
            self.assertEqual(rc, 2)            # refused

    def test_warns_but_proceeds_without_strict(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1, status="Open")
            rc = _load().main(["plan", "--bugs", "Open", "--root", str(root)])
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
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True, exist_ok=True)
            _affect(root, "src/us0002.py")  # BG0144: the Affects path must resolve on disk
            (sd / "US0002-x.md").write_text(
                "# US0002: s\n\n> **Status:** Draft\n"
                "> **Affects:** src/us0002.py\n> **Points:** 2\n", encoding="utf-8")
            rc = _load().main(["plan", "--bugs", "Open", "--stories", "Draft",
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

    def _seed_bug(self, work):
        bgd = work / "sdlc-studio" / "bugs"
        bgd.mkdir(parents=True, exist_ok=True)
        _affect(work, "src/bg0002.py")  # BG0144: the Affects path must resolve on disk
        (bgd / "BG0002-local.md").write_text(
            "# BG0002: local\n\n> **Status:** Open\n> **Severity:** Medium\n"
            "> **Affects:** src/bg0002.py\n> **Points:** 2\n",   # groomed: the gate is not the subject here
            encoding="utf-8")
        (bgd / "_index.md").write_text(
            "# Bugs\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Open | 1 |\n"
            "| **Total** | **1** |\n\n## All\n\n| ID | Title | Status | Severity | Created | Updated |\n"
            "| --- | --- | --- | --- | --- | --- |\n"
            "| [BG0002](BG0002-local.md) | local | Open | Medium | 2026-07-10 | 2026-07-10 |\n",
            encoding="utf-8")

    def test_manual_order_strict_refuses_when_behind(self):
        import io
        from contextlib import redirect_stderr, redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            work = _behind_repo(d)
            self._seed_bug(work)
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                rc = sprint.main(["plan", "--bugs", "Open", "--order", "manual",
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
                rc = sprint.main(["plan", "--bugs", "Open", "--order", "priority",
                                  "--strict", "--root", str(work)])
            self.assertEqual(rc, 2, err.getvalue() + out.getvalue())


class PlanLessonsDigestTests(unittest.TestCase):
    """CR0236 AC2: the plan an agent reads at sprint start CONTAINS the still-valid lessons -
    it does not point at a file the agent may not open."""

    LOG = ("# Project Lessons\n\n## L-0002: Read every creation path\n\n"
           "- **Rule:** grep for every code path that does the thing\n\n"
           "## L-0001: Closed one\n\n- **Status:** Closed - obsolete\n")

    def _seed(self, root: Path) -> None:
        _bug(root, 1, status="Open")
        p = root / "sdlc-studio" / ".local" / "lessons.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(self.LOG, encoding="utf-8")

    def test_build_plan_carries_the_open_lessons(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._seed(root)
            plan = _load().build_plan(root, "bug", "Open")
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
                rc = _load().main(["plan", "--bugs", "Open", "--root", str(root),
                                   "--no-fetch"])
            self.assertEqual(rc, 0)
            text = out.getvalue()
            self.assertIn("L-0002", text)
            self.assertIn("Read every creation path", text)
            self.assertNotIn("L-0001", text)  # closed lessons are not in force


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


def _drift_free_bugs(root: Path, n: int) -> None:
    """n Open bugs plus the matching index, so `--strict` has nothing else to refuse on."""
    bgd = root / "sdlc-studio" / "bugs"
    bgd.mkdir(parents=True, exist_ok=True)
    rows = []
    for i in range(1, n + 1):
        _bug(root, i)
        rows.append(f"| [BG{i:04d}](BG{i:04d}-x.md) | b | Open | Medium "
                    f"| 2026-07-14 | 2026-07-14 |")
    (bgd / "_index.md").write_text(
        f"# Bugs\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Open | {n} |\n"
        f"| **Total** | **{n}** |\n\n## All\n\n"
        "| ID | Title | Status | Severity | Created | Updated |\n"
        "| --- | --- | --- | --- | --- | --- |\n" + "\n".join(rows) + "\n",
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
            _drift_free_bugs(root, 2)          # nothing else can refuse: the census is clean
            sp = _load()
            data = sp.build_plan(root, "bug", "Open")
            self.assertEqual(sorted(data["capacity"]["over"]), ["tokens", "units"])
            rc = sp.main(["plan", "--bugs", "Open", "--root", str(root),
                          "--no-fetch", "--strict"])
            self.assertEqual(rc, 0)

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_the_over_budget_verdict_reaches_the_operator_output(self) -> None:
        import io
        import contextlib
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _config(root, "capacity:\n  units: 1\n")
            _bug(root, 1)
            _bug(root, 2)
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                _load().main(["plan", "--bugs", "Open", "--root", str(root), "--no-fetch"])
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
        # Reporting only the point estimate would hide it. Derived from the constants rather
        # than hard-coded, so a recalibration cannot quietly turn this case into a different one.
        sp = _load()
        rate = sp.POINTS_RATE_SEED
        budget = int(rate * (1 + sp.FORECAST_BAND / 2))  # above the point, below the high end
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _config(root, f"capacity:\n  tokens: {budget}\n")
            _cr(root, 1, points=1)  # one 1-point unit: forecast = the rate; high end = rate x (1 + band)
            cap = sp.build_plan(root, "cr", "Proposed")["capacity"]
            self.assertEqual(cap["over"], [])
            self.assertTrue(cap["tokens_may_exceed"])

    # A velocity row as `retro.py accuracy --write` now writes it: the estimate AS FORECAST at
    # plan time, and the constants that produced it. `{cur}` is the estimator in force, which is
    # what makes the row out-of-sample evidence rather than a row about some other model.
    VELOCITY_HEAD = (
        "| Retro | Date | Units | Measured | Forecast | Estimate (tokens, plan-time) | "
        "Actual (tokens) | Ratio (est/actual) | Wall (s) | Constants | Sample |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n")

    def _velocity(self, root: Path, rows: str) -> None:
        sp = _load()
        # the estimator IN FORCE, spelled as the velocity Constants cell records it. With no
        # evidence of its own the project's rate is the seed, so an out-of-sample row must carry
        # exactly that - a row with any other rate is judging a DIFFERENT estimator.
        cur = f"TOKENS_PER_POINT={sp.forecast_constants(root)['TOKENS_PER_POINT']}"
        retros = root / "sdlc-studio" / "retros"
        retros.mkdir(parents=True, exist_ok=True)
        (retros / "VELOCITY.md").write_text(
            self.VELOCITY_HEAD + rows.format(cur=cur), encoding="utf-8")

    def test_nothing_is_recalibrated_from_the_velocity_history(self) -> None:
        """The rate is measured from the forecast/actual evidence, not re-fitted from the
        velocity narrative. A plan built against a repo WITH velocity history reports it, and a
        human decides - the plan does not move its own rate off one narrative row."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._velocity(root, "| RETRO0001 | 2026-07-14 | 6 | 6 | 6 | 418,800 | 384,278 | "
                                 "1.09x | 1,848 | {cur} | out-of-sample |\n")
            _cr(root, 1)
            sp = _load()
            before = sp.tokens_per_point(root)["rate"]
            cal = sp.build_plan(root, "cr", "Proposed")["capacity"]["calibration"]
            self.assertEqual(sp.tokens_per_point(root)["rate"], before)  # the narrative moved nothing
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
                self._velocity(root, rows)
                cal = sp.calibration(root)
                return cal["low"], cal["high"]

        agreeing = band("| RETRO0001 | d | 6 | 6 | 6 | 400 | 400 | 1.0x | 10 | {cur} | "
                        "out-of-sample |\n")
        self.assertEqual(agreeing, (round(1 - sp.FORECAST_BAND, 2),
                                    round(1 + sp.FORECAST_BAND, 2)))
        # a miss WORSE than the declared floor - derived from the constant, so the case stays a
        # widening case whatever the band is set to, instead of quietly becoming a no-op
        miss = round(1.0 / (1.0 + sp.FORECAST_BAND) * 0.8, 2)
        under = band(f"| RETRO0001 | d | 6 | 6 | 6 | {int(400 * miss)} | 400 | {miss}x | 10 | "
                     "{cur} | out-of-sample |\n")
        self.assertGreater(under[1], agreeing[1])  # 1/miss is outside the floor - it widened

    def test_a_sprint_the_constants_were_fitted_to_does_not_widen_the_band_either(self) -> None:
        """Training error must not reach the operator's error bar any more than it reaches the
        reported ratio. A model's fit against its own training data is not a measurement of
        anything, in either direction."""
        sp = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            fitted = sp.CALIBRATION_FIT_RETROS[0]
            self._velocity(root, "| " + fitted + " | d | 6 | 6 | 6 | 280 | 400 | 0.7x | 10 | "
                                 "{cur} | in-sample |\n")
            cal = sp.calibration(root)
            self.assertEqual((cal["low"], cal["high"]),
                             (round(1 - sp.FORECAST_BAND, 2), round(1 + sp.FORECAST_BAND, 2)))
            self.assertEqual(cal["sprints"], 0)
            self.assertEqual(cal["in_sample"], 1)


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
            _bug(root, 1)
            _bug(root, 2)
            sp = _load()
            data = sp.build_plan(root, "bug", "Open")
            self.assertIn("units", data["capacity"]["over"])          # flagged at PLAN time
            rc = sp.main(["plan", "--bugs", "Open", "--root", str(root),
                          "--no-fetch", "--write"])
            self.assertEqual(rc, 0)

            guard = _load_loop_guard()
            # the breaker resolves the SAME ceiling, from the run state the plan stamped
            args = argparse.Namespace(appetite_minutes=None, appetite_units=None)
            minutes, units = guard._resolve_appetite(root, args)
            self.assertEqual(units, 1)
            self.assertEqual(minutes, float(sp.DEFAULT_CAPACITY["minutes"]))

            # ...and it FIRES there: one unit terminal is the whole appetite.
            (root / "sdlc-studio" / "bugs" / "BG0001-x.md").write_text(
                "# BG0001: b\n\n> **Status:** Fixed\n> **Severity:** Medium\n",
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


def _groomed_cr(root: Path, num: int, affects: str, points: int = 3,
                status: str = "Proposed", priority: str = "Medium") -> None:
    """A CR a planner can actually plan: it names the files it touches and its Points."""
    d = root / "sdlc-studio" / "change-requests"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"CR{num:04d}-x.md").write_text(
        f"# CR-{num:04d}: c\n\n> **Status:** {status}\n> **Priority:** {priority}\n"
        f"> **Affects:** {affects}\n> **Points:** {points}\n", encoding="utf-8")


def _groomed_bug(root: Path, num: int, affects: str, points: int = 3,
                 status: str = "Open", severity: str = "Medium") -> None:
    """A bug a planner can actually plan: it names the files it touches and its Points."""
    d = root / "sdlc-studio" / "bugs"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"BG{num:04d}-x.md").write_text(
        f"# BG{num:04d}: b\n\n> **Status:** {status}\n> **Severity:** {severity}\n"
        f"> **Affects:** {affects}\n> **Points:** {points}\n", encoding="utf-8")


def _src(root: Path, rel: str) -> str:
    """A real source file the Affects paths can resolve against."""
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("def f():\n    return 1\n", encoding="utf-8")
    return rel


class TriageInPlanTests(unittest.TestCase):
    """US0170: the judgement triage lenses (duplicate/subsumed, stale, orphaned) are surfaced IN the
    plan the operator reads - reporting-only, never a refusal. Behaviour: run the public plan path."""

    def _plan(self, root: Path):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = _load().main(["plan", "--bugs", "Open", "--root", str(root),
                               "--no-fetch", "--skip-personas"])
        return rc, out.getvalue(), err.getvalue()

    def _dupbug(self, root: Path, num: int, title: str, summary: str, affects: str) -> None:
        d = root / "sdlc-studio" / "bugs"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"BG{num:04d}-x.md").write_text(
            f"# BG{num:04d}: {title}\n\n> **Status:** Open\n> **Severity:** Medium\n"
            f"> **Affects:** {affects}\n> **Points:** 3\n\n## Summary\n\n{summary}\n",
            encoding="utf-8")

    def test_a_duplicate_pair_is_surfaced_in_the_plan_not_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _src(root, "src/a.py")
            self._dupbug(root, 1, "check_links misses an anchor link defect",
                         "check_links does not catch a broken anchor link defect", "src/a.py")
            self._dupbug(root, 2, "anchor link defect not caught by check_links",
                         "a broken anchor link defect is not caught by check_links", "src/a.py")
            rc, out, _ = self._plan(root)
            self.assertEqual(rc, 0)               # reporting, never a refusal
            self.assertIn("batch:", out)          # the plan still prints
            self.assertIn("backlog triage", out)  # and names the duplicate
            self.assertIn("duplicate", out)

    def test_a_coherent_batch_prints_no_triage_section(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _src(root, "src/a.py"); _src(root, "src/b.py")
            self._dupbug(root, 1, "colour the status output", "render green and amber", "src/a.py")
            self._dupbug(root, 2, "parser drops a field", "the last column is lost", "src/b.py")
            rc, out, _ = self._plan(root)
            self.assertEqual(rc, 0)
            self.assertNotIn("backlog triage", out)


class BreakdownGateTests(unittest.TestCase):
    """The breakdown gate: `sprint plan` REFUSES an ungroomed batch.

    Behaviour only. Every assertion here runs the public `plan` path and reads its exit code
    and its OUTPUT; none of them greps the source for a string. The load-bearing pair is
    fail-then-pass: a batch with one unit that declares no `Affects` must FAIL, and the SAME
    batch must pass once groomed. A gate that cannot fail is not a gate.
    """

    def _plan(self, root: Path, *extra: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = _load().main(["plan", "--bugs", "Open", "--root", str(root),
                               "--no-fetch", "--skip-personas", *extra])
        return rc, out.getvalue(), err.getvalue()

    def test_a_batch_with_one_ungroomed_unit_fails_plan(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _groomed_bug(root, 1, _src(root, "src/a.py"))
            _bug(root, 2, groomed=False)
            rc, out, err = self._plan(root)
            self.assertNotEqual(rc, 0)
            self.assertIn("BG0002", err)
            self.assertIn("Affects", err)
            # NO PLAN AT ALL - not the batch header, not the waves, not the forecast
            self.assertNotIn("batch:", out)
            self.assertNotIn("wave", out)
            self.assertNotIn("token forecast", out)

    def test_the_same_batch_passes_once_groomed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _groomed_bug(root, 1, _src(root, "src/a.py"))
            _groomed_bug(root, 2, _src(root, "src/b.py"))
            rc, out, _ = self._plan(root)
            self.assertEqual(rc, 0)
            self.assertIn("batch: 2 unit(s)", out)

    def test_a_unit_naming_files_but_no_size_is_still_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _groomed_bug(root, 1, _src(root, "src/a.py"))
            d2 = root / "sdlc-studio" / "bugs"
            (d2 / "BG0002-x.md").write_text(
                "# BG0002: b\n\n> **Status:** Open\n> **Severity:** Medium\n"
                "> **Affects:** src/a.py\n", encoding="utf-8")
            rc, out, err = self._plan(root)
            self.assertNotEqual(rc, 0)
            self.assertIn("BG0002", err)
            self.assertIn("size", err)
            self.assertNotIn("batch:", out)

    def test_a_refused_plan_writes_nothing_and_opens_no_run(self) -> None:
        """The refusal must not leave a half-authoritative artefact behind."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1, groomed=False)
            rc, _, _ = self._plan(root, "--write")
            self.assertNotEqual(rc, 0)
            self.assertFalse((root / "sdlc-studio" / ".local" / "sprint-plan.json").exists())
            self.assertFalse((root / "sdlc-studio" / ".local" / "run-state.json").exists())

    def test_the_refusal_names_the_unit_what_it_lacks_and_the_fix(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 7, groomed=False)
            _, _, err = self._plan(root)
            self.assertIn("BG0007", err)                 # which unit
            self.assertIn("Affects", err)                # what it lacks
            self.assertIn("Points", err)                 # ...and the other half
            self.assertIn("breakdown", err)              # the command that fixes it
            self.assertIn("sprint.breakdown: judgement", err)   # the recorded escape

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_the_recorded_opt_out_reports_and_does_not_block(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _config(root, "sprint:\n  breakdown: judgement\n")
            _bug(root, 1, groomed=False)
            rc, out, err = self._plan(root)
            self.assertEqual(rc, 0)
            self.assertIn("batch: 1 unit(s)", out)       # the plan IS printed
            self.assertIn("BG0001", err)                 # ...and the lane still reports

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_an_unknown_mode_is_not_an_escape(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _config(root, "sprint:\n  breakdown: whatever\n")
            _bug(root, 1, groomed=False)
            rc, out, _ = self._plan(root)
            self.assertNotEqual(rc, 0)
            self.assertNotIn("batch:", out)

    def test_omission_is_not_an_escape(self) -> None:
        """No config file at all must BLOCK. Only a recorded decision opts out."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1, groomed=False)
            self.assertFalse((root / "sdlc-studio" / ".config.yaml").exists())
            rc, out, _ = self._plan(root)
            self.assertNotEqual(rc, 0)
            self.assertNotIn("batch:", out)


class SharedFileClusterTests(unittest.TestCase):
    """Units touching the same file are ONE cluster, not independent parallel work."""

    def test_two_units_touching_one_file_are_clustered(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            shared = _src(root, "src/shared.py")
            _groomed_cr(root, 1, shared)
            _groomed_cr(root, 2, f"{shared}, {_src(root, 'src/other.py')}")
            _groomed_cr(root, 3, _src(root, "src/alone.py"))
            bd = _load().build_plan(root, "cr", "Proposed", skip_personas=True)["breakdown"]
            self.assertEqual([c["units"] for c in bd["clusters"]], [["CR0001", "CR0002"]])
            self.assertIn("src/shared.py", bd["clusters"][0]["files"])

    def test_the_same_file_declared_two_ways_still_clusters(self) -> None:
        """A path that resolves to one file is one file, however it was written."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _src(root, ".claude/skills/sdlc-studio/scripts/x.py")
            _groomed_cr(root, 1, "scripts/x.py")
            _groomed_cr(root, 2, ".claude/skills/sdlc-studio/scripts/x.py")
            bd = _load().build_plan(root, "cr", "Proposed", skip_personas=True)["breakdown"]
            self.assertEqual([c["units"] for c in bd["clusters"]], [["CR0001", "CR0002"]])

    def test_a_false_parallel_wave_is_called_out(self) -> None:
        """The bug this defends: two units reported as safely parallel while both edit one file."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            shared = _src(root, "src/shared.py")
            _groomed_bug(root, 1, shared)
            _groomed_bug(root, 2, shared)
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = _load().main(["plan", "--bugs", "Open", "--root", str(root),
                                   "--no-fetch", "--skip-personas"])
            self.assertEqual(rc, 0)
            self.assertIn("(parallel)", out.getvalue())   # the DAG still says parallel...
            self.assertIn("NOT safely parallel", err.getvalue())  # ...and the planner says no
            self.assertIn("BG0001", err.getvalue())
            self.assertIn("BG0002", err.getvalue())

    def test_independent_units_raise_no_cluster(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _groomed_cr(root, 1, _src(root, "src/a.py"))
            _groomed_cr(root, 2, _src(root, "src/b.py"))
            bd = _load().build_plan(root, "cr", "Proposed", skip_personas=True)["breakdown"]
            self.assertEqual(bd["clusters"], [])


def _pointed_cr(root: Path, num: int, points, affects: str = None, priority: str = "Medium",
                status: str = "Proposed") -> None:
    """A CR carrying a Points estimate (and, by default, a resolvable Affects)."""
    d = root / "sdlc-studio" / "change-requests"
    d.mkdir(parents=True, exist_ok=True)
    aff = affects if affects is not None else _src(root, f"src/cr{num:04d}.py")
    pts = f"> **Points:** {points}\n" if points is not None else ""
    (d / f"CR{num:04d}-x.md").write_text(
        f"# CR-{num:04d}: c\n\n> **Status:** {status}\n> **Priority:** {priority}\n"
        f"> **Affects:** {aff}\n{pts}", encoding="utf-8")


def _pointed_bug(root: Path, num: int, points, affects: str = None, severity: str = "Medium",
                 status: str = "Open") -> None:
    """A bug carrying a Points estimate (and, by default, a resolvable Affects)."""
    d = root / "sdlc-studio" / "bugs"
    d.mkdir(parents=True, exist_ok=True)
    aff = affects if affects is not None else _src(root, f"src/bg{num:04d}.py")
    pts = f"> **Points:** {points}\n" if points is not None else ""
    (d / f"BG{num:04d}-x.md").write_text(
        f"# BG{num:04d}: b\n\n> **Status:** {status}\n> **Severity:** {severity}\n"
        f"> **Affects:** {aff}\n{pts}", encoding="utf-8")


class SplitGateTests(unittest.TestCase):
    """THE GATE REFUSES ABOVE 8 POINTS - the rule that makes the cost model work.

    A point was a stable unit of cost from 2 to 8 (22k-27k tokens per point) and then BROKE: the
    13s came in at 14,144 per point, systematically over-estimated, and all three blind estimators
    returned them with low confidence and the words "should be split". Above the threshold the
    estimate is not worth having, and the answer is DECOMPOSITION, not a harder estimate.

    Behaviour only: every assertion drives the public `plan` path and reads its exit code and its
    output. The load-bearing pair is fail-then-pass - a 13 REFUSES, the same batch at 8 PLANS.
    """

    def _plan(self, root: Path, *extra: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = _load().main(["plan", "--bugs", "Open", "--root", str(root),
                               "--no-fetch", "--skip-personas", *extra])
        return rc, out.getvalue(), err.getvalue()

    def test_a_thirteen_point_unit_is_refused_and_the_same_batch_at_eight_plans(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _pointed_bug(root, 1, 3)
            _pointed_bug(root, 2, 13)          # over the ceiling
            rc, out, err = self._plan(root)
            self.assertNotEqual(rc, 0)
            self.assertIn("BG0002", err)                    # named
            self.assertIn("13", err)                        # with its estimate
            self.assertIn("split", err.lower())             # and told what to do
            self.assertNotIn("batch:", out)                 # NO PLAN AT ALL
            self.assertNotIn("token forecast", out)
            self.assertNotIn("BG0001", out)
            # the ONLY change: that unit is re-sized to 8. The same batch now plans.
            _pointed_bug(root, 2, 8)
            rc, out, _ = self._plan(root)
            self.assertEqual(rc, 0)
            self.assertIn("batch: 2 unit(s)", out)

    def test_a_twenty_is_refused_too_and_an_eight_is_not(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _pointed_bug(root, 1, 20)
            self.assertNotEqual(self._plan(root)[0], 0)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _pointed_bug(root, 1, 8)          # right on the line - the data says 8s are stable
            self.assertEqual(self._plan(root)[0], 0)

    def test_a_refused_batch_writes_no_plan_and_opens_no_run(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _pointed_bug(root, 1, 13)
            rc, _, _ = self._plan(root, "--write")
            self.assertNotEqual(rc, 0)
            self.assertFalse((root / "sdlc-studio" / ".local" / "sprint-plan.json").exists())
            self.assertFalse((root / "sdlc-studio" / ".local" / "run-state.json").exists())

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_the_ceiling_is_configurable_a_project_can_tighten_it_to_five(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _config(root, "sprint:\n  points_split_above: 5\n")
            _pointed_bug(root, 1, 8)          # legal by default, too chunky for THIS project
            rc, out, err = self._plan(root)
            self.assertNotEqual(rc, 0)
            self.assertIn("BG0001", err)
            self.assertIn("5", err)
            self.assertNotIn("batch:", out)
            _pointed_bug(root, 1, 5)
            self.assertEqual(self._plan(root)[0], 0)

    def test_a_unit_with_no_points_is_still_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _pointed_bug(root, 1, None)       # Affects, but nobody sized it
            rc, out, err = self._plan(root)
            self.assertNotEqual(rc, 0)
            self.assertIn("BG0001", err)
            self.assertIn("Points", err)
            self.assertNotIn("batch:", out)

    def test_a_unit_with_no_affects_is_still_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _pointed_bug(root, 1, 3, affects="")
            rc, out, err = self._plan(root)
            self.assertNotEqual(rc, 0)
            self.assertIn("BG0001", err)
            self.assertIn("Affects", err)
            self.assertNotIn("batch:", out)


class PointsForecastTests(unittest.TestCase):
    """FORECAST = sum(points) x a tokens-per-point rate MEASURED from the evidence.

    Not fitted, and with NO base term: a least-squares fit adds one (8,043) and does WORSE than
    the flat rate. These tests ATTACK the model - a forecast that does not scale linearly with
    points, or that quietly ignores the project's own measured rate, has not changed axis.
    """

    def _evidence(self, root: Path, rows: list[tuple[str, int, int]]) -> None:
        """(id, points forecast at plan time, tokens actually spent) -> the two evidence logs."""
        ev = root / "sdlc-studio" / "retros" / "evidence"
        ev.mkdir(parents=True, exist_ok=True)
        (ev / "forecasts-2026-01-01.jsonl").write_text(
            "".join(json.dumps({"id": i, "points": p, "tokens": p * 1}) + "\n"
                    for i, p, _ in rows), encoding="utf-8")
        (ev / "actuals-2026-01-01.jsonl").write_text(
            "".join(json.dumps({"id": i, "type": "cr", "tokens": t}) + "\n"
                    for i, _, t in rows), encoding="utf-8")

    def test_the_batch_forecast_is_the_points_times_the_measured_rate(self) -> None:
        """THE LOAD-BEARING FORECAST TEST. The rate comes from the project's own evidence -
        tokens actually spent, divided by the points that were forecast for them."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            # 5 delivered units: 20 points cost 400,000 tokens -> a measured 20,000 per point
            self._evidence(root, [("BG0001", 2, 40_000), ("BG0002", 3, 60_000),
                                  ("BG0003", 5, 100_000), ("BG0004", 8, 160_000),
                                  ("BG0005", 2, 40_000)])
            rate = sp.tokens_per_point(root)
            self.assertEqual(rate["rate"], 20_000)
            self.assertEqual(rate["source"], "measured")
            _pointed_cr(root, 1, 3)
            _pointed_cr(root, 2, 5)
            fc = sp.build_plan(root, "cr", "Proposed", order="wsjf")["token_forecast"]
            self.assertEqual(fc["points"], 8)
            self.assertEqual(fc["rate"], 20_000)
            self.assertEqual(fc["tokens"], 8 * 20_000)          # sum(points) x measured rate
            self.assertEqual(fc["per_unit"]["CR0001"], 3 * 20_000)
            self.assertEqual(fc["per_unit"]["CR0002"], 5 * 20_000)

    def test_there_is_no_base_term(self) -> None:
        """A fitted base term does WORSE than the flat rate. The forecast is strictly linear in
        points: a unit of 8 costs exactly 4x a unit of 2, with nothing added per unit."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            _pointed_cr(root, 1, 2)
            _pointed_cr(root, 2, 8)
            fc = sp.build_plan(root, "cr", "Proposed", order="wsjf")["token_forecast"]
            self.assertEqual(fc["per_unit"]["CR0002"], 4 * fc["per_unit"]["CR0001"])
            self.assertEqual(fc["tokens"], 10 * fc["rate"])

    def test_without_evidence_the_rate_is_the_seed_and_says_so(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            rate = sp.tokens_per_point(root)
            self.assertEqual(rate["source"], "seed")
            self.assertEqual(rate["rate"], sp.POINTS_RATE_SEED)
            self.assertIn("blind re-estimation", rate["basis"])

    def test_a_handful_of_units_is_not_a_measurement(self) -> None:
        """A rate re-fitted to one or two units is fitting noise - this project has been burned
        there before. Below the minimum the seed stands, and the plan says how far off it is."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            self._evidence(root, [("BG0001", 2, 400_000)])   # one wild unit
            rate = sp.tokens_per_point(root)
            self.assertEqual(rate["source"], "seed")
            self.assertEqual(rate["units"], 1)               # it is COUNTED, not hidden

    def test_the_order_mode_cannot_change_the_forecast(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            _pointed_cr(root, 1, 5)
            pri = sp.build_plan(root, "cr", "Proposed", order="priority")["token_forecast"]
            wsjf = sp.build_plan(root, "cr", "Proposed", order="wsjf")["token_forecast"]
            self.assertEqual(pri["tokens"], wsjf["tokens"])
            self.assertEqual(pri["tokens"], 5 * pri["rate"])

    def test_the_plan_states_the_rate_and_where_it_came_from(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _pointed_bug(root, 1, 3)
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = _load().main(["plan", "--bugs", "Open", "--root", str(root),
                                   "--no-fetch", "--skip-personas"])
            self.assertEqual(rc, 0)
            text = out.getvalue()
            self.assertIn("3 point(s)", text)
            self.assertIn("per point", text)
            self.assertIn("blind re-estimation", text)  # the evidence the rate came from

    def test_the_recorded_forecast_carries_the_points_it_was_made_from(self) -> None:
        """The closed loop: the plan records the points it forecast on, so the NEXT plan can
        measure the rate from them against the actuals that come back."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            _pointed_bug(root, 1, 5)
            with contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()):
                sp.main(["plan", "--bugs", "Open", "--root", str(root), "--no-fetch",
                         "--skip-personas"])
            sys.path.insert(0, str(SCRIPT.parent))
            import telemetry
            rec = telemetry.forecasts(root)["BG0001"]
            self.assertEqual(rec["points"], 5)
            self.assertEqual(rec["tokens"], 5 * sp.POINTS_RATE_SEED)


class WsjfIsCostOfDelayOverPointsTests(unittest.TestCase):
    """WSJF = Cost of Delay / Points, and it runs WITHOUT seat scores.

    The old WSJF needed `.local/wsjf-inputs.json`, so it almost never ran - which is why a dead
    complexity signal (r = +0.03 against cost) was doing the ordering instead (BG0147).
    """

    def test_it_runs_with_no_seat_inputs_at_all(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            _pointed_cr(root, 1, 8, priority="High")
            _pointed_cr(root, 2, 2, priority="High")     # same value, 4x cheaper
            batch = sp.select_batch(root, "cr", "Proposed", order="wsjf", skip_personas=True)
            self.assertEqual([b["id"] for b in batch], ["CR0002", "CR0001"])
            by_id = {b["id"]: b for b in batch}
            self.assertEqual(by_id["CR0002"]["wsjf"], sp.wsjf_score(sp.cost_of_delay("High"), 2))
            self.assertEqual(by_id["CR0001"]["cod_source"], "priority")

    def test_cost_of_delay_falls_out_of_priority_on_the_fibonacci_scale(self) -> None:
        sp = _load()
        self.assertGreater(sp.cost_of_delay("Critical"), sp.cost_of_delay("High"))
        self.assertGreater(sp.cost_of_delay("High"), sp.cost_of_delay("Medium"))
        self.assertGreater(sp.cost_of_delay("Medium"), sp.cost_of_delay("Low"))
        self.assertEqual(sp.cost_of_delay("P1"), sp.cost_of_delay("Critical"))
        # every rung is on the same modified Fibonacci scale the points use
        for band in ("Critical", "High", "Medium", "Low"):
            self.assertIn(sp.cost_of_delay(band), sp.sdlc_md.POINTS_SCALE)
        # an absent or unreadable priority ranks Medium - it never crashes the planner
        self.assertEqual(sp.cost_of_delay(""), sp.cost_of_delay("Medium"))
        self.assertEqual(sp.cost_of_delay("nonsense"), sp.cost_of_delay("Medium"))

    def test_a_cheaper_job_of_equal_value_goes_first(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _pointed_cr(root, 1, 8, priority="Medium")
            _pointed_cr(root, 2, 3, priority="Medium")
            batch = _load().select_batch(root, "cr", "Proposed", order="wsjf",
                                         skip_personas=True)
            self.assertEqual([b["id"] for b in batch], ["CR0002", "CR0001"])

    def test_the_dead_complexity_signal_no_longer_orders_the_batch(self) -> None:
        """BG0147. Two identical units - same priority, same points - one touching a deeply
        nested file and one touching a trivial one. The blast-radius complexity of the FILE
        (r = +0.03 against measured cost) must not decide which runs first."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            (root / "complex.py").write_text(
                "def deep(a, b, c, d):\n    if a:\n        if b:\n            if c:\n"
                "                if d:\n                    return 1\n", encoding="utf-8")
            (root / "simple.py").write_text("def s(a):\n    return a\n", encoding="utf-8")
            _pointed_cr(root, 1, 3, affects="complex.py", priority="High")
            _pointed_cr(root, 2, 3, affects="simple.py", priority="High")
            batch = sp.select_batch(root, "cr", "Proposed", order="wsjf", skip_personas=True)
            # equal WSJF: the order falls to id, which is arbitrary and HONEST. It must not be
            # decided by a number with no demonstrated meaning.
            self.assertEqual([b["id"] for b in batch], ["CR0001", "CR0002"])
            for b in batch:
                self.assertNotIn("complexity", b)

    def test_seat_scores_override_the_derived_cost_of_delay_when_they_exist(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            _pointed_cr(root, 1, 5, priority="Low")      # low priority ...
            _pointed_cr(root, 2, 5, priority="High")
            local = root / "sdlc-studio" / ".local"
            local.mkdir(parents=True, exist_ok=True)
            (local / "wsjf-inputs.json").write_text(json.dumps({
                "CR0001": {"value": 20, "time_criticality": 0, "risk_reduction": 0}}),
                encoding="utf-8")
            batch = sp.select_batch(root, "cr", "Proposed", order="wsjf")
            by_id = {b["id"]: b for b in batch}
            self.assertEqual([b["id"] for b in batch][0], "CR0001")  # ... the seats outrank it
            self.assertEqual(by_id["CR0001"]["cod_source"], "seats")
            self.assertEqual(by_id["CR0001"]["wsjf"], sp.wsjf_score(20, 5))
            self.assertEqual(by_id["CR0002"]["cod_source"], "priority")

    def test_points_divide_the_seat_score_too(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            _pointed_cr(root, 1, 8)
            local = root / "sdlc-studio" / ".local"
            local.mkdir(parents=True, exist_ok=True)
            (local / "wsjf-inputs.json").write_text(json.dumps({
                "CR0001": {"value": 9, "time_criticality": 9, "risk_reduction": 9, "size": 1}}),
                encoding="utf-8")
            batch = sp.select_batch(root, "cr", "Proposed", order="wsjf")
            # the seat `size` is NOT a second size vocabulary: points are the denominator
            self.assertEqual(batch[0]["points"], 8)
            self.assertEqual(batch[0]["wsjf"], sp.wsjf_score(27, 8))

    def test_a_declared_dependency_still_beats_the_wsjf_order(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            d2 = root / "sdlc-studio" / "change-requests"
            _pointed_cr(root, 1, 8, priority="Low")
            _pointed_cr(root, 2, 1, priority="Critical")
            (d2 / "CR0002-x.md").write_text(
                (d2 / "CR0002-x.md").read_text(encoding="utf-8") + "> **Depends on:** CR0001\n",
                encoding="utf-8")
            ids = [b["id"] for b in _load().select_batch(root, "cr", "Proposed", order="wsjf",
                                                         skip_personas=True)]
            self.assertLess(ids.index("CR0001"), ids.index("CR0002"))


class BreakdownReportTests(unittest.TestCase):
    """`sprint breakdown` - the read-only report the refusal names."""

    def test_it_reports_the_ungroomed_units_without_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _groomed_cr(root, 1, _src(root, "src/a.py"))
            _cr(root, 2, groomed=False)
            out = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                rc = _load().main(["breakdown", "--crs", "Proposed", "--root", str(root),
                                   "--format", "json"])
            self.assertEqual(rc, 0)          # a report, never a gate
            data = json.loads(out.getvalue())
            self.assertEqual([u["id"] for u in data["ungroomed"]], ["CR0002"])
            self.assertEqual(data["groomed"], ["CR0001"])
            self.assertEqual(data["mode"], "enforce")

    def test_a_large_cr_with_no_stories_is_flagged_for_decomposition(self) -> None:
        """Only stories carry executable Verify lines, so a big CR's Done is gated on prose
        until it is decomposed. A CR sized AT the split ceiling (legal, but the biggest a
        single unit may be) is doing enough work to warrant stories."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _groomed_cr(root, 1, _src(root, "src/a.py"), points=8)   # at the ceiling
            _groomed_cr(root, 2, _src(root, "src/b.py"), points=2)
            bd = _load().build_plan(root, "cr", "Proposed", skip_personas=True)["breakdown"]
            self.assertEqual([u["id"] for u in bd["decompose"]], ["CR0001"])

    def test_a_cr_a_story_already_cites_is_not_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _groomed_cr(root, 1, _src(root, "src/a.py"), points=8)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True, exist_ok=True)
            (sd / "US0001-x.md").write_text(
                "# US0001: s\n\n> **Status:** Ready\n\nActions CR0001.\n", encoding="utf-8")
            bd = _load().build_plan(root, "cr", "Proposed", skip_personas=True)["breakdown"]
            self.assertEqual(bd["decompose"], [])


if __name__ == "__main__":
    unittest.main()
