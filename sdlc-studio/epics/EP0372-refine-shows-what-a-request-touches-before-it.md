# EP0372: Refine shows what a request touches before it becomes stories

> **Status:** Draft
> **Derived Point Total:** 6
> **Parent:** CR0735
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0735. Delivers the work CR0735 requested.

## Story Breakdown

- [ ] [US1305: The repo map answers which files import a given file and which symbols closely match a given symbol, by a stated rule](../stories/US1305-the-repo-map-answers-which-files-import-a.md)
- [ ] [US1306: `refine apply` reports each story's uncovered dependants and near-duplicate symbols without changing its exit code or output, and says when the map is absent or stale](../stories/US1306-refine-apply-reports-each-story-s-uncovered-dependants.md)

## Acceptance Criteria (Epic Level)

- [ ] `refine apply --dry-run` and `apply` print, for each story, the files that import a file in its Affects and appear in no story's Affects in the same breakdown
- [ ] They print any symbol outside the story's Affects whose name and parameter list closely match a symbol inside them, by a rule the help page states
- [ ] The report never changes the exit code or the stories written, and says so when the repo map is absent or stale instead of printing nothing

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
