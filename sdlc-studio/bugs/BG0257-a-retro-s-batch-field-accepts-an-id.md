# BG0257: A retro's Batch field accepts an id RANGE, silently reads 4 units instead of 33, and publishes a velocity row an order of magnitude wrong

> **Status:** Fixed
> **Verification depth:** functional - node-addressed tests green, mutation-proven by the delivering worktree agent; merged and re-verified on the composed tree
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py,.claude/skills/sdlc-studio/templates/reviews/retro.md,.claude/skills/sdlc-studio/scripts/tests/test_retro.py
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Hit live at RUN-01KY3MFX's close. The retro's Batch line was written as 'BG0247-BG0256, US0288-US0310 (32 units, 100 points)' - a range, which reads naturally and is what a human would write. The parser expands no ranges, so it matched only the four bare ids it could see and `accuracy --write` published 'Sprint tokens/point: 2,597,269 (5,194,538 tokens over 2 delivered points)'. That number is wrong by roughly three orders of magnitude and it went into VELOCITY.md, which the header describes as the source the planner re-measures its rate from. It was caught by reading the output, not by any check. The failure is silent and fails open in the worst direction for this project: a plausible-looking number in the one file whose entire purpose is to be trusted later. Note the shape - the field is prose that the tooling parses, so a writer gets no feedback that half their batch was ignored, and the count is not cross-checked against anything. The retro's own header states the unit count separately (it said 32, and the batch names 33), so the data to detect this was present and unused.

## Steps to Reproduce

1. Write a retro whose Batch field expresses ids as a range, for example 'BG0247-BG0256, US0288-US0310'. 2. Run retro.py accuracy --id <retro> --tokens N --write. Observed: the accuracy table lists only the bare ids the parser recognised, the points denominator is the sum of those alone, and a tokens-per-point figure computed from the full token numerator over that partial denominator is written to VELOCITY.md. Expected: either the range is expanded, or the mismatch between the parsed unit count and the retro's declared unit count is refused.

## Proposed Fix

Cross-check the parsed batch against the retro's own declared unit count and REFUSE when they disagree, rather than expanding ranges - expansion invites a second ambiguity about what a range across two id families means. The count is already written in the header, so the check costs nothing. Whatever is chosen, a partially-parsed batch must never reach `record_velocity`: a wrong row in the file the planner re-measures from is worse than no row.

## Acceptance Criteria

### AC1: a batch the parser could not read in full never reaches the velocity record

The fix is complete when all of the following hold, and each is pinned by a test that fails
against the code as it stands today:

- The parsed unit count is cross-checked against the count the retro already declares in its
  own `Delivered: N / M` header, and a disagreement REFUSES the accuracy run, naming both
  counts and the ids that did parse. The writer today reports on whatever ids it recognised
  and says nothing about the rest.
- The refusal happens BEFORE `record_velocity` writes: VELOCITY.md gains no row for that
  retro, and any row already there is left exactly as it was. A partial denominator paired
  with a whole-sprint numerator must never reach the file the planner re-measures its rate
  from - that is the whole failure, and CR0391's fixed-term fit will read those same columns.
- A retro whose Batch line parses completely is unaffected: it records its row as before, so
  the check is a cross-check and not a new obstacle to a correct close.
- The refusal is actionable: it says what to do (name the units individually) rather than
  reporting a count mismatch and stopping.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::TheBatchIsCrossCheckedAgainstItsDeclaredCount::test_a_range_batch_is_refused_naming_the_parsed_and_declared_counts

### AC2: the refusal writes nothing and disturbs nothing already written

- **Given** a retro whose Batch line parses only part of its declared units, and a VELOCITY.md
  already carrying rows
- **When** the accuracy run is refused
- **Then** no row is added for that retro and every existing row is byte-identical, because a
  partial denominator paired with a whole-sprint numerator must never reach the file the
  planner re-measures its rate from
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::TheBatchIsCrossCheckedAgainstItsDeclaredCount::test_a_refused_batch_writes_no_velocity_row_and_disturbs_no_existing_one

### AC3: a batch that parses completely still records, so the check is a cross-check and not a new obstacle

- **Given** a retro whose Batch line names every unit individually and parses in full
- **When** the accuracy run executes
- **Then** its row is recorded as before
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::TheBatchIsCrossCheckedAgainstItsDeclaredCount::test_a_fully_parsed_batch_still_records_its_row

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Filed |
