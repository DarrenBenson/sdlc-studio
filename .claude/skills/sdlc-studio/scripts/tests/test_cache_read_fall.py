"""The close names a role whose cache-read share fell more than 10 points below its mean over
earlier signed pages, and the retro must name it.

A fall in a role's cache-read share means a prompt changed and stopped hitting the cache. The
close reads the session's anatomy once, before its chain, sets each role's share (at one decimal
place, as the pages print it) against its mean over the latest signed pages that state one, and
records each role more than 10 points down as a `cache-read` known issue. The page's Cost by role
table is that same reading. `retro.py validate` then demands a `## Cost` bullet naming each fallen
role, and a fall the retro names does not halt a rolling boundary.

Run from the repo root:
    pytest .claude/skills/sdlc-studio/scripts/tests/test_cache_read_fall.py
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import json
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_close_cost_regression as tccr  # noqa: E402 - the close fixture, shared
import test_meter_reads_true as meter  # noqa: E402 - the harness transcript fixture
import test_report_cache_read_trend as trend  # noqa: E402 - a signed page's Cost by role table

RETRO = tccr.RETRO
OTHER_RUN = "RUN-01OTHERRUN"
#: Agent b1's top-up: with tccr.WORK its spend is 3,750,000 priced, 1,500,000 of it cache reads,
#: so the builder's cache-read share is exactly 40.0%.
EXTRA = meter._usage(250_000, 0, 0, 0, 5_000_000)
#: Five signed pages whose builder shares average 64.14, which the pages state as 64.1%.
AC1_PAGES = (("RPT0002", "63.2%"), ("RPT0004", "64.9%"), ("RPT0005", "67.1%"),
             ("RPT0007", "62.6%"), ("RPT0009", "62.9%"))
AC1_IDS = "RPT0002, RPT0004, RPT0005, RPT0007, RPT0009"
NO_PAGE = "no earlier signed page states its cache-read share"
NO_SHARE = "this run's reading states no cache-read share"
THREE_LINE = ("# RETRO-0007: cost\n\n> **Date:** 2026-10-20\n> **Batch:** US0101, US0102, US0103\n"
              "\n## Keep\n\n- the meter read every transcript\n\n## Stop\n\n- long review rounds\n"
              "\n## Try\n\n- a fresh context per review\n")


def pages(root: Path, rows) -> None:
    """Signed pages of another run, in signing order: (id, {role: cache-read cell})."""
    for n, (rid, cells) in enumerate(rows, start=1):
        trend.write_page(root, rid, f"2026-09-{n:02d}T10:00:00Z", OTHER_RUN, cells)


def reading(**shares) -> dict:
    """A closing reading's spend by role: role -> cache-read fraction (None for no share)."""
    return {"source": "s1", "subagent_files": 1,
            "roles": [trend._role(name, share) for name, share in shares.items()],
            "total": {"agents": 2, "calls": 20, "priced": 2000}}


class CacheReadFallTests(tccr._Case):
    def builder_tree(self, *, with_pages: bool = True, cost: str = "") -> Path:
        """The close fixture with agent b1 the builder of US0102 at exactly 40.0% cache-read."""
        root = self.tree(tccr.CHEAP_ROWS, cost=cost)
        meter._Transcripts(root.parent / "transcripts").agent_says("b1", "msg_more", EXTRA)
        self.rs.update(root, delegated_tokens=[
            {"tokens": 10, "agent": "b1", "note": "", "provenance": "supplied",
             "recorded_at": "2026-09-23T00:30:00Z", "unit": "US0102"}])
        if with_pages:
            pages(root, [(rid, {"builder": v, "reviewer": "not available", "other": "48.0%"})
                         for rid, v in AC1_PAGES])
        return root

    def spied_close(self, root: Path):
        anat = meter._live("lib.cost_anatomy")
        with unittest.mock.patch.object(anat, "anatomy", wraps=anat.anatomy) as spy, \
                unittest.mock.patch.object(self.rs, "stamp_cost_roles",
                                           wraps=self.rs.stamp_cost_roles) as stamp, \
                unittest.mock.patch.object(self.sprint, "close_cache_read_fall",
                                           wraps=self.sprint.close_cache_read_fall) as check:
            rc, out = self.close(root)
        return rc, out, spy, stamp, check

    @staticmethod
    def fall_lines(out: str) -> list[str]:
        return [ln for ln in out.splitlines() if ln.startswith("close: cache-read share")]

    def page(self, root: Path) -> dict:
        rid = self.rs.read(root).get("report")
        self.assertTrue(rid)
        return json.loads((root / "sdlc-studio" / "reports" / f"{rid}.json").read_text())

    # --- the criteria -------------------------------------------------------------------------

    def test_the_close_records_a_fall_from_one_anatomy_read(self) -> None:
        """AC1. MUTANTS: `stamp_cost_roles` reading the anatomy again rather than the reading it
        is handed (two reads); the issue left out of the close's known issues; the check fed the
        newest stamped roles on a first close (none yet, so no issue)."""
        root = self.builder_tree()
        rc, out, spy, stamp, check = self.spied_close(root)
        self.assertEqual(0, rc, out)
        lines = self.fall_lines(out)
        self.assertEqual(1, len(lines), out)
        for text in ("builder 40.0%", "its mean 64.1%", "-24.1 points", AC1_IDS,
                     "over 5 signed page(s)"):
            self.assertIn(text, lines[0])
        falls = self.issues(root, "cache-read")
        self.assertEqual(1, len(falls), out)
        issue = falls[0]
        self.assertEqual(("builder", 40.0, 64.1, -24.1, RETRO),
                         (issue["role"], issue["share"], issue["mean"], issue["change"],
                          issue["retro"]))
        self.assertEqual(AC1_IDS.split(", "), issue["reports"])
        self.assertIn("builder", issue["detail"])
        self.assertEqual(1, spy.call_count, "the anatomy is read once per close")
        judged = check.call_args.args[3]
        self.assertIs(judged, stamp.call_args.kwargs.get("roles"),
                      "the stamp records the very reading the check judged")
        page = self.page(root)
        roles = next(s for s in page["sections"] if s["key"] == "cost_roles")
        cells = {r["role_name"]["value"]: r["role_cache_read"]["value"] for r in roles["rows"]}
        self.assertEqual("40.0%", cells["builder"])
        known = next(s for s in page["sections"] if s["key"] == "known_issues")["rows"]
        self.assertIn(issue["detail"], [r["issue_detail"]["value"] for r in known
                                        if r["issue_id"]["value"] == "cache-read"])

    def test_ten_points_or_less_or_no_baseline_records_nothing(self) -> None:
        """AC2. MUTANTS: `<=` for `<` (50.0% records); the 10 read as 9 or 11; the share
        compared unrounded (49.951 records); a rise counted by its size (75.0% records); either
        not-judged reason dropped or swapped; a role with fewer than five pages left unjudged."""
        root = Path(tempfile.mkdtemp(prefix="cache-fall-", dir=self.tmp))
        pages(root, [(f"RPT000{n}", {"builder": "60.0%", "reviewer": "not available",
                                     **({"orchestrator": "55.0%"} if n < 3 else {})})
                     for n in range(1, 6)])
        check = self.sprint.close_cache_read_fall
        got = {}
        for share in (0.50, 0.499, 0.75, 0.49951):
            got[share] = check(root, {"run_id": "RUN-THIS"}, RETRO,
                               reading(builder=share, reviewer=0.30, repair=None,
                                       orchestrator=0.50))
        self.assertEqual([0.499], [s for s, r in got.items() if r["issues"]])
        self.assertEqual(["builder"], [i["role"] for i in got[0.499]["issues"]])
        self.assertEqual((-10.1, 49.9), (got[0.499]["issues"][0]["change"],
                                       got[0.499]["issues"][0]["share"]))
        for share, r in got.items():
            line = r["line"]
            self.assertNotIn("\n", line)
            self.assertIn(f"reviewer ({NO_PAGE})", line)
            self.assertIn(f"repair ({NO_SHARE})", line)
            self.assertIn("orchestrator 50.0% against its mean 55.0% over 2 signed page(s)",
                          line)
        self.assertIn("builder 50.0% against its mean 60.0% over 5 signed page(s) (RPT0001, "
                      "RPT0002, RPT0003, RPT0004, RPT0005), -10.0 points: within 10",
                      got[0.50]["line"])
        self.assertIn("-10.1 points: FELL more than 10", got[0.499]["line"])
        self.assertIn("+15.0 points: within 10", got[0.75]["line"])
        self.assertIn("builder 50.0%", got[0.49951]["line"])
        # The issue states the share as the page prints it, never the reading's raw fraction.
        low = check(root, {"run_id": "RUN-THIS"}, RETRO, reading(builder=0.4994))["issues"]
        self.assertEqual([49.9], [i["share"] for i in low])
        # No earlier page at all: nobody is judged and nothing is recorded.
        bare = Path(tempfile.mkdtemp(prefix="cache-fall-", dir=self.tmp))
        none = check(bare, {"run_id": "RUN-THIS"}, RETRO, reading(builder=0.10))
        self.assertEqual([], none["issues"])
        self.assertIn(f"builder ({NO_PAGE})", none["line"])

    def test_retro_validate_demands_each_fallen_role_be_named(self) -> None:
        """AC3. MUTANTS: the demand left out of the Keep/Stop/Try path; any `## Cost` bullet
        taken as naming every role."""
        root = self.issue_tree()
        expect = ("builder", "40.0%", "62.9%", "add a `## Cost` bullet naming builder")
        for cost in ("", "\n## Cost\n\n- the repair rounds re-read the diff\n"):
            self.write_retro(root, THREE_LINE + cost)
            rc, out = self.validate(root)
            self.assertNotEqual(0, rc, out)
            for text in expect:
                self.assertIn(text, out)
        self.write_retro(root, THREE_LINE + "\n## Cost\n\n- the builder's prompt changed\n")
        rc, out = self.validate(root)
        self.assertEqual(0, rc, out)

    def test_a_named_fall_does_not_halt_a_rolling_boundary(self) -> None:
        """AC4. MUTANTS: the boundary's filter left without the cache-read test (the named fall
        halts); `_cache_fall_named` true for any cache-read issue (the unnamed one rolls on)."""
        for stops in (False, True):
            bullet = "the review rounds re-read the diff" if stops else "the builder's prompt moved"
            root = self.tree(tccr.CHEAP_ROWS, cost=f"\n## Cost\n\n- {bullet}\n")
            rc, out = self.close(root)
            self.assertEqual(0, rc, out)
            self.record_fall(root)
            self.rs.update(root, cycle={"index": 1, "remaining": 1}, policy={
                "cycles": 2, "sprint_goal": "the run costs what its work costs", "goal": "done",
                "order": "priority", "capacity": {"minutes": 240, "units": 8},
                "queries": [{"kind": "bug", "status": "Open"}], "epics": None,
                "stop_conditions": list(self.sprint.STOP_CAUSES), "skip_personas": False,
                "recorded_at": "2026-10-20T00:00:00Z"})
            with unittest.mock.patch.object(self.sprint, "_boundary_close_down",
                                            lambda *a, **k: (0, "")):
                rc, said = tccr._out(self.sprint.main, ["boundary", "--retro", RETRO,
                                                        "--no-fetch", "--root", str(root)])
            self.assertEqual(stops, "known issue(s)" in said, said)
            self.assertEqual(stops, "builder's cache-read share 40.0%" in said, said)
            self.assertEqual(not stops, "cycle 1 closed and archived" in said, said)

    # --- helpers for the retro and boundary pins ----------------------------------------------

    def issue_tree(self) -> Path:
        root = self.tree(tccr.CHEAP_ROWS)
        self.record_fall(root)
        return root

    def record_fall(self, root: Path, **shares) -> list[dict]:
        """The check's own issues over pages at builder and repair 62.9%, on the run record as
        the close records them."""
        pages(root, [(f"RPT00{n}", {"builder": "62.9%", "repair": "62.9%"})
                     for n in range(41, 46)])
        got = self.sprint.close_cache_read_fall(root, self.rs.read(root), RETRO,
                                                reading(**(shares or {"builder": 0.40})))
        self.assertTrue(got["issues"], got["line"])
        self.rs.update(root, close_known_issues=list(
            self.rs.read(root).get(self.rs.CLOSE_KNOWN_ISSUES) or []) + got["issues"])
        return got["issues"]

    def write_retro(self, root: Path, text: str) -> None:
        (root / "sdlc-studio" / "retros" / f"{RETRO}-cost.md").write_text(text, encoding="utf-8")

    # --- the guards beside the criteria -------------------------------------------------------

    def test_the_older_retro_shape_is_held_to_the_demand_too(self) -> None:
        """MUTANT: the demand left out of the older shape's `validate` path."""
        root = self.issue_tree()
        self.write_retro(root, tccr.RETRO_TEXT)
        rc, out = self.validate(root)
        self.assertNotEqual(0, rc, out)
        self.assertIn("add a `## Cost` bullet naming builder", out)
        self.write_retro(root, tccr.RETRO_TEXT + "\n## Cost\n\n- the builder's prompt moved\n")
        self.assertEqual(0, self.validate(root)[0])

    def test_every_fallen_role_is_demanded_and_only_this_retros(self) -> None:
        """MUTANTS: the demand stopping at the first issue, or met by any one role named; an
        issue recorded for another retro demanded of this one."""
        root = self.tree(tccr.CHEAP_ROWS)
        self.record_fall(root, builder=0.40, repair=0.30)
        self.write_retro(root, THREE_LINE + "\n## Cost\n\n- the builder's prompt changed\n")
        rc, out = self.validate(root)
        self.assertNotEqual(0, rc, out)
        self.assertIn("add a `## Cost` bullet naming repair", out)
        self.assertNotIn("naming builder", out)
        state = self.rs.read(root)
        self.rs.update(root, close_known_issues=[
            {**g, "retro": "RETRO0099"} for g in state[self.rs.CLOSE_KNOWN_ISSUES]])
        self.write_retro(root, THREE_LINE)
        self.assertEqual(0, self.validate(root)[0])

    def test_a_role_is_named_by_word_whatever_its_characters(self) -> None:
        """MUTANTS: the role matched case-sensitively, without its plural, inside a longer word
        or a hyphenated name, or as a pattern rather than literally; a placeholder bullet read
        as naming it. The word `other` names the `other` role: the match is by word only."""
        names = meter._live("retro").names_role

        def cost(*bullets: str) -> str:
            return THREE_LINE + "\n## Cost\n\n" + "".join(f"- {b}\n" for b in bullets)

        for role, bullet, named in (
                ("builder", "The Builder's prompt changed", True),
                ("builder", "both builders re-read the diff", True),
                ("builder", "the prebuilder step ran long", False),
                ("builder", "{{placeholder}} builder", False),
                ("qa", "the qa-lead seat re-read it", False),
                ("qa-lead", "the qa-lead seat re-read it", True),
                ("c++", "the c++ seat re-read it", True),
                ("c++", "the cxx seat re-read it", False),
                ("a.b", "the a.b seat re-read it", True),
                ("a.b", "the axb seat re-read it", False),
                ("other", "other costs rose", True)):
            with self.subTest(role=role, bullet=bullet):
                self.assertEqual(named, names(cost(bullet), role))
        self.assertFalse(names(THREE_LINE + "\n## Keep\n\n- builder\n", "builder"))

    def test_the_named_check_reads_only_a_cache_read_issue_with_its_retro(self) -> None:
        """MUTANTS: each guard of `_cache_fall_named` dropped."""
        root = self.tree(tccr.CHEAP_ROWS, cost="\n## Cost\n\n- the builder's prompt moved\n")
        named = self.sprint._cache_fall_named
        gap = {"source": "cache-read", "retro": RETRO, "role": "builder", "detail": "d"}
        self.assertTrue(named(root, gap))
        for bad in ("not a dict", {**gap, "source": "cost"}, {**gap, "retro": None},
                    {**gap, "retro": "RETRO0099"}, {**gap, "role": "repair"}):
            with self.subTest(gap=bad):
                self.assertFalse(named(root, bad))

    def test_a_re_close_judges_the_stamped_reading_and_a_reopen_reads_again(self) -> None:
        """MUTANTS: a re-close reading the anatomy again; the earlier close's cache-read issue
        kept beside this one's; a re-close with no stamped roles dropping the earlier issue; a
        reopened run judged from the old window's roles."""
        root = self.builder_tree()
        anat = meter._live("lib.cost_anatomy")
        with unittest.mock.patch.object(anat, "anatomy", wraps=anat.anatomy) as spy:
            self.assertEqual(0, self.close(root)[0])
            rc, out = self.close(root)
            self.assertEqual(0, rc, out)
            self.assertEqual(1, spy.call_count, out)
            self.assertEqual(1, len(self.issues(root, "cache-read")), out)
            self.assertIn("-24.1 points", self.fall_lines(out)[0])
            state = self.rs.read(root)
            for s in state[self.rs.TOKEN_STAMPS]:
                s.pop(self.rs.COST_ROLES, None)
            self.rs.update(root, **{self.rs.TOKEN_STAMPS: state[self.rs.TOKEN_STAMPS]})
            rc, out = self.close(root)
            self.assertEqual(1, spy.call_count, out)
            self.assertIn("UNMEASURED", self.fall_lines(out)[0])
            self.assertEqual(1, len(self.issues(root, "cache-read")), out)
            self.rs.update(root, reopened=[{"at": "2099-01-01T00:00:00Z"}])
            with unittest.mock.patch.object(self.rs, "stamp_cost_roles",
                                            wraps=self.rs.stamp_cost_roles) as stamp:
                rc, out = self.close(root)
            self.assertIsNotNone(stamp.call_args.kwargs.get("roles"), out)
            self.assertEqual(0, rc, out)
            self.assertEqual(2, spy.call_count, out)

    def test_a_reading_of_another_session_is_judged_by_nobody(self) -> None:
        """The meter reads a session the anatomy did not: the page's table reads NOT MEASURED,
        so the check judges nothing and says why, and the close completes. MUTANT: the session
        check left out of the check's first-close reading (the fall is recorded)."""
        root = self.builder_tree()
        real = self.rs._stamp

        def elsewhere(*a, **k):
            got = real(*a, **k)
            return {**got, "source": "/elsewhere/another-session.jsonl"} if got else got

        with unittest.mock.patch.object(self.rs, "_stamp", elsewhere):
            rc, out = self.close(root)
        self.assertEqual(0, rc, out)
        self.assertEqual([], self.issues(root, "cache-read"), out)
        line = self.fall_lines(out)[0]
        self.assertIn("UNMEASURED", line)
        self.assertIn("is not the one this reading's meter read", line)
        roles = next(s for s in self.page(root)["sections"] if s["key"] == "cost_roles")
        self.assertIsNotNone(roles["not_measured"])
        # A meter that gives no reading leaves no closing reading to state the roles either.
        with unittest.mock.patch.object(self.rs, "_stamp", lambda *a, **k: None):
            got, fresh = self.sprint._close_cost_roles(root, {})
        self.assertEqual(({"reason": "the meter gives no reading, so no closing reading records "
                                     "the spend by role"}, True), (got, fresh))

    def test_the_stamp_checks_a_handed_reading_against_its_session(self) -> None:
        """MUTANTS: a handed reading recorded whatever session it read; a matching one replaced."""
        root = self.tree(tccr.CHEAP_ROWS)
        self.assertIsNotNone(self.rs.stamp_tokens(root, "report"))
        source = Path(self.rs.read(root)[self.rs.TOKEN_STAMPS][-1]["source"]).stem
        mine = {**reading(builder=0.4), "source": source}
        self.assertIs(mine, self.rs.stamp_cost_roles(root, roles=mine))
        got = self.rs.stamp_cost_roles(root, roles={**mine, "source": "another-session"})
        self.assertIn("another-session", got["reason"])
        self.assertEqual(got, self.rs.read(root)[self.rs.TOKEN_STAMPS][-1][self.rs.COST_ROLES])
        unread = {"reason": "the spend by role could not be read: no transcript"}
        self.assertEqual(unread, self.rs.stamp_cost_roles(root, roles=unread))

    def test_nothing_is_held_past_a_close(self) -> None:
        """MUTANTS: the hand-off left uncleared at the top of the close (a refused close keeps a
        stale reading), or not consumed when the close files no stamp."""
        root = self.builder_tree(with_pages=False)
        self.sprint._HELD_ROLES["stale"] = {"reason": "stale"}
        rc, _out = tccr._out(self.sprint.main, ["close", "--retro", RETRO, "--root", str(root)])
        self.assertEqual(1, rc)
        self.assertEqual({}, self.sprint._HELD_ROLES)
        with unittest.mock.patch.object(self.rs, "stamp_tokens", lambda *a, **k: None):
            rc, out = self.close(root)
        self.assertEqual(0, rc, out)
        self.assertEqual({}, self.sprint._HELD_ROLES)

    def test_a_check_that_cannot_run_leaves_the_close_complete(self) -> None:
        """MUTANT: the check's failure left to end the close."""
        root = self.builder_tree(with_pages=False)

        def boom(*a, **k):
            raise RuntimeError("no reading")

        with unittest.mock.patch.object(self.sprint, "close_cache_read_fall", boom):
            rc, out = self.close(root)
        self.assertEqual(0, rc, out)
        self.assertIn("close: cache-read share by role: UNMEASURED - the check could not run "
                      "(RuntimeError: no reading)", out)
        self.assertIn("sign it with: sprint.py sign", out)


if __name__ == "__main__":
    unittest.main()
