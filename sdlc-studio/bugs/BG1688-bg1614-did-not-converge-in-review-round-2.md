# BG1688: BG1614 did not converge in review: round 2 REJECT findings

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py, changelog.d/BG1614.md, .claude/skills/sdlc-studio/scripts/tests/test_lane_accept_second_seat_brief.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/reference-sprint-toolchain.md
> **Created:** 2026-11-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-21T18:03:43Z

## Summary

BG1614 was rejected at round 2, the review cap, by Sam Eriksson (qa), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [regression] a saved QA brief with no `BRIEF:` line, as every landing before US1011's verdict files (2026-11-12) left one, now refuses every rejoinder or header-named verdict. `saved_stem` (lanes.py:999) is None, so no note sets `landed_at` (lanes.py:1012), and lanes.py:1036 refuses with "was issued by a rejoinder brief written before the landing that saved sdlc-studio/.local/briefs/US0101-qa.txt", though no landing came after that brief. The remedy it names, a fresh `--rejoinder` brief, meets the same refusal, as `saved_stem` stays None. Probed through `sprint.main` on the `test_lane_accept` fixture: round one REJECTed, round two landed, the saved brief's verdict-file section stripped with its fingerprint unchanged, then a headerless APPROVE at the issued path of a `critic.py brief --rejoinder` brief. Base 622cb415 records it, round 2, against the rejoinder brief. HEAD exits 2 with nothing recorded. The changelog's "or against a rejoinder brief when it is at the path that brief issued" is false for such a unit. In the real tree 60 of the 288 saved QA briefs have no `BRIEF:` line, all Done or Fixed today, so the live case is a unit still in review across an upgrade from a release before 6.4. No open bug covers it; BLOCKING: [new] the `landed_at is None` refusal at lanes.py:1036, which the repair makes live, is pinned by no test. Besides the case above, it fires when the landing's best-effort note (`note_brief`) is missing and a later qa re-brief noted the same fingerprint. An engineering verdict whose header names a brief issued after the landing is then refused as "written before the landing", which it was not (probe: HEAD exit 2). The mutant `if landed_at is not None and n < landed_at:` survived `test_lane_accept_second_seat_brief.py` and `test_lane_accept.py` (21 passed, 22 subtests), and in isolation it records that verdict (exit 0); RULINGS: Round-1 "a qa verdict that answers the brief `lane land` saved" is CLOSED. The round-1 scenario is a qa re-brief of the same scope after the landing, then the saved brief's verdict file with its UNIT and BRIEF header. It now records round 1 against the saved fingerprint at HEAD, as at base (exit 0, probed at both). A verdict naming the re-brief also records, and a round-one header after a repair landing is still refused (exit 2). My mutant `n <= landed_at` is killed by `test_a_re_brief_after_the_landing_reads_as_no_landing`, and the author's latest-plain-note mutant replays killed. The docstring, help/sprint.md and changelog wording the round-1 finding named now say "the landing that saved the QA brief" and are TRUE by those probes. Round-1 "the headerless rejoinder match that `_brief_of` keeps" is CLOSED: `test_a_headerless_verdict_at_a_rejoinder_s_issued_path_records_against_it` pins it, and the author's `elif False` mutant replays killed. AC1 is met: the Verify class passes 5 of 5 at HEAD. The brief's `verify_ac.py run --id BG1614 --dry-run` failed AC1 on its 120 s default timeout at load 10, as in round 1. `lane accept` passes its own longer bound, so this is noted, not a finding. The runbook row is TRUE.

## Steps to Reproduce

1. Read the round 2 REJECT of BG1614 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG1614 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [regression] a saved QA brief with no `BRIEF:` line, as every landing before US1011's verdict files (2026-11-12) left one, now refuses every rejoinder or header-named verdict. `saved_stem` (lanes.py:999) is None, so no note sets `landed_at` (lanes.py:1012), and lanes.py:1036 refuses with "was issued by a rejoinder brief written before the landing that saved sdlc-studio/.local/briefs/US0101-qa.txt", though no landing came after that brief. The remedy it names, a fresh `--rejoinder` brief, meets the same refusal, as `saved_stem` stays None. Probed through `sprint.main` on the `test_lane_accept` fixture: round one REJECTed, round two landed, the saved brief's verdict-file section stripped with its fingerprint unchanged, then a headerless APPROVE at the issued path of a `critic.py brief --rejoinder` brief. Base 622cb415 records it, round 2, against the rejoinder brief. HEAD exits 2 with nothing recorded. The changelog's "or against a rejoinder brief when it is at the path that brief issued" is false for such a unit. In the real tree 60 of the 288 saved QA briefs have no `BRIEF:` line, all Done or Fixed today, so the live case is a unit still in review across an upgrade from a release before 6.4. No open bug covers it
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** The round 2 REJECT finding no longer holds: BLOCKING: [new] the `landed_at is None` refusal at lanes.py:1036, which the repair makes live, is pinned by no test. Besides the case above, it fires when the landing's best-effort note (`note_brief`) is missing and a later qa re-brief noted the same fingerprint. An engineering verdict whose header names a brief issued after the landing is then refused as "written before the landing", which it was not (probe: HEAD exit 2). The mutant `if landed_at is not None and n < landed_at:` survived `test_lane_accept_second_seat_brief.py` and `test_lane_accept.py` (21 passed, 22 subtests), and in isolation it records that verdict (exit 0)
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC3** BG1614 AC1 still passes: Given a high-risk unit whose qa verdict is recorded and an engineering brief printed by `critic.py brief --unit <id> --seat engineering`, when `sprint.py lane accept --unit <id> --verdict <that brief's verdict file> --reviewer 'agent-x (engineering)'` runs, then the row is recorded against the brief the file's BRIEF header names, and a header naming no saved brief for the unit is refused. Fails on: the row is recorded against the saved qa brief's fingerprint, ignoring the BRIEF header.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_accept_second_seat_brief.py::LaneAcceptSecondSeatBriefTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-21 | sdlc-studio | Filed |
| 2026-11-21 | Claude Opus 5.5 (run twenty-one orchestrator) | Fixed: BG1614 was reviewed again in round three under D0573 and its qa seat (Sam Eriksson) approved, closing the round-two findings this bug carried; BG1614 is Fixed |
