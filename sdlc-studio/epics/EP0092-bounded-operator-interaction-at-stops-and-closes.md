# EP0092: Bounded operator interaction at stops and closes

> **Status:** Done
> **Parent:** CR0371
> **Derived Point Total:** 16
> **Parent:** CR0369
> **Created:** 2026-07-20
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0369 and CR0371. Delivers the operator-interaction work both requested:
decisions asked as structured questions without stalling the batch (CR0369), and a close that
can file its blockers and terminate honestly (CR0371).

## Story Breakdown

- [x] [US0280: A unit needing an operator decision is set aside and the batch continues; accumulated decisions are asked together at the stop](../stories/US0280-a-unit-needing-an-operator-decision-is-set.md)
- [x] [US0281: Operator questions are presented as structured decisions with named options and a marked recommendation](../stories/US0281-operator-questions-are-presented-as-structured-decisions-with.md)
- [x] [US0282: Close offers a bounded file-and-close path: blockers filed as linked artefacts, outcome records outstanding work](../stories/US0282-close-offers-a-bounded-file-and-close-path.md)
- [x] [US0283: Close reports whether the outstanding set shrinks or grows across re-runs; hard correctness gates stay unwaivable](../stories/US0283-close-reports-whether-the-outstanding-set-shrinks-or.md)

## Acceptance Criteria (Epic Level)

### From CR0369

- [ ] Given a batch where one unit needs an operator decision and others do not, when the run reaches it, then the blocked unit is set aside and the remaining units continue, so the run stops only when it can make no further progress
- [ ] Given the run must ask the operator something, when it asks, then the question is presented in a structured form - the question itself, named options, and the consequence of each - rather than as prose the operator must parse a decision out of
- [ ] Given the agent has a view on the right answer, when the question is presented, then its recommendation is marked as such with the reason, so the operator can accept the default quickly or override it deliberately
- [ ] Given several decisions accumulated while the run continued, when the run finally stops, then they are asked together rather than one stop per decision
- [ ] Given a non-interactive run, when a decision is needed, then behaviour is unchanged - the question is recorded and the unit is blocked, never silently defaulted

### From CR0371

- [ ] Given a close with unmet blockers, when the close runs, then the operator is offered a bounded choice - fix them, or file them and close - rather than only the fix path
- [ ] Given the operator chooses to file and close, when the close completes, then each blocker is recorded as a real artefact linked to the run, and the run's outcome states plainly that it closed with known outstanding work
- [ ] Given the operator chooses to file and close, when the close completes, then nothing is silently waived: the retro and the review anchor both name what was deferred and why
- [ ] Given a blocker that is a hard correctness gate rather than an administrative one, when the operator chooses to file and close, then it is still refused - filing is for ceremony debt, never for a failing test or a red gate
- [ ] Given repeated close attempts, when a close is re-run, then it reports whether the outstanding set is shrinking or growing, so a spiral is visible rather than inferred

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Created via `new` (deterministic) |
