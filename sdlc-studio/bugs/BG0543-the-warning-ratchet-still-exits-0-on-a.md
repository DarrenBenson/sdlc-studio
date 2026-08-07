# BG0543: the warning ratchet still exits 0 on a stale baseline, and its replacement headline contradicts the line below it

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py
> **Evidence:** RUN-01KZCAJX, 2026-08-07, independent delivery review of BG0524, probed through the shipped CLI on a throwaway fixture.
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

BG0524 was filed because `npm run lint:warning-ratchet` printed `clean` on a baseline it could not establish. Its repair changed the words and not the exit code.

Probed through the shipped CLI on a fixture with 3 recorded entries and 0 live: exit 0. AC1 says it exits non-zero and names the state; AC2 says each state exits non-zero. Both are marked `Verified: yes`, and neither verifier touches an exit code - all three tests call `render_ratchet` in-process.

That is the exact defect class the artefact's own preamble records against US0480 AC4, reproduced by the repair for it. This lane sits in the per-commit `npm run lint` chain, so a stale baseline passes every commit.

Second defect, arithmetic: the stale headline interpolates `report['live']` as the recorded count, but that branch is reached only when `stale` is non-empty, where recorded = live + stale. The fixture prints `0 recorded, 3 of them repaired and removable` one line above `3 recorded instance(s) no artefact still carries` - the headline contradicting the next line, which is what this bug exists to repair.

## Steps to Reproduce

1. Build a fixture whose `.validate-warning-baseline.json` records 3 instances the tree no longer carries. 2. `validate.py warning-ratchet`. 3. It names the state STALE and exits 0. 4. Read the headline: it reports 0 recorded, directly above a line reporting 3.

## Proposed Fix

Return non-zero from `cmd_warning_ratchet` for every untrustworthy state, not only for new instances, and assert the EXIT CODE through the command in each test rather than the rendered string in-process. Compute the recorded count as live + stale rather than live.

AC1's declared mutant is also unapplicable - `validate.py` already reads `"ok": not new`, so the criterion names a no-op as its falsifying change, and AC3's declared mutant survives its own suite.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: BG0524 was filed because `npm run lint:warning-ratchet` printed `clean` on a baseline it could not establish.
- [ ] **AC2** The proposed fix lands, pinned by a test: Return non-zero from `cmd_warning_ratchet` for every untrustworthy state, not only for new instances, and assert the EXIT CODE through the command in each test...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Filed |
