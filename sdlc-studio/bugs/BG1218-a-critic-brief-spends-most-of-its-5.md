# BG1218: A critic brief spends most of its 5 to 13 s in the per-unit affect-key parse, and a refused brief still renders before the self-check gate

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/backlog_triage.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_corpus_cache.py, changelog.d/BG1218.md, .claude/skills/sdlc-studio/scripts/tests/test_backlog_triage.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** BG1114 round-1 verdict, scratchpad run5/BG1114-verdict-r1.txt.
> **Created:** 2026-11-04
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-04T19:15:36Z

## Summary

2026-11-04, BG1114's review (pre-existing). BG1114 put the brief inside the corpus cache, but `reconcile.unit_corpus` already opened its own, so a brief is no faster. A profile put 6.25 s of a 7.75 s brief in `unit_corpus`, mostly `backlog_triage._affect_key`: 3.3 s over 9,828 calls through `resolve_affects`, `loaded_skill_dir` and Path.resolve. Separately, `cmd_brief` runs `_self_check_gate` only after rendering (critic.py:4181 after 4169, 4145 after 4139), so an author refused for a missing self-check still waits for the whole brief.

## Steps to Reproduce

1. Profile `critic.py brief --unit <id> --seat qa`.
2. Brief a unit with no recorded self-check and time the refusal.

## Proposed Fix

Memoise the affect keys per corpus walk, and run the self-check gate before rendering.

## Acceptance Criteria

- [ ] **AC1** A refused brief returns before rendering, and `_affect_key` is computed once per unit per walk.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_corpus_cache.py

## Impact

Every review brief costs 5 to 13 s of a run, and a refused one costs the same for nothing.

## Resolution

Won't Fix under D0613: the operator approved the product seat's second proposal (D0562) because a user can meet it, but it is rare and harmless and has a workaround, so fixing it costs more than it returns. A brief takes 5 to 13 s; slow but correct.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-04 | claude | Filed |
| 2026-11-04 | sdlc-studio | Retitled: was "A critic brief spends most of its 5 to 13 s in `unit_corpus`'s per-unit `_affect_key` parse, and a refused brief still renders before the self-check gate" |
| 2026-11-24 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0613: the operator approved the product seat's second list (D0562); reason in Resolution |
