# US0828: the red-criteria pass runs as N shards over a deterministic partition, every criterion in exactly one

> **Status:** Draft
> **Delivers:** CR0585
> **Created:** 2026-09-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .github/workflows/lint.yml, tools/verify-corpus.sh, tools/verify-corpus-shards.txt, tools/tests/test_verify_corpus.py
> **Epic:** EP0254
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** solo founder-engineer waiting on a corpus answer
**I want** the red-criteria pass split across N runners over a partition that provably covers every criterion exactly once
**So that** a mid-run question costs ten minutes rather than eighty-five, and the answer is the one the serial lane would have given

## Acceptance Criteria

The red pass is 84 of the job's 85.6 minutes and its criteria are independent of one another, so running them serially is a choice. The dead-stamps pass stays whole-corpus where it is at 73 s. THE SHARD FILE is `tools/verify-corpus-shards.txt`, one committed row `shards|N|why N|slowest-shard seconds|ci run id`, and it is the only place N is written. THE MANIFEST is what `verify-corpus.sh partition` writes: for each of the N shard indices, the `<record>::<AC>` identities assigned to it. THE FIXTURE CORPUS is a `VERIFY_CORPUS_ROOT` tree of stories at Done carrying executable criteria, with `VERIFY_CORPUS_BASELINE` pointed at a fixture baseline, driven exactly as `tools/tests/test_verify_corpus.py` already drives this lane - the whole point of those overrides is that the lane's logic can be exercised without paying the run it wraps.

### AC1: the union of the shards is the serial set, not merely a set every criterion appears in once

- **Given** THE FIXTURE CORPUS holding 23 stories, a count deliberately not divisible by N, and N read from THE SHARD FILE
- **When** `verify-corpus.sh partition` writes THE MANIFEST and the same corpus is walked serially
- **Then** the union of the N shards' identity lists equals the serial walk's identity set exactly, compared as sets and as counts, and no identity appears in two shards
- **Mutant:** slice each shard as `stories[i * (total / N) : (i + 1) * (total / N)]` with integer division and no remainder handling - the last `total mod N` stories land in no shard at all, and every criterion THE MANIFEST does name is still in exactly one of them
- **Verify:** pytest tools/tests/test_verify_corpus.py::ShardPartitionTests::test_the_union_of_the_shards_equals_the_serial_set

### AC2: the partition is a property of the corpus, not of the process that computed it

- **Given** THE FIXTURE CORPUS, partitioned once, then rewritten so the story files are created in reverse order with fresh mtimes and the same content
- **When** `verify-corpus.sh partition` runs a second time, in a fresh process, with `PYTHONHASHSEED` set to a different value from the first run's
- **Then** the second MANIFEST is byte-identical to the first
- **Mutant:** key the assignment on `hash(f"{record}::{ac}") % N` using CPython's built-in `hash`, which is salted per process - each shard job then computes a different assignment from the same corpus, so the union silently duplicates some criteria and drops others while every single shard looks internally consistent
- **Verify:** pytest tools/tests/test_verify_corpus.py::ShardPartitionTests::test_the_manifest_is_identical_across_processes_and_orderings

### AC3: a criterion that only passes in serial order is named as order-dependent, never banked

- **Given** THE FIXTURE CORPUS carrying a planted order dependence - one criterion whose `Verify` writes a file into the tree, and a later criterion whose `Verify` is `shell test -f` on that file, the two assigned to different shards by THE MANIFEST
- **When** `verify-corpus.sh equivalence` runs the serial pass and the sharded pass over that corpus, each shard from its own cold copy of the tree as a matrix checkout gives it
- **Then** it exits non-zero and names the dependent criterion's `<record>::<AC>` as red in the sharded pass and green in the serial one, with the remedy stated as fixing the criterion's own setup; the baseline is not read, not compared and not rewritten
- **Mutant:** run both passes in one working tree - the sharded pass inherits the file the serial pass left behind, the dependent criterion is green in both, and the check reports equal on exactly the corpus it exists to catch
- **Verify:** pytest tools/tests/test_verify_corpus.py::ShardEquivalenceTests::test_an_order_dependent_criterion_is_named_rather_than_banked

### AC4: the equivalence has been taken once on the real corpus, in CI, and the run is cited

- **Given** the committed `tools/verify-corpus-baseline.txt`
- **When** the baseline is read
- **Then** it carries a comment line recording the dual-run equivalence over this repository's own corpus at a named commit, citing the CI run id it was taken from in the shape the existing `# re-measured from CI run <digits>` line uses, and stating that the serial and sharded identity sets agreed
- **Mutant:** record the equivalence from a developer machine with no run id - BG0676 read 40 red against a baseline of 20 and every added id passed locally, so the difference between the two environments was the whole defect and a local reading is not admissible for this row
- **Verify:** pytest tools/tests/test_verify_corpus.py::ShardEquivalenceTests::test_the_baseline_cites_the_ci_run_that_proved_the_equivalence

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Created via `new` (deterministic) |
