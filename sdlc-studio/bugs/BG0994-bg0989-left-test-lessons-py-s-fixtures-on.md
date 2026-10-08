# BG0994: BG0989 left test_lessons.py's fixtures on the legacy lessons path, so seven tests print the migration line and CI's noise gate is red on main

> **Status:** Fixed
> **Severity:** High
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_lessons.py, changelog.d/BG0994.md
> **Evidence:** CI 37754183344 on 978083c6: 'test-noise: a PASSING run printed 110 diagnostic line(s), above the recorded full-run total of 104'; diffed against the green run 37654972314, the only additions are the migration line (7) and four unrelated run-specific lines already within the budget's churn.
> **Created:** 2026-10-08
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-08T09:50:04Z

## Summary

CI run 37754183344 (978083c6) ran 7124 tests green and failed the green-run noise gate: 110 diagnostic lines against the recorded total of 104. The six new lines, plus one folded into a progress line, are BG0989's migration message ('lessons: moved the project lessons log from .../.local/lessons.md to .../retros/LESSONS.md'), printed to stderr by seven `test_lessons.py` tests whose fixtures still seed the legacy path and capture only stdout. `test_lessons` is budgeted at 0. A regression introduced by BG0989 (mine): its migration runs on every lessons command, and the old fixtures were not moved to the committed default.

## Steps to Reproduce

Run `test_lessons.py` uncaptured and pipe it through the noise gate with its per-module budget: python3 -m pytest -q -s -n 0 tests/`test_lessons.py` | tools/`test_noise.py` --budget tools/test-noise-baseline.json --select `test_lessons` -> 7 lines above a budget of 0.

## Proposed Fix

Seed the fixtures at the committed default, sdlc-studio/retros/LESSONS.md: the legacy path is now only a migration source, and the migration is tested in `test_lessons_log_committed.py.`

## Acceptance Criteria

- [ ] **AC1** `test_lessons.py` run alone prints nothing a passing run should not, within its noise budget of 0
  - **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m pytest -q -s -p no:cacheprovider -n 0 tests/test_lessons.py 2>&1 | python3 ../../../../tools/test_noise.py --budget ../../../../tools/test-noise-baseline.json --select test_lessons
  - **Verified:** yes (2026-10-08)

## Review round 1 (APPROVE, 2026-10-08)

- APPROVE, light tier, nothing blocking. The ledger row carries the VERDICT, ISSUES and BLOCKING lines; the reviewer's evidence follows verbatim, since `critic.py record` refuses anything after `BLOCKING: none` (BG0950).
- The new finding (the fragment said the migration runs on every `lessons` command; it skips `--global` and an explicit `--project-file`) is corrected in `changelog.d/BG0994.md`. The untested read fallback is added to BG0992 as AC5. The nested-worktree `test_gate` failures are pre-existing and judged separately.

> Evidence (all in my own worktree, every mutant restored from a byte snapshot, tree clean afterwards):
>
> - AC1 oracle at e77cd2d5: the exact Verify line prints nothing and test_noise exits 0. pytest result: 139 passed, 1 skipped.
> - AC1 negative control: the base-ref test_lessons.py under the same Verify line exits 1 with "printed 7 diagnostic line(s), above the summed budget of 0", and every line is the BG0989 migration message. The fix is what turns the gate green.
> - Test mutant T1: I pointed all 8 re-seeded sites at retros/NOWHERE.md. 11 tests fail across PlanDigestTests, SummaryOutRootAnchoringTests, SummaryStalenessTests and ValidityHorizonTests, so the new seed path does matter to those tests. RevalidateTests and SummaryTests pass `--project-file` explicitly, so they do not care which path the seed uses; changing their seeds is harmless and keeps the file consistent.
> - Scope: the code change is limited to test_lessons.py fixture paths and the changelog fragment. The bug file and the derived \_index.md row are ordinary filing paperwork. No production code changed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-08 | sdlc-studio | Filed |
| 2026-10-08 | Claude Opus 5.5 (engineering seat) | QA round 1 APPROVE recorded; the fragment's over-claim corrected; the read fallback's missing pin added to BG0992 |
