# BG0210: every successful close immediately owes another one: derived epics never enter a retro Batch, so close-owed can never reach zero

> **Status:** Fixed
> **Verification depth:** functional (RED-first; all four branches mutation-pinned; real-repo count 44 to 12 with every survivor hand-checked)
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/close_owed.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/retro.py
> **Created:** 2026-07-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

`close_owed` treats epics as delivery units and considers a unit accounted for only when some retro's Batch field names it. apply-signoff derives parent epics terminal as its tail, AFTER the retro is written, and nothing adds them to any Batch. So the moment RUN-01KXVYGR closed cleanly - 28 units signed off, 7 epics derived Done - status reported a close owed for those same 7 epics. The condition is unclearable by closing: the next retro would cover them only if someone hand-added them, and it would derive its own epics in turn. Across the repo's history that is about 38 epics (EP0046 to EP0084) making up most of the 44 units currently reported, so the headline number is largely false. A detector that reports a permanent, growing, unclearable debt is one people learn to skim past, which is the failure mode it exists to prevent - and the same shape as the noise-gate baseline this sprint already fixed.

## Steps to Reproduce

1. Close a sprint whose stories roll up parent epics: sprint close --retro RETROxxxx --apply-signoff --principal NAME. 2. Observe the tail line deriving parent epics Done. 3. Run status.py pillars or `close_owed.py` detect. 4. Observe those same epics listed as terminal with no retro accounting for them.

## Proposed Fix

Have the close write the epics it derived into the retro's Batch as part of the apply-signoff tail, so the retro accounts for everything that close made terminal. Alternatively exclude derived parents from the close-owed census and count only the units a sprint plans - but recording them is better, because the epic is a real delivery unit and its close is what the retro is describing. Either way the detector must be able to reach zero.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Filed |
