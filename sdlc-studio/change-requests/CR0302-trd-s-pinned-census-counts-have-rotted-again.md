# CR-0302: TRD's pinned census counts have rotted again; the changelog's 'freshness guard' claim overstates what the guard checks (fixed 2026-07-06 strings plus a lenient script-count floor)

> **Status:** Proposed
> **Priority:** Low
> **Type:** docs
> **Size:** S
> **Affects:** sdlc-studio/trd.md, tools/tests/test_trd_freshness.py
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a

## Summary

Reframed after triage verification: the original finding claimed no mechanism reads the TRD, but tools/tests/`test_trd_freshness.py` exists and does read trd.md (I confirmed) - the refute vote was right on that point. What survives: the guard only forbids the specific 2026-07-06 stale strings and asserts the script-count claim as a floor (actual >= claimed), so every other pinned count can drift upward freely - and has: scripts '58' vs 66 actual, help '41' vs 43, templates '78' vs 79, lib '6 modules' vs 5, tests '(76 modules); 2151' vs 91 modules/~2511 (some drift is the two-day unreleased sprint window, but lib 6-vs-5 is simply wrong). trd.md:973's 'a freshness guard now prevents the stale claims recurring' reads as a blanket safety claim the guard does not deliver. Panel split 2-1 (survivor); downgraded to Low.

## Impact

Reframed after triage verification: the original finding claimed no mechanism reads the TRD, but tools/tests/`test_trd_freshness.py` exists and does read trd.md (I confirmed) - the refute vote was right on that point.

## Acceptance Criteria

- [ ] TRD count claims refreshed or converted to banded/approximate forms ('40+ scripts' style) that the guard actually verifies
- [ ] The 4.0.0 changelog line restated to say what the guard covers (the enumerated 2026-07-06 claims plus a script-count floor), not a blanket recurrence guarantee
- [ ] Optional: the guard extended to band-check the other pinned counts (help, templates, lib, test modules)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Raised |
