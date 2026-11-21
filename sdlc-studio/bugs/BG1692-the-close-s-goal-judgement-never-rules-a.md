# BG1692: The close's goal judgement never rules a defect on the clause basis: _open_defects never reads Falsifies

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_close_goal_judgement_in_report.py, changelog.d/BG1692.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** sprint.py:9821-9832 (_open_defects) sets id, title, priority only; critic.py:1814 reads d.get('falsifies'); git log -S'falsifies' on sprint.py shows no writer. sdlc-studio/reviews/verdicts/BG0987/b4a76987a77a-f7326d56.txt records it [pre-existing].
> **Created:** 2026-11-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-21T19:13:54Z

## Summary

sprint close judges each open bug against the goal's clauses through `critic.judge_defects_against_goal`, which blocks a defect on the clause basis only when its dict carries falsifies. `sprint._open_defects` (sprint.py:9821) builds each defect from id, title and Severity alone and never sets falsifies, so a real close can never rule a defect on the clause basis: a bug carrying a Falsifies field is ruled leavable with 'falsifies no goal clause', and the sprint report's goal judgement section can say 0 BLOCKING while an open bug says it falsifies the goal. `judge_defects_against_goal`'s docstring also says a defect blocks when 'it names one' (a clause), which no code checks. Confirmed by the qa seat in run twenty-one's BG0987 round-two review as already true at the run base.

## Steps to Reproduce

1. In a fixture with a sprint goal of two clauses, open a bug whose header carries '> **Falsifies:** <the first clause>'. 2. Run sprint close (or `close_goal_judgement` on that state). 3. The defects line reads 0 BLOCKING and the bug is listed leavable, 'falsifies no goal clause'.

## Proposed Fix

Have `_open_defects` read the bug's Falsifies field into falsifies, and make the `judge_defects_against_goal` docstring say only what the code checks (an explicit falsifies), or implement the title match it claims.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: sprint close judges each open bug against the goal's clauses through `critic.judge_defects_against_goal`, which blocks a defect on the clause basis only when...
- [ ] **AC2** The proposed fix lands, pinned by a test: Have `_open_defects` read the bug's Falsifies field into falsifies, and make the `judge_defects_against_goal` docstring say only what the code checks (an...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-21 | sdlc-studio | Filed |
