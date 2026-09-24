# BG0755: artifact.py batch ignores a story's role, capability and benefit, and its default template leaves a page of placeholders

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py
> **Evidence:** Sprint 3 planning, 2026-09-24: US0890-US0926 were minted with placeholders and rewritten to the lean shape by hand from the authors' specs.
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`artifact.py batch --type story` with items carrying `role`, `capability` and `benefit` left the User Story block's persona, capability and benefit placeholders unfilled for all 37 Sprint 3 stories, and its default `full` template added about 100 lines of placeholder sections (Context, Inherited Constraints, Scope, Technical Notes, Edge Cases, Test Scenarios, Dependencies, Estimation, Rollback Envelope, Open Questions). The single-item `new` path fills the user story. An unfilled Open Questions placeholder can hold a transition.

## Steps to Reproduce

1. Write a spec item with title, epic, role, capability, benefit, acs, verify. 2. `artifact.py batch --type story --spec <file>`. 3. The User Story block keeps its placeholders.

## Proposed Fix

Fill role/capability/benefit in the batch path exactly as `new` does, and make the lean story shape the batch default (the full template stays opt-in).

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `artifact.py batch --type story` with items carrying `role`, `capability` and `benefit` left the User Story block's persona, capability and benefit placeholders unfilled for all 37 Sprint 3...
- [ ] **AC2** The proposed fix lands, pinned by a test: Fill role/capability/benefit in the batch path exactly as `new` does, and make the lean story shape the batch default (the full template stays opt-in).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Filed |
