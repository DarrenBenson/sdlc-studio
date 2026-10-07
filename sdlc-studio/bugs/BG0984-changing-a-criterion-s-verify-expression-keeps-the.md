# BG0984: Changing a criterion's Verify expression keeps the old Verified date and evidence when the new one passes

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_restamp_on_changed_expression.py, changelog.d/BG0984.md
> **Evidence:** homelab BG0196:110-113, 2026-10-07; related BG0231
> **Created:** 2026-10-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-07T14:01:57Z

## Summary

homelab BG0196 AC1's Verify line was changed from `shell bash utilities/monitoring/check-cron-drift.sh` (a retired script) to `shell python3 utilities/fleet/drift-check.py check`. A non-dry `verify_ac.py run --id BG0196` then reported `pass=2 ... changes=0` and left `**Verified:** yes (2026-08-21)` with its evidence line describing the OLD command's run. The stamp now attests, with an August date, to a check that ran in October against a different command. BG0231 (Fixed) made freshness track the AC text; this is the residual on the PASSING path: a pass under a changed expression should restamp the date, or at least mark the evidence as the prior expression's.

## Steps to Reproduce

1. A criterion with `- **Verify:** shell <cmd A>` and `- **Verified:** yes (<old date>)`
2. Edit the Verify line to `shell <cmd B>` (which passes)
3. `verify_ac.py` run --id <unit> -> pass, changes=0; the Verified line keeps <old date>

## Proposed Fix

Record the expression's fingerprint beside the stamp (or compare against the last verify-report entry) and, on a pass under a different expression, rewrite the Verified date and drop or flag prior evidence. Test: change a passing expression to another passing one; the date must move.

## Acceptance Criteria

- [ ] **AC1** After a criterion's Verify expression changes and the new one passes, `verify_ac.py run` rewrites its Verified date to the run's date, and no evidence from the earlier expression's run stays attached to it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_restamp_on_changed_expression.py -k changed_expression_restamps
- [ ] **AC2** A criterion whose Verify expression is unchanged and still passes keeps its Verified date, so a re-run does not churn every stamp
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_restamp_on_changed_expression.py -k unchanged_expression_keeps_its_stamp

## Triage

- Reproduced at 34a7ee59 in a scratch fixture: a criterion stamped `Verified: yes (2026-08-21)` under `shell true`, its Verify changed to `shell test 1 -eq 1`, then `verify_ac.py run` -> pass=1, changes=0, and the stamp still reads 2026-08-21. Not a regression: the residual BG0231 (Fixed) left on the passing path.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | sdlc-studio | Filed |
| 2026-10-07 | Claude Opus 5.5 (triage) | Triaged: reproduced at 34a7ee59 in a fixture; tool-derived criteria replaced with two executable ones; changelog fragment added |
