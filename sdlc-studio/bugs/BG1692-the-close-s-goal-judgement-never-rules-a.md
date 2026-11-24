# BG1692: The close's goal judgement never rules a defect on the clause basis: _open_defects never reads Falsifies

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_close_goal_judgement_in_report.py, .claude/skills/sdlc-studio/reference-bug.md, changelog.d/BG1692.md
> **Evidence:** sprint.py:9821-9832 (_open_defects) sets id, title, priority only; critic.py:1814 reads d.get('falsifies'); git log -S'falsifies' on sprint.py shows no writer. sdlc-studio/reviews/verdicts/BG0987/b4a76987a77a-f7326d56.txt records it [pre-existing].
> **Created:** 2026-11-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-21T19:13:54Z

## Summary

sprint close judges each open bug against the goal's clauses through `critic.judge_defects_against_goal`, which blocks a defect on the clause basis only when its dict carries falsifies. `sprint._open_defects` (sprint.py:9821) builds each defect from id, title and Severity alone and never sets falsifies, so a real close can never rule a defect on the clause basis: a bug carrying a Falsifies field is ruled leavable with 'falsifies no goal clause', and the sprint report's goal judgement section can say 0 BLOCKING while an open bug says it falsifies the goal. `judge_defects_against_goal`'s docstring also says a defect blocks when 'it names one' (a clause), which no code checks. Confirmed by the qa seat in run twenty-one's BG0987 round-two review as already true at the run base.

Reproduced at cecc9dfe7 (2026-11-24): `sprint._open_defects` (now sprint.py:10144) over a bug file carrying `> **Falsifies:** the parser keeps every tab` returns `{id, title, priority}` with no `falsifies`, and `critic.judge_defects_against_goal` (critic.py:1809) then rules it leavable, `falsifies no goal clause`. `test_close_goal_judgement_in_report.py`'s `_closed` fixture says as much: it wraps `_open_defects` to add `falsifies`, because the close reads no such field, so the clause-basis test passes only through that patch. No template, reference or writer names a `Falsifies` field today, so the reader needs one line in reference-bug.md for a filer to find it.

## Steps to Reproduce

1. In a fixture with a sprint goal of two clauses, open a bug whose header carries '> **Falsifies:** <the first clause>'. 2. Run sprint close (or `close_goal_judgement` on that state). 3. The defects line reads 0 BLOCKING and the bug is listed leavable, 'falsifies no goal clause'.

## Proposed Fix

Have `_open_defects` read the bug's `Falsifies` header field into `falsifies` when it is present and non-empty, drop the `_open_defects` wrapper from `test_close_goal_judgement_in_report.py` so the clause half is judged from the bug file, make the `judge_defects_against_goal` docstring say only what the code checks (an explicit `falsifies`, not a clause the defect names), and name the optional field in reference-bug.md.

## Acceptance Criteria

- [ ] **AC1** Given a run whose goal is one clause and an open Low bug whose file carries `> **Falsifies:** <that clause>`, when `sprint close` runs with `_open_defects` unpatched, then the close prints `BLOCKS THE GOAL CLAIM <id>: falsifies the goal clause: <clause>`, the report's goal judgement row reads `blocks the goal claim` for it, and the close exits 0. Fails on: the bug ruled leavable, `falsifies no goal clause`, with `0 BLOCKING`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_goal_judgement_in_report.py::CloseGoalJudgementInReportTests::test_a_falsifies_field_in_the_bug_file_blocks_the_goal_claim
- [ ] **AC2** Given three bugs, one Open with a `Falsifies` field, one Open with none and one Fixed with a `Falsifies` field, when `sprint._open_defects` reads the project, then only the first carries `falsifies`, with the field's text, and the Fixed bug is not listed. Fails on: no defect ever carrying `falsifies`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_goal_judgement_in_report.py::OpenDefectsFalsifiesTests::test_open_defects_reads_falsifies_only_where_declared
- [ ] **AC3** Given `critic.judge_defects_against_goal`'s docstring, when it is read, then it no longer says a defect blocks because it names a clause, which no code checks. Fails on: the docstring's `it names one, or an explicit` clause still present.
  - **Verify:** shell ! grep -q "it names one, or" .claude/skills/sdlc-studio/scripts/critic.py

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-21 | sdlc-studio | Filed |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-five: reproduced at cecc9dfe7; line references refreshed; three executable criteria (the close unpatched, the reader, the docstring); Affects drops test_sprint.py and test_critic.py and adds reference-bug.md |
