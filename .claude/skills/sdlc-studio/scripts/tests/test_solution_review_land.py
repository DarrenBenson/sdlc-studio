"""US1347: `sprint lane land` refuses a unit `review.solution_review` names whose approach is
not agreed.

Every landing case drives `sprint.py lane land` through its entry point against a throwaway
repository and the builder's worktree, built as test_lane_land's `_LaneFixture` builds them,
and records each solution review verdict through `critic.py approach record`. A unit the
setting names lands only when its worktree's hand-in holds its approach note and the unit's
latest verdict is a GO recorded against the note's digest as it stands; every other case exits
2 before anything moves.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
from lib import lanes  # noqa: E402

SPRINT = SCRIPTS / "sprint.py"
CRITIC = SCRIPTS / "critic.py"
SKILL = SCRIPTS.parent

A, B, C = "US0101", "US0102", "US0103"
LANE = "sdlc-studio/.local/lane"
#: the approach seat is not the qa seat the landing briefs, so no code brief notice is in play
REVIEWER, AUTHOR = "Lena Marsh (product)", "Dani Okafor (engineering)"
NOTE = ("# approach\n\n## Reading\n\nr\n\n## Design\n\nd\n\n## What it may break\n\nm\n\n"
        "## Tests\n\nAC1\n\n## Sentences\n\ns\n")
HOOK = "#!/bin/sh\nexit 0\n"
ON = "review:\n  author_self_check: block\n  solution_review:\n    min_points: 2\n"
OFF = "review:\n  author_self_check: block\n"
#: each unit's points and the source file it changes
UNITS = {A: (3, "src/a.py"), B: (1, "src/b.py"), C: (3, "src/c.py")}


def _write(root: Path, rel: str, body: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _git(cwd: Path, *args: str) -> str:
    return gitutil.git(list(args), cwd, text=True).stdout.strip()


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


class SolutionReviewLandTests(unittest.TestCase):
    """A temp repository whose `review.solution_review` names its 3-point units, a stub hook
    that passes, and two builders' worktrees."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        base = self.base = Path(self._tmp.name).resolve()
        self.root = base / "repo"
        self.wt, self.wt2 = base / "lane-one-wt", base / "lane-two-wt"
        for rel in ("src/a.py", "src/b.py", "src/c.py"):
            _write(self.root, rel, "X = 1\n")
        _write(self.root, "tests/test_a.py", "def test_a():\n    assert True\n")
        _write(self.root, ".gitignore", "sdlc-studio/.local/\n")
        _write(self.root, "sdlc-studio/personas/seats/qa.md",
               "<!-- role: qa -->\n# Sam - QA amigo\n\ncharter\n\n## Lens\n\nx\n\n"
               "## Pushes Back When\n\nx\n\n## Shadow\n\nx\n")
        _write(self.root, "sdlc-studio/.config.yaml", ON)
        for unit, (points, src) in UNITS.items():
            tests = ", tests/test_a.py" if unit == A else ""
            _write(self.root, f"sdlc-studio/stories/{unit}-lane.md",
                   f"# {unit}: lane\n\n> **Status:** Review\n> **Points:** {points}\n"
                   f"> **Epic:** EP0001\n> **Affects:** {src}{tests}, changelog.d/{unit}.md\n\n"
                   "## Acceptance Criteria\n\n### AC1: works\n- **Verify:** shell true\n")
        _git(self.root, "init", "-q", "-b", "main")
        _git(self.root, "add", "-A")
        _git(self.root, "commit", "-q", "-m", "chore: the fixture")
        _write(base, "hooks/pre-commit", HOOK)
        (base / "hooks" / "pre-commit").chmod(0o755)
        _git(self.root, "config", "core.hooksPath", str(base / "hooks"))
        _git(self.root, "worktree", "add", "-q", "-b", "lane-one", str(self.wt), "main")
        _git(self.root, "worktree", "add", "-q", "-b", "lane-two", str(self.wt2), "main")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    # -- the lane a builder hands in ------------------------------------------------------

    def _hand_in(self, wt: Path, *units: str) -> None:
        """Each unit's source and fragment staged in `wt`, with its claims, mutants and the
        lane's commit message."""
        for unit in units:
            src = UNITS[unit][1]
            for rel, body in ((src, "X = 2\n"), (f"changelog.d/{unit}.md", f"{unit} done\n")):
                _write(wt, rel, body)
                _git(wt, "add", "--", rel)
            claims = [{"surface": "commit message", "claim": "x is two", "ruling": "TRUE"},
                      {"surface": f"changelog.d/{unit}.md", "claim": "x is two",
                       "ruling": "TRUE"}]
            mutants = ([{"mutant": "x stays one", "test": "tests/test_a.py::test_a",
                         "result": "killed"}] if unit == A else [])
            _write(wt, f"{LANE}/{unit}-claims.json", json.dumps(claims))
            _write(wt, f"{LANE}/{unit}-mutants.json", json.dumps(mutants))
        _write(wt, f"{LANE}/commit-msg.txt", f"feat({', '.join(units)}): x is two\n")

    def _note(self, wt: Path, unit: str, body: str = NOTE) -> Path:
        path = wt / LANE / f"{unit}-approach.md"
        _write(path.parent, path.name, body)
        return path

    def _record(self, unit: str, verdict: str, note: Path, changes: str | None = None) -> None:
        extra = []
        if changes is not None:
            _write(self.base, "changes.md", changes)
            extra = ["--changes", str(self.base / "changes.md")]
        done = subprocess.run(
            [sys.executable, "-B", str(CRITIC), "approach", "record", "--unit", unit,
             "--verdict", verdict, "--note", str(note), "--reviewer", REVIEWER, "--author",
             AUTHOR, *extra, "--root", str(self.root)],
            capture_output=True, text=True, timeout=600, cwd=str(self.root),
            env=gitutil.git_env(), check=False)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)

    def _land(self, *units: str, worktrees: tuple[Path, ...] = ()) -> subprocess.CompletedProcess:
        named = [arg for wt in worktrees or (self.wt,) for arg in ("--worktree", str(wt))]
        return subprocess.run(
            [sys.executable, "-B", str(SPRINT), "lane", "land", *named, "--units", *units,
             "--root", str(self.root)],
            capture_output=True, text=True, timeout=600, cwd=str(self.root),
            env=gitutil.git_env(), check=False)

    def _state(self, *wts: Path) -> tuple:
        return (_git(self.root, "rev-parse", "main"),
                [(_git(wt, "rev-parse", "HEAD"), _git(wt, "diff", "--cached", "--name-only"))
                 for wt in wts or (self.wt,)])

    def _assert_unmoved(self, done: subprocess.CompletedProcess, before: tuple,
                        *wts: Path) -> None:
        """Exit 2 and nothing moved: main, each worktree's HEAD and index, no kept hand-in."""
        self.assertEqual(done.returncode, 2, done.stdout + done.stderr)
        self.assertEqual(self._state(*wts), before)
        for wt in wts or (self.wt,):
            self.assertTrue(wt.is_dir())
            self.assertFalse((self.root / LANE / "landed" / wt.name).exists())

    def _flat(self, text: str) -> str:
        return re.sub(r"\s+", " ", text)

    # -- the criteria ---------------------------------------------------------------------

    def test_no_note_refuses_the_land_before_anything_moves(self) -> None:
        """AC1: a 3-point unit under `min_points: 2` with no approach note is refused, exit 2,
        naming the unit, the note's path and the lane brief, then the next step."""
        self._hand_in(self.wt, A)
        before = self._state()
        done = self._land(A)
        self._assert_unmoved(done, before)
        said = self._flat(done.stderr)
        self.assertIn(A, said)
        self.assertIn(str(self.wt / LANE / f"{A}-approach.md"), said)
        brief = f"sprint.py lane brief --units {A}"
        self.assertIn(brief, said)
        self.assertGreater(said.find(f"critic.py approach brief --unit {A}"), said.find(brief))

    def test_a_land_without_a_current_go_is_refused(self) -> None:
        """AC2: no verdict, a CHANGES latest and a GO bound to an earlier text each refuse,
        naming why; the GO bound to the note as it stands then lands."""
        self._hand_in(self.wt, A)
        note = self._note(self.wt, A)
        before = self._state()
        done = self._land(A)
        self._assert_unmoved(done, before)
        said = self._flat(done.stderr)
        self.assertIn("no solution review is recorded", said)
        self.assertIn(f"critic.py approach brief --unit {A}", said)

        self._record(A, "changes", note, changes="read AC1 again\n")
        done = self._land(A)
        self._assert_unmoved(done, before)
        self.assertIn("CHANGES at round 1", self._flat(done.stderr))

        self._record(A, "go", note)
        agreed = _digest(note)
        note.write_text(NOTE + "\n", encoding="utf-8")
        done = self._land(A)
        self._assert_unmoved(done, before)
        said = self._flat(done.stderr)
        self.assertIn("round 2", said)
        self.assertIn(agreed, said)
        self.assertIn(_digest(note), said)
        self.assertNotEqual(agreed, _digest(note))
        self.assertIn("whitespace included", said)

        note.write_text(NOTE, encoding="utf-8")
        done = self._land(A)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertNotEqual(_git(self.root, "rev-parse", "main"), before[0])

    def test_an_agreed_approach_lands_and_an_unnamed_unit_lands_as_before(self) -> None:
        """AC3: the 3-point unit with a GO on its current note and a 1-point unit the setting
        does not name land together; only the first is named in one solution review line."""
        self._hand_in(self.wt, A)
        note = self._note(self.wt, A)
        self._record(A, "go", note)
        agreed = _digest(note)  # the landing removes the worktree, and the note with it
        self._hand_in(self.wt2, B)
        done = self._land(A, B, worktrees=(self.wt, self.wt2))
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(_git(self.root, "show", "main:src/a.py"), "X = 2")
        self.assertEqual(_git(self.root, "show", "main:src/b.py"), "X = 2")
        lines = [ln for ln in done.stdout.splitlines() if "solution review" in ln.lower()]
        self.assertEqual(len(lines), 1, done.stdout)
        for part in (A, "solution review agreed", "GO", "round 1", agreed):
            self.assertIn(part, lines[0])
        for line in (done.stdout + done.stderr).splitlines():
            if B in line:
                self.assertNotRegex(line.lower(), r"solution review|approach")

    def test_the_runbook_and_the_sprint_help_say_what_land_refuses(self) -> None:
        """AC4: the runbook's land row and the Lanes section of help/sprint.md name the step."""
        runbook = (SKILL / "reference-sprint-toolchain.md").read_text(encoding="utf-8")
        rows = [ln for ln in runbook.splitlines()
                if ln.startswith("| Land a builder's staged worktree |")]
        self.assertEqual(len(rows), 1)
        for part in ("review.solution_review", "agreed approach", "removes the worktree"):
            self.assertIn(part, rows[0])
        page = (SKILL / "help" / "sprint.md").read_text(encoding="utf-8")
        start = page.index("## Lanes: dispatching work and accepting it back")
        end = page.find("\n## ", start + 1)
        section = page[start:end if end > 0 else len(page)]
        paras = [self._flat(p) for p in section.split("\n\n")
                 if "critic.py approach record" in p]
        self.assertEqual(len(paras), 1, "one Lanes paragraph names `critic.py approach record`")
        for part in ("review.solution_review", "<unit>-approach.md", "critic.py approach brief",
                     "refuses", "every refused unit is named in one message", "sprint drive",
                     "lane run", "min_points", "orchestrator's own tree", "landed/", "digest"):
            self.assertIn(part, paras[0].lower())

    # -- the guards beside them -----------------------------------------------------------

    def test_every_unit_of_one_worktree_is_named(self) -> None:
        """Two 3-point units in one worktree's `--units`, neither with a note: one refusal
        names both, so the first is not the only one judged."""
        self._hand_in(self.wt, A, C)
        before = self._state()
        done = self._land(A, C)
        self._assert_unmoved(done, before)
        for unit in (A, C):
            self.assertIn(str(self.wt / LANE / f"{unit}-approach.md"), self._flat(done.stderr))

    def test_a_landing_of_several_worktrees_refuses_whole(self) -> None:
        """An agreed unit in the first worktree and an unagreed one in the second: exit 2
        naming only the second, and neither lands."""
        self._hand_in(self.wt, A)
        self._record(A, "go", self._note(self.wt, A))
        self._hand_in(self.wt2, C)
        before = self._state(self.wt, self.wt2)
        done = self._land(A, C, worktrees=(self.wt, self.wt2))
        self._assert_unmoved(done, before, self.wt, self.wt2)
        said = self._flat(done.stderr)
        self.assertIn(str(self.wt2 / LANE / f"{C}-approach.md"), said)
        self.assertNotIn(str(self.wt / LANE / f"{A}-approach.md"), said)

    def test_a_risk_class_the_setting_lists_takes_the_step(self) -> None:
        """`min_points: 0` and `risk_classes: [high]` with a declared map: a unit in a high
        component takes the step whatever its points, and is refused with no note."""
        _write(self.root, "sdlc-studio/.config.yaml",
               OFF + "  solution_review:\n    min_points: 0\n    risk_classes: [high]\n"
               "risk:\n  components:\n    src/c.py: high\n")
        self._hand_in(self.wt, C)
        before = self._state()
        done = self._land(C)
        self._assert_unmoved(done, before)
        said = self._flat(done.stderr)
        self.assertIn(str(self.wt / LANE / f"{C}-approach.md"), said)
        self.assertIn("risk class high", said)

    def test_a_named_unit_with_no_story_is_refused(self) -> None:
        """With the setting on, a unit the project holds no artefact for cannot be judged, so
        it is refused by name rather than read as not named."""
        self._hand_in(self.wt, A)
        self._record(A, "go", self._note(self.wt, A))
        before = self._state()
        done = self._land(A, "US0109")
        self._assert_unmoved(done, before)
        said = self._flat(done.stderr)
        self.assertIn("US0109", said)
        self.assertIn("no unit US0109 is found", said)

    def test_a_malformed_setting_is_refused_naming_its_key(self) -> None:
        _write(self.root, "sdlc-studio/.config.yaml",
               OFF + "  solution_review:\n    min_points: two\n")
        self._hand_in(self.wt, B)
        before = self._state()
        done = self._land(B)
        self._assert_unmoved(done, before)
        self.assertIn("review.solution_review.min_points", done.stderr)

    def _isolated(self):
        """The operator's git configuration set aside for an in-process landing."""
        return unittest.mock.patch.dict(os.environ, gitutil.git_env(), clear=True)

    def test_no_setting_reads_no_unit_and_a_setting_reads_each(self) -> None:
        """In-process, with no patch: a unit the project holds no artefact for is refused once
        the setting is on, since the rule reads each unit's story, and passes the preflight
        with no setting, since then the rule is never consulted."""
        self._hand_in(self.wt, A)
        self._record(A, "go", self._note(self.wt, A))
        with self._isolated(), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(lanes.LandError) as caught:
                lanes._preflight(self.root, [self.wt], [A, "US0109"])  # noqa: SLF001
        self.assertEqual(caught.exception.code, 2)
        self.assertIn("no unit US0109 is found", str(caught.exception))
        _write(self.root, "sdlc-studio/.config.yaml", OFF)
        with self._isolated(), contextlib.redirect_stdout(io.StringIO()):
            landing = lanes._preflight(self.root, [self.wt], [A, "US0109"])  # noqa: SLF001
        self.assertEqual(landing[0].units, [A, "US0109"])
        self.assertEqual(landing[0].agreed, [])

    def test_a_repair_s_missing_note_names_the_kept_copy(self) -> None:
        """A recreated worktree holds no hand-in: the refusal names the copy the last landing
        kept, where to put it back, and that its GO still holds."""
        self._hand_in(self.wt, A)
        kept = self.root / LANE / "landed" / self.wt.name / f"{A}-approach.md"
        _write(kept.parent, kept.name, NOTE)
        before = _git(self.root, "rev-parse", "main")
        done = self._land(A)
        self.assertEqual(done.returncode, 2, done.stdout + done.stderr)
        self.assertEqual(_git(self.root, "rev-parse", "main"), before)
        said = self._flat(done.stderr)
        self.assertIn(str(kept), said)
        self.assertIn(str(self.wt / LANE / f"{A}-approach.md"), said)
        self.assertIn("its GO still holds", said)

    def _landed_then_restored(self, unit: str, body: str) -> tuple[Path, str]:
        """`unit` landed from `self.wt` with an agreed note of `body`, then its worktree
        recreated for a repair: the note's path in it, and the line `restore_for_repair` said."""
        self._hand_in(self.wt, unit)
        self._record(unit, "go", self._note(self.wt, unit, body))
        done = self._land(unit)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertFalse(self.wt.exists())
        said = lanes.restore_for_repair(self.root, unit)
        return self.wt / LANE / f"{unit}-approach.md", said

    def test_a_repair_s_recreated_worktree_holds_the_kept_note(self) -> None:
        """AC1, AC2: the recreated worktree holds the unit's kept approach note byte for byte
        (CRLF and a missing final newline included), so its recorded GO still binds by digest
        and a repair's land is not refused for want of a note."""
        body = NOTE.replace("\n", "\r\n").rstrip()
        note, said = self._landed_then_restored(A, body)
        kept = self.root / LANE / "landed" / self.wt.name / f"{A}-approach.md"
        self.assertTrue(note.is_file(), said)
        self.assertEqual(note.read_bytes(), kept.read_bytes())
        self.assertEqual(note.read_bytes(), body.encode())
        self.assertIn(f"restored the approach note {A}-approach.md", said)
        import critic  # noqa: PLC0415 - a sibling script, on the path
        ok, why = critic.approach_agreed(self.root, A, note)
        self.assertTrue(ok, why)
        self.assertEqual(_git(self.wt, "status", "--porcelain"), "")

    def test_a_unit_with_no_kept_note_gets_none(self) -> None:
        """Positive control: a unit whose landing kept no note, and a sibling's kept note,
        leave the recreated worktree with no hand-in folder and no note in the line."""
        self._hand_in(self.wt, B)
        _write(self.root, f"{LANE}/landed/{self.wt.name}/{A}-approach.md", NOTE)
        done = self._land(B)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        said = lanes.restore_for_repair(self.root, B)
        self.assertIn("recreated the worktree", said)
        self.assertNotIn("approach note", said)
        self.assertFalse((self.wt / LANE).exists())

    def test_the_agreed_line_waits_for_the_markdown_check(self) -> None:
        """In-process: the agreed line is printed after the markdown check and before the
        hand-in is copied, so a land the markdown check refuses prints none."""
        self._hand_in(self.wt, A)
        self._record(A, "go", self._note(self.wt, A))
        stop = unittest.mock.patch.object(lanes, "_keep_hand_ins",
                                          side_effect=lanes.LandError("copy stopped", 2))
        quiet = unittest.mock.patch.object(lanes, "_refuse_markdown", return_value=None)
        out = io.StringIO()
        with self._isolated(), quiet, stop, contextlib.redirect_stdout(out), \
                contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(lanes.land(self.root, [self.wt], [A]), 2)
        self.assertEqual(out.getvalue().count("solution review agreed"), 1, out.getvalue())
        lint = unittest.mock.patch.object(lanes, "_refuse_markdown",
                                          side_effect=lanes.LandError("lint refused", 2))
        out, err = io.StringIO(), io.StringIO()
        with self._isolated(), lint, contextlib.redirect_stdout(out), \
                contextlib.redirect_stderr(err):
            self.assertEqual(lanes.land(self.root, [self.wt], [A]), 2)
        self.assertIn("lint refused", err.getvalue())
        self.assertNotIn("solution review agreed", out.getvalue())


if __name__ == "__main__":
    unittest.main()
