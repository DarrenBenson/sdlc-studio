"""`critic.py approach brief`: a seat's review brief for a builder's approach note, and the code
review brief that carries none of the solution review.

Every brief goes through the shipped `critic.py` CLI against a throwaway project; the runbook and
catalogue test reads THIS repository's shipped pages, as the criterion names them.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

critic = loader.load_script("critic")
persona_resolve = loader.load_script("persona_resolve")
sdlc_md = critic.sdlc_md
from lib import run_state  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent.parent
SKILL = SCRIPTS.parent
ON = "review:\n  solution_review:\n    min_points: 2\n"
#: A project engineering seat with its work render and the review render's three sections, the
#: floor the persona standard holds a seat card to before it frames any brief.
PROJECT_SEAT = ("<!-- role: engineering -->\n# Ola - the project's engineer\n\n"
                "## How They Work *(work render)*\n\nSmall diffs, test first.\n"
                "\n## Lens\n\nx\n\n## Pushes Back When\n\nx\n\n## Shadow\n\nx\n")
AC1_BLOCK = ("### AC1: the widget turns\n\n- **Given** a wound widget\n- **When** it is released\n"
             "- **Then** it turns once\n- **Verify:** pytest tests/test_a.py::T::test_turns")
AC2_BLOCK = ("### AC2: the widget stops\n\n- **Given** a turning widget\n- **When** it is braked\n"
             "- **Then** it stops within a turn\n- **Verify:** pytest tests/test_a.py::T::test_stops")
STORY = ("# US0101: the widget\n\n> **Status:** Ready\n> **Points:** 3\n> **Epic:** EP0001\n"
         "> **Delivers:** CR0001\n> **Affects:** src/a.py, tests/test_a.py\n\n"
         f"## Acceptance Criteria\n\n{AC1_BLOCK}\n\n{AC2_BLOCK}\n\n"
         "## Notes\n\n- Bound by D0101 and by D0199, which the log does not hold; D0101 again.\n")
DECISIONS = {"D0101": "Widgets turn clockwise only.", "D0102": "Every widget carries a brake.",
             "D0103": "A widget stops within one turn.", "D0104": "Widgets are wound by hand."}
SECTIONS = {
    "Reading": "- AC1: \"turns once\" is one full revolution, read from the spindle.",
    "Design": "- `wind()` calls `turn()`, and `brake()` sets the stop flag.",
    "May break": "- tests/test_a.py reads `wind()`; nothing else imports it.",
    "Tests": "- AC1: test_turns, killing `turn()` removed.\n"
             "- AC2: test_stops, killing the stop flag inverted.",
    "Sentences": "- The fragment says a widget turns once and stops within a turn.",
}


def _note(sections: dict[str, str] | None = None, order: list[str] | None = None,
          titles: dict[str, str] | None = None) -> str:
    sections = sections or SECTIONS
    titles = titles or {}
    body = "".join(f"\n## {titles.get(name, name)}\n\n{sections[name]}\n"
                   for name in (order or list(sections)))
    return f"# US0101 approach: the widget\n{body}"


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:12]


def _tree(root: Path) -> dict[str, bytes]:
    return {p.relative_to(root).as_posix(): (p.read_bytes() if p.is_file() else b"<dir>")
            for p in sorted(root.rglob("*"))}


class SolutionReviewBriefTests(unittest.TestCase):

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="srbrief-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.root = self.tmp / "proj"
        sdlc = self.root / "sdlc-studio"
        for sub in ("stories", "epics", "change-requests", "personas/seats", "reviews"):
            (sdlc / sub).mkdir(parents=True)
        (sdlc / "stories" / "US0101-the-widget.md").write_text(STORY, encoding="utf-8")
        (sdlc / "epics" / "EP0001-widgets.md").write_text(
            "# EP0001: Widgets\n\n> **Status:** Draft\n> **Parent:** CR0002\n\n"
            "## Summary\n\nEvery widget follows D0102.\n", encoding="utf-8")
        (sdlc / "change-requests" / "CR0001-widgets-stop.md").write_text(
            "# CR-0001: Widgets stop\n\n> **Status:** In Progress\n\n## Summary\n\n"
            "Per D0103.\n", encoding="utf-8")
        (sdlc / "change-requests" / "CR0002-widgets-exist.md").write_text(
            "# CR-0002: Widgets exist\n\n> **Status:** In Progress\n\n## Summary\n\n"
            "Under D0104.\n", encoding="utf-8")
        rows = "".join(f"| {d} | {text} | because | accepted | -- | 2026-11-01 |\n"
                       for d, text in DECISIONS.items())
        (sdlc / "decisions.md").write_text(
            "# Project Decisions Log\n\n## Decisions\n\n"
            "| ID | Decision | Rationale | Status | Supersedes | Date |\n"
            f"| --- | --- | --- | --- | --- | --- |\n{rows}", encoding="utf-8")
        (sdlc / "personas" / "seats" / "engineering.md").write_text(PROJECT_SEAT,
                                                                     encoding="utf-8")
        self.note = sdlc / ".local" / "lane" / "US0101-approach.md"
        self.note.parent.mkdir(parents=True)
        self.note.write_text(_note(), encoding="utf-8")
        self.env = dict(os.environ, HOME=str(self.tmp / "home"), TMPDIR=str(self.tmp),
                        XDG_CONFIG_HOME=str(self.tmp / "xdg"), XDG_DATA_HOME=str(self.tmp / "xdd"),
                        PYTHONDONTWRITEBYTECODE="1")
        self.rejoinder = self.tmp / "prior-verdict.md"
        self.rejoinder.write_text("VERDICT: REJECT\nISSUES:\n- the widget never stops\n"
                                  "BLOCKING: [new] the widget never stops\n", encoding="utf-8")

    def _critic(self, *argv: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "-B", str(SCRIPTS / "critic.py"), "--root",
                               str(self.root), *argv], capture_output=True, text=True,
                              env=self.env, timeout=120)

    def _brief(self, seat: str = "engineering", note: Path | None = None,
               unit: str = "US0101") -> subprocess.CompletedProcess:
        return self._critic("approach", "brief", "--unit", unit, "--seat", seat, "--note",
                            str(note or self.note))

    def _config(self, text: str) -> None:
        (self.root / "sdlc-studio" / ".config.yaml").write_text(text, encoding="utf-8")

    def _write_note(self, name: str, text: str) -> Path:
        path = self.tmp / name
        path.write_text(text, encoding="utf-8")
        return path

    def _refused(self, run: subprocess.CompletedProcess, *words: str) -> None:
        self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
        self.assertEqual(run.stdout, "")
        for word in words:
            self.assertIn(word, run.stderr)

    def _record(self, verdict: str, reviewer: str, changes: Path | None = None
                ) -> subprocess.CompletedProcess:
        argv = ["approach", "record", "--unit", "US0101", "--verdict", verdict, "--note",
                str(self.note), "--reviewer", reviewer, "--author", "builder (engineering)"]
        run = self._critic(*argv, *(["--changes", str(changes)] if changes else []))
        self.assertEqual(run.returncode, 0, run.stderr)
        return run

    def _code_briefs(self) -> dict[tuple[str, bool], subprocess.CompletedProcess]:
        out = {}
        for seat in ("qa", "engineering"):
            for rejoinder in (False, True):
                extra = ["--rejoinder", str(self.rejoinder)] if rejoinder else []
                run = self._critic("brief", "--unit", "US0101", "--seat", seat, *extra)
                self.assertEqual(run.returncode, 0, f"{seat} {rejoinder}: {run.stderr}")
                out[(seat, rejoinder)] = run
        return out

    # -- the criteria ------------------------------------------------------------------------

    def test_the_brief_holds_what_the_seat_judges_against(self) -> None:
        """AC1. MUTANTS: the epic, Delivers or Parent hop dropped; an id printed twice; the
        decision text omitted; the note block omitted; the CHANGES record command dropped."""
        run = self._brief()
        self.assertEqual(run.returncode, 0, run.stderr)
        out = run.stdout
        card = persona_resolve.review_card(self.root, "engineering")
        self.assertEqual(card.resolve(),
                         (self.root / "sdlc-studio/personas/seats/engineering.md").resolve(),
                         "premise: the project card is the seat's review card")
        self.assertIn(f"{card} (the review render)", out)
        self.assertIn(AC1_BLOCK, out)
        self.assertIn(AC2_BLOCK, out)
        for d, text in DECISIONS.items():
            self.assertEqual(out.count(f"- {d} "), 1, f"{d} once:\n{out}")
            self.assertIn(f"- {d} (accepted): {text}", out)
        self.assertIn("- D0199: not in sdlc-studio/decisions.md", out)
        self.assertLess(out.index("- D0101 "), out.index("- D0102 "))
        self.assertLess(out.index("- D0103 "), out.index("- D0104 "))
        self.assertIn(self.note.read_text(encoding="utf-8").rstrip(), out)
        self.assertIn("Spot-check by execution", out)
        self.assertIn("in a scratch copy only", out)
        self.assertIn("You will not review this unit's code", out)
        reviewer = shlex.quote(critic.seat_signature(self.root, "engineering"))
        tail = (f"--note {shlex.quote(str(self.note.resolve()))} --reviewer {reviewer} "
                f"--author {reviewer}")
        self.assertIn(f"critic.py approach record --unit US0101 --verdict go {tail}", out)
        self.assertIn("critic.py approach record --unit US0101 --verdict changes --changes "
                      f"REVIEW.md {tail}", out)
        self.assertIn("`review.solution_review.min_points` is 0", run.stderr)

    def test_an_incomplete_note_is_refused_before_any_brief(self) -> None:
        """AC2. MUTANTS: the heading check removed; the criterion check removed."""
        missing = dict(SECTIONS)
        del missing["May break"]
        self._refused(self._brief(note=self._write_note("no-break.md", _note(missing))),
                      "## May break")
        one = dict(SECTIONS, Tests="- AC1: test_turns, killing `turn()` removed.")
        run = self._brief(note=self._write_note("ac1-only.md", _note(one)))
        self._refused(run, "AC2")
        self.assertNotIn("AC1", run.stderr)
        control = self._brief()
        self.assertEqual(control.returncode, 0, control.stderr)
        self.assertIn("--- APPROACH NOTE ---", control.stdout)

    def test_the_code_review_brief_carries_none_of_the_solution_review(self) -> None:
        """AC3. MUTANTS: the notice's seat test inverted or dropped; either branch's print of it
        removed; a seat read by the reviewer's name rather than its recorded role."""
        self._config(ON)
        before = self._code_briefs()
        for key, run in before.items():
            self.assertIsNone(re.search(r"\bGO\b", run.stdout), f"premise, {key}")
            self.assertNotIn("fresh context that has not read the note", run.stderr, key)
        self._record("go", "Ravi Approach (engineering)")
        [row] = critic.read_solution_reviews(self.root, "US0101")
        self.assertEqual(row["digest"], _digest(self.note.read_bytes()))
        note_lines = [ln for ln in self.note.read_text(encoding="utf-8").splitlines()
                      if ln.strip()]
        after = self._code_briefs()
        for key, run in after.items():
            out = run.stdout
            for banned in ("US0101-approach.md", str(self.note), row["digest"],
                           "Ravi Approach", *note_lines):
                self.assertNotIn(banned, out, key)
            self.assertIsNone(re.search(r"\bGO\b", out), key)
            notice = "fresh context that has not read the note" in run.stderr
            self.assertEqual(notice, key[0] == "engineering", f"{key}:\n{run.stderr}")

    def test_the_runbook_and_the_catalogue_name_both_commands(self) -> None:
        """AC4. MUTANTS: the row missing, before Build a unit, with a fourth cell, or naming one
        verb; the catalogue paragraph naming one verb or no ledger."""
        text = (SKILL / "reference-sprint-toolchain.md").read_text(encoding="utf-8")
        section = re.search(r"(?ms)^## 3\. Deliver a unit\n(.*?)(?=^## )", text).group(1)
        rows = [cells for ln in section.splitlines() if ln.startswith("|")
                if (cells := sdlc_md.table_cells(ln)) is not None]
        self.assertEqual(rows[0], ["Do", "Command", "Instead of"])
        self.assertTrue(all(len(r) == 3 for r in rows), rows)
        names = [r[0] for r in rows]
        review = names.index("Review a builder's approach")
        self.assertGreater(review, names.index("Build a unit"))
        self.assertIn("critic.py approach brief", rows[review][1])
        self.assertIn("critic.py approach record", rows[review][1])
        page = (SKILL / "reference-scripts-review.md").read_text(encoding="utf-8")
        entry = re.search(r"(?ms)^### `critic\.py`\n(.*?)(?=^### )", page).group(1)
        for word in ("approach brief", "approach record", "solution-reviews.md"):
            self.assertIn(word, entry)

    # -- the branches and guards beside them -------------------------------------------------

    def test_the_tests_section_is_bounded_and_ids_are_whole_words(self) -> None:
        """MUTANTS: the Tests section read to the end of the note, or only to its own first
        line; `\\b` dropped from the id match; heading equality in place of the last-words
        rule; a `###` heading accepted."""
        order = ["Reading", "Design", "May break", "Sentences", "Tests"]
        last = self._brief(note=self._write_note("tests-last.md", _note(order=order)))
        self.assertEqual(last.returncode, 0, last.stderr)
        elsewhere = dict(SECTIONS, Reading="- AC2: named before the Tests section.",
                         Tests="- AC1: test_turns.",
                         Sentences="- AC2: named after the Tests section.")
        self._refused(self._brief(note=self._write_note("elsewhere.md", _note(elsewhere))),
                      "names no test for AC2")
        longer = dict(SECTIONS, Tests="- AC1: test_turns.\n- AC20: test_other.")
        self._refused(self._brief(note=self._write_note("ac20.md", _note(longer))),
                      "names no test for AC2")
        alias = self._brief(note=self._write_note(
            "alias.md", _note(titles={"May break": "What it may break"})))
        self.assertEqual(alias.returncode, 0, alias.stderr)
        deeper = _note().replace("## Tests", "### Tests")
        run = self._brief(note=self._write_note("deeper.md", deeper))
        self._refused(run, "## Tests")
        self.assertNotIn("names no test", run.stderr, "no Tests section, no id check")
        both = dict(SECTIONS)
        del both["Design"], both["Sentences"]
        self._refused(self._brief(note=self._write_note("two.md", _note(both))),
                      "## Design", "## Sentences")

    def test_a_missing_note_unknown_unit_and_unknown_seat_are_refused(self) -> None:
        """MUTANTS: each guard removed."""
        self._refused(self._brief(note=self.tmp / "absent.md"), "names no file")
        self._refused(self._brief(unit="US0999"), "US0999")
        self._refused(self._brief(seat="astronomer"), "astronomer")

    def test_the_stderr_note_and_the_self_review_note(self) -> None:
        """MUTANTS: the not-named note printed for a named unit, or never; the self-review note
        printed for any seat, or never; the brief written anywhere."""
        before = _tree(self.root)
        unnamed = self._brief()
        self.assertEqual(_tree(self.root), before, "approach brief writes nothing")
        self.assertIn("will refuse a verdict on US0101", unnamed.stderr)
        self.assertIn("self-review", unnamed.stdout)
        self.assertIn("no lane recorded the seat that built US0101", unnamed.stdout)
        self.assertIn("Affects (the files the plan may change):\nsrc/a.py\ntests/test_a.py\n",
                      unnamed.stdout)
        self.assertIn("\nAbout 20 tool calls.\n", unnamed.stdout)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            rc = critic.main(["--root", str(self.root), "approach", "brief", "--unit", "US0101",
                              "--seat", "qa", "--note", str(self.note)])
        self.assertEqual(rc, 0, "the verb returns its exit code to an in-process caller")
        qa = self._brief(seat="qa")
        self.assertEqual(qa.returncode, 0, qa.stderr)
        self.assertNotIn("self-review", qa.stdout)
        self.assertIn(f"--reviewer {shlex.quote(critic.seat_signature(self.root, 'qa'))}",
                      qa.stdout)
        self._config(ON)
        named = self._brief(seat="qa")
        self.assertEqual(named.returncode, 0, named.stderr)
        self.assertNotIn("will refuse", named.stderr)
        self.assertIn("US0101 takes a solution review: 3 points", named.stdout)
        self._config("review:\n  solution_review:\n    min_points: three\n")
        bad = self._brief(seat="qa")
        self.assertEqual(bad.returncode, 0, bad.stderr)
        self.assertIn("will refuse a verdict on US0101", bad.stderr)
        self.assertIn("review.solution_review.min_points", bad.stderr)

    def test_the_author_is_the_seat_the_lane_recorded(self) -> None:
        """MUTANTS: the lane's recorded seat ignored; the no-lane note printed when one is
        recorded."""
        transcripts = self.tmp / "transcripts"
        transcripts.mkdir()
        with unittest.mock.patch.dict(os.environ, {run_state.TRANSCRIPTS_ENV: str(transcripts)}):
            run_state.open_run(self.root, batch=["US0101"], goal="g")
            run_state.record_lane_start(self.root, "US0101", "qa")
        run = self._brief(seat="qa")
        self.assertEqual(run.returncode, 0, run.stderr)
        qa = shlex.quote(critic.seat_signature(self.root, "qa"))
        self.assertIn(f"--reviewer {qa} --author {qa}", run.stdout)
        self.assertIn("self-review", run.stdout)
        self.assertNotIn("no lane recorded", run.stdout)

    def test_the_notice_reads_the_recorded_role_first(self) -> None:
        """MUTANTS: `verdict_seat` read before `recorded_seat`; the fallback for a cell with no
        role dropped; an unreadable ledger refusing the code brief or saying nothing."""
        self._config(ON)
        changes = self._write_note("changes.md", "Name the brake test.\n")
        self._record("changes", "Ola Smith (persona)", changes)
        self.assertEqual(critic.verdict_seat(self.root, "Ola Smith (persona)"), "engineering",
                         "premise: the name alone reads as the engineering seat")
        eng = self._critic("brief", "--unit", "US0101", "--seat", "engineering")
        self.assertEqual(eng.returncode, 0, eng.stderr)
        self.assertNotIn("fresh context", eng.stderr)
        self._record("changes", "ravi-approach-qa", changes)
        qa = self._critic("brief", "--unit", "US0101", "--seat", "qa")
        self.assertIn("solution review: the qa seat reviewed US0101's approach note before any "
                      "code, so this code review must go to a fresh context that has not read "
                      "the note", qa.stderr)
        ledger = self.root / "sdlc-studio" / "reviews" / "solution-reviews.md"
        ledger.unlink()
        ledger.mkdir()
        broken = self._critic("brief", "--unit", "US0101", "--seat", "qa")
        self.assertEqual(broken.returncode, 0, broken.stderr)
        self.assertIn("could not be read", broken.stderr)
        self.assertIn("fresh context", broken.stderr)


if __name__ == "__main__":
    unittest.main()
