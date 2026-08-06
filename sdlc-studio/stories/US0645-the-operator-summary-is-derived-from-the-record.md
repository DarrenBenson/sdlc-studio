# US0645: The operator summary is derived from the record, never composed by the signing seat

> **Status:** Done
> **Delivers:** CR0532
> **Created:** 2026-08-05
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py,.claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Epic:** EP0209
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** The operator summary is derived from the record, never composed by the signing seat
**So that** CR0532 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: every figure is read back from a record, and an absent one says so

- **Given** a closed run whose cost was never recorded
- **When** the operator summary is generated
- **Then** the cost line reads UNMEASURED rather than zero, and each of - what shipped, what was rejected, what is carried with its filed id, what it cost - names the record it came from
- **Mutant:** substitute zero for an unrecorded component - the cheapest close on file is one that measured nothing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::OperatorSummaryTests::test_an_unrecorded_component_reads_unmeasured
- **Verified:** yes (2026-08-05)

### AC2: the signing seat contributes no prose to it

- **Given** two runs identical except for the free text a signing seat wrote into its verdict
- **When** the summary is generated for each
- **Then** the two summaries are identical, because the generator reads the ledger and there is no channel through which a seat's own words reach the operator's page
- **Mutant:** interpolate the verdict's note into the summary - a seat marks its own homework and the two summaries differ
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::OperatorSummaryTests::test_the_signing_seat_contributes_no_prose
- **Verified:** yes (2026-08-05)

### AC3: it names what the operator is most likely to want to overturn

- **Given** a run carrying a finding filed under the carry-forward policy and a unit approved only after a REJECT was repaired
- **When** the summary is generated
- **Then** both are named with their ids, because leading is a bounded act only if the summary says where to look
- **Mutant:** list the delivered units alone - the summary is a manifest, and the operator must re-read the batch to lead it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::OperatorSummaryTests::test_the_reversal_candidates_are_named_with_their_ids
- **Verified:** yes (2026-08-05)

### AC4: a summary is generated for a human sign-off too

- **Given** a run closed on an operator's own sign-off
- **When** the summary is generated
- **Then** it is produced identically and states the capacity, because a second code path for the human case is a path that drifts
- **Mutant:** generate it only on the panel path - the human close and the seat close diverge
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::OperatorSummaryTests::test_the_summary_is_generated_for_a_human_signoff_too
- **Verified:** yes (2026-08-05)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-05 | sdlc-studio | Created via `new` (deterministic) |
