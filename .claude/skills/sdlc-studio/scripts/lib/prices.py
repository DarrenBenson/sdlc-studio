"""Model prices: a dated per-model table that turns a token reading into US dollars.

The priced-token figure weighs every model's tokens alike, so it cannot show the saving from a
cheaper model or compare two harnesses whose providers price tokens differently. This module reads
`templates/model-prices.json`, a table of list prices in US dollars per million tokens, one entry
per model id, each carrying its five component prices, the date they were confirmed in force and
where they were read. A project adds a model or replaces a shipped one under `pricing.models` in
`sdlc-studio/.config.yaml`, and sets the age at which the table reads as stale with
`pricing.stale_after_days`.

Three rules hold the figure honest:

* an entry missing any field is refused, naming the entry and the field - a missing price is
  never read as zero, because zero is a real price (a free model) and a guess is not;
* a model the table does not list is not priced: `cost` returns `usd=None` naming the model,
  never 0, so a total can say what share of the spend it covers;
* the table is dated, and `stale` names it once its newest effective date is older than the
  configured age, so a figure from last year's prices does not read as current.

Beside the token prices the table may carry one price per Copilot premium request
(`PREMIUM_REQUEST`), dated and sourced the same way and refused on the same terms; a table
without it prices no request, and a request count is never priced at $0 for want of one.

Pure stdlib. The project config is read through `config.get` only when `load` is given a repo
root, and that loader degrades to no override, with a warning, where PyYAML is absent.
"""
from __future__ import annotations

import datetime as dt
import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, NamedTuple

#: The shipped table.
TABLE_PATH = Path(__file__).resolve().parents[2] / "templates" / "model-prices.json"
#: The token components a reading carries, each priced in US dollars per million tokens. The set
#: is `run_state.TOKEN_COMPONENTS`; a test holds the two equal.
COMPONENTS = ("input", "output", "cache_read", "cache_write_5m", "cache_write_1h")
#: Every field an entry must carry, in the order a refusal checks them.
REQUIRED = ("model",) + COMPONENTS + ("effective", "source")
#: Fields an entry may carry beyond the required ones.
OPTIONAL = ("note",)
#: The table's key, and the `pricing` key, of the price of one Copilot premium request.
PREMIUM_REQUEST = "premium_request"
#: Every field a premium-request price must carry, in the order a refusal checks them.
REQUEST_REQUIRED = ("usd", "effective", "source")
#: The age, in days, past which the table reads as stale when `pricing.stale_after_days` is unset.
DEFAULT_STALE_AFTER_DAYS = 90
_PER = 1_000_000


class PriceTableError(ValueError):
    """The price table, or a project's `pricing` block, is malformed. The message names the
    entry and the field, or the file when the table itself cannot be read."""


@dataclass(frozen=True)
class Price:
    """One model's list prices, in US dollars per million tokens."""
    model: str
    input: float
    output: float
    cache_read: float
    cache_write_5m: float
    cache_write_1h: float
    effective: dt.date
    source: str
    note: str = ""


@dataclass(frozen=True)
class RequestPrice:
    """The list price of one Copilot premium request, in US dollars."""
    usd: float
    effective: dt.date
    source: str
    note: str = ""


@dataclass(frozen=True)
class PriceTable:
    """The shipped table with a project's `pricing.models` laid over it. `premium_request` is
    the price of one premium request, None when the table carries none."""
    models: Mapping[str, Price]
    stale_after_days: int
    origin: str
    overridden: tuple[str, ...] = field(default=())
    premium_request: RequestPrice | None = None

    @property
    def newest_effective(self) -> dt.date | None:
        """The latest effective date of any entry, or None for an empty table."""
        return max((p.effective for p in self.models.values()), default=None)


class Cost(NamedTuple):
    """A reading's estimated cost. `usd` is None when the model has no price, and `unpriced` then
    says which model; a priced reading has `unpriced` None."""
    usd: float | None
    model: str | None
    unpriced: str | None


def _price(value, where: str, name: str) -> float:
    if value is None:
        raise PriceTableError(f"{where} has no '{name}' price")
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) \
            or value < 0:
        raise PriceTableError(f"{where} has '{name}' {value!r}, not a price: give US dollars per "
                              "million tokens as a number of 0 or more")
    return float(value)


def _entry(raw, where: str, model: str | None) -> Price:
    """Validate one entry. `where` names it in a refusal; `model` is the id the entry must carry
    (a config key), or None to read it from the entry's own `model` field."""
    if not isinstance(raw, Mapping):
        raise PriceTableError(f"{where} is not a mapping of fields")
    unknown = sorted(set(raw) - set(REQUIRED) - set(OPTIONAL))
    if unknown:
        raise PriceTableError(f"{where} has unknown field(s) {', '.join(map(repr, unknown))}; "
                              f"an entry carries {', '.join(REQUIRED)}")
    if model is None:
        model = raw.get("model")
        if not isinstance(model, str) or not model.strip():
            raise PriceTableError(f"{where} has no 'model' id")
        model = model.strip()
        where = f"{where} ({model})"
    elif "model" in raw and raw["model"] != model:
        raise PriceTableError(f"{where} names model {raw['model']!r}, not its key {model!r}")
    values = {name: _price(raw.get(name), where, name) for name in COMPONENTS}
    effective, source, note = _dated(raw, where)
    return Price(model=model, effective=effective, source=source, note=note, **values)


def _dated(raw: Mapping, where: str) -> tuple[dt.date, str, str]:
    """An entry's `(effective, source, note)`, refused by name when the date or the source is
    missing or malformed."""
    effective = raw.get("effective")
    if effective is None:
        raise PriceTableError(f"{where} has no 'effective' date")
    if isinstance(effective, dt.datetime):
        effective = effective.date()
    elif not isinstance(effective, dt.date):
        try:
            effective = dt.date.fromisoformat(str(effective))
        except ValueError:
            raise PriceTableError(f"{where} has 'effective' {effective!r}, not a YYYY-MM-DD date") \
                from None
    source = raw.get("source")
    if not isinstance(source, str) or not source.strip():
        raise PriceTableError(f"{where} has no 'source': name where the prices were read")
    note = raw.get("note") or ""
    if not isinstance(note, str):
        raise PriceTableError(f"{where} has a 'note' that is not text")
    return effective, source.strip(), note


def request_price(raw, where: str = PREMIUM_REQUEST) -> RequestPrice:
    """Validate a premium-request price: `usd`, `effective` and `source`, and an optional
    `note`. Raises `PriceTableError` naming `where` and the field; a missing price is refused,
    never read as $0."""
    if not isinstance(raw, Mapping):
        raise PriceTableError(f"{where} is not a mapping of fields")
    unknown = sorted(set(raw) - set(REQUEST_REQUIRED) - set(OPTIONAL))
    if unknown:
        raise PriceTableError(f"{where} has unknown field(s) {', '.join(map(repr, unknown))}; "
                              f"it carries {', '.join(REQUEST_REQUIRED)}")
    usd = raw.get("usd")
    if usd is None:
        raise PriceTableError(f"{where} has no 'usd' price")
    if isinstance(usd, bool) or not isinstance(usd, (int, float)) or not math.isfinite(usd) \
            or usd < 0:
        raise PriceTableError(f"{where} has 'usd' {usd!r}, not a price: give US dollars per "
                              "request as a number of 0 or more")
    effective, source, note = _dated(raw, where)
    return RequestPrice(usd=float(usd), effective=effective, source=source, note=note)


def _shipped(path: Path) -> tuple[dict[str, Price], RequestPrice | None]:
    try:
        doc = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise PriceTableError(f"{path}: cannot read the price table ({exc})") from None
    entries = doc.get("models") if isinstance(doc, dict) else None
    if not isinstance(entries, list):
        raise PriceTableError(f"{path}: the table has no 'models' list")
    table: dict[str, Price] = {}
    for n, raw in enumerate(entries, start=1):
        price = _entry(raw, f"{Path(path).name}: entry {n}", None)
        if price.model in table:
            raise PriceTableError(f"{Path(path).name}: entry {n} repeats model {price.model!r}")
        table[price.model] = price
    request = doc.get(PREMIUM_REQUEST)
    return table, (None if request is None else
                   request_price(request, f"{Path(path).name}: {PREMIUM_REQUEST}"))


def _pricing_block(repo_root) -> dict:
    import config  # lazy: the loader carries the soft PyYAML dependency; this module does not
    return config.get(repo_root, "pricing", {})


def load(repo_root: Path | str | None = None, *, path: Path | str | None = None,
         pricing: Mapping | None = None) -> PriceTable:
    """The price table: the shipped one at `path` (default `TABLE_PATH`) with a `pricing` block
    laid over it. The block is `pricing` when given, else the project config's `pricing` block
    when `repo_root` is given, else none.

    `pricing.models` maps a model id to a complete entry (every field but `model`); it adds the
    model or replaces the shipped entry whole, and is refused on the same terms as a shipped
    entry. `pricing.premium_request` replaces the shipped premium-request price whole.
    `pricing.stale_after_days` is a whole number of days of 1 or more.

    Raises `PriceTableError` naming the entry and the field, or the file when the table itself
    cannot be read."""
    path = Path(path) if path is not None else TABLE_PATH
    models, request = _shipped(path)
    if pricing is None:
        pricing = _pricing_block(repo_root) if repo_root is not None else {}
    if pricing is None:
        pricing = {}
    if not isinstance(pricing, Mapping):
        raise PriceTableError("pricing: the config block is not a mapping")
    extra = pricing.get("models") or {}
    if not isinstance(extra, Mapping):
        raise PriceTableError("pricing.models: map each model id to its prices")
    overridden = []
    for model, raw in extra.items():
        model = str(model).strip()
        models[model] = _entry(raw, f"pricing.models.{model}", model)
        overridden.append(model)
    if pricing.get(PREMIUM_REQUEST) is not None:
        request = request_price(pricing[PREMIUM_REQUEST], f"pricing.{PREMIUM_REQUEST}")
    days = pricing.get("stale_after_days", DEFAULT_STALE_AFTER_DAYS)
    if isinstance(days, bool) or not isinstance(days, int) or days < 1:
        raise PriceTableError(f"pricing.stale_after_days is {days!r}: give a whole number of days, "
                              "1 or more")
    origin = str(path) + (" with the project's pricing.models" if overridden else "")
    return PriceTable(models=models, stale_after_days=days, origin=origin,
                      overridden=tuple(sorted(overridden)), premium_request=request)


def cost(model: str | None, components: Mapping[str, int],
         table: PriceTable | None = None) -> Cost:
    """A reading's estimated cost in US dollars: each component's tokens times its price per
    million, summed. A component the reading omits counts as no tokens; one the table does not
    know, or a count that is not a whole number of 0 or more, raises ValueError rather than
    dropping out of the sum. A model the table does not list costs `usd=None`, naming it."""
    for name, tokens in components.items():
        if name not in COMPONENTS:
            raise ValueError(f"reading component {name!r} is not one of {', '.join(COMPONENTS)}")
        if isinstance(tokens, bool) or not isinstance(tokens, int) or tokens < 0:
            raise ValueError(f"reading component {name!r} is {tokens!r}, not a token count")
    table = table if table is not None else load()
    name = (model or "").strip()
    if not name:
        return Cost(None, model, "not priced: the reading names no model")
    price = table.models.get(name)
    if price is None:
        return Cost(None, model, f"not priced: model {name} is not in the price table "
                                 f"(add it under pricing.models)")
    usd = sum(components.get(c, 0) * getattr(price, c) for c in COMPONENTS) / _PER
    return Cost(usd, model, None)


def stale(table: PriceTable, today: dt.date | None = None) -> str | None:
    """A sentence naming the table as stale once its newest effective date is more than
    `stale_after_days` before `today`; None while it is fresh. An empty table is stale."""
    today = today or dt.date.today()
    newest = table.newest_effective
    if newest is None:
        return f"the price table {table.origin} is stale: it prices no model"
    age = (today - newest).days
    if age > table.stale_after_days:
        return (f"the price table {table.origin} is stale: its newest effective date, "
                f"{newest.isoformat()}, is {age} days old, past pricing.stale_after_days "
                f"({table.stale_after_days})")
    return None
