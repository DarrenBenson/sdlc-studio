# EP0304: A Copilot run is priced on the basis its plan is billed by: tokens in AI credits by default, premium requests only on request billing

> **Status:** Draft
> **Derived Point Total:** 5
> **Parent:** CR0685
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0685. Delivers the work CR0685 requested.

## Story Breakdown

- [ ] [US1144: A Copilot run on token billing is priced per token from Copilot's dated AI-credit rates and the dollar value of a credit](../stories/US1144-a-copilot-run-on-token-billing-is-priced.md)
- [ ] [US1145: A project on Copilot request billing says so in its config, and only then are its premium requests priced in dollars](../stories/US1145-a-project-on-copilot-request-billing-says-so.md)

## Acceptance Criteria (Epic Level)

- [ ] `templates/model-prices.json` carries Copilot's per-token rates in AI credits, the US-dollar value of a credit and the date they were read, for each model Copilot's token billing prices
- [ ] A Copilot reading is priced per token from those rates by default, and the premium-request price applies only when the project's config names request billing
- [ ] `reference-config.md` states which Copilot plans each basis covers and the date Copilot changed basis, and a test prices one Copilot reading under each basis to different dollar figures

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | sdlc-studio | Created via `new` (deterministic) |
