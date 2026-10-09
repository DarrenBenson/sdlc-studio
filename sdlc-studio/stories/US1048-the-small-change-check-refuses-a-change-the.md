# US1048: The small-change check refuses a change the path does not fit, naming every reason at once

> **Status:** Draft
> **Delivers:** CR0626
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/small_change.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/reference-scripts.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/tests/test_small_change_disqualifiers.py, changelog.d/US1048.md
> **Epic:** EP0286
> **Points:** 5
> **Depends on:** US1047
> **Persona:** Maya Okafor

## User Story

**As** a team lead whose people and agents each fast-track fixes their own way
**I want** one check that says whether a change may take the small path and, if not, every reason why
**So that** the tool draws the line between a small change and a sprint, the same for everyone

## Acceptance Criteria

- **AC1:** Given a bug whose Affects names one existing production file and one production file not yet created, when `small_change.py check --unit` runs, then it exits non-zero naming both files and the limit of one.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_small_change_disqualifiers.py::SmallChangeDisqualifierTests::test_more_production_files_than_the_limit_is_refused
- **AC2:** Given three units, one whose Affects matches a `small_change.protected` glob, one matching `review.spec_paths`, and a story whose `Affects production runtime` is true, when `small_change.py check` runs on each, then each exits non-zero naming its own reason: the path and glob, or the field.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_small_change_disqualifiers.py::SmallChangeDisqualifierTests::test_each_protected_surface_is_refused
- **AC3:** Given three units, one an open run's batch holds, one declaring a file an open run's batch unit also declares, and one checked while a run awaits signature, when `small_change.py check` runs on each, then each exits non-zero naming the run, with the shared file or the report awaiting signature.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_small_change_disqualifiers.py::SmallChangeDisqualifierTests::test_each_collision_with_a_run_is_refused
- **AC4:** Given a unit that fails three conditions, when `small_change.py check` runs, then all three reasons print in one pass and nothing is written, and `small_change.py start` refuses the same unit with the same reasons.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_small_change_disqualifiers.py::SmallChangeDisqualifierTests::test_every_reason_is_named_in_one_pass_by_both_verbs
- **AC5:** Given a started small change with an uncommitted edit to a production file its Affects does not name, when `small_change.py check` runs, then it exits non-zero saying the change no longer qualifies, naming the file.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_small_change_disqualifiers.py::SmallChangeDisqualifierTests::test_a_change_that_outgrew_its_declaration_no_longer_qualifies

## Notes

- Release: 6.2 (D0355 breakdown G12, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the count reads only paths revert-check can revert, so a fix that creates a second module is under-counted; or tests and markdown are counted as production.
- AC2 must fail on: any one of the three readings is dropped; the test asserts each arm, so a mutant that keeps the configured list and drops the runtime field fails.
- AC3 must fail on: any one of the three run checks is dropped; the test asserts each arm, so the change could land inside a run whose close or sign then refuses a moved tree.
- AC4 must fail on: the check returns at the first failing condition, or start runs a different predicate from check.
- AC5 must fail on: check reads only the declared Affects, or only committed history since the base, so a change that grew past one file keeps the path.
- The disqualifiers are published as one module constant, each with its key and the sentence it prints. The docs story's page is checked against that constant both ways (LL0043). The terminal story re-runs this same predicate (panel change 2).
- Derived, not judged (LL0034). The production-file count reuses `verify_ac.revert_targets`, counting its `unresolvable` paths (not yet created) as production (panel answer Q2). The run checks read `run_state` and each batch unit's Affects, and `run_state.awaiting_signature`. The protected list is the project's recorded judgement.
- The diff since the base covers committed and uncommitted changes, against the recorded `Small-change` base.
- Config: `small_change.max_production_files: 1` and `small_change.protected: []` in config-defaults.yaml, documented in reference-config.md. When the list is empty, the output says no protected surfaces are configured rather than reading as clear (LL0008).
- `Affects production runtime` exists on the story template only (templates/core/story.md:177), so for a bug only the globs and `review.spec_paths` apply; the page says so.
- Glob matching uses spec_guard's rule, which `review.spec_paths` already uses, so one pattern means one thing.
- Not read: Points, which the author writes, and the derived tier, which reads the file rather than the change (see out of scope).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G12 after the refine panel's review |
