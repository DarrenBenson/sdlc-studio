# BG0676: the scheduled corpus-verify lane is red on main - 40 red criteria against a baseline of 20 - and every one of the 20 new ones passes locally

> **Status:** Open
> **Severity:** Medium
> **Points:** 5
> **Depends on:** BG0659, BG0661, BG0662, BG0664, BG0665, BG0666, BG0667, BG0668, BG0669, BG0670, BG0671, BG0672, BG0673, BG0674, BG0675, US0625, US0626, US0627, US0628, US0823
> **Affects:** .github/workflows/lint.yml, tools/verify-corpus.sh, tools/verify-corpus-baseline.txt, .claude/skills/sdlc-studio/scripts/gate.py, tools/tests/test_lint_workflow_coverage.py
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sprint planning 2026-09-15; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Lint run 34830172971 (schedule, 2026-09-14, main at 28682ce2) failed `corpus-verify`: 'red-criteria: 40, baseline 20 - the SET moved', naming 20 NEW red criteria: US0031 AC3, US0220 AC2, US0284 AC1, US0597 AC1-AC3, US0663 AC2, US0674 AC1, US0815 AC1-AC6, US0816 AC1-AC4 and AC7-AC9 (and US0666 AC2 went green). Run locally at 51f264db with raw pytest, every one of the 20 passes: the seven non-coverage selectors individually, and all 82 tests behind US0815, US0816 and US0674 together (coverage 7.15 installed). So the lane is reporting an environment difference, not a regression (LL0011), and a scheduled red nobody reads is the BG0653 shape. Three candidate causes, unproven: (1) the corpus job installs only `pyyaml pytest`, not `coverage` - the package US0815/US0816's criteria need; (2) its checkout is shallow (actions/checkout default depth 1), which history-replaying criteria (US0597's claim-drift replays) may need; (3) the red pass runs `gate.py --release`, whose verifiers take the 120 s default timeout, and GateRealWrapperTests (US0031, US0284) take ~136 s locally. The push hook reads push-triggered runs only, so nothing blocks on it - which is how it stays unread.

## Steps to Reproduce

1. `gh run view 34830172971 --json jobs` - corpus-verify failed at 'Corpus verification (dead stamps + red criteria, against the baseline)'.
2. Its log: 'red-criteria: 40, baseline 20 - the SET moved' and the NEW list.
3. Locally, run each NEW criterion's Verify selector with raw pytest - all pass.
4. Compare the corpus-verify job in .github/workflows/lint.yml with the skill-tests job: no coverage install, default shallow checkout.

## Proposed Fix

Settle the cause by experiment, not by reading: dispatch the lane with each candidate corrected in turn (coverage>=7.10 installed as the skill-tests job does; fetch-depth 0; a verifier timeout above the slowest criterion), and keep only what moves the count. Then pin the job's environment in a test the way `test_lint_workflow_coverage` pins the skill-tests job, so the two jobs cannot drift apart again.

## Acceptance Criteria

- [ ] **AC1** The corpus-verify job installs coverage at the floor the line-coverage criteria need, pinned by a test that reads that job's own steps
  - **Verify:** pytest tools/tests/test_lint_workflow_coverage.py::CorpusJobEnvironmentTests::test_the_corpus_job_installs_coverage
- [ ] **AC2** The release verify lane's per-verifier timeout (`gate.VERIFY_TIMEOUT`, a bare 120 s constant today) can be set, and the corpus job sets it above the slowest criterion it runs, pinned by a test naming both
  - **Verify:** pytest tools/tests/test_lint_workflow_coverage.py::CorpusJobEnvironmentTests::test_the_corpus_job_gives_history_and_time
- [ ] **AC3** The baseline is re-measured from a CI run, not a local one, and records every criterion that moved in either direction - US0666 AC2 went green in CI, and the lane fails on a move either way. Every id ADDED to the baseline names the bug filed for it or the proven environment cause, so the re-measure cannot bank whatever CI happens to read
  - **Verify:** pytest tools/tests/test_lint_workflow_coverage.py::CorpusJobEnvironmentTests::test_the_baseline_names_its_ci_run
- [ ] **AC4** A corpus-verify run dispatched on the commit BG0676 closes on passes against that baseline - BG0676 depends on every other unit in the batch, so it is delivered LAST and that commit carries the whole batch; a green run mid-sprint cannot stand in for the tree that ships
  - **Verify:** shell gh run list --workflow Lint --event workflow_dispatch --commit "$(git rev-parse HEAD)" --limit 1 --json conclusion --jq '.[0].conclusion' | grep -qx success

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sprint planning 2026-09-15 | Filed |
| 2026-09-15 | sprint planning 2026-09-15 | Distinct from BG0657 (Fixed), which made the corpus lane name WHICH criteria are new; this is the lane red again, at 40 against 20, for what the local runs show is an environment difference. |
| 2026-09-15 | sprint planning 2026-09-15 | Re-groomed at the sprint goal review (round 1): the CI check is bound to the CLOSING sha; the baseline file and gate.py's bare VERIFY_TIMEOUT join Affects, since the fix cannot pass without them; the baseline is re-measured from CI. The lane has failed all 8 scheduled runs since 2026-07-27 (dead-stamps before 09-14), so the goal says 'passes', not 'green again'. 3 -> 5 points. |
| 2026-09-15 | sprint planning 2026-09-15 | Goal review round 2 repairs: depends on every other batch unit so it is delivered last and AC4's dispatch runs on the commit that carries the whole batch; each id added to the re-measured baseline must name its bug or proven cause, so the baseline cannot bank whatever CI reads. |
