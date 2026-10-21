# CR-0638: The release verify lane has no vitest batch path, so in a vitest project every criterion is a cold `npx vitest run` spawn and the lane runs at three times its declared 600 s budget

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Date:** 2026-10-12
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-12T13:04:56Z

## Summary

`gate._verify_acs` batches jest (`jest_batch_cache`: one `npx jest --json` run) and pytest, and falls back to a per-criterion subprocess for everything else. A vitest project has neither: `jest_batch_cache` fails (no jest) and returns [], and because the `vitest` verb folds its tail into -t and calls a bare binary (BG1023), criteria are written `shell npx vitest run <file> -t "<name>"`, which run one cold vitest start each. A consuming project's run (2026-10-12, RUN-01M4QTY2): 562 executable criteria took 1,800 s, reported by the lane itself as 'OVER the 600s declared budget'; the whole `--release` gate took 30 min. A repair loop over the AC corpus is therefore ~40 min per iteration.

## Impact

The release gate in a vitest project is slow enough that it is run rarely, which is how its verify lane went unrun for months.

## Acceptance Criteria

- [ ] In a vitest project the release verify lane resolves file-scoped vitest criteria from one batched vitest JSON run, falls back per criterion only where the batch cannot answer, and a fixture corpus shows the batch and the per-criterion answers agree. The stories refine writes carry the executable checks.

## Triage

- Confirmed at 49bb056a by the code path: `verify_ac.py` batches jest (`jest_batch_cache`, verify_ac.py:1687) and pytest (`pytest_batch_cache`, verify_ac.py:1771) and has no vitest batch, so each vitest criterion is its own cold subprocess. Related to BG1023 (the `vitest` verb folds its tail into -t), which is why such criteria are written as `shell npx vitest run ...` today.
- Private project name generalised. A request, not yet a unit: `refine` sizes it. Not in the first 6.2 run.

## Triage (2026-10-21)

Kept (D0387). To plan it:

- Refine needs: one story, Points 5, after BG1023
- Verify into a new module, e.g. pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac_vitest_batch.py::VitestBatchTests::test_fifty_criteria_resolve_from_one_run, with vitest stubbed so the budget criterion is deterministic
- Persona: Maya Okafor (consuming vitest projects)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-12 | sdlc-studio | Raised |
| 2026-10-12 | Claude Opus 5.5 (triage) | Triaged: confirmed from the code path; project name generalised |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
