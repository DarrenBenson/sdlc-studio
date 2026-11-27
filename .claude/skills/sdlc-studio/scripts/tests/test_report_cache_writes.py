"""The run report states each role's cache-write growth and re-writes after the cache lifetime.

`sprint cost --anatomy` splits each role's cache writes into growth and the writes re-written
after a gap longer than the cache's lifetime. The closing reading keeps that split
(`run_state.stamp_cost_roles`), and the `cost_cache_writes` appendix section states it per role
with the re-write share of the role's cache writes, so the page of record says how much cache
spend each role lost to waiting. The run cases close over the session of
`test_cost_anatomy_rewrites`, whose figures are formed there from the fixture's own writes.
"""
from __future__ import annotations

import contextlib
import io
import json
import re
import sys
import unittest
import unittest.mock
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import gitutil  # noqa: E402 - the confined git helper
import test_cost_anatomy_rewrites as rw  # noqa: E402 - the session whose split is known
import test_evidence_annex_report as annex  # noqa: E402 - reads the annex as a consumer does
import test_evidence_schema_stamp as stamp  # noqa: E402 - the annex masthead's version
import test_meter_reads_true as meter  # noqa: E402 - the harness store and workspace
import test_report_cache_read_trend as trend  # noqa: E402 - a closing reading stamped by hand
import test_sprint_report as tsr  # noqa: E402 - the fixture run

KEY = "cost_cache_writes"
ROW_KEYS = ("writes_role", "writes_growth", "writes_rewrite_5m", "writes_rewrite_1h",
            "writes_rewrite_share")
NA = "not available"
NO_CACHE = "not available - this role wrote no cache"
NO_SPLIT = "the run's closing reading recorded no cache-write split by role"
#: US1337's session: the main thread's 2,000 and 500 1-hour writes are growth and its 9,000,
#: 61 minutes after the call before it, a re-write (9,000 of 11,500 is 78.3%); the builder's
#: 3,000, 400 and 400 5-minute writes are growth and its 4,000, 6 minutes on, a re-write (4,000
#: of 7,800 is 51.3%). No other role writes.
SPLIT = {"orchestrator": ("2,500", "0", "9,000", "78.3%"),
         "builder": ("3,800", "4,000", "0", "51.3%"),
         "reviewer": ("0", "0", "0", NO_CACHE), "repair": ("0", "0", "0", NO_CACHE),
         "other": ("0", "0", "0", NO_CACHE)}
#: What growth and a re-write are, as the section's `writes_basis` defines them.
BASIS = ("growth is a call's cache write within its kind's lifetime of the call before it in "
         "its transcript (300 seconds for cache_write_5m, 3,600 seconds for cache_write_1h), "
         "and a re-write follows a longer gap and counts the call's whole write, so it "
         "overstates by one turn")
#: The paragraph both twins open the section with, after its bold title.
LEDE = ("Each role's cache writes at the run's closing reading, in tokens, split into growth "
        f"and re-writes after expiry: {BASIS}. The re-write share is the role's re-writes over "
        "its cache writes. A role reads not available when any agent in it has a model call's "
        "usage record with no readable timestamp or no message id, and the share of a role "
        "that wrote no cache reads not available, never 0.")
HEADS = ("Role", "Growth", "Re-written after five-minute expiry",
         "Re-written after one-hour expiry", "Re-write share")


def section(page: dict, key: str = KEY) -> dict:
    return next(s for s in page["sections"] if s["key"] == key)


def rows_of(sec: dict) -> dict:
    return {r["writes_role"]["value"]: tuple(r[k]["value"] for k in ROW_KEYS[1:])
            for r in sec["rows"]}


def keys_of(page: dict) -> list:
    return [s["key"] for s in page["sections"]]


def stamp_split(root: Path, splits: dict, keyed: bool = True) -> None:
    """The closing reading records the spend by role with each role's `splits` value, keyed
    under `cache_writes` (or, when `keyed` is off, the roles named in `splits` keyed and the
    rest stamped as a reading taken before the split carries none)."""
    trend.stamp_roles(root, {"builder": 0.4, "reviewer": 0.3, "repair": 0.5, "other": 0.2})
    st = root / "sdlc-studio" / ".local" / "run-state.json"
    state = json.loads(st.read_text(encoding="utf-8"))
    roles = state[meter._live("lib.run_state").TOKEN_STAMPS][-1]["cost_roles"]["roles"]
    for role in roles:
        if role["role"] in splits:
            role["cache_writes"] = splits[role["role"]]
    st.write_text(json.dumps(state), encoding="utf-8")


class CacheWritesReportTests(meter._Case):
    def setUp(self) -> None:
        super().setUp()
        self.sr = meter._live("sprint_report")

    def _closed(self, name: str):
        """US1337's session in a run opened a minute before its first call, the subagent
        returned as US0101's builder, and a closing reading stamped as the close stamps it. The
        run's opening reading carries a decoy split the page must not state."""
        ws = self._timed(name)
        ws.tx._append(ws.tx.main, rw._calls(rw.MAIN))
        ws.tx._append(ws.tx.subagents / "agent-s1.jsonl", rw._calls(rw.BUILDER))
        sdlc_md = meter._live("lib.sdlc_md")
        opened = (meter.T0 - timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        with unittest.mock.patch.object(sdlc_md, "now_iso8601", return_value=opened):
            ws.open()
        rc, out = ws.lane("return", "--units", "US0101", "--agent", "s1")
        self.assertEqual(0, rc, out)
        st = ws.root / "sdlc-studio" / ".local" / "run-state.json"
        state = json.loads(st.read_text(encoding="utf-8"))
        state[self.rs.TOKEN_STAMPS][0][self.rs.COST_ROLES] = {
            "source": "decoy", "subagent_files": 0, "total": {},
            "roles": [{**trend._role("orchestrator", 0.5), "cache_writes": rw._split(1, 1, 1)}]}
        st.write_text(json.dumps(state), encoding="utf-8")
        self.assertIsNotNone(self.rs.stamp_tokens(ws.root, "close"))
        self.assertIsNotNone(self.rs.stamp_cost_roles(ws.root))   # as the close does
        return ws

    def test_the_page_states_each_roles_split_from_the_closing_reading(self) -> None:
        """AC1. MUTANTS: `cache_writes` left out of `run_state._ROLE_KEYS`, so the closing stamp
        drops the split and the section reads NOT MEASURED; a column read from another kind;
        the share's numerator or denominator missing a kind; a role that wrote no cache read
        0.0% or its whole row not available; the section left off the page; the oldest
        closing reading read rather than the newest (the decoy); either template's row
        dropped; the whole record read rather than the window's (`state` for `metered`), so
        a reading after the window's end is stated; the basis's lifetimes or its "longer gap"
        changed; either twin's column headings swapped, its basis dropped from the lede, or
        its share defined over anything but the role's cache writes."""
        sr = self.sr
        ws = self._closed("closing")
        page = ws.page()
        sec = section(page)
        self.assertIsNone(sec.get("not_measured"), sec)
        self.assertEqual(SPLIT, rows_of(sec))
        self.assertEqual(["cost_roles", "cache_read_trend", KEY],
                         keys_of(page)[keys_of(page).index("cost_roles"):][:3])
        self.assertEqual(BASIS, sec["figures"]["writes_basis"]["value"])
        # Both twins carry the definitions, the basis after its colon, and the columns in order.
        md, html = sr.render_markdown(page), sr.render_html(page)
        self.assertIn(f"**Cache writes by role.** {LEDE}", " ".join(md.split()))
        self.assertIn(f'<p class="lede"><strong>Cache writes by role.</strong> {LEDE}</p>', html)
        self.assertIn("| " + " | ".join(HEADS) + " |", md)
        self.assertIn(f'<thead><tr><th scope="col">{HEADS[0]}</th>'
                      + "".join(f'<th scope="col" class="num">{h}</th>' for h in HEADS[1:])
                      + "</tr></thead>", html)
        for role, cells in SPLIT.items():
            self.assertIn(f"| {role} | " + " | ".join(cells) + " |", md)
            self.assertIn(f'<tr><th scope="row">{role}</th>'
                          + "".join(f'<td class="num">{c}</td>' for c in cells) + "</tr>", html)
        # A reading stamped after the window's end is not the page's: the section and the Cost
        # by role table read the window's newest.
        st = ws.root / "sdlc-studio" / ".local" / "run-state.json"
        state = json.loads(st.read_text(encoding="utf-8"))
        closing = state[self.rs.TOKEN_STAMPS][-1]
        end = closing["at"]
        later = (sr._at(end) + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        state[self.rs.TOKEN_STAMPS].append({**closing, "at": later, self.rs.COST_ROLES: {
            **closing[self.rs.COST_ROLES],
            "roles": [{**r, "cache_writes": rw._split(7, 7, 7)}
                      for r in closing[self.rs.COST_ROLES]["roles"]]}})
        st.write_text(json.dumps(state), encoding="utf-8")
        held = sr.build_report(ws.root, meter.RETRO, window_end=end)
        self.assertEqual(SPLIT, rows_of(section(held)))
        self.assertEqual(section(page, "cost_roles")["rows"], section(held, "cost_roles")["rows"])
        moved = sr.build_report(ws.root, meter.RETRO, window_end=later)
        self.assertEqual(dict.fromkeys(SPLIT, ("7", "7", "7", "66.7%")), rows_of(section(moved)),
                         "control: the later reading is read when the window takes it in")

    def test_no_split_reads_not_measured_and_an_older_page_renders(self) -> None:
        """AC2. MUTANTS: no split judged by value rather than by the key's presence (a reading
        whose every role is keyed None reads rows, below); judged on every role rather than
        any (one role keyed); a reading with no roles taken as measured; the Cost by role
        table's own NOT MEASURED not carried, or carried with the record path it was handed
        for the source that table names; either template's `present` guard dropped, so a
        page filed before the section renders a block it has no figures for."""
        sr = self.sr
        root = self.tmp / "fixture"
        tsr.fixture_run(root)
        page = sr.build_report(root, tsr.FIX_RETRO)
        sec = section(page)
        self.assertEqual("the Cost by role table is not measured: no closing reading in the "
                         "run's window recorded the spend by role", sec["not_measured"]["reason"])
        self.assertEqual(section(page, "cost_roles")["not_measured"]["source"],
                         sec["not_measured"]["source"])
        self.assertEqual([], sec["rows"])
        # The source is the one the Cost by role table's NOT MEASURED names, not the path the
        # section was handed.
        nm = sr._cost_cache_writes_section({}, "the record handed", {"not_measured": {
            "source": "the record consulted", "reason": "it could not be read"}}, None)
        self.assertEqual(("the record consulted",
                          "the Cost by role table is not measured: it could not be read"),
                         (nm["not_measured"]["source"], nm["not_measured"]["reason"]))
        for splits in ({}, {"builder": rw._split(1, 2, 3)}):   # before the split; one keyed
            stamp_split(root, splits)
            page = sr.build_report(root, tsr.FIX_RETRO)
            self.assertTrue(section(page, "cost_roles")["rows"], "control: the table reads")
            self.assertEqual(NO_SPLIT, section(page)["not_measured"]["reason"], splits)
            for render in (sr.render_markdown, sr.render_html):
                self.assertRegex(render(page), r"Cache writes by role: NOT MEASURED\S* - "
                                               + NO_SPLIT)
        state = root / "sdlc-studio" / ".local" / "run-state.json"
        doc = json.loads(state.read_text(encoding="utf-8"))
        doc[self.rs.TOKEN_STAMPS][-1][self.rs.COST_ROLES]["roles"] = []
        state.write_text(json.dumps(doc), encoding="utf-8")
        self.assertEqual(NO_SPLIT, section(sr.build_report(root, tsr.FIX_RETRO))
                         ["not_measured"]["reason"])
        # A committed page filed before the section renders as signed, byte for byte.
        reports = trend.REPO / "sdlc-studio" / "reports"
        signed = json.loads((reports / "RPT0046.json").read_text(encoding="utf-8"))
        self.assertIn("cost_roles", keys_of(signed))
        self.assertNotIn(KEY, keys_of(signed))
        twin = next(reports.glob("RPT0046-*.md")).read_text(encoding="utf-8")
        self.assertEqual(twin, sr.render_markdown(signed))
        html = sr.render_html(signed)
        self.assertIn("Cost by role", html)
        self.assertNotIn("Cache writes by role", html)

    def test_a_role_with_no_split_or_no_cache_reads_not_available(self) -> None:
        """MUTANTS: a role whose split is None (an agent's call untimed) read as NOT MEASURED
        for the page or as 0; the no-cache guard testing growth alone, so a role whose every
        write is a re-write reads not available rather than 100.0%; the annex's share row
        promising a value the page does not state, or leaving out one it does."""
        sr = self.sr
        root = self.tmp / "keyed"
        tsr.fixture_run(root)
        stamp_split(root, dict.fromkeys(("builder", "reviewer", "repair", "other")))
        sec = section(sr.build_report(root, tsr.FIX_RETRO))
        self.assertIsNone(sec.get("not_measured"), sec)
        self.assertEqual({r: (NA,) * 4 for r in ("builder", "reviewer", "repair", "other")},
                         rows_of(sec))
        stamp_split(root, {"builder": rw._split(0, 0, 500), "reviewer": None,
                           "repair": rw._split(0, 0, 0), "other": rw._split(300, 100, 0)})
        page = sr.build_report(root, tsr.FIX_RETRO)
        self.assertEqual({"builder": ("0", "0", "500", "100.0%"), "reviewer": (NA,) * 4,
                          "repair": ("0", "0", "0", NO_CACHE),
                          "other": ("300", "100", "0", "25.0%")}, rows_of(section(page)))
        for render in (sr.render_markdown, sr.render_html):
            self.assertIn("A role reads not available when any agent in it has a model call's "
                          "usage record with no readable timestamp or no message id",
                          " ".join(render(page).split()))
        # The annex's share row names exactly the two values the page states in place of a
        # share: bare for a role with no split, with the reason for a role that wrote none.
        meaning = next(r["Meaning"] for r in annex.annex_table("Report row keys")
                       if (annex._key(r["Section"]), annex._key(r["Row key"]))
                       == (KEY, "writes_rewrite_share"))
        shares = {cells[-1] for cells in rows_of(section(page)).values()}
        self.assertEqual({NA, NO_CACHE}, {s for s in shares if not s.endswith("%")})
        self.assertEqual({NA, NO_CACHE}, set(re.findall(r"`([^`]+)`", meaning)), meaning)

    def test_the_section_is_replayed_at_sign_and_catalogued(self) -> None:
        """AC3. MUTANTS: the signed page's section not replayed (`_page_readings` handing None,
        or the section ignoring its replay), so a later closing reading moves a signed page;
        re-derivation building the section for a page filed without it; the section placed
        after the trend's index rather than after Cost by role; the section, its figure or a
        row key left out of the annex; the annex moved off 1.1."""
        sr = self.sr
        ws = self._closed("signed")
        for cmd in (["init", "-q", "."], ["add", "-A"],
                    ["-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false",
                     "commit", "-qm", "the delivered batch"]):
            gitutil.git(cmd, ws.root, check=False)
        rid = sr.file_report(ws.root, sr.build_report(ws.root, meter.RETRO))
        stored = sr.read_report(ws.root, rid)
        filed = section(stored)
        self.assertEqual(SPLIT, rows_of(filed))
        # The session goes on after the close: a 1-hour write 73 minutes after the last call.
        ws.tx._append(ws.tx.main, rw._calls((("msg_m4", rw._hour(7_000), 140),)))
        check = sr.revalidate(ws.root, rid)
        self.assertTrue(check["valid"], check.get("changes"))
        self.assertEqual([], check["changes"])
        when = {"as_of": stored["generated_at"], "window_end": stored.get("window_end")}
        fresh = sr.build_report(ws.root, meter.RETRO, **when)
        self.assertEqual(filed, section(fresh))
        self.assertEqual(stored["fingerprint"], sr.fingerprint(fresh))
        # Signed, then the newest reading re-stamped over the grown session.
        with contextlib.redirect_stdout(io.StringIO()):
            meter._live("sprint")._write_the_signature(ws.root, rid, "Maya Okafor")
        for cmd in (["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "-c",
                                    "commit.gpgsign=false", "commit", "-qm", "sign"]):
            gitutil.git(cmd, ws.root, check=False)
        self.assertIsNotNone(self.rs.stamp_cost_roles(ws.root))
        moved = rows_of(section(sr.build_report(ws.root, meter.RETRO, **when)))
        self.assertEqual("16,000", moved["orchestrator"][2], "control: the reading moved")
        check = sr.revalidate(ws.root, rid)
        self.assertTrue(check["valid"], check.get("changes"))
        replayed = sr.build_report(ws.root, meter.RETRO, filed=sr.read_report(ws.root, rid),
                                   **when)
        self.assertEqual(filed, section(replayed))
        self.assertEqual("9,000", rows_of(section(replayed))["orchestrator"][2])
        # A page filed without the section re-derives without it, and with no trend the
        # section still follows Cost by role.
        before = sr.build_report(ws.root, meter.RETRO, cache_writes_rule=False)
        self.assertNotIn(KEY, keys_of(before))
        self.assertIn("cache_read_trend", keys_of(before))
        old = sr.file_report(ws.root, before)
        check = sr.revalidate(ws.root, old)
        self.assertTrue(check["valid"], check.get("changes"))
        self.assertNotIn(KEY, keys_of(sr.read_report(ws.root, old)))
        bare = keys_of(sr.build_report(ws.root, meter.RETRO, cache_trend_rule=False))
        self.assertEqual(bare.index("cost_roles") + 1, bare.index(KEY))
        # The annex catalogues the section, its figure and its row keys under 1.1.
        sections = annex.keyed("Report sections", "Section")
        row = sections[KEY]
        self.assertEqual(("Cache writes by role", "appendix", "always", "-"),
                         (row["Title"], row["Placement"], row["Emitted"], row["Absent when"]))
        self.assertEqual(row["Title"], filed["title"])
        order = list(sections)
        self.assertEqual(order.index("cache_read_trend") + 1, order.index(KEY))
        note = " ".join(" ".join(annex._block("Report sections")).split())
        self.assertIn(f"one filed before the builder wrote a `{KEY}` section carries none", note)
        self.assertEqual({(KEY, "rows", k) for k in ROW_KEYS} | {(KEY, "figures", "writes_basis")},
                         {k for k in annex.figure_keys() if k[0] == KEY})
        self.assertEqual("1.1", stamp.masthead_version())
        self.assertEqual("1.1", sr.EVIDENCE_SCHEMA_VERSION)
        self.assertEqual("1.1", stored[self.rs.EVIDENCE_SCHEMA])


if __name__ == "__main__":
    unittest.main()
