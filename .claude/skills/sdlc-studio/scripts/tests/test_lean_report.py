"""US0875: the sprint report is one page answering three questions, with an appendix.

The front page answers: how accurate were the estimates, did we deliver to plan, and what known
issues are handed over - between the goal and the sign line. Everything else is appendix.

The fixture run is built so each question has a figure a wrong deriver would get wrong: a unit
resized from 3 to 8 points after the plan, a drop and an add each with a reason, a unit carried
undelivered, findings raised inside and outside the run window, and a fixed finding.
"""
from __future__ import annotations

import contextlib
import importlib
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


class _AtTestTime:
    """`sprint_report`, imported when a test first uses it rather than at discovery. A sibling
    module replaces `sys.modules["retro"]` while the suite is being discovered, so importing
    `sprint_report` here, earlier in discovery order, would bind it to a `retro` that later
    modules no longer see, and their patches of `retro` would miss it."""

    def __getattr__(self, name):
        return getattr(importlib.import_module("sprint_report"), name)


sr = _AtTestTime()

RUN = "RUN-01LEANREP"
RETRO = "RETRO0001"
FRONT = ["Goal", "Estimates", "Delivered to plan", "Known issues handed over", "Sign-off"]
MODEL = "lean-model-7"


def _unit(root: Path, uid: str, points: int, status: str) -> None:
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{uid}-a-unit.md").write_text(
        f"# {uid}: a unit\n\n> **Status:** {status}\n> **Points:** {points}\n", encoding="utf-8")


def _finding(root: Path, fid: str, *, priority: str, status: str, raised: str) -> None:
    bug = fid.startswith("BG")
    d = root / "sdlc-studio" / ("bugs" if bug else "change-requests")
    d.mkdir(parents=True, exist_ok=True)
    field = "Severity" if bug else "Priority"
    (d / f"{fid}-a-finding.md").write_text(
        f"# {fid}: the finding {fid}\n\n> **Status:** {status}\n> **{field}:** {priority}\n"
        f"> **Raised-in-batch:** {RUN} {raised}\n", encoding="utf-8")


def lean_run(root: Path, *, measured: bool = True) -> None:
    """The fixture run. `measured=False` removes every source a figure could be measured from:
    no plan snapshot, no unit actuals, no meter stamps, no rulings, no known-issue gaps."""
    (root / "sdlc-studio" / ".local").mkdir(parents=True, exist_ok=True)
    (root / "sdlc-studio" / "retros").mkdir(parents=True, exist_ok=True)
    (root / "sdlc-studio" / "reviews").mkdir(parents=True, exist_ok=True)
    _unit(root, "US0001", 8, "Done")      # planned at 3, resized to 8
    _unit(root, "US0002", 5, "Done")
    _unit(root, "US0003", 2, "Draft")     # dropped
    _unit(root, "US0004", 3, "Done")      # added
    _unit(root, "US0005", 3, "Review")    # carried, never delivered
    (root / "sdlc-studio" / "retros" / f"{RETRO}-a-sprint.md").write_text(
        f"# {RETRO}: a sprint\n\n> **Batch:** US0001, US0002, US0004, US0005\n",
        encoding="utf-8")
    (root / "sdlc-studio" / "reviews" / "critic-verdicts.md").write_text(
        "# Critic verdicts\n\n| Unit | Verdict | Reviewer | Author | Date |\n"
        "| --- | --- | --- | --- | --- |\n"
        "| US0001 | REJECT | a seat | author | 2026-09-20 |\n"
        "| US0001 | APPROVE | a seat | author | 2026-09-20 |\n"
        "| US0002 | APPROVE | a seat | author | 2026-09-20 |\n", encoding="utf-8")
    _finding(root, "BG0901", priority="High", status="Open", raised="2026-09-20T10:00:00Z")
    _finding(root, "BG0902", priority="Low", status="Open", raised="2026-09-20T11:00:00Z")
    _finding(root, "CR0901", priority="Medium", status="Proposed", raised="2026-09-20T12:00:00Z")
    _finding(root, "BG0903", priority="High", status="Fixed", raised="2026-09-20T12:30:00Z")
    _finding(root, "BG0904", priority="High", status="Open", raised="2026-08-01T10:00:00Z")
    state = {
        "schema": 1, "run_id": RUN, "started_at": "2026-09-20T08:00:00Z",
        "ended_at": "2026-09-20T18:00:00Z", "outcome": "goal-reached",
        "sprint_goal": "A sprint runs start to finish on its own and hands you one page.",
        "sprint_goal_verdict": {"verdict": "achieved", "note": "one page was handed over"},
        "batch": ["US0001", "US0002", "US0004", "US0005"],
        "batch_changes": [
            {"action": "drop", "id": "US0003", "reason": "blocked by an upstream fix",
             "at": "2026-09-20T09:00:00Z"},
            {"action": "add", "id": "US0004", "reason": "found in review of US0001",
             "at": "2026-09-20T09:30:00Z"}],
    }
    if measured:
        state["plan_snapshot"] = {
            "units": {
                "US0001": {"planned_points": 3, "forecast_tokens": 300_000,
                           "forecast_minutes": 30.0, "added": False},
                "US0002": {"planned_points": 5, "forecast_tokens": 500_000,
                           "forecast_minutes": 50.0, "added": False},
                "US0003": {"planned_points": 2, "forecast_tokens": 200_000,
                           "forecast_minutes": 20.0, "added": False},
                "US0005": {"planned_points": 3, "forecast_tokens": 300_000,
                           "forecast_minutes": 30.0, "added": False},
                "US0004": {"planned_points": 3, "forecast_tokens": 300_000,
                           "forecast_minutes": 30.0, "added": True}},
            "rates": {"tokens_per_point": {"value": 100_000, "source": "median of 5 runs"},
                      "minutes_per_point": {"value": 10.0, "source": "median of 5 runs"}}}
        state["unit_actuals"] = {
            "US0001": {"started_at": "2026-09-20T08:10:00Z", "start_tokens": 0,
                       "minutes": 90.0, "tokens": 900_000, "open": False},
            "US0002": {"started_at": "2026-09-20T10:00:00Z", "start_tokens": 0,
                       "minutes": 40.0, "tokens": 400_000, "open": False},
            "US0004": {"started_at": "2026-09-20T12:00:00Z", "start_tokens": 0,
                       "minutes": 20.0, "tokens": 200_000, "open": False}}
        state["close_known_issues"] = [
            {"source": "installed-copy", "detail": "the installed copy was not refreshed"}]
        state["rulings"] = [
            {"id": "D0301", "by": "persona", "seat": "qa", "subject": "a", "kind": "ruling"},
            {"id": "D0302", "by": "persona", "seat": "product", "subject": "b",
             "kind": "cited"},
            {"id": "D0303", "by": "operator", "seat": None, "subject": "c", "kind": "ruling"}]
        state["session_token_stamps"] = [
            {"tokens": 1_000_000, "source": "/t/s1.jsonl", "at": "2026-09-20T08:00:00Z",
             "kind": "open", "model": MODEL},
            {"tokens": 2_700_000, "source": "/t/s1.jsonl", "at": "2026-09-20T18:00:00Z",
             "kind": "report", "model": MODEL}]
        state["delegated_tokens"] = [{"tokens": 123_456, "agent": "reviewer", "note": "",
                                      "provenance": "supplied"}]
    (root / "sdlc-studio" / ".local" / "run-state.json").write_text(
        json.dumps(state, indent=2), encoding="utf-8")


def _sections(rep: dict) -> dict:
    return {s["key"]: s for s in rep["sections"]}


def _front_md(md: str) -> str:
    return md.split("\n## Appendix", 1)[0]


def _md_section(md: str, heading: str) -> str:
    return md.split(f"\n## {heading}\n", 1)[1].split("\n## ", 1)[0]


def _html_h2(html: str) -> list[str]:
    return [re.sub(r"<[^>]+>", "", h).strip()
            for h in re.findall(r"<h2[^>]*>(.*?)</h2>", html, flags=re.S)]


class OnePageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def _build(self, **kw) -> dict:
        lean_run(self.root, **kw)
        return sr.build_report(self.root, RETRO)

    def _cli(self, *argv: str) -> str:
        """Run the shipped `sprint_report.py` entry point and return what it printed."""
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = sr.main(["--root", str(self.root), *argv])
        self.assertEqual(0, rc, err.getvalue())
        return out.getvalue()

    def test_the_front_page_has_exactly_the_five_sections(self) -> None:
        """AC1. MUTANT: append any appendix section (tokens by model, DORA) to the front page -
        the page grows back toward fourteen sections and the order check fails."""
        lean_run(self.root)
        rep = json.loads(self._cli("build", "--run", RUN, "--format", "json"))
        front = [s["title"] for s in rep["sections"] if s["key"] in sr.FRONT_PAGE]
        self.assertEqual(FRONT, front)
        self.assertEqual(list(sr.FRONT_PAGE), [s["key"] for s in rep["sections"]][:5],
                         "the front page does not lead the report in order")
        md = self._cli("build", "--run", RUN)
        self.assertEqual(FRONT + ["Appendix"], re.findall(r"(?m)^## (.+)$", md),
                         "the Markdown page does not carry exactly the five sections, then "
                         "the appendix")

    def test_estimates_read_the_plan_snapshot_and_actuals(self) -> None:
        """AC2. MUTANT: take planned points from the unit file's current Points - the resized
        unit then reads planned 8, the forecast equals the actual and the error vanishes."""
        rep = self._build()
        rows = {r["est_measure"]["value"]: r for r in _sections(rep)["estimates"]["rows"]}
        self.assertEqual(["Points", "Minutes", "Tokens"], list(rows))
        # Over the delivered units US0001, US0002 and US0004.
        pts = rows["Points"]
        self.assertEqual((11, 16), (pts["est_forecast"]["value"], pts["est_actual"]["value"]))
        self.assertEqual("1.45x", pts["est_ratio"]["value"])
        # Minutes and tokens are the whole run's: forecast over every unit planned or added and
        # not dropped (US0001, 2, 4, 5), actual from the run's span (08:00 to 18:00) and meter.
        mins = rows["Minutes"]
        self.assertEqual((140.0, 600.0),
                         (mins["est_forecast"]["value"], mins["est_actual"]["value"]))
        self.assertEqual("4.29x", mins["est_ratio"]["value"])
        tok = rows["Tokens"]
        # Actual is the run meter (1,700,000) plus the delegated agent's reported 123,456.
        self.assertEqual((1_400_000, 1_823_456),
                         (tok["est_forecast"]["value"], tok["est_actual"]["value"]))
        self.assertEqual("1.3x", tok["est_ratio"]["value"])
        # The resized unit, per unit: planned from the snapshot, actual from the file.
        units = {r["unit_id"]["value"]: r for r in _sections(rep)["delivered"]["rows"]}
        self.assertEqual(3, units["US0001"]["unit_planned_points"]["value"])
        self.assertEqual(8, units["US0001"]["unit_points"]["value"])
        per_unit = {r["unit_id"]["value"]: r for r in _sections(rep)["estimates"]["unit_rows"]}
        self.assertEqual((30.0, 90.0, 300_000, 900_000),
                         tuple(per_unit["US0001"][k]["value"] for k in
                               ("eu_forecast_minutes", "eu_minutes",
                                "eu_forecast_tokens", "eu_tokens")))
        # The carried unit was never measured: its own time and tokens read so, never 0.
        for key in ("eu_minutes", "eu_tokens"):
            self.assertEqual(sr.NOT_MEASURED, per_unit["US0005"][key]["value"], key)
        md = _md_section(sr.render_markdown(rep), "Estimates")
        self.assertRegex(md, r"\| Points \| 11 \| 16 \| 1\.45x \|")

    def test_delivered_to_plan_shows_changes_and_rounds(self) -> None:
        """AC3. MUTANT: count rounds as one per unit, or drop the reason from a batch change -
        rework is erased, which is how a fifteen-round run read `1 round`."""
        rep = self._build()
        sec = _sections(rep)["delivered"]
        figs = sec["figures"]
        # Units and points at PLANNED size: 13 planned = 8 delivered + 2 dropped + 3 carried,
        # and the added unit is counted beside the plan, never inside it.
        self.assertEqual({"planned_units": 4, "planned_points": 13,
                          "plan_delivered_units": 2, "plan_delivered_points": 8,
                          "added_units": 1, "added_delivered_units": 1, "added_points": 3,
                          "dropped_units": 1, "dropped_points": 2,
                          "carried_units": 1, "carried_points": 3,
                          "points_delivered": 16},
                         {k: figs[k]["value"] for k in (
                             "planned_units", "planned_points", "plan_delivered_units",
                             "plan_delivered_points", "added_units", "added_delivered_units",
                             "added_points", "dropped_units", "dropped_points",
                             "carried_units", "carried_points", "points_delivered")})
        self.assertNotIn("delivered_units", figs, "a delivered total mixes plan and additions")
        units = {r["unit_id"]["value"]: r for r in sec["rows"]}
        self.assertEqual({"US0001", "US0002", "US0003", "US0004", "US0005"}, set(units))
        drop = units["US0003"]["unit_outcome"]["value"]
        self.assertIn("dropped", drop)
        self.assertIn("blocked by an upstream fix", drop)
        add = units["US0004"]["unit_outcome"]["value"]
        self.assertIn("added", add)
        self.assertIn("found in review of US0001", add)
        self.assertIn("delivered", add)
        carried = units["US0005"]["unit_outcome"]["value"]
        self.assertIn("carried", carried)
        self.assertIn("no reason recorded", carried)
        self.assertEqual(2, units["US0001"]["unit_rounds"]["value"])
        self.assertEqual(1, units["US0002"]["unit_rounds"]["value"])
        self.assertEqual(0, units["US0005"]["unit_rounds"]["value"])
        md = _md_section(sr.render_markdown(rep), "Delivered to plan")
        self.assertIn("blocked by an upstream fix", md)
        self.assertRegex(md, r"\| US0001 \| 3 \| 8 \| delivered \| 2 \|")
        # Two of four planned units plus one added never reads as three delivered against four.
        self.assertRegex(md, r"\| Planned \| 4 \| 13 \|")
        self.assertRegex(md, r"\| Delivered of the plan \| 2 \| 8 \|")
        self.assertRegex(md, r"\| Added mid-run and delivered \| 1 of 1 added \| 3 \|")
        self.assertRegex(md, r"\| Dropped \| 1 \| 2 \|")
        self.assertRegex(md, r"\| Carried undelivered \| 1 \| 3 \|")

    def test_known_issues_list_findings_gaps_and_carried_units(self) -> None:
        """AC4. MUTANT: list every open finding on disk - BG0904, raised before the run, is
        then handed over as this run's, and the fixed BG0903 as still open."""
        rep = self._build()
        rows = [(r["issue_id"]["value"], r["issue_priority"]["value"])
                for r in _sections(rep)["known_issues"]["rows"]]
        self.assertEqual([("BG0901", "High"), ("CR0901", "Medium"), ("BG0902", "Low"),
                          ("installed-copy", "close gap"), ("US0005", "carried unit")], rows)
        md = _md_section(sr.render_markdown(rep), "Known issues handed over")
        self.assertIn("the installed copy was not refreshed", md)
        self.assertIn("the finding BG0901", md)
        self.assertNotIn("BG0903", md)
        self.assertNotIn("BG0904", md)
        self.assertLess(md.index("BG0901"), md.index("BG0902"), "not ordered by priority")

    def test_cost_dora_and_rulings_live_in_the_appendix(self) -> None:
        """AC5. MUTANT: render tokens by model beside the estimates - the front page grows a
        cost table again and the model name appears before the appendix."""
        rep = self._build()
        keys = [s["key"] for s in rep["sections"]]
        for key in ("cost", "dora", "calibration", "rulings"):
            self.assertIn(key, sr.APPENDIX)
            self.assertGreater(keys.index(key), keys.index("signoff"),
                               f"{key} is not after the sign line")
        secs = _sections(rep)
        self.assertEqual(MODEL, secs["cost"]["rows"][0]["model_name"]["value"])
        self.assertEqual(1_700_000, secs["cost"]["rows"][0]["model_tokens"]["value"])
        self.assertEqual(123_456, secs["cost"]["figures"]["tokens_delegated"]["value"])
        self.assertEqual(100_000, secs["calibration"]["figures"]["cal_tokens_per_point"]["value"])
        self.assertEqual(10.0, secs["calibration"]["figures"]["cal_minutes_per_point"]["value"])
        rulings = secs["rulings"]["figures"]
        self.assertEqual((2, 1, 1), (rulings["persona_rulings"]["value"],
                                     rulings["operator_rulings"]["value"],
                                     rulings["cited_rulings"]["value"]))
        md = sr.render_markdown(rep)
        front, appendix = _front_md(md), md.split("\n## Appendix", 1)[1]
        for text in (MODEL, "123,456", "DORA", "Calibration", "Rulings", "Tokens by model"):
            self.assertNotIn(text, front, f"{text!r} is on the front page")
            self.assertIn(text, appendix, f"{text!r} is not in the appendix")

    def test_missing_figures_read_not_measured_in_both_renders(self) -> None:
        """AC6. MUTANT: default an absent figure to 0 - a run nobody measured reads as a run
        that cost nothing and took no time, and the two renders drift apart."""
        rep = self._build(measured=False)
        est = {r["est_measure"]["value"]: r for r in _sections(rep)["estimates"]["rows"]}
        for measure in ("Points", "Minutes", "Tokens"):
            self.assertEqual(sr.NOT_MEASURED, est[measure]["est_forecast"]["value"], measure)
            self.assertEqual(sr.NOT_MEASURED, est[measure]["est_ratio"]["value"], measure)
        self.assertEqual(sr.NOT_MEASURED, est["Tokens"]["est_actual"]["value"])
        delivered = _sections(rep)["delivered"]["figures"]
        self.assertEqual(sr.NOT_MEASURED, delivered["planned_points"]["value"])
        rid = sr.file_report(self.root, rep)   # the close's route; `build --write` refuses
        md = self._cli("render", "--report", rid)
        html = self._cli("render", "--report", rid, "--to", "html")
        self.assertEqual(FRONT, _html_h2(html)[:5], "the HTML front page differs")
        self.assertEqual("Appendix", _html_h2(html)[5])
        md_est = _md_section(md, "Estimates")
        html_est = html.split("<h2>Estimates</h2>", 1)[1].split("<h2>", 1)[0]
        for label, text in (("markdown", md_est), ("html", html_est)):
            self.assertIn("not measured", text.lower(), label)
            for zero in ("| 0 |", "| 0.0 |", ">0<", ">0.0<", "| - |", ">-<", "None"):
                self.assertNotIn(zero, text, f"{label} renders an absent figure as {zero!r}")
        for label, text in (("markdown", md), ("html", html)):
            for heading in ("Tokens by model", "Calibration", "Rulings"):
                body = text.split(heading, 1)[1][:600]
                self.assertIn("not measured", body.lower(),
                              f"{label}: {heading} does not read not measured")


class RunTotalsTests(unittest.TestCase):
    """The run's minutes and tokens are its own span and meter. Per-unit spans overlap when units
    are open together, so their sum over-counts the run and is never used as its total."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def _state(self, **changes) -> None:
        path = self.root / "sdlc-studio" / ".local" / "run-state.json"
        state = json.loads(path.read_text(encoding="utf-8"))
        for key, value in changes.items():
            if value is None:
                state.pop(key, None)
            else:
                state[key] = value
        path.write_text(json.dumps(state), encoding="utf-8")

    def _estimates(self) -> dict:
        rep = sr.build_report(self.root, RETRO)
        return {r["est_measure"]["value"]: r for r in _sections(rep)["estimates"]["rows"]}

    def test_the_token_actual_adds_the_delegated_agents_to_the_run_meter(self) -> None:
        """MUTANT: report the main-thread meter alone - a run that delegated most of its work
        reads a fraction of its cost, which is the page RPT0004 was rejected for."""
        lean_run(self.root)
        tokens = self._estimates()["Tokens"]
        self.assertEqual(1_823_456, tokens["est_actual"]["value"])
        basis = tokens["est_basis"]["value"]
        self.assertIn("1 delegated agent", basis)
        self.assertIn("appendix", basis, "the split lives in the appendix, not on the front page")

    def test_the_page_ends_with_exactly_one_newline(self) -> None:
        """MUTANT: return the collapsed text without trimming its tail - a run with no waivers
        ends the page on an empty repeat block, and the filed page fails markdownlint (MD012)."""
        lean_run(self.root)
        md = sr.render_markdown(sr.build_report(self.root, RETRO))
        self.assertTrue(md.endswith("\n") and not md.endswith("\n\n"), repr(md[-40:]))

    def test_a_run_with_no_per_unit_figures_prints_no_per_unit_table(self) -> None:
        """MUTANT: always emit the per-unit table - a run with nothing measured per unit prints
        a row of NOT MEASURED per unit, which buries the three answers on the one page."""
        lean_run(self.root, measured=False)
        # This run's own shape: a plan snapshot holding planned points and nothing per unit.
        self._state(plan_snapshot={"units": {uid: {"planned_points": 3, "forecast_tokens": None,
                                                   "forecast_minutes": None, "added": False}
                                             for uid in ("US0001", "US0002", "US0004")},
                                   "rates": {}})
        rep = sr.build_report(self.root, RETRO)
        self.assertEqual([], _sections(rep)["estimates"]["unit_rows"])
        minutes = {r["est_measure"]["value"]: r
                   for r in _sections(rep)["estimates"]["rows"]}["Minutes"]["est_forecast"]
        self.assertEqual("the plan recorded no minute forecast for any unit", minutes["reason"],
                         "a snapshot IS recorded here, so 'no plan snapshot' would be false")
        self.assertNotIn("open span", sr.render_markdown(rep))
        lean_run(self.root)
        self.assertTrue(_sections(sr.build_report(self.root, RETRO))["estimates"]["unit_rows"])

    def test_sealing_the_run_does_not_move_the_review_rounds(self) -> None:
        """MUTANT: count a sealed run's rounds by the outside-a-run rule (rows after the last
        non-final APPROVE) rather than against the run's own review base - a unit approved,
        then re-confirmed by its reviewer, reads 2 rounds while open and 1 once sealed, and the
        seal invalidates the page it signs (found rehearsing RUN-01M36R3D's seal)."""
        lean_run(self.root)
        ledger = self.root / "sdlc-studio" / "reviews" / "critic-verdicts.md"
        ledger.write_text(ledger.read_text(encoding="utf-8")
                          + "| US0002 | APPROVE | a seat | author | 2026-09-20 |\n",
                          encoding="utf-8")
        self._state(review_base={"US0001": 0, "US0002": 0, "US0004": 0, "US0005": 0})

        def rounds() -> dict:
            rep = sr.build_report(self.root, RETRO)
            return {r["unit_id"]["value"]: r["unit_rounds"]["value"]
                    for r in _sections(rep)["delivered"]["rows"]}
        before = rounds()
        self.assertEqual(2, before["US0002"])
        self._state(outcome="goal-reached")
        self.assertEqual(before, rounds(), "sealing the run moved a review-round figure")

    def test_overlapping_unit_spans_are_never_summed_into_the_run(self) -> None:
        """MUTANT: take the run's actual as the sum over `unit_actuals` - three units open over
        the same hours read three times the run's spend and time."""
        lean_run(self.root)
        overlapping = {uid: {"started_at": "2026-09-20T08:00:00Z", "start_tokens": 0,
                             "minutes": 600.0, "tokens": 1_700_000, "open": False}
                       for uid in ("US0001", "US0002", "US0004")}
        self._state(unit_actuals=overlapping)
        est = self._estimates()
        self.assertEqual(600.0, est["Minutes"]["est_actual"]["value"])
        # The run meter (1,700,000) plus the fixture's one delegated agent (123,456).
        self.assertEqual(1_823_456, est["Tokens"]["est_actual"]["value"])
        self.assertIn("span", est["Minutes"]["est_basis"]["value"])
        self.assertIn("meter", est["Tokens"]["est_basis"]["value"])
        md = _md_section(sr.render_markdown(sr.build_report(self.root, RETRO)), "Estimates")
        self.assertIn("open span", md)
        self.assertIn("overlap", md)
        self.assertNotIn("5,100,000", md, "the per-unit tokens were summed")

    def test_no_meter_and_no_span_read_not_measured_not_the_unit_sum(self) -> None:
        """MUTANT: fall back to the per-unit sum when the run's own reading is missing - the
        over-count returns exactly where nothing checks it."""
        lean_run(self.root)
        self._state(session_token_stamps=None, started_at=None)
        est = self._estimates()
        for measure in ("Minutes", "Tokens"):
            self.assertEqual(sr.NOT_MEASURED, est[measure]["est_actual"]["value"], measure)
            self.assertEqual(sr.NOT_MEASURED, est[measure]["est_ratio"]["value"], measure)
        self.assertIn("start", est["Minutes"]["est_actual"]["reason"])


class NeverZeroTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_unsized_units_and_a_missing_ledger_read_not_measured(self) -> None:
        """MUTANT: sum absent Points as 0, or count absent verdict rows as 0 rounds - a run whose
        units carry no size reads as having delivered 0 points, and an unreviewed one as having
        needed no rework."""
        lean_run(self.root)
        stories = self.root / "sdlc-studio" / "stories"
        for uid in ("US0001", "US0002", "US0004"):
            path = stories / f"{uid}-a-unit.md"
            path.write_text(re.sub(r"(?m)^> \*\*Points:\*\*.*\n", "",
                                   path.read_text(encoding="utf-8")), encoding="utf-8")
        (self.root / "sdlc-studio" / "reviews" / "critic-verdicts.md").unlink()
        rep = sr.build_report(self.root, RETRO)
        figs = _sections(rep)["delivered"]["figures"]
        self.assertEqual(sr.NOT_MEASURED, figs["points_delivered"]["value"])
        self.assertIn("3 delivered unit(s) carry no Points", figs["points_delivered"]["reason"])
        pts = {r["est_measure"]["value"]: r
               for r in _sections(rep)["estimates"]["rows"]}["Points"]["est_actual"]
        self.assertEqual(sr.NOT_MEASURED, pts["value"])
        self.assertEqual("no delivered unit carries Points", pts["reason"])
        for row in _sections(rep)["delivered"]["rows"]:
            self.assertEqual(sr.NOT_MEASURED, row["unit_rounds"]["value"])
            self.assertIn("no verdict ledger", row["unit_rounds"]["reason"])

    def test_a_run_that_delivered_nothing_reads_not_measured_points(self) -> None:
        """MUTANT: sum an empty delivered set to 0 points - the page then reads as a measured
        zero rather than as nothing delivered."""
        lean_run(self.root)
        for uid in ("US0001", "US0002", "US0004"):
            _unit(self.root, uid, 3, "In Progress")
        figs = _sections(sr.build_report(self.root, RETRO))["delivered"]["figures"]
        self.assertEqual(sr.NOT_MEASURED, figs["points_delivered"]["value"])
        self.assertEqual("no unit was delivered", figs["points_delivered"]["reason"])


class KnownIssuesPriorityTests(unittest.TestCase):
    def test_cr_priorities_rank_beside_bug_severities(self) -> None:
        """MUTANT: rank only the severity words - a P0 change request sorts after every Low
        bug, at the bottom of the hand-over."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            lean_run(root)
            for fid, priority in (("CR0902", "P0"), ("CR0903", "P3"), ("CR0904", "P1")):
                _finding(root, fid, priority=priority, status="Proposed",
                         raised="2026-09-20T13:00:00Z")
            rows = [r["issue_id"]["value"] for r in
                    _sections(sr.build_report(root, RETRO))["known_issues"]["rows"]]
            self.assertEqual(["CR0902", "BG0901", "CR0904", "CR0901", "BG0902", "CR0903"],
                             rows[:6])


class LegacyReportRenderTests(unittest.TestCase):
    def test_a_schema_one_report_renders_its_filed_twin_and_refuses_html(self) -> None:
        """MUTANT: let `render` fail on a schema-1 report as `check` does - the operator asks to
        read RPT0005 and is shown nothing at all."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            lean_run(root)
            reports = root / "sdlc-studio" / "reports"
            reports.mkdir(parents=True)
            (reports / "RPT0001.json").write_text(json.dumps(
                {"schema": 1, "report_id": "RPT0001", "run_id": RUN, "sections": []}),
                encoding="utf-8")
            twin = "# Sprint Report: an old page\n\nThe page as it was filed.\n"
            (reports / "RPT0001-sprint-report-an-old-run.md").write_text(twin, encoding="utf-8")
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = sr.main(["--root", str(root), "render", "--report", "RPT0001"])
            self.assertEqual(0, rc, err.getvalue())
            first, rest = out.getvalue().split("\n", 1)
            self.assertIn("schema 1", first)
            self.assertIn("cannot be re-derived", first)
            self.assertIn(twin.strip(), rest)
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = sr.main(["--root", str(root), "render", "--report", "RPT0001",
                              "--to", "html"])
            self.assertEqual(2, rc)
            self.assertEqual("", out.getvalue())
            self.assertIn("schema 1", err.getvalue())


if __name__ == "__main__":
    unittest.main()
