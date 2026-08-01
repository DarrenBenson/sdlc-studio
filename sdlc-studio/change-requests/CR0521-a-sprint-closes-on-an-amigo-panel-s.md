# CR-0521: a sprint closes on an amigo panel's sign-off, so the operator is informed rather than in the loop

> **Status:** Superseded
> **Priority:** High
> **Type:** Feature
> **Date:** 2026-08-01
> **Superseded by:** CR0514
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/persona_resolve.py
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; agent; v1

## Summary

Superseded by [CR0514](CR0514-the-amigo-panel-signs-off-a-sprint-to.md) before any work
started. Both describe the same change: the reviewer-of-record half of the two-role gate
satisfied by a resolved amigo panel rather than by the operator personally, so a close does
not halt waiting for a human to type.

CR0514 is the better artefact and is the one to action. It already carries everything this one
proposed, and three things this one omitted: an explicit interlock requiring brief provenance
on every adversarial verdict before a panel may sign, a termination rule gating the
review-repair loop on the growing-set detector, and an escalation path for a unit the panel
rejects twice or disagrees on.

The row is kept rather than deleted. An id that was minted and then erased leaves a gap in the
record, and a reader meeting that gap cannot tell a withdrawn duplicate from a lost file.

## Impact

None: no work is carried here. Action CR0514.

**Why this was filed at all,** recorded because it is the useful part: `file_finding.py` warned
that this was 45% similar to CR0514 and named it, and the artefact was written anyway. The
duplicate check reported correctly and was not read before the file landed - the same
read-then-ignore failure this repository's own `AGENTS.md` opens by naming.

## Acceptance Criteria

- [x] Superseded before any work began; CR0514 carries the requirement.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | Claude Opus 5 | Filed, then immediately superseded by CR0514 |
