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


#: DERIVED from the module, never hand-copied. The hand-maintained duplicate had already
#: drifted (it omitted `review-anchor`), and adding a step to the chain then reddened 17
#: close tests at once because the new step ran unpatched against fixtures that cannot
#: satisfy it. A list of the thing under test, maintained beside the thing under test, is a
#: list that goes stale silently.
_CLOSE_STEP_NAMES = tuple(_load()._CLOSE_CHAIN)


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
            self.assertEqual(calls, [*_CLOSE_STEP_NAMES[:_CLOSE_STEP_NAMES.index("lessons-summary") + 1]],
                             "the chain did not run every step up to the failing one, in order")
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
            self.assertEqual(calls[0], _CLOSE_STEP_NAMES[0])  # reached and ran the chain
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


class CloseReportReachesTheOperatorTests(_CloseReportBase):
    """US0604 at the LANE, not the library.

    Both of US0604's criteria call `sprint_report.close_report()` directly, so they were green
    for a whole sprint while the caller raised NameError on `critic` and its own advisory
    `except` ate it. The report printed only for an EMPTY batch - a batch size no real close
    has - so the one input the feature exists to serve was exactly the one it failed on.

    A library test cannot see a missing import in its caller. This drives the close.
    """

    def test_the_close_prints_the_report_for_a_non_empty_batch(self) -> None:
        """MUTANT: drop `import critic` from `_tell_the_operator`.

        Driven through `_finalise_outcome`, the PRODUCTION caller, rather than through
        `close_report` itself. The batch is non-empty (`_close_state` carries US0101), which
        is the whole point: an empty batch takes no lap of the `unit_review_rounds` loop, so
        an empty-batch fixture passes against the broken code and pins nothing.

        Note it cannot ride on `_CloseReportBase._close`: that helper patches every chain
        step, including the one whose success path reaches this report.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            # NOT `_fixture`: that stamps the outcome goal-reached already, and
            # `_finalise_outcome` returns before the report on an already-stamped run. This is
            # the state a real close arrives with - judged achieved, not yet stamped.
            state = _close_state(root, outcome="running",
                                 sprint_goal_verdict={"verdict": "achieved",
                                                      "note": "chain ran"})
            _close_story(root)
            _close_retro(root, batch="US0101")
            mod = _load()
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                mod._finalise_outcome(root, state)
            printed, errored = out.getvalue(), err.getvalue()
            self.assertNotIn("close report not emitted", errored,
                             "the report step raised and was swallowed as advisory")
            self.assertIn("CLOSE REPORT", printed,
                          "the close never told the operator what it did")
            self.assertIn("US0101", printed, "the report names no unit from the batch")
            # AC1's four sections, asserted HERE rather than only against the renderer, so the
            # criterion's oracle is the close rather than the function the close forgot to
            # reach. A report missing the cost is not 75% of a report - it is one the operator
            # has to go and look something up for, which is the behaviour being removed.
            for heading in ("SHIPPED", "CARRIED", "COST", "FINDINGS"):
                self.assertIn(heading, printed.upper(),
                              f"the close's report has no {heading} section")


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
            # BOTH lists. `defer` writes `pending_decisions` AND `deferred_units`; only one had
            # a remover, so an answered question left the unit "deferred" for ever and the
            # close reported it held on an operator decision while counting it delivered.
            self.assertEqual(state["deferred_units"], [],
                             "the unit is still recorded as deferred after its question was "
                             "answered - the two lists have come apart")

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


class StopAwaitingSignoffTests(unittest.TestCase):
    """BG0455: `stop` could not tell an unbuilt unit from one the two-role gate holds.

    A unit at Review on a project past `review.two_role_after` is not buildable by anyone in
    the authoring session - Done needs a reviewer-of-record sign-off the session is explicitly
    refused. Stopping RUN-01KYPZ1G named 14 such units as `could have proceeded` and demanded
    --force, when nothing the run could do would have moved one of them. The cost is not only
    the friction: --force exists to record what parking a run threw away, so the run record
    overstated the loss, and reaching for it became a habit when it must stay expensive.
    `reachable_end_state` already draws this distinction at plan time; `stop` never read it.
    """

    def _fixture(self, root: Path, statuses: dict, *, evidence: bool = True) -> None:
        """A run whose Review units have had their ADVERSARIAL PASS recorded.

        `evidence=True` by default because that is the state these tests are about: the only
        outstanding half is the signature, which the authoring session is refused. Without it
        the units are ordinary remaining work - the evidence half is session-doable, since
        `record_evidence` accepts an authoring-session reviewer while `record_signoff` refuses
        the same id. Every fixture here originally omitted it, so the class asserted that a
        unit owing its adversarial pass was "finished bar a signature" and pinned the defect an
        independent seat then found.
        """
        _close_state(root, batch=sorted(statuses))
        (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
        (root / "sdlc-studio" / ".config.yaml").write_text(
            "review:\n  two_role_after: 100\n", encoding="utf-8")
        d = root / "sdlc-studio" / "stories"
        d.mkdir(parents=True, exist_ok=True)
        for uid, status in statuses.items():
            (d / f"{uid}-x.md").write_text(
                f"# {uid}: s\n\n> **Status:** {status}\n> **Priority:** Medium\n"
                f"> **Affects:** src/a.py\n", encoding="utf-8")
        if evidence:
            import critic
            for uid, status in statuses.items():
                if critic.is_awaiting_signoff(status):
                    critic.record_evidence(root, uid, reviewer="an independent seat",
                                           author="the authoring session",
                                           findings="adversarial pass run; none blocking")

    def test_a_unit_held_at_Review_is_not_reported_as_able_to_proceed(self) -> None:
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._fixture(root, {"US0101": "Review", "US0102": "Ready"})
            out = mod.blocked_by_pending(root)
        self.assertEqual(["US0102"], out["unblocked"],
                         "a unit awaiting a signature is counted as work the run declined to do")
        self.assertEqual(["US0101"], out["awaiting_signoff"])

    def test_a_stop_is_not_refused_when_only_signatures_are_outstanding(self) -> None:
        """The filed reproduction: the run is finished, and the only thing outstanding is a
        signature this session is forbidden to give. That is a fact for the operator, not a
        refusal aimed at the agent."""
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._fixture(root, {"US0101": "Review", "US0102": "Review"})
            buf_out, buf_err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
                rc = mod.cmd_stop(argparse.Namespace(root=str(root), force=False,
                                                     reason="done bar the signatures"))
        self.assertEqual(0, rc, buf_err.getvalue())
        self.assertIn("await", (buf_out.getvalue() + buf_err.getvalue()).lower())

    def test_a_genuinely_unbuilt_unit_still_refuses_the_stop(self) -> None:
        """The positive control. Without it, a change that simply stopped refusing would pass
        the test above while removing the guard entirely."""
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._fixture(root, {"US0101": "Review", "US0102": "Ready"})
            with contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()) as err:
                rc = mod.cmd_stop(argparse.Namespace(root=str(root), force=False, reason="x"))
        self.assertEqual(1, rc)
        self.assertIn("US0102", err.getvalue())
        self.assertNotIn("US0101", err.getvalue(),
                         "the held unit is named among the work that could have proceeded")

    def test_without_the_two_role_rule_Review_is_ordinary_remaining_work(self) -> None:
        """The rule is the PROJECT's, not a property of the status. With no cutoff configured,
        a unit at Review is work somebody in this session can still finish."""
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._fixture(root, {"US0101": "Review"})
            (root / "sdlc-studio" / ".config.yaml").write_text("{}\n", encoding="utf-8")
            out = mod.blocked_by_pending(root)
        self.assertEqual(["US0101"], out["unblocked"])
        self.assertEqual([], out["awaiting_signoff"])

    def test_a_unit_whose_two_role_bar_is_MET_is_still_remaining_work(self) -> None:
        """The fail-open an independent review reproduced. A unit with adversarial evidence AND
        an independent sign-off recorded can reach Done right now, so reporting it as "awaiting
        a signature this session cannot give" drops real remaining work out of the stop's
        refusal - the one direction this function's own docstring says it never takes."""
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._fixture(root, {"US0101": "Review"})
            calls = {}

            def _signoff_for(_root, unit):
                calls["asked"] = unit
                return {"principal": "the operator", "unit": unit}

            import critic
            with unittest.mock.patch.object(critic, "signoff_for", _signoff_for), \
                    unittest.mock.patch.object(critic, "is_independent_signoff",
                                               lambda *_a, **_k: True):
                out = mod.blocked_by_pending(root)
        self.assertEqual("US0101", calls.get("asked"), "the sign-off record is never consulted")
        self.assertEqual([], out["awaiting_signoff"])
        self.assertEqual(["US0101"], out["unblocked"],
                         "a unit that can reach Done today was dropped from the stop")

    def test_an_id_with_no_ordinal_is_held_like_reachable_end_state_holds_it(self) -> None:
        """A v3 ULID carries no ordinal, so `id_number` returns None. Treating that as "below
        the cutoff" made the whole fix inert for the id family the product mints by default -
        and took the opposite decision to `reachable_end_state`, which this fix claims to read,
        and to the provenance check repaired in the same run. One answer across the repo."""
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._fixture(root, {"US-01JQK3F8AA": "Review"})
            out = mod.blocked_by_pending(root)
        self.assertEqual(["US01JQK3F8AA"], out["awaiting_signoff"],
                         "a v3 id is reported as work the stop threw away")

    def test_a_renamed_review_status_is_still_held(self) -> None:
        """`== "review"` was a third spelling of a predicate critic already owns, and it missed
        a project using `In Review` - which critic's matcher exists to support."""
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._fixture(root, {"US0101": "In Review"})
            out = mod.blocked_by_pending(root)
        self.assertEqual(["US0101"], out["awaiting_signoff"])

    def test_a_critic_that_RAISES_leaves_the_unit_as_remaining_work(self) -> None:
        """Round-3 finding. Every uncertainty path in `_awaits_signoff` returns False; the
        signoff block fell through to `return True`, so a critic that raised DROPPED the unit
        from the stop's refusal - the direction that loses work silently, and the exact defect
        BG0455 was filed to end, reintroduced through its own repair.

        The mutant that proves it: making the handler fail-closed SURVIVED the entire
        5,669-test suite before this test existed."""
        mod = _load()
        import critic

        def boom(*_a, **_k):
            raise RuntimeError("critic is unavailable")

        # Each target must actually be REACHED, or the test proves nothing about it.
        # `is_independent_signoff` is short-circuited unless a sign-off exists, so that case
        # supplies one - a control against asserting over a call that never happens.
        cases = [
            ("is_awaiting_signoff", {}),
            ("signoff_for", {}),
            ("is_independent_signoff", {"signoff_for": lambda *_a, **_k: {"principal": "x"}}),
        ]
        for target, extra in cases:
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                self._fixture(root, {"US0101": "Review"})
                with contextlib.ExitStack() as stack:
                    for name, fn in extra.items():
                        stack.enter_context(unittest.mock.patch.object(critic, name, fn))
                    stack.enter_context(unittest.mock.patch.object(critic, target, boom))
                    out = mod.blocked_by_pending(root)
                self.assertEqual([], out["awaiting_signoff"],
                                 f"critic.{target} raising dropped the unit from the refusal")
                self.assertEqual(["US0101"], out["unblocked"],
                                 f"critic.{target} raising lost real remaining work silently")

    def test_the_matcher_is_criticS_public_one_not_a_local_copy(self) -> None:
        """The fallback used to be a byte-identical private copy behind a broad `except`, so
        deleting critic's predicate produced no error and no behaviour change - and tightening
        it would have left this call site silently on the old broad rule."""
        import critic
        self.assertTrue(hasattr(critic, "is_awaiting_signoff"),
                        "the cross-module caller depends on a private name")
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._fixture(root, {"US0101": "Review"})
            with unittest.mock.patch.object(critic, "is_awaiting_signoff",
                                            lambda _s: False):
                out = mod.blocked_by_pending(root)
        self.assertEqual([], out["awaiting_signoff"],
                         "critic's matcher is not consulted, so a local copy is deciding")

    def test_a_unit_STILL_OWING_its_adversarial_pass_is_remaining_work(self) -> None:
        """The seat's finding. The two-role bar has two halves and only the SIGNATURE is beyond
        this session: `record_evidence` accepts an authoring-session reviewer, `record_signoff`
        refuses the same id. So a unit whose adversarial pass has not been run is work this run
        could still dispatch, and reporting it as "awaiting a sign-off this session cannot give"
        drops it from the stop's refusal - the silent-loss direction this function exists to
        avoid. Checking only the signature made the two states indistinguishable."""
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._fixture(root, {"US0101": "Review"}, evidence=False)
            out = mod.blocked_by_pending(root)
        self.assertEqual([], out["awaiting_signoff"],
                         "a unit owing its adversarial pass is reported as merely awaiting a "
                         "signature, so the work is silently uncounted")
        self.assertEqual(["US0101"], out["unblocked"],
                         "the evidence half is session-doable and must stay in the refusal")

    def test_a_stop_IS_refused_while_an_adversarial_pass_is_owed(self) -> None:
        """The consequence end to end: the stop must not exit 0 over work the run could do."""
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._fixture(root, {"US0101": "Review"}, evidence=False)
            with contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()) as err:
                rc = mod.cmd_stop(argparse.Namespace(root=str(root), force=False, reason="x"))
        self.assertEqual(1, rc, "the stop exited clean over an un-reviewed unit")
        self.assertIn("US0101", err.getvalue())

    def test_SPRINT_LEVEL_coverage_counts_as_the_adversarial_pass(self) -> None:
        """The evidence half is satisfied by a per-unit row OR by a sprint-level review covering
        the unit - the same either/or `transition._two_role_gate` applies. Reading only the
        per-unit row would report a unit covered by a full-diff pass as still owing one, and
        hold a stop that should proceed. Mutation found this limb unpinned."""
        mod = _load()
        import critic
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._fixture(root, {"US0101": "Review"}, evidence=False)
            critic.record_sprint_review(
                root, ["US0101"], reviewer="an independent seat",
                author="the authoring session", verdict="APPROVE",
                findings="full-diff pass over the batch; none blocking")
            out = mod.blocked_by_pending(root)
        self.assertEqual(["US0101"], out["awaiting_signoff"],
                         "a unit covered by a sprint-level pass is reported as still owing one")
        self.assertEqual([], out["unblocked"])

    def test_a_unit_below_the_cutoff_is_not_held(self) -> None:
        """The cutoff is a number, and it must be read as one - a project sets it precisely so
        the rule applies to new work and not to everything already on disk."""
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._fixture(root, {"US0099": "Review"})
            out = mod.blocked_by_pending(root)
        self.assertEqual(["US0099"], out["unblocked"])
        self.assertEqual([], out["awaiting_signoff"])


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
            "> **Points:** 2\n\n## Summary\n\ns\n\n\n## Acceptance Criteria\n\n- [x] the defect no longer reproduces\n", encoding="utf-8")
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
                     "sprint_covers_independently", "is_independent"):
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
        # A REALISTIC row: `evidence_for` returns one dict of `_EVIDENCE_COLS`, never a list
        # of placeholders. The old `[{"x": 1}]` was truthy, which was all any test asked of it -
        # so a reader that actually inspected the row could not be tested through this fixture.
        critic_mod.evidence_for = lambda r, u: (
            {"unit": u, "reviewer": "reviewer-a", "author": "author-b",
             "date": "2026-07-29", "findings": "probed the guard paths"}
            if u in evidence else None)
        critic_mod.signoff_for = lambda r, u: {"principal": "p"} if u in signoffs else None
        critic_mod.is_independent_signoff = lambda r, u, s: u in signoffs
        critic_mod.sprint_review_for = lambda r, u: None
        critic_mod.sprint_covers_independently = lambda r, u, rev: u in covered
        # The coverage step consults BOTH predicates: `sprint_covers_independently` for the
        # verdict-and-distinct half and `is_independent` for the PRE_GATE grandfather half.
        # These fixtures assert the pre-flight's COMPOSITION, so independence semantics are
        # stubbed true here and tested directly in BatchBoundaryReviewTests.
        critic_mod.is_independent = lambda rec: True
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
                            evidence=("US0101",), signoffs=("US0101",), covered=("US0101",))
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
                            evidence=("US0101",), signoffs=("US0101",), covered=("US0101",))
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
                            evidence=("US0101",), signoffs=("US0101",), covered=("US0101",))
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
            # Covered but with no verdict: the pre-flight is NOT ready (the sign-off half is
            # unmet), while the chain's own coverage step passes - so what this test measures
            # is the pre-flight's non-blocking property and not a different step's refusal.
            mod = self._mod(root, units=["US0101"], evidence=("US0101",), covered=("US0101",))
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
                            evidence=("US0101",), signoffs=("US0101",), covered=("US0101",))
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
              hook: str | None = _HOOK_SELECTS, measured: list | None = None,
              selected: list | None = None) -> Path:
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
        if measured is not None:
            local = root / "sdlc-studio" / ".local"
            local.mkdir(parents=True, exist_ok=True)
            doc = {"total": measured}
            if selected is not None:
                doc["total.selected"] = selected
                doc["total.last_series"] = "selected"
            (local / "gate-timings.json").write_text(json.dumps(doc), encoding="utf-8")
        return root


class ExecutionCostSourceTests(_ExecutionPolicyFixture):
    """BG0415: the budget lane and the planner disagreed by 44% about the same gate.

    `budget` read the measured series and said 457s of a 380s ceiling; `sprint plan`, pricing
    the same gate for the same sprint, read `gate_budget.baseline_seconds` and quoted 317s. The
    error compounds with batch count, and planning is the only point at which gate cost can
    still be traded against scope, so under-pricing it removes the trade.
    """

    def test_the_plans_figure_tracks_the_MEASURED_series(self) -> None:
        """AC3, and the point of the unit: move the series, watch the number move. Asserting the
        current constant would pass just as well against the stale baseline read."""
        sprint = _load()
        seen = []
        for series in ([300.0, 310.0, 320.0], [540.0, 548.0, 554.0]):
            with tempfile.TemporaryDirectory() as d:
                root = self._repo(d, measured=series)
                seen.append(sprint.execution_cost(root)["seconds"])
        self.assertEqual(seen, [320.0, 554.0],
                         "the plan quotes a fixed baseline whatever the gate actually costs")

    def test_the_measured_read_wins_over_the_declared_baseline(self) -> None:
        """One number, one source. With both present the plan and the budget lane must not be
        able to report different costs for the same gate."""
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, baseline=317, measured=[554.0])
            cost = sprint.execution_cost(root)
        self.assertEqual(cost["seconds"], 554.0)
        self.assertIn("measured", cost["basis"])

    def test_the_declared_baseline_is_the_fallback_not_the_source(self) -> None:
        """A consuming project that records no timing series still gets a priced plan - the
        baseline remains a real measurement someone took, it is simply the weaker one."""
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, baseline=317, measured=None)
            cost = sprint.execution_cost(root)
        self.assertEqual(cost["seconds"], 317.0)
        self.assertIn("baseline_seconds", cost["basis"])

    def test_neither_source_is_still_UNKNOWN_and_never_zero(self) -> None:
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, baseline=None, measured=None)
            cost = sprint.execution_cost(root)
        self.assertIsNone(cost["seconds"])
        self.assertIn("UNKNOWN", cost["why"])

    def test_an_unreadable_series_falls_back_rather_than_reporting_a_number(self) -> None:
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, baseline=317)
            local = root / "sdlc-studio" / ".local"
            local.mkdir(parents=True, exist_ok=True)
            (local / "gate-timings.json").write_text("{not json", encoding="utf-8")
            cost = sprint.execution_cost(root)
        self.assertEqual(cost["seconds"], 317.0, "a corrupt series produced a fabricated cost")

    def test_a_plan_produced_while_the_gate_is_OVER_says_so_with_both_numbers(self) -> None:
        """AC2. The verdict belongs on the plan, because planning is the moment the cost can
        still be traded against scope - and an OVER that only a human ever reads is a bound in
        name only."""
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, baseline=317, measured=[554.0])
            text = "\n".join(sprint.render_execution_policy(sprint.execution_policy(root)))
        self.assertIn("OVER", text)
        self.assertIn("554", text)
        self.assertIn("380", text, "the ceiling is not stated, so the breach cannot be judged")

    def test_the_planner_reads_the_SERIES_the_budget_lane_reads(self) -> None:
        """The defect an independent review found in the first fix. `budget_report` reads
        `total.selected` when the marker says the last run was selected; this read `total`
        unconditionally, so on a repo whose commits run selected the budget lane said 100s and
        the plan said 554s about the same gate - the disagreement inverted rather than ended."""
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, baseline=317, measured=[554.0], selected=[100.0])
            cost = sprint.execution_cost(root)
        self.assertEqual(cost["seconds"], 100.0,
                         "the plan prices a full run this repo's commits do not pay")
        self.assertIn("SELECTED", cost["basis"], "the series is not named, so 100s reads as a "
                                                 "full-run figure comparable with the baseline")

    def test_a_full_run_repo_still_reads_the_full_series(self) -> None:
        """The control: without a selected marker, nothing changes."""
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, baseline=317, measured=[554.0])
            cost = sprint.execution_cost(root)
        self.assertEqual(cost["seconds"], 554.0)
        self.assertIn("full-run", cost["basis"])

    def test_the_OVER_verdict_agrees_with_the_budget_lane(self) -> None:
        """A plan announcing a breach the budget lane does not hold is the same two-readers
        defect, pointing the other way."""
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, baseline=317, measured=[554.0], selected=[100.0])
            text = "\n".join(sprint.render_execution_policy(sprint.execution_policy(root)))
        self.assertNotIn("OVER", text,
                         "the plan declares a breach on a 100s selected run against a 380s "
                         "ceiling, which the budget lane reports as under")

    def test_the_ceiling_boundary_is_bracketed(self) -> None:
        """`>` against `>=`: a run landing exactly on the ceiling is not over it."""
        sprint = _load()
        for secs, expect_over in ((380.0, False), (381.0, True)):
            with tempfile.TemporaryDirectory() as d:
                root = self._repo(d, baseline=317, measured=[secs])
                pol = sprint.execution_policy(root)
            self.assertEqual(bool(pol["over_budget"]), expect_over, f"at {secs}s")

    def test_a_gate_under_its_ceiling_states_no_breach(self) -> None:
        """The positive control: without it, a renderer that printed OVER unconditionally would
        pass the test above."""
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, baseline=317, measured=[300.0])
            text = "\n".join(sprint.render_execution_policy(sprint.execution_policy(root)))
        self.assertNotIn("OVER", text)


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


class CloseRecordsNoSuiteVerdictTests(unittest.TestCase):
    """US0553 is REVERTED, and this is the guard that it stays reverted.

    It recorded `status=green, mode=full` into the record `gate.suite_decision` reads, on the
    premise that the close had just run the full suites. `gate.main` runs seventeen lanes and
    not one of them runs a test suite - the suites are run by `.githooks/commit-msg`. The close
    therefore stamped a full-suite green over whatever sat in the working tree, and the next
    commit read it and ran no tests: a false green written by the mechanism built to refuse
    false greens.

    Asserted as the PROPERTY - the close writes no suite verdict - rather than as the absence
    of a call, so a differently-spelled reintroduction is caught too."""

    def _repo(self) -> Path:
        d = Path(tempfile.mkdtemp(prefix="no_suite_verdict_"))
        (d / "sdlc-studio" / ".local").mkdir(parents=True)
        (d / "sdlc-studio" / "reviews").mkdir(parents=True)
        (d / "sdlc-studio" / "reviews" / "LATEST.md").write_text("# anchor\n", encoding="utf-8")
        (d / "sdlc-studio" / ".local" / "run-state.json").write_text(json.dumps({
            "run_id": "RUN-NOVERDICT", "batch": ["US0001"], "outcome": "running",
            "started_at": "2026-07-29T09:00:00Z",
            "close_output": ["sdlc-studio/reviews/LATEST.md"]}), encoding="utf-8")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        return d

    def test_a_passing_close_writes_no_suite_verdict(self) -> None:
        sprint = _load()
        root, gate = self._repo(), _stub_gate([])
        with unittest.mock.patch.dict(sys.modules, {"gate": gate}), \
                contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            ok, _detail, _ = sprint._close_gate(root, "RETRO0001", json.loads(
                (root / "sdlc-studio" / ".local" / "run-state.json").read_text(encoding="utf-8")))
        self.assertTrue(ok)
        self.assertEqual([], gate.recorded_verdicts,
                         "the close recorded a SUITE verdict it did not earn - `gate.main` runs "
                         "no test suite, so any green it writes there is fabricated")

    def test_the_close_leaves_no_suite_verdict_on_disk_however_it_is_written(self) -> None:
        """The PROPERTY, which the companion above does not check.

        That test asserts `recorded_verdicts == []` on a stub, so it catches ONE spelling: a
        reintroduction as a direct `write_text` to the file `gate.suite_decision` actually reads
        survived the whole suite, while this class's docstring claimed a differently-spelled
        reintroduction would be caught. The record is on the filesystem, so that is where the
        absence has to be asserted."""
        import gate as real_gate
        sprint = _load()
        root, gate = self._repo(), _stub_gate([])
        verdict_file = root / real_gate.SUITE_VERDICT_REL
        self.assertFalse(verdict_file.exists(), "the fixture starts with a verdict already on disk")
        with unittest.mock.patch.dict(sys.modules, {"gate": gate}), \
                contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            sprint._close_gate(root, "RETRO0001", json.loads(
                (root / "sdlc-studio" / ".local" / "run-state.json").read_text(encoding="utf-8")))
        self.assertFalse(
            verdict_file.exists(),
            f"the close wrote {real_gate.SUITE_VERDICT_REL} - the record the commit hook reads "
            f"to decide whether to run the suites at all. The close runs no suite, so whatever "
            f"green it writes there is over the working tree, not over a measurement")

    def test_the_close_gate_runs_no_suite_lane(self) -> None:
        """The premise itself, checked rather than assumed - which is what was missing the
        first time. If a suite lane is ever added to `run_gate`, this test says so and the
        revert can be revisited on evidence."""
        import gate as real_gate
        lanes = set(real_gate.DEFAULT_CHECKS)
        self.assertFalse(
            {n for n in lanes if "suite" in n or "unittest" in n or "pytest" in n},
            f"a gate lane now looks like a test-suite runner: {sorted(lanes)} - if the gate "
            f"genuinely runs the suites, the close may record a verdict again")

    def test_the_close_scoped_verdict_reuse_is_untouched(self) -> None:
        """The close's OWN gate verdict reuse (US0501) is correct and close-scoped; only the
        SUITE verdict was fabricated. Reverting one must not take the other."""
        sprint = _load()
        root, gate = self._repo(), _stub_gate([])
        with unittest.mock.patch.dict(sys.modules, {"gate": gate}), \
                contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            state = json.loads((root / "sdlc-studio" / ".local" / "run-state.json")
                               .read_text(encoding="utf-8"))
            sprint._close_gate(root, "RETRO0001", state)
            ok, detail, _ = sprint._close_gate(root, "RETRO0001", state)
        self.assertTrue(ok)
        self.assertIn("REUSED", detail)


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
        # An AUTHOR is recorded: since BG0402 the panel REFUSES rather than producing a verdict
        # it cannot prove excluded the author, so a fixture without one exercises the refusal
        # instead of the panel.
        (d / "sdlc-studio" / ".local" / "run-state.json").write_text(json.dumps({
            "run_id": "RUN-INERT", "batch": ["US0001"], "outcome": "running",
            "author": "builder", "sprint_goal": goal,
            "started_at": "2026-07-29T09:00:00Z"}), encoding="utf-8")
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

    def test_a_panel_that_cannot_prove_the_exclusion_refuses(self) -> None:
        """BG0402. `_recorded_goal_seats` returns seat NAMES and `_signoff_author` an author id,
        so the exclusion compared two namespaces and excluded nobody - while the report said
        `author excluded`. An unprovable exclusion is now a refusal, not a claim."""
        sprint = _load()
        root = self._repo()
        state = json.loads((root / "sdlc-studio" / ".local" / "run-state.json")
                           .read_text(encoding="utf-8"))
        state.pop("author")
        (root / "sdlc-studio" / ".local" / "run-state.json").write_text(json.dumps(state),
                                                                       encoding="utf-8")
        joined = "\n".join(sprint.close_goal_judgement(root, state))
        self.assertIn("NOT RUN", joined)
        self.assertNotIn("author excluded", joined,
                         "the report claimed an exclusion it could not perform")

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


class UlidUnitsAreNotFailedOpenTests(unittest.TestCase):
    """BG0354. BG0318 closed the v2-only id grammar in `conformance.py`; the same hole survived
    in `reachable_end_state`, where a unit whose id carries no comparable number was SKIPPED -
    reported as reaching Done when the sign-off gate may well cap it. A fail-open in the one
    report that tells an operator how far a batch can get."""

    def _root(self) -> Path:
        d = Path(tempfile.mkdtemp(prefix="ulid_"))
        (d / "sdlc-studio").mkdir(parents=True)
        (d / "sdlc-studio" / ".config.yaml").write_text(
            "review:\n  two_role_after: 192\n", encoding="utf-8")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        return d

    def test_a_ulid_unit_is_reported_as_capped_not_skipped(self) -> None:
        sprint = _load()
        res = sprint.reachable_end_state(self._root(), [{"id": "US-01JQK3F8"}])
        self.assertEqual(sprint.END_STATE_REVIEW, res["state"],
                         "a unit the cutoff cannot be compared against was reported as "
                         "reaching Done - the fail-open direction")
        # `norm_id` strips the dash, so the reported id is the normalised form.
        self.assertEqual(["US01JQK3F8"], res["units"])

    def test_a_numbered_unit_below_the_cutoff_still_reaches_done(self) -> None:
        """The discriminating half - a report that always caps is not a report."""
        sprint = _load()
        res = sprint.reachable_end_state(self._root(), [{"id": "US0001"}])
        self.assertEqual(sprint.END_STATE_DONE, res["state"])

    def test_a_numbered_unit_past_the_cutoff_is_capped(self) -> None:
        sprint = _load()
        res = sprint.reachable_end_state(self._root(), [{"id": "US0500"}])
        self.assertEqual(sprint.END_STATE_REVIEW, res["state"])


class BlockerGroupingTests(unittest.TestCase):
    """BG0394. The group key was (stage, id-stripped remedy) while the cause and the filed
    artefact's summary came from `blockers[0]`. Two blockers with different details and the
    same remedy merged, the second detail never reached the artefact - and the close printed
    that they were "listed inside the artefact that covers them" while one of them was not."""

    def test_two_blockers_with_different_details_are_not_merged(self) -> None:
        sprint = _load()
        groups = sprint.group_blockers([
            {"stage": "gate", "detail": "markdown lane red", "remedy": "run the gate"},
            {"stage": "gate", "detail": "neutrality guard red", "remedy": "run the gate"}])
        self.assertEqual(2, len(groups), "two different things to fix became one artefact")
        self.assertEqual({"markdown lane red", "neutrality guard red"},
                         {g["cause"] for g in groups})

    def test_blockers_differing_only_in_the_unit_still_group(self) -> None:
        """The property the grouping exists for, and the one the fix must not cost: one owed
        sign-off across twenty-three units is ONE thing to fix, not twenty-three artefacts."""
        sprint = _load()
        groups = sprint.group_blockers([
            {"stage": "sign-off", "detail": "US0001: no critic verdict",
             "remedy": "record a verdict for US0001"},
            {"stage": "sign-off", "detail": "US0002: no critic verdict",
             "remedy": "record a verdict for US0002"}])
        self.assertEqual(1, len(groups))
        self.assertEqual(["US0001", "US0002"], groups[0]["units"])

    def test_every_member_is_kept_on_its_group(self) -> None:
        """The artefact renders from `group['blockers']`, so every merged detail has to be
        there to be listed - the claim the close prints depends on it."""
        sprint = _load()
        groups = sprint.group_blockers([
            {"stage": "sign-off", "detail": "US0001: no critic verdict",
             "remedy": "record a verdict for US0001"},
            {"stage": "sign-off", "detail": "US0002: no critic verdict",
             "remedy": "record a verdict for US0002"}])
        self.assertEqual(2, len(groups[0]["blockers"]))
        self.assertEqual({"US0001: no critic verdict", "US0002: no critic verdict"},
                         {b["detail"] for b in groups[0]["blockers"]})


class ContentReviewSurvivesThePlanTests(unittest.TestCase):
    """BG0392. `record_content_review` needed no open run and wrote onto the blank state;
    `open_run` treats a state with no `run_id` as spent and replaces it. The natural order -
    review the plan, then write it - wiped the prediction without a word, and `prediction_miss`
    was permanently None: a bookend with one end, which is a question nobody ever checks."""

    def _root(self) -> Path:
        d = Path(tempfile.mkdtemp(prefix="content_review_"))
        (d / "sdlc-studio" / ".local").mkdir(parents=True)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        return d

    def test_recording_with_no_run_open_is_refused(self) -> None:
        sprint = _load()
        with self.assertRaises(ValueError) as caught:
            sprint.record_content_review(self._root(), "plan", "a goal", "yes")
        self.assertIn("no run is open", str(caught.exception))

    def test_a_plan_review_survives_a_re_plan_of_the_open_run(self) -> None:
        """The property the refusal buys: recorded against an OPEN run, a re-plan accumulates
        rather than blanking, so the prediction is still there at the close."""
        sprint = _load()
        root = self._root()
        _load().run_state.open_run(root, batch=["US0001"])
        sprint.record_content_review(root, "plan", "a goal", "yes")
        _load().run_state.open_run(root, batch=["US0001", "US0002"])
        self.assertIsNotNone(sprint.content_reviews(root)["plan"],
                             "the re-plan destroyed the plan-side review")

    def test_the_miss_is_reportable_once_both_ends_exist(self) -> None:
        sprint = _load()
        root = self._root()
        _load().run_state.open_run(root, batch=["US0001"])
        sprint.record_content_review(root, "plan", "a goal", "yes")
        sprint.record_content_review(root, "close", "a goal", "partial", missing="clause 2")
        self.assertIn("PREDICTION MISS", sprint.prediction_miss(root) or "")


class StaleLaneMarkersAreReportedTests(unittest.TestCase):
    """BG0395. The stale-marker warning was filtered to the units in the CURRENT dispatch, so a
    lane that died on US0001 was never mentioned when the operator briefed US0002 - which is
    the restart case the marker exists for. Nothing else read the markers, and `close_run` left
    them set, so a run could be signed off with one standing."""

    def _root(self) -> Path:
        d = Path(tempfile.mkdtemp(prefix="in_flight_"))
        (d / "sdlc-studio" / ".local").mkdir(parents=True)
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        _load().run_state.open_run(d, batch=["US0001", "US0002"])
        _load().run_state.update(d, sprint_goal="a goal")
        return d

    def test_a_stale_marker_naming_another_unit_is_still_reported(self) -> None:
        sprint = _load()
        root = self._root()
        _load().run_state.record_lane_start(root, "US0001")
        rows = _load().run_state.lanes_in_flight(root)
        self.assertEqual(["US0001"], [r["unit"] for r in rows])
        # The brief path warns on EVERY row it is handed, rather than intersecting with the
        # dispatch - asserted on the set the warning iterates, which is where the filter was.
        self.assertNotIn("US0002", [r["unit"] for r in rows])
        self.assertTrue(rows, "a marker for a unit outside this dispatch must still be seen")

    def test_the_close_reports_a_unit_still_marked_in_flight(self) -> None:
        sprint = _load()
        root = self._root()
        _load().run_state.record_lane_start(root, "US0001")
        joined = "\n".join(sprint.close_goal_judgement(root, sprint.run_state.read(root)))
        self.assertIn("IN FLIGHT at close: US0001", joined)

    def test_a_run_with_no_stale_marker_says_nothing(self) -> None:
        """A warning on every close is a warning nobody reads."""
        sprint = _load()
        root = self._root()
        joined = "\n".join(sprint.close_goal_judgement(root, sprint.run_state.read(root)))
        self.assertNotIn("IN FLIGHT", joined)


class LaneSeamScopeTests(unittest.TestCase):
    """BG0391. `lane_dispatch` computed seams over the ids passed to THAT call, and the shipped
    docs dispatch one unit at a time (`lane brief --units <id>`). So the seam map worked only
    when the whole batch was briefed in one command - which is the case where a lane is not the
    one-unit reader the whole design is premised on."""

    def _repo(self) -> Path:
        d = Path(tempfile.mkdtemp(prefix="lane_seam_"))
        (d / "sdlc-studio" / ".local").mkdir(parents=True)
        stories = d / "sdlc-studio" / "stories"
        stories.mkdir(parents=True)
        for uid in ("US0001", "US0002"):
            (stories / f"{uid}-x.md").write_text(
                f"# {uid}: x\n\n> **Status:** Ready\n> **Affects:** src/shared.py\n\n"
                f"## Acceptance Criteria\n\n### AC1: it works\n\n"
                f"- **Then** something observable happens\n- **Verify:** shell true\n",
                encoding="utf-8")
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        return d

    def test_a_single_unit_brief_names_its_seams_with_the_open_batch(self) -> None:
        sprint = _load()
        root = self._repo()
        sprint.run_state.open_run(root, batch=["US0001", "US0002"])
        dispatch = sprint.lane_dispatch(root, ["US0002"])
        seams = dispatch["briefs"][0]["seams"]
        self.assertTrue(seams, "a one-unit brief saw no seam with the rest of the batch")
        self.assertEqual([["US0001", "US0002"]], [s["units"] for s in seams])

    def test_the_brief_still_carries_only_its_own_seams(self) -> None:
        """Widening the SCOPE must not widen the brief: a lane reads one unit, and handing it
        a pair it is not in is noise that gets skipped."""
        sprint = _load()
        root = self._repo()
        stories = root / "sdlc-studio" / "stories"
        (stories / "US0003-y.md").write_text(
            "# US0003: y\n\n> **Status:** Ready\n> **Affects:** src/other.py\n\n"
            "## Acceptance Criteria\n\n### AC1: it works\n\n"
            "- **Then** something observable happens\n- **Verify:** shell true\n",
            encoding="utf-8")
        sprint.run_state.open_run(root, batch=["US0001", "US0002", "US0003"])
        dispatch = sprint.lane_dispatch(root, ["US0003"])
        self.assertEqual([], dispatch["briefs"][0]["seams"],
                         "US0003 shares no file, so it must be handed no pair")


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
        """The PREDICTION, driven through `close_dry_run` and then through the real chain.

        This asserted `_dry_run_result` over a hand-built list, so it never called
        `close_dry_run` at all: an independent seat gutted that function to return a fixed
        clean result and this test still passed. It also fed `[{"step": "gate", "status":
        "ok"}]`, a shape production stopped producing. The claim is that a clean preview
        predicts a close that does not refuse, so both halves have to run.
        """
        sprint = _load()
        root = self._repo()
        ok = lambda *_a, **_k: (True, "ok", "")  # noqa: E731
        steps = {f"_close_{s.replace('-', '_')}": ok for s in sprint._CLOSE_CHAIN}
        with unittest.mock.patch.object(
                sprint, "close_preflight",
                lambda *_a, **_k: {"ready": True, "blockers": [], "gate_ran": True}), \
                unittest.mock.patch.multiple(sprint, **steps):
            preview = sprint.close_dry_run(root, "RETRO9990")
            self.assertTrue(preview["clean"], "the preview is not clean, so it predicts nothing")
            # The preview must have ACTUALLY previewed. Asserting only `clean` let a
            # `close_dry_run` gutted to `return {"clean": True, "steps": []}` satisfy this -
            # the seat's mutant, which survived the first repair of this very test.
            reported = {s["step"] for s in preview["steps"]}
            self.assertEqual(set(sprint._CLOSE_CHAIN) - reported, set(),
                             "the preview reports no step, so `clean` is a claim about nothing")
            # ...and the real chain, over the same steps, refuses nothing.
            refused = [name for name in sprint._CLOSE_CHAIN
                       if not getattr(sprint, "_close_" + name.replace("-", "_"))(
                           root, "RETRO9990", {})[0]]
        self.assertEqual([], refused,
                         "the dry run reported clean and the real close refuses - the preview "
                         "does not predict the close")

    def test_a_dry_run_that_REFUSES_predicts_a_close_that_refuses(self) -> None:
        """The control. Without it, a preview hardcoded to `clean` would satisfy the test
        above while predicting nothing at all."""
        sprint = _load()
        root = self._repo()
        blocker = {"stage": "gate", "detail": "tests: 3 failing", "remedy": "fix them"}
        with unittest.mock.patch.object(
                sprint, "close_preflight",
                lambda *_a, **_k: {"ready": False, "blockers": [blocker], "gate_ran": True}):
            preview = sprint.close_dry_run(root)
        self.assertFalse(preview["clean"])
        self.assertTrue(preview["blockers"])

    def test_an_unevaluated_step_is_never_reported_as_passing(self) -> None:
        """The direction this must fail in. A step whose probe blew up in the scratch copy has
        said nothing about the real close; calling that a pass is the one way a preview could
        actively mislead."""
        sprint = _load()
        root = self._repo()

        def explode(*_a, **_kw):
            raise RuntimeError("the probe blew up in the copy")

        # Driven through close_dry_run with a REAL step raising, not a hand-built list. The
        # fabricated-list form asserted `_dry_run_result` alone, so a `close_dry_run` gutted to
        # return a fixed clean result satisfied it - the seat's mutant, twice over.
        with unittest.mock.patch.object(
                sprint, "close_preflight",
                lambda *_a, **_k: {"ready": True, "blockers": [], "gate_ran": True}), \
                unittest.mock.patch.object(sprint, "_close_handoff", explode):
            result = sprint.close_dry_run(root, "RETRO9991")
        steps = {s["step"]: s for s in result["steps"]}
        self.assertEqual("unevaluated", steps["handoff"]["status"],
                         "a step whose probe raised is reported as something other than "
                         "unevaluated")
        self.assertIn("blew up", steps["handoff"]["detail"])
        self.assertFalse(result["clean"], "an unanswered step is not a passing one")
        self.assertIn("handoff", [s["step"] for s in result["unevaluated"]])
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


class CloseChainCoverageTests(CloseDryRunTests):
    """BG0460: the dry run reported a chain step as neither refusing nor unevaluated.

    `DRY_RUN_ACTION_STEPS` was a hand-maintained restatement of `_CLOSE_CHAIN` that had lost
    `gate`, so the step simply never appeared - not `ok`, not `refuse`, not counted among the
    unevaluated. A preview whose silence about a step is indistinguishable from a pass is the
    one thing it must never be, and the docstring's "all seven steps" claim stood against a
    ten-step chain.
    """

    def test_every_chain_step_is_accounted_for_in_the_dry_run(self) -> None:
        """The property: each chain step reaches the report with SOME status. A step that is
        deliberately not executed in a preview is `unevaluated` with a reason, never absent."""
        sprint = _load()
        steps = self._steps(sprint.close_dry_run(self._repo()))
        missing = [s for s in sprint._CLOSE_CHAIN if s not in steps]
        self.assertEqual([], missing,
                         "a chain step is neither reported nor counted, so its silence reads "
                         "the same as a pass")

    def test_the_gate_step_carries_the_PREFLIGHTS_verdict(self) -> None:
        """This test used to assert `status in {"ok", "refuse", "unevaluated"}` - the set of
        every possible status, so it held nothing. An independent review mutated the skipped
        step to report `"ok"` and it SURVIVED the whole 5,658-test suite, which is precisely
        what this unit exists to forbid. It now asserts the verdict itself.

        A clean preflight means the gate RAN, against the real tree, and passed."""
        sprint = _load()
        root = self._repo()
        with unittest.mock.patch.object(
                sprint, "close_preflight",
                lambda *_a, **_k: {"ready": True, "blockers": [], "gate_ran": True}):
            steps = self._steps(sprint.close_dry_run(root))
        self.assertEqual("ok", steps.get("gate", {}).get("status"),
                         "a passing gate is not reported, so `clean` is unreachable")
        self.assertIn("preflight", steps["gate"]["detail"])

    def test_a_gate_refusal_is_reported_once_not_twice(self) -> None:
        """The other direction: the preflight already files a gate failure as a blocker, so
        noting it again would double-count the same refusal in the same report."""
        sprint = _load()
        root = self._repo()
        blocker = {"stage": "gate", "detail": "tests: 3 failing", "remedy": "fix them"}
        with unittest.mock.patch.object(
                sprint, "close_preflight",
                lambda *_a, **_k: {"ready": False, "blockers": [blocker], "gate_ran": True}):
            result = sprint.close_dry_run(root)
        gates = [s for s in result["steps"] if s["step"] == "gate"]
        self.assertEqual(1, len(gates), "the gate refusal is reported twice")
        self.assertEqual("refuse", gates[0]["status"])

    def test_a_clean_preview_can_actually_report_CLEAN(self) -> None:
        """The regression the first fix introduced. `gate` was noted `unevaluated`
        unconditionally, `clean = not blockers and not unevaluated`, and `cmd_close` returns 1
        unless clean - so every dry run in every repo exited 1 and `dry run CLEAN` became dead
        code. US0555 AC4 (a clean dry run predicts a close that does not refuse) was
        unsatisfiable in production."""
        sprint = _load()
        root = self._repo()
        ok = lambda *_a, **_k: (True, "ok", "")  # noqa: E731
        patches = {f"_close_{s.replace('-', '_')}": ok for s in sprint._CLOSE_CHAIN}
        with unittest.mock.patch.object(
                sprint, "close_preflight",
                lambda *_a, **_k: {"ready": True, "blockers": [], "gate_ran": True}), \
                unittest.mock.patch.multiple(sprint, **patches):
            result = sprint.close_dry_run(root, "RETRO9999")
        self.assertEqual([], result["unevaluated"], "a step is permanently unanswered")
        self.assertTrue(result["clean"], "no dry run can ever report clean")

    def test_a_gate_that_never_RAN_is_not_reported_as_passing(self) -> None:
        """Round-3 finding. `close_preflight` has early returns that come back on a run-state
        fault without ever calling `run_gate`, and "no gate blocker" cannot tell that from a
        clean pass - so the preview printed `ok gate: run by the preflight against the real
        tree`, a false statement about the most expensive step in the chain. The previous
        attempt at this reported `unevaluated` unconditionally, which was over-conservative but
        honest; this trades neither."""
        sprint = _load()
        root = self._repo()
        early = {"ready": False, "gate_ran": False,
                 "blockers": [{"stage": "run-state", "detail": "no run state", "remedy": "x"}]}
        with unittest.mock.patch.object(sprint, "close_preflight", lambda *_a, **_k: early):
            steps = self._steps(sprint.close_dry_run(root))
        self.assertEqual("unevaluated", steps.get("gate", {}).get("status"),
                         "a gate that was never reached is reported as having passed")
        self.assertIn("before reaching the gate", steps["gate"]["detail"])

    def test_a_preflight_with_no_gate_ran_key_is_read_as_did_not_run(self) -> None:
        """An absent key is the unanswerable case, and it resolves toward `unevaluated` - the
        direction that cannot state a falsehood about a step nobody ran."""
        sprint = _load()
        root = self._repo()
        with unittest.mock.patch.object(sprint, "close_preflight",
                                        lambda *_a, **_k: {"ready": True, "blockers": []}):
            steps = self._steps(sprint.close_dry_run(root))
        self.assertEqual("unevaluated", steps.get("gate", {}).get("status"))

    def test_the_real_preflight_reports_whether_the_gate_ran(self) -> None:
        """The mocks above are only honest if the real function supplies the key AND the key
        discriminates. Asserting only that it exists and is a bool let a mutant hardcoding it
        to True survive - the flag would then always claim the gate ran, which is the fail-open
        this whole repair closes."""
        sprint = _load()
        # An early return: no run state at all, so `run_gate` is never reached.
        with tempfile.TemporaryDirectory() as d:
            bare = Path(d)
            (bare / "sdlc-studio" / ".local").mkdir(parents=True)
            early = sprint.close_preflight(bare, None)
        self.assertIn("gate_ran", early, "the preflight contract does not carry gate_ran")
        self.assertFalse(early["gate_ran"],
                         "the preflight claims the gate ran on a path that returns before it")
        # And the ordinary path, which does reach it.
        full = sprint.close_preflight(self._repo(), None)
        self.assertIn("gate_ran", full)
        self.assertTrue(full["gate_ran"],
                        "a preflight that ran the gate reports that it did not")

    def test_a_gate_that_RAISES_is_not_recorded_as_having_run(self) -> None:
        """The third path, and the one two mutants slipped through. The early return and the
        happy path both report `gate_ran` correctly; the interesting case is `run_gate` raising,
        which reaches the SAME final return as a successful run. Without this, hardcoding
        `gate_ran = True` - at the initialiser or at the return - survives, and a gate that blew
        up is reported to the operator as one that passed."""
        sprint = _load()
        import gate as gate_mod

        def boom(*_a, **_k):
            raise RuntimeError("a lane exploded")

        with unittest.mock.patch.object(gate_mod, "run_gate", boom):
            pre = sprint.close_preflight(self._repo(), None)
        self.assertFalse(pre["gate_ran"],
                         "a gate that raised is recorded as having run")
        self.assertTrue(any(b["stage"] == "gate" for b in pre["blockers"]),
                        "the raised gate produced no blocker either")

    def test_a_raised_gate_is_not_previewed_as_ok(self) -> None:
        """The consequence, end to end through the dry run."""
        sprint = _load()
        import gate as gate_mod

        def boom(*_a, **_k):
            raise RuntimeError("a lane exploded")

        with unittest.mock.patch.object(gate_mod, "run_gate", boom):
            steps = self._steps(sprint.close_dry_run(self._repo()))
        self.assertNotEqual("ok", steps.get("gate", {}).get("status"),
                            "a gate that blew up is previewed as passing")

    def test_the_dry_run_step_set_is_DERIVED_from_the_chain(self) -> None:
        """AC2. A restated list is what lost `gate` in the first place, so adding a step to the
        chain must not be able to leave a hole here. Asserting the derivation, not the current
        membership, is what makes that true of a step nobody has written yet."""
        sprint = _load()
        self.assertEqual(set(sprint._CLOSE_CHAIN), set(sprint.DRY_RUN_ACTION_STEPS),
                         "DRY_RUN_ACTION_STEPS has drifted from the chain it previews")

    def test_the_reported_step_count_tracks_the_chain_rather_than_a_literal(self) -> None:
        """The "all seven steps" claim outlived the seven-step chain. The count must move when
        the chain does, so a reader is never told a number the code has left behind.

        Asserting `str(len(_CLOSE_CHAIN))` anywhere in the report was NOT enough: an independent
        review mutated the count to a literal 7 and the test still passed, because the digits
        "10" appeared elsewhere - in a retro message from a sibling unit in the same commit. The
        assertion is now pinned to the sentence that makes the claim."""
        sprint = _load()
        report = sprint.dry_run_report(sprint.close_dry_run(self._repo()))
        self.assertIn(f"{len(sprint._CLOSE_CHAIN)} chain step(s) previewed", report,
                      "the previewed-step count is a literal, so it can outlive the chain")
        self.assertNotIn("all seven", report.lower())


class CloseRetroDemonstrationTests(CloseDryRunTests):
    """BG0418 and BG0459: the close discarded the retro validator's own warning.

    `retro validate` prints an EXAMPLES report for a retro still carrying the template's worked
    demonstrations, and exits 0 because a scaffold-shaped retro is structurally valid. The close
    kept only its exit code, so it printed `retro-validate: RETRO0086 valid` over a document in
    which nothing had been replaced - the operator was told the opposite of the truth by a check
    that had correctly noticed it.
    """

    def _scaffold_retro(self, root: Path, rid: str = "RETRO9002", *, replaced: bool = False) -> str:
        """A retro carrying the shipped template's demonstration lines, marked as the template
        marks them. `replaced=True` strips them, which is what a filled-in retro looks like."""
        import shutil as _sh
        (root / "sdlc-studio" / "retros").mkdir(parents=True, exist_ok=True)
        tpl = (Path(__file__).resolve().parents[2] / "templates" / "reviews" / "retro.md")
        text = tpl.read_text(encoding="utf-8")
        if replaced:
            text = "\n".join(l for l in text.splitlines() if "<!-- example -->" not in l)
            text += ("\n## Lessons\n\n- a real lesson with the evidence that produced it\n"
                     "\n## Actions raised\n\n| Finding | Disposition |\n| --- | --- |\n"
                     "| a real finding | declined: it lands on a path this project does not use |\n")
        (root / "sdlc-studio" / "retros" / f"{rid}-scaffold.md").write_text(text, encoding="utf-8")
        del _sh
        return rid

    def test_the_close_step_REPORTS_the_unreplaced_demonstrations(self) -> None:
        """BG0418 AC1/AC3, verified THROUGH the close step rather than the retro CLI: the CLI
        always printed this. The defect was entirely in what the close did with it."""
        sprint = _load()
        root = self._repo()
        rid = self._scaffold_retro(root)
        _ok, detail, _remedy = sprint._close_retro_validate(root, rid, {})
        self.assertIn("EXAMPLE", detail.upper(),
                      "the close reports `valid` over a retro nobody filled in")

    def test_a_filled_in_retro_produces_no_demonstration_noise(self) -> None:
        """BG0418 AC5 and the positive control: without it, a step that always warned would
        pass the test above while making the warning worthless."""
        sprint = _load()
        root = self._repo()
        rid = self._scaffold_retro(root, "RETRO9003", replaced=True)
        _ok, detail, _remedy = sprint._close_retro_validate(root, rid, {})
        self.assertNotIn("EXAMPLE", detail.upper())

    def test_a_wholly_unreplaced_scaffold_BLOCKS_rather_than_only_warning(self) -> None:
        """BG0418 AC2 wants the blocking rule stated rather than inferred. The rule: warn on any
        leftover, REFUSE when nothing has been replaced at all. That is not a judgement about
        how much content is enough - it is the difference between a document someone wrote and
        one nobody opened."""
        sprint = _load()
        root = self._repo()
        rid = self._scaffold_retro(root)
        ok, _detail, remedy = sprint._close_retro_validate(root, rid, {})
        self.assertFalse(ok, "an untouched scaffold reached a signed-off close")
        self.assertTrue(remedy.strip(), "a refusal with no remedy is a dead end")

    def test_the_dry_run_surfaces_the_same_warning(self) -> None:
        """BG0418 AC4: the dry run routes through the same probe, so it must say the same thing
        - otherwise the preview clears a close that then refuses."""
        sprint = _load()
        root = self._repo()
        rid = self._scaffold_retro(root)
        steps = self._steps(sprint.close_dry_run(root, rid))
        self.assertIn("retro-validate", steps)
        self.assertIn("EXAMPLE", steps["retro-validate"]["detail"].upper())

    def test_every_demonstration_line_in_the_shipped_template_is_MARKED(self) -> None:
        """BG0459 AC1, as an exact set rather than a floor. A `>= 6` threshold tolerated a
        marker going missing, which is the failure it was written to catch: the three
        Actions-raised rows carried no marker and the scaffold validated clean."""
        import retro as retro_mod  # noqa: PLC0415
        tpl = (Path(__file__).resolve().parents[2] / "templates" / "reviews" / "retro.md")
        text = tpl.read_text(encoding="utf-8")
        demo = [l for l in text.splitlines() if "EXAMPLE" in l and l.strip().startswith(("-", "|"))]
        marked = [l for l in demo if retro_mod.DEMO_MARKER in l]
        self.assertEqual(demo, marked,
                         "a demonstration line ships without the marker, so it survives the "
                         "leftovers check and an unfilled retro validates clean")

    def test_an_untouched_actions_table_alone_is_still_reported(self) -> None:
        """BG0459 AC2: the specific escape. Every bullet replaced, the table left as shipped."""
        sprint = _load()
        import retro as retro_mod  # noqa: PLC0415
        root = self._repo()
        tpl = (Path(__file__).resolve().parents[2] / "templates" / "reviews" / "retro.md")
        lines = tpl.read_text(encoding="utf-8").splitlines()
        kept = [l for l in lines
                if not (retro_mod.DEMO_MARKER in l and l.strip().startswith("-"))]
        kept += ["", "- a real lesson, with the evidence that produced it", ""]
        (root / "sdlc-studio" / "retros").mkdir(parents=True, exist_ok=True)
        (root / "sdlc-studio" / "retros" / "RETRO9004-partial.md").write_text(
            "\n".join(kept), encoding="utf-8")
        _ok, detail, _r = sprint._close_retro_validate(root, "RETRO9004", {})
        self.assertIn("EXAMPLE", detail.upper(),
                      "the untouched Actions-raised rows passed unreported")


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
        # CORRECTED (BG0404). This asserted "unscoped, every recorded close counts" - which is
        # the defect, not the contract. `cmd_close` proceeds on any truthy state, and a state
        # carrying no run_id then reported the whole ledger as this close's own cost: 6x on
        # seconds and 143x on elapsed, in the one report whose purpose is measurement honesty.
        # A run with no id has no cost of its own, and saying so is the only honest answer.
        unscoped = sprint.close_cost(root)
        self.assertIsNone(unscoped["gate_seconds"],
                          "a run with no id reported every close on the ledger as its own")
        self.assertTrue(any("not attributable" in u.lower() for u in unscoped["unmeasured"]),
                        "the absence was not stated")

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


class BatchBoundaryReviewTests(unittest.TestCase):
    """US0560/US0561 (CR0500). The review belongs at the DELIVERY batch boundary, not the close.
    RUN-01KYNKDP delivered in 5h and closed in 6h35m, and about 82% of that close was repair
    generated by a close-time review - every finding it made was close work by definition."""

    def _repo(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        (root / "sdlc-studio" / ".local").mkdir(parents=True)
        return root

    def _rs(self):
        from lib import run_state
        return run_state

    def test_a_batch_span_is_recorded_on_the_run_state(self) -> None:
        root, rs = self._repo(), self._rs()
        rs.open_run(root, goal="a goal", batch=["US0001"])  # a batch is scoped to a run
        rs.start_batch(root, ["US0001", "BG0002"])
        span = rs.open_batch(root)
        self.assertIsNotNone(span, "no batch span was opened")
        self.assertEqual(span["units"], ["US0001", "BG0002"])
        self.assertIsNone(span["reviewed_at"], "a fresh span is already marked reviewed")

    def test_coverage_reads_per_unit_and_batch_level_records(self) -> None:
        import critic
        root = self._repo()
        critic.record_sprint_review(root, ["US0001"], "reviewer-a", "author-b",
                                    "APPROVE", "probed the guard paths")
        cov = sprint.review_coverage(root, ["US0001", "US0002"])
        self.assertTrue(cov["US0001"]["covered"], "a recorded independent pass did not count")
        self.assertFalse(cov["US0002"]["covered"], "an unreviewed unit was counted as covered")

    def test_a_self_review_is_not_coverage(self) -> None:
        """The whole two-role rule in one assertion: the context that wrote the code cannot
        clear its own gate. `record_sprint_review` refuses to write one at all."""
        import critic
        root = self._repo()
        with self.assertRaises(ValueError):
            critic.record_sprint_review(root, ["US0001"], "same-agent", "same-agent",
                                        "APPROVE", "looks fine to me")
        self.assertFalse(sprint.review_coverage(root, ["US0001"])["US0001"]["covered"])

    def test_a_per_unit_self_verdict_is_not_coverage_either(self) -> None:
        """The path that CAN write a self-review. `record_verdict` does not refuse
        reviewer == author - it records the pair and leaves independence to the gate reading
        it - so the coverage predicate has to do that reading. Caught by mutation: deleting
        the guard changed nothing, because the sibling test only exercised the sprint-review
        path, which refuses at write time and so could never reach the guard."""
        import critic
        root = self._repo()
        critic.record_verdict(root, "US0001", "APPROVE", reviewer="same-agent",
                              author="same-agent", issues="none")
        self.assertFalse(sprint.review_coverage(root, ["US0001"])["US0001"]["covered"],
                         "a unit signed off by its own author was counted as reviewed")

    def test_an_independent_per_unit_verdict_IS_coverage(self) -> None:
        """The positive control for the guard above: it must reject a self-verdict without
        rejecting every per-unit verdict, or the coverage step becomes unsatisfiable."""
        import critic
        root = self._repo()
        critic.record_verdict(root, "US0001", "APPROVE", reviewer="reviewer-a",
                              author="author-b", issues="probed")
        self.assertTrue(sprint.review_coverage(root, ["US0001"])["US0001"]["covered"])

    def test_a_review_does_not_cover_a_later_batch(self) -> None:
        """The surface is THAT batch's units. Reviewing batch 1 must not silently clear the
        units of a batch that had not been written when the review ran."""
        import critic
        root = self._repo()
        critic.record_sprint_review(root, ["US0001"], "reviewer-a", "author-b",
                                    "APPROVE", "batch 1 probed")
        self.assertEqual(sprint.uncovered_units(root, ["US0001", "US0009"]), ["US0009"])

    def test_review_batch_records_and_closes_the_span(self) -> None:
        root, rs = self._repo(), self._rs()
        rs.open_run(root, goal="a goal", batch=["US0001"])  # a batch is scoped to a run
        rs.start_batch(root, ["US0001"])
        args = argparse.Namespace(root=root, units=None, reviewer="reviewer-a",
                                  author="author-b", verdict="APPROVE",
                                  findings="probed the refusal paths", base="",
                                  open_units=None, format="text")
        with contextlib.redirect_stdout(io.StringIO()):
            rc = sprint.cmd_review_batch(args)
        self.assertEqual(rc, 0)
        self.assertIsNone(rs.open_batch(root), "the span stayed open after being reviewed")
        self.assertTrue(sprint.review_coverage(root, ["US0001"])["US0001"]["covered"])

    def test_the_documented_open_invocation_parses(self) -> None:
        """Through the REAL parser, not a hand-built Namespace. The sibling tests constructed
        `argparse.Namespace` directly and so could never see that `--reviewer/--author/--findings`
        were `required=True` - which made the documented `--open` form exit 2 and left the entire
        span mechanism unreachable from any documented CLI form. Found by an independent
        reviewer running the invocation printed in help/sprint.md verbatim."""
        root, rs = self._repo(), self._rs()
        # A run is open, because the documented invocation is issued mid-sprint and a delivery
        # batch is scoped to a run (BG0451). Without this the fixture exercised a state the
        # command cannot legitimately be in, which is how `start_batch` came to mint one.
        rs.open_run(root, goal="a goal", batch=["US0001"])
        parser = sprint.build_parser()
        args = parser.parse_args(["review-batch", "--open", "US0001,US0002", "--root", str(root)])
        with contextlib.redirect_stdout(io.StringIO()):
            rc = args.func(args)
        self.assertEqual(rc, 0, "the documented --open invocation was refused")
        self.assertEqual(rs.open_batch(root)["units"], ["US0001", "US0002"])

    def test_recording_a_review_still_demands_its_evidence(self) -> None:
        """The other half of that fix: relaxing the parser must not let a review be recorded
        without a reviewer, an author or findings. The demand moves to the command, where the
        open/review distinction can actually be made."""
        root = self._repo()
        parser = sprint.build_parser()
        args = parser.parse_args(["review-batch", "--units", "US0001", "--root", str(root)])
        err = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            rc = args.func(args)
        self.assertEqual(rc, 2)
        for flag in ("--reviewer", "--author", "--findings"):
            self.assertIn(flag, err.getvalue())

    def test_a_recorded_REJECT_does_not_cover_a_unit(self) -> None:
        """`review_coverage` reimplemented the independence half and forgot the VERDICT half,
        so a recorded REJECT cleared the coverage gate while the tool printed 'it clears no
        unit's gate'. The existing `critic.sprint_covers_independently` had the whole rule;
        the second copy is what drifted. Found by an independent reviewer."""
        import critic
        root = self._repo()
        critic.record_sprint_review(root, ["US0001"], "reviewer-a", "author-b",
                                    "REJECT", "this batch is broken")
        self.assertFalse(sprint.review_coverage(root, ["US0001"])["US0001"]["covered"],
                         "a REJECTED batch cleared the coverage gate")
        self.assertEqual(sprint.uncovered_units(root, ["US0001"]), ["US0001"])

    def test_a_per_unit_REJECT_is_not_covered_either(self) -> None:
        import critic
        root = self._repo()
        critic.record_verdict(root, "US0001", "REJECT", reviewer="reviewer-a",
                              author="author-b", issues="broken")
        self.assertFalse(sprint.review_coverage(root, ["US0001"])["US0001"]["covered"])

    def test_a_REJECT_is_not_laundered_into_coverage_by_the_evidence_lane(self) -> None:
        """The shape the two tests above CANNOT reach, and the one the corpus actually holds.

        Both of them build a repo carrying a verdict and no evidence row, so the REJECT fails
        lane one and every remaining lane misses - covered comes back False for the wrong
        reason, and the branch that laundered it is never executed. Add the evidence row and
        the REJECT falls through into a lane that carries no verdict column by design, cannot
        see that the unit was rejected, and reports it covered. Every reviewed-and-rejected
        unit in this workspace has exactly that shape.
        """
        import critic
        root = self._repo()
        critic.record_verdict(root, "US0001", "REJECT", reviewer="reviewer-a",
                              author="author-b", issues="the repairs are not re-reviewed")
        critic.record_evidence(root, "US0001", reviewer="reviewer-a", author="author-b",
                               findings="an adversarial pass that returned REJECT")
        got = sprint.review_coverage(root, ["US0001"])["US0001"]
        self.assertFalse(got["covered"],
                         f"a REJECT was laundered into coverage by the {got['by']} lane")
        self.assertEqual(sprint.uncovered_units(root, ["US0001"]), ["US0001"])

    def test_an_evidence_row_still_covers_a_unit_that_was_never_rejected(self) -> None:
        """The control, without which the fix above is indistinguishable from deleting the
        evidence lane. Absence of a verdict must still fall through - that is what the other
        lanes are for. Only a verdict that EXISTS and is not an APPROVE stops the search."""
        import critic
        root = self._repo()
        critic.record_evidence(root, "US0001", reviewer="reviewer-a", author="author-b",
                               findings="an adversarial pass with nothing blocking")
        got = sprint.review_coverage(root, ["US0001"])["US0001"]
        self.assertTrue(got["covered"], "the evidence lane stopped covering an unrejected unit")
        self.assertEqual(got["by"], "adversarial evidence")

    def test_an_APPROVE_beside_an_evidence_row_is_still_covered(self) -> None:
        """The second control: the new guard must not treat a POSITIVE verdict as a stop."""
        import critic
        root = self._repo()
        critic.record_verdict(root, "US0001", "APPROVE", reviewer="reviewer-a",
                              author="author-b", issues="none")
        critic.record_evidence(root, "US0001", reviewer="reviewer-a", author="author-b",
                               findings="an adversarial pass")
        self.assertTrue(sprint.review_coverage(root, ["US0001"])["US0001"]["covered"])

    def test_an_unreadable_verdict_ledger_does_not_manufacture_a_rejection(self) -> None:
        """The third control, added because its mutant SURVIVED the first three.

        The new guard reads the verdict ledger. If that read raises, answering "rejected" would
        invent a verdict nobody gave and hold a unit on a filesystem error - a guard failing
        CLOSED on the wrong evidence. The unit must instead be judged by the lanes, which
        report on their own terms. Reached through `review_coverage` rather than by calling the
        helper directly: a library test is not a lane test, and the lane is what gates the close.
        """
        import critic
        root = self._repo()
        critic.record_evidence(root, "US0001", reviewer="reviewer-a", author="author-b",
                               findings="an adversarial pass")
        real = critic.verdict_for

        def boom(*_a, **_k):
            raise OSError("permission denied reading the verdict ledger")

        critic.verdict_for = boom
        try:
            got = sprint.review_coverage(root, ["US0001"])["US0001"]
        finally:
            critic.verdict_for = real
        self.assertTrue(got["covered"],
                        "an unreadable ledger was treated as a REJECT, inventing a verdict")
        self.assertEqual(got["by"], "adversarial evidence")

    def test_the_exclusion_line_does_not_claim_a_false_batch_total(self) -> None:
        """F7. `points` is the PRICED subtotal - unpriced units are skipped before it is
        accumulated - so `priced + removed` was never "the batch" whenever anything was
        unpriced. Both the arithmetic and the whole sentence were surviving mutants."""
        out = sprint.exclusion_line({"built_not_closed": ["US0002"], "built_points": 3,
                                     "points": 5, "unpriced": ["US0003"]})
        self.assertIn("removes 3 point(s)", out)
        self.assertIn("1 unit(s) with no points at all", out,
                      "the unpriced unit was folded into a total that does not add up")
        self.assertNotIn("batch's 8", out, "the false batch total is still claimed")

    def test_the_exclusion_line_is_silent_when_nothing_is_excluded(self) -> None:
        """The other direction of the same branch: no exclusion, no arithmetic claim."""
        out = sprint.exclusion_line({"built_not_closed": ["US0002"], "built_points": 0,
                                     "points": 5, "unpriced": []})
        self.assertIn("US0002", out)
        self.assertNotIn("removes", out)

    def test_the_pre_gate_grandfather_marker_is_not_coverage(self) -> None:
        """M4 from the guard review. `sprint_covers_independently` tests only non-empty-and-
        distinct; `critic.is_independent` rejects PRE_GATE explicitly. The new gate used the
        first, so a migration sentinel the project's OWN independence predicate refuses cleared
        it. Both predicates must agree."""
        import critic
        root = self._repo()
        critic.record_verdict(root, "US0001", "APPROVE", reviewer="reviewer-a",
                              author=critic.PRE_GATE, issues="grandfathered")
        self.assertFalse(sprint.review_coverage(root, ["US0001"])["US0001"]["covered"],
                         "the pre-gate grandfather marker cleared the coverage gate")

    def test_an_empty_batch_names_the_drops_that_emptied_it(self) -> None:
        """M3 from the guard review: the empty-batch branch was untested in BOTH directions,
        and `sprint batch drop` is a one-command escape from the refusal. It still passes -
        there is nothing left to review - but the drops are named, so the escape is on the
        record instead of reading as "no batch on the run state"."""
        root = self._repo()
        state = {"batch": [], "batch_changes": [{"action": "drop", "id": "US0001",
                                                 "reason": "inconvenient"}]}
        ok, detail, _ = sprint._close_review_coverage(root, "RETRO0001", state)
        self.assertTrue(ok, "an empty batch has nothing to review and must not deadlock")
        self.assertIn("US0001", detail, "the drop that emptied the batch is not named")
        self.assertIn("emptied", detail)

    def test_a_genuinely_empty_batch_says_so(self) -> None:
        root = self._repo()
        ok, detail, _ = sprint._close_review_coverage(root, "RETRO0001", {"batch": []})
        self.assertTrue(ok)
        self.assertIn("no batch on the run state", detail)

    def test_close_batch_refuses_when_no_span_is_open(self) -> None:
        """M10: `close_batch`'s docstring calls this the misattribution it exists to stop, and
        nothing tested it. Recording a review against no batch would attribute the pass to
        whichever span happened to be last."""
        root, rs = self._repo(), self._rs()
        with self.assertRaises(ValueError):
            rs.close_batch(root, reviewer="a", author="b", verdict="APPROVE")
        rs.open_run(root, goal="a goal", batch=["US0001"])  # a batch is scoped to a run
        rs.start_batch(root, ["US0001"])
        rs.close_batch(root, reviewer="a", author="b", verdict="APPROVE")
        with self.assertRaises(ValueError):
            rs.close_batch(root, reviewer="a", author="b", verdict="APPROVE")

    def test_findings_raised_against_a_batch_are_recorded_on_it(self) -> None:
        root, rs = self._repo(), self._rs()
        rs.open_run(root, goal="a goal", batch=["US0001"])  # a batch is scoped to a run
        rs.start_batch(root, ["US0001"])
        rs.note_finding(root, "BG0500")
        self.assertIn("BG0500", rs.open_batch(root)["findings_raised"])

    def test_a_finding_raised_with_no_open_batch_attaches_to_nothing(self) -> None:
        """An absence is stated by the caller, never guessed here: attributing to the last
        CLOSED span would price a close-time finding as batch work, inverting the measurement."""
        root, rs = self._repo()  , self._rs()
        rs.open_run(root, goal="a goal", batch=["US0001"])  # a batch is scoped to a run
        rs.start_batch(root, ["US0001"])
        rs.close_batch(root, reviewer="reviewer-a", author="author-b", verdict="APPROVE")
        self.assertIsNone(rs.note_finding(root, "BG0501"))
        self.assertNotIn("BG0501", rs.batches(root)[-1].get("findings_raised") or [])


class FindingPlacementIsMeasuredNotConstantTests(unittest.TestCase):
    """BG0442. `_findings_outside_batches` opened with a function-local `import run_state`. The
    module is `lib/run_state.py`, already bound at module scope, and the local statement shadowed
    that binding and always raised ImportError - lib/run_state.py opens with a relative import no
    top-level import can satisfy. A blanket `except Exception` returned 0 and the diagnostic went
    to `sdlc_md.debug`, a no-op unless SDLC_DEBUG=1. So this was unreachable code returning a
    constant, silently, on every default run, printed under the words "the number this run drives
    to zero" - the metric read identically for 0 close-time findings and for 10,000."""

    def _root(self, *, bugs=()):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        root = Path(d)
        (root / "sdlc-studio" / "bugs").mkdir(parents=True)
        (root / "sdlc-studio" / ".local").mkdir(parents=True)
        from lib import run_state as rs
        rs.open_run(root, goal="a goal", batch=["US0001"])
        for bid, stamp in bugs:
            (root / "sdlc-studio" / "bugs" / f"{bid}-x.md").write_text(
                f"# {bid}: x\n\n> **Status:** Open\n> **Raised-in-batch:** {stamp}\n",
                encoding="utf-8")
        return root, rs

    def test_a_finding_raised_outside_every_batch_is_COUNTED(self) -> None:
        root, rs = self._root(bugs=[("BG0500", "none open 2026-07-30T00:00:00Z")])
        self.assertEqual(sprint._findings_outside_batches(root, rs.batches(root)), 1)

    def test_the_count_is_ZERO_when_nothing_was_raised_outside(self) -> None:
        """The control that makes the test above mean something: a function returning a
        constant passes any single-value assertion, which is how this went unnoticed."""
        root, rs = self._root()
        self.assertEqual(sprint._findings_outside_batches(root, rs.batches(root)), 0)

    def test_a_finding_PREDATING_the_run_is_not_this_runs_close_work(self) -> None:
        """BG0466. The predicate was `raised_in.startswith("none open") and started` - `started`
        only truthy-tested, never compared - so it did not scope by the run window at all.
        Replacing the whole condition with `True` survived all 624 tests of this module while
        genuinely changing behaviour: a pre-existing unstamped backlog bug then counted as this
        run's close work, and the line that says "this run" quietly became "this repo, ever".

        The discriminator is the STAMP against the run's own window, so this test varies only
        that: two identical unstamped bugs, one created inside the run and one long before it.
        """
        root, rs = self._root(bugs=[("BG0500", "none open - raised outside a delivery batch")])
        (root / "sdlc-studio" / "bugs" / "BG0500-x.md").write_text(
            "# BG0500: x\n\n> **Status:** Open\n> **Created:** 2020-01-01\n"
            "> **Raised-in-batch:** none open - raised outside a delivery batch\n",
            encoding="utf-8")
        self.assertEqual(sprint._findings_outside_batches(root, rs.batches(root)), 0,
                         "a bug from years before this run counted as its close work")

    def test_a_finding_raised_DURING_the_run_is_counted(self) -> None:
        """The other half of the same discriminator, so neither direction can be satisfied by a
        constant."""
        root, rs = self._root()
        (root / "sdlc-studio" / "bugs" / "BG0501-x.md").write_text(
            "# BG0501: x\n\n> **Status:** Open\n> **Created:** 2099-01-01\n"
            "> **Raised-in-batch:** none open - raised outside a delivery batch\n",
            encoding="utf-8")
        self.assertEqual(sprint._findings_outside_batches(root, rs.batches(root)), 1)

    def test_a_finding_STAMPED_to_a_batch_is_not_close_work_even_unclaimed(self) -> None:
        """AC3's discriminator, and the mutant that outlived the first attempt at it. Deleting
        the `none open` test entirely SURVIVED, because every fixture here was either unstamped
        or claimed by a span - so nothing separated "raised outside a batch" from "raised at
        all". A finding carrying a real batch timestamp is batch work by its own stamp, whether
        or not a span happens to claim it."""
        root, rs = self._root(bugs=[("BG0503", "2026-07-30T12:00:00Z")])
        self.assertEqual(sprint._findings_outside_batches(root, rs.batches(root)), 0,
                         "a finding stamped INTO a batch was counted as close work")

    def test_a_finding_with_no_Created_date_is_counted_rather_than_dropped(self) -> None:
        """The decision at the unanswerable edge, on the record. Of the two ways to be wrong,
        only one flatters the run being measured: an over-count is visible and arguable, an
        under-count reads as a clean sprint. So an artefact whose date cannot be established
        counts."""
        root, rs = self._root(bugs=[("BG0502", "none open - raised outside a delivery batch")])
        self.assertEqual(sprint._findings_outside_batches(root, rs.batches(root)), 1)

    def test_a_finding_CLAIMED_by_a_batch_is_not_counted_outside_it(self) -> None:
        root, rs = self._root(bugs=[("BG0500", "none open 2026-07-30T00:00:00Z")])
        rs.start_batch(root, ["US0001"])
        rs.note_finding(root, "BG0500")
        self.assertEqual(sprint._findings_outside_batches(root, rs.batches(root)), 0,
                         "a finding a batch span claims is batch work, not close work")

    def test_the_reported_LINE_carries_the_computed_number(self) -> None:
        """A number computed and not rendered is a number nobody reads. The line is the whole
        point: it is what makes the sprint goal's central claim falsifiable.

        TWO fixtures with different counts, because one is not a test. The sibling control
        above says in terms that "a function returning a constant passes any single-value
        assertion" and this test then made exactly that assertion: replacing the call with the
        literal `2` survived all 623 tests of this file, at every scope an independent seat
        tried. The control was placed on the helper and the defect was in the rendering path,
        which is the half this test owns."""
        counts = {}
        for n in (1, 3):
            bugs = [(f"BG050{i}", "none open 2026-07-30T00:00:00Z") for i in range(n)]
            root, _ = self._root(bugs=bugs)
            counts[n] = sprint._finding_placement(root)
        self.assertIn("1 raised outside one", counts[1])
        self.assertIn("3 raised outside one", counts[3])
        self.assertNotIn("3 raised outside one", counts[1],
                         "the rendered number does not move with the computed one")

    def test_BOTH_rendered_numbers_move_with_their_own_input(self) -> None:
        """The line carries two numbers and each needs its own control. Pinning one leaves the
        other free to be a constant: hardcoding `raised` to 0 survived its own selector, and
        hardcoding `outside` survived the whole module - the same defect twice, on the two
        halves of one sentence. Varying the batch-raised count while holding the outside count
        fixed separates them."""
        rendered = {}
        for n_in in (0, 2):
            root, rs = self._root(bugs=[("BG0509", "none open 2026-07-30T00:00:00Z")])
            rs.start_batch(root, ["US0001"])
            for i in range(n_in):
                bug = root / "sdlc-studio" / "bugs" / f"BG051{i}-x.md"
                bug.write_text(f"# BG051{i}: x\n\n> **Status:** Open\n"
                               "> **Raised-in-batch:** 2026-07-30T00:00:00Z\n", encoding="utf-8")
                rs.note_finding(root, f"BG051{i}")
            rendered[n_in] = sprint._finding_placement(root)
        self.assertIn("0 raised at a batch boundary", rendered[0])
        self.assertIn("2 raised at a batch boundary", rendered[2])
        # ...and the OTHER number held still across both, so neither is standing in for the other
        for line in rendered.values():
            self.assertIn("1 raised outside one", line)


class ArtefactKeysAreReadWithONEIdiomTests(unittest.TestCase):
    """BG0452. Three readers hand-rolled an artefact-key parse instead of using the shared one.
    `stem.split("-")[0]` yields `CR` for a v3 key `CR-0001-add-auth`, so the comparison never
    matched and the reader silently returned "not verified" for every id the product now ships
    by DEFAULT. It survived because every existing test used a v2 key: the tests agreed with the
    code about a shape the product no longer ships. Both schema versions are covered here, which
    is the durable half - repairing one call site leaves the next reader free to repeat it."""

    def _report(self, root, stem):
        loc = root / "sdlc-studio" / ".local"
        loc.mkdir(parents=True, exist_ok=True)
        (loc / "verify-report.json").write_text(json.dumps(
            {"stories": {stem: {"verified": 2, "failed": 0, "stale": 0}}}), encoding="utf-8")

    def test_a_v3_key_is_read_by_the_forecast_reader(self) -> None:
        for stem, uid in (("US0001-login", "US0001"), ("CR-0001-add-auth", "CR-0001"),
                          ("BG-01234567-x", "BG-01234567")):
            with self.subTest(stem=stem), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                self._report(root, stem)
                self.assertTrue(sprint._verifiers_all_green(root, uid),
                                f"{stem!r} was not matched to {uid!r} - the reader is splitting "
                                f"on a hyphen the id itself contains")

    def test_a_v3_key_is_read_by_the_readiness_reader(self) -> None:
        import readiness
        for stem, uid in (("US0001-login", "US0001"), ("CR-0001-add-auth", "CR-0001")):
            with self.subTest(stem=stem), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                self._report(root, stem)
                self.assertTrue(readiness._already_satisfied(root, uid))

    def test_the_retro_resolver_takes_BOTH_id_spellings(self) -> None:
        """And it delegates rather than parsing: `RETRO` is a meta prefix ID_RE does not
        recognise, so reaching for `extract_record_id` here returns None for every retro there
        is - the obvious repair for the other two sites is the wrong one for this one."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rd = root / "sdlc-studio" / "retros"
            rd.mkdir(parents=True)
            # The FILE is v3-spelled. That is the shape the hand-rolled split could not read -
            # it yields `RETRO` and matches nothing - and the shape the shared resolver accepts.
            # No such file exists in this repo today, so the divergence was latent; the test
            # pins the contract rather than reproducing a failure anyone had seen.
            target = rd / "RETRO-0047-a-sprint.md"
            target.write_text("# RETRO-0047: a sprint\n", encoding="utf-8")
            (rd / "_index.md").write_text("# Retros\n", encoding="utf-8")
            for spelling in ("RETRO0047", "RETRO-0047", "retro0047"):
                with self.subTest(spelling=spelling):
                    self.assertEqual(sprint._retro_path(root, spelling), target,
                                     f"{spelling!r} did not resolve a v3-named retro file")
            self.assertIsNone(sprint._retro_path(root, "RETRO9999"))


class TheGroomingGateReadsTheCRITERIATests(unittest.TestCase):
    """BG0449. `sprint-plan.json` recorded `mode: enforce, blocking: true, ungroomed: [],
    ok: true` and listed four stories as GROOMED while each carried the template's literal
    ungroomed banner and three `{{role}}/{{capability}}/{{benefit}}` placeholders. The gate
    asked only for Affects and Points, so a story that declared files and a size was certified
    groomed however empty its criteria were - in the mode whose entire purpose is to refuse
    them. Four stories and 15 points were planned into a sprint on that green.
    `conformance.story_is_ungroomed` already read both shapes; nothing asked it."""

    def _story(self, d: Path, sid: str, ac: str) -> dict:
        sd = d / "sdlc-studio" / "stories"
        sd.mkdir(parents=True, exist_ok=True)
        (sd / "x.py").write_text("", encoding="utf-8")
        path = sd / f"{sid}-x.md"
        path.write_text(
            f"# {sid}: s\n\n> **Status:** Draft\n> **Points:** 3\n"
            f"> **Affects:** sdlc-studio/stories/x.py\n\n"
            f"## Acceptance Criteria\n\n{ac}\n", encoding="utf-8")
        return {"id": sid, "type": "story", "path": str(path)}

    _BANNER = ("> **Ungroomed - acceptance criteria are a grooming placeholder** - author each "
               "criterion while grooming.")
    _SCAFFOLD = "### AC1: {{define}}\n\n- **Given** {{context}}\n- **When** {{action}}\n"
    _REAL = "### AC1: it behaves\n\n- **Given** a thing\n- **Verify:** shell true\n"

    def test_the_BANNER_shape_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            bd = sprint.breakdown(root, [self._story(root, "US0001", self._BANNER)])
            self.assertFalse(bd["ok"])
            self.assertEqual([u["id"] for u in bd["ungroomed"]], ["US0001"])
            self.assertIn("Acceptance Criteria", " ".join(bd["ungroomed"][0]["missing"]))

    def test_the_PLACEHOLDER_scaffold_is_refused_too(self) -> None:
        """Either shape alone can be edited away: the banner is removed by hand during
        grooming, and the scaffold is what remains if someone deletes the banner without doing
        the work. A gate reading only one of them checks something other than grooming."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            bd = sprint.breakdown(root, [self._story(root, "US0002", self._SCAFFOLD)])
            self.assertFalse(bd["ok"])
            self.assertEqual([u["id"] for u in bd["ungroomed"]], ["US0002"])

    def test_a_GROOMED_story_still_passes(self) -> None:
        """The control the original tests apparently were: a gate that always passes satisfies
        "the gate passes a groomed plan" just as well as a correct one does."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            bd = sprint.breakdown(root, [self._story(root, "US0003", self._REAL)])
            self.assertTrue(bd["ok"], f"a groomed story was refused: {bd['ungroomed']}")
            self.assertEqual(bd["groomed"], ["US0003"])

    def test_the_check_is_named_in_the_DoR_downgrade_list(self) -> None:
        """Every other grooming check can be stood down by a project's Definition of Ready, and
        one that cannot is a rule with no opt-out where its siblings all have one."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            dor = root / "sdlc-studio" / "definition-of-ready.md"
            dor.parent.mkdir(parents=True, exist_ok=True)
            dor.write_text("# Definition of Ready\n\n## Story\n\n- [ ] grooming.affects\n",
                           encoding="utf-8")
            bd = sprint.breakdown(root, [self._story(root, "US0004", self._BANNER)])
            self.assertIn("grooming.acs", bd.get("downgraded") or [],
                          "the new check cannot be stood down, unlike every sibling")


class TheCloseCertifiesRatherThanReviewsTests(unittest.TestCase):
    """US0562. The close asserts that coverage EXISTS; it does not perform the review."""

    def _repo(self, batch, reviewed=()):
        import critic
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        (root / "sdlc-studio" / ".local").mkdir(parents=True)
        for u in reviewed:
            critic.record_sprint_review(root, [u], "reviewer-a", "author-b",
                                        "APPROVE", "probed")
        return root, {"batch": list(batch)}

    def test_the_close_refuses_and_names_uncovered_units(self) -> None:
        root, state = self._repo(["US0001", "US0002"], reviewed=["US0001"])
        ok, detail, _ = sprint._close_review_coverage(root, "RETRO0001", state)
        self.assertFalse(ok, "the close passed a batch carrying an unreviewed unit")
        self.assertIn("US0002", detail, "the refusal did not name the uncovered unit")
        self.assertNotIn("US0001,", detail, "a covered unit was named as uncovered")

    def test_the_refusal_names_the_remedy(self) -> None:
        root, state = self._repo(["US0001"])
        ok, _, remedy = sprint._close_review_coverage(root, "RETRO0001", state)
        self.assertFalse(ok)
        self.assertIn("review-batch", remedy, "the refusal is not actionable from its own text")
        self.assertIn("reviewer must differ", remedy)

    def test_a_covered_batch_passes(self) -> None:
        """The check must not become a blanket refusal nobody can satisfy."""
        root, state = self._repo(["US0001", "US0002"], reviewed=["US0001", "US0002"])
        ok, detail, _ = sprint._close_review_coverage(root, "RETRO0001", state)
        self.assertTrue(ok, f"a fully covered batch was refused: {detail}")

    def test_the_close_reports_where_findings_were_raised(self) -> None:
        """The goal 'defects are found inside the sprint' is only falsifiable if the split is
        recorded. It is reported whether or not the step refuses."""
        from lib import run_state
        root, state = self._repo(["US0001"], reviewed=["US0001"])
        run_state.open_run(root, goal="a goal", batch=["US0001"])  # a batch is scoped to a run
        run_state.start_batch(root, ["US0001"])
        run_state.note_finding(root, "BG0777")
        ok, detail, _ = sprint._close_review_coverage(root, "RETRO0001", state)
        self.assertTrue(ok)
        self.assertIn("finding placement", detail)
        self.assertIn("1 raised at a batch boundary", detail)

    def test_every_chain_step_is_previewed_by_the_dry_run(self) -> None:
        """`close_dry_run` prints "N step(s) UNEVALUATED. An unevaluated step is not a passing
        one" - a completeness claim it cannot make while a step is missing from its table. The
        new blocking step was absent, so the preview reported 0 unevaluated and stayed silent
        about the step the chain then refused at. Pinned structurally so the next added step
        cannot repeat it. `gate` is the one legitimate omission: it is run separately."""
        previewed = set(sprint.DRY_RUN_ACTION_STEPS) | {"gate"}
        self.assertEqual(set(sprint._CLOSE_CHAIN) - previewed, set(),
                         "a chain step is invisible to `close --dry-run`, which asserts it "
                         "evaluated all of them")

    def test_preflight_reports_uncovered_units(self) -> None:
        """Preflight promises EVERY unmet prerequisite and says the close is one more run once
        they are cleared. It cannot say that while a blocking chain step is absent from it."""
        root, state = self._repo(["US0001", "US0002"], reviewed=["US0001"])
        blockers = sprint.coverage_blockers(root, state)
        self.assertEqual(len(blockers), 1)
        self.assertEqual(blockers[0]["stage"], "review-coverage")
        self.assertIn("US0002", blockers[0]["detail"])
        self.assertIn("review-batch", blockers[0]["remedy"])

    def test_preflight_reports_nothing_when_the_batch_is_covered(self) -> None:
        root, state = self._repo(["US0001"], reviewed=["US0001"])
        self.assertEqual([], sprint.coverage_blockers(root, state))

    def test_close_preflight_actually_calls_the_coverage_check(self) -> None:
        """The call SITE, proven by execution rather than by reading the source. The first
        attempt asserted the string `_coverage_blocker(state)` appeared in `close_preflight`'s
        source - which the closure's own `def` line supplied, so deleting the call left the
        test green. Caught by mutation. A sentinel raised from the patched function escapes
        before the expensive gate block, so this stays cheap."""
        class _Reached(Exception):
            pass

        def _boom(root, state):
            raise _Reached()

        root, _ = self._repo(["US0001"])
        from lib import run_state
        run_state.update(root, run_id="RUN-TEST", sprint_goal="a goal",
                         sprint_goal_verdict={"verdict": "achieved"}, batch=["US0001"])
        real = sprint.coverage_blockers
        sprint.coverage_blockers = _boom
        try:
            with self.assertRaises(_Reached), contextlib.redirect_stdout(io.StringIO()):
                sprint.close_preflight(root, None)
        finally:
            sprint.coverage_blockers = real

    def test_the_documented_invocations_actually_parse(self) -> None:
        """US0563 AC3 said help documents `review-batch` "in runnable invocation form" and
        verified it by grepping for the string. The string was present the whole time the
        command exited 2. A verifier that cannot fail when the claim is false is not a verifier -
        this project's own recorded scar. Every documented invocation is now PARSED."""
        import shlex
        repo = Path(__file__).resolve().parents[5]
        docs = [repo / ".claude/skills/sdlc-studio/help/sprint.md",
                repo / ".claude/skills/sdlc-studio/reference-doctrine.md"]
        parser = sprint.build_parser()
        found = 0
        for doc in docs:
            if not doc.is_file():
                continue
            text = doc.read_text(encoding="utf-8").replace("\\\n", " ")
            for line in text.splitlines():
                stripped = line.strip().lstrip("`").strip()
                if "sprint.py review-batch" not in stripped:
                    continue
                argv = shlex.split(stripped[stripped.index("sprint.py") + len("sprint.py"):])
                argv = [a for a in argv if a and not a.startswith("#")]
                if not argv or argv[0] != "review-batch":
                    continue
                found += 1
                with self.subTest(doc=doc.name, argv=" ".join(argv)):
                    try:
                        parser.parse_args(argv)
                    except SystemExit as exc:
                        self.fail(f"{doc.name} documents an invocation that does not parse "
                                  f"(exit {exc.code}): sprint.py {' '.join(argv)}")
        self.assertGreaterEqual(found, 1, "no documented review-batch invocation was found "
                                          "to check - the verifier would pass vacuously")

    def test_the_step_is_first_in_the_chain(self) -> None:
        """Refusing here costs seconds; refusing after the retro scaffold and a full gate run
        costs minutes. Placement is the fix, in the chain as well as in the lifecycle."""
        self.assertEqual(sprint._CLOSE_CHAIN[0], "review-coverage")


class CloseCostIsAttributableTests(unittest.TestCase):
    """BG0404. `close_cost` filtered on `run_id is None or r['run_id'] == run_id`, so a None
    run id SHORT-CIRCUITED the filter and summed every close ever recorded as this one's -
    over-reporting by 6x on seconds and 143x on elapsed, in the one report whose stated purpose
    is measurement honesty."""

    def _ledger(self, root, rows):
        dest = root / sprint.EXECUTION_LEDGER_REL
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps({"runs": rows}), encoding="utf-8")

    def _root(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        return Path(td.name)

    ROWS = [
        {"moment": "close", "run_id": "RUN-A", "at": "2026-07-01T00:00:00Z", "seconds": 100.0},
        {"moment": "close", "run_id": "RUN-B", "at": "2026-07-02T00:00:00Z", "seconds": 200.0},
        {"moment": "close", "run_id": "RUN-C", "at": "2026-07-03T00:00:00Z",
         "mode": "reuse", "reused_from": "2026-07-01T00:00:00Z"},
    ]

    def test_no_run_id_reports_not_attributable_not_the_whole_ledger(self) -> None:
        root = self._root()
        self._ledger(root, self.ROWS)
        cost = sprint.close_cost(root, None)
        self.assertIsNone(cost["gate_seconds"],
                          "a run with no id reported the whole ledger as its own cost")
        self.assertEqual(cost["gate_runs"], 0)
        self.assertTrue(any("not attributable" in u.lower() for u in cost["unmeasured"]),
                        f"the absence was not stated: {cost['unmeasured']}")

    def test_a_reuse_resolves_against_another_runs_row(self) -> None:
        """A reuse saves seconds a PREVIOUS run paid for, so resolving it against rows already
        filtered to THIS run could only ever fail. A measured 100s saving was reported as
        unknown with its source row two lines above it in the same file."""
        root = self._root()
        self._ledger(root, self.ROWS)
        cost = sprint.close_cost(root, "RUN-C")
        self.assertEqual(cost["reused_runs"], 1)
        self.assertEqual(cost["reused_seconds"], 100.0,
                         "the reuse's saving was not resolved from the source run's row")
        self.assertEqual(cost["unmeasured"], [])

    def test_an_untraceable_reuse_is_still_unmeasured_not_zero(self) -> None:
        root = self._root()
        self._ledger(root, [{"moment": "close", "run_id": "RUN-C", "at": "2026-07-03T00:00:00Z",
                             "mode": "reuse", "reused_from": "1999-01-01T00:00:00Z"}])
        cost = sprint.close_cost(root, "RUN-C")
        # None, not 0.0 - this module's standing convention that unmeasured is not zero. A
        # saving that cannot be traced is unknown, and reporting it as zero would understate
        # the reuse rather than admit the gap.
        self.assertIsNone(cost["reused_seconds"],
                          "an untraceable reuse was read as a measured zero")
        self.assertEqual(cost["reused_runs"], 1)
        self.assertTrue(cost["unmeasured"], "an untraceable reuse was silently swallowed")

    def test_a_named_run_sums_only_its_own_rows(self) -> None:
        root = self._root()
        self._ledger(root, self.ROWS)
        self.assertEqual(sprint.close_cost(root, "RUN-A")["gate_seconds"], 100.0)


class AnUnreadableRunStateReportsRatherThanRaisesTests(unittest.TestCase):
    """BG0405. `run_state.read` RAISES on an unparseable file by design - unreadable is not the
    same fact as absent. Two callers documented as never blocking sat above their own guards, so
    a corrupt run state produced a traceback where a brief (and a close judgement) used to be."""

    def _corrupt(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        local = root / "sdlc-studio" / ".local"
        local.mkdir(parents=True)
        (local / "run-state.json").write_text("{ this is not json", encoding="utf-8")
        return root

    def test_a_lane_brief_is_still_issued(self) -> None:
        root = self._corrupt()
        res = sprint.lane_dispatch(root, ["US0001"])
        self.assertIn("scope_note", res)
        self.assertIn("UNKNOWN", (res["scope_note"] or ""),
                      "the degraded seam scope was not reported")

    def test_a_readable_state_still_widens_the_scope(self) -> None:
        """The positive control: degrading on a corrupt file must not degrade always."""
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        (root / "sdlc-studio" / ".local").mkdir(parents=True)
        from lib import run_state
        run_state.update(root, run_id="RUN-X", batch=["US0009"])
        res = sprint.lane_dispatch(root, ["US0001"])
        self.assertIsNone(res["scope_note"], "a readable run state was reported as degraded")

    def test_the_goal_judgement_reports_rather_than_raises(self) -> None:
        root = self._corrupt()
        lines = sprint.close_goal_judgement(root, {"sprint_goal": "a goal"})
        self.assertTrue(any("UNREADABLE" in l for l in lines),
                        "the unreadable run state was not reported at all")


class BlockerGroupingSurvivesBothIdErasTests(unittest.TestCase):
    """BG0403. BG0394 put the detail in the group key so two blockers with different causes
    stop merging, and destroyed the property the grouping exists for in two ways: the local id
    pattern knew only the v2 four-digit form, and a done-gate refusal quotes the unit's OWN
    failing criterion - so one owed action fanned into one change request per unit, the exact
    fan-out CR0495 was raised to stop."""

    def _signoff(self, units):
        return [{"stage": "sign-off", "detail": f"{u}: no critic verdict recorded",
                 "remedy": f"record an independent verdict for {u}"} for u in units]

    def test_three_v2_units_are_one_group(self) -> None:
        groups = sprint.group_blockers(self._signoff(["US0001", "US0002", "US0003"]))
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0]["units"], ["US0001", "US0002", "US0003"])

    def test_three_v3_units_are_one_group_and_are_named(self) -> None:
        """The v3 half. The local pattern matched neither, so three identical blockers made
        three groups, each with `units: []` - and the per-unit criteria the same change added
        were therefore empty, so the artefact named none of the units it covered."""
        ids = ["US-01JQK3F8", "US-01JQK3F9", "US-01JQK3FA"]
        groups = sprint.group_blockers(self._signoff(ids))
        self.assertEqual(len(groups), 1, "v3 ids did not group")
        self.assertEqual(groups[0]["units"], ["US01JQK3F8", "US01JQK3F9", "US01JQK3FA"],
                         "the group names none of the v3 units it covers")

    def test_a_done_gate_refusal_is_one_group_across_units(self) -> None:
        """The cause is what is OWED - the gate refuses - and it is the same owed action for
        every unit. The per-unit criterion stays in the detail for the artefact's body."""
        blockers = [{"stage": "done-gate",
                     "cause": "the Done transition's AC-verify gate refuses",
                     "detail": f"{u}: AC{i} 'a different criterion each time' failed",
                     "remedy": "clear the gate this names, then re-run"}
                    for i, u in enumerate(("US0001", "US0002", "US0003"))]
        groups = sprint.group_blockers(blockers)
        self.assertEqual(len(groups), 1, "one owed action fanned into one artefact per unit")
        self.assertEqual(len(groups[0]["blockers"]), 3,
                         "the per-unit details were lost, not merely un-keyed")

    def test_the_done_gate_blocker_CARRIES_an_explicit_cause(self) -> None:
        """M4: deleting the `cause` key from `_done_gate_preflight`'s blocker survived all 600
        sprint tests, and the one-CR-per-unit fan-out returned in full. The sibling test builds
        the blocker by hand with a cause already in it, so it could never see the producer stop
        emitting one. Asserted at the PRODUCER."""
        import inspect
        src = inspect.getsource(sprint._done_gate_preflight)
        self.assertIn('"cause"', src,
                      "the done-gate blocker no longer states its cause, so one owed action "
                      "files one change request per unit again")

    def test_the_done_gate_producer_groups_to_one(self) -> None:
        """The behavioural half, through the real producer: three units failing the done gate
        must be ONE group, because the owed action is the same for all three."""
        import contextlib as _ctx
        import io as _io
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        sd = root / "sdlc-studio" / "stories"
        sd.mkdir(parents=True)
        for n in (1, 2, 3):
            (sd / f"US000{n}-x.md").write_text(
                f"# US000{n}: x\n\n> **Status:** Review\n\n"
                f"## Acceptance Criteria\n\n### AC{n}\n- **Verify:** shell false\n",
                encoding="utf-8")
        with _ctx.redirect_stdout(_io.StringIO()), _ctx.redirect_stderr(_io.StringIO()):
            blockers = sprint._done_gate_preflight(root, {"batch": ["US0001", "US0002", "US0003"]})
        if not blockers:
            self.skipTest("the fixture did not trip the done gate")
        groups = sprint.group_blockers(blockers)
        self.assertEqual(1, len(groups),
                         f"three units failing one gate produced {len(groups)} groups, so "
                         f"--file-and-close files that many change requests for one action")

    def test_genuinely_different_causes_stay_apart(self) -> None:
        """BG0394's property, which this must not undo: merging unrelated blockers hides one
        behind another, and the second detail never reaches the filed artefact."""
        groups = sprint.group_blockers([
            {"stage": "gate", "detail": "the validate lane failed", "remedy": "same remedy"},
            {"stage": "gate", "detail": "the review-current lane failed", "remedy": "same remedy"}])
        self.assertEqual(len(groups), 2)

    def test_the_masking_uses_the_shared_grammar(self) -> None:
        """AC4: a third id era is covered on the day it is declared, not on the day someone
        remembers this local copy exists."""
        from lib import sdlc_md as _md  # noqa: PLC0415 - deferred, as elsewhere in this file
        self.assertIs(sprint._UNIT_IN_DETAIL, _md.ID_SEARCH_RE)


class AGoalClauseIsNotAnsweredByGuessworkTests(unittest.TestCase):
    """BG0402's two remaining halves. `_recorded_clause_verdicts` carried a SECOND polarity
    mapping that read everything not-yes as `partial` - so a seat answering NO, the strongest
    signal a review can give, was recorded as a partial success while `verdict_polarity` sat
    unused in the same module. It then FANNED one plan-time whole-goal answer across every
    clause, manufacturing per-clause evidence nobody gave."""

    def _review(self, seats):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        (root / "sdlc-studio" / ".local").mkdir(parents=True)
        (root / "sdlc-studio" / ".local" / "goal-review.json").write_text(
            json.dumps({"rounds": [{"seats": seats}]}), encoding="utf-8")
        return root

    def test_a_whole_goal_answer_is_not_fanned_across_clauses(self) -> None:
        root = self._review([{"seat": "qa", "achievable": "yes"}])
        self.assertIsNone(sprint._recorded_clause_verdicts(root, ["clause a", "clause b"]),
                          "one plan-time answer about the whole goal was copied onto every "
                          "clause as per-clause evidence")

    def test_the_clauses_key_SURVIVES_the_real_writer(self) -> None:
        """The dead path an independent reviewer found. The reader was changed to require
        `seat["clauses"]` while `_seat_from_dict` whitelisted four fields and silently stripped
        it, so NO writer in the shipped code could produce one - the panel reported UNANSWERED on
        every close, permanently, and all six sibling tests asserted over a fixture shape the
        product cannot write. End-to-end through the CLI."""
        import contextlib as _ctx
        import io as _io
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        (root / "sdlc-studio" / ".local").mkdir(parents=True)
        ff = root / "gr.json"
        ff.write_text(json.dumps({"goal": "clause a and clause b", "seats": [
            {"seat": "qa", "achievable": "yes", "done_means": "d", "one_increment": "yes",
             "clauses": {"clause a": "no", "clause b": "yes"}}]}), encoding="utf-8")
        with _ctx.redirect_stdout(_io.StringIO()), _ctx.redirect_stderr(_io.StringIO()):
            rc = sprint.main(["goal-review", "record", "--fields-file", str(ff),
                              "--root", str(root)])
        self.assertEqual(0, rc)
        recorded = json.loads(
            (root / "sdlc-studio" / ".local" / "goal-review.json").read_text(encoding="utf-8"))
        seat = recorded["rounds"][-1]["seats"][0]
        self.assertIn("clauses", seat,
                      "the writer stripped the per-clause answers, so the reader can never "
                      "return anything and the panel is permanently UNANSWERED")
        self.assertEqual({"clause a": {"qa": "missed"}, "clause b": {"qa": "achieved"}},
                         sprint._recorded_clause_verdicts(root, ["clause a", "clause b"]),
                         "the round-trip through the real writer produced no verdicts")

    def test_a_seat_answering_no_is_recorded_missed_not_partial(self) -> None:
        root = self._review([{"seat": "qa", "clauses": {"clause a": "no"}}])
        got = sprint._recorded_clause_verdicts(root, ["clause a"])
        self.assertEqual(got, {"clause a": {"qa": "missed"}},
                         "a seat's NO was softened to a partial success")

    def test_a_seat_answering_yes_is_recorded_achieved(self) -> None:
        root = self._review([{"seat": "qa", "clauses": {"clause a": "yes"}}])
        self.assertEqual(sprint._recorded_clause_verdicts(root, ["clause a"]),
                         {"clause a": {"qa": "achieved"}})

    def test_an_unclear_answer_leaves_the_clause_unanswered(self) -> None:
        """Not a verdict either way. The panel already knows how to report UNANSWERED, and
        inventing one from an unreadable answer is the class this bug is about."""
        root = self._review([{"seat": "qa", "clauses": {"clause a": "maybe, hard to say"}}])
        self.assertIsNone(sprint._recorded_clause_verdicts(root, ["clause a"]))

    def test_a_clause_no_seat_answered_is_absent(self) -> None:
        root = self._review([{"seat": "qa", "clauses": {"clause a": "yes"}}])
        got = sprint._recorded_clause_verdicts(root, ["clause a", "clause b"])
        self.assertNotIn("clause b", got, "an unanswered clause was given a verdict")

    def test_the_one_polarity_reading_is_used(self) -> None:
        """AC3 asserted structurally: the seat's answer goes through `verdict_polarity`, so a
        third spelling of "no" is understood everywhere at once or nowhere."""
        root = self._review([{"seat": "qa", "clauses": {"clause a": "N"}}])
        self.assertEqual(sprint.verdict_polarity("N"), "no")
        self.assertEqual(sprint._recorded_clause_verdicts(root, ["clause a"]),
                         {"clause a": {"qa": "missed"}})


class TheCloseAsksTheEstimateQuestionTests(unittest.TestCase):
    """BG0414. The retro template reserves a block for the estimate-versus-actual comparison
    and its prose asserts the question is asked every sprint. Nothing ran it, so the largest
    sprint on record contributed no row to the calibration every later forecast is drawn from -
    and an empty block reads as "no comparison to make", indistinguishable from "never run"."""

    def test_the_accuracy_write_is_a_close_step(self) -> None:
        self.assertIn("retro-accuracy", sprint._CLOSE_CHAIN,
                      "the close still does not ask the question its own template promises")
        self.assertTrue(hasattr(sprint, "_close_retro_accuracy"))

    def test_it_runs_after_the_retro_is_validated(self) -> None:
        """Order matters: writing a generated block into a retro that has not passed its own
        content check would put derived content on top of a malformed document."""
        chain = list(sprint._CLOSE_CHAIN)
        self.assertLess(chain.index("retro-validate"), chain.index("retro-accuracy"))

    def test_the_dry_run_previews_it(self) -> None:
        """`close --dry-run` asserts it evaluated every step; a step missing from its table
        makes that claim false by omission."""
        self.assertIn("retro-accuracy", sprint.DRY_RUN_ACTION_STEPS)

    def test_a_NIL_result_does_not_block_the_close(self) -> None:
        """The docstring promised "NEVER BLOCKING on a nil result" and the first version blocked
        on exactly that: a retro naming no units has nothing to compare, and `cmd_close` returns
        1 at the first `not ok`, so every such close hard-stopped at this step. A refusal for
        lacking a measurement nobody could have taken."""
        import contextlib as _ctx
        import io as _io
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        r = root / "sdlc-studio" / "retros"
        r.mkdir(parents=True)
        (r / "RETRO0001-x.md").write_text(
            "# RETRO-0001: x\n\n> **Delivered:** 1 / 1\n\n## Delivered\n\nx\n\n"
            "## What went well\n\nx\n\n## What was hard / what stalled\n\nx\n\n"
            "## Actions raised\n\nx\n", encoding="utf-8")
        with _ctx.redirect_stdout(_io.StringIO()), _ctx.redirect_stderr(_io.StringIO()):
            ok, detail, _ = sprint._close_retro_accuracy(root, "RETRO0001", {})
        self.assertTrue(ok, f"a nil accuracy result hard-stopped the close: {detail}")
        self.assertIn("NOTHING TO MEASURE", detail,
                      "the nil result passed silently - an absence must be stated")

    def test_a_failing_write_stops_the_close_and_says_why(self) -> None:
        import retro as retro_mod
        real = retro_mod.main
        retro_mod.main = lambda argv: (_ for _ in ()).throw(SystemExit(2))
        try:
            ok, _detail, remedy = sprint._close_retro_accuracy(".", "RETRO0001", {})
        finally:
            retro_mod.main = real
        self.assertFalse(ok, "a failed accuracy write passed the close silently")
        self.assertIn("accuracy", remedy)


class TheCommandActuallyReachesTheseMechanismsTests(unittest.TestCase):
    """BG0401. Three of RUN-01KYNKDP's repairs could be fully reverted with no test going red,
    because every test called the delivered FUNCTION and none asserted the CALL from the
    command. `for line in close_goal_judgement(...)` -> `for line in []` unwired the goal panel,
    the defect judgement, the prediction miss and the whole batch caller-check, silently.

    The pattern here is a sentinel: patch the mechanism to raise, run the command, and assert
    the sentinel escapes. It cannot pass if the call site is deleted, and unlike a source grep
    it proves the line RUNS rather than that it is present."""

    def _run(self, mod, root):
        import contextlib as _ctx
        with _ctx.redirect_stdout(io.StringIO()), _ctx.redirect_stderr(io.StringIO()):
            return mod.main(["close", "--retro", "RETRO0001", "--root", str(root)])

    def _repo(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        _close_state(root)
        _close_story(root)
        _close_retro(root)
        return root

    def test_the_close_reaches_the_goal_judgement(self) -> None:
        class _Reached(Exception):
            pass

        root = self._repo()
        mod = _load()
        real = mod.close_goal_judgement
        mod.close_goal_judgement = lambda *a, **k: (_ for _ in ()).throw(_Reached())
        try:
            with _patch_close_steps(mod):
                with self.assertRaises(_Reached):
                    self._run(mod, root)
        finally:
            mod.close_goal_judgement = real

    def test_the_judgement_is_not_reached_when_the_chain_stops(self) -> None:
        """The negative control. Without it the sentinel could be firing from somewhere other
        than the close's own reporting, and the test would prove nothing about placement."""
        class _Reached(Exception):
            pass

        root = self._repo()
        mod = _load()
        real = mod.close_goal_judgement
        mod.close_goal_judgement = lambda *a, **k: (_ for _ in ()).throw(_Reached())
        try:
            with _patch_close_steps(mod, fail_at="retro-validate"):
                rc = self._run(mod, root)     # stops early; must NOT reach the judgement
            self.assertNotEqual(rc, 0)
        finally:
            mod.close_goal_judgement = real


class TheLaneCommandIssuesABriefOverACorruptStateTests(unittest.TestCase):
    """BG0405's stop-ship. The first repair guarded `lane_dispatch` and left the identical
    unguarded read three statements later in `cmd_lane`, so the artefact's own reproduction
    still tracebacked and issued no brief - and the test written for it exercised the LIBRARY
    function, not the command it names. A library test is not a lane test."""

    def _corrupt(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        (root / "sdlc-studio" / ".local").mkdir(parents=True)
        (root / "sdlc-studio" / ".local" / "run-state.json").write_text(
            "{ this is not json", encoding="utf-8")
        bugs = root / "sdlc-studio" / "bugs"
        bugs.mkdir(parents=True)
        (bugs / "BG0001-b.md").write_text(
            "# BG0001: b\n\n> **Status:** Open\n> **Severity:** Medium\n"
            "> **Affects:** a.py\n> **Points:** 2\n\n"
            "## Acceptance Criteria\n\n### AC1\n- **Verify:** shell true\n", encoding="utf-8")
        return root

    def test_the_COMMAND_does_not_traceback(self) -> None:
        root = self._corrupt()
        mod = _load()
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = mod.main(["--root", str(root), "lane", "brief", "--units", "BG0001"])
        self.assertIn(rc, (0, 1, 2), f"the command raised instead of reporting (rc={rc})")
        self.assertIn("UNKNOWN", err.getvalue(),
                      "the unreadable run state was not reported at all")

    def test_lane_RETURN_does_not_traceback_and_keeps_the_verification_result(self) -> None:
        """BG0453. The third occurrence of one defect. BG0405 guarded `lane_dispatch`; round
        two rejected it because the same unguarded read sat in `cmd_lane`; that repair guarded
        the BRIEF branch and left the RETURN branch, twenty lines below.

        The return path is the worst of the three: `lane_return` has already RUN the unit's
        acceptance criteria before this read, so a raise discards a completed verification and
        the operator cannot tell from the traceback whether the unit passed.
        """
        root = self._corrupt()
        mod = _load()
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = mod.main(["--root", str(root), "lane", "return", "--units", "BG0001",
                           "--claimed", "done"])
        self.assertIn(rc, (0, 1, 2), f"the command raised instead of reporting (rc={rc})")
        self.assertIn("BG0001", out.getvalue() + err.getvalue(),
                      "the verification result was discarded rather than reported")

    def test_no_run_state_call_in_cmd_lane_bypasses_the_guard(self) -> None:
        """The test that stops a FOURTH occurrence, over the call SITES rather than over any
        one command's output.

        Each previous round fixed the line the reviewer named instead of the class they
        described, so each repair left a sibling. A behavioural test per branch cannot catch
        the branch nobody thought to write a test for; this one fails the moment a bare
        `run_state.` call is added to `cmd_lane` without routing through `_lane_run_state`.
        """
        import ast
        import inspect
        import textwrap
        mod = _load()
        tree = ast.parse(textwrap.dedent(inspect.getsource(mod.cmd_lane)))

        # Every `run_state.x(...)` must sit inside a lambda handed to `_lane_run_state`. Read
        # with AST rather than by grepping lines: the guarded form spans several lines and puts
        # the call inside a lambda, so a line-wise check cannot tell a routed call from a bare
        # one - the first version of this test failed on its own correct subject.
        guarded, wrapped = set(), []
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id == "_lane_run_state"):
                wrapped.append(node)
                for arg in node.args:
                    for inner in ast.walk(arg):
                        if isinstance(inner, ast.Call):
                            guarded.add(id(inner))
        bare = []
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "run_state"
                    and id(node) not in guarded):
                bare.append(f"line {node.lineno}: run_state.{node.func.attr}(...)")
        self.assertEqual([], bare,
                         "these run_state calls in cmd_lane bypass the best-effort guard, so an "
                         "unreadable run state stops the command or discards its work: "
                         f"{bare}")
        self.assertGreaterEqual(len(wrapped), 3,
                                "fewer than three guarded run-state calls remain in cmd_lane - "
                                "this test would otherwise pass over a function that had simply "
                                "stopped touching the run state, proving nothing")

    def test_recording_a_lane_start_cannot_withhold_the_brief(self) -> None:
        """The third read in the same command. It writes, so it fails differently - and a
        recording failure must not swallow the brief that was already composed.

        Now asserted BEHAVIOURALLY. The previous version searched a 400-character window after
        the words `record_lane_start` for `except Exception`, which an independent reviewer
        rightly called out: the window reached the end of the function, so it could not tell
        WHICH read was guarded, and it passed only because a sibling test happened to fire.
        Structure is covered by the call-site test above; this one covers the behaviour.
        """
        root = self._corrupt()
        mod = _load()
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = mod.main(["--root", str(root), "lane", "brief", "--units", "BG0001"])
        self.assertIn(rc, (0, 1, 2), f"the command raised instead of reporting (rc={rc})")
        self.assertIn("BG0001", out.getvalue(),
                      "the brief was withheld because the lane start could not be recorded")


class BlockingScopeTests(unittest.TestCase):
    """Only what THIS unit's diff broke may hold its gate (reference-doctrine rule 19).

    The failure being fixed is not a gate that was too lenient: it is a gate no correct
    increment could pass, because every review found something true of the repository and
    every finding blocked. A verdict that fails every unit carries the same information as one
    that passes every unit.
    """

    @staticmethod
    def _load_critic():
        spec = importlib.util.spec_from_file_location(
            "critic", SCRIPT.parent / "critic.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules["critic"] = mod
        spec.loader.exec_module(mod)
        return mod

    def _review(self, issues, verdict="REJECT"):
        return {"verdict": verdict, "reviewer": "ada", "author": "grace", "issues": issues}

    def test_a_pre_existing_finding_does_not_block(self) -> None:
        """MUTANT: treat any REJECT as not covering, as the predicate used to.

        The findings are real and reported; they are simply not this increment's debt."""
        critic = self._load_critic()
        review = self._review("[pre-existing] BG0123 the gate is slow; "
                              "[pre-existing] CR0456 refine leaves placeholders")
        with tempfile.TemporaryDirectory() as d:
            covered = critic.sprint_covers_independently(Path(d), "US0001", review)
        self.assertTrue(
            covered,
            "a review whose only findings predate the base ref failed to cover the unit - "
            "the gate is judging the repository's condition, not this increment")

    def test_a_regression_still_blocks(self) -> None:
        """The positive control. MUTANT: let every REJECT through as covering.

        Without this the change is satisfied by a gate that simply stopped blocking, which is
        the failure mode opposite to the one being fixed and no better."""
        critic = self._load_critic()
        review = self._review("[regression] verify_ac crashes on empty Affects; "
                              "[pre-existing] BG0123 the gate is slow")
        with tempfile.TemporaryDirectory() as d:
            covered = critic.sprint_covers_independently(Path(d), "US0001", review)
        self.assertFalse(covered, "a REGRESSION finding did not hold the gate")

    def test_the_two_sets_are_reported_apart(self) -> None:
        """MUTANT: render one undifferentiated list.

        A reader must be able to tell what held the gate from what was merely noticed, or a
        pre-existing observation gets repaired at close time as this batch's debt."""
        sprint = _load()
        out = sprint.render_finding_sets(
            "[regression] a broke; [new] b appeared; [pre-existing] BG0123 c was always so")
        self.assertRegex(out, r"BLOCKING \(2\)")
        self.assertRegex(out, r"NOT BLOCKING \(1\)")
        head, _, tail = out.partition("NOT BLOCKING")
        self.assertIn("a broke", head)
        self.assertIn("b appeared", head)
        self.assertNotIn("c was always so", head,
                         "a pre-existing finding was listed among the blocking set")
        self.assertIn("c was always so", tail)
        self.assertIn("base ref", tail,
                      "the non-blocking set does not state WHY those findings do not block")


class LoopTerminationTests(unittest.TestCase):
    """A review-repair loop that has stopped converging must STOP, not keep going.

    The existing growing-set detector reported divergence and carried on. A loop that announces
    it is diverging and then runs another round has reported nothing - and unattended, it burns
    a night going backwards.
    """

    def test_the_round_cap_ends_the_loop(self) -> None:
        """MUTANT: raise the cap to infinity, or compare with `>` instead of `>=`.

        Asserted at the boundary rather than well past it, because an off-by-one here is a
        whole extra round of the most expensive thing the sprint does.
        """
        sprint = _load()
        stop, why = sprint.loop_termination([{"outstanding": 3}] * 4, cap=4)
        self.assertTrue(stop, "the loop ran past its declared round cap")
        self.assertIn("cap", why.lower(), "the reason does not name the cap")

    def test_a_growing_set_stops_the_loop(self) -> None:
        """MUTANT: report the growth without stopping, as the detector did before."""
        sprint = _load()
        stop, why = sprint.loop_termination(
            [{"outstanding": 2}, {"outstanding": 4}, {"outstanding": 6}], cap=10)
        self.assertTrue(stop, "an outstanding set growing twice in a row did not stop the loop")
        self.assertIn("grew", why.lower(), "the reason does not name the divergence")

    def test_one_growth_alone_does_not_stop_the_loop(self) -> None:
        """MUTANT: stop on a single growth.

        One round can legitimately surface more than it fixed - a repair exposing a neighbour
        is normal. TWO consecutive is the signal that the loop is chasing a moving target.
        """
        sprint = _load()
        stop, _why = sprint.loop_termination(
            [{"outstanding": 2}, {"outstanding": 5}, {"outstanding": 3}], cap=10)
        self.assertFalse(stop, "a single round of growth stopped a loop that then converged")

    def test_the_rule_is_wired_into_the_close_not_only_the_library(self) -> None:
        """MUTANT: delete the `loop_termination` call from `_record_close_attempt`.

        `loop_termination` passing in isolation says nothing about whether any close consults
        it. A rule reachable only from Python is the lane-not-library defect (LL0040) that cost
        this project a review round last sprint.
        """
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / "stories").mkdir(parents=True)
            (root / "sdlc-studio" / "retros").mkdir(parents=True)
            (root / "sdlc-studio" / ".local").mkdir(parents=True, exist_ok=True)
            (root / "sdlc-studio" / "stories" / "US0001-x.md").write_text(
                "# US0001: a unit\n\n> **Status:** Review\n> **Points:** 3\n"
                "> **Affects:** src/a.py\n", encoding="utf-8")
            (root / "sdlc-studio" / "retros" / "RETRO0001-r.md").write_text(
                "# RETRO0001: r\n\n> **Status:** Draft\n", encoding="utf-8")
            # FOUR attempts: the declared cap is reached, so the rule says stop.
            attempts = [{"at": f"2026-08-02T00:0{i}:00Z", "outstanding": n, "stages": ["gate"]}
                        for i, n in enumerate([3, 4, 5, 6])]
            (root / "sdlc-studio" / ".local" / "run-state.json").write_text(json.dumps(
                {"run_id": "RUN-T", "batch": ["US0001"], "outcome": "running",
                 "close_attempts": attempts}), encoding="utf-8")
            buf, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
                rc = sprint.main(["close", "--retro", "RETRO0001", "--root", str(root)])
            out = buf.getvalue() + err.getvalue()
        self.assertNotEqual(0, rc, "a close over a non-converging loop reported success")
        self.assertIn("LOOP STOPPED", out, "the close never consulted the termination rule")
        self.assertIn("stops here", out,
                      "the close REPORTED the divergence and carried on - a loop that announces "
                      "it is diverging and then runs the next round has reported nothing")

    def test_a_shrinking_set_runs_on(self) -> None:
        """The control. MUTANT: stop unconditionally.

        A gate that ends every loop discriminates no better than one that ends none.
        """
        sprint = _load()
        stop, _why = sprint.loop_termination(
            [{"outstanding": 9}, {"outstanding": 5}, {"outstanding": 2}], cap=10)
        self.assertFalse(stop, "a converging loop was stopped")


class EscalationTests(unittest.TestCase):
    """A stuck unit reaches the operator immediately, rather than waiting silently.

    Human-in-the-LEAD means the decision reaches them; it does not mean the machine blocks on
    input that will not arrive. An escalation that waits is indistinguishable from a hang.
    """

    def test_a_twice_rejected_unit_escalates(self) -> None:
        """MUTANT: escalate only on the third rejection, or never.

        Two is the boundary because a first REJECT is the loop working - the finding gets
        repaired. A second on the same unit says the repair is not converging.
        """
        sprint = _load()
        esc, why = sprint.panel_escalation(["REJECT", "REJECT"], {})
        self.assertTrue(esc, "a unit rejected twice by the panel did not escalate")
        self.assertIn("twice", why.lower(), "the reason does not say why it escalated")

    def test_one_rejection_does_not_escalate(self) -> None:
        """The control for the count. MUTANT: escalate on the first REJECT.

        That would escalate every ordinary finding and train the operator to ignore it, which
        is how a notification channel stops working.
        """
        sprint = _load()
        esc, _why = sprint.panel_escalation(["REJECT"], {})
        self.assertFalse(esc, "a single rejection escalated - the loop had not failed yet")

    def test_disagreeing_seats_escalate(self) -> None:
        """MUTANT: resolve disagreement by majority.

        The disagreement IS the signal. Auto-resolving it discards exactly the information the
        panel was convened to produce, and does so silently.
        """
        sprint = _load()
        esc, why = sprint.panel_escalation(
            [], {"qa": "REJECT", "engineering": "APPROVE", "product": "APPROVE"})
        self.assertTrue(esc, "a split panel was resolved instead of escalated")
        self.assertIn("qa", why, "the reason does not name who dissented")

    def test_a_unanimous_panel_does_not_escalate(self) -> None:
        """The control. MUTANT: escalate on every panel result."""
        sprint = _load()
        esc, _why = sprint.panel_escalation(
            [], {"qa": "APPROVE", "engineering": "APPROVE", "product": "APPROVE"})
        self.assertFalse(esc, "a unanimous panel escalated")

    def test_escalation_notifies_rather_than_waits(self) -> None:
        """MUTANT: return a reason that asks the operator to respond before continuing.

        Pinned on the CONTRACT the reason states, because the difference between notifying and
        waiting is invisible in a return value otherwise - and getting it wrong turns an
        unattended run into a silent hang.
        """
        sprint = _load()
        _esc, why = sprint.panel_escalation(["REJECT", "REJECT"], {})
        self.assertIn("notified", why.lower(),
                      "the escalation does not state that the operator is NOTIFIED")
        self.assertNotIn("waiting for", why.lower(),
                         "the escalation blocks on operator input, which unattended is a hang")


class CadenceDebtFileAndCloseTests(unittest.TestCase):
    """The documented bounded exit must work on the case it was written for.

    A close with nine independently reviewed, signed-off units could not proceed by ANY route:
    the plain close blocked on a stale repo-wide ceremony, and `--file-and-close` classed the
    same lane a hard correctness blocker and refused to file it. A close with no exit is worse
    than either behaviour on its own.
    """

    def test_a_stale_periodic_review_is_filed_as_debt(self) -> None:
        """MUTANT: drop the cadence test from the hard-blocker filter."""
        sprint = _load()
        blocker = {"stage": "gate", "detail": "CADENCE DEBT (reported, not blocking): "
                                              "reviews/LATEST.md is stale"}
        self.assertTrue(sprint._is_cadence_debt(blocker),
                        "a lane declaring itself cadence debt was not recognised as filable")

    def test_a_correctness_blocker_is_still_refused(self) -> None:
        """The positive control. MUTANT: treat every gate blocker as cadence debt.

        That would turn the bounded exit into a way to file away a red gate, which is the
        bypass it exists to prevent.
        """
        sprint = _load()
        blocker = {"stage": "gate", "detail": "conformance: 3 unit(s) have no critiqued verdict"}
        self.assertFalse(sprint._is_cadence_debt(blocker),
                         "a real correctness lane was classed as filable ceremony debt")

    def test_the_classification_is_read_from_the_lane_not_a_second_list(self) -> None:
        """MUTANT: replace the marker test with a hardcoded list of lane names here.

        A second list drifts from the first, and a lane added tomorrow is silently classed
        correctness - the enumeration failure this project keeps meeting.
        """
        src = (Path(__file__).resolve().parent.parent / "sprint.py").read_text(encoding="utf-8")
        body = src.split("def _is_cadence_debt")[1][:500]
        self.assertIn("_CADENCE_MARKER", body,
                      "the classifier does not read the lane's own declaration")
        self.assertNotIn("review-current", body,
                         "the classifier names lanes directly - a second list that will drift")


class ReviewBatchFieldsFileTests(unittest.TestCase):
    """A review's findings are the prose most likely to carry shell metacharacters.

    Backticks and `$(` inside a shell argument are command substitution, not text. This
    project mangled its own review findings that way twice in one run, and once quoted the
    mangled output back into an artefact.
    """

    def test_findings_with_metacharacters_are_stored_verbatim(self) -> None:
        """MUTANT: read the findings from the flag when a fields-file is given.

        The value carries the exact shapes that break: a backtick span and a `$(` sequence.
        """
        sprint = _load()
        hazard = ("the check ran `git log -S` and $(pwd) was wrong; "
                  "`grep -c BG0348` returned 0")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / "stories").mkdir(parents=True)
            (root / "sdlc-studio" / ".local").mkdir(parents=True, exist_ok=True)
            (root / "sdlc-studio" / "stories" / "US0001-x.md").write_text(
                "# US0001: a unit\n\n> **Status:** Review\n> **Points:** 3\n"
                "> **Affects:** src/a.py\n", encoding="utf-8")
            (root / "sdlc-studio" / ".local" / "run-state.json").write_text(
                json.dumps({"run_id": "RUN-T", "batch": ["US0001"], "outcome": "running"}),
                encoding="utf-8")
            doc = root / "findings.json"
            doc.write_text(json.dumps({"findings": hazard}), encoding="utf-8")
            # THROUGH `--fields-file`, which is what the criterion says. The first version called
            # `resolve_prose_fields` directly and never passed the flag, so deleting the whole
            # fields-file branch from `cmd_review_batch` left it green.
            buf, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
                rc = sprint.main(["review-batch", "--units", "US0001", "--reviewer", "qa",
                                  "--author", "me", "--verdict", "APPROVE",
                                  "--fields-file", str(doc), "--root", str(root)])
            out = buf.getvalue() + err.getvalue()
            record = (root / "sdlc-studio" / "reviews" / "sprint-review-record.md")
            stored = record.read_text(encoding="utf-8") if record.exists() else ""
        self.assertEqual(0, rc, f"review-batch --fields-file did not run:\n{out}")
        self.assertIn(hazard, stored,
                      "the findings text did not reach the record verbatim through "
                      "`--fields-file` - the flag the criterion names")

    def test_the_flag_path_is_unchanged(self) -> None:
        """The control. MUTANT: require a fields-file always.

        The flag stays for ordinary prose; this is an addition, not a migration.
        """
        sprint = _load()
        src = (Path(__file__).resolve().parent.parent / "sprint.py").read_text(encoding="utf-8")
        body = src.split("def cmd_review_batch")[1][:1400]
        self.assertIn('getattr(args, "fields_file", None)', body,
                      "the fields-file is read unconditionally rather than when supplied")
        self.assertIn("args.findings", body,
                      "the flag path was removed - this is an addition, not a migration")


class RunbookTests(unittest.TestCase):
    """The toolchain reaches the agent at plan time, and cannot rot silently.

    A runbook nobody is made to read is one that gets skipped, which is the whole failure it
    addresses: the hand-rolling this project keeps catching is recall failure AT A STEP
    BOUNDARY - the tool was known, just not at the moment the step arose.
    """

    def test_plan_and_run_print_the_runbook(self) -> None:
        """MUTANT: delete the render call from the plan's print path.

        Drives `sprint plan` and reads its OUTPUT. The first version greped `sprint.py` for the
        renderer's name, which a dead reference satisfies: replacing the call site with
        `_unused = render_runbook_pointer` left it green. A grep over source text is not a test
        of what the source does, and this is the file where that lesson was filed.
        """
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / "stories").mkdir(parents=True)
            (root / "sdlc-studio" / ".local").mkdir(parents=True, exist_ok=True)
            (root / "src").mkdir()
            (root / "src" / "a.py").write_text("x = 1\n", encoding="utf-8")
            skill = root / ".claude" / "skills" / "sdlc-studio"
            skill.mkdir(parents=True)
            (skill / "reference-sprint-toolchain.md").write_text(
                "# Toolchain\n\n## Orient\n\n`status.py`\n", encoding="utf-8")
            (root / "sdlc-studio" / "stories" / "US0001-x.md").write_text(
                "# US0001: a unit\n\n> **Status:** Ready\n> **Points:** 3\n"
                "> **Affects:** src/a.py\n\n## Acceptance Criteria\n\n"
                "### AC1: it behaves\n\n- **Then** it behaves\n- **Verify:** shell true\n",
                encoding="utf-8")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
                rc = sprint.main(["plan", "--stories", "Ready", "--root", str(root)])
            out = buf.getvalue()
        self.assertEqual(0, rc, f"the plan did not run:\n{out}")
        self.assertIn("reference-sprint-toolchain.md", out,
                      "`sprint plan` printed no pointer to the toolchain runbook, so the "
                      "document meant to be read at the step boundary is never mentioned")

    def test_an_absent_runbook_is_reported_not_omitted(self) -> None:
        """MUTANT: return [] when the runbook is missing.

        A plan that silently drops it reads exactly like one that never had it - the same
        absence-is-not-an-answer rule the carried lessons already follow.
        """
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            lines = sprint.render_runbook_pointer(Path(d))
        self.assertTrue(lines, "an absent runbook produced no output at all")
        self.assertIn("MISSING", " ".join(lines).upper(),
                      "the absence was not reported")


class ContentReviewGoalTests(unittest.TestCase):
    """The recorded content review carries the GOAL it was an answer about.

    The only assertion was that the flag string appears in the parser, so making `plan` accept
    `--content-review` and discard it survived - and so did recording the review against an
    empty goal. A bookend answer detached from the question it answered cannot be scored
    against anything at the close, which is the entire purpose of recording it.
    """

    def test_the_plan_records_the_review_against_its_sprint_goal(self) -> None:
        """MUTANT: pass `""` instead of `state.get("sprint_goal")`.

        Asserted on the RECORDED VALUE. A parser-level assertion is satisfied by a flag that is
        accepted and thrown away, which is what shipped.
        """
        sprint = _load()
        goal = "the close runs without the operator in it"
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / ".local").mkdir(parents=True)
            # A review belongs to a RUN - recorded against none it is written where the next
            # `plan --write` destroys it, and the writer says so. Open one first.
            import json as _j
            (root / "sdlc-studio" / ".local" / "run-state.json").write_text(
                _j.dumps({"run_id": "RUN-T", "batch": ["US0001"], "outcome": "running"}),
                encoding="utf-8")
            sprint.record_content_review(root, "plan", goal, "yes")
            recorded = sprint.content_reviews(root)
        self.assertTrue(recorded, "no content review was recorded at all")
        plan = recorded.get("plan") or {}
        self.assertEqual(goal, plan.get("goal"),
                         f"the recorded review does not carry the goal it answered: {recorded}")

    def test_a_review_recorded_against_no_goal_is_refused(self) -> None:
        """MUTANT: accept an empty goal silently.

        An answer with no question is the state the mutant above produced, so the writer must
        say so rather than storing it - otherwise the close scores a prediction about nothing.
        """
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / ".local").mkdir(parents=True)
            import json as _j
            (root / "sdlc-studio" / ".local" / "run-state.json").write_text(
                _j.dumps({"run_id": "RUN-T", "batch": ["US0001"], "outcome": "running"}),
                encoding="utf-8")
            with self.assertRaises(ValueError):
                sprint.record_content_review(root, "plan", "", "yes")


if __name__ == "__main__":
    unittest.main()
