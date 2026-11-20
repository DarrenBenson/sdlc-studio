# BG1670: persona_review.remedy names a brief command for a card held by a blocking rule, whose PASS persona_review.py record then refuses

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/persona_review.py, .claude/skills/sdlc-studio/scripts/tests/test_persona_review_block.py
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T15:06:52Z

## Summary

Run twenty's repair builder (RUN-01M7VNR0) found that for a card held by a blocking rule of the persona standard (not by a FAIL row), `persona_review.remedy` still names '`persona_review.py` brief --card <card> --seat <seat>' as the way out, but a PASS recorded from that review is refused while the blocking rule still fails, so the named command cannot clear the hold. The remedy for a blocking-rule hold is to fix the card, which the refusal's own line already says. Pre-existing from US1055.

## Steps to Reproduce

In a fixture, give a seat card a demographic token (a blocking rule), run `persona_review.py` check to read its remedy, then run the named brief and record a PASS: the record is refused while the rule fails.

## Proposed Fix

Have remedy name the card fix (the rule and its line) for a blocking-rule hold, and the brief command only for a FAIL hold; pin both.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Run twenty's repair builder (RUN-01M7VNR0) found that for a card held by a blocking rule of the persona standard (not by a FAIL row), `persona_review.remedy`...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: In a fixture, give a seat card a demographic token (a blocking rule), run `persona_review.py` check to read its remedy, then run the named brief and record a...
- [ ] **AC3** The proposed fix lands, pinned by a test: Have remedy name the card fix (the rule and its line) for a blocking-rule hold, and the brief command only for a FAIL hold; pin both.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
