# CR-0583: No command applies a unit's authored Test Plan mutants, runs each criterion's selector and registers the kills

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py, .claude/skills/sdlc-studio/help/mutation.md, .claude/skills/sdlc-studio/reference-sprint-toolchain.md
> **Evidence:** findings/todo.txt, RUN-01M2JA6J 2026-09-15: FILE AT CLOSE glue CRs, 'worktree patch merge + mutant re-run + register'; the session's hand-written mutspec.py, build_spec.py, mutants.py, mkpatch.py and verify_patches.py. Related but distinct: CR0567 (a generated run at the done gate), CR0570 (whole-file staleness).
> **Date:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

mutation.py run generates mutants by fault class, and run --from-plan only reports which planned rows were executed; nothing applies the edits a unit's Test Plan rows describe. RUN-01M2JA6J therefore hand-wrote the chain for every unit: build a spec of criterion, row, target, old text, new text and Verify selector; assert each anchor occurs exactly once; apply one mutant; run the selector with bytecode writes off and a fresh pycache prefix; restore byte for byte with a hash check; and register with --anchor only when every mutant was killed. Parallel worktree agents' changes were merged onto HEAD through hand-built patches checked byte for byte against the worktree before the mutants were re-run on the merged bytes.

## Impact

Every delivery that keeps mutation evidence, here and in consuming projects: many throwaway runners per sprint, each a chance to skip a target or register over the wrong bytes (the whole-file ledger CR records one runner silently skipping a target through three passes).

## Acceptance Criteria

- [ ] The new mode applies each planned row's edit once, runs its selector, restores the target byte for byte and registers the verdicts, beside a --dry-run that registers nothing
- [ ] A row whose anchor occurs zero times or more than once is refused before any file is changed
- [ ] A run in which any planned mutant survives registers nothing and names the survivor

## Recommendation

Add a mode to mutation.py run that takes a unit's planned rows with their anchors and applies, runs, restores and registers them under the rules the hand runners used: unique anchor, bytecode off, byte-exact restore verified by hash, and registration only when every planned mutant was killed. Document the worktree merge step (apply each agent's patch, verify byte identity, re-run the mutants on the merged bytes) in the toolchain runbook, or give it a command.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Raised |
