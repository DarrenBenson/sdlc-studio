# BG1434: The risk-class map reader drops an empty-prefix entry and a scalar risk value silently, and four refine stamping paths are pinned by no test

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/risk_class.py, .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/help/refine.md, .claude/skills/sdlc-studio/scripts/tests/test_risk_class_pins.py, changelog.d/BG1434.md, .claude/skills/sdlc-studio/scripts/tests/test_refine.py
> **Evidence:** Run twelve (RUN-01M7E52T) review of US1152, qa-seat-US1152-r1, verdict sdlc-studio/reviews/verdicts/US1152/18180f92c195-04bb7e46.txt
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run twelve orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T01:35:34Z

## Summary

Run twelve's US1152 review (APPROVE, non-blocking) found: a map entry whose prefix normalises to empty (`/: high`) is dropped with no note (lib/`risk_class.py`:104); `risk: high`, a scalar where the mapping belongs, is reported as 'no component map is declared' rather than a malformed value (lib/`risk_class.py`:90); help/refine.md:60-63 says every minted story carries `Risk-class`, but a story with no Affects carries none; and four correct behaviours are unpinned: the highest-class rule (a last-match mutant at lib/`risk_class.py`:66 survives because the fixture orders low before high), stamping on `refine apply --into` (refine.py:820), stamping on `refine add` without `--into` (refine.py:914), and the risk-note print in `cmd_add` (refine.py:1223).

## Steps to Reproduce

Declare `risk: {components: {'/': high}}`, or `risk: high`, and refine a story: no note names the ignored entry. Apply any of the four mutants named in the summary and run `test_risk_class_map.py`, `test_refine.py` and `test_lean_refine_add_into.py`: each survives.

## Proposed Fix

Report an empty-prefix entry and a non-mapping `risk` value in one line each; scope the help sentence to stories with Affects; add tests with the high class listed first, and for `apply --into`, `add` and the add note.

## Acceptance Criteria

- [ ] **AC1** Given a map entry `/: high` or a scalar `risk: high`, when refine runs, then one line names the ignored entry or value and nothing refuses. Fails on: silence, or the no-map line for a malformed value.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_risk_class_pins.py::MapNotesTests
- [ ] **AC2** Given a map listing a high-class prefix before a lower one, when a story's Affects touch both, then its class is high; and stories minted by `apply --into` and by `add` carry the class. Fails on: a last-match classifier, or either path minting without the field.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_risk_class_pins.py::StampPathTests

## Resolution

Won't Fix under D0613: the operator approved the product seat's second proposal (D0562) because a user can meet it, but it is rare and harmless and has a workaround, so fixing it costs more than it returns. A bad risk map entry is dropped silently; workaround is to correct the map.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | Claude Opus 5.5 (run twelve orchestrator) | Filed |
| 2026-11-24 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0613: the operator approved the product seat's second list (D0562); reason in Resolution |
