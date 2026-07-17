# BG0152: Per-attempt telemetry has no production writer: neither the record CLI nor the transition close can produce an attempts list

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/telemetry.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/reference-scripts-domain.md, sdlc-studio/stories/US0172-per-attempt-telemetry-records-carry-an-attempts-list.md
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a
> **Delivered-by:** claude-opus-4-8

## Summary

US0172 ('records carry an attempts list') and US0173's true-cost sum are unreachable through the interfaces the loop records with. The `telemetry record` CLI accepts only flat --tokens/--model (no --attempts); transition.py's terminal-close record passes only iterations/`wall_time_s`/`critic_verdict.` Only the Python API accepts the field, no script or reference doc drives it, and reference-scripts-domain.md:60 describes only the reader. Every real escalation lands as flat records, so `unit_cost`'s 'rework included' figure degenerates to the flat single-attempt cost - removing an attempts list is the very blocker RFC0035's accepted proposal existed to fix. US0172's AC tests only the reader (`attempts_of)`, silently exempting the writer (LL0013/LL0027); the sprint's own evidence log (actuals-2026-07-16.jsonl) contains zero attempts records. This is a scope defect in work shipped as Done, not known in-flight incompleteness. Verified 3x by the refute panel.

## Steps to Reproduce

Run `python3 .claude/skills/sdlc-studio/scripts/telemetry.py record --help` - no --attempts flag exists. Inspect transition.py:640 - the close metrics dict carries only iterations/`wall_time_s`/`critic_verdict.` Grep the repo for a production caller passing 'attempts' to telemetry.record - only tests. Observe actuals-2026-07-16.jsonl: no record carries an attempts list.

## Proposed Fix

Add an attempts writer to the record CLI (e.g. repeatable --attempt model:tokens or --attempts JSON), thread attempt data through the transition/artifact close path, document how to record an escalation in reference-scripts-domain.md, and add a writer-side AC/test to close US0172's reader-only verification gap.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Filed |
