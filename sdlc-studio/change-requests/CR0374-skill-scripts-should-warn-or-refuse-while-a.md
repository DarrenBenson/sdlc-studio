# CR-0374: skill scripts should warn or refuse while a mutation run's mutant may be on disk

> **Status:** In Progress
> **Decomposed-into:** EP0135
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/mutation.py
> **Date:** 2026-07-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

A mutation evidence run applies mutants to the live working tree one at a time for minutes at a stretch. During this sprint's close the whole session had to freeze - no artifact.py, no transition, no reconcile - because any concurrently invoked skill script could execute a mutated sibling and misbehave with no indication, and a concurrently running review subagent's test repros risked false findings for the same reason. The single-writer rule exists as doctrine, but nothing mechanical enforces or even surfaces it: the in-flight sidecar (mutation-inflight.json) already marks the exact window a mutant is applied, and no script reads it. Observed live at the RUN-01KXZQF0 close: the operator-side agent serialised by hand and delayed the review to avoid contaminated evidence.

## Impact

any project running mutation evidence in a shared session or beside subagents; the failure mode is silent wrong behaviour attributed to the wrong cause

## Acceptance Criteria

- [ ] a skill script entry point invoked while mutation-inflight.json exists prints a loud warning naming the mutated file (or refuses, for write-path scripts), so concurrent execution of a mutant is visible instead of silent
- [ ] the mutation run's own processes are exempt, and a stale sidecar (the recovery case) still recovers exactly as today

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Raised |
