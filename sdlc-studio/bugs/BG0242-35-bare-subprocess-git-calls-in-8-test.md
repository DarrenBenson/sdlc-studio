# BG0242: 35 bare subprocess git calls in 8 test modules bypass the confined helper entirely

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_gate.py,.claude/skills/sdlc-studio/scripts/tests/test_sprint.py,.claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py,.claude/skills/sdlc-studio/scripts/tests/test_mutation.py
> **Created:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Disclosed by BG0230's fix rather than found after it. BG0230 confined `gitutil.git_env` so a fixture git call can no longer be redirected at the parent repository by a polluted environment, and pinned every scrub list against drift. But 35 call sites in 8 test modules call subprocess.run(['git', ...]) directly and never reach gitutil at all, so the fix does not cover them: `test_gate` 10, `test_sprint` 8, `test_engagement_floor` 6, `test_mutation` 4, `test_sprint_rolling` 3, `test_status` 2, `test_deploy` 1, `test_flow` 1. tools/skill-tests.sh scrubs the environment for them only when the suite is run THROUGH that script - and not under the plain `unittest discover` command that BG0230's own reproduction steps use, which is also how an agent typically runs one module. The hole is bounded and visible rather than closed: BG0230 froze the count as a ratchet (`UNCONFINED_RAW_GIT_CALLS)` that fails on any rise or any new module, so it cannot silently grow, but the existing 35 remain reachable. This is the same data-loss class the repo has already suffered twice - once as BG0230 itself, and again inside RUN-01KY1WCR round 3, where an unscrubbed fixture wrote its own tree into the real repo's pending index under `git commit -a`, reproduced on three victim repos.

## Steps to Reproduce

1. Ensure the shell carries a repo-locating `GIT_` variable, as `git commit -a` supplies to a
   hook (`GIT_INDEX_FILE` pointing at the outer repo).
2. Run one affected module directly rather than through `tools/skill-tests.sh`:

   ```text
   python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_sprint.py
   ```

3. The bare `subprocess.run(["git", ...])` fixtures inherit that environment, so git resolves the
   repository from the environment rather than from `cwd`.

**Do NOT reproduce this next to a live repo.** L-0158 records the filed reproduction being
followed literally and damaging a live tree. BG0230's own reproduction was built with a
purpose-made victim repo inside `mktemp -d` for exactly this reason.

## Proposed Fix

Route the 35 sites through the confined helper rather than scrubbing at 35 call sites: gitutil.git already drops the 11 repo-locating variables and fences discovery with `GIT_CEILING_DIRECTORIES`, and it is the single canonical Python list. Convert module by module, lowering BG0230's `UNCONFINED_RAW_GIT_CALLS` ratchet as each is cleared, so progress is measured rather than asserted - and never raise the number to make a red gate green. Where a test genuinely needs a raw call, it must pass an explicit env and be registered in `SCRUB_SITES` so the existing sweep pins it. Verify by running an affected module under a deliberately polluted environment against a throwaway victim repo, confirming the victim's index is byte-identical afterwards.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Filed |
