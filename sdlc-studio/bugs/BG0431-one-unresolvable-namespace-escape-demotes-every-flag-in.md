# BG0431: one unresolvable namespace escape demotes every flag in the module to cannot-judge, and nothing bounds how far that spreads

> **Status:** Open
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

- [ ] The behaviour described is corrected: `unresolved` is module-scoped, so a single escape this analysis cannot follow demotes EVERY unread destination in that module - including ones the escape has...
- [ ] The proposed fix lands, pinned by a test: Scope the demotion to destinations the escape could plausibly reach, or add a shrink-only baseline over the unjudged set so the hole cannot silently widen.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | Claude Opus 5 (independent adversarial review of the EP0169/EP0172/EP0175 batch) | Filed |
