# BG1472: Five branches of the close's learning review and the sign's strike are right by execution but no test fails without them

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_retro_persona_learnings.py, .claude/skills/sdlc-studio/scripts/tests/test_sign_strike_learning.py, .claude/skills/sdlc-studio/reference-persona-learning.md, changelog.d/BG1472.md
> **Evidence:** QA seat's round-2 reviews of US1067 and US1068, run thirteen.
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T18:50:30Z

## Summary

Mutants survive every declared test for five branches that a probe shows work today. In retro.py, from US1067: the 'and no learning' qualifier (`role not in learned`, near line 2537); the found-after-approval keys of `adverse_keys` (near line 2515); and the approved-over-own-finding bug keys (near line 2516). In `run_state.py`, from US1068: the signature check in `signed_record` (near line 700); a run sealed with no signature, by `sprint boundary` or `--file-and-close`, would carry its learnings into the brief under the mutant, which D0488 rules must not happen. In `persona_memory.py`, also from US1068: the Struck-field check in `standing` (near line 566); under the mutant, a re-close lists a struck learning as about to go live. US1068's story note (line 44) still calls a sealed record live, against D0488.

## Steps to Reproduce

Apply each mutant the QA seat named in sdlc-studio/reviews/verdicts/US1067/af7155eeb532-c3e47dd4.txt and sdlc-studio/reviews/verdicts/US1068/50b808f82d31-827ff2f0.txt, and run `test_retro_persona_learnings.py` and `test_sign_strike_learning.py`: all pass.

## Proposed Fix

Add one test per branch through the shipped entry point, each killing its mutant: a seat with both adverse evidence and a learning; a found-after-approval round; an approved-over-own-finding bug; a run sealed STOPPED with no signature, whose learning stays held; and a struck learning re-closed. Correct the US1068 note's wording to signed, per D0488.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Mutants survive every declared test for five branches that a probe shows work today.
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Apply each mutant the QA seat named in sdlc-studio/reviews/verdicts/US1067/af7155eeb532-c3e47dd4.txt and...
- [ ] **AC3** The proposed fix lands, pinned by a test: Add one test per branch through the shipped entry point, each killing its mutant: a seat with both adverse evidence and a learning; a found-after-approval...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Filed |
