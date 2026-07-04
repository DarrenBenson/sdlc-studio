# BG0049: ts-check AC-matrix parser bleeds into later tables (Revision History rows read as AC rows)

> **Status:** Closed
> **Verification depth:** functional (unit: canonical shape passes, true positive preserved; live: TS0001/TS0002 re-checked)
> **Severity:** medium
> **Created:** 2026-07-04
> **Created-by:** sdlc-studio file

## Summary

verify_ac.ts_check locks onto the AC Coverage Matrix header and then treats EVERY subsequent table row in the file as a matrix row: the References and Revision History tables that canonically follow the matrix are parsed as ACs ('Sam no test case mapped', 'Author no test case mapped'). Empirically epic-ts FAILs on the shipped convention's own shape - TS0001, the spec of the already-closed EP0010, fails today. Same defect class as BG0046: stateful table parsing with no structural table boundary.

## Steps to Reproduce

1. Author a test-spec per TS0001's shape (matrix, then References, then Revision History). 2. Run verify_ac.py epic-ts --epic <its epic>. 3. Rows of the later tables are reported as unmapped ACs and the check FAILs.

## Proposed Fix

Scope the matrix parse structurally: a markdown heading line or a new table header row that is not a matrix header ends the matrix scope (reset cols). Regression: TS0001's real shape passes; a genuinely unmapped AC row still fails (true positive preserved).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | audit | Filed |
| 2026-07-04 | claude | Fixed: a markdown heading ends the matrix scope, so References/Revision History tables never parse as AC rows. Mutation-checked: both new tests seen RED against the unfixed parser. Live-verified on TS0001 + TS0002 (only genuine matrix rows report now). |
