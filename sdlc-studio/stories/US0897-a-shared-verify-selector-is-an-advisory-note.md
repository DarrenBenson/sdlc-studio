# US0897: A shared Verify selector is an advisory note within one artefact, never a commit refusal

> **Status:** Draft
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .githooks/pre-commit, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/critic.py, sdlc-studio/.verify-lint-baseline.json, package.json, AGENTS.md, tools/tests/test_baselines_only_shrink.py, tools/tests/hookutil.py, tools/tests/test_precommit_lane_order.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_duplicate_selectors.py
> **Epic:** EP0262
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** developer fixing a bug with a story
**I want** a Verify selector shared by two criteria of one artefact to be flagged to the reviewer, and a bug sharing its fixing story's selector to be left alone
**So that** a correct fix that reuses its story's test no longer needs a baseline entry to commit, and the reviewer still sees a criterion that cannot discriminate

## Acceptance Criteria

- **AC1:** Given a commit or `npm run lint`, then the verify-ratchet lane does not run: `verify_ac.py lint --ratchet`, its package.json script and sdlc-studio/.verify-lint-baseline.json are gone, and `test_baselines_only_shrink.py` no longer lists that baseline
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_duplicate_selectors.py::DuplicateSelectorTests::test_no_commit_or_lint_run_is_refused_on_a_shared_selector
- **AC2:** Given a bug and the story that fixed it naming the same Verify selector, when `verify_ac.py lint` runs, then no duplicate is reported; given two criteria of ONE artefact sharing a selector, it reports that pair and exits 0
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_duplicate_selectors.py::DuplicateSelectorTests::test_duplicates_are_judged_within_one_artefact_only
- **AC3:** Given `critic.py brief --unit <id>` for a unit two of whose criteria share a selector, then the brief carries one advisory line naming the pair; a unit whose selectors are distinct carries none
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_duplicate_selectors.py::DuplicateSelectorTests::test_the_brief_notes_a_shared_selector
- **AC4:** Given the test nodes this story deletes (the ratchet and cross-artefact duplicate tests in `test_verify_ac`, `LensSignatureLaneTests::test_the_ratchet_lane_carries_its_flags_at_both_invocation_sites`, the verify-baseline cases in `test_baselines_only_shrink)`, then every stamped criterion naming one (US0461, US0227, BG0431, BG0433, BG0603 among them) is retired in the D0259 pattern (`Verify: manual - retired by <this story>: <why>`, `Verified: manual (<date>) - retired, superseded by <this story>`), so `verify_ac.py stamps --staged` passes on the deleting commit
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_duplicate_selectors.py::RetiredCriteriaTests::test_the_verify_ratchet_criteria_are_retired

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
