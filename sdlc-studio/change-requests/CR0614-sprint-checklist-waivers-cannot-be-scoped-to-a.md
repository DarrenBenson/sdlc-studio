# CR-0614: Sprint-checklist waivers cannot be scoped to a unit or expire, so a defect in one checklist row has only a permanent project-wide exit

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/decisions.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_decisions.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Date:** 2026-10-07
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-07T12:36:47Z

## Summary

`decisions.py waive --subject rule:sprint-checklist:<item>` accepts only a bare item (`sprint_report.scope_tail_error` refuses `closing-review:BG0460` as 'not a checklist item'), although `--subject`'s help says 'an optional `:<unit>`/`:<id>-<id>` tail scopes it' - true only for conformance rules. Waivers also have no expiry or revoke: the 'expired' kind marks a waiver whose window had already closed, not one that lapses. So when one row is wrong for one unit (a consuming project's RUN-01M4APNQ, BG0962), the operator's choices are a waiver that switches the row off for every future sprint, or leaving the run open. Neither is proportionate.

## Impact

Operators facing a checker defect either disable a correctness row permanently or cannot close an honestly finished run.

## Acceptance Criteria

- [ ] A sprint-checklist waiver can name a unit (or run) it covers, and covers nothing else
- [ ] A waiver can carry an expiry (a run id or date) after which the row is enforced again
- [ ] The --subject help states exactly which rules accept a scope tail

## Triage

- Verified at 8b844a80: `scope_tail_error('rule:sprint-checklist:closing-review:BG0460')` refuses the scoped subject as 'not a checklist item'. BG0962 (fixed on the fast-track, D0348) removes the case that raised this, so it is no longer urgent; the proportionate exit it asks for still stands for the next checker defect.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | Claude Opus 5.5 | Raised |
| 2026-10-07 | Claude Opus 5.5 (triage) | Triaged: reproduced at 8b844a80, not a regression, consuming-project name generalised for the neutrality lane |
