# CR-0102: --no-artifacts suppress/enforce behaviour is restated verbatim across epic, story, and outputs references

> **Status:** Complete
> **Priority:** Medium
> **Type:** Improvement
> **Date:** 2026-06-24
> **Created-by:** sdlc-studio file

## Summary

The --no-artifacts behaviour (suppressed PL/TS/WF + intermediate transitions; still-enforced typecheck/full-suite/AC-verify/cascade/reconcile gates; the Ready->Done compression) is fully restated in reference-epic.md, reference-story.md, and reference-outputs.md instead of stated once with pointers. epic.md#wave-quality-gates already shows the cheaper delegate-and-do-not-restate pattern. Any change to the enforced-gate set must be edited in three coupled places or they drift.

## Acceptance Criteria

- [x] The canonical --no-artifacts definition lives in exactly one reference file (natural home reference-epic.md#flag-no-artifacts)
- [x] reference-story.md and reference-outputs.md point to that single anchor rather than restating the bullet lists, keeping only the file-local framing they need
- [x] No suppressed-files / enforced-gates claim appears verbatim in more than one file; a future change edits only the canonical location
- [x] CHANGELOG entry same commit

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-24 | audit | Raised |
