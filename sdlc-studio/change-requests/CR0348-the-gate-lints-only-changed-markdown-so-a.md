# CR-0348: the gate lints only changed markdown, so a broken file stays green until something touches it

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .github/workflows/lint.yml, package.json
> **Date:** 2026-07-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

help/sprint.md carried an unescaped pipe in a table cell (achieved|partial|missed reading as extra columns, MD056/MD060). It was present at HEAD and had been passing CI for an unknown number of commits, because the markdown lane only lints what a commit changes. It surfaced only when an unrelated story edited that file, and then blocked a commit that had nothing to do with it. The same shape hid a payload-config difference: the repo lints .claude/ under a separate lane, so a file can pass one and fail the other.

## Impact

A latent markdown defect is invisible until an unrelated change touches its file, at which point it blocks that change and looks like the change's fault. The person who pays is never the person who introduced it.

## Acceptance Criteria

- [ ] a periodic or pre-release lane lints the WHOLE markdown corpus, so a latent failure is attributed when it is introduced rather than when it is next touched
- [ ] the report distinguishes a pre-existing failure from one this change introduced

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Raised |
