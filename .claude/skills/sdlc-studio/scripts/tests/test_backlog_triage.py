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


if __name__ == "__main__":
    unittest.main()
