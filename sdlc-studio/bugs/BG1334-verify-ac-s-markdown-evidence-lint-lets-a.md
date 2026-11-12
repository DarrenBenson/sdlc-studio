# BG1334: verify_ac's markdown-evidence lint lets a grep over sdlc-studio/reviews/ through once US1011's verdict files sit there, so main fails test_every_escape_found_by_review_is_refused

> **Status:** Open
> **Severity:** High
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, changelog.d/BG1334.md
> **Evidence:** US1000's lane land refused at 2026-11-12 (land-US1000.txt): 2 failed, 2639 passed in test_verify_ac.py; reproduced on main at f8383bbc
> **Created:** 2026-11-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-12T08:31:08Z

## Summary

`lint_markdown_evidence` allows a grep verifier when it can point at a readable non-markdown file the runner reads (`_reads_a_non_markdown_file`, `verify_ac.py`:731). US1011 (b5b12fd2) makes every review brief name a verdict file under sdlc-studio/reviews/verdicts/<unit>/<fp>-<token>.txt, and those files are now in the tree. A .txt verdict file is a reviewer's prose, but the lint counts it as a non-markdown file, so `grep "anything" sdlc-studio/reviews/*` and `grep "anything" sdlc-studio/reviews/` are no longer refused. MarkdownEvidenceLintTests::`test_every_escape_found_by_review_is_refused` runs against the real repository and fails on main, which refuses every commit that selects `test_verify_ac.py` (US1000's land) and the push gate.

## Steps to Reproduce

On main at f8383bbc, run `python3 -m pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py -k test_every_escape_found_by_review_is_refused -q`: two subtests fail (`grep "anything" sdlc-studio/reviews/*` and `grep "anything" sdlc-studio/reviews/`), because sdlc-studio/reviews/verdicts/ holds .txt verdict files.

## Proposed Fix

Count a verdict file the review briefs issue (a file under sdlc-studio/reviews/verdicts/) as prose in the lint's markdown test, in the one helper both the walk and the verdict use, so a grep over review prose stays refused; a directory holding a real non-markdown source file still lets its grep through.

## Acceptance Criteria

- [ ] **AC1** Given the repository with verdict .txt files under sdlc-studio/reviews/verdicts/, when the lint judges `grep "anything" sdlc-studio/reviews/*` and `grep "anything" sdlc-studio/reviews/`, then both are refused, as `test_every_escape_found_by_review_is_refused` requires. Fails on: a .txt file under sdlc-studio/reviews/verdicts/ counted as a non-markdown file the grep reads.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::MarkdownEvidenceLintTests::test_every_escape_found_by_review_is_refused
- [ ] **AC2** Given a fixture directory holding only a verdict-style .txt file under sdlc-studio/reviews/verdicts/, a grep over it is refused; beside it, a positive control directory holding a .py source file lets its grep through. Fails on: every .txt file treated as prose, or the rule decided in two places.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::MarkdownEvidenceLintTests::test_a_verdict_file_is_prose_and_a_source_file_is_not

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-12 | Claude Opus 5.5 (orchestrator) | Filed |
