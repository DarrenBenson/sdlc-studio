# BG0181: retro accuracy reads parenthetical ids in the Batch line as rateable units

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Delivered-by:** claude-opus-4-8

## Summary

retro accuracy --write on RETRO0044 reported 'UNFORECAST: EP0063, EP0070, CR0314, RFC0043, RFC0044' - none of those are delivery units; they came from the parenthetical provenance in the Batch line ('(EP0063-EP0070, from CR0314/... RFC0043...)'). Only the delivery units (US/BG ids) carry plan-time forecasts, so the epic/CR/RFC mentions are noise that pads the UNFORECAST list and obscures the real signal. `batch_ids` (or accuracy's consumer) should scope to delivery-unit types, or to the ids before the parenthetical.

## Steps to Reproduce

1. write a retro whose Batch line carries the conventional '(EPxxxx-EPyyyy, from CRxxxx...)' parenthetical; 2. retro.py accuracy --id RETROxxxx; 3. epics/CRs/RFCs appear in the UNFORECAST list

## Proposed Fix

Filter accuracy's rateable set to delivery-unit types (story/bug), or parse the Batch line only up to the parenthetical

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Filed |
