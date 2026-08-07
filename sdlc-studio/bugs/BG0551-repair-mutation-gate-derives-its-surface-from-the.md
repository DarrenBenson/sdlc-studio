# BG0551: repair_mutation_gate derives its surface from the artefact's own Affects, so a mis-declared Affects bypasses the evidence demand entirely

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Evidence:** RUN-01KZEF9M delivery review of BG0541, 2026-08-07, qa seat. Proven pre-existing at the base ref by execution.
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`repair_mutation_gate` takes its mutatable surface from `sdlc_md.affects_files(text)` - the author's own declaration - and returns None when that yields no Python file. A repair declaring `Affects: README.md` while changing a Python module therefore reaches a terminal status with no mutation evidence at all, under `review.mutation_evidence: block`. Demonstrated by execution: a fixture with a Python diff, no ledger and no exemption exits 0 and writes `Status: Fixed`.

This is the same fail-open that `verify_no_surface_claim` was repaired for in BG0541 - its docstring now states the rule outright, that a declaration can only SHRINK the derived surface and shrinking it hands the author back the fail-open one step over. The exemption path was fixed; the gate path beside it was not, and it derives from the declaration for exactly the same reason.

Pre-existing: the derivation predates BG0541 (`git log -S 'affects_files(text)'` reaches US0564), so it did not hold BG0541's gate. It was inert while `repair_mutation_gate` had no callers and is LIVE now that the lane is wired, which is why it is filed High rather than left as a note.

## Steps to Reproduce

1. Build a repair bug whose `Affects` names only a markdown file. 2. Change a Python module and commit, so the diff carries a mutatable surface. 3. Set `review.mutation_evidence: block`. 4. `transition.py set --id <id> --status Fixed` exits 0 with no evidence of any kind.

## Proposed Fix

Derive the gate's surface the way `verify_no_surface_claim` now does - from git's diff against the run's base ref - and use `Affects` only as reported context. `mutation.mutants_over_changed_lines` already does the scoping. An empty or unresolvable base ref must refuse, on the same terms and for the same reason.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `repair_mutation_gate` takes its mutatable surface from `sdlc_md.affects_files(text)` - the author's own declaration - and returns None when that yields no...
- [ ] **AC2** The proposed fix lands, pinned by a test: Derive the gate's surface the way `verify_no_surface_claim` now does - from git's diff against the run's base ref - and use `Affects` only as reported context.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Filed |
