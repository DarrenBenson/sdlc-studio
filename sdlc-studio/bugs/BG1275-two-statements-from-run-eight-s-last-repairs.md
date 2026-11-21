# BG1275: Two statements from run eight's last repairs claim more than the code or its tests show

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/engagement_floor.py, .claude/skills/sdlc-studio/scripts/tests/test_confinement.py, .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py
> **Evidence:** run eight (RUN-01M6RZQZ) BG1274 round-2 and BG1273 round-1 QA verdicts, non-blocking findings
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T21:39:18Z

## Summary

BG1274's round-2 review: the `_declared_tokens` docstring says a bracketed note holding a comma yields fragments `_is_file_token` then drops, but a note listing two or more paths keeps a fragment that is counted. BG1273's review: the `engagement_floor.py` allowlist reason in `test_confinement.py` says the hook tests pin that it writes only the message file, but no test asserts that no other file is written.

## Steps to Reproduce

Read `engagement_floor.py` near line 445 and the `engagement_floor.py` entry in `CONFINEMENT_ALLOWLIST`, then run each against a fixture: a note listing two paths, and a `--write-trailers` run that checks every file it touched.

## Proposed Fix

Narrow the docstring to the shapes it holds for, and either add a test that `--write-trailers` writes only the message file or drop that clause from the allowlist reason.

## Acceptance Criteria

- [ ] **AC1** Given an Affects field whose bracketed note lists two paths, when `_declared_tokens` reads it, then the tokens it returns are the ones its docstring says that shape yields. Fails on: the docstring saying the note's fragments are dropped while one is counted.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py::DeclarationIsCheckableTests::test_the_declared_tokens_docstring_holds_for_a_note_listing_two_paths
- [ ] **AC2** Given a fixture repository and a commit message, when `engagement_floor.py` runs with `--write-trailers`, then the message file is the only file whose content changes, as the allowlist reason in `test_confinement.py` says. Fails on: any other file written, or the reason citing a pin that does not exist.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py::CommitMsgCheckTests::test_write_trailers_writes_only_the_message_file

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because only a test or pin is missing on behaviour that is right on every path a user reaches. Docstring and allowlist-reason wording in repo tests; the code behaves correctly and only a further pin is missing. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
