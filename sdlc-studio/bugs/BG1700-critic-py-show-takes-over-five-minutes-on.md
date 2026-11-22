# BG1700: critic.py show takes over five minutes on a repository with a long verdict ledger, so test_cli_grammar's real-tree control times out at 120 seconds under load

> **Status:** Open
> **Severity:** Low
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_show_scales.py, changelog.d/BG1700.md
> **Evidence:** Run twenty-two, 2026-11-22: lane R's builder timed critic.py show over the real tree at more than 5 minutes; lanes V, D and R each reported test_cli_grammar.py::RealTreeMarkerTests::test_the_control_holds_with_no_fragment_directory failing with 'critic.py --root ... show timed out after 120 seconds' on devserver1
> **Created:** 2026-11-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-22T09:52:29Z

## Summary

critic.py show over this repository's real tree took more than five minutes on the workstation (critic.py `cmd_show).` A person running it waits that long for a read-only summary, and `test_cli_grammar`'s RealTreeMarkerTests, which runs critic.py show against the real tree with a 120-second subprocess limit, timed out in three of run twenty-two's full-suite runs on the gate host while other lanes were running.

## Steps to Reproduce

1. In this repository, run: time python3 .claude/skills/sdlc-studio/scripts/critic.py --root . show. 2. It runs for minutes before printing. 3. Run tools/run-suite.sh all while other work loads the host: RealTreeMarkerTests::`test_the_control_holds_with_no_fragment_directory` fails with subprocess.TimeoutExpired after 120 seconds in critic.py show.

## Proposed Fix

The cost is the unit's display id, not the ledger read. `verdict_source` calls `sdlc_md.display_id(root, unit)` for every row bound to an issued file, and `display_id` reaches `find_by_id`, which walks the whole artefact tree (`artifact_files` for every type) on each call. `cmd_show` calls `verdict_source` twice per row (once for the label, once inside `verdict_file_state`), so this repository's 2,171-row ledger walks the tree about 4,300 times. A sampled stack of `critic.py --root . show` sat in `find_by_id` / `iter_artifact_files` under `verdict_source` in every sample. `find_by_id` already builds its by-id index once inside `sdlc_md.corpus_cache()`, and `critic.brief` runs inside it (BG1114), but `cmd_show` does not. Run the show listing inside `sdlc_md.corpus_cache()` so the tree is walked once per invocation.

## Acceptance Criteria

- [ ] **AC1** Given a ledger of many rows bound to issued files across a few units, when `critic.py show` runs, then the artefact tree is walked a fixed number of times, not once or twice per row: a ledger ten times longer walks it no more often. Fails on: `find_by_id` walking the tree for every row's display id.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_show_scales.py::CriticShowScalesTests
- [ ] **AC2** Given the same ledger, when `critic.py show` runs in text and in JSON, then each row's unit, label, verdict file and file state read exactly as they do before the change. Fails on: a cached display id naming another unit's file, or a state computed from a stale path.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_show_scales.py::CriticShowOutputUnchangedTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-22 | sdlc-studio | Filed |
| 2026-11-22 | Claude Opus 5.5 (run twenty-two orchestrator) | Cause found by sampling the stack of `critic.py show` (per-row `display_id` tree walks, since US1012); Proposed Fix, criteria and Affects authored for building in run twenty-two |
