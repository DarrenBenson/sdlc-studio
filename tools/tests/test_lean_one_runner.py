"""US0939: CI and the push gate give one verdict on tools/tests, because both run it the same way.

The push's `full-suite` lane runs tools/tests under pytest (xdist, the `serial_only` tests after);
CI ran them under `python3 -m unittest discover` in one process. Each runner hides a class the
other shows, so a push the gate passed went red on CI for a runner difference alone (BG0770: a
module global shared between importers is shared only under unittest). CI moves to the push's
runner rather than the push to CI's: the push stays as it is, and one runner is deleted.

The skill tree stays on unittest in CI (`tools/skill-tests.sh`), because the coverage gate and
the test-noise gate read that run.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
WORKFLOW = REPO / ".github" / "workflows" / "lint.yml"
PACKAGE = REPO / "package.json"
RUN_SUITE = REPO / "tools" / "run-suite.sh"
GATE_REL = ".claude/skills/sdlc-studio/scripts/gate.py"
GATE = REPO / GATE_REL

#: The push's plan for tools/tests, as CI and the local runners spell it.
PUSH_PLAN = "gate.py --boundary push --run-tests tools/tests/test_*.py"
#: The runner this story retires for tools/tests.
RETIRED = "unittest discover -s tools/tests"


def _ci_steps() -> list[dict]:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))["jobs"]["ci"]["steps"]


def _all_runs() -> list[str]:
    jobs = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))["jobs"]
    return [str(s.get("run", "")) for job in jobs.values() for s in job.get("steps", [])]


def _suite_index(steps: list[dict]) -> int:
    found = [i for i, s in enumerate(steps) if PUSH_PLAN in str(s.get("run", ""))]
    if len(found) != 1:
        raise AssertionError(f"expected one ci step running `{PUSH_PLAN}`, found {len(found)}")
    return found[0]


def _ci_tools_command() -> str:
    """The command CI runs over tools/tests: the suite step's lines that name the tree."""
    for step in _ci_steps():
        lines = [ln.strip() for ln in str(step.get("run", "")).splitlines()
                 if "tools/tests" in ln and not ln.strip().startswith("#")]
        if lines:
            return " && ".join(lines)
    raise AssertionError("no ci step runs tools/tests")


def _run_suite_cases() -> dict[str, str]:
    """`tools/run-suite.sh`'s `<suite>) CMD=...` lines, keyed by suite, with each `$NAME` the
    script assigns on a line of its own (`NAME='...'`) expanded to that value."""
    text = RUN_SUITE.read_text(encoding="utf-8")
    assigned = dict(re.findall(r"^([A-Z_]+)='([^'\n]*)'\s*$", text, re.M))

    def expand(command: str) -> str:
        return re.sub(r"\$\{?([A-Z_]+)\}?", lambda m: assigned.get(m.group(1), m.group(0)),
                      command)
    return {m.group(1): expand(m.group(2)) for m in
            re.finditer(r"^\s*(scripts|tools|all)\)\s*CMD=(.*?);;\s*$", text, re.M)}


def _clean_env(**extra: str) -> dict:
    env = {k: v for k, v in os.environ.items()
           if not k.startswith("GIT_") and k != "SDLC_GATE_BOUNDARY"}
    env["PATH"] = os.pathsep.join([str(Path(sys.executable).parent), env.get("PATH", "")])
    env.update(extra)
    return env


def _project(root: Path) -> Path:
    """A project shaped like this one for the runners: its pytest config and both conftests."""
    tests = root / "tools" / "tests"
    tests.mkdir(parents=True)
    (root / "sdlc-studio").mkdir()      # the gate reads a project here
    for rel in ("pytest.ini", "conftest.py", "tools/tests/conftest.py"):
        shutil.copy2(REPO / rel, root / rel)
    return tests


#: BG0770's pair. The gate module keeps a shared template in a module global and its teardown
#: deletes the directory WITHOUT forgetting it; the importer (first in discover's order) runs
#: that teardown on whatever module object `import test_bg_gate` gives it. Each test records that
#: it ran, so a run that collected nothing cannot agree by accident.
_GATE_MODULE = '''\
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_TEMPLATE = None


def template():
    global _TEMPLATE
    if _TEMPLATE is None:
        _TEMPLATE = ROOT / "shared-template"
        _TEMPLATE.mkdir(exist_ok=True)
    return _TEMPLATE


def ran(name):
    with open(ROOT / "ran.log", "a", encoding="utf-8") as fh:
        fh.write(name + "\\n")


def tearDownModule():
    if _TEMPLATE is not None:
        import shutil
        shutil.rmtree(_TEMPLATE, ignore_errors=True)


class GateTests(unittest.TestCase):
    def test_template_is_there(self):
        ran("gate")
        self.assertTrue(template().is_dir(), "the shared template was deleted under us")
'''

_IMPORTER_MODULE = '''\
import unittest

from test_bg_gate import ran, tearDownModule, template  # noqa: F401 - the shared teardown


class ImporterTests(unittest.TestCase):
    def test_uses_the_template(self):
        ran("importer")
        self.assertTrue(template().is_dir())
'''


class OneRunnerTests(unittest.TestCase):

    def test_ci_and_local_run_tools_tests_through_the_push_plan(self) -> None:
        """AC1. CI, `npm run test:tools` and `run-suite.sh tools|all` all run the push's plan,
        and nothing runs tools/tests under unittest discover.
        MUTANT: HEAD, or changing CI alone - the local commands still say unittest."""
        steps = _ci_steps()
        suite = steps[_suite_index(steps)]
        self.assertNotIn("if", suite, "the suite step runs on every push")
        self.assertIn(f"python3 {GATE_REL.replace('gate.py', '')}{PUSH_PLAN}", suite["run"])
        for run in _all_runs():
            self.assertNotIn(RETIRED, run, "a workflow step still runs tools/tests under unittest")

        scripts = json.loads(PACKAGE.read_text(encoding="utf-8"))["scripts"]
        self.assertIn(PUSH_PLAN, scripts["test:tools"])
        self.assertIn("npm run test:tools", scripts["test"])
        for name, command in scripts.items():
            self.assertNotIn(RETIRED, command, f"package.json {name}")

        cases = _run_suite_cases()
        for suite_name in ("tools", "all"):
            self.assertIn(PUSH_PLAN, cases.get(suite_name, ""), f"run-suite.sh {suite_name}")
        live = [ln for ln in RUN_SUITE.read_text(encoding="utf-8").splitlines()
                if not ln.lstrip().startswith("#")]
        self.assertFalse([ln for ln in live if RETIRED in ln],
                         "run-suite.sh still runs tools/tests under unittest")

    def test_ci_and_push_agree_on_a_shared_global_fixture(self) -> None:
        """AC2. Over BG0770's pair, CI's command (read from lint.yml) and the push's full-suite
        lane return the same verdict. The control shows the pair still splits the two runners
        the old CI step used, so agreement here is the runner, not a fixture that never fails.
        MUTANT: HEAD's CI command, `unittest discover`, which is red where the push is green."""
        with tempfile.TemporaryDirectory(prefix="us0939-") as tmp:
            root = Path(tmp)
            tests = _project(root)
            (tests / "test_bg_gate.py").write_text(_GATE_MODULE, encoding="utf-8")
            (tests / "test_a_importer.py").write_text(_IMPORTER_MODULE, encoding="utf-8")
            log = root / "ran.log"
            env = _clean_env(SDLC_STUDIO_BOUNDARY_SUITE="1")

            def verdict(argv: list[str]) -> tuple[bool, str]:
                log.unlink(missing_ok=True)
                cp = subprocess.run(argv, cwd=root, env=env, capture_output=True, text=True,
                                    timeout=600)
                out = cp.stdout + cp.stderr
                ran = sorted(set(log.read_text(encoding="utf-8").split())) if log.exists() else []
                self.assertEqual(["gate", "importer"], ran, f"both tests ran:\n{out}")
                return cp.returncode == 0, out

            ci_command = _ci_tools_command().replace(GATE_REL, str(GATE))
            ci_green, ci_out = verdict(["bash", "-c", ci_command])
            push_green, push_out = verdict([sys.executable, str(GATE), "--root", str(root),
                                            "--boundary", "push", "--only", "full-suite"])
            self.assertEqual(push_green, ci_green,
                             f"CI and the push disagree.\nCI ({ci_command}):\n{ci_out}\n"
                             f"push:\n{push_out}")

            with self.subTest("control: the pair splits unittest discover from the push"):
                old_green, old_out = verdict(["bash", "-c", f"python3 -m {RETIRED}"])
                self.assertNotEqual(push_green, old_green, old_out)

    def test_a_boundary_run_keeps_boundary_only_tests(self) -> None:
        """AC3. `--run-tests` at `--boundary push` runs the `boundary_only` tests; without a
        boundary (a commit's selection) they are still left to the push.
        MUTANT: `cmd_run_tests` passing `commit=True` whatever the boundary."""
        with tempfile.TemporaryDirectory(prefix="us0939-") as tmp:
            root = Path(tmp)
            tests = _project(root)
            (tests / "test_marked.py").write_text(
                "from pathlib import Path\n\nimport pytest\n\n"
                "ROOT = Path(__file__).resolve().parents[2]\n\n\n"
                "@pytest.mark.boundary_only\n"
                "def test_deferred():\n    (ROOT / 'deferred.ran').write_text('1')\n\n\n"
                "def test_plain():\n    (ROOT / 'plain.ran').write_text('1')\n",
                encoding="utf-8")

            def run(*boundary: str) -> subprocess.CompletedProcess:
                for name in ("deferred.ran", "plain.ran"):
                    (root / name).unlink(missing_ok=True)
                return subprocess.run([sys.executable, str(GATE), "--root", str(root),
                                       *boundary, "--run-tests", "tools/tests/test_marked.py"],
                                      cwd=root, env=_clean_env(), capture_output=True,
                                      text=True, timeout=300)

            cp = run("--boundary", "push")
            self.assertEqual(0, cp.returncode, cp.stdout + cp.stderr)
            self.assertTrue((root / "plain.ran").exists())
            self.assertTrue((root / "deferred.ran").exists(),
                            f"a push-boundary run dropped the boundary_only test:\n{cp.stdout}")

            cp = run()
            self.assertEqual(0, cp.returncode, cp.stdout + cp.stderr)
            self.assertTrue((root / "plain.ran").exists())
            self.assertFalse((root / "deferred.ran").exists(),
                             "a commit's selection ran a boundary_only test")

    def test_ci_installs_xdist_before_the_suite(self) -> None:
        """AC4. pytest-xdist is installed, unguarded, before the suite step, so the `-n 2`
        variants of `test_lean_tmp_hygiene` run in CI rather than skip.
        MUTANT: the install line without `pytest-xdist`, or installed after the suite."""
        steps = _ci_steps()
        suite = _suite_index(steps)
        installs = [i for i, s in enumerate(steps)
                    if re.search(r"pip install\b[^\n]*(?<![\w-])pytest-xdist\b",
                                 str(s.get("run", "")))]
        self.assertTrue(installs, "no ci step installs pytest-xdist")
        self.assertLess(installs[0], suite, "pytest-xdist is installed after the suite runs")
        self.assertNotIn("if", steps[installs[0]], "the xdist install runs on every push")


if __name__ == "__main__":
    unittest.main()
