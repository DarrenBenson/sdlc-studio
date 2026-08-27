# EP0242: A bug's plan or evidence gets an independent judgement, and the asymmetry is stated

> **Status:** Draft
> **Derived Point Total:** 11
> **Parent:** CR0556
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0556. Delivers the work CR0556 requested.

## Story Breakdown

- [ ] [US0797: The independent element the gate demands is STATED in the refusal when a bug reaches terminal](../stories/US0797-the-independent-element-the-gate-demands-is-stated.md)
- [ ] [US0798: A project that has not adopted the change is unaffected, bound behind a dated cutoff](../stories/US0798-a-project-that-has-not-adopted-the-change.md)
- [ ] [US0799: The doctrine STATES which types are independently judged and at which transition](../stories/US0799-the-doctrine-states-which-types-are-independently-judged.md)
- [ ] [US0800: A bug whose declared mutant was killed by a test its criterion does not name is REPORTED](../stories/US0800-a-bug-whose-declared-mutant-was-killed-by.md)

## Acceptance Criteria (Epic Level)

- [ ] Given a bug reaching a terminal status under whichever option is adopted, when the gate runs, then the independent element it demands is stated in the refusal, so an author learns what is wanted rather than that something is missing
- [ ] Given a project that has not adopted the change, when a bug transitions, then behaviour is unchanged - bound behind a dated cutoff on the same terms as every sibling gate, so an existing backlog is not retro-refused
- [ ] Given the asymmetry between bugs and stories after this lands, when the doctrine is read, then it STATES which types are independently judged and at which transition, because the current asymmetry is undocumented and was found by measurement rather than by reading
- [ ] Given a bug whose declared mutant was killed by a test its criterion does not name, when the adopted check runs, then that is reported - the specific weakness this request is filed about, and the one a review found six instances of in a single six-unit batch

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Created via `new` (deterministic) |
