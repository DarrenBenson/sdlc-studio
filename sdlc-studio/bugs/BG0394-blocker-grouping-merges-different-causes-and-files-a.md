# BG0394: Blocker grouping merges different causes and files a CR naming one unit's remedy for many

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** adversarial review of RUN-01KYMJEM, reproduced by the reviewer
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1

## Summary

The group key is (stage, id-stripped remedy) but `cause` and the filed CR's summary come from `group['blockers'][0]`. Two blockers with different details and the same remedy merge, and the second detail never reaches the artefact - while the close prints that they 'are listed inside the artefact that covers them'. Separately, the CR's acceptance criterion names one unit's remedy while covering several, so it closes when one is done.

## Steps to Reproduce

`group_blockers([`{stage:gate,detail:'markdown lane red',remedy:'run the gate'},{stage:gate,detail:'neutrality guard red',remedy:'run the gate'}]) -> one group, cause 'markdown lane red' only.

## Proposed Fix

Key on the detail as well, list every member detail in the filed artefact, and template the criterion over group['units'].

## Acceptance Criteria

- [ ] Two blockers with different details are not merged into one artefact.
- [ ] A grouped artefact lists every blocker it covers, and its criterion covers all of them.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 | Filed |
