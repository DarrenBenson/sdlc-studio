"""BG1448: `sprint lane land` refuses a replay conflict before its hooks, and regenerates a page.

The land replays the staged change onto the root's branch before the commit. A replay that
conflicted was undone and the commit run anyway, so the hooks ran their whole course and the
rebase after them refused on the same conflict. And a replay that merged cleanly could still
merge two lanes' regenerated `reference-scripts-surface.md` into drift: both lanes' rows under
one lane's count, which the hook's drift check refuses after its whole run. Every landing case
drives `sprint.py lane land` through its entry point, on `test_lane_land`'s throwaway repository
and builder worktree; the surface cases copy the shipped `docgen.py` and the modules it reads into
that repository and run it there, under a hook that refuses on its drift check as this
repository's own pre-commit does. The reference index and reference page cases, and a generator
that fails or is absent, land against a stand-in `docgen.py` that logs each verb it is given; a
generator that overruns runs `_regenerate` in process with its bound cut to five seconds, and the
verbs each staged path selects are read from `_generated_verbs` itself.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/lanes.py
from __future__ import annotations

import contextlib
import io
import shutil
import subprocess
import sys
import unittest
import unittest.mock
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


#: The reference index and two reference pages a lane may stage, under the skill directory.
INDEX = f"{SKILL_REL}/help/references.md"
MINE = f"{SKILL_REL}/reference-mine.md"
OTHER = f"{SKILL_REL}/reference-other.md"
#: A stand-in `docgen.py`: it logs each verb it is run with and appends a line naming the verb to
#: each page that verb generates (every top-level reference page for `reading-guides`, as the
#: shipped one rewrites every long reference), or, as `acts` says for the verb, exits 3 having
#: printed why, or sleeps past any bound.
STUB_DOCGEN = """import sys, time
from pathlib import Path
verb = sys.argv[1]
root = Path(sys.argv[sys.argv.index("--root") + 1])
with open({log!r}, "a", encoding="utf-8") as fh:
    fh.write(verb + "\\n")
act = {acts!r}.get(verb, "rewrite")
if act == "fail":
    print("docgen stub: " + verb + " could not read its pages")
    sys.exit(3)
if act == "hang":
    time.sleep(120)
skill = root / {skill!r}
pages = {{"surface": [skill / "reference-scripts-surface.md"],
          "references": [skill / "help" / "references.md"],
          "reading-guides": sorted(skill.glob("reference-*.md"))}}[verb]
for page in pages:
    if page.is_file():
        page.write_text(page.read_text(encoding="utf-8") + "regenerated by " + verb + "\\n",
                        encoding="utf-8")
"""


class LaneLandRegenVerbTests(base._LaneFixture):
    """Which generator runs over a replayed change, and what a run that fails or overruns does:
    the land is driven against a stand-in `docgen.py` committed in the fixture, so each verb's
    run is seen in its log and in the pages the commit carries."""

    def _skill(self, acts: dict | None = None, docgen: bool = True) -> Path:
        """The reference index and two reference pages on main, with the stand-in generator
        unless `docgen` is false, the lane brought up to them, and main moved on a file the
        lane does not touch, so the land replays. The generator's log."""
        log = Path(self._tmp.name) / "docgen.log"
        if docgen:
            base._write(self.root, f"{SKILL_REL}/scripts/docgen.py", STUB_DOCGEN.format(
                log=str(log), acts=acts or {}, skill=SKILL_REL))
        for rel, title in ((INDEX, "References"), (MINE, "Mine"), (OTHER, "Other")):
            base._write(self.root, rel, f"# {title}\n")
        gitutil.git(["add", "-A"], self.root)
        gitutil.git(["commit", "-q", "-m", "chore: the skill's pages"], self.root)
        gitutil.git(["merge", "-q", "--ff-only", "main"], self.wt)
        self._move_main("src/b.py", "B = 2\n")
        return log

    def _stage_pages(self, *rels: str) -> None:
        for rel in rels:
            self._stage(rel, (self.wt / rel).read_text(encoding="utf-8") + "the lane's line\n")
        self._stage("src/a.py", "A = 2\n")
        self._hand_in()

    def _landed(self, rel: str) -> str:
        return _git(self.root, "show", f"HEAD:{rel}") + "\n"

    def test_the_verbs_follow_the_generated_pages_staged(self) -> None:
        """Each branch alone, in the order the verbs run. MUTANTS: the `references` branch or
        the `reading-guides` branch dropped; a reference page read anywhere in the tree, below
        the skill directory's top, or with more after its `.md`; the skill directory's dots
        read as any character; a script or `help/` page taken for the page it feeds."""
        s = f"{SKILL_REL}/"
        for staged, verbs in (
                ([f"{s}reference-scripts-surface.md"], ["surface", "reading-guides"]),
                ([INDEX], ["references"]),
                ([MINE], ["reading-guides"]),
                ([MINE, INDEX, f"{s}reference-scripts-surface.md"],
                 ["surface", "references", "reading-guides"]),
                ([f"{s}scripts/sprint.py", f"{s}help/sprint.md"], []),
                ([f"{s}templates/reference-x.md", f"{s}reference-x/notes.md",
                  f"{s}reference-x.md.orig"], []),
                (["docs/reference-x.md", "xclaude/skills/sdlc-studio/reference-x.md"], []),
                ([], [])):
            with self.subTest(staged=staged):
                self.assertEqual(verbs, base.lanes._generated_verbs(staged))  # noqa: SLF001

    def test_the_index_and_a_reference_page_are_regenerated_and_staged(self) -> None:
        """AC2 for the other two generated pages. MUTANTS: the `references` or the
        `reading-guides` branch dropped, so its page lands as the replay merged it; a page the
        lane did not stage, rewritten by `reading-guides`, committed or left rewritten."""
        log = self._skill()
        self._stage_pages(INDEX, MINE)
        r = self._land(A)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertEqual(["references", "reading-guides"],
                         log.read_text(encoding="utf-8").splitlines())
        self.assertIn(f"regenerated {INDEX}, {MINE} over the replayed change (docgen.py "
                      f"references, reading-guides)", r.stdout)
        self.assertEqual("# References\nthe lane's line\nregenerated by references\n",
                         self._landed(INDEX))
        self.assertEqual("# Mine\nthe lane's line\nregenerated by reading-guides\n",
                         self._landed(MINE))
        self.assertEqual("# Other\n", (self.root / OTHER).read_text(encoding="utf-8"))
        self.assertEqual(sorted([INDEX, MINE, "src/a.py"]),
                         sorted(_git(self.root, "show", "--name-only", "--format=",
                                     "HEAD").splitlines()))
        self.assertFalse(self.wt.exists(), "the worktree was left, holding a rewritten page")

    def test_a_generator_that_fails_is_said_and_left_to_the_hook(self) -> None:
        """`_regenerate`'s failure path. MUTANTS: a failed run not said; its exit or its output
        left out of the warning; the verbs after it not run; its page taken as regenerated."""
        log = self._skill({"references": "fail"})
        self._stage_pages(INDEX, MINE)
        r = self._land(A)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("WARNING docgen.py references failed (exit 3), so its page was not "
                      "regenerated; the hook judges it: docgen stub: references could not read "
                      "its pages", r.stderr)
        self.assertEqual(["references", "reading-guides"],
                         log.read_text(encoding="utf-8").splitlines())
        self.assertEqual("# References\nthe lane's line\n", self._landed(INDEX))
        self.assertEqual("# Mine\nthe lane's line\nregenerated by reading-guides\n",
                         self._landed(MINE))
        self.assertEqual(1, self._hook_runs_in_the_worktree(), "the hook did not judge it")

    def test_a_generator_past_its_bound_is_stopped_and_said(self) -> None:
        """`_regenerate`'s bound, run in process with the bound cut to five seconds, long
        enough for the stand-in to start and log its verb on a loaded host. MUTANTS: an
        overrun not said; the verbs after it run on; a page rewritten after the stop."""
        log = self._skill({"references": "hang"})
        self._stage_pages(INDEX, MINE)
        staged = {rel: _git(self.wt, "show", f":{rel}") for rel in (INDEX, MINE)}
        out, err = io.StringIO(), io.StringIO()
        with unittest.mock.patch.object(base.lanes, "DOCGEN_TIMEOUT", 5), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            base.lanes._regenerate(self.wt)  # noqa: SLF001
        self.assertIn("WARNING docgen.py references ran past 5s and was stopped, so the "
                      "replayed pages were not regenerated; the hook judges them", err.getvalue())
        self.assertEqual(["references"], log.read_text(encoding="utf-8").splitlines())
        self.assertEqual(staged, {rel: _git(self.wt, "show", f":{rel}") for rel in staged})
        self.assertEqual("", _git(self.wt, "diff", "--name-only"))
        self.assertNotIn("regenerated", out.getvalue())

    def test_a_worktree_with_no_generator_runs_none(self) -> None:
        """MUTANT: the generator run where the worktree holds no `docgen.py`, so a missing
        script is warned of as a failed run."""
        self._skill(docgen=False)
        self._stage_pages(INDEX, MINE)
        r = self._land(A)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertNotIn("docgen.py", r.stdout + r.stderr)
        self.assertNotIn("regenerated", r.stdout)
        self.assertEqual("# References\nthe lane's line\n", self._landed(INDEX))


if __name__ == "__main__":
    unittest.main()
