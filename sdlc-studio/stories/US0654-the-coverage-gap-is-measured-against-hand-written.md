# US0654: The coverage gap is measured against hand-written docs only, never against the generator's own output

> **Status:** Ready
> **Delivers:** CR0538
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/command_audit.py, .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py, .claude/skills/sdlc-studio/scripts/docgen.py
> **Epic:** EP0211
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** The coverage gap is measured against hand-written docs only, never against the generator's own output
**So that** CR0538 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: a verb documented ONLY in a generated block reads UNDOCUMENTED

- **Given** a fixture corpus with two verbs: one named in hand-written prose inside a
  `reference-scripts`-family file, and one named only inside a `<!-- BEGIN GENERATED -->` block.
  The first lives in that family deliberately - excluding `reference-scripts*.md` wholesale is
  the other way to make the number stop moving, and only a prose-only verb INSIDE it catches
  that
- **When** `command_audit.py --coverage` runs
- **Then** the first reads DOCUMENTED and the second reads UNDOCUMENTED. That PAIR is the
  criterion, not an unchanged total: asserting only that the number does not move when the
  generated page lands is satisfied by a corpus that strips too much, or by one that excludes
  `reference-scripts*.md` wholesale - both of which measure nothing and pass. The moment a
  generated page lists every verb, a corpus that includes it returns 100% and the gap vanishes
  with no documentation added, which this project has already filed once as a document compared
  against a projection of itself
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py::CoverageThroughTheCliTests::test_the_exclusion_holds_through_the_command_and_removing_it_shows_the_difference

### AC2: the corpus rule has ONE definition, and moving it moves the reader

- **Given** `docgen.GENERATED_TARGETS` and `docgen.strip_generated_blocks()`
- **When** the module attribute is PATCHED to a value `command_audit.py` could not have computed
- **Then** the coverage corpus moves with it. Asserting the two are equal proves nothing - a
  copy compares equal - so the mutant that gives `command_audit.py` its own list survives an
  equality assertion untouched. One definition and two readers is the claim; a patch that only
  one of them sees is the test of it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py::CoverageCorpusTests::test_patching_the_shared_rule_moves_the_corpus

### AC3: a HAND-WRITTEN table of the same shape is not stripped

- **Given** the generated verb table pasted verbatim into a file with no generation markers, and
  beside it an ordinary hand-written table
- **When** the corpus is built
- **Then** the pasted block is stripped and the hand-written table is NOT. Excluding the
  generated targets closes the front door; pasting the same table into a hand-written file walks
  in the back one with no prose added. And a stripper that eats every table drives the count to
  100% undocumented, which passes an unchanged-number assertion by measuring nothing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py::CoverageCorpusTests::test_a_pasted_generated_block_is_stripped_and_a_hand_written_table_is_not

### AC4: the counts are pinned on a miniature corpus with stated literals

- **Given** a fixture of three verbs across two scripts, one of which is named in prose without
  its `script.py verb` token
- **When** `--coverage` runs
- **Then** it reports 3 enumerated, 1 undocumented, against literals written in the test. The
  repo-wide number is REPORTED and not asserted, because US0652 makes 12 more scripts enumerable
  and it will move - but a test whose expectation is computed by the function under test can
  never fail, so the fixture carries the numbers a human wrote down
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py::CoverageCorpusTests::test_the_counts_are_pinned_on_a_fixture_with_stated_literals

### AC5: severity separates absent from unusable, each pinned to its own case

- **Given** a verb whose token appears NOWHERE, one named in prose but never as an invocable
  `script.py verb` form, and a flag named nowhere
- **When** each is filed
- **Then** they carry high, medium and low RESPECTIVELY - each case asserted against its own
  severity, so a reversed mapping dies as well as a collapsed one
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py::CoverageFindingTests::test_severity_separates_absent_from_unusable

### AC6: the first run FILES, the second adds nothing, and both exit 0

- **Given** `--coverage` run twice over the same tree
- **When** each completes
- **Then** the first files at least one artefact - asserted, because a filer that files nothing
  is trivially idempotent and would pass the second half alone - and the second adds none, keyed
  on the `script.py verb` token. Both exit 0 whatever they found: a documentation guard that
  blocks is one that gets switched off
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py::CoverageFindingTests::test_the_first_run_files_and_the_second_adds_nothing

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | include the generated targets in the corpus, so the page counts as its own documentation | a verb documented ONLY in a generated block reads UNDOCUMENTED |
| AC2 | give `command_audit.py` its own copy of the target list rather than importing docgen's | the corpus rule has ONE definition |
| AC3 | strip every table-shaped block, not only generated ones | a HAND-WRITTEN table is not stripped |
| AC3 | strip generated blocks only from the declared targets, not wherever they appear | a HAND-WRITTEN table is not stripped |
| AC4 | count a verb as documented when its SCRIPT is mentioned anywhere, not the `script.py verb` token | the counts are pinned on a miniature corpus |
| AC5 | file every coverage finding at one severity | severity separates absent from unusable |
| AC5 | swap the absent and unusable severities | severity separates absent from unusable |
| AC6 | key idempotence on the finding's title rather than the `script.py verb` token | the first run FILES, the second adds nothing |
| AC6 | exit non-zero when the coverage ratio is below a threshold | the first run FILES, the second adds nothing |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-08 | sdlc-studio | AC5 added from the plan-time qa seat: excluding the generated TARGETS closes the front door, and pasting the same table into a hand-written file walks in the back one - the same flattery with one extra step and no prose |
| 2026-08-08 | sdlc-studio | Plan review round 1 REJECTed on three blocking findings, all of them the same shape: a criterion asserting a number does NOT move is satisfied by measuring nothing. AC1 is now a PAIR - a verb documented only in prose reads documented, the same verb only inside a generated block reads undocumented. AC3 requires a hand-written table of the same shape to survive the stripper, so eating every table cannot pass. AC4 pins literals on a miniature corpus, since an expectation computed by the function under test can never fail. AC2 patches the shared rule rather than comparing two lists, because a copy compares equal. `docgen.py` joins the declared Affects, which AC2 imports |
| 2026-08-08 | sdlc-studio | Plan review round 2 APPROVEd, ruling all five round-1 findings CLOSED. Its minor is folded in: the prose-only verb lives in the `reference-scripts` family, so excluding that family wholesale - the other way to make the number stop moving - fails the pair too |
