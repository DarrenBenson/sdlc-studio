# BG0987: The close's goal judgement reaches only the terminal, not the sprint report the signer is told to read, and says 'blocks the close' of defects that did not block it

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_close_goal_judgement_in_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, changelog.d/BG0987.md
> **Evidence:** Found closing a consuming project RUN-01M4APNQ on the installed skill (6.1.0 plus the BG0962 fix from main 922b9d6c), 2026-10-07. The close exited 0 and filed RPT0001; RPT0001.md, RPT0001.json and the .local HTML render contain no goal panel, no defect ruling and no caller-check line.
> **Created:** 2026-10-07
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-07T15:06:49Z

## Summary

`close_goal_judgement` (sprint.py, BG0385's repair) says it 'reports rather than refuses: the mechanisms inform the operator's sign-off'. Its lines are printed to stdout only. The close then says 'read it before signing: sdlc-studio/reports/RPT0001-...md', and that report carries none of them. In this run the terminal said: 'goal panel: UNANSWERED over 1 clause(s)'; 'defects vs goal: 4 BLOCKING, 20 leavable' (four open Highs); 'caller-check: 8 unit(s) of 10 ship a mechanism with no named caller'. A signer who reads the report, as instructed, sees none of it. Second, each blocking row reads 'priority high - a defect a release cannot carry blocks the close whatever the clause reasoning says' (`critic.judge_defects_against_goal`), but the close does not refuse on it, so the wording contradicts both the caller's contract and the exit code.

## Steps to Reproduce

Close a run with a sprint goal while a High-priority bug outside the batch is open: `sprint.py close --retro <id> --goal-verdict achieved --note x` -> terminal prints 'BLOCKING <id>: ... blocks the close ...', rc=0; `grep -c BLOCKING sdlc-studio/reports/RPT*.md` -> 0.

## Proposed Fix

Write the goal judgement (panel verdict, defects vs goal, caller-check) into the sprint report as its own section, so the sign-off artefact carries what the sign-off is meant to weigh. Reword the defect ruling for the close's reporting use ('would block a release: priority high', or 'blocks the goal claim') rather than 'blocks the close', or make the close refuse if blocking is intended.

## Acceptance Criteria

- [ ] **AC1** The sprint report filed by a close contains the goal panel verdict, each defect ruled blocking with its reason, and the caller-check count
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_goal_judgement_in_report.py -k report_carries_goal_judgement
- [ ] **AC2** No line the close prints claims to block the close when the close exits 0
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_goal_judgement_in_report.py -k no_block_claim_on_a_passing_close

## Triage

- Reproduced at e2090297 by the code path: `close_goal_judgement` (sprint.py:8324) returns lines the close prints, and `sprint_report.py` writes no goal-judgement section, so the filed report the signer is told to read carries none of them. The 'blocks the close whatever the clause reasoning says' wording is critic.py:1362, since US0543 (924ed69b, 2026-07-28). Not a regression.
- The filed text had `(`critic.judge_defects_against_goal)`` with the paren inside the span, the shape BG0967 records; corrected.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | Claude Opus 5.5 | Filed |
| 2026-10-07 | Claude Opus 5.5 (triage) | Triaged: reproduced at e2090297 by the code path, not a regression; consuming-project name generalised; a misplaced code span corrected; changelog fragment added |
