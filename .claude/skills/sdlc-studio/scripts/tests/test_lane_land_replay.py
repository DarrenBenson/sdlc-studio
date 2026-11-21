"""BG1448: `sprint lane land` refuses a replay conflict before its hooks, and regenerates a page.

The land replays the staged change onto the root's branch before the commit. A replay that
conflicted was undone and the commit run anyway, so the hooks ran their whole course and the
rebase after them refused on the same conflict. And a replay that merged cleanly could still
merge two lanes' regenerated `reference-scripts-surface.md` into drift: both lanes' rows under
one lane's count, which the hook's drift check refuses after its whole run. Every case drives
`sprint.py lane land` through its entry point, on `test_lane_land`'s throwaway repository and
builder worktree; the surface cases copy the shipped `docgen.py` and the modules it reads into
that repository and run it there, under a hook that refuses on its drift check as this
repository's own pre-commit does.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/lanes.py
from __future__ import annotations

import shutil
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import test_lane_land as base  # noqa: E402 - the lane fixture every landing case shares

from lib import drive  # noqa: E402

A = base.A
_git = base._git
SCRIPTS = Path(__file__).resolve().parent.parent
SKILL_REL = ".claude/skills/sdlc-studio"
PAGE = f"{SKILL_REL}/reference-scripts-surface.md"
#: A reference long enough to earn a reading guide and holding none, which `docgen.py
#: reading-guides` would rewrite: no lane stages it.
LONG = f"{SKILL_REL}/reference-long.md"
LONG_TEXT = "# Long\n\n" + "".join(f"## Part {n}\n\n" + "a line\n" * 50 for n in range(9))
#: The shipped generator and the modules it reads, copied into the fixture's skill directory.
DOCGEN_FILES = ("docgen.py", "lib/__init__.py", "lib/sdlc_md.py", "lib/surface.py")
#: A page holding the generation markers, which `docgen.py surface` fills between.
PAGE_SHELL = ("# Command surface\n\nThe table below is GENERATED.\n\n"
              "<!-- BEGIN GENERATED -->\n<!-- END GENERATED -->\n")
#: Refuses a commit whose checkout's surface page drifts from its scripts, as this
#: repository's pre-commit does with `docgen.py surface --check`.
DRIFT_HOOK = """#!/bin/sh
git rev-parse --show-toplevel >> "{log}"
top="$(git rev-parse --show-toplevel)"
out="$("{python}" "$top/{docgen}" surface --check --root "$top" 2>&1)"
case "$out" in
  *" 0 drift item(s)"*) exit 0 ;;
esac
echo "stub pre-commit: surface drift: $out" >&2
exit 1
"""


def _tool(name: str, verb: str) -> str:
    """A script whose parser exposes one verb, which `docgen.py surface` enumerates."""
    return ("import argparse\n\n\ndef build_parser():\n"
            "    p = argparse.ArgumentParser()\n"
            "    sub = p.add_subparsers(dest='cmd')\n"
            f"    sub.add_parser({verb!r})\n"
            "    return p\n")


class LaneLandReplayTests(base._LaneFixture):

    def _conflicting_lane(self) -> tuple[str, str]:
        """Main moves src/a.py after the lane branched, and the lane stages its own src/a.py:
        main's head and the lane's head before the land."""
        moved = self._move_main("src/a.py", "A = 3\n")
        self._stage("src/a.py", "A = 2\n")
        self._hand_in()
        return moved, _git(self.wt, "rev-parse", "HEAD")

    def test_a_replay_conflict_is_refused_before_the_hooks_run(self) -> None:
        """AC1. MUTANTS: the replay's conflict undone and the commit run anyway, as it was (the
        hook runs, and the lane is committed before the rebase refuses); the refusal worded so
        `sprint drive` reads no conflicting file from it."""
        moved, lane_head = self._conflicting_lane()
        r = self._land(A)
        out = r.stdout + r.stderr
        self.assertNotEqual(0, r.returncode, out)
        self.assertEqual(0, self._hook_runs_in_the_worktree(), "the hooks ran before the refusal")
        self.assertIn("Conflicting files: src/a.py. The lane stays", r.stderr)
        self.assertEqual(["src/a.py"], drive._CONFLICT.search(r.stderr).group(1).split(", "))  # noqa: SLF001
        self.assertNotIn("rebase --continue", out, "git's hint to continue an aborted rebase")
        self.assertNotIn("committed", r.stdout)
        # main, the lane's branch and its staged change are as they were, and no rebase is left
        self.assertEqual(moved, _git(self.root, "rev-parse", "HEAD"))
        self.assertEqual(lane_head, _git(self.wt, "rev-parse", "HEAD"))
        self.assertEqual("src/a.py", _git(self.wt, "diff", "--cached", "--name-only"))
        self.assertEqual("A = 2\n", (self.wt / "src/a.py").read_text(encoding="utf-8"))
        for left in ("rebase-merge", "rebase-apply"):
            path = Path(_git(self.wt, "rev-parse", "--path-format=absolute", "--git-path", left))
            self.assertFalse(path.exists(), f"the replay was left mid-rebase: {left}")
        self.assertIn(base.BRANCH, self._branches())
        self.assertEqual([], base.critic.read_self_checks(self.root))

    def test_the_refusal_claims_only_the_commits_hooks_did_not_run(self) -> None:
        """AC1's message against a replay that runs a hook of its own: the rebase picks the
        builder's commit, running `prepare-commit-msg` on it, before it meets the conflict, so
        the refusal says the commit's hooks never ran, not that no hook did. MUTANT: the
        message saying no hook ran, as it did."""
        base._write(self.wt, "src/b.py", "B = 2\n")
        gitutil.git(["add", "--", "src/b.py"], self.wt)
        gitutil.git(["commit", "-q", "-m", "fix: b is two, in the lane"], self.wt)
        before = self._hook_runs_in_the_worktree()  # the builder's own commit ran the stub
        picked = Path(self._tmp.name) / "prepare-commit-msg.log"
        hook = Path(self._tmp.name) / "hooks" / "prepare-commit-msg"
        hook.write_text(f'#!/bin/sh\necho "$1" >> "{picked}"\n', encoding="utf-8")
        hook.chmod(0o755)
        self._conflicting_lane()
        r = self._land(A)
        self.assertNotEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("Conflicting files: src/a.py.", r.stderr)
        self.assertEqual(before, self._hook_runs_in_the_worktree(), "the commit's hooks ran")
        # positive control: the replay itself ran a hook, so "no hook ran" would be false
        self.assertTrue(picked.is_file() and picked.read_text(encoding="utf-8").strip(),
                        "the replay ran no prepare-commit-msg hook")
        self.assertIn("the commit's hooks never ran", r.stderr)
        self.assertNotIn("no hook ran", r.stderr)

    def test_a_replay_that_applies_still_commits_through_the_hooks(self) -> None:
        """AC1's control: main moved a file the lane does not touch, so the replay applies and
        the lane commits through the hooks once and lands. MUTANT: every replay refused."""
        moved = self._move_main("src/b.py", "B = 2\n")
        self._stage("src/a.py", "A = 2\n")
        self._hand_in()
        r = self._land(A)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertEqual(1, self._hook_runs_in_the_worktree())
        self.assertIn("replayed the staged change onto main before the commit", r.stdout)
        self.assertEqual(moved, _git(self.root, "rev-parse", "HEAD^"))
        self.assertEqual(f"feat({A}): a is two", _git(self.root, "log", "-1", "--format=%s"))


class LaneLandSurfaceRegenTests(base._LaneFixture):
    """Two lanes that each regenerated the surface page from the same base: the first has
    landed on main, the second lands on top of it."""

    def setUp(self) -> None:
        super().setUp()
        # the generator's bytecode is no part of either lane, as in any checkout
        base._write(self.root, ".gitignore", "sdlc-studio/.local/\n__pycache__/\n")
        skill = self.root / SKILL_REL / "scripts"
        for rel in DOCGEN_FILES:
            (skill / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SCRIPTS / rel, skill / rel)
        base._write(skill, "mid_tool.py", _tool("mid_tool", "middle"))
        base._write(self.root, PAGE, PAGE_SHELL)
        base._write(self.root, LONG, LONG_TEXT)
        self._docgen(self.root)
        gitutil.git(["add", "-A"], self.root)
        gitutil.git(["commit", "-q", "-m", "chore: the skill and its surface page"], self.root)
        gitutil.git(["merge", "-q", "--ff-only", "main"], self.wt)
        hook = Path(self._tmp.name) / "hooks" / "pre-commit"
        hook.write_text(DRIFT_HOOK.format(log=self.log, python=sys.executable,
                                          docgen=f"{SKILL_REL}/scripts/docgen.py"),
                        encoding="utf-8")

    def _docgen(self, top: Path, *flags: str) -> str:
        done = subprocess.run([sys.executable, str(top / SKILL_REL / "scripts" / "docgen.py"),
                               "surface", *flags, "--root", str(top)],
                              capture_output=True, text=True, timeout=300, check=True,
                              env=self._env())
        return done.stdout

    def _regenerated_with(self, top: Path, name: str, verb: str) -> None:
        """A lane's new verb in `top`, with the page regenerated over it, both staged."""
        base._write(top / SKILL_REL / "scripts", name, _tool(Path(name).stem, verb))
        self._docgen(top)
        gitutil.git(["add", "--", f"{SKILL_REL}/scripts/{name}", PAGE], top)

    def _first_lane_lands_and_second_is_handed_in(self) -> None:
        # the first lane's verb sorts first and the second's last, so the replay's merge of the
        # two pages is clean and keeps one lane's count over both lanes' rows
        self._regenerated_with(self.root, "aa_tool.py", "alpha")
        gitutil.git(["commit", "-q", "-m", "feat: the first lane lands alpha"], self.root)
        self._regenerated_with(self.wt, "zz_tool.py", "omega")
        self._stage("src/a.py", "A = 2\n")
        self._hand_in()

    def test_the_second_lands_with_the_page_regenerated_over_both(self) -> None:
        """AC2. MUTANTS: the page left as the replay merged it, as it was (the hook refuses on
        drift after its run); the page regenerated but not staged again (the commit carries the
        merged page and the hook refuses); a page the lane did not stage, the long reference
        the reading guides rewrite, committed, or left rewritten in the worktree."""
        self._first_lane_lands_and_second_is_handed_in()
        r = self._land(A)
        out = r.stdout + r.stderr
        self.assertEqual(0, r.returncode, out)
        self.assertNotIn("surface drift", out)
        self.assertEqual(1, self._hook_runs_in_the_worktree())
        self.assertIn(f"regenerated {PAGE}", r.stdout)
        page = (self.root / PAGE).read_text(encoding="utf-8")
        self.assertIn("| `aa_tool.py alpha` |", page)
        self.assertIn("| `zz_tool.py omega` |", page)
        self.assertIn("docgen surface: 0 drift item(s)", self._docgen(self.root, "--check"))
        self.assertEqual(page, _git(self.root, "show", f"HEAD:{PAGE}") + "\n",
                         "the commit does not carry the regenerated page")
        self.assertEqual(sorted([f"{SKILL_REL}/scripts/zz_tool.py", PAGE, "src/a.py"]),
                         sorted(_git(self.root, "show", "--name-only", "--format=",
                                     "HEAD").splitlines()))
        self.assertEqual(LONG_TEXT, (self.root / LONG).read_text(encoding="utf-8"))
        self.assertFalse(self.wt.exists(), "the worktree was left, holding a rewritten page")

    def test_a_replay_with_no_generated_page_staged_runs_no_generator(self) -> None:
        """AC2's control: a lane staging no generated page lands as before, and nothing is
        regenerated. MUTANT: every replay regenerates, rewriting a page the lane never staged."""
        self._regenerated_with(self.root, "aa_tool.py", "alpha")
        gitutil.git(["commit", "-q", "-m", "feat: the first lane lands alpha"], self.root)
        self._stage("src/a.py", "A = 2\n")
        self._hand_in()
        r = self._land(A)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertNotIn("regenerated", r.stdout)
        self.assertEqual(["src/a.py"], _git(self.root, "show", "--name-only", "--format=",
                                            "HEAD").splitlines())


if __name__ == "__main__":
    unittest.main()
