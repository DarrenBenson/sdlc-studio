"""Unit tests for tools/check_budgets.py (line-budget guard).

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path

# tools/ lives at the repo root, six parents up from this test file.
TOOLS = Path(__file__).resolve().parents[1] / "check_budgets.py"
_spec = importlib.util.spec_from_file_location("check_budgets", TOOLS)
assert _spec and _spec.loader
check_budgets = importlib.util.module_from_spec(_spec)
sys.modules["check_budgets"] = check_budgets
_spec.loader.exec_module(check_budgets)


def _skill(root: Path, skill_lines=100) -> Path:
    sd = root / ".claude/skills/sdlc-studio"
    sd.mkdir(parents=True)
    (sd / "SKILL.md").write_text("x\n" * skill_lines)
    return sd


class BudgetTests(unittest.TestCase):
    def setUp(self) -> None:
        # the checker prints its report to stdout and findings to stderr; tests assert on
        # the exit code, so capture both to keep the unittest summary clean
        self._silence = contextlib.ExitStack()
        self._silence.enter_context(contextlib.redirect_stdout(io.StringIO()))
        self._silence.enter_context(contextlib.redirect_stderr(io.StringIO()))

    def tearDown(self) -> None:
        self._silence.close()

    def test_small_files_pass(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            sd = _skill(Path(d))
            (sd / "reference-a.md").write_text("x\n" * 200)
            self.assertEqual(check_budgets.main(["--root", d]), 0)

    def test_skill_md_over_budget_fails(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            _skill(Path(d), skill_lines=520)
            self.assertEqual(check_budgets.main(["--root", d]), 1)

    def test_unallowlisted_reference_over_600_fails(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            sd = _skill(Path(d))
            (sd / "reference-huge.md").write_text("x\n" * 700)
            self.assertEqual(check_budgets.main(["--root", d]), 1)

    def test_allowlisted_file_within_ceiling_passes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            sd = _skill(Path(d))
            (sd / "reference-epic.md").write_text("x\n" * 1052)
            self.assertEqual(check_budgets.main(["--root", d]), 0)

    def test_allowlisted_file_over_ceiling_tolerance_fails(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            sd = _skill(Path(d))
            ceiling = check_budgets.ALLOWLIST["reference-epic.md"]
            (sd / "reference-epic.md").write_text("x\n" * int(ceiling * 1.10))
            self.assertEqual(check_budgets.main(["--root", d]), 1)

    def test_real_repo_passes(self) -> None:
        repo = Path(__file__).resolve().parents[2]
        self.assertEqual(check_budgets.main(["--root", str(repo)]), 0)


class ReferenceSprintCeilingTests(unittest.TestCase):
    """The line ceiling admits the shipped file exactly, with no slack.

    A ceiling raised with headroom stops noticing growth: the next few hundred lines land
    silently, and the budget becomes a number nobody has looked at. Raised deliberately, in the
    same commit as the prose it admits, and set to the file's actual length.
    """

    def test_the_recorded_ceiling_admits_the_shipped_file_without_tolerance(self) -> None:
        """MUTANT: raise the ceiling to a round number above the file's length."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "check_budgets", Path(__file__).resolve().parents[1] / "check_budgets.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules["check_budgets"] = mod
        spec.loader.exec_module(mod)
        repo = Path(__file__).resolve().parents[2]
        target = repo / ".claude" / "skills" / "sdlc-studio" / "reference-sprint.md"
        actual = len(target.read_text(encoding="utf-8").splitlines())
        ceiling = None
        for name, value in vars(mod).items():
            if isinstance(value, dict) and "reference-sprint.md" in value:
                ceiling = value["reference-sprint.md"]
                break
        self.assertIsNotNone(ceiling, "no recorded ceiling for reference-sprint.md")
        self.assertGreaterEqual(ceiling, actual,
                                f"the ceiling {ceiling} refuses the shipped file ({actual})")
        self.assertEqual(ceiling, actual,
                         f"the ceiling {ceiling} carries {ceiling - actual} lines of slack "
                         f"over the shipped {actual} - headroom is how a budget stops noticing "
                         f"growth")


if __name__ == "__main__":
    unittest.main()
