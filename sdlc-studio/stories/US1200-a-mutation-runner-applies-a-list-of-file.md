# US1200: A mutation runner applies a list of file edits in a scratch copy and prints one verdict line for each

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0673
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation_runner.py
> **Epic:** EP0327
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** A mutation runner applies a list of file edits in a scratch copy and prints one verdict line for each
**So that** CR0673 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: Each listed edit gets one verdict line

- **Given** a scratch repository with a unit, and a JSON list of two `{file, old, new, test}` entries, one a test catches and one no test catches
- **When** the list is handed to the `mutation.py` runner entry point for that unit
- **Then** it prints exactly one line per mutant, in list order, naming the entry, `killed` or `survived` and the last line of the named test's output, and writes a report holding the same verdicts and the full mutant list. Fails on: a survivor reported as killed because the test failed for another reason before the edit was applied, or several lines per mutant
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation_runner.py::MutationRunnerTests::test_each_edit_gets_one_line_with_its_verdict_and_the_tests_last_line

### AC2: The edits run in a scratch copy and the working tree is never touched

- **Given** the same list, with one entry whose named test itself rewrites the mutated file
- **When** the runner is run, and is interrupted with SIGTERM during a second run
- **Then** every file of the working tree is byte-identical before and after both runs and `git status` is unchanged; in the scratch copy each file is restored after its mutant and its bytes checked, and a file that does not restore stops the run naming it. Fails on: an edit applied in the author's working tree, or one mutant's edit left in place for the next
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation_runner.py::MutationRunnerTests::test_the_working_tree_is_byte_identical_after_a_run_and_an_interrupt

### AC3: An edit that cannot be applied is reported, never counted as killed

- **Given** a list with an entry whose `old` text is absent from its file, one whose `old` occurs twice, one naming a file outside the unit's Affects, and a file that is not a JSON list
- **When** the runner is run on each
- **Then** the absent, the ambiguous and the out-of-scope entries are each reported as not applied with the reason and are in neither the killed nor the survived count, the other entries of the list still run, and the malformed file is refused at exit 2 with nothing run. Fails on: an unapplied edit reported as killed, which would record a mutation pass that never ran
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation_runner.py::MutationRunnerTests::test_an_edit_that_does_not_apply_is_reported_and_not_counted

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
