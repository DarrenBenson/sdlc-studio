# HO-0007: The gate and close chain report their own state honestly: freshness is fingerprinted, refusals and skips are named not silent, and a failure is attributed once to its real cause

> **Date:** 2026-07-18
> **Created-by:** sdlc-studio new
> **Run:** RUN-01KXT0YV (started 2026-07-18T06:59:57Z)
> **Outcome:** goal-reached
> **Goal:** plan
> **Batch source:** run-state.json

## Where to pick up

8 of 9 unit(s) remain (0 suit copilot-assisted completion, 8 need human judgement). Plan them straight back in:

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/sprint.py" plan \
  --worklist sdlc-studio/.local/handoff-worklist.txt --order wsjf
```

Each item below names the pointer to start from: the failing AC, the check it stalled at, the blocker that stopped it, or the file it was to touch.

## Appetite

- **Declared:** wall-clock 420 min, units 9 unit(s)
- **Spent:** 158.5 min, 1 unit(s) terminal
- **Delivered:** 1 unit(s)
- **Token forecast:** ~650,000 tokens - a plan-time estimate, never a gate (a script cannot observe token spend)

## Delivered (1)

| Unit | Type | Status | Evidence |
| --- | --- | --- | --- |
| [BG0190](../../sdlc-studio/bugs/BG0190-apply-signoff-tail-does-not-derive-parent-epics.md) | bug | Fixed | no verifier or verdict on record |

## Remaining (8)

### US0216 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/gate.py` - declared Affects
- **file:** `sdlc-studio/stories/US0216-gate-mutation-lane-surfaces-the-refused-red-baseline.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0213 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/verify_ac.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/transition.py` - declared Affects
- **file:** `sdlc-studio/stories/US0213-verify-ac-freshness-fingerprints-the-ac-section-not.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

### US0219 (story, Review) - judgement

- **issue:** `unmet-deps: US0216:Review` - tranche audit
- **issue:** `already-satisfied` - tranche audit
- **file:** `.githooks/pre-commit` - declared Affects
- **file:** `tools/gate_timing.py` - declared Affects
- **file:** `sdlc-studio/stories/US0219-gate-tracks-the-test-suite-runtime-and-warns.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:trivial, issue:unmet-deps, issue:already-satisfied

### US0220 (story, Review) - judgement

- **issue:** `unmet-deps: US0219:Review` - tranche audit
- **issue:** `already-satisfied` - tranche audit
- **file:** `.githooks/pre-commit` - declared Affects
- **file:** `tools/gate_timing.py` - declared Affects
- **file:** `sdlc-studio/stories/US0220-gate-skips-the-unit-suite-for-test-irrelevant.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:trivial, issue:unmet-deps, issue:already-satisfied

### US0217 (story, Review) - judgement

- **issue:** `unmet-deps: US0220:Review` - tranche audit
- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/conformance.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/gate.py` - declared Affects
- **file:** `sdlc-studio/stories/US0217-a-global-doc-coverage-failure-is-attributed-once.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:unmet-deps, issue:already-satisfied

### US0215 (story, Review) - judgement

- **issue:** `unmet-deps: US0217:Review` - tranche audit
- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/gate.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0215-review-current-distinguishes-an-uncommitted-but-current-latest.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:unmet-deps, issue:already-satisfied

### US0214 (story, Review) - judgement

- **issue:** `unmet-deps: US0215:Review` - tranche audit
- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/review_prep.py` - declared Affects
- **file:** `.claude/skills/sdlc-studio/scripts/sprint.py` - declared Affects
- **file:** `sdlc-studio/stories/US0214-review-close-ensures-its-rv-index-row-is.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:unmet-deps, issue:already-satisfied

### US0218 (story, Review) - judgement

- **issue:** `already-satisfied` - tranche audit
- **file:** `.claude/skills/sdlc-studio/scripts/mutation.py` - declared Affects
- **file:** `sdlc-studio/stories/US0218-bounded-mutation-biases-its-sample-toward-changed-lines.md` - the unit itself
- **Suitability:** judgement (confidence high) - seeded by difficulty:medium, issue:already-satisfied

## Open decisions

_None recorded._ Rulings made during the run live in the tranche ledger (`sdlc-studio/decisions/`); settled decisions belong in `sdlc-studio/decisions.md`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-18 | sdlc-studio | Generated at the run close (`handoff generate`) |
