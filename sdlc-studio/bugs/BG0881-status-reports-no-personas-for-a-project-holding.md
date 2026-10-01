# BG0881: status reports no personas for a project holding only the personas/index.md registry

> **Status:** Superseded
> **Superseded by:** BG0824 (35fcdee7 and 56e76452): status and review_prep count the personas registry
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/status.py, .claude/skills/sdlc-studio/scripts/tests/test_status.py
> **Evidence:** lane-2 build of BG0824 (RUN-01M3VF2J)
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-01T17:04:56Z

## Summary

status.py:375 decides requirements.personas by checking for sdlc-studio/personas.md only. Guided onboarding now seeds the registry sdlc-studio/personas/index.md (BG0824), so a fresh project reads as having no personas.

## Steps to Reproduce

1. init.py run, walk guided onboarding to the personas stage (seeds personas/index.md). 2. status.py -> requirements.personas reads missing.

## Proposed Fix

Count the registry (personas/index.md or any personas/*.md card) as personas present.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: status.py:375 decides requirements.personas by checking for sdlc-studio/personas.md only.
- [ ] **AC2** The proposed fix lands, pinned by a test: Count the registry (personas/index.md or any personas/*.md card) as personas present.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Filed |
