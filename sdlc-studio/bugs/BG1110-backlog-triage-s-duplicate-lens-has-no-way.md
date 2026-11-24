# BG1110: backlog_triage's duplicate lens has no way to record a pair confirmed distinct, so a triaged pair is re-reported on every run

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/backlog_triage.py, .claude/skills/sdlc-studio/scripts/tests/test_backlog_triage.py, .claude/skills/sdlc-studio/scripts/tests/test_triage_distinct_pairs.py, changelog.d/BG1110.md
> **Evidence:** Backlog triage, 2026-10-21 (D0387): stories slices 2 and 3 each judged both pairs distinct, with evidence (out-stories-2, out-stories-3). The post-triage `backlog_triage.py check` still lists both.
> **Created:** 2026-10-21
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-21T11:53:17Z

## Summary

`backlog_triage.py check` reports a pair as a likely duplicate when their Affects overlap and their wording is at least 50% similar, and says 'merge or supersede one, or confirm they are distinct'. Nothing records that confirmation. US1036/US1037 and US1069/US1070 were each judged distinct by two independent triage passes on 2026-10-21, and the lens still flags both. A note that can never be answered teaches its reader to skip it, which is how a real duplicate gets missed.

## Steps to Reproduce

Run `python3 .claude/skills/sdlc-studio/scripts/backlog_triage.py check`: the duplicate notes for US1036/US1037 and US1069/US1070 appear, and no field, waiver or command can answer them.

## Proposed Fix

Let a unit declare the distinct pair, for example a `Distinct from: US1037` field, which the lens reads and honours for that exact pair while the overlap it measured is unchanged. Re-report it if either side's Affects grows into new shared files.

## Acceptance Criteria

- [ ] **AC1** A pair one unit declares distinct is not re-reported while their shared files are unchanged, and is reported again once they gain a new shared file
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_triage_distinct_pairs.py::DistinctPairsTests::test_a_declared_distinct_pair_is_quiet_until_its_overlap_grows

## Impact

Every triage pays to re-judge the same pairs, and the lens's real findings are diluted by notes nobody can clear.

## Resolution

Won't Fix under D0613: the operator approved the product seat's second proposal (D0562) because a user can meet it, but it is rare and harmless and has a workaround, so fixing it costs more than it returns. A triaged distinct pair is re-reported; workaround is to ignore the repeat line.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-21 | Claude Opus 5.5 | Filed |
| 2026-11-24 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0613: the operator approved the product seat's second list (D0562); reason in Resolution |
