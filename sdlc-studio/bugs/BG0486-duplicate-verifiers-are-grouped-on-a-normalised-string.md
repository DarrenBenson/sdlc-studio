# BG0486: duplicate verifiers are grouped on a normalised string, so two ACs running the same command can read as distinct

> **Status:** Fixed
> **Verification depth:** functional (measured over the real corpus: 31 duplicate AC-partitions before and after, none gained or lost, so the regrouping's yield here is ZERO - the discriminating power was demonstrated on constructed pairs instead; the first measurement compared group COUNTS and was misleading, showing 24 'new' groups that were a renaming; ratchet staleness measured identical at HEAD, so it is pre-existing; mutation: 3 declared mutants, all KILLED, restore byte-exact)
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Carved out of BG0433, whose other two halves are delivered. The duplicate-verifier ratchet groups on a NORMALISED STRING rather than on the resolved argv, so two criteria that run the identical command can be grouped apart when their spelling differs - a different runner prefix, a reordered flag, an extra `-q`. The ratchet then reports no duplicate where one exists, which is the failure the whole lane is for: two ACs sharing a selector cannot both discriminate, and a regression in either fails both while neither says which.

Not delivered alongside the other halves deliberately. Regrouping reshapes the very baseline BG0433 just brought under the shrink guard, and doing both in one step would leave neither measurable - the new grouping's yield could not be told from the reader fix's.

## Steps to Reproduce

1. Author two ACs whose Verify lines resolve to the same command with different spelling (e.g. `pytest x.py::T::t` and `python3 -m pytest x.py::T::t`).
2. Run the ratchet; the pair is not reported as a duplicate group.

## Proposed Fix

Group on the RESOLVED argv the runner would execute, not on the written string. Re-baseline afterwards and record the before/after group count, so the regrouping's effect is a measured number rather than an assertion.

## Acceptance Criteria

- [x] **AC1** Given two criteria whose Verify lines resolve to the same command in different words - a flag ordered differently, a `-q` the runner supplies anyway - when the duplicate scan runs, then they are ONE group rather than a group of one under each spelling.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py -k dup_group_key_resolves
  - **Verified:** yes (2026-08-15)
- [x] **AC2** Given a duplicate group, when it is reported, then it names the command as the AUTHOR WROTE it, and lists any other spelling in the group beside it - the resolved argv is an internal key and appears in nobody's file.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py -k dup_group_reports_the_written_form
  - **Verified:** yes (2026-08-15)
- [x] **AC3** Given two criteria naming genuinely different selectors, when the scan runs, then they stay apart - the key decides what counts as the same command, and over-merging would hide a real pair of distinct criteria.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py -k two_different_selectors_are_not_merged
  - **Verified:** yes (2026-08-15)

## Resolution

Grouped on the resolved argv rather than the written string, and REPORTED as the author wrote it. Those are two different identities and conflating them was the trap: quoting a resolved command back at an author names a line that appears nowhere in their file, which is what the burndown tests were protecting.

**The regrouping's yield on this corpus is ZERO, and that is the number the bug asked for.** Every duplicate partition is identical before and after - 31 groups, none gained, none lost - because no unit here currently spells one command two ways. The discriminating power is real and was demonstrated on constructed pairs (`pytest x` versus `pytest -q x`, and the same flags in a different order, both now one group; two different selectors still apart). What changed is that the guard is now correct for the case it claims to cover, not that it found anything today.

The first measurement of this was misleading and is worth recording: comparing GROUP COUNTS showed 31 to 31 with "24 newly detected pairs", which looked like a large yield and was a renaming - the keys changed, the partition did not. Comparing the AC partitions instead gave the true answer.

No baseline churn either: baseline keys are normalised through `dup_group_key` on the way in, so stored entries re-normalise to the new form on read. The 16 stale entries the ratchet reports are pre-existing - measured identical at HEAD - and are a burndown owed by earlier work, not by this change.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in verify_ac.py `dup_group_key`, return the written form so two spellings group apart | Given two criteria whose Verify lines resolve to the same command in different words - a flag ordered differently, a `-q` the runner supplies anyway - when the duplicate scan runs, then they are ONE group rather than a group of one under each spelling. |
| AC2 | in verify_ac.py `duplicate_verifiers`, report the resolved key instead of the author's line | Given a duplicate group, when it is reported, then it names the command as the AUTHOR WROTE it, and lists any other spelling in the group beside it - the resolved argv is an internal key and appears in nobody's file. |
| AC3 | in verify_ac.py `dup_group_key`, key on the runner alone so every selector merges | Given two criteria naming genuinely different selectors, when the scan runs, then they stay apart - the key decides what counts as the same command, and over-merging would hide a real pair of distinct criteria. |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | Claude Opus 5 | Filed |
