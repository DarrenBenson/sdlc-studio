# BG0284: superseding a verdict cannot restore independence, so the mis-attributed-reviewer case that motivated it still strands a unit: the tool cannot tell a mis-filing from an author retiring an inconvenient verdict, and needs a principal-authorised correction path

> **Status:** Open
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py,.claude/skills/sdlc-studio/reference-review.md
> **Severity:** High
> **Points:** 5

## Summary

{{symptom}}

## Steps to Reproduce

{{steps}}

## Proposed Fix

{{fix}}

## Detail

The closing review of RUN-01KY8M6Q reproduced a COMPLETE BYPASS of the two-role gate through the
supersession path US0374/US0375 added, and the emergency fix closes the bypass at the cost of
leaving the original problem unsolved. Both halves are stated here.

**The bypass, measured end to end.** `record_verdict(US0001, reject, reviewer=qa-seat,
author=builder)`; `record_signoff(principal=qa-seat, author=builder)` is REFUSED, correctly, as an
authoring-session subagent. Then `record_supersession(US0001, ..., authorised_by="qa-seat")` is
ACCEPTED - the only mechanical guard is that the authoriser differs from the row's own author,
which any other string satisfies. The reviewer then dropped out of `_session_reviewer_ids`, and
the identical sign-off was ACCEPTED. An author, acting alone, deleted the verdict blocking them
and cleared the independence gate.

**The fix, and what it costs.** `_session_reviewer_ids` now counts superseded rows: superseding
retires a VERDICT, it cannot un-make the fact that someone reviewed the unit. The gate holds.

**What is now unsolved.** US0375 existed for a real incident: an APPROVE row wrongly naming the
operator as REVIEWER meant the operator - the legitimate reviewer of record - read as an
authoring-session reviewer, and the unit was stranded permanently. Superseding no longer clears
that, so the stranding is back.

**Why it cannot be fixed by relaxing the guard.** The two cases are mechanically identical:

- a MIS-ATTRIBUTION - the named reviewer never reviewed, so removing them is a correction of a
  false record;
- an AUTHOR retiring a TRUE verdict that blocks them.
Both are "a row is superseded and its reviewer should stop counting". Nothing in the record
distinguishes them, so the tool must not guess, and the safe default is to refuse the powerful
reading.

**The shape of a real fix.** Superseding must be an act of the PRINCIPAL (the reviewer of record,
in a separate trust boundary), not of any party the author controls - the same rule the sign-off
itself already enforces via `--delegate` / `--boundary`. In the motivating incident the operator
authorised it; in the bypass, an authoring-session subagent did. That distinction is recordable,
and is what the guard should test.

## Acceptance Criteria

### AC1: superseding requires an authoriser independent of the author, on the sign-off's own rule

- **Given** a supersession whose authoriser is an authoring-session reviewer on that unit, or the row's author
- **When** it is recorded
- **Then** it is refused, naming the independence rule - the correction path is held to the same trust boundary as the sign-off it can affect
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::PrincipalAuthorisedSupersessionTests::test_an_authoring_session_authoriser_is_refused

### AC2: a principal-authorised supersession does restore independence

- **Given** a supersession authorised by a principal in a separate trust boundary, with that boundary recorded
- **Then** the superseded row stops counting toward independence, so a mis-filed row no longer strands the unit
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::PrincipalAuthorisedSupersessionTests::test_a_principal_authorised_supersession_clears_the_strand

### AC3: the bypass stays closed

- **Given** the author's own path
- **Then** no sequence of supersessions available to the author alone clears the independence gate on a unit they authored
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::PrincipalAuthorisedSupersessionTests::test_no_author_only_sequence_clears_the_gate

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
