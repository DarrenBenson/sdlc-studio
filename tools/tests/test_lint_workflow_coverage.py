"""US0815 AC7: the CI workflow installs `coverage` BEFORE the suite that needs it, and the
repository's own docs name the dependency. The order is the assertion - the module was already
installed after the suite, for the coverage gate, and a test for presence alone would have
passed while the suite step ran without it."""
from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


class CoverageBeforeSuiteTests(unittest.TestCase):
    def test_coverage_is_installed_before_the_suite_runs_and_named_as_a_dependency(self) -> None:
        """MUTANTS: move the coverage install step below the suite step in lint.yml; delete
        `coverage` from AGENTS.md's soft-dependency table; drop the `>=7.10` floor from the
        install line."""
        text = (REPO / ".github" / "workflows" / "lint.yml").read_text(encoding="utf-8")
        install = re.search(r"pip install[^\n]*'coverage>=7\.10'", text)
        self.assertIsNotNone(install, "lint.yml must install coverage>=7.10 explicitly")
        suite = text.index("bash tools/skill-tests.sh")
        self.assertLess(install.start(), suite, "the coverage install must sit BEFORE the suite step, by position")
        agents = (REPO / "AGENTS.md").read_text(encoding="utf-8")
        start = agents.index("## Soft dependencies")
        self.assertIn("`coverage` 7.10 or later", agents[start:start + 2000], "AGENTS.md's soft-dependency table must name coverage")
        readme = (REPO / "README.md").read_text(encoding="utf-8")
        self.assertIn("**coverage** 7.10 or later, needed only by `verify_ac run --coverage`", readme, "README's dependency sentence must name coverage and what needs it")
        self.assertNotIn("PyYAML** is the one optional dependency", readme)


if __name__ == "__main__":
    unittest.main()
