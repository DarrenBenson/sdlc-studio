# BG0529: four RUN-01KZ9315 units carry no verifier that enters the shipped entry point, so the wiring each one exists to add is pinned by nothing

> **Status:** Open
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_plan_review.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_config.py
> **Evidence:** RUN-01KZ9315 close, 2026-08-06, commit c82d1248. Baselined with a stated reason in sdlc-studio/.validate-warning-baseline.json rather than repaired, because a finding surfaced during a close is filed and deferred - the rule that gives the close a fixed point. A baselined entry is reported stale and removable once fixed, never re-spendable.
> **Created:** 2026-08-06
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`lane-check` names four units of RUN-01KZ9315 - US0640, US0642, US0644, US0645 - each of which changes a command and none of whose verifiers drives that command. Every criterion is pinned in-process only.

The wiring is not unverified: both adversarial seats drove each mechanism through the CLI and reported the transcripts, and the run's own delivery exercised them by hand. What is missing is an AUTOMATED lane test - so the wiring is verified for today and pinned by nothing for tomorrow, which is precisely the state `critic.py brief --tier` was in for a whole sprint while `brief_fingerprint(brief(...))` passed in-process and the shipped verb printed nothing.

US0640's entry is worth separating from the other three. It appeared only because this close widened the unit's `Affects` to name `config.py` and `triage_noise.py`, where its AC4 actually landed. The lane is reporting a surface that was always there and was previously hidden by an understated footprint - the check got better, not the code worse.

## Steps to Reproduce

1. `git commit` on the RUN-01KZ9315 close. 2. The `warning-ratchet` lane fails, printing four LANE-CHECK lines: `US0640 ... this unit changes a command (plan_review.py, config.py, triage_noise.py) and NONE of its 4 verifier(s) enters the shipped entry point`, and the same shape for US0642 (critic.py), US0644 (critic.py) and US0645 (`sprint_report.py).`

## Proposed Fix

Add one CLI lane test per unit, driving the shipped verb in a throwaway fixture and asserting on its exit code and output rather than on a return value: `plan_review` enablement via the command that consults it, `critic.py brief` at both tiers asserting the claim-inventory block's presence and absence, `critic.py signoff` asserting the capacity column reaches the written row, and `sprint_report.py operator-summary` asserting the rendered page rather than the dict. Each already has a hand-run transcript from this run's review to assert against, so the expected output is not being invented.

CR0520 is the standing fix for the class - `verify_ac lane-check` gating a unit that changes a command and has no lane verifier - and this bug is four instances to close under it rather than a separate mechanism.

## Acceptance Criteria

- [ ] The behaviour described is corrected: `lane-check` names four units of RUN-01KZ9315 - US0640, US0642, US0644, US0645 - each of which changes a command and none of whose verifiers drives that...
- [ ] The proposed fix lands, pinned by a test: Add one CLI lane test per unit, driving the shipped verb in a throwaway fixture and asserting on its exit code and output rather than on a return value...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-06 | sdlc-studio | Filed |
