# US0652: Every script exposes build_parser, and one library enumerates the surface

> **Status:** Ready
> **Delivers:** CR0538
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/surface.py, .claude/skills/sdlc-studio/scripts/flow.py, .claude/skills/sdlc-studio/scripts/digest.py, .claude/skills/sdlc-studio/scripts/persona_resolve.py, .claude/skills/sdlc-studio/scripts/changelog.py, .claude/skills/sdlc-studio/scripts/tests/test_surface.py, .claude/skills/sdlc-studio/scripts/tests/test_cli_grammar.py, .claude/skills/sdlc-studio/scripts/doc_freshness.py, .claude/skills/sdlc-studio/scripts/schema_check.py, .claude/skills/sdlc-studio/scripts/triage_noise.py, .claude/skills/sdlc-studio/scripts/triage_sampling.py, .claude/skills/sdlc-studio/scripts/persona_gen.py, .claude/skills/sdlc-studio/scripts/migrate_v3.py, .claude/skills/sdlc-studio/scripts/backfill_audit_runs.py, .claude/skills/sdlc-studio/scripts/backfill_authorship.py
> **Epic:** EP0211
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** Every script exposes build_parser, and one library enumerates the surface
**So that** CR0538 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: every CLI script exposes `build_parser`, and the one non-CLI is named

- **Given** the 71 scripts under `scripts/`, of which 12 build their parser inline in `main()`
- **When** each is read
- **Then** all 12 expose a module-level `build_parser()` returning the configured parser, and
  exactly ONE script is exempt: `carry_forward.py`, which has no `main`, no `__main__` guard and
  no `ArgumentParser` at all. `autosprint.py` is NOT an exception - it re-exports `sprint`'s
  `build_parser` by name, so `getattr` finds it. The exemption is asserted BOTH ways: every
  non-exempt script has one, and the exempt one is exempt for a stated structural reason, so an
  extra parser bolted onto a library cannot pass unnoticed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_surface.py::BuildParserCoverageTests::test_every_cli_script_exposes_build_parser

### AC2: the enumeration NAMES what it cannot read, and never skips it

- **Given** a synthetic module that raises on import, written into the fixture beside real ones
- **When** `surface.enumerate()` runs
- **Then** it appears in the result with its exception, and the run continues over the rest.
  Silently continuing past a module that will not import is the defect this library exists to
  fix: `_all_parsers()` in `test_cli_grammar.py` does exactly that while its docstring claims to
  sweep the whole family, so the count it reports is of what happened to load. The fixture is
  synthetic because no real script in this tree fails to import - a claim that three of them do
  was made from a measurement whose own loader manufactured the failure, and did not survive
  being re-run
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_surface.py::SurfaceEnumerationTests::test_a_module_that_will_not_import_is_named_not_skipped

### AC3: positional `choices` are walked, not only subparsers

- **Given** `verify_ac.py testplan derive`, which exists as a positional `choices` value rather
  than as a subparser
- **When** the surface is enumerated
- **Then** it appears. A subparser-only walk misses it, and a verb the enumeration cannot see
  is a verb no coverage number can count as missing - the gap would be invisible in exactly the
  direction that flatters the total
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_surface.py::SurfaceEnumerationTests::test_a_positional_choice_is_enumerated_like_a_subcommand

### AC4: `test_cli_grammar.py` reads the shared library rather than its own copy

- **Given** `_all_parsers()`, which built its own parser map and swallowed every failure
- **When** the grammar tests run
- **Then** they consume `lib/surface.py`, so the sweep the docstring promises is the sweep that
  happens, and a script added tomorrow is covered by both readers or by neither. Asserted
  STRUCTURALLY - the shared enumerator is patched and the grammar tests are required to move
  with it - because a whole-module selector passes today and would pass with the delegation
  reverted, which is a criterion that cannot fail on what it claims
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_surface.py::SurfaceEnumerationTests::test_the_grammar_tests_read_the_shared_library

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | remove `build_parser` from one of the 12 converted scripts, leaving its inline parser in `main()` | every CLI script exposes `build_parser` |
| AC1 | add a `build_parser` to `carry_forward.py`, so a library counts as a CLI surface | every CLI script exposes `build_parser` |
| AC1 | list `autosprint.py` as exempt, though it re-exports `sprint`'s | every CLI script exposes `build_parser` |
| AC2 | swallow the import exception and continue, as `_all_parsers()` does today | the enumeration NAMES what it cannot read |
| AC3 | walk subparsers only, dropping the positional `choices` branch | positional `choices` are walked |
| AC4 | give `test_cli_grammar.py` back its own parser map | the grammar tests read the shared library |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-08 | sdlc-studio | Groomed, and the scope corrected against a measurement rather than the plan's estimate. The plan said 14 scripts lack `build_parser`; 12 do. `carry_forward.py` was in the declared `Affects` and is a LIBRARY - no `main`, no entrypoint, no `ArgumentParser` - so it is dropped, and `autosprint.py` already re-exports `sprint`'s. Both exclusions are stated in AC1 rather than left as a silent shortfall against a blanket title |
| 2026-08-08 | sdlc-studio | AC2's premise was FALSE and the plan-time engineering seat caught it. The claim that `github_sync.py`, `repo_map.py` and `verify_ac.py` will not import in-process was an artefact of the measurement's own loader, which fabricated the module name; all three import cleanly under a bare `import`. The criterion keeps its subject - an enumeration must name what it cannot read - with a synthetic unimportable module as its fixture, and gains the real finding underneath: a loader that fabricates names manufactures failures that are not there |
| 2026-08-08 | sdlc-studio | Plan review round 1 REJECTed both halves of my own correction. The fabricated-name claim does not reproduce - the reviewer loaded all three named scripts under a fabricated prefix and none raised - so AC2 drops it and uses a synthetic unimportable module, which is what the criterion was always about. And `autosprint.py` is NOT an exception: it re-exports `sprint`'s `build_parser`, so `getattr` finds it and an exact exception list fails on day one. `carry_forward.py` is the only one, asserted both ways |
