# BG0482: US0597 AC3 is ticked Verified and is not met: the named evidence file was never created and its verifier asserts nothing about before-and-after

> **Status:** Fixed
> **Verification depth:** functional (claim-drift-replay.json now exists with both arms, corpus and units; verifier asserts each separately and that after < before)
> **Severity:** High
> **Points:** 3
> **Affects:** sdlc-studio/stories/US0597-the-claim-drift-premise-is-replayed-against-the.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, sdlc-studio/retros/evidence/claim-drift-replay.json
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio file
> **Raised-by:** independent-critic (qa seat); human; v1
> **Raised-in-batch:** 2026-08-01T08:00:52Z

## Summary

US0597 AC3 requires that the blocking-finding count before and after the scoping rule is written to the evidence directory with the units it covers. The file its own Affects names, sdlc-studio/retros/evidence/claim-drift-replay.json, was never created: `git log --all --oneline -- sdlc-studio/retros/evidence/claim-drift-replay.json` is empty.

Its named verifier `test_the_before_and_after_is_recorded` asserts only that rec["runs"] == 1 and rec["findings"] >= 1 over a temp-directory yield accumulator. There is no before count, no after count, no units covered, and no reference to the run it claims to measure. The criterion is ticked Verified: yes.

This is a vacuous verifier standing over a false completion claim - the class US0584 was built to flag - shipped by the unit whose job was to measure the premise. `git log -S 'test_the_before_and_after_is_recorded'` -> dffea4bf, after the base ref, so it is new to this batch.

## Steps to Reproduce

1. git log --all --oneline -- sdlc-studio/retros/evidence/claim-drift-replay.json -> empty.
2. Read `test_the_before_and_after_is_recorded`: it asserts runs == 1 and findings >= 1 on a temp dir.
3. Read US0597 AC3: it requires a before count, an after count and the units covered.
4. grep -rl "claim-drift-replay" sdlc-studio/bugs/ sdlc-studio/change-requests/ -> nothing, so this is not already recorded.

## Proposed Fix

Either produce the evidence the criterion names - a replay writing the before and after blocking-finding counts and the units covered, with a verifier asserting each of those three - or amend AC3 to the claim the work actually supports and untick it until that claim is verified. Do not leave a criterion ticked against a verifier that cannot fail on its subject.

## Acceptance Criteria

- [ ] The behaviour described is corrected: US0597 AC3 requires that the blocking-finding count before and after the scoping rule is written to the evidence directory with the units it covers.
- [ ] The proposed fix lands, pinned by a test: Either produce the evidence the criterion names - a replay writing the before and after blocking-finding counts and the units covered, with a verifier...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | independent-critic (qa seat) | Filed |
