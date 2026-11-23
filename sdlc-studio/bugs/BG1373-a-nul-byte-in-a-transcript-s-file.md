# BG1373: A NUL byte in a transcript's file path makes critic.py record refuse the unit

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/verdict_provenance.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_self_review_by_context.py, changelog.d/BG1373.md
> **Evidence:** RUN-01M77177, 2026-11-12: qa-seat-US1015-r1
> **Created:** 2026-11-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run ten orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-12T13:22:13Z

## Summary

US1015's self-review check reads Edit and Write paths from the session's transcripts. A path
holding a NUL character raises `ValueError` out of `Path(value).resolve()`, in `_affected`
(verdict_provenance.py:392, the Affects edit scan) and in `_names` (verdict_provenance.py:238,
the verdict writer scan), and `critic.py record` refuses the unit instead of skipping that record.
The module's own rule is that a bad record costs only itself. Reported non-blocking at review
(sdlc-studio/reviews/verdicts/US1015/036a5e68b39b-195965f1.txt).

## Steps to Reproduce

1. In a throwaway project with US0001 (`Affects: src/unit.py`), issue a brief, write the verdict
   block, and build a transcript (the `SelfReviewByContextTests` fixture) whose context first
   calls Edit with `file_path` set to `<root>/src/unit.py` followed by a NUL, then writes the
   verdict file.
2. Run `critic.py record` for that brief.
3. Repeat with no NUL Edit, but a Write whose `file_path` is the verdict path followed by a NUL,
   before the real write of the verdict.

Measured at HEAD 3791e5193: both runs exit 2 with `record refused for US0001: lstat: embedded null
character in path`, and no row is written.

## Proposed Fix

Resolve a transcript path through one guard that returns None on `ValueError` or `OSError`, used
by `_affected` and `_names`, so a record whose path cannot be resolved is skipped and the scan
goes on to the next record.

## Acceptance Criteria

- [ ] **AC1** Given a transcript whose recording context's only Edit names `src/unit.py` with a NUL appended, when `critic.py record` records US0001's verdict, then it exits 0, the row is written, and the row is independent (the NUL record is skipped). Fails on: HEAD (measured: exit 2, `lstat: embedded null character in path`, no row).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_review_by_context.py::SelfReviewByContextTests::test_a_nul_path_in_a_transcript_is_skipped
- [ ] **AC2** Given the same NUL Edit followed by a clean Edit of `src/unit.py` before the brief, when the verdict is recorded, then the row's Source carries `self-review:src/unit.py`. Fails on: a fix that abandons the transcript, or the whole check, at the first path it cannot resolve.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_review_by_context.py::SelfReviewByContextTests::test_a_nul_path_does_not_hide_a_later_edit_of_the_unit
- [ ] **AC3** Given a Write whose `file_path` is the verdict path with a NUL appended, before the context's real write of the verdict, when the verdict is recorded, then it exits 0 and the writer is found from the real write. Fails on: HEAD's `_names` (measured: the same refusal, no row).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_review_by_context.py::SelfReviewByContextTests::test_a_nul_path_beside_the_verdict_write_is_skipped

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-12 | Claude Opus 5.5 (run ten orchestrator) | Filed |
| 2026-11-23 | Sam Eriksson (qa) | Groomed for run twenty-four: reproduced at HEAD through `critic.py record` at both resolve sites (`_affected` and `_names`); the placeholder criterion, whose Verify named a class that does not exist (`SelfReviewTests`), replaced by three executable ones in `SelfReviewByContextTests`, a control among them; Steps and Proposed Fix written from the review's finding |
