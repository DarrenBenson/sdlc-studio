# BG1236: Run six's landings left five repo-wide census tests red, which the push gate's full suite refused

> **Status:** Fixed
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/cursor_usage_hook.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_timeout_reaps.py, tools/tests/test_pre_commit_docgen.py, .claude/skills/sdlc-studio/scripts/tests/test_root_census.py, tools/tests/test_skill_tests_env.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding_bare_url.py, .claude/skills/sdlc-studio/scripts/tests/test_meter_cursor.py, sdlc-studio/reviews/root-census.md, .claude/skills/sdlc-studio/scripts/tests/test_root_anchor_contract.py, .claude/skills/sdlc-studio/scripts/tests/test_gitutil.py, tools/tests/test_commit_msg_hook.py, .claude/skills/sdlc-studio/reference-sprint.md, changelog.d/BG1236.md
> **Evidence:** push gate on devserver1, log /home/ops/sdlc-gate/local/0a5547c617a649df/boundary-suite-last.log
> **Created:** 2026-11-05
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-05T16:10:15Z

## Summary

2026-11-05, the push of c824c438. The per-commit selection never ran five repo-wide sweeps that this run's new code trips: an unconfined raw git call (likely lib/lanes.py, US1118), the root census for a new --root script (`cursor_usage_hook.py`, US1121), a test invoking the commit hook bare, and an unregistered environment scrub site (one of the new hook or lane tests). The push gate's full suite read 5 red of 8,532.

## Steps to Reproduce

1. Push main at c824c438 or later.
2. The full-suite lane on the gate host reads these five red.

## Proposed Fix

Confine the git calls through the shared helper, classify the new script in the root census, route hook invocations through the hermetic helper, and use or register the shared scrub, preferring a fix in the new files over a registry edit.

## Acceptance Criteria

- [ ] **AC1** No module calls git without a confined environment (the gitutil sweep passes on main).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gitutil.py::UnconfinedRawGitCallSweepTests::test_no_module_calls_git_without_a_confined_environment
  - **Verified:** yes (2026-11-05)
- [ ] **AC2** The root census's summary counts are the measured counts.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_root_census.py::RootCensusTests::test_the_summary_counts_are_the_measured_counts
  - **Verified:** yes (2026-11-05)
- [ ] **AC3** Every root-declaring script, the new `cursor_usage_hook.py` included, is classified with a reason.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_root_census.py::RootCensusTests::test_every_root_declaring_script_is_classified_with_a_reason
  - **Verified:** yes (2026-11-05)
- [ ] **AC4** No test file invokes the commit hook bare.
  - **Verify:** pytest tools/tests/test_commit_msg_hook.py::HookInvocationHermeticityTests::test_no_other_test_file_invokes_the_hook_bare
  - **Verified:** yes (2026-11-05)
- [ ] **AC5** Every environment scrub site is registered, or uses the shared scrub.
  - **Verify:** pytest tools/tests/test_skill_tests_env.py::ScrubSiteSweepTests::test_every_scrub_site_is_registered
  - **Verified:** yes (2026-11-05)

## Impact

Main cannot be pushed until these pass.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-05 | claude | Filed |
