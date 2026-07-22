# EP0097: The hygiene check verifies the working model, not just the pointers

> **Status:** Draft
> **Derived Point Total:** 8
> **Parent:** CR0353
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0353. Delivers the work CR0353 requested.

## Story Breakdown

- [ ] [US0295: check_instructions verifies the working model is stated, not only that cross-references exist](../stories/US0295-check-instructions-verifies-the-working-model-is-stated.md)
- [ ] [US0296: A file passing the pointer rules while stating no working model is reported with what is missing](../stories/US0296-a-file-passing-the-pointer-rules-while-stating.md)

## Acceptance Criteria (Epic Level)

- [ ] the check verifies the working model is present, not only the pointers: delivery through stories and sprints, tool-allocated ids and index rows, executable ACs gating Done, and independent review
- [ ] each new rule names the specific missing element and the template section that supplies it, so the finding is actionable without reading the whole template
- [ ] the rules degrade honestly for a project that has deliberately scoped a practice out - a recorded opt-out is reported as such rather than as a defect
- [ ] a fixture AGENTS.md carrying every pointer but no working model FAILS the check, proving the new rules discriminate rather than restating the existing six

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
