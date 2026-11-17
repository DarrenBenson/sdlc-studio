# CR-0722: Tool the machinery share so the sprint plan and report state it by theme and by path, as RFC0063 WS7 rules

> **Status:** In Progress
> **Decomposed-into:** EP0360
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint_machinery_share.py, sdlc-studio/rfcs/RFC0063-human-in-the-lead-the-accountable-engineering-lead.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, rfc lens, survived 2 of 3 refute votes; observed at sdlc-studio/decisions.md D0439, D0440, D0442, D0489, D0496 rows; rfcs/RFC0063-*.md Phased Plan row WS7 ('Becomes: CR (new)')
> **Date:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:27:55Z

## Summary

RFC0063 workstream WS7 and decisions D0439 and D0440 rule that the plan and the sprint report show points by area, and that a plan over one third machinery carries a recorded maintenance declaration. The RFC says WS7 becomes a new CR, but none exists, no story carries an area tag, and neither sprint.py nor `sprint_report.py` computes the share. Until it is tooled the orchestrator states the share by hand, both by theme and by path (D0442, restated by D0445). That hand step has already slipped in the plan decisions: D0489 for run fourteen gives the share by theme only, and D0496 for run fifteen gives none, although the retros for both runs do carry a share section. Where both readings are stated they differ widely, for example about 4% by theme against all 55 points by path in run ten, so the cap is judged on the self-assigned figure. The RFC schedules WS7 for 2027 Q1; this request records the unit that work is owed to, so the deferral is tracked by something.

## Impact

The operator approving a plan and a head of engineering reading a report cannot see how much of a run went on the delivery loop itself unless the orchestrator remembers to write it, and two recent plan decisions did not. The one-third cap RFC0063 set is applied on a figure the planner assigns itself, with the by-path reading that contradicts it left out.

## Acceptance Criteria

- [ ] Given a batch whose units carry an area tag and an Affects list, when sprint plan runs, then it prints the batch's points by area twice, once from the tags and once from a path map over each unit's Affects, and names any unit whose tag disagrees with the files it touches
- [ ] Given a plan whose machinery share is over one third by either reading and no maintenance declaration is recorded, when sprint plan runs, then it reports the missing declaration by name and still exits 0, as D0440 rules that nothing refuses the plan
- [ ] Given a closed run, when the sprint report is drawn, then it carries the same two shares as the plan printed
- [ ] RFC0063's Decomposed-into line and its WS7 row name this change request

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Raised |
