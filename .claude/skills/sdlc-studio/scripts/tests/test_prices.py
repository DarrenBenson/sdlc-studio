"""US1122 (CR0665): a dated per-model price table gives every token reading a US dollar cost.

The priced figure weighs every model's tokens alike, so it cannot show the saving from a cheaper
model or compare two harnesses. `lib/prices.py` reads a dated table shipped in
`templates/model-prices.json`, which a project extends or overrides under `pricing.models` in its
config, and prices a reading from its own model and components.

Pinned here:

* every shipped entry carries a model id, five component prices, an effective date and a source,
  and an entry missing any of them is refused by name, never read as a zero price (AC1);
* a cost is the sum of each component times its price, the shipped table prices a real captured
  Claude Code reading at the harness's own figure, and a model with no price is None naming the
  model, never 0 (AC2);
* `pricing.models` adds a model or replaces a shipped one, and `pricing.stale_after_days` decides
  when the table's newest effective date makes it stale (AC3).

Run from the repo root:
    python3 -m pytest .claude/skills/sdlc-studio/scripts/tests/test_prices.py
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/prices.py
from __future__ import annotations

import datetime as dt
import json
import math
import re
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
SKILL = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

from lib import prices  # noqa: E402
from lib import run_state  # noqa: E402

try:
    import yaml  # noqa: F401
    HAVE_YAML = True
except ImportError:  # pragma: no cover - exercised only without PyYAML
    HAVE_YAML = False

SHIPPED = SKILL / "templates" / "model-prices.json"
REF_CONFIG = SKILL / "reference-config.md"
PRICE_FIELDS = ("input", "output", "cache_read", "cache_write_5m", "cache_write_1h")
REQUIRED = ("model",) + PRICE_FIELDS + ("effective", "source")

# A Claude Code `-p --output-format json` capture of 2026-11-06 (one trivial session): its usage
# and the harness's own `modelUsage.claude-haiku-5-5.costUSD`, trimmed to the figures used here.
CAPTURED_MODEL = "claude-haiku-5-5"
CAPTURED_READING = {"input": 2, "output": 35, "cache_read": 11382, "cache_write_5m": 0,
                    "cache_write_1h": 17126}
CAPTURED_COST_USD = 0.0035567199999999998


def _entry(model: str, effective: str = "2026-01-01", **prices_) -> dict:
    base = {"model": model, "input": 1.0, "output": 2.0, "cache_read": 3.0,
            "cache_write_5m": 5.0, "cache_write_1h": 7.0, "effective": effective,
            "source": "https://example.test/prices"}
    base.update(prices_)
    return base


class PriceTableTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _table(self, entries: list, name: str = "prices.json") -> Path:
        path = self.tmp / name
        path.write_text(json.dumps({"models": entries}), encoding="utf-8")
        return path

    # --- AC1 ---------------------------------------------------------------------------------
    def test_every_entry_is_complete_and_a_partial_one_is_refused(self) -> None:
        raw = json.loads(SHIPPED.read_text(encoding="utf-8"))["models"]
        self.assertTrue(raw, "the shipped table lists no model")
        for entry in raw:
            with self.subTest(model=entry.get("model")):
                for field in REQUIRED:
                    self.assertIn(field, entry, f"shipped entry lacks {field}")
                for field in PRICE_FIELDS:
                    value = entry[field]
                    self.assertTrue(isinstance(value, (int, float)) and not isinstance(value, bool)
                                    and value >= 0, f"{field} is not a price: {value!r}")
                dt.date.fromisoformat(entry["effective"])
                self.assertRegex(entry["source"], r"^https://", "a source names where it was read")
        table = prices.load()
        self.assertEqual(set(table.models), {e["model"] for e in raw})
        self.assertEqual(len(table.models), len(raw), "a duplicate shipped id was folded in")

        # Each required field, removed from one entry or set to null, is refused by name.
        for field in REQUIRED:
            for how in ("missing", "null"):
                with self.subTest(field=field, how=how):
                    bad = _entry("model-b")
                    if how == "missing":
                        del bad[field]
                    else:
                        bad[field] = None
                    path = self._table([_entry("model-a"), bad])
                    with self.assertRaises(prices.PriceTableError) as caught:
                        prices.load(path=path)
                    message = str(caught.exception)
                    self.assertIn(field, message, "the refusal does not name the field")
                    self.assertIn("model-b" if field != "model" else "entry 2", message,
                                  "the refusal does not name the entry")

        # A price that is not a non-negative number, a malformed date, an empty source, an unknown
        # field and a repeated model id are refused as well.
        for label, bad in (("negative", _entry("m", input=-1)), ("text", _entry("m", output="2")),
                           ("bool", _entry("m", cache_read=True)), ("nan", _entry("m", input=math.nan)),
                           ("date", _entry("m", effective="06/11/2026")), ("source", _entry("m", source=" ")),
                           ("unknown", {**_entry("m"), "cache_write": 1.0})):
            with self.subTest(refused=label):
                with self.assertRaises(prices.PriceTableError):
                    prices.load(path=self._table([bad]))
        with self.assertRaises(prices.PriceTableError) as caught:
            prices.load(path=self._table([_entry("dup"), _entry("dup")]))
        self.assertIn("dup", str(caught.exception))

    # --- AC2 ---------------------------------------------------------------------------------
    def test_cost_is_the_sum_of_components_and_an_unknown_model_is_not_priced(self) -> None:
        table = prices.load(path=self._table([_entry("m")]))
        # Prices 1, 2, 3, 5, 7 per million against token counts a decade apart: each component
        # lands in its own digit, so a dropped, doubled or swapped component changes the figure.
        reading = {"input": 1_000_000, "output": 10_000_000, "cache_read": 100_000_000,
                   "cache_write_5m": 1_000_000_000, "cache_write_1h": 10_000_000_000}
        result = prices.cost("m", reading, table)
        self.assertEqual(result.usd, 1 + 20 + 300 + 5000 + 70000)
        self.assertEqual(result.model, "m")
        self.assertIsNone(result.unpriced)
        for component, price in zip(PRICE_FIELDS, (1, 2, 3, 5, 7)):
            with self.subTest(component=component):
                alone = prices.cost("m", {component: 2_000_000}, table)
                self.assertEqual(alone.usd, 2 * price)
        self.assertEqual(prices.cost("m", {}, table).usd, 0, "a reading with no tokens costs 0")

        # The shipped table prices a real captured reading at the harness's own figure.
        shipped = prices.cost(CAPTURED_MODEL, CAPTURED_READING)
        self.assertTrue(math.isclose(shipped.usd, CAPTURED_COST_USD, rel_tol=1e-12),
                        f"{shipped.usd!r} != Claude Code's own {CAPTURED_COST_USD!r}")

        # A model the table does not price is None naming it, never 0 - with or without tokens.
        for model in ("gpt-5.5-codex", None, ""):
            for tokens in (reading, {}):
                with self.subTest(model=model, tokens=bool(tokens)):
                    unknown = prices.cost(model, tokens, table)
                    self.assertIsNone(unknown.usd)
                    self.assertIsNotNone(unknown.unpriced)
                    self.assertIn(model if model else "names no model", unknown.unpriced)

        # A component the table does not know, or a count that is not a token count, is refused
        # rather than dropped from the sum.
        for bad in ({"cache_write": 10}, {"input": -1}, {"output": 1.5}, {"input": True}):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    prices.cost("m", bad, table)

    # --- AC3 ---------------------------------------------------------------------------------
    def test_config_overrides_and_staleness(self) -> None:
        shipped = self._table([_entry("kept"), _entry("replaced", input=1.0)])
        override = {"models": {
            "replaced": {k: v for k, v in _entry("replaced", input=11.0).items() if k != "model"},
            "added": {k: v for k, v in _entry("added", output=13.0).items() if k != "model"},
        }}
        table = prices.load(path=shipped, pricing=override)
        self.assertEqual(set(table.models), {"kept", "replaced", "added"})
        self.assertEqual(prices.cost("replaced", {"input": 1_000_000}, table).usd, 11.0)
        self.assertEqual(prices.cost("added", {"output": 1_000_000}, table).usd, 13.0)
        self.assertEqual(prices.cost("kept", {"input": 1_000_000}, table).usd, 1.0)
        self.assertEqual(table.overridden, ("added", "replaced"))

        # An override is held to the shipped table's completeness rule, named by its config key.
        partial = {"models": {"half": {"input": 1.0, "effective": "2026-01-01",
                                       "source": "https://example.test"}}}
        with self.assertRaises(prices.PriceTableError) as caught:
            prices.load(path=shipped, pricing=partial)
        self.assertIn("pricing.models.half", str(caught.exception))
        self.assertIn("output", str(caught.exception))

        # The same override through a project's own sdlc-studio/.config.yaml.
        if HAVE_YAML:
            root = self.tmp / "repo"
            (root / "sdlc-studio").mkdir(parents=True)
            (root / "sdlc-studio" / ".config.yaml").write_text(
                "pricing:\n  stale_after_days: 7\n  models:\n    replaced:\n"
                "      input: 11\n      output: 2\n      cache_read: 3\n      cache_write_5m: 5\n"
                "      cache_write_1h: 7\n      effective: 2026-01-01\n"
                "      source: https://example.test/contract\n", encoding="utf-8")
            from_config = prices.load(root, path=shipped)
            self.assertEqual(prices.cost("replaced", {"input": 1_000_000}, from_config).usd, 11.0)
            self.assertEqual(from_config.stale_after_days, 7)

        # Stale once the NEWEST effective date is older than stale_after_days, and not before.
        dated = self._table([_entry("old", effective="2025-06-01"), _entry("new", effective="2026-01-01")])
        month = prices.load(path=dated, pricing={"stale_after_days": 30})
        self.assertEqual(month.newest_effective, dt.date(2026, 1, 1))
        self.assertIsNone(prices.stale(month, today=dt.date(2026, 1, 31)), "30 days old is not older than 30")
        verdict = prices.stale(month, today=dt.date(2026, 2, 1))
        self.assertIsNotNone(verdict, "a table 31 days old under a 30-day limit reported fresh")
        self.assertIn("2026-01-01", verdict)
        self.assertIn("stale", verdict)
        year = prices.load(path=dated, pricing={"stale_after_days": 365})
        self.assertIsNone(prices.stale(year, today=dt.date(2026, 2, 1)), "the configured age was ignored")
        default = prices.load(path=dated)
        self.assertEqual(default.stale_after_days, prices.DEFAULT_STALE_AFTER_DAYS)
        self.assertIsNotNone(prices.stale(default, today=dt.date(2026, 1, 1)
                                          + dt.timedelta(days=prices.DEFAULT_STALE_AFTER_DAYS + 1)))
        for bad in (0, -1, "30", True, 1.5):
            with self.subTest(stale_after_days=bad):
                with self.assertRaises(prices.PriceTableError):
                    prices.load(path=dated, pricing={"stale_after_days": bad})

    # --- wiring ------------------------------------------------------------------------------
    def test_components_are_the_ones_a_reading_carries(self) -> None:
        self.assertEqual(set(prices.COMPONENTS), set(run_state.TOKEN_COMPONENTS))

    def test_the_configuration_reference_states_the_keys_and_the_built_in_age(self) -> None:
        text = REF_CONFIG.read_text(encoding="utf-8")
        self.assertIn("`pricing.models`", text)
        row = re.search(r"^\|\s*`pricing\.stale_after_days`\s*\|\s*(\d+) days", text, re.M)
        self.assertIsNotNone(row, "reference-config.md does not document pricing.stale_after_days")
        self.assertEqual(int(row.group(1)), prices.DEFAULT_STALE_AFTER_DAYS)


if __name__ == "__main__":
    unittest.main()
