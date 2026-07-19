# CR-0339: Bounded mutation should bias its sample toward changed lines, not the file head

> **Status:** Complete
> **Decomposed-into:** EP0072
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py
> **Date:** 2026-07-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

mutation.py run --files <file> --max-mutations N enumerates all mutants in the whole file and (under a low ceiling) samples the first N, which on a large multi-function file are early-file lines (imports, path constants, git helpers) - not the diff. At the RUN-01KXQH64 close, 10/826 mutants sampled peripheral helpers and all survived, telling nothing about the changed cost code. The report is honest (816 un-checked) but the run is uninformative for a diff-focused close.

## Impact

A close's mutation lane is meant to test whether THIS diff's tests can fail; sampling the file head instead makes a bounded run worthless exactly when the ceiling bites, training agents to skim the lane.

## Acceptance Criteria

- [ ] When --since (or a changed-lines set) is available, mutation prioritises mutants on the changed lines before spending the ceiling on unchanged code; a run that cannot cover the diff within the ceiling says so, naming the diff coverage achieved.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Raised |
