# BG0431: one unresolvable namespace escape demotes every flag in the module to cannot-judge, and nothing bounds how far that spreads

> **Status:** Fixed
> **Verification depth:** functional (the real corpus asserted against its baseline, plus a fixture proving both drift directions are named rather than counted)
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/command_audit.py, .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py
> **Evidence:** Executed by an independent reviewer, including the path-dependence of the story's own headline evidence run.
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (independent adversarial review of the EP0169/EP0172/EP0175 batch); agent; skill v5.0.0
> **Raised-in-batch:** 2026-07-29T15:35:33Z

## Summary

`unresolved` is module-scoped, so a single escape this analysis cannot follow demotes EVERY unread destination in that module - including ones the escape has nothing to do with. Demonstrated: a module with one `somewhere_else.setup(args)` call reports `0 dead flag(s), 1 not judged, exit 0`; delete that line and the same file reports the flag DEAD. Nothing ratchets the unjudged count: the live-corpus test asserts `dead == []` and that each unjudged entry has a reason, but sets no ceiling. Adding one `telemetry.record(args)` call to a large module would move all of its destinations to not-judged with every lane and test still green. The sibling verify-ratchet lane has a shrink-only baseline for exactly this reason and this lane has none. The verdict is also path-dependent: the same bytes analysed outside the tree fail sibling resolution and demote.

## Steps to Reproduce

1. A module with one unresolvable escape plus a flag forwarded to a callee that never reads it.
2. Detector reports 1 not judged, exit 0. Remove the escape line: the same flag reports DEAD, exit 1.

## Proposed Fix

Scope the demotion to destinations the escape could plausibly reach, or add a shrink-only baseline over the unjudged set so the hole cannot silently widen. State whichever is chosen in the reference.

## Acceptance Criteria

### AC1: the unjudged set is recorded per destination, and the shipped corpus matches it

- **Given** the real tree
- **When** the unjudged destinations are compared with the recorded baseline
- **Then** neither side has an entry the other lacks, so a destination that stops being judged is a decision somebody made rather than a side effect of an unrelated escape
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py::UnjudgedRatchetTests::test_the_shipped_corpus_matches_its_baseline
- **Verified:** yes (2026-08-02)

### AC2: a new unjudged destination is reported, and a cleared one too

- **Given** a baseline naming one pair and a scan reporting a different one
- **When** the drift is taken
- **Then** the new pair AND the cleared pair are both named - a COUNT would be satisfied by one clearing while another appears, which is the hole moving while the number stands still
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py::UnjudgedRatchetTests::test_a_new_unjudged_destination_is_reported
- **Verified:** yes (2026-08-02)

> **Recorded rather than narrowed, and why.** Scoping the demotion to destinations an escape
> could plausibly reach needs dataflow this analyser does not have; guessing at it would
> un-demote real cases. Measured, the hole is 8 destinations across 3 modules - small enough to
> record exactly, which is the option the filing offered and the idiom this repo already uses
> for a shrink-only baseline.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | Claude Opus 5 (independent adversarial review of the EP0169/EP0172/EP0175 batch) | Filed |
