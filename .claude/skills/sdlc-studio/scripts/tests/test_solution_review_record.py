"""Which units take a solution review, and `critic.py approach record`'s verdict ledger.

Every record goes through the shipped `critic.py` CLI against a throwaway project; the readers
other scripts call (`solution_review_reason`, `approach_agreed`, `read_solution_reviews`) are
called directly on the ledger the CLI wrote.
"""
from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

critic = loader.load_script("critic")
sdlc_md = critic.sdlc_md

SCRIPTS = Path(__file__).resolve().parent.parent
SKILL = SCRIPTS.parent
REFERENCE = SKILL / "reference-config.md"
LEDGER = Path("sdlc-studio") / "reviews" / "solution-reviews.md"

ON = ("review:\n  solution_review:\n    min_points: 3\n    risk_classes: [high]\n"
      "risk:\n  components:\n    src/: standard\n")
NO_MAP = "review:\n  solution_review:\n    min_points: 3\n    risk_classes: [high]\n"
POINTS_REASON = "3 points, at or above `review.solution_review.min_points` 3"
RISK_REASON = "risk class high, listed in `review.solution_review.risk_classes`"
NO_MAP_WHY = "no `risk.components` map is declared, so every unit reads standard"
STORIES = {  # id: (points or None, risk class)
    "US0001": (3, "standard"), "US0002": (2, "high"), "US0003": (2, "standard"),
    "US0004": (3, "high"), "US0006": (None, "standard"), "US-0007": (3, "standard"),
}


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:12]


class SolutionReviewRecordTests(unittest.TestCase):

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="srrec-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.root = self.tmp / "proj"
        stories = self.root / "sdlc-studio" / "stories"
        stories.mkdir(parents=True)
        for uid, (points, risk) in STORIES.items():
            pts = f"> **Points:** {points}\n" if points is not None else ""
            (stories / f"{uid}-a-story.md").write_text(
                f"# {uid}: A story\n\n> **Status:** Ready\n> **Risk-class:** {risk}\n{pts}"
                f"> **Affects:** src/a.py\n\n## Acceptance Criteria\n\n### AC1: it works\n",
                encoding="utf-8")
        self.note = self.tmp / "US0001-approach.md"
        self.note.write_text("# approach\n\n## Tests\n\nAC1: a test\n", encoding="utf-8")
        self.changes = self.tmp / "changes.txt"
        self.changes.write_text("Pin the exact reason strings.\n", encoding="utf-8")
        self.env = dict(os.environ, HOME=str(self.tmp / "home"), TMPDIR=str(self.tmp),
                        XDG_CONFIG_HOME=str(self.tmp / "xdg"), PYTHONDONTWRITEBYTECODE="1")

    def _config(self, text: str) -> None:
        (self.root / "sdlc-studio" / ".config.yaml").write_text(text, encoding="utf-8")

    def _argv(self, unit: str, verdict: str = "go", note: Path | None = None,
              changes: Path | None = None, reviewer: str = "Dani (engineering)",
              author: str = "builder (engineering)") -> list[str]:
        argv = [sys.executable, "-B", str(SCRIPTS / "critic.py"), "--root", str(self.root),
                "approach", "record", "--unit", unit, "--verdict", verdict,
                "--note", str(note or self.note), "--reviewer", reviewer, "--author", author]
        return argv + (["--changes", str(changes)] if changes else [])

    def _record(self, unit: str, **kw) -> subprocess.CompletedProcess:
        return subprocess.run(self._argv(unit, **kw), capture_output=True, text=True,
                              env=self.env, timeout=120)

    def _ledger(self) -> bytes | None:
        path = self.root / LEDGER
        return path.read_bytes() if path.exists() else None

    def _refused(self, run: subprocess.CompletedProcess, *words: str) -> None:
        self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
        for word in words:
            self.assertIn(word, run.stderr)
        self.assertEqual(run.stdout, "")

    # -- the criteria ------------------------------------------------------------------------

    def test_the_setting_decides_which_units_take_the_step(self) -> None:
        """AC1. MUTANT: `points >= min_points` read as `>`, the risk clause dropped, or the
        refusal's return removed."""
        self._config(ON)
        first = self._record("US0001")
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertIn(f"US0001 takes a solution review: {POINTS_REASON}\n", first.stdout)
        second = self._record("US0002")
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIn(f"US0002 takes a solution review: {RISK_REASON}\n", second.stdout)
        before = self._ledger()
        third = self._record("US0003")
        self._refused(third, "US0003 takes no solution review",
                      "2 points, below `review.solution_review.min_points` 3",
                      "risk class standard, not listed in "
                      "`review.solution_review.risk_classes` (high)", "Nothing was written")
        self.assertEqual(self._ledger(), before)
        self.assertEqual([r["unit"] for r in critic.read_solution_reviews(self.root)],
                         ["US0001", "US0002"])

    def test_a_verdict_is_bound_to_the_note_digest_round_by_round(self) -> None:
        """AC2. MUTANT: the round held at 1, the digest taken of the path, the changes text
        left out of its cell."""
        self._config(ON)
        first_text = self.note.read_bytes()
        run = self._record("US0001", verdict="changes", changes=self.changes)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn(f"recorded CHANGES for US0001 at round 1 against note digest "
                      f"{_digest(first_text)}", run.stdout)
        self.note.write_text("# approach, revised\n\n## Tests\n\nAC1: an exact test\n",
                             encoding="utf-8")
        run = self._record("US0001", verdict="go")
        self.assertEqual(run.returncode, 0, run.stderr)
        rows = critic.read_solution_reviews(self.root, "US0001")
        today = sdlc_md.now_date()
        self.assertEqual(
            [(r["round"], r["verdict"], r["digest"], r["changes"], r["reviewer"], r["author"],
              r["date"]) for r in rows],
            [(1, "CHANGES", _digest(first_text), "Pin the exact reason strings.",
              "Dani (engineering)", "builder (engineering)", today),
             (2, "GO", _digest(self.note.read_bytes()), "", "Dani (engineering)",
              "builder (engineering)", today)])
        self.assertNotEqual(rows[0]["digest"], rows[1]["digest"])
        text = (self.root / LEDGER).read_text(encoding="utf-8")
        self.assertIn("| Unit | Round | Verdict | Digest | Note | Reviewer | Author | Date | "
                      "Changes |", text)

    def test_a_verdict_that_cannot_stand_is_refused(self) -> None:
        """AC3. MUTANT: each of the four guards removed."""
        self._config(ON)
        cases = {
            "same identity": (dict(reviewer="Builder (Engineering)"),
                              "reviewer and author are the same identity"),
            "go with changes": (dict(verdict="go", changes=self.changes),
                                "`--verdict go` takes no `--changes`"),
            "changes without": (dict(verdict="changes"),
                                "`--verdict changes` needs `--changes FILE`"),
            "missing note": (dict(note=self.tmp / "absent.md"), "absent.md names no file"),
        }
        for name, (kw, why) in cases.items():
            with self.subTest(name):
                self._refused(self._record("US0001", **kw), why, "Nothing was written")
                self.assertIsNone(self._ledger())
        control = self._record("US0001")
        self.assertEqual(control.returncode, 0, control.stderr)
        self.assertEqual(len(critic.read_solution_reviews(self.root)), 1)

    def test_the_step_ships_off_and_the_reference_says_so(self) -> None:
        """AC4. MUTANT: the `min_points > 0` guard dropped (every unit then takes the step at
        the default), a default changed in config-defaults.yaml, a row or the sentence cut, or
        the severity block left unfolded."""
        show = subprocess.run([sys.executable, "-B", str(SCRIPTS / "config.py"), "--root",
                               str(self.root), "show", "--sources"], capture_output=True,
                              text=True, env=self.env, timeout=120)
        self.assertEqual(show.returncode, 0, show.stderr)
        lines = show.stdout.splitlines()
        self.assertIn("default review.solution_review.min_points = 0", lines)
        self.assertIn("default review.solution_review.risk_classes = []", lines)
        for uid in STORIES:
            with self.subTest(uid):
                self._refused(self._record(uid), f"{uid} takes no solution review",
                              "`review.solution_review.min_points` is 0, so no unit takes it "
                              "by points", "`review.solution_review.risk_classes` is empty")
        self.assertIsNone(self._ledger())
        page = REFERENCE.read_text(encoding="utf-8")
        rows = page.splitlines()
        for key, default in (("min_points", "`0`"), ("risk_classes", "`[]`")):
            row = [r for r in rows if r.startswith(f"| `review.solution_review.{key}` |")]
            self.assertEqual(len(row), 1, key)
            self.assertTrue(row[0].startswith(f"| `review.solution_review.{key}` | {default} |"))
            self.assertIn("the step is off", row[0])
        adopt = [r for r in rows if "adopt incrementally" in r]
        self.assertEqual(len(adopt), 1)
        self.assertIn("`review.solution_review`", adopt[0])
        self.assertLessEqual(len(rows), 732)
        self.assertNotIn("  severity_levels:\n    - critical", page)
        self.assertEqual(len([r for r in rows if r.startswith("| `review.severity_levels` |")]),
                         1)

    # -- the reason, exactly -----------------------------------------------------------------

    def test_both_reasons_are_named_when_both_rules_take_the_unit(self) -> None:
        self._config(ON)
        self.assertEqual(critic.solution_review_reason(self.root, "US0004"),
                         f"{POINTS_REASON}; {RISK_REASON}")
        self.assertEqual(critic.solution_review_reason(self.root, "US0001"), POINTS_REASON)
        self.assertEqual(critic.solution_review_reason(self.root, "US0002"), RISK_REASON)
        self.assertIsNone(critic.solution_review_reason(self.root, "US0003"))

    def test_an_undeclared_risk_map_reads_every_unit_standard(self) -> None:
        self._config(NO_MAP)
        run = self._record("US0002")
        self._refused(run, "risk class standard, not listed in "
                           f"`review.solution_review.risk_classes` (high): {NO_MAP_WHY}")
        self.assertIsNone(self._ledger())
        self._config(ON)
        self.assertNotIn(NO_MAP_WHY, self._record("US0003").stderr)

    def test_a_unit_without_points_and_an_unknown_unit_are_refused(self) -> None:
        self._config(ON)
        self._refused(self._record("US0006"), "US0006 carries no Points, so "
                      "`review.solution_review.min_points` 3 does not take it")
        self._refused(self._record("US0099"), "no unit US0099 is found")
        self.assertIsNone(self._ledger())

    def test_a_malformed_setting_is_refused_by_name(self) -> None:
        bad = {"min_points: three": "min_points", "min_points: true": "min_points",
               "min_points: -1": "min_points", "min_points: 2.5": "min_points",
               "risk_classes: high": "risk_classes", "risk_classes: [hgih]": "risk_classes",
               "risk_classes: [3]": "risk_classes"}
        for line, key in bad.items():
            with self.subTest(line):
                other = ("risk_classes: []" if key == "min_points" else "min_points: 3")
                self._config(f"review:\n  solution_review:\n    {line}\n    {other}\n")
                self._refused(self._record("US0001"), f"`review.solution_review.{key}` is",
                              "refused rather than read as off")
                self.assertIsNone(self._ledger())
        self._config("review:\n  solution_review:\n    min_points: 3\n"
                     "    risk_classes: [' High ']\nrisk:\n  components:\n    src/: standard\n")
        self.assertEqual(critic.solution_review_settings(self.root), (3, ["high"]))
        self.assertEqual(critic.solution_review_reason(self.root, "US0002"), RISK_REASON)

    def test_a_changes_file_a_note_or_a_value_that_cannot_be_written_is_refused(self) -> None:
        self._config(ON)
        empty = self.tmp / "empty.txt"
        empty.write_text("  \n", encoding="utf-8")
        tick = self.tmp / "tick.txt"
        tick.write_text("an odd ` backtick\n", encoding="utf-8")
        cases = {
            "missing changes": (dict(verdict="changes", changes=self.tmp / "gone.txt"),
                                "gone.txt cannot be read"),
            "empty changes": (dict(verdict="changes", changes=empty), "empty.txt is empty"),
            "note is a directory": (dict(note=self.tmp), "names no file"),
            "empty reviewer": (dict(reviewer=""), "no reviewer is recorded"),
            "unwritable changes": (dict(verdict="changes", changes=tick),
                                   "odd number of backticks"),
        }
        for name, (kw, why) in cases.items():
            with self.subTest(name):
                self._refused(self._record("US0001", **kw), why, "Nothing was written")
                self.assertIsNone(self._ledger())

    def test_the_changes_text_round_trips_through_the_ledger(self) -> None:
        self._config(ON)
        said = "keep a | b, snake_case, *stress* and [a link](x) as written"
        self.changes.write_text(said + "\x00\n", encoding="utf-8")
        run = self._record("US0001", verdict="changes", changes=self.changes)
        self.assertEqual(run.returncode, 0, run.stderr)
        row = critic.read_solution_reviews(self.root, "US0001")[0]
        self.assertEqual(row["changes"], said)
        line = (self.root / LEDGER).read_text(encoding="utf-8").splitlines()[-1]
        self.assertEqual(len(sdlc_md.table_cells(line)), 9)
        self.assertIn(r"a \| b", line)

    def test_two_records_at_once_take_two_rounds(self) -> None:
        """Both processes start while the test holds the ledger lock: a round counted outside
        the lock reads no rows in either, and both rows would say round 1."""
        self._config(ON)
        with sdlc_md.allocation_lock(self.root):
            procs = [subprocess.Popen(self._argv("US0001"), stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE, text=True, env=self.env)
                     for _ in range(2)]
            time.sleep(4)
        for proc in procs:
            out, err = proc.communicate(timeout=120)
            self.assertEqual(proc.returncode, 0, err)
        self.assertEqual(sorted(r["round"] for r in critic.read_solution_reviews(self.root)),
                         [1, 2])

    def test_the_note_is_named_relative_to_the_project_when_inside_it(self) -> None:
        self._config(ON)
        inside = self.root / "sdlc-studio" / ".local" / "lane" / "US0001-approach.md"
        inside.parent.mkdir(parents=True)
        inside.write_text("# approach\n", encoding="utf-8")
        self.assertEqual(self._record("US0001", note=inside).returncode, 0)
        self.assertEqual(self._record("US0001").returncode, 0)
        self.assertEqual([r["note"] for r in critic.read_solution_reviews(self.root)],
                         ["sdlc-studio/.local/lane/US0001-approach.md", str(self.note)])

    def test_a_library_caller_and_a_hand_written_row(self) -> None:
        self._config(ON)
        with self.assertRaisesRegex(ValueError, "not one of go, changes"):
            critic.record_solution_review(self.root, "US0001", "maybe", self.note, "a", "b")
        self.assertIsNone(self._ledger())
        path = self.root / LEDGER
        path.parent.mkdir(parents=True)
        path.write_text(critic._SOLUTION_HEADER + "| US0001 | x | go | abc | n | r | a | d | - |\n",
                        encoding="utf-8")
        row = critic.read_solution_reviews(self.root, "US0001")[0]
        self.assertEqual((row["round"], row["verdict"], row["changes"]), (0, "GO", ""))

    # -- approach_agreed, branch by branch -----------------------------------------------------

    def _agreed(self, unit: str = "US0001", note: Path | None = None) -> tuple[bool, str]:
        return critic.approach_agreed(self.root, unit, note or self.note)

    def test_approach_agreed_with_no_review_recorded(self) -> None:
        self._config(ON)
        self.assertEqual(self._agreed(), (False, "no solution review is recorded for US0001 in "
                                                 "sdlc-studio/reviews/solution-reviews.md"))

    def test_approach_agreed_with_changes_the_latest_verdict(self) -> None:
        self._config(ON)
        self._record("US0001", verdict="changes", changes=self.changes)
        self.assertEqual(self._agreed(), (False, "the latest solution review of US0001 is "
                                                 "CHANGES at round 1: revise the note and "
                                                 "record a new verdict"))

    def test_approach_agreed_with_a_go_on_an_earlier_note(self) -> None:
        self._config(ON)
        old = _digest(self.note.read_bytes())
        self._record("US0001")
        self.note.write_text("# approach, edited after the GO\n", encoding="utf-8")
        self.assertEqual(self._agreed(), (False, f"the GO at round 1 was recorded against note "
                                                 f"digest {old}, and the note's digest now is "
                                                 f"{_digest(self.note.read_bytes())}"))

    def test_approach_agreed_with_the_note_missing(self) -> None:
        self._config(ON)
        self._record("US0001")
        gone = self.tmp / "gone.md"
        self.assertEqual(self._agreed(note=gone), (False, f"the note {gone} names no file"))

    def test_approach_agreed_with_a_go_on_the_note_as_it_stands(self) -> None:
        self._config(ON)
        self._record("US0001", verdict="changes", changes=self.changes)
        self._record("US0001")
        self.assertEqual(self._agreed(), (True, f"GO at round 2 against note digest "
                                                f"{_digest(self.note.read_bytes())}"))

    def test_approach_agreed_reads_the_latest_verdict(self) -> None:
        self._config(ON)
        self._record("US0001")
        self._record("US0001", verdict="changes", changes=self.changes)
        ok, why = self._agreed()
        self.assertFalse(ok)
        self.assertIn("CHANGES at round 2", why)

    def test_approach_agreed_matches_a_hyphenated_id(self) -> None:
        self._config(ON)
        run = self._record("US-0007")
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(self._agreed("us-0007")[0], True)
        self.assertEqual([r["round"] for r in critic.read_solution_reviews(self.root, "US0007")],
                         [1])
        self.assertEqual(critic.read_solution_reviews(self.root, "US0001"), [])


if __name__ == "__main__":
    unittest.main()
