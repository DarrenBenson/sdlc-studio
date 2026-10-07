# BG0988: sprint plan's one-run-slot refusal tells the operator to finish a close that already finished, when only the signature is owed

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_plan_refusal_sign_owed.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, changelog.d/BG0988.md
> **Evidence:** Found in a consuming project, 2026-10-07: RUN-01M4APNQ's close exited 0 and filed RPT0001 ('sign it with: sprint.py sign --report RPT0001'); the next `sprint plan --write` was refused with the mid-close wording. Installed skill 6.1.0 plus the BG0962 fix from main 922b9d6c; code read at lib/run_state.py DisjointBatchError (~320-370).
> **Created:** 2026-10-07
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-07T15:19:15Z

## Summary

After a successful close the run stays `outcome: running` until `sprint sign` seals it, so the next plan hits DisjointBatchError. Its message reads 'RUN-01M4APNQ is mid-close, not finished: a close attempt has already run against it and left 0 item(s) outstanding. Finish that close rather than working around the run', then offers 'close the open run: sprint.py close' or 're-plan the open run'. It never names the step actually owed - `sprint.py sign --report RPT0001 --principal <operator>` - although the run state carries `report: RPT0001`. Re-running the close is a no-op (`close_is_a_noop`), so an operator following the message loops between a close that does nothing and a plan that refuses.

## Steps to Reproduce

Close a run successfully (report filed, nothing outstanding), do not sign, then `sprint.py plan --worklist <disjoint units> --write --sprint-goal x` -> 'mid-close ... left 0 item(s) outstanding. Finish that close', with no mention of `sign`.

## Proposed Fix

In DisjointBatchError, when the run state carries a filed report and the latest close attempt left 0 outstanding, say the close is complete and the run waits for its signature, and print the exact `sprint.py sign --report <id> --principal "<operator>"` command as the way forward (keeping the re-plan option).

## Acceptance Criteria

- [ ] **AC1** A plan refused by a closed-but-unsigned run names the sign command with the run's report id and does not tell the operator to finish the close
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_refusal_sign_owed.py -k names_the_sign_step
- [ ] **AC2** A plan refused by a run whose close left items outstanding still says to finish the close
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_refusal_sign_owed.py -k outstanding_close_still_says_finish

## Triage

- Reproduced at e2090297 by the code path: `DisjointBatchError`'s mid-close message (lib/run_state.py:358) says to finish the close and never names `sprint.py sign`, though the run state records the filed report. Not a regression.
- The filed text had `(`close_is_a_noop)`` with the paren inside the span, the shape BG0967 records; corrected.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | Claude Opus 5.5 | Filed |
| 2026-10-07 | Claude Opus 5.5 (triage) | Triaged: reproduced at e2090297 by the code path, not a regression; consuming-project name generalised; a misplaced code span corrected; changelog fragment added |
