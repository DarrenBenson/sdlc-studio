# EP0231: A charter can select what a request decomposed into, and says so when it cannot

> **Status:** Draft
> **Derived Point Total:** 12
> **Parent:** CR0531
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0531. Delivers the work CR0531 requested.

## Story Breakdown

- [ ] [US0750: A charter's scope query can select the units a request was decomposed into](../stories/US0750-a-charter-s-scope-query-can-select-the.md)
- [ ] [US0751: The vocabulary stays `sprint plan`'s own, parsed by the same code](../stories/US0751-the-vocabulary-stays-sprint-plan-s-own-parsed.md)
- [ ] [US0752: SC0001's query and its prose rule agree, pinned by a test](../stories/US0752-sc0001-s-query-and-its-prose-rule-agree.md)
- [ ] [US0753: A charter whose query cannot be reconciled with its rule is REPORTED at materialise time](../stories/US0753-a-charter-whose-query-cannot-be-reconciled-with.md)

## Acceptance Criteria (Epic Level)

- [ ] A charter's scope query can select the units a request was decomposed into, so a rule like `everything CR0507 decomposes into` is expressible rather than approximated by a status sweep.
- [ ] The vocabulary stays `sprint plan`'s own - one selector grammar in the tool, parsed by the same code - which is the reason D0127 chose the status query and is not given up to gain expressiveness.
- [ ] SC0001's query and its prose rule agree after the change, and a test pins that the queued charter resolves the units its rule names rather than 15 CRs against an 8-unit appetite.
- [ ] A charter whose query cannot be reconciled with its rule is REPORTED at materialise time rather than resolving quietly - the failure this bug is about is two honest fields disagreeing with nothing to notice it.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Created via `new` (deterministic) |
