# HO-0075: A run ends with one page it can be judged on, and one act that signs it. `sign` is one command taking one principal, with every step that can change a fact running before it and no batch write accepted after it. The page opens with the sprint goal verbatim, before any figure. Every figure carries the source it was derived from, and a section with no data reads NOT MEASURED by name rather than as a zero. The cost row states what the token meter covers and names the sessions it does not. And the page reads INVALIDATED once its figures no longer re-derive from the tree

> **Date:** 2026-09-18
> **Created-by:** sdlc-studio new
> **Run:** RUN-01M2SPNS (started 2026-09-18T07:20:32Z)
> **Outcome:** running
> **Batch source:** argument

## Where to pick up

9 of 9 unit(s) remain (0 suit copilot-assisted completion, 9 need human judgement). Plan them straight back in:

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/sprint.py" plan \
  --worklist sdlc-studio/.local/handoff-worklist.txt --order wsjf
```

Each item below names the pointer to start from: the failing AC, the check it stalled at, the blocker that stopped it, or the file it was to touch.

## Unanswered stop-ship questions

None: every batch unit is delivered, abandoned, ruled, dropped, parked or awaiting only a signature. Rulings read from RETRO0118's `## Known issues carried` for RUN-01M2SPNS.

## Appetite

- **Declared:** wall-clock 5760 min, units 64 unit(s)
- **Spent:** 777.9 min, 0 unit(s) terminal
- **Delivered:** 0 unit(s)
- **Token forecast:** ~4,410,787 tokens - a plan-time estimate, never a gate (the total is transcript-measured but a LOWER BOUND - delegated spend is supplied, not observed)

## Delivered (0)

_Nothing was delivered in this run._

## Remaining (9)

### US0832 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0832-close-splits-into-prepare-which-does-everything-that.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:already-satisfied

### US0833 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/critic.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/transition.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_transition.py` - declared Affects
- **file:** `sdlc-studio/stories/US0833-sign-writes-the-principal-the-date-and-the.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:already-satisfied

### US0834 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0834-prepare-refuses-to-produce-a-report-while-any.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0835 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint_report.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/lib/sdlc_md.py` - declared Affects
- **file:** `sdlc-studio/stories/US0835-the-report-json-of-record-is-derived-from.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:already-satisfied

### US0836 (story, Review) - judgement

- **issue:** `weak-AC` - tranche audit
- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint_report.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/templates/core/sprint-report.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/templates/reports/sprint-report.html` - declared Affects
- **file:** `sdlc-studio/stories/US0836-the-markdown-twin-and-the-html-rendering-are.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:weak-AC, issue:already-satisfied

### US0837 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint_report.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py` - declared Affects
- **file:** `sdlc-studio/stories/US0837-the-report-opens-with-the-sprint-goal-verbatim.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0844 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/lib/run_state.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_run_state.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/sprint_report.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py` - declared Affects
- **file:** `sdlc-studio/stories/US0844-the-run-level-token-meter-is-stamped-at.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:already-satisfied

### US0845 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint_report.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/status.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_status.py` - declared Affects
- **file:** `sdlc-studio/stories/US0845-a-report-whose-fingerprint-no-longer-matches-the.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:already-satisfied

### US0846 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/sprint_report.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py` - declared Affects
- **file:** `sdlc-studio/stories/US0846-the-report-computes-this-run-s-change-failure.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

## Open decisions

| Ref | Decision | Where |
| --- | --- | --- |
| D0050 | BG0246's fix stands as ruled in D0047 (include interactive sprints, derive per-unit from the total, label each row), but D0047's RATIONALE contained a false claim which is withdrawn: including those sprints does NOT unstick the 'N units of its own evidence' counter | decisions.md (`sdlc-studio/decisions.md`) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-18 | sdlc-studio | Generated at the run close (`handoff generate`) |
