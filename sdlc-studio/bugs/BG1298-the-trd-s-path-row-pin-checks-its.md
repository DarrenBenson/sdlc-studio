# BG1298: The TRD's path-row pin checks its depth rule in one direction only, so loosening `_matches` to accept the directory itself or a deeper file leaves the suite green

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_lean_v61_review_residue.py, changelog.d/BG1298.md
> **Evidence:** US1138 round-2 verdict (qa-seat-US1138-r1) at 7961ea8b, the two loosening mutants
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-09T00:06:44Z

## Summary

From US1138's round-2 review (qa-seat-US1138-r1, non-blocking). `_matches` at .claude/skills/sdlc-studio/scripts/tests/`test_lean_v61_review_residue.py`:629 is correct today, and the recorded tightening mutant (a slash span demanding exact length) is killed. The two loosening mutants each survive the whole module alone (10 passed, 104 subtests): a span ending in `/` accepting a write to the directory itself (`>` to `>=`), and a file span accepting a deeper path (`==` to `>=`). The fixture meant for the first, "the directory alone" near :1090, creates the directory with `mkdir`, which `_written` does not count as a write (`_PATH_WRITE_METHODS` at :112 is `write_text` and `write_bytes`), so that case is false whatever `_matches` says. A later edit could loosen the TRD's rule that a path ending in `/` stands for a file inside it (sdlc-studio/trd.md:611-612) with the suite still green.

## Steps to Reproduce

Change `>` to `>=` in `_matches`'s slash-span branch, or `==` to `>=` in its file-span branch, and run `python3 -m pytest -q .claude/skills/sdlc-studio/scripts/tests/test_lean_v61_review_residue.py`: 10 passed.

## Proposed Fix

Make the directory-alone fixture write with `write_text` to the directory's own path (so `_written` reads it as a write), and add a fixture writing a file one level deeper than a file span names. Each must fail its loosening mutant.

## Acceptance Criteria

- [ ] **AC1** Given a fixture module that writes with `write_text` to the directory's own path under a span ending in `/`, when the path-row pin judges it, then the write is not that span's. Fails on: `_matches` loosened from `>` to `>=` in its slash-span branch with the module still green.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_v61_review_residue.py::LocalPathRowPinTests::test_a_write_to_the_directory_itself_is_not_a_slash_spans
- [ ] **AC2** Given a fixture module that writes a file one level deeper than a file span names, when the path-row pin judges it, then the write is not that span's, while a write at the span's own depth still is. Fails on: `_matches` loosened from `==` to `>=` in its file-span branch with the module still green.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_v61_review_residue.py::LocalPathRowPinTests::test_a_file_one_level_deeper_is_not_a_file_spans

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because only a test or pin is missing on behaviour that is right on every path a user reaches. The path-row depth rule is correct today; two loosening mutants survive only because this repository's pin tests one direction. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
