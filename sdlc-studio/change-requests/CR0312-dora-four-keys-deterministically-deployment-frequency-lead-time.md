# CR-0312: DORA four keys, deterministically: deployment frequency, lead time, change failure rate, MTTR from git history + the deploy ledger

> **Status:** Complete
> **Decomposed-into:** EP0054
> **Priority:** Medium
> **Type:** Feature
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/deploy.py, .claude/skills/sdlc-studio/scripts/status.py, .claude/skills/sdlc-studio/reference-deploy-readiness.md
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5; agent; agile-practice gap analysis 2026-07-16

## Summary

Gap analysis vs proven practice (research sweep 2026-07-16): DORA's four keys remain the STRONG-evidence delivery-performance measures (30k+ practitioners, 2023-2025 reports), and State of Agile 17/18 shows elite orgs steering by them over framework compliance. All four are deterministically derivable from data the skill already keeps: deployment frequency from deploy.py's record ledger (or release tags), lead time for changes from commit timestamp to its deploy record, change failure rate from the ledger's rolled-back/failed statuses over total deploys, MTTR from High-severity bug Open->Fixed dates. Pure stdlib, zero model tokens, advisory-only (a metric never gates - Goodhart caveat stated in the doc, matching the velocity discipline). Scope-guarded for the Primary: a project with no deploy ledger gets 'not applicable', never nagged - Maya pre-release sees nothing.

## Impact

Projects that deploy (Jonah's team, the operator's homelab services) get no delivery-performance read from the skill at all; the four measures the largest body of delivery research validates are absent while every input for them is already recorded.

## Acceptance Criteria

- [ ] A dora (or deploy metrics) subcommand computes the four keys from the deploy ledger, git log and bug dates, printing measurement windows and refusing metrics whose source data is absent (named, not guessed)
- [ ] A workspace with no deploy records reports not-applicable cleanly; nothing prompts a non-deploying project to adopt it
- [ ] Output is advisory and descriptive: documentation states no key feeds a gate and cites the ledger/tag/bug-date sources for each

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 | Raised |
