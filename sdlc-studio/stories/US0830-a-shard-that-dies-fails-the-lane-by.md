# US0830: a shard that dies fails the lane by name, so a lost shard can never read as a corpus that got smaller

> **Status:** Draft
> **Delivers:** CR0585
> **Created:** 2026-09-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .github/workflows/lint.yml, tools/verify-corpus.sh, tools/tests/test_verify_corpus.py, tools/tests/test_lint_workflow_coverage.py
> **Epic:** EP0254
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** reader of a red corpus job
**I want** a shard that died to fail the lane by name rather than shrink the union
**So that** a lost runner is never read as a corpus that got smaller, and never answered by lowering the baseline

## Acceptance Criteria

The lane blocks in BOTH directions, and its remedy for a count BELOW the baseline is to lower the baseline in the same commit. That remedy is correct for repairs and catastrophic for a lost shard: a runner killed at its cap would hand the operator a smaller number and an instruction to bank it. A SHARD REPORT is the file a shard writes for its own slice - its index, the N it partitioned under, the identities it was assigned, the identities it executed, the red ones among them, and a completion marker written last. THE REPORTS DIRECTORY is where the collector finds them, overridable for test as the baseline and corpus roots already are.

### AC1: an absent or short SHARD REPORT fails the lane by name and judges nothing

- **Given** N of 4, a fixture baseline recording 6 red identities, and THE REPORTS DIRECTORY holding shard 0 absent and shard 2 present but short - its executed list a prefix of its assigned list - while shards 1 and 3 are complete and hold 3 of the baseline's 6 between them
- **When** `verify-corpus.sh collect` runs
- **Then** it exits non-zero naming shard 0 as absent and shard 2 as incomplete with the count of identities it was assigned and never executed, and prints no baseline comparison - in particular no count, and none of the `fewer`, `Good news that must be BANKED` or `lower the ... row` text the serial lane prints when a count falls
- **Mutant:** union the missing and short shards as empty red sets - the run then reports 3 against a baseline of 6 and tells the operator to bank a 50% improvement that is a lost runner, which is the exact reading BG0676 AC5 takes off this job
- **Verify:** pytest tools/tests/test_verify_corpus.py::LostShardTests::test_a_missing_or_short_shard_refuses_and_never_lowers_the_count

### AC2: a shard killed part-way through cannot leave a report that looks complete

- **Given** a shard running its slice against a fixture corpus of stories at Done, killed by SIGKILL after it has produced verdicts for part of its assigned list
- **When** the collector reads what that shard left behind
- **Then** the report carries no completion marker and is refused by AC1's path, because the marker is written only after every assigned identity carries a verdict and is the last thing the shard writes
- **Mutant:** write the report when the shard starts and update it as verdicts arrive - a shard killed at the cap then leaves a complete-looking report holding a prefix of its slice, and the union is short by a set nobody can name
- **Verify:** pytest tools/tests/test_verify_corpus.py::LostShardTests::test_a_killed_shard_leaves_no_complete_report

### AC3: the collector runs whatever the shards' conclusions, so the lane's verdict is the lane's

- **Given** `.github/workflows/lint.yml` with the shard matrix and the collector job
- **When** the workflow is read
- **Then** the collector job runs on the shards' completion rather than only on their success, each shard uploads its SHARD REPORT whether the shard passed, failed or timed out, and the collector's own step is what decides the job conclusion a reader takes as the corpus verdict
- **Mutant:** leave the collector on a plain `needs:` with no always-run condition - one timed-out shard skips the collector entirely, the workflow conclusion is a bare failure, and a lost runner is once again indistinguishable from a corpus regression
- **Verify:** pytest tools/tests/test_lint_workflow_coverage.py::ShardCollectorJobTests::test_the_collector_runs_even_when_a_shard_dies

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Created via `new` (deterministic) |
