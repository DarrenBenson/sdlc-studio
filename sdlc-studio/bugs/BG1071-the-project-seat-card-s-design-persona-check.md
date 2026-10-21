# BG1071: The project seat card's design-persona check stops at a full stop, so a name followed by a file path before 'design persona' passes

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_seat_admits_secondary.py, changelog.d/BG1071.md
> **Evidence:** BG1066 round-2 QA verdict (sdlc-studio/reviews/critic-verdicts.md), its [new] non-blocking finding; test_seat_admits_secondary.py:91,:93.
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T11:28:54Z

## Summary

BG1066's AC2 negative check (`test_seat_admits_secondary.py`) refuses the project product seat card naming a registry persona as 'the design persona', in either order, inside a window of 40 characters that may not cross a full stop. A path or link between the name and the phrase carries a full stop ('.md'), so 'Maya Okafor (personas/maya-okafor-founder-engineer.md) is the design persona' passes. Found by BG1066's round-2 QA reviewer as a non-blocking [new] finding; the APPROVE stands.

## Steps to Reproduce

Edit sdlc-studio/personas/seats/product.md's header to 'Maya Okafor (personas/maya-okafor-founder-engineer.md) is the design persona', then run `pytest .claude/skills/sdlc-studio/scripts/tests/test_seat_admits_secondary.py` -> 3 passed.

## Proposed Fix

Strip Markdown links and backticked or bare paths before the window is applied, or bound the window by sentence rather than by a full stop.

## Acceptance Criteria

- [ ] **AC1** The project product seat card's header (its leading HTML comment and `## Who They Are`) names no persona listed in personas/index.md, read from the registry, so no wording, path or link can declare one of them the design persona there
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_seat_admits_secondary.py::ProductSeatLensTests::test_the_project_card_header_names_no_registry_persona

## Impact

A later edit can reinstate a single design persona in the project card's header behind a path, and the suite stays green.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Filed |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
