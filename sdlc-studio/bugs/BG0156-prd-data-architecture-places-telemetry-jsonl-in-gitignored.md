# BG0156: PRD data architecture places telemetry.jsonl in gitignored .local and calls VELOCITY.md 'the one piece of measurement state deliberately committed'; committed main moved the evidence ledger to committed retros/evidence/

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Medium
> **Points:** 1
> **Affects:** sdlc-studio/prd.md
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a
> **Delivered-by:** claude-opus-4-8

## Summary

prd.md:423-428 lists telemetry.jsonl among gitignored sdlc-studio/.local/ machine state and asserts VELOCITY.md is the only committed measurement state. On committed main (856436f, before the in-flight sprint) telemetry.py declares both forecast and actuals logs COMMITTED under retros/evidence/ - with an explicit docstring section on WHY they are committed ('evidence the team cannot read on a fresh clone is not evidence') - and even migrates any pre-existing .local log there; seven evidence JSONL files are git-tracked. The PRD's data model is wrong in the direction that matters: Section 10's whole falsification story rests on this ledger, and a rebuilder following the blueprint would put it back in gitignored state - the precise defect the code fixed. Verified 3x; no CR tracks the PRD update.

## Steps to Reproduce

Read prd.md:423-428; compare telemetry.py lines 2-4 and 579 on committed main; run `git ls-files sdlc-studio/retros/evidence/` - 7 tracked JSONL files.

## Proposed Fix

Rewrite PRD Section 7's data model: forecasts/actuals JSONL live committed under retros/evidence/ (with the .local migration noted); telemetry.jsonl removed from the .local list; the 'one piece committed' sentence restated.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Filed |
