# RFC-0035: The sprint report: what a sprint delivered, what it cost, and whether the model choice was right

> **Status:** Accepted
> **Decomposed-into:** EP0048
> **Affects:** .claude/skills/sdlc-studio/scripts/telemetry.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/route.py
> **Date:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

A standard end-of-sprint report composing what the tooling now measures: value delivered, estimation accuracy, lessons learned, tickets raised, and models used. Most of it is COMPOSITION, not new measurement - the retro holds Delivered and the disposition table, retro.py accuracy holds the honest estimate-vs-actual since BG0133, the lessons store holds the lessons, and telemetry already carries model, tokens, wall-clock, iterations and critic verdict per unit. There is no report command today.

The design question is COST, and it splits in two.

ACTUAL SPEND is measurable: tokens x model price, summed. Real, auditable, the kind of number a CAB can act on.

SAVINGS is a COUNTERFACTUAL. "x stories on Haiku instead of Opus saved y" asks what a model that never ran would have cost. Nobody measured it. It is a model, not a measurement, and this project has just spent two sprints learning what happens when the two are confused: the token estimator quoted a reassuring 1.09x while actually running at 0.55x, because the figure was re-derived from its own assumptions (BG0133, LL0026). A money-saved headline is that same failure wearing a finance hat, and more dangerous, because nobody audits a number that flatters them.

The honest falsifier is REWORK, and it makes true cost computable with NO counterfactual:

  true cost of a unit = sum over EVERY attempt of (tokens x price of the model that attempt used)

A cheap model rejected twice and escalated is not cheap: Haiku + Haiku + Opus can exceed routing to Opus first. That is measurable, and it is exactly the out-of-sample validation BG0139 says the router must pass before its tiers are trusted.

THE BLOCKER: telemetry writes ONE record per unit, with `iterations` as a bare count. It does not record model and tokens PER ATTEMPT, so an escalation collapses into one record naming one model. The most valuable column in the report is the one the current data model cannot express.

CONFIGURABILITY (operator request): the report must be switchable off for token-conscious projects. The switch controls RENDERING, never RECORDING. A report not generated can be generated later; a measurement not taken is gone forever, and turning telemetry off would make the estimator unfalsifiable again for precisely the reason BG0133 was raised. Note also that a report composed deterministically by a script costs almost no tokens - only an agent writing narrative prose does - so the honest default is to make it mechanical, which makes the switch cheap to leave on.

## Design Options

- **Per-attempt telemetry (RECOMMENDED). Telemetry records each ATTEMPT with its own model and token count. An escalation shows its true summed cost. Cost: a schema change and a migration for 361 existing per-unit records. Buys: the rework column, a falsifiable router, and cost-per-outcome for the benchmark.**
- **Per-unit telemetry with a model list. Keep one record per unit but carry every model that touched it. Cheaper, no migration. But the per-attempt token split is lost, so a bad model choice still cannot be priced - it only becomes visible, not quantifiable.**
- **Report actual spend only, and never model a counterfactual. Simplest and fully honest, but it cannot answer the operator question that prompted this (was the cheap model a false economy?), because that question is comparative by nature.**

## Recommendation

Per-attempt telemetry, and report ACTUAL SPEND as a measurement with rework priced into it. Show an avoided-cost figure only if it is labelled an estimate against a named baseline, never summed into a headline, and never printed next to a measured number without saying which is which. Build the report as a deterministic script so it costs no model tokens, and gate its rendering behind config (following the lessons.loop pattern) while telemetry keeps recording regardless.

## Open Decisions

| # | Decision | Status |
| --- | --- | --- |
| D1 | Act on this finding or keep status quo | Open |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Filed |
