# BG0539: critic record cannot tell a review ROUND from a panel SEAT, so the ordinary reject-fix-approve loop escalates as an unresolved split

> **Status:** Fixed
> **Verification depth:** functional (executed: a REJECT in round 1 with an APPROVE in round 2 no longer reports a panel split; mutation: 1 declared mutant KILLED, anchor asserted unique, restore byte-exact)
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** RUN-01KZCAJX, 2026-08-07. Eight EP0207 test plans reviewed by independent subagents; round 1 rejected all eight with blocking findings, the plans were revised, round 2 approved six and rejected two. All eight escalated - six as splits, two as non-converging - so the escalation carried no signal about which four units were actually stuck.
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`critic.py record` detects a panel split by comparing the free-text `--reviewer` strings behind the verdicts on one unit. A second review round is a different context reviewing the same unit under the SAME seat after the author repaired what round one found - and it necessarily carries a different reviewer string, because it is genuinely a different reviewer. So the normal reject-repair-approve loop is reported as `the panel split ... the disagreement is the finding, so it is not resolved by majority` and escalates to the operator.

Eight units did this in one run: every one had a round-1 REJECT with substantive findings, the plans were revised, and a round-2 seat approved. Six escalated as splits. The remaining two, correctly rejected twice, escalated under a different rule - so the tool's output cannot distinguish a converging repair from a stuck one, which is the single thing an escalation exists to tell the operator.

The workaround is to reuse one reviewer string across rounds, and that is worse than the bug: it asserts that one context did both reviews when two did.

## Steps to Reproduce

1. `critic.py record --unit U --phase plan-review --verdict REJECT --reviewer 'qa; seat; round 1' --brief <fp1>`. 2. Repair whatever was found. 3. `critic.py record --unit U --phase plan-review --verdict APPROVE --reviewer 'qa; seat; round 2' --brief <fp2>`. 4. The second call escalates: the panel split, round 1 rejected while round 2 approved. There was no panel and no disagreement - there was a defect and a fix.

## Acceptance Criteria

- [x] **AC1** Given a unit reviewed across two ROUNDS - a REJECT then a later APPROVE - when the escalation is computed, then it is not reported as a panel SPLIT: a second round is a different context reviewing a revised unit, not disagreement inside one round.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py -k a_second_round_is_not_a_panel_split

## Proposed Fix

A round is not a seat. Give the verdict a round ordinal - derived from the brief fingerprint changing, which already happens whenever the artefact under review is edited, or recorded explicitly - and compare only verdicts within one round when deciding whether a panel disagreed.

Across rounds the rule is latest-wins per seat, which is what `critic.verdict_for` already does one function away for per-unit verdicts. The split detector should reuse that resolution rather than carry a second, contradicting one - two readers of one question disagreeing about it is the shape this repo files as a defect in its own right.

What must survive: two seats disagreeing INSIDE one round is still a genuine split and must still escalate, and a unit rejected twice must still escalate as non-converging. Both need a test, or the fix trades a false escalation for a missing one.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in critic.py `panel_escalation`, delete the convergence check so seat verdicts from different rounds compare as one | Given a unit reviewed across two ROUNDS - a REJECT then a later APPROVE - when the escalation is computed, then it is not reported as a panel SPLIT: a second round is a different context reviewing a revised unit, not disagreement inside one round. |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Filed |
