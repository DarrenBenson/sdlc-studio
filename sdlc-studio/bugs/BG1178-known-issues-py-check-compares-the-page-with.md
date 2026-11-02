# BG1178: known_issues.py check compares the page with the corpus but never reads the release notes' count sentence, so a hand edit of that line goes unchecked until the tag

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/known_issues.py, tools/tests/test_known_issues.py, changelog.d/BG1178.md
> **Created:** 2026-11-02
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-02T21:06:19Z

## Summary

Found by US1111's review (2026-11-02). `known_issues.py check` (tools/`known_issues.py`:406-410) judges docs/known-issues.md against the bug corpus only. The notes' `**vX.Y.Z discloses N open defects: ...**` line is written by `write` but never read back, so a working-tree edit to 174/56/118 passed the live check, AC2's test and the notes test.

## Steps to Reproduce

1. Edit the count line in docs/release-notes-v6.2.0.md.
2. Run `python3 tools/known_issues.py check`: exit 0.

## Proposed Fix

Have `check` also compare the current release's count line with the page's figures.

## Acceptance Criteria

- [ ] **AC1** `known_issues.py check` exits 1 when the current release notes' count line disagrees with the page.
  - **Verify:** pytest tools/tests/test_known_issues.py

## Impact

A release can ship notes whose open-defect count disagrees with its own disclosure page.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-02 | claude | Filed |
