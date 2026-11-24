# BG1726: readiness detector-owed reports a project lens as PRD (None) and would declare a bare pack directory as the owed unit's Affects

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/readiness.py, .claude/skills/sdlc-studio/scripts/tests/test_readiness.py
> **Evidence:** readiness.py:578-589 (`_lens_signature` iterates `profile_names` minus `REFERENCE_PROFILES)`; BG1567 qa verdict sdlc-studio/reviews/verdicts/BG1567/874ccadb1977-9e3a5e8f.txt reproduces 'detector-owed: PRD (None)'
> **Created:** 2026-11-23
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-23T10:26:45Z

## Summary

`readiness._lens_signature` skips `REFERENCE_PROFILES`, so a lens from the project pack (filed with `file_finding.py` file --lens PRD --audit-run, which BG1567 now allows) has no signature. Once two registered audit runs file under it, readiness.py detector-owed prints 'detector-owed: PRD (None)' with no profile, and detector-owed --file declares the bare pack directory as the owed unit's Affects instead of the lens's detector path.

## Steps to Reproduce

1. In a throwaway project, register two audit runs with `audit_cost.py` record (RUN-AUD-1, RUN-AUD-2). 2. File BG0001 with `file_finding.py` file --lens PRD --audit-run RUN-AUD-1 and BG0002 with --lens PRD --audit-run RUN-AUD-2. 3. Run readiness.py detector-owed: it prints 'detector-owed: PRD (None)'.

## Proposed Fix

Have `_lens_signature` resolve the project profile's lenses too (or every profile in `profile_names)`, so a project lens carries its profile and detector path; pin the PRD fixture's line and the --file Affects in `test_readiness.py.`

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `readiness._lens_signature` skips `REFERENCE_PROFILES`, so a lens from the project pack (filed with `file_finding.py` file --lens PRD --audit-run, which BG1567...
- [ ] **AC2** The proposed fix lands, pinned by a test: Have `_lens_signature` resolve the project profile's lenses too (or every profile in `profile_names)`, so a project lens carries its profile and detector path...

## Resolution

Won't Fix under D0613: the operator approved the product seat's second proposal (D0562) because a user can meet it, but it is rare and harmless and has a workaround, so fixing it costs more than it returns. Detector-owed prints PRD (None) for a project lens; cosmetic.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-23 | sdlc-studio | Filed |
| 2026-11-24 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0613: the operator approved the product seat's second list (D0562); reason in Resolution |
