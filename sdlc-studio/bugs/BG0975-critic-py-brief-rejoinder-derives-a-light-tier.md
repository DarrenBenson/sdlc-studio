# BG0975: critic.py brief --rejoinder derives a light tier from the risk band even when the round it answers was taken at an explicit full tier

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_rejoinder_tier.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, changelog.d/BG0975.md
> **Evidence:** Found running a consuming project on the installed skill 6.1.0, 2026-10-07; confirmed by reading the code at sdlc-studio main fb1ce886. the consuming project's US0601: round 1 recorded '--tier full --tier-explicit'; the rejoinder brief printed 'review tier: light (derived from the unit's risk band)'.
> **Created:** 2026-10-07
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-07T12:37:33Z

## Summary

A rejoinder re-reviews a REJECT's repairs and demands the named probes and mutants be re-executed. When round 1 was an operator's explicit full-tier choice (recorded with --tier-explicit), the rejoinder brief still derives the tier from the band and offers the bounded light pass, so the re-review defaults to less depth than the review it answers unless the operator remembers to override again.

## Steps to Reproduce

Record a REJECT with `--tier full --tier-explicit` on a low-band unit; run `critic.py brief --unit <id> --seat engineering --rejoinder <verdict file>` -> 'review tier: light (derived ...)'.

## Proposed Fix

Default a rejoinder's tier to the tier recorded on the verdict it answers (at least never lighter), and say so in the brief's stderr line.

## Acceptance Criteria

- [ ] **AC1** A rejoinder for a full-tier REJECT defaults to the full tier
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_rejoinder_tier.py -k rejoinder_inherits_full_tier

## Triage

- Reproduced at 8b844a80 by the code path: `cmd_brief`'s rejoinder branch takes `args.tier or tier_for(...)` and never reads the tier recorded on the verdict it answers (critic.py ~3101). Since US0641 (2026-08-05). Reconcile's US0641 advisory dismissed: US0641 built `tier_for`, not the rejoinder's tier. BG0951 (Won't Fix) was a different question.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | Claude Opus 5.5 | Filed |
| 2026-10-07 | Claude Opus 5.5 (triage) | Triaged: reproduced at 8b844a80, not a regression, consuming-project name generalised for the neutrality lane; changelog fragment added to Affects |
