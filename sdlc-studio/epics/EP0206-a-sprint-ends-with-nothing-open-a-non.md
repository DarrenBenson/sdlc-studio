# EP0206: A sprint ends with nothing open: a non-stop-ship finding becomes a bug and its story closes pointing at it

> **Status:** Draft
> **Derived Point Total:** 13
> **Parent:** CR0526
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0526. Delivers the work CR0526 requested.

## Story Breakdown

- [ ] [US0625: the doctrine states the rule and the stop-ship judgement is recorded per finding at review time](../stories/US0625-the-doctrine-states-the-rule-and-the-stop.md)
- [ ] [US0626: sprint close and sprint stop refuse while any batch unit is non-terminal, naming each and where its findings went](../stories/US0626-sprint-close-and-sprint-stop-refuse-while-any.md)
- [ ] [US0627: closing a story over a recorded REJECT requires a filed artefact id or an explicit stop-ship ruling](../stories/US0627-closing-a-story-over-a-recorded-reject-requires.md)
- [ ] [US0628: a story closed this way names the bug in its own record](../stories/US0628-a-story-closed-this-way-names-the-bug.md)

## Acceptance Criteria (Epic Level)

- [ ] The doctrine states the rule: a non-stop-ship finding is filed as its own artefact and the story closes pointing at it; a stop-ship finding holds the close
- [ ] `sprint close` and `sprint stop` REFUSE while any batch unit is in a non-terminal status, naming each one and the artefact its findings moved to - the refusal is what makes the rule real rather than remembered
- [ ] Closing a story over a recorded REJECT requires the finding to have somewhere to live: a filed artefact id, or an explicit stop-ship ruling that holds the close instead
- [ ] The stop-ship judgement is recorded per finding at review time rather than inferred at the close, so the close reads a decision somebody made instead of making one for them
- [ ] A story closed this way names the bug in its own record, so a reader of the story learns where the work went without consulting the retro

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
