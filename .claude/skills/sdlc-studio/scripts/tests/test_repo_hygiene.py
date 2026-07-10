"""Test-suite hygiene guards (CR0204/US0114).

A mid-file `if __name__` guard silently drops every class below it on a direct
`python3 test_x.py` run (22 tests once vanished while reporting OK) and invites
append-truncation. The guard must be the LAST top-level statement of every test file.
"""
from __future__ import annotations

import ast
import re
import subprocess
import sys
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent


def _guard_index(tree: ast.Module) -> int | None:
    """Index of the `if __name__ == "__main__"` statement in the module body, or None."""
    for i, node in enumerate(tree.body):
        if (isinstance(node, ast.If) and isinstance(node.test, ast.Compare)
                and isinstance(node.test.left, ast.Name) and node.test.left.id == "__name__"):
            return i
    return None


class GuardAtEofTests(unittest.TestCase):
    def test_every_main_guard_is_the_last_statement(self) -> None:
        offenders = []
        for p in sorted(TESTS_DIR.glob("test_*.py")):
            tree = ast.parse(p.read_text(encoding="utf-8"))
            gi = _guard_index(tree)
            if gi is not None and gi != len(tree.body) - 1:
                after = [type(n).__name__ for n in tree.body[gi + 1:]]
                offenders.append(f"{p.name}: guard at statement {gi}, followed by {after}")
        self.assertEqual(offenders, [],
                         "mid-file __main__ guards silently drop the classes below them "
                         "on direct runs - move the guard to true end-of-file:\n"
                         + "\n".join(offenders))


class DirectRunParityTests(unittest.TestCase):
    def test_direct_run_count_equals_discover_count(self) -> None:
        # The historical liar: a direct run of test_validate.py once executed 49 of 71
        # tests and reported OK. Post-normalisation the two counts must agree.
        target = TESTS_DIR / "test_validate.py"

        def ran(cmd: list[str]) -> int:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=120,
                               cwd=str(TESTS_DIR.parent.parent.parent.parent.parent))
            m = re.search(r"Ran (\d+) tests?", r.stderr + r.stdout)
            self.assertIsNotNone(m, (r.stderr + r.stdout)[-500:])
            return int(m.group(1))

        direct = ran([sys.executable, str(target)])
        discover = ran([sys.executable, "-m", "unittest", "discover",
                        "-s", ".claude/skills/sdlc-studio/scripts/tests",
                        "-p", "test_validate.py"])
        self.assertEqual(direct, discover)


if __name__ == "__main__":
    unittest.main()
