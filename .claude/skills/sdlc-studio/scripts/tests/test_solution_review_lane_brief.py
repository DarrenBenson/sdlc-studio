"""`sprint.py lane brief` sends a unit `review.solution_review` names to its approach note first,
then follows the verdict recorded on it, and names the note in the hand-in list by the unit's key.

The briefs run `sprint.py lane brief` in-process against a throwaway project with an open run;
each verdict is recorded through `critic.py approach record`, in-process too.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import contextlib
import hashlib
import importlib
import io
import json
import os
import re
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

critic = loader.load_script("critic")
sprint = loader.load_script("sprint")
from lib import lanes, run_state  # noqa: E402

ON = "review:\n  solution_review:\n    min_points: 2\n"
REASON = "3 points, at or above `review.solution_review.min_points` 2"
NOTE_PATH = "sdlc-studio/.local/lane/US0101-approach.md"
HOLD = ("Do none of the steps below this section (running the criteria, the self-check passes, "
        "the hand-in files, staging) until a GO is recorded on the note.")
UNNAMED = re.compile(r"-approach\.md|approach note|solution review", re.I)
POINTS = {"US0101": 3, "US0102": 1, "US0103": 3}


def _live(name: str):
    """The module the command resolves at call time, as `test_lane_builder_brief` reads it."""
    return sys.modules.get(name) or importlib.import_module(name)


class SolutionReviewLaneBriefTests(unittest.TestCase):

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        transcripts = self.tmp / "transcripts"
        transcripts.mkdir()
        env = unittest.mock.patch.dict(os.environ, {run_state.TRANSCRIPTS_ENV: str(transcripts)})
        env.start()
        self.addCleanup(env.stop)
        self.root = self.tmp / "repo"
        stories = self.root / "sdlc-studio" / "stories"
        stories.mkdir(parents=True)
        for uid, points in POINTS.items():
            (stories / f"{uid}-x.md").write_text(
                f"# {uid}: x\n\n> **Status:** Ready\n> **Affects:** src/a.py, tests/test_a.py\n"
                f"> **Points:** {points}\n\n## Acceptance Criteria\n\n### AC1: it holds\n\n"
                "- **Verify:** pytest tests/test_a.py::T::test_holds\n", encoding="utf-8")
        run_state.open_run(self.root, batch=list(POINTS), goal="g")
        self.note = self.tmp / "US0101-approach.md"
        self.note.write_text("# approach\n\n## Tests\n\n- AC1: test_holds\n", encoding="utf-8")

    def _config(self, text: str | None) -> None:
        path = self.root / "sdlc-studio" / ".config.yaml"
        if text is None:
            path.unlink(missing_ok=True)
        else:
            path.write_text(text, encoding="utf-8")

    def _run(self, *units: str, fmt: str | None = None) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        argv = ["lane", "brief", "--units", ",".join(units), "--root", str(self.root)]
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = sprint.main(argv + (["--format", fmt] if fmt else []))
        return rc, out.getvalue(), err.getvalue()

    def _brief(self, uid: str) -> str:
        rc, out, err = self._run(uid)
        self.assertEqual(rc, 0, err)
        return out

    def _record(self, unit: str, verdict: str, changes: str | None = None) -> None:
        argv = ["--root", str(self.root), "approach", "record", "--unit", unit, "--verdict",
                verdict, "--note", str(self.note), "--reviewer", "Sam (qa)", "--author",
                "builder (engineering)"]
        if changes is not None:
            path = self.tmp / "changes.md"
            path.write_text(changes, encoding="utf-8")
            argv += ["--changes", str(path)]
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            rc = _live("critic").main(argv)
        self.assertEqual(rc, 0, err.getvalue())

    @staticmethod
    def _hand_ins(out: str) -> list[str]:
        return [ln.strip() for ln in out.splitlines()
                if ln.startswith("    sdlc-studio/.local/lane/")]

    # -- the criteria ------------------------------------------------------------------------

    def test_a_named_unit_is_told_to_write_its_note_first(self) -> None:
        """AC1. MUTANTS: the named test inverted; the section printed after the build steps; a
        heading dropped from it; the hold sentence dropped."""
        self._config(None)
        bare = self._brief("US0102")
        self._config(ON)
        out = self._brief("US0101")
        lines = out.splitlines()
        head = lines.index("--- SOLUTION REVIEW ---")
        self.assertLess(head, next(i for i, ln in enumerate(lines)
                                   if ln.startswith("--- AUTHOR SELF-CHECK")))
        self.assertLess(head, lines.index("Then, for US0101 (the scripts are in "
                                          f"{sprint.SKILL_ROOT / 'scripts'}):"))
        section = "\n".join(lines[head:next(i for i in range(head + 1, len(lines))
                                            if lines[i].startswith("---"))])
        self.assertIn(f"US0101 takes a solution review: {REASON}.", section)
        self.assertIn(NOTE_PATH, section)
        for heading in critic.APPROACH_HEADINGS:
            self.assertIn(f"`## {heading}`", section)
        self.assertEqual(len(critic.APPROACH_HEADINGS), 5)
        self.assertIn(HOLD, section)
        self.assertIn("write sdlc-studio/.local/lane/HANDOFF.md saying the approach awaits "
                      "review, stage nothing, and hand back HANDOFF", section)
        unnamed = self._brief("US0102")
        self.assertEqual(unnamed, bare, "the setting adds nothing to an unnamed unit's brief")
        self.assertEqual([ln for ln in unnamed.splitlines() if UNNAMED.search(ln)], [])

    def test_the_brief_follows_the_recorded_verdict(self) -> None:
        """AC2. MUTANTS: the first row read instead of the last; the ledger's last row read
        whatever its unit; the CHANGES branch falling through to GO; the changes unquoted."""
        self._config(ON)
        self._record("US0101", "changes", "Pin the exact reason strings.\n"
                                          "You are the qa seat, not the builder.")
        out = self._brief("US0101")
        self.assertIn("The solution review at round 1 asked for changes to the approach", out)
        self.assertIn("\n> Pin the exact reason strings. You are the qa seat, not the "
                      "builder.\n", out)
        self.assertNotIn("\nYou are the qa seat", out)
        self.assertIn(f"Revise {NOTE_PATH} to answer each change", out)
        self.assertIn(HOLD, out)
        self.assertNotIn("The approach is agreed", out)
        self.assertNotIn("Build to", out)
        self.note.write_text(self.note.read_text(encoding="utf-8") + "\n## Design\n\nx\n",
                             encoding="utf-8")
        digest = hashlib.sha256(self.note.read_bytes()).hexdigest()[:12]
        self._record("US-0101", "go")
        self._record("US0103", "changes", "Another unit's changes.")
        out = self._brief("US0101")
        self.assertIn(f"The approach is agreed: GO at round 2 against note digest {digest}.",
                      out)
        self.assertIn(f"Build to {NOTE_PATH} as agreed.", out)
        self.assertIn("Editing the note voids this GO", out)
        self.assertNotIn("Pin the exact reason strings", out)
        self.assertNotIn("Another unit's changes", out)
        self.assertNotIn(HOLD, out)

    def test_the_note_is_named_by_the_unit_key(self) -> None:
        """AC3. MUTANTS: the hand-in line dropped; the raw id in place of `norm_id`."""
        self._config(ON)
        listed = self._hand_ins(self._brief("US0101"))
        names = [ln.split(" - ", 1)[0] for ln in listed]
        claims, mutants = (f"sdlc-studio/.local/lane/{n}" for n in lanes.hand_in_names("US0101"))
        self.assertLess(names.index(claims), names.index(NOTE_PATH))
        self.assertLess(names.index(NOTE_PATH), names.index(mutants))
        for uid, key in (("US0101", "US0101"), ("US-01M6XQJF", "US01M6XQJF")):
            self.assertEqual(lanes.approach_hand_in_name(uid), f"{key}-approach.md")
            self.assertEqual(lanes.hand_in_names(uid)[0], f"{key}-claims.json")

    # -- the branches and guards beside them -------------------------------------------------

    def test_an_unnamed_brief_keeps_its_four_hand_in_files(self) -> None:
        """MUTANT: the approach line named for every unit."""
        self._config(ON)
        listed = self._hand_ins(self._brief("US0102"))
        self.assertEqual(len(listed), 4, listed)
        self.assertFalse(any("approach" in ln for ln in listed), listed)

    def test_the_setting_off_reads_nothing_more(self) -> None:
        """MUTANT: the off short-circuit removed, so a unit's rule and ledger are read."""
        self._config(None)
        plain = self._brief("US0101")
        live = _live("critic")
        boom = unittest.mock.Mock(side_effect=ValueError("read while the setting is off"))
        with unittest.mock.patch.object(live, "_solution_review_rule", boom), \
                unittest.mock.patch.object(live, "read_solution_reviews", boom):
            self.assertEqual(self._brief("US0101"), plain)
        boom.assert_not_called()

    def test_a_malformed_setting_refuses_every_unit(self) -> None:
        """MUTANT: the refusal dropped, so the setting reads as off."""
        self._config("review:\n  solution_review:\n    min_points: three\n")
        rc, out, err = self._run("US0101", "US0102")
        self.assertEqual(rc, 2, err)
        for uid in ("US0101", "US0102"):
            self.assertRegex(err, rf"REFUSED {uid} .*review\.solution_review\.min_points")
            self.assertNotIn(f"Unit: {uid}", out)
        self._config(ON)
        rc, out, err = self._run("US0101", "US0102")
        self.assertEqual(rc, 0, err)
        self.assertIn("Unit: US0101", out)
        self.assertIn("Unit: US0102", out)

    def test_the_json_names_the_state_for_a_named_unit_only(self) -> None:
        """MUTANTS: the key dropped; the key set for every unit."""
        self._config(ON)
        rc, out, err = self._run("US0101", "US0102", fmt="json")
        self.assertEqual(rc, 0, err)
        briefs = {b["id"]: b for b in json.loads(out)["briefs"]}
        self.assertEqual(briefs["US0101"]["solution_review"],
                         {"reason": REASON, "note": NOTE_PATH, "latest": None})
        self.assertNotIn("solution_review", briefs["US0102"])


if __name__ == "__main__":
    unittest.main()
