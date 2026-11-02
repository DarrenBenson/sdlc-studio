# BG1179: The TRD refresh test pins vocabulary rather than US1101's corrected claims: the ADR-012 row, the ADR sentences and an aliased urlopen all slip past it

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/tests/test_lean_trd_refresh.py, changelog.d/BG1179.md
> **Created:** 2026-11-02
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-02T21:06:29Z

## Summary

Found by US1101's full-tier reviews (2026-11-02), each mutant re-tested in isolation. (1) Removing ADR-012 from the 2026-10-09 revision row (trd.md:1319) survives, because US1101's own row also names it (`test_lean_trd_refresh.py`:669). (2) Reverting the RV0028 corrections to ADR-009 (trd.md:1062) and ADR-012 (:1191, :1208, :1223) survives, because the test reads verbs, seats and paths, not the corrected sentences (:647, :696). (3) `from urllib.request import urlopen as _uo` then `_uo(url)` in a shipped script passes with no Network paths row, because the scanner reads only names in `_CONNECTS` (:482, :552). BG1164 item 2 (gh argv spellings) is separate and already filed.

## Steps to Reproduce

Apply each mutant above to a scratch copy and run `pytest tools/tests/test_lean_trd_refresh.py`: green.

## Proposed Fix

Pin the ADR-012 acceptance row by date and id, pin each corrected ADR sentence by its claim, and resolve import aliases in the connection scanner.

## Acceptance Criteria

- [ ] **AC1** Each of the three mutant families above turns tools/tests/`test_lean_trd_refresh.py` red.
  - **Verify:** pytest tools/tests/test_lean_trd_refresh.py

## Impact

Later edits can revert US1101's corrections with the suite green.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-02 | claude | Filed |
