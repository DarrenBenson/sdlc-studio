# US0455: One availability contract: the PRD clause, the TSD NFR row and ADR-004 all state the fail-loud sync behaviour, and the branch taken is recorded as a decision

> **Status:** Review
> **Delivers:** CR0427
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/prd.md, sdlc-studio/tsd.md, sdlc-studio/trd.md, sdlc-studio/decisions.md, tools/tests/test_availability_contract.py
> **Epic:** EP0168
> **Points:** 3

## User Story

**As an** engineer reading the Availability NFR to decide whether sync needs a soft no-op path
**I want** the PRD clause, the TSD NFR-mapping row and ADR-004 to describe the same shipped behaviour, with the choice between rewording and implementing recorded as a decision
**So that** the requirement is testable against the acceptance signal that exists, and a later reader can see the fork was ruled on rather than quietly resolved by an editor

## Acceptance Criteria

### AC1: both spec rows agree with the measured gh-absent behaviour

- **Given** github_sync.gh() raising RuntimeError when shutil.which('gh') is None and main() returning 127 (github_sync.py:83, :745), monkeypatched in-process rather than shelled out
- **When** the guard calls the entry point, records the observed exit code, then reads the PRD Availability clause (prd.md section 5) and the TSD NFR-mapping Availability row by heading
- **Then** both passages state the fail-loud contract - the offline core pipeline needs no network, github_sync aborts non-zero and names the missing CLI - and neither says sync degrades gracefully; the verdict is computed from the observed exit code, so removing the abort would permit the graceful wording again
- **Verify:** pytest tools/tests/test_availability_contract.py::AvailabilityContractAgrees::test_the_prd_clause_and_tsd_row_match_the_measured_abort
- **Verified:** yes (2026-07-29)

### AC2: ADR-004's Consequences line is the third copy and is corrected too

- **Given** ADR-004 at trd.md:704-722, whose first Positive consequence currently reads 'sync degrades gracefully when `gh` is absent'
- **When** the guard extracts the ADR-004 block alone by its heading and the next `### ADR-` boundary, never the whole TRD, and applies the same derived rule it applied to the PRD and TSD
- **Then** the extracted block states the same fail-loud contract as the other two passages, so a reader cannot find a third answer to one question
- **Verify:** pytest tools/tests/test_availability_contract.py::AvailabilityContractAgrees::test_adr_004_block_states_the_same_contract
- **Verified:** yes (2026-07-29)

### AC3: a reintroduced graceful-degradation claim reddens the guard

- **Given** the rule exposed as a pure function over passage text, not as a monolithic assertion over the live files
- **When** it is handed a fixture passage in which the 'degrades gracefully when gh is absent' wording has been restored
- **Then** it returns a finding naming the passage and the offending claim, proving the defence fails on the exact defect it was built for rather than only passing on the repaired tree
- **Verify:** pytest tools/tests/test_availability_contract.py::AvailabilityContractAgrees::test_a_reintroduced_graceful_claim_returns_a_finding
- **Verified:** yes (2026-07-29)

### AC4: the branch taken is recorded as a decision row the guard resolves

- **Given** CR0427's acceptance criterion posing a fork - reword the PRD to the shipped contract, or keep graceful degradation and file the implementation work
- **When** the guard reads sdlc-studio/decisions.md for a row whose Decision text names CR0427 and states which branch was taken
- **Then** the row exists, names the branch, and the wording the three passages carry is the one that branch implies, so the edit is traceable to a ruling instead of to an unrecorded editorial choice
- **Verify:** pytest tools/tests/test_availability_contract.py::AvailabilityContractAgrees::test_the_branch_is_recorded_as_a_decision_row
- **Verified:** yes (2026-07-29)

### AC5: a passage or decision row that cannot be located fails loud

- **Given** fixture documents in which the PRD Availability heading, the TSD NFR row, the ADR-004 heading or the CR0427 decision row has been renamed, renumbered or removed
- **When** the guard tries to extract each
- **Then** it fails with a message naming which passage or row it could not find, and never reports a clean result for text it did not read - the empty-set pass that let the original drift survive four revisions
- **Verify:** pytest tools/tests/test_availability_contract.py::AvailabilityContractAgrees::test_a_missing_passage_or_row_fails_rather_than_reporting_clean
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: authored from the reviewed breakdown (two adversarial rounds), scope capped to the request per D0069 |
