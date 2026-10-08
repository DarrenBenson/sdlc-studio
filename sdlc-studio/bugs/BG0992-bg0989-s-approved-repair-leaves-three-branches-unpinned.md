# BG0992: BG0989's approved repair leaves three branches unpinned, and its docs over-claim which commands move the legacy lessons log

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_lessons_log_committed.py, .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/reference-agentic-lessons.md, .claude/skills/sdlc-studio/help/lessons.md, .claude/skills/sdlc-studio/scripts/tests/test_lessons_log_followups.py, .claude/skills/sdlc-studio/scripts/tests/test_lessons.py
> **Evidence:** BG0989 round-2 QA APPROVE, 2026-10-08 (critic-verdicts.md), mutants N3-N5.
> **Created:** 2026-10-08
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-08T08:13:48Z

## Summary

The round-2 QA review of BG0989 approved it and recorded these as non-blocking. Three branches have no test that fails without them: prune's removal of a pruned lesson's hard-wrapped continuation lines (lessons.py `drop_from_summary)`, the gist alternative in the summary guard's `same` (a retitled lesson with a gist is held), and carry and violated refusing when both logs exist (the both-logs refusal is pinned only through add and retro extract). The guard's docstring says a retitled lesson is still the same lesson, which holds only when it has a gist; every retro-extracted and plain `lessons add` lesson is gist-less, and is refused (fail-closed, so only the sentence is wrong). The gist alternative also counts a different lesson as held when it reuses both a listed id and its gist, low risk because any other missing lesson still stops the guard. And the changelog fragment, reference-agentic-lessons.md and help/lessons.md say any or the first `lessons` command moves a legacy log, without the `--global` exception AC2 states.

## Steps to Reproduce

Apply each mutant the reviewer named (N3: drop the continuation-line removal, N4: drop the gist alternative, N5: take carry and violated out of `_PROJECT_TIER_VERBS`) and run `test_lessons_log_committed.py`: all pass. `lessons list --global` on a legacy-only project leaves the legacy log in place.

## Proposed Fix

Add the three tests, each with its named mutant; say in the docstring that a gist-less retitled lesson is refused; decide whether the gist alternative needs the title to share a stem too; add the `--global` exception to the three doc sentences.

## Acceptance Criteria

- [ ] **AC1** A wrapped summary pruned then regenerated is pinned by a test that fails when the continuation-line removal is dropped
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons_log_followups.py -k prune_drops_wrapped_lines
- [ ] **AC2** A retitled lesson with a gist is pinned as held, and a gist-less retitled one as refused, each by a test
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons_log_followups.py -k retitled_lesson
- [ ] **AC3** carry and violated each refuse a project holding both logs, pinned by a test
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons_log_followups.py -k carry_and_violated_refuse_two_logs
- [ ] **AC4** Every doc sentence about which command moves the legacy log names the --global exception
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons_log_committed.py -k remedy_and_docs_name_the_committed_path

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-08 | sdlc-studio | Filed |
