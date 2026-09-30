# HO-0092: Jonah's team installs v6 via Claude Code or Copilot CLI; migrate predicts the gate's reconcile, conformance, validate and floor failures

> **Date:** 2026-09-30
> **Created-by:** sdlc-studio new
> **Run:** RUN-01M3RPSK (started 2026-09-30T08:17:59Z)
> **Outcome:** running
> **Goal:** done
> **Batch source:** argument

## Where to pick up

7 of 7 unit(s) remain (0 suit copilot-assisted completion, 7 need human judgement). Plan them straight back in:

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/sprint.py" plan \
  --worklist sdlc-studio/.local/handoff-worklist.txt --order wsjf
```

Each item below names the pointer to start from: the failing AC, the check it stalled at, the blocker that stopped it, or the file it was to touch.

## Unanswered stop-ship questions

None: every batch unit is delivered, abandoned, ruled, dropped, parked or awaiting only a signature. No retro's carried table could be read for RUN-01M3RPSK, so no ruling answers any unit.

## Appetite

- **Declared:** wall-clock 5760 min, units 64 unit(s)
- **Spent:** 261.1 min, 0 unit(s) terminal
- **Delivered:** 0 unit(s)
- **Token forecast:** ~3,745,392 tokens - a plan-time estimate, never a gate (the total is transcript-measured but a LOWER BOUND - delegated spend is supplied, not observed)

## Delivered (0)

_Nothing was delivered in this run._

## Remaining (7)

### BG0842 (bug, In Progress) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/project_upgrade.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_project_upgrade.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/gate.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_gate.py` - declared Affects
- **file:** `changelog.d/BG0842.md` - declared Affects
- **file:** `sdlc-studio/bugs/BG0842-migrate-reports-2-index-drift-items-on-a.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:already-satisfied

### BG0844 (bug, In Progress) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/project_upgrade.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_project_upgrade.py` - declared Affects
- **file:** `changelog.d/BG0844.md` - declared Affects
- **file:** `sdlc-studio/bugs/BG0844-an-upgraded-project-never-gets-the-sdlc-studio.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### BG0843 (bug, In Progress) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/migrate.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_migrate.py` - declared Affects
- **file:** `changelog.d/BG0843.md` - declared Affects
- **file:** `sdlc-studio/bugs/BG0843-migrate-names-no-engagement-floor-cutoff-so-a.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### BG0845 (bug, In Progress) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/migrate.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_lean_migrate_cutoff.py` - declared Affects
- **file:** `changelog.d/BG0845.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_migrate.py` - declared Affects
- **file:** `sdlc-studio/bugs/BG0845-migrate-s-conformance-cutoff-on-a-v4-1.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### BG0853 (bug, In Progress) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/templates/agent-instructions.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/templates/agent-instructions.README.md` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/init.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/validate.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_validate.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/project_upgrade.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_init.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_project_upgrade.py` - declared Affects
- **file:** `changelog.d/BG0853.md` - declared Affects
- **file:** `sdlc-studio/bugs/BG0853-the-agent-instructions-template-names-the-claude-code.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:already-satisfied

### BG0854 (bug, In Progress) - judgement

- **issue:** `unmet-deps: BG0842:In Progress, BG0843:In Progress, BG0844:In Progress, BG0845:In Progress` - tranche audit
- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/project_upgrade.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/migrate.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_project_upgrade.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_migrate.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_lean_migrate_gate_agree.py` - declared Affects
- **file:** `changelog.d/BG0854.md` - declared Affects
- **file:** `sdlc-studio/bugs/BG0854-nothing-runs-migrate-and-then-the-gate-on.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:unmet-deps, issue:already-satisfied

### BG0856 (bug, In Progress) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `install.sh` - declared Affects
- **file:** `docs/INSTALL.md` - declared Affects
- **file:** `tools/tests/test_install_copilot_global.py` - declared Affects
- **file:** `changelog.d/BG0852.md` - declared Affects
- **file:** `changelog.d/BG0856.md` - declared Affects
- **file:** `sdlc-studio/bugs/BG0856-bg0852-did-not-converge-in-review-round-2.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

## Open decisions

| Ref | Decision | Where |
| --- | --- | --- |
| D0050 | BG0246's fix stands as ruled in D0047 (include interactive sprints, derive per-unit from the total, label each row), but D0047's RATIONALE contained a false claim which is withdrawn: including those sprints does NOT unstick the 'N units of its own evidence' counter | decisions.md (`sdlc-studio/decisions.md`) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-30 | sdlc-studio | Generated at the run close (`handoff generate`) |
