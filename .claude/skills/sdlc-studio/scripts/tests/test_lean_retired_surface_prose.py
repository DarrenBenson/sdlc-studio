"""BG0896: migrate's retired-surface scan does not read ordinary prose as a retired command.

The shipped scanner made a script's `.py` optional, so 'We run a mutation audit every quarter.'
in a consuming project's docs was reported as naming the retired `mutation.py audit`. The
consumer scan now names a script only as a command is written: with its `.py`, or inside a code
span. This repository's own doc tests keep the stricter bare-name reading (`derived()`).
Driven through the shipped `migrate.py` against a throwaway project.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/retired_surface.py
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent

_README = ("# Operations\n\n"
           "We run a mutation audit every quarter.\n"
           "`mutation.py audit`\n"
           "Then run mutation.py audit by hand.\n"
           "Or `mutation audit` from the skill.\n"
           "Walk the sprint preflight checklist first.\n")


def _py(*argv: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", *argv], capture_output=True, text=True,
                          check=False, timeout=300)


class RetiredSurfaceProseTests(unittest.TestCase):
    """AC1."""

    def test_prose_without_the_script_name_is_not_surface(self) -> None:
        """AC1. MUTANT: HEAD's optional `.py` - line 3 (and the preflight prose on line 7) are
        named too. The controls: the script with its `.py` (lines 4 and 5) and the bare name in a
        code span (line 6) are still named."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "p"
            root.mkdir()
            proc = _py(str(SCRIPTS / "init.py"), "run", "--root", str(root))
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            (root / "README.md").write_text(_README, encoding="utf-8")
            proc = _py(str(SCRIPTS / "migrate.py"), "--root", str(root))
            out = proc.stdout + proc.stderr
            self.assertEqual(0, proc.returncode, out)
            named = sorted(int(ln.split("README.md:", 1)[1].split()[0])
                           for ln in out.splitlines() if "README.md:" in ln)
            self.assertEqual([4, 5, 6], named, out)


if __name__ == "__main__":
    unittest.main()
