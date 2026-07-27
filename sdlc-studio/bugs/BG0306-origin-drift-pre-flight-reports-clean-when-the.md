# BG0306: Origin-drift pre-flight reports clean when the fetch itself fails - even under --strict

> **Status:** Open
> **Severity:** High
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_rolling.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0

## Summary

The stale-checkout gate discards the result of git fetch (and folds a failed rev-list into behind=0), so a machine that cannot reach the remote computes behind=0, prints nothing, and passes - including under --strict, whose documented contract is to refuse exactly the stale checkout this failure produces. 'Up to date' and 'could not ask the remote' are conflated, the LL0018 failure class by name.

## Steps to Reproduce

Evidence (`origin_drift()` lines 2417-2441; _git() lines 2396-2402; `_origin_drift_preflight()` lines 2495-2513): Line 2427 drops the fetch result with a '# best-effort; ignore failure' comment;_git returns None on any exception; lines 2431-2432 leave behind=0 on rev-list failure; `_drift_warning` returns None at behind=0 so nothing is printed and --strict does not refuse.

## Proposed Fix

Capture the fetch and rev-list results; on failure emit an 'origin unreachable - drift unverifiable' warning, and under --strict return the refusal exit code instead of a silent pass.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Filed |
| 2026-07-27 | Claude Fable 5 | Affects corrected to the fix footprint incl. its test file (BG0343: the filer wrote the evidence location) |
| 2026-07-27 | Claude Fable 5 | Triaged vs US0099/US0231 (already-delivered advisory): distinct - those stories deliver fetch+compare and strict refusal on divergence; this bug is the fetch itself failing being reported clean, a path their ACs never cover. Stays Open. |
