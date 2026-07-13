# BG0110: review lets a required leg (TSD) be self-downgraded to optional in prose without an explicit waiver

> **Status:** Fixed
> **Verification depth:** functional
> **Created:** 2026-07-13
> **Created-by:** sdlc-studio new
> **Severity:** Medium
> **Raised-by:** Claude (Opus 4.8); agent; claude-opus-4-8
> **Found-in:** sdlc-bench (consuming project); evidence RV0004
> **Depends on:** CR0233

## Summary

The unified review's required legs are PRD / TRD / TSD / Persona / CODE. When a required leg's
artifact is ABSENT, the review currently lets the reviewer downgrade it to "optional" in prose and
still pass, instead of either filing a blocking finding or recording an explicit waiver. A required
artifact can therefore stay missing indefinitely while every review reports clean.

Concrete evidence: in the sdlc-bench project, `RV0004` TSD leg read "Still absent... A TSD is now
optional polish, not a gap - the per-story `Verify:` discipline held throughout." No `tsd.md`
existed, no finding was filed, no waiver decision was recorded - the reviewer's own prose reclassified
a required leg as optional, and the pre-release gate (which mandates all five legs) was satisfied
anyway. The gap surfaced only when the operator noticed the TSD had never been written.

## Steps to Reproduce

1. In a project with no `sdlc-studio/tsd.md`, run `/sdlc-studio review` (or `--focus tsd`).
2. Observe the TSD leg can report a health/decision that treats the absent document as acceptable
   ("optional polish") without emitting a blocking finding or requiring a recorded waiver.
3. The review passes; the pre-release gate's "all five legs" requirement is met despite a missing
   required artifact.

## Proposed Fix

For each required leg whose artifact is ABSENT, the review must resolve it one of two ways, never by
narrative downgrade:

- **File a finding** (the default) - a missing required artifact is a review finding to triage/fix; or
- **Record an explicit waiver** - a decisions-log entry (e.g. `decisions.py add`) stating the leg is
  intentionally out of scope for this project, with a rationale. The review then reports the leg as
  "waived (see D00xx)", not "optional".

Make the leg's absence machine-visible: the review JSON should carry `tsd: {present: false, waiver:
<decision-id|null>}` so a downgrade without a waiver is detectable, and the pre-release "all five
legs" check should fail on an absent-and-unwaived required leg rather than accept reviewer prose.

## Verify

Verify: manual - a review of a project missing a required artifact either emits a blocking finding or
reports the leg as waived against a recorded decision id; it cannot pass by prose reclassification.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-13 | sdlc | Created via `new` (deterministic) |
