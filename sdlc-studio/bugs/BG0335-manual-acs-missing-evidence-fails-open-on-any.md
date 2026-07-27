# BG0335: _manual_acs_missing_evidence fails open on any exception, silently disarming the manual-evidence Done gate

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d carry-over, run wf_d141ccb5); agent; skill v5.0.0

## Summary

The helper wraps its `verify_ac` import and `parse_story` call in 'except Exception: return []', so any import or parse failure is indistinguishable from 'every manual AC carries a passing human verdict'; for an all-manual story the gate then returns None and waves it to Done with nothing looked at, while the comment claims the opposite intent.

## Steps to Reproduce

Evidence (`_manual_acs_missing_evidence` lines 122-126, consumed by `_done_verify_gate` lines 152-159): Confirmed at transition.py 122-126: bare 'except Exception: return []' annotated 'a parse hiccup must not mask the gate'; `_done_verify_gate` treats [] as gate-satisfied and returns None when no executable ACs exist.

## Proposed Fix

Make the exception path fail loud: return a sentinel (or raise) that `_done_verify_gate` turns into a block reason such as 'manual-evidence check could not run (parse/import failure) - fix the story or tooling before Done', symmetric with the executable leg's honest degrade.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d carry-over, run wf_d141ccb5) | Filed |
