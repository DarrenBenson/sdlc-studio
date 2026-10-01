"""BG0865: the signed page names each known issue's ruling, and lists what the close files.

The Known issues section carried a ruling only for a STOP-SHIP; a finding the retro ruled
not-stop-ship, accepted-risk or deferred read exactly like one nobody ruled, so the operator
signed without seeing the rulings at all. And a finding the close itself files (a lesson's
graduation CR) in the second the page is generated fell outside the page's `[start, end)` window.

Driven through `sprint.py close` (the lean close fixture, chain stubbed green except the steps
under test) in throwaway trees; AC3 checks this repository's own signed pages, read-only.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint_report.py
from __future__ import annotations

import json
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone
import unittest
import unittest.mock
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import test_lean_close as lean  # noqa: E402 - the close fixture, shared

REPO = HERE.parents[4]
#: The instant the close runs at, for every clock it reads: the close files and derives at once.
NOW = "2026-10-01T09:00:00Z"


def _retro(root: Path, rows: str) -> None:
    """RETRO0001 in the three-line shape, naming the run, with the carried table and `rows`."""
    retro = lean._live("retro")
    (root / "sdlc-studio" / "retros" / "RETRO0001-lean.md").write_text(
        "# RETRO-0001: lean\n\n> **Date:** 2026-09-23\n> **Run:** RUN-LEAN0001\n"
        "> **Batch:** US0101\n\n## Keep\n\n- small units\n\n## Stop\n\n- hand tables\n\n"
        "## Try\n\n- name the mutant first\n\n## Known issues carried\n\n"
        f"{retro.known_issues_table()}\n{rows}", encoding="utf-8")


def _known_issues(root: Path) -> dict:
    """The filed page's Known issues rows: `{issue id: detail}`."""
    state = lean._read(root)
    page = lean._live("sprint_report").read_report(root, state["report"])
    sec = next(s for s in page["sections"] if s["key"] == "known_issues")
    return {r["issue_id"]["value"]: r["issue_detail"]["value"] for r in sec.get("rows") or []}


class KnownIssueRulingTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        env = unittest.mock.patch.dict(os.environ, {
            lean._live("sprint").run_state.TRANSCRIPTS_ENV: "/nonexistent-transcripts"})
        env.start()
        self.addCleanup(env.stop)

    def test_each_known_issue_names_its_retro_ruling(self) -> None:
        """AC1. MUTANTS: HEAD, whose rows carry no ruling unless STOP-SHIP; a ruling that drops
        who ruled; one ruling applied to every row."""
        root = self.root
        lean._fixture(root, batch=["US0101", "US0102"])
        critic = lean._live("critic")
        for issues in ("[new] the widget drops a row", "[new] the widget still drops it"):
            critic.record_verdict(root, "US0101", "REJECT", reviewer="rev-a", author="builder",
                                  issues=issues)
        carried = next(c["reason"].split(":", 1)[1].strip()
                       for c in lean._read(root)["batch_changes"]
                       if c["id"] == "US0101")
        other = lean._live("file_finding").file_finding(root, "bug", "the widget logs twice", {
            "severity": "Medium", "points": "2", "affects": "src/widget.py",
            "summary": "The widget writes each line to the log twice when it restarts.",
            "steps": "1. Restart the widget and read the log.",
            "fix": "Write the line once."})["id"]
        carried, other = (lean._live("sprint").sdlc_md.norm_id(x) for x in (carried, other))
        _retro(root, f"| {carried} | not-stop-ship | Maya | 2026-10-01 |\n"
                     f"| {other} | accepted-risk | Darren | 2026-10-01 |\n")
        # The close an hour after the findings were filed, so the window holds them whatever
        # second this test runs in: this criterion is about the rulings, not the boundary.
        later = (datetime.now(timezone.utc) + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        sdlc_md = lean._live("sprint").sdlc_md
        with unittest.mock.patch.object(sdlc_md, "now_iso8601", lambda *a, **k: later):
            rc, _out, err = lean._close(root)
        self.assertEqual(0, rc, err)
        rows = _known_issues(root)
        self.assertIn(carried, rows, f"premise: the carried bug is not a known issue: {rows}")
        self.assertIn(other, rows, f"premise: the open finding is not a known issue: {rows}")
        self.assertTrue(rows[carried].endswith(" - not-stop-ship, ruled by Maya"), rows[carried])
        self.assertTrue(rows[other].endswith(" - accepted-risk, ruled by Darren"), rows[other])
        # And on the Markdown twin the operator reads.
        md = next((root / "sdlc-studio" / "reports").glob("RPT0001-*.md")).read_text(
            encoding="utf-8")
        self.assertIn("not-stop-ship, ruled by Maya", md)

    def test_a_finding_the_close_files_is_on_the_page(self) -> None:
        """AC2. MUTANTS: HEAD's `[start, end)` window, which excludes the graduation CR the close
        files in the page's own second; an end inclusive for every finding, which would also take
        one a later run files in that second (the control below)."""
        root = self.root
        lean._fixture(root)
        (root / "sdlc-studio" / ".config.yaml").write_text("schema_version: 3\n",
                                                          encoding="utf-8")
        (root / "sdlc-studio" / "lessons.jsonl").write_text(json.dumps({
            "id": "LC-900", "class": "class 900", "rule": "Rule 900 holds.",
            "behaviour": "Behaviour 900 follows.", "inject": ["build"], "state": "active",
            "recorded_run": "RUN-0",
            "hits": [{"run": "RUN-1", "unit": "US0001", "source": "critic:RUN-1"},
                     {"run": "RUN-2", "unit": "US0002", "source": "critic:RUN-2"}]}) + "\n",
            encoding="utf-8")
        _retro(root, "| LC-900 | deferred | Maya | 2026-10-01 |\n")
        # The control: a finding stamped in that same second by ANOTHER run is not this run's.
        bugs = root / "sdlc-studio" / "bugs"
        bugs.mkdir(parents=True, exist_ok=True)
        (bugs / "BG0901-later.md").write_text(
            "# BG0901: a later run's finding\n\n> **Status:** Open\n> **Severity:** Medium\n"
            f"> **Raised-in-batch:** RUN-LATER close, {NOW}\n", encoding="utf-8")
        sdlc_md = lean._live("sprint").sdlc_md
        with unittest.mock.patch.object(sdlc_md, "now_iso8601", lambda *a, **k: NOW):
            rc, out, err = lean._close(root, real=("retro-extract",))
        self.assertEqual(0, rc, err)
        self.assertIn("LC-900 graduating -> CR", out + err, "premise: no graduation CR")
        rows = json.loads((root / "sdlc-studio" / "lessons.jsonl").read_text(
            encoding="utf-8").splitlines()[0])
        cr = rows["cr"]
        listed = _known_issues(root)
        self.assertIn(cr, listed, f"the close's own graduation CR is not on the page: {listed}")
        self.assertTrue(listed[cr].endswith(" - deferred, ruled by Maya"), listed[cr])
        self.assertNotIn("BG0901", listed, "a finding another run filed in that second is listed")

    def test_signed_pages_stay_valid(self) -> None:
        """AC3. MUTANT: re-deriving an old page's finding rows with the ruling appended, a row
        the signed page does not hold."""
        report = lean._live("sprint_report")
        for rid in ("RPT0011", "RPT0012"):
            with self.subTest(report=rid):
                if not (REPO / "sdlc-studio" / "reports" / f"{rid}.json").is_file():
                    self.skipTest(f"{rid} is this repository's own page")
                check = report.revalidate(REPO, rid)
                self.assertTrue(check["valid"], check["changes"])


if __name__ == "__main__":
    unittest.main()
