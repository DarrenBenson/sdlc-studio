# BG0551: repair_mutation_gate derives its surface from the artefact's own Affects, so a mis-declared Affects bypasses the evidence demand entirely

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/reference-doctrine.md
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

### AC1: a mis-declared Affects cannot shrink the surface to nothing

- **Given** a repair whose diff changes a Python module while its `Affects` declares only
  markdown - the measured reproduction: no ledger, no exemption, blocking mode
- **When** it is driven to a terminal status
- **Then** it is REFUSED for missing mutation evidence, because the surface is taken from the
  DIFF. A declaration can only ever SHRINK the derived surface, so deriving from it hands the
  author the fail-open one step over - the same repair `verify_no_surface_claim` already had.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k a_misdeclared_affects_cannot_shrink_the_surface_to_nothing
- **Verified:** yes (2026-08-11)
- **Mutant:** in `transition.py`, derive the targets from `sdlc_md.affects_files(text)` again.

### AC2: a surface that cannot be derived refuses

- **Given** no open run, so there is no base ref to diff against
- **When** the gate is asked
- **Then** it REFUSES, naming why. A derivation that cannot run yields no targets, and no targets
  is indistinguishable from nothing to mutate - so the fail-open would be reachable by simply not
  having a run open, which is not a bar at all.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k the_gate_refuses_when_it_cannot_take_a_diff
- **Verified:** yes (2026-08-11)
- **Mutant:** in `transition.py`, return None when there is no base ref.

### AC3: the exemption stays the record's to grant

- **Given** a repair whose diff touches no mutatable file and which carries NO recorded exemption
- **When** it is driven to a terminal status
- **Then** it is still REFUSED. An empty derived surface is a CLAIM, granted by a recorded
  exemption that is re-derived, never inferred from the derivation coming back empty - otherwise
  the record decides nothing and the exemption is a box.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k a_no_surface_repair_records_the_exemption_and_its_reason
- **Verified:** yes (2026-08-11)
- **Mutant:** in `transition.py`, return None as soon as the derived surface is empty.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `transition.py`, derive the targets from `sdlc_md.affects_files(text)` again | a mis-declared Affects cannot shrink the surface to nothing |
| AC2 | in `transition.py`, return None when there is no base ref | a surface that cannot be derived refuses |
| AC3 | in `transition.py`, return None as soon as the derived surface is empty | the exemption stays the record's to grant |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Filed |
| 2026-08-07 | sdlc-studio | Raised again at panel sign-off, reproduced through the CLI: under `block` a repair declaring only a markdown `Affects` reaches Fixed with no evidence and no warning. `reference-doctrine.md` rule 21 called `block` a hard bar without caveat and told readers to set it, so a project taking that advice got false confidence - the one place the increment still overstated. The doctrine now names the gap and cites the exemption path beside it, which already derives from the diff. Fix this and the caveat comes out |
