# BG0948: A migrating project cannot baseline pre-existing placeholder findings, and v3 ids can never be baselined

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py
> **Created:** 2026-10-05
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-05T15:44:28Z

## Summary

`validate.py check --emit-baseline` emits only the criteria baseline. There is no emitter for `.placeholder-baseline.txt`, whose contract says it is 'captured from the checker's own output, never hand-written', so a project upgraded from an old skill (sdlc-studio-lens: 32 Done stories with an unfilled Story Points token) is left with errors it can only clear by hand-writing the file. Separately, `_baselined` keys on `(BG|US|EP|CR|RFC)\d{4}`, so a short-ULID (schema 3) artefact can never match a baseline line. Raised from sdlc-studio-lens RV0003 (observability gap analysis, 2026-10-05).

## Steps to Reproduce

1. Copy a 4.0-era schema-3 workspace with Done stories carrying an unfilled Story Points token. 2. Run validate.py check: placeholder errors. 3. Run validate.py check --emit-baseline: only criteria ids are printed. 4. Read validate.py `_baselined`: the id regex has no ULID alternative.

## Proposed Fix

Have --emit-baseline also emit the placeholder record (ID:{{token}}) for a separate redirect, and match ids with the shared `sdlc_md` id pattern so v3 ids resolve.

## Acceptance Criteria

- [ ] **AC1** `validate.py check --emit-baseline` can produce the placeholder baseline record from the checker's own output
- [ ] **AC2** A placeholder finding in a v3-id artefact listed in the baseline is downgraded to a warning, shown by a test
- [ ] **AC3** A new placeholder in a baselined artefact still errors

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-05 | Claude Opus 5.5 | Filed |
