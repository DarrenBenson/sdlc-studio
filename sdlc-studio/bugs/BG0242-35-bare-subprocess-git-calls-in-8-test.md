# BG0242: 35 bare subprocess git calls in 8 test modules bypass the confined helper entirely

> **Status:** Fixed
> **Verification depth:** functional - a fresh victim repo per module under `mktemp -d`, its
> worktree deliberately diverging from its index, with the hook-shaped `GIT_DIR` /
> `GIT_WORK_TREE` / `GIT_INDEX_FILE` / `GIT_PREFIX` pollution aimed at it. At HEAD, 5 of the 8
> modules rewrote that victim's index and 3 of them wiped its uncommitted state outright; after
> the conversion, none of the 9 modules touched it. Both arms were run, and the census was
> re-run rather than asserted.
> **Severity:** High
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_gate.py,.claude/skills/sdlc-studio/scripts/tests/test_sprint.py,.claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py,.claude/skills/sdlc-studio/scripts/tests/test_mutation.py
> **Created:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Disclosed by BG0230's fix rather than found after it. BG0230 confined `gitutil.git_env` so a fixture git call can no longer be redirected at the parent repository by a polluted environment, and pinned every scrub list against drift. But 35 call sites in 8 test modules call subprocess.run(['git', ...]) directly and never reach gitutil at all, so the fix does not cover them: `test_gate` 10, `test_sprint` 8, `test_engagement_floor` 6, `test_mutation` 4, `test_sprint_rolling` 3, `test_status` 2, `test_deploy` 1, `test_flow` 1. tools/skill-tests.sh scrubs the environment for them only when the suite is run THROUGH that script - and not under the plain `unittest discover` command that BG0230's own reproduction steps use, which is also how an agent typically runs one module. The hole is bounded and visible rather than closed: BG0230 froze the count as a ratchet (`UNCONFINED_RAW_GIT_CALLS)` that fails on any rise or any new module, so it cannot silently grow, but the existing 35 remain reachable. This is the same data-loss class the repo has already suffered twice - once as BG0230 itself, and again inside RUN-01KY1WCR round 3, where an unscrubbed fixture wrote its own tree into the real repo's pending index under `git commit -a`, reproduced on three victim repos.

## Sizing

RE-SIZED 3 -> 5 before work started, per D0049. The original 3 came from the reporting agent's
summary rather than from reading the call sites. A census over the 8 named modules finds 37 git
call sites of which 35 are unconfined, matching the reviewer's count exactly:

| module | git calls | unconfined |
| --- | --- | --- |
| `test_gate` | 10 | 10 |
| `test_sprint` | 9 | 8 |
| `test_engagement_floor` | 6 | 6 |
| `test_mutation` | 4 | 4 |
| `test_sprint_rolling` | 4 | 3 |
| `test_status` | 2 | 2 |
| `test_deploy` | 1 | 1 |
| `test_flow` | 1 | 1 |
| **total** | **37** | **35** |

The work is mechanical but broad, and it is not a blind sweep: `test_sprint` already HAS a confined
helper passing `gitutil.git_env()` and then bypasses it in fixture setup, so each conversion has to
check whether a confined route already exists rather than adding a second one. Each site also has
to be checked for a test that depends on ambient environment, which is the way a mechanical
conversion turns into a behaviour change.

Note the forecast is NOT re-priced: the plan recorded BG0242 at the 3-point price and
first-record-wins, so the retro will judge the original number and show the estimate missed. That
is the intended behaviour, and it is the evidence the estimator needs rather than a figure to
tidy away.

A caution for whoever takes this: a quick `subprocess.run(["git"` grep finds only 24 of the 35.
`test_sprint` imports `subprocess as _sp`, so the alias hides 11 call sites from the obvious
pattern. Count with a pattern that matches any `<name>.run(["git"`, or the sweep will report done
while a third of the hole remains.

## Acceptance Criteria

- [x] **AC1:** Every git call site in the eight named test modules routes through the confined helper: the census run with a pattern that catches the `subprocess as _sp` alias reports zero unconfined sites.
      **Verify:** shell python3 -m unittest discover -s tools/tests -p test_skill_tests_env.py
- [x] **AC2:** The sweep still FAILS on a newly planted unconfined call, including one written through an import alias, so the guard cannot pass by being blind.
      **Verify:** shell python3 -m unittest discover -s tools/tests -p test_skill_tests_env.py
- [x] **AC3:** Where a module already had a confined helper, the bare calls route through THAT helper rather than a second one being added alongside it.
      **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_sprint.py

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

## Resolution

All 35 unconfined call sites converted, per D0049. The census is 0, re-run rather than asserted:

| module | git calls | unconfined before | unconfined after |
| --- | --- | --- | --- |
| `test_gate` | 10 | 10 | 0 |
| `test_sprint` | 9 | 8 | 0 |
| `test_engagement_floor` | 6 | 6 | 0 |
| `test_mutation` | 4 | 4 | 0 |
| `test_sprint_rolling` | 4 | 3 | 0 |
| `test_status` | 2 | 2 | 0 |
| `test_deploy` | 1 | 1 | 0 |
| `test_flow` | 1 | 1 | 0 |
| **total** | **37** | **35** | **0** |

The census was taken with the AST detector, which matches `<name>.run(["git", ...])` on the
attribute rather than on the name it hangs off. The naive `subprocess.run(["git"` grep finds
only 24 of the 35: `test_sprint` and `test_sprint_rolling` both `import subprocess as _sp`, and
the alias hides 11 sites.

Where a module already had a confined route, the conversion went through it rather than adding a
second one: `test_sprint` and `test_sprint_rolling` both have a `_run` helper passing
`env=gitutil.git_env()` and were bypassing it in fixture setup, so the bare `init --bare`,
`symbolic-ref` and `clone` calls now go through `_run`. Elsewhere the module-level or
per-class `_git` helper had its body swapped for `gitutil.git`, and the handful of one-off
sites call `gitutil.git` directly. `test_deploy`, `test_flow` and `test_engagement_floor` gained
the tests-directory `sys.path` entry and the `gitutil` import they lacked.

No call site was left raw, so nothing new was registered in `SCRUB_SITES`.

One test genuinely turns on the ambient environment:
`test_gate.HookEnabledEquivalentConfigTests.test_foreign_git_dir_env_does_not_redirect_the_check`
sets `GIT_DIR` in `os.environ` and asserts that `gate.hook_enablement_gap` still evaluates the
fixture. That pollution wraps the call to the code UNDER TEST, not a fixture call, and every
fixture call in it runs before the variable is set, so confining the fixtures leaves the
property it pins intact - it still passes, and it still fails if `gate.py`'s own scrub is
removed. Nothing else read the ambient environment.

`UNCONFINED_RAW_GIT_CALLS` is now `{}` and is no longer a ratchet that may only fall: it is a
zero, and a single unconfined call in any module fails the sweep. Emptying it cost the old
anti-vacuity test (`test_the_detector_still_sees_the_modules_it_guards` asserted `test_gate` was
an offender, which is exactly what the fix stops being true), so it is replaced by two tests that
survive the debt reaching zero: a planted offender in a throwaway directory the sweep must name,
and a check that the sweep's default directory really is the suite's own. Both were confirmed to
fail on cue, and a probe planted in the live tests directory made the sweep fail naming
`{'test_bg0242_probe': (2, 0)}` - both its call sites, one of them through the `_sp` alias.

Not in scope, and still declared debt in `SCRUB_SITES`: the PARTIAL scrubs in `gate.py` and
`lessons.py`. They are why several modules still FAIL (without damaging anything) under a
polluted environment - the redirection lands in the script under test, not in a fixture. That
count fell sharply with the fix all the same: 48 failures to 8 in `test_sprint`, 18 to 9 in
`test_engagement_floor`, 11 to 9 in `test_flow`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Filed |
| 2026-07-21 | sdlc-studio | Fixed: all 35 sites converted, census re-run at 0, ratchet emptied to a zero-tolerance sweep, containment proven against a per-module victim repo |
