# CR-0306: Candidates dropped by the verification cap vanish into the workflow journal - persist the overflow as a carry-over worklist a scoped follow-up can verify

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/reference-audit.md, .claude/skills/sdlc-studio/templates/automation/audit-finder.md
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5; agent; audit-process-retro wf_9903a6e6-53a

## Summary

reference-audit.md's budget section rightly mandates logging what a cap dropped, but a log line is not a work item: the dropped candidates themselves live only in the harness's session-local journal and are gone once the session is. The 2026-07-16 run verified the top 80 of 122 candidates by finder-assigned severity (itself unvalidated at drop time) and the 42 overflow candidates - each a grounded file+claim+evidence record - have no durable home and no route into a follow-up. The audit should treat overflow as carried work, mirroring the two-backlog discipline: findings are cheap to re-derive badly and expensive to re-derive well.

## Impact

On any audit that finds more candidates than the verify budget, the tail is silently unverifiable afterwards: the 2026-07-16 run dropped 42 of 122 candidates unverified, recoverable only by spelunking a session-local workflow journal.

## Acceptance Criteria

- [ ] reference-audit.md budget section requires writing capped-out candidates (full JSON: title, file, claim, evidence, lens, severity) to a durable carry-over file (e.g. .local/audit-carryover-<date>.json), not just logging the count
- [ ] The audit close-out report names the carry-over file and the one-line scoped command that verifies just those candidates (skipping find)
- [ ] A follow-up run can ingest the carry-over file as its candidate pool directly, running refute panels without re-finding

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 | Raised |
