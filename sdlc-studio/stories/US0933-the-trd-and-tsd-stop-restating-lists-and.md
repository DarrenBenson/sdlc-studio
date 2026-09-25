# US0933: The TRD and TSD stop restating lists and counts the code derives, and the tests that pinned the restatements are deleted

> **Status:** Done
> **Delivers:** CR0594
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/trd.md, sdlc-studio/tsd.md, tools/tests/test_trd_surface_derivation.py, tools/tests/test_trd_freshness.py, tools/tests/test_spec_counts_are_not_pinned.py, sdlc-studio/stories/US0059-refresh-the-trd-to-the-shipped-script-layer.md, sdlc-studio/stories/US0458-the-trd-s-shipped-surface-enumerations-are-derived.md, sdlc-studio/bugs/BG0332-test-scope-pinned-to-a-58-script-inventory.md, sdlc-studio/bugs/BG0457-four-spec-agreement-guards-pin-prose-to-prose.md, sdlc-studio/bugs/BG0571-the-repaired-spec-agreement-guards-pin-word-patterns.md, tools/tests/test_lean_spec_restatements.py, changelog.d/US0933.md
> **Epic:** EP0264
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As** Maya Okafor, who has paid for seven units of rework keeping the specs' copies of code lists in step (BG0332, BG0401, BG0420, BG0457, BG0571, CR0302, US0766)
**I want** the TRD and TSD to say what only a person decides and point at the code for lists and counts it derives
**So that** a spec stops needing a pinning test to stay true, and the tests that pinned it go - End goal 4, "Keep specs, code, and tests in sync so the documentation never quietly drifts from reality"

## Acceptance Criteria

- **AC1:** Given the refreshed `sdlc-studio/trd.md`, then no passage outside the Revision History enumerates the gate's default lanes (at most two names from `gate.DEFAULT_CHECKS` appear in any one paragraph or table row), the router's type list or reconcile's drift kinds, and each such passage names the code that holds the list instead; the check reads the lists from the code, and is red against today's TRD, which names twelve lanes in one paragraph
  - **Verify:** pytest tools/tests/test_lean_spec_restatements.py::SpecRestatementTests::test_the_trd_enumerates_no_list_the_code_derives
  - **Verified:** yes (2026-09-25)
- **AC2:** Given the refreshed `trd.md` and `tsd.md`, then neither states a count of scripts, modules, files or tests outside its Revision History, its ADRs and the claims a shipped reader checks (`doc_freshness`'s census claims, which D0266 keeps because a non-test reader holds them), counting forms with up to two words between the number and the noun ("(40+ help files)", "70+ shipped Python scripts"); today's "(6 modules)", "well over 2,500 tests" and the TSD's "90+ modules" are cut, and neither file carries a `<!-- measured: ... -->` timing marker, whose only reader (`check_spec_claims.py`) US0879 deleted; red against today's TRD and TSD
  - **Verify:** pytest tools/tests/test_lean_spec_restatements.py::SpecRestatementTests::test_no_spec_states_a_component_count
  - **Verified:** yes (2026-09-25)
- **AC3:** Given `tools/tests/test_trd_surface_derivation.py`, `test_trd_freshness.py` and `test_spec_counts_are_not_pinned.py` are deleted, then every criterion whose stamped `Verify:` selector names one of their tests (on US0059, US0458, BG0332, BG0457 and BG0571) reads `Verify: manual - retired by <this story>` with a matching `Verified: manual` line, and no `Verified: yes` selector under `sdlc-studio/` names a deleted test node, so the stamps-staged lane has nothing to refuse
  - **Verify:** pytest tools/tests/test_lean_spec_restatements.py::SpecRestatementTests::test_no_stamp_names_a_deleted_pin
  - **Verified:** yes (2026-09-25)
- **AC4:** Given the refreshed `tsd.md`, then its `## Test Levels` section, the only part the runner reads, still parses: `sprint.tsd_levels` returns at least one level carrying a path, and `sprint.test_strategy` for a unit affecting `.claude/skills/sdlc-studio/scripts/sprint.py` assigns it a proof band; a cut that removed or reshaped the section fails it
  - **Verify:** pytest tools/tests/test_lean_spec_restatements.py::SpecRestatementTests::test_the_tsd_test_levels_still_drive_the_strategy
  - **Verified:** yes (2026-09-25)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-25 | Product seat | Groomed from CR0594's refinement: user story and criteria authored |
| 2026-09-25 | Claude Opus 5.5 | AC2 amended after round-1 review, following D0266: counts in ADRs and counts `doc_freshness`'s census reads stay, since a shipped reader holds them; the count form widened to two qualifying words |
