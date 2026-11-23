"""The commit-time links lane judges the tree the commit records, not the working tree.

The lane used to walk the working tree, so a staged index row linking to a file that existed
only untracked passed the commit and turned CI red on push. Each fixture here is a throwaway
repository; the lane is run exactly as `.githooks/pre-commit` declares it, with the checker's
path swapped for this tree's copy.

Run from the repo root:
    python3 -m pytest -q tools/tests/test_check_links_staged_targets.py
"""
# test-census-subject: tools/check_links.py
from __future__ import annotations

import importlib.util
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / "tools" / "check_links.py"
HOOK = REPO / ".githooks" / "pre-commit"


def _load_gitutil():
    """The shared confined-git helper, loaded by path under a private name."""
    path = REPO / ".claude/skills/sdlc-studio/scripts/tests/gitutil.py"
    spec = importlib.util.spec_from_file_location("_staged_targets_gitutil", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


gitutil = _load_gitutil()

INDEX = "sdlc-studio/bugs/_index.md"
ROW = "| [{id}]({id}-{slug}.md) | {slug} |\n"


def _lane_argv() -> list[str]:
    """The links lane's command as the pre-commit hook declares it, run against this tree."""
    text = HOOK.read_text(encoding="utf-8")
    m = re.search(r'^run "links" \\\n(?:.*\\\n)*?\s*-- (.+)$', text, re.M)
    assert m, "the pre-commit hook declares no links lane"
    argv = shlex.split(m.group(1))
    return [sys.executable if a == "python3" else str(TOOL) if a == "tools/check_links.py" else a
            for a in argv]


def _write(root: Path, rel: str, text: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


class _Fixture:
    """A repository holding a skill root, one bug and the index row that links it."""

    def __init__(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="staged_targets_"))
        self.root = self.tmp / "repo"
        self.root.mkdir()
        self.git("init", "-q")
        _write(self.root, ".claude/skills/sdlc-studio/SKILL.md", "# Skill\n")
        _write(self.root, "README.md", "# Fixture\n")
        _write(self.root, INDEX, "# Bugs\n\n| ID | Title |\n| --- | --- |\n"
               + ROW.format(id="BG0001", slug="a"))
        _write(self.root, "sdlc-studio/bugs/BG0001-a.md", "# BG0001\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "seed")

    def git(self, *args: str, env_extra: dict | None = None) -> subprocess.CompletedProcess:
        return gitutil.git(list(args), cwd=self.root, text=True, env_extra=env_extra)

    def add_row(self, bug_id: str, slug: str, *, stage_target: bool) -> None:
        """Write a bug file and its index row; stage the row, and the file only when asked."""
        _write(self.root, f"sdlc-studio/bugs/{bug_id}-{slug}.md", f"# {bug_id}\n")
        with (self.root / INDEX).open("a", encoding="utf-8") as f:
            f.write(ROW.format(id=bug_id, slug=slug))
        self.git("add", INDEX)
        if stage_target:
            self.git("add", f"sdlc-studio/bugs/{bug_id}-{slug}.md")

    def lane(self, argv: list[str] | None = None,
             env_extra: dict | None = None) -> subprocess.CompletedProcess:
        return subprocess.run(argv or _lane_argv(), cwd=self.root, capture_output=True,
                              text=True, env=gitutil.git_env(**(env_extra or {})), timeout=120)

    def cleanup(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)


class StagedTargetTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fx = _Fixture()
        self.addCleanup(self.fx.cleanup)

    def test_an_untracked_target_is_refused(self) -> None:
        """AC1: the row is staged, its target only untracked: the commit would not carry it."""
        self.fx.add_row("BG0002", "b", stage_target=False)
        r = self.fx.lane()
        self.assertEqual(1, r.returncode, r.stdout + r.stderr)
        self.assertIn(f"{INDEX}:6 -> BG0002-b.md [untracked: the commit does not carry it - "
                      "stage it, or drop the link]", r.stdout)
        self.assertEqual(1, r.stdout.count(" -> "), r.stdout)

    def test_a_staged_target_passes(self) -> None:
        """AC2: the same row passes once its target is staged (and refused before it is)."""
        self.fx.add_row("BG0002", "b", stage_target=False)
        self.assertEqual(1, self.fx.lane().returncode, "the untracked target was not refused")
        self.fx.git("add", "sdlc-studio/bugs/BG0002-b.md")
        r = self.fx.lane()
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("All markdown links resolve", r.stdout)

    def test_an_unstaged_deletion_still_resolves(self) -> None:
        """AC3: the target is gone from the working tree but not the index, so the commit has it."""
        (self.fx.root / "sdlc-studio/bugs/BG0001-a.md").unlink()
        with (self.fx.root / INDEX).open("a", encoding="utf-8") as f:
            f.write("\nOne bug filed.\n")
        self.fx.git("add", INDEX)
        r = self.fx.lane()
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)


class StagedTreeTests(unittest.TestCase):
    """The other passes, and the content, read the commit's tree too."""

    def setUp(self) -> None:
        self.fx = _Fixture()
        self.addCleanup(self.fx.cleanup)

    def _refused(self, line: str) -> None:
        r = self.fx.lane()
        self.assertEqual(1, r.returncode, r.stdout + r.stderr)
        self.assertIn(line, r.stdout)

    def test_an_artefact_body_link_to_an_untracked_file_is_named(self) -> None:
        _write(self.fx.root, "sdlc-studio/bugs/BG0003-c.md", "# BG0003\n")
        _write(self.fx.root, "sdlc-studio/stories/US0001-x.md",
               "# US0001\n\nSee [BG0003](../bugs/BG0003-c.md).\n")
        self.fx.git("add", "sdlc-studio/stories/US0001-x.md")
        self._refused("sdlc-studio/stories/US0001-x.md:3 -> ../bugs/BG0003-c.md [untracked:")

    def test_a_root_doc_link_to_an_untracked_file_is_named(self) -> None:
        _write(self.fx.root, "docs/guide.md", "# Guide\n")
        _write(self.fx.root, "README.md", "# Fixture\n\nSee [the guide](docs/guide.md).\n")
        self.fx.git("add", "README.md")
        self._refused("README.md:3 -> docs/guide.md [untracked:")

    def test_a_skill_reference_to_an_untracked_file_is_named(self) -> None:
        _write(self.fx.root, ".claude/skills/sdlc-studio/reference-y.md", "## Part {#part}\n")
        _write(self.fx.root, ".claude/skills/sdlc-studio/help/x.md",
               "# X\n\nRead `../reference-y.md#part`.\n")
        self.fx.git("add", ".claude/skills/sdlc-studio/help/x.md")
        self._refused("help/x.md:3 -> ../reference-y.md#part [untracked:")

    def test_a_loading_guide_cell_naming_an_untracked_file_is_named(self) -> None:
        _write(self.fx.root, ".claude/skills/sdlc-studio/scripts/new.py", "")
        _write(self.fx.root, ".claude/skills/sdlc-studio/SKILL.md",
               "# Skill\n\n## Progressive Loading Guide\n\n| Task | Load |\n| --- | --- |\n"
               "| run it | scripts/new.py |\n")
        self.fx.git("add", ".claude/skills/sdlc-studio/SKILL.md")
        self._refused("SKILL.md loading guide: scripts/new.py names 'scripts/new.py', which is "
                      "untracked: the commit does not carry it - stage it, or correct the cell")
        r = self.fx.lane()
        self.assertNotIn("which is not on disk", r.stdout)
        self.assertEqual(1, r.stdout.count("loading guide"), r.stdout)

    def test_a_target_absent_everywhere_is_still_missing(self) -> None:
        with (self.fx.root / INDEX).open("a", encoding="utf-8") as f:
            f.write(ROW.format(id="BG0009", slug="z"))
        self.fx.git("add", INDEX)
        self._refused(f"{INDEX}:6 -> BG0009-z.md [file missing]")

    def test_a_link_climbing_out_of_the_repository_is_missing_not_a_crash(self) -> None:
        _write(self.fx.tmp, "outside.md", "# Outside\n")
        _write(self.fx.root, "README.md", "# Fixture\n\nSee [it](../outside.md).\n")
        self.fx.git("add", "README.md")
        self._refused("README.md:3 -> ../outside.md [file missing]")

    def test_an_unstaged_edit_is_not_judged(self) -> None:
        """A broken link only the working tree holds is not in the commit, so it refuses nothing."""
        _write(self.fx.root, "README.md", "# Fixture\n\nSee [gone](gone.md).\n")
        r = self.fx.lane()
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)

    def test_the_staged_content_is_judged_not_the_working_copy(self) -> None:
        _write(self.fx.root, "README.md", "# Fixture\n\nSee [gone](gone.md).\n")
        self.fx.git("add", "README.md")
        _write(self.fx.root, "README.md", "# Fixture\n")
        self._refused("README.md:3 -> gone.md [file missing]")

    def test_a_pathspec_commit_judges_its_own_index(self) -> None:
        """`git commit -- <path>` records HEAD plus that path, from a temporary index git names
        in GIT_INDEX_FILE, so a target staged only in the main index is not in this commit."""
        self.fx.add_row("BG0002", "b", stage_target=True)
        hook = self.fx.root / ".git" / "hooks" / "pre-commit"
        hook.write_text("#!/bin/sh\nexec " + shlex.join(_lane_argv()) + "\n", encoding="utf-8")
        hook.chmod(0o755)
        r = gitutil.git(["commit", "-q", "-m", "row only", "--", INDEX], cwd=self.fx.root,
                        check=False, text=True)
        self.assertNotEqual(0, r.returncode, "a commit not carrying the target passed")
        self.assertIn("BG0002-b.md [untracked:", r.stdout + r.stderr)
        r = gitutil.git(["commit", "-q", "-m", "both"], cwd=self.fx.root, check=False, text=True)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)

    def test_without_the_flag_the_working_tree_is_read(self) -> None:
        """CI checks out the commit, so there the working tree is the commit: unchanged."""
        self.fx.add_row("BG0002", "b", stage_target=False)
        argv = [a for a in _lane_argv() if a != "--staged"]
        self.assertIn("--staged", _lane_argv(), "the hook's links lane does not pass --staged")
        r = self.fx.lane(argv)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)

    def test_outside_a_repository_the_staged_check_says_so(self) -> None:
        bare = self.fx.tmp / "plain"
        _write(bare, ".claude/skills/sdlc-studio/SKILL.md", "# Skill\n")
        r = subprocess.run(_lane_argv(), cwd=bare, capture_output=True, text=True,
                           env=gitutil.git_env(), timeout=120)
        self.assertEqual(2, r.returncode, r.stdout + r.stderr)
        self.assertIn("--staged reads the index of a git repository", r.stderr)

    def test_an_unreadable_index_is_an_error_not_a_pass(self) -> None:
        bad = self.fx.tmp / "corrupt-index"
        bad.write_bytes(b"not an index")
        r = self.fx.lane(env_extra={"GIT_INDEX_FILE": str(bad)})
        self.assertEqual(2, r.returncode, r.stdout + r.stderr)
        self.assertIn("error: the index could not be written out to check: ", r.stderr)
        self.assertNotIn("All markdown links resolve", r.stdout)

    def test_a_root_outside_the_repository_is_refused(self) -> None:
        other = self.fx.tmp / "other-skill"
        _write(other, "SKILL.md", "# Skill\n")
        r = self.fx.lane(_lane_argv() + ["--root", str(other), "--repo-root", "."])
        self.assertEqual(2, r.returncode, r.stdout + r.stderr)
        self.assertIn(f"{other.resolve()} is outside the repository", r.stderr)


if __name__ == "__main__":
    unittest.main()
