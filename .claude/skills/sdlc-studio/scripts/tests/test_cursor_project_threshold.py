"""The Cursor meter books a hook-ledger response by the project's price table.

A project's `pricing.models` entry for a model replaces the shipped one whole, its long-context
threshold with it. `meter_cursor.read` books each ledger response by the table of the repo root
it is metering, so a project whose contract moves a threshold sees its prompts booked under the
long-context id at that threshold, and a project with no pricing block sees the shipped table's.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/meter_cursor.py
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib import meter_cursor, prices, run_state  # noqa: E402

try:
    import yaml  # noqa: F401
    HAVE_YAML = True
except ImportError:  # the project config is read through PyYAML
    HAVE_YAML = False

LONG = "grok-4.7" + prices.LONG_CONTEXT_ID

#: The shipped grok-4.7 entry, its long-context threshold moved from 200,000 to 128,000.
CONFIG = """\
pricing:
  models:
    grok-4.7:
      input: 2.0
      output: 6.0
      cache_read: 0.5
      cache_write_5m: 2.0
      cache_write_1h: 2.0
      effective: 2026-11-09
      source: https://example.test/contract
      long_context:
        from_prompt_tokens: 128000
        input: 4.0
        output: 12.0
        cache_read: 1.0
        cache_write_5m: 4.0
        cache_write_1h: 4.0
        effective: 2026-11-12
        source: https://example.test/contract
"""


class CursorProjectThresholdTests(unittest.TestCase):

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        (self.root / "sdlc-studio").mkdir()
        self.env = {"HOME": str(self.root / "home")}      # no cloud key: the CLI is read

    def ledger(self, prompt: int) -> None:
        path = meter_cursor.ledger_path(self.root)
        path.parent.mkdir(parents=True, exist_ok=True)
        row = {"model": "grok-4.7", "input_tokens": prompt, "output_tokens": 1_000,
               "cache_read_tokens": prompt - 2_000, "cache_write_tokens": 0}
        path.write_text(json.dumps(row) + "\n", encoding="utf-8")

    def split(self) -> dict:
        got = meter_cursor.read(self.root, self.env)
        self.assertIsNotNone(got["tokens"], got.get("reason"))
        return got[run_state.BY_MODEL]

    @unittest.skipUnless(HAVE_YAML, "the project config is read through PyYAML")
    def test_a_project_threshold_moves_the_booking(self) -> None:
        """AC1. MUTANT: `read_cli` calls `read_ledger(ledger)`, whose `_rates()` loads the
        shipped table only, so a 150,000-token prompt is booked at the short rate."""
        (self.root / "sdlc-studio" / ".config.yaml").write_text(CONFIG, encoding="utf-8")
        self.ledger(150_000)
        split = self.split()
        self.assertEqual({LONG}, set(split), "the one response is booked under the long id alone")
        self.assertEqual(1_000, split[LONG]["output"], "the response is booked long")

    @unittest.skipUnless(HAVE_YAML, "the project config is read through PyYAML")
    def test_a_prompt_under_the_project_threshold_is_booked_short(self) -> None:
        """The boundary beside it: 127,999 is under the project's 128,000."""
        (self.root / "sdlc-studio" / ".config.yaml").write_text(CONFIG, encoding="utf-8")
        self.ledger(127_999)
        split = self.split()
        self.assertEqual(1_000, split["grok-4.7"]["output"])
        self.assertEqual(0, split[LONG]["output"])

    def test_no_project_block_books_by_the_shipped_threshold(self) -> None:
        """AC2. MUTANT: a threading of repo_root that breaks the default table, so the 150,000
        prompt reads long, or the 200,000 one short."""
        self.ledger(150_000)
        split = self.split()
        self.assertEqual(1_000, split["grok-4.7"]["output"], "150,000 is under the shipped 200,000")
        self.assertEqual(0, split[LONG]["output"])
        self.ledger(200_000)
        self.assertEqual(1_000, self.split()[LONG]["output"])

    def test_a_config_that_will_not_load_books_every_response_under_its_own_model(self) -> None:
        """The malformed-input path: a pricing block `prices.load` refuses leaves no table to
        book by, so the meter reads on, every response under its own model, as it does for a
        table that cannot be read at all, rather than raising out of the meter."""
        (self.root / "sdlc-studio" / ".config.yaml").write_text(
            "pricing:\n  models: nonsense\n", encoding="utf-8")
        self.ledger(200_000)
        self.assertEqual({"grok-4.7"}, set(self.split()))


if __name__ == "__main__":
    unittest.main()
