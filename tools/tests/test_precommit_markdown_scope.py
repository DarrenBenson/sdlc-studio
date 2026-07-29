"""What the pre-commit markdown lanes can SEE (BG0341).

markdownlint's `**/*.md` glob cannot enter a dot-directory, and the hook answered that by
naming one: `.claude/**/*.md`. An enumerated list silently exempts what it forgot, and it
forgot `.github/` - three tracked files (the pull-request template and two issue
templates) matched neither glob here nor in `npm run lint:md`, so a markdown defect in any
of them passed every per-commit and per-push lane. Reproduced before the repair: a file at
`.github/broken.md` with an MD032 violation lints clean under `markdownlint '**/*.md'` and
fails when named directly.

The enumeration is now derived from `git ls-files`, and this executes the hook's own
enumeration block rather than a copy of it: a test that re-implemented the partition would
agree with itself while the hook did something else.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / ".githooks" / "pre-commit"

_BLOCK_RE = re.compile(r"^# >>> md-enumeration.*?\n(.*?)^# <<< md-enumeration",
                       re.S | re.M)


def _enumeration_block() -> str:
    m = _BLOCK_RE.search(HOOK.read_text(encoding="utf-8"))
    if not m:
        raise AssertionError(
            "the pre-commit hook no longer marks its markdown enumeration block; this test "
            "executes the shipped code rather than a copy of it, so the markers are load-bearing")
    return m.group(1)


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True,
                   capture_output=True, text=True)


class MarkdownEnumerationTests(unittest.TestCase):
    """The partition, run as the hook runs it, over a real index."""

    def _lists(self, root: Path) -> tuple[list[str], list[str]]:
        script = (_enumeration_block()
                  + '\nprintf "ROOT:%s\\n" "${md_root[@]}"\n'
                  + 'printf "PAYLOAD:%s\\n" "${md_payload[@]}"\n')
        out = subprocess.run(["bash", "-uo", "pipefail", "-c", script],
                             cwd=root, capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        lines = out.stdout.splitlines()
        return ([ln[5:] for ln in lines if ln.startswith("ROOT:") and ln != "ROOT:"],
                [ln[8:] for ln in lines if ln.startswith("PAYLOAD:") and ln != "PAYLOAD:"])

    def _repo(self, d: str) -> Path:
        root = Path(d)
        _git(root, "init", "-q")
        _git(root, "config", "user.email", "t@example.com")
        _git(root, "config", "user.name", "t")
        for rel in (".github/PULL_REQUEST_TEMPLATE.md",
                    ".github/ISSUE_TEMPLATE/bug_report.md",
                    "README.md",
                    "docs/guide.md",
                    ".claude/skills/sdlc-studio/SKILL.md",
                    ".claude/worktrees/scratch/half-written.md"):
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("# x\n", encoding="utf-8")
        _git(root, "add", "-A")
        _git(root, "commit", "-q", "-m", "seed")
        return root

    def test_tracked_dot_directory_markdown_is_enumerated(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            md_root, _payload = self._lists(self._repo(d))
        for rel in (".github/PULL_REQUEST_TEMPLATE.md",
                    ".github/ISSUE_TEMPLATE/bug_report.md"):
            self.assertIn(rel, md_root,
                          "tracked .github/ markdown was linted by nothing per commit")

    def test_ordinary_markdown_is_still_enumerated(self) -> None:
        """The control: widening the scope must not have dropped what already worked."""
        with tempfile.TemporaryDirectory() as d:
            md_root, _payload = self._lists(self._repo(d))
        self.assertIn("README.md", md_root)
        self.assertIn("docs/guide.md", md_root)

    def test_the_payload_keeps_its_own_lane(self) -> None:
        """`.claude/` is linted under the payload config, so it must land in that list and
        not in the root one, or the two rule sets get applied to the wrong files."""
        with tempfile.TemporaryDirectory() as d:
            md_root, payload = self._lists(self._repo(d))
        self.assertIn(".claude/skills/sdlc-studio/SKILL.md", payload)
        self.assertNotIn(".claude/skills/sdlc-studio/SKILL.md", md_root)

    def test_transient_worktrees_are_excluded_from_both(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            md_root, payload = self._lists(self._repo(d))
        stray = ".claude/worktrees/scratch/half-written.md"
        self.assertNotIn(stray, md_root)
        self.assertNotIn(stray, payload)

    def test_a_newly_staged_file_is_covered_on_the_commit_that_adds_it(self) -> None:
        """The index, not HEAD. A file added by the commit being gated must be linted by
        that commit, or the lane always runs one commit late."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d)
            (root / ".github" / "NEW.md").write_text("# new\n", encoding="utf-8")
            _git(root, "add", ".github/NEW.md")
            md_root, _payload = self._lists(root)
        self.assertIn(".github/NEW.md", md_root)


class RealRepoCoverageTests(unittest.TestCase):
    """Against this repo's own index, and against the linter itself."""

    def test_this_repos_github_markdown_is_now_in_scope(self) -> None:
        tracked = [p for p in subprocess.run(
            ["git", "ls-files", "-z", "--", "*.md"], cwd=REPO, capture_output=True,
            text=True, check=True).stdout.split("\0") if p.startswith(".github/")]
        self.assertTrue(tracked, "this repo no longer tracks any .github/ markdown")
        script = (_enumeration_block()
                  + '\nprintf "%s\\n" "${md_root[@]}"\n')
        out = subprocess.run(["bash", "-uo", "pipefail", "-c", script],
                             cwd=REPO, capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        listed = set(out.stdout.splitlines())
        self.assertTrue(set(tracked) <= listed,
                        f"not enumerated: {sorted(set(tracked) - listed)}")

    def test_the_defect_is_real_the_glob_cannot_see_a_dot_directory(self) -> None:
        """The premise, checked rather than quoted: a violation under a dot-directory is
        invisible to `**/*.md` and visible when the file is named. If this ever stops
        holding, the enumeration above is solving a problem that no longer exists."""
        linter = REPO / "node_modules" / ".bin" / "markdownlint"
        if not linter.is_file():
            found = shutil.which("markdownlint")
            if not found:
                self.skipTest("markdownlint not installed (npm install)")
            linter = Path(found)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / ".github").mkdir()
            # MD032: a list with no blank line before it.
            (root / ".github" / "broken.md").write_text(
                "# Title\n\nText\n- a\n- b\n\nend\n", encoding="utf-8")
            glob = subprocess.run([str(linter), "**/*.md", "--ignore", "node_modules"],
                                  cwd=root, capture_output=True, text=True)
            direct = subprocess.run([str(linter), ".github/broken.md"],
                                    cwd=root, capture_output=True, text=True)
        self.assertEqual(glob.returncode, 0,
                         "the glob was expected to miss the dot-directory entirely")
        self.assertNotEqual(direct.returncode, 0,
                            "the fixture file must actually violate a rule")


class NpmLaneSeesEverythingTheHookDoesTests(unittest.TestCase):
    """BG0374. BG0341 derived the HOOK's set from `git ls-files` and left the npm lanes as the
    root glob plus one hand-added dot-directory - so `npm run lint`, which CI runs, was still
    blind to the three tracked files under `.github/` that started all this. Two lanes with two
    enumerations is the same defect waiting to recur on whichever one is not updated next."""

    SCRIPT = REPO / "tools" / "lint-md.sh"

    def test_the_npm_lanes_delegate_to_the_derived_enumeration(self) -> None:
        import json
        scripts = json.loads((REPO / "package.json").read_text(encoding="utf-8"))["scripts"]
        for lane in ("lint:md", "lint:fix"):
            with self.subTest(lane=lane):
                self.assertIn("tools/lint-md.sh", scripts[lane],
                              f"{lane} still names a glob of its own; a glob cannot enter a "
                              f"dot-directory, which is the whole defect")
                self.assertNotIn("**/*.md", scripts[lane])

    def test_the_script_reads_the_tracked_set(self) -> None:
        """Executable lines only - the header explains the defect by quoting the glob, and a
        check that reads comments would refuse the explanation along with the bug."""
        code = "\n".join(line for line in self.SCRIPT.read_text(encoding="utf-8").splitlines()
                         if not line.lstrip().startswith("#"))
        self.assertIn("git ls-files", code, "the set must be DERIVED, not enumerated")
        self.assertNotIn("**/*.md", code)

    def test_every_tracked_markdown_file_is_covered_by_one_lane(self) -> None:
        """The property, measured against the repository rather than asserted about the code.
        A file in neither partition is a file no lane lints."""
        out = subprocess.run(["git", "-C", str(REPO), "ls-files", "-z", "--", "*.md"],
                             capture_output=True, text=True, check=False)
        tracked = [f for f in out.stdout.split("\0") if f]
        self.assertTrue(tracked, "git ls-files returned nothing - this check proves nothing")
        covered = [f for f in tracked if not f.startswith(".claude/worktrees/")]
        self.assertTrue(any(f.startswith(".github/") for f in covered),
                        "the .github/ files this bug is about are not in the tracked set - the "
                        "fixture for this regression has gone, so the check is inert")
        payload = [f for f in covered if f.startswith(".claude/")]
        root = [f for f in covered if not f.startswith(".claude/")]
        self.assertEqual(sorted(covered), sorted(root + payload),
                         "a tracked markdown file falls into neither lane")


if __name__ == "__main__":
    unittest.main()
