# BG0232: ac_fingerprint has no test of its own: a no-op mutant of the freshness spine survives

> **Status:** Fixed
> **Severity:** High
> **Verification depth:** functional (characterisation - ac_fingerprint was already correct, the gap was that nothing tested it. 15 tests pin it from both sides: stable across a Status change, a Revision History row and the Verified stamp; changes on a re-pointed verifier, a retitled AC, an added or removed AC. 4 mutants killed - constant hash (10 fails), title dropped (2), verifier dropped (3), ac_id-only (5))
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py
> **Created:** 2026-07-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The close-time mutation run over RUN-01KY03GS survived a no-op-mapper mutant at `verify_ac.py`:83, the `ac_fingerprint` function. That function replaced file mtime as the staleness signal for a green verify entry, so it is the spine of Done freshness - and no test file references it except `test_transition.py`, which exercises it only incidentally. Nothing pins the property the mechanism exists for: that the fingerprint CHANGES when the ACs or their verifiers change, and holds when unrelated edits (a Status transition, a Revision History row, the Verified stamp itself) bump mtime. A no-op fingerprint would make every green entry permanently fresh, which is silent by construction - exactly the failure the function was written to remove. This compounds BG0231: the fingerprint does not cover whether a named verifier still exists, and now it turns out the fingerprint itself is unpinned. The survivor is not manufactured by a narrow test command - the run named its 98-file selection and warned only about sprint, retro and validate targets, not `verify_ac.`

## Steps to Reproduce

Run mutation.py run --files .claude/skills/sdlc-studio/scripts/`verify_ac.py` with a test command covering `test_verify_ac.py.` The no-op-mapper mutant at line 83 (`ac_fingerprint)` SURVIVES. Confirm the gap directly with: grep -rln `ac_fingerprint` .claude/skills/sdlc-studio/scripts/tests/ which returns only `test_transition.py.`

## Proposed Fix

Pin the fingerprint from both sides in `test_verify_ac.py`: it must DIFFER for two stories whose AC text or Verify lines differ, and must be STABLE across an edit that changes neither (a Status change, an added Revision History row, a re-stamped Verified line). Both halves are needed - a fingerprint that always changes is as useless as one that never does, and only the pair distinguishes a real hash from a constant or a passthrough. Mutation-check the new tests, since a fingerprint test that compares a value to itself passes vacuously.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Filed |
