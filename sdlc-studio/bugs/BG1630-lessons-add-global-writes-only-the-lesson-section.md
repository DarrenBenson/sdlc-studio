# BG1630: lessons add --global writes only the Lesson section and ships the template's other sections as placeholders

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/tests/test_lessons.py, .claude/skills/sdlc-studio/lessons/LL0056-every-check-must-earn-its-place-a-constraint-added-without-retiring-one-is-how-a-process-ratchets-shut.md, changelog.d/BG1630.md
> **Evidence:** LL0056's file; rehearsal of LL0057, 2026-11-19
> **Created:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T20:46:39Z

## Summary

`lessons.py add --global` takes only a title and a body (flags or --fields-file) and writes the body into the Lesson section of templates' LL shape, leaving Why / what it cost, How to apply, Generalises to, Guard and the whole operational block (Incident, Runbook, Decay) as `{{...}}` placeholders in a lesson that ships with the skill. LL0056 shipped that way: its file reads `**Lesson.** **Lesson.**` and carries the placeholder sections after its real text, because its author put the whole lesson in the body. A rehearsal on 2026-11-19 reproduced it for LL0057.

## Steps to Reproduce

In a git work tree holding a copy of lessons/ with its registry committed, run `lessons.py add --global --fields-file f.json --lessons-dir <copy>/lessons` with {"title": "t", "body": "b"}: the new LL file carries every section after Lesson as a placeholder.

## Proposed Fix

Accept why, how, generalises and guard fields in the fields file and write them; drop the operational block and the Guard line unless given; refuse a skill-tier write that would leave a `{{` placeholder. Repair LL0056.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `lessons.py add --global` takes only a title and a body (flags or --fields-file) and writes the body into the Lesson section of templates' LL shape, leaving...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: In a git work tree holding a copy of lessons/ with its registry committed, run `lessons.py add --global --fields-file f.json --lessons-dir <copy>/lessons` with...
- [ ] **AC3** The proposed fix lands, pinned by a test: Accept why, how, generalises and guard fields in the fields file and write them; drop the operational block and the Guard line unless given; refuse a...

## Resolution

Won't Fix under D0613: the operator approved the product seat's second proposal (D0562) because a user can meet it, but it is rare and harmless and has a workaround, so fixing it costs more than it returns. Only the maintainer promoting a lesson meets it; workaround is to fill the sections by hand.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
| 2026-11-24 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0613: the operator approved the product seat's second list (D0562); reason in Resolution |
