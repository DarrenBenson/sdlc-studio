# BG1672: changelog.d/US1057.md says validate.py personas and seats exited with a UnicodeDecodeError traceback, though they printed a one-line Error and aborted the check

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 2
> **Affects:** changelog.d/US1057.md, .claude/skills/sdlc-studio/best-practices/persona.md, .claude/skills/sdlc-studio/reference-persona.md
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T16:46:48Z

## Summary

US1057's round-two qa review (RUN-01M7VNR0) found that the fragment overstates the old behaviour: at the base, validate.py personas and seats printed a one-line Error: and aborted the check on a card that is not valid UTF-8, not a traceback. The fix the fragment describes is right; only the description of what it replaced is wrong, and it ships in the 6.5 release notes.

## Steps to Reproduce

At 63f0e65c^, run validate.py personas in a fixture holding a card with a 0xff byte: it prints one Error: line and exits, with no traceback.

## Proposed Fix

Reword the fragment to say the check aborted with an error on such a card.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: US1057's round-two qa review (RUN-01M7VNR0) found that the fragment overstates the old behaviour: at the base, validate.py personas and seats printed a...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: At 63f0e65c^, run validate.py personas in a fixture holding a card with a 0xff byte: it prints one Error: line and exits, with no traceback.
- [ ] **AC3** The proposed fix lands, pinned by a test: Reword the fragment to say the check aborted with an error on such a card.

- Widened from US1057's round-three engineering review (RUN-01M7VNR0): two more sentences are false by execution. best-practices/persona.md:48-49 says a card that is not UTF-8 is held 'before any rule reads it. No rule can judge it', but every rule still reads its replaced text (persona_review.py check --card on a seat card holding 0xff reports seat-no-review-render, persona-evidence and persona-review-owed beside card-not-utf8). changelog.d/US1057.md:12 and reference-persona.md:390 say each owed line ends in the brief command that reviews it, but the owed line for such a card ends in 'Run next: save ... as UTF-8, then python3 ... check --card ...', the right remedy. Reword all three to what runs.

## Resolution

Won't Fix under D0613: the operator approved the product seat's second proposal (D0562) because the change it asks for is a wording preference, not a defect a user meets. A fragment over-states the old traceback.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
| 2026-11-24 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0613: the operator approved the product seat's second list (D0562); reason in Resolution |
