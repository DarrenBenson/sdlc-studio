# BG1592: US1317's enterprise-page tests cannot tell a forecast figure from an actual, miss four network-call shapes, plant no failure for the http address check, and pin no link or key outside the controls section

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 2
> **Affects:** tools/tests/test_enterprise_doc.py
> **Evidence:** sdlc-studio/reviews/verdicts/US1317/60b1992c5231-2634e155.txt, findings 1 to 4.
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T16:19:17Z

## Summary

The qa review of US1317 (APPROVE, round 1) found, by mutation on an isolated export: swapping the $3.37 forecast and $2.00 actual on docs/enterprise.md, or calling the $172.05 forecast the actual, leaves the cost test green; the network scan misses `from socket import`, a git wrapper under another name, a git argv split across lines and a bare curl of a quoted URL variable; the http marker pattern (`_MARKERS`) set to an empty pattern survives; and an anchor typo, a misnamed config key or an invented installer flag outside the controls section all pass. The page is correct today; the tests would not catch it going wrong.

## Steps to Reproduce

On an export of fbdb7b10, swap $3.37 and $2.00 on docs/enterprise.md line 120, or plant `from socket import create_connection` in a skill script, then run tools/tests/`test_enterprise_doc.py`: all four tests stay green.

## Proposed Fix

Match each cost figure to the column it is labelled with (forecast or actual); widen the scan patterns to the four shapes; plant a failure for the http address check; walk every link and named config key on the page.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: The qa review of US1317 (APPROVE, round 1) found, by mutation on an isolated export: swapping the $3.37 forecast and $2.00 actual on docs/enterprise.md, or...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: On an export of fbdb7b10, swap $3.37 and $2.00 on docs/enterprise.md line 120, or plant `from socket import create_connection` in a skill script, then run...
- [ ] **AC3** The proposed fix lands, pinned by a test: Match each cost figure to the column it is labelled with (forecast or actual); widen the scan patterns to the four shapes; plant a failure for the http address...

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because only a test or pin is missing on behaviour that is right on every path a user reaches. docs/enterprise.md figures are correct; mutants swapping forecast and actual or using other network shapes survive. Test gaps only. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
