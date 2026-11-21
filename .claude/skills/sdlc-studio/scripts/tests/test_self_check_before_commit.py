"""`sprint lane land` judges each unit's self-check before it commits anything.

A self-check `critic.py self-check record` would refuse, one missing a required surface above
all, is refused before the commit: the builder's worktree, its staged change and its branch are
left as they were, main does not move and the commit hook never runs, so the builder repairs its
hand-in in place and lands again. Every case drives `sprint.py lane land` through its entry point
against the throwaway repository of `test_lane_land`, whose stub pre-commit hook logs each
checkout it ran in.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/lanes.py
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import test_lane_land as base  # noqa: E402

A, B, LANE = base.A, base.B, base.LANE
#: a commit-message claim alone: A's Affects also declares changelog.d/US0101.md
NO_FRAGMENT = [{"surface": "commit message", "claim": "a is two", "ruling": "TRUE"}]


class SelfCheckBeforeCommitTests(base._LaneFixture):
    """A self-check the critic refuses stops the landing before the commit."""

    def _lane(self) -> None:
        self._stage("src/a.py", "A = 2\n")
        self._hand_in()

    def _untouched(self, r: subprocess.CompletedProcess, main: str, unit: str = A) -> None:
        """Nothing moved: exit 2, the unit named, no commit, the worktree intact and staged."""
        said = r.stdout + r.stderr
        self.assertEqual(2, r.returncode, said)
        self.assertIn(f"{unit}'s self-check", r.stderr)
        self.assertEqual(0, self._hook_runs_in_the_worktree(),
                         "the commit hook ran, so the commit was attempted first")
        self.assertEqual(main, base._git(self.root, "rev-parse", "HEAD"), "main moved")
        self.assertEqual(main, base._git(self.wt, "rev-parse", "HEAD"),
                         "the worktree's branch gained a commit")
        self.assertTrue(self.wt.is_dir(), "the worktree was removed")
        self.assertIn(base.BRANCH, self._branches())
        self.assertEqual("src/a.py", base._git(self.wt, "diff", "--cached", "--name-only"),
                         "the staged change was not left staged")
        self.assertTrue((self.wt / LANE / "commit-msg.txt").is_file(),
                        "the hand-in was taken out of the worktree")
        self.assertEqual([], base.critic.read_self_checks(self.root))
        self.assertFalse((self.root / f"sdlc-studio/.local/briefs/{unit}-qa.txt").exists())

    def test_a_self_check_missing_a_required_surface_is_refused_before_the_commit(self) -> None:
        main = base._git(self.root, "rev-parse", "HEAD")
        self._lane()
        base._write(self.wt, f"{LANE}/{A}-claims.json", json.dumps(NO_FRAGMENT))
        r = self._land(A)
        self._untouched(r, main)
        self.assertIn(f"no claim from the changelog.d/{A}.md", r.stderr,
                      "the critic's own reason was not carried")
        self.assertNotIn("committed", r.stdout)

    def test_the_repaired_hand_in_then_lands_from_the_same_worktree(self) -> None:
        """The refusal is the whole point of judging first: the builder fixes the file in its
        worktree and the next landing commits, records and briefs."""
        self._lane()
        base._write(self.wt, f"{LANE}/{A}-claims.json", json.dumps(NO_FRAGMENT))
        self.assertEqual(2, self._land(A).returncode)
        self._hand_in()
        r = self._land(A)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertEqual(1, self._hook_runs_in_the_worktree())
        self.assertEqual("A = 2\n", (self.root / "src/a.py").read_text(encoding="utf-8"))
        self.assertEqual([A], [row["unit"] for row in base.critic.read_self_checks(self.root)])
        self.assertTrue((self.root / f"sdlc-studio/.local/briefs/{A}-qa.txt").is_file())

    def test_a_refused_repair_leaves_the_brief_the_last_landing_wrote(self) -> None:
        """Nothing landed, so the code on main is still the code the last brief covers."""
        self._stage("src/a.py", "A = 2\n")
        self._hand_in()
        self._land_and_reopen()
        brief = self.root / f"sdlc-studio/.local/briefs/{A}-qa.txt"
        before = (brief.read_bytes(), brief.stat().st_ino)
        main = base._git(self.root, "rev-parse", "HEAD")
        self._stage("src/a.py", "A = 3\n")
        self._hand_in(message=f"fix({A}): a is three")
        base._write(self.wt, f"{LANE}/{A}-claims.json", json.dumps(NO_FRAGMENT))
        r = self._land(A)
        self.assertEqual(2, r.returncode, r.stdout + r.stderr)
        self.assertEqual(main, base._git(self.root, "rev-parse", "HEAD"))
        self.assertEqual(before, (brief.read_bytes(), brief.stat().st_ino))
        self.assertFalse(brief.with_suffix(".none").exists())

    def test_every_cause_the_critic_refuses_is_judged_before_the_commit(self) -> None:
        cases = {
            "a mutant against a test the unit does not declare": (
                f"{A}-mutants.json",
                json.dumps([{"mutant": "a stays one", "test": "tests/test_b.py::test_b",
                             "result": "killed"}]),
                "not a test file the unit's Affects declares"),
            "a claims file that is not JSON": (f"{A}-claims.json", "{not json",
                                               "cannot read"),
            "a claims file that is not UTF-8": (f"{A}-claims.json", b"\xff\xfe[]",
                                                "cannot read"),
            "a claim ruled FALSE": (
                f"{A}-claims.json",
                json.dumps([*NO_FRAGMENT, {"surface": f"changelog.d/{A}.md", "claim": "x",
                                           "ruling": "FALSE"}]), "ruled FALSE"),
            "a runner report for another unit": (
                f"{A}-mutation-edits.json",
                json.dumps({"kind": "mutation-edits", "version": 1, "unit": B,
                            "mutants": [], "counts": {}}), f"not {A}"),
        }
        for label, (name, body, reason) in cases.items():
            with self.subTest(label):
                main = base._git(self.root, "rev-parse", "HEAD")
                self._lane()
                path = self.wt / LANE / name
                (path.write_bytes if isinstance(body, bytes) else path.write_text)(body)
                r = self._land(A)
                self._untouched(r, main)
                self.assertIn(reason, r.stderr)
                path.unlink()
                gitutil.git(["reset", "-q", "--hard"], self.wt)

    def test_the_self_check_is_judged_against_the_affects_on_the_root(self) -> None:
        """Where it is recorded once landed: main dropped the fragment from A's Affects after the
        worktree branched, so a commit-message claim alone is whole, though the worktree's
        older copy of A still declares the fragment."""
        base._story(self.root, A, "src/a.py, tests/test_a.py")
        gitutil.git(["commit", "-q", "-am", "chore: A ships no fragment"], self.root)
        self._lane()
        base._write(self.wt, f"{LANE}/{A}-claims.json", json.dumps(NO_FRAGMENT))
        r = self._land(A)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertEqual([A], [row["unit"] for row in base.critic.read_self_checks(self.root)])

    def test_a_unit_only_the_lane_holds_is_judged_against_its_own_file(self) -> None:
        unit = "US0103"
        base._story(self.wt, unit, f"src/c.py, changelog.d/{unit}.md")
        gitutil.git(["add", "--", f"sdlc-studio/stories/{unit}-lane.md"], self.wt)
        self._stage("src/c.py", "C = 1\n")
        base._write(self.wt, f"{LANE}/commit-msg.txt", f"feat({unit}): c\n")
        base._write(self.wt, f"{LANE}/{unit}-claims.json", json.dumps(
            [*NO_FRAGMENT, {"surface": f"changelog.d/{unit}.md", "claim": "c", "ruling": "TRUE"}]))
        base._write(self.wt, f"{LANE}/{unit}-mutants.json", "[]")
        r = self._land(unit)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertEqual([unit], [row["unit"] for row in base.critic.read_self_checks(self.root)])

    def test_a_hand_in_with_no_self_check_files_is_not_judged_before_the_commit(self) -> None:
        """Judging first covers the self-check the landing would record; a hand-in that carries
        none still lands and is named as unrecorded after, as before."""
        self._stage("src/a.py", "A = 2\n")
        self._hand_in(self_check=False)
        r = self._land(A)
        self.assertEqual(1, r.returncode, r.stdout + r.stderr)
        self.assertEqual("A = 2\n", (self.root / "src/a.py").read_text(encoding="utf-8"))
        self.assertIn(f"{A}: self-check NOT RECORDED", r.stderr)


class SelfCheckBeforeCommitSeveralTests(base._LaneFixture):
    """Landing several worktrees as one commit judges every unit's self-check before it."""

    def setUp(self) -> None:
        super().setUp()
        self.wt2 = Path(self._tmp.name).resolve() / "lane-us0102"
        gitutil.git(["worktree", "add", "-q", "-b", "lane-us0102", str(self.wt2), "main"],
                    self.root)

    def test_a_refused_self_check_in_a_later_worktree_stops_both_before_the_commit(self) -> None:
        main = base._git(self.root, "rev-parse", "HEAD")
        self._stage("src/a.py", "A = 2\n")
        self._hand_in(units=(A,))
        first, self.wt = self.wt, self.wt2
        try:
            self._stage("src/b.py", "B = 2\n")
            self._hand_in(units=(B,), message=f"feat({B}): b is two")
            base._write(self.wt, f"{LANE}/{B}-claims.json", json.dumps(NO_FRAGMENT))
        finally:
            self.wt = first
        r = subprocess.run(
            [sys.executable, "-B", str(base.SPRINT), "lane", "land", "--worktree", str(self.wt),
             "--worktree", str(self.wt2), "--units", A, B, "--root", str(self.root)],
            capture_output=True, text=True, timeout=600, cwd=str(self.root), env=self._env(),
            check=False)
        self.assertEqual(2, r.returncode, r.stdout + r.stderr)
        self.assertIn(f"{B}'s self-check", r.stderr)
        self.assertIn(f"no claim from the changelog.d/{B}.md", r.stderr)
        self.assertEqual(main, base._git(self.root, "rev-parse", "HEAD"))
        lines = self.log.read_text(encoding="utf-8").splitlines() if self.log.exists() else []
        self.assertEqual([], [ln for ln in lines if ln in (str(self.wt), str(self.wt2))])
        self.assertEqual("src/a.py", base._git(self.wt, "diff", "--cached", "--name-only"))
        self.assertEqual("src/b.py", base._git(self.wt2, "diff", "--cached", "--name-only"))
        self.assertEqual([], base.critic.read_self_checks(self.root))


if __name__ == "__main__":
    unittest.main()
