# BG0027: persona checks flag non-persona files and review-seat charters as old/ill-formed

> **Status:** Closed
> **Created:** 2026-06-22
> **Created-by:** sdlc-studio new
> **Severity:** Medium

## Summary

After migrating to the Cooper model, `project upgrade` still reported 'old persona model present' because `_old_persona_model` rglob'd into `personas/seats/` (review-seat charters, a different RFC0016 schema) and scanned a `consult-guide.md`; and `validate.check_personas` only skipped `index.md`, flagging other non-design files. A guide / charter living beside personas should not trip a design-persona model/well-formedness check.

## Steps to Reproduce

On a migrated project: `project upgrade` reports the persona judgement item even though personas are already Cooper; `validate personas` flags consult-guide/readme.

## Proposed Fix

`_old_persona_model` now scans top-level design personas only (seats/ excluded) and skips readme/consult-guide/`_*`; `check_personas` skips index/readme/consult-guide/`_*`. Verified read-only on a consuming project: audit manual=[] , _old_persona_model False, personas well-formed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-22 | sdlc | Created via `new` (deterministic) |
