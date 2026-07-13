# BG0118: engagement-floor over-refuses an extension-less real file in Affects (Makefile, Dockerfile, dotfiles)

> **Status:** Open
> **Severity:** Low
> **Created:** 2026-07-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Sam Eriksson; persona; v1

## Summary

Found by the CR0229 round-3 review (2026-07-13), non-blocking, fails safe. `engagement_floor._FILE_TOKEN_RE` requires a dotted extension (a filename token ending `.ext`), so a declaration whose only footprint is an extension-less real file - Makefile, Dockerfile, LICENSE, or a dotfile like .gitignore / .env - reads as NOT a real path and the unit is flagged undeclared. Reproduced: a single-file Makefile change with no AC, honestly declaring Affects: Makefile, is a VIOLATION and is forced to plan or record a waiver. This fails SAFE (over-refusal - it never lets a defect through) and hits a narrow class, but a false refusal that forces a waiver on a legitimate single-file change trains reflexive waivering, the exact anti-pattern the floor's own design tries to avoid. Minor sibling false-accept: Affects: v1.2 (a version string) reads as a file.

## Steps to Reproduce

1. A workspace with `engagement_floor` active past the cutoff. 2. A Done story touching ONLY Makefile, no AC, declaring Affects: Makefile. 3. gate: engagement-floor flags it undeclared/VIOLATION.

## Proposed Fix

Broaden `_FILE_TOKEN_RE` to accept a path-shaped token (one bearing a / separator) OR an allow-list of known extension-less filenames (Makefile, Dockerfile, LICENSE) and dotfiles, so a legitimate single-file declaration of such a file is accepted. Keep rejecting bare prose / n/a / version strings. Add tests: Affects: Makefile passes; Affects: v1.2 fails.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-13 | Sam Eriksson | Filed |
