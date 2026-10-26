"""US1095: the close compares the run's priced cost per point with the median of recent runs, or a
configured baseline until three exist, and carries a run over 1.5 times it as a known issue with
a per-unit breakdown, whose cause the retro must name.

A cost regression used to be found runs after the run that caused it. Pinned here, through the
shipped entry points in throwaway trees whose meter reads fixture harness transcripts: the close
records one `cost` known issue for a run over 1.5 x the trailing median (strictly over, an
absent Priced/pt cell never read as 0, the run's own row never in its baseline), the retro then
owes a `## Cost` cause, the plan prints the budget beside the token forecast, a configured
baseline stands in below three priced runs, past runs are seeded into COST-BASELINE.md without
touching VELOCITY.md, and an answered cost issue stops neither `sign` nor `boundary`.

Run from the repo root:
    pytest .claude/skills/sdlc-studio/scripts/tests/test_close_cost_regression.py
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
import unittest.mock
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_meter_reads_true as meter  # noqa: E402 - the harness transcript fixture, shared

#: The units, each with its Points: four gate-cleared points in all.
UNITS = {"US0101": 2, "US0102": 1, "US0103": 1}
RETRO = "RETRO0007"
#: US0101's work and US0102's (a subagent's): 3,000,000 priced each, 1,200,000 counted. The
#: cache reads are most of the price and none of the count, so priced and counted tell apart.
WORK = meter._usage(1_000_000, 200_000, 0, 0, 10_000_000)
#: The orchestrator's spend between the units, in no span: 400,000 priced.
ORCHESTRATE = meter._usage(200_000, 20_000, 0, 0, 1_000_000)
SOURCE = "harness (main thread and subagents, once per message)"
HEADER = ("| Retro | Date | Units | Measured | Forecast | Points | Actual (tokens) | Model | Source "
          "| Priced/pt |\n| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n")
#: Median 1,000,000, mean 1,360,000. The run's own row is newest: counted, it displaces
#: RETRO0001 and the median moves to 1,100,000.
AC1_ROWS = {"RETRO0001": "800,000", "RETRO0002": "3,000,000", "RETRO0003": "900,000",
            "RETRO0004": "1,000,000", "RETRO0005": "1,100,000", "RETRO0006": "-",
            RETRO: "1,600,000"}
#: Median 1,000,000. Read as 0, the absent RETRO0006 displaces RETRO0001 and the median falls to
#: 900,000.
AC2_ROWS = {"RETRO0001": "3,000,000", "RETRO0002": "800,000", "RETRO0003": "900,000",
            "RETRO0004": "1,000,000", "RETRO0005": "1,100,000", "RETRO0006": "-"}
#: Two priced runs: their median, 1,000,000, would flag the run at 1.6 x.
TWO_ROWS = {"RETRO0001": "1,000,000", "RETRO0002": "1,000,000"}
#: Five priced runs whose median, 2,000,000, holds a 1.6M run within bounds.
CHEAP_ROWS = {f"RETRO000{n}": "2,000,000" for n in range(1, 6)}
COST_BULLET = "- the review rounds re-read the whole diff on every turn\n"

RETRO_TEXT = (
    "# RETRO-0007: cost\n\n> **Date:** 2026-10-20\n> **Batch:** US0101, US0102, US0103\n\n"
    "## Delivered\n\n- US0101, US0102 and US0103 shipped\n\n"
    "## What went well\n\n- the meter read every transcript\n\n"
    "## What was hard / what stalled\n\n- the review rounds ran long\n\n"
    "## Lessons\n\n- a fresh context per review is cheaper\n\n"
    "## Actions raised\n\n| Finding | Disposition |\n| --- | --- |\n"
    "| nothing of note | declined: nothing to raise |\n")


def _out(fn, *args, **kw) -> tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        rc = fn(*args, **kw)
    return rc, buf.getvalue()


@contextlib.contextmanager
def _chain_green(mod, real=("retro-validate",)):
    """Every close-chain step but `real` stubbed green, and the report holds cleared."""
    with contextlib.ExitStack() as stack:
        stack.enter_context(unittest.mock.patch.object(mod, "_report_holds", lambda *a, **k: []))
        for name in mod._CLOSE_CHAIN:
            if name not in real:
                stack.enter_context(unittest.mock.patch.object(
                    mod, "_close_" + name.replace("-", "_"),
                    lambda *a, _n=name, **k: (True, f"{_n} ok", "")))
        yield


class _Case(unittest.TestCase):
    """A tree per call: three Review stories whose gates clear, a retro over them, VELOCITY.md,
    and an open run whose meter reads fixture transcripts. US0101 spans its own work, the
    orchestrator spends between the units, US0102's span is left open for the close to settle,
    and US0103 never enters In Progress."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        self.rs = meter._live("lib.run_state")
        self.sprint, self.retro = meter._live("sprint"), meter._live("retro")
        self.n = 0

    def tree(self, rows: dict, *, orchestrate: bool = True, cost: str = "",
             config: str = "") -> Path:
        self.n += 1
        root = self.tmp / f"t{self.n}" / "repo"
        tx = meter._Transcripts(self.tmp / f"t{self.n}" / "transcripts")
        env = unittest.mock.patch.dict(os.environ, {self.rs.TRANSCRIPTS_ENV: str(tx.dir)})
        env.start()
        self.addCleanup(env.stop)
        stories, local = root / "sdlc-studio" / "stories", root / "sdlc-studio" / ".local"
        stories.mkdir(parents=True)
        local.mkdir(parents=True)
        report = {"stories": {}}
        for uid, pts in UNITS.items():
            (stories / f"{uid}-a.md").write_text(
                f"# {uid}: a\n\n> **Status:** Review\n> **Points:** {pts}\n> **Epic:** EP0001\n\n"
                "## Acceptance Criteria\n\n### AC1: it behaves\n\n- **Verify:** shell true\n",
                encoding="utf-8")
            report["stories"][f"{uid}-a"] = {"failed": 0, "stale": 0, "failures": [],
                                             "ac_count": 1,
                                             "verified_at": "2099-01-01T00:00:00Z"}
        (local / "verify-report.json").write_text(json.dumps(report), encoding="utf-8")
        reviews = root / "sdlc-studio" / "reviews"
        reviews.mkdir(parents=True)
        (reviews / "sprint-review-record.md").write_text(
            "# Sprint-level Reviews\n\n| Base | Reviewer | Author | Verdict | Date | Units | "
            "Findings |\n| --- | --- | --- | --- | --- | --- | --- |\n| - | qa-seat | Claude Opus 5 "
            f"| APPROVE | 2026-09-20 | {' '.join(UNITS)} | none blocking |\n", encoding="utf-8")
        retros = root / "sdlc-studio" / "retros"
        retros.mkdir(parents=True)
        (retros / f"{RETRO}-cost.md").write_text(RETRO_TEXT + cost, encoding="utf-8")
        (retros / "_index.md").write_text(
            "# Retro Registry\n\n| ID | Title | Date |\n| --- | --- | --- |\n"
            f"| [RETRO-0007]({RETRO}-cost.md) | cost | 2026-10-20 |\n", encoding="utf-8")
        (retros / "VELOCITY.md").write_text(
            "# Velocity history\n\n" + HEADER + "".join(
                f"| {rid} | 2026-10-0{rid[-1]} | 2 | 0 | 0 | 10 | 4,000,000 | {meter.MODEL} | "
                f"{SOURCE} | {priced} |\n" for rid, priced in rows.items()), encoding="utf-8")
        if config:
            (root / "sdlc-studio" / ".config.yaml").write_text(config, encoding="utf-8")
        tx.main_says("msg_before", meter.MAIN_1)
        self.rs.open_run(root, batch=list(UNITS), goal="done")
        self.rs.update(root, sprint_goal="the run costs what its work costs")
        self.rs.record_unit_actual(root, "US0101", "In Progress", False)
        tx.main_says("msg_us0101", WORK)
        self.rs.record_unit_actual(root, "US0101", "Review", True)
        if orchestrate:
            tx.main_says("msg_orchestrate", ORCHESTRATE)
        self.rs.record_unit_actual(root, "US0102", "In Progress", False)
        tx.agent_says("b1", "msg_us0102", WORK)
        return root

    def close(self, root: Path, real=("retro-validate",)) -> tuple[int, str]:
        with _chain_green(self.sprint, real):
            return _out(self.sprint.main, ["close", "--retro", RETRO, "--goal-verdict",
                                           "achieved", "--note", "the batch shipped",
                                           "--root", str(root)])

    def issues(self, root: Path, source: str = "cost") -> list[dict]:
        return [g for g in self.rs.read(root).get(self.rs.CLOSE_KNOWN_ISSUES) or []
                if g.get("source") == source]

    def validate(self, root: Path) -> tuple[int, str]:
        return _out(self.retro.main, ["--root", str(root), "validate", "--id", RETRO])

    def set_cost(self, root: Path, cost: str) -> None:
        (root / "sdlc-studio" / "retros" / f"{RETRO}-cost.md").write_text(
            RETRO_TEXT + cost, encoding="utf-8")


class CloseCostRegressionTests(_Case):
    def test_a_run_over_one_and_a_half_times_the_median_is_a_known_issue(self) -> None:
        """AC1. MUTANTS: the close refusing over the issue; the counted tokens (655,000 per point)
        compared in place of the priced (1,600,000); the mean of the five (1,360,000) for their
        median; the run's own VELOCITY row in its own baseline (median 1,100,000, ratio 1.45);
        a unit with no span given a figure or dropped; the remainder left out."""
        root = self.tree(AC1_ROWS, cost="\n## Cost\n\n" + COST_BULLET)
        rc, out = self.close(root)
        self.assertEqual(0, rc, out)
        cost = self.issues(root)
        self.assertEqual(1, len(cost), out)
        issue = cost[0]
        self.assertEqual(RETRO, issue["retro"])
        self.assertEqual(1_600_000, issue["per_point"])
        self.assertEqual(1_000_000, issue["baseline"])
        self.assertEqual(1.6, issue["ratio"])
        self.assertEqual(["RETRO0001", "RETRO0002", "RETRO0003", "RETRO0004", "RETRO0005"],
                         issue["retros"])
        self.assertEqual({"US0101": 3_000_000, "US0102": 3_000_000, "US0103": None},
                         issue["units"])
        self.assertEqual(400_000, issue["remainder"])
        detail = issue["detail"]
        for text in ("1,600,000", "1,000,000", "1.60 x", "RETRO0001, RETRO0002, RETRO0003, "
                     "RETRO0004, RETRO0005", "US0101 3,000,000", "US0102 3,000,000",
                     "US0103 NOT MEASURED", "unattributed remainder 400,000"):
            self.assertIn(text, detail)
        # Filed as any other known issue is: the report's known-issues section carries it.
        report = self.rs.read(root).get("report")
        self.assertTrue(report, out)
        page = json.loads((root / "sdlc-studio" / "reports" / f"{report}.json").read_text())
        rows = next(s for s in page["sections"] if s["key"] == "known_issues")["rows"]
        self.assertIn(detail, [r["issue_detail"]["value"] for r in rows
                               if r["issue_id"]["value"] == "cost"])
        self.assertIn("sign it with: sprint.py sign", out)

    def test_the_boundary_and_an_absent_cell_record_no_issue(self) -> None:
        """AC2. MUTANTS: `>=` for `>` (the run is exactly 1.5 x: 6,000,000 over 4 points against
        1,000,000); an absent Priced/pt cell read as 0 (it displaces RETRO0001 and the median
        falls to 900,000, so the run reads 1.67 x)."""
        root = self.tree(AC2_ROWS, orchestrate=False)
        rc, out = self.close(root)
        self.assertEqual(0, rc, out)
        self.assertEqual([], self.issues(root), out)
        self.assertIn("1,500,000 priced input-equivalent tokens per gate-cleared point", out)
        self.assertIn("1.50 x the baseline 1,000,000 per point, the median of the 5 most recent "
                      "priced runs (RETRO0001, RETRO0002, RETRO0003, RETRO0004, RETRO0005): "
                      "within 1.5 x", out)


class RetroCostCauseTests(_Case):
    def test_the_retro_must_name_the_cause_of_a_flagged_run(self) -> None:
        """AC3. MUTANTS: the section demanded of every retro (the in-bounds run's retro, the
        same text, is refused); a `{{placeholder}}` bullet accepted; the demand read from the
        retro's text rather than the run's recorded issue (two runs, one retro text, two
        verdicts)."""
        root = self.tree(AC1_ROWS)
        rc, out = self.close(root)
        self.assertEqual(0, rc, out)
        self.assertEqual(1, len(self.issues(root)), out)
        # The close's own validate step read this close's issue, not a stale record.
        self.assertTrue(any("'## Cost'" in g["detail"] for g in self.issues(root, "retro-validate")),
                        out)
        rc, said = self.validate(root)
        self.assertEqual(1, rc, said)
        self.assertIn("'## Cost' must name the cause", said)
        self.set_cost(root, "\n## Cost\n\n- {{the cause}}\n")
        rc, said = self.validate(root)
        self.assertEqual(1, rc, said)
        self.assertIn("'## Cost' must name the cause", said)
        self.set_cost(root, "\n## Cost\n\n" + COST_BULLET)
        rc, said = self.validate(root)
        self.assertEqual(0, rc, said)

        within = self.tree(CHEAP_ROWS)
        rc, out = self.close(within)
        self.assertEqual(0, rc, out)
        self.assertEqual([], self.issues(within), out)
        rc, said = self.validate(within)
        self.assertEqual(0, rc, said)
        self.assertNotIn("## Cost", said)


class PlanBudgetTests(_Case):
    def plan(self, root: Path) -> tuple[int, str]:
        for n in (1, 2):
            (root / "src").mkdir(exist_ok=True)
            (root / "src" / f"bg{n}.py").write_text("", encoding="utf-8")
            bugs = root / "sdlc-studio" / "bugs"
            bugs.mkdir(parents=True, exist_ok=True)
            (bugs / f"BG000{n}-x.md").write_text(
                f"# BG000{n}: b\n\n> **Status:** Open\n> **Severity:** Medium\n"
                f"> **Affects:** src/bg{n}.py\n> **Points:** 2\n\n## Acceptance Criteria\n\n"
                "### AC1: it behaves\n\n- **Verify:** shell true\n", encoding="utf-8")
        with unittest.mock.patch.object(sys, "stdin", io.StringIO("")):
            return _out(self.sprint.main, ["plan", "--bugs", "Open", "--no-fetch",
                                           "--sprint-goal", "every open bug is fixed",
                                           "--root", str(root)])

    def test_the_plan_prints_the_budget_and_its_basis(self) -> None:
        """AC4. MUTANTS: the budget priced from the forecast's tokens-per-point rate (400,000
        here, a different basis); a budget printed with no M or no rows beside it; the
        configured baseline used without being named."""
        root = self.tree(AC2_ROWS)
        rc, out = self.plan(root)
        self.assertEqual(0, rc, out)
        lines = out.splitlines()
        at = next(i for i, ln in enumerate(lines) if "cost budget:" in ln)
        self.assertLess(next(i for i, ln in enumerate(lines) if "token forecast:" in ln), at)
        self.assertEqual("  cost budget: 6,000,000 priced input-equivalent tokens = 4 point(s) x "
                         "1.5 x 1,000,000 per point", lines[at])
        self.assertIn("the median of the 5 most recent priced runs (RETRO0001, RETRO0002, "
                      "RETRO0003, RETRO0004, RETRO0005)", lines[at + 1])

        few = self.tree(TWO_ROWS)
        rc, out = self.plan(few)
        self.assertEqual(0, rc, out)
        shipped = meter._live("config").get(few, "cost.baseline_per_point")
        self.assertIn(f"= 4 point(s) x 1.5 x {shipped:,} per point", out)
        self.assertIn("the configured baseline `cost.baseline_per_point` (2 priced run(s), and 3 "
                      "are needed for a median)", out)


class CloseCostBaselineTests(_Case):
    def test_fewer_than_three_runs_use_the_configured_baseline(self) -> None:
        """AC5. MUTANTS: the baseline typed in the code beside the config file (the shipped
        figure is read from config-defaults.yaml, a project's figure from its .config.yaml, and
        defaults lacking the key leave it unconfigured); a median over two rows (it would flag
        the run at 1.6 x); the baseline used without being named; `off` still comparing."""
        import yaml  # noqa: PLC0415 - the config's own reader, as the loader uses it
        config = meter._live("config")
        shipped = yaml.safe_load(config.DEFAULTS_PATH.read_text(encoding="utf-8"))["cost"][
            "baseline_per_point"]
        # This repository's own measure: two of its runs, priced at about 2.0M and 3.0M.
        self.assertTrue(isinstance(shipped, int) and 2_000_000 <= shipped <= 3_000_000, shipped)

        root = self.tree(TWO_ROWS)
        rc, out = self.close(root)
        self.assertEqual(0, rc, out)
        self.assertEqual([], self.issues(root), out)
        self.assertIn(f"the baseline {shipped:,} per point, the configured baseline "
                      f"`cost.baseline_per_point` (2 priced run(s), and 3 are needed for a "
                      f"median)", out)

        project = self.tree(TWO_ROWS, cost="\n## Cost\n\n" + COST_BULLET,
                            config="cost:\n  baseline_per_point: 1000000\n")
        rc, out = self.close(project)
        self.assertEqual(0, rc, out)
        issue = self.issues(project)[0]
        self.assertEqual((1_000_000, "configured", 1.6),
                         (issue["baseline"], issue["baseline_kind"], issue["ratio"]))
        self.assertIn("the configured baseline `cost.baseline_per_point`", issue["detail"])

        bare = self.tmp / "defaults-without-cost.yaml"
        bare.write_text("sprint:\n  breakdown: enforce\n", encoding="utf-8")
        real = config.load_config
        unconfigured = self.tree(TWO_ROWS)
        with unittest.mock.patch.object(config, "load_config",
                                        lambda root, defaults_path=None: real(root, bare)):
            rc, out = self.close(unconfigured)
        self.assertEqual(0, rc, out)
        self.assertEqual([], self.issues(unconfigured), out)
        self.assertIn("UNMEASURED - 2 priced run(s), and 3 are needed for a median; no "
                      "`cost.baseline_per_point` is configured", out)

        off = self.tree(TWO_ROWS, config="cost:\n  baseline_per_point: off\n")
        rc, out = self.close(off)
        self.assertEqual(0, rc, out)
        self.assertEqual([], self.issues(off), out)
        self.assertIn("against its baseline UNMEASURED - 2 priced run(s), and 3 are needed for a "
                      "median; `cost.baseline_per_point` is off", out)


class CostBaselineSeedTests(_Case):
    def test_a_seeded_run_joins_the_median_and_velocity_is_untouched(self) -> None:
        """AC6. MUTANTS: a VELOCITY row rewritten; the window priced by a second loop summing
        records (each message is three records here, so it triples) rather than the meter's
        once-per-message read; a record outside the window counted; an empty window written as
        0; baseline rows left out of the median (two VELOCITY rows alone use the configured
        baseline)."""
        root = self.tree(TWO_ROWS)
        tx = meter._Transcripts(self.tmp / "past")
        os.environ[self.rs.TRANSCRIPTS_ENV] = str(tx.dir)
        t0 = meter.T0
        tx.main_says("past_before", meter.MAIN_1, at=t0)
        tx.main_says("past_in", meter.MAIN_2, at=t0 + timedelta(hours=2))
        tx.agent_says("p1", "past_agent", meter.AGENT_A, at=t0 + timedelta(hours=3))
        tx.main_says("past_after", WORK, at=t0 + timedelta(hours=9))
        (root / "sdlc-studio" / "stories" / "US0201-p.md").write_text(
            "# US0201: p\n\n> **Status:** Done\n> **Points:** 5\n", encoding="utf-8")
        (root / "sdlc-studio" / "retros" / "RETRO0003-past.md").write_text(
            "# RETRO-0003: past\n\n> **Batch:** US0201\n", encoding="utf-8")
        velocity = (root / "sdlc-studio" / "retros" / "VELOCITY.md").read_bytes()
        baseline = root / "sdlc-studio" / "retros" / "COST-BASELINE.md"

        def add(since, until) -> tuple[int, str]:
            return _out(self.retro.main, ["--root", str(root), "cost-baseline", "add",
                                          "--retro", "RETRO0003", "--since", meter._iso(since),
                                          "--until", meter._iso(until)])

        rc, said = add(t0 + timedelta(hours=4), t0 + timedelta(hours=8))
        self.assertEqual(1, rc, said)
        self.assertIn("no transcript record", said)
        self.assertFalse(baseline.exists(), "an empty window was written")

        rc, said = add(t0 + timedelta(hours=1), t0 + timedelta(hours=4))
        self.assertEqual(0, rc, said)
        priced = meter._priced(meter._sum(meter.MAIN_2, meter.AGENT_A))
        rows = [ln for ln in baseline.read_text(encoding="utf-8").splitlines()
                if ln.startswith("| RETRO0003 |")]
        self.assertEqual(1, len(rows), baseline.read_text(encoding="utf-8"))
        cells = [c.strip() for c in rows[0].strip("|").split("|")]
        self.assertEqual(["RETRO0003", "2026-10-02T10:00:00Z to 2026-10-02T13:00:00Z", "5",
                          f"{priced:,}", f"{round(priced / 5):,}",
                          "input 1, output 5, cache write 5m 1.25, cache write 1h 2.0, "
                          "cache read 0.1"], cells[:6])
        self.assertEqual(velocity, (root / "sdlc-studio" / "retros" / "VELOCITY.md").read_bytes())

        rc, said = add(t0 + timedelta(hours=1), t0 + timedelta(hours=4))
        self.assertEqual(1, rc, said)
        self.assertEqual(1, baseline.read_text(encoding="utf-8").count("| RETRO0003 |"))

        rc, out = PlanBudgetTests.plan(self, root)
        self.assertEqual(0, rc, out)
        self.assertIn("the median of the 3 most recent priced runs (RETRO0001, RETRO0002, "
                      "RETRO0003)", out)


class CostIssueHandOverTests(_Case):
    def test_a_named_cause_stops_neither_sign_nor_boundary(self) -> None:
        """The close hands the issue over and the run is signed. MUTANTS: `boundary` halting on
        every close known issue (the answered run stops); the filter waving through a cost issue
        whose retro names no cause (the run whose retro lost its cause rolls on); `sign` refusing
        a known issue."""
        named = self.tree(AC1_ROWS, cost="\n## Cost\n\n" + COST_BULLET)
        rc, out = self.close(named)
        self.assertEqual(0, rc, out)
        self.assertEqual(["cost"], [g["source"] for g in
                                    self.rs.read(named).get(self.rs.CLOSE_KNOWN_ISSUES)])
        rc, said = _out(self.sprint.main, ["sign", "--principal", "Darren Benson", "--author",
                                           "Claude Opus 5", "--root", str(named)])
        self.assertEqual(0, rc, said)
        self.assertTrue(self.rs.read(named).get("signature"), said)

        # Both runs close with the cause named, so the cost issue is their only known issue;
        # the second retro then loses its `## Cost` section before the boundary reads it.
        for stops in (False, True):
            root = self.tree(AC1_ROWS, cost="\n## Cost\n\n" + COST_BULLET)
            rc, out = self.close(root)
            self.assertEqual(0, rc, out)
            self.assertEqual(["cost"], [g["source"] for g in
                                        self.rs.read(root).get(self.rs.CLOSE_KNOWN_ISSUES)])
            if stops:
                self.set_cost(root, "")
            self.rs.update(root, cycle={"index": 1, "remaining": 1}, policy={
                "cycles": 2, "sprint_goal": "the run costs what its work costs", "goal": "done",
                "order": "priority", "capacity": {"minutes": 240, "units": 8},
                "queries": [{"kind": "bug", "status": "Open"}], "epics": None,
                "stop_conditions": list(self.sprint.STOP_CAUSES), "skip_personas": False,
                "recorded_at": "2026-10-20T00:00:00Z"})
            with unittest.mock.patch.object(self.sprint, "_boundary_close_down",
                                            lambda *a, **k: (0, "")):
                rc, said = _out(self.sprint.main, ["boundary", "--retro", RETRO, "--no-fetch",
                                                   "--root", str(root)])
            self.assertEqual(stops, "known issue(s)" in said, said)
            self.assertEqual(not stops, "cycle 1 closed and archived" in said, said)


if __name__ == "__main__":
    unittest.main()
