# BG0173: Refute-panel verdicts silently count failed skeptic votes as refutations - an outage mid-panel mass-refutes candidates and the audit reports the wrong survivor set as complete

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/reference-audit.md, .claude/skills/sdlc-studio/templates/automation/audit-refute.md
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5; agent; audit-process-retro wf_9903a6e6-53a
> **Delivered-by:** claude-opus-4-8

## Summary

The refute-panel spec (survive on >=M of N votes) says nothing about a skeptic vote FAILING to arrive. The natural implementation - drop dead votes, count non-refutations against the fixed threshold - converts an infrastructure outage into mass refutation: a candidate whose 3 skeptics all died has 0 non-refutations and is scored refuted. Observed live on 2026-07-16: a session-limit outage killed 95 refuter agents mid-run; the audit completed and reported 34 survivors / 46 refuted as a finished verdict. Re-running the dead votes with full panels gave the true verdict: 61 survivors / 19 refuted. 27 verified findings were silently mislabelled refuted - the exact silent-misleading-failure class LL0009 names, in the tool whose job is catching it.

## Steps to Reproduce

1. Run an audit fan-out with a 3-vote refute panel per reference-audit.md. 2. Kill some refuter agents mid-run (session limit, network, any terminal agent error - agent() returns null). 3. Observe candidates with incomplete panels scored refuted (0 or 1 arrived non-refutations < threshold 2) and the run reporting a complete-looking survivors/refuted split with no unjudged count.

## Proposed Fix

Specify in reference-audit.md#audit-refute and templates/automation/audit-refute.md: a candidate's verdict is valid only if all N votes arrived (or threshold scaled to arrived votes with a minimum quorum); an incomplete panel marks the candidate UNJUDGED, never refuted; the run report must carry an unjudged count and fail loud (or auto-resume) when it is non-zero.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 | Filed |
