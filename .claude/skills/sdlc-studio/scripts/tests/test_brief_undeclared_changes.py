"""BG0982: `critic.py brief` names the files the unit's commits changed outside its Affects.

The brief's diff is bounded to the unit's declared Affects. A unit whose Affects left out the
module that does the work pointed its reviewer at the edges of the change and away from its
centre, and nothing said so. The brief now carries a 'changed but not declared' block naming
each file the unit's commits since the run's base changed outside its Affects, and suggests
correcting Affects; the diff it carries and names stays bounded to the Affects.

A unit's commits are the ones `verify_ac` already counts as its own: the subject or a `Refs:`
line names the unit. The workspace's records (`sdlc-studio/`), which status and review
bookkeeping commits write under the unit's id, are not named.

Each case drives the shipped `critic.py brief` against a throwaway git repository whose open run
names the unit, with git confined to the fixture; the git failure case runs in-process.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402 - confined git for the fixture repo
import loader  # noqa: E402

critic = loader.load_script("critic")
SCRIPTS = loader.SCRIPTS_DIR
BLOCK = "Changed but not declared"
STORY = "sdlc-studio/stories/US0001-the-widget.md"


def _write(root: Path, rel: str, body: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _story(root: Path, affects: str) -> None:
    _write(root, STORY, f"# US0001: the widget\n\n> **Status:** In Progress\n"
                        f"> **Affects:** {affects}\n> **Points:** 2\n\n## Acceptance Criteria\n\n"
                        "- [ ] **AC1** it works\n  - **Verify:** shell true\n")


def _commit(root: Path, message: str, files: dict[str, str] | None = None) -> str:
    for rel, body in (files or {}).items():
        _write(root, rel, body)
    gitutil.git(["add", "-A"], root)
    gitutil.git(["commit", "-q", "--no-verify", "-m", message], root)
    return gitutil.git(["rev-parse", "HEAD"], root, text=True).stdout.strip()


def _project(root: Path, affects: str) -> str:
    """US0001 declaring `affects`, an open run naming it, and the base commit, returned."""
    _story(root, affects)
    _write(root, "src/a.py", "a = 1\n")
    _write(root, ".gitignore", "sdlc-studio/.local/\n")
    gitutil.git(["init", "-q"], root)
    base = _commit(root, "base")
    state = root / "sdlc-studio" / ".local" / "run-state.json"
    state.parent.mkdir(parents=True, exist_ok=True)
    state.write_text(json.dumps({"schema": 1, "run_id": "RUN-A", "outcome": "running",
                                 "started_at": "2026-10-01T08:00:00Z", "batch": ["US0001"],
                                 "base_ref": base}), encoding="utf-8")
    return base


def _brief(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-B", str(SCRIPTS / "critic.py"), "brief", "--unit", "US0001",
         "--seat", "qa", "--tier", "light", "--root", str(root)],
        capture_output=True, text=True, check=False, timeout=120, env=gitutil.git_env())


def _block(text: str) -> list[str] | None:
    """The block's listed paths, or None when the brief carries no block."""
    at = text.find(BLOCK)
    if at < 0:
        return None
    lines = text[at:].split("\n\n", 1)[0].splitlines()[1:]
    return [line[2:] for line in lines if line.startswith("- ")]


class UndeclaredChangeTests(unittest.TestCase):

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def _unit_commits(self) -> None:
        """US0001's commits: one naming it in the subject, one naming it only on a `Refs:`
        line, and a bookkeeping one writing its story; beside them another unit's commit, a
        commit naming no unit, and one naming US0001 only in body prose."""
        root = self.root
        _commit(root, "feat(US0001): the widget", {"src/a.py": "a = 2\n", "src/drift.py": "d = 1\n",
                                                   "tests/test_drift.py": "t = 1\n"})
        _commit(root, "chore: two units\n\nRefs: US0001\nRefs: US0002", {"src/refd.py": "r = 1\n"})
        story = (root / STORY).read_text(encoding="utf-8").replace("In Progress", "Done")
        _commit(root, "docs(RUN-A): US0001 is Done", {STORY: story})
        _commit(root, "feat(US0002): another", {"src/other.py": "o = 1\n"})
        _commit(root, "chore: tidy", {"src/tidy.py": "t = 1\n"})
        _commit(root, "chore: prose\n\nThis follows US0001.", {"src/prose.py": "p = 1\n"})

    def test_undeclared_change_is_named(self) -> None:
        """AC1. Mutants: the block dropped; the subject read and the `Refs:` line not (the refd
        file unnamed); another unit's commit, a commit naming no unit or one naming the unit
        only in prose read as the unit's; a declared file named; the workspace's records
        named; the block on stderr rather than in the brief the reviewer reads."""
        root = self.root
        base = _project(root, "src/a.py")
        self._unit_commits()
        proc = _brief(root)
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertEqual(["src/drift.py", "src/refd.py", "tests/test_drift.py"],
                         _block(proc.stdout), proc.stdout)
        self.assertIn(f"git log {base}..HEAD", proc.stdout)
        self.assertNotIn(BLOCK, proc.stderr)

    def test_declared_changes_print_no_block(self) -> None:
        """AC2. Mutants: a block printed whenever the unit has commits; a declared directory's
        member read as undeclared; an empty block printed with no path in it; a git failure
        read as no undeclared change."""
        root = self.root
        _project(root, "src/a.py, src/drift.py, tests/, src/refd.py")
        self._unit_commits()
        proc = _brief(root)
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertIsNone(_block(proc.stdout), proc.stdout)
        self.assertNotIn(BLOCK, proc.stdout)
        # git that cannot list the unit's commits is said in the brief, never read as clean
        real = critic._git

        def broken(at, *args):
            if "log" in args:
                return subprocess.CompletedProcess([], 128, b"", b"fatal: bad object\n")
            return real(at, *args)

        with unittest.mock.patch.object(critic, "_git", broken):
            text = critic.brief(root, "US0001", "qa", "light")
        self.assertIn(f"{BLOCK}: not checked - git could not list the unit's commits "
                      f"(fatal: bad object)", text)

    def test_diff_scope_stays_bounded(self) -> None:
        """AC3. Mutants: the undeclared files added to the diff's pathspec, its heading, or the
        scope line; the block missing its suggestion to correct Affects."""
        root = self.root
        base = _project(root, "src/a.py")
        self._unit_commits()
        proc = _brief(root)
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertIn(f"--- UNIT DIFF (git diff {base} HEAD -- src/a.py) ---", proc.stdout)
        self.assertIn(f"Diff against the run's base commit: git diff {base} -- src/a.py\n",
                      proc.stdout)
        self.assertIn("+a = 2", proc.stdout)
        for line in ("+d = 1", "+t = 1", "+r = 1"):
            self.assertNotIn(line, proc.stdout, "an undeclared file's diff reached the brief")
        block = proc.stdout[proc.stdout.index(BLOCK):].split("\n\n", 1)[0]
        self.assertIn("does not widen this review", block)
        self.assertRegex(block, re.compile(r"correct\s+its\s+Affects", re.I))


if __name__ == "__main__":
    unittest.main()
