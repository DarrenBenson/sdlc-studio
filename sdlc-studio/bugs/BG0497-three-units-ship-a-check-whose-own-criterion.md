# BG0497: three units ship a check whose own criterion names the mechanism that was not implemented

> **Status:** Fixed
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Provenance:** dogfood
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/doc_coverage.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_batch_capacity.py, .claude/skills/sdlc-studio/scripts/tests/test_help_structure.py, .claude/skills/sdlc-studio/scripts/tests/test_cli_grammar.py, .claude/skills/sdlc-studio/scripts/tests/test_doc_coverage.py, .claude/skills/sdlc-studio/scripts/tests/test_conformance.py
> **Severity:** High
> **Points:** 5
> **Verification depth:** functional (each criterion's named mutant applied to the shipped file, bytecode purged, run under `python3 -B`, the anchor asserted unique, the patch asserted to have changed the file, the tree verified byte-identical afterwards; the `doc-coverage` lane additionally exercised through `doc_coverage.py --root` and through `gate.py._doc_coverage` on a fixture skill tree with a help page deleted)

## Summary

The final review pass over RUN-01KYZKY5 found the same shape three times, and named it precisely: in each case the criterion STATES the mechanism, and the mechanism is the part that was not built, while the prose reports it as done.

US0466 AC2 requires a `doc_coverage` LANE that turns red when a help page is deleted. `help_page_findings` has no caller: `doc_coverage.check()`, which gate.py:192 runs as the lane, never invokes it. Executed with help/refine.md deleted - the lane exits 0 and only a unit test reddens.

US0470 AC5 requires the id-list forms be parsed and read back through the shared helper. Its verifier loads `sprint` into an unused variable and asserts only on `sdlc_md.split_id_list`; returning 99 from the `batch swap` dispatch SURVIVES it, while the five sibling tests fail, proving the harness works. Two of the three grammar forms the AC names - a positional incoming id, and `--outs` - do not exist in the parser. The conformance-sweep registration the AC requires never landed: the diff on `test_cli_grammar.py` is empty though the file is in the declared Affects.

US0473 AC2 requires each documented invocation be parsed by `build_parser()`. The verifier regexes out the bare verb WORD and checks it is known; flags are never seen, so a documented `--nonexistent-flag zzz` survives. Implementing the AC as written surfaces a real pre-existing page defect: `/sdlc-studio sprint --bugs Open --autonomous` is rejected by the parser, and `--autonomous` appears on the page five times.

US0473 AC3 requires the invocations be found WITHIN the named section's body; the check is file-wide, so moving the block out of the section and emptying it still passes. It also omits `batch add-epic` and `appetite resize`, the two in-flight controls this very run shipped.

## Steps to Reproduce

1. Delete a help page in a scratch checkout, run `doc_coverage.py` -> exits 0.
2. Return 99 from the batch swap dispatch, run the US0470 AC5 verifier -> passes.
3. Add a nonexistent flag to a documented invocation in help/sprint.md, run the US0473 AC2 verifier -> passes.
4. Move the in-flight block out of its section in reference-sprint.md -> AC3's check still passes.

## Proposed Fix

Implement each criterion's stated mechanism: call `help_page_findings` from `doc_coverage.check` so the lane is the thing that reddens; drive `batch swap` through the CLI in AC5's verifier and register it in the conformance sweep; parse each extracted invocation with `build_parser()` rather than matching a verb word, and scope the AC3 lookup to the section body. Then correct the two AC texts that name grammar the parser does not offer, and fix or file the pre-existing `--autonomous` page defect the parse surfaces.

## Acceptance Criteria

> **Groomed 2026-08-11.** Two of the four criteria being repaired name a mechanism that does not
> exist, and the ruling on each is recorded here rather than left to the diff.
>
> **US0470 AC5's grammar is CORRECTED to the shipped one, not built out.** The AC named three
> forms; the parser offers `--out`/`--in`, each repeatable and each accepting a comma list, and
> that is the house grammar `sdlc_md.split_id_list` defines. A positional incoming id would
> collide with the `id` positional `drop`/`add` already use for a different thing, and `--outs`
> would be a second spelling of a list the comma form already covers - the exact second grammar
> the conformance sweep exists to prevent. The half of that criterion that was real and never
> landed is the sweep registration, and that is built.
>
> **US0473 AC2's `--autonomous` is NOT a page defect.** `help/arguments.md` declares it as a
> slash-command flag the skill reads and not a `sprint.py` parser flag, and
> `reference-sprint.md` carries a section on the mode. The slash surface is deliberately a
> superset of the script's, so the check models both surfaces and reads the skill-only set from
> that declaration. Implementing the criterion did surface one real page defect beside it:
> `/sdlc-studio sprint <worklist.md> --order wsjf` documented a bare positional the parser does
> not accept - nor did the version that shipped alongside the line, checked at `1e7fbe25` - and
> every other mention of a tranche file on the page and in the reference spells it
> `--worklist <file>`. The PAGE is fixed.

### AC1: deleting a help page reddens the lane, not only a unit test

- **Given** a fixture skill tree whose Type Reference resolves to a help page each, covered
- **When** the `help_page_findings` call is removed from `doc_coverage.check` and a help page is
  deleted
- **Then** the check fails, because `check` is what `gate.py` runs as the `doc-coverage` lane
  and what `conformance` reads for its `documented` stage; the enumerator shipped with NO caller,
  so a deleted page reddened one unit test and nothing an operator runs. Driven through
  `doc_coverage.main`, the shipped entry point, because the wiring is the part a library call
  cannot see
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_doc_coverage.py::HelpPageCoverageTests::test_deleting_a_help_page_reddens_the_lane_the_gate_runs

### AC2: `batch swap` is registered in the conformance sweep as a two-list verb

- **Given** a second sweep table for verbs carrying more than one id list, which `resolve_ids`
  cannot serve because it hard-reads the `--id`/`--ids` pair, with `batch swap`'s `--out` and
  `--in` as its rows
- **When** `--out` is changed from `action="append"` to a plain store
- **Then** the sweep fails, because the repeated and comma forms stop reaching the same list
  through `sdlc_md.split_id_list`. This is the half of US0470 AC5 that never landed - the diff on
  `test_cli_grammar.py` was empty though the file was in the declared footprint - so the verb sat
  outside the sweep that exists to stop the next two-list verb reinventing the grammar
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cli_grammar.py::IdGrammarConformance::test_every_list_id_verb_reads_both_house_forms_through_the_shared_helper

### AC3: a documented flag no surface owns is refused

- **Given** the fenced invocations on `help/sprint.md`, on both the slash and the `sprint.py`
  surface, each parsed by `sprint.build_parser()` after the flags `help/arguments.md` declares
  as slash-only are removed from the slash-surface lines alone
- **When** the check is reduced to asking whether the parser knows the bare verb WORD
- **Then** it fails on `/sdlc-studio sprint --bugs Open --nonexistent-flag zzz`, which the verb
  match accepted; and it still accepts both a real parser flag and the declared slash-only
  `--autonomous` on the slash surface, while refusing that same flag on the script surface,
  whose parser does not own it - so the binder separates the cases a verb match cannot rather
  than refusing or excusing everything
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_help_structure.py::SprintInvocationBinderTests::test_a_documented_flag_no_surface_owns_is_refused

### AC4: the in-flight controls are looked up WITHIN their own section

- **Given** `reference-sprint.md`, whose generated reading-guide row also carries the
  `{#in-flight-controls}` anchor, and the eight controls that section must show as invocations -
  including `batch add-epic` and `appetite resize`, which the previous list omitted
- **When** the heading is deleted, or the fenced block is moved out of the section leaving it
  empty
- **Then** the check fails in each case, distinguishing no-section from empty-section; the
  file-wide lookup it replaces passed on both, so the criterion's "within that section's body"
  was stated and not implemented
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_help_structure.py::SprintInvocationBinderTests::test_moving_the_controls_out_of_their_section_is_refused

## Impact

This is the run's dominant defect class recurring in the units that had never been reviewed, which is evidence it is systemic rather than incidental. It is also the strongest available argument for CR0525: in all three cases the criterion said exactly what to build, and reviewing the test plan against the criterion before the code would have caught every one.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | {{name the production change this test must fail on}} | deleting a help page reddens the lane, not only a unit test |
| AC2 | {{name the production change this test must fail on}} | `batch swap` is registered in the conformance sweep as a two-list verb |
| AC3 | {{name the production change this test must fail on}} | a documented flag no surface owns is refused |
| AC4 | {{name the production change this test must fail on}} | the in-flight controls are looked up WITHIN their own section |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-11 | Claude Opus 5 | Groomed: four criteria authored, each naming the production change that must redden it; the two rulings the fix needed - correct US0470 AC5 to the shipped grammar, and treat the slash surface as the superset it is documented to be - recorded above the criteria rather than left to the diff |
