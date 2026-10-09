# CR-0633: The learning loop: at the retro each seat is scored on its own verdicts and writes what it will do differently, approved by another seat

> **Status:** Proposed
> **Parent:** RFC0061
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/persona_memory.py, .claude/skills/sdlc-studio/reference-retro.md, .claude/skills/sdlc-studio/reference-persona.md
> **Priority:** High
> **Type:** Feature
> **Size:** L

## Summary

RFC0061 workstream 3 (D2, D3, D4). At the retro, each seat's verdicts are scored mechanically from the verdict ledger against what followed: an APPROVE on a unit later found defective, a REJECT finding later overturned, a defect found only in a later round, rounds to converge, operator rulings naming it, closing-review and consuming-project findings. A context framed as that persona is briefed with its own record and writes its learning in its own words; a different seat reviews it against the evidence; the learnings are listed on the retro the operator signs, where the operator can strike any. Depends on CR0619 (verdicts recorded as the reviewer wrote them, EP0280) and BG1003 (authorised rounds recordable).

## Acceptance Criteria

- [ ] A retro proposes, for each seat that reviewed in the run, the evidence of its verdicts against outcomes, and records the learning that seat wrote with the approving seat
- [ ] A learning the operator strikes on the signed retro never reaches the persona's brief

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | Claude Opus 5.5 | Created via `new` (deterministic) |
