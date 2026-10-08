# CR-0627: goal-review brief is identical for every seat - give each seat its own lens and persona card

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Feature
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/persona_resolve.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_persona_resolve.py
> **Evidence:** homelab RUN-01M4EMNN goal review, 2026-10-08
> **Date:** 2026-10-08
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-08T21:01:23Z

## Summary

`sprint goal-review brief --seat product|qa|engineering|sre` produced byte-identical text in the homelab (2026-10-08). The seat only matters when its verdict is recorded; the brief itself carries no role framing, no persona card, and no seat-specific questions, so the orchestrator has to hand-write each seat's lens (which it did, for five seats including a served-persona lens). Proposal: the brief renders the seat's persona card (`persona_resolve` --render review) and a role-specific question set - product: does the increment serve the named persona's goals; QA: which criteria are manual-only and could be executable; engineering: build order, rollback, shared files; SRE: which failures alarm and how each alarm is proven by induction; served persona (CR0621): the standing criteria that persona needs. Pairs with CR0620 (seats chosen by what a change touches).

## Acceptance Criteria

_None yet: add them here, or on the stories `refine` decomposes this into._

## Triage

- Confirmed at be92626b: `_compose_seat_brief` (sprint.py:11059) takes no seat, so `goal-review brief --seat <any>` composes the same text; the seat matters only when its verdict is recorded.
- Priority Medium stands; Size M (render the seat's review card through `persona_resolve` and a per-role question set). Related: CR-0620 and CR-0622 (which seats review), CR-0621 (a served persona's standing criteria as a lens) and BG1002 (the same brief's stale fields); refine with them.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-08 | sdlc-studio | Raised |
| 2026-10-09 | Claude Opus 5.5 (triage) | Triaged: confirmed; Affects made repository paths; Size M; relations recorded |
