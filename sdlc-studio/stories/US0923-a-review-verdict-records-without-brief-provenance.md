# US0923: A review verdict records without brief provenance

> **Status:** Done
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_brief_optional.py, changelog.d/US0923.md, AGENTS.md, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_file_history.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_plan_phase.py, sdlc-studio/bugs/BG0672-critic-record-accepts-a-brief-fingerprint-no-brief.md, sdlc-studio/stories/US0578-recording-a-verdict-with-no-brief-provenance-is.md
> **Epic:** EP0263
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer recording a reviewer's verdict
**I want** `critic.py record` to accept a verdict with or without `--brief`, never matching or refusing the fingerprint, while `critic.py brief` keeps briefing the seat
**So that** a review is recorded in one step, and the shipped brief is used because it is useful, not because a fingerprint check demands it

## Acceptance Criteria

- **AC1:** Given a fixture project setting `review.require_brief_provenance: true`, when `critic.py record` runs with no `--brief`, then the verdict is recorded with exit 0 and no provenance refusal or note; and `critic.py brief --unit <id> --seat qa` still prints the seat charter, the bounded diff scope and the unit's criteria. Fails on: HEAD's provenance refusal, and on a deletion that takes the brief verb with it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_brief_optional.py::BriefProvenanceGoneTests::test_record_needs_no_brief
  - **Verified:** yes (2026-09-26)
- **AC2:** Given a fixture with seat cards under `sdlc-studio/personas/seats/`, when `critic.py record --brief` runs once with a non-hex value and once with a 12-hex value matching no brief, then each row stores the value as given, unmarked, with no refusal; and a historical row whose brief cell carries `<fingerprint> unmatched` still reads as having no fingerprint, so two such rows sharing a value do not answer a REJECT. Fails on: HEAD, which refuses the non-hex value and marks the unmatched fingerprint; deleting the mark's reader (`critic._brief_key`) with its writer, which lets the 26 marked rows in this repository start pairing
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_brief_optional.py::BriefProvenanceGoneTests::test_a_brief_value_is_stored_not_judged
  - **Verified:** yes (2026-09-26)
- **AC3:** Given config-defaults.yaml, then it carries no `review.require_brief_provenance` and no shipped script reads it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_brief_optional.py::BriefProvenanceGoneTests::test_the_provenance_key_is_retired
  - **Verified:** yes (2026-09-26)
- **AC4:** Given the criteria whose stamped Verify selector names a test this story deletes (the refusal and stand-down tests in BriefProvenanceTests, and all of UnmatchedBriefFingerprintTests): US0577 (2) and BG0672 (5), then each is retired in the D0259 pattern (`Verify: manual - retired by US0923: <why>`, `Verified: manual (<date>) - retired, superseded by US0923`), and no `Verified: yes` selector under sdlc-studio/ names a deleted test node. `AbsentBriefTests` (BG0625) and the print, record and stability tests in BriefProvenanceTests (US0578) stay
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_brief_optional.py::BriefProvenanceGoneTests::test_no_stamp_names_a_deleted_test
  - **Verified:** yes (2026-09-26)

## Notes

- The old AC3 (the brief verb still briefs) passed at HEAD, so it is now the control half of AC1.
- `AbsentBriefTests` guards `_unanswered_rejects`' brief-key rule, which survives, so it is kept.
- Lands after US0914 (which scopes the fingerprint second key to historic rows) and US0919 (the panel interlock at critic.py 2231).
- `help/status.md` and `help/help.md` document `status --brief`, a different flag, so they left Affects. The shared prose edits to `reference-sprint-toolchain.md` and `reference-scripts-review.md` moved to US0924.
- - Re-measured at 013a46d0: `require_brief_provenance: true` at config-defaults.yaml 92, read at `critic.py` 4516; `UNMATCHED_MARK` at 107 and its reader `_brief_key` near 811. 26 verdict rows carry the mark (BG0676, US0844, US0890 among them). The writer and the refusal go; the reader stays.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
| 2026-09-25 | Engineering seat | Groomed for Sprint 4 from the readiness review: 2 -> 3 points; AC2 fixture has seat cards and tries a non-hex and an unmatched 12-hex value; the old AC3 control folded into AC1; the stamp criterion keeps AbsentBriefTests and the surviving BriefProvenanceTests (US0577 (2) and BG0672 (5) retire); Affects drops help/status.md and help/help.md, moves reference-sprint-toolchain.md and reference-scripts-review.md to US0924, and adds the changelog fragment |
| 2026-09-25 | sdlc-studio v6 planning | Sprint 5 grooming (engineering seat): AC2 adds the historical control that a marked row still reads as unbriefed |
| 2026-09-26 | sdlc | Landed: AC4's wording names US0577 where the retired stamps are US0578 AC1 and AC3, and AC2's 26 marked rows are 29; the retirements follow the real stamps (QA round 1) |
