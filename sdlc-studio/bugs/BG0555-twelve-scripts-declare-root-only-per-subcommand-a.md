# BG0555: twelve scripts declare --root only per-subcommand, a grammar defect the conformance sweep could not see because it silently skipped them

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/backfill_audit_runs.py, .claude/skills/sdlc-studio/scripts/backfill_authorship.py, .claude/skills/sdlc-studio/scripts/changelog.py, .claude/skills/sdlc-studio/scripts/digest.py, .claude/skills/sdlc-studio/scripts/doc_freshness.py, .claude/skills/sdlc-studio/scripts/flow.py, .claude/skills/sdlc-studio/scripts/migrate_v3.py, .claude/skills/sdlc-studio/scripts/persona_gen.py, .claude/skills/sdlc-studio/scripts/persona_resolve.py, .claude/skills/sdlc-studio/scripts/schema_check.py, .claude/skills/sdlc-studio/scripts/triage_noise.py, .claude/skills/sdlc-studio/scripts/triage_sampling.py, .claude/skills/sdlc-studio/scripts/tests/test_cli_grammar.py, .claude/skills/sdlc-studio/scripts/tests/test_backfill_audit_runs.py, .claude/skills/sdlc-studio/scripts/tests/test_backfill_authorship.py, .claude/skills/sdlc-studio/scripts/tests/test_changelog.py, .claude/skills/sdlc-studio/scripts/tests/test_digest.py, .claude/skills/sdlc-studio/scripts/tests/test_doc_freshness.py, .claude/skills/sdlc-studio/scripts/tests/test_flow.py, .claude/skills/sdlc-studio/scripts/tests/test_migrate_v3.py, .claude/skills/sdlc-studio/scripts/tests/test_persona_gen.py, .claude/skills/sdlc-studio/scripts/tests/test_persona_resolve.py, .claude/skills/sdlc-studio/scripts/tests/test_schema_check.py, .claude/skills/sdlc-studio/scripts/tests/test_triage_noise.py, .claude/skills/sdlc-studio/scripts/tests/test_triage_sampling.py
> **Evidence:** RUN-01KZF9AF, 2026-08-08, while building US0652. Fourteen conformance failures appeared the moment the sweep could see the twelve scripts it had been skipping.
> **Created:** 2026-08-08
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`RootPlacementConformance` asserts that `--root` is a global option, valid before OR after the subcommand, uniformly across the script family. Twelve scripts declare it only per-subcommand, so `script.py --root X <sub>` is rejected and a subcommand default can clobber a value given before the verb.\n\nThe defect is old; what is new is that anybody can SEE it. `_all_parsers()` swept the directory itself and swallowed every script without a module-level `build_parser` with a bare `continue`, so these twelve were never in the family it checked - while its docstring claimed to walk the whole one. US0652 gave them `build_parser` and pointed the sweep at `lib/surface.py`, and fourteen conformance failures surfaced at once.\n\nThey are recorded in `ROOT_GRAMMAR_DEBT`, NAMED rather than skipped, and the set may only shrink. That is the difference from the `continue` it replaced: a reader can see exactly which twelve are unchecked and why.

## Steps to Reproduce

1. `python3 .claude/skills/sdlc-studio/scripts/changelog.py --root /tmp check` - rejected, because `--root` is declared on the subcommand only. 2. `changelog.py check --root /tmp` works. 3. Remove `changelog.py` from `ROOT_GRAMMAR_DEBT` in `tests/test_cli_grammar.py` and the conformance sweep fails, naming it.

## Proposed Fix

Install the global option with `sdlc_md.add_global_root` on each script's top-level parser, keep the per-subcommand one so both placements parse, and let `sdlc_md.resolve_root(args)` settle precedence - the pattern the compliant scripts already use. Then remove each name from `ROOT_GRAMMAR_DEBT`; the set is there to be emptied.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `RootPlacementConformance` asserts that `--root` is a global option, valid before OR after the subcommand, uniformly across the script family.
- [ ] **AC2** The proposed fix lands, pinned by a test: Install the global option with `sdlc_md.add_global_root` on each script's top-level parser, keep the per-subcommand one so both placements parse, and let...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-08 | sdlc-studio | Filed |
