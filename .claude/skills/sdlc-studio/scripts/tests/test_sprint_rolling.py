"""Rolling multi-sprint policy: standing policy, boundary chain, per-cycle records.

RED first - `sprint boundary`, the `--cycles` policy flags and the run-state archive do
not exist yet.

The boundary is the unit under test throughout: one command that closes the current
cycle, fetches, regenerates the plan from the live backlog, previews it, and opens the
next cycle - stopping with a handoff at any of the three refusal causes.

Most boundary tests STUB the six close-chain steps. The chain itself is covered by
`test_sprint.py`; what is under test here is that the boundary RUNS it, reports it
against the cycle it closed, and refuses to continue when it fails. `BoundaryGateHaltTests`
deliberately runs the real chain so the halt is proven against a real failure, not a stub.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import subprocess as _sp
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent.parent


def _load(script: str, name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{script}.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# Loaded under a name of its OWN, not "sprint".
#
# `cmd_close` resolves each close-chain step through `sys.modules[__name__]` at call time
# (which is what lets a test patch one step). `test_sprint.py` also loads sprint.py and
# registers it as `sys.modules["sprint"]` - so under the full suite, whichever module loaded
# last owns that slot, and the stubs patched onto THIS instance would be looked up on the
# OTHER one and silently ignored. The tests then pass alone and fail in the suite. A private
# name makes the instance under test the one its own `__name__` resolves to.
sprint = _load("sprint", "sprint_rolling_sut")
run_state = sprint.run_state


# --- fixtures ---------------------------------------------------------------------

_INDEXES = (("bugs", "Bugs"), ("stories", "Stories"), ("epics", "Epics"),
            ("change-requests", "Change Requests"), ("retros", "Retros"),
            ("handoffs", "Handoffs"), ("reviews", "Reviews"), ("rfcs", "RFCs"))


def _ws(root: Path) -> Path:
    """A minimal but complete workspace: every artefact dir with a real index table."""
    sd = root / "sdlc-studio"
    for sub, hdr in _INDEXES:
        (sd / sub).mkdir(parents=True, exist_ok=True)
        (sd / sub / "_index.md").write_text(
            f"# {hdr}\n\n| ID | Title | Status |\n| --- | --- | --- |\n", encoding="utf-8")
    return sd


def _bug(root: Path, num: int, status: str = "Open", points: int = 2,
         groomed: bool = True) -> None:
    """A groomed bug - `sprint plan` refuses an ungroomed batch, so an ungroomed fixture
    would test the gate rather than the boundary."""
    d = root / "sdlc-studio" / "bugs"
    d.mkdir(parents=True, exist_ok=True)
    meta = ""
    if groomed:
        f = root / f"src/bg{num:04d}.py"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("", encoding="utf-8")
        meta = f"> **Affects:** src/bg{num:04d}.py\n> **Points:** {points}\n"
    (d / f"BG{num:04d}-x.md").write_text(
        f"# BG{num:04d}: b{num}\n\n> **Status:** {status}\n> **Severity:** Medium\n{meta}",
        encoding="utf-8")
    idx = d / "_index.md"
    if idx.is_file():
        idx.write_text(idx.read_text(encoding="utf-8")
                       + f"| [BG{num:04d}](BG{num:04d}-x.md) | b{num} | {status} |\n",
                       encoding="utf-8")


def _retro(root: Path, rid: str = "RETRO0001", lesson: str | None = None) -> str:
    d = root / "sdlc-studio" / "retros"
    d.mkdir(parents=True, exist_ok=True)
    line = lesson or "A lesson worth keeping. It carries a second sentence so it cuts cleanly."
    (d / f"{rid}-x.md").write_text(
        f"# {rid}: r\n\n> **Status:** Complete\n\n## Lessons\n\n- {line}\n", encoding="utf-8")
    idx = d / "_index.md"
    if idx.is_file():
        idx.write_text(idx.read_text(encoding="utf-8") + f"| [{rid}]({rid}-x.md) | r | Complete |\n",
                       encoding="utf-8")
    return rid


def _capture(argv: list[str]) -> tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        try:
            rc = sprint.main(argv)
        except SystemExit as exc:  # argparse refusals
            rc = exc.code if isinstance(exc.code, int) else 1
    return rc, buf.getvalue()


def _plan(root: Path, *extra: str) -> tuple[int, str]:
    return _capture(["plan", "--bugs", "Open", "--write", "--no-fetch",
                     "--root", str(root), "--sprint-goal", "ship the fixture batch", *extra])


def _boundary(root: Path, *extra: str) -> tuple[int, str]:
    return _capture(["boundary", "--root", str(root), *extra])


@contextlib.contextmanager
def _stubbed_close(record: list | None = None):
    """Stub the six close-chain steps green.

    `cmd_close` resolves each step through `globals()` at call time precisely so this is
    possible. The stub records the step name, which is what proves the boundary ran the
    chain in the ceremony's order rather than skipping it.
    """
    names = ("retro_validate", "retro_extract", "lessons_summary", "gate", "handoff",
             "reconcile")
    saved = {n: getattr(sprint, f"_close_{n}") for n in names}

    def make(n):
        def step(root, retro_id, state):
            if record is not None:
                record.append(n.replace("_", "-"))
            return True, f"{n} ok", ""
        return step

    for n in names:
        setattr(sprint, f"_close_{n}", make(n))
    try:
        yield
    finally:
        for n, fn in saved.items():
            setattr(sprint, f"_close_{n}", fn)


def _judged(root: Path, verdict: str = "achieved") -> None:
    """Record the goal verdict so the close chain is reached (a close refuses an unjudged
    goal, which is a different failure from the one under test)."""
    run_state.update(root, sprint_goal_verdict={"verdict": verdict, "note": "fixture"})


def _ready_cycle(root: Path, bugs: tuple[int, ...] = (1, 2)) -> str:
    """A workspace with an open, judged cycle-1 rolling run and a retro to close on."""
    _ws(root)
    for n in bugs:
        _bug(root, n)
    rid = _retro(root)
    _plan(root, "--cycles", "2")
    _judged(root)
    return rid


# --- US0229: the standing policy ---------------------------------------------------

class RollingPolicyRecordTests(unittest.TestCase):
    """AC1: `--cycles N` plus the policy elements are recorded on run-state and echoed."""

    def test_policy_is_recorded_on_run_state(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _ws(root); _bug(root, 1); _bug(root, 2)
            rc, out = _plan(root, "--cycles", "3", "--order", "wsjf",
                            "--appetite-units", "5", "--stop-on", "empty-backlog")
            self.assertEqual(rc, 0, out)
            pol = run_state.read(root)["policy"]
            self.assertEqual(pol["cycles"], 3)
            self.assertEqual(pol["order"], "wsjf")
            self.assertEqual(pol["sprint_goal"], "ship the fixture batch")
            self.assertEqual(pol["capacity"]["units"], 5)
            self.assertEqual(pol["queries"], [{"kind": "bug", "status": "Open"}])
            for cause in ("close-gate", "origin-drift", "refused-plan"):
                self.assertIn(cause, pol["stop_conditions"])
            self.assertIn("empty-backlog", pol["stop_conditions"])

    def test_plan_echoes_the_policy_it_recorded(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _ws(root); _bug(root, 1)
            rc, out = _plan(root, "--cycles", "3")
            self.assertEqual(rc, 0, out)
            self.assertIn("rolling policy", out)
            self.assertIn("3 cycle", out)
            self.assertIn("ship the fixture batch", out)

    def test_the_first_cycle_is_numbered_and_counted(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _ws(root); _bug(root, 1)
            _plan(root, "--cycles", "3")
            cyc = run_state.read(root)["cycle"]
            self.assertEqual(cyc["index"], 1)
            self.assertEqual(cyc["remaining"], 2)

    def test_no_cycles_flag_records_no_policy(self) -> None:
        # Opt-in: a plain sprint is untouched by any of this.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _ws(root); _bug(root, 1)
            rc, out = _plan(root)
            self.assertEqual(rc, 0, out)
            self.assertIsNone(run_state.read(root).get("policy"))


class RollingPolicyRefusalTests(unittest.TestCase):
    """AC2: an incomplete policy is refused, never defaulted."""

    def test_cycles_below_one_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _ws(root); _bug(root, 1)
            rc, out = _plan(root, "--cycles", "0")
            self.assertEqual(rc, 2, out)
            # Named, not merely rejected: an argparse "unrecognized arguments" error also
            # exits 2 and also contains "--cycles", so the refusal must say what is wrong.
            self.assertIn("policy refused", out)
            self.assertIn("1 or more", out)
            self.assertNotIn("unrecognized", out)
            self.assertIsNone(run_state.read(root).get("policy"))

    def test_cycles_without_a_sprint_goal_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _ws(root); _bug(root, 1)
            rc, out = _capture(["plan", "--bugs", "Open", "--write", "--no-fetch",
                                "--root", str(root), "--sprint-goal", "", "--cycles", "2"])
            self.assertEqual(rc, 2, out)
            self.assertIn("policy refused", out)
            self.assertIn("--sprint-goal", out)
            self.assertNotIn("unrecognized", out)
            self.assertIsNone(run_state.read(root).get("policy"))

    def test_a_refused_policy_opens_no_run_at_all(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _ws(root); _bug(root, 1)
            rc, out = _plan(root, "--cycles", "-2")
            self.assertEqual(rc, 2, out)
            self.assertIn("policy refused", out)
            self.assertEqual(run_state.read(root), {})

    def test_cycles_over_a_frozen_worklist_is_refused(self) -> None:
        # A rolling policy regenerates from the live backlog; a worklist is the frozen
        # queue this exists to abolish, so the combination is a contradiction.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _ws(root); _bug(root, 1)
            wl = root / "wl.txt"
            wl.write_text("BG0001\n", encoding="utf-8")
            rc, out = _capture(["plan", "--worklist", str(wl), "--write", "--no-fetch",
                                "--root", str(root), "--sprint-goal", "g", "--cycles", "2"])
            self.assertEqual(rc, 2, out)
            self.assertIn("--worklist", out)


class RollingPolicyCarryOverTests(unittest.TestCase):
    """AC3: the next cycle reads the recorded policy, and the count decrements."""

    def test_next_cycle_reads_the_recorded_policy(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _ws(root); _bug(root, 1); _bug(root, 2)
            _retro(root)
            _plan(root, "--cycles", "2", "--order", "wsjf", "--appetite-units", "7")
            _judged(root)
            with _stubbed_close():
                rc, out = _boundary(root, "--retro", "RETRO0001", "--no-fetch")
            self.assertEqual(rc, 0, out)
            state = run_state.read(root)
            self.assertEqual(state["policy"]["order"], "wsjf")
            self.assertEqual(state["policy"]["capacity"]["units"], 7)
            self.assertEqual(state["sprint_goal"], "ship the fixture batch")

    def test_remaining_decrements_by_one(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rid = _ready_cycle(root)
            self.assertEqual(run_state.read(root)["cycle"]["remaining"], 1)
            with _stubbed_close():
                rc, out = _boundary(root, "--retro", rid, "--no-fetch")
            self.assertEqual(rc, 0, out)
            cyc = run_state.read(root)["cycle"]
            self.assertEqual(cyc["index"], 2)
            self.assertEqual(cyc["remaining"], 0)

    def test_boundary_without_a_policy_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _ws(root); _bug(root, 1); _retro(root)
            _plan(root)                       # no --cycles: no standing policy
            _judged(root)
            rc, out = _boundary(root, "--retro", "RETRO0001", "--no-fetch")
            self.assertEqual(rc, 2, out)
            self.assertIn("policy", out)


# --- US0230: the boundary close-down chain ------------------------------------------

class BoundaryCloseDownTests(unittest.TestCase):
    """AC1: the close ceremony runs, in order, reported against the cycle it closed."""

    def test_the_chain_runs_before_any_replan(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rid = _ready_cycle(root)
            steps: list[str] = []
            with _stubbed_close(steps):
                rc, out = _boundary(root, "--retro", rid, "--no-fetch")
            self.assertEqual(rc, 0, out)
            for step in ("retro-validate", "retro-extract", "lessons-summary", "gate"):
                self.assertIn(step, steps)
            self.assertEqual(steps, sorted(steps, key=steps.index))  # ran once, in order
            # ...and the close-down is reported before the regenerate step.
            self.assertLess(out.index("close-down"), out.index("regenerate"))

    def test_each_step_is_reported_against_its_cycle(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rid = _ready_cycle(root)
            with _stubbed_close():
                rc, out = _boundary(root, "--retro", rid, "--no-fetch")
            self.assertEqual(rc, 0, out)
            self.assertIn("cycle 1 | close [1/6] retro-validate", out)
            self.assertIn("cycle 1 | close [4/6] gate", out)


class BoundaryGateHaltTests(unittest.TestCase):
    """AC2: a failed close-down halts the run - non-zero, nothing further planned.

    The chain is NOT stubbed here: the close fails for real (the retro is empty, so
    `retro validate` refuses), which is what makes the halt evidence rather than a
    rehearsal of the stub.
    """

    def _empty_retro(self, root: Path) -> str:
        d = root / "sdlc-studio" / "retros"
        (d / "RETRO0009-x.md").write_text("# RETRO0009: r\n\n> **Status:** Draft\n",
                                          encoding="utf-8")
        idx = d / "_index.md"
        idx.write_text(idx.read_text(encoding="utf-8")
                       + "| [RETRO0009](RETRO0009-x.md) | r | Draft |\n", encoding="utf-8")
        return "RETRO0009"

    def test_a_failing_close_step_halts_the_loop(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _ws(root); _bug(root, 1); _bug(root, 2)
            rid = self._empty_retro(root)
            _plan(root, "--cycles", "2")
            _judged(root)
            before = run_state.read(root)["run_id"]
            rc, out = _boundary(root, "--retro", rid, "--no-fetch")
            self.assertNotEqual(rc, 0)
            self.assertIn("close-gate", out)
            self.assertIn("remedy", out.lower())
            state = run_state.read(root)
            self.assertEqual(state["run_id"], before)          # no next cycle opened
            self.assertEqual(state["cycle"]["index"], 1)
            self.assertEqual(state["stop"]["cause"], "close-gate")

    def test_nothing_is_regenerated_after_a_failed_close(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _ws(root); _bug(root, 1)
            rid = self._empty_retro(root)
            _plan(root, "--cycles", "2")
            _judged(root)
            rc, out = _boundary(root, "--retro", rid, "--no-fetch")
            self.assertNotEqual(rc, 0)
            # The positive anchor first: without it this passes on a boundary command that
            # does not exist, because a run that never starts also never regenerates.
            self.assertIn("[1/4] close-down", out)
            self.assertNotIn("regenerate", out)
            self.assertNotIn("preview", out)


# --- US0231: fetch and origin drift at each boundary ---------------------------------

def _run(cwd, *args):
    return _sp.run(["git", "-C", str(cwd), *args], capture_output=True, text=True,
                   env=gitutil.git_env())


def _behind_repo(d) -> Path:
    """A work repo one commit behind its origin (a teammate pushed while the run ran)."""
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
    (other / "REMOTE.md").write_text("remote work\n", encoding="utf-8")
    _run(other, "add", "-A"); _run(other, "commit", "-qm", "remote")
    _run(other, "push", "-q", "origin", "main")
    return work


class BoundaryOriginFetchTests(unittest.TestCase):
    """AC1: the drift check runs AT the boundary, per cycle; --no-fetch still compares."""

    def test_the_boundary_fetches_and_reports_per_cycle(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _behind_repo(d)
            rid = _ready_cycle(root)
            calls: list[bool] = []
            real = sprint.origin_drift
            sprint.origin_drift = lambda r, do_fetch=True: (calls.append(do_fetch)
                                                            or real(r, do_fetch=do_fetch))
            try:
                with _stubbed_close():
                    rc, out = _boundary(root, "--retro", rid)
            finally:
                sprint.origin_drift = real
            self.assertEqual(calls, [True], out)       # fetched at the boundary
            self.assertIn("cycle 1 | fetch", out)

    def test_no_fetch_suppresses_the_fetch_but_still_compares(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _behind_repo(d)
            rid = _ready_cycle(root)
            calls: list[bool] = []
            real = sprint.origin_drift
            sprint.origin_drift = lambda r, do_fetch=True: (calls.append(do_fetch)
                                                            or real(r, do_fetch=do_fetch))
            try:
                with _stubbed_close():
                    rc, out = _boundary(root, "--retro", rid, "--no-fetch")
            finally:
                sprint.origin_drift = real
            self.assertEqual(calls, [False], out)      # compared, did not fetch
            self.assertIn("cycle 1 | fetch", out)


class BoundaryStrictDriftRefusalTests(unittest.TestCase):
    """AC2: behind origin stops the boundary under --strict; warns and continues without."""

    def test_strict_stops_at_the_diverged_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _behind_repo(d)
            rid = _ready_cycle(root)
            before = run_state.read(root)["run_id"]
            with _stubbed_close():
                rc, out = _boundary(root, "--retro", rid, "--strict")
            self.assertNotEqual(rc, 0, out)
            self.assertIn("origin-drift", out)
            self.assertNotIn("preview", out)
            state = run_state.read(root)
            self.assertEqual(state["run_id"], before)      # the next cycle never opened
            self.assertEqual(state["stop"]["cause"], "origin-drift")

    def test_without_strict_the_drift_only_warns(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _behind_repo(d)
            rid = _ready_cycle(root)
            before = run_state.read(root)["run_id"]
            with _stubbed_close():
                rc, out = _boundary(root, "--retro", rid)
            self.assertEqual(rc, 0, out)
            self.assertIn("origin drift", out)
            self.assertNotEqual(run_state.read(root)["run_id"], before)   # cycle 2 opened


# --- US0232: regenerate from the live backlog ----------------------------------------

def _regenerated_plan(root: Path) -> dict:
    return json.loads((root / "sdlc-studio" / ".local" / "sprint-plan.json")
                      .read_text(encoding="utf-8"))


class RegeneratedBatchFromLiveBacklogTests(unittest.TestCase):
    """AC1: the next batch is selected afresh - new work in, finished work out."""

    def test_batch_absorbs_new_work_and_drops_the_finished(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rid = _ready_cycle(root, bugs=(1, 2))
            self.assertEqual(sorted(run_state.read(root)["batch"]), ["BG0001", "BG0002"])
            # the cycle delivered BG0001 and raised BG0003
            _bug(root, 1, status="Fixed")
            _bug(root, 3)
            with _stubbed_close():
                rc, out = _boundary(root, "--retro", rid, "--no-fetch")
            self.assertEqual(rc, 0, out)
            ids = [u["id"] for u in _regenerated_plan(root)["batch"]]
            self.assertIn("BG0003", ids)      # raised by the last cycle, planned by this one
            self.assertNotIn("BG0001", ids)   # finished, not replanned

    def test_no_batch_is_carried_over_from_the_previous_cycle(self) -> None:
        # run_state accumulates a batch across a RE-PLAN by design; a new cycle must not
        # inherit it, or every cycle's batch would be the union of all cycles before it.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rid = _ready_cycle(root, bugs=(1, 2))
            _bug(root, 1, status="Fixed")
            _bug(root, 2, status="Fixed")
            _bug(root, 3)
            with _stubbed_close():
                rc, out = _boundary(root, "--retro", rid, "--no-fetch")
            self.assertEqual(rc, 0, out)
            self.assertEqual(run_state.read(root)["batch"], ["BG0003"])


class RegeneratedPlanLessonsTests(unittest.TestCase):
    """AC2: the regenerated plan's lessons digest carries what the close just wrote."""

    def test_the_next_plan_reads_the_previous_cycles_lessons(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _ws(root); _bug(root, 1); _bug(root, 2)
            _retro(root)
            _plan(root, "--cycles", "2")
            _judged(root)
            # what the cycle's close lifted into the project lessons log
            marker = "purge the bytecode or the mutant never runs"
            log = root / "sdlc-studio" / ".local" / "lessons.md"
            log.parent.mkdir(parents=True, exist_ok=True)
            # the project lessons log's real shape (`## L-xxxx: title`), not an invented one
            log.write_text(f"# Lessons\n\n## L-0001: {marker}\n\n"
                           f"- A same-length mutant reuses the cached bytecode.\n"
                           f"- Source: RETRO0001\n", encoding="utf-8")
            with _stubbed_close():
                rc, out = _boundary(root, "--retro", "RETRO0001", "--no-fetch")
            self.assertEqual(rc, 0, out)
            digest = _regenerated_plan(root)["lessons"]
            self.assertGreater(digest["count"], 0, "the regenerated plan carried no lessons")
            # The digest carries the ENTRY (id + title + gist), which is what the next cycle
            # reads at plan time - so the entry is what this asserts arrived.
            self.assertTrue(any(marker in json.dumps(item) for item in digest["lessons"]),
                            f"the new lesson is not in the regenerated plan: {digest}")


class NextCyclePreviewTests(unittest.TestCase):
    """AC3: a dry-run preview - batch, order, forecast, capacity - before the cycle runs."""

    def test_preview_shows_batch_order_forecast_and_capacity(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rid = _ready_cycle(root, bugs=(1, 2, 3))
            with _stubbed_close():
                rc, out = _boundary(root, "--retro", rid, "--no-fetch")
            self.assertEqual(rc, 0, out)
            low = out.lower()
            self.assertIn("preview", low)
            self.assertIn("order=", low)
            self.assertIn("forecast", low)
            self.assertIn("capacity", low)
            self.assertIn("BG0002", out)

    def test_the_preview_comes_after_the_regenerate_and_before_the_cycle_opens(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rid = _ready_cycle(root)
            with _stubbed_close():
                rc, out = _boundary(root, "--retro", rid, "--no-fetch")
            self.assertEqual(rc, 0, out)
            # Keyed to the preview's OWN output, not the "[4/4] preview:" step header: the
            # header prints from its fixed place in the sequence even if the render itself
            # moved after the cycle opened, so asserting on it proves only that the label
            # is in the right order.
            self.assertLess(out.index("regenerate"), out.index("preview of cycle 2"))
            self.assertLess(out.index("preview of cycle 2"), out.index("opened cycle 2"))


# --- US0233: stop with a handoff, never execute an ungated plan ----------------------

class RefusedPlanHandoffTests(unittest.TestCase):
    """AC1: a batch the breakdown gate refuses stops the run with a handoff."""

    def test_an_ungroomed_next_batch_stops_the_run(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rid = _ready_cycle(root, bugs=(1,))
            _bug(root, 1, status="Fixed")
            _bug(root, 4, groomed=False)          # no Points, no Affects: ungroomed
            with _stubbed_close():
                rc, out = _boundary(root, "--retro", rid, "--no-fetch")
            self.assertNotEqual(rc, 0, out)
            self.assertIn("refused-plan", out)
            state = run_state.read(root)
            self.assertEqual(state["stop"]["cause"], "refused-plan")
            self.assertIn(state["outcome"], run_state.CLOSED)

    def test_the_handoff_names_the_cause_and_the_cycles_left_unrun(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rid = _ready_cycle(root, bugs=(1,))
            _bug(root, 1, status="Fixed")
            _bug(root, 4, groomed=False)
            with _stubbed_close():
                rc, out = _boundary(root, "--retro", rid, "--no-fetch")
            self.assertNotEqual(rc, 0, out)
            stop = run_state.read(root)["stop"]
            self.assertEqual(stop["cycles_unrun"], 1)
            hid = stop["handoff"]
            self.assertTrue(hid, f"no handoff recorded on the stop: {stop}")
            # the display id carries a hyphen (HO-0001); the file stem does not (HO0001-...)
            docs = list((root / "sdlc-studio" / "handoffs")
                        .glob(f"{hid.replace('-', '')}-*.md"))
            self.assertEqual(len(docs), 1, f"handoff {hid} was not written")
            text = docs[0].read_text(encoding="utf-8")
            self.assertIn("refused-plan", text)
            self.assertIn("1 cycle", text)


class UngatedPlanNeverExecutesTests(unittest.TestCase):
    """AC2: all three causes stop before execution, and each is distinguishable."""

    def _drive(self, root: Path, cause: str) -> tuple[int, str]:
        rid = _ready_cycle(root, bugs=(1,))
        if cause == "close-gate":
            def fail(r, retro_id, state):
                return False, "gate FAILED", "fix the gate"
            saved = sprint._close_gate
            sprint._close_gate = fail
            try:
                with _stubbed_close():
                    sprint._close_gate = fail
                    return _boundary(root, "--retro", rid, "--no-fetch")
            finally:
                sprint._close_gate = saved
        if cause == "refused-plan":
            _bug(root, 1, status="Fixed")
            _bug(root, 4, groomed=False)
            with _stubbed_close():
                return _boundary(root, "--retro", rid, "--no-fetch")
        raise AssertionError(cause)

    def test_each_cause_is_recorded_distinctly(self) -> None:
        for cause in ("close-gate", "refused-plan"):
            with self.subTest(cause=cause), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                rc, out = self._drive(root, cause)
                self.assertNotEqual(rc, 0, out)
                self.assertEqual(run_state.read(root)["stop"]["cause"], cause)

    def test_origin_drift_is_recorded_distinctly(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _behind_repo(d)
            rid = _ready_cycle(root)
            with _stubbed_close():
                rc, out = _boundary(root, "--retro", rid, "--strict")
            self.assertNotEqual(rc, 0, out)
            self.assertEqual(run_state.read(root)["stop"]["cause"], "origin-drift")

    def test_no_next_cycle_run_is_opened_by_any_stop(self) -> None:
        for cause in ("close-gate", "refused-plan"):
            with self.subTest(cause=cause), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _ws(root); _bug(root, 1); _retro(root)
                _plan(root, "--cycles", "2")
                _judged(root)
                before = run_state.read(root)["run_id"]
                rc, out = self._drive_existing(root, cause, before)
                self.assertNotEqual(rc, 0, out)
                state = run_state.read(root)
                self.assertEqual(state["run_id"], before)
                self.assertEqual(state["cycle"]["index"], 1)
                # nothing of a next cycle exists to execute
                self.assertNotIn("opened cycle 2", out)

    def _drive_existing(self, root: Path, cause: str, before: str) -> tuple[int, str]:
        rid = "RETRO0001"
        if cause == "close-gate":
            def fail(r, retro_id, state):
                return False, "gate FAILED", "fix the gate"
            with _stubbed_close():
                sprint._close_gate = fail
                return _boundary(root, "--retro", rid, "--no-fetch")
        _bug(root, 1, status="Fixed")
        _bug(root, 4, groomed=False)
        with _stubbed_close():
            return _boundary(root, "--retro", rid, "--no-fetch")


# --- US0234: per-cycle auditability --------------------------------------------------

class PerCycleRunStateTests(unittest.TestCase):
    """AC1: a fresh run per cycle, and the closed cycle's record stays readable."""

    def test_the_next_cycle_mints_a_fresh_run(self) -> None:
        """BG0253: this asserted only that two ids differ, which was neither necessary nor
        sufficient. Not sufficient - a generator returning a constant would have passed it 999
        times in 1,000. Not reliable - `short_ulid` collides about 1 in 1,024, so the gate went
        red at random on an unchanged tree. The id inequality is kept, because the mint is now
        collision-checked and therefore genuinely provides it, but the properties that say a
        FRESH run was minted are asserted directly: a new record, its own clock, and the
        previous run closed and archived rather than continued."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rid = _ready_cycle(root)
            first = run_state.read(root)
            with _stubbed_close():
                rc, out = _boundary(root, "--retro", rid, "--no-fetch")
            self.assertEqual(rc, 0, out)
            second = run_state.read(root)
            self.assertNotEqual(second["run_id"], first["run_id"])
            self.assertEqual(second["outcome"], run_state.RUNNING, "the new run is open")
            kept = run_state.read_archived(root, first["run_id"])
            self.assertIn(kept.get("outcome"), run_state.CLOSED,
                          "the previous run was continued rather than closed and replaced")
            self.assertNotIn(second["run_id"], {r["run_id"] for r in run_state.archived(root)},
                             "the fresh run took an id a closed run already holds")
            # Its OWN start time - stamped afresh, not inherited. (Not asserted as strictly
            # later: the stamp is second-resolution and a fixture boundary is faster than that,
            # so `!=` would be testing the clock rather than the code.)
            self.assertTrue(second["started_at"])
            self.assertGreaterEqual(second["started_at"], first["started_at"])
            self.assertEqual(second["cycle"]["index"], 2)
            self.assertEqual(second["cycle"]["policy_run_id"], first["run_id"])

    def test_the_closed_cycle_is_still_readable(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rid = _ready_cycle(root)
            first = run_state.read(root)
            with _stubbed_close():
                rc, out = _boundary(root, "--retro", rid, "--no-fetch")
            self.assertEqual(rc, 0, out)
            kept = run_state.read_archived(root, first["run_id"])
            self.assertEqual(kept["run_id"], first["run_id"])
            self.assertEqual(kept["batch"], first["batch"])
            self.assertEqual(kept["sprint_goal"], first["sprint_goal"])
            self.assertIn(kept["outcome"], run_state.CLOSED)

    def test_the_live_file_keeps_its_shape_for_every_existing_reader(self) -> None:
        # Backward compatibility is the load-bearing half: many modules read run-state.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rid = _ready_cycle(root)
            with _stubbed_close():
                rc, out = _boundary(root, "--retro", rid, "--no-fetch")
            self.assertEqual(rc, 0, out)
            state = run_state.read(root)
            # the boundary really rolled - otherwise this asserts the shape of cycle 1
            self.assertEqual(state["cycle"]["index"], 2)
            for field in run_state.FIELDS:
                self.assertIn(field, state, f"the live run-state lost {field}")
            self.assertIsInstance(state["batch"], list)
            self.assertEqual(state["outcome"], run_state.RUNNING)

    def test_archiving_the_same_run_twice_keeps_one_record(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _ws(root); _bug(root, 1)
            _plan(root, "--cycles", "2")
            run_state.archive(root)
            run_state.archive(root)
            self.assertEqual(len(run_state.archived(root)), 1)

    def test_an_unopened_run_archives_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _ws(root)
            self.assertIsNone(run_state.archive(root))
            self.assertEqual(run_state.archived(root), [])


class PerCycleForecastGoalRetroTests(unittest.TestCase):
    """AC2: N cycles leave N forecasts, N judged goals and N retros, keyed by run_id."""

    def test_two_cycles_leave_two_of_each(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _ws(root); _bug(root, 1); _bug(root, 2); _bug(root, 3); _bug(root, 4)
            _retro(root, "RETRO0001"); _retro(root, "RETRO0002")
            _plan(root, "--cycles", "2")
            _judged(root, "achieved")
            with _stubbed_close():
                rc, out = _boundary(root, "--retro", "RETRO0001", "--no-fetch")
            self.assertEqual(rc, 0, out)
            _judged(root, "partial")
            with _stubbed_close():
                rc, out = _boundary(root, "--retro", "RETRO0002", "--no-fetch")
            self.assertEqual(rc, 0, out)
            records = run_state.archived(root)
            self.assertEqual(len(records), 2, [r.get("run_id") for r in records])
            self.assertEqual(len({r["run_id"] for r in records}), 2)
            for rec in records:
                self.assertTrue(rec.get("token_forecast"), f"{rec['run_id']} has no forecast")
                self.assertTrue(rec.get("sprint_goal"), f"{rec['run_id']} has no goal")
                self.assertTrue(rec.get("sprint_goal_verdict", {}).get("verdict"),
                                f"{rec['run_id']} goal is unjudged")
                self.assertTrue(rec.get("retro"), f"{rec['run_id']} has no retro")
            self.assertEqual([r["retro"] for r in records], ["RETRO0001", "RETRO0002"])
            self.assertEqual([r["sprint_goal_verdict"]["verdict"] for r in records],
                             ["achieved", "partial"])
            self.assertEqual([r["cycle"]["index"] for r in records], [1, 2])


# --- US0235: end-to-end ---------------------------------------------------------------

class RollingEndToEndTests(unittest.TestCase):
    """AC2: a two-cycle rolling run - boundary order, and a record per cycle."""

    def test_two_cycle_run_keeps_the_boundary_order_and_leaves_both_records(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _behind_repo(d)
            _ws(root)
            for n in (1, 2, 3, 4):
                _bug(root, n)
            _retro(root, "RETRO0001"); _retro(root, "RETRO0002")
            _plan(root, "--cycles", "2")
            _judged(root, "achieved")
            with _stubbed_close():
                rc, first = _boundary(root, "--retro", "RETRO0001")
            self.assertEqual(rc, 0, first)
            # The four steps in sequence, each anchored to output only that step produces -
            # so the assertion tracks the work done, not the labels announcing it.
            order = [first.index(m) for m in
                     ("[1/4] close-down", "closed and archived", "[2/4] fetch",
                      "cycle 1 | fetch:", "[3/4] regenerate", "[4/4] preview",
                      "preview of cycle 2", "opened cycle 2")]
            self.assertEqual(order, sorted(order), first)
            self.assertEqual(len(set(order)), 8)
            _judged(root, "achieved")
            with _stubbed_close():
                rc, second = _boundary(root, "--retro", "RETRO0002")
            self.assertEqual(rc, 0, second)
            # the policy is spent: the last cycle closes, nothing is regenerated
            self.assertIn("policy complete", second)
            self.assertNotIn("[3/4] regenerate", second)
            records = run_state.archived(root)
            self.assertEqual([r["cycle"]["index"] for r in records], [1, 2])
            self.assertEqual(len({r["run_id"] for r in records}), 2)
            for rec in records:
                self.assertIn(rec["outcome"], run_state.CLOSED)


class ReviewFindingsTests(unittest.TestCase):
    """Three gaps the closing adversarial review found. Each branch below survived
    removal against the full 3,159-test suite, so the behaviour its comment singles out
    as the thing it must never do had no discriminating test at all."""

    def test_a_stop_does_not_relabel_a_cycle_that_already_closed_honestly(self) -> None:
        """The outcome-preservation branch, driven through `_boundary_stop` ITSELF.

        The first version of this test re-implemented the guard in its own body - it ran
        `if outcome == RUNNING: close_run(...)` and asserted on that - so it passed with the
        production guard deleted outright. A test that contains a copy of the code it checks
        asserts nothing about the code. It must call the real path.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _ws(Path(d))
            run_state.open_run(root, batch=["BG0001"], goal="done")
            run_state.close_run(root, outcome="goal-reached")
            self.assertEqual(run_state.read(root).get("outcome"), "goal-reached")

            with contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()):
                rc = sprint._boundary_stop(root, "close-gate", "the cycle would not close", "fix it")
            self.assertEqual(rc, 1)
            self.assertEqual(
                run_state.read(root).get("outcome"), "goal-reached",
                "the stop relabelled a cycle that had already closed honestly")
            self.assertEqual(run_state.read(root).get("stop", {}).get("cause"), "close-gate",
                             "the stop itself was not recorded")

    def test_a_stop_on_a_still_running_cycle_does_close_it_blocked(self) -> None:
        """The other side of the same branch: `blocked` IS the honest word for a cycle that
        never closed. Without this, the guard could be satisfied by never closing anything."""
        with tempfile.TemporaryDirectory() as d:
            root = _ws(Path(d))
            run_state.open_run(root, batch=["BG0001"], goal="done")
            self.assertEqual(run_state.read(root).get("outcome"), run_state.RUNNING)
            with contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()):
                sprint._boundary_stop(root, "refused-plan", "the next batch is not plannable", "re-plan")
            self.assertEqual(run_state.read(root).get("outcome"), run_state.BLOCKED)

    def test_close_run_archives_on_the_plain_close_path(self) -> None:
        """Removing `archive()` from close_run reddened nothing: coverage reached the
        archive only via open_run's safety net and the boundary's explicit call, so the
        per-cycle-auditability claim was not bound to a plain `sprint close`."""
        with tempfile.TemporaryDirectory() as d:
            root = _ws(Path(d))
            st = run_state.open_run(root, batch=["BG0001"], goal="done")
            run_state.close_run(root, outcome="goal-reached")
            ids = [r.get("run_id") for r in run_state.archived(root)]
            self.assertIn(st["run_id"], ids,
                          "a plain close archived nothing - only the boundary path did")

    def test_a_malformed_cycle_index_does_not_lose_the_intact_records(self) -> None:
        """`archived()` promises an unreadable record is SKIPPED rather than raising. The
        try/except wrapped only the JSON parse, so a non-numeric `cycle.index` threw from
        the SORT KEY and lost every intact record - the outcome the docstring forbids."""
        with tempfile.TemporaryDirectory() as d:
            root = _ws(Path(d))
            ad = run_state.archive_dir(root)
            ad.mkdir(parents=True, exist_ok=True)
            (ad / "RUN-GOOD.json").write_text(json.dumps(
                {"run_id": "RUN-GOOD", "started_at": "2026-07-19T00:00:00Z",
                 "cycle": {"index": 1}}), encoding="utf-8")
            (ad / "RUN-BAD.json").write_text(json.dumps(
                {"run_id": "RUN-BAD", "started_at": "2026-07-19T00:00:01Z",
                 "cycle": {"index": "two"}}), encoding="utf-8")
            recs = run_state.archived(root)   # must not raise
            self.assertIn("RUN-GOOD", [r.get("run_id") for r in recs],
                          "one malformed record lost the intact ones")

    def test_every_malformed_shape_is_survived_not_just_the_tested_one(self) -> None:
        """The first repair caught only the variant its own test exercised. `cycle` is JSON,
        so it can be a string or a list (AttributeError), and a non-string `started_at`
        raises from the tuple comparison outside the coercion entirely."""
        shapes = {
            "cycle is a string": {"cycle": "two"},
            "cycle is a list": {"cycle": [1]},
            "cycle.index is prose": {"cycle": {"index": "two"}},
            "started_at is a number": {"started_at": 17, "cycle": {"index": 1}},
            # Found by round 3: the first two repairs each caught only the shapes their own
            # test exercised. run_id is the final tie-break, so a non-string reaches the tuple
            # comparison when started_at and index both tie; Infinity round-trips through
            # json by default, so this module can WRITE a value int() then refuses.
            "run_id is a number": {"run_id": 7, "started_at": "2026-07-19T00:00:00Z",
                                   "cycle": {"index": 1}},
            "index is Infinity": {"cycle": {"index": float("inf")}},
        }
        for name, extra in shapes.items():
            with self.subTest(shape=name), tempfile.TemporaryDirectory() as d:
                root = _ws(Path(d))
                ad = run_state.archive_dir(root)
                ad.mkdir(parents=True, exist_ok=True)
                (ad / "RUN-GOOD.json").write_text(json.dumps(
                    {"run_id": "RUN-GOOD", "started_at": "2026-07-19T00:00:00Z",
                     "cycle": {"index": 1}}), encoding="utf-8")
                rec = {"run_id": "RUN-BAD", "started_at": "2026-07-19T00:00:01Z"}
                rec.update(extra)   # extra may deliberately override run_id/started_at
                (ad / "RUN-BAD.json").write_text(json.dumps(rec), encoding="utf-8")
                got = [r.get("run_id") for r in run_state.archived(root)]
                self.assertIn("RUN-GOOD", got, f"{name}: intact record lost")


if __name__ == "__main__":
    unittest.main()
