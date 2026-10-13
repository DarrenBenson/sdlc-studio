"""BG0978: the pre-push hook tests' stub PATH runs the interpreter the tests run under, with its
packages, so the push gate can pass where pytest lives only in a virtualenv.

`_Clone.stub_path` once symlinked `shutil.which("python3")` into a temporary directory. A
virtualenv's interpreter finds its packages through the `pyvenv.cfg` beside the path it was
started as, so started through that symlink it ran as the bare base interpreter, and the hook's
gate reported 'No module named pytest'. The same fault turned a gate host's first push gate red.

The test builds its own venv-shaped interpreter (`venv --without-pip`, so no network and no pip),
puts a marker module in its site-packages only, and runs the fixture under it: the stub PATH's
`python3` must import the marker. MUTANT: the stub `python3` a symlink to the interpreter again.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

TESTS = Path(__file__).resolve().parent

PROBE = textwrap.dedent('''
    import shutil, subprocess, sys
    sys.path.insert(0, {tests!r})
    import test_pre_push_hook as hook
    clone = hook._Clone()
    try:
        stub = clone.stub_path()
        r = subprocess.run([str(stub / "python3"), "-c", "import bg0978_marker"],
                           capture_output=True, text=True, env={{"PATH": str(stub)}})
        print(r.returncode)
        print(r.stderr.strip()[-300:])
    finally:
        shutil.rmtree(clone.tmp, ignore_errors=True)
''')


class StubInterpreterTests(unittest.TestCase):
    def test_stub_path_keeps_the_running_interpreter(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            venv = Path(d) / "venv"
            subprocess.run([sys.executable, "-m", "venv", "--without-pip", str(venv)],
                           check=True, capture_output=True, timeout=120)
            python = venv / "bin" / "python3"
            site = subprocess.run([str(python), "-c",
                                   "import sysconfig; print(sysconfig.get_paths()['purelib'])"],
                                  check=True, capture_output=True, text=True).stdout.strip()
            (Path(site) / "bg0978_marker.py").write_text("OK = 1\n", encoding="utf-8")
            control = subprocess.run([str(python), "-c", "import bg0978_marker"],
                                     capture_output=True, text=True)
            self.assertEqual(0, control.returncode, "the venv cannot import its own marker")
            base = shutil.which("python3", path="/usr/bin:/bin") or sys.executable
            bare = subprocess.run([base, "-c", "import bg0978_marker"], capture_output=True,
                                  text=True)
            self.assertNotEqual(0, bare.returncode,
                                "the base interpreter sees the marker, so the test proves nothing")
            env = {**os.environ, "PATH": f"{venv / 'bin'}{os.pathsep}{os.environ.get('PATH', '')}"}
            env.pop("PYTHONPATH", None)
            r = subprocess.run([str(python), "-c", PROBE.format(tests=str(TESTS))],
                               capture_output=True, text=True, env=env, timeout=300)
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            rc, _, err = r.stdout.partition("\n")
            self.assertEqual("0", rc.strip(),
                             f"the stub PATH's python3 lost the running interpreter's "
                             f"packages: {err}")


if __name__ == "__main__":
    unittest.main()
