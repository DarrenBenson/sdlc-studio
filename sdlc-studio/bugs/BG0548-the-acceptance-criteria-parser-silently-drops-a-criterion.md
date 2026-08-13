# BG0548: the acceptance-criteria parser silently drops a criterion whose heading is not AC<digits>, so a whole criterion and its Verify line vanish without a word

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py
> **Evidence:** RUN-01KZEF9M, 2026-08-07. Hit while splitting US0661's AC2 into a gate half and a record-shape half after a plan review; the split criterion vanished and only the count revealed it.
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

A story carrying six criteria headed AC1, AC2, AC2a, AC3, AC4 and AC5 is reported by `verify_ac.py run` as `ac=5`. The AC2a heading matches no pattern the parser accepts, so the criterion and its Verify line are dropped, and nothing in the output says a heading was skipped. AC2a is a natural thing to write when a criterion is split during grooming and the author does not want to renumber every row of the test plan beneath it. The count is the only symptom, and a count is exactly what a reader does not check against a document they just wrote. This is LL0013 in the parser rather than in an AC: what the reader does not recognise, it silently exempts.

## Steps to Reproduce

1. Add a criterion headed `### AC2a: ...` with a Verify line to any story, between AC2 and AC3. 2. Run `verify_ac.py run --id <id> --dry-run`. 3. The count reports five criteria where the document has six, and no line names the heading that was skipped.

## Proposed Fix

Report every `### AC...` heading the parser declines to accept, naming the heading and the pattern it failed. Silence is the defect - whether the suffixed form is then accepted or refused is a smaller decision than whether the author is told. A refusal is defensible; dropping it is not.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: A story carrying six criteria headed AC1, AC2, AC2a, AC3, AC4 and AC5 is reported by `verify_ac.py run` as `ac=5`.
- [ ] **AC2** The proposed fix lands, pinned by a test: Report every `### AC...` heading the parser declines to accept, naming the heading and the pattern it failed.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | {{name the production change this test must fail on}} | The behaviour described is corrected: A story carrying six criteria headed AC1, AC2, AC2a, AC3, AC4 and AC5 is reported by `verify_ac.py run` as `ac=5`. |
| AC2 | {{name the production change this test must fail on}} | The proposed fix lands, pinned by a test: Report every `### AC...` heading the parser declines to accept, naming the heading and the pattern it failed. |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Filed |
