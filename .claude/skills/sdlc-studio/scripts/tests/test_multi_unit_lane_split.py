"""A multi-unit lane's one builder total is split between its units by their Points.

`sprint lane return --agent A` over three units reads agent A's transcript once and records
each unit's share of it, weighted by Points, so each unit is priced and the page says the
figure was split. A unit with no Points refuses the split, as the one total did before.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import test_lane_priced as lp  # noqa: E402 - the builder transcript's messages
import test_meter_reads_true as meter  # noqa: E402 - US1091's harness store and workspace

#: Three units of unequal Points, so a split by points differs from an even one or by order.
POINTS = {"US0101": 2, "US0102": 1, "US0103": 3}
SPLIT = "split by points"


class MultiUnitLaneSplitTests(meter._Case):
    def _three(self, points: dict | None = None):
        """An open run over three units whose builder b7 logged two messages."""
        points = POINTS if points is None else points
        ws = self.workspace()
        stories = ws.root / "sdlc-studio" / "stories"
        for uid, pts in points.items():
            size = f"> **Points:** {pts}\n" if pts is not None else ""
            (stories / f"{uid}-x.md").write_text(
                f"# {uid}: x\n\n> **Status:** Ready\n{size}\n## Acceptance Criteria\n\n"
                "### AC1: it holds\n\n- **Verify:** file src/a.py\n", encoding="utf-8")
        (ws.root / "sdlc-studio" / "retros" / f"{meter.RETRO}-meter.md").write_text(
            f"# RETRO-0001: meter\n\n> **Batch:** {', '.join(points)}\n", encoding="utf-8")
        self.rs.open_run(ws.root, batch=list(points), goal="g")
        self.rs.update(ws.root, sprint_goal="the run states what it cost",
                       plan_snapshot={"units": {uid: {
                           "planned_points": pts or 1, "forecast_minutes": 20.0,
                           "forecast_tokens": 2_000, "added": False}
                           for uid, pts in points.items()}})
        lp._says(ws.tx, "b7", "msg_b7_x", lp.BUILD_X)
        lp._says(ws.tx, "b7", "msg_b7_y", lp.BUILD_Y)
        return ws

    def _records(self, ws) -> dict[str, list[dict]]:
        out: dict[str, list[dict]] = {}
        for r in ws.state().get(self.rs.DELEGATED) or []:
            out.setdefault(r.get("unit"), []).append(r)
        return out

    def _return(self, ws, *extra: str) -> str:
        rc, out = ws.lane("return", "--units", *POINTS, "--agent", "b7", *extra)
        self.assertEqual(0, rc, out)
        return out

    def test_one_agent_total_is_split_by_points_and_each_unit_is_priced(self) -> None:
        """AC1. MUTANTS: the refusal kept (no record at all); an even split (US0103 holds as
        much as US0102); every unit given the whole (the shares sum past it); the shares
        floored with the remainder dropped (they sum short of it); the components or the
        priced figure left whole on each record; the mark left off the record, the line or
        the page's tokens and priced cells."""
        ws = self._three()
        out = self._return(ws)
        parts = meter._sum(lp.BUILD_X, lp.BUILD_Y)
        whole = {"tokens": meter._tokens(parts), "priced": meter._priced(parts)}
        recs = self._records(ws)
        self.assertEqual(set(POINTS), set(recs), out)
        of = sum(POINTS.values())
        for key, total in whole.items():
            with self.subTest(key=key):
                self.assertEqual(total, sum(r[key] for [r] in recs.values()))
                for uid, pts in POINTS.items():
                    self.assertLess(abs(recs[uid][0][key] - total * pts / of), 1, uid)
        for comp, total in parts.items():
            with self.subTest(component=comp):
                self.assertEqual(total, sum(r["components"][comp] for [r] in recs.values()))
        self.assertEqual(whole["tokens"], self.rs.delegated_total(ws.state()),
                         "the lane's total counts once in the run's")
        for uid, pts in POINTS.items():
            [rec] = recs[uid]
            with self.subTest(unit=uid):
                self.assertEqual({"by": "points", "points": pts, "of": of, "units": 3,
                                  "tokens": whole["tokens"]}, rec[self.rs.APPORTIONED])
                self.assertEqual("agent-b7.jsonl", Path(rec["transcript"]).name)
                self.assertIn(f"{uid}: ", out)
        self.assertEqual(3, out.count(f"{SPLIT} ("), out)
        self.assertNotIn("cannot be split", out)
        sr = meter._live("sprint_report")
        page = ws.page()
        rows = {u["unit_id"]["value"]: u for u in next(
            s for s in page["sections"] if s["key"] == "estimates")["unit_rows"]}
        text = sr.render_markdown(page)
        for uid in POINTS:
            [rec] = recs[uid]
            with self.subTest(unit=uid):
                self.assertEqual(rec["tokens"], rows[uid]["eu_tokens"]["value"])
                self.assertEqual(rec["priced"], rows[uid]["eu_priced"]["value"])
                for cell in ("eu_tokens", "eu_priced"):
                    self.assertIn(SPLIT, rows[uid][cell]["label"], cell)
                    self.assertIn(sr._cell(rows[uid][cell]), text, cell)

    def test_a_unit_with_no_points_refuses_the_split_and_records_nothing(self) -> None:
        """MUTANTS: the unsized unit given a share, or the others split among themselves, so a
        total no weight placed lands on the run; the warning not naming the unit."""
        ws = self._three({"US0101": 2, "US0102": None, "US0103": 3})
        rc, out = ws.lane("return", "--units", *POINTS, "--agent", "b7")
        self.assertEqual(0, rc, out)
        self.assertIn("WARNING --agent was not recorded", out)
        self.assertIn("US0102 has no Points", out)
        self.assertEqual({}, self._records(ws))

    def test_a_second_return_replaces_each_share(self) -> None:
        """MUTANT: a share superseding only on the transcript, so the second return's first
        share replaces all three, or on nothing, so each unit counts the lane twice."""
        ws = self._three()
        self._return(ws)
        first = {uid: [r["tokens"] for r in rs] for uid, rs in self._records(ws).items()}
        self.assertEqual(set(POINTS), set(first), "each unit holds its own share")
        self._return(ws)
        self.assertEqual(first, {uid: [r["tokens"] for r in rs]
                                 for uid, rs in self._records(ws).items()})

    def test_a_one_unit_return_is_not_marked_split(self) -> None:
        """The control: one unit priced from its builder's transcript carries no mark, and its
        cells read as they did."""
        ws = self._three()
        rc, out = ws.lane("return", "--units", "US0101", "--agent", "b7")
        self.assertEqual(0, rc, out)
        [rec] = self._records(ws)["US0101"]
        self.assertNotIn(self.rs.APPORTIONED, rec)
        self.assertNotIn(SPLIT, out)
        row = next(u for u in next(s for s in ws.page()["sections"] if s["key"] == "estimates")
                   ["unit_rows"] if u["unit_id"]["value"] == "US0101")
        self.assertEqual(("agent tokens", "priced"),
                         (row["eu_tokens"]["label"], row["eu_priced"]["label"]))

    def test_the_split_page_round_trips(self) -> None:
        """LC-017: a page filed over split shares re-derives to itself at sign. MUTANT: the
        label read from anything the record does not hold, so the re-derivation moves it."""
        sr = meter._live("sprint_report")
        ws = self._three()
        self._return(ws)
        self.rs.update(ws.root, report_gate_clear=list(POINTS))
        self.rs.stamp_tokens(ws.root, "report")
        page = sr.build_report(ws.root, meter.RETRO)
        self.assertIn(SPLIT, sr.render_markdown(page))
        check = sr.revalidate(ws.root, sr.file_report(ws.root, page))
        self.assertTrue(check["valid"], check["changes"])


if __name__ == "__main__":
    unittest.main()
