# CR-0599: The sprint signature is recorded in a tracked file, so any clone can verify a signed report

> **Status:** Proposed
> **Priority:** High
> **Type:** Feature
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Date:** 2026-09-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-25T18:05:05Z
> **Decomposed-into:** US0959, US0960, BG0795, BG0788

## Summary

A signed sprint report is anchored to signature.report and signature.fingerprint in the run record, which lives in gitignored sdlc-studio/.local and exists only in the clone that signed. Anyone who can write that clone's .local can re-point or strip the signature, and any other clone cannot verify the signature at all (`sprint_report` check exits 2 with no run record). Found by BG0775's QA review.

## Acceptance Criteria

_None yet: add them here, or on the stories `refine` decomposes this into._

## Notes

- Decomposed for Sprint 6 into US0959 (the sealed run record is tracked and `check` reads record and signature from tracked history), BG0795 (CI runs frozen on the record at PREPARE), BG0788 (verdict row identities frozen at PREPARE) and US0960 (migrate files records for reports already signed; US0941 AC5 restored). Measured at dee380d9: a clean clone exits 2 on RPT0006-RPT0010; with the run records copied in, a clone whose `gh` reaches GitHub reads RPT0006, RPT0007, RPT0009 and RPT0010 INVALIDATED on DORA, and a depth-1 clone reads them INVALIDATED on `dora_band`, so tracking the signature alone would not make a report checkable anywhere else.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Raised |
| 2026-09-26 | sdlc | US0940 re-pointed US0941 AC5 at hermetic tests: check cannot re-validate RPT0006-RPT0009 in a clean clone without .local, so the pre-fix-signed clause is uncarried until the signature record is tracked; restore AC5's original Verify when this lands |
| 2026-09-27 | sdlc-studio v6 planning | Decomposed by the Sprint 6 engineering seat into US0959, US0960, BG0795 and BG0788; the acceptance criteria live on those units |
