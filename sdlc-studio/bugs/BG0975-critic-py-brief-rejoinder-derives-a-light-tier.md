# BG0975: critic.py brief --rejoinder derives a light tier from the risk band even when the round it answers was taken at an explicit full tier

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_rejoinder_tier.py, changelog.d/BG0975.md
> **Evidence:** Found running a consuming project on the installed skill 6.1.0, 2026-10-07; confirmed by reading the code at sdlc-studio main fb1ce886. the consuming project's US0601: round 1 recorded '--tier full --tier-explicit'; the rejoinder brief printed 'review tier: light (derived from the unit's risk band)'.
> **Created:** 2026-10-07
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-07T12:37:33Z

## Summary

A rejoinder re-reviews a REJECT's repairs and demands the named probes and mutants be re-executed. When round 1 was an operator's explicit full-tier choice (recorded with --tier-explicit), the rejoinder brief still derives the tier from the band and offers the bounded light pass, so the re-review defaults to less depth than the review it answers unless the operator remembers to override again.

## Steps to Reproduce

1. On a unit whose risk band derives the light tier (`critic.tier_for` returns `light`), record a REJECT with `critic.py record --from-verdict <file> --tier full --tier-explicit`; the ledger row's tier cell reads `full (explicit)`.
2. `critic.py brief --unit <id> --seat qa --rejoinder <verdict file>`, or `--rejoinder` alone to quote the ledger: stderr prints `review tier: light (derived from the unit's risk band)`, the record command it prints carries `--tier light`, and the brief has no CLAIM INVENTORY section.

## Proposed Fix

In `cmd_brief`'s rejoinder branch, when `--tier` is not given, take the tier recorded on the REJECT being answered (the briefed seat's standing REJECT row, `seat_standing_reject`, whichever way the prior verdict is supplied) when it is deeper than the derived tier, and say so in the `review tier:` line. An explicit `--tier` still wins.

## Acceptance Criteria

- [ ] **AC1** Given a light-band unit whose standing REJECT was recorded with `--tier full --tier-explicit`, when `critic.py brief --rejoinder <verdict file>` runs without `--tier`, then stderr reads `review tier: full` naming the REJECT it answers as the source, the printed record command carries `--tier full`, and the brief carries CLAIM INVENTORY. Fails on: `review tier: light (derived from the unit's risk band)` and a light brief.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_rejoinder_tier.py::RejoinderTierTests::test_a_rejoinder_from_a_verdict_file_inherits_the_full_tier
- [ ] **AC2** Given the same unit and REJECT, when `critic.py brief --rejoinder` quotes the prior verdict from the ledger, then the tier is full as in AC1. Fails on: the derived light tier.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_rejoinder_tier.py::RejoinderTierTests::test_a_rejoinder_from_the_ledger_inherits_the_full_tier
- [ ] **AC3** Given the same REJECT, when the rejoinder is briefed with an explicit `--tier light`, then it is light and printed as chosen; and a rejoinder answering a light-tier REJECT on a light-band unit stays light. Fails on: a fix that overrides the operator's explicit tier or forces every rejoinder to full (this guard holds today).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_rejoinder_tier.py::RejoinderTierTests::test_an_explicit_tier_and_a_light_round_are_kept

## Triage

- Reproduced at cecc9dfe through `critic.py brief --rejoinder`, both from a verdict file and from the ledger, 2026-11-24: the branch is unchanged.
- Reproduced at 8b844a80 by the code path: `cmd_brief`'s rejoinder branch takes `args.tier or tier_for(...)` and never reads the tier recorded on the verdict it answers (critic.py ~3101). Since US0641 (2026-08-05). Reconcile's US0641 advisory dismissed: US0641 built `tier_for`, not the rejoinder's tier. BG0951 (Won't Fix) was a different question.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | Claude Opus 5.5 | Filed |
| 2026-10-07 | Claude Opus 5.5 (triage) | Triaged: reproduced at 8b844a80, not a regression, consuming-project name generalised for the neutrality lane; changelog fragment added to Affects |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-five: reproduced at cecc9dfe on both rejoinder sources; criteria rewritten as three executable cases (file, ledger, and a guard that an explicit tier and a light round are kept); Steps and Proposed Fix made concrete; Affects drops test_critic.py; Points stay 1 |
