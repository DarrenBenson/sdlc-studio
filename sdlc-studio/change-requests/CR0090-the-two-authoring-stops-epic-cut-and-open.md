# CR-0090: the two authoring STOPs epic cut and open questions plus autonomy ceiling

> **Status:** Proposed
> **Created:** 2026-06-24
> **Created-by:** sdlc-studio new
> **Priority:** High
> **Type:** Feature

## Summary

**WS1 of RFC0019. Estimate: 3 points. Depends on CR0089.** The two non-negotiable authoring
pauses the field agent identified (RFC0019 D2): **STOP 1 - approve the epic cut** before any
story is written (the highest-stakes call; getting it wrong silently wastes the whole backlog);
**STOP 2 - resolve the PRD's open questions** (or state the assumptions) before story authoring,
since those decisions propagate into every story. Under `--autonomous` both convert to
record-the-assumption-and-proceed (logged to the decisions ledger), per autosprint's existing
autonomy ceiling - not silent.

## Acceptance Criteria

- [ ] STOP 1 presents the proposed epic cut (count, titles, mapping to PRD features) and waits
      for approve/edit before authoring any story
- [ ] STOP 2 surfaces unresolved PRD open questions; the operator answers, or the assumptions
      are recorded (promoted into `decisions.md` via `decisions.py promote`, CR0080)
- [ ] `--autonomous` converts both STOPs to record-and-proceed, logged to the per-tranche
      ledger (never silent); interactive mode keeps them as hard pauses
- [ ] unit/flow tests cover both STOPs + the autonomous ceiling; CHANGELOG entry (LL0004)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-24 | sdlc | Created via `new` (deterministic) |
