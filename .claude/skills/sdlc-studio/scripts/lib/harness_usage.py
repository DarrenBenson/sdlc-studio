"""Each CLI's headless usage output, normalised to one basis.

`parse(harness, text)` reads the stdout of one headless session of Claude Code
(`-p --output-format json`), Cursor CLI (`-p --output-format json`), Codex CLI (`exec --json`),
Copilot CLI (`-p --output-format json`) or OpenCode (`run --format json`) and returns a `Usage`:

* `input` - prompt tokens neither read from nor written to a cache;
* `cache_read`, `cache_write` - the cached prompt tokens, apart from `input`, so
  `input + cache_read + cache_write` (`prompt`) is the prompt counted once; `cache_write_1h` is
  the part of `cache_write` held for an hour, where the CLI splits it;
* `output` - generated tokens, reasoning included; `reasoning` - the part of `output` that was
  reasoning;
* `model` and `session_id`;
* `by_model` - each model's own counts, on the same basis, where the CLI names its models
  (Claude Code's `modelUsage`, Copilot's `modelMetrics`): they sum to the session's counts, so
  a session that used two models is priced per model. None where the output names none.

A reasoning count or a model the output does not carry is None and named in `unreported`,
never zero; `cache_write_1h` is None where the CLI does not split its writes.

How each CLI forms "input", from the sessions captured on 2026-11-06 (the fixtures under
`tests/fixtures/harness_usage/`). Each is marked observed, or assumed with the reason:

* Claude Code: `modelUsage.<model>` per model (falling back to `usage`). Input excludes cache:
  observed, since the capture's `costUSD` is reproduced exactly with 2 input beside 11382 cache
  reads and 17126 one-hour writes. `outputTokens` holds `thinkingTokens`: observed, the same fit
  prices all 35 output tokens, 31 of them thinking.
* Cursor CLI: `usage`. `inputTokens` excludes `cacheReadTokens`: observed, two directories under
  one parent read 23289 input with no cache, and 17312 input beside 6016 cache reads where the
  prefix was cached; their prompts agree (23289 and 23328) only with the reads apart, and read
  as inside, the second would be 6k short. `cacheWriteTokens` is taken as apart too: assumed,
  since every capture wrote none. No reasoning count and no model are printed.
* Codex CLI: `turn.completed.usage`, summed over turns (assumed per turn: one was captured).
  `input_tokens` holds `cached_input_tokens`: observed, since the session's rollout records
  `total_tokens` 14529, which is the 14524 input plus 5 output; read apart, with the 12288
  cached added, it would be 26817.
  `cache_write_input_tokens` is taken as inside `input_tokens` and `reasoning_output_tokens` as
  inside `output_tokens`: assumed, both were 0. The stream names no model.
* Copilot CLI: the last `session.usage_checkpoint` or `session.shutdown`, whose
  `accountingSnapshot.modelMetrics.<model>.usage` is taken as a running total, so it is read
  once and never summed: assumed from its session-total fields, since one call was captured. `inputTokens` holds both cache parts: observed, 27582 input is 4 uncached plus
  27578 cache writes, as the session accounting books it. `reasoningTokens` is taken as inside
  `outputTokens`: assumed, it was 0.
* OpenCode: `step_finish` part `tokens`, summed over steps (assumed per step: one was captured).
  Input excludes cache: observed, `total` is 9896 input + 3 output + 1792 cache reads. Reasoning
  is taken as reported beside output, so `output` adds it: assumed, it was 0. The stream names
  no model.

The `model` keyword fills the model where the output names none, and `model_source` says which
supplied it.

A non-zero exit (the caller's `exit_code`, or Copilot's own `exitCode`), output carrying no
usage (a usage or accounting container that is not a JSON object included), and a line that
does not parse as a JSON object, or a count that is not one, are each unmetered: `metered`
False, `unmetered` naming which (`NONZERO_EXIT`, `NO_USAGE`, `UNPARSEABLE`), `reason` saying
why, and every count None, never zero.

Where the output carries the harness's own total, the normalised figure is checked against it
(`checks`): Claude Code's `total_cost_usd` against the normalised counts priced from `prices`,
Copilot's session accounting (`accountingSnapshot.tokenDetails`) and OpenCode's `total` against
the normalised token total. A gap above `TOLERANCE` is named in `disagreements`; a check that
cannot be made, as for a model `prices` does not hold, is recorded `unchecked`, never passed.
"""
from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field

HARNESSES = ("claude", "cursor", "codex", "copilot", "opencode")
NONZERO_EXIT = "nonzero-exit"
NO_USAGE = "no-usage"
UNPARSEABLE = "unparseable"
#: The fraction by which the normalised figure may differ from the harness's own total.
TOLERANCE = 0.05
#: The per-million US dollar rate keys `prices` holds for a model; `cache_write` is the
#: five-minute (or unsplit) write rate.
RATE_KEYS = ("input", "output", "cache_read", "cache_write", "cache_write_1h")
_COUNTS = ("input", "cache_read", "cache_write", "cache_write_1h", "output", "reasoning")


@dataclass(frozen=True)
class Check:
    """One comparison of the normalised figure with a total the harness reported."""
    against: str
    harness: float | None
    normalised: float | None
    status: str  # "agrees", "disagrees" or "unchecked"
    detail: str


@dataclass(frozen=True)
class Usage:
    harness: str
    metered: bool
    unmetered: str | None = None
    reason: str | None = None
    input: int | None = None
    cache_read: int | None = None
    cache_write: int | None = None
    cache_write_1h: int | None = None
    output: int | None = None
    reasoning: int | None = None
    model: str | None = None
    model_source: str | None = None
    session_id: str | None = None
    unreported: tuple[str, ...] = ()
    checks: tuple[Check, ...] = field(default_factory=tuple)
    by_model: Mapping[str, Mapping[str, int | None]] | None = field(default=None, hash=False)

    @property
    def prompt(self) -> int | None:
        """The prompt counted once: input, cache read and cache write together."""
        if not self.metered:
            return None
        return self.input + self.cache_read + self.cache_write

    @property
    def disagreements(self) -> tuple[str, ...]:
        return tuple(f"{c.against}: {c.detail}" for c in self.checks if c.status == "disagrees")


class _Refused(Exception):
    def __init__(self, kind: str, reason: str) -> None:
        super().__init__(reason)
        self.kind, self.reason = kind, reason


def _count(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _need(record: Mapping, key: str, where: str) -> int:
    value = record.get(key)
    if not _count(value):
        raise _Refused(UNPARSEABLE, f"{where} {key} {value!r} does not parse as a token count")
    return value


def _opt(record: Mapping, key: str, where: str) -> int | None:
    return None if key not in record else _need(record, key, where)


def _events(text: str) -> list[dict]:
    """The output as JSON objects: one document, or one per non-blank line."""
    try:
        whole = json.loads(text)
    except ValueError:
        whole = None
    if isinstance(whole, dict):
        return [whole]
    events = []
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except ValueError:
            event = None
        if not isinstance(event, dict):
            raise _Refused(UNPARSEABLE, f"line {number} does not parse as a JSON object")
        events.append(event)
    return events


def _container(value, where: str) -> dict:
    """`value` as a JSON object, an absent one (None) as empty; any other value is no usage."""
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise _no_usage(f"{where} is not a JSON object")
    return value


def _last(events: list[dict], *types: str) -> dict | None:
    return next((e for e in reversed(events) if e.get("type") in types), None)


def _no_usage(what: str) -> _Refused:
    return _Refused(NO_USAGE, f"no usage in the output: {what}")


def _check(against: str, harness: float, normalised: float, unit: str = "") -> Check:
    gap = abs(normalised - harness) / harness if harness else (0.0 if not normalised else 1.0)
    status = "disagrees" if gap > TOLERANCE else "agrees"
    detail = (f"the harness reports {harness:g}{unit}, the normalised figure is "
              f"{normalised:g}{unit}, {gap:.1%} apart")
    return Check(against, harness, normalised, status, detail)


def _claude(events, prices):
    result = _last(events, "result") or (events[-1] if events else None)
    if not result or not (result.get("modelUsage") or result.get("usage")):
        raise _no_usage("no result carrying usage or modelUsage")
    per_model = {}
    models = _container(result.get("modelUsage"), "modelUsage")
    if models:
        for name, mu in models.items():
            where = f"modelUsage.{name}"
            mu = _container(mu, where)
            per_model[name] = {
                "input": _need(mu, "inputTokens", where),
                "cache_read": _need(mu, "cacheReadInputTokens", where),
                "cache_write": _need(mu, "cacheCreationInputTokens", where),
                "cache_write_1h": _opt(mu, "cacheCreationEphemeral1hInputTokens", where),
                "output": _need(mu, "outputTokens", where),
                "reasoning": _opt(mu, "thinkingTokens", where)}
    else:
        u = _container(result["usage"], "usage")
        split = _container(u.get("cache_creation"), "usage.cache_creation")
        per_model[None] = {
            "input": _need(u, "input_tokens", "usage"),
            "cache_read": _need(u, "cache_read_input_tokens", "usage"),
            "cache_write": _need(u, "cache_creation_input_tokens", "usage"),
            "cache_write_1h": _opt(split, "ephemeral_1h_input_tokens", "usage.cache_creation"),
            "output": _need(u, "output_tokens", "usage"),
            "reasoning": _opt(_container(u.get("output_tokens_details"),
                                         "usage.output_tokens_details"),
                              "thinking_tokens", "usage.output_tokens_details")}
    counts = _sum(per_model.values())
    model = _largest(per_model)
    checks = ()
    total = result.get("total_cost_usd")
    if isinstance(total, (int, float)) and not isinstance(total, bool):
        checks = (_cost_check(total, per_model, prices or {}),)
    return counts, model, result.get("session_id"), checks, _split(per_model)


def _cost_check(total: float, per_model: dict, prices: Mapping) -> Check:
    cost, missing = 0.0, []
    for name, c in per_model.items():
        rates = prices.get(name) if name is not None else None
        if rates is None:
            missing.append(f"no price for {name or 'an unnamed model'}")
            continue
        one_hour = c["cache_write_1h"] or 0
        weights = {"input": c["input"], "output": c["output"], "cache_read": c["cache_read"],
                   "cache_write": c["cache_write"] - one_hour, "cache_write_1h": one_hour}
        for key, tokens in weights.items():
            if tokens and key not in rates:
                missing.append(f"no {key} rate for {name}")
            elif tokens:
                cost += tokens * rates[key] / 1_000_000
    if missing:
        return Check("total_cost_usd", total, None, "unchecked",
                     f"the harness reports {total:g} USD, not checked: {'; '.join(missing)}")
    return _check("total_cost_usd", total, cost, " USD")


def _cursor(events, _prices):
    result = _last(events, "result") or (events[-1] if events else None)
    u = (result or {}).get("usage")
    if not isinstance(u, dict):
        raise _no_usage("no result carrying usage")
    counts = {"input": _need(u, "inputTokens", "usage"),
              "cache_read": _need(u, "cacheReadTokens", "usage"),
              "cache_write": _need(u, "cacheWriteTokens", "usage"),
              "cache_write_1h": None, "output": _need(u, "outputTokens", "usage"),
              "reasoning": None}
    return counts, None, result.get("session_id"), (), None


def _codex(events, _prices):
    turns = [e for e in events if e.get("type") == "turn.completed"]
    if not turns or not all(isinstance(t.get("usage"), dict) for t in turns):
        raise _no_usage("no turn.completed event carrying usage")
    per_turn = []
    for t in turns:
        u = t["usage"]
        total = _need(u, "input_tokens", "turn.completed.usage")
        read = _need(u, "cached_input_tokens", "turn.completed.usage")
        write = _need(u, "cache_write_input_tokens", "turn.completed.usage")
        per_turn.append({"input": _uncached(total, read, write, "input_tokens"),
                         "cache_read": read, "cache_write": write, "cache_write_1h": None,
                         "output": _need(u, "output_tokens", "turn.completed.usage"),
                         "reasoning": _opt(u, "reasoning_output_tokens", "turn.completed.usage")})
    started = _last(events, "thread.started") or {}
    return _sum(per_turn), None, started.get("thread_id"), (), None


def _uncached(total: int, read: int, write: int, name: str) -> int:
    if read + write > total:
        raise _Refused(UNPARSEABLE, f"cache parts {read} + {write} exceed {name} {total}, "
                                    f"which should hold them")
    return total - read - write


def _copilot(events, _prices):
    result = _last(events, "result")
    code = (result or {}).get("exitCode")
    if code not in (None, 0):
        raise _Refused(NONZERO_EXIT, f"the session reports exit status {code!r}")
    record = _last(events, "session.usage_checkpoint", "session.shutdown") or {}
    data = _container(record.get("data"), f"{record.get('type')}.data")
    snapshot = _container(data.get("accountingSnapshot"), "data.accountingSnapshot")
    metrics = snapshot.get("modelMetrics")
    if not isinstance(metrics, dict) or not metrics:
        raise _no_usage("no session.usage_checkpoint or session.shutdown carrying modelMetrics")
    per_model = {}
    for name, m in metrics.items():
        where = f"modelMetrics.{name}.usage"
        u = _container(_container(m, f"modelMetrics.{name}").get("usage"), where)
        read, write = _need(u, "cacheReadTokens", where), _need(u, "cacheWriteTokens", where)
        per_model[name] = {"input": _uncached(_need(u, "inputTokens", where), read, write,
                                              "inputTokens"),
                           "cache_read": read, "cache_write": write, "cache_write_1h": None,
                           "output": _need(u, "outputTokens", where),
                           "reasoning": _opt(u, "reasoningTokens", where)}
    counts = _sum(per_model.values())
    checks = ()
    details = _container(snapshot.get("tokenDetails"), "accountingSnapshot.tokenDetails")
    if details:
        booked = [_container(d, f"accountingSnapshot.tokenDetails.{kind}").get("tokenCount")
                  for kind, d in details.items()]
        if all(_count(b) for b in booked):
            checks = (_check("session accounting", sum(booked), _token_total(counts)),)
        else:
            checks = (Check("session accounting", None, _token_total(counts), "unchecked",
                            "accountingSnapshot.tokenDetails holds a count that does not "
                            "parse"),)
    return (counts, _largest(per_model), (result or {}).get("sessionId"), checks,
            _split(per_model))


def _opencode(events, _prices):
    steps = [e for e in events if e.get("type") == "step_finish"]
    tokens = [_container(e.get("part"), "step_finish.part").get("tokens") for e in steps]
    if not steps or not all(isinstance(t, dict) for t in tokens):
        raise _no_usage("no step_finish event carrying tokens")
    per_step, totals = [], []
    for t in tokens:
        cache = _container(t.get("cache"), "tokens.cache")
        reasoning = _need(t, "reasoning", "tokens")
        per_step.append({"input": _need(t, "input", "tokens"),
                         "cache_read": _need(cache, "read", "tokens.cache"),
                         "cache_write": _need(cache, "write", "tokens.cache"),
                         "cache_write_1h": None,
                         "output": _need(t, "output", "tokens") + reasoning,
                         "reasoning": reasoning})
        totals.append(_opt(t, "total", "tokens"))
    counts = _sum(per_step)
    checks = ()
    if all(x is not None for x in totals):
        checks = (_check("total", sum(totals), _token_total(counts)),)
    session = steps[-1].get("sessionID") or (steps[-1].get("part") or {}).get("sessionID")
    return counts, None, session, checks, None


def _token_total(c: Mapping) -> int:
    return c["input"] + c["cache_read"] + c["cache_write"] + c["output"]


def _sum(records) -> dict:
    """Each count summed; a count any record leaves unreported stays None."""
    records = list(records)
    return {k: (None if any(r[k] is None for r in records) else sum(r[k] for r in records))
            for k in _COUNTS}


def _largest(per_model: dict) -> str | None:
    """The model that carried the most tokens, the session's model where it used several."""
    return max(per_model, key=lambda m: _token_total(per_model[m])) if per_model else None


def _split(per_model: dict) -> dict | None:
    """Each named model's own counts, a copy, or None where a model is unnamed (Claude Code's
    `usage` with no `modelUsage`), so a split never books a session under no model."""
    if not per_model or None in per_model:
        return None
    return {name: dict(counts) for name, counts in per_model.items()}


_READERS = {"claude": _claude, "cursor": _cursor, "codex": _codex, "copilot": _copilot,
            "opencode": _opencode}


def parse(harness: str, text: str, *, exit_code: int | None = None, model: str | None = None,
          prices: Mapping[str, Mapping[str, float]] | None = None) -> Usage:
    """The normalised usage of one headless session's stdout `text`.

    `exit_code` is the CLI's exit status, where the caller has it; `model` is the model the
    session was launched with, used only where the output names none; `prices` maps a model to
    its per-million US dollar rates (`RATE_KEYS`), for the check against Claude Code's
    `total_cost_usd`. Raises ValueError for a harness not in `HARNESSES`."""
    if harness not in _READERS:
        raise ValueError(f"unknown harness {harness!r}; expected one of {', '.join(HARNESSES)}")
    try:
        if exit_code not in (None, 0):
            raise _Refused(NONZERO_EXIT, f"the CLI exited with status {exit_code}")
        counts, named, session, checks, split = _READERS[harness](_events(text), prices)
    except _Refused as refused:
        return Usage(harness, False, unmetered=refused.kind, reason=refused.reason)
    source = "output" if named else ("caller" if model else None)
    unreported = tuple(k for k in ("reasoning",) if counts[k] is None)
    if not (named or model):
        unreported += ("model",)
    return Usage(harness, True, model=named or model, model_source=source, session_id=session,
                 unreported=unreported, checks=checks, by_model=split, **counts)
