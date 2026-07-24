# CR-0372: an append-only review log has no correction path, so one mis-entry can strand a unit permanently

> **Status:** Complete
> **Decomposed-into:** EP0133
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/reference-review.md
> **Date:** 2026-07-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The critic verdict log is append-only and latest-row-wins, which is right for an audit trail. But there is no way to correct a row that records an event which did not happen, and one class of mis-entry is unrecoverable: recording the operator as the critic REVIEWER when they were the reviewer of record. The sign-off gate then refuses that same person as principal, because it correctly requires the principal to differ from any recorded reviewer on the unit - so the unit can never be signed off, by anyone, and can never reach a conformant Done. Hit live: a US0276 row naming the operator as reviewer was written in error and blocked the legitimate sign-off until the row was removed by hand with the operator's authorisation and an erratum recorded in the file header. Hand-editing an append-only log is exactly what it exists to prevent, so the escape hatch should be a command with a recorded reason, not a text editor.

## Impact

Any project where a verdict is mis-recorded, which is easy to do because reviewer and principal are different roles that both look like a name in a flag. The unit is stranded with no in-tool remedy, and the only route out is editing the audit log by hand - which destroys the property that makes the log worth having.

## Acceptance Criteria

- [ ] Given a verdict row that records an event which did not happen, when the operator issues a correction, then the row is superseded through a command rather than a hand edit, and the correction states what was wrong and who authorised it
- [ ] Given a correction has been issued, when the sign-off gate evaluates the unit, then the superseded row no longer disqualifies a principal, while remaining visible in the record
- [ ] Given no correction has been issued, when anyone attempts one, then authorship alone is not sufficient - the author who wrote the wrong row cannot quietly erase it

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Raised |
