# BG0713: the per-unit coverage gate charges a unit for its batch siblings' added lines in a shared file

> **Status:** Won't Fix
> **Duplicate of:** BG0706 - the same defect, recorded from RUN-01M2JA6J on 2026-09-15. BG0706 also carries the mechanism this one missed: attribution is by git blame against a commit whose subject or Refs names the unit, so UNCOMMITTED lines cannot be attributed and are charged to every unit sharing the file.
> **Severity:** High
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Created:** 2026-09-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

The per-unit coverage gate charges every unit for every added line in a file it shares with a sibling, so a batch whose units edit one file cannot clear it without ruling thousands of lines that other units' tests do execute.

## Steps to Reproduce

`verify_ac.coverage_report` asks 'which of the unit's own added lines did its own verifiers execute?' - where 'its own added lines' is every line added in the unit's declared `Affects` files since the run's base ref, whoever added them. When several units of one batch declare the same file, each is charged with all of their additions.

Measured on RUN-01M2SPNS, whose US0832, US0833 and US0834 all declare `scripts/sprint.py` and `tests/test_sprint.py`:

```text
US0832: sprint.py 191 added statements, 102 executed, 89 uncovered
        test_sprint.py 449 added, 106 executed, 343 uncovered
        uncovered total 432
```

The uncovered sets are dominated by the siblings' lines. sprint.py 9761-9789 is US0834's `_report_holds`; `test_sprint.py` 19955-20120 is US0833's `TheSealIsATransactionTests`. Every one of those lines IS executed by a test in this run - by another unit's verifiers, in the same suite, in the same commit.

Under `review.line_coverage: block` this refuses the Done transition for all three units. The documented remedies do not fit: `coverage rule` asks for a reason why NO test can execute the line, which is false here, and takes one line per invocation; `--force` waives the whole gate rather than the misattribution.

The gate is right that an added line no test reaches is a defect. What it cannot currently express is that the line is reached by the RUN's tests rather than by this unit's. A run-scope reading - the union of the batch's verifiers against the batch's added lines - would answer the same question honestly, and a unit whose line no test in the whole run executes would still be refused.

NOT repaired in the run it refuses, under the standing rule: record the wall, leave the run open.

## Proposed Fix

Give the measurement a RUN SCOPE: measure the batch's added lines against the union of the batch's verifiers, so the question becomes 'did any test in this run execute this added line?'. A line no test in the whole run reaches is still refused, which is what the gate exists for; a line another unit's test executes stops being charged to a unit that did not write it. Keep the per-unit reading available for a batch whose units are file-disjoint, and name which reading was taken in the refusal, so a reader can tell a genuinely unreached line from a misattributed one.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: The per-unit coverage gate charges every unit for every added line in a file it shares with a sibling, so a batch whose units edit one file cannot clear it...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: `verify_ac.coverage_report` asks 'which of the unit's own added lines did its own verifiers execute?' - where 'its own added lines' is every line added in the...
- [ ] **AC3** The proposed fix lands, pinned by a test: Give the measurement a RUN SCOPE: measure the batch's added lines against the union of the batch's verifiers, so the question becomes 'did any test in this run...

## Impact

Blocks the Done transition for every unit of a batch that shares a file, and the documented remedies do not fit: `coverage rule` asks why NO test can execute the line, which is false here, and `--force` waives the whole gate rather than the misattribution.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-18 | sdlc-studio | Filed |
