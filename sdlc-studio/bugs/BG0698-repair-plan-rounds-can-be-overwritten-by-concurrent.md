# BG0698: Repair-plan rounds can be overwritten by concurrent records, a re-record after approval counts as a failed round, and the escalation notice counts a repair-plan REJECT

> **Status:** Superseded
> **Closes with:** US0913 (D0264: superseded only once it ships; backlog sweep D0265, sdlc-studio/reviews/backlog-sweep-2026-09-24.md)
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/repair_plan.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_repair_plan.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/reference-scripts.md, .claude/skills/sdlc-studio/reference-scripts-review.md
> **Evidence:** Independent delivery review, RUN-01M2JA6J 2026-09-15: verdicts/BG0678-delivery-engineering.txt (engineering seat); verdicts/BG0678-delivery-qa.txt (qa seat); verdicts/BG0673-delivery-engineering.txt (engineering seat); verdicts/BG0673-delivery-qa.txt (qa seat); verdict rows in sdlc-studio/reviews/critic-verdicts.md. Also queued in findings/todo.txt (round files not written exclusively; re-record after approval counted as a failed round).
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Round files are not written exclusively: twelve concurrent record calls on one unit all exited 0 but left nine round files (`repair_plan.py`:287-290 takes max+1, then `write_text)`, which contradicts 'none is ever written over' (`repair_plan.py`:73). Every re-record after an approval counts as a failed round: a plan approved twice and re-recorded a third time with design retain is refused as 'has failed 2 round(s)' though no round was rejected (probed). `plan_reviewed` re-implements `verdict_for`'s retirement filter and unanswered-REJECT scan and calls the private `critic._brief_key` and `critic._is_principal_superseded` (`repair_plan.py`:366-383), a second copy of the rule that can drift. The escalation notice reads plan-review rows without their kind (critic.py:2270), so a `repair_plan.py` review REJECT followed by a critic.py record --kind test-plan REJECT prints 'ESCALATED ... rejected this unit twice'; a notice only, it never blocks. Unpinned: AC1 case 5 proves 'not only the latest round' but not 'any round' - a `plan_reviewed` that reads only round one's file (`repair_plan.py`:398) passes all 34 tests, and the reverse case (reviewer wrote round two, row names round one's author) is untested; the read-back at `test_repair_plan.py`:737 pins `plan_authors`, not that `plan_reviewed` calls it. `review_repair_plan`'s any-round independence refusal (`repair_plan.py`:324) can revert to the latest author alone with every test passing. The rule that only a LATER APPROVE by the same reviewer retires a REJECT (`repair_plan.py`:379, live[i + 1:]) is unpinned. The case-folded identity comparison (`critic.same_identity)` can become an exact-string compare with every test passing. Doc drift: reference-scripts.md:205 and reference-scripts-review.md:38 still say the verdict is pinned to the findings, and neither they nor the review --reviewer help say a reviewer must keep one name across rounds.

## Steps to Reproduce

1. Run twelve python3 .claude/skills/sdlc-studio/scripts/`repair_plan.py` record --unit <bug> calls concurrently - all exit 0, nine round files remain. 2. Record, approve, re-record, approve, then re-record with design retain - refused as 'has failed 2 round(s)'. 3. `repair_plan.py` review --unit <bug> --verdict REJECT --reviewer carol, then critic.py record --unit <bug> --kind test-plan --verdict REJECT - the ESCALATED notice prints.

## Proposed Fix

Create each round file with open(p, 'x') and retry on FileExistsError. Count failed rounds from REJECT verdicts, not from re-records. Have `plan_reviewed` call one public critic helper for retirement and the unanswered scan. Filter escalation rows by kind. Add tests for the reverse any-round case, the independence refusal, a same-reviewer later APPROVE and case-folded names. Update the two reference pages and the --reviewer help.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Round files are not written exclusively: twelve concurrent record calls on one unit all exited 0 but left nine round files (`repair_plan.py`:287-290 takes...
- [ ] **AC2** The proposed fix lands, pinned by a test: Create each round file with open(p, 'x') and retry on FileExistsError.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Filed |
| 2026-09-24 | Claude Opus 5.5 | Backlog sweep D0265 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md): held open under D0264 until US0913 ships - planning: SUPERSEDED - repair-plan rounds: repair ledger deleted in batch 2; superseded only once US0913 ships (D0264) |
| 2026-09-25 | sdlc-studio BG0772 | Superseded under D0264: its closing story US0913 is Done (BG0772) |
