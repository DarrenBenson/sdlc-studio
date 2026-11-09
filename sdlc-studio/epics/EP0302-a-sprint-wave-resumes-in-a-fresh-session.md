# EP0302: A sprint wave resumes in a fresh session from a bounded on-disk brief

> **Status:** Draft
> **Derived Point Total:** 10
> **Parent:** CR0670
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0670. Delivers the work CR0670 requested.

## Story Breakdown

- [ ] [US1140: The run's next action and a resume brief of at most 8k tokens are derived from disk alone](../stories/US1140-the-run-s-next-action-and-a-resume.md)
- [ ] [US1141: The sprint hands off to a resume brief and resumes from it in a fresh session at the same next action](../stories/US1141-the-sprint-hands-off-to-a-resume-brief.md)
- [ ] [US1142: The sprint reference defines a wave boundary and runs the close in its own fresh session](../stories/US1142-the-sprint-reference-defines-a-wave-boundary-and.md)

## Acceptance Criteria (Epic Level)

- [ ] `sprint.py handoff` writes a resume brief of at most 8k tokens naming the open run, each unit's lane state, in-flight agent ids, pending verdicts and briefs, the run's rulings, known issues and the next action, and a size-budget test refuses a brief over 8k tokens.
- [ ] `sprint.py resume`, started in a fresh session from that brief, reaches the same next action as the session that wrote it: in a fixture run `sprint.py next` prints the same step before and after the hand-off.
- [ ] reference-sprint.md defines a wave boundary (every lane of the wave accepted, none in flight), routes the close through its own fresh session, and `sprint plan --write` names a fresh session as its next step.
- [ ] The sprint entry reads its own session's size through the token meter and, under `sprint.fresh_session: warn|block` (warn by default), names the projected re-read cost when the session holds more than 80k tokens; block refuses, and a fixture shows both.
- [ ] Before and after: on the next sprint the cost anatomy (US1124) reports the orchestrator's average context per call below 150k against run six's 407k, and flags any run above 150k.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | sdlc-studio | Created via `new` (deterministic) |
