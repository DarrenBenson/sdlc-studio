# EP0312: The commit hook runs the cheap repo-wide sweeps on every commit and refuses a new test module with no census marker

> **Status:** Draft
> **Derived Point Total:** 5
> **Parent:** CR0671
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0671. Delivers the work CR0671 requested.

## Story Breakdown

- [x] [US1167: A test module or class marked `# test-selection: sweep` joins every commit's selection, within a 30-second budget](../stories/US1167-a-test-module-or-class-marked-test-selection.md)
- [ ] [US1168: The commit hook refuses a staged new test module with no `test-census-subject` marker](../stories/US1168-the-commit-hook-refuses-a-staged-new-test.md)

## Acceptance Criteria (Epic Level)

- [ ] A test module can declare `# test-selection: sweep`, and `gate.select_tests` adds every sweep module to each commit's selection while their recorded total run time stays within a 30 s budget; a test pins that a change to scripts/sprint.py now selects `test_doc_claims.py.`
- [ ] `test_doc_claims`, `test_precommit_floor_pending`, `test_root_census`, the `test_skill_tests_env` scrub sweep, the `test_gitutil` raw-git sweep and the commit-hook hermeticity test carry the marker, and the RealRepoTests of `test_test_census.py` stay at the push gate.
- [ ] A pre-commit lane refuses a staged new test module whose head has no `test-census-subject` marker, naming the marker to add, and passes a module that carries one.
- [ ] Replayed in a throwaway clone, the run-six commits that turned `test_doc_claims.py` and `test_precommit_floor_pending.py` red, and the landings BG1236 later repaired, are each refused at commit by the sweep lane.
- [ ] Before and after: the next sprint's report shows no round-1 blocking finding of the sweep-red class and no unit added for a push-gate sweep red.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Created via `new` (deterministic) |
