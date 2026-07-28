# BG0374: The markdownlint path fixed in BG0341 still cannot see every tracked markdown file

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** tools/lint-style.sh, package.json
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (RUN-01KYKVZM review carry-forward); agent; skill v5.0.0

## Summary

BG0341 widened the per-commit markdownlint lanes so tracked .github markdown is linted. The widening is an added path rather than a derivation, so markdown tracked outside both the original glob and the added path remains unlinted, and the same failure recurs the next time a tracked directory is added. This is the enumerated-list shape the carried lessons already name.

## Steps to Reproduce

Observed during the RUN-01KYKVZM review of BG0341's repair. Compare the linted set against git ls-files '*.md': the sets differ.

## Proposed Fix

Derive the linted set from the tracked set rather than from globs, as the corpus lane already does, so a new tracked directory is covered without list maintenance.

## Acceptance Criteria

No acceptance criterion could be derived from this finding's evidence: none of its prose fields carries fewer than 5 words of substance, so nothing here states what fixed would look like. Whoever picks this up agrees the contract with the author before starting - this is a stated gap, not a criterion to tick.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 (RUN-01KYKVZM review carry-forward) | Filed |
