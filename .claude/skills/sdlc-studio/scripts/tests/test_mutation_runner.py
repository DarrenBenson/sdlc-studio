"""The mutation runner: `mutation.py run --edits <list.json> --scope <id>`.

Each test builds a scratch git repository holding a unit whose `Affects` names the files the
list may edit, and drives the runner through its command line, as an author or a reviewer
would. The named tests are real pytest tests inside the fixture, so a verdict is the runner's
reading of a real run, never a stub's.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/mutation.py
from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ dir, for the shared gitutil helper
import gitutil  # noqa: E402

SCRIPT = Path(__file__).resolve().parent.parent / "mutation.py"

CALC = "def add(a, b):\n    return a + b\n"
EXTRA = "def double(x):\n    return x * 2\n"
TEST_CALC = """import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import calc


def test_add():
    assert calc.add(2, 3) == 5


def test_red():
    assert False, "red before any edit"
"""
# Rewrites the file the runner mutated, then passes: the runner must put the bytes back.
TEST_REWRITE = """import pathlib

CALC = pathlib.Path(__file__).resolve().parent.parent / "calc.py"


def test_rewrites_calc():
    CALC.write_text("garbage = True\\n", encoding="utf-8")


def test_replaces_calc_with_a_directory():
    CALC.unlink()
    CALC.mkdir()
"""
# Sleeps only while the mutant is on disk, after saying so, so a signal lands mid-mutant.
TEST_SLOW = """import os
import pathlib
import time

CALC = pathlib.Path(__file__).resolve().parent.parent / "calc.py"


def test_slow_under_the_mutant():
    if "a - b" in CALC.read_text(encoding="utf-8"):
        pathlib.Path(os.environ["RUNNER_MARK"]).write_text(str(os.getpid()), encoding="utf-8")
        time.sleep(60)
"""
STORY = "# US0001: x\n\n> **Status:** Ready\n> **Affects:** {affects}\n"
AFFECTS = "calc.py, lib/, tests/test_calc.py, tests/test_rewrite.py, tests/test_slow.py"


def _entry(name, file, old, new, test):
    return {"mutant": name, "file": file, "old": old, "new": new, "test": test}


KILLED = _entry("adds", "calc.py", "a + b", "a - b", "tests/test_calc.py::test_add")
SURVIVED = _entry("doubles", "lib/extra.py", "x * 2", "x * 3", "tests/test_calc.py::test_add")


def _alive(pid: int) -> bool:
    """True while `pid` runs; a zombie waiting on its reaper has stopped running."""
    try:
        stat = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8")
    except OSError:
        return False
    return stat.rsplit(") ", 1)[-1][:1] not in ("Z", "X")


class MutationRunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.base = Path(tempfile.mkdtemp(prefix="mutation_runner_"))
        self.addCleanup(shutil.rmtree, self.base, True)
        self.root = self.base / "repo"
        self.tmp = self.base / "tmp"      # the runner's TMPDIR, so its scratch copy is visible
        self.tmp.mkdir()
        files = {
            "calc.py": CALC,
            "lib/extra.py": EXTRA,
            "other.py": "def other():\n    return 1\n",
            "tests/test_calc.py": TEST_CALC,
            "tests/test_rewrite.py": TEST_REWRITE,
            "tests/test_slow.py": TEST_SLOW,
            "sdlc-studio/stories/US0001-x.md": STORY.format(affects=AFFECTS),
        }
        for rel, text in files.items():
            (self.root / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.root / rel).write_text(text, encoding="utf-8")
        (self.root / ".gitignore").write_text("sdlc-studio/.local/\n", encoding="utf-8")
        gitutil.git(["init", "-q"], self.root)
        gitutil.git(["add", "-A"], self.root)
        gitutil.git(["commit", "-qm", "fixture"], self.root)

    def _env(self, **extra: str) -> dict:
        return gitutil.git_env(TMPDIR=str(self.tmp), **extra)

    def _write_list(self, entries, name: str = "edits.json") -> Path:
        path = self.base / name
        path.write_text(json.dumps(entries), encoding="utf-8")
        return path

    def _args(self, edits: Path, report: Path | None = None) -> list[str]:
        args = [sys.executable, str(SCRIPT), "run", "--edits", str(edits), "--scope", "US0001",
                "--root", str(self.root)]
        return args + (["--report", str(report)] if report else [])

    def _run(self, edits: Path, report: Path | None = None) -> subprocess.CompletedProcess:
        return subprocess.run(self._args(edits, report), capture_output=True, text=True,
                              env=self._env(), timeout=300)

    def _snapshot(self) -> dict:
        """Every file of the working tree, outside `.git`, with its bytes."""
        return {str(p.relative_to(self.root)): p.read_bytes()
                for p in sorted(self.root.rglob("*"))
                if p.is_file() and ".git" not in p.relative_to(self.root).parts}

    def _status(self) -> str:
        return gitutil.git(["status", "--porcelain", "--untracked-files=all"], self.root,
                           text=True).stdout

    def test_each_edit_gets_one_line_with_its_verdict_and_the_tests_last_line(self) -> None:
        """AC1. Two edits, one a test catches and one none does: one line each, in list order,
        naming the entry, its verdict and the test's last line; the report holds the same."""
        proc = self._run(self._write_list([KILLED, SURVIVED]))
        lines = proc.stdout.splitlines()
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)  # a survivor exits 1
        self.assertEqual(len(lines), 3, f"one line per mutant and one summary:\n{proc.stdout}")
        self.assertTrue(lines[0].startswith("adds killed: "), lines[0])
        self.assertIn("1 failed", lines[0])
        self.assertTrue(lines[1].startswith("doubles survived: "), lines[1])
        self.assertIn("1 passed", lines[1])
        self.assertIn("killed 1, survived 1, not applied 0, error 0", lines[2])
        report_path = self.root / "sdlc-studio" / ".local" / "mutation-edits-US0001.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["unit"], "US0001")
        self.assertEqual(report["counts"],
                         {"killed": 1, "survived": 1, "not_applied": 0, "error": 0})
        self.assertEqual([{k: m[k] for k in ("mutant", "file", "old", "new", "test")}
                          for m in report["mutants"]], [KILLED, SURVIVED])
        self.assertEqual([m["result"] for m in report["mutants"]], ["killed", "survived"])
        self.assertEqual([m["last_line"] for m in report["mutants"]],
                         [ln.split(": ", 1)[1] for ln in lines[:2]])
        # A test red before the edit was applied cannot kill it: the verdict is an error.
        red = _entry("red", "calc.py", "a + b", "a - b", "tests/test_calc.py::test_red")
        proc = self._run(self._write_list([red, KILLED]), self.base / "red.json")
        lines = proc.stdout.splitlines()
        self.assertEqual(len(lines), 3, proc.stdout + proc.stderr)
        self.assertTrue(lines[0].startswith("red error: "), lines[0])
        self.assertIn("does not pass without the edit", lines[0])
        self.assertTrue(lines[1].startswith("adds killed: "), lines[1])
        report = json.loads((self.base / "red.json").read_text(encoding="utf-8"))
        self.assertEqual(report["counts"],
                         {"killed": 1, "survived": 0, "not_applied": 0, "error": 1})

    def test_the_working_tree_is_byte_identical_after_a_run_and_an_interrupt(self) -> None:
        """AC2. The edits and the tests run in a scratch copy: a test that rewrites the mutated
        file, a SIGTERM mid-mutant and a file that will not restore leave the tree as it was."""
        before, status = self._snapshot(), self._status()
        rewrite = _entry("rewriter", "calc.py", "a + b", "a * b",
                         "tests/test_rewrite.py::test_rewrites_calc")
        proc = self._run(self._write_list([rewrite, KILLED]), self.base / "one.json")
        lines = proc.stdout.splitlines()
        self.assertTrue(lines[0].startswith("rewriter survived: "), proc.stdout + proc.stderr)
        # The next mutant found the original bytes: its edit applied and its test killed it.
        self.assertTrue(lines[1].startswith("adds killed: "), proc.stdout + proc.stderr)
        self.assertEqual(self._snapshot(), before)
        self.assertEqual(self._status(), status)
        self.assertEqual(list(self.tmp.iterdir()), [], "the scratch copy is removed")

        mark = self.base / "mark"
        slow = _entry("slow", "calc.py", "a + b", "a - b",
                      "tests/test_slow.py::test_slow_under_the_mutant")
        runner = subprocess.Popen(self._args(self._write_list([slow]), self.base / "two.json"),
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                  env=self._env(RUNNER_MARK=str(mark)))
        self.addCleanup(lambda: runner.poll() is None and runner.kill())
        deadline = time.monotonic() + 120
        while not mark.exists() and runner.poll() is None and time.monotonic() < deadline:
            time.sleep(0.1)
        self.assertTrue(mark.exists(), "the slow test never ran under the mutant")
        time.sleep(0.2)
        runner.send_signal(signal.SIGTERM)
        runner.communicate(timeout=60)
        self.assertEqual(runner.returncode, -signal.SIGTERM)
        self.assertEqual(self._snapshot(), before)
        self.assertEqual(self._status(), status)
        self.assertEqual(list(self.tmp.iterdir()), [], "an interrupt still removes the copy")
        self.assertFalse((self.base / "two.json").exists(), "an interrupted run writes no report")
        pid = int(mark.read_text(encoding="utf-8"))
        deadline = time.monotonic() + 10
        while _alive(pid) and time.monotonic() < deadline:
            time.sleep(0.1)
        self.assertFalse(_alive(pid), "the test's process outlived the interrupted run")

        broken = _entry("dir", "calc.py", "a + b", "a * b",
                        "tests/test_rewrite.py::test_replaces_calc_with_a_directory")
        proc = self._run(self._write_list([broken, KILLED]), self.base / "three.json")
        self.assertEqual(proc.returncode, 3, proc.stdout + proc.stderr)
        self.assertIn("calc.py", proc.stderr)
        self.assertIn("did not restore", proc.stderr)
        self.assertNotIn("adds", proc.stdout, "the run stops at the file that did not restore")
        self.assertEqual(self._snapshot(), before)
        self.assertEqual(self._status(), status)
        self.assertEqual(list(self.tmp.iterdir()), [])

    def test_an_edit_that_does_not_apply_is_reported_and_not_counted(self) -> None:
        """AC3. Absent, ambiguous and out-of-scope edits are reported with the reason and are
        neither killed nor survived; the rest of the list still runs; a malformed file is
        refused at exit 2 with nothing run."""
        absent = _entry("absent", "calc.py", "a ** b", "a - b", "tests/test_calc.py::test_add")
        twice = _entry("twice", "calc.py", "b", "c", "tests/test_calc.py::test_add")
        outside = _entry("outside", "other.py", "return 1", "return 2",
                         "tests/test_calc.py::test_add")
        escape = _entry("escape", "lib/../other.py", "return 1", "return 2",
                        "tests/test_calc.py::test_add")
        report_path = self.base / "report.json"
        proc = self._run(self._write_list([absent, twice, outside, escape, KILLED]), report_path)
        lines = proc.stdout.splitlines()
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertEqual(len(lines), 6, proc.stdout + proc.stderr)
        self.assertTrue(lines[0].startswith("absent not-applied: "), lines[0])
        self.assertIn("not in calc.py", lines[0])
        self.assertTrue(lines[1].startswith("twice not-applied: "), lines[1])
        self.assertIn("2 times", lines[1])
        self.assertTrue(lines[2].startswith("outside not-applied: "), lines[2])
        self.assertIn("not in US0001's Affects", lines[2])
        self.assertTrue(lines[3].startswith("escape not-applied: "), lines[3])
        self.assertIn("not in US0001's Affects", lines[3])
        self.assertTrue(lines[4].startswith("adds killed: "), lines[4])
        self.assertIn("killed 1, survived 0, not applied 4, error 0", lines[5])
        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["counts"],
                         {"killed": 1, "survived": 0, "not_applied": 4, "error": 0})
        self.assertEqual([m["result"] for m in report["mutants"]],
                         ["not-applied"] * 4 + ["killed"])
        self.assertTrue(all(m["reason"] for m in report["mutants"][:4]))
        # Not a JSON list of entries: refused at 2 with nothing run - no line, no report, and
        # no scratch copy made.
        for name, text in (("object.json", json.dumps({"mutants": [KILLED]})),
                           ("empty.json", "[]"),
                           ("broken.json", "[{\"file\": "),
                           ("entry.json", json.dumps([KILLED, "calc.py"]))):
            path = self.base / name
            path.write_text(text, encoding="utf-8")
            refused_report = self.base / f"refused-{name}"
            proc = subprocess.run(self._args(path, refused_report), capture_output=True,
                                  text=True, env=self._env(), timeout=120)
            self.assertEqual(proc.returncode, 2, f"{name}: {proc.stdout}{proc.stderr}")
            self.assertEqual(proc.stdout, "", name)
            self.assertIn(name, proc.stderr)
            self.assertFalse(refused_report.exists(), name)
            self.assertEqual(list(self.tmp.iterdir()), [], name)
        # The list's own mode: no unit to scope it, or a target or test command beside it.
        good = self._write_list([KILLED])
        unscoped = [a for a in self._args(good) if a not in ("--scope", "US0001")]
        for argv in (unscoped, self._args(good) + ["--test", "true"]):
            proc = subprocess.run(argv, capture_output=True, text=True, env=self._env(),
                                  timeout=120)
            self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
            self.assertIn("--edits", proc.stderr)
            self.assertEqual(proc.stdout, "")
            self.assertEqual(list(self.tmp.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
