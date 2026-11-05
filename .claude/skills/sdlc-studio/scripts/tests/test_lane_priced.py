"""US1117: `sprint lane return --agent` prices a lane from its builder's own transcript, and the
sprint report's unit row shows that priced cost.

Every case drives the command (`sprint.main(["lane", "return", ...])`) over US1091's fixture
harness store (`test_meter_reads_true`), and reads the record the command wrote or the page
`build_report` derives from it. The expected prices are formed from the fixture's own weight
table, typed in that module and nowhere in the code under test.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import json
import sys
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import test_meter_reads_true as meter  # noqa: E402 - US1091's harness store and workspace

#: The builder's two messages: X is logged on two lines, the first with a smaller output count
#: than the message's last, as the harness logs a message per content block.
BUILD_X = meter._usage(40, 400, 5_000, 0, 120_000)
BUILD_X_EARLY_OUTPUT = 90
BUILD_Y = meter._usage(15, 150, 800, 0, 30_000)
#: The repair agent's one message.
REPAIR_Z = meter._usage(25, 250, 2_500, 0, 60_000)


def _priced_with(parts: dict, weights: dict) -> int:
    return round(sum(parts[c] * weights[c] for c in meter.COMPONENTS))


def _says(tx, agent: str, msg_id: str, usage: dict, early_output: int | None = None) -> None:
    """`agent` logs one message to its own transcript: on two lines when `early_output` is given
    (the first carrying that smaller output count), else on one."""
    usages = ([dict(usage, output_tokens=early_output)] if early_output is not None else [])
    lines = [json.dumps({"type": "assistant", "cwd": "/work/repo",
                         "message": {"id": msg_id, "model": meter.MODEL, "role": "assistant",
                                     "content": [{"type": "text"}], "usage": u}})
             for u in usages + [usage]]
    tx._append(tx.subagents / f"agent-{agent}.jsonl", lines)


class LanePricedTests(meter._Case):
    def _records(self, ws, unit: str) -> list[dict]:
        return [r for r in ws.state().get(self.rs.DELEGATED) or [] if r.get("unit") == unit]

    def _build(self, ws) -> None:
        _says(ws.tx, "b7", "msg_b7_x", BUILD_X, early_output=BUILD_X_EARLY_OUTPUT)
        _says(ws.tx, "b7", "msg_b7_y", BUILD_Y)

    def _priced_run(self):
        """An open run whose US0101 was built by agent b7 and repaired by agent r9, each
        returned with `--agent`, US0101 cleared by the gate and the meter read since."""
        ws = self.workspace()
        ws.open()
        self._build(ws)
        rc, out = ws.lane("return", "--units", "US0101", "--agent", "b7")
        self.assertEqual(0, rc, out)
        _says(ws.tx, "r9", "msg_r9_z", REPAIR_Z)
        rc, out = ws.lane("return", "--units", "US0101", "--agent", "r9")
        self.assertEqual(0, rc, out)
        self.rs.update(ws.root, report_gate_clear=["US0101"])
        self.rs.stamp_tokens(ws.root, "report")
        return ws

    def test_the_agent_transcript_prices_the_lane_once_per_message(self) -> None:
        """AC1. MUTANTS: `_aggregate` summing a message's two lines instead of keeping one (X's
        output counted as 90 + 400); keeping a message's first line instead of its largest (90);
        the lane reading the whole session (`claude_tokens`, so the main thread and agent a1
        join b7); a weight copied rather than read from `TOKEN_WEIGHTS` at the moment of
        pricing (the patched output weight of 7 is not applied); the components or the priced
        figure left off the record. Each moves the priced figure or the components asserted."""
        weights = dict(meter.WEIGHTS, output=7)
        live = meter._live("lib.run_state")
        with unittest.mock.patch.dict(live.TOKEN_WEIGHTS, {"output": 7}):
            ws = self.workspace()
            ws.open()
            self._build(ws)
            rc, out = ws.lane("return", "--units", "US0101", "--agent", "b7")
        self.assertEqual(0, rc, out)
        parts = meter._sum(BUILD_X, BUILD_Y)
        [rec] = self._records(ws, "US0101")
        self.assertEqual(parts, rec["components"])
        self.assertEqual(_priced_with(parts, weights), rec["priced"])
        self.assertNotEqual(meter._priced(parts), rec["priced"],
                            "premise: the patched weight moves the price")
        self.assertEqual(meter._tokens(parts), rec["tokens"])
        self.assertEqual(self.rs.READ_FROM_TRANSCRIPT, rec["provenance"])
        self.assertEqual("agent-b7.jsonl", Path(rec["transcript"]).name)
        self.assertIn(f"agent priced cost recorded (read from agent-b7.jsonl): "
                      f"{rec['priced']:,} {self.rs.PRICED_LABEL}", out)

    def test_a_repair_adds_to_the_unit_priced_row(self) -> None:
        """AC2. MUTANTS: `unit_agent_totals` keeping the last priced record instead of summing
        them (the row reads the repair alone); the row's label not `priced`; the cell dropped
        from the unit row; the per-point row dividing by the planned points (4) instead of the
        delivered (2), or dividing the Tokens row instead of the Priced cost row; the per-point
        row left out of the page `render_markdown` writes; the Priced column left out of either
        template, so the page a reader reads shows no unit's priced cost; a unit no agent was
        priced for given no cell under the rule, so the page refuses its unfilled placeholder."""
        sr = meter._live("sprint_report")
        ws = self._priced_run()
        page = ws.page()
        units = next(s for s in page["sections"] if s["key"] == "estimates")["unit_rows"]
        row = next(u for u in units if u["unit_id"]["value"] == "US0101")
        build = meter._priced(meter._sum(BUILD_X, BUILD_Y))
        repair = meter._priced(meter._parts(REPAIR_Z))
        self.assertEqual(build + repair, row["eu_priced"]["value"])
        self.assertEqual("priced", row["eu_priced"]["label"])
        other = next(u for u in units if u["unit_id"]["value"] == "US0102")
        self.assertEqual(sr.NOT_MEASURED, other["eu_priced"]["value"],
                         "a unit no agent was priced for reads NOT MEASURED, as its neighbours do")
        self.assertIn("lane return --units US0102 --agent", other["eu_priced"]["reason"])
        # The page a reader reads: the cell in a column headed Priced, in both renders.
        shown = f"{build + repair:,} priced"
        md = sr.render_markdown(page)
        self.assertIn("| Forecast tokens | Tokens | Priced |", md)
        line = next(ln for ln in md.splitlines() if ln.startswith("| US0101 |"))
        self.assertTrue(line.endswith(f" agent tokens | {shown} |"), line)
        line = next(ln for ln in md.splitlines() if ln.startswith("| US0102 |"))
        self.assertIn(f"| {sr.NOT_MEASURED} - no agent returned for it was priced", line)
        html = sr.render_html(page)
        self.assertIn('<th scope="col" class="num">Tokens</th>'
                      '<th scope="col" class="num">Priced</th>', html)
        self.assertIn(f'<td class="num">{shown}</td></tr>', html)
        priced = ws.row(page, "Priced cost")["est_actual"]["value"]
        self.assertIsInstance(priced, int, "premise: the run's priced cost is measured")
        per_point = ws.row(page, "Priced per point")
        self.assertEqual(round(priced / 2), per_point["est_actual"]["value"])
        self.assertNotEqual(round(priced / 4), per_point["est_actual"]["value"],
                            "premise: delivered and planned points differ")
        self.assertIn("Priced per point", meter._live("sprint_report").render_markdown(page))

    def test_an_unknown_agent_warns_and_records_no_priced_cost(self) -> None:
        """AC3. MUTANTS: the warning dropped, or naming the id but not the directory searched;
        a priced 0 recorded for an agent with no transcript; the return raising or refusing on
        an unknown agent; a warning printed with the transcript present (the control)."""
        ws = self.workspace()
        ws.open()
        rc, out = ws.lane("return", "--units", "US0101", "--agent", "nosuch")
        self.assertEqual(0, rc, out)
        self.assertIn("US0101: ", out)
        self.assertIn("WARNING --agent nosuch was not priced", out)
        self.assertIn(str(ws.tx.subagents), out)
        self.assertEqual([], self._records(ws, "US0101"))
        rc, out = ws.lane("return", "--units", "US0101", "--agent", "nosuch", "--tokens", "5000")
        self.assertEqual(0, rc, out)
        [rec] = self._records(ws, "US0101")
        self.assertEqual(5000, rec["tokens"])
        self.assertNotIn("priced", rec)
        self.assertEqual(self.rs.SUPPLIED, rec["provenance"])
        self._build(ws)
        rc, out = ws.lane("return", "--units", "US0102", "--agent", "b7")
        self.assertEqual(0, rc, out)
        self.assertNotIn("WARNING", out)
        self.assertIsInstance(self._records(ws, "US0102")[0]["priced"], int)

    def test_a_second_return_of_the_same_agent_replaces_its_reading(self) -> None:
        """MUTANT: `record_delegated_tokens` appending a second reading of the same transcript
        for the same unit instead of replacing the first, so the messages the first reading
        held are counted twice on the unit's row."""
        ws = self.workspace()
        ws.open()
        self._build(ws)
        ws.lane("return", "--units", "US0101", "--agent", "b7")
        _says(ws.tx, "b7", "msg_b7_w", REPAIR_Z)
        rc, out = ws.lane("return", "--units", "US0101", "--agent", "b7")
        self.assertEqual(0, rc, out)
        [rec] = self._records(ws, "US0101")
        whole = meter._priced(meter._sum(BUILD_X, BUILD_Y, REPAIR_Z))
        self.assertEqual(whole, rec["priced"])
        self.assertEqual(whole, self.rs.unit_agent_totals(ws.state())["US0101"]["priced"])

    def test_the_priced_unit_mark_round_trips(self) -> None:
        """LC-017. MUTANTS: the mark dropped from the envelope (`build_report`), so a page filed
        under the rule re-derives with it off and reads INVALIDATED; the rule hard-wired on in
        `revalidate`, so a page filed before it re-derives with rows it never carried; either
        gated output built without its rule check (the per-point row, or the unit's priced
        cell), or the Priced column shown on a page without the mark. The control: the page
        with its mark removed by hand reads INVALIDATED, not edited."""
        sr = meter._live("sprint_report")
        ws = self._priced_run()
        page = sr.build_report(ws.root, meter.RETRO)
        self.assertEqual(sr.PRICED_PER_POINT, page[sr.PRICED_UNIT_RULE])
        check = sr.revalidate(ws.root, sr.file_report(ws.root, page))
        self.assertTrue(check["valid"], check["changes"])
        before = sr.build_report(ws.root, meter.RETRO, priced_unit_rule=False)
        self.assertNotIn(sr.PRICED_UNIT_RULE, before)
        check = sr.revalidate(ws.root, sr.file_report(ws.root, before))
        self.assertTrue(check["valid"], check["changes"])
        # Each gated output, one by one: a page filed without the mark carries and renders
        # neither, so an output leaking past its gate is caught here and not first by a signed
        # page reading INVALIDATED.
        est = next(s for s in before["sections"] if s["key"] == "estimates")
        self.assertNotIn("Priced per point", [r["est_measure"]["value"] for r in est["rows"]])
        self.assertEqual([], [u["unit_id"]["value"] for u in est["unit_rows"] if "eu_priced" in u])
        ruled = next(s for s in page["sections"] if s["key"] == "estimates")["unit_rows"]
        shown = sr._cell(next(u for u in ruled if u["unit_id"]["value"] == "US0101")["eu_priced"])
        for name, render in (("markdown", sr.render_markdown), ("html", sr.render_html)):
            self.assertIn(shown, render(page), f"premise: the {name} page shows the cell")
            text = render(before)
            self.assertNotIn("Priced per point", text, name)
            self.assertNotIn(shown, text, name)
            self.assertNotIn("| Priced |", text, name)
            self.assertNotIn('class="num">Priced</th>', text, name)
        dropped = {k: v for k, v in page.items() if k not in (sr.PRICED_UNIT_RULE, "fingerprint")}
        check = sr.revalidate(ws.root, sr.file_report(ws.root, dropped))
        self.assertFalse(check["valid"], "the rule moves no figure on this fixture")
        self.assertTrue(check["changes"], check)
        self.assertEqual([], check["edited"], "INVALIDATED, not an edited page")


if __name__ == "__main__":
    unittest.main()
