# EP0333: An author's self-check proves each criterion at its observable before a reviewer is briefed

> **Status:** Draft
> **Derived Point Total:** 14
> **Parent:** CR0682
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0682. Delivers the work CR0682 requested.

## Story Breakdown

- [ ] [US1220: Self-check record runs one shipped command for each criterion and stores its exit and an output digest](../stories/US1220-self-check-record-runs-one-shipped-command-for.md)
- [ ] [US1221: The self-check lists the documents outside Affects that name what the diff changed and needs a ruling on each](../stories/US1221-the-self-check-lists-the-documents-outside-affects.md)
- [ ] [US1222: Story and bug templates take a Capture line, and a lint flags a reader of another tool's output without one](../stories/US1222-story-and-bug-templates-take-a-capture-line.md)
- [ ] [US1223: Critic record takes a defect class on each blocking finding and the sprint report counts blockers by class](../stories/US1223-critic-record-takes-a-defect-class-on-each.md)

## Acceptance Criteria (Epic Level)

- [ ] The self-check lists each criterion with its quoted observable, CLAIMS.json carries one claim per criterion whose command invokes a shipped CLI rather than only a pytest selector, and `self-check record` re-runs each command once and stores its exit and an output digest; a fixture of US1119's dropped-warning case is ruled FALSE.
- [ ] `_self_check_scope` greps `reference-*.md`, `help/*.md` and README.md outside Affects for the basenames of changed scripts and the long flags the diff adds or removes, prints the hits as docs that name what changed, and `check_self_check` requires a ruling for each; a fixture reproduces BG1236's stale reference-sprint.md line.
- [ ] Story and bug templates gain an optional `Capture:` line (producer, version, recorded sample path), refine asks for it when a unit reads another tool's output, and a lint flags a unit whose Affects names a `meter_*.py` or `*_hook.py` reader without one.
- [ ] `critic.py record` accepts a defect class after the origin tag (sweep-red, vacuous-pin, proxy-observable, unstated-invariant, external-format, doc-drift, other), and the sprint report's unit table and the retro digest count round-1 blockers by class.
- [ ] Before and after: with the sweep-lane, mutation-runner and hostile-kit CRs landed, the next two sprints put at most 20% of units in a second review round.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
