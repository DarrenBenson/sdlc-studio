# BG0497: three units ship a check whose own criterion names the mechanism that was not implemented

> **Status:** Open
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Provenance:** dogfood
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/doc_coverage.py, .claude/skills/sdlc-studio/scripts/tests/test_batch_capacity.py, .claude/skills/sdlc-studio/scripts/tests/test_help_structure.py, .claude/skills/sdlc-studio/scripts/tests/test_cli_grammar.py
> **Severity:** High
> **Points:** 5

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

## Impact

This is the run's dominant defect class recurring in the units that had never been reviewed, which is evidence it is systemic rather than incidental. It is also the strongest available argument for CR0525: in all three cases the criterion said exactly what to build, and reviewing the test plan against the criterion before the code would have caught every one.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
