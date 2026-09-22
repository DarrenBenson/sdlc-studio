"""Backlog triage lenses: is this backlog worth planning from?

The load-bearing cases are the ones a real backlog hits and a human caught by accident: two units
that edit the same file with near-identical wording (a duplicate filed twice); a unit sized past the
point anyone can estimate; an item rotting untouched; a dependency on something already closed. Each
lens is tested on a positive AND a negative, because a lens that only fires (or never fires) is not a
lens - the negative proves it does not cry wolf on a clean backlog.
"""
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import backlog_triage  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent))
import workspace  # noqa: E402 - the one authority for "am I in the dev repo?"


def _w(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _unit(root: Path, kind: str, cid: str, *, title: str, status: str, affects: str = "",
          summary: str = "", points: str = "", depends: str = "", date: str = "2026-07-16") -> None:
    d = {"story": ("stories", "US"), "bug": ("bugs", "BG"), "cr": ("change-requests", "CR"),
         "rfc": ("rfcs", "RFC"), "epic": ("epics", "EP")}[kind]
    lines = [f"# {cid}: {title}", "", f"> **Status:** {status}"]
    if affects:
        lines.append(f"> **Affects:** {affects}")
    if points:
        lines.append(f"> **Points:** {points}")
    if depends:
        lines.append(f"> **Depends on:** {depends}")
    lines.append(f"> **Date:** {date}")
    body = "\n".join(lines) + f"\n\n## Summary\n\n{summary or title}\n"
    _w(root / "sdlc-studio" / d[0] / f"{cid}-x.md", body)


class TriageBase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def _lenses(self, report):
        return {f["lens"] for f in report["findings"]}


class DuplicateLensTests(TriageBase):
    def test_same_file_and_similar_wording_flags_duplicate(self) -> None:
        _unit(self.root, "bug", "BG0001", title="check_links misses anchor defects",
              status="Open", affects="tools/check_links.py",
              summary="check_links.py does not catch a broken markdown anchor link defect")
        _unit(self.root, "bug", "BG0002", title="check_links anchor link defect not caught",
              status="Open", affects="tools/check_links.py",
              summary="a broken markdown anchor link defect is not caught by check_links.py")
        report = backlog_triage.triage(self.root, today="2026-07-16")
        self.assertIn("duplicate", self._lenses(report))

    def test_subset_affects_flags_subsumed_not_duplicate(self) -> None:
        _unit(self.root, "cr", "CR0001", title="add a telemetry attribution field",
              status="Proposed", affects="scripts/telemetry.py",
              summary="add an attribution field to telemetry and segment the accuracy report by it")
        _unit(self.root, "cr", "CR0002", title="add a telemetry attribution field and segment",
              status="Proposed", affects="scripts/telemetry.py, scripts/retro.py",
              summary="add an attribution field to telemetry and segment the accuracy report by it")
        report = backlog_triage.triage(self.root, today="2026-07-16")
        self.assertIn("subsumed", self._lenses(report))
        self.assertNotIn("duplicate", self._lenses(report))

    def test_different_files_no_duplicate(self) -> None:
        _unit(self.root, "bug", "BG0001", title="fix the parser", status="Open",
              affects="scripts/a.py", summary="the parser drops a field")
        _unit(self.root, "bug", "BG0002", title="fix the parser", status="Open",
              affects="scripts/b.py", summary="the parser drops a field")
        report = backlog_triage.triage(self.root, today="2026-07-16")
        self.assertNotIn("duplicate", self._lenses(report))  # no shared file -> not a duplicate

    def test_same_file_unrelated_wording_no_duplicate(self) -> None:
        _unit(self.root, "bug", "BG0001", title="add colour to the status output", status="Open",
              affects="scripts/status.py", summary="status output should render green and amber")
        _unit(self.root, "bug", "BG0002", title="status crashes on an empty backlog", status="Open",
              affects="scripts/status.py", summary="an empty project raises a division by zero")
        report = backlog_triage.triage(self.root, today="2026-07-16")
        self.assertNotIn("duplicate", self._lenses(report))


class OversizedLensTests(TriageBase):
    def test_over_ceiling_blocks(self) -> None:
        _unit(self.root, "story", "US0001", title="do everything", status="Draft", points="13")
        report = backlog_triage.triage(self.root, today="2026-07-16")
        self.assertTrue(report["blocked"])
        self.assertEqual(report["blocking"][0]["units"], ["US0001"])

    def test_at_ceiling_reports_not_blocks(self) -> None:
        _unit(self.root, "story", "US0001", title="a big one", status="Draft", points="8")
        report = backlog_triage.triage(self.root, today="2026-07-16")
        self.assertFalse(report["blocked"])
        self.assertIn("oversized", self._lenses(report))

    def test_within_ceiling_clean(self) -> None:
        _unit(self.root, "story", "US0001", title="a normal one", status="Draft", points="5")
        report = backlog_triage.triage(self.root, today="2026-07-16")
        self.assertNotIn("oversized", self._lenses(report))


class StaleLensTests(TriageBase):
    def test_old_and_undepended_is_stale(self) -> None:
        _unit(self.root, "cr", "CR0001", title="an old idea", status="Proposed", date="2026-01-01")
        report = backlog_triage.triage(self.root, today="2026-07-16", stale_days=90)
        self.assertIn("stale", self._lenses(report))

    def test_recent_is_not_stale(self) -> None:
        _unit(self.root, "cr", "CR0001", title="a fresh idea", status="Proposed", date="2026-07-10")
        report = backlog_triage.triage(self.root, today="2026-07-16", stale_days=90)
        self.assertNotIn("stale", self._lenses(report))

    def test_depended_on_is_not_stale(self) -> None:
        _unit(self.root, "cr", "CR0001", title="an old but needed idea", status="Proposed",
              date="2026-01-01")
        _unit(self.root, "cr", "CR0002", title="needs the old one", status="Proposed",
              date="2026-07-10", depends="CR0001")
        report = backlog_triage.triage(self.root, today="2026-07-16", stale_days=90)
        self.assertNotIn("stale", self._lenses(report))


class OrphanedDependencyLensTests(TriageBase):
    def test_dependency_on_absent_or_terminal_is_orphaned(self) -> None:
        _unit(self.root, "cr", "CR0001", title="depends on a closed thing", status="Proposed",
              depends="US0999")  # US0999 is not an open artefact
        report = backlog_triage.triage(self.root, today="2026-07-16")
        self.assertIn("orphaned-dependency", self._lenses(report))

    def test_dependency_on_open_artefact_is_clean(self) -> None:
        _unit(self.root, "cr", "CR0001", title="depends on an open thing", status="Proposed",
              depends="US0002")
        _unit(self.root, "story", "US0002", title="the dependency", status="Draft", points="2")
        report = backlog_triage.triage(self.root, today="2026-07-16")
        self.assertNotIn("orphaned-dependency", self._lenses(report))


class UnruledRequestTests(TriageBase):
    """US0848: a request that is In Progress, finished by its children, and never ruled.

    This is the state RUN-01M306PY's sweep clears: 41 requests sat In Progress with children at
    every depth, so `Discovery=67` read as 67 live options when most were abandoned. Clearing it
    once is a tidy; the lane is what stops it rebuilding silently.
    """

    def _req(self, cid, *, status, children=(), ruled=False):
        lines = [f"# {cid}: a request", "", f"> **Status:** {status}"]
        if children:
            lines.append("> **Decomposed-into:** " + ", ".join(children))
        lines += ["> **Date:** 2026-07-16", "", "## Summary", "", "a request", "",
                  "## Revision History", "", "| Date | Author | Change |", "| --- | --- | --- |",
                  "| 2026-07-16 | sdlc-studio | Filed |"]
        if ruled:
            lines.append("| 2026-09-21 | audit ruling | still wanted, correctly in progress |")
        d = self.root / "sdlc-studio" / "change-requests"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{cid}-x.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _units(self, *specs):
        for cid, status in specs:
            _unit(self.root, "story", cid, title="a child", status=status)

    def test_an_in_progress_request_with_no_unresolved_child_and_no_ruling_is_reported(self) -> None:
        """MUTANT: report every In-Progress request whose children are all resolved, ruled or
        not. The lane then fires on requests that WERE judged, becomes noise within one sweep,
        and gets switched off - which is how this project's 120s gate budget failed.
        """
        self._units(("US0001", "Done"), ("US0002", "Draft"), ("US0003", "Done"), ("US0004", "Done"))
        self._req("CR0001", status="In Progress", children=["US0001", "US0002"])   # still working
        self._req("CR0002", status="In Progress", children=["US0003"], ruled=True)  # judged
        self._req("CR0003", status="In Progress", children=["US0004"])              # finished, unruled
        report = backlog_triage.triage(self.root, today="2026-09-21")
        flagged = sorted(u for f in report["findings"] if f["lens"] == "unruled"
                         for u in f["units"])
        self.assertEqual(["CR0003"], flagged,
                         f"the lane did not isolate the finished-but-unruled request: {flagged}")

    def test_the_unruled_finding_renders_with_its_lens_name_and_remedy(self) -> None:
        """The finding has to survive RENDERING, not just exist in the report dict.

        `render` sorts by a lens-order map, and a lens missing from that map falls to the default
        bucket - which reads as a lane nobody thought about, beneath the ones that were. The
        rendered line is also the only form most readers ever see, so a remedy present in the
        dict and absent from the page has not been delivered.

        MUTANT: drop `unruled` from `render`'s order map. The finding still exists and every
        other assertion in this class still passes, while the line a reader actually meets moves
        to the bottom of the list under a default nobody chose.
        """
        self._units(("US0001", "Done"),)
        self._req("CR0001", status="In Progress", children=["US0001"])
        text = backlog_triage.render(backlog_triage.triage(self.root, today="2026-09-21"))
        self.assertIn("unruled", text, "the lens name is absent from the rendered page")
        self.assertIn("CR0001", text)
        self.assertIn("audit ruling", text,
                      f"the rendered line does not name what clears it: {text}")
        self.assertIn("[note ]", text, "an advisory finding rendered as a blocking one")

    def test_a_childless_request_is_not_reported_as_unruled(self) -> None:
        """A childless request is the separate `undecomposed` case `status` already counts as
        awaiting refine. Reporting it here too makes one problem look like two.

        MUTANT: treat zero children as `every child resolved` - a vacuously-true reading that
        reports every undecomposed request and doubles the lane's output on a backlog that
        already carries 25 of them.
        """
        self._req("CR0001", status="In Progress")
        report = backlog_triage.triage(self.root, today="2026-09-21")
        self.assertNotIn("unruled", self._lenses(report))

    def test_the_unruled_finding_is_advisory_and_names_its_remedy(self) -> None:
        """MUTANT: make the finding blocking - a backlog-hygiene lane that refuses a commit
        stops unrelated work for a state nobody created in that commit, which is the line this
        project already draws between drift a change causes and drift that predates it.
        """
        self._units(("US0001", "Done"),)
        self._req("CR0001", status="In Progress", children=["US0001"])
        report = backlog_triage.triage(self.root, today="2026-09-21")
        found = [f for f in report["findings"] if f["lens"] == "unruled"]
        self.assertTrue(found, "the lane reported nothing")
        self.assertEqual("report", found[0]["severity"])
        self.assertFalse(report["blocked"], "a hygiene lane blocked the commit")
        self.assertIn("audit ruling", found[0]["detail"],
                      f"the finding does not name what clears it: {found[0]['detail']}")


class CleanBacklogTests(TriageBase):
    def test_a_coherent_backlog_is_clean(self) -> None:
        _unit(self.root, "story", "US0001", title="add a flag", status="Draft",
              affects="scripts/a.py", points="3", date="2026-07-15")
        _unit(self.root, "bug", "BG0001", title="fix a crash", status="Open",
              affects="scripts/b.py", points="2", date="2026-07-15")
        report = backlog_triage.triage(self.root, today="2026-07-16")
        self.assertEqual(report["findings"], [])
        self.assertFalse(report["blocked"])

    def test_check_exit_code_and_render(self) -> None:
        _unit(self.root, "story", "US0001", title="huge", status="Draft", points="13")
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            rc = backlog_triage.main(["--root", str(self.root), "check"])
        self.assertEqual(rc, 1)
        self.assertIn("BLOCK", buf.getvalue())



class ReviewRegressionTests(TriageBase):
    """Regressions from the independent review: date honesty, orphaned classification, drop accounting."""

    def test_future_or_prose_date_does_not_suppress_stale(self) -> None:
        # M3: an old CR whose SUMMARY mentions a future deadline must still be stale - the future
        # date is not a last-touched date.
        _unit(self.root, "cr", "CR0001", title="an old idea", status="Proposed",
              date="2026-01-01", summary="an old idea we should finish by 2026-12-31 at the latest")
        report = backlog_triage.triage(self.root, today="2026-07-16", stale_days=90)
        self.assertIn("stale", {f["lens"] for f in report["findings"]})

    def test_dependency_on_open_test_spec_is_not_orphaned(self) -> None:
        # M2: a live dependency on an open non-triage-type artefact (a test-spec) must not be flagged.
        _unit(self.root, "cr", "CR0001", title="depends on a live test spec", status="Proposed",
              depends="TS0007")
        _w(self.root / "sdlc-studio" / "test-specs" / "TS0007-x.md",
           "# TS0007: a spec\n\n> **Status:** Draft\n")
        report = backlog_triage.triage(self.root, today="2026-07-16")
        self.assertNotIn("orphaned-dependency", {f["lens"] for f in report["findings"]})

    def test_terminal_and_absent_dependencies_are_worded_differently(self) -> None:
        # M5: a resolved (terminal) dep and an absent (mistyped) dep get different advice.
        _unit(self.root, "cr", "CR0001", title="depends on a done thing", status="Proposed",
              depends="US0002")
        _unit(self.root, "story", "US0002", title="the done dependency", status="Done", points="2")
        _unit(self.root, "cr", "CR0003", title="depends on a ghost", status="Proposed",
              depends="US9999")
        findings = {f["units"][0]: f["detail"] for f in backlog_triage.triage(self.root, today="2026-07-16")["findings"]
                    if f["lens"] == "orphaned-dependency"}
        self.assertIn("already resolved", findings["CR0001"])
        self.assertIn("does not exist", findings["CR0003"])

    def test_unreadable_file_is_counted_not_swallowed(self) -> None:
        # M4: a non-UTF-8 artefact is a NAMED gap, never a silent clean pass.
        d = self.root / "sdlc-studio" / "bugs"
        d.mkdir(parents=True, exist_ok=True)
        (d / "BG0001-x.md").write_bytes(b"# BG0001: x\n\xff\xfe not utf-8\n")
        report = backlog_triage.triage(self.root, today="2026-07-16")
        self.assertEqual(report["skipped"], 1)

    def test_pointed_container_over_ceiling_is_oversized(self) -> None:
        # N3: a legacy CR carrying points > 8 is oversized wherever it lives, like the plan gate.
        _unit(self.root, "cr", "CR0001", title="a huge legacy CR", status="Proposed", points="13")
        report = backlog_triage.triage(self.root, today="2026-07-16")
        self.assertTrue(report["blocked"])


class FilerNeverBreaksTests(TriageBase):
    """M1: a duplicate warning must never break a filing, even when a sibling artefact is unreadable."""

    def test_duplicate_candidates_returns_empty_on_unreadable_sibling(self) -> None:
        import file_finding as ff
        d = self.root / "sdlc-studio" / "bugs"
        d.mkdir(parents=True, exist_ok=True)
        (d / "BG0001-x.md").write_bytes(b"\xff\xfe\x00 not utf-8")
        # must not raise - degrade to no candidates
        self.assertEqual(ff.duplicate_candidates(self.root, "a new bug",
                         {"affects": "src/thing.py", "summary": "s"}), [])


class AbandonedRequestLensTests(TriageBase):
    """BG0722. The `unruled` lens catches a request nobody CLOSED - In Progress, every child
    resolved, no judgement recorded. Run against this repository's real backlog it reported ZERO,
    because all 37 In Progress requests had at least one child still open. The path that actually
    accumulates is the request everybody ABANDONED: work started, stopped, and the children have
    not moved since. Judged by the CHILDREN's dates, because the request's own date says only that
    somebody wrote on it - and the sweep's own dated audit ruling is a write."""

    def _request(self, cid: str, *, status: str = "In Progress", date: str,
                 children: list[str], ruled: bool = False) -> None:
        d = "change-requests" if cid.startswith("CR") else "rfcs"
        lines = [f"# {cid}: a request", "", f"> **Status:** {status}",
                 f"> **Decomposed-into:** {', '.join(children)}", f"> **Date:** {date}"]
        body = "\n".join(lines) + "\n\n## Summary\n\nsomething\n"
        if ruled:
            body += ("\n## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n"
                     f"| {date} | audit ruling | still wanted |\n")
        _w(self.root / "sdlc-studio" / d / f"{cid}-x.md", body)

    def _child(self, uid: str, *, status: str, date: str) -> None:
        _unit(self.root, "story", uid, title="a child", status=status, date=date)

    def test_a_request_edited_today_with_frozen_children_is_reported(self) -> None:
        """AC1. The request's own date is not evidence of progress - somebody writing on it is
        not the work moving. This is the case the shipped lens cannot see at all."""
        self._request("CR9001", date="2026-07-16", children=["US9001"])
        self._child("US9001", status="Draft", date="2026-01-01")
        report = backlog_triage.triage(self.root, today="2026-07-16")
        self.assertIn("abandoned", self._lenses(report))

    def test_an_audit_ruling_does_not_silence_the_lens(self) -> None:
        """AC2. A guard its own remedy switches off goes blind exactly once it has been used -
        which is how `stale` was lost. The children are what must move, not the paperwork."""
        self._request("CR9002", date="2026-07-16", children=["US9002"], ruled=True)
        self._child("US9002", status="Draft", date="2026-01-01")
        report = backlog_triage.triage(self.root, today="2026-07-16")
        abandoned = [f for f in report["findings"] if f["lens"] == "abandoned"]
        self.assertTrue(any("CR9002" in f["units"] for f in abandoned),
                        "a dated audit ruling is a write on the request, not movement in the work")

    def test_a_request_with_moving_children_is_not_reported(self) -> None:
        """AC3, the discriminating half - and the direction the shipped lens fails in, by
        reporting nothing at all."""
        self._request("CR9003", date="2026-01-01", children=["US9003"])
        self._child("US9003", status="Draft", date="2026-07-10")
        report = backlog_triage.triage(self.root, today="2026-07-16")
        abandoned = [f for f in report["findings"] if f["lens"] == "abandoned"]
        self.assertFalse(any("CR9003" in f["units"] for f in abandoned))

    def test_both_lenses_report_their_own_case(self) -> None:
        """AC4. Complementary, not overlapping: finished-but-never-closed against
        started-and-left. Collapsing them would re-lose whichever the survivor does not catch."""
        # The finished child is OLD, so the two lenses are genuinely distinguished. With a child
        # dated today, `abandoned` could not fire on CR9004 whatever the code did, and the mutant
        # that dates a request from ALL its children rather than its OPEN ones survived.
        self._request("CR9004", date="2026-07-16", children=["US9004"])
        self._child("US9004", status="Done", date="2026-01-01")
        self._request("CR9005", date="2026-07-16", children=["US9005"])
        self._child("US9005", status="Draft", date="2026-01-01")
        report = backlog_triage.triage(self.root, today="2026-07-16")
        by_lens = {f["lens"]: [u for x in report["findings"] if x["lens"] == f["lens"]
                               for u in x["units"]] for f in report["findings"]}
        self.assertIn("CR9004", by_lens.get("unruled", []))
        self.assertIn("CR9005", by_lens.get("abandoned", []))
        # Both NEGATIVES too. Without them the criterion says "each under its own lens" while the
        # fixture only checks that each appears under one - a mutant reading dates from ALL
        # children instead of the OPEN ones put CR9004 under both and survived.
        self.assertNotIn("CR9004", by_lens.get("abandoned", []),
                         "a request finished by its children is unruled, not abandoned")
        self.assertNotIn("CR9005", by_lens.get("unruled", []),
                         "a request with open children has not been finished by them")

    def test_a_proposed_request_with_idle_children_is_not_abandoned(self) -> None:
        """Scoped to In Progress, which is what the shape means. A Proposed request whose
        children are idle has not been abandoned, it has not been started."""
        self._request("CR9007", status="Proposed", date="2026-07-16", children=["US9007"])
        self._child("US9007", status="Draft", date="2026-01-01")
        report = backlog_triage.triage(self.root, today="2026-07-16")
        abandoned = [f for f in report["findings"] if f["lens"] == "abandoned"]
        self.assertFalse(any("CR9007" in f["units"] for f in abandoned))

    def test_a_child_carrying_no_date_at_all_does_not_crash_the_sweep(self) -> None:
        """The guard above the aggregation is load-bearing and had no cover: an open child with
        no `Date`, `Created`, `Updated` or Revision History gives `max([])` -> ValueError out of
        `triage()`, in a path both `status` and `sprint plan` call."""
        self._request("CR9008", date="2026-01-01", children=["US9008"])
        d = self.root / "sdlc-studio" / "stories"
        d.mkdir(parents=True, exist_ok=True)
        (d / "US9008-x.md").write_text("# US9008: a child\n\n> **Status:** Draft\n",
                                       encoding="utf-8")
        report = backlog_triage.triage(self.root, today="2026-07-16")   # must not raise
        abandoned = [f for f in report["findings"] if f["lens"] == "abandoned"]
        self.assertFalse(any("CR9008" in f["units"] for f in abandoned),
                         "a request whose open work records no date cannot be judged idle")

    def test_the_finding_is_advisory_and_never_blocks(self) -> None:
        """The sibling `unruled` lens shipped this test a day earlier and this one dropped it.
        Flipping the severity to `block` sets `report['blocked']`, makes `check` exit 1 and
        refuses `sprint plan` - and it would fire today, on three live findings."""
        self._request("CR9009", date="2026-07-16", children=["US9009"])
        self._child("US9009", status="Draft", date="2026-01-01")
        report = backlog_triage.triage(self.root, today="2026-07-16")
        abandoned = [f for f in report["findings"] if f["lens"] == "abandoned"]
        self.assertTrue(abandoned)
        self.assertEqual({"report"}, {f["severity"] for f in abandoned})
        self.assertFalse(report["blocked"], "an advisory lens must not refuse a plan")
        self.assertIn("abandoned", backlog_triage.render(report))

    def test_the_oldest_idle_child_decides_not_the_newest(self) -> None:
        """A request is as idle as its MOST RECENTLY touched open child - if anything is moving,
        the request is not abandoned. `min` instead of `max` reverses that, and no fixture had
        two open children so the aggregation rule the lens turns on was untested."""
        self._request("CR9010", date="2026-07-16", children=["US9010", "US9011"])
        self._child("US9010", status="Draft", date="2026-01-01")   # long idle
        self._child("US9011", status="Draft", date="2026-07-10")   # moving
        report = backlog_triage.triage(self.root, today="2026-07-16")
        abandoned = [f for f in report["findings"] if f["lens"] == "abandoned"]
        self.assertFalse(any("CR9010" in f["units"] for f in abandoned),
                         "one child still moving means the request is not abandoned")

    def test_the_threshold_boundary_is_exclusive_on_the_day_before(self) -> None:
        """The one tunable constant, argued at length and pinned by nothing: every value from 7
        to 57 passed the module. These two fixtures sit either side of 45."""
        self._request("CR9012", date="2026-07-16", children=["US9012"])
        self._child("US9012", status="Draft", date="2026-06-02")   # 44 days idle
        self._request("CR9013", date="2026-07-16", children=["US9013"])
        self._child("US9013", status="Draft", date="2026-06-01")   # 45 days idle
        report = backlog_triage.triage(self.root, today="2026-07-16")
        named = {u for f in report["findings"] if f["lens"] == "abandoned" for u in f["units"]}
        self.assertNotIn("CR9012", named, "44 days idle is under the threshold")
        self.assertIn("CR9013", named, "45 days idle is at it")

    def test_only_a_request_is_judged_abandoned_never_an_epic(self) -> None:
        """The type scope. I claimed dropping it was an equivalent mutant; the reviewer built the
        distinguishing input and it is not - an In Progress EPIC naming an idle story parses into
        the backlog and would be reported. An epic is delivery work, and `abandoned` is a question
        about a REQUEST nobody is carrying forward."""
        d = self.root / "sdlc-studio" / "epics"
        d.mkdir(parents=True, exist_ok=True)
        (d / "EP9300-x.md").write_text(
            "# EP9300: an epic\n\n> **Status:** In Progress\n"
            "> **Decomposed-into:** US9300\n> **Date:** 2026-07-16\n", encoding="utf-8")
        self._child("US9300", status="Draft", date="2026-01-01")
        report = backlog_triage.triage(self.root, today="2026-07-16")
        abandoned = [f for f in report["findings"] if f["lens"] == "abandoned"]
        self.assertFalse(any("EP9300" in f["units"] for f in abandoned))

    def test_the_lens_is_not_inert_against_the_real_corpus(self) -> None:
        """AC5, and the criterion that matters most. The shipped `unruled` lens is CORRECT and its
        mutants are killed, yet it reports ZERO against this repository - a detector proved only
        on a fixture is the inert-mechanism class this project has paid for repeatedly. Skipped
        rather than failed outside the dev repo, because a consuming project's backlog is its own
        and says nothing about this lens."""
        if not workspace.in_dev_repo():
            self.skipTest("not the dev repo - a consuming backlog cannot pin this lens")
        report = backlog_triage.triage(workspace.REPO)
        abandoned = [f for f in report["findings"] if f["lens"] == "abandoned"]
        self.assertGreater(len(abandoned), 0,
                           "the lens reports nothing against the very backlog it was built for, "
                           "which is the defect BG0722 records about its predecessor")

    def test_a_request_with_no_children_is_not_reported(self) -> None:
        """A request nobody has decomposed is the separate `undecomposed` case `status` already
        counts. Reporting it here as well would make one problem look like two."""
        self._request("CR9006", date="2026-01-01", children=[])
        report = backlog_triage.triage(self.root, today="2026-07-16")
        abandoned = [f for f in report["findings"] if f["lens"] == "abandoned"]
        self.assertFalse(any("CR9006" in f["units"] for f in abandoned))


if __name__ == "__main__":
    unittest.main()
