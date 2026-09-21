# EP0256: Stakeholder feedback arrives while it is still cheap to act on

> **Status:** Draft
> **Derived Point Total:** 37
> **Parent:** RFC0058
> **Created:** 2026-09-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from RFC0058. Delivers the work RFC0058 requested.

## Story Breakdown

- [ ] [US0838: refine runs a stakeholder consult over the epic and its stories and records it as an artefact naming the units it covered](../stories/US0838-refine-runs-a-stakeholder-consult-over-the-epic.md)
- [ ] [US0839: a risk trigger derived from Affects and unit type names which units still owe a consult, and most bugs skip without a reason](../stories/US0839-a-risk-trigger-derived-from-affects-and-unit.md)
- [x] [US0840: a consult artefact carries each persona's verdict and a disposition per finding, so a consult can be counted rather than remembered](../stories/US0840-a-consult-artefact-carries-each-persona-s-verdict.md)
- [ ] [US0841: an unanswered stakeholder Reject is reported at the close, holding nothing, and the operator rules it](../stories/US0841-an-unanswered-stakeholder-reject-is-reported-at-the.md)
- [ ] [US0842: consult yield is measured - findings per consult and the share folded or filed - so the requirement is revisited on evidence](../stories/US0842-consult-yield-is-measured-findings-per-consult-and.md)
- [ ] [US0847: a persona card records when it was authored, from what evidence and when it was last revisited, and every consult figure carries that age](../stories/US0847-a-persona-card-records-when-it-was-authored.md)
- [ ] [US0858: a consult artefact's verdicts and dispositions come from closed sets, and a FILE disposition names an id that resolves](../stories/US0858-a-consult-artefact-s-verdicts-and-dispositions-come.md)
- [ ] [US0859: a consult artefact's coverage is the stamped unit list and each verdict row's cast role is read from the persona card](../stories/US0859-a-consult-artefact-s-coverage-is-the-stamped.md)

## Acceptance Criteria (Epic Level)

- [ ] **EA1** `refine` completes only by producing a stakeholder consult or a written skip reason (D0211), and a project with no personas authored degrades to a recorded skip rather than a refusal.
- [ ] **EA2** A consult artefact carries each persona's verdict, a disposition per finding, the units it covered, and per-persona fresh-context provenance - the field that separates an independent consult from a session reviewing its own work.
- [ ] **EA3** The risk trigger ships ADVISORY, refusing nothing, and its measured behaviour over this repository's existing backlog is recorded before it is trusted (US0839 AC4).
- [ ] **EA4** The owed list is printed at `sprint plan`, the cheap moment, and an unanswered stakeholder Reject is reported at the close without holding it (D0210).
- [ ] **EA5** Consult yield counts anti-persona findings separately from primary-persona findings, and states the persona-validity limit (RFC0058 D5, open) wherever the number is shown.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Created via `new` (deterministic) |
