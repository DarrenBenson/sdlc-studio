# EP0085: The close review is a bounded loop: rounds are counted, repair regressions are named, cost is surfaced, and the reviewer's brief is neutral by construction

> **Status:** Draft
> **Derived Point Total:** 17
> **Parent:** CR0358
> **Created:** 2026-07-19
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0358. Delivers the work CR0358 requested.

## Story Breakdown

- [ ] [US0261: Count review rounds on the run state and refuse another past a configured ceiling without explicit operator confirmation](../stories/US0261-count-review-rounds-on-the-run-state-and.md)
- [ ] [US0262: Detect a repair regression: a finding in code the previous round's repair touched is reported distinctly from a fresh finding](../stories/US0262-detect-a-repair-regression-a-finding-in-code.md)
- [ ] [US0263: On a repair regression, escalate to a revert / redesign / accept-and-file decision instead of another patch round](../stories/US0263-on-a-repair-regression-escalate-to-a-revert.md)
- [ ] [US0264: Record cumulative review token cost per round and show it when the next round is offered](../stories/US0264-record-cumulative-review-token-cost-per-round-and.md)
- [ ] [US0265: Generate the reviewer brief from a neutral template carrying the diff and risk surface but no prior verdicts, round number or expected conclusion](../stories/US0265-generate-the-reviewer-brief-from-a-neutral-template.md)

## Acceptance Criteria (Epic Level)

- [ ] the review loop counts its rounds on the run state and refuses to start another past a configured ceiling without explicit operator confirmation
- [ ] a finding located in code the previous round's repair touched is reported as a repair regression, distinctly from a fresh finding
- [ ] on a repair regression the loop escalates to a revert / redesign / accept-and-file decision instead of another patch round
- [ ] cumulative review token cost is recorded per round and shown when the next round is offered
- [ ] the reviewer brief is generated from a neutral template that carries the diff and risk surface but not the prior verdicts, the round number, or any expected conclusion

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Created via `new` (deterministic) |
