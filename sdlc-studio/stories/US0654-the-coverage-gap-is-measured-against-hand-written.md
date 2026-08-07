# US0654: The coverage gap is measured against hand-written docs only, never against the generator's own output

> **Status:** Ready
> **Delivers:** CR0538
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/command_audit.py, .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py
> **Epic:** EP0211
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** The coverage gap is measured against hand-written docs only, never against the generator's own output
**So that** CR0538 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: the corpus EXCLUDES every generated target, and the number does not move when the page lands

- **Given** the coverage measurement taken before `reference-scripts-surface.md` exists, and
  again after it is generated with every verb on it
- **When** `command_audit.py --coverage` runs on each
- **Then** the two numbers are THE SAME. This is the criterion the whole change turns on: the
  moment a generated page lists every verb, a corpus that includes it makes the coverage query
  return 100% and the gap vanishes without one word of hand-written documentation being added.
  That is a document compared against a projection of itself, which this project has already
  filed once. `docgen.py` exports `GENERATED_TARGETS` and `strip_generated_blocks()`, and
  `command_audit.py` imports them - one definition, two readers, because two copies of this rule
  would drift and the drift would be invisible in the flattering direction
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py::CoverageCorpusTests::test_the_generated_page_does_not_change_the_coverage_number

### AC2: the gap is measured, and the number is the one a human can check

- **Given** the skill's hand-written markdown
- **When** `--coverage` runs
- **Then** it reports the count of enumerated verbs, the count carrying no `script.py verb` token
  in that corpus, and the ratio - and the counts are reproducible by hand from the same corpus.
  Measured today: 179 verbs enumerable, 69 undocumented. The plan estimated 211 and 49; the
  difference is that 12 scripts build their parser inline and are not enumerable until US0652
  lands, so the number is expected to MOVE when it does, and a criterion pinned to a constant
  would be wrong by then
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py::CoverageCorpusTests::test_the_counts_are_reproducible_from_the_same_corpus

### AC3: findings carry a severity that distinguishes absent from unusable

- **Given** a verb whose token appears NOWHERE, one that appears in prose but never as an
  invocable `script.py verb` form, and a flag named nowhere
- **When** each is filed
- **Then** they carry high, medium and low. A verb a reader cannot find at all and one they can
  read about but not invoke are different failures with different fixes, and one severity for
  both gives triage nothing to sort on
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py::CoverageFindingTests::test_severity_separates_absent_from_unusable

### AC4: filing is idempotent and the lane always exits 0

- **Given** `--coverage` run twice over the same tree
- **When** the second run completes
- **Then** no second artefact exists for the same `script.py verb` token, and both runs exit 0
  whatever they found. A documentation guard that blocks is one that gets switched off, which is
  the operator's stated decision and the reason this reports rather than refuses
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py::CoverageFindingTests::test_filing_is_idempotent_and_the_lane_exits_zero

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | include the generated targets in the corpus, so the page counts as its own documentation | the corpus EXCLUDES every generated target |
| AC1 | give `command_audit.py` its own copy of the target list rather than importing docgen's | the corpus EXCLUDES every generated target |
| AC2 | count a verb as documented when its SCRIPT is mentioned anywhere, not the `script.py verb` token | the gap is measured |
| AC3 | file every coverage finding at one severity | findings carry a severity that distinguishes |
| AC4 | key idempotence on the finding's title rather than the `script.py verb` token | filing is idempotent and the lane always exits 0 |
| AC4 | exit non-zero when the coverage ratio is below a threshold | filing is idempotent and the lane always exits 0 |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Created via `new` (deterministic) |
