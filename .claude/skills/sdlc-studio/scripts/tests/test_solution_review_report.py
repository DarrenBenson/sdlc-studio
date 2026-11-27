"""The run report sets first-round approval and rounds per unit for the units that took a
solution review beside the units that did not.

A solution review is a seat's verdict on a builder's approach note before any code, one row per
round in `sdlc-studio/reviews/solution-reviews.md`. The `solution_review` section states two rows:
the units the delivery review judged in the run that took one, and those that did not, each with
its unit count, first-round approvals (no REJECT among the unit's delivery verdicts in the run),
their rate, delivery rounds per unit (verdict rows, as the Delivered table counts them), solution
review rounds per unit and priced tokens per unit. A run where no unit took the step reads NOT
MEASURED, never 0%. The rows are frozen at close, so a row recorded later moves no signed page.
"""
from __future__ import annotations

import importlib.util
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import critic  # noqa: E402
import gitutil  # noqa: E402 - the confined git helper
import sprint_report as sr  # noqa: E402
import test_evidence_annex_report as annex  # noqa: E402 - reads the annex as a consumer does
import test_evidence_schema_stamp as stamp  # noqa: E402 - the annex masthead's version
import test_sprint_report as tsr  # noqa: E402 - the fixture run
from lib import run_state, sdlc_md  # noqa: E402

REPO = Path(__file__).resolve().parents[5]
ANNEX = REPO / ".claude" / "skills" / "sdlc-studio" / "reference-evidence-schema.md"
DAY = "2026-09-15"   # the fixture run's one day
LATER = "2026-09-16"  # the day after it
EARLIER = "2026-09-01"  # a fortnight before it
UNITS = ["US0101", "US0102", "US0103"]
TOOK, NONE, NOT_TAKEN = "took a solution review", "took none", "not taken"
NO_UNIT = "no unit in the run took a solution review"
EMPTY = "no unit in this group was judged by the delivery review in the run"
LEDGER = "sdlc-studio/reviews/solution-reviews.md"
VERDICTS = "sdlc-studio/reviews/critic-verdicts.md"
KEYS = ("sr_group", "sr_units", "sr_first_round", "sr_rate", "sr_delivery_rounds",
        "sr_solution_rounds", "sr_priced")
CONFIG = "review:\n  solution_review:\n    min_points: 3\n"


def section(page: dict) -> dict:
    return next(s for s in page["sections"] if s["key"] == "solution_review")


def values(sec: dict) -> list[dict]:
    return [{k: row[k]["value"] for k in KEYS} for row in sec["rows"]]


def md_section(md: str) -> str:
    """The Markdown twin from the section's lede to the next heading."""
    start = md.index("**Solution review")
    return md[start:md.index("\n###", start)]


def md_table(md: str) -> list[list[tuple]]:
    """The Markdown twin's rows, each keyed by its column heading, in column order."""
    lines = [ln for ln in md_section(md).splitlines() if ln.startswith("|")]
    cells = [[c.strip() for c in ln.strip("|").split("|")] for ln in lines]
    return [list(zip(cells[0], row)) for row in cells[2:]]


def html_table(html: str) -> list[list[tuple]]:
    """The HTML twin's rows, each keyed by its column heading, in column order."""
    start = html.index("<strong>Solution review.</strong>")
    table = html[start:html.index("</table>", start)]
    heads = re.findall(r"<th scope=\"col\"[^>]*>(.*?)</th>", table)
    body = table[table.index("<tbody>"):]
    return [list(zip(heads, re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", row)))
            for row in re.findall(r"<tr>(.*?)</tr>", body)]


class SolutionReviewReportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp(prefix="solution-review-report-")
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.root = Path(self.tmp)
        tsr.fixture_run(self.root)
        cfg = self.root / "sdlc-studio" / ".config.yaml"
        with cfg.open("a", encoding="utf-8") as fh:
            fh.write(CONFIG)
        self.edit_state(batch=list(UNITS))
        self.note = self.root / "note.md"
        self.note.write_text("the approach\n", encoding="utf-8")
        self.changes = self.root / "changes.md"
        self.changes.write_text("read AC1 as the criterion says\n", encoding="utf-8")

    # --- the fixture ------------------------------------------------------------------------

    def edit_state(self, **fields) -> dict:
        st = self.root / "sdlc-studio" / ".local" / "run-state.json"
        state = json.loads(st.read_text(encoding="utf-8"))
        for k, v in fields.items():
            if v is None:
                state.pop(k, None)
            else:
                state[k] = v
        st.write_text(json.dumps(state, indent=2), encoding="utf-8")
        return state

    def delivery(self, rows: list[tuple]) -> None:
        """The delivery ledger, one row per `(unit, verdict[, reviewer[, day]])`."""
        lines = []
        for i, row in enumerate(rows):
            uid, verdict = row[0], row[1]
            who = row[2] if len(row) > 2 else "Rowan Vale"
            day = row[3] if len(row) > 3 else DAY
            lines.append(f"| {uid} | {verdict} | {who} | author-session | {day} | bf{i:04d} "
                         f"| full | {'one issue' if verdict == 'REJECT' else 'none'} |")
        (self.root / VERDICTS).write_text(tsr.VERDICTS + "\n".join(lines) + "\n",
                                          encoding="utf-8")

    def solution(self, uid: str, verdict: str, day: str = DAY,
                 reviewer: str = "Lena Marsh") -> None:
        """One verdict on the unit's approach, through the shipped writer, dated `day`."""
        with mock.patch.object(sdlc_md, "now_date", return_value=day):
            critic.record_solution_review(
                self.root, uid, verdict, self.note, reviewer, "Dani Okafor",
                changes_file=self.changes if verdict == "changes" else None)

    def priced(self, figures: dict) -> None:
        self.edit_state(delegated_tokens=[
            {"tokens": p, "agent": "builder", "note": "", "provenance": "supplied",
             "model": tsr.FIX_MODEL, "unit": uid, "priced": p} for uid, p in figures.items()])

    def build(self, **kw) -> dict:
        return sr.build_report(self.root, tsr.FIX_RETRO, **kw)

    def three_units(self) -> None:
        """AC1's run: CHANGES then GO and a round-one APPROVE; GO and REJECT then APPROVE; no
        solution review and REJECT then APPROVE."""
        self.delivery([("US0101", "APPROVE"), ("US0102", "REJECT"), ("US0102", "APPROVE"),
                       ("US0103", "REJECT"), ("US0103", "APPROVE")])
        self.solution("US0101", "changes")
        self.solution("US0101", "go")
        self.solution("US0102", "go")

    # --- the criteria -----------------------------------------------------------------------

    def test_the_two_groups_stand_side_by_side(self) -> None:
        """AC1. MUTANTS: first-round read as the first row being APPROVE; the REJECT test
        inverted; rounds per unit over every unit rather than the group's; the rate rounded
        down or to even; a unit the delivery review never judged counted; solution review
        rounds read as the highest Round cell, or as rows, rather than the most one seat
        recorded in the run; a seat read from the reviewer's name alone, or from the role group
        alone; a solution row dated outside the run counted as taken; a superseded delivery row,
        or a later run's, counted; the tokens mean taken over the units that have a figure; the
        twins' columns or headings swapped; the lede's first-round rule reworded."""
        self.three_units()
        self.priced({"US0101": 100_000, "US0102": 300_000, "US0103": 250_000})
        page = self.build()
        sec = section(page)
        self.assertIsNone(sec["not_measured"])
        self.assertEqual({}, sec["figures"])
        self.assertEqual(
            [{"sr_group": TOOK, "sr_units": 2, "sr_first_round": 1, "sr_rate": "50%",
              "sr_delivery_rounds": 1.5, "sr_solution_rounds": 1.5, "sr_priced": 200_000},
             {"sr_group": NONE, "sr_units": 1, "sr_first_round": 0, "sr_rate": "0%",
              "sr_delivery_rounds": 2.0, "sr_solution_rounds": NOT_TAKEN,
              "sr_priced": 250_000}], values(sec))
        # Delivery rounds agree with the Delivered table's, unit by unit.
        delivered = next(s for s in page["sections"] if s["key"] == "delivered")
        self.assertEqual({"US0101": 1, "US0102": 2, "US0103": 2},
                         {r["unit_id"]["value"]: r["unit_rounds"]["value"]
                          for r in delivered["rows"]})
        # Each cell names what it is read from: the group from the solution ledger, the counts
        # from the delivery ledger, the tokens from the run record.
        record = page["sections"][0]["figures"]["run_id"]["source"]
        for row in sec["rows"]:
            self.assertEqual({"sr_group": LEDGER, "sr_units": f"{VERDICTS}, {LEDGER}",
                              "sr_first_round": VERDICTS, "sr_rate": VERDICTS,
                              "sr_delivery_rounds": VERDICTS, "sr_solution_rounds": LEDGER,
                              "sr_priced": record}, {k: row[k]["source"] for k in KEYS})
        # Both twins carry the rows and say what the delivery figure counts.
        md = sr.render_markdown(page)
        self.assertIn("| took a solution review | 2 | 1 | 50% | 1.5 | 1.5 | 200,000 |", md)
        self.assertIn("| took none | 1 | 0 | 0% | 2.0 | not taken | 250,000 |", md)
        html = sr.render_html(page)
        self.assertIn('<tr><th scope="row">took a solution review</th><td class="num">2</td>'
                      '<td class="num">1</td><td class="num">50%</td><td class="num">1.5</td>'
                      '<td class="num">1.5</td><td class="num">200,000</td></tr>', html)
        for text in (md, html):
            flat = " ".join(text.split())
            self.assertIn("is approved at its first round when none of its delivery verdicts in "
                          "the run is a REJECT", flat)
            self.assertIn("Delivery rounds count verdict rows, as the Delivered table does", flat)
            self.assertIn("solution review rounds count the most verdicts any one seat recorded "
                          "on a unit's approach in the run, so a panel whose seats each give one "
                          "verdict counts one", flat)
            self.assertIn("the mean, over the group's units, of the priced tokens of the agents "
                          "recorded against each unit", flat)
        # One took unit with no priced record makes the whole cell NOT MEASURED, naming it.
        self.priced({"US0101": 100_000, "US0103": 250_000})
        cell = section(self.build())["rows"][0]["sr_priced"]
        self.assertEqual(sr.NOT_MEASURED, cell["value"])
        self.assertEqual("no agent recorded against US0102 carries a priced figure",
                         cell["reason"])
        # Two seats: qa APPROVE then engineering REJECT is no first-round approval; two
        # APPROVEs are one, at two rounds.
        self.delivery([("US0101", "APPROVE", "Ada Seat"), ("US0101", "REJECT", "Eng Seat"),
                       ("US0101", "APPROVE", "Eng Seat"), ("US0102", "APPROVE", "Ada Seat"),
                       ("US0102", "APPROVE", "Eng Seat"), ("US0103", "APPROVE")])
        got = values(section(self.build()))
        self.assertEqual((2, 1, "50%", 2.5), tuple(got[0][k] for k in KEYS[1:5]))
        self.assertEqual((1, 1, "100%", 1.0), tuple(got[1][k] for k in KEYS[1:5]))
        # Each twin's column under its own heading, in order: every took cell differs.
        self.priced({"US0101": 100_000, "US0102": 300_000, "US0103": 250_000})
        page = self.build()
        heads = ("Group", "Units", "First-round approvals", "Rate", "Delivery rounds per unit",
                 "Solution review rounds per unit", "Priced tokens per unit")
        want = [list(zip(heads, (TOOK, "2", "1", "50%", "2.5", "1.5", "200,000"))),
                list(zip(heads, (NONE, "1", "1", "100%", "1.0", NOT_TAKEN, "250,000")))]
        self.assertEqual(want, md_table(sr.render_markdown(page)))
        self.assertEqual(want, html_table(sr.render_html(page)))
        # A carried unit with a REJECT joins its group, lowering its rate.
        self.edit_state(batch_changes=[{"id": "US0104", "action": "drop",
                                        "reason": "carried at the review cap"}])
        self.delivery([("US0101", "APPROVE"), ("US0102", "REJECT"), ("US0102", "APPROVE"),
                       ("US0103", "APPROVE"), ("US0104", "REJECT")])
        got = values(section(self.build()))
        self.assertEqual((2, 1, "50%", 1.0), tuple(got[1][k] for k in KEYS[1:5]))
        # A solution row dated outside the run's days is not taken; the rate rounds half up.
        self.edit_state(batch_changes=None)
        self.solution("US0103", "go", day=LATER)
        self.delivery([("US0101", "APPROVE"), ("US0102", "APPROVE"), ("US0103", "REJECT"),
                       ("US0103", "APPROVE")])
        got = values(section(self.build()))
        self.assertEqual((NONE, 1, NOT_TAKEN), (got[1]["sr_group"], got[1]["sr_units"],
                                                got[1]["sr_solution_rounds"]))
        self.solution("US0103", "go")
        got = values(section(self.build()))
        self.assertEqual((3, 2, "67%", round(4 / 3, 1)), tuple(got[0][k] for k in KEYS[1:5]))
        # Only its rows in the run count: US0103's round one fell the day after, so it reads
        # one round, not its Round cell of two.
        self.assertEqual(round(4 / 3, 1), got[0]["sr_solution_rounds"])
        self.assertEqual((0, sr.NOT_MEASURED, sr.NOT_MEASURED),
                         (got[1]["sr_units"], got[1]["sr_first_round"], got[1]["sr_rate"]))
        self.assertEqual(EMPTY, section(self.build())["rows"][1]["sr_rate"]["reason"])
        # A superseded delivery row is no round and no verdict: US0103's REJECT retired.
        critic.record_supersession(self.root, "US0103", DAY, "the review ran on another unit",
                                   "Operator", "the operator's own session",
                                   reviewer="Rowan Vale", verdict="REJECT")
        got = values(section(self.build()))
        self.assertEqual((3, 3, "100%", 1.0), tuple(got[0][k] for k in KEYS[1:5]))
        for n, d, want in ((1, 3, "33%"), (2, 3, "67%"), (1, 8, "13%"), (1, 2, "50%"),
                           (0, 1, "0%"), (1, 1, "100%")):
            self.assertEqual(want, sr.whole_percent(n, d), f"{n} of {d}")
        # A panel of two seats agreeing at once is one round, though the writer numbers the
        # second verdict round two; a seat is the Reviewer cell's role, else the reviewer.
        self.solution("US0102", "go", reviewer="Kai Other")
        self.assertEqual([1, 2], [r["round"] for r in critic.read_solution_reviews(
            self.root, "US0102")])
        self.assertEqual(round(4 / 3, 1), values(section(self.build()))[0]["sr_solution_rounds"])
        self.solution("US0101", "go", reviewer="Ada Seat (qa)")
        self.solution("US0101", "go", reviewer="Eng Seat (engineering)")
        self.assertEqual(round(4 / 3, 1), values(section(self.build()))[0]["sr_solution_rounds"])
        # Two holders of one seat are that seat's two rounds.
        self.solution("US0102", "go", reviewer="Bo Seat (qa)")
        self.solution("US0102", "go", reviewer="Cy Seat (qa)")
        self.assertEqual(round(5 / 3, 1), values(section(self.build()))[0]["sr_solution_rounds"])
        # A later run's verdict on the same day is not this run's: US0103's REJECT, after the
        # base a run opened that afternoon recorded, leaves its first-round approval.
        archive = self.root / "sdlc-studio" / ".local" / "run-archive"
        archive.mkdir(parents=True, exist_ok=True)
        (archive / "later.json").write_text(json.dumps(
            {"schema": 1, "run_id": "RUN-LATER", "started_at": f"{DAY}T15:00:00Z",
             run_state.REVIEW_BASE: {"US0103": 1}}), encoding="utf-8")
        self.delivery([("US0101", "APPROVE"), ("US0102", "APPROVE"), ("US0103", "APPROVE"),
                       ("US0103", "REJECT", "Eng Seat")])
        self.assertEqual((3, 3, "100%", 1.0),
                         tuple(values(section(self.build()))[0][k] for k in KEYS[1:5]))
        (archive / "later.json").unlink()
        self.assertEqual((3, 2, "67%", round(4 / 3, 1)),
                         tuple(values(section(self.build()))[0][k] for k in KEYS[1:5]))

    def test_a_run_where_no_unit_took_the_step_reads_not_measured(self) -> None:
        """AC2. MUTANTS: the section measured with no solution row; a row for a unit outside
        the run read as the run's; a took unit with no delivery row read as none taken; the
        missing delivery ledger read as zero rounds."""
        page = self.build()
        sec = section(page)
        self.assertEqual([], sec["rows"])
        self.assertEqual({"key": "solution_review", "value": sr.NOT_MEASURED, "source": LEDGER,
                          "reason": NO_UNIT}, sec["not_measured"])
        shown = f"Solution review: NOT MEASURED** - {NO_UNIT} (consulted {LEDGER})"
        md, html = sr.render_markdown(page), sr.render_html(page)
        self.assertIn(shown, md)
        self.assertIn(f"Solution review: NOT MEASURED</b> - {NO_UNIT} (consulted {LEDGER})",
                      html)
        self.assertNotIn("%", md_section(md))
        # A row for a unit outside the run is not the run's.
        self.solution("US0110", "go")
        self.assertEqual(NO_UNIT, section(self.build())["not_measured"]["reason"])
        # A unit that took the step but was never judged: the run took it, the took row is 0.
        self.delivery([("US0101", "APPROVE"), ("US0102", "REJECT")])
        self.solution("US0103", "go")
        sec = section(self.build())
        self.assertIsNone(sec["not_measured"])
        got = values(sec)
        self.assertEqual((TOOK, 0, sr.NOT_MEASURED, sr.NOT_MEASURED, sr.NOT_MEASURED, sr.NOT_MEASURED,
                          sr.NOT_MEASURED), tuple(got[0][k] for k in KEYS))
        self.assertEqual({k: EMPTY for k in KEYS[2:]},
                         {k: sec["rows"][0][k]["reason"] for k in KEYS[2:]})
        self.assertEqual((NONE, 2, 1, "50%", 1.0), tuple(got[1][k] for k in KEYS[:5]))
        # No delivery ledger: no unit's rounds are known.
        (self.root / VERDICTS).unlink()
        nm = section(self.build())["not_measured"]
        self.assertEqual(sr.NOT_MEASURED, nm["value"])
        self.assertEqual(VERDICTS, nm["source"])
        self.assertEqual(f"no verdict ledger at {VERDICTS}, so no unit's delivery rounds are "
                         f"known", nm["reason"])

    def test_the_section_holds_at_sign_and_an_older_page_renders(self) -> None:
        """AC3. MUTANTS: the frozen rows ignored, or read from the ledger whole without the
        frozen identities; `solution_review_rule` hard-wired on in `revalidate`; the `when` gate
        dropped from either template; the freeze read over every day rather than the run's."""
        self.solution("US0103", "go", day=EARLIER)
        self.three_units()
        for cmd in (["init", "-q", "."], ["add", "-A"],
                    ["-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false",
                     "commit", "-qm", "the delivered batch"]):
            gitutil.git(cmd, self.root, check=False)
        sr.freeze_review_rows(self.root)
        state = run_state.read(self.root)
        self.assertEqual([2, 1, 0], [len(state[sr.SOLUTION_ROWS][u]) for u in UNITS])
        self.assertIn(sr.REVIEW_ROWS, state)
        page = self.build()
        self.assertEqual([(TOOK, 2), (NONE, 1)],
                         [(r["sr_group"], r["sr_units"]) for r in values(section(page))])
        rid = sr.file_report(self.root, page)
        stored = sr.read_report(self.root, rid)
        # After the close: one more GO for US0102 on the run's day, and a duplicated row.
        self.solution("US0102", "go")
        path = self.root / LEDGER
        lines = path.read_text(encoding="utf-8").splitlines()
        path.write_text("\n".join(lines + [lines[-2]]) + "\n", encoding="utf-8")
        check = sr.revalidate(self.root, rid)
        self.assertTrue(check["valid"], check.get("changes"))
        self.assertEqual([], check["changes"])
        fresh = self.build(as_of=stored["generated_at"], window_end=stored.get("window_end"))
        self.assertEqual(section(stored), section(fresh))
        self.assertEqual(stored["fingerprint"], sr.fingerprint(fresh))
        # A frozen row the ledger lost is no round: US0101's round-two GO deleted.
        path.write_text("\n".join(ln for ln in lines if "| US0101 | 2 | GO |" not in ln)
                        + "\n", encoding="utf-8")
        self.assertEqual(1.0, values(section(self.build()))[0]["sr_solution_rounds"])
        path.write_text("\n".join(lines + [lines[-2]]) + "\n", encoding="utf-8")
        # A page filed without the section re-derives without it.
        before = self.build(solution_review_rule=False)
        self.assertNotIn("solution_review", [s["key"] for s in before["sections"]])
        old = sr.file_report(self.root, before)
        check = sr.revalidate(self.root, old)
        self.assertTrue(check["valid"], check.get("changes"))
        self.assertEqual([], check["changes"])
        # A second prepare re-reads the ledger itself, never the earlier freeze.
        sr.freeze_review_rows(self.root)
        self.assertEqual(3, len(run_state.read(self.root)[sr.SOLUTION_ROWS]["US0102"]))
        # The control: a record with no frozen rows reads the ledger live, by the date rule.
        self.edit_state(**{sr.SOLUTION_ROWS: None})
        live = values(section(self.build()))
        self.assertEqual(2.0, live[0]["sr_solution_rounds"])
        # A committed page filed before the section renders as signed, byte for byte.
        reports = REPO / "sdlc-studio" / "reports"
        signed = json.loads((reports / "RPT0046.json").read_text(encoding="utf-8"))
        self.assertNotIn("solution_review", [s["key"] for s in signed["sections"]])
        twin = next(reports.glob("RPT0046-*.md")).read_text(encoding="utf-8")
        self.assertEqual(twin, sr.render_markdown(signed))
        html = sr.render_html(signed)
        self.assertIn("Calibration", html)
        for text in (twin, html):
            self.assertNotIn("Solution review", text)
            self.assertNotIn("{{", text)

    def test_the_annex_catalogues_the_section(self) -> None:
        """AC4. MUTANTS: the section, or a row key, left out of the annex; the section listed
        as conditional or out of page order; the note that a page filed before it carries none
        dropped; the solution rounds meaning back to the Round cell; the constant or the
        masthead moved off 1.1; the annex over its ceiling."""
        sections = annex.keyed("Report sections", "Section")
        row = sections["solution_review"]
        self.assertEqual(("Solution review", "appendix", "always", "-"),
                         (row["Title"], row["Placement"], row["Emitted"], row["Absent when"]))
        order = list(sections)
        self.assertEqual(order.index("calibration") + 1, order.index("solution_review"))
        note = " ".join(" ".join(annex._block("Report sections")).split())
        self.assertIn("one filed before the builder wrote a `solution_review` section carries "
                      "none", note)
        self.three_units()
        page = self.build()
        keys = [s["key"] for s in page["sections"]]
        self.assertEqual(keys.index("calibration") + 1, keys.index("solution_review"))
        self.assertIn("solution_review", sr.APPENDIX)
        md = sr.render_markdown(page)
        self.assertLess(md.index("### Calibration"), md.index("**Solution review.**"))
        self.assertLess(md.index("**Solution review.**"), md.index("### Rulings"))
        sec = section(page)
        emitted = {("solution_review", "figures", k) for k in sec["figures"]}
        emitted |= {("solution_review", "rows", k) for r in sec["rows"] for k in r}
        catalogued = {k for k in annex.figure_keys() if k[0] == "solution_review"}
        self.assertEqual({("solution_review", "rows", k) for k in KEYS}, catalogued)
        self.assertEqual(emitted, catalogued)
        meanings = {r["Row key"].strip("`"): r["Meaning"] for r in annex.annex_table(
            "Report row keys") if r["Section"] == "`solution_review`"}
        self.assertIn("verdict rows", meanings["sr_delivery_rounds"])
        self.assertIn(LEDGER, meanings["sr_solution_rounds"])
        self.assertIn("one seat recorded for the unit (the Reviewer cell's role, else the "
                      "reviewer), so a panel agreeing at once counts one",
                      meanings["sr_solution_rounds"])
        self.assertEqual("1.1", stamp.masthead_version())
        self.assertEqual("1.1", sr.EVIDENCE_SCHEMA_VERSION)
        self.assertEqual("1.1", page[run_state.EVIDENCE_SCHEMA])
        spec = importlib.util.spec_from_file_location("check_budgets",
                                                      REPO / "tools" / "check_budgets.py")
        budgets = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(budgets)
        lines = len(ANNEX.read_text(encoding="utf-8").splitlines())
        ceiling = budgets.ALLOWLIST[ANNEX.name] * budgets.CEILING_TOLERANCE
        self.assertLessEqual(lines, ceiling, f"the annex is {lines} lines")


if __name__ == "__main__":
    unittest.main()
