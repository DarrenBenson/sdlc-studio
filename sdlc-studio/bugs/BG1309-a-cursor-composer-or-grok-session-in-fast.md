# BG1309: A Cursor Composer or Grok session in Fast mode is priced at the standard rate, because the model id a reading carries cannot tell Fast from standard

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/templates/model-prices.json, .claude/skills/sdlc-studio/scripts/lib/prices.py, .claude/skills/sdlc-studio/scripts/tests/test_prices.py, changelog.d/BG1309.md
> **Evidence:** US1143's builder hand-back and the notes on its Composer and Grok entries (2026-11-09)
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-09T13:30:58Z

## Summary

Found building US1143 on 2026-11-09. Cursor's pricing page (`https://cursor.com/docs/models-and-pricing`, read 2026-11-09) makes Fast the default for Composer, and for Grok 4.7 on Premium and higher plans, and bills Fast higher (Composer Fast $3 / $0.50 / $15 per million input / cached / output tokens, against $0.50 / $0.20 / $2.50 standard). A reading carries only the model id the caller launched it with, which is the same for both speeds, so `lib/prices.py` prices every Fast session at the standard rate and under-states its dollar cost several times over. US1143 states the limit in the table's notes and reference-config.md; nothing prices it. xAI's own page has the same shape: a priority tier billed at twice the standard rate, which an `xai/<model>` reading cannot tell apart either (qa-seat-US1143-r1, non-blocking finding 3, 2026-11-09). The same review's round 2 found the Cursor Fast caveat still on the `xai/grok-4.7`, `xai/grok-4.6` and `xai/grok-4.5` notes, though xAI's page says Fast is not on its public API; the fix moves that caveat to the Cursor slugs alone.

## Steps to Reproduce

1. Run a lane on Cursor with Composer in Fast mode (Cursor's default) and meter it.
2. Read the sprint report's dollar figure for the run.
3. It is priced at Composer's standard rate, not the Fast rate Cursor bills.

## Proposed Fix

Carry the speed with the reading where a harness exposes it (a `--fast` flag, a model suffix or the ledger), price Fast rows from their own dated entries, and where the speed cannot be read, label the figure a lower bound rather than a price.

## Acceptance Criteria

- [ ] **AC1** Given a reading under a Cursor slug whose Fast variant bills higher and cannot be told apart from standard (`composer-2.5`, `grok-4.7`), when `lib/prices.py` prices it, then the cost carries a `lower_bound` saying a Fast session bills more than the figure, so the report's Dollar cost row says a lower bound. Fails on: a Fast session's dollars stated as a price when they may fall short several times over.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_prices.py::NonClaudePriceTests::test_a_cursor_slug_with_a_fast_variant_is_priced_as_a_lower_bound
- [ ] **AC2** Given a reading that does carry the speed (the id or recorded speed names Fast), when it is priced, then it is priced from the Fast entry's own dated and sourced rates (Composer 2.5 Fast at 3.00, 0.50 and 15.00 dollars per million input, cached and output tokens) and carries no Fast lower bound. Fails on: a known Fast session priced at the standard rate.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_prices.py::NonClaudePriceTests::test_a_reading_that_carries_fast_is_priced_from_the_fast_entry
- [ ] **AC3** Given the shipped price table, when its notes are read, then the Cursor Fast caveat sits on the Cursor slugs alone and no `xai/` entry carries it. Fails on: the caveat left on `xai/grok-4.7`, `xai/grok-4.6` and `xai/grok-4.5`, whose provider offers no Fast on its public API.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_prices.py::NonClaudePriceTests::test_the_fast_caveat_sits_on_the_cursor_slugs_alone

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
