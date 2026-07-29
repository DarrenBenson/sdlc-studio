"""Unit tests for sprint.py (RED first - the script does not exist yet)."""
from __future__ import annotations

import argparse
import contextlib
import importlib.util
import inspect
import io
import json
import sys
import tempfile
import shutil
import types
import unittest
import unittest.mock
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


def _tsd_with_levels(root: Path, *paths: str) -> None:
    """A TSD whose `## Test Levels` names the given paths, so `test_strategy` runs its batch
    loop instead of early-returning. Without a Test Levels section the loop never executes -
    which is why the BG0299 crash slipped through every plan test until this one."""
    body = "# Test Strategy\n\n## Test Levels\n\n### Unit\n\n"
    body += "".join(f"Covers `{p}`.\n" for p in paths)
    body += "\n## Traceability\n\nend.\n"
    (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
    (root / "sdlc-studio" / "tsd.md").write_text(body, encoding="utf-8")


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

    def test_plan_does_not_crash_when_the_tsd_has_test_levels(self) -> None:
        # BG0299: cmd_plan builds data["batch"] as unit RECORDS (dicts), but _print_test_strategy
        # handed them straight to test_strategy, whose contract is a list of ids - crashing every
        # `sprint plan` in a project with a `## Test Levels` TSD, on both text and json output.
        # The prior plan tests all passed because a TSD-less fixture makes test_strategy early-return
        # before it iterates the batch. Seed the TSD so the batch loop actually runs.
        for fmt in ("text", "json"):
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _bug(root, 1, severity="High")
                _tsd_with_levels(root, "src/bg0001.py")
                mod = _load()
                with contextlib.redirect_stdout(io.StringIO()), \
                        contextlib.redirect_stderr(io.StringIO()):
                    rc = mod.main(["plan", "--bugs", "Open", "--root", str(root), "--format", fmt])
                self.assertEqual(rc, 0, f"sprint plan crashed with a Test Levels TSD ({fmt})")
                # And the batch loop it now reaches attributes the unit to the level naming its file.
                strat = mod.test_strategy(root, ["BG0001"])
                self.assertTrue(strat["available"])
                self.assertIn("BG0001", strat["units"])


class BatchCliTests(unittest.TestCase):
    """`sprint batch drop/add` at the CLI (CR0421 US0433) - the verb an operator reaches for
    instead of hand-editing run-state.json."""

    def _open(self, root, batch):
        mod = _load()
        mod.run_state.open_run(str(root), batch=batch, goal="g")
        return mod

    def _run(self, mod, argv):
        buf, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
            rc = mod.main(argv)
        return rc, buf.getvalue(), err.getvalue()

    def test_drop_removes_the_unit_and_records_the_reason(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = self._open(root, ["US0001", "US0002"])
            rc, out, _ = self._run(mod, ["batch", "drop", "US0002",
                                         "--reason", "not started", "--root", str(root)])
            self.assertEqual(rc, 0)
            self.assertEqual(mod.run_state.read(str(root))["batch"], ["US0001"])
            self.assertIn("dropped US0002", out)

    def test_drop_without_a_reason_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = self._open(root, ["US0001"])
            rc, _, err = self._run(mod, ["batch", "drop", "US0001", "--root", str(root)])
            self.assertEqual(rc, 2)
            self.assertIn("--reason is required", err)
            self.assertEqual(mod.run_state.read(str(root))["batch"], ["US0001"], "not dropped")

    def test_add_puts_the_unit_in_the_batch(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = self._open(root, ["US0001"])
            rc, out, _ = self._run(mod, ["batch", "add", "US0002", "--root", str(root)])
            self.assertEqual(rc, 0)
            self.assertEqual(mod.run_state.read(str(root))["batch"], ["US0001", "US0002"])
            self.assertIn("added US0002", out)


class CloseAttemptTrendTests(unittest.TestCase):
    """CR0421 US0435: once the outstanding set is GROWING across close attempts, the trend line
    names the way out - but HONESTLY. `--file-and-close` can only file deferrable (ceremony)
    blockers; it refuses a hard correctness lane. So the offer names file-and-close only for the
    deferrable items, and a set of only hard blockers is told to clear the lanes, not sent to a
    dead-end. A first or converging attempt makes no offer at all."""

    def _pre(self, stages: list[str]) -> dict:
        return {"blockers": [{"stage": s, "detail": "", "remedy": ""} for s in stages]}

    def _grow(self, mod, root, first: dict, second: dict) -> str:
        mod.run_state.open_run(root, batch=["US0001"], goal="g")
        self.assertIsNone(mod._record_close_attempt(root, first), "first attempt: no trend")
        return mod._record_close_attempt(root, second)

    def test_a_growing_deferrable_set_offers_the_bounded_exit(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = str(Path(d))
            mod = _load()
            line = self._grow(mod, root, self._pre(["retro", "sign-off"]),
                              self._pre(["retro", "sign-off", "goal-verdict"]))  # 2 -> 3, all deferrable
            self.assertIn("growing", line)
            self.assertIn("--file-and-close", line, "deferrable growth names the bounded exit")

    def test_a_growing_hard_set_is_told_to_clear_the_lanes_not_sent_to_a_dead_end(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = str(Path(d))
            mod = _load()
            line = self._grow(mod, root, self._pre(["gate", "gate"]),
                              self._pre(["gate", "gate", "gate"]))  # 2 -> 3, all hard
            self.assertIn("growing", line)
            self.assertNotIn("Bounded exit", line,
                             "an all-hard set is not offered an exit that would refuse it")
            self.assertIn("clear the lane", line)

    def test_a_mixed_growing_set_files_the_deferrable_and_names_the_hard(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = str(Path(d))
            mod = _load()
            line = self._grow(mod, root, self._pre(["gate", "retro"]),
                              self._pre(["gate", "gate", "retro"]))  # 2 -> 3, mixed
            self.assertIn("--file-and-close", line)
            self.assertIn("must be cleared first", line, "the hard remainder is named, not filed")

    def test_a_converging_or_first_attempt_makes_no_offer(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = str(Path(d))
            mod = _load()
            mod.run_state.open_run(root, batch=["US0001"], goal="g")
            self.assertIsNone(mod._record_close_attempt(root, self._pre(["gate"] * 5)),
                              "first attempt: no offer")
            shrank = mod._record_close_attempt(root, self._pre(["gate"] * 2))  # 5 -> 2
            self.assertIn("shrinking", shrank)
            self.assertNotIn("--file-and-close", shrank, "a converging close makes no offer")


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
            # stdout captured: a green suite must print nothing, or a real error
            # hides in the noise (the repo's test-noise budget enforces it).
            with contextlib.redirect_stdout(io.StringIO()):
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


class SeatCoverageTests(unittest.TestCase):
    """BG0247: an inputs file that scores NO unit in the batch is not a stale file.

    The two facts call for the same action and describe different situations, and only one
    of them was ever true here: 'your scores are old' hid 'you have no scores for this work'."""

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

    def _plan(self, root):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = _load().main(["plan", "--crs", "Proposed", "--root", str(root),
                               "--no-fetch", "--order", "wsjf"])
        return rc, out.getvalue(), err.getvalue()

    def test_out_of_batch_scores_are_not_reported_as_merely_stale(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1)
            _cr(root, 2)
            # scored: only ids that are NOT in the batch, and long past the window
            self._inputs(root, {"CR0900": {"value": 5, "time_criticality": 1,
                                           "risk_reduction": 1}}, age_days=11)
            data = _load().build_plan(root, "cr", "Proposed", order="wsjf")
            prov = data["seat_provenance"]
            self.assertEqual(prov["covered"], 0)
            self.assertEqual(prov["entries"], 1)
            self.assertTrue(prov["irrelevant"])
            self.assertFalse(prov["stale"])     # scores that apply to nothing cannot be stale
            rc, out, err = self._plan(root)
            self.assertEqual(rc, 0)
            blob = out + err
            self.assertNotIn("day(s) old", blob)         # the age advisory is suppressed
            self.assertIn("scores NO unit in this batch", blob)
            self.assertIn("0/2", blob)                   # coverage leads, not age

    def test_scores_that_apply_are_still_reported_stale(self) -> None:
        """The advisory must survive for the case it was written for."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1)
            self._inputs(root, {"CR0001": {"value": 5, "time_criticality": 1,
                                           "risk_reduction": 1}}, age_days=11)
            data = _load().build_plan(root, "cr", "Proposed", order="wsjf")
            self.assertTrue(data["seat_provenance"]["stale"])
            self.assertFalse(data["seat_provenance"]["irrelevant"])
            rc, out, err = self._plan(root)
            self.assertIn("day(s) old", out + err)

    def test_the_unscored_line_does_not_claim_the_order_fell_back_to_priority(self) -> None:
        """WSJF still RUNS with no seat inputs: the Cost of Delay falls back to Priority,
        the ordering does not. Saying otherwise is the same class of defect as the age
        advisory - a message describing a situation that is not the one on screen."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1)
            rc, out, err = self._plan(root)
            self.assertEqual(rc, 0)
            blob = out + err
            self.assertNotIn("priority fallback", blob)
            self.assertIn("Cost of Delay derived from Priority", blob)
            data = _load().build_plan(root, "cr", "Proposed", order="wsjf")
            self.assertEqual(data["batch"][0]["cod_source"], "priority")
            self.assertIn("wsjf", data["batch"][0])   # the order really is still WSJF


class ReconcileBeforePlanTests(unittest.TestCase):
    """CR0094: the planner surfaces index drift before selecting; --strict refuses."""

    def test_strict_refuses_on_drift(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1, status="Open")   # a bug file but no _index.md -> missing-index drift
            # stdout captured: a green suite must print nothing, or a real error
            # hides in the noise (the repo's test-noise budget enforces it).
            with contextlib.redirect_stdout(io.StringIO()):
                rc = _load().main(["plan", "--bugs", "Open", "--strict", "--root", str(root)])
            self.assertEqual(rc, 2)            # refused

    def test_warns_but_proceeds_without_strict(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1, status="Open")
            # stdout captured: a green suite must print nothing, or a real error
            # hides in the noise (the repo's test-noise budget enforces it).
            with contextlib.redirect_stdout(io.StringIO()):
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
            # stdout captured: a green suite must print nothing, or a real error
            # hides in the noise (the repo's test-noise budget enforces it).
            with contextlib.redirect_stdout(io.StringIO()):
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
            # stdout captured: a green suite must print nothing, or a real error
            # hides in the noise (the repo's test-noise budget enforces it).
            with contextlib.redirect_stdout(io.StringIO()):
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
    _run(d, "init", "-q", "--bare", str(origin))
    _run(origin, "symbolic-ref", "HEAD", "refs/heads/main")
    work = Path(d) / "work"; work.mkdir()
    _run(work, "init", "-q"); _run(work, "checkout", "-q", "-b", "main")
    _run(work, "config", "user.email", "t@t"); _run(work, "config", "user.name", "t")
    _run(work, "remote", "add", "origin", str(origin))
    (work / "README.md").write_text("base\n", encoding="utf-8")
    _run(work, "add", "-A"); _run(work, "commit", "-qm", "base")
    _run(work, "push", "-q", "origin", "main")
    other = Path(d) / "other"
    _run(d, "clone", "-q", str(origin), str(other))
    _run(other, "config", "user.email", "o@o"); _run(other, "config", "user.name", "o")
    crd = other / "sdlc-studio" / "change-requests"; crd.mkdir(parents=True)
    (crd / "CR0001-remote.md").write_text("# CR-0001: remote\n", encoding="utf-8")
    _run(other, "add", "-A"); _run(other, "commit", "-qm", "remote cr")
    _run(other, "push", "-q", "origin", "main")
    return work


def _up_to_date_repo(d):
    """A work clone that is level with origin (no divergence)."""
    origin = Path(d) / "origin.git"
    _run(d, "init", "-q", "--bare", str(origin))
    _run(origin, "symbolic-ref", "HEAD", "refs/heads/main")
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
    _run(d, "init", "-q", "--bare", str(origin))
    _run(origin, "symbolic-ref", "HEAD", f"refs/heads/{branch}")
    seed = Path(d) / "seed"; seed.mkdir()
    _run(seed, "init", "-q"); _run(seed, "checkout", "-q", "-b", branch)
    _run(seed, "config", "user.email", "s@s"); _run(seed, "config", "user.name", "s")
    _run(seed, "remote", "add", "origin", str(origin))
    crd = seed / "sdlc-studio" / "change-requests"; crd.mkdir(parents=True)
    (crd / "CR0005-remote.md").write_text("# CR-0005: r\n", encoding="utf-8")
    _run(seed, "add", "-A"); _run(seed, "commit", "-qm", "cr5")
    _run(seed, "push", "-q", "origin", branch)
    work = Path(d) / "work"
    _run(d, "clone", "-q", str(origin), str(work))
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
            # stdout captured: a green suite must print nothing, or a real error
            # hides in the noise (the repo's test-noise budget enforces it).
            with contextlib.redirect_stdout(io.StringIO()):
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
            # stdout captured: a green suite must print nothing, or a real error
            # hides in the noise (the repo's test-noise budget enforces it).
            with contextlib.redirect_stdout(io.StringIO()):
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

    def test_an_unreadable_backlog_artefact_is_logged_as_a_drop_in_the_plan(self) -> None:
        # BG0163: a backlog file the triage scan cannot read must be NAMED in the plan's triage
        # section, not silently truncated into a clean-looking plan (the drop status already
        # surfaces). The batch itself is one coherent, readable bug.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _src(root, "src/a.py"); _src(root, "src/b.py")
            self._dupbug(root, 1, "colour the status output", "render green and amber", "src/a.py")
            # a non-UTF-8 backlog artefact the scan counts as skipped, never swallows (a CR, so it
            # is off the --bugs batch: the drop is a triage gap, not a selection failure)
            (root / "sdlc-studio" / "change-requests").mkdir(parents=True, exist_ok=True)
            (root / "sdlc-studio" / "change-requests" / "CR0009-bad.md").write_bytes(
                b"# CR-0009: broken\n\xff\xfe not utf-8\n")
            rc, out, _ = self._plan(root)
            self.assertEqual(rc, 0)                       # reporting, never a refusal
            self.assertIn("unreadable", out)
            self.assertIn("not triaged", out)


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


def _verified_story(root: Path, num: int, affects: str | None, verifiers: list[str],
                    points: int = 2, status: str = "Ready") -> Path:
    """A story whose ACs carry `Verify:` lines - the files a unit will touch, named in the
    one place a unit already names them."""
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    aff = f"> **Affects:** {affects}\n" if affects else ""
    body = "".join(
        f"\n### AC{i}: a\n\n- **Given** x\n- **Verify:** {v}\n" for i, v in enumerate(verifiers, 1))
    p = d / f"US{num:04d}-x.md"
    p.write_text(f"# US{num:04d}: s\n\n> **Status:** {status}\n> **Priority:** Medium\n"
                 f"{aff}> **Points:** {points}\n\n## Acceptance Criteria\n{body}",
                 encoding="utf-8")
    return p


class ContradictedAffectsTests(unittest.TestCase):
    """US0292/CR0347. `breakdown` already computed `unresolvable` per path but reported it only
    when EVERY declared path failed, so four real files plus one typo read as fully groomed and
    the typo travelled on into the collision analysis and the engagement floor, both of which
    read `Affects`.

    This is not a hypothetical: four of the twenty-two stories minted for this batch carried a
    wrong or incomplete `Affects`, one written by the author minutes after ruling on the defect."""

    def _bd(self, root: Path) -> dict:
        return _load().build_plan(root, "story", "Ready", skip_personas=True)["breakdown"]

    def test_a_partly_unresolvable_affects_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _src(root, "src/real.py")
            _src(root, "tests/test_p.py")
            _verified_story(root, 1, "src/real.py,src/typo.py",
                            ["pytest tests/test_p.py -k test_x"])
            adv = {a["id"]: a for a in self._bd(root)["affects_advisories"]}
            self.assertIn("US0001", adv, "one bad path among good ones is still reported")
            self.assertEqual(adv["US0001"]["unresolvable"], ["src/typo.py"])

    def test_a_file_the_acs_name_but_affects_omits_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _src(root, "src/real.py")
            _src(root, "tests/test_p.py")
            _verified_story(root, 1, "src/real.py", ["pytest tests/test_p.py -k test_x"])
            adv = {a["id"]: a for a in self._bd(root)["affects_advisories"]}
            self.assertIn("tests/test_p.py", adv["US0001"]["undeclared"])

    def test_the_affects_advisory_never_changes_the_grooming_verdict(self) -> None:
        """The bound that keeps this reportable rather than obstructive. A path to a file the
        unit will CREATE cannot resolve, so refusing on it would refuse the ordinary case."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _src(root, "src/real.py")
            _src(root, "tests/test_p.py")
            _verified_story(root, 1, "src/real.py,src/not-yet.py",
                            ["pytest tests/test_p.py -k test_x"])
            bd = self._bd(root)
            self.assertTrue(bd["affects_advisories"], "the precondition: it IS reported")
            self.assertEqual(bd["groomed"], ["US0001"])
            self.assertEqual(bd["ungroomed"], [])
            self.assertTrue(bd["ok"])

    def test_a_clean_affects_raises_no_advisory(self) -> None:
        """The negative control. Without it every assertion above is satisfied by a function
        that reports every unit unconditionally."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _src(root, "src/real.py")
            _src(root, "tests/test_p.py")
            _verified_story(root, 1, "src/real.py,tests/test_p.py",
                            ["pytest tests/test_p.py -k test_x"])
            self.assertEqual(self._bd(root)["affects_advisories"], [])


class DerivedClusterFileTests(unittest.TestCase):
    """US0291/CR0347: the collision analysis saw only what somebody DECLARED, and test files
    are almost never declared - so the one file parallel work most often shares was the one
    file the analysis was blind to. US0252 and US0256 both wrote test_reconcile.py, neither
    declared it, two agents edited it concurrently and the suite failed with an import error
    belonging to neither.

    D0053 bounds it: derived from Verify lines ONLY (prose has no grammar to parse), and a
    derived path must NEVER satisfy the grooming gate's `Affects` requirement."""

    def _bd(self, root: Path) -> dict:
        return _load().build_plan(root, "story", "Ready", skip_personas=True)["breakdown"]

    def test_units_sharing_an_undeclared_test_file_are_one_cluster(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _src(root, "src/a.py")
            _src(root, "src/b.py")
            _src(root, "tests/test_shared.py")
            _verified_story(root, 1, "src/a.py", ["pytest tests/test_shared.py -k test_one"])
            _verified_story(root, 2, "src/b.py", ["pytest tests/test_shared.py -k test_two"])
            bd = self._bd(root)
            self.assertEqual([c["units"] for c in bd["clusters"]], [["US0001", "US0002"]])
            self.assertIn("tests/test_shared.py", bd["clusters"][0]["files"])

    def test_derived_files_come_from_the_verifier_parser(self) -> None:
        """Every path is the one `verify_ac` resolves for that expression, across the DSL
        verbs that carry one - so the planner and the verifier cannot disagree about what a
        Verify line targets."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            for rel in ("tests/test_p.py", "docs/ref.md", "src/one.py", "src/two.py"):
                _src(root, rel)
            text = _verified_story(root, 1, "src/one.py", [
                "pytest tests/test_p.py -k test_x",
                "file docs/ref.md",
                "grep \"a pattern\" src/two.py",
                "jest some test name",          # carries no path - nothing is invented
            ]).read_text(encoding="utf-8")
            derived = sp.verify_files(root, text)
            self.assertEqual(sorted(derived),
                             ["docs/ref.md", "src/two.py", "tests/test_p.py"])
            # ...and they are the SAME strings verify_ac builds its command from
            sys.path.insert(0, str(SCRIPT.parent))
            import verify_ac
            _, cmd = verify_ac._build_command("pytest tests/test_p.py -k test_x", cwd=root)
            self.assertIn("tests/test_p.py", cmd)

    def test_cluster_files_record_declared_or_derived(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _src(root, "src/shared.py")
            _src(root, "tests/test_shared.py")
            _verified_story(root, 1, "src/shared.py",
                            ["pytest tests/test_shared.py -k test_one"])
            _verified_story(root, 2, "src/shared.py",
                            ["pytest tests/test_shared.py -k test_two"])
            cluster = self._bd(root)["clusters"][0]
            self.assertEqual(cluster["sources"]["src/shared.py"], "declared")
            self.assertEqual(cluster["sources"]["tests/test_shared.py"], "derived")

    def test_derived_files_do_not_satisfy_the_affects_gate(self) -> None:
        """D0053: if derivation could satisfy the gate, a unit declaring NOTHING would pass
        by having its verifiers read - disarming the field the engagement floor depends on."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _src(root, "tests/test_shared.py")
            _verified_story(root, 1, None, ["pytest tests/test_shared.py -k test_one"])
            _verified_story(root, 2, None, ["pytest tests/test_shared.py -k test_two"])
            bd = self._bd(root)
            missing = {u["id"]: u["missing"] for u in bd["ungroomed"]}
            self.assertEqual(sorted(missing), ["US0001", "US0002"])
            self.assertIn("Affects", missing["US0001"])
            # ...and the derived files still reach the collision analysis
            self.assertEqual([c["units"] for c in bd["clusters"]], [["US0001", "US0002"]])
            self.assertIn("tests/test_shared.py", bd["clusters"][0]["files"])


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


_VELOCITY_HEADER = (
    "| Retro | Date | Units | Measured | Forecast | Points | Estimate (tokens, plan-time) | "
    "Actual (tokens) | Ratio (est/actual) | Tokens/pt | Oversized | Wall (s) | Constants | "
    "Sample | Model | Note | Source |\n"
    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | "
    "--- | --- | --- |\n")


def _velocity(root: Path, rows: list[dict]) -> Path:
    """Write a VELOCITY.md holding `rows` - the record the tokens-per-point rate is MANDATED
    to be re-measured from. Each row: id/points/actual/model/estimate/constants.

    `measured` is a KEY, not a constant. It used to be hardcoded to 0 on every fixture row,
    which pinned every test to the sprint-level shape and made the per-unit-sum shape - the
    one whose Actual measures the BUILD and not the whole sprint - unreachable from the
    suite (L-0174)."""
    p = root / "sdlc-studio" / "retros" / "VELOCITY.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    body = ""
    for r in rows:
        units = r.get("units", 3)
        body += ("| {id} | 2026-01-01 | {units} | {measured} | {units} | {points} | {estimate} "
                 "| {actual} | {ratio} | - | 0 | - | {constants} | - | {model} | - | harness |\n"
                 ).format(id=r["id"], units=units, measured=r.get("measured", 0),
                          points=r.get("points", "-"),
                          estimate=r.get("estimate", 0), actual=r.get("actual", "-"),
                          ratio=r.get("ratio", "-"), constants=r.get("constants", "-"),
                          model=r.get("model", "-"))
    p.write_text(_VELOCITY_HEADER + body, encoding="utf-8")
    return p


class RateFromVelocityRecordTests(unittest.TestCase):
    """US0290: VELOCITY.md is the MANDATED source of the tokens-per-point rate, and nothing in
    the planner read it. The per-unit evidence log an interactive sprint never writes was the
    only source, so the plan quoted the seed forever while the record held real measurements."""

    def _plan(self, root: Path, *extra: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = _load().main(["plan", "--crs", "Proposed", "--root", str(root),
                               "--no-fetch", "--skip-personas", *extra])
        return rc, out.getvalue(), err.getvalue()

    def test_the_plan_rate_is_measured_from_the_velocity_record(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            _velocity(root, [{"id": "RETRO0001", "points": 30, "actual": 2_390_624,
                              "model": "claude-opus-4-8"},
                             {"id": "RETRO0002", "points": 31, "actual": 1_265_392,
                              "model": "claude-opus-4-8"}])
            rate = sp.tokens_per_point(root)
            self.assertEqual(rate["source"], "velocity-record")
            self.assertEqual(rate["rate"], round((2_390_624 + 1_265_392) / 61))
            self.assertIn("VELOCITY.md", rate["basis"])
            _pointed_cr(root, 1, 3)
            fc = sp.build_plan(root, "cr", "Proposed", order="wsjf")["token_forecast"]
            self.assertEqual(fc["rate_source"], "velocity-record")
            self.assertEqual(fc["tokens"], 3 * rate["rate"])
            rc, out, err = self._plan(root)
            self.assertEqual(rc, 0)
            self.assertIn("velocity-record", out)

    def test_an_interactive_sprint_can_now_advance_the_rate(self) -> None:
        """BG0248, stated as the property it denied. An interactive sprint has no runner and so
        writes NO per-unit actual: on this repo 208 forecast records carried plan-time points and
        exactly 3 had a per-unit actual, all from the runner era, so a rate joined against that
        log could never advance however well a sprint was measured. The assertion that matters is
        the emptiness: with nothing in the per-unit log at all, the velocity record alone must
        still yield a MEASURED rate."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            _velocity(root, [{"id": "RETRO0001", "points": 30, "actual": 2_390_624,
                              "model": "claude-opus-4-8"},
                             {"id": "RETRO0002", "points": 31, "actual": 1_265_392,
                              "model": "claude-opus-4-8"}])
            import telemetry
            self.assertEqual(telemetry.actuals(root), {},
                             "the premise: an interactive project records no per-unit actual")
            rate = sp.tokens_per_point(root)
            self.assertEqual(rate["source"], "velocity-record",
                             "the rate advances on sprint-level evidence alone")
            self.assertEqual(rate["rate"], round((2_390_624 + 1_265_392) / 61))
            self.assertIsNone(rate.get("refused"))

    def test_a_rate_spanning_two_models_refuses_rather_than_averaging(self) -> None:
        """The other half of BG0248, and the reason this repo still reads `seed` today: three of
        its four velocity rows carry no model, so the record spans `unrecorded` and a named one.
        Averaging them would publish a rate describing neither. Recording the delivering model is
        CR0373 and is NOT in this batch, so the honest outcome here is a refusal carrying its
        reason, never a silent seed."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            _velocity(root, [{"id": "RETRO0001", "points": 30, "actual": 2_390_624,
                              "model": "claude-opus-4-8"},
                             {"id": "RETRO0002", "points": 31, "actual": 1_265_392}])
            rate = sp.tokens_per_point(root)
            self.assertEqual(rate["source"], "seed")
            self.assertIn("REFUSED", rate["refused"])
            self.assertIn("model", rate["refused"])
            _pointed_cr(root, 1, 3)   # the forecast block only renders for a non-empty batch
            rc, out, err = self._plan(root)
            self.assertEqual(rc, 0, "a plan is never refused over a token estimate")
            self.assertIn("velocity record yields no usable rate", out,
                          "the refusal reaches the operator instead of a bare seed")

    def test_no_measured_rate_is_quoted_as_a_seed_and_says_so(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            _velocity(root, [])          # a record with no row that carries both
            rate = sp.tokens_per_point(root)
            self.assertEqual(rate["source"], "seed")
            self.assertEqual(rate["rate"], sp.POINTS_RATE_SEED)
            _pointed_cr(root, 1, 3)
            rc, out, err = self._plan(root)
            self.assertEqual(rc, 0)
            self.assertIn("rate (seed)", out)
            self.assertIn("measured no rate of its own", out)
            self.assertIn("token forecast", out)          # planning is never refused over it

    def test_a_refused_rate_reaches_the_plan_output(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            _velocity(root, [{"id": "RETRO0001", "points": 30, "actual": 2_390_624,
                              "model": "claude-opus-4-8"},
                             {"id": "RETRO0002", "points": 31, "actual": 1_265_392,
                              "model": "claude-haiku-4-5"}])
            rate = sp.tokens_per_point(root)
            self.assertEqual(rate["source"], "seed")
            self.assertIn("claude-opus-4-8", rate["refused"])
            self.assertIn("claude-haiku-4-5", rate["refused"])
            _pointed_cr(root, 1, 3)
            rc, out, err = self._plan(root)
            self.assertEqual(rc, 0)
            blob = out + err
            self.assertIn("claude-opus-4-8", blob)
            self.assertIn("claude-haiku-4-5", blob)

    def test_the_seed_line_carries_its_out_of_sample_result(self) -> None:
        """The seed's one live test failed at 0.44x. A seed quoted with nothing beside it
        reads as calibrated."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            _velocity(root, [{"id": "RETRO0028", "estimate": 250_000, "actual": 564_066,
                              "ratio": "0.44x",
                              "constants": f"TOKENS_PER_POINT={sp.POINTS_RATE_SEED}"}])
            _pointed_cr(root, 1, 3)
            fc = sp.build_plan(root, "cr", "Proposed", order="wsjf")["token_forecast"]
            self.assertEqual([r["id"] for r in fc["rate_out_of_sample"]], ["RETRO0028"])
            self.assertEqual(fc["rate_out_of_sample"][0]["ratio"], 0.44)
            rc, out, err = self._plan(root)
            self.assertEqual(rc, 0)
            # the result must sit ON the rate line, not somewhere else in the plan: a reader
            # of a seed must see its one live test beside the number, not three blocks away
            line = next(ln for ln in out.splitlines() if "out-of-sample test of this seed" in ln)
            self.assertIn("RETRO0028", line)
            self.assertIn("0.44x", line)


class ForecastScopeTests(unittest.TestCase):
    """BG0254: the point forecast prices the BUILD. On this project the review, the repair
    rounds and the re-verification cost more than the build did, and the forecast did not
    admit they exist - so every plan understated by design and the capacity check that reads
    it was calibrated against a fiction. The fix is to name the exclusion and show the
    measured excess, NOT to refit the constant against one sprint."""

    def _plan(self, root: Path) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = _load().main(["plan", "--crs", "Proposed", "--root", str(root),
                               "--no-fetch", "--skip-personas"])
        return rc, out.getvalue(), err.getvalue()

    def test_the_forecast_names_what_it_prices_and_what_it_excludes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            _pointed_cr(root, 1, 3)
            fc = sp.build_plan(root, "cr", "Proposed", order="wsjf")["token_forecast"]
            self.assertEqual(fc["scope"], "build")
            excl = " ".join(fc["excludes"]).lower()
            self.assertIn("review", excl)
            self.assertIn("repair", excl)
            rc, out, err = self._plan(root)
            self.assertEqual(rc, 0)
            self.assertIn("prices the BUILD", out)
            self.assertIn("excludes", out)

    def test_the_excess_over_the_build_forecast_is_measured_not_a_constant(self) -> None:
        """The proving term the operator can see. It is READ OFF the record - every sprint
        that carries both a plan-time forecast and a whole-sprint actual - and it is never
        attributed to proving alone, because the record cannot separate proving cost from an
        under-estimated build."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            seed = sp.POINTS_RATE_SEED
            _velocity(root, [{"id": "RETRO0065", "estimate": 400_000, "actual": 2_634_055,
                              "ratio": "0.15x", "constants": f"TOKENS_PER_POINT={seed}"}])
            term = sp.whole_sprint_excess(root)
            self.assertTrue(term["measured"])
            self.assertEqual(term["sprints"], ["RETRO0065"])
            self.assertAlmostEqual(term["high"], round(2_634_055 / 400_000, 2))
            _pointed_cr(root, 1, 3)
            rc, out, err = self._plan(root)
            self.assertEqual(rc, 0)
            self.assertIn("RETRO0065", out)
            self.assertIn("whole-sprint", out)
            self.assertNotIn("proving cost is 1.5x", out)   # no fitted multiplier is invented

    def test_an_unmeasured_excess_says_so_rather_than_assuming_a_multiplier(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            _pointed_cr(root, 1, 3)
            term = sp.whole_sprint_excess(root)
            self.assertFalse(term["measured"])
            self.assertEqual(term["sprints"], [])
            self.assertIsNone(term["low"])
            rc, out, err = self._plan(root)
            self.assertEqual(rc, 0)
            self.assertIn("UNMEASURED", out)

    def test_the_caveat_that_the_excess_is_not_proving_cost_is_printed(self) -> None:
        """The caveat is the honesty of the number, not decoration around it: the excess is
        proving PLUS whatever the build was under-estimated by, and the record carries no split
        between them. Deleting the line left 289 tests green, so nothing pinned the one
        sentence that stops the figure being read as a measured proving multiplier."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            seed = sp.POINTS_RATE_SEED
            _velocity(root, [{"id": "RETRO0065", "estimate": 400_000, "actual": 2_634_055,
                              "constants": f"TOKENS_PER_POINT={seed}"}])
            _pointed_cr(root, 1, 3)
            rc, out, err = self._plan(root)
            self.assertEqual(rc, 0)
            self.assertIn("NOT attributed to proving alone", out)
            self.assertIn("under-estimate of the build", out)
            # ...and it sits with the excess, not in some other block
            lines = out.splitlines()
            at = next(i for i, ln in enumerate(lines) if "whole-sprint cost against" in ln)
            self.assertIn("NOT attributed to proving alone", lines[at + 1])

    def test_a_row_the_estimator_in_force_did_not_forecast_is_not_an_observation(self) -> None:
        """The in-sample filter is load-bearing and nothing pinned it: deleting it left 289
        tests green while widening the published span on this project's own record from
        1.63x-6.59x over 4 sprints to 0.3x-6.59x over 8. A row forecast by the RETIRED
        base/tpc estimator judges that estimator, so its multiple says nothing about the
        forecast this plan is about to quote."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            seed = sp.POINTS_RATE_SEED
            _velocity(root, [{"id": "RETRO0026", "estimate": 348_400, "actual": 902_503,
                              "constants": "base=50000 tpc=600"},
                             {"id": "RETRO0065", "estimate": 400_000, "actual": 2_634_055,
                              "constants": f"TOKENS_PER_POINT={seed}"}])
            self.assertEqual(sp.sample_class("RETRO0026",
                                             {"BASE_TOKEN_BUDGET": 50_000,
                                              "TOKENS_PER_COGNITIVE": 600}, root),
                             sp.SAMPLE_STALE)
            term = sp.whole_sprint_excess(root)
            self.assertEqual(term["sprints"], ["RETRO0065"])
            self.assertEqual(term["low"], term["high"])
            self.assertNotIn("RETRO0026", [o["id"] for o in term["observations"]])

    def test_a_per_unit_build_sum_is_not_a_whole_sprint_actual(self) -> None:
        """The span is labelled whole-sprint, so only a whole-sprint Actual may enter it. A row
        whose every unit carries per-unit telemetry (Measured == Units) holds the sum of the
        units' BUILD cost - orchestration, review and repair are not in it - and dividing that
        by a build forecast measures nothing about the whole sprint. This repo published
        RETRO0028 (Units 3 / Measured 3) at 2.26x inside exactly that span."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            seed = sp.POINTS_RATE_SEED
            _velocity(root, [{"id": "RETRO0028", "units": 3, "measured": 3, "points": 10,
                              "estimate": 250_000, "actual": 564_066,
                              "constants": f"TOKENS_PER_POINT={seed}"},
                             {"id": "RETRO0065", "units": 7, "measured": 0, "points": 18,
                              "estimate": 400_000, "actual": 2_634_055,
                              "constants": f"TOKENS_PER_POINT={seed}"}])
            term = sp.whole_sprint_excess(root)
            self.assertEqual(term["sprints"], ["RETRO0065"],
                             "a per-unit build sum is excluded, not published as whole-sprint")
            self.assertAlmostEqual(term["low"], round(2_634_055 / 400_000, 2))
            # the negative control: the same row, measured as a sprint-level total, IS one
            _velocity(root, [{"id": "RETRO0028", "units": 3, "measured": 0, "points": 10,
                              "estimate": 250_000, "actual": 564_066,
                              "constants": f"TOKENS_PER_POINT={seed}"}])
            self.assertEqual(sp.whole_sprint_excess(root)["sprints"], ["RETRO0028"])


class RowClassSurvivesRemeasurementTests(unittest.TestCase):
    """MAJOR, RUN-01KY3MFX review: US0290 made the tokens-per-point rate RE-MEASURED from
    VELOCITY.md on every plan, while `sample_class` still classified each recorded row by
    comparing its stamped constants against that live rate. So the moment a later sprint moved
    the rate, every historical row read `stale-constants` - the measured whole-sprint excess
    emptied to UNMEASURED and the forecast band silently reverted to its default, without one
    recorded fact having changed.

    A row's class is a fact about the plan that WROTE it. Nothing measured afterwards can
    reach back and change what a past plan forecast with."""

    #: This repo's own four rows carrying both a forecast and a sprint actual. Three record no
    #: model, which is what refuses the record today and pins the rate at the seed; CR0373 will
    #: stamp them, and that stamp alone is the whole trigger.
    ROWS = ((28, 10, 250_000, 564_066), (60, 30, 750_000, 2_390_624),
            (61, 31, 775_000, 1_265_392), (65, 18, 400_000, 2_634_055))

    def _record(self, root: Path, *, stamped: bool) -> None:
        seed = _load().POINTS_RATE_SEED
        _velocity(root, [{"id": f"RETRO00{n}", "points": pts, "estimate": est, "actual": act,
                          "constants": f"TOKENS_PER_POINT={seed}",
                          "model": "claude-opus-4-8" if (stamped or n == 28) else "-"}
                         for n, pts, est, act in self.ROWS])

    def test_stamping_the_model_does_not_empty_the_measured_excess(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            self._record(root, stamped=False)
            before_rate, before = sp.tokens_per_point(root), sp.whole_sprint_excess(root)
            self.assertEqual(before_rate["source"], "seed")   # refused across two models
            self.assertTrue(before["measured"])
            self.assertEqual(before["low"], 1.63)
            self.assertEqual(before["high"], 6.59)

            self._record(root, stamped=True)                  # the CR0373 stamp, and nothing else
            after_rate, after = sp.tokens_per_point(root), sp.whole_sprint_excess(root)
            self.assertEqual(after_rate["source"], "velocity-record")
            self.assertEqual(after_rate["rate"], 77_013)      # the rate DID move, as it should
            self.assertTrue(after["measured"],
                            "a re-measurement must not retire the evidence that justified it")
            self.assertEqual(after["sprints"], before["sprints"])
            self.assertEqual((after["low"], after["high"]), (before["low"], before["high"]))

    def test_the_calibration_band_does_not_revert_when_the_rate_moves(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            _velocity(root, [{"id": "RETRO0028", "points": 10, "estimate": 250_000,
                              "actual": 564_066, "ratio": "0.44x",
                              "constants": f"TOKENS_PER_POINT={sp.POINTS_RATE_SEED}",
                              "model": "claude-opus-4-8"}])
            cal = sp.calibration(root)
            self.assertEqual(cal["sprints"], 1)
            self.assertEqual(cal["stale_constants"], 0)
            self.assertGreater(cal["high"], 1.0 + sp.FORECAST_BAND)   # the row WIDENED the band
            self.assertEqual(sp.tokens_per_point(root)["source"], "velocity-record",
                             "the premise: this row's own model now sets the live rate")

    def test_a_row_is_classified_against_the_estimator_that_forecast_it(self) -> None:
        """Directly, without a record: the live rate is the seed here, and a row forecast at a
        DIFFERENT calibration of the same estimator is still evidence about that estimator.
        Only a row carrying the retired estimator's parameters is stale."""
        sp = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.assertEqual(sp.tokens_per_point(root)["rate"], sp.POINTS_RATE_SEED)
            self.assertEqual(sp.sample_class("RETRO0099", {"TOKENS_PER_POINT": 999_999}, root),
                             sp.SAMPLE_OUT)
            self.assertEqual(sp.sample_class("RETRO0099", {"BASE_TOKEN_BUDGET": 50_000,
                                                           "TOKENS_PER_COGNITIVE": 600}, root),
                             sp.SAMPLE_STALE)


class RefusalTravelsWithEverySourceTests(unittest.TestCase):
    """MAJOR, RUN-01KY3MFX review: `tokens_per_point` promises that neither source is ever
    silently substituted for the other, and BG0248 AC2 claims the refusal reason is carried to
    the plan output. The per-unit evidence branch carried no `refused` key at all, so a
    REFUSED velocity record was discarded in silence whenever the evidence log had enough
    units. Every existing refusal test left that log EMPTY, so all four landed on the seed and
    the branch was never reached (L-0174)."""

    def _log(self, root: Path, units: int, points: int, tokens: int) -> None:
        import telemetry
        telemetry.record_forecasts(root, [{"id": f"BG{i:04d}", "points": points,
                                           "tokens": points * 25_000}
                                          for i in range(1, units + 1)])
        for i in range(1, units + 1):
            telemetry.record(root, {"id": f"BG{i:04d}", "tokens": tokens,
                                    "model": "claude-opus-4-8"})

    def _refusing_record(self, root: Path) -> None:
        _velocity(root, [{"id": "RETRO0001", "points": 30, "actual": 2_390_624,
                          "model": "claude-opus-4-8"},
                         {"id": "RETRO0002", "points": 31, "actual": 1_265_392,
                          "model": "claude-haiku-4-5"}])

    def test_the_evidence_log_answer_still_carries_the_records_refusal(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            self._refusing_record(root)
            self._log(root, sp.RATE_MIN_UNITS + 1, 3, 120_000)
            rate = sp.tokens_per_point(root)
            self.assertEqual(rate["source"], "measured", "the premise: the branch is reached")
            self.assertIn("REFUSED", rate["refused"] or "",
                          "the mandated source was set aside; the reason travels with the answer")
            self.assertIn("claude-haiku-4-5", rate["refused"])

    def test_the_refusal_reaches_the_plan_whatever_source_stood_instead(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            self._refusing_record(root)
            self._log(root, sp.RATE_MIN_UNITS + 1, 3, 120_000)
            _pointed_cr(root, 1, 3)
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = sp.main(["plan", "--crs", "Proposed", "--root", str(root),
                              "--no-fetch", "--skip-personas"])
            self.assertEqual(rc, 0)
            blob = out.getvalue()
            self.assertIn("velocity record yields no usable rate", blob)
            self.assertIn("claude-haiku-4-5", blob)
            self.assertNotIn("so the seed stands instead", blob,
                             "the seed did NOT stand: the evidence log did, and it says so")
            self.assertIn("per-unit evidence log stands instead", blob)

    def test_the_refusal_names_the_seed_when_the_seed_is_what_stands(self) -> None:
        """The OTHER half of the same sentence, and the reason the fallback default under it
        is dead: only these two sources can be standing here. The velocity record is the one
        that refused, so it is never also the one that stands (MINOR, round 2)."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            self._refusing_record(root)          # ...and no evidence log at all
            _pointed_cr(root, 1, 3)
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = sp.main(["plan", "--crs", "Proposed", "--root", str(root),
                              "--no-fetch", "--skip-personas"])
            self.assertEqual(rc, 0)
            blob = out.getvalue()
            self.assertEqual(sp.tokens_per_point(root)["source"], sp.RATE_SEED,
                             "the premise: the seed is what stood")
            self.assertIn("velocity record yields no usable rate", blob)
            self.assertIn("the seed stands instead", blob)
            self.assertNotIn("per-unit evidence log stands instead", blob)


class BatchHistoryTests(unittest.TestCase):
    """What sprints ACTUALLY cost is the plan's real input, so it must not silently drop the
    most relevant sprints. An interactive sprint has no runner and therefore no per-unit
    telemetry, so its `Measured` column is 0 while its sprint-level Actual is real. Gating the
    block on `Measured` dropped every one of them and left the OLDEST runner-era rows standing
    as the current cost picture.

    Both kinds are shown, and each row says WHICH it is: a sprint-level per-unit figure is the
    sprint total divided by its units, so the variance between units is hidden - one unit may
    have eaten half the budget. That is the accepted cost of including them, and the label is
    what stops the two being read as the same measurement.
    """

    HEAD = ("| Retro | Date | Units | Measured | Estimate (tokens, plan-time) | "
            "Actual (tokens) | Ratio (est/actual) | Constants | Sample |\n"
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n")

    def _velocity(self, root: Path, rows: str) -> None:
        retros = root / "sdlc-studio" / "retros"
        retros.mkdir(parents=True, exist_ok=True)
        (retros / "VELOCITY.md").write_text(self.HEAD + rows, encoding="utf-8")

    #: The two sprints the filed bug names, verbatim from this project's own history.
    INTERACTIVE = ("| RETRO0060 | 2026-07-20 | 9 | 0 | 0 | 2,390,624 | - | - | - |\n"
                   "| RETRO0061 | 2026-07-20 | 13 | 0 | 0 | 1,265,392 | - | - | - |\n")
    RUNNER = "| RETRO0025 | 2026-07-14 | 5 | 5 | 352,600 | 642,358 | 0.55x | - | - |\n"

    def test_an_interactive_sprint_is_included_and_costed_from_its_total(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            self._velocity(root, self.INTERACTIVE)
            hist = {h["id"]: h for h in sp.batch_history(root)}
            self.assertEqual(sorted(hist), ["RETRO0060", "RETRO0061"])
            self.assertEqual(hist["RETRO0060"]["units"], 9)
            self.assertEqual(hist["RETRO0060"]["per_unit"], 2_390_624 // 9)
            self.assertEqual(hist["RETRO0061"]["per_unit"], 1_265_392 // 13)

    def test_each_row_says_which_kind_of_evidence_it_is(self) -> None:
        """The label is the whole reason inclusion is honest: sprint-level hides per-unit
        variance, per-unit does not, and a reader cannot weigh a row without knowing which."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            self._velocity(root, self.RUNNER + self.INTERACTIVE)
            basis = {h["id"]: h["basis"] for h in sp.batch_history(root)}
            self.assertEqual(basis["RETRO0025"], "per-unit")
            self.assertEqual(basis["RETRO0060"], "sprint-level")
            self.assertEqual(basis["RETRO0061"], "sprint-level")

    def test_a_per_unit_row_divides_by_the_units_that_were_measured(self) -> None:
        """A runner-era sprint that delivered 7 units but recorded telemetry for 5 is evidence
        about those 5. Dividing by the 7 would report a per-unit cost for two units nothing was
        measured on."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            self._velocity(root,
                           "| RETRO0027 | 2026-07-14 | 7 | 5 | 349,000 | 789,591 | - | - | - |\n")
            row = sp.batch_history(root)[0]
            self.assertEqual(row["units"], 5)
            self.assertEqual(row["per_unit"], 789_591 // 5)
            self.assertEqual(row["basis"], "per-unit")

    def test_a_sprint_with_no_recorded_actual_stays_out(self) -> None:
        """Inclusion is about the DIVISOR, not the numerator. A sprint whose tokens were never
        captured has no cost to report, and inventing one from units alone would be fabrication.
        Both shapes of absence are here: a blank cell, and the 0 an earlier close wrote into one
        - a recorded zero is the same non-measurement and must not become a 0/unit row."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            self._velocity(root, "| RETRO0064 | 2026-07-21 | 10 | 0 | 0 | - | - | - | - |\n"
                                 "| RETRO0059 | 2026-07-20 | 6 | 0 | 0 | 0 | - | - | - |\n")
            self.assertEqual(sp.batch_history(root), [])

    def test_a_sprint_with_an_actual_but_no_units_at_all_stays_out(self) -> None:
        """No divisor of either kind: a per-unit figure cannot be derived, so no row is made
        rather than one that divides by zero or quietly reports the total as a per-unit cost."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            self._velocity(root, "| RETRO0065 | 2026-07-21 | 0 | 0 | 0 | 900,000 | - | - | - |\n")
            self.assertEqual(sp.batch_history(root), [])

    #: The same table with the Source column the history now records. Provenance is a fact
    #: about the NUMERATOR; `basis` is a fact about the divisor, and neither answers the other.
    HEAD_SOURCED = ("| Retro | Date | Units | Measured | Estimate (tokens, plan-time) | "
                    "Actual (tokens) | Ratio (est/actual) | Constants | Sample | Source |\n"
                    + "| --- " * 10 + "|\n")

    def _sourced(self, root: Path, rows: str) -> None:
        retros = root / "sdlc-studio" / "retros"
        retros.mkdir(parents=True, exist_ok=True)
        (retros / "VELOCITY.md").write_text(self.HEAD_SOURCED + rows, encoding="utf-8")

    def test_a_typed_total_cannot_pass_as_a_measured_one(self) -> None:
        """Admitting sprint-level rows admitted operator-TYPED ones with them, and the label
        `sprint-level` describes the divisor, not where the number came from - so a figure
        somebody keyed in read exactly like a harness capture in the block the plan quotes."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            self._sourced(root,
                          "| RETRO0060 | 2026-07-20 | 9 | 0 | 0 | 2,390,624 | - | - | - | "
                          "harness |\n"
                          "| RETRO0061 | 2026-07-20 | 13 | 0 | 0 | 1,265,392 | - | - | - | "
                          "supplied |\n")
            hist = {h["id"]: h for h in sp.batch_history(root)}
            self.assertEqual(hist["RETRO0060"]["source"], "harness")
            self.assertEqual(hist["RETRO0061"]["source"], "supplied")

    def test_a_row_with_no_recorded_source_says_unrecorded_not_measured(self) -> None:
        """Every row already on disk. Absent provenance is absent, and defaulting it to either
        answer would invent the distinction the column exists to record."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            self._velocity(root, self.INTERACTIVE)
            self.assertIsNone(sp.batch_history(root)[0]["source"])

    def test_the_printed_block_names_a_typed_total_as_a_claim(self) -> None:
        """It has to reach the operator's eye. A typed figure quoted in the cost picture with
        nothing marking it is the same defect the mutation ledger's provenance mark fixed."""
        sp = _load()
        data = {"token_forecast": {
            "tokens": 50_000, "points": 2, "rate": 25_000, "rate_source": "seed",
            "rate_basis": "b", "rate_units": 0,
            "history": [{"id": "RETRO0025", "units": 5, "tokens": 642_358,
                         "per_unit": 128_471, "basis": "per-unit", "source": "per-unit"},
                        {"id": "RETRO0061", "units": 13, "tokens": 1_265_392,
                         "per_unit": 97_337, "basis": "sprint-level",
                         "source": "supplied"}]}}
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            sp._render_token_forecast(data)
        text = buf.getvalue()
        self.assertIn("typed", text.lower())          # the caveat, once, under the block
        # ON THE ROW, not only in the caveat below it: a reader scanning four rows for the one
        # they want must be able to see which of them is a claim without counting caveats.
        row = next(ln for ln in text.splitlines() if "RETRO0061" in ln)
        self.assertIn("supplied", row, row)
        self.assertNotIn("supplied", next(ln for ln in text.splitlines() if "RETRO0025" in ln))

    def test_the_printed_block_labels_every_row_and_explains_the_derived_kind(self) -> None:
        """The label has to reach the operator's eye, not just the JSON: this block is read as
        the authoritative cost picture, and an unlabelled derived figure reads as a measured one."""
        sp = _load()
        data = {"token_forecast": {
            "tokens": 50_000, "points": 2, "rate": 25_000, "rate_source": "seed",
            "rate_basis": "b", "rate_units": 0,
            "history": [{"id": "RETRO0025", "units": 5, "tokens": 642_358,
                         "per_unit": 128_471, "basis": "per-unit"},
                        {"id": "RETRO0060", "units": 9, "tokens": 2_390_624,
                         "per_unit": 265_625, "basis": "sprint-level"}]}}
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            sp._render_token_forecast(data)
        text = buf.getvalue()
        self.assertIn("RETRO0060", text)
        self.assertIn("265,625/unit", text)
        self.assertIn("sprint-level", text)
        self.assertIn("per-unit", text)
        self.assertIn("variance", text)          # the hidden risk is stated, not assumed known

    def test_a_history_of_only_per_unit_rows_does_not_print_the_derived_caveat(self) -> None:
        """The caveat is about sprint-level rows. Printed unconditionally it would be noise on
        a block that is fine, which is how a real caveat stops being read."""
        sp = _load()
        data = {"token_forecast": {
            "tokens": 50_000, "points": 2, "rate": 25_000, "rate_source": "seed",
            "rate_basis": "b", "rate_units": 0,
            "history": [{"id": "RETRO0025", "units": 5, "tokens": 642_358,
                         "per_unit": 128_471, "basis": "per-unit"}]}}
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            sp._render_token_forecast(data)
        self.assertNotIn("variance", buf.getvalue())


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


class SprintGoalTests(unittest.TestCase):
    """US0183: an operator-supplied Sprint Goal is recorded at plan time - a product
    outcome, distinct from the --goal ladder rung. Absent = recorded as none, never invented."""

    def _plan(self, root, *extra):
        # stdin is ISOLATED: under a real terminal the goal prompt would otherwise block
        # the suite silently (redirect_stdout swallows the prompt) - the critic's repro.
        mod = _load()
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), \
                unittest.mock.patch.object(sys, "stdin", io.StringIO("")):
            rc = mod.main(["plan", "--bugs", "Open", "--no-fetch", "--root", str(root), *extra])
        return rc, out.getvalue(), err.getvalue()

    def test_sprint_goal_recorded_on_plan_and_run_state(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1)
            rc, _, _ = self._plan(root, "--write", "--sprint-goal", "make the estimator honest")
            self.assertEqual(rc, 0)
            plan = json.loads((root / "sdlc-studio" / ".local" / "sprint-plan.json").read_text())
            self.assertEqual(plan["sprint_goal"], "make the estimator honest")
            state = json.loads((root / "sdlc-studio" / ".local" / "run-state.json").read_text())
            self.assertEqual(state["sprint_goal"], "make the estimator honest")

    def test_absent_goal_recorded_as_none_never_invented(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1)
            rc, _, _ = self._plan(root, "--write")
            self.assertEqual(rc, 0)
            plan = json.loads((root / "sdlc-studio" / ".local" / "sprint-plan.json").read_text())
            self.assertIsNone(plan["sprint_goal"])
            state = json.loads((root / "sdlc-studio" / ".local" / "run-state.json").read_text())
            self.assertIsNone(state.get("sprint_goal"))

    def test_replan_without_flag_preserves_recorded_goal(self):
        # A mid-run re-cut (blocker sweep, re-plan) must not erase the goal the operator
        # set: like open_run's rung goal, absent preserves, only a stated value writes.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1)
            rc, _, _ = self._plan(root, "--write", "--sprint-goal", "make it honest")
            self.assertEqual(rc, 0)
            rc, _, _ = self._plan(root, "--write")  # re-cut, no flag
            self.assertEqual(rc, 0)
            state = json.loads((root / "sdlc-studio" / ".local" / "run-state.json").read_text())
            self.assertEqual(state["sprint_goal"], "make it honest")

    def test_interactive_prompt_reaches_plan_and_run_state(self):
        # AC1's prompted path: a tty operator with no flag is asked once; the answer
        # lands in BOTH records from one variable (LL0016).
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1)
            mod = _load()
            tty = unittest.mock.Mock()
            tty.isatty.return_value = True
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), \
                    unittest.mock.patch.object(sys, "stdin", tty), \
                    unittest.mock.patch("builtins.input", return_value="a prompted goal"):
                rc = mod.main(["plan", "--bugs", "Open", "--no-fetch", "--write",
                               "--root", str(root)])
            self.assertEqual(rc, 0)
            plan = json.loads((root / "sdlc-studio" / ".local" / "sprint-plan.json").read_text())
            state = json.loads((root / "sdlc-studio" / ".local" / "run-state.json").read_text())
            self.assertEqual((plan["sprint_goal"], state["sprint_goal"]),
                             ("a prompted goal", "a prompted goal"))

    def test_explicit_empty_flag_means_none_and_never_prompts(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1)
            mod = _load()
            tty = unittest.mock.Mock()
            tty.isatty.return_value = True
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), \
                    unittest.mock.patch.object(sys, "stdin", tty), \
                    unittest.mock.patch("builtins.input",
                                        side_effect=AssertionError("must not prompt")):
                rc = mod.main(["plan", "--bugs", "Open", "--no-fetch", "--write",
                               "--sprint-goal", "", "--root", str(root)])
            self.assertEqual(rc, 0)
            plan = json.loads((root / "sdlc-studio" / ".local" / "sprint-plan.json").read_text())
            self.assertIsNone(plan["sprint_goal"])


def _pointed_story(root: Path, num: int, points: int, status: str = "Ready") -> None:
    """A groomed story - resolvable Affects and Points, so the gate plans it."""
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    aff = _src(root, f"src/us{num:04d}.py")
    (d / f"US{num:04d}-x.md").write_text(
        f"# US{num:04d}: s\n\n> **Status:** {status}\n> **Priority:** Medium\n"
        f"> **Affects:** {aff}\n> **Points:** {points}\n", encoding="utf-8")


def _seats(root: Path, roles: tuple[str, ...] = ("product", "engineering", "qa")) -> None:
    """Project review seats. The goal consult is demanded of seats that EXIST: a project
    that has adopted none has nobody to demand it of."""
    d = root / "sdlc-studio" / "personas" / "seats"
    d.mkdir(parents=True, exist_ok=True)
    for role in roles:
        (d / f"{role}.md").write_text(
            f"# Sam - {role} seat\n\n<!-- role: {role} -->\n\n## Lens\nx\n\n"
            f"## Pushes Back When\ny\n\n## Shadow\nz\n", encoding="utf-8")


def _goal_review(root: Path, goal: str, seats=(("product", "yes", "every unit Fixed", "yes"),)):
    d = root / "sdlc-studio" / ".local"
    d.mkdir(parents=True, exist_ok=True)
    (d / "goal-review.json").write_text(json.dumps({
        "goal": goal, "reviewed_at": "2026-07-22T00:00:00Z",
        "seats": [{"seat": s, "achievable": a, "done_means": dm, "one_increment": oi}
                  for s, a, dm, oi in seats]}), encoding="utf-8")


class GoalConsultTests(unittest.TestCase):
    """US0297/CR0354/D0045: the seats scored WSJF and nothing reviewed what the run was FOR.

    RUN-01KXVYGR is the argument: a Sprint Goal unreachable BY CONSTRUCTION, unnoticed for a
    whole session and closed as partial. D0045 ruled the consult BLOCKING, because an advisory
    goal review would have been skipped exactly as the advisory WSJF consult was."""

    def _plan(self, root, *extra):
        mod = _load()
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), \
                unittest.mock.patch.object(sys, "stdin", io.StringIO("")):
            rc = mod.main(["plan", "--bugs", "Open", "--no-fetch", "--root", str(root), *extra])
        return rc, out.getvalue(), err.getvalue()

    def test_plan_records_a_seat_verdict_on_the_sprint_goal(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1)
            _seats(root)
            _goal_review(root, "empty the sized backlog",
                         seats=(("product", "yes", "every bug Fixed and signed off", "yes"),))
            rc, out, err = self._plan(root, "--format", "json", "--order", "wsjf",
                                      "--sprint-goal", "empty the sized backlog")
            self.assertEqual(rc, 0, err)
            data = json.loads(out)
            gr = data["goal_review"]
            self.assertTrue(gr["reviewed"])
            seat = gr["seats"][0]
            self.assertEqual(seat["seat"], "product")
            self.assertEqual(seat["achievable"], "yes")
            self.assertEqual(seat["done_means"], "every bug Fixed and signed off")
            self.assertEqual(seat["one_increment"], "yes")
            # alongside the WSJF components, never in place of them
            self.assertIsNotNone(data.get("seat_provenance"))

    def test_goal_review_is_stamped_on_the_run_state_at_plan_time(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1)
            _seats(root)
            _goal_review(root, "empty the sized backlog")
            rc, out, err = self._plan(root, "--write", "--sprint-goal",
                                      "empty the sized backlog")
            self.assertEqual(rc, 0, err)
            state = json.loads((root / "sdlc-studio" / ".local" / "run-state.json").read_text())
            self.assertEqual(state["sprint_goal"], "empty the sized backlog")
            gr = state["sprint_goal_review"]
            self.assertTrue(gr["reviewed"])
            self.assertEqual(gr["reviewed_at"], "2026-07-22T00:00:00Z")
            self.assertEqual([s["seat"] for s in gr["seats"]], ["product"])

    def test_plan_refuses_a_sprint_goal_no_seat_has_reviewed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1)
            _seats(root)
            rc, out, err = self._plan(root, "--write", "--sprint-goal", "empty the backlog")
            self.assertEqual(rc, 2)
            self.assertFalse((root / "sdlc-studio" / ".local" / "sprint-plan.json").exists())
            self.assertFalse((root / "sdlc-studio" / ".local" / "run-state.json").exists())
            self.assertIn("goal-review record", err)

    def test_a_review_of_a_different_goal_does_not_count_as_a_review(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1)
            _seats(root)
            _goal_review(root, "some other goal entirely")
            rc, out, err = self._plan(root, "--write", "--sprint-goal", "empty the backlog")
            self.assertEqual(rc, 2)
            self.assertIn("a different goal", err)

    def test_a_verdict_missing_an_answer_is_not_a_review(self) -> None:
        """Achievability without a definition of done is an opinion about an unstated target:
        the close would then judge the increment against a definition nobody wrote down."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1)
            _seats(root)
            (root / "sdlc-studio" / ".local").mkdir(parents=True, exist_ok=True)
            (root / "sdlc-studio" / ".local" / "goal-review.json").write_text(json.dumps({
                "goal": "empty the backlog", "reviewed_at": "2026-07-22T00:00:00Z",
                "seats": [{"seat": "product", "achievable": "yes", "one_increment": "yes"}]}),
                encoding="utf-8")
            status = _load().goal_review_status(root, "empty the backlog")
            self.assertFalse(status["reviewed"])
            rc, out, err = self._plan(root, "--write", "--sprint-goal", "empty the backlog")
            self.assertEqual(rc, 2)

    def test_skip_personas_records_the_goal_as_unreviewed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1)
            _seats(root)
            rc, out, err = self._plan(root, "--write", "--skip-personas",
                                      "--sprint-goal", "empty the backlog")
            self.assertEqual(rc, 0, err)
            self.assertTrue((root / "sdlc-studio" / ".local" / "sprint-plan.json").exists())
            state = json.loads((root / "sdlc-studio" / ".local" / "run-state.json").read_text())
            self.assertFalse(state["sprint_goal_review"]["reviewed"])
            self.assertEqual(state["sprint_goal_review"]["skipped"], "--skip-personas")
            self.assertIn("went UNREVIEWED", out)

    def test_a_project_with_no_seats_of_its_own_is_not_blocked(self) -> None:
        """The gate demands a review from seats that EXIST. Refusing every plan on a project
        that never adopted personas would block on a ceremony nobody there can perform."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1)
            rc, out, err = self._plan(root, "--write", "--sprint-goal", "empty the backlog")
            self.assertEqual(rc, 0, err)
            state = json.loads((root / "sdlc-studio" / ".local" / "run-state.json").read_text())
            self.assertFalse(state["sprint_goal_review"]["reviewed"])
            self.assertIn("no review seats", out + err)

    def test_the_record_command_writes_what_the_plan_reads(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            out = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
                rc = mod.main(["goal-review", "record", "--root", str(root),
                               "--goal", "empty the backlog",
                               "--seat", "product|yes|every bug Fixed|yes"])
            self.assertEqual(rc, 0, out.getvalue())
            status = mod.goal_review_status(root, "empty the backlog")
            self.assertTrue(status["reviewed"])
            self.assertEqual(status["seats"][0]["done_means"], "every bug Fixed")


class NegativeGoalVerdictHasAnEffectTests(unittest.TestCase):
    """BG0262: a seat that judged the Sprint Goal NOT achievable used to discharge the plan gate
    exactly as one that said it was - the verdict's CONTENT was never read. Now a negative verdict
    refuses the plan unless an override with a reason is recorded."""

    def _plan(self, root, *extra):
        mod = _load()
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), \
                unittest.mock.patch.object(sys, "stdin", io.StringIO("")):
            rc = mod.main(["plan", "--bugs", "Open", "--no-fetch", "--root", str(root), *extra])
        return rc, out.getvalue(), err.getvalue()

    def test_the_verdict_vocabulary_reads_no_from_a_reasoned_answer(self) -> None:
        sp = _load()
        self.assertEqual(sp.verdict_polarity("no - not at the stated appetite"), "no")
        self.assertEqual(sp.verdict_polarity("yes"), "yes")
        self.assertEqual(sp.verdict_polarity("never"), "no")
        self.assertEqual(sp.verdict_polarity("maybe later"), "unclear")

    def test_a_negative_verdict_refuses_the_plan(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1)
            _seats(root)
            _goal_review(root, "empty the sized backlog",
                         seats=(("engineering", "no", "every bug Fixed", "no"),))
            rc, out, err = self._plan(root, "--write", "--sprint-goal", "empty the sized backlog")
            self.assertEqual(rc, 2, "a seat saying NOT achievable must stop the plan")
            self.assertFalse((root / "sdlc-studio" / ".local" / "run-state.json").exists())
            self.assertFalse((root / "sdlc-studio" / ".local" / "sprint-plan.json").exists())
            self.assertIn("NOT achievable", err)

    def test_a_positive_verdict_still_proceeds(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1)
            _seats(root)
            _goal_review(root, "empty the sized backlog")   # default seat: achievable=yes
            rc, out, err = self._plan(root, "--write", "--sprint-goal", "empty the sized backlog")
            self.assertEqual(rc, 0, err)
            self.assertTrue((root / "sdlc-studio" / ".local" / "run-state.json").exists())

    def test_an_override_lets_the_plan_proceed_and_records_the_reason(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1)
            _seats(root)
            _goal_review(root, "empty the sized backlog",
                         seats=(("engineering", "no", "every bug Fixed", "yes"),))
            rc, out, err = self._plan(root, "--write", "--sprint-goal", "empty the sized backlog",
                                      "--override-goal-review", "accepted the appetite risk")
            self.assertEqual(rc, 0, err)
            state = json.loads((root / "sdlc-studio" / ".local" / "run-state.json").read_text())
            ovr = state["goal_review_override"]
            self.assertEqual(ovr["reason"], "accepted the appetite risk")
            self.assertEqual(ovr["objections"][0]["seat"], "engineering")


class GoalReviewKeepsItsRoundsTests(unittest.TestCase):
    """BG0263: the goal review had ONE record - a second review overwrote the first, so a goal
    rewritten in answer to a REJECT read as a smooth first-time approval. Rounds now accumulate,
    the gate reads the latest, and the round count reaches the run state."""

    def _record(self, root, goal, seat):
        mod = _load()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return mod.main(["goal-review", "record", "--root", str(root),
                             "--goal", goal, "--seat", seat])

    def _plan(self, root, *extra):
        mod = _load()
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), \
                unittest.mock.patch.object(sys, "stdin", io.StringIO("")):
            rc = mod.main(["plan", "--bugs", "Open", "--no-fetch", "--root", str(root), *extra])
        return rc, out.getvalue(), err.getvalue()

    def test_rounds_accumulate_rather_than_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            self._record(root, "goal A", "engineering|no|every bug Fixed|no")
            self._record(root, "goal B", "engineering|yes|every bug Fixed|yes")
            rounds = sp.goal_review_rounds(sp.goal_review(root))
            self.assertEqual(len(rounds), 2, "the rejection of goal A must survive the rewrite")
            self.assertEqual(rounds[0]["goal"], "goal A")
            self.assertEqual(rounds[0]["seats"][0]["achievable"], "no")
            self.assertEqual(rounds[1]["goal"], "goal B")

    def test_the_gate_reads_the_latest_round(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1)
            _seats(root)
            self._record(root, "goal A", "engineering|no|every bug Fixed|no")
            self._record(root, "goal B", "engineering|yes|every bug Fixed|yes")
            # the LATEST round (goal B) discharges the gate; the earlier goal A no longer matches
            rc_b, _, _ = self._plan(root, "--write", "--sprint-goal", "goal B")
            self.assertEqual(rc_b, 0)
            rc_a, _, err_a = self._plan(root, "--write", "--sprint-goal", "goal A")
            self.assertEqual(rc_a, 2, "a goal that is not the latest round no longer discharges")
            self.assertIn("different goal", err_a)

    def test_the_round_count_reaches_the_run_state(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1)
            _seats(root)
            self._record(root, "goal A", "engineering|no|every bug Fixed|no")
            self._record(root, "the final goal", "engineering|yes|every bug Fixed|yes")
            rc, out, err = self._plan(root, "--write", "--sprint-goal", "the final goal")
            self.assertEqual(rc, 0, err)
            state = json.loads((root / "sdlc-studio" / ".local" / "run-state.json").read_text())
            self.assertEqual(state["sprint_goal_review"]["rounds"], 2,
                             "the close must be able to say the goal took two rounds")


class ReachableEndStateTests(unittest.TestCase):
    """US0298/CR0354: RUN-01KXVYGR's goal, 'the sized delivery backlog is empty', could not
    be reached BY CONSTRUCTION - with `review.two_role_after` set, every unit past the cutoff
    needs a reviewer-of-record sign-off the authoring session is refused, so the furthest
    reachable state was Review. Nobody noticed until the close."""

    def _config(self, root: Path, body: str) -> None:
        (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
        (root / "sdlc-studio" / ".config.yaml").write_text(body, encoding="utf-8")

    def test_plan_names_the_reachable_end_state_under_the_two_role_gate(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._config(root, "review:\n  two_role_after: 192\n")
            _pointed_story(root, 200, 3)
            _pointed_story(root, 201, 3)
            data = _load().build_plan(root, "story", "Ready", skip_personas=True)
            res = data["reachable_end_state"]
            self.assertEqual(res["state"], "Review")
            self.assertIn("two_role_after", res["reason"])
            self.assertEqual(res["units"], ["US0200", "US0201"])
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = _load().main(["plan", "--stories", "Ready", "--root", str(root),
                                   "--no-fetch", "--skip-personas"])
            self.assertEqual(rc, 0)
            self.assertIn("reachable end state: Review", out.getvalue() + err.getvalue())

    def test_a_batch_the_two_role_gate_does_not_reach_can_still_reach_done(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._config(root, "review:\n  two_role_after: 192\n")
            _pointed_story(root, 10, 3)          # below the cutoff
            data = _load().build_plan(root, "story", "Ready", skip_personas=True)
            self.assertEqual(data["reachable_end_state"]["state"], "Done")
            self.assertIsNone(data["reachable_end_state"]["reason"])
            self.assertEqual(data["reachable_end_state"]["units"], [])
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)                       # ...and with no cutoff configured at all
            _pointed_story(root, 200, 3)
            data = _load().build_plan(root, "story", "Ready", skip_personas=True)
            self.assertEqual(data["reachable_end_state"]["state"], "Done")
            self.assertIsNone(data["reachable_end_state"]["reason"])

    def test_a_project_that_stood_the_two_role_rule_down_still_reaches_done(self) -> None:
        """The cap is derived from the SAME fields the conformance gate reads, including the
        story Definition of Done's `review.two-role` stand-down. A cap that disagreed with the
        gate it claims to derive would be worse than no cap at all."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._config(root, "review:\n  two_role_after: 192\n")
            (root / "sdlc-studio" / "definition-of-done.md").write_text(
                "# DoD\n\n## Story\n\n- verified [check: verify.acs]\n", encoding="utf-8")
            _pointed_story(root, 200, 3)
            data = _load().build_plan(root, "story", "Ready", skip_personas=True)
            self.assertEqual(data["reachable_end_state"]["state"], "Done")
            self.assertIsNone(data["reachable_end_state"]["reason"])

    def test_the_reachable_end_state_is_recorded_on_the_run_state(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._config(root, "review:\n  two_role_after: 192\n")
            _pointed_story(root, 200, 3)
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), \
                    unittest.mock.patch.object(sys, "stdin", io.StringIO("")):
                rc = _load().main(["plan", "--stories", "Ready", "--root", str(root),
                                   "--no-fetch", "--skip-personas", "--write",
                                   "--sprint-goal", "every story Done"])
            self.assertEqual(rc, 0, err.getvalue())
            state = json.loads((root / "sdlc-studio" / ".local" / "run-state.json").read_text())
            res = state["reachable_end_state"]
            self.assertEqual(res["state"], "Review")
            self.assertIn("two_role_after", res["reason"])
            self.assertEqual(res["units"], ["US0200"])
            self.assertEqual(state["sprint_goal"], "every story Done")


class GoalVerdictTests(unittest.TestCase):
    """US0183: the closing review judges the increment against the recorded goal."""

    def _open_run_with_goal(self, root, goal="make it honest"):
        mod = _load()
        out, err = io.StringIO(), io.StringIO()
        _bug(root, 1)
        args = ["plan", "--bugs", "Open", "--no-fetch", "--write", "--root", str(root)]
        if goal is not None:
            args += ["--sprint-goal", goal]
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), \
                unittest.mock.patch.object(sys, "stdin", io.StringIO("")):
            rc = mod.main(args)
        assert rc == 0, err.getvalue()
        return mod

    def test_goal_verdict_recorded_on_run_state(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = self._open_run_with_goal(root)
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = mod.main(["goal-verdict", "--verdict", "achieved",
                               "--note", "shipped the honest path", "--root", str(root)])
            self.assertEqual(rc, 0)
            state = json.loads((root / "sdlc-studio" / ".local" / "run-state.json").read_text())
            # the round count is DERIVED from the ledger and stamped on the record (BG0261)
            self.assertEqual(state["sprint_goal_verdict"],
                             {"verdict": "achieved", "note": "shipped the honest path",
                              "rounds": 0})

    def test_goal_verdict_refused_when_no_goal_recorded(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = self._open_run_with_goal(root, goal=None)
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = mod.main(["goal-verdict", "--verdict", "achieved",
                               "--note", "x", "--root", str(root)])
            self.assertNotEqual(rc, 0)
            self.assertIn("no sprint goal", err.getvalue().lower())

    def test_goal_verdict_rejects_unknown_verdict(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = self._open_run_with_goal(root)
            with self.assertRaises(SystemExit), \
                    contextlib.redirect_stderr(io.StringIO()):
                mod.main(["goal-verdict", "--verdict", "smashed-it", "--root", str(root)])


_REPORT_RETRO = """# RETRO-9100: a sprint

> **Batch:** US0001, US0002
> **Date:** 2026-07-17

## Delivered

- US0001 - shipped

## Lessons

- a real lesson worth keeping for next time
"""


def _report_fixture(root: Path) -> None:
    """A retro the report composer can actually compose from: batch, date, and the
    Done+pointed stories the delivered-points figure is read off."""
    (root / "sdlc-studio" / "retros").mkdir(parents=True, exist_ok=True)
    (root / "sdlc-studio" / "retros" / "RETRO9100-a-sprint.md").write_text(
        _REPORT_RETRO, encoding="utf-8")
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    for sid, pts in (("US0001", 3), ("US0002", 5)):
        (d / f"{sid}-s.md").write_text(
            f"# {sid}: s\n\n> **Status:** Done\n> **Points:** {pts}\n", encoding="utf-8")


class SprintReportRouteTests(unittest.TestCase):
    """US0223: `sprint report` is the command surface over sprint_report.py show - same
    output, every flag threaded, the composer's exit code returned unchanged."""

    def _run(self, mod, argv) -> tuple[int, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = mod.main(argv)
        return rc, out.getvalue()

    def test_route_output_matches_the_composer(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _report_fixture(root)
            mod = _load()
            import sprint_report
            rc_route, via_route = self._run(mod, ["report", "--id", "RETRO9100",
                                                  "--root", str(root)])
            out = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                rc_direct = sprint_report.main(["--root", str(root), "show", "--id", "RETRO9100"])
            self.assertEqual(rc_route, 0)
            self.assertEqual(rc_route, rc_direct)
            self.assertIn("Sprint report - RETRO9100", via_route)   # it really composed a page
            self.assertEqual(via_route, out.getvalue())

    def test_every_flag_is_threaded_to_the_composer(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _report_fixture(root)
            mod = _load()
            rc, out = self._run(mod, ["report", "--id", "RETRO9100", "--tokens", "200000",
                                      "--elapsed-hours", "2", "--format", "json",
                                      "--root", str(root)])
            self.assertEqual(rc, 0)
            rep = json.loads(out)                                    # --format json honoured
            self.assertEqual(rep["velocity"]["points_per_elapsed_hour"], 4.0)  # 8pts / 2h
            self.assertEqual(rep["sprint_actual_tokens"], 200000)             # --tokens
            self.assertEqual(rep["velocity"]["sprint_tokens_per_point"], 25000)

    def test_composer_exit_code_is_returned_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _report_fixture(root)
            mod = _load()
            import sprint_report
            rc_route, out = self._run(mod, ["report", "--id", "RETRO9999", "--root", str(root)])
            with contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()):
                rc_direct = sprint_report.main(["--root", str(root), "show", "--id", "RETRO9999"])
            self.assertEqual(rc_direct, 1, "fixture guard: the composer must fail on a missing retro")
            self.assertEqual(rc_route, rc_direct)   # not swallowed, not remapped to 0
            self.assertIn("unavailable", out)


def _close_state(root: Path, **over) -> dict:
    """A legal run-state for close tests, written directly (the plan path is covered
    elsewhere; close reads the object, not the ceremony that made it)."""
    state = {
        "schema": 1, "run_id": "RUN-TEST0001", "started_at": "2026-07-16T00:00:00Z",
        "ended_at": None, "outcome": "running", "goal": "done",
        "batch": ["US0101"], "plan": "sdlc-studio/.local/sprint-plan.json",
        "handoff": None, "appetite": {"minutes": 240.0, "units": 8},
        "sprint_goal": "make the close honest",
        "sprint_goal_verdict": {"verdict": "achieved", "note": "chain ran"},
        "token_forecast": 50000,
    }
    state.update(over)
    p = root / "sdlc-studio" / ".local" / "run-state.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state), encoding="utf-8")
    return state


def _close_story(root: Path) -> None:
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    (d / "US0101-widget.md").write_text(
        "# US0101: widget frobnicates\n\n> **Status:** Review\n> **Points:** 5\n"
        "> **Epic:** EP0001\n\n## Acceptance Criteria\n\n### AC1: works\n"
        "- **Verify:** shell echo ok\n", encoding="utf-8")


def _close_retro(root: Path, rid: str = "RETRO0001", with_index: bool = True,
                 batch: str = "") -> None:
    """A retro file (and, by default, its index row) so a `close --retro <rid>` resolves it.
    With `with_index=False` the row is omitted, exercising the close's index-row self-heal.
    `batch` adds the Batch front-matter the report composer reads its units off."""
    d = root / "sdlc-studio" / "retros"
    d.mkdir(parents=True, exist_ok=True)
    stem = f"{rid}-widget-sprint"
    batch_line = f"> **Batch:** {batch}\n" if batch else ""
    (d / f"{stem}.md").write_text(
        f"# {rid[:5]}-{rid[5:]}: widget sprint\n\n> **Date:** 2026-07-16\n{batch_line}\n"
        "## Delivered\n\n- US0101 - shipped\n\n## Lessons\n\n- learned a thing\n",
        encoding="utf-8")
    if with_index:
        disp = f"{rid[:5]}-{rid[5:]}"
        (d / "_index.md").write_text(
            "# Retro Registry\n\n**Last Updated:** 2026-07-16\n\n"
            "| ID | Title | Date |\n| --- | --- | --- |\n"
            f"| [{disp}]({stem}.md) | widget sprint | 2026-07-16 |\n", encoding="utf-8")


_CLOSE_STEP_NAMES = ("retro-validate", "retro-extract", "lessons-summary",
                     "gate", "handoff", "reconcile")


def _patch_close_steps(mod, fail_at=None, remedy="fix it", record=None):
    """Patch every chain step to succeed (recording call order), optionally failing
    at one named step. Returns the contextlib.ExitStack the caller must close."""
    import contextlib as _ctx
    stack = _ctx.ExitStack()
    for name in _CLOSE_STEP_NAMES:
        attr = "_close_" + name.replace("-", "_")

        def make(nm):
            def step(*a, **k):
                if record is not None:
                    record.append(nm)
                if nm == fail_at:
                    return False, f"{nm} broke", remedy
                return True, f"{nm} ok", ""
            return step
        stack.enter_context(unittest.mock.patch.object(mod, attr, make(name)))
    return stack


class CloseChainTests(unittest.TestCase):
    """US0198: sprint close runs the chain in order, stops loudly at the first
    failing gate naming the remedy, and a re-run resumes idempotently."""

    def test_runs_steps_in_order_and_stops_at_first_failure(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root)
            _close_story(root)
            _close_retro(root)
            mod = _load()
            calls: list[str] = []
            out, err = io.StringIO(), io.StringIO()
            with _patch_close_steps(mod, fail_at="lessons-summary", remedy="run lessons summary",
                                    record=calls), \
                    contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = mod.main(["close", "--retro", "RETRO0001", "--root", str(root)])
            self.assertNotEqual(rc, 0)
            self.assertEqual(calls, ["retro-validate", "retro-extract", "lessons-summary"])
            self.assertIn("STOPPED", err.getvalue())
            self.assertIn("run lessons summary", err.getvalue())   # the remedy, named

    def test_rerun_after_repair_resumes_and_prints_brief(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root, handoff="HO0001", outcome="goal-reached")
            _close_story(root)
            _close_retro(root)
            mod = _load()
            out, err = io.StringIO(), io.StringIO()
            with _patch_close_steps(mod), \
                    contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = mod.main(["close", "--retro", "RETRO0001", "--root", str(root)])
            self.assertEqual(rc, 0, err.getvalue())
            # the recorded goal-verdict is reused, not re-asked, and the brief prints
            self.assertIn("already judged", out.getvalue().lower())
            self.assertIn("sign-off request", out.getvalue().lower())

    def test_goal_verdict_recorded_via_close_flag(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root, sprint_goal_verdict=None)
            _close_story(root)
            _close_retro(root)
            mod = _load()
            out, err = io.StringIO(), io.StringIO()
            with _patch_close_steps(mod), \
                    contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = mod.main(["close", "--retro", "RETRO0001",
                               "--goal-verdict", "achieved", "--note", "chain ran",
                               "--root", str(root)])
            self.assertEqual(rc, 0, err.getvalue())
            state = json.loads((root / "sdlc-studio" / ".local" / "run-state.json").read_text())
            self.assertEqual(state["sprint_goal_verdict"]["verdict"], "achieved")


class CloseRealChainTests(unittest.TestCase):
    """The chain's steps run REAL sibling modules - no stubs - so a signature or
    wiring break in any of them cannot hide behind patched-out steps."""

    def test_close_refuses_named_but_missing_retro(self) -> None:
        # A close naming a retro that does not exist must refuse clearly with the remedy
        # named (CR0345: a chosen id cannot be minted by the sequential allocator) - never
        # a raw crash, and never reaching the chain.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root)
            _close_story(root)
            mod = _load()
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = mod.main(["close", "--retro", "RETRO9999", "--root", str(root)])
            self.assertNotEqual(rc, 0)
            self.assertIn("not found", err.getvalue())
            self.assertIn("artifact.py new --type retro", err.getvalue())  # the remedy

    def test_derived_outcome_from_partial_verdict_is_stopped(self) -> None:
        # AC3: the handoff outcome derives from the recorded verdict, never a default -
        # a partial goal must not close the run as goal-reached.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root, sprint_goal_verdict={"verdict": "partial", "note": "half"})
            _close_story(root)
            mod = _load()
            # run the REAL _close_handoff against a stubbed handoff module so the
            # derived outcome is observable without a full gate-passing workspace
            import types
            calls: dict = {}

            def fake_main(argv):
                calls["argv"] = argv
                return 0
            with unittest.mock.patch.dict(sys.modules, {"handoff": types.SimpleNamespace(main=fake_main)}):
                ok, detail, _ = mod._close_handoff(root, "RETRO0001",
                                                   json.loads((root / "sdlc-studio" / ".local" /
                                                               "run-state.json").read_text()))
            self.assertTrue(ok)
            i = calls["argv"].index("--outcome")
            self.assertEqual(calls["argv"][i + 1], "stopped")   # partial -> stopped, not goal-reached

    def test_run_cli_handles_string_systemexit(self) -> None:
        mod = _load()

        def exits(argv):
            raise SystemExit("boom")
        rc, out = mod._run_cli(exits, [])
        self.assertEqual(rc, 1)   # a string exit code is a failure, not a crash


class CloseRetroScaffoldTests(unittest.TestCase):
    """CR0345: sprint close scaffolds the retro through the deterministic path so it is never
    hand-authored into a missing index row the reconcile step catches only at the end."""

    def test_scaffolds_and_stops_when_retro_omitted(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root, sprint_goal="ship the widget", batch=["US0101", "US0102"])
            _close_story(root)
            mod = _load()
            out, err = io.StringIO(), io.StringIO()
            # No --retro: close must scaffold one and STOP, never run the chain.
            with _patch_close_steps(mod), \
                    contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = mod.main(["close", "--root", str(root)])
            self.assertNotEqual(rc, 0)                       # stopped, action needed
            self.assertIn("scaffolded", out.getvalue().lower())
            retros = list((root / "sdlc-studio" / "retros").glob("RETRO*-*.md"))
            self.assertEqual(len(retros), 1, "exactly one retro scaffolded")
            body = retros[0].read_text(encoding="utf-8")
            # The index row was created by the deterministic path...
            idx = (root / "sdlc-studio" / "retros" / "_index.md").read_text(encoding="utf-8")
            self.assertIn(retros[0].stem.split("-")[0], idx.replace("-", ""))
            # ...and Batch/Goal were pre-filled from run state, not left as placeholders.
            self.assertIn("US0101, US0102", body)
            self.assertIn("ship the widget", body)
            self.assertNotIn("{{batch}}", body)
            self.assertNotIn("{{goal}}", body)

    def test_a_goal_derived_h1_carries_no_trailing_punctuation(self) -> None:
        """BG0179's defect in a second generator, and the reason to share one helper.

        A Sprint Goal is a sentence and ends in a full stop, so an H1 built from it does
        too, and markdownlint MD026 blocks the very commit carrying the retro. `handoff`
        was fixed for exactly this and the retro scaffold was not, so the close-paperwork
        commit was blocked at a real close and the heading corrected by hand. Both paths
        now strip through one helper rather than each keeping its own idea of a heading.
        """
        goals = {
            "full stop": "The review loop is bounded and the close tells the truth.",
            "question mark": "Can the close tell the truth?",
            "ellipsis": "Bound the loop...",
            "trailing spaces": "Bound the loop.   ",
        }
        for name, goal in goals.items():
            with self.subTest(goal=name), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _close_state(root, sprint_goal=goal, batch=["US0101"])
                _close_story(root)
                mod = _load()
                out, err = io.StringIO(), io.StringIO()
                with _patch_close_steps(mod), \
                        contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                    mod.main(["close", "--root", str(root)])
                retros = list((root / "sdlc-studio" / "retros").glob("RETRO*-*.md"))
                h1 = retros[0].read_text(encoding="utf-8").splitlines()[0]
                self.assertTrue(h1.startswith("# "), f"not an H1: {h1!r}")
                self.assertFalse(h1.rstrip().endswith((".", ",", ";", ":", "!", "?", "…")),
                                 f"H1 ends in punctuation (MD026): {h1!r}")

    def test_bare_close_rerun_reuses_scaffold_not_a_second_retro(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root, sprint_goal="ship it")
            _close_story(root)
            mod = _load()
            for _ in range(2):                               # two bare closes in a row
                out, err = io.StringIO(), io.StringIO()
                with _patch_close_steps(mod), \
                        contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                    rc = mod.main(["close", "--root", str(root)])
                self.assertNotEqual(rc, 0)
            retros = list((root / "sdlc-studio" / "retros").glob("RETRO*-*.md"))
            self.assertEqual(len(retros), 1, "the re-run reused the scaffold, minted no duplicate")
            state = json.loads((root / "sdlc-studio" / ".local" / "run-state.json").read_text())
            self.assertTrue(state.get("scaffolded_retro"), "scaffolded id stashed on run state")

    def test_goal_verdict_on_scaffold_call_is_recorded_not_dropped(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root, sprint_goal="ship it", sprint_goal_verdict=None)
            _close_story(root)
            mod = _load()
            out, err = io.StringIO(), io.StringIO()
            with _patch_close_steps(mod), \
                    contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = mod.main(["close", "--goal-verdict", "achieved", "--note", "done",
                               "--root", str(root)])
            self.assertNotEqual(rc, 0)                        # still scaffolds + stops
            state = json.loads((root / "sdlc-studio" / ".local" / "run-state.json").read_text())
            self.assertEqual(state["sprint_goal_verdict"]["verdict"], "achieved")  # not dropped

    def test_proceeds_when_retro_exists(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root)
            _close_story(root)
            _close_retro(root)                               # file + index row present
            mod = _load()
            calls: list[str] = []
            out, err = io.StringIO(), io.StringIO()
            with _patch_close_steps(mod, record=calls), \
                    contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = mod.main(["close", "--retro", "RETRO0001", "--root", str(root)])
            self.assertEqual(rc, 0, err.getvalue())
            self.assertEqual(calls[0], "retro-validate")     # reached and ran the chain
            self.assertNotIn("scaffolded", out.getvalue().lower())

    def test_heals_missing_index_row_for_existing_retro(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root)
            _close_story(root)
            _close_retro(root, with_index=False)             # retro file, NO index row
            mod = _load()
            out, err = io.StringIO(), io.StringIO()
            with _patch_close_steps(mod), \
                    contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = mod.main(["close", "--retro", "RETRO0001", "--root", str(root)])
            self.assertEqual(rc, 0, err.getvalue())
            idx = root / "sdlc-studio" / "retros" / "_index.md"
            self.assertTrue(idx.is_file(), "index bootstrapped by the self-heal")
            self.assertIn("RETRO", idx.read_text(encoding="utf-8"))   # the row was added


class _CloseReportBase(unittest.TestCase):
    """Shared fixture for the close's report step: a run whose retro names the batch, so the
    report composes a real page rather than an empty one."""

    def _fixture(self, root: Path) -> None:
        _close_state(root, handoff="HO0001", outcome="goal-reached")
        _close_story(root)
        _close_retro(root, batch="US0101")

    def _close(self, mod, root: Path) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with _patch_close_steps(mod), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = mod.main(["close", "--retro", "RETRO0001", "--root", str(root)])
        return rc, out.getvalue(), err.getvalue()


class CloseDrawsReportTests(_CloseReportBase):
    """US0224: the close draws the sprint report, before the sign-off brief, and a report
    that cannot be composed is noted rather than allowed to fail the close."""

    def test_report_drawn_before_the_signoff_brief(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._fixture(root)
            mod = _load()
            rc, out, err = self._close(mod, root)
            self.assertEqual(rc, 0, err)
            self.assertIn("Sprint report - RETRO0001", out)
            # Composed from THIS run, not a stub: the unit count comes off the retro's Batch
            # and the goal line off the run state.
            self.assertIn("Delivered: 1 unit(s)", out)
            self.assertIn("Sprint Goal: make the close honest", out)
            brief = out.lower().index("sign-off request")
            self.assertLess(out.index("Sprint report - RETRO0001"), brief)

    def test_uncomposable_report_is_noted_and_the_close_still_passes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._fixture(root)
            mod = _load()
            import sprint_report
            with unittest.mock.patch.object(sprint_report, "report",
                                            side_effect=RuntimeError("composer exploded")):
                rc, out, err = self._close(mod, root)
            self.assertEqual(rc, 0, err)                    # noted, never fatal
            self.assertIn("sprint report not drawn", (out + err).lower())
            self.assertIn("composer exploded", out + err)   # named, not swallowed silently
            self.assertIn("sign-off request", out.lower())  # the brief still prints

    def test_unavailable_report_is_noted_and_the_close_still_passes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._fixture(root)
            mod = _load()
            import sprint_report
            bad = {"ok": False, "id": "RETRO0001", "errors": ["retro not found"]}
            with unittest.mock.patch.object(sprint_report, "report", return_value=bad):
                rc, out, err = self._close(mod, root)
            self.assertEqual(rc, 0, err)
            self.assertIn("unavailable", out + err)
            self.assertIn("sign-off request", out.lower())

    def test_rerun_redraws_the_report_and_writes_nothing(self) -> None:
        # The close is resumable: a second run must draw the page again and add no file -
        # the report step is a read, and a read must not become a write on the re-run.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._fixture(root)
            mod = _load()
            rc1, out1, err1 = self._close(mod, root)
            before = {p.relative_to(root) for p in root.rglob("*") if p.is_file()}
            rc2, out2, err2 = self._close(mod, root)
            after = {p.relative_to(root) for p in root.rglob("*") if p.is_file()}
            self.assertEqual((rc1, rc2), (0, 0), err1 + err2)
            self.assertIn("Sprint report - RETRO0001", out1)
            self.assertIn("Sprint report - RETRO0001", out2)
            self.assertEqual(before, after, "the report step wrote a file on the re-run")


class CloseReportDisabledTests(_CloseReportBase):
    """US0224 AC2: `report.enabled: false` skips the PAGE, never the close."""

    def _disable(self, root: Path) -> None:
        (root / "sdlc-studio" / ".config.yaml").write_text("report:\n  enabled: false\n",
                                                           encoding="utf-8")

    def test_page_omitted_but_chain_and_brief_complete(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._fixture(root)
            self._disable(root)
            mod = _load()
            rc, out, err = self._close(mod, root)
            self.assertEqual(rc, 0, err)
            self.assertNotIn("Sprint report - RETRO0001", out)   # no page
            # The chain still completed. Derived from the module, never a hardcoded index: the
            # old `[6/6]` pinned a step COUNT, so adding a step failed a test about report
            # rendering, which is not what it is meant to guard.
            last = len(mod._CLOSE_CHAIN)
            self.assertIn(f"[{last}/{last}] {mod._CLOSE_CHAIN[-1]}", out)
            self.assertIn("reconcile: ok", out)
            self.assertIn("sign-off request", out.lower())       # the brief still printed

    def test_exit_code_is_the_same_as_with_rendering_on(self) -> None:
        with tempfile.TemporaryDirectory() as on, tempfile.TemporaryDirectory() as off:
            root_on, root_off = Path(on), Path(off)
            self._fixture(root_on)
            self._fixture(root_off)
            self._disable(root_off)
            mod = _load()
            rc_on, out_on, _ = self._close(mod, root_on)
            rc_off, out_off, _ = self._close(mod, root_off)
            self.assertEqual(rc_on, rc_off)
            self.assertIn("Sprint report - RETRO0001", out_on)    # guard: the on-run drew a page
            self.assertNotIn("Sprint report - RETRO0001", out_off)


class CloseBriefTests(unittest.TestCase):
    """US0198: the decision brief is composed from the committed records - deliveries,
    verdict + REJECT history, gate and mutation results, forecast vs measured spend."""

    def _fixture(self, root: Path) -> None:
        _close_state(root)
        _close_story(root)
        _close_retro(root)
        spec = importlib.util.spec_from_file_location("critic", SCRIPT.parent / "critic.py")
        c = importlib.util.module_from_spec(spec)
        sys.modules["critic"] = c
        spec.loader.exec_module(c)
        c.record_verdict(root, "US0101", "reject", reviewer="qa-seat", author="builder",
                         issues="vacuous killing test")
        c.record_verdict(root, "US0101", "approve", reviewer="qa-seat", author="builder")
        ev = root / "sdlc-studio" / "retros" / "evidence"
        ev.mkdir(parents=True, exist_ok=True)
        (ev / "actuals-2026-07.jsonl").write_text(
            json.dumps({"id": "US0101", "type": "story", "tokens": 111000,
                        "model": "m", "project": "p"}) + "\n", encoding="utf-8")

    def test_brief_composed_from_records(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._fixture(root)
            mod = _load()
            out, err = io.StringIO(), io.StringIO()
            with _patch_close_steps(mod), \
                    contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = mod.main(["close", "--retro", "RETRO0001", "--root", str(root)])
            self.assertEqual(rc, 0, err.getvalue())
            text = out.getvalue()
            self.assertIn("widget frobnicates", text)          # delivery title
            self.assertIn("REJECT", text)                      # reject history
            self.assertIn("vacuous killing test", text)
            self.assertIn("50,000", text)                      # forecast
            self.assertIn("111,000", text)                     # measured spend
            self.assertIn("no mutation report", text.lower())  # absent named, not invented
            for path in ("approve", "hold", "delegate"):
                self.assertIn(path, text.lower())

    def test_unmeasured_spend_is_named_not_claimed_as_zero(self) -> None:
        # AC2 honesty: a batch with no telemetry rows must read "not measured, not
        # zero" - never a zero-spend claim dressed as a measurement.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root)
            _close_story(root)   # no telemetry actuals written
            _close_retro(root)
            mod = _load()
            out, err = io.StringIO(), io.StringIO()
            with _patch_close_steps(mod), \
                    contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = mod.main(["close", "--retro", "RETRO0001", "--root", str(root)])
            self.assertEqual(rc, 0, err.getvalue())
            self.assertIn("not measured, not zero", out.getvalue())
            self.assertNotIn("tokens measured across", out.getvalue())

    def test_red_baseline_mutation_report_named_worthless(self) -> None:
        # A report whose baseline is red proves nothing; the brief must say so,
        # never render it as a neutral killed/survived line (closing-critic finding).
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._fixture(root)
            rep = {"generated_at": "x", "git_rev": "abc1234", "baseline": "fail",
                   "summary": {"applied": 25, "killed": 0, "survived": 0, "errors": 25}}
            p = root / "sdlc-studio" / ".local" / "mutation-report.json"
            p.write_text(json.dumps(rep), encoding="utf-8")
            mod = _load()
            out, err = io.StringIO(), io.StringIO()
            with _patch_close_steps(mod), \
                    contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = mod.main(["close", "--retro", "RETRO0001", "--root", str(root)])
            self.assertEqual(rc, 0, err.getvalue())
            self.assertIn("WORTHLESS", out.getvalue())
            self.assertNotIn("0 killed / 0 survived", out.getvalue())

    def test_mutation_errors_and_truncation_surface(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._fixture(root)
            rep = {"generated_at": "x", "git_rev": "abc1234", "baseline": "pass",
                   "summary": {"applied": 25, "killed": 20, "survived": 2,
                               "errors": 3, "truncated": 65}}
            p = root / "sdlc-studio" / ".local" / "mutation-report.json"
            p.write_text(json.dumps(rep), encoding="utf-8")
            mod = _load()
            out, err = io.StringIO(), io.StringIO()
            with _patch_close_steps(mod), \
                    contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = mod.main(["close", "--retro", "RETRO0001", "--root", str(root)])
            self.assertEqual(rc, 0, err.getvalue())
            self.assertIn("3 errored", out.getvalue())
            self.assertIn("65", out.getvalue())   # the truncation, not silent

    def test_brief_includes_mutation_summary_when_report_exists(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._fixture(root)
            rep = {"generated_at": "x", "git_rev": "abc1234",
                   "summary": {"applied": 25, "killed": 21, "survived": 3,
                               "errors": 0, "unviable": 1}}
            p = root / "sdlc-studio" / ".local" / "mutation-report.json"
            p.write_text(json.dumps(rep), encoding="utf-8")
            mod = _load()
            out, err = io.StringIO(), io.StringIO()
            with _patch_close_steps(mod), \
                    contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = mod.main(["close", "--retro", "RETRO0001", "--root", str(root)])
            self.assertEqual(rc, 0, err.getvalue())
            self.assertIn("21", out.getvalue())                # killed
            self.assertIn("survived", out.getvalue().lower())


def _critic_mod():
    spec = importlib.util.spec_from_file_location("critic", SCRIPT.parent / "critic.py")
    c = importlib.util.module_from_spec(spec)
    sys.modules["critic"] = c
    spec.loader.exec_module(c)
    return c


def _signoffable_story(root: Path, verified: bool = True) -> None:
    """A story at Review with an Epic, a Verify line, a verify-report entry (green by default,
    red with `verified=False`) and recorded critic evidence + APPROVE by `builder`, so
    `--apply-signoff` (principal != builder) can sign it and transition it Done."""
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    (d / "US0101-widget.md").write_text(
        "# US0101: widget frobnicates\n\n> **Status:** Review\n> **Points:** 5\n"
        "> **Epic:** EP0001\n\n## Acceptance Criteria\n\n### AC1: works\n"
        "- **Verify:** shell true\n", encoding="utf-8")
    rp = root / "sdlc-studio" / ".local" / "verify-report.json"
    rp.parent.mkdir(parents=True, exist_ok=True)
    entry = {"failed": 0 if verified else 1, "stale": 0,
             "failures": [] if verified else [{"ac": "AC1"}],
             "ac_count": 1, "verified_at": "2099-01-01T00:00:00Z"}
    rp.write_text(json.dumps({"stories": {"US0101-widget": entry}}), encoding="utf-8")
    c = _critic_mod()
    c.record_verdict(root, "US0101", "approve", reviewer="qa-seat", author="builder")
    c.record_evidence(root, "US0101", reviewer="qa-seat", author="builder",
                      findings="probed the frob path; none blocking")


class ApplySignoffTests(unittest.TestCase):
    """US0236: `sprint close --apply-signoff` fans a recorded operator approval into per-unit
    reviewer-of-record sign-offs and Done transitions, refusing without an explicit principal."""

    def test_ApplySignoff_refuses_without_principal(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root)
            _signoffable_story(root)
            _close_retro(root)
            mod = _load()
            out, err = io.StringIO(), io.StringIO()
            with _patch_close_steps(mod), \
                    contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = mod.main(["close", "--retro", "RETRO0001", "--apply-signoff",
                               "--root", str(root)])
            self.assertNotEqual(rc, 0)
            self.assertIn("--principal", err.getvalue())
            c = _critic_mod()
            self.assertIsNone(c.signoff_for(root, "US0101"))       # nothing recorded

    def test_ApplySignoff_resolves_author_from_a_sprint_level_review(self) -> None:
        # US0247 x US0236: a unit covered ONLY by a sprint-level review (no per-unit verdict) must
        # still resolve its author, so `--apply-signoff` works without an explicit --author.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root)
            # a story with a green verify-report but NO per-unit critic verdict/evidence
            dd = root / "sdlc-studio" / "stories"
            dd.mkdir(parents=True, exist_ok=True)
            (dd / "US0101-widget.md").write_text(
                "# US0101: widget frobnicates\n\n> **Status:** Review\n> **Points:** 5\n"
                "> **Epic:** EP0001\n\n## Acceptance Criteria\n\n### AC1: works\n"
                "- **Verify:** shell true\n", encoding="utf-8")
            rp = root / "sdlc-studio" / ".local" / "verify-report.json"
            rp.parent.mkdir(parents=True, exist_ok=True)
            rp.write_text(json.dumps({"stories": {"US0101-widget": {
                "failed": 0, "stale": 0, "failures": [], "ac_count": 1,
                "verified_at": "2099-01-01T00:00:00Z"}}}), encoding="utf-8")
            c = _critic_mod()
            c.record_sprint_review(root, ["US0101"], reviewer="qa-seat", author="build-seat",
                                   verdict="APPROVE", findings="full-diff pass; none blocking")
            _close_retro(root)
            mod = _load()
            rc, out, err = _run_apply_signoff(root, mod, principal="Darren")   # no --author
            self.assertEqual(rc, 0, err)
            text = (dd / "US0101-widget.md").read_text()
            self.assertIn("Status:** Done", text)

    def test_ApplySignoff_records_and_dones(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root)
            _signoffable_story(root)
            _close_retro(root)
            mod = _load()
            out, err = io.StringIO(), io.StringIO()
            with _patch_close_steps(mod), \
                    contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = mod.main(["close", "--retro", "RETRO0001", "--apply-signoff",
                               "--principal", "Darren", "--root", str(root)])
            self.assertEqual(rc, 0, err.getvalue())
            c = _critic_mod()
            so = c.signoff_for(root, "US0101")
            self.assertTrue(c.is_independent_signoff(root, "US0101", so))
            text = (root / "sdlc-studio" / "stories" / "US0101-widget.md").read_text()
            self.assertIn("Status:** Done", text)


class ApplySignoffStopsTests(unittest.TestCase):
    """US0236 AC3: a subagent principal is refused and a red Done gate stops the fan loudly,
    leaving no partial-silent state."""

    def test_ApplySignoffStops_on_subagent_principal(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root)
            _signoffable_story(root)          # qa-seat is a recorded reviewer on US0101
            _close_retro(root)
            mod = _load()
            out, err = io.StringIO(), io.StringIO()
            with _patch_close_steps(mod), \
                    contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = mod.main(["close", "--retro", "RETRO0001", "--apply-signoff",
                               "--principal", "qa-seat", "--root", str(root)])
            self.assertNotEqual(rc, 0)
            self.assertIn("STOPPED", err.getvalue())
            text = (root / "sdlc-studio" / "stories" / "US0101-widget.md").read_text()
            self.assertIn("Status:** Review", text)   # not advanced

    def test_ApplySignoffStops_on_red_done_gate(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root)
            _signoffable_story(root, verified=False)   # AC-verify red -> Done blocked
            _close_retro(root)
            mod = _load()
            out, err = io.StringIO(), io.StringIO()
            with _patch_close_steps(mod), \
                    contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = mod.main(["close", "--retro", "RETRO0001", "--apply-signoff",
                               "--principal", "Darren", "--root", str(root)])
            self.assertNotEqual(rc, 0)
            self.assertIn("STOPPED", err.getvalue())
            text = (root / "sdlc-studio" / "stories" / "US0101-widget.md").read_text()
            self.assertIn("Status:** Review", text)   # Done gate refused; left at Review


def _run_apply_signoff(root, mod, principal="Darren", retro="RETRO0001"):
    out, err = io.StringIO(), io.StringIO()
    argv = ["close"]
    if retro:
        argv += ["--retro", retro]
    argv += ["--apply-signoff", "--principal", principal, "--root", str(root)]
    with _patch_close_steps(mod), \
            contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = mod.main(argv)
    return rc, out.getvalue(), err.getvalue()


class FileAndCloseTests(unittest.TestCase):
    """US0282/US0283 (CR0371): a blocked close gets a bounded exit - file the blockers as
    real artefacts and close honestly with them recorded - never only the fix path, never
    a waiver of a hard correctness gate, and the outstanding set's trend made visible."""

    ADMIN = {"ready": False, "blockers": [
        {"stage": "sign-off", "detail": "US0101: no independent reviewer-of-record sign-off",
         "remedy": "`critic.py signoff ...`"},
        {"stage": "goal-verdict", "detail": "the Sprint Goal is unjudged",
         "remedy": "`sprint.py goal-verdict ...`"},
    ]}
    HARD = {"ready": False, "blockers": [
        {"stage": "gate", "detail": "skill-tests: 3 failing", "remedy": "fix the suite"},
    ]}

    def _fixture(self, d) -> Path:
        root = Path(d)
        _close_state(root)
        _close_retro(root, batch="US0101")
        (root / "sdlc-studio" / "reviews").mkdir(parents=True, exist_ok=True)
        (root / "sdlc-studio" / "reviews" / "LATEST.md").write_text(
            "# Reviews - LATEST (anchor)\n\n## Where the pipeline is\n\nfine.\n",
            encoding="utf-8")
        (root / "sdlc-studio" / "change-requests").mkdir(parents=True, exist_ok=True)
        (root / "sdlc-studio" / "change-requests" / "_index.md").write_text(
            "# Change Requests\n\n| ID | Title | Status |\n| --- | --- | --- |\n",
            encoding="utf-8")
        return root

    def _close(self, mod, root: Path, pre: dict, extra: tuple = ()) -> tuple:
        out, err = io.StringIO(), io.StringIO()
        with unittest.mock.patch.object(mod, "close_preflight", return_value=pre), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = mod.main(["close", "--retro", "RETRO0001", "--root", str(root), *extra])
        return rc, out.getvalue(), err.getvalue()

    def test_blocked_close_offers_file_and_close(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._fixture(d)
            mod = _load()
            rc, out, err = self._close(mod, root, self.ADMIN)
            offer = out + err
            self.assertIn("fix", offer.lower())
            self.assertIn("--file-and-close", offer)   # the bounded second path is NAMED

    def test_file_and_close_records_linked_artefacts_and_outcome(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._fixture(d)
            mod = _load()
            rc, out, err = self._close(mod, root, self.ADMIN, extra=("--file-and-close",))
            self.assertEqual(rc, 0, err)
            crs = list((root / "sdlc-studio" / "change-requests").glob("CR*.md"))
            self.assertEqual(len(crs), 2, "one artefact per blocker")
            body = crs[0].read_text(encoding="utf-8")
            self.assertIn("RUN-TEST0001", body)        # linked to the run
            state = json.loads((root / "sdlc-studio" / ".local" / "run-state.json")
                               .read_text(encoding="utf-8"))
            self.assertEqual(state["outcome"], "closed-outstanding")
            self.assertIn("known outstanding work", out)

    def test_file_and_close_names_deferrals_in_retro_and_anchor(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._fixture(d)
            mod = _load()
            rc, out, err = self._close(mod, root, self.ADMIN, extra=("--file-and-close",))
            self.assertEqual(rc, 0, err)
            retro_text = (root / "sdlc-studio" / "retros" / "RETRO0001-widget-sprint.md")\
                .read_text(encoding="utf-8")
            self.assertIn("Deferred at close", retro_text)
            self.assertIn("sign-off", retro_text)
            anchor = (root / "sdlc-studio" / "reviews" / "LATEST.md").read_text(
                encoding="utf-8")
            self.assertIn("Deferred at close", anchor)
            self.assertIn("CR", anchor)                # the filed ids are named, not implied

    def _set_outcome(self, root, outcome):
        f = root / "sdlc-studio" / ".local" / "run-state.json"
        st = json.loads(f.read_text(encoding="utf-8"))
        st["outcome"] = outcome
        f.write_text(json.dumps(st, indent=2), encoding="utf-8")

    def test_a_run_stopped_mid_flight_can_still_file_and_close(self) -> None:
        """BG0223 - budget-spent and stopped are mid-flight states, not completed closes.

        loop_guard's own recommended flow stamps them, and such a run has filed NOTHING, so
        refusing it as "already closed ... would duplicate the filing" is false on both counts
        and denies the bounded exit to one of its natural customers.
        """
        for outcome in ("budget-spent", "stopped"):
            with tempfile.TemporaryDirectory() as d:
                root = self._fixture(d)
                mod = _load()
                self._set_outcome(root, outcome)
                rc, out, err = self._close(mod, root, self.ADMIN, extra=("--file-and-close",))
                self.assertEqual(rc, 0, f"{outcome}: {err}")
                crs = list((root / "sdlc-studio" / "change-requests").glob("CR*.md"))
                self.assertEqual(len(crs), 2, f"{outcome}: the blockers were not filed")

    def test_a_completed_close_still_refuses_a_second_filing(self) -> None:
        for outcome in ("goal-reached", "closed-outstanding"):
            with tempfile.TemporaryDirectory() as d:
                root = self._fixture(d)
                mod = _load()
                self._set_outcome(root, outcome)
                rc, out, err = self._close(mod, root, self.ADMIN, extra=("--file-and-close",))
                self.assertEqual(rc, 2, f"{outcome} must refuse a second filing")
                self.assertRegex(err, r"(?i)already")

    def test_a_run_that_already_filed_refuses_whatever_its_outcome(self) -> None:
        """The duplication guard is the filed-blockers record, not the outcome string."""
        with tempfile.TemporaryDirectory() as d:
            root = self._fixture(d)
            mod = _load()
            rc, _out, err = self._close(mod, root, self.ADMIN, extra=("--file-and-close",))
            self.assertEqual(rc, 0, err)
            self._set_outcome(root, "stopped")      # mid-flight string, but a filing exists
            rc2, _o2, err2 = self._close(mod, root, self.ADMIN, extra=("--file-and-close",))
            self.assertEqual(rc2, 2)
            self.assertRegex(err2, r"(?i)already filed")

    def test_hard_correctness_gate_refuses_file_and_close(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._fixture(d)
            mod = _load()
            rc, out, err = self._close(mod, root, self.HARD, extra=("--file-and-close",))
            self.assertNotEqual(rc, 0)
            self.assertIn("skill-tests", err)          # the hard gate is named
            self.assertEqual(list((root / "sdlc-studio" / "change-requests").glob("CR*.md")),
                             [], "a red gate is never filed away")
            state = json.loads((root / "sdlc-studio" / ".local" / "run-state.json")
                               .read_text(encoding="utf-8"))
            self.assertNotEqual(state["outcome"], "closed-outstanding")

    def test_file_and_close_refuses_a_rerun_and_duplicates_nothing(self) -> None:
        # round-1 MAJOR: a second invocation filed a duplicate CR set, appended second
        # sections to the retro and anchor, and overwrote deferred_blockers
        with tempfile.TemporaryDirectory() as d:
            root = self._fixture(d)
            mod = _load()
            rc, out, err = self._close(mod, root, self.ADMIN, extra=("--file-and-close",))
            self.assertEqual(rc, 0, err)
            rc2, out2, err2 = self._close(mod, root, self.ADMIN, extra=("--file-and-close",))
            # exactly 2, not merely non-zero: a mutant stubbing the refusal's return to None
            # passed `assertNotEqual(rc, 0)` while the CLI would have exited 0 over REFUSED
            self.assertEqual(rc2, 2, "a closed run's filing must not be repeatable")
            self.assertIn("already", (out2 + err2).lower())
            crs = list((root / "sdlc-studio" / "change-requests").glob("CR*.md"))
            self.assertEqual(len(crs), 2, "no duplicate CR set")
            retro_text = (root / "sdlc-studio" / "retros" / "RETRO0001-widget-sprint.md")\
                .read_text(encoding="utf-8")
            self.assertEqual(retro_text.count("Deferred at close"), 1)
            anchor = (root / "sdlc-studio" / "reviews" / "LATEST.md").read_text(
                encoding="utf-8")
            self.assertEqual(anchor.count("Deferred at close"), 1)

    def test_file_and_close_refuses_a_goal_less_run(self) -> None:
        # round-1 MINOR: the plain close refuses a goal-less run unconditionally, and a CR
        # saying "set one at plan time" is unsatisfiable after the run is closed
        with tempfile.TemporaryDirectory() as d:
            root = self._fixture(d)
            mod = _load()
            pre = {"ready": False, "blockers": [
                {"stage": "sprint-goal", "detail": "no sprint goal recorded on this run",
                 "remedy": "set one at plan time with --sprint-goal"}]}
            rc, out, err = self._close(mod, root, pre, extra=("--file-and-close",))
            self.assertNotEqual(rc, 0)
            self.assertEqual(list((root / "sdlc-studio" / "change-requests").glob("CR*.md")),
                             [])

    def test_close_presents_pending_decisions_at_the_stop(self) -> None:
        # round-1 MINOR: nothing mechanically asked the accumulated decisions at a stop
        with tempfile.TemporaryDirectory() as d:
            root = self._fixture(d)
            _close_state(root, pending_decisions=[{
                "unit": "US0101", "question": "Which auth method should the sync use?",
                "options": [{"label": "oauth", "consequence": "rotates"},
                            {"label": "api-key", "consequence": "standing secret"}],
                "recommend": {"label": "oauth", "reason": "rotation"},
                "deferred_at": "2026-07-20T00:00:00Z", "resolution": None}])
            mod = _load()
            rc, out, err = self._close(mod, root, self.ADMIN)
            self.assertIn("Which auth method should the sync use?", out + err)
            self.assertIn("oauth", out + err)

    def test_reclose_reports_outstanding_set_trend(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._fixture(d)
            mod = _load()
            five = {"ready": False, "blockers": self.ADMIN["blockers"] * 2 + self.HARD["blockers"]}
            self._close(mod, root, five)
            rc, out, err = self._close(mod, root, self.ADMIN)
            self.assertIn("5 -> 2", out + err)
            self.assertIn("shrinking", out + err)
            rc, out, err = self._close(mod, root, five)
            self.assertIn("growing", out + err)


class DeferredOperatorDecisions(unittest.TestCase):
    """US0280/US0281 (CR0369): a unit needing an operator decision is set aside while the
    batch continues; accumulated decisions are asked together at the stop, as structured
    questions - named options with consequences, the recommendation marked with its reason -
    and an autonomous run records and blocks, never silently defaults."""

    def _defer(self, mod, root: Path, unit: str = "US0101", extra: tuple = ()) -> tuple:
        out, err = io.StringIO(), io.StringIO()
        argv = ["decision", "defer", "--unit", unit,
                "--question", "Which auth method should the sync use?",
                "--option", "oauth|tokens rotate themselves; needs an app registration",
                "--option", "api-key|works today; the key sits in config for ever",
                "--recommend", "oauth|rotation removes the standing secret",
                "--root", str(root), *extra]
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = mod.main(argv)
        return rc, out.getvalue(), err.getvalue()

    def _list(self, mod, root: Path) -> str:
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            rc = mod.main(["decision", "list", "--root", str(root)])
        self.assertEqual(rc, 0, out.getvalue())
        return out.getvalue()

    def test_undecidable_unit_is_set_aside_and_batch_continues(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root)
            mod = _load()
            rc, out, err = self._defer(mod, root)
            self.assertEqual(rc, 0, err)
            state = json.loads((root / "sdlc-studio" / ".local" / "run-state.json")
                               .read_text(encoding="utf-8"))
            self.assertEqual([p["unit"] for p in state["pending_decisions"]], ["US0101"])
            self.assertIn("US0101", state["deferred_units"])
            self.assertIsNone(state["pending_decisions"][0]["resolution"])
            self.assertIn("batch continues", out)   # the stop happens later, not here

    def test_accumulated_decisions_are_asked_together(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root)
            mod = _load()
            self._defer(mod, root, unit="US0101")
            self._defer(mod, root, unit="US0102")
            out = self._list(mod, root)   # ONE invocation carries every pending decision
            self.assertIn("2", out.splitlines()[0])
            self.assertIn("US0101", out)
            self.assertIn("US0102", out)

    def test_operator_question_has_named_options_and_consequences(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root)
            mod = _load()
            self._defer(mod, root)
            out = self._list(mod, root)
            self.assertIn("Which auth method should the sync use?", out)
            self.assertIn("oauth", out)
            self.assertIn("api-key", out)
            self.assertIn("tokens rotate themselves", out)
            self.assertIn("the key sits in config for ever", out)

    def test_recommendation_is_marked_with_reason(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root)
            mod = _load()
            self._defer(mod, root)
            out = self._list(mod, root)
            marked = [ln for ln in out.splitlines() if "RECOMMENDED" in ln]
            self.assertEqual(len(marked), 1)
            self.assertIn("oauth", marked[0])
            self.assertIn("rotation removes the standing secret", marked[0])

    def test_autonomous_run_records_and_blocks_never_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root)
            _signoffable_story(root)
            (root / "sdlc-studio" / "stories" / "_index.md").write_text(
                "# Stories\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [US0101](US0101-widget.md) | widget frobnicates | Review |\n",
                encoding="utf-8")
            mod = _load()
            rc, out, err = self._defer(mod, root, extra=("--block",))
            self.assertEqual(rc, 0, err)
            story = (root / "sdlc-studio" / "stories" / "US0101-widget.md").read_text(
                encoding="utf-8")
            self.assertIn("Blocked", story)          # recorded and blocked...
            state = json.loads((root / "sdlc-studio" / ".local" / "run-state.json")
                               .read_text(encoding="utf-8"))
            self.assertIsNone(state["pending_decisions"][0]["resolution"])  # ...never answered

    def test_resolve_records_the_choice_and_empties_the_queue(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root)
            mod = _load()
            self._defer(mod, root)
            out = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                rc = mod.main(["decision", "resolve", "--index", "1", "--choice", "oauth",
                               "--note", "registration cost accepted", "--root", str(root)])
            self.assertEqual(rc, 0, out.getvalue())
            state = json.loads((root / "sdlc-studio" / ".local" / "run-state.json")
                               .read_text(encoding="utf-8"))
            self.assertEqual(state["pending_decisions"], [])
            self.assertEqual(state["resolved_decisions"][0]["resolution"]["choice"], "oauth")

    def test_decision_refuses_cleanly_on_a_corrupt_run_state(self) -> None:
        # round-1 MINOR: RunStateError escaped as a traceback where close refuses cleanly
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = root / "sdlc-studio" / ".local" / "run-state.json"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("{corrupt", encoding="utf-8")
            mod = _load()
            for argv in (["decision", "list", "--root", str(root)],
                         ["decision", "defer", "--unit", "US0101", "--question", "q",
                          "--option", "a|x", "--option", "b|y", "--root", str(root)]):
                err = io.StringIO()
                with contextlib.redirect_stdout(io.StringIO()), \
                        contextlib.redirect_stderr(err):
                    rc = mod.main(argv)
                self.assertEqual(rc, 2, argv)
                self.assertIn("run state", err.getvalue().lower())

    def test_defer_refuses_a_freeform_prose_question(self) -> None:
        # fewer than two named options IS the prose failure mode - refused, with the fix named
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root)
            mod = _load()
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                rc = mod.main(["decision", "defer", "--unit", "US0101",
                               "--question", "what should I do?",
                               "--option", "yes|it happens", "--root", str(root)])
            self.assertNotEqual(rc, 0)
            self.assertIn("two", err.getvalue())


def _batch_story(root: Path, num: int, status: str = "Ready", depends: str = "") -> None:
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    dep = f"> **Depends on:** {depends}\n" if depends else ""
    (d / f"US{num:04d}-x.md").write_text(
        f"# US{num:04d}: s\n\n> **Status:** {status}\n> **Priority:** Medium\n{dep}",
        encoding="utf-8")


class UnblockedWorkBlocksTheStopTests(unittest.TestCase):
    """US0299/CR0378: in RUN-01KY03GS one unit needed an operator decision and the whole
    13-unit sprint stopped waiting for it, while four units nothing blocked could have been
    built meanwhile. The mechanism to prevent that already existed and nothing obliged its
    use, so the available-but-optional path was not taken and the expensive one was.

    D0052 bounds the blocked set: only a declared `Depends on:` edge blocks. A shared-file
    cluster is a SEQUENCING constraint, and treating a collision as blockage would let one
    deferred decision stop a whole file cluster - the over-stopping this exists to end."""

    def _fixture(self, root: Path, batch=("US0101", "US0102", "US0103")) -> None:
        _close_state(root, batch=list(batch))
        _batch_story(root, 101)
        _batch_story(root, 102)
        _batch_story(root, 103, depends="US0101")

    def _defer(self, mod, root: Path, unit: str = "US0101") -> tuple:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = mod.main(["decision", "defer", "--unit", unit,
                           "--question", "which auth?",
                           "--option", "a|one consequence", "--option", "b|another",
                           "--root", str(root)])
        return rc, out.getvalue(), err.getvalue()

    def _stop(self, mod, root: Path, *extra: str) -> tuple:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = mod.main(["stop", "--root", str(root), "--reason",
                           "waiting on the auth decision", *extra])
        return rc, out.getvalue(), err.getvalue()

    def test_defer_names_the_units_the_batch_continues_with(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._fixture(root)
            rc, out, err = self._defer(_load(), root)
            self.assertEqual(rc, 0, err)
            self.assertIn("US0102", out)               # named, not merely counted
            self.assertNotIn("US0103", out)            # a declared dependant is blocked too
            self.assertIn("batch continues", out)

    def test_a_stop_with_unblocked_work_remaining_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._fixture(root)
            mod = _load()
            self._defer(mod, root)
            rc, out, err = self._stop(mod, root)
            self.assertNotEqual(rc, 0)
            self.assertIn("US0102", err)
            self.assertIn("sprint decision defer", err)
            state = json.loads((root / "sdlc-studio" / ".local" / "run-state.json").read_text())
            self.assertEqual(state["outcome"], "running")   # the refusal changed nothing
            self.assertIsNone(state.get("stop"))

    def test_a_stop_is_allowed_when_no_unit_can_proceed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._fixture(root)
            mod = _load()
            self._defer(mod, root, unit="US0101")
            self._defer(mod, root, unit="US0102")
            rc, out, err = self._stop(mod, root)
            self.assertEqual(rc, 0, err)
            state = json.loads((root / "sdlc-studio" / ".local" / "run-state.json").read_text())
            self.assertEqual(state["stop"]["cause"], "pending-decision")
            self.assertEqual(state["outcome"], "stopped")

    def test_only_the_deferred_unit_and_its_dependants_are_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._fixture(root)
            mod = _load()
            self._defer(mod, root, unit="US0101")
            blocked = mod.blocked_by_pending(root)
            self.assertEqual(blocked["blocked"], ["US0101", "US0103"])
            self.assertEqual(blocked["unblocked"], ["US0102"])

    def test_a_shared_file_is_not_a_declared_dependency(self) -> None:
        """D0052: a collision is a sequencing constraint, never a reason a unit cannot
        proceed. Treating it as blockage is the over-stopping this change exists to end."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root, batch=["US0101", "US0102"])
            _src(root, "src/shared.py")
            for num in (101, 102):
                (root / "sdlc-studio" / "stories" / f"US{num:04d}-x.md").parent.mkdir(
                    parents=True, exist_ok=True)
                (root / "sdlc-studio" / "stories" / f"US{num:04d}-x.md").write_text(
                    f"# US{num:04d}: s\n\n> **Status:** Ready\n> **Priority:** Medium\n"
                    f"> **Affects:** src/shared.py\n", encoding="utf-8")
            mod = _load()
            self._defer(mod, root, unit="US0101")
            self.assertEqual(mod.blocked_by_pending(root)["unblocked"], ["US0102"])


class StopRecordTests(unittest.TestCase):
    """US0300/CR0378: a stop is expensive and its cost was invisible, so nothing pushed back
    on taking one. A parked run looked exactly like a finished one."""

    def _fixture(self, root: Path) -> None:
        _close_state(root, batch=["US0101", "US0102"])
        _batch_story(root, 101)
        _batch_story(root, 102)

    def _stop(self, mod, root: Path, *extra: str) -> tuple:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = mod.main(["stop", "--root", str(root), "--reason", "operator called it",
                           *extra])
        return rc, out.getvalue(), err.getvalue()

    def test_a_stop_records_its_cause_and_the_units_it_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._fixture(root)
            mod = _load()
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                mod.main(["decision", "defer", "--unit", "US0101", "--question", "q?",
                          "--option", "a|x", "--option", "b|y", "--root", str(root)])
            rc, out, err = self._stop(mod, root, "--force")
            self.assertEqual(rc, 0, err)
            stop = json.loads((root / "sdlc-studio" / ".local" / "run-state.json")
                              .read_text())["stop"]
            self.assertEqual(stop["cause"], "operator")
            self.assertEqual(stop["blocked"], ["US0101"])
            self.assertTrue(stop["stopped_at"])
            self.assertEqual(stop["detail"], "operator called it")

    def test_a_forced_stop_names_the_units_that_could_have_proceeded(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._fixture(root)
            mod = _load()
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                mod.main(["decision", "defer", "--unit", "US0101", "--question", "q?",
                          "--option", "a|x", "--option", "b|y", "--root", str(root)])
            rc, out, err = self._stop(mod, root, "--force")
            self.assertEqual(rc, 0, err)
            blob = out + err
            self.assertIn("US0102", blob)              # named individually...
            self.assertNotIn("1 unit(s) remaining", blob)   # ...never folded into a count
            stop = json.loads((root / "sdlc-studio" / ".local" / "run-state.json")
                              .read_text())["stop"]
            self.assertEqual(stop["could_have_proceeded"], ["US0102"])

    def test_elapsed_marks_and_excludes_the_recorded_idle_gap(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            state = {"started_at": "2026-07-22T00:00:00Z", "ended_at": "2026-07-22T04:00:00Z",
                     "idle_gaps": [{"from": "2026-07-22T01:00:00Z",
                                    "to": "2026-07-22T02:30:00Z", "cause": "pending-decision"}]}
            _close_state(root, **state)
            el = mod.run_elapsed(root)
            self.assertEqual(el["raw_hours"], 4.0)
            self.assertEqual(el["idle_hours"], 1.5)
            self.assertEqual(el["hours"], 2.5)          # the denominator excludes the wait
            self.assertEqual(len(el["gaps"]), 1)
            # ...and the rule lives in ONE place, shared rather than copied (D0052)
            sys.path.insert(0, str(SCRIPT.parent))
            import telemetry
            self.assertEqual(telemetry.idle_hours(state), 1.5)
            self.assertEqual(
                telemetry.elapsed_excluding_idle(
                    state["started_at"], state["ended_at"], state)["hours"], 2.5)

    def test_an_open_gap_is_not_counted_as_idle_time(self) -> None:
        """A gap the run never came back from has no measured length. Extending it to `now`
        would book the wall-clock since as measured idle, which is a different claim."""
        sys.path.insert(0, str(SCRIPT.parent))
        import telemetry
        state = {"idle_gaps": [{"from": "2026-07-22T01:00:00Z", "to": None}]}
        self.assertEqual(telemetry.idle_hours(state), 0.0)
        self.assertEqual(telemetry.idle_gaps(state), [])

    def test_a_wait_that_begins_when_the_run_stops_deducts_nothing(self) -> None:
        """MAJOR, RUN-01KY3MFX review. Driven through the REAL `sprint stop` flow, because the
        AC's verifier hand-wrote a gap INSIDE the window and the system cannot produce one:
        `cmd_stop` opens the gap immediately BEFORE `close_run`, so the gap always begins at
        `ended_at` and closes entirely after the measured window. The deduction then removed
        time the wall clock never contained - two hours of work and a three-hour wait after
        the stop reported ZERO hours, and `retro` publishes that as points per elapsed-hour."""
        sys.path.insert(0, str(SCRIPT.parent))
        import telemetry
        from lib import sdlc_md as md
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root, batch=["US0101", "US0102"],
                         started_at="2026-07-22T00:00:00Z", ended_at=None, outcome="running")
            _batch_story(root, 101)
            _batch_story(root, 102)
            mod = _load()

            def run(argv, at):
                with unittest.mock.patch.object(md, "now_iso8601", return_value=at), \
                        contextlib.redirect_stdout(io.StringIO()), \
                        contextlib.redirect_stderr(io.StringIO()):
                    return mod.main([*argv, "--root", str(root)])

            self.assertEqual(run(["decision", "defer", "--unit", "US0101", "--question", "q?",
                                  "--option", "a|x", "--option", "b|y"],
                                 "2026-07-22T02:00:00Z"), 0)
            # two hours of work, then the operator is asked and the run stops
            self.assertEqual(run(["stop", "--force", "--reason", "waiting"],
                                 "2026-07-22T02:00:00Z"), 0)
            # ...and answers three hours later, which closes the gap
            self.assertEqual(run(["decision", "resolve", "--index", "1", "--choice", "a"],
                                 "2026-07-22T05:00:00Z"), 0)

            state = json.loads((root / "sdlc-studio" / ".local" / "run-state.json").read_text())
            self.assertEqual(state["ended_at"], "2026-07-22T02:00:00Z")
            gap = state["idle_gaps"][0]                 # the wait IS recorded, in full
            self.assertEqual((gap["from"], gap["to"]),
                             ("2026-07-22T02:00:00Z", "2026-07-22T05:00:00Z"))
            self.assertEqual(telemetry.idle_hours(state), 3.0)

            el = mod.run_elapsed(root)
            self.assertEqual(el["raw_hours"], 2.0)
            self.assertEqual(el["hours"], 2.0,
                             "a sprint that worked two hours worked two hours")
            self.assertEqual(el["idle_hours"], 0.0,
                             "the deduction may only remove time the window CONTAINED")
            self.assertEqual(el["recorded_idle_hours"], 3.0,
                             "and the wait itself is still reported, not discarded")

    def test_only_the_part_of_a_wait_inside_the_run_is_deducted(self) -> None:
        """The general rule, stated on a gap that straddles the end: a run open 00:00-02:00
        that waited 01:30-05:00 waited half an hour of its own wall-clock, not three and a
        half. Clamping to the intersection is what makes the arithmetic true for every shape,
        rather than only for the one the fixture happened to hand-write."""
        sys.path.insert(0, str(SCRIPT.parent))
        import telemetry
        state = {"idle_gaps": [{"from": "2026-07-22T01:30:00Z", "to": "2026-07-22T05:00:00Z"}]}
        el = telemetry.elapsed_excluding_idle("2026-07-22T00:00:00Z", "2026-07-22T02:00:00Z",
                                              state)
        self.assertEqual(el["raw_hours"], 2.0)
        self.assertEqual(el["idle_hours"], 0.5)
        self.assertEqual(el["recorded_idle_hours"], 3.5)
        self.assertEqual(el["hours"], 1.5)
        # a gap wholly BEFORE the run is outside it too
        before = {"idle_gaps": [{"from": "2026-07-21T01:00:00Z", "to": "2026-07-21T04:00:00Z"}]}
        self.assertEqual(
            telemetry.elapsed_excluding_idle("2026-07-22T00:00:00Z", "2026-07-22T02:00:00Z",
                                             before)["hours"], 2.0)


class ReachableEndStateBoundaryTests(unittest.TestCase):
    """MINOR, RUN-01KY3MFX review: `reachable_end_state` and the conformance gate both compare
    a unit's id number against `review.two_role_after` with a STRICT `>`, and the docstring
    leans on the two agreeing. Mutating either comparison to `>=` left all 289 tests green,
    because no test ever put a unit ON the cutoff. The boundary unit is the only one the two
    can disagree about."""

    def _batch(self, root: Path, num: int) -> list[dict]:
        _batch_story(root, num)
        return [{"id": f"US{num:04d}",
                 "path": str(root / "sdlc-studio" / "stories" / f"US{num:04d}-x.md")}]

    def _cutoff(self, root: Path, value: int) -> None:
        p = root / "sdlc-studio" / ".config.yaml"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"review:\n  two_role_after: US{value:04d}\n", encoding="utf-8")

    def test_the_unit_ON_the_cutoff_is_not_past_it(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cutoff(root, 192)
            res = _load().reachable_end_state(root, self._batch(root, 192))
            self.assertEqual(res["cutoff"], 192)
            self.assertEqual(res["state"], "Done")
            self.assertEqual(res["units"], [])

    def test_the_next_unit_after_the_cutoff_is_capped(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cutoff(root, 192)
            res = _load().reachable_end_state(root, self._batch(root, 193))
            self.assertEqual(res["cutoff"], 192)
            self.assertEqual(res["state"], "Review")
            self.assertEqual(res["units"], ["US0193"])


class ApplySignoffTailTests(unittest.TestCase):
    """US0237: the apply-signoff tail writes the run's velocity row (so a closed sprint no longer
    needs a forgotten manual `retro accuracy --write`) and runs a final reconcile."""

    def test_ApplySignoffTail_writes_velocity_row(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root, scaffolded_retro="RETRO0001")
            _signoffable_story(root)
            _close_retro(root)
            mod = _load()
            rc, out, err = _run_apply_signoff(root, mod)
            self.assertEqual(rc, 0, err)
            vel = root / "sdlc-studio" / "retros" / "VELOCITY.md"
            self.assertTrue(vel.exists(), "velocity file not written")
            self.assertIn("RETRO0001", vel.read_text())

    def test_interactive_close_captures_token_actuals(self) -> None:
        """US0279 (CR0350): the close captures the harness-tracked token total itself -
        no operator hand-supply - and the velocity row records the actual, so
        estimate-versus-actual closes for interactive runs as it does for runner ones.

        BG0236: what it records is the run's own DELTA from the baseline stamped at
        `open_run`, not the session meter. Here the session already carried 900,000 tokens
        when the run opened, and the row must show the 120,000 this run spent."""
        import os
        import unittest.mock as _mock
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            tdir = root / "transcripts"
            tdir.mkdir()
            src = tdir / "session.jsonl"
            src.write_text(
                json.dumps({"message": {"usage": {"input_tokens": 900_000}}}) + "\n" +
                json.dumps(
                    {"message": {"usage": {"input_tokens": 10_000, "output_tokens": 40_000,
                                           "cache_creation_input_tokens": 70_000,
                                           "cache_read_input_tokens": 5_000_000}}}) + "\n",
                encoding="utf-8")
            _close_state(root, scaffolded_retro="RETRO0001",
                         session_token_baseline={"tokens": 900_000, "source": str(src),
                                                 "at": "2026-07-16T00:00:00Z"})
            _signoffable_story(root)
            _close_retro(root, batch="US0101")
            mod = _load()
            with _mock.patch.dict(os.environ, {"SDLC_STUDIO_TRANSCRIPTS": str(tdir)}):
                rc, out, err = _run_apply_signoff(root, mod)
            self.assertEqual(rc, 0, err)
            self.assertIn("token actual captured", out)
            vel = (root / "sdlc-studio" / "retros" / "VELOCITY.md").read_text(encoding="utf-8")
            self.assertIn("120,000", vel, "the run's own spend is ON the row")
            self.assertNotIn("1,020,000", vel, "and the session meter is not")
            row = [ln for ln in vel.splitlines() if "RETRO0001" in ln][0]
            self.assertIn("| 5 |", row, "the delivered points are on the row beside it")

    def test_ApplySignoffTail_records_velocity_from_the_close_retro_argument(self) -> None:
        """BG0200: a retro scaffolded with `artifact.py new` never sets `scaffolded_retro`.

        That is the documented way to make one, so the tail must fall back to the id the
        close was actually given rather than skip the measurement it owes. Previously the
        whole velocity block was guarded on the run-state field alone, so this close
        printed success having recorded no row and said nothing about it.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root)  # no scaffolded_retro - the artifact.py new path
            _signoffable_story(root)
            _close_retro(root)
            mod = _load()
            rc, out, err = _run_apply_signoff(root, mod)
            self.assertEqual(rc, 0, err)
            vel = root / "sdlc-studio" / "retros" / "VELOCITY.md"
            self.assertTrue(vel.exists(), "velocity row skipped: the close owes this measurement")
            self.assertIn("RETRO0001", vel.read_text())

    def test_ApplySignoffTail_warns_loudly_when_no_retro_id_resolves(self) -> None:
        """With no id from either source the tail must SAY so - silence reads as done.

        Driven against the tail directly: the shipped close cannot reach this state
        (given no `--retro` it scaffolds one and stops before the fan), but the branch
        guards every out-of-band and future caller, and an uncovered silent-skip is the
        defect this bug was.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            state = _close_state(root)
            _signoffable_story(root)
            _close_retro(root)
            mod = _load()
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                mod._apply_signoff_tail(root, state, units=[], retro_arg=None)
            self.assertIn("velocity not recorded", err.getvalue().lower())

    def test_a_completed_close_records_the_outcome_its_verdict_earned(self) -> None:
        """BG0208: the outcome field was written on the failure paths and forgotten here.

        A run that stopped earlier, then completed its whole close chain with a verdict of
        `achieved`, kept `outcome: stopped`. Run state is archived per cycle, so that is the
        PERMANENT record: sprint report, velocity, boundary regeneration and the close-owed
        detector all read the field, and a goal-reached sprint was indistinguishable from an
        abandoned one. `close_run` is documented idempotent and re-stamps, so promoting the
        outcome once the close has actually completed is the intended use, not an override.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            state = _close_state(root, scaffolded_retro="RETRO0001", outcome="stopped",
                                 sprint_goal_verdict={"verdict": "achieved", "note": "n"})
            _signoffable_story(root)
            _close_retro(root)
            (root / "sdlc-studio" / "stories" / "_index.md").write_text(
                "# Stories\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [US0101](US0101-widget.md) | widget frobnicates | Review |\n",
                encoding="utf-8")
            mod = _load()
            with contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()):
                mod._apply_signoff_tail(root, state, units=["US0101"], retro_arg="RETRO0001")
            after = json.loads(
                (root / "sdlc-studio" / ".local" / "run-state.json").read_text(encoding="utf-8"))
            self.assertEqual(after["outcome"], "goal-reached")

    def test_promoting_the_outcome_does_not_move_when_the_run_ended(self) -> None:
        """`close_run` re-stamps `ended_at` to now, and the correction is the OUTCOME only.

        With the close and a later `--apply-signoff` separated in time, re-stamping would
        stretch the archived run's started->ended span, which `retro` reads as elapsed. The
        argument for this fix is that the archive is the permanent record, so the fix must
        not corrupt a different field of it.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            state = _close_state(root, scaffolded_retro="RETRO0001", outcome="stopped",
                                 ended_at="2026-07-19T09:00:00Z",
                                 sprint_goal_verdict={"verdict": "achieved", "note": "n"})
            _signoffable_story(root)
            _close_retro(root)
            (root / "sdlc-studio" / "stories" / "_index.md").write_text(
                "# Stories\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [US0101](US0101-widget.md) | widget frobnicates | Review |\n",
                encoding="utf-8")
            mod = _load()
            with contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()):
                mod._apply_signoff_tail(root, state, units=["US0101"], retro_arg="RETRO0001")
            after = json.loads(
                (root / "sdlc-studio" / ".local" / "run-state.json").read_text(encoding="utf-8"))
            self.assertEqual(after["outcome"], "goal-reached")
            self.assertEqual(after["ended_at"], "2026-07-19T09:00:00Z", "ended_at was moved")

    def test_a_plain_close_also_corrects_a_stale_outcome(self) -> None:
        """The promotion must not be reachable only through `--apply-signoff`.

        `_close_handoff` short-circuits when a handoff already exists AND the outcome is
        terminal - the branch a re-run takes - and that skip covered the outcome as well as
        the artefact. That is exactly how the run this bug was filed from kept `stopped`:
        it had a handoff and a stale terminal outcome, so nothing re-derived it.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            state = _close_state(root, outcome="stopped", handoff="HO0009",
                                 sprint_goal_verdict={"verdict": "achieved", "note": "n"})
            mod = _load()
            with contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()):
                ok, _msg, _ = mod._close_handoff(root, "RETRO0001", state)
            self.assertTrue(ok)
            after = json.loads(
                (root / "sdlc-studio" / ".local" / "run-state.json").read_text(encoding="utf-8"))
            self.assertEqual(after["outcome"], "goal-reached")

    def test_a_close_whose_goal_was_not_achieved_is_not_promoted(self) -> None:
        """The promotion must follow the VERDICT, not the fact that a close ran.

        Otherwise every close reports goal-reached and the field stops carrying
        information - the failure mode this bug is, inverted. There is deliberately no
        outcome value meaning "closed cleanly, goal not met": the vocabulary has four
        terms and inventing a fifth is a schema change, so a non-achieved verdict simply
        leaves the recorded outcome alone.
        """
        for verdict in ("partial", "missed"):
            with self.subTest(verdict=verdict), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                state = _close_state(root, scaffolded_retro="RETRO0001", outcome="stopped",
                                     sprint_goal_verdict={"verdict": verdict, "note": "n"})
                _signoffable_story(root)
                _close_retro(root)
                (root / "sdlc-studio" / "stories" / "_index.md").write_text(
                    "# Stories\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                    "| [US0101](US0101-widget.md) | widget frobnicates | Review |\n",
                    encoding="utf-8")
                mod = _load()
                with contextlib.redirect_stdout(io.StringIO()), \
                        contextlib.redirect_stderr(io.StringIO()):
                    mod._apply_signoff_tail(root, state, units=["US0101"],
                                            retro_arg="RETRO0001")
                after = json.loads((root / "sdlc-studio" / ".local" / "run-state.json")
                                   .read_text(encoding="utf-8"))
                self.assertEqual(after["outcome"], "stopped")

    def test_ApplySignoffTail_final_reconcile_drift_fails(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root, scaffolded_retro="RETRO0001")
            _signoffable_story(root)
            _close_retro(root)
            # A story index that CLAIMS US0101 is Draft is drift once the fan transitions it Done.
            idx = root / "sdlc-studio" / "stories" / "_index.md"
            idx.write_text("# Stories\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                           "| [US0101](US0101-widget.md) | widget frobnicates | Draft |\n"
                           "| [US0102](US0102-ghost.md) | ghost | Draft |\n", encoding="utf-8")
            mod = _load()
            rc, out, err = _run_apply_signoff(root, mod)
            self.assertNotEqual(rc, 0)
            self.assertIn("reconcile", (out + err).lower())


class ApplySignoffIdempotentTests(unittest.TestCase):
    """US0238: a re-run after a mid-cascade stop resumes - already-done+signed units are skipped,
    the velocity row is upserted, and an idempotent re-close records no second terminal telemetry."""

    def test_ApplySignoffIdempotent_rerun_skips_done_units(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root, scaffolded_retro="RETRO0001")
            _signoffable_story(root)
            _close_retro(root)
            mod = _load()
            rc1, out1, err1 = _run_apply_signoff(root, mod)
            self.assertEqual(rc1, 0, err1)
            rc2, out2, err2 = _run_apply_signoff(root, mod)   # same command again
            self.assertEqual(rc2, 0, err2)
            self.assertIn("1 already complete", out2)          # skipped, not re-done
            self.assertIn("0 transitioned Done", out2)

    def test_ApplySignoffIdempotent_velocity_row_not_duplicated(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root, scaffolded_retro="RETRO0001")
            _signoffable_story(root)
            _close_retro(root)
            mod = _load()
            _run_apply_signoff(root, mod)
            _run_apply_signoff(root, mod)
            vel = (root / "sdlc-studio" / "retros" / "VELOCITY.md").read_text()
            self.assertEqual(vel.count("| RETRO0001 |"), 1)    # upserted, not appended twice


class CloseRefusalTests(unittest.TestCase):
    """US0198: absent retro content, an unset goal, or an unjudged goal-verdict are
    refusals with the command to run - never defaults."""

    def test_refuses_absent_run_state(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                rc = mod.main(["close", "--retro", "RETRO0001", "--root", str(root)])
            self.assertNotEqual(rc, 0)
            self.assertIn("sprint plan", err.getvalue())       # the command to run

    def test_refuses_unset_sprint_goal(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root, sprint_goal=None, sprint_goal_verdict=None)
            mod = _load()
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                rc = mod.main(["close", "--retro", "RETRO0001", "--root", str(root)])
            self.assertNotEqual(rc, 0)
            self.assertIn("--sprint-goal", err.getvalue())     # how to set one

    def test_refuses_unjudged_goal_verdict(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root, sprint_goal_verdict=None)
            _close_retro(root)
            mod = _load()
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                rc = mod.main(["close", "--retro", "RETRO0001", "--root", str(root)])
            self.assertNotEqual(rc, 0)
            self.assertIn("goal-verdict", err.getvalue())      # the command to run

    def test_goal_verdict_flag_requires_note(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root, sprint_goal_verdict=None)
            _close_retro(root)
            mod = _load()
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                rc = mod.main(["close", "--retro", "RETRO0001",
                               "--goal-verdict", "achieved", "--root", str(root)])
            self.assertNotEqual(rc, 0)
            self.assertIn("--note", err.getvalue())
class ApplySignoffParentEpicTests(unittest.TestCase):
    """BG0190: the tail derives a parent epic terminal once all its children are.

    The per-unit cascade ticks the epic's breakdown checkbox but never sets the epic's own
    Status, and with `two_backlog.enforce` off (the default) reconcile does not derive it
    either - so a close that transitioned every story Done left the epic at Draft, to be
    moved by hand. US0237's AC2 claimed this worked; its Verify line only covered the
    reconcile-drift half, so the gap passed review (L-0063: a suite is evidence only about
    the cases it runs).
    """

    def _epic(self, root, status="Draft", units=("US0101",)):
        d = root / "sdlc-studio" / "epics"
        d.mkdir(parents=True, exist_ok=True)
        lines = [f"# EP0001: widgets", "", f"> **Status:** {status}", "",
                 "## Story Breakdown", ""]
        lines += [f"- [ ] [{u}: x](../stories/{u}-widget.md)" for u in units]
        (d / "EP0001-widgets.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        (d / "_index.md").write_text(
            "# Epics\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            f"| [EP0001](EP0001-widgets.md) | widgets | {status} |\n", encoding="utf-8")

    def _epic_status(self, root):
        text = (root / "sdlc-studio" / "epics" / "EP0001-widgets.md").read_text(encoding="utf-8")
        return next(line.split("**Status:**")[1].strip()
                    for line in text.splitlines() if "**Status:**" in line)

    def test_parent_epic_derived_done_when_all_children_terminal(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root, scaffolded_retro="RETRO0001")
            _signoffable_story(root)
            _close_retro(root)
            self._epic(root)
            mod = _load()
            rc, out, err = _run_apply_signoff(root, mod)
            self.assertEqual(rc, 0, err)
            self.assertEqual(self._epic_status(root), "Done")

    def test_epic_with_a_live_child_is_not_derived(self) -> None:
        """A half-finished epic must not be swept terminal by its finished sibling."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root, scaffolded_retro="RETRO0001")
            _signoffable_story(root)
            _close_retro(root)
            # a second child that stays live
            (root / "sdlc-studio" / "stories" / "US0102-widget.md").write_text(
                "# US0102: later\n\n> **Status:** Draft\n> **Epic:** EP0001\n", encoding="utf-8")
            self._epic(root, units=("US0101", "US0102"))
            mod = _load()
            _run_apply_signoff(root, mod)
            self.assertNotEqual(self._epic_status(root), "Done")

    def test_epic_with_no_children_is_not_derived(self) -> None:
        """"No children" is not "all children complete"."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root, scaffolded_retro="RETRO0001")
            _signoffable_story(root)
            _close_retro(root)
            self._epic(root, units=())
            mod = _load()
            _run_apply_signoff(root, mod)
            self.assertNotEqual(self._epic_status(root), "Done")

    def test_already_terminal_epic_is_left_alone(self) -> None:
        """Idempotent: a re-run must not re-transition (nor fail on) a finished epic."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root, scaffolded_retro="RETRO0001")
            _signoffable_story(root)
            _close_retro(root)
            self._epic(root, status="Done")
            mod = _load()
            rc, out, err = _run_apply_signoff(root, mod)
            self.assertEqual(rc, 0, err)
            self.assertEqual(self._epic_status(root), "Done")


class ApplySignoffOverSweepTests(unittest.TestCase):
    """BG0190 repair: deriving completion is a CLAIM, made only on complete evidence.

    The first implementation evaluated `all(terminal)` over the units
    `reconcile._breakdown_units` could RESOLVE - and that helper silently skips a breakdown
    id with no backing file, and a unit file with no Status. An epic decomposed up front
    whose stories are written incrementally (the ordinary `epic decompose` -> `story create`
    flow) was therefore marked Done off its one delivered story. It also swept EVERY epic in
    the repo, writing false completion onto epics the run never touched.

    Found by the independent adversarial review of RUN-01KXT0YV, which REJECTed the sprint.
    """

    def _epic(self, root, breakdown_lines, status="Draft", eid="EP0001"):
        d = root / "sdlc-studio" / "epics"
        d.mkdir(parents=True, exist_ok=True)
        lines = [f"# {eid}: widgets", "", f"> **Status:** {status}", "",
                 "## Story Breakdown", ""] + list(breakdown_lines)
        (d / f"{eid}-widgets.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        idx = d / "_index.md"
        rows = idx.read_text(encoding="utf-8") if idx.exists() else (
            "# Epics\n\n| ID | Title | Status |\n| --- | --- | --- |\n")
        idx.write_text(rows + f"| [{eid}]({eid}-widgets.md) | widgets | {status} |\n",
                       encoding="utf-8")

    def _status(self, root, eid="EP0001"):
        text = (root / "sdlc-studio" / "epics" / f"{eid}-widgets.md").read_text(encoding="utf-8")
        return next(line.split("**Status:**")[1].strip()
                    for line in text.splitlines() if "**Status:**" in line)

    def test_unresolvable_child_blocks_derivation(self) -> None:
        """A breakdown id with no backing file is UNKNOWN, not done."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root, scaffolded_retro="RETRO0001")
            _signoffable_story(root)
            _close_retro(root)
            self._epic(root, [
                "- [ ] [US0101: x](../stories/US0101-widget.md)",
                "- [ ] [US0102: not written yet](../stories/US0102-ghost.md)",
                "- [ ] [US0103: not written yet](../stories/US0103-ghost.md)",
            ])
            mod = _load()
            rc, out, err = _run_apply_signoff(root, mod)
            self.assertNotEqual(self._status(root), "Done")
            self.assertIn("could not be read", err)

    def test_child_without_status_blocks_derivation(self) -> None:
        """A unit file asserting no Status is UNKNOWN, not done."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root, scaffolded_retro="RETRO0001")
            _signoffable_story(root)
            _close_retro(root)
            (root / "sdlc-studio" / "stories" / "US0102-widget.md").write_text(
                "# US0102: no status field\n\nbody only\n", encoding="utf-8")
            self._epic(root, [
                "- [ ] [US0101: x](../stories/US0101-widget.md)",
                "- [ ] [US0102: y](../stories/US0102-widget.md)",
            ])
            mod = _load()
            _run_apply_signoff(root, mod)
            self.assertNotEqual(self._status(root), "Done")

    def test_untouched_epic_is_never_derived(self) -> None:
        """A close must not write completion onto an epic this run never touched."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root, scaffolded_retro="RETRO0001")
            _signoffable_story(root)
            _close_retro(root)
            self._epic(root, ["- [ ] [US0101: x](../stories/US0101-widget.md)"])
            # a SECOND epic, complete on its own terms, but no unit of it is in this run
            (root / "sdlc-studio" / "stories" / "US0900-other.md").write_text(
                "# US0900: other\n\n> **Status:** Done\n", encoding="utf-8")
            self._epic(root, ["- [ ] [US0900: other](../stories/US0900-other.md)"],
                       eid="EP0002")
            mod = _load()
            _run_apply_signoff(root, mod)
            self.assertEqual(self._status(root, "EP0001"), "Done")     # ours derives
            self.assertNotEqual(self._status(root, "EP0002"), "Done")  # theirs does not

    def test_empty_units_derives_nothing(self) -> None:
        """A bug/CR-only batch yields NO story units - that must derive nothing, never
        everything. `_batch_story_units` is story-scoped by design, so a run closing only
        bugs reaches the tail with units=[]; a truthiness escape there restored the
        full-repo sweep on exactly the batch shape with no business touching an epic."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root, scaffolded_retro="RETRO0001")
            (root / "sdlc-studio" / "stories").mkdir(parents=True, exist_ok=True)
            (root / "sdlc-studio" / "stories" / "US0900-other.md").write_text(
                "# US0900: other\n\n> **Status:** Done\n", encoding="utf-8")
            self._epic(root, ["- [ ] [US0900: other](../stories/US0900-other.md)"],
                       eid="EP0002")
            mod = _load()
            self.assertEqual(mod._derive_parent_epics(root, []), [])
            self.assertEqual(mod._derive_parent_epics(root, None), [])
            self.assertNotEqual(self._status(root, "EP0002"), "Done")


class ApplySignoffRefreshesHandoffTests(unittest.TestCase):
    """BG0191: the chain writes the handoff at step 5, the cascade transitions at the tail, so
    the document listed as remaining the very units the close had just completed."""

    def _handoff(self, root: Path, hid: str = "HO0001") -> Path:
        d = root / "sdlc-studio" / "handoffs"
        d.mkdir(parents=True, exist_ok=True)
        p = d / f"{hid}-a-run.md"
        p.write_text(
            f"# {hid}: a run\n\n> **Date:** 2026-07-16\n> **Created-by:** sdlc-studio new\n"
            "> **Run:** RUN-TEST0001 (started 2026-07-16T00:00:00Z)\n"
            "> **Outcome:** goal-reached\n> **Batch source:** run-state.json\n\n"
            "## Where to pick up\n\n1 of 1 unit(s) remain. Plan them straight back in:\n\n"
            "## Delivered (0)\n\n_Nothing was delivered in this run._\n\n"
            "## Remaining (1)\n\n- US0101\n\n## Open decisions\n\n_None._\n\n"
            "## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n"
            "| 2026-07-16 | sdlc-studio | Created |\n", encoding="utf-8")
        return p

    def test_the_handoff_is_rewritten_after_the_cascade(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root, scaffolded_retro="RETRO0001", handoff="HO0001")
            _signoffable_story(root)
            _close_retro(root)
            path = self._handoff(root)
            mod = _load()
            rc, out, err = _run_apply_signoff(root, mod)
            self.assertEqual(rc, 0, err)
            text = path.read_text(encoding="utf-8")
            self.assertIn("## Remaining (0)", text)
            self.assertIn("## Delivered (1)", text)

    def test_the_tail_reports_the_refresh(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root, scaffolded_retro="RETRO0001", handoff="HO0001")
            _signoffable_story(root)
            _close_retro(root)
            self._handoff(root)
            mod = _load()
            rc, out, err = _run_apply_signoff(root, mod)
            self.assertEqual(rc, 0, err)
            self.assertIn("HO0001 refreshed", out)

    def test_the_worklist_no_longer_carries_the_delivered_unit(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root, scaffolded_retro="RETRO0001", handoff="HO0001")
            _signoffable_story(root)
            _close_retro(root)
            self._handoff(root)
            mod = _load()
            rc, out, err = _run_apply_signoff(root, mod)
            self.assertEqual(rc, 0, err)
            wl = root / "sdlc-studio" / ".local" / "handoff-worklist.txt"
            self.assertNotIn("US0101", wl.read_text(encoding="utf-8"))

    def test_the_revision_history_survives_the_rewrite(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root, scaffolded_retro="RETRO0001", handoff="HO0001")
            _signoffable_story(root)
            _close_retro(root)
            path = self._handoff(root)
            mod = _load()
            _run_apply_signoff(root, mod)
            text = path.read_text(encoding="utf-8")
            self.assertIn("## Revision History", text)
            self.assertIn("2026-07-16 | sdlc-studio | Created", text)
            self.assertIn("# HO0001: a run", text)  # id and title, not a new artefact

    def test_the_rewrite_leaves_no_doubled_blank_line(self) -> None:
        # render_body already terminates its last section, so joining the kept Revision
        # History onto it produced two blank lines and the markdown gate (MD012) refused the
        # commit. A generated document must not need hand-fixing after every refresh.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root, scaffolded_retro="RETRO0001", handoff="HO0001")
            _signoffable_story(root)
            _close_retro(root)
            path = self._handoff(root)
            mod = _load()
            _run_apply_signoff(root, mod)
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("\n\n\n", text)
            self.assertTrue(text.endswith("\n"))

    def test_a_missing_handoff_file_is_reported_not_silently_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root, scaffolded_retro="RETRO0001", handoff="HO0009")
            _signoffable_story(root)
            _close_retro(root)
            mod = _load()
            rc, out, err = _run_apply_signoff(root, mod)
            self.assertEqual(rc, 0, err)  # a stale handoff must not lose the close
            self.assertIn("HO0009", out + err)
            self.assertIn("not refreshed", out + err)

    def test_the_refresh_is_scoped_to_the_passed_run_not_whatever_run_is_open(self) -> None:
        # The handoff belongs to the run being closed. `build` defaults to the run state on
        # disk, so an unscoped refresh re-renders a CLOSED run's handoff against whichever
        # run happens to be open - which is how a hand-run refresh overwrote a shipped
        # handoff with the next sprint's batch.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root, scaffolded_retro="RETRO0001", handoff="HO0001",
                         batch=["US0102"])          # what is OPEN on disk
            _signoffable_story(root)                # US0101, about to go Done
            _close_retro(root)
            path = self._handoff(root)
            mod = _load()
            closing_state = dict(_close_state(root, scaffolded_retro="RETRO0001",
                                              handoff="HO0001", batch=["US0102"]))
            closing_state["batch"] = ["US0101"]     # the run being CLOSED
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                mod._apply_signoff_tail(root, closing_state, units=["US0101"])
            text = path.read_text(encoding="utf-8")
            self.assertIn("US0101", text)
            self.assertNotIn("US0102", text)

    def test_a_run_with_no_handoff_recorded_does_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root, scaffolded_retro="RETRO0001", handoff=None)
            _signoffable_story(root)
            _close_retro(root)
            mod = _load()
            rc, out, err = _run_apply_signoff(root, mod)
            self.assertEqual(rc, 0, err)
            self.assertNotIn("refreshed", out)


def _quiet_brief(root, units):
    """build_gate_briefing with its diagnostics captured (the test-noise gate is a budget)."""
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return sprint.build_gate_briefing(root, units)


class GateBriefingTests(unittest.TestCase):
    """US0266: the plan briefs the gates instead of leaving them to be met as refusals."""

    def _bug(self, root: Path, depth: str = "") -> None:
        d = root / "sdlc-studio" / "bugs"
        d.mkdir(parents=True, exist_ok=True)
        line = f"> **Verification depth:** {depth}\n" if depth else ""
        (d / "BG0001-x.md").write_text(
            f"# BG0001: x\n\n> **Status:** Open\n{line}> **Severity:** Low\n"
            "> **Points:** 2\n\n## Summary\n\ns\n\n\n## Acceptance Criteria\n\n- [ ] the defect no longer reproduces\n", encoding="utf-8")
        (d / "_index.md").write_text(
            "# Bugs\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            "| [BG0001](BG0001-x.md) | x | Open |\n", encoding="utf-8")

    def test_briefing_names_unmet_requirements(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._bug(root)
            brief = _quiet_brief(root, [{"id": "BG0001", "type": "bug"}])
            self.assertEqual(len(brief["units"]), 1)
            self.assertIn("Verification depth", brief["units"][0]["unmet"][0])
            self.assertEqual(brief["units"][0]["target"], "Fixed")

    def test_a_satisfied_unit_carries_no_requirement(self) -> None:
        # The negative branch: a briefing that always reported something would be noise,
        # and would still satisfy the assertion above.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._bug(root, depth="functional (reproduced)")
            brief = _quiet_brief(root, [{"id": "BG0001", "type": "bug"}])
            self.assertEqual(brief["units"], [])

    def test_briefing_is_generated_from_definitions(self) -> None:
        """AC2: the commit-check list comes from the gate, so it cannot drift from it.

        Proven by adding a check to the gate's own definition and asserting it appears. A
        hand-maintained list in the briefing would pass every other test here while going
        stale the moment a check is added or removed.
        """
        import gate
        original = dict(gate.DEFAULT_CHECKS)
        try:
            gate.DEFAULT_CHECKS["sentinel-check"] = lambda *a, **k: None
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                self._bug(root)
                brief = _quiet_brief(root, [{"id": "BG0001", "type": "bug"}])
            self.assertIn("sentinel-check", brief["commit_checks"],
                          "the briefing restates the check list instead of reading it")
        finally:
            gate.DEFAULT_CHECKS.clear()
            gate.DEFAULT_CHECKS.update(original)

    def test_briefing_is_scoped_to_the_batch(self) -> None:
        # AC4: only the types actually in the batch. A briefing that described every type
        # would bury the relevant lines, which is how a checklist stops being read.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._bug(root)
            brief = _quiet_brief(root, [{"id": "BG0001", "type": "bug"}])
            self.assertEqual(brief["types"], ["bug"])

    def test_an_unresolvable_unit_does_not_break_the_plan(self) -> None:
        # A briefing is an aid, never a gate: a unit it cannot resolve is skipped, not raised.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir(parents=True)
            brief = _quiet_brief(root, [{"id": "BG9999", "type": "bug"}])
            self.assertEqual(brief["units"], [])


class CloseReconcileBlockedDerivableTests(unittest.TestCase):
    """The close's reconcile step must not deadlock behind drift `apply` cannot clear.

    A `request-derivable` item another gate refuses is real drift, but the remedy the step
    prints - `reconcile.py apply` - provably cannot clear it, so every close in the project
    stalls behind one pending decision. Found live: the sign-off and the Done transitions for
    a fully-reviewed batch were stranded behind an RFC awaiting a decision nobody in the run
    could make.

    The exemption is narrow on purpose. These tests pin BOTH directions, because an exemption
    that waves through ordinary drift is worse than the deadlock it replaces.
    """

    def _mod_with(self, detect_rc, derivable, per_type_drift=0):
        mod = _load()
        rec = mod.reconcile
        self.addCleanup(setattr, rec, "main", rec.main)
        self.addCleanup(setattr, rec, "derivable_request_drift", rec.derivable_request_drift)
        self.addCleanup(setattr, rec, "detect_type", rec.detect_type)
        rec.main = lambda argv: detect_rc
        rec.derivable_request_drift = lambda root, explain=True: derivable
        rec.detect_type = lambda t, root: {"drift": [{"x": 1}] * per_type_drift}
        return mod

    def test_a_blocked_derivable_request_does_not_stop_the_close(self) -> None:
        mod = self._mod_with(1, [{"id": "RFC0046", "blocked_by": "1 Open decision"}])
        ok, detail, _ = mod._close_reconcile(Path("."), "RETRO0001", {})
        self.assertTrue(ok, detail)
        self.assertIn("RFC0046", detail)
        self.assertIn("not clearable by apply", detail)

    def test_ordinary_drift_still_stops_the_close(self) -> None:
        """The exemption must not become a blanket pass: real drift alongside a blocked item
        still blocks. Without this, 'detect exited non-zero' would always be forgiven."""
        mod = self._mod_with(1, [{"id": "RFC0046", "blocked_by": "1 Open decision"}],
                             per_type_drift=1)
        ok, _, remedy = mod._close_reconcile(Path("."), "RETRO0001", {})
        self.assertFalse(ok)
        self.assertIn("reconcile.py apply", remedy)

    def test_an_unblocked_derivable_request_still_stops_the_close(self) -> None:
        """It is clearable by the command the remedy names, so it must be cleared, not excused."""
        mod = self._mod_with(1, [{"id": "CR0001", "blocked_by": None}])
        ok, _, remedy = mod._close_reconcile(Path("."), "RETRO0001", {})
        self.assertFalse(ok)
        self.assertIn("reconcile.py apply", remedy)

    def test_a_clean_tree_reports_no_drift(self) -> None:
        mod = self._mod_with(0, [])
        ok, detail, _ = mod._close_reconcile(Path("."), "RETRO0001", {})
        self.assertTrue(ok)
        self.assertEqual(detail, "no index drift")


class ClosePreflightTests(unittest.TestCase):
    """CR0359: the close discovered its blockers one at a time.

    Each refusal was correct and well explained, but each was found only after the preceding
    ones were cleared, and every cycle cost a full gate run. The information was all available
    before the first attempt. These tests pin that it is now reported in one pass, that the pass
    is read-only, and - the part that made the old behaviour so expensive - that it covers the
    apply-signoff prerequisites, which surfaced last of all.
    """

    def _mod(self, root, *, lanes=(), units=None, verdicts=None, evidence=(), signoffs=(),
             covered=()):
        """sprint module with the gate and critic stubbed, so these run in milliseconds and
        assert the PRE-FLIGHT's composition rather than re-testing the gate."""
        mod = _load()
        import gate as gate_mod
        import critic as critic_mod
        self.addCleanup(setattr, gate_mod, "run_gate", gate_mod.run_gate)
        for name in ("verdict_for", "evidence_for", "signoff_for",
                     "is_independent_signoff", "sprint_review_for",
                     "sprint_covers_independently"):
            self.addCleanup(setattr, critic_mod, name, getattr(critic_mod, name))
        gate_mod.run_gate = lambda *a, **k: {"ok": not lanes, "checks": [
            {"check": c, "status": "fail", "blocking": True, "detail": f"{c} detail"}
            for c in lanes]}
        # The two-role half only applies past `review.two_role_after`. Without this the whole
        # evidence/sign-off branch is skipped and the sign-off tests pass for the wrong reason.
        cfg = root / "sdlc-studio" / ".config.yaml"
        cfg.parent.mkdir(parents=True, exist_ok=True)
        cfg.write_text("review:\n  two_role_after: 100\n", encoding="utf-8")
        verdicts = verdicts or {}
        critic_mod.verdict_for = lambda r, u, phase="delivery": verdicts.get(u)
        critic_mod.evidence_for = lambda r, u: [{"x": 1}] if u in evidence else []
        critic_mod.signoff_for = lambda r, u: {"principal": "p"} if u in signoffs else None
        critic_mod.is_independent_signoff = lambda r, u, s: u in signoffs
        critic_mod.sprint_review_for = lambda r, u: None
        critic_mod.sprint_covers_independently = lambda r, u, rev: u in covered
        batch = list(units or ["US0101"])
        # Real artefacts behind the batch ids: the sign-off brief refuses an id with no unit,
        # and a fixture naming units that do not exist would fail for that reason rather than
        # for anything the pre-flight decides.
        sd = root / "sdlc-studio" / "stories"
        sd.mkdir(parents=True, exist_ok=True)
        for u in batch:
            # With a criterion: BG0378 made the criteria floor fire at the transition VERB, so
            # a unit with none is blocked by the done-gate and these tests would be asserting
            # the pre-flight's composition against a fixture that fails for an unrelated reason.
            (sd / f"{u}-x.md").write_text(
                f"# {u}: x\n\n> **Status:** Done\n> **Points:** 2\n\n"
                f"## Acceptance Criteria\n\n- [ ] it behaves\n",
                encoding="utf-8")
        _close_state(root, batch=batch)
        return mod

    def _retro(self, root, rid="RETRO0001"):
        d = root / "sdlc-studio" / "retros"
        d.mkdir(parents=True, exist_ok=True)
        # Every REQUIRED_SECTION: a partial retro is a legitimate blocker, and a fixture missing
        # one would make these tests fail for a reason unrelated to the pre-flight.
        (d / f"{rid}-x.md").write_text(
            f"# {rid}: r\n\n## Delivered\n\n- a thing\n\n"
            "## What went well\n\n- it went\n\n"
            "## What was hard / what stalled\n\n- it stalled\n\n"
            "## Lessons\n\n- a real lesson worth carrying forward\n\n"
            "## Actions raised\n\n| Finding | Disposition |\n| --- | --- |\n"
            "| a finding | declined: not worth it |\n",
            encoding="utf-8")
        return rid

    def _stages(self, res):
        return [b["stage"] for b in res["blockers"]]

    def test_preflight_reports_every_blocker_in_one_pass(self) -> None:
        """AC1: several unmet prerequisites, ONE invocation, all of them named."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = self._mod(root, lanes=("conformance", "reconcile"), units=["US0101"])
            _close_state(root, batch=["US0101"], sprint_goal_verdict=None)
            res = mod.close_preflight(root, None)
            self.assertFalse(res["ready"])
            stages = self._stages(res)
            # goal-verdict AND retro AND both gate lanes AND the sign-off gap - together.
            self.assertIn("goal-verdict", stages)
            self.assertIn("retro", stages)
            self.assertEqual(stages.count("gate"), 2, res["blockers"])
            self.assertIn("sign-off", stages)
            self.assertGreaterEqual(len(res["blockers"]), 5)

    def test_preflight_writes_nothing(self) -> None:
        """AC2: it answers the question without committing to a close."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = self._mod(root, lanes=("conformance",))
            before = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
            mod.close_preflight(root, None)
            after = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
            self.assertEqual(before, after, "the pre-flight wrote to the tree")

    def test_preflight_reports_ready_when_nothing_is_unmet(self) -> None:
        """AC3: ready is a positive answer, not merely the absence of output."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = self._mod(root, units=["US0101"], verdicts={"US0101": {"verdict": "APPROVE"}},
                            evidence=("US0101",), signoffs=("US0101",))
            rid = self._retro(root)
            res = mod.close_preflight(root, rid)
            self.assertTrue(res["ready"], res["blockers"])
            self.assertEqual(res["blockers"], [])

    def test_preflight_names_missing_signoff_prerequisites(self) -> None:
        """US0274 AC1: the prerequisites that surface LAST today are surfaced first."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = self._mod(root, units=["US0101"])
            rid = self._retro(root)
            res = mod.close_preflight(root, rid)
            signoff = [b for b in res["blockers"] if b["stage"] == "sign-off"]
            self.assertTrue(signoff, res["blockers"])
            self.assertIn("US0101", signoff[0]["detail"])
            self.assertIn("critic.py", signoff[0]["remedy"])

    def test_preflight_accepts_sprint_level_coverage(self) -> None:
        """US0274 AC2: a pre-flight that OVER-reports is as untrustworthy as one that under-
        reports. Sprint coverage satisfies the critique gate, so it must not be flagged."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = self._mod(root, units=["US0101"], covered=("US0101",), signoffs=("US0101",))
            rid = self._retro(root)
            res = mod.close_preflight(root, rid)
            self.assertEqual([b for b in res["blockers"] if b["stage"] == "sign-off"], [],
                             "sprint-level coverage was reported as a missing critique")

    def test_preflight_delegates_to_critic(self) -> None:
        """US0274 AC3: swap critic's verdict and the pre-flight must follow.

        A pre-flight carrying its own copy of the independence rule is two answers to one
        question, and it would pass every other test in this class.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = self._mod(root, units=["US0101"], verdicts={"US0101": {"verdict": "APPROVE"}},
                            evidence=("US0101",), signoffs=("US0101",))
            rid = self._retro(root)
            self.assertTrue(mod.close_preflight(root, rid)["ready"])
            import critic as critic_mod
            critic_mod.is_independent_signoff = lambda r, u, s: False   # the gate now refuses
            res = mod.close_preflight(root, rid)
            self.assertIn("sign-off", self._stages(res),
                          "the pre-flight reimplements the sign-off rule instead of asking")

    def test_preflight_reports_the_done_gate_apply_signoff_will_hit(self) -> None:
        """The pre-flight said READY and `--apply-signoff` then refused.

        The critic checks are only half of what apply-signoff demands: it calls `artifact.close`,
        which is AC-verify gated. A unit with every critic prerequisite satisfied but executable
        ACs never run passed the pre-flight and was refused by the close - the exact
        preview-disagrees-with-run defect this whole change exists to remove.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = self._mod(root, units=["US0101"],
                            verdicts={"US0101": {"verdict": "APPROVE"}},
                            evidence=("US0101",), signoffs=("US0101",))
            # An executable AC that was never verified: `transition -> Done` blocks on it.
            p = root / "sdlc-studio" / "stories" / "US0101-x.md"
            p.write_text(p.read_text(encoding="utf-8")
                         + "\n## Acceptance Criteria\n\n### AC1: it works\n\n"
                           "- **Verify:** shell true\n", encoding="utf-8")
            rid = self._retro(root)
            res = mod.close_preflight(root, rid)
            self.assertFalse(res["ready"], "the pre-flight reported ready on a refused close")
            self.assertIn("done-gate", self._stages(res))

    def test_an_unreadable_unit_is_reported_not_raised(self) -> None:
        """A pre-flight must never turn a clean refusal into a traceback.

        The done-gate preview caught only `(ValueError, FileNotFoundError)`, so a PermissionError
        escaped. Because the report correctly runs above EVERY refusal, that took down closes
        which would otherwise have refused instantly for an unrelated reason - a regression the
        placement fix enlarged the blast radius of.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = self._mod(root, units=["US0101"],
                            verdicts={"US0101": {"verdict": "APPROVE"}},
                            evidence=("US0101",), signoffs=("US0101",))
            rid = self._retro(root)
            import artifact as artifact_mod
            self.addCleanup(setattr, artifact_mod, "close", artifact_mod.close)

            def boom(*_a, **_k):
                raise PermissionError(13, "Permission denied")
            artifact_mod.close = boom
            res = mod.close_preflight(root, rid)     # must not raise
            detail = [b for b in res["blockers"] if b["stage"] == "done-gate"]
            self.assertTrue(detail, res["blockers"])
            self.assertIn("Permission denied", detail[0]["detail"])

    def test_preflight_ignores_a_batch_id_with_no_artefact(self) -> None:
        """US0274 AC2, the over-reporting half: apply-signoff resolves batch ids through
        `_batch_story_units` and skips one with no artefact behind it, so reporting it as owed
        work is a blocker the close will never ask for."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = self._mod(root, units=["US0101"])
            (root / "sdlc-studio" / "stories" / "US0101-x.md").unlink()
            rid = self._retro(root)
            res = mod.close_preflight(root, rid)
            self.assertEqual([b for b in res["blockers"]
                              if b["stage"] in ("sign-off", "done-gate")], [],
                             "reported work for a batch id with no artefact")

    def test_close_reports_blockers_that_its_own_refusals_would_short_circuit(self) -> None:
        """The report must sit ABOVE the early refusals, or it never runs when one fires.

        Placed after them, an unjudged goal returned before the pre-flight was reached, so the
        gate and sign-off blockers stayed hidden - serial discovery, reintroduced by placement.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = self._mod(root, lanes=("conformance",), units=["US0101"])
            _close_state(root, batch=["US0101"], sprint_goal_verdict=None)   # an early refusal
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                mod.main(["close", "--root", str(root)])
            out = err.getvalue()
            self.assertIn("close pre-flight", out)
            self.assertIn("conformance", out, "the gate blockers were hidden by the refusal")
            self.assertIn("sign-off", out, "the sign-off blockers were hidden by the refusal")

    def test_close_reports_all_blockers_before_executing(self) -> None:
        """US0275 AC1: printed before the first chain step runs."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = self._mod(root, lanes=("conformance",), units=["US0101"])
            rid = self._retro(root)
            order = []
            original = mod._close_retro_validate
            mod._close_retro_validate = lambda *a, **k: (order.append("step") or
                                                         (False, "stop", "fix it"))
            try:
                err = io.StringIO()
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                    mod.main(["close", "--retro", rid, "--root", str(root)])
                out = err.getvalue()
            finally:
                mod._close_retro_validate = original
            self.assertIn("close pre-flight", out)
            self.assertIn("this is ALL of them", out)
            self.assertLess(out.index("close pre-flight"), out.index("close STOPPED"),
                            "the pre-flight report came after a chain step had already run")

    def test_close_with_nothing_outstanding_is_unchanged(self) -> None:
        """US0275 AC2: the pre-flight adds a report, never a new refusal."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = self._mod(root, units=["US0101"], verdicts={"US0101": {"verdict": "APPROVE"}},
                            evidence=("US0101",), signoffs=("US0101",))
            rid = self._retro(root)
            self.assertTrue(mod.close_preflight(root, rid)["ready"])
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = mod.main(["close", "--retro", rid, "--root", str(root)])
            # STDERR, which is where the report is written. Asserting on stdout alone made this
            # test vacuous: a mutant that always printed the report still passed it.
            self.assertNotIn("close pre-flight", err.getvalue())
            self.assertNotIn("close pre-flight", out.getvalue())
            self.assertIsNotNone(rc)

    def test_a_close_that_is_not_ready_still_reaches_its_chain(self) -> None:
        """AC2 tested where the property CAN fail: a NOT-ready workspace.

        The previous version compared a ready workspace against one with the pre-flight stubbed
        out. That could essentially never fail: with nothing unmet the report is silent, so both
        arms agreed no matter what was mutated around the call. A literal `return 1` after the
        pre-flight survived it, which is exactly the refusal AC2 forbids.

        Here the pre-flight HAS blockers, so a mutant that turned the report into a refusal stops
        the close before the chain and this goes red.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = self._mod(root, units=["US0101"])      # no verdict: the pre-flight is not ready
            rid = self._retro(root)
            self.assertFalse(mod.close_preflight(root, rid)["ready"])
            reached = []
            original = mod._close_retro_validate
            mod._close_retro_validate = lambda *a, **k: (reached.append(1) or (True, "ok", ""))
            try:
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    mod.main(["close", "--retro", rid, "--root", str(root)])
            finally:
                mod._close_retro_validate = original
            self.assertEqual(reached, [1],
                             "an unmet pre-flight stopped the close instead of only reporting")


class CarryForwardCloseTests(unittest.TestCase):
    """US0334: the close records the policy in force and lists the findings carried."""

    def _sprint(self):
        import importlib.util, sys
        from pathlib import Path
        base = Path(__file__).resolve().parent.parent
        for name in ("carry_forward", "sprint"):
            spec = importlib.util.spec_from_file_location(name, base / f"{name}.py")
            m = importlib.util.module_from_spec(spec); sys.modules[name] = m
            spec.loader.exec_module(m)
        return sys.modules["sprint"]

    def _root(self, policy):
        d = Path(tempfile.mkdtemp(prefix="cf_close_"))
        (d / "sdlc-studio").mkdir(parents=True)
        (d / "sdlc-studio" / ".config.yaml").write_text(f"review:\n  policy: {policy}\n")
        return d

    def test_the_close_records_the_policy_resolved_at_close_time(self) -> None:
        sprint = self._sprint()
        d = self._root("carry-forward")
        try:
            rec = sprint.carry_forward_close_record(d, carried=[{"ref": "BG9001"}])
            self.assertEqual(rec["policy"], "carry-forward")
            # resolved from the config NOW, not carried from run-open: flip it and re-read
            (d / "sdlc-studio" / ".config.yaml").write_text("review:\n  policy: block\n")
            self.assertEqual(sprint.carry_forward_close_record(d)["policy"], "block")
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_a_close_carrying_nothing_is_distinguishable_from_a_dropped_list(self) -> None:
        sprint = self._sprint()
        d = self._root("carry-forward")
        try:
            two = sprint.carry_forward_close_record(d, carried=[{"ref": "BG9001"}, {"ref": "BG9002"}])
            none = sprint.carry_forward_close_record(d, carried=[])
            self.assertEqual(two["carried_count"], 2)
            self.assertEqual([c["ref"] for c in two["carried"]], ["BG9001", "BG9002"])
            # an empty list is a real, present, EMPTY list - not an absent/dropped one
            self.assertEqual(none["carried_count"], 0)
            self.assertEqual(none["carried"], [])
            self.assertIn("carried", none)
        finally:
            shutil.rmtree(d, ignore_errors=True)


def _plan_text(root: Path) -> str:
    """Run `plan` and return its stdout - the surface an operator reads."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        _load().main(["plan", "--crs", "Proposed", "--root", str(root),
                      "--no-fetch", "--skip-personas"])
    return out.getvalue()


#: Three whole-sprint velocity rows (Measured 0, ceremony included), same model - at or above
#: FIXED_MIN_SPRINTS, so the fitted fixed term may be APPLIED to a forecast total.
_FIXED_ROWS_APPLIED = [
    {"id": "RETRO0001", "units": 4, "measured": 0, "points": 18, "actual": 4_119_916,
     "model": "claude-opus-4-8"},
    {"id": "RETRO0002", "units": 33, "measured": 0, "points": 100, "actual": 5_194_538,
     "model": "claude-opus-4-8"},
    {"id": "RETRO0003", "units": 12, "measured": 0, "points": 50, "actual": 4_650_000,
     "model": "claude-opus-4-8"},
]
#: Two whole-sprint rows - the fit is MEASURED but below the apply minimum (CR0391's own case).
_FIXED_ROWS_CANDIDATE = _FIXED_ROWS_APPLIED[:2]


class TheForecastCarriesAFixedTermTests(unittest.TestCase):
    """US0336 / CR0391: the forecast carries an explicit FIXED per-sprint term beside the
    marginal per-point term, and the plan shows BOTH rather than a single product. A small batch
    is not priced as though the ceremony, review rounds and close were free."""

    def _applied_root(self, d) -> Path:
        root = Path(d)
        _velocity(root, _FIXED_ROWS_APPLIED)
        return root

    def test_the_total_is_a_fixed_term_plus_points_times_the_marginal_rate(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._applied_root(d)
            sp = _load()
            _pointed_cr(root, 1, 5)
            _pointed_cr(root, 2, 3)
            fc = sp.build_plan(root, "cr", "Proposed", order="wsjf")["token_forecast"]
            self.assertTrue(fc["fixed_applied"])
            self.assertGreater(fc["fixed_term"], 0)
            self.assertGreater(fc["fixed_marginal"], 0)
            self.assertEqual(fc["rate"], fc["fixed_marginal"],
                             "the marginal half of the fit is the per-point rate")
            self.assertEqual(fc["points"], 8)
            self.assertEqual(fc["tokens"], fc["fixed_term"] + fc["points"] * fc["fixed_marginal"])
            # neither term can be recovered by dividing the other out: total/points != marginal
            self.assertNotEqual(fc["tokens"] // fc["points"], fc["rate"])

    def test_the_rendered_forecast_shows_both_terms_and_not_one_product(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._applied_root(d)
            _pointed_cr(root, 1, 5)
            text = _plan_text(root)
            self.assertIn("fixed per-sprint term", text)   # the fixed term, its own line
            self.assertIn("per-point (build) term", text)  # the marginal term, its own line
            self.assertIn("APPLIED", text)
            # the fixed figure is quoted, not folded into a bare points-times-a-rate product
            fixed_line = next(ln for ln in text.splitlines() if "fixed per-sprint term" in ln)
            self.assertRegex(fixed_line, r"[0-9][0-9,]+")

    def test_a_half_size_batch_costs_more_than_half_and_more_per_point(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._applied_root(d)
            sp = _load()
            _pointed_cr(root, 1, 8)
            _pointed_cr(root, 2, 4)
            cr1 = root / "sdlc-studio" / "change-requests" / "CR0001-x.md"
            cr2 = root / "sdlc-studio" / "change-requests" / "CR0002-x.md"
            big = sp._token_forecast(root, [{"id": "CR0001", "path": str(cr1), "points": 8}])
            small = sp._token_forecast(root, [{"id": "CR0002", "path": str(cr2), "points": 4}])
            self.assertTrue(big["fixed_applied"] and small["fixed_applied"])
            self.assertGreater(small["tokens"], big["tokens"] / 2,
                               "the fixed term is amortised over fewer points, so > half")
            self.assertGreater(small["tokens"] / small["points"],
                               big["tokens"] / big["points"],
                               "and the smaller batch costs strictly more per point")


class AFitIsNeverAppliedAutomaticallyTests(unittest.TestCase):
    """US0338 / CR0391: a fit is never applied automatically. The plan states how many sprints it
    rests on and refuses to spend a fit below FIXED_MIN_SPRINTS - a line through two points is not
    calibration."""

    def test_a_two_sprint_fit_is_reported_and_kept_out_of_the_total(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            _velocity(root, _FIXED_ROWS_CANDIDATE)         # two whole-sprint rows
            _pointed_cr(root, 1, 5)
            fc = sp.build_plan(root, "cr", "Proposed", order="wsjf")["token_forecast"]
            self.assertFalse(fc["fixed_applied"])
            self.assertIsNotNone(fc["fixed_term"], "the candidate fit is still reported")
            self.assertEqual(fc["fixed_in_total"], 0, "and kept OUT of the total")
            self.assertEqual(fc["tokens"], fc["points"] * fc["rate"],
                             "the total prices the build only - it did not move when row 2 landed")
            text = _plan_text(root)
            self.assertIn("NOT APPLIED", text)
            self.assertIn(str(sp.FIXED_MIN_SPRINTS), text)   # the minimum required
            self.assertIn("2", text)                         # the count the project has

    def test_every_quoted_fixed_term_states_the_sprint_count_behind_it(self) -> None:
        sp = _load()
        # candidate case: a figure is quoted, so its sample size (2) must sit beside it
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _velocity(root, _FIXED_ROWS_CANDIDATE)
            _pointed_cr(root, 1, 5)
            self.assertIn("fitted on 2 sprint", _plan_text(root))
        # applied case: the figure is quoted, so its sample size (3) must sit beside it
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _velocity(root, _FIXED_ROWS_APPLIED)
            _pointed_cr(root, 1, 5)
            self.assertIn("fitted on 3 whole-sprint", _plan_text(root))

    def test_a_fit_at_the_minimum_is_applied_and_names_its_sprint_count(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            self.assertEqual(len(_FIXED_ROWS_APPLIED), sp.FIXED_MIN_SPRINTS,
                             "the fixture sits exactly AT the apply minimum")
            _velocity(root, _FIXED_ROWS_APPLIED)
            _pointed_cr(root, 1, 5)
            fc = sp.build_plan(root, "cr", "Proposed", order="wsjf")["token_forecast"]
            self.assertTrue(fc["fixed_applied"], "at the minimum the fit is applied")
            self.assertEqual(fc["fixed_in_total"], fc["fixed_term"])
            self.assertGreater(fc["tokens"], fc["points"] * fc["fixed_marginal"],
                               "the fixed term entered the total")
            text = _plan_text(root)
            self.assertIn("APPLIED", text)
            self.assertIn("3", text)                         # the sprint count behind it


class TheSeedBasisNamesItsConditionTests(unittest.TestCase):
    """US0339 / CR0391: the shipped seed's basis names the DATA the no-base-term finding was
    measured on (per-unit actuals with no sprint ceremony), instead of asserting flatly that a
    base term does worse - the sentence a future author would cite to reject the fixed term."""

    CONDITION = "per-unit actuals with no sprint ceremony"

    def test_the_seed_basis_states_the_data_the_no_base_term_finding_was_measured_on(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            sp = _load()
            rate = sp.tokens_per_point(Path(d))       # no evidence -> the shipped seed
            self.assertEqual(rate["source"], "seed")
            self.assertIn(self.CONDITION, rate["basis"].lower(),
                          "the seed basis names the data the no-base-term result was measured on")
            # it no longer asserts the bare, unconditional claim
            self.assertNotIn("no base term: fitting one does worse than not fitting at all",
                             rate["basis"].lower())

    def test_the_qualification_survives_when_a_local_rate_replaces_the_seed(self) -> None:
        # A DIFFERENT fixture: this project has measured a rate of its own, so the forecast quotes
        # that, not the seed. The condition must still travel with the figure - a criterion checked
        # only in the seed case would be satisfied by AC1's fixture and discriminate nothing.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = _load()
            _velocity(root, _FIXED_ROWS_CANDIDATE)     # two whole-sprint rows -> a local rate
            _pointed_cr(root, 1, 5)
            fc = sp.build_plan(root, "cr", "Proposed", order="wsjf")["token_forecast"]
            self.assertNotEqual(fc["rate_source"], "seed",
                                "the premise: a local rate has replaced the seed")
            self.assertIn(self.CONDITION, fc["basis"].lower(),
                          "the condition still travels with the figure when the seed is gone")


class HelpAndRefusalNameTheSameRoutesTests(unittest.TestCase):
    """US0329: help/sprint.md states the single run slot and the two ways past a refused disjoint
    batch, spelled as the SAME two routes an operator sees in the refusal - so either surface leads
    to the same action, and no third route is implied."""

    HELP = SCRIPT.parent.parent / "help" / "sprint.md"

    def _help(self) -> str:
        return self.HELP.read_text(encoding="utf-8")

    def test_the_help_states_the_slot_the_refusal_and_the_accumulating_replan(self) -> None:
        # AC1's three facts, present and no fourth behaviour implied.
        text = self._help().lower()
        self.assertIn("one run", text)                       # a project holds one run at a time
        self.assertTrue("refused, not merged" in text or "refused rather than merged" in text,
                        "a disjoint batch is refused rather than merged")
        self.assertIn("accumulat", text)                     # an overlapping re-plan accumulates

    def test_the_refusal_and_help_sprint_name_the_same_two_routes_and_spellings(self) -> None:
        sp = _load()
        refusal = str(sp.run_state.DisjointBatchError("RUN-01TEST", "running", 6, repo_root="."))
        refusal_cmds = [ln for ln in refusal.splitlines() if "sprint.py" in ln]
        # the refusal names exactly two routes, as commands
        self.assertEqual(len(refusal_cmds), 2)
        self.assertTrue(any("close" in c for c in refusal_cmds))
        self.assertTrue(any("plan" in c and "--write" in c for c in refusal_cmds))

        # the help names the SAME two routes, spelled as the same commands, and no third
        help_text = self._help()
        slot = help_text.split("## One run slot", 1)[1].split("\n## ", 1)[0]
        ways = slot.split("two ways forward", 1)[1]          # only the ways-forward list
        route_lines = [ln for ln in ways.splitlines()
                       if "`sprint close`" in ln or ("`sprint plan" in ln and "--write" in ln)]
        self.assertEqual(len(route_lines), 2, "the help names exactly the two routes, no third")
        self.assertTrue(any("close" in ln for ln in route_lines))
        self.assertTrue(any("plan" in ln and "--write" in ln for ln in route_lines))
        # the two surfaces agree on the two actions: close, and a --write re-plan
        self.assertEqual(
            {"close" if "close" in c else "replan" for c in refusal_cmds},
            {"close" if "close" in ln else "replan" for ln in route_lines})


class _DeliveryModeFixture(unittest.TestCase):
    """Shared batch builder for the EP0154 delivery-mode tests. Each story declares its own
    Affects and a node-addressed Verify line, so the offer reads real files."""

    def _story(self, root, num, affects, verify_file):
        d = root / "sdlc-studio" / "stories"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"US{num:04d}-x.md").write_text(
            f"# US{num:04d}: x\n\n> **Status:** Draft\n> **Points:** 2\n"
            f"> **Affects:** {affects}\n\n## Acceptance Criteria\n\n"
            f"### AC1\n- **Verify:** pytest {verify_file}::T::t\n", encoding="utf-8")
        # the affected + verify files must resolve for _affect_key to key them by path
        for p in [a.strip() for a in affects.split(",")] + [verify_file]:
            fp = root / p
            fp.parent.mkdir(parents=True, exist_ok=True)
            if not fp.exists():
                fp.write_text("# marker\n", encoding="utf-8")
        return {"id": f"US{num:04d}", "path": str(d / f"US{num:04d}-x.md"), "points": 2}


class DeliveryModeOfferTests(_DeliveryModeFixture):
    """US0407: parallel is offered only for a genuinely file-disjoint batch, and the choice is
    recorded against the offer that permitted it."""

    def test_a_parallelisable_batch_offers_both_modes_and_records_the_choice(self):
        s = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            batch = [self._story(root, 1, "src/a.py", "tests/test_a.py"),
                     self._story(root, 2, "src/b.py", "tests/test_b.py")]
            offer = s.delivery_mode_offer(root, batch)
            self.assertEqual(offer["modes"], ["sequential", "parallel"])
            self.assertTrue(offer["parallel_available"])
            # a valid choice records; an unavailable one is refused, so a recorded mode is real
            self.assertEqual(s.record_delivery_mode(offer, "parallel")["mode"], "parallel")
            self.assertEqual(len(offer["groups"]), 2)

    def test_a_one_unit_batch_is_sequential_and_says_why_parallel_was_withheld(self):
        s = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            batch = [self._story(root, 1, "src/a.py", "tests/test_a.py")]
            offer = s.delivery_mode_offer(root, batch)
            self.assertEqual(offer["modes"], ["sequential"])
            self.assertFalse(offer["parallel_available"])
            self.assertIn("one-unit", offer["reason"])
            with self.assertRaises(ValueError):
                s.record_delivery_mode(offer, "parallel")

    def test_a_unit_without_affects_withholds_parallel_even_if_the_rest_is_disjoint(self):
        s = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            batch = [self._story(root, 1, "src/a.py", "tests/test_a.py")]
            # a second story with NO Affects line - unknown blast radius
            sd = root / "sdlc-studio" / "stories"
            (sd / "US0002-x.md").write_text(
                "# US0002: x\n\n> **Status:** Draft\n> **Points:** 2\n", encoding="utf-8")
            batch.append({"id": "US0002", "path": str(sd / "US0002-x.md"), "points": 2})
            offer = s.delivery_mode_offer(root, batch)
            self.assertFalse(offer["parallel_available"])   # withheld despite src/a.py being disjoint
            self.assertIn("US0002", offer["undeclared_affects"])
            self.assertIn("no Affects", offer["reason"])

    def test_an_all_coupled_batch_is_not_offered_parallel(self):
        s = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            # both units touch src/shared.py -> one coupled component
            batch = [self._story(root, 1, "src/shared.py", "tests/test_a.py"),
                     self._story(root, 2, "src/shared.py", "tests/test_b.py")]
            offer = s.delivery_mode_offer(root, batch)
            self.assertFalse(offer["parallel_available"])
            self.assertEqual(len(offer["groups"]), 1)
            self.assertIn("does not decompose", offer["reason"])


class DeliveryModeTestFileCouplingTests(_DeliveryModeFixture):
    """US0408: a shared TEST file couples two units even when their Affects are disjoint."""

    def test_a_shared_test_file_counts_as_coupling(self):
        s = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            # disjoint source files, but the SAME test file in both Verify lines
            batch = [self._story(root, 1, "src/a.py", "tests/test_shared.py"),
                     self._story(root, 2, "src/b.py", "tests/test_shared.py")]
            offer = s.delivery_mode_offer(root, batch)
            self.assertFalse(offer["parallel_available"])

    def test_a_test_file_only_overlap_denies_the_parallel_offer(self):
        s = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            batch = [self._story(root, 1, "src/a.py", "tests/test_shared.py"),
                     self._story(root, 2, "src/b.py", "tests/test_shared.py")]
            offer = s.delivery_mode_offer(root, batch)
            self.assertEqual(offer["groups"], [["US0001", "US0002"]])
            self.assertEqual(offer["modes"], ["sequential"])


class LanePartitionTests(_DeliveryModeFixture):
    """US0349: the plan emits a report-only file-disjoint lane partition, from the same
    machinery the delivery-mode offer uses, and it changes no plan decision."""

    def _no_affects(self, root, num):
        sd = root / "sdlc-studio" / "stories"
        sd.mkdir(parents=True, exist_ok=True)
        (sd / f"US{num:04d}-x.md").write_text(
            f"# US{num:04d}: x\n\n> **Status:** Draft\n> **Points:** 2\n", encoding="utf-8")
        return {"id": f"US{num:04d}", "path": str(sd / f"US{num:04d}-x.md"), "points": 2}

    def test_no_file_appears_in_two_lanes(self):
        """AC1. Overlapping Affects merge into one lane; disjoint ones split - and no file is ever
        shared across two lanes, computed from _unit_files (the same set the clusters use)."""
        s = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            # us1+us2 share src/shared.py (one lane); us3 is disjoint (its own lane)
            batch = [self._story(root, 1, "src/shared.py", "tests/test_a.py"),
                     self._story(root, 2, "src/shared.py", "tests/test_b.py"),
                     self._story(root, 3, "src/c.py", "tests/test_c.py")]
            part = s.lane_partition(root, batch)
            lanes = part["lanes"]
            # every file lives in at most one lane (shared WITHIN a lane is fine; across is not)
            seen: dict[str, int] = {}
            for i, lane in enumerate(lanes):
                for uid in lane:
                    for f in part["files_by_unit"][uid]:
                        if f in seen:
                            self.assertEqual(seen[f], i, f"{f} in lanes {seen[f]} and {i}")
                        seen[f] = i
            # the coupled pair is together, the disjoint one apart
            lane_of = {uid: i for i, lane in enumerate(lanes) for uid in lane}
            self.assertEqual(lane_of["US0001"], lane_of["US0002"])
            self.assertNotEqual(lane_of["US0001"], lane_of["US0003"])

    def test_the_partition_changes_nothing_else_in_the_plan(self):
        """AC2. The partition is a view, not an input: computing it leaves the delivery-mode
        decision (the batch, its groups, the offered modes) byte-identical."""
        s = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            batch = [self._story(root, 1, "src/a.py", "tests/test_a.py"),
                     self._story(root, 2, "src/b.py", "tests/test_b.py")]
            offer_before = s.delivery_mode_offer(root, batch)
            _ = s.lane_partition(root, batch)          # compute the report
            offer_after = s.delivery_mode_offer(root, batch)
            # the decision the offer records is unchanged by the report existing
            self.assertEqual(offer_before, offer_after)
            self.assertEqual(s.record_delivery_mode(offer_after, "parallel"),
                             s.record_delivery_mode(offer_before, "parallel"))

    def test_an_undeclared_unit_is_named_not_placed(self):
        """AC3. A unit that declares no Affects is unplaceable and NAMED, never dropped into a
        lane - an undeclared file is invisible to a collision check, so it cannot be assumed
        safe to sit beside anything."""
        s = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            batch = [self._story(root, 1, "src/a.py", "tests/test_a.py"),
                     self._no_affects(root, 2)]
            part = s.lane_partition(root, batch)
            self.assertIn("US0002", part["unplaceable"])
            placed = {uid for lane in part["lanes"] for uid in lane}
            self.assertNotIn("US0002", placed)          # not silently placed
            self.assertIn("US0001", placed)


class LaneExportTests(_DeliveryModeFixture):
    """US0350: each lane exports as a worklist the planner reads back; collision-freedom is
    asserted on the exported artefacts, not the in-memory structure that produced them."""

    def test_each_lane_round_trips_through_the_worklist_reader(self):
        """AC1. Each export is a `sprint plan --worklist`-readable file, and re-reading it
        reproduces exactly that lane's units."""
        s = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            batch = [self._story(root, 1, "src/a.py", "tests/test_a.py"),
                     self._story(root, 2, "src/b.py", "tests/test_b.py")]
            out = root / "lanes"
            res = s.export_lanes(root, batch, out)
            part = s.lane_partition(root, batch)
            self.assertEqual(len(res["lane_files"]), len(part["lanes"]))
            for path, lane in zip(res["lane_files"], part["lanes"]):
                units, _deps = s._worklist_units(root, path)
                self.assertEqual([u["id"] for u in units], lane)

    def test_the_exports_themselves_are_pairwise_disjoint(self):
        """AC2. Read the exports back and intersect the units' Affects pairwise across lanes:
        every pair is disjoint. The assertion is on the artefacts handed to teams."""
        s = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            batch = [self._story(root, 1, "src/shared.py", "tests/test_a.py"),
                     self._story(root, 2, "src/shared.py", "tests/test_b.py"),
                     self._story(root, 3, "src/c.py", "tests/test_c.py")]
            out = root / "lanes"
            res = s.export_lanes(root, batch, out)
            # files each exported lane actually touches, read back from disk
            lane_files_sets = []
            for path in res["lane_files"]:
                units, _ = s._worklist_units(root, path)
                fs: set[str] = set()
                for u in units:
                    fs |= set(s._unit_files(root, Path(u["path"]).read_text(encoding="utf-8")))
                lane_files_sets.append(fs)
            for i in range(len(lane_files_sets)):
                for j in range(i + 1, len(lane_files_sets)):
                    self.assertEqual(lane_files_sets[i] & lane_files_sets[j], set(),
                                     f"lanes {i} and {j} share a file")

    def test_the_undeclared_file_risk_is_stated_in_the_export(self):
        """AC3 (function leg). The caveat travels with every export artefact, not just the doc:
        disjointness is only as good as the declared Affects."""
        s = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            batch = [self._story(root, 1, "src/a.py", "tests/test_a.py"),
                     self._story(root, 2, "src/b.py", "tests/test_b.py")]
            out = root / "lanes"
            res = s.export_lanes(root, batch, out)
            for path in res["lane_files"]:
                self.assertIn("undeclared", Path(path).read_text(encoding="utf-8"))


class OverAppetiteReportTests(unittest.TestCase):
    """US0360: the close reports an accepted over-appetite batch as the over-commitment it was,
    not as the raised ceiling."""

    def test_the_close_states_the_overage_not_the_raised_ceiling(self) -> None:
        """AC1. A close of a run recorded 32 units against a standing 8 states exactly that,
        never 32/32."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root, appetite={"units": 32, "minutes": 960, "standing_units": 8,
                                         "standing_minutes": 240, "over_appetite": True})
            _close_story(root)
            mod = _load()
            out, err = io.StringIO(), io.StringIO()
            with _patch_close_steps(mod), \
                    contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                mod.main(["close", "--root", str(root)])       # scaffolds a retro and stops
            text = out.getvalue()
            self.assertIn("OVER APPETITE", text)
            self.assertIn("32 units against a standing appetite of 8", text)
            # the record must not read as though the batch fitted the ceiling it was given
            self.assertNotIn("standing appetite of 32", text)

    def test_a_within_appetite_close_reports_no_overage(self) -> None:
        """The complement: a run inside its standing appetite prints no overage line, so the
        line means something when it does appear."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _close_state(root, appetite={"units": 6, "minutes": 180, "standing_units": 8,
                                         "standing_minutes": 240, "over_appetite": False})
            _close_story(root)
            mod = _load()
            out, err = io.StringIO(), io.StringIO()
            with _patch_close_steps(mod), \
                    contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                mod.main(["close", "--root", str(root)])
            self.assertNotIn("OVER APPETITE", out.getvalue())


class HelpStatesBatchSizeTradeoffTests(unittest.TestCase):
    """US0397: help/sprint.md states the fixed-cost-versus-review-convergence trade-off from
    the measured rows and prescribes NO batch-size number."""

    HELP = SCRIPT.parent.parent / "help" / "sprint.md"

    def _norm(self) -> str:
        import re as _re
        return _re.sub(r"\s+", " ", self.HELP.read_text(encoding="utf-8")
                       .replace("*", "").replace("`", "")).lower()

    def test_it_states_the_trade_off_grounds_it_and_prescribes_no_number(self) -> None:
        h = self._norm()
        # AC1: both arms
        self.assertIn("fixed", h)
        self.assertIn("per point falls", h)
        self.assertTrue("convergence cost pulls the other way" in h or "cost pulls the other" in h)
        # AC2: grounded in the measured rows, count of sprints named
        self.assertIn("velocity.md", h)
        self.assertRegex(h, r"(one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s+"
                            r"(?:build\s+)?sprints")
        # AC3: no number prescribed
        self.assertTrue("no number is prescribed" in h or "fixes no optimum" in h)
        self.assertNotRegex(h, r"aim for \d+|target of \d+|keep (?:the )?batch(?:es)? (?:to|at|under) \d+")


class DeliveryModeBuildToolingCouplingTests(_DeliveryModeFixture):
    """US0416: build tooling and shared config couple the batch, not as ordinary files.

    Two units editing DIFFERENT tooling files still share the one gate that runs across every
    worktree, so a merge-clean file split is not parallel-safe. The batch must go sequential
    whenever any unit touches the DECLARED build-tooling set - never inferred from a name."""

    def test_a_unit_touching_build_tooling_is_never_parallel_safe(self):
        # AC1. src/a.py vs src/b.py are file-disjoint and would otherwise parallelise; the
        # second unit touching tools/ collapses the offer to sequential.
        s = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            batch = [self._story(root, 1, "src/a.py", "tests/test_a.py"),
                     self._story(root, 2, "tools/check_links.py", "tests/test_b.py")]
            offer = s.delivery_mode_offer(root, batch)
            self.assertFalse(offer["parallel_available"])
            self.assertEqual(offer["modes"], ["sequential"])
            self.assertIn("US0002", offer["build_tooling_coupled"])
            self.assertIn("build tooling", offer["reason"])
            with self.assertRaises(ValueError):
                s.record_delivery_mode(offer, "parallel")

    def test_two_units_editing_different_tooling_files_still_do_not_parallelise(self):
        # AC1. Distinct tooling files are still coupling: the gate spans both worktrees.
        s = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            batch = [self._story(root, 1, "tools/check_links.py", "tests/test_a.py"),
                     self._story(root, 2, "install.sh", "tests/test_b.py")]
            offer = s.delivery_mode_offer(root, batch)
            self.assertFalse(offer["parallel_available"])
            self.assertEqual(sorted(offer["build_tooling_coupled"]), ["US0001", "US0002"])

    def test_the_build_tooling_set_is_declared_not_inferred_by_name(self):
        # AC2. The set is an explicit declared constant. A file whose NAME merely looks like
        # config (a .yaml the set does not name) is NOT treated as tooling; a path the set
        # DOES declare is - so membership is by declaration, not by a filename shape.
        s = _load()
        self.assertIsInstance(s.BUILD_TOOLING_PATHS, tuple)
        self.assertIn("tools/", s.BUILD_TOOLING_PATHS)
        self.assertIn("package.json", s.BUILD_TOOLING_PATHS)
        # a lookalike name the declaration does not list is not tooling
        self.assertEqual(s._build_tooling_hits(["src/app.config.yaml"]), [])
        self.assertEqual(s._build_tooling_hits(["src/test_helpers.py"]), [])
        # a declared directory covers its subtree; a declared file matches exactly
        self.assertEqual(s._build_tooling_hits(["tools/tests/test_x.py"]),
                         ["tools/tests/test_x.py"])
        self.assertEqual(s._build_tooling_hits(["package.json"]), ["package.json"])

    def test_an_ordinary_disjoint_batch_still_parallelises(self):
        # Guard against over-reach: units touching only their own source/test files, none of
        # them tooling, must still be offered parallel.
        s = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            batch = [self._story(root, 1, "src/a.py", "tests/test_a.py"),
                     self._story(root, 2, "src/b.py", "tests/test_b.py")]
            offer = s.delivery_mode_offer(root, batch)
            self.assertTrue(offer["parallel_available"])
            self.assertEqual(offer["build_tooling_coupled"], [])

    def test_the_contract_is_documented_where_the_mode_is(self):
        # AC3. The build-tooling coupling is written where delivery mode is documented.
        doc = (Path(__file__).resolve().parents[2] / "reference-sprint.md").read_text(
            encoding="utf-8")
        section = doc.split("Delivery mode", 1)[1].split("##", 1)[0]
        self.assertIn("build tooling", section.lower())
        self.assertIn("declared", section.lower())


class DeliveryModeDeterminismTests(_DeliveryModeFixture):
    """US0409: the offer is deterministic and the plan states the mode and the alternative."""

    def test_the_same_batch_offers_the_same_modes_every_time(self):
        s = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            batch = [self._story(root, 1, "src/a.py", "tests/test_a.py"),
                     self._story(root, 2, "src/b.py", "tests/test_b.py")]
            a = s.delivery_mode_offer(root, batch)
            b = s.delivery_mode_offer(root, batch)
            self.assertEqual(a, b)

    def test_the_plan_states_the_mode_and_the_reason_for_the_alternative(self):
        s = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            batch = [self._story(root, 1, "src/a.py", "tests/test_a.py"),
                     self._story(root, 2, "src/b.py", "tests/test_b.py")]
            offer = s.delivery_mode_offer(root, batch)
            # both modes named, and the reason states the alternative is on the table
            self.assertIn("SEQUENTIAL", offer["reason"])
            self.assertIn("PARALLEL", offer["reason"])
            self.assertTrue(offer["reason"])


class _GoalReviewFixture(unittest.TestCase):
    """Shared setup for the goal-review tests: a project with its own review seats."""

    def _project(self, roles=("product", "engineering", "qa")):
        d = Path(tempfile.mkdtemp(prefix="goal_review_"))
        seats = d / "sdlc-studio" / "personas" / "seats"
        seats.mkdir(parents=True)
        for r in roles:
            (seats / f"{r}.md").write_text(f"<!-- role: {r} -->\n# {r}\n", encoding="utf-8")
        (d / "sdlc-studio" / ".local").mkdir(parents=True)
        return d

    def _record(self, s, root, *argv):
        import contextlib, io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            rc = s.main(["goal-review", "record", "--root", str(root), *argv])
        return rc, buf.getvalue()


class AmendGoalReviewTests(_GoalReviewFixture):
    """US0402: an amendment carries the requesting seat's verdict forward and records the trail."""

    def _seed_goal_a(self, s, root):
        return self._record(s, root, "--goal", "goal A",
                            "--seat", "product|yes|shipped|yes",
                            "--seat", "engineering|yes|shipped|yes",
                            "--seat", "qa|yes|shipped|yes")

    def test_amendment_carries_forward_the_satisfied_seats_verdict(self):
        s = _load()
        root = self._project()
        self._seed_goal_a(s, root)
        rc, _ = self._record(s, root, "--goal", "goal B", "--amend-from", "goal A",
                             "--requesting-seat", "engineering")
        self.assertEqual(rc, 0)
        status = s.goal_review_status(root, "goal B")
        self.assertTrue(status["reviewed"])                       # goal B is reviewed...
        self.assertIn("engineering", {x["seat"] for x in status["seats"]})  # ...for engineering

    def test_the_amend_round_records_prior_wording_and_requesting_seat(self):
        s = _load()
        root = self._project()
        self._seed_goal_a(s, root)
        self._record(s, root, "--goal", "goal B", "--amend-from", "goal A",
                     "--requesting-seat", "engineering")
        latest = s.goal_review_rounds(s.goal_review(root))[-1]
        self.assertEqual(latest["amended_from"], "goal A")
        self.assertEqual(latest["requesting_seat"], "engineering")

    def test_seats_not_satisfied_by_the_amendment_still_need_reconsult(self):
        s = _load()
        root = self._project()
        self._seed_goal_a(s, root)
        self._record(s, root, "--goal", "goal B", "--amend-from", "goal A",
                     "--requesting-seat", "engineering")
        status = s.goal_review_status(root, "goal B")
        self.assertEqual(status["needs_reconsult"], ["product", "qa"])   # engineering discharged

    def test_an_amendment_whose_requesting_seat_never_reviewed_the_prior_goal_is_refused(self):
        # The closing review caught this: a requesting seat with no prior verdict carries nothing,
        # producing a round that declares a requesting seat AND flags it needs_reconsult.
        s = _load()
        root = self._project()
        self._record(s, root, "--goal", "goal A", "--seat", "product|yes|shipped|yes")  # product only
        rc, out = self._record(s, root, "--goal", "goal B", "--amend-from", "goal A",
                               "--requesting-seat", "engineering")
        self.assertEqual(rc, 2)
        self.assertIn("nothing to carry", out.lower())
        # and nothing was written for goal B
        self.assertNotEqual(s.goal_review_rounds(s.goal_review(root))[-1]["goal"], "goal B")


class MaterialGoalChangeTests(_GoalReviewFixture):
    """US0403: a material change carries no verdict forward and records the operator's call."""

    def test_a_material_declaration_carries_no_verdict_forward(self):
        s = _load()
        root = self._project()
        self._record(s, root, "--goal", "goal A", "--seat", "engineering|yes|shipped|yes")
        self._record(s, root, "--goal", "goal B", "--amend-from", "goal A", "--material",
                     "--seat", "product|yes|shipped|yes")
        status = s.goal_review_status(root, "goal B")
        roles = {x["seat"] for x in status["seats"]}
        self.assertNotIn("engineering", roles)                    # nothing carried
        self.assertIn("engineering", status["needs_reconsult"])   # must review goal B afresh

    def test_the_change_classification_is_recorded_as_an_operator_declaration(self):
        s = _load()
        root = self._project()
        self._record(s, root, "--goal", "goal A", "--seat", "engineering|yes|shipped|yes")
        self._record(s, root, "--goal", "goal B", "--amend-from", "goal A", "--material",
                     "--seat", "product|yes|shipped|yes")
        self.assertEqual(s.goal_review_rounds(s.goal_review(root))[-1]["change_type"], "material")
        # and the amendment case records the other declaration
        self._record(s, root, "--goal", "goal C", "--amend-from", "goal B",
                     "--requesting-seat", "product")
        self.assertEqual(s.goal_review_rounds(s.goal_review(root))[-1]["change_type"], "amendment")


class SeatBriefEmitTests(unittest.TestCase):
    """US0404: the seat brief is composed deterministically and names the grooming state."""

    def _planned(self):
        d = Path(tempfile.mkdtemp(prefix="seat_brief_"))
        (d / "sdlc-studio" / ".local").mkdir(parents=True)
        plan = {"count": 3, "order": "priority",
                "sprint_goal": "make the bar real",
                "breakdown": {"ungroomed": [{"id": "US0001"}],
                              "clusters": [{"units": ["US0002", "US0003"]}]},
                "reachable_end_state": {"state": "Review", "basis": "two-role gate caps it"}}
        (d / "sdlc-studio" / ".local" / "sprint-plan.json").write_text(json.dumps(plan))
        (d / "sdlc-studio" / ".local" / "run-state.json").write_text(json.dumps(
            {"schema": 1, "run_id": "R", "sprint_goal": "make the bar real", "batch": []}))
        (d / "sdlc-studio" / ".local" / "lessons.md").write_text(
            "## L-0001: a repair masks the defect beside it\n- **Rule:** re-check the neighbour\n")
        return d

    def test_the_brief_is_derived_deterministically_from_the_batch(self):
        s = _load()
        d = self._planned()
        self.assertEqual(s.seat_brief(d), s.seat_brief(d))        # same batch -> same brief

    def test_the_brief_names_placeholder_acs_shared_clusters_and_end_state(self):
        s = _load()
        brief = s.seat_brief(self._planned())
        self.assertIn("US0001", brief)                            # placeholder-AC unit
        self.assertIn("US0002, US0003", brief)                    # the shared-file cluster
        self.assertIn("Review", brief)                            # reachable end state

    def test_the_brief_draws_failure_modes_from_the_lessons_registry(self):
        s = _load()
        brief = s.seat_brief(self._planned())
        self.assertIn("L-0001", brief)                            # this project's own lesson


class SeatBriefRecordedTests(_GoalReviewFixture):
    """US0405: the brief is stored in the same round as the verdicts and read back with it."""

    def test_the_brief_is_stored_with_the_recorded_verdicts(self):
        s = _load()
        root = self._project()
        self._record(s, root, "--goal", "goal A", "--seat", "engineering|yes|shipped|yes",
                     "--brief", "the batch has one placeholder-AC unit")
        latest = s.goal_review_rounds(s.goal_review(root))[-1]
        self.assertEqual(latest["brief"], "the batch has one placeholder-AC unit")

    def test_the_recorded_brief_is_readable_back_with_the_round(self):
        s = _load()
        root = self._project()
        self._record(s, root, "--goal", "goal A", "--seat", "engineering|yes|shipped|yes",
                     "--brief", "thin brief")
        # a round with NO brief is distinguishable from a thin one
        self._record(s, root, "--goal", "goal B", "--seat", "engineering|yes|shipped|yes")
        rounds = s.goal_review_rounds(s.goal_review(root))
        self.assertEqual(rounds[0].get("brief"), "thin brief")
        self.assertIsNone(rounds[1].get("brief"))


class GoalReviewFieldsFileTests(_GoalReviewFixture):
    """US0406: goal-review record reads seats from a fields-file, so a note quoting a command in
    backticks is stored verbatim rather than mangled by a shell."""

    def test_record_reads_seat_verdicts_from_a_fields_file(self):
        s = _load()
        root = self._project()
        (root / "f.json").write_text(json.dumps(
            {"goal": "goal A", "seats": [{"seat": "engineering", "achievable": "yes",
                                          "done_means": "shipped", "one_increment": "yes"}]}))
        rc, _ = self._record(s, root, "--fields-file", str(root / "f.json"))
        self.assertEqual(rc, 0)
        latest = s.goal_review_rounds(s.goal_review(root))[-1]
        self.assertIn("engineering", {x["seat"] for x in latest["seats"]})

    def test_a_note_with_backticks_is_stored_verbatim(self):
        s = _load()
        root = self._project()
        note = "held to `make check` and $(date) - no word deleted"
        (root / "f.json").write_text(json.dumps(
            {"goal": "goal A", "seats": [{"seat": "engineering", "achievable": "yes",
                                          "done_means": "shipped", "one_increment": "yes",
                                          "note": note}]}))
        rc, _ = self._record(s, root, "--fields-file", str(root / "f.json"))
        self.assertEqual(rc, 0)
        stored = s.goal_review_rounds(s.goal_review(root))[-1]["seats"][0]["note"]
        self.assertEqual(stored, note)                            # byte-for-byte


class SprintFieldsFileTests(unittest.TestCase):
    """US0392 AC2: `goal-verdict` takes its verdict and note from a fields-file, so a rationale
    carrying shell metacharacters is stored verbatim rather than interpreted by a shell."""

    def test_fields_file_goal_and_note_are_stored_verbatim(self) -> None:
        import contextlib, io, json
        s = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / ".local").mkdir(parents=True)
            (root / "sdlc-studio" / ".local" / "run-state.json").write_text(json.dumps(
                {"schema": 1, "run_id": "RUN-X", "sprint_goal": "make the bar real",
                 "outcome": "running", "batch": []}))
            hazard = "held to `make check` and $(date) as the bar"
            (root / "ff.json").write_text(json.dumps({"verdict": "achieved", "note": hazard}))
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                rc = s.main(["goal-verdict", "--fields-file", str(root / "ff.json"),
                             "--root", str(root)])
            self.assertEqual(rc, 0)
            state = json.loads((root / "sdlc-studio" / ".local" / "run-state.json").read_text())
            rec = state["sprint_goal_verdict"]
            self.assertEqual(rec["verdict"], "achieved")
            self.assertIn("`make check`", rec["note"])   # backtick survived
            self.assertIn("$(date)", rec["note"])         # command substitution stored verbatim

    def test_a_whitespace_only_note_is_refused_like_an_empty_one(self):
        # The closing review caught this: the emptiness check ran on the UNstripped note, so a
        # whitespace-only note passed the "a bare verdict is an assertion" guard.
        import contextlib, io
        s = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / ".local").mkdir(parents=True)
            (root / "sdlc-studio" / ".local" / "run-state.json").write_text(json.dumps(
                {"schema": 1, "run_id": "R", "sprint_goal": "g", "batch": []}))
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                rc = s.main(["goal-verdict", "--verdict", "achieved", "--note", "   ",
                             "--root", str(root)])
            self.assertEqual(rc, 2)
            self.assertNotIn("sprint_goal_verdict", json.loads(
                (root / "sdlc-studio" / ".local" / "run-state.json").read_text()))


class ThemedBatchNotAnObjectionTests(_GoalReviewFixture):
    """BG0270: `achievable=no` is an objection; `one_increment=no` is a classification. Folding
    them into one blocking predicate refused every themed batch and misreported the seats."""

    def _seats_all_achievable_but_themed(self, s, root):
        return self._record(s, root, "--goal", "clear the backlog",
                            "--seat", "product|yes|backlog at zero|no - a themed clearance batch",
                            "--seat", "engineering|yes|gate green throughout|no - twelve groups",
                            "--seat", "qa|yes|every AC red then green|no - themed")

    def test_one_increment_no_alone_does_not_refuse_the_plan(self):
        s = _load()
        root = self._project()
        self._seats_all_achievable_but_themed(s, root)
        status = s.goal_review_status(root, "clear the backlog")
        self.assertTrue(status["reviewed"])
        self.assertFalse(status["objected"])        # nobody objected to achievability
        self.assertEqual(status["objections"], [])
        self.assertEqual(len(status["themed"]), 3)  # ...and the classification is kept

    def test_an_achievable_no_still_refuses(self):
        s = _load()
        root = self._project()
        self._record(s, root, "--goal", "boil the ocean",
                     "--seat", "product|yes|shipped|yes",
                     "--seat", "engineering|no - not at this appetite|shipped|yes")
        status = s.goal_review_status(root, "boil the ocean")
        self.assertTrue(status["objected"])          # a real objection still blocks
        self.assertEqual([o["seat"] for o in status["objections"]], ["engineering"])

    def test_the_themed_batch_note_is_reported(self):
        import contextlib, io
        s = _load()
        root = self._project()
        self._seats_all_achievable_but_themed(s, root)
        status = s.goal_review_status(root, "clear the backlog")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            s._render_goal_review({"goal_review": status, "sprint_goal": "clear the backlog"})
        self.assertIn("THEMED BATCH", buf.getvalue())   # the information is not lost

    def test_the_refusal_message_never_misreports_achievability(self):
        s = _load()
        root = self._project()
        _, out = self._seats_all_achievable_but_themed(s, root)
        # the exact false sentence this bug produced, over seats that all said achievable=yes
        self.assertNotIn("judged it NOT achievable", out)
        self.assertIn("THEMED", out.upper())


class CloseGateOrderingTests(unittest.TestCase):
    """BG0279: the chain gates at step 4 while units sit at Review, then --apply-signoff moves
    them to Done. Conformance requires evidence at Done that Review does not, so a close could
    print `gate: ok` and leave the tree red for whoever committed next."""

    def _repo(self, verified: bool):
        d = Path(tempfile.mkdtemp(prefix="close_gate_"))
        st = d / "sdlc-studio" / "stories"
        st.mkdir(parents=True)
        (d / "sdlc-studio" / "epics").mkdir(parents=True)
        body = ("# US0001: a manual criterion\n\n> **Status:** Done\n> **Points:** 2\n"
                "> **Epic:** [EP0001: e](../epics/EP0001-e.md)\n\n"
                "## Acceptance Criteria\n\n### AC1: the doc states the rule\n\n"
                "- **Given** a reader\n- **Then** it is stated\n- **Verify:** manual\n")
        if verified:
            body += "- **Verified:** yes (2026-07-24)\n"
        (st / "US0001-x.md").write_text(body, encoding="utf-8")
        return d

    def test_the_gate_is_evaluated_after_the_done_transitions(self):
        # The unit is Done and owes its Verified annotation: the post-transition check must SEE
        # that, which the pre-transition gate structurally could not.
        s = _load()
        d = self._repo(verified=False)
        found = s._post_transition_conformance(d, units=["US0001"])
        self.assertTrue(found, "the post-transition check did not judge the Done state")
        self.assertIn("US0001", found[0])
        self.assertIn("verified", found[0])

    def test_a_close_that_would_leave_the_tree_red_reports_it(self):
        """The check reports what is ACTUALLY missing, not a blanket alarm.

        A Done story owes `verified` AND `critiqued`. Annotating the manual AC clears exactly
        `verified` and leaves `critiqued` outstanding - which is the honest answer, and proves
        the check reads real per-unit state rather than flagging every Done unit."""
        s = _load()
        without = s._post_transition_conformance(self._repo(verified=False), units=["US0001"])
        with_evidence = s._post_transition_conformance(self._repo(verified=True), units=["US0001"])
        self.assertIn("verified", without[0])
        self.assertNotIn("verified", with_evidence[0])   # the annotation cleared exactly that
        self.assertIn("critiqued", with_evidence[0])     # ...and nothing it did not earn

    def test_the_close_TAIL_actually_runs_the_check_not_just_the_helper(self):
        """LANE test, not a library test (LL0040). The three tests above call the helper
        directly, so deleting the call from `_apply_signoff_tail` would leave them all green -
        a mutation proved exactly that. This one drives the tail and asserts the report reaches
        stderr, which is the only thing that fixes the harm."""
        import contextlib, io
        s = _load()
        d = self._repo(verified=False)
        (d / "sdlc-studio" / ".local").mkdir(parents=True, exist_ok=True)
        state = {"run_id": "RUN-T", "batch": ["US0001"], "handoff": "", "outcome": "running"}
        buf = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(buf):
            s._apply_signoff_tail(d, state, units=["US0001"], retro_arg=None)
        out = buf.getvalue()
        self.assertIn("NOT conformant after the transitions", out)
        self.assertIn("US0001", out)

    def test_an_empty_scope_reports_NOTHING_not_the_whole_repo(self):
        """A BUG-ONLY batch yields no story units, and a truthiness escape then reported every
        non-conformant unit in the repo as though this close had caused it. `units=["US9999"]`
        passes either way, so it never caught this - the empty list is the discriminating case."""
        s = _load()
        d = self._repo(verified=False)          # holds a genuinely non-conformant unit
        self.assertTrue(s._post_transition_conformance(d, units=["US0001"]))   # control
        self.assertEqual(s._post_transition_conformance(d, units=[]), [])
        self.assertEqual(s._post_transition_conformance(d, units=None), [])

    def test_the_check_is_scoped_to_this_runs_units(self):
        # A close reports the state IT created, never the repo's pre-existing debt.
        s = _load()
        d = self._repo(verified=False)
        self.assertEqual(s._post_transition_conformance(d, units=["US9999"]), [])


class RefusedPlanLeavesNothingTests(unittest.TestCase):
    """BG0268: the forecast record and sprint-plan.json were written BEFORE open_run, so a batch
    open_run refused left both behind while run-state.json's own guarantee held."""

    def _repo(self):
        d = Path(tempfile.mkdtemp(prefix="refused_plan_"))
        (d / "sdlc-studio" / "bugs").mkdir(parents=True)
        (d / "sdlc-studio" / ".local").mkdir(parents=True)
        (d / "src").mkdir()
        (d / "src" / "a.py").write_text("# marker\n")
        (d / "sdlc-studio" / "bugs" / "BG0001-x.md").write_text(
            "# BG0001: x\n\n> **Status:** Open\n> **Severity:** High\n> **Points:** 2\n"
            "> **Affects:** src/a.py\n", encoding="utf-8")
        return d

    def _plan(self, s, root, *argv):
        import contextlib, io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            rc = s.main(["plan", "--bugs", "Open", "--root", str(root), *argv])
        return rc, buf.getvalue()

    def test_a_refused_open_run_leaves_no_plan_json_or_forecast(self):
        s = _load()
        root = self._repo()
        plan_json = root / "sdlc-studio" / ".local" / "sprint-plan.json"
        real_open = s.run_state.open_run
        try:
            def _refuse(*a, **k):
                raise s.run_state.DisjointBatchError("RUN-OTHER", "running", 3)
            s.run_state.open_run = _refuse
            rc, _ = self._plan(s, root, "--write")
            self.assertEqual(rc, 2)
        finally:
            s.run_state.open_run = real_open
        self.assertFalse(plan_json.exists(), "a refused plan left sprint-plan.json behind")
        forecasts = root / "sdlc-studio" / ".local" / "forecasts.json"
        if forecasts.exists():
            self.assertNotIn("BG0001", forecasts.read_text(encoding="utf-8"),
                             "a refused plan recorded a forecast for its batch")

    def test_a_successful_plan_still_writes_both(self):
        s = _load()
        root = self._repo()
        rc, _ = self._plan(s, root, "--write")
        self.assertEqual(rc, 0)
        self.assertTrue((root / "sdlc-studio" / ".local" / "sprint-plan.json").exists())
        self.assertTrue((root / "sdlc-studio" / ".local" / "run-state.json").exists())


class SeatBriefFreshnessTests(unittest.TestCase):
    """BG0277: the brief derived from the PERSISTED plan, but the review it informs gates
    `plan --write` - so on a new sprint it silently described the previous batch."""

    def _repo(self, plan_count, outcome):
        d = Path(tempfile.mkdtemp(prefix="brief_fresh_"))
        (d / "sdlc-studio" / ".local").mkdir(parents=True)
        (d / "sdlc-studio" / "stories").mkdir(parents=True)
        (d / "scripts").mkdir()
        (d / "scripts" / "m.py").write_text("# marker\n")
        (d / "sdlc-studio" / ".local" / "sprint-plan.json").write_text(json.dumps(
            {"count": plan_count, "order": "priority", "sprint_goal": "the OLD goal",
             "breakdown": {"ungroomed": [{"id": "US9999"}], "clusters": []},
             "reachable_end_state": {"state": "Review", "basis": "b"}}))
        (d / "sdlc-studio" / ".local" / "run-state.json").write_text(json.dumps(
            {"schema": 1, "run_id": "RUN-OLD", "sprint_goal": "the OLD goal",
             "outcome": outcome, "batch": []}))
        return d

    def test_the_brief_describes_the_batch_it_is_given_not_the_persisted_plan(self):
        s = _load()
        d = self._repo(plan_count=19, outcome="goal-reached")
        f = d / "sdlc-studio" / "stories" / "US0001-x.md"
        f.write_text("# US0001: x\n\n> **Status:** Draft\n> **Points:** 2\n"
                     "> **Affects:** scripts/m.py\n", encoding="utf-8")
        wl = d / "wl.txt"
        wl.write_text("US0001\n", encoding="utf-8")
        brief = s.seat_brief(d, worklist=str(wl))
        self.assertIn("1 unit(s)", brief)          # the batch it was GIVEN
        self.assertNotIn("19 unit(s)", brief)      # not the persisted one
        self.assertNotIn("US9999", brief)          # nor its grooming state

    def test_a_stale_plan_is_named_not_rendered_as_current(self):
        s = _load()
        d = self._repo(plan_count=19, outcome="goal-reached")   # the run that plan belongs to CLOSED
        brief = s.seat_brief(d)
        self.assertIn("NO CURRENT BATCH TO BRIEF", brief)
        self.assertIn("RUN-OLD", brief)
        self.assertNotIn("19 unit(s)", brief)      # the wrong batch is never rendered

    def test_a_live_run_still_briefs_from_its_own_plan(self):
        s = _load()
        d = self._repo(plan_count=19, outcome="running")        # unregressed happy path
        brief = s.seat_brief(d)
        self.assertIn("19 unit(s)", brief)
        self.assertNotIn("NO CURRENT BATCH", brief)


class ReviewAnchorRefreshTests(unittest.TestCase):
    """BG0275: only the BLOCKED close path touched the review anchor, so a successful close left
    the previous run's state standing - including a sign-off that had already landed."""

    def _repo(self, anchor_text=None):
        d = Path(tempfile.mkdtemp(prefix="anchor_"))
        (d / "sdlc-studio" / "reviews").mkdir(parents=True)
        if anchor_text is not None:
            (d / "sdlc-studio" / "reviews" / "LATEST.md").write_text(anchor_text, encoding="utf-8")
        return d

    def test_the_review_anchor_step_is_WIRED_INTO_the_close_chain(self):
        """LANE test (LL0040). The tests above call refresh_review_anchor directly, so deleting
        `review-anchor` from _CLOSE_CHAIN left the whole suite green - a mutation proved it. This
        asserts the step is in the chain AND that a dispatchable handler exists for it."""
        s = _load()
        self.assertIn("review-anchor", s._CLOSE_CHAIN)
        self.assertTrue(callable(getattr(s, "_close_review_anchor", None)),
                        "the chain names a step with no handler to dispatch to")

    def test_the_signoff_tail_restamps_the_anchor_as_RECORDED(self):
        """The anchor must not say OWED on the close that records the sign-off. The chain stamps
        at step 7 while units are still at Review, so the tail re-stamps once they are Done."""
        import contextlib, io, json
        s = _load()
        d = Path(tempfile.mkdtemp(prefix="restamp_"))
        (d / "sdlc-studio" / "reviews").mkdir(parents=True)
        (d / "sdlc-studio" / ".local").mkdir(parents=True)
        (d / "sdlc-studio" / "reviews" / "LATEST.md").write_text(
            "# Reviews - LATEST (anchor)\n\nprose\n", encoding="utf-8")
        state = {"run_id": "RUN-T", "batch": [], "handoff": "", "outcome": "goal-reached"}
        (d / "sdlc-studio" / ".local" / "run-state.json").write_text(json.dumps(state))
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            s._apply_signoff_tail(d, state, units=[], retro_arg=None)
        text = (d / "sdlc-studio" / "reviews" / "LATEST.md").read_text(encoding="utf-8")
        self.assertIn("RUN-T", text)
        self.assertIn("RECORDED", text)          # an empty batch owes nothing
        self.assertNotIn("OWED", text)

    def test_a_successful_close_states_this_runs_outcome_not_the_previous_one(self):
        s = _load()
        stale = ("# Reviews - LATEST (anchor)\n\n"
                 "> **RUN-OLD delivered 43 units.** Sign-off is owed and is the operator's.\n\n"
                 "## Where the pipeline is\n\nnarrative that must survive\n")
        d = self._repo(stale)
        s.refresh_review_anchor(d, "RUN-NEW", "goal-reached", 19, signoff_owed=False)
        text = (d / "sdlc-studio" / "reviews" / "LATEST.md").read_text(encoding="utf-8")
        self.assertIn("RUN-NEW closed goal-reached", text)
        self.assertIn("Sign-off is RECORDED", text)          # states that nothing is owed
        self.assertIn("narrative that must survive", text)   # the prose is untouched

    def test_the_block_is_replaced_in_place_not_appended_on_each_close(self):
        s = _load()
        d = self._repo("# Reviews - LATEST (anchor)\n\nprose\n")
        s.refresh_review_anchor(d, "RUN-A", "goal-reached", 5, signoff_owed=True)
        s.refresh_review_anchor(d, "RUN-B", "partial", 7, signoff_owed=False)
        text = (d / "sdlc-studio" / "reviews" / "LATEST.md").read_text(encoding="utf-8")
        self.assertEqual(text.count(s.ANCHOR_BEGIN), 1)      # one block, not two
        self.assertIn("RUN-B closed partial", text)
        self.assertNotIn("RUN-A", text)

    def test_an_owed_signoff_is_named_and_a_recorded_one_is_stated_plainly(self):
        s = _load()
        owed = s.anchor_status_block("RUN-X", "goal-reached", 3, signoff_owed=True)
        done = s.anchor_status_block("RUN-X", "goal-reached", 3, signoff_owed=False)
        self.assertIn("OWED", owed)
        self.assertIn("RECORDED", done)
        self.assertNotEqual(owed, done)   # the reader never has to diff it against the run state


class RateProvenanceExhaustiveTests(unittest.TestCase):
    """BG0278: the provenance lookup was two keys wide with a docstring proving the domain closed.
    Two later features each added a source; three of five crashed at an operator's plan."""

    def _render(self, s, source):
        import contextlib, io
        tf = {"rate_refused": "the record refused", "rate_source": source,
              "rate_units": 0, "rate_out_of_sample": []}
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            s._render_rate_provenance(tf)
        return buf.getvalue()

    def test_a_fixed_fit_rate_source_with_a_refused_record_renders(self):
        s = _load()
        out = self._render(s, s.RATE_FIXED_FIT)          # this raised KeyError before the fix
        self.assertIn("fitted fixed-term marginal", out)

    def test_every_rate_source_is_handled(self):
        # Enumerated FROM THE MODULE, not from a list kept beside it - a list would drift exactly
        # the way the original two-key lookup did.
        s = _load()
        sources = sorted({v for k, v in vars(s).items()
                          if k.startswith("RATE_") and isinstance(v, str)})
        self.assertGreaterEqual(len(sources), 5, "the enumeration found nothing to judge")
        for src in sources:
            with self.subTest(rate_source=src):
                self.assertIn(src, s._RATE_STOOD_INSTEAD,
                              f"rate source {src!r} has no provenance sentence - add one to "
                              f"_RATE_STOOD_INSTEAD rather than letting it reach an operator")
                out = self._render(s, src)
                self.assertTrue(out.strip(), f"{src} rendered nothing")
                self.assertNotIn("unmapped rate source", out)


class ClosePreflightDriftTests(unittest.TestCase):
    """US0389: a drifted installed copy is one named blocker in the same single pass.

    Borrows the stubbed-gate fixture above (without inheriting its tests), so this asserts
    what the pre-flight COMPOSES rather than re-testing the gate.
    """

    _mod = ClosePreflightTests._mod
    _retro = ClosePreflightTests._retro

    def setUp(self) -> None:
        if shutil.which("rsync") is None:
            self.skipTest("rsync not on PATH")
        import test_status
        if not test_status._FORWARD_PORT.is_file():
            self.skipTest("tools/forward-port.sh not present (consuming project)")

    def test_installed_copy_drift_is_a_named_blocker_with_the_mirror_remedy(self) -> None:
        import os
        import test_status
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as h:
            root = Path(d)
            mod = self._mod(root, units=["US0101"], verdicts={"US0101": {"verdict": "APPROVE"}},
                            evidence=("US0101",), signoffs=("US0101",))
            rid = self._retro(root)
            with unittest.mock.patch.dict(os.environ, {"HOME": h}):
                # otherwise ready: without the drift this close has nothing outstanding
                self.assertTrue(mod.close_preflight(root, rid)["ready"])
                test_status._dev_repo_with_check(root)
                target = test_status._installed_copy(Path(h))
                target.joinpath("SKILL.md").write_text("# stale\n", encoding="utf-8")
                target.joinpath("scripts", "a.py").write_text("x = 1\n", encoding="utf-8")
                target.joinpath("stale-one.md").write_text("old\n", encoding="utf-8")
                res = mod.close_preflight(root, rid)
            self.assertFalse(res["ready"])
            named = [b for b in res["blockers"] if b["stage"] == "installed-copy"]
            self.assertEqual(len(named), 1, res["blockers"])
            self.assertIn("2 file(s)", named[0]["detail"])           # the measured count
            self.assertIn("forward-port.sh --yes", named[0]["remedy"])


class CloseStampRungTests(unittest.TestCase):
    """The close's anchor stamp told a DESIGN rung that sign-off was owed to reach Done.

    Nothing in that rung was going to Done: a design rung grooms stories, its units correctly
    end at Ready, and their acceptance criteria are correctly RED - that is the bar it exists to
    prove. The stamp lands in the one file every fresh session is ordered to read first, so a
    false owed-action arrives exactly where there is no other context to correct it.
    """

    def test_a_design_rung_is_not_told_it_owes_a_done_signoff(self) -> None:
        sprint = _load()
        block = sprint.anchor_status_block("RUN-X", "stopped", 18, True, rung="design")
        self.assertNotIn("two-role gate holds Done", block)
        self.assertIn("design", block)
        self.assertIn("no Done sign-off is owed", block)

    def test_a_build_rung_still_states_the_owed_signoff(self) -> None:
        """This fix must NARROW the claim, not remove it. A build rung past the two-role
        cutoff still owes the operator a signature, and the stamp must still say so."""
        sprint = _load()
        block = sprint.anchor_status_block("RUN-Y", "goal-reached", 28, True, rung="done")
        self.assertIn("**Sign-off is OWED and is the operator's**", block)
        self.assertIn("two-role gate holds Done", block)
        # and a build rung whose sign-off HAS landed says so rather than staying silent
        done = sprint.anchor_status_block("RUN-Y", "goal-reached", 28, False, rung="done")
        self.assertIn("**Sign-off is RECORDED**", done)

    def test_the_default_is_the_build_rung(self) -> None:
        """An omitted rung must behave as it always did. A caller that has not been updated
        cannot be allowed to silently lose the owed-sign-off line."""
        sprint = _load()
        self.assertIn("two-role gate holds Done",
                      sprint.anchor_status_block("RUN-Z", "goal-reached", 3, True))


class ApplySignoffBatchCoverageTests(unittest.TestCase):
    """`--apply-signoff` fans into story units only, and the assumption that made that safe -
    that a bug or CR in a mixed batch is already terminal by the time the close runs - was
    measured FALSE: a 28-unit batch closed `goal-reached` with its 10 bugs still Open while the
    handoff the same close wrote said "10 remaining"."""

    def _repo(self, d: str, units: dict[str, tuple[str, str]]) -> Path:
        """units: {id: (kind_dir, status)} written as minimal artefacts."""
        root = Path(d)
        for uid, (kind_dir, status) in units.items():
            folder = root / "sdlc-studio" / kind_dir
            folder.mkdir(parents=True, exist_ok=True)
            (folder / f"{uid}-x.md").write_text(
                f"# {uid}: x\n\n> **Status:** {status}\n\n\n## Acceptance Criteria\n\n- [ ] the unit behaves\n", encoding="utf-8")
        return root

    def test_bugs_in_the_batch_are_transitioned_or_named(self) -> None:
        """AC1. A non-story batch unit that is not terminal must be NAMED with the status it
        actually holds - measured from the artefact, never assumed."""
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, {
                "BG0001": ("bugs", "Open"),        # not terminal -> must be named
                "BG0002": ("bugs", "Fixed"),       # terminal -> must NOT be named
                "US0001": ("stories", "Review"),   # story -> the fan-out reaches it
            })
            out = sprint._batch_unfanned_units(root, ["BG0001", "BG0002", "US0001"])
        ids = [u[0] for u in out]
        self.assertIn("BG0001", ids, "an Open bug in the batch must be named, not skipped")
        self.assertNotIn("BG0002", ids, "a terminal bug is not outstanding")
        self.assertNotIn("US0001", ids, "a story is reached by the fan-out itself")
        self.assertEqual(out[0][2], "Open", "the status must be the one it actually holds")

    def test_outcome_and_handoff_agree_on_the_delivered_count(self) -> None:
        """AC2. The count the close reports and the count outstanding must be derivable from
        one measurement, so a `goal-reached` cannot be read over a batch that is not done."""
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, {
                "BG0001": ("bugs", "Open"), "BG0002": ("bugs", "Open"),
                "US0001": ("stories", "Review"),
            })
            batch = ["BG0001", "BG0002", "US0001"]
            unfanned = sprint._batch_unfanned_units(root, batch)
            stories = sprint._batch_story_units(root, batch)
        # 3 units: 1 the fan-out reaches, 2 it does not. No unit may fall in neither set
        # unaccounted for - that gap is how 10 bugs went missing from a 28-unit close.
        self.assertEqual(len(stories) + len(unfanned), len(batch),
                         "every batch unit is either fanned into or reported outstanding")

    def test_the_FANOUT_names_the_unfanned_units(self) -> None:
        """The lane test, not the helper test. Mutating the CALL SITE - `unfanned = []` - left
        every helper test green, because a function that returns the right answer to nobody
        proves nothing. This drives `_apply_signoff` itself and reads what it printed."""
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, {
                "BG0001": ("bugs", "Open"),
                "US0001": ("stories", "Review"),
            })
            state = {"run_id": "RUN-T", "batch": ["BG0001", "US0001"], "outcome": "goal-reached"}
            err, out = io.StringIO(), io.StringIO()
            with contextlib.redirect_stderr(err), contextlib.redirect_stdout(out):
                try:
                    sprint._apply_signoff(str(root), state, principal="op",
                                          author_default="author")
                except Exception:  # noqa: BLE001 - the fixture lacks the close's machinery
                    pass            # the assertion is on what it PRINTED before that
        printed = err.getvalue() + out.getvalue()
        self.assertIn("BG0001", printed,
                      "an Open bug in the batch must be NAMED, not silently skipped")
        self.assertIn("NOT reached", printed)

    def test_an_unknown_id_is_not_silently_counted_as_delivered(self) -> None:
        """A batch id with no artefact behind it must not read as terminal by default."""
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, {"US0001": ("stories", "Review")})
            out = sprint._batch_unfanned_units(root, ["BG9999"])
        self.assertEqual(out, [], "an id with no artefact is not claimed as an outstanding unit")


class CloseDoesNotForecloseSignoffTests(unittest.TestCase):
    """`sprint close` without `--apply-signoff` SEALS the run, and the sprint-level review the
    follow-up sign-off needs cannot be recorded against a sealed run. The refusal said so and
    offered "or reopen it" - a remedy with no implementation - so the documented two-invocation
    close flow could not be completed once the first invocation had run."""

    def _closed(self, root: Path):
        from lib import run_state
        state = run_state.open_run(root, batch=["US0001"], goal="done")
        run_state.close_run(root, "goal-reached", handoff="HO-0001")
        self._run_id = state["run_id"]
        return run_state

    def test_the_review_can_still_be_recorded_after_the_brief_invocation(self) -> None:
        """AC1. After the brief-producing close, the run can be reopened so the review the
        sign-off requires can still be recorded against it."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / ".local").mkdir(parents=True)
            rs = self._closed(root)
            self.assertNotEqual(rs.read(root).get("outcome"), "running")
            rs.reopen_run(root, "record the sprint-level review the sign-off needs")
            state = rs.read(root)
        self.assertEqual(state["outcome"], "running")
        self.assertIsNone(state["ended_at"], "a reopened run must not still carry an end time")
        self.assertEqual(state["reopened"][0]["reason"],
                         "record the sprint-level review the sign-off needs")

    def test_every_named_remedy_is_a_real_command(self) -> None:
        """AC2. The refusal offers a reopen; a refusal that names a remedy which does not exist
        is worse than one that names none, because it sends the reader looking."""
        from lib import run_state
        self.assertTrue(hasattr(run_state, "reopen_run"))
        sprint = _load()
        self.assertTrue(hasattr(sprint, "cmd_reopen"))

    def test_a_reopen_without_a_reason_is_refused(self) -> None:
        """A run that can be silently reopened is a run whose closure means nothing."""
        from lib import run_state
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / ".local").mkdir(parents=True)
            self._closed(root)
            with self.assertRaises(ValueError):
                run_state.reopen_run(root, "   ")

    def test_reopening_an_open_run_is_refused(self) -> None:
        from lib import run_state
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / ".local").mkdir(parents=True)
            run_state.open_run(root, batch=["US0001"], goal="done")
            with self.assertRaises(ValueError):
                run_state.reopen_run(root, "no reason to")

    def test_the_archived_close_record_is_not_rewritten(self) -> None:
        """The archive is the evidence of what was claimed at the close. Rewriting it to match
        a later correction is exactly the failure this project exists to refuse."""
        from lib import run_state
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / ".local").mkdir(parents=True)
            self._closed(root)
            archived_before = run_state.read_archived(root, self._run_id)
            run_state.reopen_run(root, "late review")
            archived_after = run_state.read_archived(root, self._run_id)
        self.assertEqual(archived_before, archived_after,
                         "reopening must not rewrite the archived close record")
        self.assertEqual(archived_after.get("outcome"), "goal-reached")


class GoalAwareBreakdownTests(unittest.TestCase):
    """D0062: the breakdown gate distinguishes the rung it is gating. A design rung exists to
    PRODUCE the grooming, so refusing it for the absence of what it produces is a circularity -
    the debt could then only be cleared by unbatched hand-work, which is the ad-hoc work the
    engagement floor exists to catch. Clearing it once cost 27 hand-edited artefacts."""

    def _args(self, goal: str):
        return types.SimpleNamespace(goal=goal, root=".")

    def test_an_ungroomed_batch_is_still_refused_at_goal_done(self) -> None:
        """AC1, and the one that must not weaken. D0062 NARROWS the gate; it does not remove
        it. A build rung over ungroomed units is the false authority the gate abolished."""
        sprint = _load()
        self.assertTrue(sprint._ungroomed_blocks_at(self._args("done")))

    def test_the_same_batch_is_accepted_at_goal_design(self) -> None:
        """AC2."""
        sprint = _load()
        self.assertFalse(sprint._ungroomed_blocks_at(self._args("design")))

    def test_the_size_and_affects_gates_bind_at_the_design_rung_too(self) -> None:
        """AC3. The exemption is for ungroomed ACs ONLY. A design rung cannot forecast an
        unsized unit either, and cannot place one whose collisions are invisible."""
        sprint = _load()
        self.assertTrue(sprint._oversized_blocks_at(self._args("design")))
        self.assertTrue(sprint._oversized_blocks_at(self._args("done")))

    def test_an_unknown_goal_blocks_like_a_build(self) -> None:
        """Fail-safe: only the design rung is exempt, and only when it says so. An absent or
        unrecognised goal must not become an accidental escape."""
        sprint = _load()
        for goal in (None, "", "DONE", "triage", "nonsense"):
            with self.subTest(goal=goal):
                self.assertTrue(sprint._ungroomed_blocks_at(self._args(goal)))


def _ungroomed_marker() -> str:
    """The shipped ungroomed marker, read from the module that defines it - never a copy. A
    fixture carrying its own spelling would keep passing after the real token changed."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from lib import sdlc_md as _md
    return _md.UNGROOMED_AC_TOKEN


class GroomingReportTests(unittest.TestCase):
    """The counterweight D0062 requires. Letting a design rung plan over an ungroomed batch is
    only safe if the close then says what it produced - otherwise "this rung will groom them" is
    a promise nobody checks."""

    def _repo(self, d: str, stories: dict[str, str]) -> Path:
        root = Path(d)
        folder = root / "sdlc-studio" / "stories"
        folder.mkdir(parents=True)
        for uid, acs in stories.items():
            (folder / f"{uid}-x.md").write_text(
                f"# {uid}: x\n\n> **Status:** Ready\n\n## Acceptance Criteria\n\n{acs}\n",
                encoding="utf-8")
        return root

    def test_the_close_reports_the_grooming_it_produced(self) -> None:
        """AC1."""
        sprint = _load()
        real = "### AC1: a real one\n\n- **Given** x\n- **When** y\n- **Then** z\n- **Verify:** manual\n"
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, {"US0001": real, "US0002": _ungroomed_marker()})
            rep = sprint.grooming_report(root, ["US0001", "US0002"])
        self.assertEqual(rep["total"], 2)
        self.assertEqual(rep["groomed"], 1)
        self.assertEqual(rep["names"], ["US0002"])
        line = sprint.render_grooming_report(rep)
        self.assertIn("1/2 groomed", line)
        self.assertIn("US0002", line)

    def test_a_rung_that_groomed_nothing_is_reported_not_passed(self) -> None:
        """AC2. Accepting an ungroomed batch and grooming none of it is exactly the abuse the
        relaxation invites, so it must be the loudest thing the close says about the rung."""
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, {"US0001": _ungroomed_marker(),
                                  "US0002": _ungroomed_marker()})
            rep = sprint.grooming_report(root, ["US0001", "US0002"])
        line = sprint.render_grooming_report(rep)
        self.assertIn("NOTHING WAS GROOMED", line)
        self.assertEqual(rep["groomed"], 0)

    def test_a_fully_groomed_rung_says_none_outstanding(self) -> None:
        sprint = _load()
        real = "### AC1: a real one\n\n- **Given** x\n- **When** y\n- **Then** z\n- **Verify:** manual\n"
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, {"US0001": real})
            line = sprint.render_grooming_report(sprint.grooming_report(root, ["US0001"]))
        self.assertIn("none outstanding", line)
        self.assertNotIn("NOTHING WAS GROOMED", line)


class DisclosureTests(unittest.TestCase):
    """AC2 of US0428: the close is what the operator reads at the moment of the decision, so
    the disclosure has to appear there and not only in a report they must know to generate."""

    def test_the_close_output_discloses_delegated_signoffs(self) -> None:
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / "reviews").mkdir(parents=True)
            import critic
            critic.record_verdict(root, "US0001", "approve", reviewer="qa-seat",
                                  author="builder")
            critic.record_signoff(root, "US0001", principal="operator", author="builder",
                                  delegate="qa-seat", boundary="its own agent context")
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                sprint._disclose_delegated_signoffs(str(root))
        printed = err.getvalue()
        self.assertIn("US0001", printed)
        self.assertIn("NOT by an independent reviewer", printed)

    def test_a_close_with_no_delegated_signoffs_prints_nothing(self) -> None:
        """The control: a disclosure that fires on every close is noise, and noise is skipped."""
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / "reviews").mkdir(parents=True)
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                sprint._disclose_delegated_signoffs(str(root))
        self.assertEqual(err.getvalue(), "")


class TestStrategyTests(unittest.TestCase):
    """D0060 / RFC0049 option C. Planning decided WHAT to build and said nothing about HOW each
    unit would be proved, so proof strategy was settled mid-build by whoever held the keyboard -
    which is how this project keeps shipping a test that decorates code rather than pinning it,
    and catching it only by mutating afterwards."""

    TSD = """# TSD

## Test Levels

### Unit Testing

Covers `alpha.py` and `beta.py`.

### Mutation Testing (assertion integrity)

Covers `gate.py`.

### Security Testing

Covers `auth.py`.

## Next Section
"""

    def _repo(self, d: str, units: dict[str, str], tsd: str | None = None) -> Path:
        root = Path(d)
        (root / "sdlc-studio" / "stories").mkdir(parents=True)
        (root / "sdlc-studio" / "tsd.md").write_text(
            self.TSD if tsd is None else tsd, encoding="utf-8")
        for uid, affects in units.items():
            (root / "sdlc-studio" / "stories" / f"{uid}-x.md").write_text(
                f"# {uid}: x\n\n> **Status:** Ready\n> **Affects:** {affects}\n",
                encoding="utf-8")
        return root

    def test_the_plan_names_the_tsd_risk_areas_the_batch_touches(self) -> None:
        """AC1, resolved from the units' Affects against the document - not from the QA seat's
        WSJF score, which is collapsed into an ordering number and discarded."""
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, {"US0001": "alpha.py", "US0002": "gate.py"})
            strat = sprint.test_strategy(root, ["US0001", "US0002"])
        self.assertIn("Unit Testing", strat["areas"])
        self.assertIn("Mutation Testing (assertion integrity)", strat["areas"])
        self.assertNotIn("Security Testing", strat["areas"], "an untouched area is not reported")

    def test_no_risk_area_is_stated_explicitly_not_left_blank(self) -> None:
        """AC2. An empty section is indistinguishable from a lane that did not run, which is
        the reporting failure this project has already had to repair once."""
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, {"US0001": "docs/readme.md"})
            lines = sprint.render_test_strategy(sprint.test_strategy(root, ["US0001"]))
        self.assertTrue(any("touches NO TSD risk area" in ln for ln in lines))

    def test_a_newly_added_risk_area_appears_without_a_code_change(self) -> None:
        """AC3. The strategy is derived from the DOCUMENT at plan time. A list baked into the
        planner would be a second copy of the TSD, and the two would drift - the failure EP0071
        spent a sprint repairing."""
        sprint = _load()
        extended = self.TSD.replace("## Next Section",
                                    "### Chaos Testing\n\nCovers `chaos.py`.\n\n## Next Section")
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, {"US0001": "chaos.py"}, tsd=extended)
            strat = sprint.test_strategy(root, ["US0001"])
        self.assertIn("Chaos Testing", strat["areas"])

    def test_a_missing_tsd_is_unavailable_not_empty(self) -> None:
        """'No areas' and 'no document' are different answers and only one of them is safe."""
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, {"US0001": "alpha.py"}, tsd="# TSD\n\nno levels here\n")
            strat = sprint.test_strategy(root, ["US0001"])
        self.assertFalse(strat["available"])
        self.assertIn("NOT the same as a batch that touches nothing", strat["why"])


class ProofRequirementTests(unittest.TestCase):
    """AC set for US0420: each unit carries the proof its band requires, and coverage the TSD
    demands but the batch omits is flagged."""

    def test_each_unit_carries_the_proof_its_band_requires(self) -> None:
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = TestStrategyTests()._repo(d, {"US0001": "gate.py", "US0002": "alpha.py"})
            strat = sprint.test_strategy(root, ["US0001", "US0002"])
        self.assertIn("mutation", strat["units"]["US0001"])
        self.assertEqual(strat["units"]["US0002"], ["unit"])

    def test_the_close_reports_a_claimed_proof_the_evidence_does_not_show(self) -> None:
        """AC3. A stated intent nobody checks at the end is a comment - the whole value of
        writing the proof requirement at plan time is being measured against it."""
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = TestStrategyTests()._repo(d, {"US0001": "gate.py", "US0002": "alpha.py"})
            gaps = sprint.claimed_proof_gaps(root, ["US0001", "US0002"])
        self.assertEqual(gaps, ["US0001"],
                         "the unit whose band demanded mutation, with no mutation evidence")
        self.assertNotIn("US0002", gaps,
                         "a unit whose band demands no mutation cannot be in arrears for it")

    def test_a_band_nobody_can_check_is_not_reported_as_a_gap(self) -> None:
        """Claiming a unit failed a bar that cannot be measured is the false precision this
        project refuses. Only the mutation band is mechanically checkable today."""
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = TestStrategyTests()._repo(d, {"US0001": "auth.py"})   # Security band
            self.assertEqual(sprint.claimed_proof_gaps(root, ["US0001"]), [])

    def test_demanded_coverage_the_batch_omits_is_flagged(self) -> None:
        """A plan that silently omits demanded coverage cannot be found by reading the batch."""
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = TestStrategyTests()._repo(d, {"US0001": "alpha.py"})
            strat = sprint.test_strategy(root, ["US0001"])
        self.assertIn("Security Testing", strat["gaps"])
        self.assertNotIn("Unit Testing", strat["gaps"], "a delivered area is not a gap")


class StaleTsdTests(unittest.TestCase):
    """A strategy review against a rotted document produces confident wrong answers."""

    def test_a_current_tsd_passes_on_comparison_not_on_a_marker(self) -> None:
        """The verdict is a comparison of commit times, never a freshness stamp anyone can
        write: a stamp asserts currency, it does not establish it."""
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)   # not a git repo: staleness is UNKNOWN, not False
            verdict = sprint.tsd_staleness(root)
        self.assertFalse(verdict["known"])
        self.assertIn("not the same as fresh", verdict["why"])

    def test_a_stale_tsd_is_reported_before_it_is_used(self) -> None:
        """Order matters: a reader who sees the areas before being told the document is rotted
        has already believed them."""
        sprint = _load()
        src = inspect.getsource(sprint._print_test_strategy)
        self.assertLess(src.index("tsd_staleness"), src.index("render_test_strategy"))


class StrategyScopedMutationTests(unittest.TestCase):
    """US0422: the stated strategy names which units are worth mutating, replacing the blanket
    close-scoped sweep that spent its ceiling on whatever it reached first."""

    def test_the_run_mutates_the_units_the_strategy_named(self) -> None:
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = TestStrategyTests()._repo(d, {"US0001": "gate.py", "US0002": "alpha.py"})
            targets = sprint.strategy_mutation_targets(root, ["US0001", "US0002"])
        self.assertEqual(targets, ["US0001"],
                         "only the unit whose band demands mutation is named")

    def test_an_unavailable_strategy_names_nothing_rather_than_everything(self) -> None:
        """Fail-safe direction: an underivable strategy must not silently promote the whole
        batch to mutation, which would be the blanket sweep under a new name."""
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = TestStrategyTests()._repo(d, {"US0001": "gate.py"},
                                             tsd="# TSD\n\nno levels\n")
            self.assertEqual(sprint.strategy_mutation_targets(root, ["US0001"]), [])


class PlanFindingDispositionTests(unittest.TestCase):
    """The retro already enforces file-or-decline and silence is not an answer there. A plan
    critic whose findings can be ignored is advice nobody has to take."""

    def test_write_is_refused_while_a_finding_is_undispositioned(self) -> None:
        """AC1."""
        sprint = _load()
        import critic
        rep = critic.plan_critique(["US0001"],
                                   {"scope": [{"title": "already in stdlib", "disposition": ""}]})
        msg = sprint.plan_critic_refusal(rep)
        self.assertIn("REFUSED", msg)
        self.assertIn("already in stdlib", msg, "the finding must be named")
        self.assertIn("Nothing was written", msg)

    def test_a_decline_without_a_real_reason_is_refused(self) -> None:
        """AC2. A decline whose reason is a placeholder records that someone clicked past it,
        which is worse than no record because it looks like a decision."""
        sprint = _load()
        import critic
        for disp in ("declined", "declined:", "declined: {{why}}", "   "):
            with self.subTest(disposition=disp):
                rep = critic.plan_critique(
                    ["US0001"], {"scope": [{"title": "t", "disposition": disp}]})
                self.assertIn("REFUSED", sprint.plan_critic_refusal(rep))

    def test_a_real_disposition_lets_the_plan_proceed(self) -> None:
        """The control: a gate that refuses everything is a gate nobody can satisfy."""
        sprint = _load()
        import critic
        for disp in ("BG0123", "declined: the stdlib version does not handle the empty case"):
            with self.subTest(disposition=disp):
                rep = critic.plan_critique(
                    ["US0001"], {"scope": [{"title": "t", "disposition": disp}]})
                self.assertEqual(sprint.plan_critic_refusal(rep), "")


def _derivable_cr(root: Path, cr_num: int = 900, ep_num: int = 900,
                  epic_status: str = "Done") -> str:
    """A CR decomposed into one epic, wired both ways (`Decomposed-into` / `Parent`), the CR left
    non-terminal. With the epic terminal the CR is derivable; otherwise it is not. Returns the CR
    id. Minimal indexes so `transition` can sync the row it moves."""
    crd = root / "sdlc-studio" / "change-requests"
    crd.mkdir(parents=True, exist_ok=True)
    cid = f"CR{cr_num:04d}"
    (crd / f"{cid}-x.md").write_text(
        f"# CR-{cr_num:04d}: c\n\n> **Status:** In Progress\n> **Priority:** Medium\n"
        f"> **Decomposed-into:** EP{ep_num:04d}\n", encoding="utf-8")
    (crd / "_index.md").write_text(
        "# Change Requests\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
        f"| [CR-{cr_num:04d}]({cid}-x.md) | c | In Progress |\n", encoding="utf-8")
    epd = root / "sdlc-studio" / "epics"
    epd.mkdir(parents=True, exist_ok=True)
    eid = f"EP{ep_num:04d}"
    (epd / f"{eid}-x.md").write_text(
        f"# {eid}: e\n\n> **Status:** {epic_status}\n> **Parent:** {cid}\n", encoding="utf-8")
    (epd / "_index.md").write_text(
        "# Epics\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
        f"| [{eid}]({eid}-x.md) | e | {epic_status} |\n", encoding="utf-8")
    return cid


class ApplySignoffRequestDerivationTests(unittest.TestCase):
    """US0445 (CR0422): the close tail derives a parent CR/RFC terminal once its children are all
    terminal, so a delivered request is not left for a manual `reconcile apply`."""

    @staticmethod
    def _status(root: Path, cid: str) -> str:
        import sys as _sys
        _sys.path.insert(0, str(SCRIPT.parent))
        from lib import sdlc_md  # noqa: PLC0415
        hit = sdlc_md.find_by_id(root, cid)
        return sdlc_md.canonical_status(
            sdlc_md.extract_field(hit[0].read_text(encoding="utf-8"), "Status"),
            sdlc_md.status_vocab("cr", root))

    def test_derives_parent_request_when_all_children_terminal(self) -> None:  # AC1
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cid = _derivable_cr(root, epic_status="Done")
            with contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()):
                derived = _load()._derive_parent_requests(root)
            self.assertIn(cid, derived)
            self.assertEqual(self._status(root, cid), "Complete")

    def test_leaves_request_with_a_nonterminal_child(self) -> None:  # AC2
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cid = _derivable_cr(root, epic_status="In Progress")
            with contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()):
                derived = _load()._derive_parent_requests(root)
            self.assertEqual(derived, [])
            self.assertEqual(self._status(root, cid), "In Progress")

    def test_names_each_derived_request(self) -> None:  # AC3
        # The request must be IN-SCOPE for this run: a story Done under EP0900, which the tail
        # derives, which in turn makes CR0900 (EP0900's parent) derivable AND in scope.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            (sd / "US0101-x.md").write_text(
                "# US0101: s\n\n> **Status:** Done\n> **Epic:** EP0900\n\n"
                "## Acceptance Criteria\n\n### AC1: works\n- **Verify:** shell true\n",
                encoding="utf-8")
            (sd / "_index.md").write_text(
                "# Stories\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [US0101](US0101-x.md) | s | Done |\n", encoding="utf-8")
            ed = root / "sdlc-studio" / "epics"
            ed.mkdir(parents=True)
            (ed / "EP0900-x.md").write_text(
                "# EP0900: e\n\n> **Status:** In Progress\n> **Parent:** CR0900\n\n"
                "## Story Breakdown\n\n- [x] [US0101](../stories/US0101-x.md)\n", encoding="utf-8")
            (ed / "_index.md").write_text(
                "# Epics\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [EP0900](EP0900-x.md) | e | In Progress |\n", encoding="utf-8")
            crd = root / "sdlc-studio" / "change-requests"
            crd.mkdir(parents=True)
            (crd / "CR0900-x.md").write_text(
                "# CR-0900: c\n\n> **Status:** In Progress\n> **Priority:** Medium\n"
                "> **Decomposed-into:** EP0900\n", encoding="utf-8")
            (crd / "_index.md").write_text(
                "# Change Requests\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [CR-0900](CR0900-x.md) | c | In Progress |\n", encoding="utf-8")
            state = _close_state(root, batch=["US0101"])
            _close_retro(root)
            out = io.StringIO()
            mod = _load()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                mod._apply_signoff_tail(root, state, units=["US0101"], retro_arg="RETRO0001")
            self.assertIn("CR0900", out.getvalue())
            self.assertIn("derived parent request", out.getvalue())

    def test_out_of_scope_request_is_not_derived(self) -> None:  # scoping repair
        # A derivable CR whose children are none of THIS run's units is left as ordinary drift -
        # the close must not sweep and name requests it did not complete.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cid = _derivable_cr(root, epic_status="Done")     # derivable, but unrelated to the run
            with contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()):
                derived = _load()._derive_parent_requests(root, scope_ids=["US9999"])
            self.assertEqual(derived, [])
            self.assertEqual(self._status(root, cid), "In Progress")

    def test_no_parent_request_is_safe(self) -> None:  # AC4
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1, status="Open")           # a batch with no parent request at all
            with contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()):
                derived = _load()._derive_parent_requests(root)
            self.assertEqual(derived, [])


# The hook shapes the policy is read against. Fragments, not the whole file: what is asserted
# is that the mode is DERIVED from the hook rather than restated beside it, so a hook that
# selects and a hook that always runs must produce different answers from the same reader.
_HOOK_SELECTS = """#!/usr/bin/env bash
relevance_out="$(python3 "$skill/gate.py" --root . --test-relevant)"
case "$relevance_out" in *"test-relevant: yes"*) suites_needed=1 ;; esac
python3 -m unittest discover -s tools/tests
"""
_HOOK_ALWAYS = """#!/usr/bin/env bash
python3 -m unittest discover -s tools/tests
"""
_HOOK_NOTHING = """#!/usr/bin/env bash
bash tools/lint-style.sh
"""


class _ExecutionPolicyFixture(unittest.TestCase):
    """A repo carrying a declared execution policy, a measured baseline and a commit hook."""

    def _repo(self, d, *, declared: dict | None = None, baseline: int | None = 317,
              hook: str | None = _HOOK_SELECTS) -> Path:
        root = Path(d)
        (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
        cfg = ""
        if declared:
            cfg += "test_execution:\n" + "".join(f"  {k}: {v}\n" for k, v in declared.items())
        if baseline is not None:
            cfg += (f"gate_budget:\n  seconds: 380\n  baseline_seconds: {baseline}\n"
                    f"  baseline_date: 2026-07-26\n")
        (root / "sdlc-studio" / ".config.yaml").write_text(cfg or "{}\n", encoding="utf-8")
        if hook is not None:
            (root / ".githooks").mkdir(parents=True, exist_ok=True)
            (root / ".githooks" / "pre-commit").write_text(hook, encoding="utf-8")
        return root


class TestStrategyPolicyTests(_ExecutionPolicyFixture):
    """US0497: the plan-time strategy states the EXECUTION policy and its cost, not only the
    proof each unit owes. The largest single cost in a sprint was set by a habit living in a
    hook that nobody proposed and nobody signed off."""

    def test_the_strategy_states_the_execution_policy_and_cost(self) -> None:
        """AC1: the per-commit mode, the boundary runs, and an estimated cost for each."""
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d)
            text = "\n".join(sprint.render_test_strategy(sprint.test_strategy(root, [])))
        self.assertIn("per commit", text)
        self.assertIn("at close", text)
        self.assertIn("at release", text)
        self.assertIn("317", text, "each moment is priced from the measured baseline")

    def test_an_unmeasured_execution_cost_is_never_rendered_as_zero(self) -> None:
        """A cost nobody measured, printed as 0, is the cheapest-looking lie a plan can tell."""
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, baseline=None)
            pol = sprint.execution_policy(root)
            text = "\n".join(sprint.render_execution_policy(pol))
        self.assertFalse(pol["measured"])
        self.assertIsNone(pol["cost_s"]["at_close"], "unknown is not zero")
        self.assertIn("NOT MEASURED", text)

    def test_a_policy_diverging_from_the_hook_is_reported(self) -> None:
        """AC2: a declared policy the hook does not implement is named, in both directions."""
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, declared={"per_commit": "full"}, hook=_HOOK_SELECTS)
            diverged = sprint.execution_policy(root)
        self.assertIsNotNone(diverged["divergence"])
        self.assertIn("full", diverged["divergence"])
        self.assertIn("selected", diverged["divergence"])
        self.assertIn("execution policy DIVERGES",
                      "\n".join(sprint.render_execution_policy(diverged)))
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, declared={"per_commit": "selected"}, hook=_HOOK_SELECTS)
            agreed = sprint.execution_policy(root)
        self.assertIsNone(agreed["divergence"], "an agreeing hook reports no divergence")

    def test_the_hook_mode_is_read_from_the_hook_not_restated_beside_it(self) -> None:
        """Three different hooks must give three different answers, or the reader is a copy
        of the rule rather than a measurement of it (LL0042)."""
        sprint = _load()
        modes = []
        for hook in (_HOOK_SELECTS, _HOOK_ALWAYS, _HOOK_NOTHING, None):
            with tempfile.TemporaryDirectory() as d:
                root = self._repo(d, hook=hook)
                modes.append(sprint.hook_per_commit_mode(root)["mode"])
        self.assertEqual(modes, ["selected", "full", "none", "unknown"])

    def test_an_unreadable_hook_is_unreconciled_never_agreement(self) -> None:
        """A hook nobody can read has not been shown to agree with the declaration."""
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, declared={"per_commit": "selected"}, hook=None)
            pol = sprint.execution_policy(root)
        self.assertIsNotNone(pol["divergence"])
        self.assertIn("UNRECONCILED", pol["divergence"])


class TestStrategyPersistenceTests(_ExecutionPolicyFixture):
    """US0498: a strategy that leaves no record is advice, not a plan. It is written with the
    plan so it can be reviewed, signed off with the goal, and compared afterwards with what
    actually ran."""

    def _plan(self, root, *extra):
        mod = _load()
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), \
                unittest.mock.patch.object(sys, "stdin", io.StringIO("")):
            rc = mod.main(["plan", "--bugs", "Open", "--no-fetch", "--root", str(root), *extra])
        return rc, out.getvalue(), err.getvalue()

    def test_the_strategy_is_persisted_with_the_plan(self) -> None:
        """AC1: the plan RECORD carries it, so it survives the terminal and can be read back."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, declared={"per_commit": "full"})
            _bug(root, 1)
            rc, _, _ = self._plan(root, "--write")
            self.assertEqual(rc, 0)
            plan = json.loads(
                (root / "sdlc-studio" / ".local" / "sprint-plan.json").read_text())
        self.assertIn("test_strategy", plan, "the plan record must carry the strategy")
        strat = plan["test_strategy"]
        self.assertEqual(strat["execution"]["declared"]["per_commit"], "full")
        self.assertIn("units", strat, "the proof obligations travel with it")

    def test_the_close_reads_back_the_recorded_strategy(self) -> None:
        """AC2: what is judged at the close is what was agreed at the plan.

        The recorded policy and the live config are deliberately DIFFERENT, so a close that
        re-derived instead of reading back would answer `selected` and fail here."""
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, declared={"per_commit": "selected"})
            local = root / "sdlc-studio" / ".local"
            local.mkdir(parents=True, exist_ok=True)
            (local / "sprint-plan.json").write_text(json.dumps({
                "test_strategy": {"available": True, "areas": ["Unit Testing"], "units": {},
                                  "gaps": [], "why": "",
                                  "execution": {"declared": {"per_commit": "full"}}}}),
                encoding="utf-8")
            got = sprint.close_test_strategy(root, ["BG0001"])
        self.assertEqual(got["source"], "recorded")
        self.assertEqual(got["strategy"]["execution"]["declared"]["per_commit"], "full")

    def test_a_run_with_no_recorded_strategy_says_it_re_derived_one(self) -> None:
        """The honest degrade. A re-derivation is not what was agreed, and it is NAMED as a
        re-derivation rather than presented as the plan's own strategy."""
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d)
            got = sprint.close_test_strategy(root, [])
        self.assertEqual(got["source"], "re-derived")
        self.assertIn("not what was agreed", got["why"])

    def test_the_CLOSE_states_which_strategy_it_judges_against(self) -> None:
        """LANE test, not a library test (LL0040): deleting the call from `cmd_close` would
        leave the three above green. The line is printed above every refusal, so a close that
        stops later still states what it was judging against."""
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d)
            local = root / "sdlc-studio" / ".local"
            local.mkdir(parents=True, exist_ok=True)
            (local / "run-state.json").write_text(json.dumps({
                "run_id": "RUN-T", "batch": ["BG0001"], "outcome": "running",
                "started_at": "2026-07-28T00:00:00+00:00"}), encoding="utf-8")
            (local / "sprint-plan.json").write_text(json.dumps({
                "test_strategy": {"available": True, "areas": [], "units": {}, "gaps": [],
                                  "why": "", "execution": {"declared": {"per_commit": "full"}}}}),
                encoding="utf-8")
            args = argparse.Namespace(root=str(root), retro=None, goal_verdict=None, note=None,
                                      file_and_close=False, apply_signoff=False,
                                      principal=None, author=None)
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                sprint.cmd_close(args)
        self.assertIn("test strategy recorded", out.getvalue() + err.getvalue())


def _stub_gate(lanes: list[tuple[str, str]], *, surface: str = "HASH"):
    """A gate module that refuses on exactly `lanes`, printing the real gate's verdict shape.

    Stubbed because the behaviour under test is what the CLOSE does with a refusal, not what
    the gate decides - and a close driven against the real gate would be measuring the
    fixture's artefact debt instead."""
    mod = types.ModuleType("gate")

    def main(argv=None):
        for name, detail in lanes:
            print(f"  [FAIL] {name}: {detail}")
        print(f"gate: {'FAIL' if lanes else 'PASS'}")
        return 1 if lanes else 0

    mod.main = main
    mod.surface_files = lambda root=".": []
    mod.surface_hash = lambda root=".": surface
    mod.calls = lanes
    # US0553: the close records the green it earned into the record the COMMIT HOOK reads, so
    # the commits that follow can reuse it. Captured rather than stubbed away, because "the
    # close calls this" is the whole behaviour - the reuse decision itself already existed and
    # was simply never reached from here.
    mod.recorded_verdicts = []

    def record_suite_verdict(root=".", *, run, status="green", mode="full", digest=None):
        mod.recorded_verdicts.append({"root": str(root), "run": str(run),
                                      "status": status, "mode": mode})
        return Path(root) / "sdlc-studio" / ".local" / "gate-suite-verdict.json"

    mod.record_suite_verdict = record_suite_verdict
    return mod


class CloseSelfInvalidationTests(unittest.TestCase):
    """US0500: `sprint close` writes the review anchor and the handoff, which leaves the
    anchor uncommitted, which fails the review-current lane on the next attempt. RUN-01KYHVWK
    took four attempts and about 16 minutes of test execution to record a decision already
    made - the close chasing a target it was moving itself."""

    def _repo(self, *, close_output: list[str] | None = None,
              close_findings: list[dict] | None = None) -> Path:
        import os
        import time
        d = Path(tempfile.mkdtemp(prefix="close_self_"))
        (d / "sdlc-studio" / ".local").mkdir(parents=True)
        (d / "sdlc-studio" / "reviews").mkdir(parents=True)
        anchor = d / "sdlc-studio" / "reviews" / "LATEST.md"
        anchor.write_text("# Reviews - LATEST (anchor)\n", encoding="utf-8")
        old = time.time() - 7200
        os.utime(anchor, (old, old))
        (d / "sdlc-studio" / "stories").mkdir(parents=True)
        (d / "sdlc-studio" / "stories" / "US0001-x.md").write_text(
            "# US0001: s\n\n> **Status:** Done\n", encoding="utf-8")
        (d / "sdlc-studio" / "bugs").mkdir(parents=True)
        (d / "sdlc-studio" / "bugs" / "BG9001-filed.md").write_text(
            "# BG9001: filed during the close\n\n> **Status:** Open\n", encoding="utf-8")
        state = {"run_id": "RUN-SELF", "batch": ["US0001"], "outcome": "running",
                 "started_at": "2026-07-28T09:00:00Z",
                 "close_output": close_output or [],
                 "close_findings": close_findings or []}
        (d / "sdlc-studio" / ".local" / "run-state.json").write_text(
            json.dumps(state), encoding="utf-8")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        return d

    def _state(self, root) -> dict:
        return json.loads(
            (root / "sdlc-studio" / ".local" / "run-state.json").read_text(encoding="utf-8"))

    def _close_gate(self, sprint, root, lanes):
        gate = _stub_gate(lanes)
        out, err = io.StringIO(), io.StringIO()
        with unittest.mock.patch.dict(sys.modules, {"gate": gate}), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            ok, detail, remedy = sprint._close_gate(root, "RETRO0001", self._state(root))
        return ok, detail, remedy

    def test_the_close_output_does_not_fail_its_own_review_lane(self) -> None:
        """AC1: the anchor, the handoff and the close's other output are recognised as its
        own and do not make the review stale."""
        sprint = _load()
        own = ["sdlc-studio/reviews/LATEST.md", "sdlc-studio/bugs/BG9001-filed.md",
               "sdlc-studio/stories/US0001-x.md"]
        root = self._repo(close_output=own)
        currency = sprint.close_review_currency(root, self._state(root))
        self.assertTrue(currency["self_caused"])
        self.assertEqual(currency["stale"], [], "nothing but the close's own output is newer")
        ok, detail, _ = self._close_gate(
            sprint, root, [("review-current", "reviews/LATEST.md is stale - 3 artefact(s) "
                                              "changed since the last review")])
        self.assertTrue(ok, "the close must not refuse itself for the paperwork it just wrote")
        self.assertIn("created by this close", detail)

    def test_a_finding_filed_during_the_close_is_carried(self) -> None:
        """AC2: filing an honest finding during a close is the behaviour the doctrine asks
        for, and it must not cost another full gate."""
        sprint = _load()
        root = self._repo(close_output=["sdlc-studio/reviews/LATEST.md",
                                        "sdlc-studio/stories/US0001-x.md"])
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            sprint.record_close_finding(root, "BG9001", "sdlc-studio/bugs/BG9001-filed.md")
        state = self._state(root)
        self.assertIn("sdlc-studio/bugs/BG9001-filed.md",
                      sprint.close_own_output(root, state))
        self.assertTrue(sprint.close_review_currency(root, state)["self_caused"],
                        "a finding the close filed is not unreviewed work against that close")
        carried = sprint.carried_close_findings(root, state)
        self.assertEqual([c["id"] for c in carried], ["BG9001"])
        self.assertIn("CARRIED into the next run", sprint.carried_findings_line(carried) or "")
        self.assertEqual(sprint.carried_findings_line([]), "",
                         "a close that filed nothing says nothing")

    def test_a_real_blocker_still_refuses_and_is_named_as_such(self) -> None:
        """AC3: a correctness failure in the batch still refuses, and the message says which
        blockers are in the work and which the close made for itself."""
        sprint = _load()
        root = self._repo(close_output=["sdlc-studio/reviews/LATEST.md",
                                        "sdlc-studio/bugs/BG9001-filed.md",
                                        "sdlc-studio/stories/US0001-x.md"])
        ok, detail, remedy = self._close_gate(
            sprint, root, [("conformance", "US0001: missing critiqued evidence"),
                           ("review-current", "reviews/LATEST.md is stale")])
        self.assertFalse(ok, "a blocker in the work is never waved through")
        self.assertIn("in the WORK", detail)
        self.assertIn("conformance", detail)
        self.assertTrue(remedy)

    def test_a_stale_artefact_the_close_did_not_write_still_refuses(self) -> None:
        """The discriminating case for AC1: register only the anchor, and the story that
        genuinely changed keeps the lane red."""
        sprint = _load()
        root = self._repo(close_output=["sdlc-studio/reviews/LATEST.md"])
        currency = sprint.close_review_currency(root, self._state(root))
        self.assertFalse(currency["self_caused"])
        self.assertTrue(currency["stale"])
        ok, detail, _ = self._close_gate(
            sprint, root, [("review-current", "reviews/LATEST.md is stale")])
        self.assertFalse(ok)
        self.assertIn("in the WORK", detail)

    def test_an_unattributable_refusal_is_never_called_self_inflicted(self) -> None:
        """A gate whose verdict this cannot parse has not been shown to be the close's own
        fault, and a refusal wrongly labelled self-inflicted is one that gets walked past."""
        sprint = _load()
        root = self._repo(close_output=["sdlc-studio/reviews/LATEST.md",
                                        "sdlc-studio/bugs/BG9001-filed.md",
                                        "sdlc-studio/stories/US0001-x.md"])
        gate = _stub_gate([])
        gate.main = lambda argv=None: (print("gate blew up in a shape nobody parses"), 1)[1]
        out, err = io.StringIO(), io.StringIO()
        with unittest.mock.patch.dict(sys.modules, {"gate": gate}), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            ok, detail, _ = sprint._close_gate(root, "RETRO0001", self._state(root))
        self.assertFalse(ok)
        self.assertIn("could not be attributed", detail)


class CloseVerdictReuseTests(unittest.TestCase):
    """US0553. The close runs the FULL suites as step 4 of seven and then commits. It recorded
    that green only into its own close-private ledger, so the commit hook - which reads
    `gate-suite-verdict.json` - knew nothing about it and the first commit of the close paid
    for the suites again, seconds later, over the same script tree.

    Nothing here is a new decision: `suite_decision` has known how to reuse a green since
    US0493. What was missing was a caller, which is why these tests assert the CALL and not
    the reuse logic - a mechanism that reaches no caller is inert however well it is tested."""

    def _repo(self) -> Path:
        (d := Path(tempfile.mkdtemp(prefix="close_verdict_"))).joinpath(
            "sdlc-studio", ".local").mkdir(parents=True)
        (d / "sdlc-studio" / "reviews").mkdir(parents=True)
        (d / "sdlc-studio" / "reviews" / "LATEST.md").write_text("# anchor\n", encoding="utf-8")
        (d / "sdlc-studio" / ".local" / "run-state.json").write_text(json.dumps({
            "run_id": "RUN-VERDICT", "batch": ["US0001"], "outcome": "running",
            "started_at": "2026-07-29T09:00:00Z",
            "close_output": ["sdlc-studio/reviews/LATEST.md"]}), encoding="utf-8")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        return d

    def _run(self, sprint, root, gate):
        with unittest.mock.patch.dict(sys.modules, {"gate": gate}), \
                contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            return sprint._close_gate(root, "RETRO0001", json.loads(
                (root / "sdlc-studio" / ".local" / "run-state.json").read_text(encoding="utf-8")))

    def test_the_close_gate_step_records_the_verdict_it_earned(self) -> None:
        sprint = _load()
        root, gate = self._repo(), _stub_gate([])
        ok, _, _ = self._run(sprint, root, gate)
        self.assertTrue(ok)
        self.assertEqual(1, len(gate.recorded_verdicts),
                         "the close ran the full suites and recorded no verdict the hook reads")
        recorded = gate.recorded_verdicts[0]
        self.assertEqual("green", recorded["status"])
        self.assertEqual("full", recorded["mode"],
                         "a boundary declines a SELECTED green, so the close must not claim one")
        self.assertEqual("RUN-VERDICT", recorded["run"],
                         "the verdict is attributed to the run that earned it")

    def test_a_refused_gate_records_no_verdict(self) -> None:
        """The discriminating half. A close that FAILED its gate must leave nothing behind for
        the next commit to reuse, or one red close would buy a green for the commit after it."""
        sprint = _load()
        root, gate = self._repo(), _stub_gate([("conformance", "US0001: no critic verdict")])
        ok, _, _ = self._run(sprint, root, gate)
        self.assertFalse(ok)
        self.assertEqual([], gate.recorded_verdicts)

    def test_a_reused_close_verdict_records_nothing_new(self) -> None:
        """When the close's own retry path short-circuits, no suites ran, so there is no fresh
        green to record - re-stamping one would launder an old verdict as a new measurement."""
        sprint = _load()
        root, gate = self._repo(), _stub_gate([])
        self.assertTrue(self._run(sprint, root, gate)[0])
        gate.recorded_verdicts.clear()
        gate.main = lambda argv=None: self.fail("the retry must not re-run the gate")
        ok, detail, _ = self._run(sprint, root, gate)
        self.assertTrue(ok)
        self.assertIn("REUSED", detail)
        self.assertEqual([], gate.recorded_verdicts)


class InertMechanismsAreReachedTests(unittest.TestCase):
    """BG0385. Five units of RUN-01KYMJEM built `goal_panel`, `judge_defects_against_goal`,
    both ends of the bookend content review and `prediction_miss` - green tests, killed
    mutants, and NOTHING called any of them. The per-clause verdict the close recorded was
    assembled by hand, so the panel's author-exclusion never fired once.

    These tests assert the CALL from the command, not the function. A unit test on the
    mechanism is what all five already had."""

    def _repo(self, *, goal="one thing; and another thing") -> Path:
        d = Path(tempfile.mkdtemp(prefix="inert_"))
        (d / "sdlc-studio" / ".local").mkdir(parents=True)
        (d / "sdlc-studio" / "bugs").mkdir(parents=True)
        (d / "sdlc-studio" / "stories").mkdir(parents=True)
        (d / "sdlc-studio" / "stories" / "US0001-a-unit.md").write_text(
            "# US0001: a unit\n\n> **Status:** Review\n", encoding="utf-8")
        (d / "sdlc-studio" / "bugs" / "BG0001-an-open-defect.md").write_text(
            "# BG0001: an open defect that mentions another thing\n\n"
            "> **Status:** Open\n> **Severity:** P1\n", encoding="utf-8")
        (d / "sdlc-studio" / ".local" / "run-state.json").write_text(json.dumps({
            "run_id": "RUN-INERT", "batch": ["US0001"], "outcome": "running",
            "sprint_goal": goal, "started_at": "2026-07-29T09:00:00Z"}), encoding="utf-8")
        (d / "sdlc-studio" / ".local" / "goal-review.json").write_text(json.dumps({
            "rounds": [{"goal": goal, "seats": [
                {"seat": "qa", "achievable": "yes", "done_means": "x", "one_increment": "yes"}]}]
        }), encoding="utf-8")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        return d

    def test_the_close_reaches_the_goal_panel_and_reports_per_clause(self) -> None:
        sprint = _load()
        root = self._repo()
        lines = sprint.close_goal_judgement(root, json.loads(
            (root / "sdlc-studio" / ".local" / "run-state.json").read_text(encoding="utf-8")))
        joined = "\n".join(lines)
        self.assertIn("goal panel", joined, "the panel is still unreachable from the close")
        self.assertIn("one thing", joined, "the verdict is reported per CLAUSE")
        self.assertIn("another thing", joined)

    def test_the_close_reaches_the_defect_judgement(self) -> None:
        sprint = _load()
        root = self._repo()
        joined = "\n".join(sprint.close_goal_judgement(root, json.loads(
            (root / "sdlc-studio" / ".local" / "run-state.json").read_text(encoding="utf-8"))))
        self.assertIn("defects vs goal", joined)
        self.assertIn("BLOCKING BG0001", joined,
                      "a P1 blocks whatever the clause reasoning says, and the close must say so")

    def test_the_close_reaches_the_caller_check_over_the_batch(self) -> None:
        """AC2. The repo's own check for this defect class, never once run over a batch - which
        is why BG0385 was found by an operator's question rather than by the tool."""
        sprint = _load()
        root = self._repo()
        joined = "\n".join(sprint.close_goal_judgement(root, json.loads(
            (root / "sdlc-studio" / ".local" / "run-state.json").read_text(encoding="utf-8"))))
        self.assertIn("caller-check", joined)
        self.assertIn("of 1 ship a mechanism", joined, "the scope is named, not inferred")

    def test_the_plan_records_the_content_review_and_the_close_scores_it(self) -> None:
        """Both ends of the bookend, through the CLI, plus the prediction miss that only exists
        because both ends were reached."""
        sprint = _load()
        root = self._repo()
        sprint.record_content_review(root, "plan", "one thing; and another thing", "yes")
        sprint.record_content_review(root, "close", "one thing; and another thing", "partial",
                                     missing="the second clause did not land")
        reviews = sprint.content_reviews(root)
        self.assertEqual("yes", reviews["plan"]["answer"])
        self.assertEqual("partial", reviews["close"]["answer"])
        miss = sprint.prediction_miss(root)
        self.assertIsNotNone(miss, "with both ends recorded the miss must be reportable")
        self.assertIn("PREDICTION MISS", miss)
        self.assertIn(miss, "\n".join(sprint.close_goal_judgement(root, json.loads(
            (root / "sdlc-studio" / ".local" / "run-state.json").read_text(encoding="utf-8")))))

    def test_the_plan_cli_takes_the_content_review(self) -> None:
        """The flag exists on the command that should ask the question - which is what "wired"
        means. A helper nobody can invoke is the state this bug records."""
        sprint = _load()
        parser = sprint.build_parser()
        plan = parser._subparsers._group_actions[0].choices["plan"]   # noqa: SLF001
        close = parser._subparsers._group_actions[0].choices["close"]  # noqa: SLF001
        for name, sub in (("plan", plan), ("close", close)):
            with self.subTest(command=name):
                flags = {opt for a in sub._actions for opt in a.option_strings}  # noqa: SLF001
                self.assertIn("--content-review", flags)
                self.assertIn("--content-missing", flags)

    def test_the_panel_refuses_a_goal_with_no_clauses_rather_than_inventing_one(self) -> None:
        """The reporting lane must degrade, never crash a close: the mechanisms inform a
        sign-off, and a reporting lane that can block one is a lane that gets switched off."""
        sprint = _load()
        root = self._repo(goal="")
        lines = sprint.close_goal_judgement(root, json.loads(
            (root / "sdlc-studio" / ".local" / "run-state.json").read_text(encoding="utf-8")))
        self.assertNotIn("goal panel:", "\n".join(lines),
                         "no clauses means no panel, not a panel over nothing")


class CloseDryRunTests(unittest.TestCase):
    """US0555. `close` runs seven steps and stops at the first unmet prerequisite; RUN-01KYMJEM
    took three attempts, two of them stopping on a refusal, and each restart re-ran the steps
    before it. `preflight` reports every prerequisite at once and always did - but it cannot
    judge the retro's CONTENT before a retro exists, and that is precisely the class that
    refused. The dry run performs the action steps against a scratch copy so it can."""

    @staticmethod
    def _steps(result: dict) -> dict:
        return {s["step"]: s for s in result["steps"]}

    def _repo(self) -> Path:
        d = Path(tempfile.mkdtemp(prefix="close_dry_"))
        (d / "sdlc-studio" / ".local").mkdir(parents=True)
        (d / "sdlc-studio" / "reviews").mkdir(parents=True)
        (d / "sdlc-studio" / "reviews" / "LATEST.md").write_text("# anchor\n", encoding="utf-8")
        (d / "sdlc-studio" / ".local" / "run-state.json").write_text(json.dumps({
            "run_id": "RUN-DRY", "batch": ["US0001"], "outcome": "running",
            "sprint_goal": "a goal", "started_at": "2026-07-29T09:00:00Z"}), encoding="utf-8")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        return d

    @staticmethod
    def _fingerprint(root: Path) -> list[tuple[str, int, float]]:
        return sorted((str(p.relative_to(root)), p.stat().st_size, p.stat().st_mtime)
                      for p in root.rglob("*") if p.is_file())

    def _broken_retro(self, root: Path, retro_id: str = "RETRO9001") -> str:
        """A retro that EXISTS and whose content is wrong - an undecided finding. Since US0558
        the scaffold passes its own validator, so a content refusal has to be constructed
        rather than assumed; a test that relied on the scaffold failing would now be asserting
        the defect US0558 removed."""
        (root / "sdlc-studio" / "retros").mkdir(parents=True, exist_ok=True)
        (root / "sdlc-studio" / "retros" / f"{retro_id}-broken.md").write_text(
            f"# {retro_id}: a sprint\n\n## Delivered\n\n- US0001 - shipped\n\n"
            "## What went well\n\n- it went well\n\n## What was hard / what stalled\n\n"
            "- it was hard\n\n## Lessons\n\n- a real lesson, learned the hard way\n\n"
            "## Actions raised\n\n| Finding | Disposition |\n| --- | --- |\n"
            "| a finding nobody decided | |\n", encoding="utf-8")
        return retro_id

    def test_every_refusing_step_is_reported_not_only_the_first(self) -> None:
        """The property the whole story is for: a close stops at its first refusal, a dry run
        must not. Refusals from two different stages, in one pass."""
        sprint = _load()
        root = self._repo()
        retro_id = self._broken_retro(root)
        pre = sprint.close_preflight(root, retro_id)
        self.assertGreater(len(pre["blockers"]), 1,
                           "the fixture must produce several prerequisite gaps, or this test "
                           "cannot tell 'every one' from 'the first one'")
        result = sprint.close_dry_run(root, retro_id)
        stages = [s["step"] for s in result["blockers"]]
        # EVERY prerequisite the preflight found, by count and not merely by presence - a
        # report that kept the first of each stage would still name the stages.
        self.assertEqual([b["stage"] for b in pre["blockers"]], stages[:len(pre["blockers"])],
                         "the dry run dropped prerequisite refusals the preflight had found")
        self.assertIn("retro-validate", stages,
                      "the undecided finding is a CONTENT gap, and it is reported in the same "
                      "pass as the prerequisites above rather than on the next attempt")
        self.assertGreater(len(result["blockers"]), len(pre["blockers"]),
                           "the chain steps add refusals of their own; the pass covers both")

    def test_retro_content_defects_are_reported_in_the_same_pass(self) -> None:
        """What `preflight` cannot do. With no `--retro` given there is no retro to validate,
        so a read-only pass says NOTHING about its content - not "fine", nothing. The dry run
        scaffolds one in the copy and judges what `close` would actually mint, so the content
        step has a verdict in the same pass as the prerequisites."""
        sprint = _load()
        root = self._repo()
        pre = sprint.close_preflight(root, None)
        self.assertNotIn("retro-validate", {b["stage"] for b in pre["blockers"]},
                         "the preflight cannot reach the content class - that is the premise")
        self.assertNotIn("retro-validate", {b["stage"] for b in pre["blockers"]})
        steps = self._steps(sprint.close_dry_run(root))
        self.assertEqual("ok", steps["retro-scaffold"]["status"])
        self.assertIn("RETRO", steps["retro-scaffold"]["detail"])
        self.assertIn(steps["retro-validate"]["status"], ("ok", "refuse"),
                      "the content step is EVALUATED, which is the whole difference from a "
                      "read-only preflight that cannot reach it at all")

    def test_a_retro_whose_content_is_wrong_refuses_before_one_is_written(self) -> None:
        """The discriminating half of the same property: the verdict tracks the content rather
        than always reading ok. Since US0558 a scaffolded retro passes, so a test that only
        watched the scaffold would pass whatever this step did."""
        sprint = _load()
        root = self._repo()
        retro_id = self._broken_retro(root)
        steps = self._steps(sprint.close_dry_run(root, retro_id))
        self.assertEqual("refuse", steps["retro-validate"]["status"])
        self.assertIn("not dispositioned", steps["retro-validate"]["detail"])

    def test_the_dry_run_writes_nothing(self) -> None:
        sprint = _load()
        root = self._repo()
        before = self._fingerprint(root)
        sprint.close_dry_run(root)
        self.assertEqual(before, self._fingerprint(root),
                         "a preview that wrote to the real tree is a close, not a preview")

    def test_the_scratch_copy_is_removed(self) -> None:
        sprint = _load()
        result = sprint.close_dry_run(self._repo())
        self.assertIsNotNone(result["scratch"])
        self.assertFalse(Path(result["scratch"]).exists(),
                         "a dry run per close would otherwise leave a 14MB copy behind each time")

    def test_a_clean_dry_run_predicts_a_close_that_does_not_refuse(self) -> None:
        """`clean` has to mean something a caller can act on, so it is asserted against the
        report rather than inferred: no refusal AND no unevaluated step."""
        sprint = _load()
        self.assertTrue(sprint._dry_run_result(
            [{"step": "gate", "status": "ok", "detail": "", "remedy": ""}], None)["clean"])
        self.assertFalse(sprint._dry_run_result(
            [{"step": "gate", "status": "refuse", "detail": "", "remedy": ""}], None)["clean"])

    def test_an_unevaluated_step_is_never_reported_as_passing(self) -> None:
        """The direction this must fail in. A step whose probe blew up in the scratch copy has
        said nothing about the real close; calling that a pass is the one way a preview could
        actively mislead."""
        sprint = _load()
        result = sprint._dry_run_result(
            [{"step": "handoff", "status": "unevaluated", "detail": "boom", "remedy": ""}], None)
        self.assertFalse(result["clean"], "an unanswered step is not a passing one")
        self.assertEqual([], result["blockers"])
        self.assertEqual(1, len(result["unevaluated"]))
        report = sprint.dry_run_report(result)
        self.assertIn("UNEVALUATED", report)
        self.assertNotIn("CLEAN", report)

    def test_a_step_that_raises_in_the_copy_is_unevaluated_not_ok(self) -> None:
        sprint = _load()
        root = self._repo()

        def explode(*_a, **_kw):
            raise RuntimeError("the probe blew up")

        with unittest.mock.patch.object(sprint, "_close_reconcile", explode):
            steps = self._steps(sprint.close_dry_run(root))
        self.assertEqual("unevaluated", steps["reconcile"]["status"])
        self.assertIn("blew up", steps["reconcile"]["detail"])

    def test_the_report_names_every_step_and_its_remedy(self) -> None:
        sprint = _load()
        result = sprint.close_dry_run(self._repo())
        report = sprint.dry_run_report(result)
        self.assertIn("nothing was written", report)
        for step in sprint.DRY_RUN_ACTION_STEPS:
            self.assertIn(step, report, f"{step} is missing from the report")


class CloseCostReportTests(unittest.TestCase):
    """US0559. The close's own cost was recalled, never reported: RUN-01KYMJEM's `~32 minutes`
    was reconstructed afterwards from a timings file and a memory of how many attempts there
    had been. A reduction judged against an impression is not a reduction anyone can check."""

    def _root(self, runs: list[dict]) -> Path:
        d = Path(tempfile.mkdtemp(prefix="close_cost_"))
        (d / "sdlc-studio" / ".local").mkdir(parents=True)
        (d / "sdlc-studio" / ".local" / "test-execution.json").write_text(
            json.dumps({"runs": runs}), encoding="utf-8")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        return d

    @staticmethod
    def _row(at, **kw):
        row = {"at": at, "moment": "close", "mode": "full", "seconds": 400.0,
               "verdict": "pass", "surface": "H", "run_id": "RUN-COST", "reused_from": None}
        row.update(kw)
        return row

    def test_the_close_reports_its_gate_seconds_and_elapsed(self) -> None:
        sprint = _load()
        root = self._root([self._row("2026-07-29T10:00:00+00:00", seconds=398.0),
                           self._row("2026-07-29T10:12:00+00:00", seconds=427.0)])
        cost = sprint.close_cost(root, "RUN-COST")
        self.assertEqual(825.0, cost["gate_seconds"])
        self.assertEqual(2, cost["measured_runs"])
        self.assertEqual(720, cost["elapsed_seconds"])
        line = sprint.close_cost_line(cost)
        self.assertIn("825s", line)
        self.assertIn("12m00s", line)

    def test_the_close_cost_is_recorded_on_the_run(self) -> None:
        """Read back off the ledger the close writes, so a later close can be compared with
        this one rather than with a number somebody remembers."""
        sprint = _load()
        root = self._root([self._row("2026-07-29T10:00:00+00:00", run_id="RUN-OTHER"),
                           self._row("2026-07-29T10:05:00+00:00", seconds=100.0)])
        self.assertEqual(100.0, sprint.close_cost(root, "RUN-COST")["gate_seconds"],
                         "another run's close is not this run's cost")
        self.assertEqual(500.0, sprint.close_cost(root)["gate_seconds"],
                         "unscoped, every recorded close counts")

    def test_a_reused_verdict_is_reported_as_a_saving(self) -> None:
        sprint = _load()
        root = self._root([
            self._row("2026-07-29T10:00:00+00:00", seconds=400.0),
            self._row("2026-07-29T10:10:00+00:00", mode="reuse", seconds=0.0,
                      reused_from="2026-07-29T10:00:00+00:00")])
        cost = sprint.close_cost(root, "RUN-COST")
        self.assertEqual(1, cost["reused_runs"])
        self.assertEqual(400.0, cost["reused_seconds"], "the saving is the run it reused")
        self.assertEqual(400.0, cost["gate_seconds"], "a reuse cost nothing and adds nothing")
        self.assertIn("saving about 400s", sprint.close_cost_line(cost))

    def test_an_unmeasured_component_is_never_reported_as_zero(self) -> None:
        """The direction this must fail in. A close whose seconds were never recorded would
        otherwise report the cheapest close on file."""
        sprint = _load()
        root = self._root([self._row("2026-07-29T10:00:00+00:00", seconds=None),
                           self._row("2026-07-29T10:04:00+00:00", seconds=None)])
        cost = sprint.close_cost(root, "RUN-COST")
        self.assertIsNone(cost["gate_seconds"], "no measurement is not zero seconds")
        self.assertEqual(0, cost["measured_runs"])
        self.assertEqual(2, len(cost["unmeasured"]))
        self.assertIn("UNMEASURED", sprint.close_cost_line(cost))

    def test_a_close_with_no_gate_event_says_so_rather_than_reporting_zero(self) -> None:
        sprint = _load()
        line = sprint.close_cost_line(sprint.close_cost(self._root([]), "RUN-COST"))
        self.assertIn("UNMEASURED, not zero", line)

    def test_a_single_event_has_no_span_and_reports_none(self) -> None:
        """One event is a moment, not a duration. Reporting 0m00s would read as an instant
        close - the same false cheapness an unmeasured component would produce."""
        sprint = _load()
        root = self._root([self._row("2026-07-29T10:00:00+00:00")])
        self.assertIsNone(sprint.close_cost(root, "RUN-COST")["elapsed_seconds"])
        self.assertNotIn("elapsed", sprint.close_cost_line(sprint.close_cost(root, "RUN-COST")))


class CloseRetryTests(unittest.TestCase):
    """US0501: RUN-01KYHVWK's close took four attempts, each paying a full gate, to record a
    decision already made. A retry over an unchanged test-relevant surface reuses the verdict
    it already earned; a retry after a real change never does."""

    #: The surface the stub gate reports. The anchor is in it deliberately: the close writes
    #: that file itself, and excluding it is what makes a retry read as unchanged.
    SURFACE = ("src/code.py", "sdlc-studio/reviews/LATEST.md")

    def _repo(self) -> Path:
        d = Path(tempfile.mkdtemp(prefix="close_retry_"))
        (d / "sdlc-studio" / ".local").mkdir(parents=True)
        (d / "sdlc-studio" / "reviews").mkdir(parents=True)
        (d / "sdlc-studio" / "reviews" / "LATEST.md").write_text("# anchor\n", encoding="utf-8")
        (d / "src").mkdir()
        (d / "src" / "code.py").write_text("x = 1\n", encoding="utf-8")
        (d / "sdlc-studio" / ".local" / "run-state.json").write_text(json.dumps({
            "run_id": "RUN-RETRY", "batch": ["US0001"], "outcome": "running",
            "started_at": "2026-07-28T09:00:00Z",
            "close_output": ["sdlc-studio/reviews/LATEST.md"]}), encoding="utf-8")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        return d

    def _gate(self, calls: list, rc: int = 0):
        mod = types.ModuleType("gate")

        def main(argv=None):
            calls.append(list(argv or []))
            print("gate: PASS" if rc == 0 else "  [FAIL] conformance: red\ngate: FAIL")
            return rc

        mod.main = main
        mod.surface_files = lambda root=".": list(self.SURFACE)
        # US0553: the close stamps the green it earned where the commit hook reads it. Captured
        # here too so this suite exercises the real call rather than a gate module that happens
        # not to have it.
        mod.recorded_verdicts = []
        mod.record_suite_verdict = lambda root=".", **kw: (
            mod.recorded_verdicts.append(kw), Path(root))[1]
        return mod

    def _attempt(self, sprint, root, gate):
        state = json.loads(
            (root / "sdlc-studio" / ".local" / "run-state.json").read_text(encoding="utf-8"))
        with unittest.mock.patch.dict(sys.modules, {"gate": gate}), \
                contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            return sprint._close_gate(root, "RETRO0001", state)

    def test_a_retry_over_an_unchanged_surface_reuses_the_verdict(self) -> None:
        """AC1: four attempts at a close cost one gate run, not four - and the close's own
        paperwork, written between the attempts, does not count as a change."""
        sprint = _load()
        root = self._repo()
        calls: list = []
        gate = self._gate(calls)
        ok, first, _ = self._attempt(sprint, root, gate)
        self.assertTrue(ok)
        self.assertEqual(len(calls), 1)
        self.assertNotIn("REUSED", first)
        # The close stamps its own anchor between attempts - the exact write that made the
        # review stale and cost RUN-01KYHVWK three further gates.
        (root / "sdlc-studio" / "reviews" / "LATEST.md").write_text(
            "# anchor\n\nstamped by the close\n", encoding="utf-8")
        ok, second, _ = self._attempt(sprint, root, gate)
        self.assertTrue(ok)
        self.assertEqual(len(calls), 1, "the retry must not pay for a second gate run")
        self.assertIn("REUSED", second)

    def test_a_retry_after_a_change_reruns_the_gate(self) -> None:
        """AC2: the reuse can never mask work done between attempts."""
        sprint = _load()
        root = self._repo()
        calls: list = []
        gate = self._gate(calls)
        self._attempt(sprint, root, gate)
        self.assertEqual(len(calls), 1)
        (root / "src" / "code.py").write_text("x = 2\n", encoding="utf-8")
        ok, detail, _ = self._attempt(sprint, root, gate)
        self.assertTrue(ok)
        self.assertEqual(len(calls), 2, "a changed surface pays for the gate again")
        self.assertNotIn("REUSED", detail)

    def test_a_red_verdict_is_never_reused(self) -> None:
        """A recorded refusal is not a verdict worth saving anyone a run: the surface that
        earned it is exactly the surface that must be re-judged."""
        sprint = _load()
        root = self._repo()
        calls: list = []
        red = self._gate(calls, rc=1)
        ok, _, _ = self._attempt(sprint, root, red)
        self.assertFalse(ok)
        self.assertEqual(len(calls), 1)
        ok, detail, _ = self._attempt(sprint, root, red)
        self.assertEqual(len(calls), 2, "a red verdict is re-run, never reused")
        self.assertNotIn("REUSED", detail)

    def test_an_unhashable_surface_runs_rather_than_reuses(self) -> None:
        """None is UNKNOWN, never `unchanged`. A cache that answered skip on a thing not known
        would be the false-green class the whole gate exists to refuse."""
        sprint = _load()
        root = self._repo()
        calls: list = []
        gate = self._gate(calls)
        self._attempt(sprint, root, gate)
        broken = self._gate(calls)
        def _boom(root="."):
            raise OSError("the surface cannot be listed")
        broken.surface_files = _boom
        ok, detail, _ = self._attempt(sprint, root, broken)
        self.assertEqual(len(calls), 2, "an unknown surface pays in full")
        self.assertNotIn("REUSED", detail)

    def test_every_gate_run_is_recorded_in_the_execution_ledger(self) -> None:
        """The close's own runs are the half of the execution actuals the close can measure;
        without the record the retro reports the cost as uncaptured."""
        sprint = _load()
        root = self._repo()
        calls: list = []
        gate = self._gate(calls)
        self._attempt(sprint, root, gate)
        self._attempt(sprint, root, gate)
        rows = sprint.read_execution_ledger(root)
        self.assertEqual([r["mode"] for r in rows], ["full", "reuse"])
        self.assertEqual(rows[0]["moment"], "close")
        self.assertIsNotNone(rows[0]["seconds"])
        self.assertEqual(rows[1]["reused_from"], rows[0]["at"])


# ---------------------------------------------------------------------------
# The lane contract: what a lane is dispatched with, and what it must return.
# ---------------------------------------------------------------------------


def _lane_story(root: Path, num: int, ac_section: str, affects: str = "src/lane.py",
                points: int = 2, status: str = "Ready") -> Path:
    """A story whose Acceptance Criteria section is written verbatim by the caller, so a test
    can hand the lane contract the exact shape it is meant to judge (absent, placeholder or
    authored) without a helper deciding it."""
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    _affect(root, affects)
    p = d / f"US{num:04d}-lane.md"
    p.write_text(f"# US{num:04d}: a lane unit\n\n> **Status:** {status}\n"
                 f"> **Priority:** Medium\n> **Affects:** {affects}\n> **Points:** {points}\n\n"
                 f"## User Story\n\n**As a** x **I want** y **So that** z\n\n{ac_section}",
                 encoding="utf-8")
    return p


class LaneContractTests(unittest.TestCase):
    """US0508. Six units reached Fixed last sprint carrying no acceptance criterion at all: the
    lane inferred a contract from the summary, delivered against the inference, and nothing
    downstream could tell the difference. A lane that cannot read what it is being held to must
    say so at dispatch, when the cost is a sentence, rather than at review."""

    def test_a_unit_with_no_criteria_is_refused_at_dispatch(self) -> None:
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _lane_story(root, 900, "")  # no Acceptance Criteria section at all
            contract = sprint.lane_contract(root, "US0900")
            self.assertFalse(contract["ok"])
            self.assertIn("US0900", contract["refusal"])
            self.assertIn("acceptance criteria", contract["refusal"].lower())
            dispatch = sprint.lane_dispatch(root, ["US0900"])
            self.assertEqual([r["id"] for r in dispatch["refused"]], ["US0900"])
            self.assertEqual(dispatch["briefs"], [])

    def test_an_ungroomed_placeholder_is_refused_too(self) -> None:
        sprint = _load()
        sdlc_md = sys.modules["sdlc_md"] if "sdlc_md" in sys.modules else None
        token = sdlc_md.UNGROOMED_AC_TOKEN if sdlc_md else (
            "Ungroomed - acceptance criteria are a grooming placeholder")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _lane_story(root, 901, f"## Acceptance Criteria\n\n- {token}\n")
            contract = sprint.lane_contract(root, "US0901")
            self.assertFalse(contract["ok"], "a placeholder is an absent contract in the shape "
                                             "of one")
            self.assertIn("placeholder", contract["refusal"].lower())
            _lane_story(root, 902, "## Acceptance Criteria\n\n### AC1: {{criterion}}\n\n"
                                   "- **Given** {{context}}\n- **Verify:** {{command}}\n")
            self.assertFalse(sprint.lane_contract(root, "US0902")["ok"],
                             "the bare template scaffold is the same absence, older shape")

    def test_criteria_the_runner_cannot_parse_are_refused_not_dispatched_empty(self) -> None:
        """The checkbox shape - what 475 live units carry. `_ac_signals` reads it as authored
        while the runner's parser returns no blocks, so the unit passed the gate with an EMPTY
        contract and was dispatched under the very obligation to refuse it.

        Pinned here because it was not: the refusal shipped asserted by nothing, and replacing
        its condition with a constant false left the whole suite green. US0505 - shipped in the
        same batch - is the rule that a behaviour change carries a test a silent revert reddens.
        """
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _lane_story(root, 904, "## Acceptance Criteria\n\n"
                                   "- [x] the lane refuses a unit it cannot read\n"
                                   "- [ ] and says which shape it wanted\n")
            contract = sprint.lane_contract(root, "US0904")
            self.assertFalse(contract["ok"],
                             "criteria the runner cannot parse are an empty contract, and a "
                             "lane dispatched on one can never report the unit fixed")
            self.assertIn("US0904", contract["refusal"])
            self.assertIn("### AC", contract["refusal"],
                          "the refusal must name the shape it wanted, or the author cannot act")
            self.assertEqual(contract["criteria"], [])
            dispatch = sprint.lane_dispatch(root, ["US0904"])
            self.assertEqual([r["id"] for r in dispatch["refused"]], ["US0904"])
            self.assertEqual(dispatch["briefs"], [])

    def test_one_parser_decides_and_builds_the_contract(self) -> None:
        """The root defect was two parsers answering one question: `_ac_signals` decided and
        `parse_story` built. Whatever decides must be what builds, or the gap between them is
        where a unit slips through - silently, because each parser is individually correct."""
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _lane_story(root, 905, "## Acceptance Criteria\n\n### AC1: it holds\n\n"
                                   "- **Given** a thing\n- **Verify:** file src/lane.py\n")
            ok = sprint.lane_contract(root, "US0905")
            self.assertTrue(ok["ok"])
            self.assertTrue(ok["criteria"], "a dispatched unit must carry a NON-EMPTY contract")
            _lane_story(root, 906, "## Acceptance Criteria\n\n- [x] prose only\n")
            bad = sprint.lane_contract(root, "US0906")
            self.assertFalse(bad["ok"])
            self.assertEqual(bool(ok["criteria"]), ok["ok"])
            self.assertEqual(bool(bad["criteria"]), bad["ok"],
                             "ok and a readable contract must be the same answer - they were "
                             "two answers, and 475 units were dispatched on the gap")

    def test_an_authored_unit_is_dispatched(self) -> None:
        """The positive control. A refusal that fires on everything is not a gate, and a test
        suite that only ever asserts the refusal cannot tell one from the other."""
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _lane_story(root, 903, "## Acceptance Criteria\n\n### AC1: it holds\n\n"
                                   "- **Given** a thing\n- **Verify:** file src/lane.py\n")
            contract = sprint.lane_contract(root, "US0903")
            self.assertTrue(contract["ok"], contract.get("refusal"))
            self.assertEqual([c["ac"] for c in contract["criteria"]], ["AC1"])
            dispatch = sprint.lane_dispatch(root, ["US0903"])
            self.assertEqual(dispatch["refused"], [])
            self.assertEqual([b["id"] for b in dispatch["briefs"]], ["US0903"])

    def test_the_dispatch_carries_the_obligations(self) -> None:
        """The obligations ride the DISPATCH, not the sprint brief somebody typed that night.

        The caller hands `lane_dispatch` a root and a list of ids and nothing else, and every
        brief comes back carrying every obligation - DERIVED from the shared `LANE_OBLIGATIONS`
        rather than listed here, so one added later is covered without editing this test. The
        three concerns are asserted as a floor because an emptied tuple would satisfy the
        derived loop while proving nothing.
        """
        sprint = _load()
        obligations = list(sprint.LANE_OBLIGATIONS)
        self.assertTrue(obligations, "an empty obligation set passes every derived check below")
        joined = " ".join(obligations).lower()
        for concern in ("acceptance criteria", "before returning", "proof"):
            self.assertIn(concern, joined, f"no obligation covers the {concern!r} concern")
        # the caller cannot supply them: there is nowhere in the signature to put them, so a
        # dispatch is never as good or as bad as the memory of whoever wrote that night's prompt
        self.assertEqual(list(inspect.signature(sprint.lane_dispatch).parameters),
                         ["repo_root", "unit_ids"],
                         "the dispatch must take its obligations from the shared template, "
                         "never from its caller")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            authored = ("## Acceptance Criteria\n\n### AC1: it holds\n\n"
                        "- **Given** a thing\n- **Verify:** file src/lane.py\n")
            _lane_story(root, 904, authored)
            _lane_story(root, 905, authored)
            dispatch = sprint.lane_dispatch(root, ["US0904", "US0905"])
            self.assertEqual(dispatch["refused"], [])
            self.assertEqual(len(dispatch["briefs"]), 2)
            for brief in dispatch["briefs"]:
                self.assertEqual(brief["obligations"], obligations,
                                 f"{brief['id']} was dispatched without the shared obligations")
            # each lane gets its own copy: an edit to what one lane received must not reach the
            # next dispatch, or the obligations stop being the same for every lane
            dispatch["briefs"][0]["obligations"].append("deliver on your own judgement")
            again = sprint.lane_dispatch(root, ["US0904"])
            self.assertEqual(again["briefs"][0]["obligations"], obligations)


class LaneVerifyTests(unittest.TestCase):
    """US0509. Every verifier below is REAL - `file` resolves to `test -e` and `pytest` to a
    pytest process - because the behaviour under test is what the runner actually reports, and a
    stubbed runner would only prove that this module can read a dictionary it wrote itself."""

    def test_a_red_criterion_returns_blocked_not_fixed(self) -> None:
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _lane_story(root, 910, "## Acceptance Criteria\n\n### AC1: the file is there\n\n"
                                   "- **Verify:** file src/lane.py\n\n"
                                   "### AC2: the other file is there\n\n"
                                   "- **Verify:** file src/never-written.py\n")
            result = sprint.lane_return(root, "US0910", claimed="fixed")
            self.assertEqual(result["outcome"], "blocked")
            self.assertEqual(result["claimed"], "fixed")
            self.assertIn("AC2", result["why"])
            self.assertEqual(result["verification"]["blocking"], ["AC2"])
            states = {c["ac"]: c["state"] for c in result["verification"]["criteria"]}
            self.assertEqual(states, {"AC1": "passed", "AC2": "failed"})

    def test_the_result_carries_the_verifier_output(self) -> None:
        """Not a summary of it. A lane that returns "all green" is asking to be trusted; one
        that returns the runner's own exit code and text can be checked."""
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "src").mkdir(parents=True, exist_ok=True)
            (root / "src" / "shout.sh").write_text("echo THE-RUNNER-SAID-THIS\n", encoding="utf-8")
            _lane_story(root, 911, "## Acceptance Criteria\n\n### AC1: it speaks\n\n"
                                   "- **Verify:** shell sh src/shout.sh\n")
            result = sprint.lane_return(root, "US0911", claimed="fixed")
            crit = result["verification"]["criteria"][0]
            self.assertEqual(crit["state"], "passed")
            self.assertEqual(crit["exit_code"], 0)
            self.assertEqual(crit["verifier"], "shell sh src/shout.sh")
            self.assertIn("THE-RUNNER-SAID-THIS", crit["output"])

    def test_an_unresolvable_criterion_is_not_a_pass(self) -> None:
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _lane_story(root, 912, "## Acceptance Criteria\n\n### AC1: a test that is not there\n"
                                   "\n- **Verify:** pytest tests/test_absent.py::Gone::test_gone"
                                   "\n")
            result = sprint.lane_return(root, "US0912", claimed="fixed")
            crit = result["verification"]["criteria"][0]
            self.assertEqual(crit["state"], "unresolved",
                             "a check that could not be answered is not a check that passed")
            self.assertEqual(result["outcome"], "blocked")
            self.assertIn("AC1", result["verification"]["blocking"])

    def test_a_green_unit_returns_what_the_lane_claimed(self) -> None:
        """The positive control: a gate that blocks everything reports the same as one that
        works, and only a green case can tell them apart."""
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _lane_story(root, 913, "## Acceptance Criteria\n\n### AC1: the file is there\n\n"
                                   "- **Verify:** file src/lane.py\n")
            result = sprint.lane_return(root, "US0913", claimed="fixed")
            self.assertEqual(result["outcome"], "fixed")
            self.assertTrue(result["verification"]["ok"])
            self.assertEqual(result["verification"]["blocking"], [])

    def test_an_unverifiable_criterion_blocks_rather_than_disappearing(self) -> None:
        """An AC with no Verify line proves nothing, so it cannot be counted as proven. It is
        reported unspecified and blocks, rather than vanishing from the arithmetic."""
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _lane_story(root, 914, "## Acceptance Criteria\n\n### AC1: nobody said how\n\n"
                                   "- **Given** a criterion with no verifier\n")
            result = sprint.lane_return(root, "US0914", claimed="fixed")
            self.assertEqual(result["verification"]["criteria"][0]["state"], "unspecified")
            self.assertEqual(result["outcome"], "blocked")


def _tsd_mutation_level(root: Path, *paths: str) -> None:
    """A TSD whose `## Test Levels` puts the given paths under `### Mutation Testing`, so a unit
    declaring one of them owes the `mutation` proof band."""
    body = ("# Test Strategy\n\n## Test Levels\n\n### Mutation Testing\n\n"
            + "".join(f"Covers `{p}`.\n" for p in paths)
            + "\n## Traceability\n\nend.\n")
    (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
    (root / "sdlc-studio" / "tsd.md").write_text(body, encoding="utf-8")


class LaneProofTests(unittest.TestCase):
    """US0510. The plan named the proof each unit owed and then nothing read it back at the
    lane, so six obligations went unmet in RUN-01KYJZGZ without one line of output saying so.
    The obligation is derived from the TSD through `test_strategy`, never listed here."""

    def _story(self, root: Path, num: int) -> None:
        _tsd_mutation_level(root, "src/lane.py")
        _lane_story(root, num, "## Acceptance Criteria\n\n### AC1: the file is there\n\n"
                               "- **Verify:** file src/lane.py\n")

    def test_a_lane_returns_the_assigned_proof(self) -> None:
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, 920)
            evidence = "3 mutants, 3 killed - sdlc-studio/.local/mutation-report.json"
            result = sprint.lane_return(root, "US0920", claimed="fixed",
                                        proof={"mutation": evidence})
            proof = result["proof"]
            self.assertEqual(proof["obligations"], ["mutation"])
            self.assertEqual(proof["discharged"],
                             [{"obligation": "mutation", "evidence": evidence}])
            self.assertEqual(proof["undischarged"], [])

    def test_an_undischarged_obligation_is_stated_not_omitted(self) -> None:
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, 921)
            silent = sprint.lane_return(root, "US0921", claimed="fixed")["proof"]
            self.assertEqual([g["obligation"] for g in silent["undischarged"]], ["mutation"])
            self.assertTrue(silent["undischarged"][0]["why"],
                            "a gap with no reason is the omission this unit exists to stop")
            self.assertEqual(silent["discharged"], [])
            stated = sprint.lane_return(
                root, "US0921", claimed="fixed",
                proof_gaps={"mutation": "no mutation runner on this machine"})["proof"]
            self.assertEqual(stated["undischarged"],
                             [{"obligation": "mutation",
                               "why": "no mutation runner on this machine"}])

    def test_an_underivable_strategy_is_reported_not_read_as_no_obligations(self) -> None:
        """An absence is not an answer. With no TSD the obligations cannot be derived, and
        reporting that as "this unit owes nothing" is the silent false-negative the carried
        lessons name."""
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _lane_story(root, 922, "## Acceptance Criteria\n\n### AC1: the file is there\n\n"
                                   "- **Verify:** file src/lane.py\n")
            proof = sprint.lane_return(root, "US0922", claimed="fixed")["proof"]
            self.assertFalse(proof["available"])
            self.assertIn("Test Levels", proof["why"])


def _carried_set(root: Path, *titles: str) -> Path:
    """The curated carried-lessons file the retro writes - a fixed-size set, numbered."""
    d = root / "sdlc-studio" / "retros"
    d.mkdir(parents=True, exist_ok=True)
    body = "# The carried lessons\n\nA fixed-size set.\n\n"
    for i, t in enumerate(titles, 1):
        body += f"## {i}. {t}\n\nWhy it is here.\n\n"
    p = d / "LESSONS-TOP.md"
    p.write_text(body, encoding="utf-8")
    return p


class CarriedLessonsBriefTests(unittest.TestCase):
    """US0520. The retro curates the set and the plan printed it once, into a terminal the
    delivery agent never sees. A lesson that reaches only the operator has been paid for and
    not spent, so it travels in every lane brief and in the reviewers'."""

    TITLES = ("a mechanism that reaches no caller is inert",
              "an absence is not an answer")

    def test_every_lane_brief_carries_the_set(self) -> None:
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _carried_set(root, *self.TITLES)
            ids = []
            for num in (930, 931, 932):
                _lane_story(root, num, "## Acceptance Criteria\n\n### AC1: it holds\n\n"
                                       f"- **Verify:** file src/lane{num}.py\n",
                            affects=f"src/lane{num}.py")
                ids.append(f"US{num:04d}")
            dispatch = sprint.lane_dispatch(root, ids)
            self.assertEqual(len(dispatch["briefs"]), 3)
            # Derived from what the dispatch produced, never from a list written here: a brief
            # added later is covered by this assertion without an edit.
            for brief in dispatch["briefs"]:
                text = sprint.lane_brief_text(brief)
                for title in self.TITLES:
                    self.assertIn(title, text, f"{brief['id']} went out without the carried set")
            # ...and in the lane worklists the plan exports for a team to pick up.
            batch = [{"id": i, "path": str(next((root / "sdlc-studio" / "stories").glob(
                f"{i}-*.md")))} for i in ids]
            out = sprint.export_lanes(root, batch, root / "export")
            self.assertTrue(out["lane_files"])
            for f in out["lane_files"]:
                body = Path(f).read_text(encoding="utf-8")
                for title in self.TITLES:
                    self.assertIn(title, body, f"{f} went out without the carried set")

    def test_the_review_brief_carries_the_set(self) -> None:
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _carried_set(root, *self.TITLES)
            (root / "sdlc-studio" / ".local").mkdir(parents=True, exist_ok=True)
            (root / "sdlc-studio" / ".local" / "sprint-plan.json").write_text(json.dumps(
                {"count": 1, "order": "priority", "sprint_goal": "g",
                 "breakdown": {"ungroomed": [], "clusters": []},
                 "reachable_end_state": {"state": "Review", "basis": "b"}}), encoding="utf-8")
            (root / "sdlc-studio" / ".local" / "run-state.json").write_text(json.dumps(
                {"schema": 1, "run_id": "R", "sprint_goal": "g", "batch": []}), encoding="utf-8")
            brief = sprint.seat_brief(root)
            for title in self.TITLES:
                self.assertIn(title, brief)

    def test_an_absent_set_is_reported(self) -> None:
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            # No LESSONS-TOP.md at all.
            missing = sprint.carried_lessons(root)
            self.assertFalse(missing["available"])
            self.assertTrue(missing["why"])
            _lane_story(root, 933, "## Acceptance Criteria\n\n### AC1: it holds\n\n"
                                   "- **Verify:** file src/lane.py\n")
            brief = sprint.lane_brief_text(sprint.lane_dispatch(root, ["US0933"])["briefs"][0])
            self.assertIn("CARRIED LESSONS UNAVAILABLE", brief)
            # A file that exists but names no lesson is the same unanswered question, not an
            # answer of "there are none".
            (root / "sdlc-studio" / "retros").mkdir(parents=True, exist_ok=True)
            (root / "sdlc-studio" / "retros" / "LESSONS-TOP.md").write_text(
                "# The carried lessons\n\nnothing curated yet.\n", encoding="utf-8")
            empty = sprint.carried_lessons(root)
            self.assertFalse(empty["available"])
            self.assertTrue(empty["why"])


class DropVersusDeferredDoneGateTests(unittest.TestCase):
    """US0433 AC3, verified where the AC actually makes its claim: at the DONE-GATE.

    The verifier this replaces asserted `assertIn`/`assertNotIn` on `run_state.read()["batch"]`
    and left the gate linkage in a comment. That is a proxy for the run state, not a test of the
    gate: it stays green if the gate is changed to skip Deferred units, and green if the gate
    stops reading `state["batch"]` at all - the two regressions the AC exists to rule out.

    So the gate is invoked. The two units are IDENTICAL in every respect the gate reads (same
    body, same unverified executable AC, both undelivered) and differ only in what was done to
    them: one transitioned to `Deferred` through the real transition, one removed with the real
    `batch drop`. Any difference in the refusal set is therefore attributable to that, and
    nothing else.
    """

    BODY = ("# {uid}: undelivered\n\n> **Status:** In Progress\n> **Points:** 2\n\n"
            "## Acceptance Criteria\n\n### AC1: it works\n\n- **Verify:** shell true\n")

    def _repo(self, d: str):
        root = Path(d)
        sd = root / "sdlc-studio" / "stories"
        sd.mkdir(parents=True)
        for uid in ("US0101", "US0102"):
            (sd / f"{uid}-x.md").write_text(self.BODY.format(uid=uid), encoding="utf-8")
        return root

    def _blocked_ids(self, blockers) -> set[str]:
        return {b["detail"].split(":")[0].strip() for b in blockers}

    def test_deferred_still_blocks_the_done_gate_while_dropped_does_not(self) -> None:
        import transition
        from lib import run_state
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d)
            run_state.open_run(root, batch=["US0101", "US0102"], goal="g")
            transition.transition(root, "US0101", "Deferred")   # judges the WORK
            self.assertIn("US0101", run_state.read(root)["batch"],
                          "Deferred must leave the unit in the batch the gate reads")
            run_state.drop_from_batch(root, "US0102", reason="out of scope for this batch")
            blockers = sprint._done_gate_preflight(root, run_state.read(root))
            blocked = self._blocked_ids(blockers)
        self.assertIn("US0101", blocked,
                      "the Deferred unit was released by the done-gate - Deferred judges the "
                      "WORK and must still block")
        self.assertNotIn("US0102", blocked,
                         "the dropped unit is still demanded by the done-gate - drop judges "
                         "THIS BATCH and must release it")
        self.assertEqual(len(blockers), 1, blockers)

    def test_the_gate_is_refusing_for_a_reason_not_returning_empty(self) -> None:
        """The control. With nothing dropped, BOTH identical units are refused - so the single
        refusal above is the drop's doing, not a gate that happens to name one unit."""
        import transition
        from lib import run_state
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d)
            run_state.open_run(root, batch=["US0101", "US0102"], goal="g")
            transition.transition(root, "US0101", "Deferred")
            blocked = self._blocked_ids(
                sprint._done_gate_preflight(root, run_state.read(root)))
        self.assertEqual(blocked, {"US0101", "US0102"})


class LaneTrustBoundaryTests(unittest.TestCase):
    """The lane runner must not be more permissive than the authoritative one. It was: a story
    stamped `Provenance: external` with a `shell` verifier was FAILED by verify_ac and PASSED by
    the lane, which also executed the command. Both now read one shared rule."""

    def _story(self, root, provenance, marker):
        d = root / "sdlc-studio" / "stories"
        d.mkdir(parents=True, exist_ok=True)
        p = d / "US0777-x.md"
        prov = f"> **Provenance:** {provenance}\n" if provenance else ""
        p.write_text(f"# US0777: probe\n\n> **Status:** Ready\n{prov}> **Epic:** EP0001\n\n"
                     f"## Acceptance Criteria\n\n### AC1: probe\n\n- **Given** x\n- **When** y\n"
                     f"- **Then** z\n- **Verify:** shell touch {marker}\n", encoding="utf-8")
        (d / "_index.md").write_text(
            "# Stories\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            "| [US0777](US0777-x.md) | probe | Ready |\n", encoding="utf-8")
        return p

    def test_an_external_provenance_shell_verifier_does_not_run_in_the_lane(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            marker = root / "PWNED"
            self._story(root, "external", marker)
            res = sprint.lane_verify(root, "US0777")
            self.assertFalse(marker.exists(),
                             "the lane executed shell from an external-provenance artefact")
            self.assertTrue(res["blocking"], "an unrunnable verifier must block, not pass")

    def test_the_lane_and_the_authoritative_runner_agree(self):
        import verify_ac
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            marker = root / "PWNED"
            path = self._story(root, "external", marker)
            lane_ok = sprint.lane_verify(root, "US0777")["ok"]
            report = verify_ac.verify_story(path, dry_run=True, timeout=30, repo_root=root)
            self.assertEqual(lane_ok, report.failed == 0,
                             "the lane and verify_story must reach the SAME verdict on one file")

    def test_a_local_provenance_shell_verifier_still_runs(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            marker = root / "RAN"
            self._story(root, "", marker)
            sprint.lane_verify(root, "US0777")
            self.assertTrue(marker.exists(),
                            "the fix must not disable shell verifiers for ordinary artefacts")


class SeatBriefGoalTests(unittest.TestCase):
    """BG0381. `seat_brief` took no goal argument at all, so the CLI's `--goal` never reached
    it, and both branches let the run state override unconditionally - including a CLOSED run.
    The seats were briefed on one goal and their verdict recorded against another, and
    `plan --write` cannot catch that: by then both sides name the same string."""

    def _root(self, d) -> Path:
        root = Path(d)
        (root / "sdlc-studio" / ".local").mkdir(parents=True)
        return root

    def test_a_goal_passed_to_the_brief_is_the_goal_it_names(self) -> None:
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            _load().run_state.open_run(root, batch=["US0001"])
            _load().run_state.update(root, sprint_goal="THE OLD GOAL")
            self.assertEqual(mod._brief_goal(root, "THE NEW GOAL", {}), "THE NEW GOAL")

    def test_a_closed_run_s_goal_does_not_reach_the_next_brief(self) -> None:
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            _load().run_state.open_run(root, batch=["US0001"])
            _load().run_state.update(root, sprint_goal="THE OLD GOAL")
            _load().run_state.update(root, ended_at="2026-07-28T10:00:00Z")
            self.assertIsNone(mod._brief_goal(root, None, {}))

    def test_an_open_run_s_goal_is_still_the_fallback(self) -> None:
        """The carve-out is about a CLOSED run, not about ignoring run state - a brief taken
        mid-sprint should describe the sprint that is running."""
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            _load().run_state.open_run(root, batch=["US0001"])
            _load().run_state.update(root, sprint_goal="THE OPEN GOAL")
            self.assertEqual(mod._brief_goal(root, None, {}), "THE OPEN GOAL")

    def test_the_plan_s_goal_outranks_the_run_state(self) -> None:
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            _load().run_state.open_run(root, batch=["US0001"])
            _load().run_state.update(root, sprint_goal="THE OLD GOAL")
            self.assertEqual(mod._brief_goal(root, None, {"sprint_goal": "THE PLANNED GOAL"}),
                             "THE PLANNED GOAL")


class GoalClauseTests(unittest.TestCase):
    """US0541. A Sprint Goal with more than one clause was judged with one word, so a goal
    reached in two parts of three had to be reported as achieved or missed - both wrong."""

    THREE = ("A sprint tells the truth about itself: seams have owners, the goal is judged by "
             "a panel, and the defects are repaired rather than carried")

    def test_a_three_clause_goal_reports_three_verdicts(self) -> None:
        self.assertEqual(len(_load().run_state.goal_clauses(self.THREE)), 3)

    def test_a_single_clause_goal_is_one_clause_not_shredded(self) -> None:
        """Conservative on purpose: a comma is ordinary punctuation unless the sentence also
        carries the Oxford `, and ` an operator uses to enumerate commitments."""
        self.assertEqual(_load().run_state.goal_clauses("Ship the widget, quickly"),
                         ["Ship the widget, quickly"])

    def test_semicolons_separate_and_a_hyphenated_word_does_not(self) -> None:
        self.assertEqual(len(_load().run_state.goal_clauses("A thing; another thing; a third")), 3)
        self.assertEqual(len(_load().run_state.goal_clauses("Ship the well-tested widget")), 1)

    def test_no_goal_yields_no_clauses_rather_than_one_empty_one(self) -> None:
        self.assertEqual(_load().run_state.goal_clauses(""), [])
        self.assertEqual(_load().run_state.goal_clauses(None), [])

    def test_the_verdict_record_carries_the_clauses_beside_the_word(self) -> None:
        """Beside, not instead of: the single word is what every existing reader consumes, and
        the clause list is what makes `partial` mean something specific."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / ".local").mkdir(parents=True)
            _load().run_state.open_run(root, batch=["US0001"])
            _load().run_state.update(root, sprint_goal=self.THREE)
            rec = _load().run_state.record_goal_verdict(
                root, "partial", clauses=[{"clause": "seams have owners", "verdict": "achieved"},
                                          {"clause": "the goal is judged", "verdict": "missed"}])
            self.assertEqual(rec["verdict"], "partial")
            self.assertEqual([c["verdict"] for c in rec["clauses"]], ["achieved", "missed"])


class SprintNamingTests(unittest.TestCase):
    """US0548-US0550. A sprint was identified by a run id alone, so a list of them said nothing
    about what any of them was for without opening each one."""

    def test_a_sprint_file_carries_its_goal_slug(self) -> None:
        name = _load().run_state.sprint_name("RUN-01KYMJEM", "ship the widget end to end")
        self.assertTrue(name.startswith("sprint-RUN-01KYMJEM-"))
        self.assertIn("ship-the-widget", name)

    def test_the_run_id_resolves_a_sprint_whose_slug_is_stale(self) -> None:
        """The reason the id stays first and canonical: a goal is routinely reworded between
        the plan and the close, and a name that resolved only through its slug would orphan
        every reference to that sprint the moment it changed."""
        self.assertEqual(_load().run_state.run_id_from_name("sprint-RUN-01KYMJEM-an-old-wording"),
                         "RUN-01KYMJEM")
        self.assertEqual(
            _load().run_state.run_id_from_name(_load().run_state.sprint_name("RUN-01KYMJEM", "a new wording")),
            "RUN-01KYMJEM")

    def test_a_run_with_no_goal_is_named_by_id_alone(self) -> None:
        """No invented slug. A goal nobody wrote is absent, not guessed - the same discipline
        as reporting an unmeasured figure rather than zero."""
        self.assertEqual(_load().run_state.sprint_name("RUN-01KYMJEM"), "sprint-RUN-01KYMJEM")
        self.assertEqual(_load().run_state.sprint_name("RUN-01KYMJEM", "   "), "sprint-RUN-01KYMJEM")

    def test_a_name_with_no_run_id_resolves_to_nothing(self) -> None:
        self.assertIsNone(_load().run_state.run_id_from_name("sprint-something-else"))

    def test_an_empty_run_id_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            _load().run_state.sprint_name("", "a goal")


class SeamBriefTests(unittest.TestCase):
    """US0539. The seam is a fact about a PAIR, and a lane reads one unit - so the neighbouring
    property a lane must not regress is the one thing it can never learn from its own brief's
    unit. Asserted on the brief's CONTENT, not on the map's existence: a map computed and not
    rendered helps nobody."""

    def _unit(self, root: Path, uid: str, affects: str) -> None:
        d = root / "sdlc-studio" / "stories"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{uid}-x.md").write_text(
            f"# {uid}: x\n\n> **Status:** Ready\n> **Affects:** {affects}\n\n"
            f"## Acceptance Criteria\n\n### AC1: it works\n\n- **Verify:** shell true\n",
            encoding="utf-8")

    def test_the_brief_names_the_neighbouring_property(self) -> None:
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root, "US0001", "src/thing.py")
            self._unit(root, "US0002", "src/thing.py")
            dispatch = mod.lane_dispatch(root, ["US0001", "US0002"])
            texts = {b["id"]: mod.lane_brief_text(b) for b in dispatch["briefs"]}
            self.assertIn("Seam with US0002", texts["US0001"])
            self.assertIn("src/thing.py", texts["US0001"])
            self.assertIn("Seam with US0001", texts["US0002"])

    def test_a_lane_with_no_seam_carries_no_seam_line(self) -> None:
        """A brief that always names a seam is one whose seam lines are furniture."""
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root, "US0001", "src/a.py")
            self._unit(root, "US0002", "src/b.py")
            dispatch = mod.lane_dispatch(root, ["US0001", "US0002"])
            for b in dispatch["briefs"]:
                self.assertNotIn("Seam with", mod.lane_brief_text(b))

    def test_the_dispatch_carries_the_map_for_the_review_brief_too(self) -> None:
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root, "US0001", "src/thing.py")
            self._unit(root, "US0002", "src/thing.py")
            self.assertEqual(len(mod.lane_dispatch(root, ["US0001", "US0002"])["seams"]), 1)


class LaneInFlightTests(unittest.TestCase):
    """BG0355. A lane that dies mid-flight leaves real code in the working tree behind a unit
    still marked Ready, and a restart cannot tell a delivered unit from an untouched one - the
    revision row is written BEFORE the work. Observed four times in one night; one restarted
    lane was dispatched onto three units whose repair was already present, with no signal, and
    a partial edit reached a commit that way."""

    def _root(self, d) -> Path:
        root = Path(d)
        (root / "sdlc-studio" / ".local").mkdir(parents=True)
        return root

    def test_a_briefed_unit_is_marked_in_flight(self) -> None:
        rs = _load().run_state
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            rs.open_run(root, batch=["US0001"])
            rs.record_lane_start(root, "US0001")
            self.assertEqual([r["unit"] for r in rs.lanes_in_flight(root)], ["US0001"])

    def test_a_returned_unit_is_cleared_whatever_the_outcome(self) -> None:
        """A BLOCKED return is still a lane that came back. Leaving the marker set would warn
        about a unit nobody is mid-way through, and a warning that fires on everything is one
        an operator learns to scroll past."""
        rs = _load().run_state
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            rs.open_run(root, batch=["US0001"])
            rs.record_lane_start(root, "US0001")
            self.assertTrue(rs.record_lane_return(root, "US0001"))
            self.assertEqual(rs.lanes_in_flight(root), [])

    def test_clearing_a_unit_that_was_never_dispatched_reports_false(self) -> None:
        rs = _load().run_state
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            rs.open_run(root, batch=["US0001"])
            self.assertFalse(rs.record_lane_return(root, "US0009"))

    def test_a_dispatch_that_never_returned_survives_to_be_reported(self) -> None:
        """The property that matters: the marker OUTLIVES the process that set it, because the
        lane that would have cleared it is the one that died."""
        rs = _load().run_state
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            rs.open_run(root, batch=["US0001", "US0002"])
            rs.record_lane_start(root, "US0001")
            rs.record_lane_start(root, "US0002")
            rs.record_lane_return(root, "US0001")
            self.assertEqual([r["unit"] for r in rs.lanes_in_flight(root)], ["US0002"])
            self.assertTrue(rs.lanes_in_flight(root)[0]["started_at"])

    def test_a_re_dispatch_does_not_duplicate_the_marker(self) -> None:
        rs = _load().run_state
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            rs.open_run(root, batch=["US0001"])
            rs.record_lane_start(root, "US0001")
            rs.record_lane_start(root, "US0001")
            self.assertEqual(len(rs.lanes_in_flight(root)), 1)

    def test_no_open_run_records_nothing_rather_than_raising(self) -> None:
        rs = _load().run_state
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            self.assertIsNone(rs.record_lane_start(root, "US0001"))


class GoalContentReviewTests(unittest.TestCase):
    """US0545-US0547. The seats reviewed whether a GOAL was achievable; nobody ever asked
    whether the chosen CONTENT would deliver it, or - at the other end - whether what was
    delivered did. A plan-time answer nobody scores is one given carelessly."""

    def _root(self, d) -> Path:
        root = Path(d)
        (root / "sdlc-studio" / ".local").mkdir(parents=True)
        _load().run_state.open_run(root, batch=["US0001"])
        return root

    def test_an_unexplained_partial_is_refused(self) -> None:
        """The value of the question is the LIST of what the content does not cover. An
        unexplained doubt records something nobody can act on and the close cannot score."""
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            with self.assertRaises(ValueError) as caught:
                mod.record_content_review(root, "plan", "G", "partial")
            self.assertIn("NAME what is missing", str(caught.exception))
            with self.assertRaises(ValueError):
                mod.record_content_review(root, "plan", "G", "no", missing="   ")

    def test_a_yes_needs_no_missing_list(self) -> None:
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            self.assertEqual(mod.record_content_review(root, "plan", "G", "yes")["answer"],
                             "yes")

    def test_the_close_question_supplies_the_shortfall(self) -> None:
        """SUPPLIED, not recalled: the judgement rests on the evidence in front of the panel,
        which is the difference between a review and a recollection."""
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            entry = mod.record_content_review(
                root, "close", "G", "partial", missing="the panel half never ran",
                shortfall={"undelivered": ["US0002"], "defects": ["BG0009"]})
            self.assertEqual(entry["shortfall"]["undelivered"], ["US0002"])
            self.assertEqual(entry["shortfall"]["defects"], ["BG0009"])

    def test_a_prediction_miss_is_reported(self) -> None:
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            mod.record_content_review(root, "plan", "G", "yes")
            mod.record_content_review(root, "close", "G", "partial", missing="a clause slipped")
            miss = mod.prediction_miss(root)
            self.assertIn("PREDICTION MISS", miss)

    def test_agreement_reports_no_miss_and_one_end_alone_reports_nothing(self) -> None:
        """A report that always fires is one nobody reads, and a miss claimed from one answer
        would be a comparison against nothing."""
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            mod.record_content_review(root, "plan", "G", "yes")
            self.assertIsNone(mod.prediction_miss(root))
            mod.record_content_review(root, "close", "G", "yes")
            self.assertIsNone(mod.prediction_miss(root))

    def test_both_answers_are_recorded_side_by_side(self) -> None:
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            mod.record_content_review(root, "plan", "G", "yes")
            mod.record_content_review(root, "close", "G", "no", missing="nothing landed")
            rev = mod.content_reviews(root)
            self.assertEqual((rev["plan"]["answer"], rev["close"]["answer"]), ("yes", "no"))

    def test_re_recording_one_end_replaces_it_rather_than_appending(self) -> None:
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            mod.record_content_review(root, "plan", "G", "partial", missing="first")
            mod.record_content_review(root, "plan", "G", "yes")
            self.assertEqual(mod.content_reviews(root)["plan"]["answer"], "yes")


class FileAndCloseGroupingTests(unittest.TestCase):
    """US0551/US0552. One owed sign-off across twenty-three units is ONE thing to fix, and it
    arrived in the discovery backlog as twenty-three identical change requests - a cost paid
    twice, once at the close and again by whoever had to work out they were one."""

    def _blockers(self, n: int) -> list[dict]:
        return [{"stage": "sign-off", "detail": f"US{500 + i:04d}: no critic verdict",
                 "remedy": f"record a sign-off for US{500 + i:04d}"} for i in range(n)]

    def test_one_cause_files_one_artefact_listing_its_units(self) -> None:
        mod = _load()
        groups = mod.group_blockers(self._blockers(4))
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0]["units"], ["US0500", "US0501", "US0502", "US0503"])

    def test_distinct_causes_are_filed_separately(self) -> None:
        """Grouping must not merge unrelated blockers - hiding one behind another is worse
        than filing both."""
        mod = _load()
        mixed = self._blockers(2) + [{"stage": "retro", "detail": "no retro exists",
                                      "remedy": "write the retro"}]
        self.assertEqual(len(mod.group_blockers(mixed)), 2)

    def test_the_close_reports_filings_and_cause_count(self) -> None:
        """A fan-out is visible at the moment it happens rather than discovered later."""
        mod = _load()
        groups = mod.group_blockers(self._blockers(23))
        self.assertEqual(len(groups), 1)
        self.assertEqual(len(groups[0]["blockers"]), 23)

    def test_a_single_blocker_still_files_one_artefact(self) -> None:
        mod = _load()
        self.assertEqual(len(mod.group_blockers(self._blockers(1))), 1)


class DefectAgainstGoalTests(unittest.TestCase):
    """US0543. Whether an open defect could be left was decided on a severity somebody guessed,
    with no connection to what the sprint set out to do."""

    CLAUSES = ["seams have owners", "the goal is judged clause by clause"]

    def test_a_clause_falsifying_defect_blocks_and_others_are_recorded_leavable(self) -> None:
        import critic
        r = critic.judge_defects_against_goal(
            [{"id": "BG0001", "priority": "Medium"},
             {"id": "BG0002", "priority": "Low", "falsifies": "seams have owners"}], self.CLAUSES)
        self.assertEqual([d["id"] for d in r["blocking"]], ["BG0002"])
        self.assertEqual([d["id"] for d in r["leavable"]], ["BG0001"])
        self.assertIn("priority medium", r["leavable"][0]["why"])

    def test_a_release_stopping_priority_blocks_whatever_the_clause_reasoning(self) -> None:
        """A clause argument can be made for almost anything, so the severity floor is not
        negotiable by it: 'the goal was met anyway' is not an answer to a user who cannot work
        around the defect."""
        import critic
        r = critic.judge_defects_against_goal([{"id": "BG0003", "priority": "P1"}], self.CLAUSES)
        self.assertEqual([d["id"] for d in r["blocking"]], ["BG0003"])

    def test_nothing_is_silently_dropped(self) -> None:
        import critic
        defects = [{"id": f"BG{n:04d}", "priority": "Low"} for n in range(1, 6)]
        r = critic.judge_defects_against_goal(defects, self.CLAUSES)
        self.assertEqual(len(r["blocking"]) + len(r["leavable"]), len(defects))


if __name__ == "__main__":
    unittest.main()
