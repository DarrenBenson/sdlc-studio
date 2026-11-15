# BG1478: SECURITY.md's Supported Versions table lists 4.x as current and 3.x as security-only, though the current major is 6

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** SECURITY.md, tools/tests/test_security_policy_versions.py, changelog.d/BG1478.md
> **Evidence:** Run fourteen, US1163's builder hand-back, 2026-11-15.
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T20:47:04Z

## Summary

SECURITY.md says support tracks the current major, restated at each major release, but its table still reads 4.x Yes, 3.x security fixes only, older No. The current release is 6.3.0, so a head of engineering reading the policy is told 6.x and 5.x are unsupported. It was never restated at the 5.0 or 6.0 release. SUPPORT.md (US1163) makes no version claim because of it.

## Steps to Reproduce

Read SECURITY.md's Supported Versions table and compare it with the latest release tag.

## Proposed Fix

Restate the table for 6.x (Yes) and 5.x (security fixes only), and add a test that the table's current major matches the version the skill reports, so the next major cannot leave it stale.

## Acceptance Criteria

- [ ] **AC1** Given SECURITY.md and the skill's current version, when the Supported Versions table is read, then its first row names the current major as supported and the row below it the previous major as security fixes only. Fails on: a table naming any older major as current.
  - **Verify:** pytest tools/tests/test_security_policy_versions.py

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Filed |
