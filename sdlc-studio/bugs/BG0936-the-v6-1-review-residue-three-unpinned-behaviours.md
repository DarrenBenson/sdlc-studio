# BG0936: The v6.1 review residue: three unpinned behaviours, a dropped seats entry, a slow note parser and two TRD rows nothing writes

> **Status:** In Progress
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, sdlc-studio/trd.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_v61_review_residue.py, changelog.d/BG0936.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py
> **Created:** 2026-10-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-03T13:50:33Z

## Summary

Low findings the v6.1 reviews raised that no unit carries (D0326, D0333): the goal-review test cannot tell the no-file refusal from the fields-file one (BG0933); a non-dict seats entry is silently dropped (BG0933, pre-existing); nothing pins that transcripts are sorted before the newest is picked (BG0932, pre-existing); the note-ratio parser slows quadratically on long punctuation runs, about 2.6 s on 8,000 characters (BG0922); the TRD's .local table lists project-state.json and review-queue.json, which no script writes (US0984).

## Steps to Reproduce

Each is reproduced in its review's evidence (the v6.1 verdicts for BG0933, BG0932, BG0922 and US0984).

## Proposed Fix

Pin the two refusals apart and the transcript sort; refuse or name a non-dict seats entry the way a missing key is named; bound the parser's scan so it is linear; remove or correct the two TRD rows. No new gate.

## Acceptance Criteria

- [ ] **AC1** Given a goal-review run with no fields file and one whose fields file has no seats, then each prints its own refusal, and a seats entry that is not an object is named rather than dropped. Fails on: the current code, which drops it and whose test cannot tell the two refusals apart
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_v61_review_residue.py::V61ReviewResidueTests::test_goal_review_refusals_are_distinct_and_name_a_bad_seat
  - **Verified:** yes (2026-10-03)
- [ ] **AC2** Given a transcript folder whose files list out of time order, when the newest is resolved, then the newest by time is read. Fails on: a mutant returning glob order unsorted
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_v61_review_residue.py::V61ReviewResidueTests::test_the_newest_transcript_is_chosen_by_time
  - **Verified:** yes (2026-10-03)
- [ ] **AC3** Given a goal note holding 8,000 consecutive punctuation characters, when the close checks it, then it finishes in well under a second. Fails on: the current quadratic scan
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_v61_review_residue.py::V61ReviewResidueTests::test_the_note_parser_is_linear
  - **Verified:** yes (2026-10-03)
- [ ] **AC4** Given the TRD's .local table, then every row names a file a shipped script or the harness writes. Fails on: the current project-state.json and review-queue.json rows
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_v61_review_residue.py::V61ReviewResidueTests::test_every_local_row_has_a_writer
  - **Verified:** yes (2026-10-03)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-03 | sdlc-studio | Filed |
