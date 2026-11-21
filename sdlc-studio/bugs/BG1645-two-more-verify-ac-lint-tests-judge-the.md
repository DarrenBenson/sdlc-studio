# BG1645: Two more verify_ac lint tests judge the live help/ directory, so a non-markdown file there turns them red

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T01:30:47Z

## Summary

BG1644 moved MarkdownEvidenceLintTests' review-directory escapes onto a fixture root after committed JSON records under sdlc-studio/reviews/ turned the push gate red. Its builder found two more tests in the same class that still judge the live repository: `test_the_file_verb_is_refused_over_markdown_and_over_a_prose_directory` and `test_a_missing_operand_proves_nothing` in .claude/skills/sdlc-studio/scripts/tests/`test_verify_ac.py` read the real help/ directory, so the first non-markdown file committed there flips them for a reason unrelated to the lint.

## Steps to Reproduce

In a throwaway copy, add help/x.json and run pytest .claude/skills/sdlc-studio/scripts/tests/`test_verify_ac.py` -k '`prose_directory` or `missing_operand`': the prose-directory refusal is no longer returned.

## Proposed Fix

Judge both tests against a temporary root holding a markdown-only help/, as MarkdownEvidenceLintTests now does.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: BG1644 moved MarkdownEvidenceLintTests' review-directory escapes onto a fixture root after committed JSON records under sdlc-studio/reviews/ turned the push...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: In a throwaway copy, add help/x.json and run pytest .claude/skills/sdlc-studio/scripts/tests/`test_verify_ac.py` -k '`prose_directory` or `missing_operand`'...
- [ ] **AC3** The proposed fix lands, pinned by a test: Judge both tests against a temporary root holding a markdown-only help/, as MarkdownEvidenceLintTests now does.

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because only a test or pin is missing on behaviour that is right on every path a user reaches. Two lint tests read the live help/ directory, so a stray non-markdown file there turns them red. Test fixture gap, with no shipped effect. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
