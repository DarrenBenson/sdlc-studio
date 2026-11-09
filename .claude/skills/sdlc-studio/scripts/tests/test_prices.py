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


#: US1143. xAI's own price page for Grok and Cursor's for Composer.
XAI_PAGE = "https://docs.x.ai/developers/pricing"
CURSOR_PAGE = "https://cursor.com/docs/models-and-pricing"
#: US1135. Each non-Claude provider's own published price page, by the prefix of the model ids it
#: prices: OpenAI's for the models behind Codex CLI, OpenCode's for its Zen (Console) models,
#: which the OpenCode reader names `opencode/<model>`. GitHub's prices Copilot premium requests.
#: US1143 adds xAI's for Grok, under the Cursor slug and the OpenCode `xai/<model>` id, and
#: Cursor's for Composer.
PROVIDER_PAGES = (("gpt-", "https://developers.openai.com/api/docs/pricing"),
                  ("opencode/", "https://opencode.ai/docs/"),
                  ("grok-", XAI_PAGE), ("xai/grok-", XAI_PAGE), ("composer-", CURSOR_PAGE))
COPILOT_PAGE = "https://docs.github.com/en/copilot/"
READ_ON = re.compile(r"\bread (\d{4}-\d{2}-\d{2})\b")
#: The free model of OpenCode's captured session (`fixtures/harness_usage/opencode.jsonl`), as
#: the OpenCode reader names it, and a paid OpenCode model the table does not list.
FREE = "opencode/deepseek-v4.1-flash-free"
OPENCODE_UNLISTED = "opencode/deepseek-v4.1-flash"
FIXTURES = SCRIPTS / "tests" / "fixtures" / "harness_usage"
#: US1143. The id each harness's reading carries for a Grok or Composer model: Cursor CLI prints
#: no model, so its reading carries the `--model` slug `sprint lane run --harness cursor` passes;
#: OpenCode's carries its `<provider>/<model>` id. Any other form is an id no reading carries.
GROK_OR_COMPOSER = re.compile(r"grok|composer", re.I)
CURSOR_SLUG = re.compile(r"^(?:grok|composer)-[\w.-]+$")
OPENCODE_XAI = re.compile(r"^xai/grok-[\w.-]+$")
#: Each Grok and Composer entry's (input, cache_read, output) US dollars per million, typed from
#: xAI's and Cursor's pages as read on 2026-11-09, so a changed rate fails here.
GROK_COMPOSER_RATES = {
    "grok-4.7": (2.0, 0.5, 6.0), "grok-4.6": (2.0, 0.5, 6.0), "grok-4.5": (2.0, 0.3, 6.0),
    "xai/grok-4.7": (2.0, 0.5, 6.0), "xai/grok-4.6": (2.0, 0.5, 6.0),
    "xai/grok-4.5": (2.0, 0.3, 6.0), "composer-2.5": (0.5, 0.2, 2.5)}
#: Cursor's first captured reading (9,046 input, 6,016 cached, 31 output) priced by hand.
CURSOR_READING_USD = {"grok-4.7": (9_046 * 2.0 + 6_016 * 0.5 + 31 * 6.0) / 1e6,
                      "composer-2.5": (9_046 * 0.5 + 6_016 * 0.2 + 31 * 2.5) / 1e6}
#: An unlisted id beside its listed sibling: each Fast variant bills at its own rate.
UNLISTED_SIBLINGS = (("grok-4.7-fast", "grok-4.7"), ("composer-2.5-fast", "composer-2.5"))


class NonClaudePriceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.doc = json.loads(SHIPPED.read_text(encoding="utf-8"))
        self.table = prices.load(path=SHIPPED, pricing={})

    def _sourced(self, entry: dict, page: str) -> None:
        """`entry` carries an effective date and a source on `page` naming the day it was read,
        no earlier than the effective date."""
        effective = dt.date.fromisoformat(entry["effective"])
        source = entry.get("source") or ""
        self.assertTrue(source.startswith(page), f"{source!r} is not the provider's page {page}")
        read = READ_ON.search(source)
        self.assertIsNotNone(read, f"{source!r} names no day it was read")
        self.assertGreaterEqual(dt.date.fromisoformat(read.group(1)), effective)

    def test_every_non_claude_price_is_sourced_and_dated(self) -> None:
        """AC1. MUTANTS: a non-Claude entry's source emptied (refused by the loader), undated, or
        another provider's page (OpenCode's page lists the OpenAI models too); a model no
        provider page prices listed; the premium-request price undated, unsourced or dropped by
        the loader. The control: every Claude entry is held by US1122's own test."""
        others = [e for e in self.doc["models"] if not e["model"].startswith("claude-")]
        priced_from = {page: [] for _prefix, page in PROVIDER_PAGES}
        for entry in others:
            with self.subTest(model=entry["model"]):
                page = next((p for prefix, p in PROVIDER_PAGES
                             if entry["model"].startswith(prefix)), None)
                self.assertIsNotNone(page, "a model no provider's own page prices is not listed")
                self._sourced(entry, page)
                priced_from[page].append(entry["model"])
        for page, models in priced_from.items():
            self.assertTrue(models, f"premise: the table lists a model priced from {page}")
        request = self.doc.get(prices.PREMIUM_REQUEST)
        self.assertIsInstance(request, dict, "the table carries no premium-request price")
        self._sourced(request, COPILOT_PAGE)
        got = self.table.premium_request
        self.assertIsNotNone(got, "the loader dropped the premium-request price")
        self.assertEqual((request["usd"], request["effective"], request["source"]),
                         (got.usd, got.effective.isoformat(), got.source))
        # A request price with no price, date or source is refused by name, never read as $0.
        for missing in ("usd", "effective", "source"):
            with self.subTest(missing=missing), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "prices.json"
                path.write_text(json.dumps({"models": [], prices.PREMIUM_REQUEST: {
                    k: v for k, v in request.items() if k != missing}}), encoding="utf-8")
                with self.assertRaisesRegex(prices.PriceTableError,
                                            f"{prices.PREMIUM_REQUEST}.*{missing}"):
                    prices.load(path=path, pricing={})

    def test_a_free_opencode_model_prices_at_zero_not_unpriced(self) -> None:
        """AC3. MUTANTS: the free model left unlisted (not priced) or listed under another id
        than the reader's; a paid model entered at zero; the free model's $0 counted as not
        covered. The control: an unlisted OpenCode model reads not priced, never $0."""
        harness_usage = __import__("lib.harness_usage", fromlist=["parse"])
        text = (SCRIPTS / "tests" / "fixtures" / "harness_usage" / "opencode.jsonl").read_text(
            encoding="utf-8")
        reading = harness_usage.parse("opencode", text, model=FREE)
        self.assertEqual(FREE, reading.model, "premise: the reader names the model so")
        free = prices.cost(reading.model, {"input": 9_896, "cache_read": 1_792, "output": 3},
                           self.table)
        self.assertEqual((0.0, None), (free.usd, free.unpriced))
        unlisted = prices.cost(OPENCODE_UNLISTED, {"input": 9_896}, self.table)
        self.assertIsNone(unlisted.usd)
        self.assertIn(OPENCODE_UNLISTED, unlisted.unpriced)
        tokens = {"input": 1_000, "output": 0, "cache_read": 0, "cache_write_5m": 0,
                  "cache_write_1h": 0}
        got = run_state.usd({FREE: tokens, OPENCODE_UNLISTED: dict(tokens, input=3_000)},
                            self.table)
        self.assertEqual(0.0, got["usd"], "the free model is priced, at $0")
        self.assertEqual(0.25, got["covered"], "its share is covered")
        self.assertEqual([OPENCODE_UNLISTED], [u["model"] for u in got["unpriced"]])
        # Only a model its provider's page calls free is entered at zero.
        for entry in self.doc["models"]:
            if not any(entry[c] for c in PRICE_FIELDS):
                with self.subTest(model=entry["model"]):
                    self.assertTrue(entry["model"].endswith("-free"), entry["model"])
                    self.assertIn("free", entry.get("note", "").lower())

    # --- US1143 ------------------------------------------------------------------------------
    def _grok_and_composer(self) -> list[dict]:
        return [e for e in self.doc["models"] if GROK_OR_COMPOSER.search(e["model"])]

    def _captures(self) -> dict[str, str]:
        cursor = json.loads((FIXTURES / "cursor.json").read_text(encoding="utf-8"))
        return {"cursor": cursor["captures"][0]["stdout"],
                "opencode": (FIXTURES / "opencode.jsonl").read_text(encoding="utf-8")}

    def test_every_grok_and_composer_price_names_its_provider_page_and_the_day_read(self) -> None:
        """US1143 AC1. MUTANTS: a Grok or Composer entry dropped; one sourced from another
        provider's page or a reseller's, or undated; one under an id no reading carries (such as
        `opencode/grok-4.7`); a cache-write slot at a rate the provider does not bill it at."""
        lanes = __import__("lib.lanes", fromlist=["headless_command"])
        harness_usage = __import__("lib.harness_usage", fromlist=["parse"])
        captures = self._captures()
        entries = self._grok_and_composer()
        ids = [e["model"] for e in entries]
        for prefix in ("grok-", "xai/grok-", "composer-"):
            self.assertTrue(any(i.startswith(prefix) for i in ids), f"premise: a {prefix} entry")
        with tempfile.TemporaryDirectory() as tmp:
            for entry in entries:
                model = entry["model"]
                with self.subTest(model=model):
                    harness, flag = (("cursor", "--model") if CURSOR_SLUG.match(model) else
                                     ("opencode", "-m") if OPENCODE_XAI.match(model) else
                                     (None, None))
                    self.assertIsNotNone(harness, f"{model!r} is no id a harness's reading carries")
                    argv = lanes.headless_command(harness, "brief", model, Path(tmp))
                    self.assertEqual(model, argv[argv.index(flag) + 1])
                    reading = harness_usage.parse(harness, captures[harness], model=model)
                    self.assertEqual((model, "caller"), (reading.model, reading.model_source))
                    self._sourced(entry, CURSOR_PAGE if "composer" in model else XAI_PAGE)
                    # Neither page prices a cache write: a written token is billed as input.
                    self.assertEqual((entry["input"],) * 2,
                                     (entry["cache_write_5m"], entry["cache_write_1h"]))
                    self.assertIn("cache-write", entry.get("note", ""))

    def test_a_recorded_grok_and_composer_reading_is_priced_in_dollars(self) -> None:
        """US1143 AC2. MUTANTS: an entry's rate changed or another model's; the reading read as
        not priced or at $0; a component dropped from the sum."""
        harness_usage = __import__("lib.harness_usage", fromlist=["parse"])
        captures = self._captures()
        self.assertEqual(set(GROK_COMPOSER_RATES), {e["model"] for e in self._grok_and_composer()},
                         "every Grok and Composer entry has its rates typed here")
        for model, (inp, cached, out) in GROK_COMPOSER_RATES.items():
            harness = "opencode" if model.startswith("xai/") else "cursor"
            with self.subTest(model=model):
                r = harness_usage.parse(harness, captures[harness], model=model)
                components = {"input": r.input, "cache_read": r.cache_read, "output": r.output,
                              "cache_write_5m": r.cache_write or 0,
                              "cache_write_1h": r.cache_write_1h or 0}
                self.assertTrue(r.input and r.cache_read and r.output, "premise: three components")
                writes = components["cache_write_5m"] + components["cache_write_1h"]
                expected = (r.input * inp + r.cache_read * cached + r.output * out
                            + writes * inp) / 1_000_000
                got = prices.cost(r.model, components, self.table)
                self.assertIsNone(got.unpriced)
                self.assertGreater(got.usd, 0)
                self.assertTrue(math.isclose(got.usd, expected, rel_tol=1e-12),
                                f"{got.usd!r} != {expected!r}")
                if model in CURSOR_READING_USD:
                    self.assertTrue(math.isclose(got.usd, CURSOR_READING_USD[model],
                                                 rel_tol=1e-12))

    def test_an_unlisted_grok_or_composer_id_is_not_priced_beside_a_listed_one(self) -> None:
        """US1143 AC3. MUTANTS: an unlisted id priced by prefix or nearest name at its listed
        sibling's rate, or read as free. The control: the listed sibling is priced."""
        million = {"input": 1_000_000, "output": 0, "cache_read": 0, "cache_write_5m": 0,
                   "cache_write_1h": 0}
        by_model = {}
        for unlisted, listed in UNLISTED_SIBLINGS:
            with self.subTest(unlisted=unlisted):
                self.assertTrue(unlisted.startswith(listed), "premise: a listed id plus a suffix")
                control = prices.cost(listed, million, self.table)
                self.assertEqual((GROK_COMPOSER_RATES[listed][0], None),
                                 (control.usd, control.unpriced))
                got = prices.cost(unlisted, million, self.table)
                self.assertIsNone(got.usd)
                self.assertIn(unlisted, got.unpriced or "")
            by_model[listed] = dict(million, input=2_000)
            by_model[unlisted] = dict(million, input=1_000)
        run = run_state.usd(by_model, self.table)
        self.assertEqual(sorted(u for u, _ in UNLISTED_SIBLINGS),
                         sorted(u["model"] for u in run["unpriced"]))
        for row in run["unpriced"]:
            self.assertTrue(math.isclose(row["share"], 1 / 6), row)
        self.assertEqual(sorted(s for _, s in UNLISTED_SIBLINGS),
                         sorted(m["model"] for m in run["models"]))
        self.assertTrue(math.isclose(run["usd"], 2_000 * (2.0 + 0.5) / 1e6, rel_tol=1e-12))
        self.assertTrue(math.isclose(run["covered"], 2 / 3))

    def test_the_configuration_reference_names_the_grok_and_composer_sources(self) -> None:
        """US1143 AC4. MUTANTS: xAI's or Cursor's page, or either harness's id form, dropped from
        the reference or the table's `about`. The control: OpenAI's and OpenCode's still named."""
        text = REF_CONFIG.read_text(encoding="utf-8")
        section = text.split("## Model Prices {#pricing}", 1)[1].split("\n## ", 1)[0]
        for where, prose in (("reference-config.md#pricing", section),
                             ("the table's about", self.doc["about"])):
            sentence = next((s for s in re.split(r"(?<=[.;])\s+", prose) if "OpenAI's" in s), "")
            for needed in ("OpenAI's", "OpenCode's", "xAI's", "Cursor's"):
                with self.subTest(where=where, needed=needed):
                    self.assertIn(needed, sentence, "the sentence naming the non-Claude sources")
            for needed in ("--model", "<provider>/<model>", "xai/", "Grok", "Composer"):
                with self.subTest(where=where, needed=needed):
                    self.assertIn(needed, prose)


if __name__ == "__main__":
    unittest.main()
