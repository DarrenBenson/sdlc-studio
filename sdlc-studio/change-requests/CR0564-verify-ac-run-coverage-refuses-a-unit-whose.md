# CR-0564: verify_ac run --coverage refuses a unit whose new lines its own verifiers never execute

> **Status:** Complete
> **Decomposed-into:** EP0247
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Evidence:** RUN-01M1WPNV delivery, 2026-09-07: BG0646 (two REJECTs r1) and BG0649 (three REJECTs r1, two r2) - every rejection was a check a seat did in minutes that the author had not: run the shipped lane on this repository, measure a number written into prose, write a mutant for a branch the fixture never reached. Analysis recorded in the run's retro.
> **Date:** 2026-09-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Every surviving mutant the seats found this sprint sat on a branch the unit's own Verify selectors never executed (the quarantined and missing units of `handoff._classify`, the source-scan, no-output, first-line, timeout and label branches of the module-alone lane). The plan-time mutant table cannot name branches that do not exist yet, and the done-gate reads only those rows. Run the unit's selectors under coverage over its Affects files and report every added or changed line with zero hits; the transition to Fixed refuses a unit with uncovered new lines unless each is ruled equivalent with a reason, the way a mutant row is.

## Impact

Every rejected unit this sprint would have been refused Fixed before briefing instead of after a review round of about an hour across three seats; the seats confirm rather than discover.

## Acceptance Criteria

- [ ] Given a unit whose Affects diff adds a branch no Verify selector reaches, when `verify_ac.py run --id <unit> --coverage` runs, then the report names the file and lines uncovered by the unit's own verifiers, and `transition.py set <unit> Fixed` refuses naming them; a unit whose new lines are all executed passes - the control.
- [ ] Given an uncovered line ruled equivalent with a reason through the shipped command, when the transition runs again, then it passes and the ruling is in the depth field.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-07 | sdlc-studio | Raised |
