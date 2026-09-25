"""BG0770: CI's `python3 -m unittest discover -s tools/tests` agrees with the local pytest run.

CI runs the repo guards under unittest, in one process, in discover's order; the push gate runs
them under pytest, which imports each file as its own module. Two tests went red only on CI:

- `test_lean_refusal_log` imports `test_message_first_gate`'s `tearDownModule`, and under unittest
  the two share one module object, so the importer's teardown deleted the shared scripts template
  the gate module's own later tests still pointed at.
- `test_lean_tmp_hygiene` ran pytest with `-n 2`, and CI installs pytest without pytest-xdist.

Each test runs the REAL modules under `python3 -m unittest`, as CI does, in a subprocess.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TESTS = Path(__file__).resolve().parent

#: What makes an interpreter look like CI's, as a `sitecustomize` on PYTHONPATH: the path finder
#: cannot see `xdist`, so both `import xdist` and `find_spec("xdist")` (gate.py's probe) say it is
#: absent. pytest's entry-point loader would still import the plugin by name, so the addopts block
#: it, and `-n` is an unrecognised argument there as it is on CI.
NO_XDIST = '''\
import importlib.machinery

_find = importlib.machinery.PathFinder.find_spec


def _hide(cls, name, path=None, target=None):
    return None if name.partition(".")[0] == "xdist" else _find(name, path, target)


importlib.machinery.PathFinder.find_spec = classmethod(_hide)
'''
NO_XDIST_ADDOPTS = "-p no:xdist -p no:xdist.looponfail"


def _xdist_imports() -> bool:
    try:
        import xdist  # noqa: F401
    except ImportError:
        return False
    return True


def _unittest(*names: str, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-m", "unittest", "-v", *names], cwd=TESTS,
                          env={**os.environ, "SDLC_STUDIO_BOUNDARY_SUITE": "1", **(env or {})},
                          capture_output=True, text=True, timeout=600)


class CiUnittestRunTests(unittest.TestCase):

    def test_the_gate_fixture_survives_an_importers_teardown(self) -> None:
        """AC1. The importer runs first, as discover orders them, then every gate test must pass.
        MUTANT: HEAD's `tearDownModule`, which removes the template but leaves the global set."""
        order = ["test_lean_refusal_log", "test_message_first_gate"]
        self.assertEqual(sorted(order), order, "discover runs modules in sorted file order")
        proc = _unittest(*order)
        out = proc.stdout + proc.stderr
        self.assertEqual(0, proc.returncode, out)
        for module in order:            # both ran: the importer's teardown did fire in between
            self.assertIn(f"({module}.", out)
        self.assertNotIn("can't open file", out)

    def test_the_tmp_probe_skips_worker_runs_without_xdist(self) -> None:
        """AC2. Without xdist the three `-n 2` sessions are skipped, each named; with it they run.
        MUTANT: HEAD, whose `-n 2` sessions exit 4 on the usage error."""
        shim = Path(tempfile.mkdtemp(prefix="bg0770-"))
        self.addCleanup(shutil.rmtree, shim, True)
        (shim / "sitecustomize.py").write_text(NO_XDIST, encoding="utf-8")
        path = os.pathsep.join(p for p in (str(shim), os.environ.get("PYTHONPATH")) if p)
        proc = _unittest("test_lean_tmp_hygiene",
                         env={"PYTHONPATH": path, "PYTEST_ADDOPTS": NO_XDIST_ADDOPTS})
        out = proc.stdout + proc.stderr
        self.assertEqual(0, proc.returncode, out)
        self.assertIn("OK (skipped=3)", out)
        # `-v` prints the subtest's parameters, then (on the next line) its docstring's first line.
        skipped = re.findall(r"workers=\['-n', '2'\]\)(?:\n.*?)? \.\.\. skipped '([^']*)'", out)
        self.assertEqual(3, len(skipped), out)
        self.assertTrue(all("pytest-xdist" in reason for reason in skipped), skipped)

        with self.subTest("where xdist imports, the -n 2 sessions still run"):
            if not _xdist_imports():
                self.skipTest("pytest-xdist is not installed, so only the skip can be shown here")
            proc = _unittest("test_lean_tmp_hygiene")
            out = proc.stdout + proc.stderr
            self.assertEqual(0, proc.returncode, out)
            self.assertNotIn("skipped", out)


if __name__ == "__main__":
    unittest.main()
