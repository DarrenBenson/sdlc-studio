# BG1570: The evidence pack trusts the run record as committed at the build revision, so one commit that edits a report's figures, its signature and its run record together still passes

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/evidence_pack.py, .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_build.py
> **Evidence:** Found by the run sixteen builder of BG1524 and US1292, 2026-11-17.
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T23:01:38Z

## Summary

BG1524 (run sixteen) makes the evidence pack check that a report's signature binds the page it signs. The pack reads the run record from the tree at the revision it builds from, not from the history that wrote it, so a single later commit that rewrites the report's figures, re-enters the signature block and edits the run record to match is accepted as signed. The signature is only as strong as the record it is compared against, and that record is as editable as the page.

## Steps to Reproduce

1. Take a signed report and its run record. 2. In one commit, change a figure on the page, update the signature block's fingerprint and the run record to agree. 3. Build the evidence pack at that commit.

## Proposed Fix

Compare the signature against the run record as it stood at the seal commit (`git show <seal>:<record>`), and refuse a pack whose report or record changed after the seal without a recorded amendment.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: BG1524 (run sixteen) makes the evidence pack check that a report's signature binds the page it signs.
- [ ] **AC2** The proposed fix lands, pinned by a test: Compare the signature against the run record as it stood at the seal commit (`git show <seal>:<record>`), and refuse a pack whose report or record changed...

## Impact

A change board reading the pack as proof that the signed figures are the ones the operator signed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
