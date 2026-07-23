# CR-0377: mutation run should derive the minimal covering test command from its own reference scan

> **Status:** In Progress
> **Decomposed-into:** EP0138
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/help/mutation.md
> **Date:** 2026-07-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The wall-time of an evidence run is mutants times suite runtime, and the suite command is chosen by hand: too narrow manufactures survivors (the CR0363 failure), too wide pays the full suite per mutant. The run already scans which test files reference each target to produce its selection warnings - the same scan can PROPOSE the minimal covering command (the referencing test files per target), so the ceiling buys roughly twice the mutants per minute with the manufactured-survivor risk policed by the very warning that shipped beside it. Measured at the RUN-01KXZQF0 close: ~40s per mutant against the three-suite command, ~40min total for 40 mutants; a per-target covering command would roughly halve it.

## Impact

the per-close cost of mutation evidence, which is the main wall-clock argument against ever making the lane blocking (RFC0048 D3)

## Acceptance Criteria

- [ ] given targets and no --test, or a --suggest-test flag, the run prints the derived covering command per target (the referencing test files its scan found), with the honest caveat that reference-scan coverage is a heuristic
- [ ] a run executed with the derived command produces zero out-of-selection warnings for its targets, by construction
- [ ] the hand-supplied --test path is unchanged and remains the default

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Raised |
