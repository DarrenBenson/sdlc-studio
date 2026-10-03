"""BG0925: migrate's retired-surface scan names a bare retired command inside a fenced code block.

BG0896 made the consumer scan name a bare script name only inside a code span, so a runbook's
bash fence holding `mutation audit` was no longer named, where the scan before it named it. A
fenced block is code: its lines count as a span does, and prose beside it stays unnamed.
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

_README = ("# Runbook\n"
           "\n"
           "Run mutation audit by hand.\n"
           "\n"
           "```bash\n"
           "mutation audit\n"
           "```\n"
           "\n"
           "Then mutation audit again.\n"
           "\n"
           "~~~\n"
           "  sprint preflight --root .\n"
           "~~~\n")


def _py(*argv: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", *argv], capture_output=True, text=True,
                          check=False, timeout=300)


class RetiredSurfaceFencedTests(unittest.TestCase):
    """AC1."""

    def test_a_fenced_bare_command_is_named(self) -> None:
        """AC1. MUTANT: 569c10e3's span-only reading - neither fenced line (6, 12) is named. The
        controls: the same name in prose before the fence (3) and after it closes (9) is not."""
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
            self.assertEqual([6, 12], named, out)


if __name__ == "__main__":
    unittest.main()
