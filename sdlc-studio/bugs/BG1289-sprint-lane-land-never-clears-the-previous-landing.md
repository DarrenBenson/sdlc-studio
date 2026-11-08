# BG1289: `sprint lane land` never clears the previous landing's hand-in, so a repair round that hands in no self-check files records round one's as its own and the `author_self_check: block` gate passes an unchecked diff

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py, changelog.d/BG1289.md
> **Evidence:** the between-releases review before v6.3.0 (D0427, LL0005), code leg B; repro under scratchpad rel63/legs/scratch-b/
> **Created:** 2026-11-08
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-08T13:08:50Z

## Summary

`lane land` copies the worktree's hand-in into `sdlc-studio/.local/lane/landed/<worktree name>/` and never clears that directory first. `_record_and_brief` then reads `<unit>-claims.json` and `<unit>-mutants.json` from it. `lane run` always names a unit's worktree `lane-<unit>`, so a repair round lands into the same directory as the first round. When the repair builder hands in no claims or mutants files, the first round's files are still there. They get recorded with `critic.py self-check record`, which binds them to the repair's current Affects digest (`critic.record_self_check).` The expected refusal is 'self-check NOT RECORDED - the hand-in carries no ...'. Under `review.author_self_check: block`, the `critic.py brief` gate then passes a diff its author never self-checked.

## Steps to Reproduce

bash rel63/legs/scratch-b/`land_stale.sh` <scratch-b> (temp HOME; `_critic` stubbed to print the claims file it is handed). Round 1 hands in claims and mutants. Round 2, the repair, hands in only commit-msg.txt. Observed for round 2: 'critic self-check record --claims .../landed/lane-us0001/US0001-claims.json -> content: [{"claim": "ROUND ONE claims"}]', then 'US0001: self-check recorded; QA brief sdlc-studio/.local/briefs/US0001-qa.txt ...', exit 0.

## Proposed Fix

In `_land`, before copying, remove `keep` (or the `<unit>-claims.json`, `<unit>-mutants.json`, commit-msg.txt and HANDOFF.md under it), or write each landing to its own directory, such as `<worktree>-<landed sha>`. Have `_record_and_brief` check the worktree's `hand_in` for the two files, not `keep`. Pin both with a two-round landing test.

## Acceptance Criteria

- **AC1:** Given a unit landed once from worktree `lane-<unit>` with claims and mutants handed in, and a repair round landed from the same worktree name that hands in only `commit-msg.txt`, when the repair lands, then no self-check is recorded for it and the landing says the hand-in carries no claims or mutants file. Fails on: round one's `<unit>-claims.json` read from `landed/<worktree>/` (the observed 'ROUND ONE claims').
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_a_repair_round_without_a_hand_in_records_no_stale_self_check
  - **Verified:** yes (2026-11-08)
- **AC2:** Given any landing, then the files it records come from that landing's own hand-in: nothing under `landed/<worktree>/` survives from an earlier landing. Fails on: `_land` copying into `keep` without clearing it first.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_each_landing_starts_from_its_own_hand_in
  - **Verified:** yes (2026-11-08)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-08 | Claude Opus 5.5 | Filed |
| 2026-11-08 | Claude Opus 5.5 (grooming) | Criteria with Verify lines for the 6.3.0 cut (D0428); the changelog fragment joins Affects |
