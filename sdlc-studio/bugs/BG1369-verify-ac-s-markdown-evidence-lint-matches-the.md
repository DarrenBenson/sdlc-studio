# BG1369: verify_ac's markdown-evidence lint matches the verdicts path as written, so reviews/../reviews/ and a symlink get through

> **Status:** Open
> **Supersedes:** BG1362
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_markdown_evidence_paths.py, changelog.d/BG1369.md, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Evidence:** RUN-01M77177, 2026-11-12: qa-seat-BG1334-r1
> **Created:** 2026-11-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run ten orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-12T13:21:51Z

## Summary

Pre-existing at base: the path is not resolved before matching. Reported non-blocking at review.

## Steps to Reproduce

Run the case the review describes.

## Proposed Fix

Correct the behaviour and pin it.

## Acceptance Criteria

- [ ] **AC1** Given the case the review named, the behaviour matches the documented rule. Fails on: the case as the review probed it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_markdown_evidence_paths.py::MarkdownEvidencePathTests::test_a_dotdot_or_symlinked_verdicts_path_is_prose
- [ ] **AC2** (carried from BG1362) Given the page or output named, its wording states only what the code does. Fails on: the over-claim the review quoted.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-12 | Claude Opus 5.5 (run ten orchestrator) | Filed |
| 2026-11-14 | Claude Opus 5.5 (backlog triage, D0473) | Supersedes BG1362, closed at the backlog triage as a duplicate; its criteria are carried here as AC2 |
