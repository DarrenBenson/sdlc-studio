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
import re
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import loader  # noqa: E402
import test_meter_reads_true as meter  # noqa: E402 - the fixture harness store and its weights

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
from lib import lanes, run_state, sdlc_md  # noqa: E402

SPRINT = SCRIPTS / "sprint.py"
critic = loader.load_script("critic")
sprint = loader.load_script("sprint")

A, B = "US0101", "US0102"
#: A schema-3 id as a schema-3 project spells it; `sdlc_md.norm_id` drops its hyphen.
V3 = "US-01M6XQJF"
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

RED = "stub pre-commit: tests/test_a.py is red"
#: refuses a commit whose checkout holds a failing tests/test_a.py, as a suite run would
RED_HOOK = """#!/bin/sh
git rev-parse --show-toplevel >> "{log}"
if grep -q 'assert False' tests/test_a.py; then
  echo "%s" >&2
  exit 1
fi
exit 0
""" % RED


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


class _LaneFixture(unittest.TestCase):
    """The throwaway repository, its stub hook and the builder's worktree every case lands."""

    #: the worktree's directory name: `lane-<unit>`, as `sprint lane run` names it every round
    WORKTREE = BRANCH

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        base = Path(self._tmp.name).resolve()
        self.root, self.wt, self.log = base / "repo", base / self.WORKTREE, base / "hook.log"
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
            env=self._env(), check=False)

    def _env(self) -> dict:
        """The environment every command here runs in: the operator's git configuration set aside."""
        return gitutil.git_env()

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


class LaneLandTests(_LaneFixture):

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

    # -- a worktree the builder verified in, and one behind main --------------------------

    def _verify_in_the_worktree(self) -> str:
        """`verify_ac.py run --id <unit>` in the worktree, as the lane brief has a builder run it:
        it writes its Verified lines into the unit's story, outside the Affects the builder
        staged. The story's path, relative to the worktree."""
        rel = f"sdlc-studio/stories/{A}-lane.md"
        before = (self.wt / rel).read_text(encoding="utf-8")
        r = subprocess.run([sys.executable, "-B", str(SCRIPTS / "verify_ac.py"), "run", "--id",
                            A, "--root", str(self.wt)], capture_output=True, text=True,
                           timeout=300, cwd=str(self.wt), env=gitutil.git_env(), check=False)
        self.assertNotEqual(before, (self.wt / rel).read_text(encoding="utf-8"),
                            f"verify_ac wrote nothing into the story:\n{r.stdout}{r.stderr}")
        return rel

    def test_verify_acs_artefact_edit_does_not_block_the_land(self) -> None:
        moved = self._move_main("src/b.py", "B = 2\n")
        self._stage("src/a.py", "A = 2\n")
        self._hand_in()
        story = self._verify_in_the_worktree()
        r = self._land(A)
        out = r.stdout + r.stderr
        self.assertEqual(0, r.returncode, out)
        self.assertNotIn("unstaged changes", out)
        self.assertEqual(moved, _git(self.root, "rev-parse", "HEAD^"))
        self.assertEqual("A = 2\n", (self.root / "src/a.py").read_text(encoding="utf-8"))
        self.assertEqual(["src/a.py"],
                         _git(self.root, "show", "--name-only", "--format=", "HEAD").split(),
                         "verify_ac's edit to the story was committed outside the Affects")
        self.assertIn(f"discarded {story}", out, "the discarded edit was not named")
        self.assertFalse(self.wt.exists(), "the worktree was not removed")

    def test_an_unstaged_edit_to_any_other_file_is_kept_and_still_stops_the_land(self) -> None:
        main_before = self._move_main("src/b.py", "B = 2\n")
        self._stage("src/a.py", "A = 2\n")
        self._hand_in()
        self._verify_in_the_worktree()
        _write(self.wt, "tests/test_a.py", "def test_a():\n    assert 1\n")
        r = self._land(A)
        out = r.stdout + r.stderr
        self.assertNotEqual(0, r.returncode, out)
        self.assertIn("unstaged changes", out)
        self.assertEqual(main_before, _git(self.root, "rev-parse", "HEAD"))
        self.assertEqual("def test_a():\n    assert 1\n",
                         (self.wt / "tests/test_a.py").read_text(encoding="utf-8"),
                         "an unstaged edit outside the unit's own artefact was discarded")
        # the replay git refused is undone: the lane holds its own commit and nothing else
        self.assertEqual([f"feat({A}): a is two"],
                         _git(self.wt, "log", "--format=%s", "main..HEAD").splitlines())

    def test_a_lane_behind_main_is_judged_on_mains_code(self) -> None:
        self._move_main("tests/test_a.py", "def test_a():\n    assert False\n")
        gitutil.git(["merge", "-q", "--ff-only", "main"], self.wt)  # the lane's base is red
        fixed = self._move_main("tests/test_a.py", "def test_a():\n    assert True\n")
        # from here the hook refuses a commit whose checkout still holds the red test
        _write(Path(self._tmp.name), "hooks/pre-commit", RED_HOOK.format(log=self.log))
        self._stage("src/a.py", "A = 2\n")
        self._hand_in()
        r = self._land(A)
        out = r.stdout + r.stderr
        self.assertEqual(0, r.returncode, out)
        self.assertNotIn(RED, out)
        self.assertEqual(1, self._hook_runs_in_the_worktree(),
                         "the commit did not run the pre-commit hook in the worktree")
        self.assertEqual(f"feat({A}): a is two", _git(self.root, "log", "-1", "--format=%s"))
        self.assertEqual(fixed, _git(self.root, "log", "-1", "--format=%P"),
                         "the lane was not landed as one commit on main's fixed head")
        self.assertEqual("A = 2\n", (self.root / "src/a.py").read_text(encoding="utf-8"))
        self.assertEqual("def test_a():\n    assert True\n",
                         (self.root / "tests/test_a.py").read_text(encoding="utf-8"))

    def test_a_staged_change_main_already_holds_leaves_nothing_to_commit(self) -> None:
        moved = self._move_main("src/a.py", "A = 2\n")
        self._stage("src/a.py", "A = 2\n")
        self._hand_in()
        r = self._land(A)
        out = r.stdout + r.stderr
        self.assertEqual(0, r.returncode, out)
        self.assertIn("the staged change is already on main", out)
        self.assertEqual(0, self._hook_runs_in_the_worktree(), "an empty change was committed")
        self.assertEqual(moved, _git(self.root, "rev-parse", "HEAD"))
        self.assertFalse(self.wt.exists(), "the worktree was not removed")

    # -- a schema-3 unit, named as written (BG1303) ---------------------------------------

    def _schema3_brief(self) -> dict[str, str]:
        """Make the project schema 3 with a hyphenated story on main, open a run on it and brief
        it by its id as written: the hand-in paths that brief prints, keyed by kind."""
        _write(self.root, "sdlc-studio/.config.yaml",
               "schema_version: 3\nreview:\n  author_self_check: block\n")
        _story(self.root, V3, "src/a.py, tests/test_a.py")
        gitutil.git(["add", "-A"], self.root)
        gitutil.git(["commit", "-q", "-m", f"chore: {V3} on a schema-3 project"], self.root)
        transcripts = Path(self._tmp.name) / "transcripts"
        transcripts.mkdir()
        out, err = io.StringIO(), io.StringIO()
        with unittest.mock.patch.dict(os.environ, {run_state.TRANSCRIPTS_ENV: str(transcripts)}), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            run_state.open_run(self.root, batch=[V3], goal="g")
            rc = sprint.main(["lane", "brief", "--units", V3, "--root", str(self.root)])
        self.assertEqual(0, rc, err.getvalue())
        printed = dict(re.findall(rf"^ +({LANE}/\S+-(claims|mutants)\.json) - ", out.getvalue(),
                                  re.M))
        named = {kind: path for path, kind in printed.items()}
        self.assertEqual({"claims", "mutants"}, set(named), out.getvalue())
        return named

    def _schema3_hand_in(self, files: dict[str, str]) -> None:
        self._stage("src/a.py", "A = 2\n")
        _write(self.wt, f"{LANE}/commit-msg.txt", f"feat({V3}): a is two\n")
        body = {"claims": [{"surface": "commit message", "claim": "a is two", "ruling": "TRUE"}],
                "mutants": [{"mutant": "a stays one", "test": "tests/test_a.py::test_a",
                             "result": "killed"}]}
        for kind, rel in files.items():
            _write(self.wt, rel, json.dumps(body[kind]))

    def test_a_schema3_unit_landed_by_its_hyphenated_id_records_its_self_check_and_writes_its_qa_brief(
            self) -> None:
        named = self._schema3_brief()
        self._schema3_hand_in(named)
        r = self._land(V3)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertNotIn("self-check NOT RECORDED", r.stdout + r.stderr)
        self.assertEqual(["US01M6XQJF"], [sdlc_md.norm_id(row["unit"])
                                         for row in critic.read_self_checks(self.root)])
        line = [ln for ln in r.stdout.splitlines() if ln.startswith(f"{V3}: ")]
        self.assertEqual(1, len(line), r.stdout)
        brief = re.search(r"self-check recorded; QA brief (\S+), review tier", line[0])
        self.assertIsNotNone(brief, line[0])
        self.assertTrue((self.root / brief.group(1)).is_file(), f"no QA brief at {brief.group(1)}")

    def test_a_schema3_hand_in_missing_its_files_is_still_named_by_the_spelling_land_read(
            self) -> None:
        """The mutants file under the brief's name and the claims file under the hyphenated
        spelling: land reads only the brief's key, so the claims file is the one named."""
        named = self._schema3_brief()
        self._schema3_hand_in({"claims": f"{LANE}/{V3}-claims.json",
                               "mutants": named["mutants"]})
        r = self._land(V3)
        self.assertEqual(1, r.returncode, r.stdout + r.stderr)
        line = [ln for ln in r.stderr.splitlines() if ln.startswith(f"{V3}: ")]
        self.assertEqual(1, len(line), r.stderr)
        self.assertIn("self-check NOT RECORDED", line[0])
        self.assertTrue(line[0].endswith("the hand-in carries no US01M6XQJF-claims.json"),
                        line[0])
        self.assertEqual([], critic.read_self_checks(self.root))
        self.assertEqual([], sorted((self.root / lanes.BRIEFS).glob("*-qa.txt")))


#: the builder's two messages, in the harness's usage shape
BUILD_1 = meter._usage(40, 400, 5_000, 0, 120_000)
BUILD_2 = meter._usage(15, 150, 800, 0, 30_000)


class LandPricesTheBuilderTests(_LaneFixture):
    """BG1330. `lane land` read the builder's id off its `agent-<id>` worktree only as the
    self-check's author and recorded no return, so a unit no one returned by hand with `lane
    return --agent` read NOT MEASURED. Each case lands through `sprint.py lane land` with HOME,
    CLAUDE_CONFIG_DIR and XDG_DATA_HOME on a temporary harness store, never the operator's, and
    prices against the fixture store's own weight table (`test_meter_reads_true`)."""

    AGENT = "a1b2c3d4e5f6"
    WORKTREE = f"agent-{AGENT}"

    def setUp(self) -> None:
        super().setUp()
        base = Path(self._tmp.name).resolve()
        self.home = base / "home"
        self.tx = meter._Transcripts(self.home / ".claude" / "projects"
                                     / run_state.harness_project_slug(self.root))
        # the orchestrating session's own transcript, whose subagents directory holds the builder's
        meter._Transcripts._append(self.tx.main, self.tx._records("msg_main", meter.MAIN_1, None,
                                                                  str(self.root)))
        (base / "no-transcripts").mkdir()
        with unittest.mock.patch.dict(os.environ,
                                      {run_state.TRANSCRIPTS_ENV: str(base / "no-transcripts")}):
            run_state.open_run(self.root, batch=[A, B], goal="g")
        self.builder = self.tx.subagents / f"agent-{self.AGENT}.jsonl"

    def _env(self) -> dict:
        env = {k: v for k, v in gitutil.git_env().items() if k != run_state.TRANSCRIPTS_ENV}
        env.update(HOME=str(self.home), CLAUDE_CONFIG_DIR=str(self.home / ".claude"),
                   XDG_DATA_HOME=str(self.home / ".local" / "share"))
        return env

    def _builder_says(self, *usages: dict) -> None:
        lines = [ln for n, usage in enumerate(usages)
                 for ln in self.tx._records(f"msg_build_{n}", usage, None, str(self.wt))]
        meter._Transcripts._append(self.builder, lines)

    def _returns(self, unit: str = A) -> list[dict]:
        return [r for r in run_state.read(self.root).get(run_state.DELEGATED) or []
                if r.get("unit") == unit]

    def test_a_landed_unit_is_priced_from_its_builders_transcript(self) -> None:
        self._builder_says(BUILD_1, BUILD_2)
        self._stage("src/a.py", "A = 2\n")
        self._hand_in()
        r = self._land(A)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        parts = meter._sum(BUILD_1, BUILD_2)
        landed = self._returns()
        self.assertEqual(1, len(landed), r.stdout + r.stderr)
        self.assertEqual((meter._priced(parts), meter._tokens(parts), str(self.builder),
                          f"agent-{self.AGENT}"),
                         tuple(landed[0].get(k) for k in ("priced", "tokens", "transcript",
                                                          "agent")))
        self.assertIn(f"{A}'s return priced from {self.WORKTREE}'s transcript: "
                      f"{meter._tokens(parts):,} tokens", r.stdout)
        # `lane return --agent` reading the same transcript writes the same record, in its place
        back = subprocess.run([sys.executable, "-B", str(SPRINT), "lane", "return", "--units", A,
                               "--agent", self.AGENT, "--root", str(self.root)],
                              capture_output=True, text=True, timeout=600, cwd=str(self.root),
                              env=self._env(), check=False)
        returned = self._returns()
        self.assertEqual(1, len(returned), back.stdout + back.stderr)
        for key in ("tokens", "priced", "components", run_state.BY_MODEL, "transcript", "agent",
                    "provenance"):
            with self.subTest(key=key):
                self.assertEqual(returned[0].get(key), landed[0].get(key))

    def test_a_worktree_whose_transcript_cannot_be_read_still_lands_and_names_the_unit_unpriced(
            self) -> None:
        self._stage("src/a.py", "A = 2\n")
        self._hand_in()
        r = self._land(A)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertEqual("A = 2\n", (self.root / "src/a.py").read_text(encoding="utf-8"))
        self.assertEqual([], self._returns())
        self.assertIn(f"{A}'s return UNPRICED: ", r.stderr)
        self.assertIn(f"agent-{self.AGENT}.jsonl in {self.tx.subagents}", r.stderr)

    def test_a_lane_of_several_units_prices_none_of_them_from_one_transcript(self) -> None:
        self._builder_says(BUILD_1)
        for rel, body in (("src/a.py", "A = 2\n"), (f"changelog.d/{A}.md", "a is two\n"),
                          ("src/b.py", "B = 2\n"), (f"changelog.d/{B}.md", "b is two\n")):
            self._stage(rel, body)
        self._hand_in(units=(A, B), message=f"feat({A}): a and b are two")
        r = self._land(A, B)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        for unit in (A, B):
            with self.subTest(unit=unit):
                self.assertEqual([], self._returns(unit))
                self.assertIn(f"{unit}'s return UNPRICED: --agent was not recorded: one total "
                              f"cannot be split between 2 units", r.stderr)


if __name__ == "__main__":
    unittest.main()
