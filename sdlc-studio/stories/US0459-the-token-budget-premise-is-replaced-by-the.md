# US0459: The token-budget premise is replaced by the measured one everywhere it is asserted: transcript-measured, and a lower bound because delegated spend is supplied not measured

> **Status:** Review
> **Delivers:** CR0431
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/trd.md, sdlc-studio/decisions.md, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/loop_guard.py, .claude/skills/sdlc-studio/scripts/handoff.py, tools/tests/test_token_premise.py
> **Epic:** EP0168
> **Points:** 3

## User Story

**As a** future reader weighing whether a token breaker is appropriate
**I want** every live copy of the reason - the TRD, the D0020 row and the shipped payload strings - to state the real limit rather than the falsified one
**So that** the decision is re-argued against what the code can actually observe, and amending the row does not leave nine copies of the claim it contradicts

## Acceptance Criteria

### AC1: a measuring session_tokens refuses the cannot-observe claim

- **Given** a synthetic harness transcript and lib/run_state.session_tokens (run_state.py:507) reading it
- **When** the guard calls the function, observes it returns a measured total, and then reads the two TRD passages (trd.md:625-629 and the Won't Have bullet at :1055-1057) and the D0020 row
- **Then** none of them states that a script cannot observe token spend; the verdict is derived from the call's result, so if the measurement were ever removed the claim would be permitted again rather than banned by a hardcoded rule
- **Verify:** pytest tools/tests/test_token_premise.py::TokenPremiseMatchesTheCode::test_a_measuring_session_tokens_refuses_the_cannot_observe_claim
- **Verified:** yes (2026-07-29)

### AC2: the recorded limit matches the delegated lower-bound behaviour

- **Given** a run record carrying a supplied delegated total (run_state.delegated_total, :901) alongside a measured session total
- **When** the guard confirms the delegated figure is supplied rather than measured and is excluded from the measured total, then reads the reason the TRD and D0020 give for a breaker being or not being appropriate
- **Then** both documents state that reason - tokens are transcript-measured but a lower bound because delegated and sidechain spend is invisible - rather than the falsified premise or a vaguer restatement
- **Verify:** pytest tools/tests/test_token_premise.py::TokenPremiseMatchesTheCode::test_both_documents_state_the_delegated_lower_bound_reason
- **Verified:** yes (2026-07-29)

### AC3: no live file still asserts the falsified premise

- **Given** the nine live sites the sweep finds today - reference-config.md:249, reference-sprint.md:634, loop_guard.py:23, handoff.py:555 and sprint.py:30, :594, :636, :1245, :3209 - and a named allowlist of immutable historical records (CHANGELOG.md, closed change-requests, handoffs, retros) that must not be rewritten
- **When** the guard sweeps tracked .md and .py files outside that allowlist for the 'cannot observe token spend' family of phrasings
- **Then** it finds none, and reintroducing the phrase in a fixture file outside the allowlist reddens the sweep - so the epic's own LL0016 rule about two copies of one contract is held rather than only cited
- **Verify:** pytest tools/tests/test_token_premise.py::ThePremiseIsGoneFromEveryLiveFile::test_no_live_file_outside_the_history_allowlist_asserts_the_premise
- **Verified:** yes (2026-07-29)

### AC4: the amended D0020 row cites no file that no longer says what it is cited for

- **Given** the D0020 row, whose current Rationale reads 'No script can observe token spend (telemetry.py states this)' while telemetry.py no longer asserts it anywhere
- **When** the guard extracts every file path the amended row cites and reads each cited file for the claim it is cited as supporting
- **Then** each citation is borne out by the file it names, so a rotted citation fails; the check is derived by reading the cited file, so the row cannot keep pointing at evidence that has moved
- **Verify:** pytest tools/tests/test_token_premise.py::ThePremiseIsGoneFromEveryLiveFile::test_the_d0020_citation_is_borne_out_by_the_file_it_names
- **Verified:** yes (2026-07-29)

### AC5: an absent D0020 row fails rather than passing silently

- **Given** a fixture decisions log from which the D0020 row has been removed or renumbered
- **When** the guard tries to resolve the row it is asserting against
- **Then** it fails with a message naming the row it could not find, so a deleted decision cannot read as a compliant one - the empty-input clean verdict that hides the whole class
- **Verify:** pytest tools/tests/test_token_premise.py::ThePremiseIsGoneFromEveryLiveFile::test_a_missing_d0020_row_fails_rather_than_passing_silently
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: authored from the reviewed breakdown (two adversarial rounds), scope capped to the request per D0069 |
