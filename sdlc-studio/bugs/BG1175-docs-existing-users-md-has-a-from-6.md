# BG1175: docs/existing-users.md has a From 6.0 to 6.1 section but none for 6.1 to 6.2, so the upgrade page stops one release short

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** docs/existing-users.md, changelog.d/BG1175.md
> **Evidence:** docs/existing-users.md:52 at c9e1a9c3.
> **Created:** 2026-11-02
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-02T09:14:35Z

## Summary

2026-11-02, found by US1110's builder. docs/existing-users.md, the upgrade page, carries '### From 6.0 to 6.1' (line 52) and no section for 6.2. The 6.2.0 release notes carry the whole 6.1 upgrade path themselves (reinstall, `migrate`, `migrate --apply`, the lessons log), so a 6.1 user who starts from the notes is served, but one who starts from the upgrade page is told nothing about 6.2.

## Steps to Reproduce

1. `grep -n '^### From' docs/existing-users.md`.
2. See 6.0 to 6.1 and nothing later.

## Proposed Fix

Add a 'From 6.1 to 6.2' section that links the 6.2.0 notes' upgrade section, giving the same commands.

## Acceptance Criteria

- [ ] **AC1** docs/existing-users.md has a section for upgrading from 6.1 to 6.2 that links docs/release-notes-v6.2.0.md, and `tools/check_links.py` passes.
  - **Verify:** shell grep -qE '^### From 6\.1 to 6\.2' docs/existing-users.md && grep -q 'release-notes-v6.2.0.md' docs/existing-users.md && python3 tools/check_links.py

## Impact

A 6.1 user reading the upgrade page rather than the notes misses the 6.2 steps.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-02 | claude | Filed |
