# BG1638: config-defaults.yaml still calls two_backlog.enforce the one gate-bearing key that ships off

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/templates/config-defaults.yaml, tools/tests/test_lean_prd_refresh.py
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T00:05:10Z

## Summary

BG1525's repair (RUN-01M7TTK3) made the PRD and reference-config.md name nine gate-bearing keys that ship off or advisory, among them provenance.enforce, `sprint.affects_check` and `sprint.fresh_session.` templates/config-defaults.yaml:119-120, which every project copies, still says `two_backlog.enforce` is 'the one gate-bearing key whose absence does NOT block'. A reader of the shipped defaults is told the opposite of the PRD. Found by BG1525's qa review and left by its repair as outside that unit's Affects.

## Steps to Reproduce

Read templates/config-defaults.yaml:119-120, then the Feature Flags introduction in sdlc-studio/prd.md: the file says one key, the PRD names nine.

## Proposed Fix

Reword the comment to say `two_backlog.enforce` is one of the gate-bearing keys that ship off, naming where the full list lives, and extend the PRD test that reads the defaults file to refuse 'the one gate-bearing key' there.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: BG1525's repair (RUN-01M7TTK3) made the PRD and reference-config.md name nine gate-bearing keys that ship off or advisory, among them provenance.enforce...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Read templates/config-defaults.yaml:119-120, then the Feature Flags introduction in sdlc-studio/prd.md: the file says one key, the PRD names nine.
- [ ] **AC3** The proposed fix lands, pinned by a test: Reword the comment to say `two_backlog.enforce` is one of the gate-bearing keys that ship off, naming where the full list lives, and extend the PRD test that...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
