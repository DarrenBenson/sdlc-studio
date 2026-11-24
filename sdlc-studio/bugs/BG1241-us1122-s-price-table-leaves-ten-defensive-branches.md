# BG1241: US1122's price table leaves ten defensive branches unpinned, promises a date format its parser does not hold to, and prices a bare `cost()` call without the project's overrides

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/prices.py, .claude/skills/sdlc-studio/templates/model-prices.json, .claude/skills/sdlc-studio/scripts/tests/test_prices.py, changelog.d/BG1241.md
> **Evidence:** run seven (RUN-01M6RAP7) US1122 review round 1
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T14:35:52Z

## Summary

Run seven, US1122 round 1 (APPROVE, non-blocking). (1) Ten mutants of `prices.py` survive the suite, each on a branch no test exercises: the empty table reading as stale (`prices.py:222-223`, a claim the `stale()` docstring makes), a blank model id refused (:108), a datetime effective converted to a date (:118-119), a config entry whose model differs from its key (:112-113), a non-text note (:130), a pricing block or `pricing.models` that is not a mapping (:175-178), a table with no models list (:141), an unreadable table file (:138) and the stripped lookup in `cost()` (:206). The unmutated code is correct on each and none sits in a Fails-on clause. (2) The effective-date refusal says "not a YYYY-MM-DD date" (`prices.py:124`), but `date.fromisoformat` on Python 3.11+ also accepts `20261106` and `2026-W45-5`, and a YAML integer 20261106 becomes 2026-11-06 through `str()` (:122); all three were accepted. (3) `cost()` with no table argument calls `load()` without a repo root (`prices.py:205`), so a caller that leaves the table out silently ignores the project's `pricing.models` and re-reads the JSON on every call; the docstring does not say so. (4) `claude-haiku-5-5` carries only its rates for prompts up to 100,000 tokens (`model-prices.json:16`); the live pricing page charges 5x on every component above that, so a long-prompt session is understated by up to 5x. The entry's note says so, but no consumer surfaces it. (5) The live page still prices Claude Mythos 5, Opus 4.5 and Sonnet 4.5, which the table does not ship, so a reading on any of them reports not priced (AC2 allows it); and `opus-5-5`'s cache read is the 0.05x rate as `sonnet-5-5`'s is, but only the `sonnet-5-5` entry says so (`model-prices.json:8` against :13).

## Steps to Reproduce

1. In a scratch copy apply each mutant named above and run `pytest .claude/skills/sdlc-studio/scripts/tests/test_prices.py`: all pass. 2. Load a table whose effective date is `2026-W45-5`: it is accepted. 3. Call `cost()` with no table in a project whose config overrides a model's price: the shipped price is used.

## Proposed Fix

Add one test per surviving branch. Refuse any effective date that is not literally YYYY-MM-DD (a pattern check before `fromisoformat`, and refuse a non-string), or reword the message to what the parser accepts. Make `cost()` take the repo root or require the table, and say which in its docstring. Mark a priced haiku figure whose prompts exceed 100,000 tokens as a lower bound wherever it is shown, or model the long-context tier. Add the three still-priced models and the `opus-5-5` cache-read note.

## Acceptance Criteria

- [ ] **AC1** Given a table entry whose `effective` is `20261106`, `2026-W45-5` or the YAML integer 20261106, when `prices.load` reads it, then each is refused naming the entry and the YYYY-MM-DD form, while `2026-11-06` still loads. Fails on: any date that is not literally YYYY-MM-DD being accepted.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_prices.py::PriceTableTests::test_an_effective_date_not_literally_yyyy_mm_dd_is_refused
- [ ] **AC2** Given each defensive branch the summary's item 1 names (an empty table, a blank model id, a datetime effective, a config entry whose model differs from its key, a non-text note, a pricing block or `pricing.models` that is not a mapping, a table with no models list, an unreadable table file, a model id with surrounding space passed to `cost()`), when the table is loaded or priced, then each gives the outcome its docstring states. Fails on: any of the ten named mutants passing the module.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_prices.py::PriceTableTests::test_each_defensive_branch_is_exercised
- [ ] **AC3** Given a project whose config overrides a model's price, when `cost()` is called with no table, then the figure is the project's overridden price or the call is refused for want of a table, and the docstring says which. Fails on: the shipped price returned silently.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_prices.py::PriceTableTests::test_cost_without_a_table_never_ignores_the_project_overrides
- [ ] **AC4** Given the shipped table, when it is loaded, then Claude Mythos 5, Opus 4.5 and Sonnet 4.5 each price with a source and an effective date, the `claude-opus-5-5` note names its 0.05x cache read, and a `claude-haiku-5-5` total priced without a prompt size is marked a lower bound. Fails on: a reading on any of the three reporting not priced, or a long-prompt haiku figure shown as exact.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_prices.py::PriceTableTests::test_the_shipped_table_prices_the_older_models_and_bounds_long_prompt_haiku

## Resolution

Won't Fix under D0613: the operator approved the product seat's second proposal (D0562) because only a test or pin is missing on behaviour that is right on every path a user reaches. Ten unpinned defensive branches in prices.py.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
| 2026-11-24 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0613: the operator approved the product seat's second list (D0562); reason in Resolution |
