# HO-0033: Every gate the audit showed silently standing down or silently passing fails loud, and no terminal artefact carries a claim its own verifier contradicts

> **Date:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Run:** RUN-01KYHVWK (started 2026-07-27T13:08:23Z)
> **Outcome:** goal-reached
> **Batch source:** run-state.json

## Where to pick up

5 of 21 unit(s) remain (0 suit copilot-assisted completion, 5 need human judgement). Plan them straight back in:

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/sprint.py" plan \
  --worklist sdlc-studio/.local/handoff-worklist.txt --order wsjf
```

Each item below names the pointer to start from: the failing AC, the check it stalled at, the blocker that stopped it, or the file it was to touch.

## Appetite

- **Declared:** wall-clock 960 min, units 64 unit(s)
- **Spent:** 617.6 min, 16 unit(s) terminal
- **Delivered:** 16 unit(s)
- **Token forecast:** ~4,239,012 tokens - a plan-time estimate, never a gate (a script cannot observe token spend)

## Delivered (16)

| Unit | Type | Status | Evidence |
| --- | --- | --- | --- |
| [BG0302](../../sdlc-studio/bugs/BG0302-conformance-adopt-after-still-310-after-d0055-s.md) | bug | Fixed | no verifier or verdict on record |
| [BG0303](../../sdlc-studio/bugs/BG0303-done-stories-executable-verify-lines-have-rotted-renamed.md) | bug | Fixed | no verifier or verdict on record |
| [BG0304](../../sdlc-studio/bugs/BG0304-39-done-stories-ship-a-literal-role-user.md) | bug | Fixed | no verifier or verdict on record |
| [BG0305](../../sdlc-studio/bugs/BG0305-parse-story-s-naive-fence-toggle-executes-verify.md) | bug | Fixed | no verifier or verdict on record |
| [BG0306](../../sdlc-studio/bugs/BG0306-origin-drift-pre-flight-reports-clean-when-the.md) | bug | Fixed | no verifier or verdict on record |
| [BG0314](../../sdlc-studio/bugs/BG0314-force-claims-recorded-as-an-override-but-no.md) | bug | Fixed | no verifier or verdict on record |
| [BG0315](../../sdlc-studio/bugs/BG0315-cmd-set-s-one-call-close-neither-pre.md) | bug | Fixed | no verifier or verdict on record |
| [BG0316](../../sdlc-studio/bugs/BG0316-done-gate-waves-through-acs-with-no-verify.md) | bug | Fixed | no verifier or verdict on record |
| [BG0317](../../sdlc-studio/bugs/BG0317-skipped-pytest-test-stamps-an-ac-green-on.md) | bug | Fixed | no verifier or verdict on record |
| [BG0321](../../sdlc-studio/bugs/BG0321-eval-gate-can-print-gate-pass-while-a.md) | bug | Fixed | no verifier or verdict on record |
| [BG0322](../../sdlc-studio/bugs/BG0322-pvd-sync-mode-symlink-reports-synced-and-exits.md) | bug | Fixed | no verifier or verdict on record |
| [BG0323](../../sdlc-studio/bugs/BG0323-provenance-check-silently-reports-an-unreadable-artifact-as.md) | bug | Fixed | no verifier or verdict on record |
| [BG0324](../../sdlc-studio/bugs/BG0324-github-sync-cascade-conflates-a-gh-failure-with.md) | bug | Fixed | no verifier or verdict on record |
| [BG0325](../../sdlc-studio/bugs/BG0325-readiness-gate-reports-every-unit-ready-and-exits.md) | bug | Fixed | no verifier or verdict on record |
| [BG0326](../../sdlc-studio/bugs/BG0326-remote-aware-id-allocation-silently-degrades-to-local.md) | bug | Fixed | no verifier or verdict on record |
| [BG0329](../../sdlc-studio/bugs/BG0329-test-relevance-measurement-records-only-paths-that-exist.md) | bug | Fixed | no verifier or verdict on record |

## Remaining (5)

### US0447 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/lib/sdlc_md.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py` - declared Affects
- **file:** `sdlc-studio/stories/US0447-a-shared-reader-parses-the-design-persona-registry.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0448 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/artifact.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_artifact.py` - declared Affects
- **file:** `sdlc-studio/stories/US0448-artifact-py-resolves-persona-through-the-registry-the.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0449 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/artifact.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/refine.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_refine.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/tests/test_artifact.py` - declared Affects
- **file:** `sdlc-studio/stories/US0449-the-batch-and-refine-minting-paths-resolve-the.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:high, issue:already-satisfied

### US0450 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `sdlc-studio/prd.md` - declared Affects
- **file:** `tools/tests/test_persona_coherence.py` - declared Affects
- **file:** `sdlc-studio/stories/US0450-the-prd-target-users-section-names-the-registry.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:low, issue:already-satisfied

### US0451 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `sdlc-studio/personas.md` - declared Affects
- **file:** `sdlc-studio/personas/index.md` - declared Affects
- **file:** `tools/tests/test_persona_coherence.py` - declared Affects
- **file:** `sdlc-studio/stories/US0451-personas-md-is-labelled-a-legacy-appendix-whose.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:low, issue:already-satisfied

## Open decisions

| Ref | Decision | Where |
| --- | --- | --- |
| D0050 | BG0246's fix stands as ruled in D0047 (include interactive sprints, derive per-unit from the total, label each row), but D0047's RATIONALE contained a false claim which is withdrawn: including those sprints does NOT unstick the 'N units of its own evidence' counter | decisions.md (`sdlc-studio/decisions.md`) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Generated at the run close (`handoff generate`) |
