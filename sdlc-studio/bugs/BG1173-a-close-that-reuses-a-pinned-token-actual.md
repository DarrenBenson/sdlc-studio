# BG1173: A close that reuses a pinned token actual writes 'Priced cost: not stated' into the retro with a lower-case reason, though its report states the run's priced cost

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, changelog.d/BG1173.md
> **Evidence:** Commit 519d125c, sdlc-studio/retros/RETRO0137-6-2-is-releasable-its-documents-and-personas.md, the line after '24 of 24 forecast at plan time'.
> **Created:** 2026-11-02
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-02T07:37:03Z

## Summary

2026-11-02, RUN-01M6A3K2's close. RETRO0137's token actual had been pinned with `retro.py accuracy --tokens 22817311`. The close's retro-accuracy step reused it (`SOURCE_UNCHANGED)` and wrote '**Priced cost: not stated.** the token actual already recorded was reused, not re-captured, so no component was read again; the row keeps the Priced/pt it was recorded with' into the retro's accuracy block. The reason starts lower-case after a full stop and carries no closing stop (retro.py `_priced_lines` and the `SOURCE_UNCHANGED` reason). RPT0023 from the same close states the priced cost as 111,425,278, so the retro and the report disagree on whether the run's cost is known.

## Steps to Reproduce

1. Pin a retro's token actual with `retro.py accuracy --id <retro> --tokens N --write`.
2. Run `sprint.py close --retro <retro>`.
3. Read the retro's accuracy block: 'Priced cost: not stated.' with a lower-case reason, while the report's Priced cost row holds a figure.

## Proposed Fix

When the token actual is reused, read the priced components afresh for the priced line, or omit it, and write the reason as a sentence.

## Acceptance Criteria

- [ ] **AC1** A close that reuses a pinned token actual leaves the retro stating the priced cost the report states, or no priced line, and no sentence in the accuracy block starts lower-case.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py

## Impact

A reader of the retro is told the run's priced cost is unknown when the report beside it states it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-02 | claude | Filed |
