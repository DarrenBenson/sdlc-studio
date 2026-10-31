# BG1139: lessons.py revalidate --extend accepts --reason and discards it, so a judged extension leaves no record and cannot be told from an unjudged one

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lesson_lifecycle.py, .claude/skills/sdlc-studio/scripts/tests/test_lessons.py, .claude/skills/sdlc-studio/help/lessons.md, .claude/skills/sdlc-studio/reference-scripts-domain.md, changelog.d/BG1139.md
> **Evidence:** lessons.py cmd_revalidate: the --extend branch calls upsert_field(e, 'Review-by', ...) and never reads args.reason; close_entry writes `Closed - <reason>`.
> **Created:** 2026-10-31
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-31T21:28:13Z

## Summary

`revalidate --close` writes its reason onto the lesson (`- **Status:** Closed - <reason>`), but `revalidate --extend` only rewrites Review-by and ignores a --reason it accepts without complaint. A lesson extended after a check against the tree therefore looks exactly like one of the 265 that D0391 extended without a judgement, and CR0655's re-validation (US1105-US1109) has no record to verify.

## Steps to Reproduce

1. In a throwaway project with a lessons log, run `lessons.py revalidate --extend L-0001 --reason "still true: the hook refuses it"`.
2. Read L-0001 in the log.
3. Expected: the reason and today's date recorded on the lesson. Actual: only Review-by changed, and the command exits 0 with the reason gone.

## Proposed Fix

Record each extension on the lesson as a `- **Revalidated:** <date> - <reason>` bullet (the latest one replaces an earlier one). Refuse `--extend` with no reason, naming the flag. Add `revalidate --unjudged-since DATE [--range L-NNNN:L-NNNN]`, which exits 1 and lists every open lesson in the range that has neither a close nor a Revalidated date on or after DATE, so a re-validation pass is checkable by one command.

## Acceptance Criteria

- [ ] **AC1** `revalidate --extend L-NNNN --reason R` records `Revalidated: <today> - R` on each lesson it extends, replacing an earlier Revalidated line, and still moves Review-by by the validity window.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lesson_lifecycle.py
- [ ] **AC2** `revalidate --extend` with no reason is refused by name, writing nothing.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lesson_lifecycle.py
- [ ] **AC3** `revalidate --unjudged-since DATE --range A:B` exits 1 listing each open lesson in the range with neither a close nor a Revalidated date on or after DATE, and exits 0 when there is none (positive control).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lesson_lifecycle.py

## Impact

A re-validation pass cannot be audited and CR0655's stories have no executable verifier. The validity lane can be satisfied by moving dates with no judgement made.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-31 | claude | Filed |
