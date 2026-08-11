"""Unit tests for tools/repo_writes.py - the guard that refuses a suite run which wrote
into the working tree (BG0569).

The guard lives beside the other repo-only checkers in `tools/`; this file drives it, and the
last class drives the two commit hooks that carry it over a real `git commit`. Nothing here
runs a suite, so nothing recurses.

Run from the repo root:
    python3 -m pytest tools/tests/test_repo_writes.py
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
GITHOOKS = REPO / ".githooks"
GUARD = REPO / "tools" / "repo_writes.py"

sys.path.insert(0, str(REPO / "tools"))
import repo_writes  # noqa: E402 - the module under test, imported the way its callers reach it

snapshot = repo_writes.snapshot
differences = repo_writes.differences
_clean_env = repo_writes._clean_env


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(cwd), *args],
                          capture_output=True, text=True, env=_clean_env())


def _seed(root: Path) -> None:
    """A throwaway git repo holding the two directories the invariant names."""
    (root / "sdlc-studio" / "bugs").mkdir(parents=True)
    (root / "sdlc-studio" / ".local").mkdir(parents=True)
    (root / "tools").mkdir()
    (root / ".gitignore").write_text("sdlc-studio/.local/\n", encoding="utf-8")
    (root / "tools" / "thing.py").write_text("VALUE = 1\n", encoding="utf-8")
    (root / "sdlc-studio" / "bugs" / "BG0002-real.md").write_text("# real\n", encoding="utf-8")
    _git(root, "init", "-q")
    _git(root, "config", "user.email", "t@t")
    _git(root, "config", "user.name", "t")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "--no-verify", "-m", "fixture")


class SnapshotTests(unittest.TestCase):
    """What the two readings can and cannot see."""

    def _round(self, write) -> list[tuple[str, str]]:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "r"
            root.mkdir()
            _seed(root)
            before = snapshot(root)
            write(root)
            return differences(before, snapshot(root))

    def test_a_nested_untracked_file_is_seen_not_only_a_top_level_entry(self) -> None:
        """The trap the bug records: the earlier guard read top-level entries only, so the stray
        it was written for - a bug artefact three directories down - was invisible to it. The
        assertion is on the FULL path, which a top-level reading cannot produce.

        TWO strays, and the second is the one that discriminates. `sdlc-studio/bugs/` already
        holds a tracked file, so git names a new file inside it even in its default untracked
        mode; a wholly UNTRACKED directory is what that mode collapses to a single entry. A test
        carrying only the first case passes with `--untracked-files=all` removed."""
        def write(r: Path) -> None:
            (r / "sdlc-studio" / "bugs" / "BG0001-x.md").write_text("x\n", encoding="utf-8")
            fresh = r / "sdlc-studio" / "handoffs" / "run"
            fresh.mkdir(parents=True)
            (fresh / "HO0001.md").write_text("x\n", encoding="utf-8")
        found = self._round(write)
        self.assertIn(("created", "sdlc-studio/bugs/BG0001-x.md"), found,
                      f"the nested stray was not reported: {found}")
        self.assertIn(("created", "sdlc-studio/handoffs/run/HO0001.md"), found,
                      f"a stray inside a wholly untracked directory was collapsed away: {found}")

    def test_a_write_into_gitignored_local_is_seen(self) -> None:
        """The half no git command reports, and the half that destroyed 23 registrations."""
        found = self._round(
            lambda r: (r / "sdlc-studio" / ".local" / "mutation-runs.json").write_text(
                "{}\n", encoding="utf-8"))
        self.assertIn(("created", "sdlc-studio/.local/mutation-runs.json"), found)

    def test_a_write_nested_under_local_is_seen_too(self) -> None:
        """`.local/` is walked to its leaves, never listed."""
        def write(r: Path) -> None:
            d = r / "sdlc-studio" / ".local" / "runs" / "01KZ"
            d.mkdir(parents=True)
            (d / "state.json").write_text("{}\n", encoding="utf-8")
        found = self._round(write)
        self.assertIn(("created", "sdlc-studio/.local/runs/01KZ/state.json"), found)

    def test_a_rewrite_of_a_tracked_file_is_seen(self) -> None:
        found = self._round(
            lambda r: (r / "tools" / "thing.py").write_text("VALUE = 999\n", encoding="utf-8"))
        self.assertIn(("modified", "tools/thing.py"), found,
                      f"a rewritten tracked file was not reported: {found}")

    def test_a_deleted_tracked_file_is_seen(self) -> None:
        found = self._round(lambda r: (r / "sdlc-studio" / "bugs" / "BG0002-real.md").unlink())
        self.assertIn(("deleted", "sdlc-studio/bugs/BG0002-real.md"), found,
                      f"a deleted tracked file was not reported: {found}")

    def test_an_untouched_tree_reports_nothing(self) -> None:
        """The positive control. A lane that reddens on everything is the same failure as one
        that reddens on nothing, and only this case tells them apart."""
        self.assertEqual([], self._round(lambda r: None))

    def test_the_harness_records_are_exempt_by_name_and_their_neighbours_are_not(self) -> None:
        """MUTANT: widen the exemption to all of `.local/`. The gate writes its own timing and
        verdict records inside the comparison window, so those must not be findings - but the
        mutation registrations that were destroyed live in that same directory, and a wildcard
        would exempt them too. Both halves are asserted from one run."""
        def write(r: Path) -> None:
            local = r / "sdlc-studio" / ".local"
            (local / "gate-timings.json").write_text("{}\n", encoding="utf-8")
            (local / "suite-logs").mkdir()
            (local / "suite-logs" / "all-1.log").write_text("x\n", encoding="utf-8")
            (local / "mutation-runs.json").write_text("{}\n", encoding="utf-8")
        self.assertEqual([("created", "sdlc-studio/.local/mutation-runs.json")],
                         self._round(write))

    def test_bytecode_is_not_a_finding_in_either_reading(self) -> None:
        """Running python writes `__pycache__`, and the suites purge and rebuild it every run. A
        guard reporting that would redden on every commit and be switched off within a day.

        BOTH readings, in one case: the `.local/` walk skips it by directory name, and the git
        reading has to skip it by path - measured, because the first version exempted only the
        walk and the wiring test refused its own control commit over two stray `.pyc` files."""
        def write(r: Path) -> None:
            for cache in (r / "sdlc-studio" / ".local" / "__pycache__",
                          r / "tools" / "__pycache__"):
                cache.mkdir()
                (cache / "x.cpython-313.pyc").write_bytes(b"\x00")
        self.assertEqual([], self._round(write))


class CommandLineTests(unittest.TestCase):
    """The shipped entry point, not the library. The wiring is what a library test cannot
    exercise, and this repo has shipped a lane that printed nothing while its function passed."""

    def _run(self, root: Path, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(GUARD), *args],
                              capture_output=True, text=True, cwd=str(root), env=_clean_env())

    def test_the_cli_refuses_a_run_that_wrote_and_names_the_path(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "r"
            root.mkdir()
            _seed(root)
            snap = Path(d) / "snap.json"
            self.assertEqual(0, self._run(root, "snapshot", "--root", ".",
                                          "--out", str(snap)).returncode)
            (root / "sdlc-studio" / "bugs" / "BG0001-x.md").write_text("x\n", encoding="utf-8")
            proc = self._run(root, "check", "--root", ".", "--since", str(snap))
            self.assertEqual(1, proc.returncode, proc.stdout + proc.stderr)
            self.assertIn("sdlc-studio/bugs/BG0001-x.md", proc.stdout)
            self.assertIn("--dry-run", proc.stdout, "the refusal must name where to look")

    def test_the_cli_is_green_over_an_untouched_tree(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "r"
            root.mkdir()
            _seed(root)
            snap = Path(d) / "snap.json"
            self._run(root, "snapshot", "--root", ".", "--out", str(snap))
            proc = self._run(root, "check", "--root", ".", "--since", str(snap))
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)

    def test_a_missing_snapshot_refuses_rather_than_reading_as_unchanged(self) -> None:
        """An absent record means the question was never asked. Fail-open here would make the
        lane vanish the first time the snapshot step could not write."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "r"
            root.mkdir()
            _seed(root)
            proc = self._run(root, "check", "--root", ".", "--since", str(Path(d) / "absent"))
            self.assertEqual(2, proc.returncode)
            self.assertIn("unknown", proc.stderr)


PASS_SH = "#!/usr/bin/env bash\nexit 0\n"
PASS_PY = "import sys\nsys.exit(0)\n"

#: A stub tools/ suite that writes a bug artefact into the tree it runs in - instance four,
#: reduced to one line. `unittest discover` runs it as a normal test that PASSES, so nothing
#: except the repo-writes lane can refuse the commit.
STRAY_SUITE = '''\
import pathlib
import unittest


class T(unittest.TestCase):
    def test_writes_a_stray(self):
        p = pathlib.Path("sdlc-studio/bugs/BG0001-x.md")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("# stray\\n", encoding="utf-8")
        self.assertTrue(True)
'''

CLEAN_SUITE = '''\
import unittest


class T(unittest.TestCase):
    def test_ok(self):
        self.assertTrue(True)
'''


class HookWiringTests(unittest.TestCase):
    """The lane runs, in the hooks people actually run, over a real `git commit`.

    Built on the fixture shape of `tools/tests/test_precommit_window_guard.py`: every other
    guard is stubbed to pass, so a refusal can only have come from this lane.
    """

    def _repo(self, tmp: Path, suite: str) -> Path:
        root = tmp / "r"
        (root / "tools" / "tests").mkdir(parents=True)
        (root / "sdlc-studio" / ".local").mkdir(parents=True)
        (root / "sdlc-studio" / "bugs").mkdir(parents=True)
        (root / ".githooks").mkdir(parents=True)
        (root / ".claude" / "skills" / "sdlc-studio" / "scripts").mkdir(parents=True)
        (root / "node_modules" / ".bin").mkdir(parents=True)

        for name in ("pre-commit", "commit-msg"):
            hook = root / ".githooks" / name
            hook.write_text((GITHOOKS / name).read_text(encoding="utf-8"), encoding="utf-8")
            hook.chmod(0o755)

        for name in ("lint-style.sh", "check_action_pins.sh", "skill-tests.sh"):
            p = root / "tools" / name
            p.write_text(PASS_SH, encoding="utf-8")
            p.chmod(0o755)
        # DERIVED from the hooks - see tools/tests/hookutil.py - so a lane added to the gate
        # reaches this fixture without anybody remembering to come here.
        from hookutil import hook_skill_scripts, hook_tool_scripts, seed_verify_baseline
        for name in hook_tool_scripts():
            (root / "tools" / name).write_text(PASS_PY, encoding="utf-8")
        seed_verify_baseline(root)
        for rel in hook_skill_scripts():
            dest = root / rel
            if dest.exists() or not dest.parent.is_dir():
                continue
            dest.write_text(PASS_PY, encoding="utf-8")
        scripts = root / ".claude" / "skills" / "sdlc-studio" / "scripts"
        for name in ("engagement_floor.py", "reconcile.py"):
            (scripts / name).write_text(PASS_PY, encoding="utf-8")
        # `gate.py` separately, and not merely for tidiness: it is reached through the hook's
        # inline block rather than through a `run` lane, so the derivation above cannot see it.
        (scripts / "gate.py").write_text(PASS_PY, encoding="utf-8")
        md = root / "node_modules" / ".bin" / "markdownlint"
        md.write_text(PASS_SH, encoding="utf-8")
        md.chmod(0o755)
        # The guard under test is NOT stubbed. It is written AFTER the derivation above, which
        # stubs every tools/ script a hook lane names - and this one is named by a hook lane, so
        # without this line the fixture would exercise a stub that always passes.
        (root / "tools" / "repo_writes.py").write_text(
            GUARD.read_text(encoding="utf-8"), encoding="utf-8")
        (root / "tools" / "tests" / "__init__.py").write_text("", encoding="utf-8")
        (root / "tools" / "tests" / "test_stub.py").write_text(suite, encoding="utf-8")
        (root / ".gitignore").write_text("sdlc-studio/.local/\n", encoding="utf-8")
        (root / "README.md").write_text("notes\n", encoding="utf-8")

        _git(root, "init", "-q")
        _git(root, "config", "user.email", "t@t")
        _git(root, "config", "user.name", "t")
        _git(root, "add", "-A")
        _git(root, "commit", "-q", "--no-verify", "-m", "fixture")
        _git(root, "config", "core.hooksPath", ".githooks")
        return root

    def _commit(self, root: Path, rel: str, body: str) -> tuple[int, str]:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
        _git(root, "add", "-A")
        out = subprocess.run(["git", "-C", str(root), "commit", "-m", "fix(BG0001): a change"],
                             capture_output=True, text=True, env=_clean_env())
        return out.returncode, out.stdout + out.stderr

    def test_a_suite_that_writes_into_the_tree_refuses_the_commit_and_names_the_path(self)\
            -> None:
        """MUTANT: delete the `run "repo-writes"` lane from `.githooks/commit-msg`, or the
        snapshot step from `.githooks/pre-commit`. Either leaves the stray in the tree with the
        commit landing green, which is the state all four instances shipped in."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d), STRAY_SUITE)
            rc, out = self._commit(root, "tools/thing.py", "VALUE = 2\n")
            self.assertNotEqual(rc, 0, f"the commit was NOT refused:\n{out}")
            self.assertIn("repo-writes", out)
            self.assertIn("sdlc-studio/bugs/BG0001-x.md", out,
                          "the refusal must name the path the suite wrote")
            self.assertEqual("fixture", _git(root, "log", "--format=%s").stdout.strip(),
                             "the refusal printed but did not stop the commit")

    def test_a_clean_suite_leaves_the_lane_green(self) -> None:
        """The control that makes the case above mean something: identical staged content,
        identical hooks, a stub suite that writes nothing, and the commit lands.

        MUTANT: make `check` return 1 whatever it found. A lane that reddens on everything is
        the same failure as one that reddens on nothing, and only this case tells them apart.
        The record's removal is asserted too - it is one-shot, and one left behind would charge
        the next `commit-msg`-only operation against a tree from a run that never happened."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d), CLEAN_SUITE)
            rc, out = self._commit(root, "tools/thing.py", "VALUE = 2\n")
            self.assertEqual(rc, 0, f"a clean run was refused:\n{out}")
            self.assertIn("repo-writes", out, "a lane that never ran cannot have been green")
            self.assertFalse((root / ".git" / "sdlc-repo-writes").exists(),
                             "the snapshot record outlived the commit it was taken for")

    def test_a_docs_only_commit_pays_nothing_because_no_suite_ran(self) -> None:
        """MUTANT: move the snapshot step in `pre-commit` outside the suite-selection block.
        The lane would then read a tree no suite touched, on every commit, for no information -
        and a snapshot with no run between its halves is evidence of nothing.

        The RECORD is the assertion that mutant fails on. Asserting only that the lane printed
        nothing passes with the snapshot taken unconditionally, because `commit-msg` exits at
        its handover check before ever reaching the lane - so the cost would be paid on every
        commit while the output looked identical."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d), CLEAN_SUITE)
            rc, out = self._commit(root, "README.md", "notes and more notes\n")
            self.assertEqual(rc, 0, out)
            self.assertNotIn("repo-writes", out, "the lane ran on a commit that ran no suite")
            self.assertIn("no test-relevant file staged", out)
            self.assertFalse((root / ".git" / "sdlc-repo-writes").exists(),
                             "a snapshot was taken for a commit that ran no suite")


class RosterTests(unittest.TestCase):
    """A guard nobody has written down is one nobody notices losing."""

    def test_the_roster_names_this_lane_and_both_hooks_that_carry_it(self) -> None:
        agents = (REPO / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("repo_writes.py", agents,
                      "AGENTS.md's lane roster does not name the repo-writes checker")
        self.assertIn('run "repo-writes"',
                      (GITHOOKS / "commit-msg").read_text(encoding="utf-8"),
                      "commit-msg does not carry the lane the roster claims")
        self.assertIn("repo_writes.py snapshot",
                      (GITHOOKS / "pre-commit").read_text(encoding="utf-8"),
                      "pre-commit does not take the snapshot the lane compares against")


if __name__ == "__main__":
    unittest.main()
