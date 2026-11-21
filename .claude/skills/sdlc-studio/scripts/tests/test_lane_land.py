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


def _leftovers(stderr: str) -> str:
    """The leftovers a land's refusal names, exactly as it lists them; empty where none is."""
    hit = re.search(r"no commit of the lane carries: (.*?)\. Nothing was committed", stderr)
    return hit.group(1) if hit else ""


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
               "<!-- role: qa -->\n# Sam - QA amigo\n\ncharter\n\n## Lens\n\nx\n\n## Pushes Back When\n\nx\n\n## Shadow\n\nx\n")
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
        """Judged before the commit, so it is refused with nothing landed and the worktree kept
        (`test_self_check_before_commit` holds the rest of that criterion)."""
        main = _git(self.root, "rev-parse", "HEAD")
        self._stage("src/a.py", "A = 2\n")
        self._hand_in()
        # no claim from the changelog fragment A's Affects declares: `critic.py` refuses it
        _write(self.wt, f"sdlc-studio/.local/lane/{A}-claims.json", json.dumps(
            [{"surface": "commit message", "claim": "a is two", "ruling": "TRUE"}]))
        r = self._land(A)
        self.assertEqual(2, r.returncode, r.stdout + r.stderr)
        self.assertIn(f"{A}'s self-check", r.stderr)
        self.assertIn(f"no claim from the changelog.d/{A}.md", r.stderr,
                      "the critic's own reason was not carried")
        self.assertEqual(main, _git(self.root, "rev-parse", "HEAD"))
        self.assertTrue(self.wt.is_dir())
        self.assertEqual([], critic.read_self_checks(self.root))
        self.assertFalse((self.root / f"sdlc-studio/.local/briefs/{A}-qa.txt").exists())

    # -- what a builder leaves in its worktree beside the staged change ------------------------

    def _ledger_on_main(self) -> Path:
        """The self-check ledger committed on main and brought into the worktree, so the row a
        builder's own `self-check record` appends leaves it modified and unstaged."""
        ledger = critic.self_checks_path(self.root)
        _write(self.root, ledger.relative_to(self.root).as_posix(), "# Author self-checks\n")
        gitutil.git(["add", "--", str(ledger)], self.root)
        gitutil.git(["commit", "-q", "-m", "chore: the self-check ledger"], self.root)
        gitutil.git(["merge", "-q", "--ff-only", "main"], self.wt)
        return critic.self_checks_path(self.wt)

    def test_a_self_check_ledger_left_unstaged_does_not_stop_the_land(self) -> None:
        """BG1470 AC1. The builder recorded its self-check in the worktree, leaving the ledger
        modified and its mutants file new, neither staged: both are put back, since the land
        records the self-check on the root, and the lane commits, rebases and fast-forwards in
        one pass. MUTANTS: the ledger left in place (the rebase after the commit refuses over
        it); the mutants file left in place (the worktree cannot be removed)."""
        ledger = self._ledger_on_main()
        with ledger.open("a", encoding="utf-8") as fh:
            fh.write("| US0101 | the builder's own row |\n")
        mutants = critic.author_mutants_path(self.wt, A)
        _write(self.wt, mutants.relative_to(self.wt).as_posix(), "[]\n")
        self._stage("src/a.py", "A = 2\n")
        self._hand_in()
        r = self._land(A)
        out = r.stdout + r.stderr
        self.assertEqual(0, r.returncode, out)
        self.assertEqual(1, self._hook_runs_in_the_worktree(), out)
        self.assertNotIn("cannot rebase", out)
        for rel in (ledger, mutants):
            self.assertIn(f"put back {rel.relative_to(self.wt).as_posix()}", r.stdout)
        self.assertEqual(f"feat({A}): a is two", _git(self.root, "log", "-1", "--format=%s"))
        self.assertEqual("A = 2\n", (self.root / "src/a.py").read_text(encoding="utf-8"))
        self.assertFalse(self.wt.exists(), "the worktree was not removed")
        self.assertEqual([A], [row["unit"] for row in critic.read_self_checks(self.root)])
        self.assertNotIn("the builder's own row",
                         _git(self.root, "show", f"HEAD:{ledger.relative_to(self.wt).as_posix()}"))

    def test_a_leftover_file_is_refused_before_the_hooks_run(self) -> None:
        """BG1470 AC2. An untracked file and an unstaged edit outside the hand-in path: the land
        refuses before the commit, naming both, and neither is discarded. MUTANTS: the leftovers
        left for the rebase after the hooks to refuse, as it was; the untracked file not looked
        for; a leftover silently discarded."""
        main, lane_head = _git(self.root, "rev-parse", "HEAD"), _git(self.wt, "rev-parse", "HEAD")
        self._stage("src/a.py", "A = 2\n")
        self._hand_in()
        _write(self.wt, "src/stray.py", "S = 1\n")
        _write(self.wt, "src/b.py", "B = 9\n")
        r = self._land(A)
        self.assertEqual(2, r.returncode, r.stdout + r.stderr)
        for named in ("src/stray.py (untracked)", "src/b.py (unstaged)", str(self.wt)):
            self.assertIn(named, r.stderr)
        self.assertEqual(0, self._hook_runs_in_the_worktree(), "the hooks ran before the refusal")
        self.assertEqual(main, _git(self.root, "rev-parse", "HEAD"))
        self.assertEqual(lane_head, _git(self.wt, "rev-parse", "HEAD"), "the lane was committed")
        self.assertEqual("src/a.py", _git(self.wt, "diff", "--cached", "--name-only"))
        self.assertEqual("S = 1\n", (self.wt / "src/stray.py").read_text(encoding="utf-8"))
        self.assertEqual("B = 9\n", (self.wt / "src/b.py").read_text(encoding="utf-8"))
        self.assertEqual([], critic.read_self_checks(self.root))

    def _land_refused(self) -> str:
        """Land the lane the case handed in beside its leftover, check `lane land` refused it
        from its preflight before anything moved (exit 2, no traceback, no hook run, main where
        it was, no hand-in copied), and return the leftovers the refusal names."""
        main = _git(self.root, "rev-parse", "HEAD")
        r = self._land(A)
        out = r.stdout + r.stderr
        self.assertEqual(2, r.returncode, out)
        self.assertNotIn("Traceback", out)
        self.assertEqual(0, self._hook_runs_in_the_worktree(), "the hooks ran before the refusal")
        self.assertEqual(main, _git(self.root, "rev-parse", "HEAD"))
        self.assertFalse((self.root / LANE / "landed" / self.wt.name).exists(),
                         "the hand-in was copied before the refusal")
        return _leftovers(r.stderr)

    def test_an_unstaged_deletion_is_refused_before_the_hooks_run(self) -> None:
        """BG1470 AC2 for a tracked file deleted and not staged, which `git status` marks D in
        its work-tree column: refused by name before any hook, and left deleted. MUTANT: only a
        modification counted as unstaged (the hook runs, the lane commits, and the rebase after
        it refuses over the deletion)."""
        self._stage("src/a.py", "A = 2\n")
        self._hand_in()
        (self.wt / "src/b.py").unlink()
        self.assertEqual("src/b.py (unstaged)", self._land_refused())
        self.assertFalse((self.wt / "src/b.py").exists(), "the deletion was discarded")

    def test_a_name_that_is_not_utf8_is_named_rather_than_stopping_the_land(self) -> None:
        """BG1470 AC2 for an untracked file whose name holds the byte 0xff: the refusal names it
        before any hook. `os.fsdecode` reads the byte as a surrogate escape, which stderr's
        backslashreplace handler writes out, so the refusal reads `src/stray-\\udcff.py
        (untracked)`; the pattern checks that the name is there, not how its byte is spelt.
        MUTANT: the path decoded as strict UTF-8 (the land stops on a UnicodeDecodeError
        traceback, exit 1)."""
        self._stage("src/a.py", "A = 2\n")
        self._hand_in()
        try:
            (self.wt / os.fsdecode(b"src/stray-\xff.py")).write_text("S = 1\n", encoding="utf-8")
        except OSError as exc:  # a filesystem that takes only UTF-8 names, as macOS's does
            self.skipTest(f"this filesystem refuses a name that is not UTF-8: {exc}")
        self.assertRegex(self._land_refused(), r"^src/stray-\S+\.py \(untracked\)$")

    def test_a_clean_lane_still_lands(self) -> None:
        """BG1470 AC3. The staged change, the hand-in and the unstaged verify edit to the unit's
        own story: it lands as before. MUTANT: the story's verify edit refused rather than
        discarded; the hand-in's own exemption is `test_a_hand_in_git_can_see_is_no_leftover`."""
        self._stage("src/a.py", "A = 2\n")
        self._hand_in()
        story = self.wt / f"sdlc-studio/stories/{A}-lane.md"
        story.write_text(story.read_text(encoding="utf-8") + "\n<!-- verified -->\n",
                         encoding="utf-8")
        r = self._land(A)
        out = r.stdout + r.stderr
        self.assertEqual(0, r.returncode, out)
        self.assertIn(f"discarded sdlc-studio/stories/{A}-lane.md", r.stdout)
        self.assertEqual(f"feat({A}): a is two", _git(self.root, "log", "-1", "--format=%s"))
        self.assertEqual(["src/a.py"], _git(self.root, "show", "--name-only", "--format=",
                                            "HEAD").splitlines())

    def test_a_leftover_made_after_a_refused_commit_is_refused_on_the_resume(self) -> None:
        """BG1470 AC2 on a resume, which runs no preflight: the hook refused the commit, the
        builder repaired the stage and left a file beside it, and `--resume` refuses it by name
        before the hook runs again. MUTANT: the commit step's own check dropped (the hook runs a
        second time and the lane lands with the file still in its worktree)."""
        self._stage("src/refuse.py", "X = 1\n")
        self._hand_in()
        r = self._land(A)
        self.assertEqual(1, r.returncode, r.stdout + r.stderr)
        self.assertIn(REFUSAL, r.stderr)
        main = _git(self.root, "rev-parse", "HEAD")
        gitutil.git(["rm", "-q", "-f", "--", "src/refuse.py"], self.wt)
        self._stage("src/a.py", "A = 2\n")
        _write(self.wt, "src/stray.py", "S = 1\n")
        r = subprocess.run(
            [sys.executable, "-B", str(SPRINT), "lane", "land", "--worktree", str(self.wt),
             "--units", A, "--root", str(self.root), "--resume"],
            capture_output=True, text=True, timeout=600, cwd=str(self.root),
            env=self._env(), check=False)
        self.assertEqual(1, r.returncode, r.stdout + r.stderr)
        self.assertIn("src/stray.py (untracked)", r.stderr)
        self.assertEqual(1, self._hook_runs_in_the_worktree(), "the hook ran on the resume")
        self.assertEqual(main, _git(self.root, "rev-parse", "HEAD"))
        self.assertEqual("src/a.py", _git(self.wt, "diff", "--cached", "--name-only"))
        self.assertEqual("S = 1\n", (self.wt / "src/stray.py").read_text(encoding="utf-8"))

    def test_a_staged_rename_is_no_leftover(self) -> None:
        """`git status` names a staged rename's source after its target: that source is no path
        of the worktree's own, so only the untracked file beside it is loose. MUTANT: the source
        read as an entry of its own."""
        gitutil.git(["mv", "--", "src/b.py", "src/b2.py"], self.wt)
        _write(self.wt, "src/stray.py", "S = 1\n")
        self.assertEqual({"src/stray.py": "untracked"}, lanes._loose(self.wt))  # noqa: SLF001

    def test_a_rename_made_in_the_work_tree_is_named_by_its_own_paths(self) -> None:
        """A tracked file moved and its new path added with `git add -N`: `git status` reads that
        as a rename in its work-tree column and names the source after the target. The refusal
        names both, the source since it is deleted there, and a source whose name begins with C
        or R is not misread as an entry of its own, so the untracked file after it is still
        named. MUTANTS: the source skipped only after a rename in the index column (`/b.py` and
        `NGES.txt` named, `src/stray.py` missed); the source not named."""
        _write(self.root, "CHANGES.txt", "the changes\n")
        gitutil.git(["add", "--", "CHANGES.txt"], self.root)
        gitutil.git(["commit", "-q", "-m", "chore: a file whose name begins with C"], self.root)
        gitutil.git(["merge", "-q", "--ff-only", "main"], self.wt)
        self._stage("src/a.py", "A = 2\n")
        self._hand_in()
        (self.wt / "src/b.py").rename(self.wt / "src/b3.py")
        gitutil.git(["add", "-N", "--", "src/b3.py"], self.wt)
        with self.subTest("src/b.py moved to src/b3.py"):
            self.assertEqual("src/b.py (unstaged), src/b3.py (unstaged)", self._land_refused())
        gitutil.git(["reset", "-q", "--", "src/b3.py"], self.wt)
        (self.wt / "src/b3.py").rename(self.wt / "src/b.py")
        (self.wt / "CHANGES.txt").rename(self.wt / "tests/docs.txt")
        gitutil.git(["add", "-N", "--", "tests/docs.txt"], self.wt)
        _write(self.wt, "src/stray.py", "S = 1\n")
        with self.subTest("CHANGES.txt moved to tests/docs.txt, beside an untracked file"):
            self.assertEqual("CHANGES.txt (unstaged), src/stray.py (untracked), "
                             "tests/docs.txt (unstaged)", self._land_refused())

    def test_a_copy_names_its_source_only_where_it_changed(self) -> None:
        """Where `status.renames` finds copies, `git status` names a copy's source after it in
        either column, and lists a source that was edited, as both sources here are, again on its
        own: a staged copy leaves nothing loose, and a copy in the work tree is loose beside its
        edited source, with no path misread from the source's name. MUTANTS: the source skipped
        only after a copy in the work-tree column (`/b.py` named), or only after one in the index
        column (`/a.py` named)."""
        gitutil.git(["config", "status.renames", "copies"], self.root)
        self._stage("src/b.py", "B = 2\n")
        self._stage("src/b5.py", "B = 1\n")
        _write(self.wt, "src/a.py", "A = 9\n")
        _write(self.wt, "src/a4.py", "A = 1\n")
        gitutil.git(["add", "-N", "--", "src/a4.py"], self.wt)
        self.assertEqual({"src/a.py": "unstaged", "src/a4.py": "unstaged"},
                         lanes._loose(self.wt))  # noqa: SLF001

    def test_a_hand_in_git_can_see_is_no_leftover(self) -> None:
        """BG1470 AC3 where the project ignores nothing, so the hand-in files are untracked in
        the worktree rather than ignored: the check for leftovers passes over them, and names
        only the stray file beside them. MUTANT: the hand-in counted as a leftover."""
        _write(self.root, ".gitignore", "")
        gitutil.git(["add", "--", ".gitignore"], self.root)
        gitutil.git(["commit", "-q", "-m", "chore: nothing ignored"], self.root)
        gitutil.git(["merge", "-q", "--ff-only", "main"], self.wt)
        self._stage("src/a.py", "A = 2\n")
        self._hand_in()
        self.assertIn(f"{LANE}/commit-msg.txt", lanes._loose(self.wt))  # noqa: SLF001
        lane = lanes._Lane(BRANCH, self.root / LANE / "landed" / BRANCH, "main",  # noqa: SLF001
                           top=self.wt, units=[A])
        lanes._refuse_leftovers([lane], 2)  # noqa: SLF001
        _write(self.wt, "src/stray.py", "S = 1\n")
        with self.assertRaises(lanes.LandError) as refused:
            lanes._refuse_leftovers([lane], 2)  # noqa: SLF001
        self.assertIn("src/stray.py (untracked)", str(refused.exception))
        self.assertNotIn(LANE, str(refused.exception))

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
        """A file no commit carries, made after the land's check for leftovers, which refuses
        one the builder left (`test_a_leftover_file_is_refused_before_the_hooks_run`): here the
        commit's own hook leaves it, so the lane lands and its worktree cannot be removed."""
        hook = Path(self._tmp.name) / "hooks" / "pre-commit"
        hook.write_text(HOOK.format(log=self.log, refusal=REFUSAL).replace(
            "exit 0\n", "echo 'S = 1' > src/stray.py\nexit 0\n"), encoding="utf-8")
        self._stage("src/a.py", "A = 2\n")
        self._hand_in()
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
        # refused before the commit: no hook ran, and the lane holds its staged change and no
        # commit of its own
        self.assertEqual(0, self._hook_runs_in_the_worktree())
        self.assertEqual([], _git(self.wt, "log", "--format=%s", "main..HEAD").splitlines())
        self.assertEqual("src/a.py", _git(self.wt, "diff", "--cached", "--name-only"))

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


class _PricedFixture(_LaneFixture):
    """The lane fixture with an open run and a temporary harness store, never the operator's:
    HOME, CLAUDE_CONFIG_DIR and XDG_DATA_HOME point into it, and a builder's transcript is
    priced against the fixture store's own weight table (`test_meter_reads_true`)."""

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

    def _builder_says(self, *usages: dict, agent: str | None = None,
                      wt: Path | None = None) -> None:
        """The builder `agent` (this fixture's own by default) spends `usages` in `wt`."""
        lines = [ln for n, usage in enumerate(usages)
                 for ln in self.tx._records(f"msg_build_{agent or self.AGENT}_{n}", usage, None,
                                            str(wt or self.wt))]
        meter._Transcripts._append(self.tx.subagents / f"agent-{agent or self.AGENT}.jsonl",
                                   lines)

    def _returns(self, unit: str = A) -> list[dict]:
        return [r for r in run_state.read(self.root).get(run_state.DELEGATED) or []
                if r.get("unit") == unit]


class LandPricesTheBuilderTests(_PricedFixture):
    """BG1330. `lane land` read the builder's id off its `agent-<id>` worktree only as the
    self-check's author and recorded no return, so a unit no one returned by hand with `lane
    return --agent` read NOT MEASURED. Each case lands through `sprint.py lane land` with HOME,
    CLAUDE_CONFIG_DIR and XDG_DATA_HOME on a temporary harness store, never the operator's, and
    prices against the fixture store's own weight table (`test_meter_reads_true`)."""

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

    def test_a_lane_of_several_units_splits_its_one_transcript_by_points(self) -> None:
        """One builder's transcript for a lane of two units of 2 points each is split between
        them by their Points: each unit is priced with its half, the halves add up to the
        whole, and the line says it was split. MUTANT: the old refusal, so neither is priced."""
        self._builder_says(BUILD_1)
        for rel, body in (("src/a.py", "A = 2\n"), (f"changelog.d/{A}.md", "a is two\n"),
                          ("src/b.py", "B = 2\n"), (f"changelog.d/{B}.md", "b is two\n")):
            self._stage(rel, body)
        self._hand_in(units=(A, B), message=f"feat({A}): a and b are two")
        r = self._land(A, B)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        parts = meter._sum(BUILD_1)
        shares = {unit: self._returns(unit) for unit in (A, B)}
        for unit, recs in shares.items():
            with self.subTest(unit=unit):
                self.assertEqual(1, len(recs), r.stdout + r.stderr)
                self.assertEqual({"by": "points", "points": 2, "of": 4, "units": 2,
                                  "tokens": meter._tokens(parts)}, recs[0][run_state.APPORTIONED])
                self.assertIn(f"{unit}'s return priced from {self.WORKTREE}'s transcript: "
                              f"{recs[0]['tokens']:,} tokens, {recs[0]['priced']:,} "
                              f"{run_state.PRICED_LABEL}, split by points (2 of 4)", r.stdout)
        for key, whole in (("tokens", meter._tokens(parts)), ("priced", meter._priced(parts))):
            self.assertEqual(whole, sum(recs[0][key] for recs in shares.values()), key)
        self.assertNotIn("UNPRICED", r.stderr)



class LandSeveralWorktreesTests(_PricedFixture):
    """`lane land` given several builders' worktrees of one root lands them as one commit, so the
    commit hook is paid once for the lot, while each unit keeps what is its own: its hand-in, its
    self-check, its QA brief and its price. The second builder works in `agent-<id>` beside the
    first; each staged its unit's Affects and handed in its own message and self-check files."""

    OTHER = "f6e5d4c3b2a1"

    def setUp(self) -> None:
        super().setUp()
        self.wt2 = Path(self._tmp.name).resolve() / f"agent-{self.OTHER}"
        gitutil.git(["worktree", "add", "-q", "-b", "lane-us0102", str(self.wt2), "main"],
                    self.root)

    def _two_lanes(self) -> None:
        """Builder one stages A in the first worktree; builder two stages B in the second."""
        for rel, body in (("src/a.py", "A = 2\n"), (f"changelog.d/{A}.md", "a is two\n")):
            self._stage(rel, body)
        self._hand_in(units=(A,), message=f"feat({A}): a is two")
        _write(self.wt, f"{LANE}/HANDOFF.md", "builder one\n")
        first, self.wt = self.wt, self.wt2
        try:
            for rel, body in (("src/b.py", "B = 2\n"), (f"changelog.d/{B}.md", "b is two\n")):
                self._stage(rel, body)
            self._hand_in(units=(B,), message=f"feat({B}): b is two\n\nBuilder two's body.")
            _write(self.wt, f"{LANE}/HANDOFF.md", "builder two\n")
        finally:
            self.wt = first

    def _land_both(self, *worktrees: Path, resume: bool = False) -> subprocess.CompletedProcess:
        named = [arg for wt in worktrees or (self.wt, self.wt2) for arg in ("--worktree", str(wt))]
        return self._sprint("lane", "land", *named, "--units", A, B,
                            *(["--resume"] if resume else []))

    def _sprint(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-B", str(SPRINT), *args, "--root", str(self.root)],
            capture_output=True, text=True, timeout=600, cwd=str(self.root), env=self._env(),
            check=False)

    def _hook_runs(self) -> int:
        """The commits the hook judged in either worktree; the fixture's own on main are not."""
        lines = self.log.read_text(encoding="utf-8").splitlines() if self.log.exists() else []
        return sum(lines.count(str(wt)) for wt in (self.wt, self.wt2))

    def _staged(self, wt: Path) -> list[str]:
        return sorted(_git(wt, "diff", "--cached", "--name-only").splitlines())

    def test_two_worktrees_land_as_one_commit_with_a_refs_trailer_each(self) -> None:
        moved = self._move_main("README.md", "main moved on\n")
        self._two_lanes()
        r = self._land_both()
        out = r.stdout + r.stderr
        self.assertEqual(0, r.returncode, out)
        self.assertEqual("1", _git(self.root, "rev-list", "--count", f"{moved}..HEAD"),
                         "the two worktrees did not land as exactly one commit")
        self.assertEqual(moved, _git(self.root, "rev-parse", "HEAD^"))
        self.assertEqual(sorted(["src/a.py", f"changelog.d/{A}.md", "src/b.py",
                                 f"changelog.d/{B}.md"]),
                         sorted(_git(self.root, "show", "--format=", "--name-only",
                                     "HEAD").splitlines()))
        self.assertEqual(1, self._hook_runs(), "the commit hook did not run exactly once")
        self.assertEqual([A, B], _git(self.root, "log", "-1",
                                      "--format=%(trailers:key=Refs,valueonly)").splitlines())
        self.assertEqual(f"feat({A}, {B}): a is two", _git(self.root, "log", "-1", "--format=%s"))
        self.assertIn("Builder two's body.", _git(self.root, "log", "-1", "--format=%b"))
        for rel, body in (("src/a.py", "A = 2\n"), ("src/b.py", "B = 2\n"),
                          ("README.md", "main moved on\n")):
            self.assertEqual(body, (self.root / rel).read_text(encoding="utf-8"), rel)
        for wt in (self.wt, self.wt2):
            self.assertFalse(wt.exists(), f"{wt.name} was not removed")
        self.assertEqual(["main"], self._branches())

    def test_each_unit_keeps_its_own_hand_in_and_price(self) -> None:
        self._builder_says(BUILD_1)
        self._builder_says(BUILD_2, agent=self.OTHER, wt=self.wt2)
        self._two_lanes()
        r = self._land_both()
        out = r.stdout + r.stderr
        self.assertEqual(0, r.returncode, out)
        landed = self.root / LANE / "landed"
        rows = {row["unit"]: row for row in critic.read_self_checks(self.root)}
        fingerprints = set()
        for unit, wt, says, other in ((A, self.wt, BUILD_1, B), (B, self.wt2, BUILD_2, A)):
            with self.subTest(unit=unit):
                kept = landed / wt.name
                self.assertEqual("builder one\n" if unit == A else "builder two\n",
                                 (kept / "HANDOFF.md").read_text(encoding="utf-8"),
                                 "one worktree's hand-in overwrote the other's")
                self.assertTrue((kept / f"{unit}-claims.json").is_file())
                self.assertFalse((kept / f"{other}-claims.json").exists())
                self.assertEqual(wt.name, rows[unit]["author"],
                                 "the self-check was not recorded from the unit's own worktree")
                brief = self.root / lanes.BRIEFS / f"{unit}-qa.txt"
                self.assertTrue(brief.is_file(), f"no QA brief written for {unit}")
                fingerprints.add(critic.brief_fingerprint(brief.read_text(encoding="utf-8")))
                recs = self._returns(unit)
                self.assertEqual(1, len(recs), out)
                parts = meter._sum(says)
                self.assertEqual((meter._tokens(parts), meter._priced(parts),
                                  str(self.tx.subagents / f"{wt.name}.jsonl")),
                                 (recs[0]["tokens"], recs[0]["priced"], recs[0]["transcript"]),
                                 "the unit was not priced from its own builder's transcript")
                self.assertNotIn(run_state.APPORTIONED, recs[0])
                self.assertIn(f"{unit}'s return priced from {wt.name}'s transcript", r.stdout)
        self.assertEqual(2, len(fingerprints), "the two units share one QA brief")

    def test_a_leftover_in_a_later_worktree_is_refused_before_anything_moves(self) -> None:
        """BG1470 AC2 for a landing of several worktrees: an untracked file in the second is
        refused by the preflight, exit 2, before either hand-in is copied or a land record is
        written. MUTANT: the several-worktree preflight check dropped (the commit step's own check
        refuses it with exit 1, after both hand-ins are copied and the landing recorded)."""
        head = _git(self.root, "rev-parse", "HEAD")
        self._two_lanes()
        _write(self.wt2, "src/stray.py", "S = 1\n")
        r = self._land_both()
        out = r.stdout + r.stderr
        self.assertEqual(2, r.returncode, out)
        self.assertEqual("src/stray.py (untracked)", _leftovers(r.stderr))
        self.assertIn(str(self.wt2), r.stderr)
        self.assertEqual(0, self._hook_runs(), out)
        self.assertEqual(head, _git(self.root, "rev-parse", "HEAD"))
        for wt in (self.wt, self.wt2):
            self.assertFalse((self.root / LANE / "landed" / wt.name).exists(),
                             f"{wt.name}'s hand-in was copied before the refusal")
        self.assertFalse(lanes._record_file(self.root, self.wt.name).exists(),  # noqa: SLF001
                         "the landing was recorded before the refusal")
        self.assertEqual("S = 1\n", (self.wt2 / "src/stray.py").read_text(encoding="utf-8"))

    def test_a_conflict_or_a_refused_commit_lands_nothing(self) -> None:
        head = _git(self.root, "rev-parse", "HEAD")
        self._two_lanes()
        rival = "A = 3\n"
        _write(self.wt2, "src/a.py", rival)
        gitutil.git(["add", "--", "src/a.py"], self.wt2)
        staged = {wt: self._staged(wt) for wt in (self.wt, self.wt2)}

        def lands_nothing(r: subprocess.CompletedProcess, hooks: int) -> None:
            out = r.stdout + r.stderr
            self.assertNotEqual(0, r.returncode, out)
            self.assertEqual(head, _git(self.root, "rev-parse", "HEAD"), "a half landing")
            self.assertEqual(hooks, self._hook_runs(), out)
            for wt in (self.wt, self.wt2):
                self.assertTrue(wt.is_dir(), f"{wt.name} was removed")
                self.assertEqual(staged[wt], self._staged(wt), f"{wt.name}'s staged change moved")
            self.assertEqual([], critic.read_self_checks(self.root))

        with self.subTest("the same file staged with different content in both"):
            r = self._land_both()
            lands_nothing(r, 0)
            self.assertEqual(2, r.returncode, "the conflict was not refused before anything moved")
            for named in ("src/a.py", str(self.wt), str(self.wt2)):
                self.assertIn(named, r.stderr)
            self.assertEqual(rival, (self.wt2 / "src/a.py").read_text(encoding="utf-8"))

        gitutil.git(["reset", "-q", "--", "src/a.py"], self.wt2)
        gitutil.git(["checkout", "--", "src/a.py"], self.wt2)
        self._stage_in(self.wt2, "src/refuse.py", "X = 1\n")
        staged = {wt: self._staged(wt) for wt in (self.wt, self.wt2)}
        with self.subTest("a commit the hook refuses"):
            r = self._land_both()
            lands_nothing(r, 1)
            self.assertIn(REFUSAL, r.stderr, "the hook's own refusal was not shown")
            self.assertNotEqual("B = 2\n", (self.wt / "src/b.py").read_text(encoding="utf-8"),
                                "the first worktree still holds the second's change")
            # the unit whose file the hook refused is the one a repair brief must reach
            for unit in (B, A):
                repair = self._sprint("lane", "brief", "--units", unit, "--repair")
                self.assertEqual(0, repair.returncode,
                                 f"{unit} has no repair route: {repair.stdout + repair.stderr}")
                self.assertIn(REFUSAL, repair.stdout,
                              f"{unit}'s repair brief does not quote the hook's refusal")

        kept = self.root / LANE / "landed" / self.wt.name / "kept.marker"
        _write(kept.parent, kept.name, "an earlier landing's\n")
        with self.subTest("one worktree named twice"):
            r = self._land_both(self.wt, self.wt / "src")
            lands_nothing(r, 1)
            self.assertEqual(2, r.returncode, r.stderr)
            self.assertIn("named twice", r.stderr)
            self.assertTrue(kept.is_file(), "the refusal came after the hand-in was copied")

        # the second builder commits its code and leaves only its changelog staged
        gitutil.git(["rm", "-q", "--cached", "--", "src/refuse.py"], self.wt2)
        (self.wt2 / "src/refuse.py").unlink()
        gitutil.git(["commit", "-q", "--no-verify", "-m", "b is two", "--", "src/b.py"],
                    self.wt2)
        ahead = _git(self.wt2, "rev-parse", "HEAD")
        staged = {wt: self._staged(wt) for wt in (self.wt, self.wt2)}
        self.assertEqual([f"changelog.d/{B}.md"], staged[self.wt2])
        for how, resume in (("landed", False), ("resumed", True)):
            with self.subTest(f"a later worktree holding a commit ahead of main, {how}"):
                r = self._land_both(resume=resume)
                lands_nothing(r, 1)
                self.assertIn(str(self.wt2), r.stderr)
                self.assertIn("ahead of main", r.stderr)
                self.assertEqual(ahead, _git(self.wt2, "rev-parse", "HEAD"),
                                 "the commit ahead was moved")
                self.assertEqual("B = 1\n", (self.root / "src/b.py").read_text(encoding="utf-8"))
                if not resume:
                    self.assertEqual(2, r.returncode, "not refused before anything moved")
                    self.assertTrue(kept.is_file(), "the refusal came after the hand-in was copied")

        gitutil.git(["reset", "-q", "--soft", "HEAD~1"], self.wt2)
        with self.subTest("the resumed landing commits, and leaves no refusal to repair"):
            r = self._land_both(resume=True)
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            self.assertEqual("B = 2\n", (self.root / "src/b.py").read_text(encoding="utf-8"))
            for unit in (A, B):
                repair = self._sprint("lane", "brief", "--units", unit, "--repair")
                self.assertEqual(2, repair.returncode,
                                 f"{unit}'s landed change still reads as refused: {repair.stdout}")

    def _stage_in(self, wt: Path, rel: str, body: str) -> None:
        _write(wt, rel, body)
        gitutil.git(["add", "--", rel], wt)


if __name__ == "__main__":
    unittest.main()
