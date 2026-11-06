"""US1123: the sprint report states each run's and unit's estimated US dollar cost, the retro's
priced line states dollars per point and the price table's date, and the report carries the
per-role table `sprint cost --anatomy` prints.

Every case drives US1091's fixture harness store (`test_meter_reads_true`): the transcripts the
meter reads, `sprint lane return --agent` for a unit's builder, and the page `build_report`
derives. Prices come from a fixture table typed in this module, laid in place of the shipped
one, and the expected dollars are formed here from those typed prices and the fixture's own
usage records, never from the code under test.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint_report.py
from __future__ import annotations

import contextlib
import datetime as dt
import io
import json
import subprocess
import sys
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_meter_reads_true as meter  # noqa: E402 - US1091's harness store and workspace
import gitutil  # noqa: E402 - confines the signed-page test's git calls (BG1255)

OPUS, HAIKU, UNPRICED = meter.MODEL, "claude-haiku-5-5", "model-nobody-prices"
#: US dollars per million tokens, typed here: opus and haiku differ in every component, so a
#: figure priced at one model's rate cannot equal one priced per model.
PRICES = {OPUS: {"input": 4.0, "output": 20.0, "cache_read": 0.4, "cache_write_5m": 5.0,
                 "cache_write_1h": 8.0},
          HAIKU: {"input": 1.0, "output": 5.0, "cache_read": 0.1, "cache_write_5m": 1.25,
                  "cache_write_1h": 2.0}}

#: After the run opens: one opus message on the main thread, one haiku message beside it, and
#: the builder b7's two haiku messages in its own transcript.
MAIN_OPUS = meter._usage(30, 300, 0, 2_000, 80_000)
MAIN_HAIKU = meter._usage(1_000, 20_000, 50_000, 0, 2_000_000)
BUILD_1 = meter._usage(500, 9_000, 40_000, 0, 900_000)
BUILD_2 = meter._usage(200, 3_000, 10_000, 0, 300_000)
MAIN_UNPRICED = meter._usage(400, 6_000, 0, 30_000, 1_000_000)


def _dollars(model: str, parts: dict) -> float:
    return sum(parts[c] * PRICES[model][c] for c in meter.COMPONENTS) / 1_000_000


def _money(v: float) -> str:
    return f"${v:,.2f}" if v >= 1 else f"${v:.4f}"


def _line(msg_id: str, usage: dict, model: str) -> str:
    return json.dumps({"type": "assistant", "cwd": "/work/repo",
                       "message": {"id": msg_id, "model": model, "role": "assistant",
                                   "content": [{"type": "text"}], "usage": usage}})


class ReportUsdTests(meter._Case):
    def setUp(self) -> None:
        super().setUp()
        self.sr = meter._live("sprint_report")
        self.prices = meter._live("lib.prices")
        self.table(dt.date.today())

    def table(self, effective: dt.date, scale: float = 1.0) -> None:
        """Lay the typed table in place of the shipped one, every entry dated `effective` and
        every price times `scale` (a revision of the table)."""
        path = self.tmp / f"prices-{effective.isoformat()}-{scale:g}.json"
        path.write_text(json.dumps({"models": [
            {"model": m, **{c: v * scale for c, v in p.items()},
             "effective": effective.isoformat(), "source": "typed in the test"}
            for m, p in PRICES.items()]}), encoding="utf-8")
        patch = unittest.mock.patch.object(self.prices, "TABLE_PATH", path)
        patch.start()
        self.addCleanup(patch.stop)

    def _run(self, *, unpriced: bool = False, delivered: bool = True):
        """An open run: opus and haiku on the main thread after it opened (and a model no
        table prices, when asked), US0101 built by agent b7 in haiku and returned with
        `--agent`, the stories Done, and a closing reading stamped."""
        ws = self.workspace()
        ws.open()
        ws.tx._append(ws.tx.main, [_line("m_opus", MAIN_OPUS, OPUS),
                                   _line("m_haiku", MAIN_HAIKU, HAIKU)]
                      + ([_line("m_free", MAIN_UNPRICED, UNPRICED)] if unpriced else []))
        ws.tx._append(ws.tx.subagents / "agent-b7.jsonl",
                      [_line("b_1", BUILD_1, HAIKU), _line("b_2", BUILD_2, HAIKU)])
        rc, out = ws.lane("return", "--units", "US0101", "--agent", "b7")
        self.assertEqual(0, rc, out)
        if delivered:
            for f in (ws.root / "sdlc-studio" / "stories").glob("US*.md"):
                f.write_text(f.read_text(encoding="utf-8").replace("Ready", "Done"),
                             encoding="utf-8")
        self.assertIsNotNone(self.rs.stamp_tokens(ws.root, "close"))
        self.assertIsNotNone(self.rs.stamp_cost_roles(ws.root))   # as the close does
        return ws

    def _unit(self, page: dict, uid: str) -> dict:
        est = next(s for s in page["sections"] if s["key"] == "estimates")
        return next(u for u in est["unit_rows"] if u["unit_id"]["value"] == uid)

    def test_run_and_unit_rows_carry_dollars(self) -> None:
        """AC1. MUTANTS: the run's dollars formed from its priced total, or its summed
        components, at one model's rate; a model's dollars dropped from the sum; the unit's
        dollars priced from its priced total rather than its agents' own split; the per-point
        figure over the wrong points. The control: the Priced cost row beside it is unchanged."""
        ws = self._run()
        page = ws.page()
        whole = (_dollars(OPUS, meter._parts(MAIN_OPUS))
                 + _dollars(HAIKU, meter._sum(MAIN_HAIKU, BUILD_1, BUILD_2)))
        at_one_rate = _dollars(OPUS, meter._sum(MAIN_OPUS, MAIN_HAIKU, BUILD_1, BUILD_2))
        self.assertNotEqual(_money(whole), _money(at_one_rate), "premise: the rates differ")
        row = ws.row(page, "Dollar cost")
        self.assertEqual(_money(whole), row["est_actual"]["value"])
        self.assertIn("covers 100.0% of the priced tokens", row["est_basis"]["value"])
        priced = ws.row(page, "Priced cost")["est_actual"]["value"]
        self.assertEqual(meter._priced(meter._sum(MAIN_OPUS, MAIN_HAIKU, BUILD_1, BUILD_2)),
                         priced, "the dollars sit beside the priced tokens they price")
        measures = [r["est_measure"]["value"] for r in ws.estimates(page)]
        self.assertEqual(measures.index("Priced per point") + 1, measures.index("Dollar cost"))
        self.assertEqual(measures.index("Dollar cost") + 1, measures.index("Dollars per point"))
        self.assertEqual(_money(whole / 4), ws.row(page, "Dollars per point")["est_actual"]["value"])
        unit = self._unit(page, "US0101")["eu_usd"]
        self.assertEqual(_money(_dollars(HAIKU, meter._sum(BUILD_1, BUILD_2))), unit["value"])
        self.assertEqual("estimated", unit.get("label"))
        self.assertEqual(self.sr.NOT_MEASURED, self._unit(page, "US0102")["eu_usd"]["value"])
        html = self.sr.render_html(page)
        self.assertIn(self.sr._cell(unit), html)
        self.assertIn(_money(whole), html)
        # The committed twin states the same figures, the unit's dollars beside its id where
        # the HTML's Dollars column stands: the twin is the page of record (LC-018).
        md = self.sr.render_markdown(page)
        self.assertIn("| Unit | Dollars | Forecast minutes |", md)
        self.assertNotIn("| Unit | Forecast minutes |", md, "one unit table, not two")
        self.assertIn(f"| US0101 | {self.sr._cell(unit)} |", md)
        self.assertIn(f"| US0102 | {self.sr._cell(self._unit(page, 'US0102')['eu_usd'])} |", md)
        self.assertIn(f"| Dollar cost | {self.sr._cell(row['est_forecast'])} | {_money(whole)} |",
                      md)

    def test_an_unpriced_model_is_named_with_the_covered_share(self) -> None:
        """AC2. MUTANTS: the unpriced model summed in at $0 with a share of 100%; the model
        left unnamed; the share taken over tokens rather than the priced tokens; a reading
        holding only an unpriced model printing $0 rather than NOT MEASURED."""
        ws = self._run(unpriced=True)
        page = ws.page()
        priced_models = (_dollars(OPUS, meter._parts(MAIN_OPUS))
                         + _dollars(HAIKU, meter._sum(MAIN_HAIKU, BUILD_1, BUILD_2)))
        row = ws.row(page, "Dollar cost")
        self.assertEqual(_money(priced_models), row["est_actual"]["value"])
        everything = meter._priced(meter._sum(MAIN_OPUS, MAIN_HAIKU, BUILD_1, BUILD_2,
                                              MAIN_UNPRICED))
        free = meter._priced(meter._parts(MAIN_UNPRICED))
        basis = row["est_basis"]["value"]
        self.assertIn(f"covers {100 * (everything - free) / everything:.1f}% of the priced "
                      f"tokens", basis)
        self.assertIn(f"{UNPRICED} ({100 * free / everything:.1f}% of the priced tokens)", basis)
        rs = self.rs
        got = rs.usd({UNPRICED: meter._parts(MAIN_UNPRICED)},
                     self.prices.load(path=self.prices.TABLE_PATH))
        self.assertIsNone(got["usd"], "an unpriced reading is never $0")
        self.assertIn(UNPRICED, got["reason"])
        mixed = rs.usd({rs.SESSION_MODEL_MIXED: meter._parts(MAIN_OPUS)},
                       self.prices.load(path=self.prices.TABLE_PATH))
        self.assertIsNone(mixed["usd"], "a collapsed mixed reading is never priced at one rate")
        ws2 = self.workspace(agents=False)
        ws2.open()
        ws2.tx._append(ws2.tx.main, [_line("only_free", MAIN_UNPRICED, UNPRICED)])
        self.rs.stamp_tokens(ws2.root, "close")
        alone = ws2.row(ws2.page(), "Dollar cost")["est_actual"]
        self.assertEqual(self.sr.NOT_MEASURED, alone["value"])
        self.assertIn(UNPRICED, alone["reason"])

    def test_the_retro_line_states_dollars_and_the_table_date(self) -> None:
        """AC3. MUTANTS: the stale mark dropped, or shown on a fresh table; the table's date
        left out; the dollars per point left off the line or formed over the wrong points."""
        retro = meter._live("retro")
        ws = self._run()
        self.rs.update(ws.root, goal="done")   # a build run: only that rung earns a per-point
        cap = retro.run_attributed_tokens(ws.root, meter.RETRO)
        whole = (_dollars(OPUS, meter._parts(MAIN_OPUS))
                 + _dollars(HAIKU, meter._sum(MAIN_HAIKU, BUILD_1, BUILD_2)))

        def line() -> str:
            res = retro.accuracy(ws.root, meter.RETRO, sprint_tokens=cap["tokens"], priced=cap)
            return next(p for p in retro._points_lines(res) if p.startswith("**Priced cost"))
        fresh = line()
        priced = cap["priced"]
        self.assertIn(f"{round(priced / 4):,} per point over 4 delivered points", fresh)
        self.assertIn(f"{_money(whole / 4)} per point", fresh)
        self.assertIn(f"price table effective {dt.date.today().isoformat()}", fresh)
        self.assertNotIn("STALE", fresh)
        old = dt.date.today() - dt.timedelta(days=400)
        self.table(old)
        stale = line()
        self.assertIn(f"price table effective {old.isoformat()} (STALE", stale)
        self.assertIn(f"{_money(whole / 4)} per point", stale)

    def test_the_report_carries_the_per_role_table(self) -> None:
        """AC4. MUTANTS: the report's table formed by a second computation, a column taken from
        another field (cache read for output), a role's cells reformatted, or the reviewer's
        record ignored. The control: the table `sprint cost --anatomy` prints, read off its
        output at the moment of the closing reading the page states it from."""
        critic = meter._live("critic")
        ws = self._run()
        ws.tx._append(ws.tx.subagents / "agent-rv1.jsonl", [_line("r_1", BUILD_2, OPUS)])
        verdicts = [{"unit": "US0101", "verdict": "APPROVE", "reviewer": "rv1", "author": "b7"}]
        with unittest.mock.patch.object(critic, "read_verdicts", return_value=verdicts):
            self.assertIsNotNone(self.rs.stamp_tokens(ws.root, "close"))
            self.assertIsNotNone(self.rs.stamp_cost_roles(ws.root))
            page = ws.page()
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = meter._live("sprint").main(["cost", "--anatomy", "--root", str(ws.root)])
        self.assertEqual(0, rc, out.getvalue())
        printed = {}
        for text in out.getvalue().splitlines():
            cells = text.split()
            if cells and cells[0] in ("orchestrator", "builder", "reviewer", "repair", "other"):
                printed[cells[0]] = [" ".join(cells[1:])]
        sec = next(s for s in page["sections"] if s["key"] == "cost_roles")
        self.assertIsNone(sec.get("not_measured"), sec)
        keys = [k for k, _n, _kind in self.sr.ROLE_COLUMNS]
        mine = {r["role_name"]["value"]: [" ".join(str(r[k]["value"]) for k in keys)]
                for r in sec["rows"]}
        self.assertEqual(printed, mine)
        self.assertNotIn("not available", mine["reviewer"][0].split()[0], "premise: rv1 counted")
        html = self.sr.render_html(page)
        for r in sec["rows"]:
            self.assertIn(f'<th scope="row">{r["role_name"]["value"]}</th>', html)
        # The committed twin carries the same table, cell for cell in the command's column
        # order: AC4 holds on the page of record, not only on the HTML (LC-018).
        md = self.sr.render_markdown(page)
        self.assertIn("**Cost by role.**", md)
        for r in sec["rows"]:
            self.assertIn("| " + " | ".join(str(self.sr._cell(r[k]))
                                            for k in ("role_name", *keys)) + " |", md)
        # The path beside it: a role section NOT MEASURED says so, with its reason, in both.
        gone = json.loads(json.dumps(page))
        roles = next(s for s in gone["sections"] if s["key"] == "cost_roles")
        roles.update(rows=[], not_measured={"reason": "no closing reading recorded one",
                                            "source": "run.json"})
        for render in (self.sr.render_markdown, self.sr.render_html):
            self.assertRegex(render(gone), r"Cost by role: NOT MEASURED\S* - no closing "
                                           r"reading recorded one")

    def test_the_role_table_is_the_close_s_not_the_live_transcript(self) -> None:
        """AC4, at sign. MUTANTS: the table re-derived from the live transcripts through
        `cost_anatomy.anatomy` (it grows after the close, so the page filed there no longer
        re-derives and sign refuses it); the table read from the run's oldest closing reading
        rather than its newest. The control: the same growth taken as a new closing reading
        does move the table."""
        sr = self.sr
        ws = self._run()
        page = sr.build_report(ws.root, meter.RETRO)
        sec = next(s for s in page["sections"] if s["key"] == "cost_roles")
        self.assertIsNone(sec.get("not_measured"), sec)
        rid = sr.file_report(ws.root, page)
        ws.tx._append(ws.tx.main, [_line("m_after", MAIN_OPUS, OPUS)])   # the session goes on
        check = sr.revalidate(ws.root, rid)
        self.assertTrue(check["valid"], check["changes"])
        self.assertIsNotNone(self.rs.stamp_tokens(ws.root, "close"))
        self.assertIsNotNone(self.rs.stamp_cost_roles(ws.root))
        moved = next(s for s in sr.build_report(ws.root, meter.RETRO)["sections"]
                     if s["key"] == "cost_roles")
        self.assertNotEqual(sec["rows"], moved["rows"], "the growth moves a closing reading")

    def _lane_session(self, ws, session: str, usage: dict, model: str | None) -> None:
        """A metered `sprint lane run` session record of US0102, in the shape `lanes._run`
        writes it: the CLI's summed usage and the one model it names (`usage_model`)."""
        parts = meter._parts(usage)
        path = ws.root / meter._live("lib.lanes").RUN_RECORDS / "US0102" / f"{session}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "unit": "US0102", "run_id": ws.state()["run_id"], "harness": "claude",
            "metered": True, "usage_model": model,
            "usage": {"input": parts["input"], "output": parts["output"],
                      "cache_write": parts["cache_write_5m"] + parts["cache_write_1h"],
                      "cache_write_1h": parts["cache_write_1h"],
                      "cache_read": parts["cache_read"]}}), encoding="utf-8")

    def test_a_lane_run_unit_is_priced_at_each_session_s_model(self) -> None:
        """AC1, on the headless delivery path (`sprint lane run`, one record per session).
        MUTANTS: the lane reading's model dropped from its delegated record (round 1: the row
        read NOT MEASURED, "the reading names no model", beside a lane run cost the return had
        just printed); every session priced at one session's rate; a repair's session
        replacing its builder's. The controls: sessions naming no model, or a model the table
        does not price, still read NOT MEASURED with their reasons, never $0."""
        ws = self._run()
        self._lane_session(ws, "s1-builder", BUILD_1, HAIKU)
        self._lane_session(ws, "s2-repair", BUILD_2, OPUS)
        rc, out = ws.lane("return", "--units", "US0102")
        self.assertEqual(0, rc, out)
        each = _dollars(HAIKU, meter._parts(BUILD_1)) + _dollars(OPUS, meter._parts(BUILD_2))
        both = meter._sum(BUILD_1, BUILD_2)
        self.assertNotIn(_money(each), [_money(_dollars(m, both)) for m in (HAIKU, OPUS)]
                         + [_money(_dollars(OPUS, meter._parts(BUILD_2)))],
                         "premise: one rate, or the repair alone, cannot equal the sum")
        got = self._unit(ws.page(), "US0102")["eu_usd"]
        self.assertEqual(_money(each), got["value"], got)
        self.assertEqual("estimated", got.get("label"))
        for model, why in ((None, "no model named"), (UNPRICED, UNPRICED)):
            with self.subTest(model=model):
                self._lane_session(ws, "s1-builder", BUILD_1, model)
                self._lane_session(ws, "s2-repair", BUILD_2, model)
                rc, out = ws.lane("return", "--units", "US0102")
                self.assertEqual(0, rc, out)
                got = self._unit(ws.page(), "US0102")["eu_usd"]
                self.assertEqual(self.sr.NOT_MEASURED, got["value"], got)
                self.assertIn(why, got["reason"])

    def test_a_signed_page_keeps_the_prices_it_was_filed_with(self) -> None:
        """LC-017, the price table's round-trip. MUTANTS: the signed page's table not read
        back (`_page_readings` handing `price_table` None), so the next revision of the table
        re-prices every signed dollar page and `sprint sign`'s check reads it INVALIDATED; the
        table left off the envelope. The control: a live derivation after the revision does
        state the revised dollars, so the table moved."""
        sr, ws = self.sr, self._run()

        def git(*argv: str) -> None:
            subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com",
                            "-c", "commit.gpgsign=false", *argv], cwd=ws.root, check=True,
                           capture_output=True, env=gitutil.git_env())
        git("init", "-q", ".")
        git("add", "-A")
        git("commit", "-qm", "the delivered batch")
        page = sr.build_report(ws.root, meter.RETRO)
        rid = sr.file_report(ws.root, page)
        with contextlib.redirect_stdout(io.StringIO()):
            meter._live("sprint")._write_the_signature(ws.root, rid, "Maya Okafor")
        git("add", "-A")
        git("commit", "-qm", "sign the report")
        self.assertTrue(sr.revalidate(ws.root, rid)["valid"], "premise: valid before")
        signed = ws.row(page, "Dollar cost")["est_actual"]["value"]
        self.table(dt.date.today(), scale=2.0)
        whole = (_dollars(OPUS, meter._parts(MAIN_OPUS))
                 + _dollars(HAIKU, meter._sum(MAIN_HAIKU, BUILD_1, BUILD_2)))
        self.assertEqual(_money(2 * whole), ws.row(ws.page(), "Dollar cost")["est_actual"]
                         ["value"], "control: the revision moves a live derivation")
        check = sr.revalidate(ws.root, rid)
        self.assertTrue(check["valid"], check["changes"])
        self.assertEqual(_money(whole), signed)
        replayed = sr.build_report(ws.root, meter.RETRO, filed=sr.read_report(ws.root, rid))
        self.assertEqual(signed, ws.row(replayed, "Dollar cost")["est_actual"]["value"])

    def test_premium_requests_are_their_own_unit(self) -> None:
        """AC5. MUTANTS: premium requests dropped from the page, added into the tokens or the
        priced tokens, or priced into the dollars. The control: the same run with no premium
        requests states the same tokens and dollars and no premium row."""
        ws = self._run()
        before = ws.page()
        self.assertNotIn("Premium requests",
                         [r["est_measure"]["value"] for r in ws.estimates(before)])

        def asked(state: dict) -> dict:
            stamps = state[self.rs.TOKEN_STAMPS]
            for n, s in enumerate(stamps):
                s[self.rs.PREMIUM_REQUESTS] = 3 if n == 0 else 10
            return state
        self.rs._mutate(ws.root, asked)
        after = ws.page()
        self.assertEqual(7, ws.row(after, "Premium requests")["est_actual"]["value"])
        for measure in ("Tokens", "Priced cost", "Dollar cost"):
            self.assertEqual(ws.row(before, measure)["est_actual"]["value"],
                             ws.row(after, measure)["est_actual"]["value"], measure)
        measures = [r["est_measure"]["value"] for r in ws.estimates(after)]
        self.assertGreater(measures.index("Premium requests"), measures.index("Dollar cost"))

    def test_the_usd_mark_round_trips(self) -> None:
        """LC-017. MUTANTS: the mark dropped from the envelope, so a page filed under it
        re-derives with it off; the rule hard-wired on in `revalidate`; a gated output (the
        dollar rows, the unit's dollar cell, the role section, the price table) built without
        its rule check. The control: the page with its mark removed reads INVALIDATED."""
        sr = self.sr
        ws = self._run()
        page = sr.build_report(ws.root, meter.RETRO)
        self.assertEqual(sr.USD_PER_MODEL, page[sr.USD_RULE])
        self.assertIn(sr.PRICE_TABLE, page)
        check = sr.revalidate(ws.root, sr.file_report(ws.root, page))
        self.assertTrue(check["valid"], check["changes"])
        before = sr.build_report(ws.root, meter.RETRO, usd_rule=False)
        self.assertNotIn(sr.USD_RULE, before)
        self.assertNotIn(sr.PRICE_TABLE, before)
        check = sr.revalidate(ws.root, sr.file_report(ws.root, before))
        self.assertTrue(check["valid"], check["changes"])
        est = next(s for s in before["sections"] if s["key"] == "estimates")
        self.assertEqual([], [r for r in est["rows"] if r["est_measure"]["value"]
                              in ("Dollar cost", "Dollars per point", "Premium requests")])
        self.assertEqual([], [u for u in est["unit_rows"] if "eu_usd" in u])
        self.assertNotIn("cost_roles", [s["key"] for s in before["sections"]])
        for render in (sr.render_markdown, sr.render_html):
            text = render(before)
            self.assertNotIn("Dollar cost", text)
            self.assertNotIn("Cost by role", text)
            self.assertNotIn('class="num">Dollars</th>', text)
            self.assertNotIn("| Dollars |", text)
        self.assertIn('class="num">Dollars</th>', sr.render_html(page))
        self.assertIn("| Unit | Dollars |", sr.render_markdown(page))
        dropped = {k: v for k, v in page.items() if k not in (sr.USD_RULE, "fingerprint")}
        check = sr.revalidate(ws.root, sr.file_report(ws.root, dropped))
        self.assertFalse(check["valid"], "the rule moves no figure on this fixture")
        self.assertEqual([], check["edited"], "INVALIDATED, not an edited page")


if __name__ == "__main__":
    unittest.main()
