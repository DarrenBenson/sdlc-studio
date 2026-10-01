"""BG0851: the sprint report states the operator's own interventions.

The page read "the operator ruled 0 time(s)" over a `sprint.py decision resolve`, and "no gate
stood down for this seal" over units moved with `transition.py set --force` inside the run,
including a unit dropped from the batch before it was forced (RPT0012's BG0852). Listing them
must not move a signed page: an override written after the seal, and a page signed before the
rule, still check VALID.

Driven through `sprint.py`, `decisions.py`, `transition.py` and `sprint_report.py`, the shipped
entry points, in throwaway trees - except AC4, which checks this repository's own signed RPT0012
read-only, because that page is the case the criterion names.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint_report.py
from __future__ import annotations

import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import test_lean_close as lean  # noqa: E402 - the close fixture, shared
import test_lean_sign as signing  # noqa: E402 - the sign fixture, shared

REPO = HERE.parents[4]


def _cli(name: str, root: Path, *argv: str) -> str:
    """A sibling script's `main`, quietly; a non-zero exit fails with its output."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        rc = lean._live(name).main([*argv, "--root", str(root)])
    assert rc == 0, f"{name} {' '.join(argv)} exited {rc}:\n{out.getvalue()}"
    return out.getvalue()


def _story(root: Path, uid: str, override: str = "") -> None:
    """A story at Review whose criterion is unverified, so its Done gate refuses unforced."""
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    extra = f"> **Forced-override:** {override}\n" if override else ""
    (d / f"{uid}-x.md").write_text(
        f"# {uid}: x\n\n> **Status:** Review\n> **Points:** 2\n> **Epic:** EP0001\n{extra}\n"
        "## Acceptance Criteria\n\n### AC1: works\n- **Verify:** shell true\n", encoding="utf-8")


def _report(root: Path) -> dict:
    return lean._live("sprint_report").build_report(root, "RETRO0001")


def _section(report: dict, key: str) -> dict:
    return next(s for s in report["sections"] if s["key"] == key)


def _waiver_ids(report: dict) -> list[str]:
    return [r["waiver_id"]["value"] for r in _section(report, "waivers").get("rows") or []]


class OperatorInterventionTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        env = unittest.mock.patch.dict(os.environ, {
            lean._live("sprint").run_state.TRANSCRIPTS_ENV: "/nonexistent-transcripts"})
        env.start()
        self.addCleanup(env.stop)

    def test_a_resolved_decision_counts_as_an_operator_ruling(self) -> None:
        """AC1. MUTANT: HEAD's resolve, which writes no ruling, so the section reads NOT
        MEASURED on a run with no `rulings` list; a ruling recorded `by` persona."""
        lean._fixture(self.root, batch=["US0101", "US0102"])
        _cli("sprint", self.root, "decision", "defer", "--unit", "US0101", "--question",
             "Force US0101 to Done?", "--option", "force|it ships as it stands",
             "--option", "wait|it waits a run")
        _cli("sprint", self.root, "decision", "resolve", "--index", "1", "--choice", "force",
             "--note", "the operator forced it")
        report = _report(self.root)
        page = lean._live("sprint_report").render_markdown(report)
        self.assertIn("the operator ruled 1 time(s)", page)
        self.assertEqual(1, _section(report, "rulings")["figures"]["operator_rulings"]["value"])
        _cli("decisions", self.root, "add", "--decision", "raise the cap once",
             "--rationale", "one more round", "--by", "operator")
        page = lean._live("sprint_report").render_markdown(_report(self.root))
        self.assertIn("the operator ruled 2 time(s)", page)

    def test_every_forced_override_in_the_window_is_listed(self) -> None:
        """AC2. MUTANTS: HEAD ("no gate stood down"); the batch's current units only, which
        omits the dropped US0102 (the RPT0012 shape); every Forced-override whatever its date,
        which lists US0103's from before the run."""
        lean._fixture(self.root, batch=["US0101", "US0102", "US0103"])
        _story(self.root, "US0102")       # US0101 is the close fixture's own story at Review
        _story(self.root, "US0103", "2026-09-01: --force waived 1 gate(s) on Done - long ago")
        _cli("sprint", self.root, "batch", "drop", "US0102", "--reason", "out of scope")
        for uid in ("US0101", "US0102"):
            _cli("transition", self.root, "set", "--id", uid, "--status", "Done", "--force")
        report = _report(self.root)
        self.assertEqual(["US0101", "US0102"], sorted(_waiver_ids(report)))
        rows = {r["waiver_id"]["value"]: r for r in _section(report, "waivers")["rows"]}
        for uid in ("US0101", "US0102"):
            self.assertIn("1 gate(s) on Done", rows[uid]["waiver_subject"]["value"])
            self.assertTrue(rows[uid]["waiver_reason"]["value"].strip(), rows[uid])
        note = _section(report, "waivers")["figures"]["waivers_note"]["value"]
        self.assertNotIn("no gate stood down", note)

    def test_an_override_after_the_seal_does_not_move_the_signed_page(self) -> None:
        """AC3. MUTANT: re-deriving without the filed page's reading, which places the late
        date-only Forced-override in the window, lists it and prints INVALIDATED."""
        root = self.root
        lean._fixture(root, batch=["US0101", "US0102"])
        _story(root, "US0102")
        env = signing._git_repo(root)
        with unittest.mock.patch.dict(os.environ, env):
            _cli("sprint", root, "batch", "drop", "US0102", "--reason", "carried")
            rc, _out, err = lean._close(root)
            self.assertEqual(0, rc, err)
            later = {**env, "GIT_COMMITTER_DATE": "2099-01-01T00:00:00Z"}
            for argv in (["add", "-A"], ["commit", "-q", "-m", "close paperwork"]):
                subprocess.run(["git", "-C", str(root), *argv], env=later, check=True,
                               capture_output=True)
            rc, _out, err = signing._sign(root)
            self.assertEqual(0, rc, err)
            for argv in (["add", "-A"], ["commit", "-q", "-m", "seal"]):
                subprocess.run(["git", "-C", str(root), *argv], env=later, check=True,
                               capture_output=True)
            _cli("transition", root, "set", "--id", "US0102", "--status", "Done", "--force")
            # The premise: read afresh, the late override sits in the window and is listed.
            self.assertIn("US0102", _waiver_ids(_report(root)))
            check = lean._live("sprint_report").revalidate(root, "RPT0001")
        self.assertTrue(check["valid"], check["changes"])

    def test_a_page_signed_before_the_rule_still_checks_valid(self) -> None:
        """AC4. MUTANT: the new rule applied to a page signed before it, which lists BG0852's
        in-window override on the re-derivation, a row RPT0012 does not hold."""
        report = REPO / "sdlc-studio" / "reports" / "RPT0012.json"
        if not report.is_file():
            self.skipTest("RPT0012 is this repository's own page")
        bug = next((REPO / "sdlc-studio" / "bugs").glob("BG0852-*.md")).read_text(
            encoding="utf-8")
        self.assertTrue(lean._live("sprint_report").sdlc_md.extract_field(
            bug, "Forced-override").startswith("2026-09-30"), "premise: BG0852's override")
        check = lean._live("sprint_report").revalidate(REPO, "RPT0012")
        self.assertTrue(check["valid"], check["changes"])


if __name__ == "__main__":
    unittest.main()
