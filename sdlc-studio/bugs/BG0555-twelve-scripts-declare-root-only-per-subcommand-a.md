# BG0555: twelve scripts declare --root only per-subcommand, a grammar defect the conformance sweep could not see because it silently skipped them

> **Status:** Fixed
> **Verification depth:** functional (executed through the shipped CLI: the filed reproduction now answers about the fixture in both flag placements, with the pre-fix parser restored as the negative control - it exited 0 reporting this repository's 19 fragments instead; mutation: 3 declared mutants, all KILLED, restore byte-exact)
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/backfill_audit_runs.py, .claude/skills/sdlc-studio/scripts/backfill_authorship.py, .claude/skills/sdlc-studio/scripts/changelog.py, .claude/skills/sdlc-studio/scripts/digest.py, .claude/skills/sdlc-studio/scripts/doc_freshness.py, .claude/skills/sdlc-studio/scripts/flow.py, .claude/skills/sdlc-studio/scripts/migrate_v3.py, .claude/skills/sdlc-studio/scripts/persona_gen.py, .claude/skills/sdlc-studio/scripts/persona_resolve.py, .claude/skills/sdlc-studio/scripts/schema_check.py, .claude/skills/sdlc-studio/scripts/triage_noise.py, .claude/skills/sdlc-studio/scripts/triage_sampling.py, .claude/skills/sdlc-studio/scripts/tests/test_cli_grammar.py, .claude/skills/sdlc-studio/scripts/tests/test_backfill_audit_runs.py, .claude/skills/sdlc-studio/scripts/tests/test_backfill_authorship.py, .claude/skills/sdlc-studio/scripts/tests/test_changelog.py, .claude/skills/sdlc-studio/scripts/tests/test_digest.py, .claude/skills/sdlc-studio/scripts/tests/test_doc_freshness.py, .claude/skills/sdlc-studio/scripts/tests/test_flow.py, .claude/skills/sdlc-studio/scripts/tests/test_migrate_v3.py, .claude/skills/sdlc-studio/scripts/tests/test_persona_gen.py, .claude/skills/sdlc-studio/scripts/tests/test_persona_resolve.py, .claude/skills/sdlc-studio/scripts/tests/test_schema_check.py, .claude/skills/sdlc-studio/scripts/tests/test_triage_noise.py, .claude/skills/sdlc-studio/scripts/tests/test_triage_sampling.py
> **Evidence:** RUN-01KZF9AF, 2026-08-08, while building US0652. Fourteen conformance failures appeared the moment the sweep could see the twelve scripts it had been skipping.
> **Created:** 2026-08-08
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`RootPlacementConformance` asserts that `--root` is a global option, valid before OR after the subcommand, uniformly across the script family. Twelve scripts were recorded as declaring it only per-subcommand, so `script.py --root X <sub>` is rejected and a subcommand default can clobber a value given before the verb.\n\nThe defect is old; what is new is that anybody can SEE it. `_all_parsers()` swept the directory itself and swallowed every script without a module-level `build_parser` with a bare `continue`, so these twelve were never in the family it checked - while its docstring claimed to walk the whole one. US0652 gave them `build_parser` and pointed the sweep at `lib/surface.py`, and fourteen conformance failures surfaced at once.\n\nThey are recorded in `ROOT_GRAMMAR_DEBT`, NAMED rather than skipped, and the set may only shrink. That is the difference from the `continue` it replaced: a reader can see exactly which twelve are unchecked and why.

## Steps to Reproduce

1. `python3 .claude/skills/sdlc-studio/scripts/changelog.py --root /tmp check` - rejected, because `--root` is declared on the subcommand only. 2. `changelog.py check --root /tmp` works. 3. Remove `changelog.py` from `ROOT_GRAMMAR_DEBT` in `tests/test_cli_grammar.py` and the conformance sweep fails, naming it.

## Proposed Fix

Install the global option with `sdlc_md.add_global_root` on each script's top-level parser, keep the per-subcommand one so both placements parse, and let `sdlc_md.resolve_root(args)` settle precedence - the pattern the compliant scripts already use. Then remove each name from `ROOT_GRAMMAR_DEBT`; the set is there to be emptied.

## Acceptance Criteria

- [x] **AC1** Given any script in the family, when its parser is swept, then `--root` is a global option accepted before or after the verb, and every per-subcommand copy defaults to SUPPRESS so it cannot clobber a value given first.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cli_grammar.py -k "root_is_a_global_flag or subcommand_root_cannot_clobber"
  - **Verified:** yes (2026-08-14)
- [x] **AC2** Given `ROOT_GRAMMAR_DEBT`, when the suite runs, then it is empty and a test says so - the set only shrinks, and eight of its twelve names were already stale.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cli_grammar.py -k debt_set_is_empty
  - **Verified:** yes (2026-08-14)
- [x] **AC3** Given an empty fixture root passed before the verb, when `changelog.py check` runs from inside this repository, then it answers about the fixture and not about the repository - the value is READ, not merely parsed.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cli_grammar.py -k root_given_before_the_verb_selects
  - **Verified:** yes (2026-08-14)

## Resolution

Only FOUR of the twelve were still real when the set was emptied and re-measured: `backfill_audit_runs.py`, `changelog.py`, `persona_gen.py` and `persona_resolve.py`. The other eight had been repaired at some point and nobody re-read the list, so a debt record written once was being read as current - the same shape as the stale open bugs BG0577 was filed for.

`changelog.py` was the interesting one. It DID call `add_global_root`, three lines before its subparsers existed, so the call could re-point nothing and every subcommand default still won. The filed reproduction says the command was "rejected". It was not: `changelog.py --root <empty fixture> check` exited 0 and reported this repository's nineteen fragments. A rejection is visible; answering confidently about the wrong tree is not, and that is BG0556's class, found here by accident.

The debt set is now empty, and a test asserts it, so the next entry has to be argued for rather than added.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in backfill_audit_runs.py `build_parser`, remove the global --root so the flag is per-subcommand again | Given any script in the family, when its parser is swept, then `--root` is a global option accepted before or after the verb, and every per-subcommand copy defaults to SUPPRESS so it cannot clobber a value given first. |
| AC2 | in tests/test_cli_grammar.py, re-admit `changelog.py` to ROOT_GRAMMAR_DEBT so the ratchet stops holding | Given `ROOT_GRAMMAR_DEBT`, when the suite runs, then it is empty and a test says so - the set only shrinks, and eight of its twelve names were already stale. |
| AC3 | in changelog.py `build_parser`, drop the global --root so the value parses but is not read | Given an empty fixture root passed before the verb, when `changelog.py check` runs from inside this repository, then it answers about the fixture and not about the repository - the value is READ, not merely parsed. |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-08 | sdlc-studio | Filed |
