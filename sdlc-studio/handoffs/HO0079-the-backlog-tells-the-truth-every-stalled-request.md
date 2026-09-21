# HO-0079: the backlog tells the truth: every stalled request and stale finding carries a dated ruling, and the state that let them accumulate cannot rebuild

> **Date:** 2026-09-21
> **Created-by:** sdlc-studio new
> **Run:** RUN-01M306PY (started 2026-09-20T20:04:04Z)
> **Outcome:** running
> **Batch source:** argument

## Where to pick up

7 of 8 unit(s) remain (0 suit copilot-assisted completion, 7 need human judgement). Plan them straight back in:

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/sprint.py" plan \
  --worklist sdlc-studio/.local/handoff-worklist.txt --order wsjf
```

Each item below names the pointer to start from: the failing AC, the check it stalled at, the blocker that stopped it, or the file it was to touch.

## Unanswered stop-ship questions

None: every batch unit is delivered, abandoned, ruled, dropped, parked or awaiting only a signature. No retro's carried table could be read for RUN-01M306PY, so no ruling answers any unit.

## Appetite

- **Declared:** wall-clock 5760 min, units 64 unit(s)
- **Spent:** 876.3 min, 1 unit(s) terminal
- **Delivered:** 1 unit(s)
- **Token forecast:** ~4,208,715 tokens - a plan-time estimate, never a gate (the total is transcript-measured but a LOWER BOUND - delegated spend is supplied, not observed)

## Delivered (1)

| Unit | Type | Status | Evidence |
| --- | --- | --- | --- |
| [BG0718](../../sdlc-studio/bugs/BG0718-the-seal-widens-the-dora-window-it-is.md) | bug | Fixed | 6/6 AC(s) verified |

## Remaining (7)

### US0848 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/backlog_triage.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_backlog_triage.py` - declared Affects
- **file:** `sdlc-studio/stories/US0848-the-guard-a-discovery-request-in-progress-with.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:low, issue:already-satisfied

### US0849 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `sdlc-studio/change-requests` - declared Affects
- **file:** `sdlc-studio/rfcs` - declared Affects
- **file:** `sdlc-studio/stories/US0849-rule-the-close-and-ceremony-cluster-against-head.md` - the unit itself
- **Suitability:** judgement (confidence low) - seeded by difficulty:low, issue:already-satisfied

### US0850 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `sdlc-studio/change-requests` - declared Affects
- **file:** `sdlc-studio/rfcs` - declared Affects
- **file:** `sdlc-studio/stories/US0850-rule-the-review-and-critic-cluster-against-head.md` - the unit itself
- **Suitability:** judgement (confidence low) - seeded by difficulty:low, issue:already-satisfied

### US0851 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `sdlc-studio/change-requests` - declared Affects
- **file:** `sdlc-studio/rfcs` - declared Affects
- **file:** `sdlc-studio/stories/US0851-rule-the-evidence-and-mutation-cluster-against-head.md` - the unit itself
- **Suitability:** judgement (confidence low) - seeded by difficulty:low, issue:already-satisfied

### US0852 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `sdlc-studio/change-requests` - declared Affects
- **file:** `sdlc-studio/rfcs` - declared Affects
- **file:** `sdlc-studio/stories/US0852-rule-the-config-docs-and-remaining-requests-against.md` - the unit itself
- **Suitability:** judgement (confidence low) - seeded by difficulty:low, issue:already-satisfied

### US0853 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `sdlc-studio/bugs` - declared Affects
- **file:** `sdlc-studio/change-requests` - declared Affects
- **file:** `sdlc-studio/stories/US0853-re-triage-bg0463-s-twenty-batch-boundary-findings.md` - the unit itself
- **Suitability:** judgement (confidence low) - seeded by difficulty:low, issue:already-satisfied

### US0854 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `sdlc-studio/stories` - declared Affects
- **file:** `sdlc-studio/stories/US0854-decompose-the-four-8-point-stories-and-resolve.md` - the unit itself
- **Suitability:** judgement (confidence low) - seeded by difficulty:low, issue:already-satisfied

## Open decisions

| Ref | Decision | Where |
| --- | --- | --- |
| D0050 | BG0246's fix stands as ruled in D0047 (include interactive sprints, derive per-unit from the total, label each row), but D0047's RATIONALE contained a false claim which is withdrawn: including those sprints does NOT unstick the 'N units of its own evidence' counter | decisions.md (`sdlc-studio/decisions.md`) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-21 | sdlc-studio | Generated at the run close (`handoff generate`) |
