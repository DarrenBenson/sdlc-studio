# BG1260: `init run` and `init guided` exit 1 and leave a half-built project when `.claude` is a regular file, which the base initialised cleanly

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/init.py, .claude/skills/sdlc-studio/scripts/tests/test_init.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_guided_stage_confirm.py, .claude/skills/sdlc-studio/scripts/tests/test_init_claude_not_a_directory.py, changelog.d/BG1260.md
> **Evidence:** run eight (RUN-01M6RZQZ) US1131 review round 1 ([regression] and [new]), and the orchestrator's friction log (R8-F2)
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T20:37:33Z

## Summary

Regression from US1131. Drafting the shipped agent definitions (`AGENT_DEFINITIONS`, `.claude/skills/sdlc-studio/scripts/init.py:75-77`) creates `.claude/agents/`, and where `.claude` is a regular file the `NotADirectoryError` is not caught per file (`init.py:531` in `init run`, `init.py:769` through `_write` in `init guided`, lines at review round 1), so both exit 1 with the tree half written. At `fd1c2b5b` the same project initialised cleanly. The input is rare, the error is reported cleanly and a re-run after moving the file recovers, so the reviewer did not hold the gate. A second gap from the same review: narrowing the unreadable-file check to `INSTRUCTION_FILES` (`init.py:537`) has no test. Widening it back to `AGENT_FILES` passes `test_init.py` and `test_lean_guided_stage_confirm.py`, and then an unreadable definition prints a false 'so the doctrine check can read it' directive and, through the `if not unreadable` guard (`init.py:542`), hides the doctrine offer.

## Steps to Reproduce

In a fixture directory create `.claude` as an empty regular file, then run `init run` and `init guided` against it: each exits 1 reporting `NotADirectoryError`, with the instruction files partly written. At `fd1c2b5b` the same fixture exits 0. For the second gap, make the unreadable-file check at `init.py:537` iterate `AGENT_FILES` and run `test_init.py` and `test_lean_guided_stage_confirm.py`: both stay green.

## Proposed Fix

Catch `OSError` per definition file while drafting `.claude/agents/`, report the definition skipped with its reason, and let the stage finish the instruction files and exit 0 as the base did. Add a test with `.claude` as a regular file for `init run` and `init guided`, and one that an unreadable agent definition neither prints the doctrine-check directive nor hides the doctrine offer.

## Acceptance Criteria

- [ ] **AC1** Given a fixture whose `.claude` is an empty regular file, when `init.py run` runs on it, then it exits 0, writes AGENTS.md, CLAUDE.md and every later scaffold file (the decisions log among them), and reports each agent definition under `.claude/agents/` as skipped with its OSError reason.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_init_claude_not_a_directory.py::ClaudeIsAFileTests::test_init_run_finishes_and_names_each_skipped_definition
  - **Verified:** yes (2026-11-15)
- [ ] **AC2** Given the same fixture, when `init.py guided` drafts its agents stage, then the stage writes the instruction files, exits 0 and names each skipped definition with its reason; with `.claude` absent (the control) both definitions are written.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_init_claude_not_a_directory.py::ClaudeIsAFileTests::test_init_guided_agents_stage_finishes
  - **Verified:** yes (2026-11-15)
- [ ] **AC3** Given an agent definition at `.claude/agents/sdlc-builder.md` that cannot be read and an AGENTS.md without the doctrine, when the agents stage runs, then it prints no 'so the doctrine check can read it' directive for the definition and still offers the doctrine.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_init_claude_not_a_directory.py::ClaudeIsAFileTests::test_an_unreadable_definition_neither_misdirects_nor_hides_the_doctrine_offer
  - **Verified:** yes (2026-11-15)

## Notes

- AC1 must fail on: exit 1 with NotADirectoryError, the decisions log unwritten, or a skip that names no reason
- AC2 must fail on: stage_agents' unguarded mkdir and write (init.py:527-533)
- AC3 must fail on: the unreadable check at init.py:537 iterating AGENT_FILES instead of INSTRUCTION_FILES
- Still true at HEAD: stage_agents (init.py:503-533) and the scaffold's step 4 (init.py:768-772, through `_write` at :710) catch no OSError per file. The last change to init.py is c985273f, the US1131 landing that regressed it.
- The filed criteria were file_finding's derived stubs (truncated with '...', no Verify line) and Affects had no changelog fragment; both replaced.
- Make the definition unreadable without chmod (root ignores mode bits): a directory at the definition's path raises IsADirectoryError on read. A skipped test now reads its criterion red (BG1005), so the test must not skip on any host.
- Which entry point reaches which line: confirm with the fixture rather than the bug's line numbers, which name them the other way round.
- End goal 6 (onboarding never leaves a half-built project).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
| 2026-11-15 | Claude Opus 5.5 (run fourteen grooming, D0479) | Groomed for run fourteen: Affects, criteria with Verify lines, notes |
