# US0831: per-shard wall clock is recorded and the job cap is set from the measured figure

> **Status:** Draft
> **Delivers:** CR0585
> **Created:** 2026-09-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .github/workflows/lint.yml, tools/verify-corpus.sh, tools/verify-corpus-shards.txt, tools/tests/test_verify_corpus.py, tools/tests/test_lint_workflow_coverage.py
> **Epic:** EP0254
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As an** operator paying for the runners this lane occupies
**I want** each shard's wall clock and the billed total recorded, and the cap derived from them
**So that** the lane's cost is chosen from measurement rather than arithmetic, and a latency win is not paid for with an invisible bill

## Acceptance Criteria

Sharding trades one visible cost for N cheaper ones that are billed together: the wait falls from 85.6 minutes to roughly the slowest shard, while the runner minutes billed are the SUM and can only rise. Both figures must be recorded or the lane looks cheaper than it is. THE SHARD FILE is `tools/verify-corpus-shards.txt`, one committed row `shards|N|why N|slowest-shard seconds|ci run id`, the single place N is written. The cap is the sharper edge: a job killed at its ceiling is marked failure, which reads exactly like a corpus regression, and the 90 minutes this job held was sized on the first of three measurements that then spread 9.7 minutes apart.

### AC1: the collector reports the wait and the bill as two figures, never one

- **Given** 4 SHARD REPORTS carrying wall clocks of 9, 11, 10 and 24 minutes
- **When** `verify-corpus.sh collect` reports
- **Then** its output names each shard's wall clock, the slowest shard by index as the lane's WAIT, and the sum of the four as the BILLED runner minutes, labelled as such and stated beside the 85.6-minute serial figure the lane replaces
- **Mutant:** print the slowest shard's 24 minutes alone as the lane's cost - the 54 billed minutes disappear from every report anybody reads, which is the trade this epic was consulted on and told not to make silently
- **Verify:** pytest tools/tests/test_verify_corpus.py::ShardCostTests::test_the_wait_and_the_billed_total_are_both_reported

### AC2: the cap is derived from a CI measurement, and N is recorded with its reason

- **Given** THE SHARD FILE and `.github/workflows/lint.yml`, both as committed
- **When** both are read
- **Then** THE SHARD FILE's row carries all five fields with the slowest-shard seconds as a number and the ci run id as digits, its `why N` field names both the wait N buys and the billed minutes N costs, and the shard job's `timeout-minutes` is at least 1.5 times the recorded slowest-shard figure, rounded up to the minute
- **Mutant:** set the cap by dividing the serial 85.6 minutes by N and citing no run - that is the same arithmetic that sized the 90 this job held, which left 4 minutes of headroom against measurements that then spread 9.7 minutes apart, and BG0676 proved a figure not taken in CI inadmissible for this lane
- **Verify:** pytest tools/tests/test_lint_workflow_coverage.py::ShardCapTests::test_the_cap_is_derived_from_the_recorded_ci_measurement

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Created via `new` (deterministic) |
