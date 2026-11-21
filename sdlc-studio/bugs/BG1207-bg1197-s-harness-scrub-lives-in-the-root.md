# BG1207: BG1197's harness scrub lives in the root conftest, so unittest runs (skill-tests.sh, the hook's unittest fallback) still read the harness from the environment

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/loader.py, sdlc-studio/tsd.md, changelog.d/BG1207.md
> **Evidence:** BG1197 builder report, 2026-11-04, outside-the-unit items 2 and 3.
> **Created:** 2026-11-04
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-04T13:55:46Z

## Summary

2026-11-04, BG1197's build (run five). The autouse scrub in the root conftest.py covers every pytest run from the root. `tools/skill-tests.sh` and the commit hook's unittest fallback (BG1144) load no conftest, so under Cursor the meter modules still fail there, confirmed with `python3 -m unittest`. tsd.md:776 also still describes the root conftest only as temp-directory confinement.

## Steps to Reproduce

1. `env -u CLAUDECODE CURSOR_AGENT=1 python3 -m unittest .claude/skills/sdlc-studio/scripts/tests/test_retro.py`.
2. The meter tests fail on the Cursor reader's reason.

## Proposed Fix

Apply the same scrub from the shared test loader the unittest path imports, built from `token_meters.selection_variables()`, and update the TSD row.

## Acceptance Criteria

- [ ] **AC1** Under `CURSOR_AGENT`=1 with CLAUDECODE unset, the meter modules pass under python3 -m unittest.
  - **Verify:** shell env -u CLAUDECODE CURSOR_AGENT=1 python3 -m unittest .claude/skills/sdlc-studio/scripts/tests/test_retro.py

## Impact

A contributor working from Cursor gets a red result from the unittest route.

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because it affects only this repository's own CI, hooks or tools, nothing a consuming project installs. Cursor-agent scrub lives in the pytest conftest only; unittest runs under Cursor fail in this repository, and pytest is the supported route. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-04 | claude | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
