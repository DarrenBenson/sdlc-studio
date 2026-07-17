# BG0176: migrate's needs-human list advises re-sizing terminal units: 14+ Closed/Fixed legacy-Effort bugs each get 'set its Points by judgement', work nobody should do

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/migrate.py, .claude/skills/sdlc-studio/scripts/migrate_v3.py
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5; agent; dogfood retro 2026-07-16
> **Delivered-by:** claude-opus-4-8

## Summary

migrate's needs-human report passes `migrate_v3`'s re-size bucket through with no terminal-status filter, so the 2026-07-16 dogfood run told the operator to re-size BG0053-BG0066 (all Closed, some since June) 'on the Fibonacci scale by judgement'. Points exist to plan and cost DELIVERY; a terminal unit will never be planned, so the advice is wrong, and it buries the handful of genuinely open legacy-Effort units (e.g. BG0131, BG0143, BG0147) in ~2x noise. The honesty rule migrate was built on (report judgement, never guess it) is undermined when half the reported judgement calls are no-ops.

## Steps to Reproduce

1. In a workspace with Closed bugs carrying legacy 'Effort:' lines, run scripts/migrate.py. 2. The needs-human section lists each Closed bug with '-> re-size BGxxxx: set its Points'. 3. Check the bug file: Status Closed - re-sizing changes nothing downstream.

## Proposed Fix

Filter the re-size needs-human bucket to non-terminal units (one authority: the shared terminal-status set in lib/`sdlc_md).` Report terminal legacy-sized units, if at all, as a one-line count ('N terminal units keep legacy sizing - historical, no action').

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 | Filed |
