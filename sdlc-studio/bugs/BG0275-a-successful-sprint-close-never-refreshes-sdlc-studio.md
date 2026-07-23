# BG0275: a successful sprint close never refreshes sdlc-studio/reviews/LATEST.md, so the review anchor AGENTS.md orders every agent to re-anchor on still states the previous run's owed sign-off after that sign-off landed

> **Status:** Open
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py,sdlc-studio/reviews/LATEST.md
> **Severity:** Medium
> **Points:** 3

## Summary

{{symptom}}

## Steps to Reproduce

{{steps}}

## Proposed Fix

{{fix}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |

## Detail

Hit at the very first step of the Sprint 2 session, during the re-anchor AGENTS.md mandates
("At session start, and after any context reset or compaction: re-read
`sdlc-studio/reviews/LATEST.md` ... before acting"). RUN-01KY7W1F had closed goal-reached with
the operator sign-off applied and all 19 units Done, yet the anchor still read "**Sign-off is
owed and is the operator's**". An agent obeying the instruction is told to chase a sign-off that
already landed.

The cause is a one-sided implementation: `sprint.py` writes the anchor ONLY in `_file_and_close`
(the bounded exit for a blocked close, sprint.py:4019). The normal success path - goal-verdict,
retro, gate, handoff, reconcile, and `--apply-signoff` - never touches it. So the anchor is
refreshed exactly when the run went badly, and left stale exactly when it went well.

This is the class of defect the rest of the repo builds tooling to prevent: a derived record that
states something false, in the one file the doctrine points every new context at.

## Acceptance Criteria

- [ ] AC1: a successful close refreshes the review anchor rather than leaving the previous run's state
- **Given** a run closed goal-reached with sign-off applied and every unit terminal
- **When** the close chain completes
- **Then** `sdlc-studio/reviews/LATEST.md` states THIS run's outcome and no longer claims the prior run's sign-off is owed
- **Verify:** manual

- [ ] AC2: the anchor names what is owed, or states plainly that nothing is
- **Given** a close where sign-off is genuinely still owed
- **Then** the anchor says so, and where it is not owed it says that instead - the reader never has to diff the anchor against the run state to learn which is true
- **Verify:** manual
| 2026-07-24 | sdlc-studio | Fixed and mutation-proven |
