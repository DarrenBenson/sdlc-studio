# US0660: A surviving mutant becomes a severity-rated bug and the transition proceeds, and the run names the mode that held it

> **Status:** Ready
> **Delivers:** CR0537
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Epic:** EP0212
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** A surviving mutant becomes a severity-rated bug and the transition proceeds, and the run names the mode that held it
**So that** CR0537 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: a survivor is filed and the transition proceeds

- **Given** a repair whose ledger records one surviving mutant, under the default mode
- **When** `transition.py set --id BG0001 --status Fixed` runs through the shipped verb
- **Then** it exits 0, the artefact reads `Fixed`, and a new bug exists naming the unit, the
  criterion, the mutant and the test that failed to kill it - the finding reaches the backlog
  rather than dying with the terminal window
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::SurvivorFilingCLITests::test_a_survivor_is_filed_and_the_close_proceeds

### AC2: severity is derived, and says what it read

- **Given** three survivors - one inside a function that raises, one inside a function that only
  reports, and one on a module-level constant
- **When** each is filed
- **Then** they carry High, Medium and Low, and each names the structural signal its severity was
  read from, so triage has something to sort on and something to disagree with
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::SurvivorSeverityTests::test_severity_is_derived_from_the_enclosing_function

### AC3: re-filing is idempotent

- **Given** a survivor already filed, its fingerprint stamped on the artefact rather than held in
  a cache that a cache loss would re-mint from
- **When** the same transition runs again on the same survivor
- **Then** no second bug is minted and the output names the existing finding
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::SurvivorFilingCLITests::test_the_same_survivor_does_not_mint_a_second_bug

### AC4: the run names the mode that held it

- **Given** a project setting `review.mutation_evidence: block` and one leaving it absent
- **When** the close's mutation note is composed
- **Then** each names its resolved mode, and an unrecognised value is refused BY NAME rather than
  defaulted - a typo must not silently switch a project's hard bar off
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::MutationEvidenceModeTests::test_the_close_names_the_resolved_mode

### AC5: the close counts the survivors this run let through, by severity

- **Given** a run that filed three survivor bugs at High, Medium and Low
- **When** the close report is composed
- **Then** it states the count by severity, derived from the filed artefacts rather than from a
  tally kept alongside them, because reporting rather than blocking is a trade the operator only
  gets to make if the thing traded away is visible: a survivor filed and never counted is a
  survivor silently dropped, which is the outcome blocking was rejected in favour of avoiding,
  not the outcome that was chosen
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::MutationSurvivorCountTests::test_the_close_counts_survivors_by_severity

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | change transition.py to report the survivor in the warning and mint nothing | a survivor is filed and the transition proceeds |
| AC2 | collapse the derived severity in mutation.py to a uniform Medium | severity is derived, and says what it read |
| AC3 | change transition.py to key idempotence on a .local cache rather than the artefact field | re-filing is idempotent |
| AC4 | change sprint.py to default an unrecognised evidence mode instead of refusing it by name | the run names the mode that held it |
| AC5 | change sprint_report.py to state a survivor total with no severity split | the close counts the survivors this run let through, by severity |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-07 | sdlc-studio | AC5 added from the plan-time seat review: product found that CR0537's count of survivors by severity was in no unit, so the visibility that bought the reporting trade did not ship with it |
