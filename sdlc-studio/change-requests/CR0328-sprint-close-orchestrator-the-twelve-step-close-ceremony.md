# CR-0328: sprint close orchestrator: the twelve-step close ceremony as one deterministic command ending in the decision brief

> **Status:** Proposed
> **Priority:** High
> **Type:** Feature
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/reference-sprint.md
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5; agent; seams-sprint retro RUN-01KXPA4N

## Summary

The review close became one command (CR0307); the sprint close is the last big hand-carried ceremony. Ship `sprint close --retro RETROxxxx [--goal-verdict achieved|partial|missed --note ...]`: orchestrates the deterministic chain (goal-verdict recording, retro validate + extract + lessons summary, gate --require-retro, handoff generate, reconcile detect) with fail-loud stops at each gate, then PRINTS the sign-off decision brief (deliveries, critic verdicts with their REJECT histories from the ledger, gate/mutation results, forecast-vs-measured-subagent spend) for the reviewer-of-record ask. Judgement steps stay outside: writing the retro's content, the goal verdict's note, and the signature itself remain human/agent work - the orchestrator sequences and refuses, never invents. Composes with CR0323 (the two-role gate) and CR0318 (the brief).

## Impact

Both of today's sprint closes were ~12 hand-sequenced steps (goal-verdict, scoped mutation runs, retro mint/validate/extract, lessons summary, close gate, handoff, reconcile, commit, forward-port, sign-off brief) - executed correctly twice, but each step is a skippable seam under a less careful run, and RFC0042 only gated the OUTCOME, not the sequencing.

## Acceptance Criteria

- [ ] sprint close runs the chain in order and STOPS loudly at the first failing gate, naming the remedy; a re-run after repair resumes idempotently
- [ ] The printed decision brief carries per-unit deliveries, each unit's verdict + reject history from critic-verdicts.md, gate and mutation results, and forecast vs measured subagent spend - the CR0318 content, composed not hand-written
- [ ] Nothing is invented: absent retro content, an unset goal, or an unjudged goal-verdict are refusals with the command to run, never defaults

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 | Raised |
