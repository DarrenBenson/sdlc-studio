# BG1007: A signed report's figure sources are outside its fingerprint, so every source can be rewritten and the page still checks VALID

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_report_sources_signed.py, .claude/skills/sdlc-studio/reference-sprint.md, changelog.d/BG1007.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** Reproduced through the shipped close, sign and check at e6c9b480 (scratchpad probe_sources.py); found by the G2 breakdown of CR0610.
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-09T07:47:53Z

## Summary

The report fingerprint covers each figure's section, key and value, never its `source`. Reproduced at e6c9b480 on a fixture closed and signed through the shipped `sprint close` and `sprint sign`: rewriting all 112 `source` fields in the filed RPT0001.json to `made-up/elsewhere.json` and committing leaves `sprint_report.py check --report RPT0001` at `VALID: RPT0001 re-derives to the fingerprint it records`. The figures are protected; where each says it came from is not, so a reader following a signed page's provenance can be sent anywhere. Found while drafting the CR0610 breakdown (D0355), which relies on it: re-pointing citations is safe for already-signed pages precisely because sources are unsigned.

## Steps to Reproduce

Close and sign a run; edit any figure's `source` in reports/RPTxxxx.json; commit; `sprint_report.py check --report RPTxxxx` -> VALID.

## Proposed Fix

Either fold each figure's source into what `check` judges (a source change names the figure as edited, as a value change does), or state on the page and in reference-sprint.md that sources are unsigned pointers. Decide with CR0610's citation re-pointing, which must not invalidate pages signed before it.

## Acceptance Criteria

- [ ] **AC1** A signed page whose figure sources were edited after signing is reported by `check` as edited, naming each figure, or the page and reference state plainly that sources are not signed
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_sources_signed.py::SignedSourcesTests::test_an_edited_source_is_named_by_check

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Filed |
