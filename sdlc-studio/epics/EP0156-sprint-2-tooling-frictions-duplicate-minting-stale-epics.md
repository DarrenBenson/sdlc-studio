# EP0156: Sprint 2 tooling frictions: duplicate minting, stale epics, lane coupling, attribution, writer keys

> **Status:** Draft
> **Parent:** CR0417
> **Parent:** CR0416
> **Parent:** CR0415
> **Parent:** CR0414
> **Derived Point Total:** 17
> **Parent:** CR0413
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0413. Delivers the work CR0413 requested.

## Story Breakdown

- [ ] [US0413: artifact.py new warns on a near-duplicate title before minting, naming the existing id](../stories/US0413-artifact-py-new-warns-on-a-near-duplicate.md)
- [ ] [US0414: the duplicate check is advisory by default and refusable under --strict, with the escape recorded](../stories/US0414-the-duplicate-check-is-advisory-by-default-and.md)
- [ ] [US0415: a lane detects an epic whose stories a delivered sprint already satisfied and reports it as derivable](../stories/US0415-a-lane-detects-an-epic-whose-stories-a.md)
- [ ] [US0416: the disjointness check treats build tooling and shared config as coupling, not as ordinary files](../stories/US0416-the-disjointness-check-treats-build-tooling-and-shared.md)
- [ ] [US0417: the engagement floor attributes a git add -A commit to every unit it touched, not only those named](../stories/US0417-the-engagement-floor-attributes-a-git-add-a.md)
- [ ] [US0418: a writer's --fields-file accepts metadata keys as well as prose, so one invocation sets both](../stories/US0418-a-writer-s-fields-file-accepts-metadata-keys.md)

## Acceptance Criteria (Epic Level)

- [ ] AC1: `artifact.py new` warns on a probable duplicate at mint, using the same detection as the finding filer
- [ ] AC2: one implementation, not two
- [ ] AC3: a warning, never a refusal
- [ ] AC4: authoring criteria onto a scaffolded artefact does not leave the placeholder behind

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
