# BG0055: ts-check verify-report cross-check keys on bare AC id, flagging unrelated stories

> **Status:** Closed
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Severity:** High
> **Raised-by:** Sam Eriksson (QA amigo), repository review RV0006
> **Effort:** S

## Summary

`_report_failed_acs` collapses failures from all stories into a set of bare AC labels
("AC3"), against a docstring that promises `id::ac`. `ts_check` then flags any test-spec
matrix row whose AC label collides, regardless of which story actually failed.

## Evidence

- `.claude/skills/sdlc-studio/scripts/verify_ac.py:671` -
  `failed.add(str(f.get("ac", "")).upper())` stores just the bare AC id.
- `verify_ac.py:657` - docstring claims "id::ac upper-cased".
- `verify_ac.py:707` - `elif ac.upper() in failed_in_report` compares bare label to bare set.
- The matrix has a Story column (scaffold header at `verify_ac.py:737`) the cross-check never
  reads.

## Impact

AC ids are AC1..ACn in every story, so on any multi-story merged report one red AC produces
false "matrix says passing but the verify-report marks it failing" findings across unrelated
stories, failing `ts-check --verify-report` (exit 1) spuriously. It undermines trust in the
one cross-check meant to stop a matrix claiming green over a red runner.

## Steps to Reproduce

1. Verify two stories into a merged `verify-report.json`; story A's AC1 fails, story B's AC1
   passes.
2. Run `ts-check --verify-report` on story B's test-spec.
3. B's AC1 row is flagged "matrix says passing but the verify-report marks it failing" though
   B's AC1 passed.

## Proposed Fix

Key the failure set as `STORYID::AC` (the report is already keyed by story stem) and compare
against the matrix row's Story + AC cells rather than the bare AC label.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | Sam Eriksson (QA amigo) | Created via `new` (deterministic) |
| 2026-07-06 | Sam Eriksson (QA amigo) | Evidence verified; filed from RV0006 code-level leg |
| 2026-07-06 | Dani Okafor (Engineering amigo) | Fixed with a failing-first regression test on branch sprint/rv0006-bugfixes; transitioned to Closed |
