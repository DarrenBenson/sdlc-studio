# BG1072: test_persona_coherence's id check reads a fixed list of id prefixes, so a card citing a handoff or test-spec id that resolves to nothing passes

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/tests/test_persona_coherence.py, changelog.d/BG1072.md
> **Evidence:** US1079 round-2 QA verdict (sdlc-studio/reviews/critic-verdicts.md), mutants M26 (TS9999) and M27 (HO9999); test_persona_coherence.py:73.
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T11:48:40Z

## Summary

US1079's AC4 says every id the maintainer card cites anywhere resolves, and the test scans the whole card, but with a fixed prefix list (D, BG, US, CR, EP, RV, RFC, LL, RETRO, RPT; `test_persona_coherence.py`:73). An id of another registered type, such as a handoff (HO) or a test spec (TS), is never read, so a card citing HO9999 or TS9999 passes. The card cites no such id today. Found by US1079's round-2 QA reviewer as a non-blocking [new] finding; the APPROVE stands.

## Steps to Reproduce

Add 'TS9999' to the Frustrations of sdlc-studio/personas/rowan-achterberg-skill-maintainer.md, then run `pytest tools/tests/test_persona_coherence.py` -> all pass.

## Proposed Fix

Derive the prefixes from `sdlc_md.ARTIFACT_TYPES` and `META_TYPES`, plus D for decisions and LL for lessons, rather than listing them.

## Acceptance Criteria

- [ ] **AC1** A persona card citing an id of any registered artefact type that resolves to nothing fails the check
  - **Verify:** pytest tools/tests/test_persona_coherence.py -k evidence_resolves_and_states_the_boundary

## Impact

A dead citation of an unlisted type reaches a persona card with the suite green.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Filed |
