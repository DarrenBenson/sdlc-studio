"""BG0681: `config.py show --key` crashed on a key whose value holds an unquoted YAML date.

BG0670 gave the whole-config `show` a json default for date and datetime values; the `--key`
branch still called `json.dumps` without it, so `show --key gate_budget` on this repository's
own config exited 1 with a TypeError. Both tests run the shipped CLI in a fixture project.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "config.py"

try:
    import yaml  # noqa: F401
    HAVE_YAML = True
except ImportError:
    HAVE_YAML = False

CONFIG = ("gate_budget:\n"
          "  baseline_date: 2026-07-26\n")


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class ConfigShowDateTests(unittest.TestCase):

    def _show_key(self, key: str) -> subprocess.CompletedProcess:
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "sdlc-studio").mkdir()
            (Path(d) / "sdlc-studio" / ".config.yaml").write_text(CONFIG, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(SCRIPT), "show", "--key", key, "--root", d],
                capture_output=True, text=True, timeout=60)

    def test_a_nested_date_under_a_key_prints(self) -> None:
        """AC1. MUTANT: HEAD's `json.dumps(get(...))` with no default - TypeError, exit 1."""
        proc = self._show_key("gate_budget")
        self.assertEqual(proc.returncode, 0,
                         f"show --key gate_budget must print a mapping holding a date:\n"
                         f"{proc.stderr}")
        budget = json.loads(proc.stdout)
        self.assertEqual(budget["baseline_date"], "2026-07-26",
                         "the nested date must print as its ISO-8601 string")

    def test_a_scalar_date_key_prints(self) -> None:
        """AC2. MUTANT: converting dates only inside mappings (walking dict values before
        dumping) - the bare date reaches json.dumps unconverted and raises."""
        proc = self._show_key("gate_budget.baseline_date")
        self.assertEqual(proc.returncode, 0,
                         f"show --key on a scalar date must print it:\n{proc.stderr}")
        self.assertEqual(proc.stdout.strip(), '"2026-07-26"',
                         "a scalar date key prints as the quoted ISO date")


if __name__ == "__main__":
    unittest.main()
