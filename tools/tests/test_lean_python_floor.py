"""US0908: the skill's scripts run on the Python 3.10 it declares.

SKILL.md and README declare Python 3.10+, and `sprint_report.py` stopped parsing there: a
backslash inside an f-string replacement field is legal from 3.12 only, so the close and the
report broke for every consumer on 3.10 or 3.11. `tools/tests/test_test_noise.py` carried the
same construct. Nothing noticed, because every machine and CI ran 3.12 or newer.

The check needs the REAL interpreter. `ast.parse(source, feature_version=(3, 10))` under a newer
Python accepts the offending line, because the grammar change is in the tokenizer, which
`feature_version` does not wind back. So each test here runs `python3.10` (on PATH, or found by
`uv python find 3.10`), and with neither it skips naming why - except under CI, where a skip
would leave the floor unchecked on every push, so it fails instead.

This is not a commit lane (LC-008): the suite step in `.github/workflows/lint.yml` runs it once
per push, under the 3.10 a workflow step installs. Its place is earned by two parse failures at
the floor, one of which reached consumers (`sprint_report.py`:425; `test_test_noise.py` is
repo-only), and it replaces the per-commit floor checker US0811 proposed.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest import mock

import yaml

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"
WORKFLOW = REPO / ".github" / "workflows" / "lint.yml"
HOOKS = REPO / ".githooks"
FLOOR = (3, 10)
THIS_MODULE = "tools/tests/test_lean_python_floor.py"
#: The suite step's command, which collects this module - where the check runs in CI.
SUITE_RUN = "unittest discover -s tools/tests"

#: Compiles every path on stdin, prints one line per failure, then the count it compiled.
#: `compile` rather than `py_compile`: nothing is written into the tree.
_COMPILE_ALL = """
import sys
paths = sys.stdin.read().splitlines()
for p in paths:
    try:
        with open(p, "rb") as f:
            compile(f.read(), p, "exec", dont_inherit=True)
    except (SyntaxError, ValueError) as e:
        print(f"FAIL {p}:{getattr(e, 'lineno', '?')}: {getattr(e, 'msg', e)}")
print(f"COMPILED {len(paths)}")
"""


def _version(interpreter: str) -> tuple[int, int] | None:
    try:
        r = subprocess.run([interpreter, "-c", "import sys; print(*sys.version_info[:2])"],
                           capture_output=True, text=True, timeout=30)
    except OSError:
        return None
    parts = r.stdout.split()
    return (int(parts[0]), int(parts[1])) if r.returncode == 0 and len(parts) == 2 else None


def floor_interpreter() -> str | None:
    """A Python 3.10 interpreter, or None. Each candidate is asked its version, so a
    `python3.10` name pointing at something else is not trusted."""
    candidates = [shutil.which("python3.10")]
    uv = shutil.which("uv")
    if uv:
        r = subprocess.run([uv, "python", "find", "--no-project", "3.10"],
                           capture_output=True, text=True, timeout=60)
        candidates.append(r.stdout.strip() if r.returncode == 0 else None)
    return next((c for c in candidates if c and _version(c) == FLOOR), None)


def _under_ci() -> bool:
    return os.environ.get("CI", "").strip().lower() not in ("", "0", "false")


def _tracked_python_files() -> list[str]:
    out = subprocess.run(["git", "ls-files", "-z", "--", "*.py"], cwd=REPO,
                         capture_output=True, text=True, check=True).stdout
    return [p for p in out.split("\0") if p and (REPO / p).is_file()]


def _tracked_python_count() -> int:
    """The floor on the enumeration, counted a second way: every tracked path, filtered here
    rather than by pathspec, so narrowing the list the check compiles cannot also narrow this."""
    out = subprocess.run(["git", "ls-files", "-z"], cwd=REPO,
                         capture_output=True, text=True, check=True).stdout
    return sum(1 for p in out.split("\0") if p.endswith(".py") and (REPO / p).is_file())


def _shipped_scripts() -> list[Path]:
    return sorted([*SCRIPTS.glob("*.py"), *SCRIPTS.glob("hooks/*.py")])


def _shipped_script_count() -> int:
    return sum(1 for d in (SCRIPTS, SCRIPTS / "hooks") for n in os.listdir(d)
               if n.endswith(".py") and (d / n).is_file())


def _setup_python_versions(step: dict) -> list[str] | None:
    if "actions/setup-python" not in str(step.get("uses", "")):
        return None
    return str((step.get("with") or {}).get("python-version", "")).split()


def _installs_floor(step: dict) -> bool:
    return "3.10" in (_setup_python_versions(step) or [])


def _runs_on_push(job: dict) -> bool:
    guard = job.get("if")
    return guard is None or "push" in str(guard)


class PythonFloorTests(unittest.TestCase):

    def _interpreter(self) -> str:
        found = floor_interpreter()
        if found:
            return found
        why = ("no Python 3.10 interpreter: python3.10 is not on PATH and `uv python find "
               "3.10` found none, so the declared floor cannot be checked here")
        if _under_ci():
            self.fail(f"{why}. CI must install 3.10 (.github/workflows/lint.yml) - a skip "
                      "there would leave the floor unchecked on every push")
        self.skipTest(why)

    def test_every_tracked_file_compiles_under_3_10(self) -> None:
        interpreter = self._interpreter()
        paths = _tracked_python_files()
        for named in (".claude/skills/sdlc-studio/scripts/sprint_report.py",
                      "tools/tests/test_test_noise.py"):
            self.assertIn(named, paths)
        r = subprocess.run([interpreter, "-c", _COMPILE_ALL], input="\n".join(paths),
                           cwd=REPO, capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stderr)
        failures = [ln for ln in r.stdout.splitlines() if ln.startswith("FAIL ")]
        self.assertEqual(failures, [], "tracked files that do not compile under Python 3.10")
        self.assertIn(f"COMPILED {_tracked_python_count()}\n", r.stdout,
                      "the check compiled fewer files than git tracks")

    def test_every_shipped_script_starts_under_3_10(self) -> None:
        interpreter = self._interpreter()
        scripts = _shipped_scripts()
        self.assertIn(SCRIPTS / "sprint_report.py", scripts)

        with tempfile.TemporaryDirectory() as cwd:
            def start(script: Path) -> tuple[Path, subprocess.CompletedProcess]:
                return script, subprocess.run([interpreter, str(script), "--help"], cwd=cwd,
                                              capture_output=True, text=True, timeout=120)
            with ThreadPoolExecutor(max_workers=8) as pool:
                results = list(pool.map(start, scripts))
        self.assertEqual(len(results), _shipped_script_count(),
                         "the check started fewer scripts than scripts/ ships")
        failed = {str(s.relative_to(REPO)): (r.returncode, r.stderr.strip().splitlines()[-1:])
                  for s, r in results if r.returncode != 0}
        self.assertEqual(failed, {}, "shipped scripts whose --help fails under Python 3.10")

    def test_ci_runs_the_floor_check_once_under_3_10(self) -> None:
        workflow = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
        # PyYAML reads the bare key `on` as the boolean True.
        triggers = workflow.get("on", workflow.get(True)) or {}
        self.assertIn("main", (triggers.get("push") or {}).get("branches", []))

        jobs = workflow["jobs"]
        self.assertTrue(_runs_on_push(jobs["ci"]), "the ci job runs on push")
        # Every step, guarded or not: a guard of any kind on the 3.10 step means a push may
        # not install it, so it is refused rather than read as installed.
        steps = jobs["ci"].get("steps", [])
        floor = [i for i, s in enumerate(steps) if _installs_floor(s)]
        self.assertEqual(len(floor), 1, "the ci job installs Python 3.10 in exactly one step")
        self.assertNotIn("if", steps[floor[0]], "the 3.10 step runs on every push, unguarded")
        suite = [i for i, s in enumerate(steps) if SUITE_RUN in str(s.get("run", ""))]
        self.assertEqual(len(suite), 1, f"one ci step runs `{SUITE_RUN}`, which collects "
                         "this module")
        self.assertNotIn("if", steps[suite[0]], "the suite step runs on every push")
        self.assertLess(floor[0], suite[0], "3.10 is installed before the suite that checks it")
        # The default interpreter stays the newer one: the setup-python step that runs LAST
        # sets the default, so every other setup-python step comes after the 3.10 one.
        default = [i for i, s in enumerate(steps)
                   if _setup_python_versions(s) is not None and not _installs_floor(s)]
        self.assertTrue(default, "the ci job sets up a default Python besides 3.10")
        self.assertLess(floor[0], min(default), "3.10 is set up before the default Python")
        self.assertTrue((REPO / THIS_MODULE).is_file())

        # Once per push: no other job a push triggers installs 3.10 or runs the check, and no
        # step names this module beside the suite that already collects it.
        for name, job in jobs.items():
            named = [s for s in job.get("steps", [])
                     if "test_lean_python_floor" in str(s.get("run", ""))]
            self.assertEqual(named, [], f"{name} runs the floor module a second time")
            if name != "ci" and _runs_on_push(job):
                self.assertFalse(any(_installs_floor(s) for s in job.get("steps", [])),
                                 f"{name} also checks the floor on push")

        # A workflow step, not a commit lane.
        for hook in sorted(HOOKS.iterdir()):
            text = hook.read_text(encoding="utf-8", errors="replace")
            self.assertNotIn("test_lean_python_floor", text, hook.name)
            self.assertNotIn("python3.10", text, hook.name)

    def test_no_floor_interpreter_fails_under_ci_and_skips_naming_why_elsewhere(self) -> None:
        """AC1's CI clause, with the interpreter lookup forced empty: a runner that lost its
        3.10 install goes red, and a machine without one skips saying why - never passes,
        and never skips under CI."""
        module = sys.modules[__name__]
        probe = PythonFloorTests("test_every_tracked_file_compiles_under_3_10")

        def outcome(env: dict, found: str | None) -> tuple[str, str]:
            # Caught here, both kinds: a SkipTest escaping this test would skip IT, and a
            # skip is exactly the silent outcome the CI clause exists to refuse.
            with mock.patch.object(module, "floor_interpreter", return_value=found), \
                    mock.patch.dict(os.environ, env, clear=True):
                try:
                    return "ran", probe._interpreter()
                except unittest.SkipTest as e:
                    return "skip", str(e)
                except probe.failureException as e:
                    return "fail", str(e)

        without_ci = {k: v for k, v in os.environ.items() if k != "CI"}
        for ci in ("true", "1"):
            with self.subTest(CI=ci):
                kind, why = outcome(dict(without_ci, CI=ci), None)
                self.assertEqual(kind, "fail", why)
                self.assertIn("no Python 3.10 interpreter", why)
                self.assertIn("lint.yml", why)
        for ci in (None, "", "false", "0"):
            with self.subTest(CI=ci):
                kind, why = outcome(dict(without_ci, **({} if ci is None else {"CI": ci})), None)
                self.assertEqual(kind, "skip", why)
                self.assertIn("no Python 3.10 interpreter", why)
        # The positive control: with an interpreter found, neither happens.
        self.assertEqual(outcome(dict(without_ci, CI="true"), "/x/python3.10"),
                         ("ran", "/x/python3.10"))


if __name__ == "__main__":
    unittest.main()
