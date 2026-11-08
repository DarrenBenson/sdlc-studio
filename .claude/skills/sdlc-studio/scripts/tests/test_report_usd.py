"""US1123: the sprint report states each run's and unit's estimated US dollar cost, the retro's
priced line states dollars per point and the price table's date, and the report carries the
per-role table `sprint cost --anatomy` prints.

Every case drives US1091's fixture harness store (`test_meter_reads_true`): the transcripts the
meter reads, `sprint lane return --agent` for a unit's builder, and the page `build_report`
derives. Prices come from a fixture table typed in this module, laid in place of the shipped
one, and the expected dollars are formed here from those typed prices and the fixture's own
usage records, never from the code under test.

BG1280: a run whose Codex readings bring in a model new to the run prices only that model's own
spend, read through the Codex reader from a fixture store under a temporary HOME and
`CODEX_HOME` (never the real `~/.codex`); and a span over two readings whose splits were
synthesised from one model name each, the names differing, is booked whole, never the opening
reading's history as a delta.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint_report.py
from __future__ import annotations

import contextlib
import datetime as dt
import io
import json
import os
import sqlite3
import subprocess
import sys
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_meter_reads_true as meter  # noqa: E402 - US1091's harness store and workspace
import gitutil  # noqa: E402 - confines the signed-page test's git calls (BG1255)
import test_meter_codex as codex_store  # noqa: E402 - the captured Codex store's columns (BG1280)

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
#: US dollars per Copilot premium request, typed here.
REQUEST_USD = 0.04
#: OpenAI's Standard, short-context rates for two models behind Codex CLI, as its published
#: price page states them (developers.openai.com/api/docs/pricing, read 2026-11-06), typed here
#: and never read from the code under test: gpt-6.1-sol bills its 30-minute and 12-hour cache
#: writes; gpt-5.3-codex lists no cache-write price, so a written prompt token bills as input.
OPENAI = {"gpt-6.1-sol": {"input": 2.0, "output": 10.0, "cache_read": 0.1,
                          "cache_write_5m": 2.5, "cache_write_1h": 5.0},
          "gpt-5.3-codex": {"input": 1.75, "output": 14.0, "cache_read": 0.175,
                            "cache_write_5m": 1.75, "cache_write_1h": 1.75}}
#: A Codex lane session's usage: every component non-zero but the 1-hour write, which the Codex
#: reader does not split out.
CODEX = meter._usage(1_000, 20_000, 50_000, 0, 2_000_000)


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

    def table(self, effective: dt.date, scale: float = 1.0,
              request: float | None = REQUEST_USD) -> None:
        """Lay the typed table in place of the shipped one, every entry dated `effective` and
        every price times `scale` (a revision of the table), with a premium-request price of
        `request` times `scale`, or none when `request` is None."""
        path = self.tmp / f"prices-{effective.isoformat()}-{scale:g}-{request}.json"
        path.write_text(json.dumps({"models": [
            {"model": m, **{c: v * scale for c, v in p.items()},
             "effective": effective.isoformat(), "source": "typed in the test"}
            for m, p in PRICES.items()], **({"premium_request": {
                "usd": request * scale, "effective": effective.isoformat(),
                "source": "typed in the test"}} if request is not None else {})}),
            encoding="utf-8")
        patch = unittest.mock.patch.object(self.prices, "TABLE_PATH", path)
        patch.start()
        self.addCleanup(patch.stop)

    def _run(self, *, unpriced: bool = False, delivered: bool = True, stamped: bool = True):
        """An open run: opus and haiku on the main thread after it opened (and a model no
        table prices, when asked), US0101 built by agent b7 in haiku and returned with
        `--agent`, the stories Done, and a closing reading stamped (unless `stamped` is off,
        for a test whose close takes its own)."""
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
        if stamped:
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

    def _lane_session(self, ws, session: str, usage: dict, model: str | None,
                      harness: str = "claude") -> None:
        """A metered `sprint lane run` session record of US0102, in the shape `lanes._run`
        writes it: the CLI's summed usage and the one model it names (`usage_model`)."""
        parts = meter._parts(usage)
        path = ws.root / meter._live("lib.lanes").RUN_RECORDS / "US0102" / f"{session}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "unit": "US0102", "run_id": ws.state()["run_id"], "harness": harness,
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

    def _whole(self) -> float:
        return (_dollars(OPUS, meter._parts(MAIN_OPUS))
                + _dollars(HAIKU, meter._sum(MAIN_HAIKU, BUILD_1, BUILD_2)))

    def _unsigned(self):
        """The fixture run's page, filed by `file_report` as the close files it, and unsigned."""
        ws = self._run()
        page = self.sr.build_report(ws.root, meter.RETRO)
        rid = self.sr.file_report(ws.root, page)
        self.assertIsNone(self.sr.read_report(ws.root, rid).get("signature"), "premise: unsigned")
        return ws, page, rid

    def test_an_unsigned_page_keeps_the_prices_it_was_filed_with(self) -> None:
        """BG1242 AC1, LC-017's round-trip for a page nobody has signed yet. MUTANTS: the
        filed page's table not handed back (`revalidate` passing `filed_prices` None, or
        `build_report` ignoring it), so a revision of the table between the close and the
        signature re-prices the page and `sprint sign`'s check (`revalidate`) refuses it; the
        mark left off the envelope. The control: a live derivation after the revision states
        the revised dollars, so the table moved."""
        sr = self.sr
        ws, page, rid = self._unsigned()
        self.assertEqual(sr.TABLE_REPLAYED, page[sr.TABLE_RULE])
        whole, built = self._whole(), _dollars(HAIKU, meter._sum(BUILD_1, BUILD_2))
        self.assertEqual(_money(whole), ws.row(page, "Dollar cost")["est_actual"]["value"])
        self.assertEqual(_money(built), self._unit(page, "US0101")["eu_usd"]["value"])
        self.table(dt.date.today(), scale=2.0)
        live = ws.page()
        self.assertEqual(_money(2 * whole), ws.row(live, "Dollar cost")["est_actual"]["value"],
                         "control: the revision moves a live derivation")
        self.assertEqual(_money(2 * built), self._unit(live, "US0101")["eu_usd"]["value"])
        check = sr.revalidate(ws.root, rid)
        self.assertTrue(check["valid"], check["changes"])
        self.assertEqual([], check["changes"], "est_actual and eu_usd re-derive as filed")
        self.assertEqual(page["fingerprint"], check["fingerprint"])

    def test_an_edited_price_table_on_an_unsigned_page_is_named(self) -> None:
        """BG1242 AC2. MUTANTS: the table replayed from the file but left out of the digest
        (`digest_entries` without its envelope entry), so an edit that moves no figure reads
        valid and one that re-prices the dollars reads INVALIDATED rather than edited; the
        fallback naming an unnamed figure rather than the table. The control: the page as
        filed reads valid."""
        sr = self.sr
        ws, page, rid = self._unsigned()
        self.assertTrue(sr.revalidate(ws.root, rid)["valid"], "control: valid as filed")
        path = sr.report_dir(ws.root) / f"{rid}.json"
        filed = path.read_text(encoding="utf-8")

        def edit(change) -> dict:
            stored = json.loads(filed)
            change(stored[sr.PRICE_TABLE]["models"])
            path.write_text(json.dumps(stored, indent=2), encoding="utf-8")
            return sr.revalidate(ws.root, rid)

        quiet = edit(lambda models: models[OPUS].update(source="edited after the close"))
        self.assertFalse(quiet["valid"], "an edit that moves no figure is still an edit")
        self.assertIn(f"envelope.{sr.PRICE_TABLE}", [e["figure"] for e in quiet["edited"]])
        self.assertEqual([], quiet["changes"], "premise: no figure moved")
        loud = edit(lambda models: models[HAIKU].update(input=models[HAIKU]["input"] * 2))
        self.assertFalse(loud["valid"])
        self.assertTrue(any(repr(_money(self._whole())) in e["detail"]
                            for e in loud["edited"]), loud["edited"])

    def test_the_close_itself_files_the_role_table(self) -> None:
        """BG1242 AC3: the close is driven through `sprint.py close`, never by calling
        `stamp_cost_roles` here. MUTANT: `run_state.stamp_cost_roles(root)` in
        `sprint._file_the_report` replaced by `pass`, so the filed page reads the role table NOT
        MEASURED. The control: before the close the run holds no role reading, and a page
        derived then reads the table NOT MEASURED."""
        import test_lean_close as lean  # noqa: PLC0415 - its close driver, every step green
        sr, ws = self.sr, self._run(stamped=False)

        def roles(page: dict) -> dict:
            return next(s for s in page["sections"] if s["key"] == "cost_roles")
        self.assertIsNotNone(roles(ws.page()).get("not_measured"), "control: no reading yet")
        self.rs.update(ws.root, sprint_goal_verdict={"verdict": "achieved", "note": "it did"})
        mod = meter._live("sprint")
        with lean._green_steps(mod), contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()) as err:
            mod.main(["close", "--retro", meter.RETRO, "--root", str(ws.root)])
        rid = ws.state().get("report")
        self.assertTrue(rid, err.getvalue())
        sec = roles(sr.read_report(ws.root, rid))
        self.assertIsNone(sec.get("not_measured"), sec)
        self.assertTrue(sec["rows"], sec)

    def test_staleness_is_judged_on_the_run_s_end_date(self) -> None:
        """BG1242 AC4. MUTANTS: `"today": None` in `build_report`, or `retro._usd_batch`
        pricing with no `today`, so a page or a retro derived after the table turned stale
        marks dollars STALE that were fresh on the day the run ended. The control: on the later
        day the table itself reads stale."""
        retro = meter._live("retro")
        ws = self._run()
        self.rs.update(ws.root, goal="done",
                       ended_at=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
        table, _error = self.rs.price_table(ws.root)
        later = dt.date.today() + dt.timedelta(days=table.stale_after_days + 30)
        real = self.prices.stale
        with unittest.mock.patch.object(self.prices, "stale",
                                        lambda t, today=None: real(t, today or later)):
            self.assertIsNotNone(self.prices.stale(table), "control: stale on the later day")
            basis = ws.row(ws.page(), "Dollar cost")["est_basis"]["value"]
            self.assertIn("price table effective", basis)
            self.assertNotIn("STALE", basis)
            cap = retro.run_attributed_tokens(ws.root, meter.RETRO)
            res = retro.accuracy(ws.root, meter.RETRO, sprint_tokens=cap["tokens"], priced=cap)
            line = next(p for p in retro._points_lines(res) if p.startswith("**Priced cost"))
            self.assertIn("price table effective", line)
            self.assertNotIn("STALE", line)

    def test_the_table_mark_round_trips(self) -> None:
        """LC-017, BG1242's mark. MUTANTS: the rule hard-wired on in `revalidate`, so a page
        filed before the mark is re-derived under it and reads INVALIDATED; the mark built
        without its rule check; the mark dropped from the envelope. The control: the page as
        filed under the mark reads valid."""
        sr = self.sr
        ws = self._run()
        page = sr.build_report(ws.root, meter.RETRO)
        self.assertTrue(sr.revalidate(ws.root, sr.file_report(ws.root, page))["valid"])
        before = sr.build_report(ws.root, meter.RETRO, table_rule=False)
        self.assertNotIn(sr.TABLE_RULE, before)
        self.assertIn(sr.PRICE_TABLE, before, "the table is carried as US1123 carried it")
        self.assertNotEqual(page["fingerprint"], before["fingerprint"], "the table is digested")
        check = sr.revalidate(ws.root, sr.file_report(ws.root, before))
        self.assertTrue(check["valid"], check["changes"])
        dropped = {k: v for k, v in page.items() if k != sr.TABLE_RULE}
        check = sr.revalidate(ws.root, sr.file_report(ws.root, dropped))
        self.assertFalse(check["valid"], "the mark is under the fingerprint it changes")

    def test_a_codex_lane_is_priced_at_its_openai_rate(self) -> None:
        """US1135 AC2, on the shipped table. MUTANTS: a Codex model priced at a Claude rate, at
        zero, or at another OpenAI model's rate; gpt-5.3-codex's cache writes entered at 0 rather
        than the input rate it bills them at, or its note silent on it; an OpenAI model with no
        published price read as $0. The control: that model reads NOT MEASURED, naming it."""
        shipped = Path(self.prices.__file__).resolve().parents[2] / "templates" / \
            "model-prices.json"
        patch = unittest.mock.patch.object(self.prices, "TABLE_PATH", shipped)
        patch.start()
        self.addCleanup(patch.stop)
        notes = {e["model"]: e.get("note", "") for e in json.loads(
            shipped.read_text(encoding="utf-8"))["models"]}
        self.assertIn("billed as input", notes["gpt-5.3-codex"])
        ws = self._run()
        parts = meter._parts(CODEX)
        want = {m: sum(parts[c] * r[c] for c in meter.COMPONENTS) / 1_000_000
                for m, r in OPENAI.items()}
        claude = sum(parts[c] * PRICES[OPUS][c] for c in meter.COMPONENTS) / 1_000_000
        unbilled = sum(parts[c] * OPENAI["gpt-5.3-codex"][c] for c in meter.COMPONENTS
                       if not c.startswith("cache_write")) / 1_000_000
        self.assertEqual(4, len({_money(v) for v in (*want.values(), claude, unbilled)}),
                         "premise: each wrong rate moves the figure")
        for model, usd in want.items():
            with self.subTest(model=model):
                self._lane_session(ws, "s1-builder", CODEX, model, harness="codex")
                rc, out = ws.lane("return", "--units", "US0102")
                self.assertEqual(0, rc, out)
                got = self._unit(ws.page(), "US0102")["eu_usd"]
                self.assertEqual(_money(usd), got["value"], got)
        self._lane_session(ws, "s1-builder", CODEX, "gpt-5.5-codex", harness="codex")
        rc, out = ws.lane("return", "--units", "US0102")
        self.assertEqual(0, rc, out)
        got = self._unit(ws.page(), "US0102")["eu_usd"]
        self.assertEqual(self.sr.NOT_MEASURED, got["value"], got)
        self.assertIn("gpt-5.5-codex", got["reason"])

    def _shipped_table(self):
        """The shipped price table, laid in place of the typed one, and read."""
        shipped = Path(self.prices.__file__).resolve().parents[2] / "templates" / \
            "model-prices.json"
        patch = unittest.mock.patch.object(self.prices, "TABLE_PATH", shipped)
        patch.start()
        self.addCleanup(patch.stop)
        table, error = self.rs.price_table(None)
        self.assertIsNone(error)
        return table

    def test_a_model_new_to_the_run_books_only_its_own_spend(self) -> None:
        """BG1280 AC2, through the Codex reader and the shipped table. Before the run the
        workspace holds 1,010,000 tokens of history on gpt-5.3-codex; the run adds one thread
        on gpt-6.1-sol of 51,000. MUTANTS: the reading named `', '.join(sorted(models))` with
        no split, so the history is booked as a delta under gpt-5.3-codex (the observed $1.89);
        no split carried; the new thread booked under the old thread's model; a split that
        holds a model new to the span booked whole rather than per model."""
        rs, tm = self.rs, meter._live("lib.token_meters")
        home = self.tmp / "codex-home"
        codex, repo = home / ".codex", self.tmp / "codex-repo"
        codex.mkdir(parents=True)
        repo.mkdir()

        def thread(tid: str, model: str, inp: int, cached: int, out: int) -> None:
            usage = {"input_tokens": inp, "cached_input_tokens": cached,
                     "cache_write_input_tokens": 0, "output_tokens": out,
                     "reasoning_output_tokens": 0, "total_tokens": inp + out}
            rollout = codex / f"rollout-{tid}.jsonl"
            rollout.write_text(json.dumps(codex_store.token_count(usage)) + "\n",
                               encoding="utf-8")
            with contextlib.closing(sqlite3.connect(codex / "state_5.sqlite")) as con, con:
                for ddl in (codex_store.THREADS_DDL, codex_store.EDGES_DDL):
                    con.execute(ddl.replace("CREATE TABLE", "CREATE TABLE IF NOT EXISTS", 1))
                con.execute("INSERT INTO threads VALUES (?, ?, 1, 1, 'exec', 'openai', ?, 'OK', "
                            "?, '0.160.0', ?)", (tid, str(rollout), str(repo), inp + out, model))

        with unittest.mock.patch.dict(os.environ):
            for v in (*tm.selection_variables(), "CODEX_HOME"):
                os.environ.pop(v, None)
            os.environ.update({"HOME": str(home), "XDG_DATA_HOME": str(home),
                               "CODEX_HOME": str(codex), "SDLC_STUDIO_HARNESS": "codex",
                               rs.TRANSCRIPTS_ENV: str(self.tmp / "no-transcripts")})
            thread("history", "gpt-5.3-codex", 1_000_000, 0, 10_000)
            opened = rs._stamp(repo, "open")
            thread("run", "gpt-6.1-sol", 60_000, 10_000, 1_000)
            closed = rs._stamp(repo, "close")
        self.assertEqual((opened["tokens"], closed["tokens"]), (1_010_000, 1_061_000))
        total = rs.run_token_total({rs.TOKEN_STAMPS: [{**opened, "at": "2026-11-08T10:00:00Z"},
                                                      {**closed, "at": "2026-11-08T11:00:00Z"}]})
        sol = {"input": 50_000, "output": 1_000, "cache_write_5m": 0, "cache_write_1h": 0,
               "cache_read": 10_000}
        self.assertEqual(total["tokens"], 51_000, total.get("reason"))
        self.assertEqual({m: c for m, c in total[rs.BY_MODEL].items() if any(c.values())},
                         {"gpt-6.1-sol": sol}, "nothing is booked under gpt-5.3-codex")
        table = self._shipped_table()
        got = rs.usd(total[rs.BY_MODEL], table)
        self.assertEqual(([m["model"] for m in got["models"]], got["unpriced"], got["covered"]),
                         (["gpt-6.1-sol"], [], 1.0))
        want = sum(sol[c] * OPENAI["gpt-6.1-sol"][c] for c in meter.COMPONENTS) / 1_000_000
        rows = self.sr._usd_rows(total, [], "state.json",
                                 {"table": table, "error": None, "today": dt.date.today()})
        self.assertEqual(rows[0]["est_actual"]["value"], _money(want), rows[0])

    def test_a_synthesised_split_whose_name_changes_is_not_booked_as_history(self) -> None:
        """BG1280 AC3, for every harness. Two readings carrying no split, each naming one
        model, the names differing: each stamp's split is synthesised from its one name.
        MUTANT: a name absent from one reading read as 0, which books the opening reading's
        1,010,000 tokens of history under its model and the closing reading's whole total under
        the other, both priced in the typed table."""
        rs = self.rs
        history = {"input": 1_000_000, "output": 10_000, "cache_write_5m": 0,
                   "cache_write_1h": 0, "cache_read": 0}
        grown = {**history, "input": 1_050_000, "output": 11_000}
        span = {c: grown[c] - history[c] for c in meter.COMPONENTS}

        def reading(harness: str, model: str, comps: dict) -> dict:
            cap = {"tokens": comps["input"] + comps["output"] + comps["cache_write_5m"]
                   + comps["cache_write_1h"], "components": dict(comps),
                   "priced": rs.price(comps), "model": model, rs.HARNESS: harness,
                   "source": f"{harness}'s store", "basis": "typed in the test"}
            return {**cap, rs.METER: rs.METER_BASIS} if harness == rs.CLAUDE else cap

        table, error = rs.price_table(None)
        self.assertIsNone(error)
        for harness in meter._live("lib.token_meters").HARNESSES:
            with self.subTest(harness=harness):
                stamps = []
                for kind, at, cap in (("open", "2026-11-08T10:00:00Z",
                                       reading(harness, OPUS, history)),
                                      ("close", "2026-11-08T11:00:00Z",
                                       reading(harness, HAIKU, grown))):
                    with unittest.mock.patch.object(rs, "session_tokens", return_value=cap):
                        stamps.append({**rs._stamp(self.tmp, kind), "at": at})
                self.assertEqual(stamps[0][rs.BY_MODEL], {OPUS: history},
                                 "premise: the opening split is synthesised from its name")
                total = rs.run_token_total({rs.TOKEN_STAMPS: stamps})
                self.assertEqual(total["components"], span, total.get("reason"))
                self.assertEqual(total[rs.BY_MODEL], {rs.SESSION_MODEL_MIXED: span})
                got = rs.usd(total[rs.BY_MODEL], table)
                self.assertIsNone(got["usd"], got)
                self.assertEqual([u["model"] for u in got["unpriced"]],
                                 [rs.SESSION_MODEL_MIXED])

    def _ask_premium(self, ws) -> None:
        """Stamp 3 premium requests on the run's first reading and 10 on every later one."""
        def asked(state: dict) -> dict:
            for n, s in enumerate(state[self.rs.TOKEN_STAMPS]):
                s[self.rs.PREMIUM_REQUESTS] = 3 if n == 0 else 10
            return state
        self.rs._mutate(ws.root, asked)

    def test_premium_requests_are_priced_on_their_own_row(self) -> None:
        """US1135 AC4. MUTANTS: the premium dollars summed into the Dollar cost row; the row
        priced at another price than the table's, or without its date; an absent request price
        read as $0. The control: with no request price the row reads not priced and still
        states the count."""
        ws = self._run()
        before = ws.page()
        self._ask_premium(ws)
        after = ws.page()
        row = ws.row(after, "Premium requests")
        self.assertEqual(7, row["est_actual"]["value"])
        basis = row["est_basis"]["value"]
        self.assertIn(f"{_money(7 * REQUEST_USD)} at {_money(REQUEST_USD)} per request", basis)
        self.assertIn(f"effective {dt.date.today().isoformat()}", basis)
        for measure in ("Dollar cost", "Dollars per point"):
            self.assertEqual(ws.row(before, measure)["est_actual"]["value"],
                             ws.row(after, measure)["est_actual"]["value"], measure)
        self.table(dt.date.today(), request=None)
        row = ws.row(ws.page(), "Premium requests")
        self.assertEqual(7, row["est_actual"]["value"])
        self.assertIn("not priced", row["est_basis"]["value"])
        self.assertNotIn("$0", row["est_basis"]["value"])

    def test_the_premium_price_mark_round_trips(self) -> None:
        """LC-017, US1135. MUTANTS: the mark dropped from the envelope, so a page filed under it
        re-derives with it off; the rule hard-wired on in `revalidate`; the request price left
        out of the page's table, so a revision of the table re-prices a filed page. The control:
        the page with its mark removed reads INVALIDATED."""
        sr = self.sr
        ws = self._run()
        self._ask_premium(ws)
        page = sr.build_report(ws.root, meter.RETRO)
        self.assertEqual(sr.PREMIUM_PRICED, page[sr.PREMIUM_USD_RULE])
        self.assertEqual(REQUEST_USD, page[sr.PRICE_TABLE][self.prices.PREMIUM_REQUEST]["usd"])
        filed = sr.file_report(ws.root, page)
        self.table(dt.date.today(), scale=2.0)
        check = sr.revalidate(ws.root, filed)
        self.assertTrue(check["valid"], check["changes"])
        before = sr.build_report(ws.root, meter.RETRO, premium_usd_rule=False)
        self.assertNotIn(sr.PREMIUM_USD_RULE, before)
        self.assertNotIn(self.prices.PREMIUM_REQUEST, before[sr.PRICE_TABLE])
        self.assertNotIn("per request", ws.row(before, "Premium requests")["est_basis"]["value"])
        check = sr.revalidate(ws.root, sr.file_report(ws.root, before))
        self.assertTrue(check["valid"], check["changes"])
        dropped = {k: v for k, v in page.items() if k not in (sr.PREMIUM_USD_RULE, "fingerprint")}
        check = sr.revalidate(ws.root, sr.file_report(ws.root, dropped))
        self.assertFalse(check["valid"], "the rule moves no figure on this fixture")

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
