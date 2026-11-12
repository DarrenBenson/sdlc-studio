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

GitHub Copilot bills by tokens in AI credits. The table's `COPILOT` block carries the US-dollar
value of one credit, dated and sourced, and each model's five component rates in AI credits per
million tokens under the id the Copilot CLI records (`claude-sonnet-5.5`, dotted, where the
Anthropic API's is `claude-sonnet-5-5`). `load` turns each rate into US dollars at the credit's
value and prices the id beside the `models` entries; an id in both is refused, so a lookup by id
alone is never ambiguous, and a gap in the block is refused by name, never read as zero.

A plan bills Copilot on one basis, never both: `pricing.copilot_billing` is `tokens` (the
default), where the block's ids are priced and a premium request is not, or `requests`, for a
plan kept on request-based billing, where every id the block rates reads not priced, saying
the plan bills by request, and the report prices the premium requests instead. Any other
value is refused, naming the key and the two values it takes.

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
#: An entry's optional block of its provider's long-context rates: the five component prices,
#: `from_prompt_tokens` (the prompt size from which they apply) and its own effective date and
#: source. A request whose prompt is that size or more is billed at them for all its tokens.
LONG_CONTEXT = "long_context"
#: The id `load` prices an entry's long-context block under, beside the entry: its model + this.
LONG_CONTEXT_ID = "@long-context"
#: The table's key, and the `pricing` key, of the price of one Copilot premium request.
PREMIUM_REQUEST = "premium_request"
#: Every field a premium-request price must carry, in the order a refusal checks them.
REQUEST_REQUIRED = ("usd", "effective", "source")
#: The age, in days, past which the table reads as stale when `pricing.stale_after_days` is unset.
DEFAULT_STALE_AFTER_DAYS = 90
#: The table's key of GitHub Copilot's token billing, kept apart from the provider-API `models`.
COPILOT = "copilot_token_billing"
#: Every field the Copilot block must carry, in the order a refusal checks them.
COPILOT_REQUIRED = ("credit_usd", "effective", "source", "models")
#: Every field a Copilot model rate must carry; it may carry a `note` beside them.
COPILOT_RATE_REQUIRED = ("model",) + COMPONENTS
#: The `pricing` key naming the basis a project's Copilot plan bills on, and the two values
#: it takes: token billing in AI credits, the default, and request-based billing.
COPILOT_BILLING = "copilot_billing"
TOKEN_BILLING, REQUEST_BILLING = "tokens", "requests"
BILLING_BASES = (TOKEN_BILLING, REQUEST_BILLING)
_PER = 1_000_000
_USD = "US dollars per million tokens"
_CREDITS = "AI credits per million tokens"


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
    #: On a long-context price, the prompt size in tokens from which it applies; None otherwise.
    from_prompt_tokens: int | None = None
    #: The entry's long-context price (`LONG_CONTEXT`), which `load` also lists under its own id.
    long_context: "Price | None" = None


@dataclass(frozen=True)
class RequestPrice:
    """The list price of one Copilot premium request, in US dollars."""
    usd: float
    effective: dt.date
    source: str
    note: str = ""


@dataclass(frozen=True)
class CreditBilling:
    """GitHub Copilot's token billing: the US-dollar value of one AI credit, and each Copilot
    model's five component rates in AI credits per million tokens, by the Copilot CLI's id."""
    credit_usd: float
    effective: dt.date
    source: str
    rates: Mapping[str, Mapping[str, float]]
    note: str = ""


@dataclass(frozen=True)
class PriceTable:
    """The shipped table with a project's `pricing.models` laid over it. `premium_request` is
    the price of one premium request, None when the table carries none. `copilot_billing` is
    the basis the project's Copilot plan bills on, and `billed_by_request` the ids `cost` reads
    as not priced because that plan bills them by request (none on token billing)."""
    models: Mapping[str, Price]
    stale_after_days: int
    origin: str
    overridden: tuple[str, ...] = field(default=())
    premium_request: RequestPrice | None = None
    copilot: CreditBilling | None = None
    copilot_billing: str = TOKEN_BILLING
    billed_by_request: tuple[str, ...] = field(default=())

    @property
    def newest_effective(self) -> dt.date | None:
        """The latest effective date of any entry, or None for an empty table."""
        return max((p.effective for p in self.models.values()), default=None)


class Cost(NamedTuple):
    """A reading's estimated cost. `usd` is None when the model has no price, and `unpriced` then
    says which model; a priced reading has `unpriced` None. `lower_bound` says why a figure priced
    from a total, for a model with a long-context rate, may fall short of the bill; else None."""
    usd: float | None
    model: str | None
    unpriced: str | None
    lower_bound: str | None = None


def _price(value, where: str, name: str, unit: str = _USD) -> float:
    if value is None:
        raise PriceTableError(f"{where} has no '{name}' price")
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) \
            or value < 0:
        raise PriceTableError(f"{where} has '{name}' {value!r}, not a price: give {unit} as a "
                              "number of 0 or more")
    return float(value)


def _entry(raw, where: str, model: str | None) -> Price:
    """Validate one entry. `where` names it in a refusal; `model` is the id the entry must carry
    (a config key), or None to read it from the entry's own `model` field."""
    if not isinstance(raw, Mapping):
        raise PriceTableError(f"{where} is not a mapping of fields")
    unknown = sorted(set(raw) - set(REQUIRED) - set(OPTIONAL) - {LONG_CONTEXT})
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
    long = (None if raw.get(LONG_CONTEXT) is None else
            _long_context(raw[LONG_CONTEXT], f"{where} {LONG_CONTEXT}", model))
    return Price(model=model, effective=effective, source=source, note=note, long_context=long,
                 **values)


def _long_context(raw, where: str, model: str) -> Price:
    """An entry's long-context block as a price under `model` + `LONG_CONTEXT_ID`, refused by
    name on the same terms as an entry, and when its threshold is not a whole number of 1 or
    more."""
    if not isinstance(raw, Mapping):
        raise PriceTableError(f"{where} is not a mapping of fields")
    known = set(COMPONENTS) | {"from_prompt_tokens", "effective", "source"} | set(OPTIONAL)
    unknown = sorted(set(raw) - known)
    if unknown:
        raise PriceTableError(f"{where} has unknown field(s) {', '.join(map(repr, unknown))}")
    least = raw.get("from_prompt_tokens")
    if isinstance(least, bool) or not isinstance(least, int) or least < 1:
        raise PriceTableError(f"{where} has 'from_prompt_tokens' {least!r}: give the prompt "
                              "size in tokens from which the rates apply, a whole number of 1 "
                              "or more")
    values = {name: _price(raw.get(name), where, name) for name in COMPONENTS}
    effective, source, note = _dated(raw, where)
    return Price(model=model + LONG_CONTEXT_ID, effective=effective, source=source, note=note,
                 from_prompt_tokens=least, **values)


def _list(models: dict, price: Price) -> None:
    """Add `price` to `models` with its long-context price under its own id, replacing whatever
    either id held, so an entry replaced whole loses a long-context price it no longer carries."""
    models[price.model] = price
    models.pop(price.model + LONG_CONTEXT_ID, None)
    if price.long_context is not None:
        models[price.long_context.model] = price.long_context


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


def credit_billing(raw, where: str = COPILOT) -> CreditBilling:
    """Validate a Copilot token-billing block: `credit_usd`, `effective`, `source` and a `models`
    list of rates, each a `model` id and its five components in AI credits per million tokens,
    with an optional `note` on the block and on each rate. Raises `PriceTableError` naming
    `where` and the field; a missing value is refused, never read as 0."""
    if not isinstance(raw, Mapping):
        raise PriceTableError(f"{where} is not a mapping of fields")
    unknown = sorted(set(raw) - set(COPILOT_REQUIRED) - set(OPTIONAL))
    if unknown:
        raise PriceTableError(f"{where} has unknown field(s) {', '.join(map(repr, unknown))}; "
                              f"it carries {', '.join(COPILOT_REQUIRED)}")
    credit = _price(raw.get("credit_usd"), where, "credit_usd", "US dollars per AI credit")
    effective, source, note = _dated(raw, where)
    rows = raw.get("models")
    if not isinstance(rows, list) or not rows:
        raise PriceTableError(f"{where} has no 'models' list of rates in {_CREDITS}")
    rates: dict[str, dict[str, float]] = {}
    for n, row in enumerate(rows, start=1):
        at = f"{where}: model {n}"
        if not isinstance(row, Mapping):
            raise PriceTableError(f"{at} is not a mapping of fields")
        model = row.get("model")
        if not isinstance(model, str) or not model.strip():
            raise PriceTableError(f"{at} has no 'model' id")
        model = model.strip()
        at = f"{at} ({model})"
        unknown = sorted(set(row) - set(COPILOT_RATE_REQUIRED) - set(OPTIONAL))
        if unknown:
            raise PriceTableError(f"{at} has unknown field(s) {', '.join(map(repr, unknown))}; "
                                  f"a rate carries {', '.join(COPILOT_RATE_REQUIRED)}")
        if not isinstance(row.get("note") or "", str):
            raise PriceTableError(f"{at} has a 'note' that is not text")
        if model in rates:
            raise PriceTableError(f"{at} repeats model {model!r}")
        rates[model] = {c: _price(row.get(c), at, c, _CREDITS) for c in COMPONENTS}
    return CreditBilling(credit_usd=credit, effective=effective, source=source, rates=rates,
                         note=note)


def _in_dollars(model: str, billing: CreditBilling) -> Price:
    """A Copilot model's credit rates as US-dollar prices: each rate times the credit's value."""
    rates = billing.rates[model]
    return Price(model=model, effective=billing.effective, source=billing.source,
                 note=f"Copilot token billing in AI credits at ${billing.credit_usd:g} a credit",
                 **{c: rates[c] * billing.credit_usd for c in COMPONENTS})


def _shipped(path: Path) -> tuple[dict[str, Price], RequestPrice | None, CreditBilling | None]:
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
        _list(table, price)
    request = doc.get(PREMIUM_REQUEST)
    request = (None if request is None else
               request_price(request, f"{Path(path).name}: {PREMIUM_REQUEST}"))
    billing = None
    if COPILOT in doc:
        billing = credit_billing(doc[COPILOT], f"{Path(path).name}: {COPILOT}")
        for model in billing.rates:
            if model in table:
                raise PriceTableError(f"{Path(path).name}: {COPILOT} prices {model!r}, which "
                                      "the table's models list prices too, so a lookup by id "
                                      "would be ambiguous")
            table[model] = _in_dollars(model, billing)
    return table, request, billing


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
    entry, a Copilot id among them. `pricing.premium_request` replaces the shipped
    premium-request price whole. The shipped table's Copilot block prices its ids in US dollars
    beside the `models` entries, each rate times the credit's value (`credit_billing`).
    `pricing.stale_after_days` is a whole number of days of 1 or more. `pricing.copilot_billing`
    is `tokens` (unset or null) or `requests`, which leaves every id the Copilot block rates
    unpriced (`billed_by_request`), a `pricing.models` entry for one among them.

    Raises `PriceTableError` naming the entry and the field, or the file when the table itself
    cannot be read."""
    path = Path(path) if path is not None else TABLE_PATH
    models, request, billing = _shipped(path)
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
        _list(models, _entry(raw, f"pricing.models.{model}", model))
        overridden.append(model)
    if pricing.get(PREMIUM_REQUEST) is not None:
        request = request_price(pricing[PREMIUM_REQUEST], f"pricing.{PREMIUM_REQUEST}")
    days = pricing.get("stale_after_days", DEFAULT_STALE_AFTER_DAYS)
    if isinstance(days, bool) or not isinstance(days, int) or days < 1:
        raise PriceTableError(f"pricing.stale_after_days is {days!r}: give a whole number of days, "
                              "1 or more")
    basis = pricing.get(COPILOT_BILLING)
    basis = TOKEN_BILLING if basis is None else basis
    if not isinstance(basis, str) or basis not in BILLING_BASES:
        raise PriceTableError(f"pricing.{COPILOT_BILLING} is {basis!r}: give {TOKEN_BILLING} "
                              f"(GitHub's token billing in AI credits, the default) or "
                              f"{REQUEST_BILLING} (a plan kept on request-based billing)")
    by_request = (tuple(sorted(billing.rates))
                  if basis == REQUEST_BILLING and billing is not None else ())
    origin = str(path) + (" with the project's pricing.models" if overridden else "")
    return PriceTable(models=models, stale_after_days=days, origin=origin,
                      overridden=tuple(sorted(overridden)), premium_request=request,
                      copilot=billing, copilot_billing=basis, billed_by_request=by_request)


def long_context(model: str | None, table: PriceTable) -> Price | None:
    """`model`'s long-context price, listed under its `LONG_CONTEXT_ID` id; None for a model
    priced at one rate whatever its prompt size."""
    name = (model or "").strip()
    if not name or name.endswith(LONG_CONTEXT_ID):
        return None
    return table.models.get(name + LONG_CONTEXT_ID)


def request_id(model: str | None, prompt_tokens: int, table: PriceTable) -> str | None:
    """The id one request of `model` is priced under: its long-context id when its prompt of
    `prompt_tokens` reaches that price's `from_prompt_tokens`, else `model`."""
    long = long_context(model, table)
    if long is not None and long.from_prompt_tokens and prompt_tokens >= long.from_prompt_tokens:
        return long.model
    return model


def cost(model: str | None, components: Mapping[str, int],
         table: PriceTable | None = None, prompt_tokens: int | None = None) -> Cost:
    """A reading's estimated cost in US dollars: each component's tokens times its price per
    million, summed. A component the reading omits counts as no tokens; one the table does not
    know, or a count that is not a whole number of 0 or more, raises ValueError rather than
    dropping out of the sum. A model the table does not list costs `usd=None`, naming it, and
    so does one the plan bills by request (`billed_by_request`), saying so.

    `prompt_tokens` is given when `components` are ONE request's, of a prompt that size: a
    model with a long-context price is then priced at the rate that prompt bills, for all its
    tokens (`request_id`). Without it the components are a total, which cannot tell a long
    request from a short one, so such a model is priced at its own rate and `lower_bound` says
    the figure may fall short."""
    for name, tokens in components.items():
        if name not in COMPONENTS:
            raise ValueError(f"reading component {name!r} is not one of {', '.join(COMPONENTS)}")
        if isinstance(tokens, bool) or not isinstance(tokens, int) or tokens < 0:
            raise ValueError(f"reading component {name!r} is {tokens!r}, not a token count")
    table = table if table is not None else load()
    name = (model or "").strip()
    if name and prompt_tokens is not None:
        name = request_id(name, prompt_tokens, table)
    if not name:
        return Cost(None, model, "not priced: the reading names no model")
    if name in table.billed_by_request:
        return Cost(None, model, f"not priced: the plan bills by request "
                                 f"(pricing.{COPILOT_BILLING}: {REQUEST_BILLING}), so model "
                                 f"{name}'s tokens carry no price and the premium requests do")
    price = table.models.get(name)
    if price is None:
        return Cost(None, model, f"not priced: model {name} is not in the price table "
                                 f"(add it under pricing.models)")
    usd = sum(components.get(c, 0) * getattr(price, c) for c in COMPONENTS) / _PER
    long = long_context(name, table) if prompt_tokens is None else None
    if long is None:
        return Cost(usd, model, None)
    reach = (f"{long.from_prompt_tokens:,} tokens or more" if long.from_prompt_tokens else
             "past its long-context threshold")
    return Cost(usd, model, None, f"a lower bound for {name}: its provider bills a request "
                                  f"whose prompt is {reach} at the long-context rate for all its "
                                  f"tokens, and a total cannot tell those requests apart, so "
                                  f"every token here is priced at the shorter prompts' rate")


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
