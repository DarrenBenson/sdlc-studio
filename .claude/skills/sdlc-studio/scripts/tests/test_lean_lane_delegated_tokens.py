"""US0980: a lane return records the builder's token and minute totals (CR0606).

RPT0014 printed a 0.2x tokens ratio: the forecast covered every unit's work, the actual was the
main-thread meter, and the meter cannot see a delegated builder's spend. `sprint lane return`
now takes the builder's own `--tokens` and `--minutes`, recorded through the existing delegated
record (`run_state.record_delegated_tokens`, tagged to the unit), so they count once in the
run's delegated total and read as the unit's agent totals. The Estimates tokens ratio is
withheld unless every delivered unit's delegated spend was supplied: a ratio over a partial
actual is the 0.2x again. Agent minutes take precedence over the lane span (D0298), which stays
the fallback.

Every test drives `sprint.py lane` in-process against a throwaway workspace with its own
transcript directory and clock, and derives the page through `sprint_report.build_report`.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import contextlib
import importlib
import io
import json
import os
import sys
import tempfile
import unittest
import unittest.mock
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))

T0 = datetime(2026, 10, 2, 9, 0, tzinfo=timezone.utc)
RETRO = "RETRO0001"
UNITS = ("US0101", "US0102")


def _live(name: str):
    """The module the command resolves at call time (see `test_lean_close._live`)."""
    return sys.modules.get(name) or importlib.import_module(name)


@contextlib.contextmanager
def _clock(at: datetime):
    """The unit clock set to `at` on every run-state module object a caller may hold, patched
    by name (LC-010) and on the one `sprint` imported."""
    stamp = at.isoformat().replace("+00:00", "Z")
    with contextlib.ExitStack() as stack:
        stack.enter_context(unittest.mock.patch("lib.run_state._unit_clock", lambda: stamp))
        held = _live("sprint").run_state
        if held is not sys.modules.get("lib.run_state"):
            stack.enter_context(unittest.mock.patch.object(held, "_unit_clock", lambda: stamp))
        yield


class _Workspace:
    """Two Ready stories whose one criterion passes, an open run over both with a plan
    snapshot forecasting each, and a retro, so the page derives."""

    def __init__(self, d: str) -> None:
        self.root = Path(d) / "repo"
        self.transcripts = Path(d) / "transcripts"
        self.transcripts.mkdir()
        (self.root / "src").mkdir(parents=True)
        (self.root / "src" / "a.py").write_text("x = 1\n", encoding="utf-8")
        stories = self.root / "sdlc-studio" / "stories"
        stories.mkdir(parents=True)
        for uid in UNITS:
            (stories / f"{uid}-x.md").write_text(
                f"# {uid}: x\n\n> **Status:** Ready\n> **Points:** 2\n\n## Acceptance Criteria"
                "\n\n### AC1: it holds\n\n- **Verify:** file src/a.py\n", encoding="utf-8")
        retros = self.root / "sdlc-studio" / "retros"
        retros.mkdir(parents=True)
        (retros / f"{RETRO}-lean.md").write_text(
            f"# RETRO-0001: lean\n\n> **Batch:** {', '.join(UNITS)}\n", encoding="utf-8")
        self.spend(1000)
        rs = _live("lib.run_state")
        rs.open_run(self.root, batch=list(UNITS), goal="g")
        rs.stamp_tokens(self.root, "open", self.transcripts)   # the meter's opening reading
        rs.update(self.root, sprint_goal="every unit's spend is on the page",
                  plan_snapshot={"units": {uid: {
                      "planned_points": 2, "forecast_minutes": 20.0,
                      "forecast_tokens": 200_000, "added": False} for uid in UNITS}})

    def spend(self, tokens: int) -> None:
        with (self.transcripts / "session.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"message": {"model": "m", "usage": {
                "input_tokens": tokens, "output_tokens": 0}}}) + "\n")

    def lane(self, *argv: str, at: datetime) -> tuple[int, str]:
        out = io.StringIO()
        with _clock(at), contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            try:
                rc = _live("sprint").main(["lane", *argv, "--root", str(self.root)])
            except SystemExit as exc:                     # the parser's own usage error
                rc = exc.code
        return rc, out.getvalue()

    def deliver(self, uid: str, *extra: str, minutes: int = 7) -> str:
        """Brief `uid` at T0, return it passing `minutes` later with `extra`, then mark it
        Done in place (delivered on the page, without a transition that could move the span)."""
        rc, out = self.lane("brief", "--units", uid, at=T0)
        assert rc == 0, out
        rc, out = self.lane("return", "--units", uid, *extra,
                            at=T0 + timedelta(minutes=minutes))
        assert rc == 0, out
        p = self.root / "sdlc-studio" / "stories" / f"{uid}-x.md"
        p.write_text(p.read_text(encoding="utf-8").replace("Ready", "Done"), encoding="utf-8")
        return out

    def page(self) -> dict:
        return _live("sprint_report").build_report(self.root, RETRO)

    def tokens_row(self, page: dict) -> dict:
        sec = next(s for s in page["sections"] if s["key"] == "estimates")
        return next(r for r in sec["rows"] if r["est_measure"]["value"] == "Tokens")

    def unit_rows(self, page: dict) -> dict:
        sec = next(s for s in page["sections"] if s["key"] == "estimates")
        return {r["unit_id"]["value"]: r for r in sec.get("unit_rows") or []}

    def delegated(self, page: dict) -> dict:
        sec = next(s for s in page["sections"] if s["key"] == "cost")
        return sec["figures"]["tokens_delegated"]


class LaneDelegatedTokensTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.ws = _Workspace(self._tmp.name)
        env = unittest.mock.patch.dict(
            os.environ, {_live("lib.run_state").TRANSCRIPTS_ENV: str(self.ws.transcripts)})
        env.start()
        self.addCleanup(env.stop)

    def test_a_lane_return_records_agent_totals_and_the_ratio_is_withheld_without_them(
            self) -> None:
        """AC1. MUTANTS: HEAD, which has no `--tokens` on `lane return` (a usage error) and
        prints a ratio from the meter alone; recording the total untagged, so X's row reads
        its span and not 250,000 agent tokens; computing the ratio whenever the meter has a
        reading, so the run with no delegated total prints 0.0x."""
        ws = self.ws
        ws.spend(5000)                                    # main-thread traffic inside the run
        rc, out = ws.lane("brief", "--units", "US0101", "US0102", at=T0)
        self.assertEqual(0, rc, out)
        page = ws.page()                                  # no delegated total supplied
        self.assertEqual(5000, ws.tokens_row(page)["est_actual"]["value"], "premise: the meter")
        ratio = ws.tokens_row(page)["est_ratio"]
        self.assertEqual("NOT MEASURED", ratio["value"], "a ratio over the meter alone")
        self.assertTrue(ratio["reason"].startswith("withheld"), ratio["reason"])
        self.assertIn("no delegated spend was supplied", ratio["reason"])

        out = ws.deliver("US0101", "--tokens", "250000", "--minutes", "40")
        self.assertIn("250,000", out)
        ws.deliver("US0102", "--tokens", "150000", "--minutes", "12")
        page = ws.page()
        row = ws.unit_rows(page)["US0101"]
        self.assertEqual((250_000, "agent tokens"),
                         (row["eu_tokens"]["value"], row["eu_tokens"].get("label")))
        self.assertEqual((40.0, "agent minutes"),
                         (row["eu_minutes"]["value"], row["eu_minutes"].get("label")))
        self.assertEqual(400_000, ws.delegated(page)["value"], "the run's delegated total")
        tok = ws.tokens_row(page)
        # Every delivered unit supplied its spend: the ratio is computed, over the meter's
        # 5,000 plus the 400,000 delegated, against the 400,000 forecast.
        self.assertEqual((400_000, 405_000, "1.01x"),
                         tuple(tok[k]["value"] for k in ("est_forecast", "est_actual",
                                                         "est_ratio")))

    def test_a_partial_delegated_total_withholds_the_ratio(self) -> None:
        """AC2. MUTANT: compute the ratio from the units that supplied totals (or from the
        meter plus whatever was supplied), so one unit's 250,000 against both units' 400,000
        forecast prints a number."""
        ws = self.ws
        ws.deliver("US0101", "--tokens", "250000", "--minutes", "40")
        ws.deliver("US0102")                              # its lane supplied nothing
        ratio = ws.tokens_row(ws.page())["est_ratio"]
        self.assertEqual("NOT MEASURED", ratio["value"])
        self.assertTrue(ratio["reason"].startswith("withheld"), ratio["reason"])
        self.assertIn("delegated spend not measured for every unit", ratio["reason"])
        self.assertIn("US0102", ratio["reason"])
        self.assertNotIn("US0101", ratio["reason"])

    def test_a_briefed_unit_without_a_total_withholds_the_ratio(self) -> None:
        """US0980 round 1, the reviewer's repro. MUTANT: check only the DELIVERED units, while
        the forecast sums every live unit, so US0102 - briefed, returned blocked with no total
        and carried - leaves a ratio over a partial actual (0.64x). Every live unit that was
        briefed or carries a span must have supplied its builder's total."""
        ws = self.ws
        p = ws.root / "sdlc-studio" / "stories" / "US0102-x.md"
        p.write_text(p.read_text(encoding="utf-8").replace("src/a.py", "src/missing.py"),
                     encoding="utf-8")                    # US0102's criterion is red
        ws.spend(5000)
        ws.deliver("US0101", "--tokens", "250000", "--minutes", "40")
        rc, out = ws.lane("brief", "--units", "US0102", at=T0)
        self.assertEqual(0, rc, out)
        rc, out = ws.lane("return", "--units", "US0102", at=T0 + timedelta(minutes=9))
        self.assertEqual(1, rc, out)                      # blocked, and no total supplied
        ratio = ws.tokens_row(ws.page())["est_ratio"]
        self.assertEqual("NOT MEASURED", ratio["value"], "a ratio over a partial actual")
        self.assertIn("delegated spend not measured for every unit", ratio["reason"])
        self.assertIn("US0102", ratio["reason"])
        self.assertNotIn("US0101", ratio["reason"])

    def test_agent_minutes_take_precedence_over_the_lane_span(self) -> None:
        """AC3 (D0298). MUTANTS: sum the agent's minutes and the span (47); take the span over
        the agent (7); drop the label, so 40 reads as a span. Control: US0102, returned with no
        agent total, reads its 9-minute lane span, unlabelled."""
        ws = self.ws
        ws.deliver("US0101", "--tokens", "250000", "--minutes", "40", minutes=7)
        ws.deliver("US0102", minutes=9)
        rows = ws.unit_rows(ws.page())
        self.assertEqual((40.0, "agent minutes"),
                         (rows["US0101"]["eu_minutes"]["value"],
                          rows["US0101"]["eu_minutes"].get("label")))
        self.assertEqual((9.0, None), (rows["US0102"]["eu_minutes"]["value"],
                                       rows["US0102"]["eu_minutes"].get("label")))

    def test_totals_are_optional_and_unattributable_ones_are_not_recorded(self) -> None:
        """No refusal: a return with no totals passes as before; `--minutes` with no `--tokens`
        (a delegated record is a token total) and a total given for two units at once (it
        cannot be split) each pass with a warning and record nothing. MUTANT: record the
        minutes-only or the two-unit total, so a figure no agent reported for that unit lands
        in the run's delegated record."""
        ws = self.ws
        rs = _live("lib.run_state")
        ws.lane("brief", "--units", "US0101", "US0102", at=T0)
        rc, out = ws.lane("return", "--units", "US0101", "--minutes", "40",
                          at=T0 + timedelta(minutes=5))
        self.assertEqual(0, rc, out)
        self.assertIn("WARNING", out)
        rc, out = ws.lane("return", "--units", "US0101", "US0102", "--tokens", "9000",
                          at=T0 + timedelta(minutes=6))
        self.assertEqual(0, rc, out)
        self.assertIn("WARNING", out)
        self.assertEqual([], rs.delegated_records(rs.read(ws.root)))
        for flag, value in (("--tokens", "0"), ("--tokens", "-5"), ("--minutes", "0"),
                            ("--minutes", "-3"), ("--minutes", "nan")):
            with self.subTest(flag=flag, value=value):
                totals = (("--tokens", "9000") if flag == "--minutes" else ()) + (flag, value)
                rc, out = ws.lane("return", "--units", "US0101", *totals,
                                  at=T0 + timedelta(minutes=7))
                self.assertEqual(2, rc, f"{flag} {value} is a malformed value (D0302): {out}")
                self.assertIn(f"argument {flag}", out)
        self.assertEqual([], rs.delegated_records(rs.read(ws.root)))

    def test_a_page_filed_before_the_rule_re_derives_its_ratio(self) -> None:
        """RPT0006-RPT0014 were signed with a ratio over a partial actual. MUTANTS: apply the
        rule when re-deriving a page that carries no mark, so every one reads INVALIDATED on
        est_ratio; leave the mark off a new page, so its re-derivation computes a ratio its
        signed page withheld."""
        ws = self.ws
        sr = _live("sprint_report")
        ws.spend(5000)
        ws.lane("brief", "--units", "US0101", at=T0)
        before = sr.build_report(ws.root, RETRO, ratio_rule=False)   # the pre-rule derivation
        self.assertEqual("0.01x", ws.tokens_row(before)["est_ratio"]["value"])
        self.assertNotIn(sr.TOKEN_RATIO_RULE, before)
        check = sr.revalidate(ws.root, sr.file_report(ws.root, before))
        self.assertTrue(check["valid"], check["changes"])
        after = sr.build_report(ws.root, RETRO)
        self.assertEqual(sr.TOKEN_RATIO_EVERY_UNIT, after.get(sr.TOKEN_RATIO_RULE))
        check = sr.revalidate(ws.root, sr.file_report(ws.root, after))
        self.assertTrue(check["valid"], check["changes"])

    def test_a_blocked_return_still_records_the_agent_s_spend(self) -> None:
        """The builder spent its tokens whether or not the criteria passed. MUTANT: record only
        on a passing return, so a blocked lane's spend is missing from the run's total."""
        ws = self.ws
        (ws.root / "src" / "a.py").unlink()               # the criterion is red
        ws.lane("brief", "--units", "US0101", at=T0)
        rc, out = ws.lane("return", "--units", "US0101", "--tokens", "70000",
                          at=T0 + timedelta(minutes=5))
        self.assertEqual(1, rc, out)
        rs = _live("lib.run_state")
        self.assertEqual(70_000, rs.delegated_total(rs.read(ws.root)))


if __name__ == "__main__":
    unittest.main()
