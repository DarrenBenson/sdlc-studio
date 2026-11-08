"""US1118: `sprint lane land` commits a builder's staged lane through the hooks and lands it.

Every case drives `sprint.py lane land` through its entry point against a throwaway repository
whose `core.hooksPath` holds a stub pre-commit hook: it logs the checkout it ran in and refuses any
commit staging a file under `src/refuse`. So both a hook that passes and one that refuses are
exercised, and a commit that bypassed the hook would leave no line in its log. The fixture's units
are real enough for `critic.py self-check record` and `critic.py brief --seat qa` to run, under
`review.author_self_check: block`, so a brief is only written when the self-check recorded on
main matches what landed. One case stubs the critic, for a brief refusal no real unit provokes
within one landing.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/lanes.py
from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import loader  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
from lib import lanes  # noqa: E402

SPRINT = SCRIPTS / "sprint.py"
critic = loader.load_script("critic")
sprint = loader.load_script("sprint")

A, B = "US0101", "US0102"
BRANCH = "lane-us0101"
LANE = "sdlc-studio/.local/lane"
REFUSAL = "stub pre-commit: REFUSED src/refuse.py"
HOOK = """#!/bin/sh
git rev-parse --show-toplevel >> "{log}"
if git diff --cached --name-only | grep -q '^src/refuse'; then
  echo "{refusal}" >&2
  exit 1
fi
exit 0
"""


def _write(root: Path, rel: str, body: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _story(root: Path, unit: str, affects: str) -> None:
    _write(root, f"sdlc-studio/stories/{unit}-lane.md",
           f"# {unit}: lane\n\n> **Status:** Review\n> **Points:** 2\n> **Epic:** EP0001\n"
           f"> **Affects:** {affects}\n\n## Acceptance Criteria\n\n### AC1: works\n"
           "- **Verify:** shell true\n")


def _git(cwd: Path, *args: str) -> str:
    return gitutil.git(list(args), cwd, text=True).stdout.strip()


class LaneLandTests(unittest.TestCase):

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        base = Path(self._tmp.name).resolve()
        # the worktree is named `lane-<unit>`, as `sprint lane run` names it for every round
        self.root, self.wt, self.log = base / "repo", base / BRANCH, base / "hook.log"
        _write(self.root, "src/a.py", "A = 1\n")
        _write(self.root, "src/b.py", "B = 1\n")
        _write(self.root, "tests/test_a.py", "def test_a():\n    assert True\n")
        _write(self.root, ".gitignore", "sdlc-studio/.local/\n")
        _write(self.root, "sdlc-studio/personas/seats/qa.md",
               "<!-- role: qa -->\n# Sam - QA amigo\n\ncharter\n")
        _write(self.root, "sdlc-studio/.config.yaml", "review:\n  author_self_check: block\n")
        _story(self.root, A, f"src/a.py, tests/test_a.py, changelog.d/{A}.md")
        _story(self.root, B, f"src/b.py, changelog.d/{B}.md")
        gitutil.git(["init", "-q", "-b", "main"], self.root)
        gitutil.git(["add", "-A"], self.root)
        gitutil.git(["commit", "-q", "-m", "chore: the fixture"], self.root)
        _write(base, "hooks/pre-commit", HOOK.format(log=self.log, refusal=REFUSAL))
        (base / "hooks" / "pre-commit").chmod(0o755)
        gitutil.git(["config", "core.hooksPath", str(base / "hooks")], self.root)
        gitutil.git(["worktree", "add", "-q", "-b", BRANCH, str(self.wt), "main"], self.root)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    # -- the lane a builder hands in ------------------------------------------------------

    def _stage(self, rel: str, body: str) -> None:
        _write(self.wt, rel, body)
        gitutil.git(["add", "--", rel], self.wt)

    def _hand_in(self, units: tuple[str, ...] = (A,), message: str = f"feat({A}): a is two",
                 self_check: bool = True) -> None:
        lane = "sdlc-studio/.local/lane"
        _write(self.wt, f"{lane}/commit-msg.txt", message + "\n")
        for unit in units if self_check else ():
            claims = [{"surface": "commit message", "claim": "a is two", "ruling": "TRUE"},
                      {"surface": f"changelog.d/{unit}.md", "claim": "a is two",
                       "ruling": "TRUE"}]
            mutants = ([{"mutant": "a stays one", "test": "tests/test_a.py::test_a",
                         "result": "killed"}] if unit == A else [])
            _write(self.wt, f"{lane}/{unit}-claims.json", json.dumps(claims))
            _write(self.wt, f"{lane}/{unit}-mutants.json", json.dumps(mutants))

    def _move_main(self, rel: str, body: str) -> str:
        """A commit on main after the lane branched, so landing it needs a real rebase."""
        _write(self.root, rel, body)
        gitutil.git(["add", "--", rel], self.root)
        gitutil.git(["commit", "-q", "-m", f"chore: main moves {rel}"], self.root)
        return _git(self.root, "rev-parse", "HEAD")

    def _land(self, *units: str, author: str | None = None) -> subprocess.CompletedProcess:
        named = ["--author", author] if author else []
        return subprocess.run(
            [sys.executable, "-B", str(SPRINT), "lane", "land", "--worktree", str(self.wt),
             "--units", *units, *named, "--root", str(self.root)],
            capture_output=True, text=True, timeout=600, cwd=str(self.root),
            env=gitutil.git_env(), check=False)

    def _hook_runs_in_the_worktree(self) -> int:
        lines = self.log.read_text(encoding="utf-8").splitlines() if self.log.exists() else []
        return lines.count(str(self.wt))

    def _branches(self) -> list[str]:
        return _git(self.root, "branch", "--format=%(refname:short)").splitlines()

    def _land_round_one(self) -> str:
        """Round one of a lane: landed from `lane-<unit>` with its claims, its mutants and a
        HANDOFF.md handed in, then the same worktree name checked out again for a repair, as
        `sprint lane run` does. Main's head after round one."""
        self._stage("src/a.py", "A = 2\n")
        self._hand_in()
        _write(self.wt, f"{LANE}/HANDOFF.md", "ROUND ONE handoff\n")
        self._land_and_reopen()
        return _git(self.root, "rev-parse", "HEAD")

    def _land_and_reopen(self) -> None:
        """Land a round that must land cleanly, then check the same worktree name out again."""
        r = self._land(A)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertFalse(self.wt.exists(), "the landed round's worktree was not removed")
        gitutil.git(["worktree", "add", "-q", "-b", BRANCH, str(self.wt), "main"], self.root)

    # -- the criteria ---------------------------------------------------------------------

    def test_a_staged_lane_is_committed_rebased_and_fast_forwarded(self) -> None:
        moved = self._move_main("src/b.py", "B = 2\n")
        self._stage("src/a.py", "A = 2\n")
        self._hand_in()
        r = self._land(A)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertEqual(1, self._hook_runs_in_the_worktree(),
                         "the commit did not run the pre-commit hook in the worktree")
        self.assertEqual(f"feat({A}): a is two", _git(self.root, "log", "-1", "--format=%s"))
        # rebased onto the moved main and fast-forwarded: one parent, and that parent is main
        self.assertEqual(moved, _git(self.root, "rev-parse", "HEAD^"))
        self.assertEqual(1, len(_git(self.root, "log", "-1", "--format=%P").split()))
        self.assertEqual("A = 2\n", (self.root / "src/a.py").read_text(encoding="utf-8"))
        self.assertEqual("B = 2\n", (self.root / "src/b.py").read_text(encoding="utf-8"))
        self.assertFalse(self.wt.exists(), "the worktree was not removed")
        self.assertNotIn(str(self.wt), _git(self.root, "worktree", "list"))
        self.assertEqual(["main"], self._branches())
        landed = self.root / "sdlc-studio/.local/lane/landed" / self.wt.name / "commit-msg.txt"
        self.assertTrue(landed.is_file(), "the hand-in was not copied out before the removal")

    def test_a_hook_refusal_leaves_main_and_the_worktree_untouched(self) -> None:
        self._stage("src/refuse.py", "X = 1\n")
        self._hand_in()
        main_before, lane_before = (_git(self.root, "rev-parse", "HEAD"),
                                    _git(self.wt, "rev-parse", "HEAD"))
        r = self._land(A)
        out = r.stdout + r.stderr
        self.assertNotEqual(0, r.returncode, out)
        self.assertEqual(1, self._hook_runs_in_the_worktree())
        self.assertIn(REFUSAL, out, "the hook's own refusal was not printed")
        self.assertIn(f"Resume in {self.wt}", out, "the worktree to resume in was not named")
        self.assertEqual(main_before, _git(self.root, "rev-parse", "HEAD"))
        self.assertTrue(self.wt.is_dir(), "the worktree was removed after a refusal")
        self.assertEqual(lane_before, _git(self.wt, "rev-parse", "HEAD"))
        self.assertEqual("src/refuse.py", _git(self.wt, "diff", "--cached", "--name-only"))
        self.assertIn(BRANCH, self._branches())
        self.assertFalse((self.root / "sdlc-studio/reviews/author-self-checks.md").exists(),
                         "a self-check was recorded for a lane that never landed")

    def test_a_rebase_conflict_is_aborted_and_named(self) -> None:
        moved = self._move_main("src/a.py", "A = 3\n")
        self._stage("src/a.py", "A = 2\n")
        self._hand_in()
        r = self._land(A)
        out = r.stdout + r.stderr
        self.assertNotEqual(0, r.returncode, out)
        self.assertIn("Conflicting files: src/a.py.", out)
        self.assertNotIn("rebase --continue", out, "git's hint to continue an aborted rebase")
        self.assertEqual(moved, _git(self.root, "rev-parse", "HEAD"))
        self.assertEqual("A = 3\n", (self.root / "src/a.py").read_text(encoding="utf-8"))
        rebase_dir = Path(_git(self.wt, "rev-parse", "--path-format=absolute",
                               "--git-path", "rebase-merge"))
        self.assertFalse(rebase_dir.exists(), "the rebase was left in progress, not aborted")
        self.assertEqual("A = 2\n", (self.wt / "src/a.py").read_text(encoding="utf-8"))
        self.assertEqual(f"feat({A}): a is two", _git(self.wt, "log", "-1", "--format=%s"))
        self.assertIn(BRANCH, self._branches())

    def test_each_landed_unit_gets_its_self_check_and_brief(self) -> None:
        self._stage("src/a.py", "A = 2\n")
        self._stage(f"changelog.d/{A}.md", "a is two\n")
        self._stage("src/b.py", "B = 2\n")
        self._stage(f"changelog.d/{B}.md", "b is two\n")
        self._hand_in(units=(A, B), message=f"feat({A}): a and b are two")
        r = self._land(A, B)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        head = _git(self.root, "rev-parse", "HEAD")
        rows = {row["unit"]: row for row in critic.read_self_checks(self.root)}
        self.assertEqual({A, B}, set(rows))
        for unit in (A, B):
            with self.subTest(unit=unit):
                # taken on main, after the landing: at main's new head, not in the worktree
                self.assertTrue(head.startswith(rows[unit]["commit"]) and rows[unit]["commit"],
                                f"{unit}'s self-check was not taken at main's landed head")
                self.assertEqual(self.wt.name, rows[unit]["author"],
                                 "with no --author the worktree's directory name is the author")
                brief = self.root / f"sdlc-studio/.local/briefs/{unit}-qa.txt"
                self.assertTrue(brief.is_file(), f"no QA brief written for {unit}")
                fp = critic.brief_fingerprint(brief.read_text(encoding="utf-8"))
                lines = [ln for ln in r.stdout.splitlines() if ln.startswith(f"{unit}: ")]
                self.assertEqual(1, len(lines), r.stdout)
                self.assertIn(f"review tier: {critic.tier_for(self.root, unit)},", lines[0])
                self.assertIn(f"fingerprint: {fp}", lines[0])

    # -- the refusals and the resume the module documents ---------------------------------

    def test_a_staged_change_with_no_commit_message_is_refused_before_anything_moves(self) -> None:
        self._stage("src/a.py", "A = 2\n")
        r = self._land(A)
        self.assertEqual(2, r.returncode, r.stdout + r.stderr)
        self.assertIn("no commit message", r.stderr)
        self.assertEqual(0, self._hook_runs_in_the_worktree())
        self.assertEqual("src/a.py", _git(self.wt, "diff", "--cached", "--name-only"))

    def test_a_worktree_that_is_not_the_roots_own_is_refused(self) -> None:
        other = Path(self._tmp.name) / "other"
        other.mkdir()
        gitutil.git(["init", "-q", "-b", "main"], other)
        main_before = _git(self.root, "rev-parse", "HEAD")
        for worktree, said in ((self.root, "is the root checkout itself"),
                               (other, "is not a worktree of"),
                               (Path(self._tmp.name) / "absent", "no worktree at")):
            with self.subTest(worktree=worktree.name):
                r = subprocess.run(
                    [sys.executable, "-B", str(SPRINT), "lane", "land", "--worktree",
                     str(worktree), "--units", A, "--root", str(self.root)],
                    capture_output=True, text=True, timeout=120, cwd=str(self.root),
                    env=gitutil.git_env(), check=False)
                self.assertEqual(2, r.returncode, r.stdout + r.stderr)
                self.assertIn(said, r.stderr)
        self.assertEqual(main_before, _git(self.root, "rev-parse", "HEAD"))

    def test_a_branch_already_committed_is_landed_without_a_second_commit(self) -> None:
        r = self._land(A)
        self.assertEqual(2, r.returncode, r.stdout + r.stderr)
        self.assertIn("nothing to land", r.stderr)
        self._stage("src/a.py", "A = 2\n")
        gitutil.git(["commit", "-q", "-m", f"feat({A}): a is two"], self.wt)
        self._hand_in()
        r = self._land(A)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertNotIn("committed", r.stdout)
        self.assertEqual(2, int(_git(self.root, "rev-list", "--count", "HEAD")))
        self.assertFalse(self.wt.exists())

    def test_a_unit_whose_hand_in_lacks_its_self_check_files_is_named(self) -> None:
        self._stage("src/a.py", "A = 2\n")
        self._hand_in(units=(A,))
        r = self._land(A, B, author="builder-x")
        self.assertEqual(1, r.returncode, r.stdout + r.stderr)
        self.assertIn(f"{B}: self-check NOT RECORDED", r.stderr)
        self.assertIn(f"{B}-claims.json", r.stderr)
        self.assertEqual([(A, "builder-x")], [(row["unit"], row["author"])
                                             for row in critic.read_self_checks(self.root)])
        self.assertTrue((self.root / f"sdlc-studio/.local/briefs/{A}-qa.txt").is_file(),
                        f"{B}'s missing files stopped {A} being briefed")
        self.assertFalse((self.root / f"sdlc-studio/.local/briefs/{B}-qa.txt").exists())

    def test_a_self_check_the_critic_refuses_is_named_and_leaves_no_brief(self) -> None:
        self._stage("src/a.py", "A = 2\n")
        self._hand_in()
        # no claim from the changelog fragment A's Affects declares: `critic.py` refuses it
        _write(self.wt, f"sdlc-studio/.local/lane/{A}-claims.json", json.dumps(
            [{"surface": "commit message", "claim": "a is two", "ruling": "TRUE"}]))
        r = self._land(A)
        self.assertEqual(1, r.returncode, r.stdout + r.stderr)
        self.assertIn(f"{A}: self-check REFUSED and no brief written", r.stderr)
        self.assertIn(f"no claim from the changelog.d/{A}.md", r.stderr,
                      "the critic's own reason was not carried")
        self.assertEqual([], critic.read_self_checks(self.root))
        self.assertFalse((self.root / f"sdlc-studio/.local/briefs/{A}-qa.txt").exists())

    def test_a_brief_the_critic_refuses_is_named_and_none_is_written(self) -> None:
        """The one stubbed critic: a brief refused after its self-check recorded cannot be
        provoked from a real unit within one landing, so `brief` alone is answered refused."""
        self._stage("src/a.py", "A = 2\n")
        self._hand_in()
        real = lanes._critic

        def critic_refusing_the_brief(root, *args):
            if args[0] == "brief":
                return subprocess.CompletedProcess(args, 2, "", "brief refused: stubbed\n")
            return real(root, *args)

        out, err = io.StringIO(), io.StringIO()
        with unittest.mock.patch.dict(os.environ, gitutil.git_env(), clear=True), \
                unittest.mock.patch.object(lanes, "_critic", critic_refusing_the_brief), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = sprint.main(["lane", "land", "--worktree", str(self.wt), "--units", A,
                                "--root", str(self.root)])
        self.assertEqual(1, code, out.getvalue() + err.getvalue())
        self.assertIn(f"{A}: self-check recorded; QA brief REFUSED - brief refused: stubbed",
                      err.getvalue())
        self.assertEqual([A], [row["unit"] for row in critic.read_self_checks(self.root)])
        self.assertFalse((self.root / f"sdlc-studio/.local/briefs/{A}-qa.txt").exists())

    def test_a_repair_round_without_a_hand_in_records_no_stale_self_check(self) -> None:
        first = self._land_round_one()
        rows = critic.read_self_checks(self.root)
        self.assertEqual([A], [row["unit"] for row in rows])
        self.assertTrue(first.startswith(rows[0]["commit"]) and rows[0]["commit"],
                        "round one's self-check was not recorded at its own landing")
        # the repair hands in its commit message alone: no claims and no mutants
        self._stage("src/a.py", "A = 3\n")
        self._hand_in(message=f"fix({A}): a is three", self_check=False)
        r = self._land(A)
        self.assertEqual(1, r.returncode, r.stdout + r.stderr)
        self.assertEqual("A = 3\n", (self.root / "src/a.py").read_text(encoding="utf-8"),
                         "the repair did not land")
        self.assertIn(f"{A}: self-check NOT RECORDED and no brief written - the hand-in "
                      f"carries no {A}-claims.json or {A}-mutants.json", r.stderr)
        self.assertEqual(rows, critic.read_self_checks(self.root),
                         "round one's claims and mutants were recorded for the repair")

    def _handed(self) -> dict[str, bytes]:
        return {p.name: p.read_bytes() for p in (self.wt / LANE).iterdir() if p.is_file()}

    def test_each_landing_starts_from_its_own_hand_in(self) -> None:
        self._land_round_one()
        keep = self.root / LANE / "landed" / self.wt.name
        own = [{"surface": "commit message", "claim": "a is three", "ruling": "TRUE"},
               {"surface": f"changelog.d/{A}.md", "claim": "a is three", "ruling": "TRUE"}]
        # round two stages its change, so the landing commits it and writes commit.log
        self._stage("src/a.py", "A = 3\n")
        self._hand_in(message=f"fix({A}): a is three")
        _write(self.wt, f"{LANE}/{A}-claims.json", json.dumps(own))
        handed = self._handed()
        self.assertNotIn("HANDOFF.md", handed)
        self._land_and_reopen()
        landed = {p.name: p.read_bytes() for p in keep.iterdir() if p.name != "commit.log"}
        self.assertEqual(handed, landed, "a file from round one's hand-in survived round two")
        log = (keep / "commit.log").read_text(encoding="utf-8")
        self.assertIn(f"fix({A}): a is three", log)
        self.assertNotIn(f"feat({A}): a is two", log)
        # round three lands a branch already committed: no commit message, no commit.log
        self._stage("src/a.py", "A = 4\n")
        gitutil.git(["commit", "-q", "-m", f"fix({A}): a is four"], self.wt)
        for name in (f"{A}-claims.json", f"{A}-mutants.json"):
            _write(self.wt, f"{LANE}/{name}", handed[name].decode("utf-8"))
        handed = self._handed()
        self.assertEqual({f"{A}-claims.json", f"{A}-mutants.json"}, set(handed))
        r = self._land(A)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertEqual(handed, {p.name: p.read_bytes() for p in keep.iterdir()},
                         "a file from round two's landing survived round three")

    def test_a_worktree_holding_an_uncommitted_change_is_left_in_place(self) -> None:
        self._stage("src/a.py", "A = 2\n")
        self._hand_in()
        _write(self.wt, "src/stray.py", "S = 1\n")
        r = self._land(A)
        self.assertEqual(1, r.returncode, r.stdout + r.stderr)
        self.assertEqual("A = 2\n", (self.root / "src/a.py").read_text(encoding="utf-8"))
        self.assertIn(f"the worktree {self.wt} was left in place", r.stderr)
        self.assertTrue((self.wt / "src/stray.py").is_file(), "the stray change was deleted")
        self.assertIn(BRANCH, self._branches())


if __name__ == "__main__":
    unittest.main()
