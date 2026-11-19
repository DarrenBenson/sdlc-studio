# BG1593: tools/check_links.py does not read docs/enterprise.md, so a broken link or anchor on the page exits 0

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/check_links.py, tools/tests/test_check_links.py, changelog.d/BG1593.md
> **Evidence:** sdlc-studio/reviews/verdicts/US1317/60b1992c5231-2634e155.txt, finding 5 (pre-existing).
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T16:19:28Z

## Summary

The qa review of US1317 found that lint:links (tools/`check_links.py)` skips docs/enterprise.md: a link to a missing file, an anchor typo and a typo in a sibling page's anchor all exit 0 on an isolated export. The checker's page list predates the page; docs/harnesses.md is likely skipped the same way.

## Steps to Reproduce

Add a link to a missing file in docs/enterprise.md and run `python3 tools/check_links.py`: it exits 0.

## Proposed Fix

Have `check_links.py` read every page under docs/ (or derive its list from the tree), with a test that a broken link on a new docs page fails.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: The qa review of US1317 found that lint:links (tools/`check_links.py)` skips docs/enterprise.md: a link to a missing file, an anchor typo and a typo in a...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Add a link to a missing file in docs/enterprise.md and run `python3 tools/check_links.py`: it exits 0.
- [ ] **AC3** The proposed fix lands, pinned by a test: Have `check_links.py` read every page under docs/ (or derive its list from the tree), with a test that a broken link on a new docs page fails.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
