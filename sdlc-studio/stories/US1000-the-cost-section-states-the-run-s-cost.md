# US1000: The cost section states the run's cost in money from a pricing snapshot frozen at the close

> **Status:** Draft
> **Delivers:** CR0610
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/telemetry.py, .claude/skills/sdlc-studio/templates/core/sprint-report.md, .claude/skills/sdlc-studio/templates/reports/sprint-report.html, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/reference-scripts-domain.md, .claude/skills/sdlc-studio/scripts/tests/test_report_pricing_snapshot.py, changelog.d/US1000.md
> **Epic:** EP0276
> **Points:** 5
> **Depends on:** US0997, US0999, US0991
> **Persona:** Maya Okafor

## User Story

**As** a founder-engineer paying for the tokens a sprint burns
**I want** the report of record to show the prices the run was costed at and the money each model's tokens cost
**So that** I read the sprint's cost in money on the signed page, priced from my own rates, instead of re-pricing its tokens at whatever the rate is today

## Acceptance Criteria

- **AC1:** Given `pricing.claude-opus-5-5: 15` in the project config, a run metered at 1,000,000 main-thread tokens on that model and a delegated total recorded against the same model, when `sprint close` files the report, then the run record carries a pricing snapshot, and the cost section and its Markdown twin state, beside each priced row's money, the model, the price 15, US dollars per million tokens and the snapshot's date, with 15.00 for the main thread and the delegated total priced at the same rate.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_pricing_snapshot.py::PricingSnapshotTests::test_close_freezes_prices_and_states_money
- **AC2:** Given a run whose tokens include a `claude-sonnet-4-6` main-thread session with no configured price, a `mixed` main-thread row and a delegated total that records no model, when `sprint close` files the report, then each is listed as unpriced with its token count, the money total says how many tokens it leaves unpriced, and no money figure reads 0 or an estimate for them.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_pricing_snapshot.py::PricingSnapshotTests::test_unpriced_tokens_are_named_never_zero_or_estimated
- **AC3:** Given that page signed and committed, when `pricing.claude-opus-5-5` is changed to 20 and `sprint_report check` runs in a fresh clone, then it reads VALID and the page still states 15 and 15.00.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_pricing_snapshot.py::PricingSnapshotTests::test_a_price_change_after_the_close_moves_nothing
- **AC4:** Given a signed page whose run record carries no snapshot, as every page filed before this change, and a page filed after the change, when a price is configured and `sprint_report check` runs on each, then both read VALID with their Markdown twins and only the later page carries money.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_pricing_snapshot.py::PricingSnapshotTests::test_a_page_without_a_snapshot_is_unchanged

## Notes

- Release: 6.2 (D0355 breakdown G2, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: pricing at render time from telemetry.model_price without recording a snapshot, a snapshot the cost section never reads, or money printed with no price, currency or date beside it
- AC2 must fail on: calling telemetry.model_price unchanged, which prices the sonnet session at its 6.00 estimate default (telemetry.py:496), or `price or 0`, which prices unpriced tokens at nothing and states the total as complete
- AC3 must fail on: the cost section re-reading today's config at re-derivation instead of the record's snapshot
- AC4 must fail on: pricing a snapshot-less record from live config, or a template that prints an empty money line for a page with no snapshot
- Serves Maya's scenario, 'priced from her own rates' (maya-okafor-founder-engineer.md:62-63); CR0610's third criterion asks for the snapshot (model, price, currency, date) in the cost section, so the page shows it, not only the record.
- Configured rates only, per the panel's product answer: a model with no `pricing.<model-id>` or `pricing.<family>` key reads unpriced on the report of record even where telemetry has an estimate default. Needs a price lookup that reports the config key it matched and returns nothing for the estimate fallback; `show` keeps model_price as it is.
- Freeze the snapshot in `_file_the_report` beside freeze_ci_runs (sprint.py:9459). A re-close keeps the first close's snapshot, as it keeps the first close's cost window through REPORT_WINDOW_END (sprint.py:9474; panel engineering answer), so a config edit between close and re-close moves nothing.
- The cost section gains delegated rows per recorded model; a run whose delegated entries carry no model shows no such rows, so earlier pages re-derive unchanged. Money figures are in the digest; the money block sits in its own when-block in both templates, so an earlier twin renders identically under the new template.
- Document `pricing.<model>` in reference-config.md, where Maya looks for settings; today it is only in reference-scripts-domain.md:126.
- Currency is US dollars per million tokens, the unit model_price already returns; no conversion.
- Sized at 5 with delegated-model capture as its own 2-point story before it, per the panel.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G2 after the refine panel's review |
