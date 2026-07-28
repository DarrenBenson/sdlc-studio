# BG0345: US0480 and US0461 specify two incompatible ratchets for one concept, and neither can fail as written

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** High
> **Points:** 3
> **Affects:** sdlc-studio/stories/US0480-validate-ratchets-the-footprint-and-criterion-warnings-against.md, sdlc-studio/stories/US0461-verify-ac-lint-ratchet-refuses-a-duplicate-group.md, tools/tests/test_ratchet_story_agreement.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (independent adversarial review of the residue stories); agent; skill v5.0.0

## Summary

US0461 (CR0433) builds a SET-based baseline at sdlc-studio/.verify-lint-baseline.json whose entries carry reasons, and its AC explicitly rejects count comparison. US0480 (CR0443) builds a COUNT-based baseline recomputed from the corpus for the same ratchet concept in the same repo. Neither story acknowledges the other. Worse, US0480's AC1 and AC2 contradict: if the expected count is recomputed from the same corpus being judged it always equals the actual, so the new instance AC1 requires to fail never can. The missing element is a reference state - a merge-base, or a stored instance-identity set - which neither AC names. Separately the ratchet is built where nothing blocking reads it: gate.py counts only severity == error from validate, discarding warnings, and the pre-commit hook runs gate.py rather than validate.py check, so making validate exit non-zero refuses nothing.

## Steps to Reproduce

1. Read US0461 AC2 (set-based, reasons per entry, count comparison rejected) beside US0480 AC2 (count recomputed from the corpus). 2. Note neither story references the other and no ratchet machinery exists yet in either validate.py or `verify_ac.py.` 3. Trace gate.py's validate lane: only severity == error is counted, so no warning ratchet reaches a blocking lane. 4. Confirm the pre-commit hook invokes gate.py, not validate.py check.

## Proposed Fix

Settle one ratchet design before either story is built - the set-with-reasons form, since a count cannot say WHICH instance is new and cannot carry a waiver. Then give US0480 a reference state to compare against, and either wire the ratchet into a gate lane (adding gate.py, the hook and the lane-order test to its Affects) or state explicitly that it is CLI-only and file the wiring separately.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (independent adversarial review of the residue stories) | Filed |
| 2026-07-28 | Claude Opus 5 | Fixed: one set-with-reasons design settled across US0480 and US0461, each naming the other; US0480 given a reference-state baseline and the blocking-lane wiring; guarded by `tools/tests/test_ratchet_story_agreement.py`. `validate.py` and `gate.py` dropped from Affects - the wiring is US0480's to build, this fix is story-level |
