# BG0549: the non-convergence escalation is sticky: a converging APPROVE still reports that the panel is not converging, because the notice counts historical REJECTs and never re-reads the latest verdict

> **Status:** Open
> **Verification depth:** functional (executed over six cases: reject+reject escalates, reject+reject+APPROVE does not, a split within a round escalates, a split then APPROVE does not)
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** RUN-01KZEF9M, 2026-08-07. Three plan-review APPROVEs, each printing a non-convergence escalation, after two rounds that closed 21 of 24 findings between them.
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`critic.py record` escalates a unit to the operator once two REJECTs are on its log. It then prints that escalation on EVERY later record for the unit, including the APPROVE that resolves it: recording round 3's APPROVE on BG0541, US0660 and US0661 each printed 'the panel rejected this unit twice - the repair is not converging' beside a verdict that had just converged. The count is a lifetime one and the notice never consults the latest verdict, so the strongest signal the tool has - a panel that rejected twice and then approved - is rendered indistinguishable from a panel still rejecting. An operator reading the escalations sees three non-converging units where there are none, which is how a real escalation stops being read.

## Steps to Reproduce

1. Record two REJECT verdicts for a unit with `critic.py record --phase plan-review`. 2. Record an APPROVE for the same unit. 3. The APPROVE prints the non-convergence escalation, with the same wording as the second REJECT did.

## Proposed Fix

Resolve the escalation on a later APPROVE, and say so - 'converged at round 3 after 2 REJECT(s)' carries the useful part of the history without the false present tense. The reject count is worth keeping and worth reporting; what is wrong is the verb tense and the absence of the latest verdict from the sentence. This is LL0018 in a notice rather than a retry loop: 'it failed' and 'it is failing' are different questions.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `critic.py record` escalates a unit to the operator once two REJECTs are on its log.
- [ ] **AC2** The proposed fix lands, pinned by a test: Resolve the escalation on a later APPROVE, and say so - 'converged at round 3 after 2 REJECT(s)' carries the useful part of the history without the false...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Filed |
