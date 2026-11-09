# BG1314: Two US1146 persona checks cannot catch a swapped Primary, and `validate.py personas` compares the whole Interface cell, so a card reverted to Primary passes AC2's own Verify

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** tools/tests/test_persona_coherence.py, .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py
> **Evidence:** US1146-verdict-r1 (RUN-01M7061X) and its mutant log
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-09T14:31:03Z

## Summary

From US1146's QA review (qa-seat-US1146-r1, non-blocking, 2026-11-09). (1) tools/tests/`test_persona_coherence.py`:749 accepts Trevor Hale's Boundaries naming Rowan Achterberg as the shipped skill's Primary and Abena Osei as the tooling Primary, and :458 accepts Jonah Reyes's cast line calling Abena the tooling Primary: the suite stays green under either swap, the class US1079's round-1 review found. (2) Pre-existing: validate.py:1283-1293 compares the whole Interface cell, so US1146 AC2's Verify passes with Maya Okafor's card reverted to Primary; only AC3's Verify catches it.

## Steps to Reproduce

1. In a scratch copy, swap the two Primaries' interfaces in Trevor Hale's Boundaries and run tools/tests/`test_persona_coherence.py`: it passes.
2. Revert Maya Okafor's card to Primary for the shipped skill and run US1146 AC2's Verify: it passes.

## Proposed Fix

Pin each Primary to its own interface by name in both checks, and have validate.py compare the cast role per interface rather than the cell as a whole; add the swap and the revert as failing fixtures.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: From US1146's QA review (qa-seat-US1146-r1, non-blocking, 2026-11-09).
- [ ] **AC2** The proposed fix lands, pinned by a test: Pin each Primary to its own interface by name in both checks, and have validate.py compare the cast role per interface rather than the cell as a whole; add the...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
