"""US1000: the cost section states the run's cost in money from the prices frozen at the close.

The page lists each model its Dollar cost row priced with that model's five component prices in
US dollars per million tokens, the entry's effective date and its source, all read from the
page's own price table, beside that model's dollars; and over a meter that leaves delegated
agents' spend out, the Dollar cost row adds the totals read from an agent's transcript at their
models' rates and names a supplied total it cannot price, with its token count. A revision of
the project's `pricing.models` after the close moves nothing on the signed page, and a page
filed before the rule (`PRICES_RULE`) re-derives as it was filed.

Every case drives US1091's fixture harness store (`test_meter_reads_true`) and US1123's fixture
price table (`test_report_usd`): the project's `pricing.models` entry for the session model is
typed here in the fixture's own `.config.yaml`, and every expected dollar figure is formed here
from those typed prices and the fixture's own usage records, never from the code under test.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint_report.py
from __future__ import annotations

import contextlib
import datetime as dt
import io
import json
import re
import subprocess
import sys
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_meter_reads_true as meter  # noqa: E402 - US1091's harness store and workspace
import test_report_usd as usd_case  # noqa: E402 - US1123's typed table and money format
import gitutil  # noqa: E402 - confines the fixture's git calls (LC-020)

OPUS, HAIKU, UNPRICED = usd_case.OPUS, usd_case.HAIKU, usd_case.UNPRICED
#: A model the table prices that the run never used: a price row for it would be a row read
#: from the table rather than from the models the dollars priced.
IDLE = "claude-idle-5-5"
#: The project's own `pricing.models` entry for the session model, typed here: input 15.
CONFIGURED = {"input": 15.0, "output": 75.0, "cache_read": 1.5, "cache_write_5m": 18.75,
              "cache_write_1h": 30.0}
SOURCE = "the operator's own rate card"
#: The configured entry's effective date, ten days before the typed table's entries (dated
#: today): the table's own date is its newest entry's, so a row stating the table's date in
#: place of its entry's reads today on the opus row and fails.
CONFIGURED_ON = (dt.date.today() - dt.timedelta(days=10)).isoformat()
#: The five components in the order the page states them, with their row keys.
COLUMNS = (("price_input", "input"), ("price_output", "output"),
           ("price_cache_write_5m", "cache_write_5m"), ("price_cache_write_1h", "cache_write_1h"),
           ("price_cache_read", "cache_read"))
#: A delegated agent's transcript, read by `lane return --agent`: two opus messages.
AGENT_1 = meter._usage(300, 4_000, 20_000, 0, 600_000)
AGENT_2 = meter._usage(100, 1_000, 5_000, 0, 200_000)
SUPPLIED = 150_000


def _at(model: str, parts: dict, rates: dict) -> float:
    return sum(parts[c] * rates[model][c] for c in meter.COMPONENTS) / 1_000_000


def _price(v: float) -> str:
    return f"${v:,.2f}"


class PricingSnapshotTests(meter._Case):
    def setUp(self) -> None:
        super().setUp()
        self.sr = meter._live("sprint_report")
        self.prices = meter._live("lib.prices")
        path = self.tmp / "prices.json"
        today = dt.date.today().isoformat()
        path.write_text(json.dumps({"models": [
            {"model": m, **p, "effective": today, "source": "typed in the test"}
            for m, p in {**usd_case.PRICES, IDLE: usd_case.PRICES[HAIKU]}.items()]}),
            encoding="utf-8")
        patch = unittest.mock.patch.object(self.prices, "TABLE_PATH", path)
        patch.start()
        self.addCleanup(patch.stop)
        #: The rates the page should state: the typed table with the configured opus entry.
        self.rates = {**usd_case.PRICES, OPUS: CONFIGURED}

    def configure(self, root: Path, input_price: float) -> None:
        """The project's `pricing.models` entry for the session model, at `input_price`."""
        entry = {**CONFIGURED, "input": input_price}
        lines = ["pricing:", "  models:", f"    {OPUS}:"]
        lines += [f"      {k}: {v}" for k, v in entry.items()]
        lines += [f"      effective: '{CONFIGURED_ON}'", f"      source: {SOURCE}"]
        (root / "sdlc-studio" / ".config.yaml").write_text("\n".join(lines) + "\n",
                                                           encoding="utf-8")

    def git(self, root: Path, *argv: str) -> None:
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com",
                        "-c", "commit.gpgsign=false", *argv], cwd=root, check=True,
                       capture_output=True, env=gitutil.git_env())

    def _metered_run(self):
        """US1123's run (opus and haiku on the main thread, US0101 built by agent b7 in haiku,
        read from its transcript), its stories Done, under the configured opus entry; the
        meter reads every subagent transcript."""
        ws = self.workspace()
        self.configure(ws.root, 15)
        ws.open()
        ws.tx._append(ws.tx.main, [usd_case._line("m_opus", usd_case.MAIN_OPUS, OPUS),
                                   usd_case._line("m_haiku", usd_case.MAIN_HAIKU, HAIKU)])
        ws.tx._append(ws.tx.subagents / "agent-b7.jsonl",
                      [usd_case._line("b_1", usd_case.BUILD_1, HAIKU),
                       usd_case._line("b_2", usd_case.BUILD_2, HAIKU)])
        rc, out = ws.lane("return", "--units", "US0101", "--agent", "b7")
        self.assertEqual(0, rc, out)
        self._deliver(ws)
        return ws

    @staticmethod
    def _deliver(ws) -> None:
        for f in (ws.root / "sdlc-studio" / "stories").glob("US*.md"):
            f.write_text(f.read_text(encoding="utf-8").replace("Ready", "Done"),
                         encoding="utf-8")

    def _close(self, ws) -> str:
        """`sprint close`, every chain step but the filing stubbed green; the page's id."""
        import test_lean_close as lean  # noqa: PLC0415 - its close driver
        self.rs.update(ws.root, sprint_goal_verdict={"verdict": "achieved", "note": "it did"})
        mod = meter._live("sprint")
        with lean._green_steps(mod), contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()) as err:
            mod.main(["close", "--retro", meter.RETRO, "--root", str(ws.root)])
        rid = ws.state().get("report")
        self.assertTrue(rid, err.getvalue())
        return rid

    def _delegated_run(self, mixed: bool = False):
        """A run whose meter leaves delegated agents' spend out: the closing reading is taken
        before any subagent transcript exists. Then agent d1's opus transcript is read for
        US0101 (`--agent`) and US0102's builder supplies 150,000 (`--tokens`) with no split;
        `mixed` adds a delegated record whose split collapsed to `mixed`."""
        ws = self.workspace(agents=False)
        self.configure(ws.root, 15)
        ws.open()
        ws.tx._append(ws.tx.main, [usd_case._line("m_opus", usd_case.MAIN_OPUS, OPUS),
                                   usd_case._line("m_free", usd_case.MAIN_UNPRICED, UNPRICED)])
        self.assertIsNotNone(self.rs.stamp_tokens(ws.root, "close"))
        ws.tx._append(ws.tx.subagents / "agent-d1.jsonl",
                      [usd_case._line("d_1", AGENT_1, OPUS), usd_case._line("d_2", AGENT_2, OPUS)])
        for argv in (("--units", "US0101", "--agent", "d1"),
                     ("--units", "US0102", "--tokens", str(SUPPLIED))):
            rc, out = ws.lane("return", *argv)
            self.assertEqual(0, rc, out)
        if mixed:
            held = ws.state()[self.rs.DELEGATED]
            self.rs.update(ws.root, **{self.rs.DELEGATED: held + [{
                "tokens": 9_000, "agent": "m1", "provenance": self.rs.READ_FROM_TRANSCRIPT,
                "priced": 1, "components": meter._parts(AGENT_2),
                self.rs.BY_MODEL: {self.rs.SESSION_MODEL_MIXED: meter._parts(AGENT_2)}}]})
        self._deliver(ws)
        return ws

    @staticmethod
    def _prices(page: dict) -> dict:
        return next(s for s in page["sections"] if s["key"] == "cost_prices")

    def test_close_freezes_prices_and_states_money(self) -> None:
        """AC1. MUTANTS: price rows read from today's config or the shipped table rather than
        the page's `price_table` (the idle model gains a row, or a row drops the configured
        15); a row with no unit or no effective date; rows built from the cost section's stamp
        grouping, which reads `mixed` for this session, rather than the models the dollars
        priced; a model's dollars taken from the run's total; the twin left without the rows; the
        HTML row dropping its Effective, Source or Dollars cell; a row stating the table's own
        (newest) date in place of its entry's, which the opus entry dated apart exposes."""
        sr, ws = self.sr, self._metered_run()
        rid = self._close(ws)
        page = sr.read_report(ws.root, rid)
        table = page[sr.PRICE_TABLE]["models"]
        self.assertEqual(15, table[OPUS]["input"], "premise: the page froze the configured entry")
        sec = self._prices(page)
        self.assertIsNone(sec.get("not_measured"), sec)
        rows = {r["price_model"]["value"]: r for r in sec["rows"]}
        self.assertEqual({OPUS, HAIKU}, set(rows), "each model the Dollar cost row priced, only")
        cost = next(s for s in page["sections"] if s["key"] == "cost")
        self.assertIn(self.rs.SESSION_MODEL_MIXED, [r["model_name"]["value"] for r in
                                                    cost["rows"]],
                      "premise: the stamp grouping reads mixed, so it cannot be the source")
        spent = {OPUS: meter._parts(usd_case.MAIN_OPUS),
                 HAIKU: meter._sum(usd_case.MAIN_HAIKU, usd_case.BUILD_1, usd_case.BUILD_2)}
        for model, row in rows.items():
            for key, comp in COLUMNS:
                self.assertEqual(_price(table[model][comp]), row[key]["value"], (model, key))
                self.assertEqual(_price(self.rates[model][comp]), row[key]["value"])
            self.assertEqual(table[model]["effective"], row["price_effective"]["value"])
            self.assertEqual(table[model]["source"], row["price_source"]["value"])
            self.assertEqual(usd_case._money(_at(model, spent[model], self.rates)),
                             row["price_usd"]["value"], model)
        self.assertEqual("$15.00", rows[OPUS]["price_input"]["value"])
        self.assertEqual(SOURCE, rows[OPUS]["price_source"]["value"])
        newest = max(e["effective"] for e in table.values())
        self.assertNotEqual(newest, table[OPUS]["effective"],
                            "premise: the opus entry is dated apart from the table's own date")
        self.assertEqual(CONFIGURED_ON, rows[OPUS]["price_effective"]["value"],
                         "the opus row states its entry's date, not the table's")
        whole = sum(_at(m, spent[m], self.rates) for m in spent)
        self.assertEqual(usd_case._money(whole), ws.row(page, "Dollar cost")["est_actual"]["value"])
        twin = next((ws.root / "sdlc-studio" / "reports").glob(f"{rid}*.md"))
        for text in (twin.read_text(encoding="utf-8"), sr.render_html(page)):
            self.assertIn("US dollars per million tokens", text)
            for model, row in rows.items():
                cells = [row[k]["value"] for k, _ in COLUMNS] + [
                    row["price_effective"]["value"], row["price_source"]["value"],
                    row["price_usd"]["value"]]
                if text.startswith("<"):
                    # The whole row, all nine cells in order: dropping the Effective, Source
                    # or Dollars cell fails here, not only a price cell.
                    self.assertRegex(text, "".join(
                        [rf'<tr><th scope="row" class="mono">{re.escape(model)}</th>']
                        + [rf'<td class="num">{re.escape(c)}</td>' for c in cells[:5]]
                        + [rf"\s*<td>{re.escape(cells[5])}</td><td>{re.escape(cells[6])}</td>",
                           rf'<td class="num">{re.escape(cells[7])}</td></tr>']), model)
                else:
                    self.assertIn(f"| {model} | " + " | ".join(cells) + " |", text)

    def test_unpriced_tokens_are_named_never_zero_or_estimated(self) -> None:
        """AC2. MUTANTS: the read total left out of the dollars; the supplied total priced at
        the session model's rate or at $0; the supplied tokens left out of the reach clause;
        the read totals priced again over a meter that already read every subagent transcript;
        an unpriced model or a `mixed` split summed in at $0 rather than named with its share."""
        sr, ws = self.sr, self._delegated_run(mixed=True)
        state = ws.state()
        total = self.rs.run_token_total(state)
        self.assertFalse(total["includes_subagents"], "premise: the meter leaves agents out")
        read = meter._sum(AGENT_1, AGENT_2)
        tokens, agents = sr._run_tokens_actual(state, total)
        self.assertEqual(3, agents, "premise: the Tokens row adds the delegated totals")
        page = sr.build_report(ws.root, meter.RETRO)
        sr.file_report(ws.root, page)
        row = ws.row(page, "Dollar cost")
        main = _at(OPUS, meter._parts(usd_case.MAIN_OPUS), self.rates)
        self.assertEqual(usd_case._money(main + _at(OPUS, read, self.rates)),
                         row["est_actual"]["value"], "the read total's dollars are added")
        basis = row["est_basis"]["value"]
        self.assertIn(f"{SUPPLIED:,} tokens", basis)
        self.assertIn("US0102", basis)
        self.assertIn(f"the dollars leave {SUPPLIED:,} tokens unpriced", basis)
        at_session = usd_case._money(main + _at(OPUS, read, self.rates)
                                     + SUPPLIED * CONFIGURED["input"] / 1_000_000)
        self.assertNotEqual(at_session, row["est_actual"]["value"])
        money = basis.replace("never counted as $0", "")
        self.assertIsNone(re.search(r"\$0(\.0+)?(?![.\d])", money), basis)
        self.assertNotIn("$0.0000", sr.render_markdown(page))
        priced = {OPUS: meter._priced(meter._sum(usd_case.MAIN_OPUS, AGENT_1, AGENT_2)),
                  UNPRICED: meter._priced(meter._parts(usd_case.MAIN_UNPRICED)),
                  self.rs.SESSION_MODEL_MIXED: meter._priced(meter._parts(AGENT_2))}
        whole = sum(priced.values())
        for model in (UNPRICED, self.rs.SESSION_MODEL_MIXED):
            self.assertIn(f"{model} ({100 * priced[model] / whole:.1f}% of the priced tokens)",
                          basis)
        self.assertIn(f"covers {100 * priced[OPUS] / whole:.1f}% of the priced tokens", basis)
        self.assertEqual(self.sr.NOT_MEASURED, next(
            u for u in next(s for s in page["sections"] if s["key"] == "estimates")["unit_rows"]
            if u["unit_id"]["value"] == "US0102")["eu_usd"]["value"])
        # Over a meter that reads every subagent transcript, the read total is in the meter's
        # own split already: priced once, and no supplied total is named against the dollars.
        whole_ws = self._metered_run()
        rc, out = whole_ws.lane("return", "--units", "US0102", "--tokens", str(SUPPLIED))
        self.assertEqual(0, rc, out)
        self.assertIsNotNone(self.rs.stamp_tokens(whole_ws.root, "close"))
        self.assertTrue(self.rs.run_token_total(whole_ws.state())["includes_subagents"])
        once = whole_ws.row(whole_ws.page(), "Dollar cost")
        spent = (_at(OPUS, meter._parts(usd_case.MAIN_OPUS), self.rates)
                 + _at(HAIKU, meter._sum(usd_case.MAIN_HAIKU, usd_case.BUILD_1,
                                         usd_case.BUILD_2), self.rates))
        self.assertEqual(usd_case._money(spent), once["est_actual"]["value"])
        self.assertNotIn("unpriced", once["est_basis"]["value"])

    def _signed(self, ws, rid: str) -> None:
        with contextlib.redirect_stdout(io.StringIO()):
            meter._live("sprint")._write_the_signature(ws.root, rid, "Maya Okafor")
        self.git(ws.root, "add", "-A")
        self.git(ws.root, "commit", "-qm", "sign the report")

    def test_a_price_change_after_the_close_moves_nothing(self) -> None:
        """AC3, LC-017's round trip for the price rows. MUTANTS: the rows re-reading today's
        config at re-derivation rather than the page's `price_table`, so the signed page reads
        INVALIDATED in a fresh clone once the entry's input price is 20; the rows left off the
        digest. The control: the clone's own config does price opus input at 20."""
        sr, ws = self.sr, self._metered_run()
        (ws.root / ".gitignore").write_text("sdlc-studio/.local/\n", encoding="utf-8")
        self.git(ws.root, "init", "-q", ".")
        self.git(ws.root, "add", "-A")
        self.git(ws.root, "commit", "-qm", "the delivered batch")
        rid = self._close(ws)
        self.git(ws.root, "add", "-A")
        self.git(ws.root, "commit", "-qm", "file the report")
        self._signed(ws, rid)
        filed = sr.read_report(ws.root, rid)
        dollars = ws.row(filed, "Dollar cost")["est_actual"]["value"]
        self.configure(ws.root, 20)
        self.git(ws.root, "commit", "-qam", "the operator's new rate")
        clone = self.tmp / "fresh"
        self.git(self.tmp, "clone", "-q", f"file://{ws.root}", str(clone))
        self.assertFalse((clone / "sdlc-studio" / ".local").exists(), "premise: a fresh clone")
        self.assertEqual(20, self.prices.load(clone).models[OPUS].input,
                         "control: the clone's config moved the price")
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            rc = sr.main(["--root", str(clone), "check", "--report", rid])
        self.assertEqual(0, rc, out.getvalue())
        self.assertIn("VALID", out.getvalue())
        self.assertNotIn("INVALIDATED", out.getvalue())
        page = sr.read_report(clone, rid)
        row = next(r for r in self._prices(page)["rows"] if r["price_model"]["value"] == OPUS)
        self.assertEqual("$15.00", row["price_input"]["value"])
        self.assertEqual(dollars, ws.row(page, "Dollar cost")["est_actual"]["value"])
        twin = next((clone / "sdlc-studio" / "reports").glob(f"{rid}*.md")).read_text(
            encoding="utf-8")
        self.assertIn(f"| {OPUS} | $15.00 |", twin)
        self.assertNotIn("$20.00", twin)

    def test_a_page_without_a_snapshot_is_unchanged(self) -> None:
        """AC4, LC-017. MUTANTS: the price rows or the delegated dollars emitted for a page
        with no mark for them; the mark dropped from the envelope or hard-wired on in
        `revalidate`; a template printing an empty price block for such a page. The control:
        the later page with its mark removed reads INVALIDATED, not an edited page."""
        sr, ws = self.sr, self._delegated_run()
        before = sr.build_report(ws.root, meter.RETRO, prices_rule=False)
        after = sr.build_report(ws.root, meter.RETRO)
        self.assertEqual(sr.USD_PER_MODEL, before[sr.USD_RULE], "premise: dollars, as RPT0028")
        self.assertIn(sr.PRICE_TABLE, before)
        self.assertNotIn(sr.PRICES_RULE, before)
        self.assertEqual(sr.PRICES_STATED, after[sr.PRICES_RULE])
        self.assertNotIn("cost_prices", [s["key"] for s in before["sections"]])
        self.assertIn("cost_prices", [s["key"] for s in after["sections"]])
        main = _at(OPUS, meter._parts(usd_case.MAIN_OPUS), self.rates)
        read = _at(OPUS, meter._sum(AGENT_1, AGENT_2), self.rates)
        self.assertEqual(usd_case._money(main), ws.row(before, "Dollar cost")["est_actual"]
                         ["value"], "no delegated dollars on the earlier page")
        self.assertNotIn("unpriced", ws.row(before, "Dollar cost")["est_basis"]["value"])
        self.assertEqual(usd_case._money(main + read),
                         ws.row(after, "Dollar cost")["est_actual"]["value"])
        for page, has in ((before, False), (after, True)):
            rid = sr.file_report(ws.root, page)
            check = sr.revalidate(ws.root, rid)
            self.assertTrue(check["valid"], check["changes"])
            twin = next((ws.root / "sdlc-studio" / "reports").glob(f"{rid}*.md")).read_text(
                encoding="utf-8")
            self.assertEqual(sr.render_markdown(sr.read_report(ws.root, rid)), twin)
            for text in (twin, sr.render_html(page)):
                self.assertEqual(has, "US dollars per million tokens" in text)
                self.assertEqual(has, "Prices" in text)
        dropped = {k: v for k, v in after.items() if k not in (sr.PRICES_RULE, "fingerprint")}
        check = sr.revalidate(ws.root, sr.file_report(ws.root, dropped))
        self.assertFalse(check["valid"], "the mark moves the dollars and the rows")
        self.assertEqual([], check["edited"], "INVALIDATED, not an edited page")


if __name__ == "__main__":
    unittest.main()
