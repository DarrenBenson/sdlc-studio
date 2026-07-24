# BG0285: sprint close without --apply-signoff closes the run, and the sprint-level review that the sign-off needs cannot then be recorded against it, so the documented two-invocation close flow cannot be completed and no reopen path exists

> **Status:** Open
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py,.claude/skills/sdlc-studio/scripts/lib/run_state.py
> **Severity:** High
> **Points:** 3

## Summary

{{symptom}}

## Steps to Reproduce

{{steps}}

## Proposed Fix

{{fix}}

## Detail

Hit closing RUN-01KY8M6Q, in the documented two-invocation flow.

`sprint close --retro RETROxxxx` (no `--apply-signoff`) runs the whole chain, and step 5 -
`handoff` - CLOSES the run object. The operator is then meant to read the sign-off brief, decide,
and re-run with `--apply-signoff`. But that second invocation refuses every unit with "no critic
verdict and no sprint-level review covering it", and the review cannot be supplied:

```text
sprint-review refused: cannot record a review round against a run that already ended at
'2026-07-24T11:59:17Z' - the review would be accepted against a closed run and counted after
the fact. Record the round before the run is closed, or reopen it
```

The refusal is right on its own terms - a review recorded after a run ends IS counted after the
fact. But it names a remedy, "or reopen it", that does not exist: `run_state` has no reopen verb,
and `sprint.py` has no caller for one. The only recorded use of the word is inside this very
refusal message.

So the sequence the close documents cannot be completed once the first invocation has run, unless
the review happened to be recorded BEFORE it. That ordering is not stated anywhere the operator
meets it, and the previous sprint only worked because the review was recorded first by habit.

**Confidence: the refusal above is verbatim and reproducible; the causal chain is not yet
confirmed.** After filing, a review row covering all 28 units was found in the working tree that
appears to predate the failing pre-flight - which, if true, means the pre-flight refused while
coverage existed and the cause is something other than the ordering described here. Re-run the
close from a clean checkout and record which of the two it is BEFORE repairing.

## Impact

Any close that follows the documented order. The run is left closed with the units un-signed and
no supported route forward - the ceremony deadlocks at exactly the step that certifies the work.

## Acceptance Criteria

### AC1: the close does not foreclose the sign-off it is about to ask for

- **Given** a close run WITHOUT `--apply-signoff`, which exists to print the sign-off brief
- **When** the chain completes
- **Then** the follow-up `--apply-signoff` invocation can still record the sprint-level review the sign-off requires - either because the run is not sealed until the sign-off lands, or because the review may be recorded against a run closed in this same close
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseDoesNotForecloseSignoffTests::test_the_review_can_still_be_recorded_after_the_brief_invocation

### AC2: a refusal never names a remedy that does not exist

- **Given** the review-after-close refusal
- **Then** every remedy it names is a command that exists - a reopen verb is implemented, or the message stops offering one
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseDoesNotForecloseSignoffTests::test_every_named_remedy_is_a_real_command

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
