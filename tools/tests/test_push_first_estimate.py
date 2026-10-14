"""US1006: the push's first-run cost line says what it does not know, instead of a fixed figure.

With no recorded boundary run the hook printed "expect about five minutes" (fifteen at a tag), a
figure measured on another machine that read 26 to 64 minutes on a busy one. The line
now says what this clone and interpreter decide: that no run is recorded here, how many test
modules the suite holds, whether they run in parallel (pytest-xdist present) or serially, and,
when this clone has timed a full commit-suite run, that median as a floor for this machine.

Each test drives the tracked hook through `test_pre_push_hook._Clone`; what is installed is the
test's choice (a `*.dist-info` first on PYTHONPATH, or a `sitecustomize` hiding it).

MUTANTS: the literals restored, a reworded figure ("expect five minutes", "about an hour")
appended, or the hook's own fallback given one (AC1); `in parallel` hard-coded, or the module count
a fixed figure or a count of every `.py` file (AC2); the clone's own full commit-suite series
ignored, its mean cited for its median, or a fixed figure added beside the floor (AC3); AGENTS.md's
figure left in or reworded (AC4); `first-run` speaking beside a recorded history; the counted
directories drifting from the gate's.
"""
# test-census-subject: .githooks/pre-push
from __future__ import annotations

import ast
import json
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_pre_push_hook as hook  # noqa: E402 - the hook's fixture, shared

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))
import gate_timing  # noqa: E402 - the tool under test

#: Any statement of a duration: a time unit named at all ("five minutes", "about an hour"), or a
#: number carrying one ("300s", "5 min"). The no-history line states none, so any is a fixed figure.
FIXED_FIGURE = re.compile(r"\b(?:seconds?|secs?|minutes?|mins?|hours?|hrs?)\b"
                          r"|\d+(?:\.\d+)?\s*(?:s|m|h)\b", re.I)

HIDE_XDIST = textwrap.dedent('''
    import importlib.metadata as _m
    _version = _m.version
    def version(name):
        if name.lower() == "pytest-xdist":
            raise _m.PackageNotFoundError(name)
        return _version(name)
    _m.version = version
''')


class FirstRunEstimateTests(unittest.TestCase):
    def _clone(self, timings: dict | None = None) -> hook._Clone:
        fx = hook._Clone(no_timings_file=True)
        self.addCleanup(fx.cleanup)
        for rel in (".claude/skills/sdlc-studio/scripts/tests/test_a.py",
                    ".claude/skills/sdlc-studio/scripts/tests/test_b.py",
                    "tools/tests/test_c.py",
                    # not test modules, so not counted
                    ".claude/skills/sdlc-studio/scripts/tests/conftest.py",
                    "tools/tests/_helpers.py"):
            path = fx.clone / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("import unittest\n", encoding="utf-8")
        shutil.copy(REPO / "tools" / "gate_prereqs.py", fx.clone / "tools" / "gate_prereqs.py")
        hook._git(fx.clone, "add", "-A")
        hook._git(fx.clone, "commit", "-q", "-m", "three test modules and the prerequisite check")
        if timings is not None:
            local = fx.clone / "sdlc-studio" / ".local"
            local.mkdir(parents=True, exist_ok=True)
            (local / "gate-timings.json").write_text(json.dumps(timings), encoding="utf-8")
        return fx

    def _pythonpath(self, xdist: bool) -> str:
        d = Path(tempfile.mkdtemp(prefix="first_estimate_"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        if xdist:
            info = d / "pytest_xdist-3.6.0.dist-info"
            info.mkdir()
            (info / "METADATA").write_text("Metadata-Version: 2.1\nName: pytest-xdist\n"
                                           "Version: 3.6.0\n", encoding="utf-8")
        else:
            (d / "sitecustomize.py").write_text(HIDE_XDIST, encoding="utf-8")
        return str(d)

    def _cost_line(self, fx: hook._Clone, *refspec: str, xdist: bool = True) -> str:
        env = {"STUB_ARGV": str(fx.argv), "STUB_RC": "1", "PATH": str(fx.stub_path()),
               "STUB_GH_MODE": "empty", "STUB_GH_ARGV": str(fx.tmp / "gh-argv.txt"),
               "PYTHONPATH": self._pythonpath(xdist)}
        r = hook._git(fx.clone, "push", "-q", "origin", *(refspec or ("main",)), check=False,
                      env=env)
        line = next((ln for ln in r.stderr.splitlines() if "Bypass once with" in ln), "")
        self.assertTrue(line, f"no cost line was announced:\n{r.stderr}")
        return line

    def test_no_fixed_duration_is_announced_without_a_recorded_run(self) -> None:
        fx = self._clone()
        branch = self._cost_line(fx)
        self.assertIn("boundary-push: no run is recorded on this clone", branch)
        self.assertIsNone(FIXED_FIGURE.search(branch), branch)
        hook._git(fx.clone, "tag", "v0.0.2")
        tag = self._cost_line(fx, "v0.0.2")
        self.assertIn("boundary-release: no run is recorded on this clone", tag)
        self.assertIsNone(FIXED_FIGURE.search(tag), tag)

    def test_the_cost_line_reads_parallel_or_serial_from_the_interpreter(self) -> None:
        # A clone each: the first push records its boundary run, which the second would read.
        serial = self._cost_line(self._clone(), xdist=False)
        self.assertIn("serially (pytest-xdist is not installed) over 3 test module(s)", serial)
        parallel = self._cost_line(self._clone(), xdist=True)
        self.assertIn("in parallel across this machine's cores (pytest-xdist, -n auto) over 3 test "
                      "module(s)", parallel)

    def test_a_recorded_full_commit_suite_run_is_cited_as_a_floor(self) -> None:
        # skewed, so the median (400) and the mean (900) differ
        fx = self._clone(timings={"total": [300.0, 400.0, 2000.0]})
        line = self._cost_line(fx)
        self.assertIn("boundary-push: no run is recorded on this clone", line)
        self.assertIn("this clone's full commit-suite runs took a median of 400s, a floor", line)
        self.assertIsNone(FIXED_FIGURE.search(line.replace("a median of 400s", "")),
                          f"a figure beside the floor:\n{line}")

    def test_agents_md_names_the_command_not_a_figure(self) -> None:
        text = (REPO / "AGENTS.md").read_text(encoding="utf-8")
        row = next(ln for ln in text.splitlines() if ln.startswith("| pre-push hook |"))
        # a command's own flags (`--warn-seconds`) are not a stated duration
        self.assertIsNone(FIXED_FIGURE.search(re.sub(r"`[^`]*`", "", row)), row)
        self.assertIn("gate_timing.py estimate --suite boundary-push", row)
        r = subprocess.run([sys.executable, "tools/gate_timing.py", "estimate", "--suite",
                            "boundary-push", "--warn-seconds", "0"], cwd=REPO,
                           capture_output=True, text=True, timeout=60, check=False)
        self.assertEqual(0, r.returncode, r.stderr)


    def test_the_hook_falls_back_to_a_line_without_a_figure(self) -> None:
        """The hook's own fallback, reached when `first-run` prints nothing (a clone whose
        gate_timing.py predates it)."""
        fx = self._clone()
        (fx.clone / "tools" / "gate_timing.py").write_text("import sys\nsys.exit(0)\n",
                                                           encoding="utf-8")
        hook._git(fx.clone, "commit", "-q", "-am", "a gate_timing that says nothing")
        line = self._cost_line(fx)
        self.assertIn("pre-push: boundary-push: no run is recorded on this clone. Bypass", line)
        self.assertIsNone(FIXED_FIGURE.search(line), line)

    def test_first_run_is_silent_beside_a_recorded_history(self) -> None:
        root = Path(tempfile.mkdtemp(prefix="first_run_history_"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        argv = [sys.executable, str(REPO / "tools" / "gate_timing.py"), "--root", str(root),
                "first-run", "--suite", "boundary-push"]
        bare = subprocess.run(argv, capture_output=True, text=True, timeout=60, check=False)
        self.assertIn("no run is recorded on this clone", bare.stdout, bare.stderr)
        local = root / "sdlc-studio" / ".local"
        local.mkdir(parents=True)
        (local / "gate-timings.json").write_text(json.dumps({"boundary-push": [900.0]}),
                                                 encoding="utf-8")
        seeded = subprocess.run(argv, capture_output=True, text=True, timeout=60, check=False)
        self.assertEqual(("", 0), (seeded.stdout, seeded.returncode), seeded.stderr)

    def test_the_counted_directories_are_the_gates(self) -> None:
        gate = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts" / "gate.py"
        tree = ast.parse(gate.read_text(encoding="utf-8"))
        dirs = next(ast.literal_eval(node.value) for node in tree.body
                    if isinstance(node, ast.Assign)
                    and any(getattr(t, "id", "") == "TEST_SUITE_DIRS" for t in node.targets))
        self.assertEqual(tuple(dirs), gate_timing.SUITE_DIRS)


if __name__ == "__main__":
    unittest.main()
