# BG-0008: TRD script contract rule 5 is incomplete: verify_ac and lessons.py write outside the stated 'single exception'

> **Status:** Fixed
> **Severity:** High
> **Reporter:** Project Audit
> **Date:** 2026-06-20
> **Epic:** --
> **Story:** --

## Summary

Contract rule 5 says scripts never mutate files outside .local/ or the files passed on the command line, with plan.py archive as the single exception. But verify_ac.py rewrites story files discovered by a default directory walk, and lessons.py add --global writes into the skill's own lessons/ folder, both unacknowledged.

## Problem

trd.md:201-203 states the 'single exception is plan.py archive'. Two further in-workspace writers exist: verify_ac.py run defaults to --dir sdlc-studio/stories and rewrites the Verified: line in every matching story (verify_ac.py:338) with files discovered by walking, not passed on the command line; and lessons.py add --global writes LL{NNNN}.md and rewrites _index.md inside SKILL_LESSONS_DIR derived from **file** (lessons.py:34,275), mutating the installed skill directory itself. scripts/README.md:20 repeats the same too-narrow 'one script that writes outside .local/' claim. The threat-model row (trd.md:395) rests on this contract being complete.

## Proposed Fix

Amend contract rule 5 to name verify_ac.py (mutates story files under --dir/--story as its sanctioned in-workspace write) and lessons.py add --global (writes only into the bundled lessons/ registry, never deletes, refuses to overwrite) as additional bounded write-exceptions alongside plan.py archive. Correct scripts/README.md:20 accordingly.

## Evidence

trd.md:201-203 'single exception is plan.py archive' vs verify_ac.py:338 story_path.write_text(...) (default --dir) and lessons.py:34/275 SKILL_LESSONS_DIR write

## Impact

A migrator rebuilding from this TRD would implement an over-restrictive contract that forbids verify_ac.py's core behaviour and the cross-project lessons-promotion capability, or wrongly conclude the shipped scripts violate their own security contract.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Project Audit | Filed from the 2026-06-20 project-profile audit (lens: trd) |
