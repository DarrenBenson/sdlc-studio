# BG0528: a delivered unit left at Ready is invisible to every close gate: twenty blockers were reported and not one of them said the units had never been transitioned

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_conformance.py
> **Evidence:** RUN-01KZ9315, 2026-08-06, at commits 9dc330f5 through f1762b8c. `sprint.py preflight` output showing twenty blockers with no status line; `critic.py signoff --panel --from-run` writing 4 of 12 units and skipping 8 with the status reason; the same command writing all 8 after `transition.py set --status Review`.
> **Created:** 2026-08-06
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Eight of RUN-01KZ9315's twelve units had their code committed with a green full suite and were never transitioned out of `Ready`. The close then reported twenty unmet prerequisites across four categories - no independent review coverage, no critic verdict, no reviewer-of-record sign-off, and a blocked Done gate on each story - and not one of them named the actual cause. Every message described a downstream consequence of a status that had not moved.

The cost was a run held open for more than twenty-four hours. The diagnosis arrived only when `critic.py signoff` refused with the one message in the chain that reads the status directly: `its status is 'Ready', which is neither terminal nor awaiting sign-off - the work has not been delivered`. That message exists, it is exact, and nothing upstream of it asks the question.

The pre-flight is the command whose whole purpose is to report every blocker in one pass (US0638). It reports what is missing from the ledgers and never that the units are not yet in a state where a ledger entry is meaningful. A unit at `Ready` with committed code is a state the tooling can detect for nothing: its `Affects` files carry commits inside the run window and its status has not moved.

## Steps to Reproduce

Observed on RUN-01KZ9315, 2026-08-06. 1. Twelve units delivered across six commits, full suite green at each. 2. Four bugs reached `Fixed`; eight stories stayed at `Ready`. 3. `sprint.py preflight` exits 1 with `20 unmet prerequisite(s) - ALL of them`, listing review coverage, sign-off and Done-gate failures for the eight stories. No line mentions their status. 4. `critic.py signoff --panel` is the first command to say it: `sign-off SKIPPED for US0638: its status is 'Ready', which is neither terminal nor awaiting sign-off`. 5. `transition.py set --id <id> --status Review` on each, and the same sign-off command then writes all eight.

## Proposed Fix

Add a status pre-condition to `close_preflight`, ahead of the review-coverage check, that names any batch unit still in a pre-delivery status whose declared `Affects` carry commits inside the run window - and prints the transition that moves it. It belongs there rather than at the sign-off step because the pre-flight is the command that promises to report every blocker in one pass, and a blocker it cannot see makes the other nineteen unreadable.

Derive the pre-delivery set from the status vocabulary rather than listing `Ready` and `In Progress` by name, or the check exempts whatever status a project adds next.

The deeper fix is that nothing makes a commit and a status agree. A unit whose files were committed inside the run window and whose status never moved is a detectable disagreement, and it is the same shape as the claim-drift lane: the code and the record say different things.

## Acceptance Criteria

- [ ] The behaviour described is corrected: Eight of RUN-01KZ9315's twelve units had their code committed with a green full suite and were never transitioned out of `Ready`.
- [ ] The proposed fix lands, pinned by a test: Add a status pre-condition to `close_preflight`, ahead of the review-coverage check, that names any batch unit still in a pre-delivery status whose declared...

## Impact

Every run. The failure is silent, it costs the whole close, and the operator's visible symptom is a long list of blockers none of which is the problem.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-06 | sdlc-studio | Filed |
