# BG1109: The artefact gate's conformance and engagement-floor lanes re-read the verdict ledger, the decisions log and each verifier's collection once per unit

> **Status:** Open
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/decisions.py, .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/engagement_floor.py, .claude/skills/sdlc-studio/scripts/tests/test_gate_reads_once.py, changelog.d/BG1109.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_decisions.py, .claude/skills/sdlc-studio/scripts/tests/test_conformance.py, .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py
> **Evidence:** BG1065's Further evidence (2026-10-20 profile at fd16f28a); split out of BG1065 by the operator's ruling D0388, which keeps BG1065 to re-deriving the budget.
> **Created:** 2026-10-21
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-21T11:43:47Z

## Summary

A profile of `gate.py --root .` on a clean tree (BG1065's further evidence, 2026-10-20) puts 283 of its 330 seconds in three per-unit re-reads. `critic.read_verdicts` is called once per unit, 812 times, and re-parses the whole verdict ledger each time: 125 s, 51 s of it in `sdlc_md.table_cells`. `verify_ac._collect_nodes` starts 257 collection subprocesses: 130 s. `decisions.list_decisions` is called 2229 times through `waiver_for`: 27.6 s. Each reader returns the same answer for every unit of one gate run.

## Steps to Reproduce

Run `python3 -m cProfile -s cumulative .claude/skills/sdlc-studio/scripts/gate.py --root .` on a clean tree and read the cumulative column: `read_verdicts`, `_collect_nodes` and `list_decisions` dominate.

## Proposed Fix

Read each ledger once per gate run and pass it to the per-unit readers, or memoise it on the file's identity (path, mtime, size). Collect each verifier module once per run, not once per criterion. Keep every lane's verdict identical, which a test can check by comparing the lane output with and without the cache.

## Acceptance Criteria

- [ ] **AC1** One gate run reads the verdict ledger and the decisions log once each, and each lane's output is the same as with the per-unit re-reads
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate_reads_once.py::GateReadsOnceTests::test_each_ledger_is_read_once_and_the_lanes_agree

## Impact

The gate costs 330 s on a whole-workspace run, against a 45 s budget, and that cost runs on every clean-tree gate and every message-only amend (BG1104). It is most of why BG1065's budget line carries no signal.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-21 | Claude Opus 5.5 | Filed |
