# BG1177: README's 6.2.0 line and the notes' theme heading say a reviewer judges only self-checked work, though the shipped default only reports a missing self-check

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** README.md, docs/release-notes-v6.2.0.md, tools/tests/test_lean_release_notes_v62.py, changelog.d/BG1177.md
> **Created:** 2026-11-02
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-02T21:04:53Z

## Summary

Found by US1111's review (2026-11-02). README.md:474 calls 6.2.0 the release where 'a reviewer judges only work its author has self-checked', and docs/release-notes-v6.2.0.md:12 heads its first theme the same way. But `review.author_self_check` ships as `report` (templates/config-defaults.yaml:87), and under `report` `critic.py brief` still prints the brief with a notice (critic.py:3113-3114). Only `block` refuses it. The notes' body and their opening line qualify it. The README line does not.

## Steps to Reproduce

1. Read README.md:474.
2. On a fresh project, run `critic.py brief --unit <id> --seat qa` with no self-check recorded: the brief prints.

## Proposed Fix

Word the README line and the theme heading as the notes' opening line does: a review brief can now require the author's own check first.

## Acceptance Criteria

- [ ] **AC1** README's release-notes line and the notes' first theme say a brief CAN require the author's self-check, not that every review judges only self-checked work.
  - **Verify:** pytest tools/tests/test_lean_release_notes_v62.py

## Impact

A reader of the front page believes self-checks are enforced by default.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-02 | claude | Filed |
