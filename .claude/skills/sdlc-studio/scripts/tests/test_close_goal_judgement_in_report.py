"""BG0987: the close's goal judgement reaches the sprint report the signer is told to read.

`close_goal_judgement` printed the goal panel's verdict, the open defects judged against the goal
and the caller-check to the terminal only, so the filed report carried none of them; and each
priority-floor defect read 'blocks the close' of a close that did not refuse on it. Driven
through the shipped `sprint close` (the lean close fixture, its chain steps stubbed green) with a
recorded goal-review round, an author on the run and an open High bug outside the batch; the
report is read as filed, JSON and Markdown twin, rendered as the HTML page, and through
`sprint_report.revalidate`. The
judgement is its own section, never rows of the Known issues table, which lists open findings.

MUTANTS, each of which a test here fails on: (1) the judgement is printed and not recorded, so
the page carries none of it; (2) the panel, its per-clause verdicts, a blocking defect, the
defect count or the caller-check is left off the page; (3) a priority-floor defect is labelled
as falsifying the goal, or a clause defect as a release stopper, on the close's line or the
report's row; (4) the close refuses on a priority-floor defect; (5) the recorded judgement is
re-read live at revalidation, so the page no longer re-derives; (6) the judgement is written into
the Known issues table; (7) the HTML page leaves the section out; (8) the defects detail for a
goal with no clause is dropped, so the page reads `none open` over open defects.

BG1692: the clause half is judged from the bug file itself. `_open_defects` reads a bug's
`Falsifies` header field, so the close runs unpatched; MUTANTS: the field never read (the bug
ruled leavable, `0 BLOCKING`); read from a bug that is not open; read when empty, above another
header line whose `>` `extract_field` reads on into; read when it holds only `>`, `·` or another
field.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import test_lean_close as lean  # noqa: E402 - the close fixture, shared

BUG = "BG0901"
#: A Low bug that falsifies the fixture's one goal clause, so its basis is `clause`.
CLAUSE_BUG = "BG0902"
GOAL = "the close finishes in one pass"
AUTHOR = "Dani Okafor (engineering)"


def _closed(falsifies: str | None = None) -> tuple[int, str, dict, str, str]:
    """`(rc, stdout, the filed report, its Markdown twin, its HTML page)` for one close over the
    fixture. With `falsifies`, a second open bug, Low, carries `> **Falsifies:** <falsifies>`
    in its header, which the close reads from the file: nothing in the close is patched."""
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        lean._fixture(root, author=AUTHOR)
        bugs = root / "sdlc-studio" / "bugs"
        bugs.mkdir(parents=True)
        (bugs / f"{BUG}-a-release-stopper.md").write_text(
            f"# {BUG}: a release stopper\n\n> **Status:** Open\n> **Severity:** High\n"
            "> **Raised-in-batch:** none open - raised outside a delivery batch, "
            "2026-09-23T13:28:22Z\n", encoding="utf-8")
        (root / "sdlc-studio" / ".local" / "goal-review.json").write_text(json.dumps({
            "rounds": [{"goal": GOAL, "seats": [
                {"seat": "qa", "achievable": "yes", "done_means": "x", "one_increment": "yes"}]}]
        }), encoding="utf-8")
        if falsifies:
            (bugs / f"{CLAUSE_BUG}-a-goal-breaker.md").write_text(
                f"# {CLAUSE_BUG}: a goal breaker\n\n> **Status:** Open\n> **Severity:** Low\n"
                f"> **Falsifies:** {falsifies}\n", encoding="utf-8")
        with unittest.mock.patch.dict(os.environ, gitutil.git_env(), clear=True):
            rc, out, err = lean._close(root)
            assert rc == 0, err
            state = lean._read(root)
            report = json.loads((root / "sdlc-studio" / "reports" / f"{state['report']}.json")
                                .read_text(encoding="utf-8"))
            twin = next((root / "sdlc-studio" / "reports").glob(f"{state['report']}-*.md"))
            check = lean._live("sprint_report").revalidate(root, state["report"])
            assert check["valid"], (check["changes"], check["edited"])
            page = lean._live("sprint_report").render_html(report)
            return rc, out, report, twin.read_text(encoding="utf-8"), page


def _rows(report: dict) -> list[tuple[str, str, str]]:
    section = next(s for s in report["sections"] if s["key"] == "goal_judgement")
    return [(r["judged_item"]["value"], r["judged_ruling"]["value"], r["judged_detail"]["value"])
            for r in section["rows"]]


def _known_issues(report: dict) -> list[tuple[str, str, str]]:
    section = next(s for s in report["sections"] if s["key"] == "known_issues")
    return [(r["issue_id"]["value"], r["issue_priority"]["value"], r["issue_detail"]["value"])
            for r in section["rows"]]


class CloseGoalJudgementInReportTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.rc, cls.out, cls.report, cls.twin, cls.html = _closed()
        cls.clause_rc, cls.clause_out, cls.clause_report, _twin, _page = _closed(falsifies=GOAL)

    def test_report_carries_goal_judgement(self) -> None:
        rows = _rows(self.report)
        panel = [r for r in rows if r[1] == "goal panel"]
        self.assertEqual(1, len(panel), rows)
        # The panel's line AND its per-clause verdict, each clause in full.
        self.assertEqual("UNANSWERED over 1 clause(s), 1 seat(s), no seat matched the author; "
                         f"UNANSWERED (1 seat(s) silent): {GOAL}", panel[0][2])
        self.assertIn("goal panel: UNANSWERED over 1 clause(s)", self.out,
                      "the page and the terminal give the panel different verdicts")
        defect = [r for r in rows if r[0] == BUG and r[1] == "would block a release"]
        self.assertEqual(1, len(defect), f"the blocking defect is not on the page: {rows}")
        self.assertIn("priority high", defect[0][2])
        self.assertEqual([("open defects", "defects vs goal", "1 BLOCKING, 0 leavable")],
                         [r for r in rows if r[1] == "defects vs goal"], rows)
        caller = [r for r in rows if r[1] == "caller-check"]
        self.assertEqual(1, len(caller), rows)
        self.assertRegex(caller[0][2], r"^\d+ unit\(s\) of 1 ship a mechanism with no named caller")
        section = self.twin[self.twin.index("### Goal judgement"):]
        for item, label, detail in rows:
            self.assertIn(f"| {item} | {label} | {detail} |", section,
                          "the Markdown twin the signer reads does not carry it")
        page = self.html[self.html.index("<h3>Goal judgement</h3>"):]
        page = page[:page.index("<h3>Tokens by model</h3>")]
        for item, label, detail in rows:
            self.assertIn(f'<tr><th scope="row"><span class="uid">{item}</span></th>'
                          f'<td><span class="pill">{label}</span></td><td>{detail}</td></tr>',
                          page, "the HTML page does not carry it")
        # The bug is also an open finding the run raised: the Known issues table lists it as a
        # finding, and carries no row of the judgement.
        known = _known_issues(self.report)
        self.assertIn((BUG, "High", "a release stopper"), known, known)
        self.assertEqual([], [r for r in known if r[1] in {label for _i, label, _d in rows}],
                         "the goal judgement is written into the Known issues table")

    def test_blocking_defects_carry_a_structured_basis(self) -> None:
        critic = lean._live("critic")
        ruling = critic.judge_defects_against_goal(
            [{"id": "BG0001", "priority": "High"},
             {"id": "BG0002", "priority": "Low", "falsifies": "seams have owners"},
             {"id": "BG0003", "priority": "Low"}], ["seams have owners"])
        self.assertEqual({"BG0001": "priority", "BG0002": "clause"},
                         {d["id"]: d["basis"] for d in ruling["blocking"]})
        self.assertEqual(["BG0003"], [d["id"] for d in ruling["leavable"]])
        for d in ruling["blocking"]:
            self.assertNotIn("blocks the close", d["why"],
                             "a defect the close does not refuse on reads as blocking it")
        self.assertIn("falsifies the goal clause: seams have owners",
                      next(d["why"] for d in ruling["blocking"] if d["id"] == "BG0002"))
        self.assertIn(f"WOULD BLOCK A RELEASE {BUG}: priority high", self.out,
                      "the close's line is not labelled from the defect's basis")
        self.assertNotIn(f"BLOCKS THE GOAL CLAIM {BUG}", self.out)
        self.assertNotIn(BUG, [r[0] for r in _rows(self.report) if r[1] == "blocks the goal claim"])
        self.assertEqual(0, self.rc, "a close whose only blocking defect is a priority floor "
                                     "must not refuse")

    def test_a_falsifies_field_in_the_bug_file_blocks_the_goal_claim(self) -> None:
        """BG1692 AC1. The clause half, over a Low bug whose file carries `Falsifies` and a
        close whose `_open_defects` is the shipped one: the bug is labelled as blocking the goal
        claim, on the close's line and on the report's row, beside the priority one, and the
        close does not refuse on it."""
        why = f"falsifies the goal clause: {GOAL}"
        self.assertIn(f"BLOCKS THE GOAL CLAIM {CLAUSE_BUG}: {why}", self.clause_out)
        self.assertNotIn(f"WOULD BLOCK A RELEASE {CLAUSE_BUG}", self.clause_out)
        self.assertIn(f"WOULD BLOCK A RELEASE {BUG}: priority high", self.clause_out)
        rows = _rows(self.clause_report)
        self.assertEqual([(CLAUSE_BUG, "blocks the goal claim", why)],
                         [r for r in rows if r[0] == CLAUSE_BUG], rows)
        self.assertEqual([BUG], [r[0] for r in rows if r[1] == "would block a release"], rows)
        self.assertEqual(0, self.clause_rc, "the close refused on a clause-basis defect")
        self.assertEqual([("open defects", "defects vs goal", "2 BLOCKING, 0 leavable")],
                         [r for r in rows if r[1] == "defects vs goal"], rows)

    def test_defects_the_goal_cannot_judge_say_why(self) -> None:
        """MUTANT: drop the defects detail for a goal with no clause, so the record and the page
        read `none open` over an open defect. `sprint close` refuses a run with no sprint goal,
        so the judgement is called as the close calls it, over a run state with none."""
        sprint, sprint_report = lean._live("sprint"), lean._live("sprint_report")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            bugs = root / "sdlc-studio" / "bugs"
            bugs.mkdir(parents=True)
            (bugs / f"{BUG}-a-release-stopper.md").write_text(
                f"# {BUG}: a release stopper\n\n> **Status:** Open\n> **Severity:** High\n",
                encoding="utf-8")
            record: dict = {}
            sprint.close_goal_judgement(root, {"sprint_goal": "", "batch": []}, record=record)
            detail = ("not judged - 1 open, and the sprint goal states no clause to judge them "
                      "against")
            self.assertEqual(detail, record["defects"])
            self.assertEqual([], record["blocking"])
            section = sprint_report._goal_judgement_section(
                root, {sprint_report.CLOSE_GOAL_JUDGEMENT: record}, "run-state.json")
            rows = [(r["judged_item"]["value"], r["judged_ruling"]["value"],
                     r["judged_detail"]["value"]) for r in section["rows"]]
            self.assertIn(("open defects", "defects vs goal", detail), rows)


class CloseSeverityFloorTests(unittest.TestCase):
    """The close judges the open defects against the project's own severity floor,
    `review.blocking_priority`, not the shipped `high`: called without the project root, the
    judge read the shipped floor whatever the project set."""

    @staticmethod
    def _judged(setting: str | None) -> dict:
        """The close's goal judgement record over one open Medium bug and a one-clause goal,
        under `review.blocking_priority: setting` (None: no setting)."""
        sprint = lean._live("sprint")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            bugs = root / "sdlc-studio" / "bugs"
            bugs.mkdir(parents=True)
            (bugs / "BG0931-a-medium-finding.md").write_text(
                "# BG0931: a medium finding\n\n> **Status:** Open\n> **Severity:** Medium\n\n"
                "## Summary\n\nThe parser drops a tab.\n", encoding="utf-8")
            if setting:
                (root / "sdlc-studio" / ".config.yaml").write_text(
                    f"review:\n  blocking_priority: {setting}\n", encoding="utf-8")
            record: dict = {}
            sprint.close_goal_judgement(root, {"sprint_goal": GOAL, "batch": []}, record=record)
            return record

    def test_an_open_medium_blocks_the_close_where_the_project_bars_medium(self) -> None:
        """With `medium` set, an open Medium is BLOCKING on its priority; with no setting it
        stays leavable under the shipped `high` (the control). MUTANT: the close's judge called
        without the project root."""
        barred = self._judged("medium")
        self.assertEqual("1 BLOCKING, 0 leavable", barred["defects"], barred)
        self.assertEqual([("BG0931", "priority")],
                         [(b["id"], b["basis"]) for b in barred["blocking"]], barred)
        shipped = self._judged(None)
        self.assertEqual("0 BLOCKING, 1 leavable", shipped["defects"], shipped)
        self.assertEqual([], shipped["blocking"], shipped)


class OpenDefectsFalsifiesTests(unittest.TestCase):

    @staticmethod
    def _defects(*bugs: tuple[str, str, str]) -> dict[str, dict]:
        """`_open_defects` over a project holding each `(id, status, field line)` bug, the field
        line written between its Status and its Severity, as a filer writes a header."""
        sprint = lean._live("sprint")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            folder = root / "sdlc-studio" / "bugs"
            folder.mkdir(parents=True)
            for uid, status, extra in bugs:
                (folder / f"{uid}-x.md").write_text(
                    f"# {uid}: x\n\n> **Status:** {status}\n{extra}> **Severity:** Low\n\n"
                    f"## Summary\n\nThe parser drops a tab.\n", encoding="utf-8")
            return {x["id"]: x for x in sprint._open_defects(root)}

    def test_open_defects_reads_falsifies_only_where_declared(self) -> None:
        """BG1692 AC2. An Open bug declaring `Falsifies`, an Open one with none, a Fixed one
        declaring it, and an In Progress one whose field is empty above its Severity line: only
        the first carries `falsifies`, with the field's text, and the Fixed bug is not listed.
        The empty field sits above another header line, where `extract_field` reads on into
        that line and returns its `>`."""
        got = self._defects(
            ("BG0911", "Open", "> **Falsifies:** the parser keeps every tab\n"),
            ("BG0912", "Open", ""),
            ("BG0913", "Fixed", "> **Falsifies:** the parser keeps every tab\n"),
            ("BG0914", "In Progress", "> **Falsifies:**\n"))
        self.assertEqual(["BG0911", "BG0912", "BG0914"], sorted(got))
        self.assertEqual("the parser keeps every tab", got["BG0911"]["falsifies"])
        self.assertNotIn("falsifies", got["BG0912"])
        self.assertNotIn("falsifies", got["BG0914"])
        self.assertEqual("Low", got["BG0911"]["priority"])
        self.assertEqual("Low", got["BG0914"]["priority"])

    def test_a_falsifies_field_holding_only_header_text_declares_nothing(self) -> None:
        """A field whose value is only header punctuation or another field declares no clause,
        while a clause on a `·` run is still read. MUTANTS: the punctuation guard dropped (`>`
        and `·` read as clauses); the field guard dropped (the next field read as the clause)."""
        got = self._defects(
            ("BG0921", "Open", "> **Falsifies:** >\t>\n"),
            ("BG0922", "Open", "> **Points:** 1 · **Falsifies:** · **Epic:** EP0001\n"),
            ("BG0923", "Open", "**Falsifies:** **Epic:** EP0001\n"),
            ("BG0924", "Open", "> **Points:** 1 · **Falsifies:** every tab is kept\n"),
            ("BG0925", "Open", "> **Falsifies:**\n> the parser keeps every tab\n"))
        self.assertEqual({"BG0924": "every tab is kept"},
                         {uid: d["falsifies"] for uid, d in got.items() if "falsifies" in d})
        self.assertEqual(5, len(got))


if __name__ == "__main__":
    unittest.main()
