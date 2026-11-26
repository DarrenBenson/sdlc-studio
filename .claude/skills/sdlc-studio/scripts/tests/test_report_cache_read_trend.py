"""The run report sets each role's cache-read share against its mean over earlier signed runs.

A fall in a role's cache-read share means a prompt changed and stopped hitting the cache; on its
own page the share has nothing to be read against. The `cache_read_trend` section states, per
role, this run's share (the closing reading the Cost by role table states), the mean over the
five most recent pages signed before this page was generated that state a figure for the role,
the change in points and the pages averaged. A role no earlier page measures reads not
available, never 0.
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import gitutil  # noqa: E402 - the confined git helper
import sprint_report as sr  # noqa: E402
import test_evidence_annex_report as annex  # noqa: E402 - reads the annex as a consumer does
import test_evidence_schema_stamp as stamp  # noqa: E402 - the annex masthead's version
import test_sprint_report as tsr  # noqa: E402 - the fixture run
from lib import run_state  # noqa: E402

REPO = Path(__file__).resolve().parents[5]
#: The page's generation time: every earlier page below is signed before it.
AS_OF = "2026-09-15T14:00:00Z"
OTHER_RUN = "RUN-01OTHERRUN"
NA = "not available"
NO_PAGE = "not available - no earlier signed page states this role's cache-read share"
NO_SHARE = "not available - this run's closing reading states no cache-read share for this role"
ROW_KEYS = ("trend_role", "trend_share", "trend_mean", "trend_change", "trend_runs",
            "trend_pages")

#: The earlier pages, in signing order: (id, signed at, run, builder, repair, shape). The 70.0%
#: page is signed first, so the five newest builder figures leave it out, though it carries the
#: highest report id: newest means newest signature, never highest id. A page the Cost by role
#: table did not measure, a page with no such table and the run's own earlier page sit among
#: them and are passed over.
PAGES = (("RPT0012", "2026-09-01T10:00:00Z", OTHER_RUN, "70.0%", None, "rows"),
         ("RPT0002", "2026-09-02T10:00:00Z", OTHER_RUN, "63.2%", None, "rows"),
         ("RPT0003", "2026-09-03T10:00:00Z", OTHER_RUN, None, None, "not measured"),
         ("RPT0004", "2026-09-04T10:00:00Z", OTHER_RUN, "64.9%", "58.0%", "rows"),
         ("RPT0005", "2026-09-05T10:00:00Z", OTHER_RUN, "67.1%", None, "rows"),
         ("RPT0006", "2026-09-06T10:00:00Z", OTHER_RUN, None, None, "no section"),
         ("RPT0007", "2026-09-07T10:00:00Z", OTHER_RUN, "62.6%", "61.0%", "rows"),
         ("RPT0008", "2026-09-08T10:00:00Z", tsr.FIX_RUN, "10.0%", "10.0%", "rows"),
         ("RPT0009", "2026-09-09T10:00:00Z", OTHER_RUN, "62.9%", None, "rows"),
         # Signed at the very moment the page is generated: not before it, so left out.
         ("RPT0010", AS_OF, OTHER_RUN, "1.0%", "1.0%", "rows"))


def _cell(value: str) -> dict:
    return {"key": "role_cache_read", "value": value, "source": "sdlc-studio/.local/run.json"}


def write_page(root: Path, rid: str, signed_at: str, run_id: str, cells: dict,
               shape: str = "rows") -> None:
    """A signed page whose Cost by role table states `cells` (role -> cache-read cell)."""
    sec = {"key": "cost_roles", "title": "Cost by role", "figures": {}, "not_measured": None,
           "rows": [{"role_name": {"key": "role_name", "value": role, "source": "x"},
                     "role_cache_read": _cell(v)} for role, v in cells.items()]}
    if shape == "not measured":
        sec.update(rows=[], not_measured={"key": "cost_roles", "value": sr.NOT_MEASURED,
                                          "source": "x", "reason": "no reading"})
    page = {"schema": sr.SCHEMA, "report_id": rid, "run_id": run_id,
            "generated_at": signed_at, "sections": [] if shape == "no section" else [sec],
            "signature": {"principal": "Operator <op@example.com>", "signed_at": signed_at,
                          "fingerprint": "f"}}
    d = sr.report_dir(root)
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{rid}.json").write_text(json.dumps(page), encoding="utf-8")


def _role(name: str, cache_read) -> dict:
    return {"role": name, "agents": 1, "calls": 10, "priced": 1000, "share": 0.25,
            "split": {"cache_read": cache_read, "cache_write": 0.1, "output": 0.05},
            "first_context": 1000, "avg_context": 2000}


def stamp_roles(root: Path, roles: dict) -> None:
    """The closing reading records the spend by role, as `stamp_cost_roles` does."""
    st = root / "sdlc-studio" / ".local" / "run-state.json"
    state = json.loads(st.read_text(encoding="utf-8"))
    state[run_state.TOKEN_STAMPS][-1][run_state.COST_ROLES] = {
        "source": "/t/s1.jsonl", "subagent_files": 3,
        "roles": [_role(n, v) for n, v in roles.items()],
        "total": {"agents": 4, "calls": 40, "priced": 4000}}
    st.write_text(json.dumps(state), encoding="utf-8")


def earlier_pages(root: Path) -> None:
    for rid, at, run, builder, repair, shape in PAGES:
        cells = {"builder": builder, "reviewer": NA, "other": "48.0%"} if builder else {}
        if repair:
            cells["repair"] = repair
        write_page(root, rid, at, run, cells, shape)


def trend(page: dict) -> dict:
    return next(s for s in page["sections"] if s["key"] == "cache_read_trend")


def rows_of(sec: dict) -> dict:
    return {r["trend_role"]["value"]: {k: r[k]["value"] for k in ROW_KEYS[1:]}
            for r in sec["rows"]}


class CacheReadTrendTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp(prefix="cache-trend-")
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.root = Path(self.tmp)
        tsr.fixture_run(self.root)
        stamp_roles(self.root, {"builder": 0.40, "reviewer": 0.30, "repair": 0.55,
                                "other": None})
        earlier_pages(self.root)

    def test_each_role_share_stands_beside_its_five_run_mean(self) -> None:
        """AC1. MUTANTS: the oldest five figures for the newest; the pages ordered by report
        id rather than by signing time; five pages taken before their figures are filtered; the
        run's own earlier page averaged; the change from the raw mean; the share sourced
        anywhere but the Cost by role cell it is read from; the basis sentence dropped from
        either twin; the section placed anywhere but after Cost by role."""
        page = sr.build_report(self.root, tsr.FIX_RETRO, as_of=AS_OF)
        keys = [s["key"] for s in page["sections"]]
        self.assertEqual(keys.index("cost_roles") + 1, keys.index("cache_read_trend"))
        sec = trend(page)
        self.assertIsNone(sec["not_measured"])
        got = rows_of(sec)
        self.assertEqual(["builder", "reviewer", "repair", "other"], list(got))
        self.assertEqual({"trend_share": "40.0%", "trend_mean": "64.1%",
                          "trend_change": "-24.1 points", "trend_runs": 5,
                          "trend_pages": "RPT0002, RPT0004, RPT0005, RPT0007, RPT0009"},
                         got["builder"])
        # The mean's source is the pages it averaged, each one a file a reader can open.
        row = next(r for r in sec["rows"] if r["trend_role"]["value"] == "builder")
        self.assertEqual(", ".join(f"sdlc-studio/reports/RPT{n:04d}.json" for n in (2, 4, 5, 7, 9)),
                         row["trend_mean"]["source"])
        self.assertEqual(tsr.FIX_RUN, page["run_id"])
        # The share's source is the Cost by role cell it is read from, this run's own record,
        # never the earlier pages the mean is taken over.
        roles = next(s for s in page["sections"] if s["key"] == "cost_roles")
        cell = next(r for r in roles["rows"] if r["role_name"]["value"] == "builder")
        self.assertIn(tsr.FIX_RUN, cell["role_cache_read"]["source"])
        self.assertEqual(cell["role_cache_read"]["source"], row["trend_share"]["source"])
        # One helper computes the baseline the page states, for the close to read too.
        base = sr.cache_read_baseline(self.root, tsr.FIX_RUN, AS_OF)
        self.assertEqual({"mean": 64.1, "reports": ["RPT0002", "RPT0004", "RPT0005",
                                                    "RPT0007", "RPT0009"]}, base["builder"])
        self.assertNotIn("reviewer", base)
        with self.assertRaises(sr.ReportError):
            sr.cache_read_baseline(self.root, tsr.FIX_RUN, "not a moment")
        # A rise reads with its sign, and no change reads 0.0, never -0.0.
        stamp_roles(self.root, {"builder": 0.70, "repair": 0.595})
        later = rows_of(trend(sr.build_report(self.root, tsr.FIX_RETRO, as_of=AS_OF)))
        self.assertEqual("+5.9 points", later["builder"]["trend_change"])
        self.assertEqual("0.0 points", later["repair"]["trend_change"])
        # Both twins carry the row, in the column order the page states.
        md = sr.render_markdown(page)
        self.assertIn("**Cache-read trend.**", md)
        self.assertIn("beside its mean over the 5 most recent pages signed before this page was "
                      "generated that state the role's share, the run's own pages left out.",
                      " ".join(md.split()))
        self.assertIn("| builder | 40.0% | 64.1% | -24.1 points | 5 | RPT0002, RPT0004, "
                      "RPT0005, RPT0007, RPT0009 |", md)
        html = sr.render_html(page)
        self.assertIn('<th scope="row">builder</th><td class="num">40.0%</td>'
                      '<td class="num">64.1%</td><td class="num">-24.1 points</td>'
                      '<td class="num">5</td><td>RPT0002, RPT0004, RPT0005, RPT0007, '
                      'RPT0009</td>', html)
        self.assertIn("beside its mean over the 5 most recent pages signed before this page was "
                      "generated that state the role's share, the run's own pages left out.",
                      " ".join(html.split()))

    def test_a_role_with_no_earlier_figure_reads_not_available(self) -> None:
        """AC2. MUTANTS: a `not available` cell read as 0; the mean over a role's pages
        padded to five; the change computed over a share the run did not state; a trend
        stated over a Cost by role table that was not measured."""
        page = sr.build_report(self.root, tsr.FIX_RETRO, as_of=AS_OF)
        got = rows_of(trend(page))
        self.assertEqual({"trend_share": "30.0%", "trend_mean": NO_PAGE,
                          "trend_change": NO_PAGE, "trend_runs": 0, "trend_pages": "none"},
                         got["reviewer"])
        self.assertEqual({"trend_share": "55.0%", "trend_mean": "59.5%",
                          "trend_change": "-4.5 points", "trend_runs": 2,
                          "trend_pages": "RPT0004, RPT0007"}, got["repair"])
        self.assertEqual({"trend_share": NA, "trend_mean": "48.0%", "trend_change": NO_SHARE,
                          "trend_runs": 5,
                          "trend_pages": "RPT0002, RPT0004, RPT0005, RPT0007, RPT0009"},
                         got["other"])
        # A cell that states no percentage is passed over, never read as 0.
        self.assertEqual(62.9, sr._cell_pct("62.9%"))
        for cell in ("bad%", NA, sr.NOT_MEASURED, None):
            self.assertIsNone(sr._cell_pct(cell))
        # A malformed earlier page (a row with no role, a nameless role, a role with no cache
        # cell) adds no role and moves no mean.
        d = sr.report_dir(self.root)
        (d / "RPT0011.json").write_text(json.dumps({
            "report_id": "RPT0011", "run_id": OTHER_RUN, "signature": {
                "principal": "op", "signed_at": "2026-09-10T10:00:00Z"},
            "sections": [{"key": "cost_roles", "rows": [
                {"role_cache_read": _cell("50.0%")},
                {"role_name": {"value": ""}, "role_cache_read": _cell("50.0%")},
                {"role_name": {"value": "builder"}}]}]}), encoding="utf-8")
        self.assertEqual({"builder", "repair", "other"},
                         set(sr.cache_read_baseline(self.root, tsr.FIX_RUN, AS_OF)))
        self.assertEqual(rows_of(trend(page)), rows_of(trend(
            sr.build_report(self.root, tsr.FIX_RETRO, as_of=AS_OF))))
        row = next(r for r in trend(page)["rows"] if r["trend_role"]["value"] == "reviewer")
        self.assertEqual("sdlc-studio/reports", row["trend_mean"]["source"])
        for render in (sr.render_markdown, sr.render_html):
            self.assertIn(NO_PAGE, render(page))
        # The unmeasured case: no closing reading recorded the spend by role, so the trend is
        # NOT MEASURED with that reason, and no row reads a share of 0.
        st = self.root / "sdlc-studio" / ".local" / "run-state.json"
        state = json.loads(st.read_text(encoding="utf-8"))
        del state[run_state.TOKEN_STAMPS][-1][run_state.COST_ROLES]
        st.write_text(json.dumps(state), encoding="utf-8")
        gone = sr.build_report(self.root, tsr.FIX_RETRO, as_of=AS_OF)
        sec = trend(gone)
        # Sourced to the reading the Cost by role table consulted, never to the earlier pages.
        consulted = next(s for s in gone["sections"] if s["key"] == "cost_roles")
        self.assertIn(tsr.FIX_RUN, consulted["not_measured"]["source"])
        self.assertEqual(consulted["not_measured"]["source"], sec["not_measured"]["source"])
        self.assertEqual([], sec["rows"])
        self.assertEqual(sr.NOT_MEASURED, sec["not_measured"]["value"])
        self.assertEqual("the Cost by role table is not measured: no closing reading in the "
                         "run's window recorded the spend by role", sec["not_measured"]["reason"])
        for render in (sr.render_markdown, sr.render_html):
            self.assertRegex(render(gone), r"Cache-read trend: NOT MEASURED\S* - the Cost by "
                                           r"role table is not measured")
        # A page filed with no Cost by role section (before its mark) carries no trend either.
        self.assertNotIn("cache_read_trend", [s["key"] for s in sr.build_report(
            self.root, tsr.FIX_RETRO, as_of=AS_OF, usd_rule=False)["sections"]])

    def test_the_section_holds_at_sign_and_an_older_page_renders(self) -> None:
        """AC3. MUTANTS: the baseline taken over every signed page rather than those signed
        before the page was generated; re-derivation building the section for a page filed
        without it."""
        for cmd in (["init", "-q", "."], ["add", "-A"],
                    ["-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false",
                     "commit", "-qm", "the delivered batch"]):
            gitutil.git(cmd, self.root, check=False)
        page = sr.build_report(self.root, tsr.FIX_RETRO, as_of=AS_OF)
        rid = sr.file_report(self.root, page)
        stored = sr.read_report(self.root, rid)
        # After the page is generated, the run's own page and one more page are signed.
        write_page(self.root, "RPT0090", "2026-09-16T10:00:00Z", tsr.FIX_RUN,
                   {"builder": "5.0%", "reviewer": "9.0%"})
        write_page(self.root, "RPT0091", "2026-09-17T10:00:00Z", OTHER_RUN,
                   {"builder": "99.0%", "reviewer": "9.0%"})
        check = sr.revalidate(self.root, rid)
        self.assertTrue(check["valid"], check.get("changes"))
        self.assertEqual([], check["changes"])
        fresh = sr.build_report(self.root, tsr.FIX_RETRO, as_of=stored["generated_at"],
                                window_end=stored.get("window_end"))
        self.assertEqual(trend(stored), trend(fresh))
        self.assertEqual(stored["fingerprint"], sr.fingerprint(fresh))
        # A page filed without the section re-derives without it.
        before = sr.build_report(self.root, tsr.FIX_RETRO, as_of=AS_OF, cache_trend_rule=False)
        self.assertNotIn("cache_read_trend", [s["key"] for s in before["sections"]])
        old = sr.file_report(self.root, before)
        check = sr.revalidate(self.root, old)
        self.assertTrue(check["valid"], check.get("changes"))
        # A committed page filed before the section renders as signed, byte for byte.
        reports = REPO / "sdlc-studio" / "reports"
        signed = json.loads((reports / "RPT0046.json").read_text(encoding="utf-8"))
        self.assertIn("cost_roles", [s["key"] for s in signed["sections"]])
        self.assertNotIn("cache_read_trend", [s["key"] for s in signed["sections"]])
        twin = next(reports.glob("RPT0046-*.md")).read_text(encoding="utf-8")
        self.assertEqual(twin, sr.render_markdown(signed))
        html = sr.render_html(signed)
        self.assertIn("Cost by role", html)
        self.assertNotIn("Cache-read trend", html)

    def test_the_annex_catalogues_the_section_at_version_1_1(self) -> None:
        """AC4. MUTANTS: the section, a figure key or a row key left out of the annex; the
        section listed as conditional, which a page with no Cost by role table never makes it,
        since every page that carries one carries the trend; the note that a page filed before
        the section carries none dropped; the constant or the masthead left at 1.0."""
        sections = annex.keyed("Report sections", "Section")
        row = sections["cache_read_trend"]
        self.assertEqual(("Cache-read trend", "appendix", "always", "-"),
                         (row["Title"], row["Placement"], row["Emitted"], row["Absent when"]))
        # Listed as always, the way `cost_roles` is: the note under the table says a page filed
        # before the section carries none, so such a page still reads as the annex states.
        note = " ".join(" ".join(annex._block("Report sections")).split())
        self.assertIn("one filed before the builder wrote a `cache_read_trend` section carries "
                      "none", note)
        order = list(sections)
        self.assertEqual(order.index("cost_roles") + 1, order.index("cache_read_trend"))
        page = sr.build_report(self.root, tsr.FIX_RETRO, as_of=AS_OF)
        sec = trend(page)
        emitted = {("cache_read_trend", "figures", k) for k in sec["figures"]}
        emitted |= {("cache_read_trend", "rows", k) for r in sec["rows"] for k in r}
        catalogued = {k for k in annex.figure_keys() if k[0] == "cache_read_trend"}
        self.assertEqual(emitted, catalogued)
        self.assertEqual({("cache_read_trend", "rows", k) for k in ROW_KEYS}
                         | {("cache_read_trend", "figures", "trend_basis")}, catalogued)
        self.assertEqual("1.1", stamp.masthead_version())
        self.assertEqual("1.1", sr.EVIDENCE_SCHEMA_VERSION)
        self.assertEqual("1.1", page[run_state.EVIDENCE_SCHEMA])


if __name__ == "__main__":
    unittest.main()
