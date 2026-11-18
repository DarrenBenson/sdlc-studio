# US1291: Sprint sign under delegation requires an accepted authorising decision id and records it in the signature block

> **Status:** Done
> **Risk-class:** standard
> **Delivers:** CR0729
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_sign_principal.py, changelog.d/US1291.md
> **Epic:** EP0366
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** Sprint sign under delegation requires an accepted authorising decision id and records it in the signature block
**So that** CR0729 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A delegated signature with no accepted decision is refused

- **Given** a closed run awaiting signature, and a decisions log holding one accepted decision and one superseded decision
- **When** `sprint.py sign --report <id> --principal <operator>` is entered as a delegated signature with no decision id, with an id the log does not hold, and with the superseded one
- **Then** each exits non-zero with a `sign REFUSED:` line naming the decision it needs, the run stays open and its record holds no signature. Fails on: a delegated signature sealed with no decision, or with one the log does not show as accepted
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_sign_principal.py::DelegatedSignatureTests::test_a_delegated_signature_without_an_accepted_decision_is_refused
- **Verified:** yes (2026-11-18)

### AC2: The signature block records the delegation and its decision

- **Given** the same closed run and the accepted decision
- **When** the delegated signature is entered naming that decision's id
- **Then** the command exits 0, the run is sealed, the run record's `signature` block states that the signature was delegated and holds the decision id beside the principal, and the `sealed` line names the decision. Fails on: a delegated seal whose signature block reads as one the operator entered
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_sign_principal.py::DelegatedSignatureTests::test_a_delegated_signature_records_its_decision_in_the_signature_block
- **Verified:** yes (2026-11-18)

### AC3: A signature the operator enters needs no decision

- **Given** a closed run awaiting signature
- **When** `sprint.py sign` is entered with no delegation option
- **Then** the run is sealed as it is today and its signature block carries no delegation and no decision id. Fails on: every signature being asked for a decision id, or an undelegated signature recorded as delegated
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_sign_principal.py::DelegatedSignatureTests::test_an_undelegated_signature_seals_without_a_decision
- **Verified:** yes (2026-11-18)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-17 | Claude Opus 5.5 (run sixteen) | Affects widened in run: its changelog fragment, which the build did not write |
