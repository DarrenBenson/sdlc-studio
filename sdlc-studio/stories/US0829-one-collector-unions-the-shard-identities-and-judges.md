# US0829: one collector unions the shard identities and judges them against the single baseline, naming NEW, went-green and VANISHED as the serial lane does

> **Status:** Won't Implement
> **Closed with findings in:** D0265 backlog sweep 2026-09-24 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md), RETIRE
> **Delivers:** CR0585
> **Created:** 2026-09-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .github/workflows/lint.yml, tools/verify-corpus.sh, tools/verify-corpus-baseline.txt, tools/verify-corpus-shards.txt, tools/tests/test_verify_corpus.py, tools/tests/test_lint_workflow_coverage.py
> **Epic:** EP0254
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** reviewer of record reading a corpus verdict
**I want** one collector to judge the union of the shards against the single baseline
**So that** the verdict says what the serial lane's said, and no criterion changes its status by moving between shards

## Acceptance Criteria

The baseline stays one file and one row per metric, because a per-shard baseline hides a criterion moving between shards. THE SHARD FILE is `tools/verify-corpus-shards.txt`, one committed row `shards|N|why N|slowest-shard seconds|ci run id`, the only place N is written and the one both the partitioner and the collector read. A SHARD REPORT is what a shard writes for its own slice: its index, the N it partitioned under, the identities it was assigned, the identities it executed, the red ones among them, its wall clock, and a completion marker. THE REPORTS DIRECTORY is where the collector finds them, overridable for test as `VERIFY_CORPUS_BASELINE` and `VERIFY_CORPUS_ROOT` already are. Assignment is not execution: this story judges what came back, not what was handed out.

### AC1: the union is judged against the single baseline, and an equal-sized swap is not silent

- **Given** a fixture baseline whose `red-criteria` row records 6 identities, and 4 SHARD REPORTS whose unioned red identities are also 6 - one baseline identity repaired, one identity not in the baseline red, and one baseline identity whose record no longer exists in the fixture corpus
- **When** `verify-corpus.sh collect` runs over THE REPORTS DIRECTORY
- **Then** it exits non-zero and prints the serial lane's own wording - `NEW:` naming the unlisted identity, `went green:` naming the repaired one, and `VANISHED from the corpus (deleted or renumbered, NOT repaired):` naming the third - with the counts matching and the report saying so
- **Mutant:** sum the shards' red counts and compare the number alone, dropping the identity payload - the counts match, the lane exits 0, and the corpus that changed underneath it is the exact case the identities were added for
- **Verify:** pytest tools/tests/test_verify_corpus.py::ShardCollectorTests::test_an_equal_sized_swap_across_shards_is_not_silent

### AC2: the collector demands exactly N reports, with N from THE SHARD FILE

- **Given** THE SHARD FILE recording N as 8, and THE REPORTS DIRECTORY holding 7 SHARD REPORTS, shard 3 absent, the 7 present unioning to a red set that matches the baseline exactly
- **When** `verify-corpus.sh collect` runs
- **Then** it exits non-zero naming shard 3 of 8 and THE SHARD FILE as where the 8 came from, and prints no baseline comparison at all - no count, no `NEW:`, no `went green:`
- **Mutant:** take N from the number of reports found (`ls "$REPORTS"/shard-*.json | wc -l`) - seven eighths of the corpus is then judged as the whole of it and the lane goes green, which is the finding that a matrix with fewer entries than N drops a slice while every criterion is still assigned to exactly one shard
- **Verify:** pytest tools/tests/test_verify_corpus.py::ShardCollectorTests::test_a_short_matrix_refuses_and_judges_nothing

### AC3: the verdict does not depend on N

- **Given** one fixture corpus and one fixture baseline, collected twice: once from the reports of a 4-way partition and once from the reports of a 7-way partition of the same corpus
- **When** both collections run
- **Then** both exit with the same status and print the same red identity set and the same count, and the baseline file is byte-identical after both
- **Mutant:** key the baseline by shard - one `red-criteria.<i>` row per shard, each judged by its own shard - so a criterion that moves between shards when N changes reads as went-green in one row and NEW in another, and re-recording both is the documented remedy
- **Verify:** pytest tools/tests/test_verify_corpus.py::ShardCollectorTests::test_the_verdict_is_the_same_at_four_shards_and_at_seven

### AC4: the workflow matrix and THE SHARD FILE cannot drift apart unnoticed

- **Given** the committed `.github/workflows/lint.yml` and THE SHARD FILE
- **When** the shard matrix is read
- **Then** its entries are exactly the N indices THE SHARD FILE records, one live job per index, and a matrix whose length differs from that N fails at commit time rather than at the weekly run
- **Mutant:** hard-code the matrix as a literal list and leave N to move in THE SHARD FILE alone - the drift is then caught only by AC2's runtime refusal, on a scheduled lane, whose red is BG0653's three-weeks-unread shape
- **Verify:** pytest tools/tests/test_lint_workflow_coverage.py::ShardMatrixTests::test_the_matrix_lists_exactly_the_recorded_shards

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-24 | Claude Opus 5.5 | Backlog sweep D0265 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md): RETIRE - shard union collector with baseline judging |
