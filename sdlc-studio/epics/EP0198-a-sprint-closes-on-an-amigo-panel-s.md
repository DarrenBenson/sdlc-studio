# EP0198: A sprint closes on an amigo panel's sign-off, so the operator is informed and never a step in the machine

> **Status:** Draft
> **Derived Point Total:** 31
> **Parent:** CR0514
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** XL

## Summary

Decomposed from CR0514. Delivers the work CR0514 requested.

## Story Breakdown

- [ ] [US0598: persona_resolve panel assigns the adversarial seats and the SIGNING seat disjointly, and the assignment is recorded on the run](../stories/US0598-persona-resolve-panel-assigns-the-adversarial-seats-and.md)
- [ ] [US0599: A panel may sign a unit only when every adversarial verdict on it carries brief provenance, and missing provenance STOPS the run and notifies rather than parking it](../stories/US0599-a-panel-may-sign-a-unit-only-when.md)
- [ ] [US0600: The review-repair loop declares a round cap and the growing-set detector GATES rather than reports, so a diverging loop stops and hands off](../stories/US0600-the-review-repair-loop-declares-a-round-cap.md)
- [ ] [US0601: review.signoff is operator by default and panel only by explicit config, so no consuming project silently loses its human](../stories/US0601-review-signoff-is-operator-by-default-and-panel.md)
- [ ] [US0602: A panel-signed unit is distinguishable from an operator-signed one forever, in the signoff record and in the sprint report](../stories/US0602-a-panel-signed-unit-is-distinguishable-from-an.md)
- [ ] [US0603: A unit the panel rejects twice, or whose seats disagree, escalates to the operator by NOTIFYING rather than waiting](../stories/US0603-a-unit-the-panel-rejects-twice-or-whose.md)
- [ ] [US0604: The close actively REPORTS to the operator - shipped, carried, cost and what the reviews found - rather than leaving a file to be discovered](../stories/US0604-the-close-actively-reports-to-the-operator-shipped.md)

## Acceptance Criteria (Epic Level)

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

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
