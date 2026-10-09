# US1009: A sprint-checklist waiver can carry an expiry date, after which its row is enforced again

> **Status:** Draft
> **Delivers:** CR0614
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/decisions.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/help/decisions.md, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/reference-scripts-create.md, .claude/skills/sdlc-studio/scripts/tests/test_waiver_until.py, changelog.d/US1009.md
> **Epic:** EP0279
> **Points:** 5
> **Depends on:** US1007, BG1012
> **Persona:** Maya Okafor

## User Story

**As** a founder-engineer setting a checklist row aside until a filed fix lands
**I want** to record the date the waiver stops covering the row, and to renew it if the fix slips
**So that** the row comes back on its own instead of relying on somebody remembering to retract the waiver

## Acceptance Criteria

- **AC1:** Given a checklist waiver recorded at +01:00 with `[until: 2026-11-01]` and a run whose record says it closed at 2026-11-01T22:30:00Z, which is 23:30 on the named day in the waiver's own offset, when `sprint_report.py checklist --format json` runs, then the row reads waived.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_waiver_until.py::WaiverExpiryTests::test_a_close_on_the_expiry_day_is_covered
- **AC2:** Given the same waiver and a run that closed at 2026-11-01T23:30:00Z, which is 00:30 on 2 November in the waiver's offset, when the checklist runs, then the row is outstanding and its detail names the waiver and the date it lapsed.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_waiver_until.py::WaiverExpiryTests::test_a_close_after_the_expiry_day_in_the_waivers_offset_is_not_covered
- **AC3:** Given a clone holding only the tracked record of a run that closed before an expiry now past on today's clock, when the checklist is read today, then the row still reads waived.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_waiver_until.py::WaiverExpiryTests::test_expiry_is_judged_at_the_runs_close_from_the_tracked_record
- **AC4:** Given a lapsed checklist waiver and a later waiver of the same subject, recorded with `--until` and `--authorised-by` and covering the close, when the checklist and `decisions.waiver_authoriser` read them, then the row reads waived by the later id and the later row's authoriser is returned.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_waiver_until.py::WaiverExpiryTests::test_a_renewed_waiver_is_read_in_place_of_the_lapsed_one
- **AC5:** Given `--until 2026-11-01` on `leg:tsd`, `rule:engagement-floor` and `rule:conformance:verified` in turn, when `decisions.py waive` runs on each, then each exits 2 naming rule:sprint-checklist as the family that reads an expiry, and writes nothing.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_waiver_until.py::WaiverExpiryTests::test_an_expiry_is_refused_where_no_checker_reads_one

## Notes

- Release: 6.2 (D0355 breakdown G5, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the expiry is compared with `<` in place of `<=`, so a run closed on the named day falls outside it.
- AC2 must fail on: the expiry is written and never read; or it is compared with the close's UTC date, which still reads 1 November.
- AC3 must fail on: outside a close the expiry is compared with today, or with nothing because the live record is gone, so a filed run's checklist changes after the fact.
- AC4 must fail on: the checklist keeps `waiver_for`'s first accepted row (decisions.py:426 returns the oldest), so a renewed waiver is never read; or the `[until: ...]` marker is written after `[authorised by: ...]`, whose reader is anchored to the end of the cell.
- AC5 must fail on: `--until` is accepted on every family, so an expiry nothing reads is recorded and the waiver never lapses.
- Flag: `--until YYYY-MM-DD`, written as an in-cell `[until: YYYY-MM-DD]` marker before the authoriser marker, like `[kind: ...]`. The waiver is inclusive to the end of the named day in the offset its own Date cell records, because `record_waiver` stamps the moment with its offset. A close is read from the run record's `ended_at`, which is UTC. AC1 and AC2 pin both the inclusive boundary and the time zone.
- It is reported as `lapsed`, never `expired`: `expired` is already a waiver kind (WAIVER_KINDS) and a checklist state (EXPIRED).
- The close instant is the resolved run record's `ended_at`, live, tracked or archived through BG1012's lookup. Inside a close (`live_gate=True`) it is now. Outside a close, a run with no readable `ended_at` gives a dated waiver nothing to judge against, so it covers nothing and the row stays outstanding.
- Every accepted waiver for a subject is read, not the first: a waiver answers when it has not lapsed at the close, and the newest such row wins. `waiver_kind` and `waiver_authoriser` read that same row.
- Refused at record time: a malformed date, or one before the moment of recording, since a waiver lapsed on arrival covers nothing. The AC fixtures write their rows through `decisions.record_waiver(today=...)`, so a past expiry can be set up without that refusal; the reader under test is the CLI.
- Which families read an expiry is published by each checker (a declared constant found by the discovery `waivable_subjects` already runs at record time), not listed in decisions.py.
- The comment at sprint.py:5616 is reworded: the unanswered-unit hold is unchanged (D0196), but its stated reason, 'a waiver never expires', no longer holds.
- Panel: the first story to cut if 6.2 is tight.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G5 after the refine panel's review |
