# CR-0514: The amigo panel signs off a sprint to completion: a different seat from the one that reviewed it, gated on brief provenance and a converging review loop

> **Status:** Proposed
> **Supersedes:** CR0521
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/persona_resolve.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/reference-doctrine.md
> **Priority:** High
> **Type:** Feature
> **Size:** L

## Summary

OPERATOR POLICY: **human in the LEAD, not in the loop.** The operator sets the goal, the
appetite and the scope, is told what happened, and is otherwise not a step in the machine.

The lived process today is the opposite, and it is the requirement stated as a defect: the code
completes, the operator signs off, the reviews THEN run and fail for many hours, and the sprint
closes afterwards. That sequence is wrong in three separate places at once. The signature covers
work no reviewer has yet looked at. The operator blocks the critical path while being uninformed
about the failure that follows. And the reviews are positioned where `help/sprint.md` already
says they must not be - at the close, where "every defect it finds is close work by definition"
rather than at the delivery batch boundary where it is priced in the batch that caused it.

The fix is a RE-SEQUENCE, not only a change of signer.

- PLAN - the operator sets goal, appetite and scope. This is the lead decision and the one place
  a human belongs in the path.
- DELIVER - each batch is reviewed at its own boundary, by a seat that did not write it, and its
  findings are repaired inside that batch. No human, and no phase of accumulated failure after
  the work is done.
- CLOSE - the panel signs, the run closes, and the operator is TOLD: what shipped, what was
  carried, what it cost, and what the reviews found.
- EXCEPTION - only a non-converging loop or a stop-ship interrupts, and it interrupts by
  NOTIFYING, never by parking silently and waiting to be discovered.

A sprint runs to completion and closes on the amigo panel's judgement, with no human signature. Today the reviewer-of-record role is the operator's, so every autonomous run stalls at the close holding units at Review - on RUN-01KYX375, thirty-three points across nine units waited on one signature. A product a developer can actually use cannot require its author to sign each unit.

The two-role rule is NOT relaxed. `is_independent_signoff` already refuses any principal drawn from `_session_reviewer_ids` - every seat that recorded evidence or a verdict on that unit - so the separation the doctrine protects is 'the seat that reviewed it never signs it', not 'a human signs it'. A DIFFERENT amigo seat signing is already structurally legal; what is missing is the role assignment, the safety interlock, and a termination condition.

The interlock matters more than the rest. An auto-signed sprint is only as good as the brief its reviewers were given, and RUN-01KYX375 measured both ends of that: four rounds of hand-written prompts produced sprawling, partly-spurious REJECTs over the whole repository, while the same units re-reviewed from `critic.py brief` produced one precise blocking finding each with pre-existing noise reported and set aside. Panel sign-off without enforced brief provenance would automate the first behaviour.

## Impact

Unblocks autonomous delivery: `sprint --autonomous` currently cannot reach Done, so the Goal-Driven loop the product is sold on stops one step short. It also removes the failure this run hit twice - a close held for a signature while the work was finished and independently reviewed.

The risk it introduces is a self-approving loop, and the mitigations are the interlock (no provenance, no panel sign-off), disjoint role assignment (the signing seat never reviewed the unit), and a hard termination condition so a non-converging review cannot spin.

## Acceptance Criteria

- [ ] With `review.signoff: panel`, a unit whose adversarial pass came from a different seat reaches Done with no human signature, and the record names the signing seat
- [ ] A seat that recorded evidence or a verdict on a unit is REFUSED as that unit's signer - the existing independence rule, proven still to hold under panel mode
- [ ] A unit whose adversarial verdicts carry no brief provenance is NOT panel-signed; the sign-off falls back to the operator and states the reason
- [ ] A review-repair loop whose outstanding set grows across two consecutive rounds stops the run and hands off, rather than continuing - the positive control being that a converging set runs on
- [ ] A unit the panel rejects twice escalates to the operator instead of looping, and the escalation notifies rather than parking the unit to be discovered
- [ ] A run delivering more than one batch opens and closes a review span per batch, so a review finding is recorded against the batch that caused it - proven by a run whose finding carries a batch id rather than `none open`
- [ ] A run reaching its close having opened no span REPORTS that its reviews were mispositioned, distinctly from a run that had no findings
- [ ] The close emits an operator report naming what shipped, what was carried, what it cost and what the reviews found, and a run that cannot deliver that report says so rather than closing silently
- [ ] No path holds a unit at Review awaiting a human signature under `review.signoff: panel`; the only human-blocking states are a notified escalation or a notified tooling failure
- [ ] `review.signoff` defaults to `operator`, so an existing consuming project's behaviour is unchanged until it opts in
- [ ] A panel-signed unit and an operator-signed unit are distinguishable in the signoff record and in the sprint report, asserted by reading both back

## Proposed Fix

1. ROLE ASSIGNMENT. `persona_resolve.py panel` assigns the adversarial seats and the SIGNING seat for a unit, disjoint by construction, and the assignment is recorded on the run. The existing `_session_reviewer_ids` refusal then enforces it at write time with no change.
2. INTERLOCK. Panel sign-off is permitted for a unit ONLY when every adversarial verdict on it carries the brief provenance CR0512 introduces. An unbriefed panel never signs - but missing provenance is a TOOLING failure, not a judgement call, so the run STOPS and NOTIFIES rather than parking the unit at Review awaiting a human. The distinction is the whole policy: a machine that cannot proceed tells the operator immediately; it never silently queues work behind a signature.
3. TERMINATION. The review-repair loop declares a round cap, and the growing-set detector that already exists (`sprint.py`, outstanding-set shrank-or-grew) GATES rather than reports: a set that grows across two consecutive rounds stops the run and hands off to the operator with the divergence named. A loop with no exit is worse than a stalled close.
4. OPT-IN, NOT DEFAULT. `review.signoff: operator | panel` in `.config.yaml`, defaulting to `operator`, so no consuming project silently loses its human. This repo sets `panel`.
5. THE RECORD SAYS WHICH. A panel-signed unit is distinguishable from an operator-signed one forever, in the signoff record and in the sprint report. The product's claim is that its records mean something; 'who accepted this' is exactly the kind of fact that must not become ambiguous.
6. ESCALATION. A unit the panel REJECTS twice, or one whose seats disagree, is escalated to the operator rather than auto-resolved - and escalation NOTIFIES rather than waits.
7. REVIEW PLACEMENT IS PART OF THIS. Panel sign-off is worth little if the reviews still run as a serial phase after delivery. `sprint` opens a review span per delivery batch and closes it when that batch commits, so a failing review is delivery work in the batch that caused it rather than hours of accumulated close work. A run that reaches its close having opened no span is reporting that its reviews were mispositioned, not that it had none.
8. INFORM. The close ACTIVELY reports to the operator - shipped, carried, cost, and what the reviews found - rather than leaving a file to be discovered. Being informed is the operator's half of the contract; a report nobody is told about is the same as no report.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
