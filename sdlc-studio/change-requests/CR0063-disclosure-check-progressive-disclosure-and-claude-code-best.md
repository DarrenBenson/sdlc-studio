# CR-0063: disclosure check progressive disclosure and claude code best practice advisory

> **Status:** Complete
> **Created:** 2026-06-21
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Feature

## Summary

The skill is loaded into agent sessions, so progressive-disclosure discipline is a token lever.
Add `scripts/disclosure.py` (advisory): flag reference-/help- files missing a `Load when:` trigger
or orphaned from every index, plus best-practice items from `best-practices/claude-skill.md`. It
holds new files to the discipline and reports the existing backlog (~36 advisories today). Advisory
by decision - never blocks; this CR does not mass-fix the backlog.

## Acceptance Criteria

- [x] `disclosure.py` flags missing `Load when:` markers + orphans (not reachable from SKILL.md /
  help/references.md / help/help.md) across reference-/help- files
- [x] best-practice checks: scripts executable + expose `--help`, templates use `{{placeholder}}`,
  SKILL.md has a When-to-Use section; skill-dev only (no-op for consuming repos)
- [x] wired into the gate as NON-BLOCKING (advisory); `--strict` opts into a non-zero exit;
  `npm run lint:disclosure` available
- [x] tested; gate stays green with disclosure findings present; doc-coverage finds the new script

## Implementation

New `scripts/disclosure.py` (`check(root)`, mirrors doc_coverage's skill-dev no-op) + tests;
gate.py `disclosure` check (blocking=False, the constitution-advisory pattern); reference-scripts.md
entry; best-practices/claude-skill.md note; package.json `lint:disclosure`. Did NOT mass-fix the ~36
advisory gaps (advisory by decision - addressed incrementally / a later sweep).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | Autosprint | Created via `new` (deterministic) |
