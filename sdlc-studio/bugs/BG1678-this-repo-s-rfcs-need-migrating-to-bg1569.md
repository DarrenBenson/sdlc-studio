# BG1678: This repo's RFCs need migrating to BG1569's Delivered status, and the 20 with no change requests need a status ruling

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** sdlc-studio/rfcs/, changelog.d/BG1678.md, .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py
> **Evidence:** Run twenty-one lane T builder (BG1569), reconcile on the work-in-progress patch at 611367cf; split from BG1569 when 8 points tripped the oversized ceiling (US0854 AC1) at the push gate.
> **Created:** 2026-11-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-21T12:21:40Z

## Summary

BG1569 builds D0513's Delivered status. With it in, reconcile reports 56 drift items on this repository's own RFCs: 36 Accepted RFCs whose change requests have finished now derive Delivered (request-derivable), and 20 Accepted RFCs with no change request read as undecomposed. Half of the fix BG1569 starts: the corpus has to move in the same commit, or the gate's reconcile lane is red.

## Steps to Reproduce

Apply BG1569's work-in-progress patch (sdlc-studio/.local/lane/landed/agent-ad1bb647a0067e108/BG1569-wip.patch) and run reconcile.py detect: it reports 56 drift items across sdlc-studio/rfcs/.

## Proposed Fix

Record a ruling (a decisions row) on what an Accepted RFC with no change request is under D0513, then migrate the corpus with reconcile.py apply for the 36 derivable ones and the ruling for the 20. Land it in one lane commit with BG1569, pinned by reconcile detect reading 0 drift on the migrated corpus.

## Acceptance Criteria

- [ ] **AC1** Given BG1569's Delivered status is in, when reconcile.py detect runs on this repository, then it reports 0 drift items across sdlc-studio/rfcs/. Fails on: the 56 request-derivable and undecomposed items lane T measured.
  - **Verify:** shell python3 .claude/skills/sdlc-studio/scripts/reconcile.py detect | grep -q 'drift_items=0'
- [ ] **AC2** Given an Accepted RFC with no change request, when the ruling is read in sdlc-studio/decisions.md, then it names that RFC state and what reconcile reports for it. Fails on: no ruling recorded, so 20 RFCs read as undecomposed with no decision behind them.
  - **Verify:** shell grep -E '^[|] D[0-9]{4} [|].*BG1678' sdlc-studio/decisions.md | grep -i 'accepted' | grep -qi 'reconcile'

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-21 | sdlc-studio | Filed |
| 2026-11-23 | Claude Opus 5.5 (run twenty-four orchestrator) | Run twenty-four goal review: AC2's grep passed on any mention of the id. It now needs a decisions row naming BG1678 that states the Accepted RFC state and what reconcile reports. AC1 passes at HEAD until BG1569's status lands, so the two land in one commit |
| 2026-11-23 | Claude Opus 5.5 (run twenty-four orchestrator) | D0611 records the ruling AC2 asks for (an Accepted RFC with no request or epic is decision-only, stays Accepted with 'none - <reason>', and never derives Delivered); decisions.md leaves Affects, since the row is on main |
| 2026-11-23 | Claude Opus 5.5 (run twenty-four orchestrator) | Affects widened: D0611's decision-only rule needs one guard in reconcile.py's undecomposed check (a predicate in sdlc_md.py) with its test, since the check never read Decomposed-into |
