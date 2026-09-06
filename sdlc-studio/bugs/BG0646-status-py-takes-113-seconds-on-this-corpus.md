# BG0646: status.py takes 113 seconds on this corpus, so the command every session is ordered to run first times out under a two-minute tool default

> **Status:** Open
> **Verification depth:** functional [[derived: criteria 3; plan rows 5; EVIDENCE ABSENT - the mutation ledger holds no entry for this unit, which is not the same fact as nought killed; NOT RUN 5 (AC1 row 0, AC1 row 1, AC2 row 0, AC3 row 0, AC3 row 1); entry point 0 of 3 criteria through the shipped CLI, 0 in-process; 3 undetermined (the named node could not be isolated) | fp bdbacdf625f1 ]]
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/status.py, .claude/skills/sdlc-studio/scripts/tests/test_status.py, .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py
> **Created:** 2026-09-04
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

AGENTS.md orders every session to run status second, before acting. Measured on 2026-09-04 over 814 stories and 644 bugs: 113 s wall clock (rc 0), and an earlier invocation in the same session was killed by a 120 s tool timeout with the output lost. A read-only dashboard that costs two minutes is one an agent learns to skip, which is the failure mode AGENTS.md names for this repository. The cost is not stated by the command and nothing prints before the census completes.

## Steps to Reproduce

1. time python3 .claude/skills/sdlc-studio/scripts/status.py on this tree. 2. Observe about 113 s with no output until the end. 3. Run it under a 120 s tool timeout and observe the kill.

## Proposed Fix

Profile the census: the likely cost is per-artefact parsing repeated across the requirements, bugs, reviews and backlog passes plus the already-delivered advisory's pairwise title comparison over 256 open artefacts. Parse each artefact once and share the census across passes, cache the parse keyed on file mtime under sdlc-studio/.local, print the headline lines before the advisories, and record the measured duration in gate-timings so a regression is visible. Target: under 15 s on this corpus.

## Acceptance Criteria

- [ ] **AC1** Given this corpus at HEAD, when `python3 status.py` runs, then `gather` completes in under 15 s wall-clock on this machine and the headline lines (run of record, pipeline state, next step) print before any advisory - measured by the test through `time.monotonic()` around `gather(REPO_ROOT)`, with the 112 s figure of 2026-09-06 as the reproduction
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::GatherPerformanceTests::test_gather_over_this_corpus_completes_under_the_bound_with_the_headline_first
- [ ] **AC2** Given a fixture corpus of 300 artefacts, when `gather` runs, then every artefact file is read at most once per run - counted by a `read_text` spy on `sdlc_md` - and the census, the backlog and the review anchor all draw from that one pass
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::GatherPerformanceTests::test_every_artefact_is_read_at_most_once_per_gather
- [ ] **AC3** Given the same fixture, when `gather` runs twice in one process with no file changed, then the second call reads no artefact file at all and returns the same census - the cache is keyed on file mtime and size, and one changed file re-reads only itself
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::GatherPerformanceTests::test_a_second_gather_reads_nothing_and_a_changed_file_re_reads_only_itself

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `status.py`, keep the per-section walk that parses every artefact once per section - today's code | Given this corpus at HEAD, when `python3 status.py` runs, then `gather` completes in under 15 s wall-clock on this machine and the headline lines (run of record, pipeline state, next step) print before any advisory - measured by the test through `time.monotonic()` around `gather(REPO_ROOT)`, with the 112 s figure of 2026-09-06 as the reproduction |
| AC1 | in `status.py`, print the advisories before the headline | Given this corpus at HEAD, when `python3 status.py` runs, then `gather` completes in under 15 s wall-clock on this machine and the headline lines (run of record, pipeline state, next step) print before any advisory - measured by the test through `time.monotonic()` around `gather(REPO_ROOT)`, with the 112 s figure of 2026-09-06 as the reproduction |
| AC2 | in `status.py`, read each artefact twice, once for the census and once for the backlog, so the spy counts two per file | Given a fixture corpus of 300 artefacts, when `gather` runs, then every artefact file is read at most once per run - counted by a `read_text` spy on `sdlc_md` - and the census, the backlog and the review anchor all draw from that one pass |
| AC3 | in `status.py`, key the cache on the path alone so a changed file is served stale | Given the same fixture, when `gather` runs twice in one process with no file changed, then the second call reads no artefact file at all and returns the same census - the cache is keyed on file mtime and size, and one changed file re-reads only itself |
| AC3 | in `status.py`, drop the cache so the second gather re-reads every file | Given the same fixture, when `gather` runs twice in one process with no file changed, then the second call reads no artefact file at all and returns the same census - the cache is keyed on file mtime and size, and one changed file re-reads only itself |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-04 | sdlc-studio | Filed |
