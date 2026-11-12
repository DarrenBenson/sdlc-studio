# US1000: The cost section states the run's cost in money from a pricing snapshot frozen at the close

> **Status:** Done
> **Delivers:** CR0610
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/templates/core/sprint-report.md, .claude/skills/sdlc-studio/templates/reports/sprint-report.html, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_report_pricing_snapshot.py, .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_delegated_tokens.py, changelog.d/US1000.md
> **Epic:** EP0276
> **Points:** 5
> **Depends on:** US0997
> **Persona:** Graham Doyle

## User Story

**As** a founder-engineer paying for the tokens a sprint burns
**I want** the report of record to show the prices the run was costed at and the money each model's tokens cost
**So that** I read the sprint's cost in money on the signed page, priced from my own rates, instead of re-pricing its tokens at whatever the rate is today

## Acceptance Criteria

- **AC1:** Given a project `pricing.models` entry for `claude-opus-5-5` whose input price is 15 (its other four component prices, `effective` and `source` set) and a run metered on that model, when `sprint close` files the report, then the cost section and its Markdown twin list each model the Dollar cost row priced with its five component prices in US dollars per million tokens, the entry's effective date and its source, all read from the page's own `price_table`, beside that model's dollars.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_pricing_snapshot.py::PricingSnapshotTests::test_close_freezes_prices_and_states_money
  - **Verified:** yes (2026-11-12)
- **AC2:** Given a run whose meter reading leaves delegated agents' spend out (so the Tokens row adds the delegated totals), one delegated total read from an agent's transcript with a per-model split on `claude-opus-5-5` and one supplied `--tokens` total with no split, when `sprint close` files the report, then the Dollar cost row adds the read total's dollars at its model's rates, names the supplied total as unpriced with its token count, and says how many tokens the dollars leave unpriced; no money figure reads $0 or an estimate for it; and over a meter that reads the subagent transcripts no delegated total is priced a second time. An unpriced model and a `mixed` row read as they do at HEAD: named with their share, never $0.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_pricing_snapshot.py::PricingSnapshotTests::test_unpriced_tokens_are_named_never_zero_or_estimated
  - **Verified:** yes (2026-11-12)
- **AC3:** Given that page signed and committed, when the `pricing.models` entry's input price for `claude-opus-5-5` is changed to 20 and `sprint_report check` runs in a fresh clone, then it reads VALID and the page still states 15 and the dollars it was filed with.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_pricing_snapshot.py::PricingSnapshotTests::test_a_price_change_after_the_close_moves_nothing
  - **Verified:** yes (2026-11-12)
- **AC4:** Given a signed page filed before this change (dollars under USD_RULE, no price rows and no delegated dollars, as RPT0028) and a page filed after it, when a price is configured and `sprint_report check` runs on each, then both read VALID with their Markdown twins and only the later page carries the price rows and the delegated dollars.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_pricing_snapshot.py::PricingSnapshotTests::test_a_page_without_a_snapshot_is_unchanged
  - **Verified:** yes (2026-11-12)

## Notes

- Release: 6.4, run ten (D0461); was 6.3 (D0388) (D0355 breakdown G2, reviewed by the refine panel; see the request's revision history).
- Re-scoped at HEAD 508e2408 (2026-11-12). Run seven's US1122 and US1123 shipped most of what this story first asked: a dated per-model price table (lib/prices.py, templates/model-prices.json, `pricing.models` overrides documented in reference-config.md:344-364), the Dollar cost, Dollars per point and per-unit dollar rows (`_usd_rows`, sprint_report.py:3801; `_unit_usd`, :3881), the table carried on the page as `price_table` (`USD_RULE`, `PRICE_TABLE`, :4437-4439) and, since `TABLE_RULE` (:4446), digested and replayed on every re-derivation, signed or not (:4585-4609). RPT0028 states $126.64 covering 100% of the priced tokens.
- Already met at HEAD, so not left to a builder: the original AC3 in substance (test_report_usd.py::ReportUsdTests::test_a_signed_page_keeps_the_prices_it_was_filed_with and ::test_an_unsigned_page_keeps_the_prices_it_was_filed_with), the original AC4 in substance (::test_the_usd_mark_round_trips), and the original AC2 for an unpriced model and a `mixed` row (::test_an_unpriced_model_is_named_with_the_covered_share). AC3 and AC4 stay as guards on the rows this story adds.
- Not met at HEAD, and this story's remaining scope: (1) the rendered page states only the table's effective date beside the dollars (`_table_note`, :3794), never a model's prices or source, so CR0610's "(model, price, currency, date)" lives only in the JSON envelope; (2) a delegated total the Tokens row adds over a meter that leaves subagents out sits outside the Priced cost and so outside the Dollar cost (help/sprint.md:81; `_usd_rows` prices `run_tokens[BY_MODEL]` alone, :3807), and nothing names it against the dollars.
- The original AC1 named a flat `pricing.claude-opus-5-5: 15` key. The report never reads flat keys: they feed telemetry.model_price for `sprint_report show` only (reference-config.md:364), and the table prices five components, so the criterion now names a `pricing.models` entry.
- AC1 must fail on: price rows read from today's config or the shipped table at render rather than the page's `price_table`; a price row with no unit (US dollars per million tokens) or no effective date; rows built from `_cost_section`'s stamp grouping (:4241), which reads `mixed` on RPT0028, rather than from the models `run_state.usd` priced
- AC2 must fail on: the supplied total priced at the session model's rate or at $0; the delegated read totals priced again over a meter that already reads every subagent transcript (`includes_subagents`); the unpriced supplied tokens left out of the reach clause (`_usd_reach`, :3785)
- AC3 must fail on: the new rows re-reading today's config at re-derivation instead of the page's `price_table`
- AC4 must fail on: the new rows or delegated dollars emitted for a page with no mark for them (a new rule mark round-trips as `USD_RULE` does), or a template that prints an empty price block for such a page
- Keep `run_state.usd`'s signature (lib/run_state.py:1703); test_prices.py, test_report_usd.py and test_lane_run.py call it. Fold the delegated splits into the by-model dict it is given.
- Existing tests that pin what this changes: test_report_usd.py (dollar rows, reach clause, round trips), test_sprint_report.py:4796-4810 (a filed-before page's cost figures in page order), test_lean_report.py:305-307 (cost rows and tokens_delegated), test_lean_lane_delegated_tokens.py:124 and :163 (the delegated figure).
- Docs it makes stale: help/sprint.md:81-86 and reference-sprint.md:667-680 (#dollar-cost) say what the dollars cover.
- A re-close re-derives at the table in force (`_file_the_report` passes no `filed_prices`, sprint.py:10050-10051); out of scope here.
- Depends on US0997 (the new figures cite the tracked record). US0991 is Done; US0999 is no longer a dependency, since this prices transcript-read splits and a supplied total stays unpriced with or without a model. If US0999 lands first, name the unpriced total by its recorded model.
- Overlaps BG1330 (run eleven), which prices each unit's builder automatically at `lane land`; this story prices the run-level row. Not absorbed.
- Serves Maya's scenario, 'priced from her own rates' (maya-okafor-founder-engineer.md:65-66), and Abena Osei's End goal 3 (cost per point by harness).
- Sized at 5 still: a new rule mark and its round trip, two templates, the price rows and the delegated dollars.

## Triage (2026-10-21)

Kept (D0387). To plan it:

- Same open CR0610 consult questions as US0999 (pricing basis 'confirm', money scope (a) or (b)); settle before planning.
- Release note stale: the story says 'Release: 6.2' but D0382 (2026-10-20, supersedes D0381) sets the path to the 6.2.0 tag as run three plus run four's doc refreshes only, so this lands after 6.2.0; re-tag when a run takes it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G2 after the refine panel's review |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
| 2026-11-12 | Claude Opus 5.5 (engineering seat) | Re-groomed at HEAD for run ten: re-scoped to what US1122 and US1123 left (per-model prices on the page, delegated dollars over a meter that leaves subagents out); AC1 now names a `pricing.models` entry, not a flat key; AC2 now covers delegated totals, unpriced models keeping HEAD's reading; AC3 and AC4 kept as guards on the new rows; Affects drops sprint.py, telemetry.py, reference-config.md and reference-scripts-domain.md and gains lib/run_state.py, reference-sprint.md and four test modules; Depends on drops US0999 and US0991; release set to 6.4 (D0461) |
