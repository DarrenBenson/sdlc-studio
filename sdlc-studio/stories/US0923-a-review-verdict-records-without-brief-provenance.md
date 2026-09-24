# US0923: A review verdict records without brief provenance

> **Status:** Draft
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/help/status.md, .claude/skills/sdlc-studio/help/help.md, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/reference-scripts-review.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_brief_optional.py
> **Epic:** EP0263
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer recording a reviewer's verdict
**I want** `critic.py record` to accept a verdict with or without `--brief`, never matching or refusing the fingerprint, while `critic.py brief` keeps briefing the seat
**So that** a review is recorded in one step, and the shipped brief is used because it is useful, not because a fingerprint check demands it

## Acceptance Criteria

- **AC1:** Given a fixture project setting `review.require_brief_provenance: true`, when `critic.py record` runs with no `--brief`, then the verdict is recorded with exit 0 and no provenance refusal or note
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_brief_optional.py::BriefProvenanceGoneTests::test_record_needs_no_brief
- **AC2:** Given `critic.py record --brief <value>`, when it runs, then the row stores the value as given, never matched against a regenerated brief or marked unmatched, and no format refusal fires
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_brief_optional.py::BriefProvenanceGoneTests::test_a_brief_value_is_stored_not_judged
- **AC3:** Given `critic.py brief --unit <id> --seat qa`, when it runs, then it still prints the seat charter, the bounded diff scope and the unit's criteria
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_brief_optional.py::BriefProvenanceGoneTests::test_the_brief_verb_still_briefs
- **AC4:** Given config-defaults.yaml, then it carries no `review.require_brief_provenance` and no shipped script reads it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_brief_optional.py::BriefProvenanceGoneTests::test_the_provenance_key_is_retired
- **AC5:** Given every criterion whose stamped Verify selector names a test this story deletes (BriefProvenanceTests, UnmatchedBriefFingerprintTests and AbsentBriefTests; at least those on BG0625, BG0672, US0577, US0578), then each is retired as `Verify: manual - retired by <this story>` with a matching `Verified: manual` line, and no `Verified: yes` selector under sdlc-studio/ names a deleted test node, so the stamps-staged lane has nothing to refuse
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_brief_optional.py::BriefProvenanceGoneTests::test_no_stamp_names_a_deleted_test

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
