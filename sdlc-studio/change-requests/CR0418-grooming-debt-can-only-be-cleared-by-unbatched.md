# CR-0418: grooming debt can only be cleared by unbatched hand-work outside any unit

> **Status:** Proposed
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Priority:** Medium
> **Type:** Feature
> **Size:** M

## Summary

{{what changes and why}}

## Impact

{{who this affects and what breaks}}

## Detail

Hit planning Sprint 3a. The delivery backlog held 31 Draft stories; 27 carried no `Affects` and
16 held placeholder acceptance criteria. Every `sprint plan` invocation was refused for it -
correctly, and at `--goal design` too:

```text
sprint plan REFUSED: ... lacks: Affects
```

The design rung is the rung whose stated purpose is to produce that grooming. It cannot be
planned until the grooming exists. So the debt has to be cleared by hand, outside any unit, with
no story behind it, no estimate and no review - which is precisely the ad-hoc work the
engagement floor exists to catch. Clearing it this session meant hand-editing 27 artefacts and
splitting a 13-point bug, unbatched.

The gate is deliberately goal-agnostic, and the reasoning in `sprint.py` is sound on its own
terms: "a separate grooming step that nobody runs is doctrine, and doctrine is what gets skipped
under effort pressure". The consequence was not chosen: grooming became the one kind of work the
two-backlog rule cannot see.

## Impact on planning

Any project whose backlog accumulates refined-but-ungroomed stories - which `refine` produces by
design. The larger the backlog, the more unbatched work is required before any plan can be
written, and the more the process rewards not looking.

## Options

**A. Let the design rung plan over ungroomed units.** Make the breakdown gate goal-aware:
`--goal done` refuses, `--goal design` accepts and records grooming as the rung's own output.
Cheapest, and matches what the rung already claims to be. Risk: the escape becomes the habit.

**B. A grooming unit type.** Grooming a tranche becomes a first-class artefact with its own
points and review, so the work is tracked without weakening the plan gate. More machinery.

**C. `refine` refuses to mint an ungroomed story.** Push the cost to the moment of creation.
Cleanest backlog, but makes bulk refinement impractical - and bulk refinement is how a discovery
backlog gets triaged.

Recommend A, with the rung's close required to report how many units it groomed.

## Acceptance Criteria

- [ ] The breakdown gate distinguishes the rung it is gating: an ungroomed batch is refused at `--goal done` and accepted at `--goal design`
- [ ] A design rung's close reports the grooming it produced, so an accepted-but-ungroomed batch cannot close silently
- [ ] The decision between A, B and C is recorded in the decisions ledger before the change lands

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
