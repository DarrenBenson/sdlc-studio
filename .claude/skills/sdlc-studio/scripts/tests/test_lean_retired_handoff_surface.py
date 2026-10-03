"""BG0929: migrate names the retired handoff surface in a project's own docs.

6.1 retired the handoff writers (`handoff.py generate`, `artifact.py new --type handoff`) and
`gate.py --require-handoff`, but none of them sat where migrate's retired-surface scan reads
retirements, so a 6.0 runbook still running them was never named. The verb is registered in
`handoff.py`'s `RETIRED_VERBS` and the two flags in a `#### Retired flags` table, and each
named line carries what replaced the surface. Driven through the shipped `migrate.py` against a
throwaway project.
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
           "We read the last handoff before planning, and the handoff writers wrote it.\n"
           "\n"
           "At the close run `handoff.py generate --title \"Sprint 3\"`.\n"
           "\n"
           "```bash\n"
           "python3 scripts/artifact.py new --type handoff --title \"Sprint 3\"\n"
           "python3 scripts/gate.py --release --require-handoff HO0003\n"
           "```\n")

#: README line -> (the surface it must be named for, a phrase of what replaced it).
_EXPECTED = {
    5: ("handoff.py generate", "sprint.py plan --worklist RPTxxxx"),
    8: ("artifact.py new --type handoff", "sprint.py plan --worklist RPTxxxx"),
    9: ("gate.py --require-handoff", "sprint.py sign"),
}


def _py(*argv: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", *argv], capture_output=True, text=True,
                          check=False, timeout=300)


class RetiredHandoffSurfaceTests(unittest.TestCase):
    """AC1."""

    def test_the_retired_handoff_surface_is_named(self) -> None:
        """AC1. MUTANT: HEAD's scan, which names none of lines 5, 8 and 9 (no `RETIRED_VERBS`
        entry in handoff.py, no retired-flag row for either flag). MUTANT: a named line with no
        replacement (the detail as it read before, `names the retired X - edit it`). The
        control: line 3 names handoffs in prose and is not reported."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "p"
            root.mkdir()
            proc = _py(str(SCRIPTS / "init.py"), "run", "--root", str(root))
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            (root / "README.md").write_text(_README, encoding="utf-8")
            proc = _py(str(SCRIPTS / "migrate.py"), "--root", str(root))
            out = proc.stdout + proc.stderr
            self.assertEqual(0, proc.returncode, out)
            named = {int(ln.split("README.md:", 1)[1].split()[0]): ln
                     for ln in out.splitlines() if "README.md:" in ln}
            self.assertEqual(sorted(_EXPECTED), sorted(named), out)
            for line, (surface, replacement) in _EXPECTED.items():
                with self.subTest(line=line):
                    self.assertIn(f"`{surface}`", named[line])
                    self.assertIn(replacement, named[line].split(f"`{surface}`", 1)[1])


if __name__ == "__main__":
    unittest.main()
