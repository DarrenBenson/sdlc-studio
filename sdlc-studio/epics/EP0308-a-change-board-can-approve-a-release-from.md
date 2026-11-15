# EP0308: A change board can approve a release from one evidence pack built from the run's committed record, naming who is accountable for each change

> **Status:** Draft
> **Derived Point Total:** 5
> **Parent:** CR0692
> **Created:** 2026-11-14
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0692. Delivers the work CR0692 requested.

## Story Breakdown

- [x] [US1155: One command writes a release's evidence pack from committed records](../stories/US1155-one-command-writes-a-release-s-evidence-pack.md)
- [ ] [US1156: Each change in the pack states what is known wrong and names the accountable person, never the agent](../stories/US1156-each-change-in-the-pack-states-what-is.md)

## Acceptance Criteria (Epic Level)

- [ ] One command writes a release's evidence pack from committed records only: the signed reports, verdicts, verify runs, known issues and the accountable person for each unit in the release
- [ ] Each change in the pack states what changed, which criteria passed, who reviewed it independently, what is known to be wrong, and the accountable person, never 'the agent'
- [ ] The pack groups changes by each unit's risk and compliance class (D0459), lists high-risk changes first, and states for each high-risk change its second review seat's verdict (D0460)
- [ ] The pack reads without running the tool, and the companion dashboard can read it through the versioned evidence annex (EP0275)

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-14 | sdlc-studio | Created via `new` (deterministic) |
