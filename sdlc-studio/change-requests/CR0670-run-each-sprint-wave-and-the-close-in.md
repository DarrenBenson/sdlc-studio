# CR-0670: Run each sprint wave, and the close, in a fresh orchestrator session started from a bounded on-disk resume brief, so no session carries earlier waves or the planning conversation

> **Status:** Complete
> **Decomposed-into:** EP0302
> **Parent:** RFC0062
> **Priority:** High
> **Type:** Feature
> **Size:** L
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/SKILL.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py
> **Evidence:** RFC0062 Phase 3, orchestration lens: findings 1 and 3, combo.py replay (B3 8.54M, A 3.97M, B4 9.07M); tool-output lens: finding 2 (0.90M, a subset); ceremony lens: finding 4 (close, inside the replay)
> **Date:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T12:22:54Z

## Summary

Run six's orchestrator cost 15.1M of 37.5M priced (40%): one session of 323 calls that opened at 183k, about 127k of it planning context carried in from the same session, and grew without compaction to 591k. Cache reads were 13.12M of its 15.08M; 5.91M of that is the carry-in re-read 323 times and 7.24M is growth re-read. 228k of the 410k growth was its own xhigh reasoning, about 52k tool results and 29k hand-backs. The close (retro, report, reconcile, close, sign: 24 calls, 1.35M) ran at the same 407k average. Nothing in the sprint workflow mentions session lifetime: a grep for fresh session, /clear or compaction over `reference-sprint*.md` and help/sprint.md finds only the per-unit builder rule. Already true of the tree, not a regression of run six.

## Impact

The orchestrator pays about 0.047M a call at run six's context, so every operator who runs a multi-wave sprint in one session pays it, in this repository and in a consuming project. Replayed (combo.py), three wave sessions of 60k each take the orchestrator from 15.12M to 6.58M.

## Acceptance Criteria

- [ ] `sprint.py handoff` writes a resume brief of at most 8k tokens naming the open run, each unit's lane state, in-flight agent ids, pending verdicts and briefs, the run's rulings, known issues and the next action, and a size-budget test refuses a brief over 8k tokens.
- [ ] `sprint.py resume`, started in a fresh session from that brief, reaches the same next action as the session that wrote it: in a fixture run `sprint.py next` prints the same step before and after the hand-off.
- [ ] reference-sprint.md defines a wave boundary (every lane of the wave accepted, none in flight), routes the close through its own fresh session, and `sprint plan --write` names a fresh session as its next step.
- [ ] The sprint entry reads its own session's size through the token meter and, under `sprint.fresh_session: warn|block` (warn by default), names the projected re-read cost when the session holds more than 80k tokens; block refuses, and a fixture shows both.
- [ ] Before and after: on the next sprint the cost anatomy (US1124) reports the orchestrator's average context per call below 150k against run six's 407k, and flags any run above 150k.

## Recommendation

Add `sprint.py handoff` and `sprint.py resume`, a wave-boundary definition and a fresh-session warning at the sprint entry. Route by harness: headless, the sprint-drive CR starts a fresh orchestrator session per wave on CR0667's lane runner; in Claude Code a thin main thread hands each wave to a fresh non-fork agent if a nesting test shows that agent receives its builders' hand-backs, otherwise the run stops at the boundary for a /clear and resume. Saving 8.54M per run: combo.py replays the 323 calls with the context reset to 60k at the run open and at calls 107 and 214, charging each new session 2 x 60k cache write and 6 orientation calls (conservative 80k start and 12 orientation calls: 7.67M). It includes, counted once, the fresh run open (3.97M), the planning tool output carried in (0.90M, tool-output lens) and most of the close in a small context (ceremony lens, 0.8M; a close session of its own is about the replay's fourth segment, four sessions 9.07M, not carried). Risks: whatever was decided but not written to disk is lost at a boundary (run six's rulings were recorded); a boundary must fall where no lane is in flight, because Claude Code delivers a hand-back only to the session that spawned the agent; the nesting route is untested; a /clear at each boundary would break the no-mid-run-questions norm, so the headless route is the default.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Raised |
