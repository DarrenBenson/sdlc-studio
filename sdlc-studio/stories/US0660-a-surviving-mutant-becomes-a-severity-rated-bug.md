# US0660: A surviving mutant becomes a severity-rated bug and the transition proceeds, and the run names the mode that held it

> **Status:** Review
> **Delivers:** CR0537
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Epic:** EP0212
> **Points:** 8
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** A surviving mutant becomes a severity-rated bug and the transition proceeds, and the run names the mode that held it
**So that** CR0537 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: a survivor is filed and the transition proceeds

- **Given** a repair whose ledger records one surviving mutant, under the default mode, its
  `Verification depth` already stamped so the bug's own depth gate is not what answers
- **When** `transition.py set --id BG0001 --status Fixed` runs through the shipped verb
- **Then** it exits 0, the artefact reads `Fixed`, and a new bug exists naming the unit, the
  criterion, the mutant and the test that failed to kill it - the finding reaches the backlog
  rather than dying with the terminal window
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::SurvivorFilingCLITests::test_a_survivor_is_filed_and_the_close_proceeds
- **Verified:** yes (2026-08-07)

### AC2: one command mints one bug, and a dry run mints none

- **Given** TWO pristine fixtures, each with an empty backlog and the same surviving mutant: the
  first run as `set --reviewer <name> --status Fixed`, the second run as `--dry-run` ONLY
- **When** each completes
- **Then** the first leaves exactly one bug and the second leaves none. The two fixtures are
  separate because a single fixture cannot see this defect: once AC4's idempotence exists, a
  second filing dedupes against the first, so a dry run that files after a real one leaves nothing
  either and passes for the wrong reason. `_pre_write_gates` runs up to three times per `set` -
  the dry-run preflight, the real transition, and the force-bypass re-run with force off - and the
  preflight runs before any write, so an unguarded filing there breaks the stated contract that a
  dry run introduces no write of its own. That contract, not the count, is what the second fixture
  measures. The dry-run leg is the lethal half: on the real leg the later ladder passes dedupe
  against the first, so its count holds under the mutant too
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::SurvivorFilingCLITests::test_one_command_mints_exactly_one_bug_and_a_dry_run_mints_none
- **Verified:** yes (2026-08-07)

### AC3: severity is derived from structure, and says what it read

- **Given** three survivors differing ONLY in the structure enclosing them - the same file, the
  same function name, the body changed from one that raises on a branch, to one that only
  reports, to a module-level constant
- **When** each is filed
- **Then** they carry High, Medium and Low, and each names the structural signal its severity was
  read from. Holding the file and the name fixed is what stops a mapping keyed on either from
  passing, which is the implementation a hurried author actually writes; and the signal string is
  asserted because without it all three severities can be right for no stated reason, and triage
  has a verdict it cannot disagree with
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::SurvivorSeverityTests::test_severity_is_derived_from_the_enclosing_structure_and_names_its_signal
- **Verified:** yes (2026-08-07)

### AC4: re-filing survives a loss of the filer's own bookkeeping

- **Given** a survivor already filed, and the filer's own idempotence bookkeeping under
  `sdlc-studio/.local/` DELETED between the two runs while `mutation-runs.json`,
  `mutation-report.json` and `mutation-series.jsonl` are left intact - every other file under that
  directory is unlinked, rather than one guessed cache path, so a bookkeeping key the author
  happened to name differently cannot survive a no-op delete
- **When** the same transition runs again on the same survivor
- **Then** no second bug is minted and the output names the existing finding. Only the filer's
  bookkeeping is cleared: `sdlc-studio/.local/` is also where the survivor evidence itself lives,
  so deleting the whole directory removes the ledger the Given depends on and run two finds no
  survivor to file - a `.local`-keyed implementation then mints nothing for the wrong reason and
  the mutant survives. The distinction between the evidence and the bookkeeping is the criterion
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::SurvivorFilingCLITests::test_the_same_survivor_does_not_mint_a_second_bug_after_a_cache_loss
- **Verified:** yes (2026-08-07)

### AC5: the run names the mode that held it

- **Given** three projects: one setting `review.mutation_evidence: block`, one leaving it absent,
  and one setting the typo `blcok`
- **When** the close's mutation note is composed
- **Then** the first two name their resolved mode, and the third is refused with the offending
  value quoted. The accepted pair is the positive control, without which a resolver that refuses
  everything passes; a typo must not silently switch a project's hard bar off
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::MutationEvidenceModeTests::test_the_close_names_the_resolved_mode
- **Verified:** yes (2026-08-07)

### AC6: the close counts the survivors this run let through, by severity

- **Given** a run that filed two survivor bugs at High and Medium, and a THIRD survivor bug
  artefact written straight into the fixture backlog without going through the filer, carrying the
  same artefact header and `Mutation-run` attribution a filed one carries and differing only in
  never having passed through it
- **When** the close report is composed
- **Then** it counts three, split by severity - so the count is derived from the filed artefacts
  and not from a tally the filer kept alongside them. A tally is the implementation a hurried
  author writes and it is invisible to any fixture whose artefacts all arrive through the filer.
  Reporting rather than blocking is a trade the operator only gets to make if the thing traded
  away is visible: a survivor filed and never counted is a survivor silently dropped, which is
  the outcome blocking was rejected to avoid, not the one that was chosen
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::MutationSurvivorCountTests::test_the_close_counts_survivors_by_severity
- **Verified:** yes (2026-08-07)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | change transition.py to report the survivor in the warning and mint nothing | a survivor is filed and the transition proceeds |
| AC2 | file the survivor inside `_pre_write_gates`, which runs up to three times per `set` and once during the dry-run preflight | one command mints one bug, and a dry run mints none |
| AC2 | drop the artefact-key dedupe, so each ladder pass mints its own | one command mints one bug, and a dry run mints none |
| AC3 | change mutation.py to map severity from the target file's suffix rather than from the enclosing structure | severity is derived from structure, and says what it read |
| AC3 | change mutation.py to file the derived severity with no signal string | severity is derived from structure, and says what it read |
| AC4 | change transition.py to key idempotence on a `.local` cache rather than the artefact field | re-filing survives a cache loss |
| AC5 | change sprint.py to default an unrecognised evidence mode instead of refusing it by name | the run names the mode that held it |
| AC6 | change sprint_report.py to count from a tally the filer wrote rather than from the filed artefacts | the close counts the survivors this run let through, by severity |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-07 | sdlc-studio | AC5 added from the plan-time seat review: product found that CR0537's count of survivors by severity was in no unit, so the visibility that bought the reporting trade did not ship with it |
| 2026-08-07 | sdlc-studio | Plan review round 1 REJECTed: the idempotence mutant was invisible to a same-fixture double run, no row covered the duplicate mint that three gate-ladder passes per `set` makes likeliest or the dry-run write it would break, the count row was satisfied by the tally implementation its own criterion rejects, and the severity provenance string had no mutant at all. AC2 is new, AC4 now deletes the cache between runs, AC6's fixture writes one artefact past the filer, AC3 holds file and name fixed, AC5 names the typo fixture, and the points move 5 to 8 |
| 2026-08-07 | sdlc-studio | Plan review round 2 ruled AC3, AC5 and the typo fixture CLOSED and two repairs MOVED. AC4 was deleting `sdlc-studio/.local/` wholesale, which is where the mutation ledger lives, so run two found no survivor and the mutant survived exactly as before - only the filer's bookkeeping is cleared now. AC2's two legs shared one fixture, so the dedupe passed both under the mutant; each leg now gets a pristine backlog and the dry run goes first. AC6's third artefact carries the header and attribution a correct reader requires |
| 2026-08-07 | sdlc-studio | Plan review round 3 APPROVEd, ruling all four round-2 findings CLOSED. Its two minors are folded in: AC4's delete is an exclusion set rather than a guessed path, and AC2 records that the dry-run leg is the lethal half so the real leg's count is not read as carrying the mutant |
| 2026-08-07 | sdlc-studio | Built. Two things the mutation check corrected. The first AC2 mutant was placed AFTER the dry-run return and SURVIVED, which is the finding rather than an error in the code: only a filing inside `_pre_write_gates` reproduces the defect, because that is the function running three times per `set` and once during a dry run. The severity rule's first cut used `len(returns) < 2` for the implicit-None path, which fires on every single-return function and derived High for the Medium fixture; the structural fact is whether the body can fall off its end |
| 2026-08-07 | sdlc-studio | AC3's verifier moved from `test_mutation.py` to `test_transition.py`, where `_survivor_severity` landed: the severity is read by the filer, and the filer lives beside the transition it hangs off |
