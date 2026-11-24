# BG1638: config-defaults.yaml still calls two_backlog.enforce the one gate-bearing key that ships off

> **Status:** Won't Fix
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

## Resolution

Won't Fix under D0613: the operator approved the product seat's second proposal (D0562) because the change it asks for is a wording preference, not a defect a user meets. A config comment about a gate key.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
| 2026-11-24 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0613: the operator approved the product seat's second list (D0562); reason in Resolution |
