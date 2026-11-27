"""The sprint report and the seat scorecard state the release change failure rate (US1235).

The page carries a `release_cfr` section after the DORA table and `retro.py seats` one line and
one JSON key, both read through `escape.failure_rate`, the calculation `escape.py failure-rate`
prints: the releases with a linked incident over the releases counted, over the 90 days ending
on the window's end, with a 14-day settling period. The DORA table's own change failure rate
counts CI push runs and is left as it is. Nothing measured reads NOT MEASURED with the
command's reason, never 0%. The section is replayed when a page is re-derived, so a signed page
keeps the figure it was signed with when an incident is linked later, and a page filed before
the section renders as it was signed.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint_report.py
from __future__ import annotations

import contextlib
import functools
import io
import json
import os
import re
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import gitutil  # noqa: E402 - the confined git helper
import test_evidence_annex_report as annex  # noqa: E402 - reads the annex as a consumer does
import test_evidence_schema_stamp as stamp  # noqa: E402 - commit, sign and check a filed page
import test_sprint_report as tsr  # noqa: E402 - the fixture run

KEY = "release_cfr"
RECORDS = "sdlc-studio/reports/releases.jsonl"
CAUSE = ("The review approved a checkout total never tested at the empty basket, so the "
         "boundary shipped unpinned.")
#: The four releases AC1 counts, each settled by the fixture run's window end, 2026-09-15.
SETTLED = (("1.0.0", "2026-06-22"), ("1.1.0", "2026-07-06"), ("1.2.0", "2026-08-03"),
           ("1.3.0", "2026-08-24"))
#: The 90 days ending on the fixture run's window end, both days included.
WINDOW = "2026-06-18 to 2026-09-15 (both days included), 14-day settling period"
RATE = f"25% (1 of 4 releases) over {WINDOW}, pending: none"
ROWS = ["1.0.0", "1.1.0 (incident IS9801; bug BG9801)", "1.2.0", "1.3.0"]
#: The annex fixture's full page: 1.0.0 is outside its window, 1.2.0 inside the settling period.
FULL_RATE = ("0% (0 of 1 releases) over 2026-06-27 to 2026-09-24 (both days included), 14-day "
             "settling period, pending: 1.2.0")
NO_DATE = "carries no Date, so the window is the command's default, ending today"
HOW_KEPT = "a signed one keeps the figures it was filed with"


def records(root: Path, *releases: tuple[str, str], lines: list[str] | None = None) -> None:
    body = lines if lines is not None else [
        json.dumps({"version": v, "date": d, "previous": None, "reports": []})
        for v, d in releases]
    path = root / RECORDS
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(body) + "\n", encoding="utf-8")


def incident(root: Path, iid: str, decomposed: str | None) -> None:
    """An incident: an issue whose Root Cause is written, triaged into `decomposed`."""
    text = f"# {iid}: the checkout fell over\n\n> **Status:** Triaged\n> **Created:** 2026-08-02\n"
    if decomposed:
        text += f"> **Decomposed-into:** {decomposed}\n"
    text += f"\n## Summary\n\nThe checkout fell over.\n\n## Root Cause\n\n{CAUSE}\n"
    d = root / "sdlc-studio" / "issues"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{iid}-the-checkout-fell-over.md").write_text(text, encoding="utf-8")


def bug(root: Path, bid: str, shipped: str) -> None:
    """An escaped bug shipped in `shipped`, raised before every fixture run's window."""
    d = root / "sdlc-studio" / "bugs"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{bid}-the-total-is-wrong.md").write_text(
        f"# {bid}: the total is wrong\n\n> **Status:** Open\n> **Created:** 2026-08-02\n"
        f"> **Escaped:** yes\n> **Shipped-in:** {shipped}\n", encoding="utf-8")


def project(root: Path, releases=SETTLED, incidents: bool = True) -> Path:
    """The fixture run, its release records, IS9801 triaged into BG9801 on v1.1.0, and BG9802,
    escaped on 1.2.0 with no incident, which moves nothing."""
    root.mkdir(parents=True)
    tsr.fixture_run(root)
    if releases:
        records(root, *releases)
    if incidents:
        incident(root, "IS9801", "BG9801")
        bug(root, "BG9801", "v1.1.0")
        bug(root, "BG9802", "1.2.0")
    return root


def section(page: dict, key: str = KEY) -> dict:
    return next(s for s in page["sections"] if s["key"] == key)


def keys_of(page: dict) -> list:
    return [s["key"] for s in page["sections"]]


def block(text: str, start: str, end: str) -> str:
    """The rendering between two headings, refusing a page where they are out of order."""
    i, j = text.index(start), text.index(end)
    if j < i:
        raise AssertionError(f"{end!r} comes before {start!r}")
    return text[i:j]


def cli(mod, argv: list[str]) -> tuple[int, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = mod.main(argv)
    return rc, out.getvalue() + err.getvalue()


class ReportChangeFailureRateTests(unittest.TestCase):

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        patcher = unittest.mock.patch.dict(os.environ, gitutil.git_env(), clear=True)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.sr = annex._live("sprint_report")

    def build(self, root: Path, **kw) -> dict:
        return self.sr.build_report(root, tsr.FIX_RETRO, **kw)

    def renders(self, page: dict) -> list[str]:
        """The section's block in the Markdown twin and the HTML page, each between its DORA
        and Calibration headings."""
        return [block(self.sr.render_markdown(page), "### Release change failure rate",
                      "### Calibration"),
                block(self.sr.render_html(page), "<h3>Release change failure rate</h3>",
                      "<h3>Calibration</h3>")]

    def test_the_report_shows_the_release_rate_with_its_source_records(self) -> None:
        """AC1. MUTANTS: the window ending today rather than on the page's window end; rows over
        the failed releases rather than the counted; a failed release's incident and bug left off
        its row; the counts swapped; a figure citing anything but the release record file; the
        section before DORA or left out of `APPENDIX`; either template's block dropped; the
        release figure written into the DORA table."""
        sr = self.sr
        root = project(self.tmp / "rate")
        bare = self.tmp / "bare"
        bare.mkdir()
        tsr.fixture_run(bare)
        page = self.build(root)
        keys = keys_of(page)
        self.assertEqual(keys.index("dora") + 1, keys.index(KEY))
        self.assertLess(sr.APPENDIX.index("dora"), sr.APPENDIX.index(KEY))
        sec = section(page)
        self.assertIsNone(sec["not_measured"])
        self.assertEqual("Release change failure rate", sec["title"])
        self.assertEqual({"cfr_rate": RATE}, {k: f["value"] for k, f in sec["figures"].items()})
        self.assertEqual(ROWS, [r["cfr_release"]["value"] for r in sec["rows"]])
        self.assertEqual([["cfr_release"]] * 4, [list(r) for r in sec["rows"]])
        cited = [f["source"] for f in sec["figures"].values()]
        cited += [r["cfr_release"]["source"] for r in sec["rows"]]
        self.assertEqual([annex._live("release_cut").RELEASES_REL] * 5, cited)
        self.assertEqual([RECORDS] * 5, cited)
        # The DORA table is the one the same run reads with no release record at all.
        self.assertEqual(section(self.build(bare), "dora"), section(page, "dora"))
        dora = [r for r in section(page, "dora")["rows"]
                if r["dora_key"]["value"] == "Change failure rate"]
        self.assertEqual(1, len(dora))
        md, bare_md = sr.render_markdown(page), sr.render_markdown(self.build(bare))
        row = re.compile(r"(?m)^\| Change failure rate \|.*$")
        self.assertEqual(row.findall(bare_md), row.findall(md))
        block(md, "### DORA", "### Release change failure rate")
        block(sr.render_html(page), "<h3>DORA</h3>", "<h3>Release change failure rate</h3>")
        for text in self.renders(page):
            self.assertIn(RATE, text)
            for value in ROWS:
                self.assertIn(value, text)
            self.assertIn(RECORDS, text)
            self.assertIn("escape.py failure-rate", text)
            self.assertNotIn("NOT MEASURED", text)

    def test_the_seat_scorecard_shows_the_figure_the_command_derives(self) -> None:
        """AC2. MUTANTS: the window ending today rather than on the retro's Date; the figure
        taken from anywhere but `escape.failure_rate`; the scorecard line dropped, or its
        no-Date clause dropped or said of a dated retro."""
        retro, escape = annex._live("retro"), annex._live("escape")
        root = project(self.tmp / "seats")
        seats = ["--root", str(root), "seats", "--id", tsr.FIX_RETRO]
        rc, out = cli(retro, seats + ["--format", "json"])
        self.assertEqual(0, rc, out)
        got = json.loads(out)[KEY]
        rc, out = cli(escape, ["failure-rate", "--root", str(root), "--until", "2026-09-15",
                               "--format", "json"])
        self.assertEqual(0, rc, out)
        command = json.loads(out)
        self.assertEqual(command, {k: v for k, v in got.items() if k != "source"})
        self.assertEqual(RECORDS, got["source"])
        self.assertEqual((25, ["1.0.0", "1.1.0", "1.2.0", "1.3.0"], [], "2026-09-15"),
                         (got["rate_percent"], got["counted"], got["pending"], got["until"]))
        self.assertEqual([{"release": "1.1.0", "incidents": ["IS9801"], "bugs": ["BG9801"]}],
                         got["failed"])
        rc, out = cli(retro, seats)
        self.assertEqual(0, rc, out)
        line = (f"  release change failure rate {RATE}; counted: {', '.join(ROWS)} "
                f"(read from {RECORDS})")
        self.assertIn(line, out.splitlines())
        self.assertNotIn(NO_DATE, out)
        # A project with no release record: the command's own reason, with the window.
        none = project(self.tmp / "none", releases=(), incidents=False)
        reason = escape.failure_rate(none, until="2026-09-15")["not_measured"]
        rc, out = cli(retro, ["--root", str(none), "seats", "--id", tsr.FIX_RETRO])
        self.assertIn(f"  release change failure rate not measured: {reason}; window {WINDOW} "
                      f"(read from {RECORDS})", out.splitlines())
        # No Date, or one the scorecard cannot read: the command's default window, said so.
        path = next((root / "sdlc-studio" / "retros").glob(f"{tsr.FIX_RETRO}*.md"))
        dated = path.read_text(encoding="utf-8")
        sdlc_md = annex._live("lib.sdlc_md")
        for date_line in ("", "> **Date:** soon\n"):
            path.write_text(dated.replace("> **Date:** 2026-09-15\n", date_line),
                            encoding="utf-8")
            with unittest.mock.patch.object(sdlc_md, "now_date", return_value="2026-09-15"):
                rc, out = cli(retro, seats + ["--format", "json"])
                _rc, cmd = cli(escape, ["failure-rate", "--root", str(root), "--format", "json"])
                _rc, text = cli(retro, seats)
            self.assertEqual(json.loads(cmd), {k: v for k, v in json.loads(out)[KEY].items()
                                               if k != "source"}, date_line)
            self.assertIn(f"{line}; {tsr.FIX_RETRO} {NO_DATE}", text.splitlines(), date_line)

    def test_not_measured_and_pending_reach_the_report(self) -> None:
        """AC3. MUTANTS: a record file the command refuses raised through the close rather than
        read NOT MEASURED; the window clause dropped from the reason, or added to a refusal,
        which states no window; NOT MEASURED read as 0%; either template's NOT MEASURED line
        dropped."""
        sr, escape = self.sr, annex._live("escape")
        cases = {
            "none": project(self.tmp / "none", releases=(), incidents=False),
            "pending": project(self.tmp / "pending", releases=(("1.4.0", "2026-09-12"),)),
            "no-incident": project(self.tmp / "no-incident", incidents=False),
        }
        starts = {"none": "no release record in the window",
                  "pending": "every release in the window is still inside the 14-day settling "
                             "period: 1.4.0",
                  "no-incident": "no incident recorded"}
        for name, root in cases.items():
            page = self.build(root)
            nm = section(page)["not_measured"]
            command = escape.failure_rate(root, until="2026-09-15")["not_measured"]
            self.assertTrue(command.startswith(starts[name]), command)
            self.assertEqual(f"{command}; window {WINDOW}", nm["reason"], name)
            self.assertEqual(("NOT MEASURED", RECORDS), (nm["value"], nm["source"]), name)
            self.assertEqual(({}, []), (section(page)["figures"], section(page)["rows"]), name)
            for text in self.renders(page):
                self.assertIn(f"NOT MEASURED</b> - {nm['reason']} (consulted {RECORDS})"
                              if text.startswith("<h3>") else
                              f"NOT MEASURED - {nm['reason']} (consulted {RECORDS})", text)
                self.assertNotIn("0%", text, name)
        # A record line the command cannot read: NOT MEASURED naming it, and the page files.
        bad = project(self.tmp / "bad", releases=(), incidents=False)
        records(bad, lines=["{not json"])
        page = self.build(bad)
        reason = section(page)["not_measured"]["reason"]
        self.assertTrue(reason.startswith(f"{RECORDS} line 1 "), reason)
        self.assertTrue(reason.endswith("; nothing is counted until the record file is "
                                        "corrected, and a close files its page regardless"),
                        reason)
        self.assertNotIn("; window ", reason)
        self.assertTrue(sr.file_report(bad, page).startswith("RPT"))

    def _closed(self, name: str) -> tuple[Path, dict]:
        """The annex fixture's full run, closed through `sprint close` and committed."""
        root = self.tmp / name
        root.mkdir()
        annex._run(root, True)
        page = annex._close(root)
        stamp._commit_all(root, "filed")
        return root, page

    def _link_an_incident(self, root: Path, page: dict) -> None:
        """IS0002 triaged into BG0001 on 1.1.0, the release the page counted: a fresh build over
        the page's own window now reads 100%, so the records did move."""
        incident(root, "IS0002", "BG0001")
        bug(root, "BG0001", "v1.1.0")
        stamp._commit_all(root, "triaged")
        fresh = self.sr.build_report(root, annex.RETRO, as_of=page["generated_at"],
                                     window_end=page["window_end"])
        self.assertTrue(section(fresh)["figures"]["cfr_rate"]["value"]
                        .startswith("100% (1 of 1 releases)"))

    def test_a_signed_page_holds_and_an_older_page_renders(self) -> None:
        """AC4. MUTANTS: the signed page's section not replayed (`_page_readings` handing None,
        or the section ignoring its replay), so the incident moves a signed page; a template
        block not held behind `release_cfr_present`, so an older page refuses a placeholder."""
        sr = self.sr
        root, page = self._closed("signed")
        rid = page["report_id"]
        filed = section(page)
        self.assertEqual(FULL_RATE, filed["figures"]["cfr_rate"]["value"])
        self.assertEqual(["1.1.0"], [r["cfr_release"]["value"] for r in filed["rows"]])
        stamp._sign(root, rid)
        stamp._commit_all(root, "signed")
        self._link_an_incident(root, page)
        self.assertRegex(stamp._check(root, rid), rf"(?m)^VALID: {rid}\b")
        stored = sr.read_report(root, rid)
        self.assertEqual(filed, section(stored))
        for text in (sr.render_markdown(stored), sr.render_html(stored)):
            self.assertIn(FULL_RATE, text)
        # A committed page filed before the section renders as signed, byte for byte.
        reports = annex.REPO / "sdlc-studio" / "reports"
        older = json.loads((reports / "RPT0046.json").read_text(encoding="utf-8"))
        self.assertNotIn(KEY, keys_of(older))
        self.assertIn("dora", keys_of(older))
        twin = next(reports.glob("RPT0046-*.md")).read_text(encoding="utf-8")
        self.assertEqual(twin, sr.render_markdown(older))
        html = sr.render_html(older)
        self.assertIn("<h3>DORA</h3>", html)
        self.assertNotIn("Release change failure rate", html + twin)

    def test_an_unsigned_page_replays_its_own_section(self) -> None:
        """MUTANT: an unsigned page's own section not handed to its re-derivation, so an
        incident triaged between the close and the sign reads INVALIDATED and refuses it."""
        root, page = self._closed("unsigned")
        self._link_an_incident(root, page)
        rid = page["report_id"]
        self.assertRegex(stamp._check(root, rid), rf"(?m)^VALID: {rid}\b")

    def test_a_page_filed_without_the_section_stays_without_it(self) -> None:
        """MUTANTS: re-derivation building the section for a page filed without it; whether
        the page carries it read from the file on disk rather than from the signed page."""
        sr = self.sr
        root = self.tmp / "before"
        root.mkdir()
        annex._run(root, True)
        before = functools.partial(sr.build_report, release_cfr_rule=False)
        with unittest.mock.patch.object(sr, "build_report", before):
            page = annex._close(root)
        rid = page["report_id"]
        self.assertNotIn(KEY, keys_of(page))
        stamp._commit_all(root, "filed")
        stamp._sign(root, rid)
        stamp._commit_all(root, "signed")
        self.assertRegex(stamp._check(root, rid), rf"(?m)^VALID: {rid}\b")
        # A section written onto the page on disk is an edit, never a figure the tree moved.
        path = root / "sdlc-studio" / "reports" / f"{rid}.json"
        stored = json.loads(path.read_text(encoding="utf-8"))
        stored["sections"].append(section(sr.build_report(root, annex.RETRO)))
        path.write_text(json.dumps(stored), encoding="utf-8")
        check = sr.revalidate(root, rid)
        self.assertFalse(check["valid"])
        self.assertEqual([], check["changes"])

    def test_page_readings_carry_the_section(self) -> None:
        """MUTANT: the key left out of either branch of `_page_readings`."""
        sr = self.sr
        self.assertIsNone(sr._page_readings(None)[KEY])
        self.assertIsNone(sr._page_readings({"sections": [{"key": "dora"}]})[KEY])
        sec = {"key": KEY, "figures": {}, "rows": []}
        self.assertIs(sec, sr._page_readings({"sections": [{"key": "dora"}, sec]})[KEY])

    def test_two_incidents_and_two_bugs_read_plural(self) -> None:
        """MUTANT: the row's incident and bug nouns fixed singular, or only the first named."""
        root = project(self.tmp / "plural")
        incident(root, "IS9802", "BG9803")
        bug(root, "BG9803", "1.1.0")
        rows = [r["cfr_release"]["value"] for r in section(self.build(root))["rows"]]
        self.assertEqual("1.1.0 (incidents IS9801, IS9802; bugs BG9801, BG9803)", rows[1])
        self.assertEqual(f"25% (1 of 4 releases) over {WINDOW}, pending: none",
                         section(self.build(root))["figures"]["cfr_rate"]["value"])

    def test_the_window_and_the_settling_period_are_the_commands(self) -> None:
        """MUTANTS: a window wider than 90 days, which counts 0.9.0; no settling period, which
        counts 1.4.0; the pending releases left off the figure."""
        root = project(self.tmp / "window", releases=(("0.9.0", "2026-05-01"), *SETTLED,
                                                      ("1.4.0", "2026-09-12")))
        sec = section(self.build(root))
        self.assertEqual(f"25% (1 of 4 releases) over {WINDOW}, pending: 1.4.0",
                         sec["figures"]["cfr_rate"]["value"])
        self.assertEqual(ROWS, [r["cfr_release"]["value"] for r in sec["rows"]])
        bare = self.tmp / "bare-annex"
        bare.mkdir()
        annex._run(bare, False)
        nm = section(annex._close(bare))["not_measured"]
        self.assertTrue(nm["reason"].startswith("no release record in the window"), nm)

    def test_the_annex_catalogues_the_section(self) -> None:
        """AC5. MUTANTS: the section, its figure or its row key left out of the annex, or listed
        conditional; the note's two clauses dropped; the annex or the constant moved off 1.1."""
        sections = annex.keyed("Report sections", "Section")
        row = sections[KEY]
        self.assertEqual(("Release change failure rate", "appendix", "always", "-"),
                         (row["Title"], row["Placement"], row["Emitted"], row["Absent when"]))
        order = list(sections)
        self.assertEqual(order.index("dora") + 1, order.index(KEY))
        note = " ".join(" ".join(annex._block("Report sections")).split())
        self.assertIn(f"one filed before the builder wrote a `{KEY}` section carries none and "
                      f"{HOW_KEPT}", note)
        self.assertEqual({(KEY, "figures", "cfr_rate"), (KEY, "rows", "cfr_release")},
                         {k for k in annex.figure_keys() if k[0] == KEY})
        self.assertEqual("1.1", self.sr.EVIDENCE_SCHEMA_VERSION)
        self.assertEqual("1.1", stamp.masthead_version())


if __name__ == "__main__":
    unittest.main()
