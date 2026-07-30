# BG0428: a supersession waiver was keyed on whoever declared it rather than on who superseded whom, and a parenthetical annotation manufactured a phantom waived pair

> **Status:** Fixed
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py, sdlc-studio/.supersession-waivers.json, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py
> **Evidence:** Found by an independent adversarial review of US0484. The reviewer also showed the corrupt-waiver protection was absent (filed separately) and that the count pin is not a ratchet.
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (from the independent review of US0477/US0484); agent; skill v5.0.0
> **Raised-in-batch:** 2026-07-29T15:35:33Z
> **Verification depth:** functional

## Summary

Two defects. (1) The waiver key is documented as directional (`superseder>superseded`) so that waiving 'A replaced B' cannot also waive the opposite claim about which design won - and a `reverse in waivers` fallback then made the lookup direction-agnostic. The fallback was load-bearing because the emitter keyed on whoever DECLARED, which put ten of the eleven live pairs in the file the other way round; so the documented property was false and the test that named it passed only because its fixture used the one direction where the two orderings coincide. (2) Ids were scraped from the whole field including its parentheticals, so a field of the shape `Superseded-by: X (shipped via Y; residual folded into X)` read Y as a second superseder and manufactured a pair that never existed. That phantom reached the tolerated set carrying a reason asserting something untrue about an artefact that superseded nothing, and it could only ever have been cleared by writing a false declaration. `decomposed_ids`, twenty lines below in the same module, already strips parentheticals for exactly this reason.

## Steps to Reproduce

1. Waive `A>B` as legitimate, then have B assert it supersedes A - drift goes to zero, so the opposite claim is silently exempted.
2. Delete the `or reverse in waivers` clause - the live-corpus test fails, proving the keys were the wrong way round.
3. Read the parser over a field whose parenthetical names another id - two superseders reported, one fictional.

## Proposed Fix

FIXED. The emitter names which artefact superseded which, so the key is directional in fact as well as in prose, and the reverse fallback is gone. Parentheticals are stripped and markdown links reduced to their text before ids are scanned. The tolerated set is regenerated with correct keys and drops from eleven pairs to ten. A test now asserts the waived SET equals the found set rather than only that the two counts agree.

## Acceptance Criteria

- [x] The waiver key is directional IN FACT: the emitter names which artefact superseded which, and the reverse-key fallback that hid the inconsistency is gone.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::SupersessionTests::test_a_waiver_is_DIRECTIONAL
- [x] A parenthetical annotation contributes no counterpart id, so no phantom pair is manufactured; the tolerated set is regenerated and holds 10 real pairs, not 11.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::SupersessionLiveCorpusTests::test_the_existing_pairs_are_waived_or_repaired
- [x] The waived SET is compared with the found set, not just the two counts - two agreeing numbers can be about different pairs.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::SupersessionLiveCorpusTests::test_the_detector_actually_finds_the_waived_pairs_when_they_are_NOT_waived

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | Claude Opus 5 (from the independent review of US0477/US0484) | Filed |
