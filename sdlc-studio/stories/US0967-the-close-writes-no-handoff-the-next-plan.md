# US0967: The close writes no handoff; the next plan reads the last signed report's carried work

> **Status:** In Progress
> **Delivers:** CR0590
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_report_replaces_handoff.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_close_housekeeping.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_rolling.py, changelog.d/US0967.md, .claude/skills/sdlc-studio/scripts/loop_guard.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_close.py, .claude/skills/sdlc-studio/scripts/tests/test_autosprint.py
> **Epic:** EP0268
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** a run to end with the signed report alone, and the next `sprint plan` to tell me what that report handed over
**So that** I read one page, not two that can disagree, and the close has one fewer artefact to write

## Summary

Groomed under D0291 (sdlc-studio/reviews/backlog-sweep-2026-10-01.md), 5 points, a deletion. The signed report already carries the remaining work: its "Known issues handed over" section lists every open finding raised in the run and every carried unit (`sprint_report._known_issues_section`), the same set the operator summary prints as `Carried, still open:` (sprint_report.py:2516). The handoff restates it and can disagree with it (premise below). So:

- the close stops calling `handoff.py generate` (`_close_handoff`), the close cascade and `sign` stop calling `handoff.refresh`, and the cycle-boundary stop writes no handoff; `_finalise_outcome`, which `_close_handoff` also runs, keeps a caller;
- `sprint plan`'s last-run notice (sprint.py:9719, `pending_handoff`/`handoff_line`) reads the last signed report's known-issues ids, and `--worklist` accepts that report's id (`--worklist RPT0013`) as a batch source;
- a run ended by `sprint.py stop --force` has no report, so the notice reads the waived units from run state's `unanswered` list instead (CR0581 AC1, merged here);
- retired: `gate.py --require-handoff` (reference-sprint.md:192), the handoff checklist step (`_ck_handoff`), `artifact.py new --type handoff` with its inline scaffold, and `handoff.py generate` with the retro link it writes. `handoff.py`'s remaining-count predicate stays, because `status.py` reads it.

Old HO files and the handoffs index stay on disk, readable and unrewritten; nothing new is added to them. No report section is added. CR0590's AC5 (BG0717, the retro-link blank line) is already Fixed; removing the link writer closes that path for good.

## Premise at HEAD

Executed at `85042135` in this repository, after RUN-01M3T8N1 closed with RPT0013:

```text
$ python3 .claude/skills/sdlc-studio/scripts/sprint.py plan --stories Ready 2>&1 | grep handoff
handoff: the last run (goal-reached) left HO-0093 with nothing carried over - its backlog is clear
$ grep -A6 '## Known issues handed over' sdlc-studio/reports/RPT0013-sprint-report-run-01m3t8n1.md
3 open finding(s) raised in the run, 0 close gap(s), 0 carried unit(s)
| BG0863 | Medium | An unreadable verdict ledger drops unreviewed units ...
| BG0864 | Medium | transition to Fixed admits a bug whose Verify lines have never been run ...
| BG0865 | Medium | The signed page names a known issue's retro ruling only when it is STOP-SHIP ...
```

The handoff the plan reads says nothing is carried; the signed report hands over three findings.

## Acceptance Criteria

- [ ] **AC1** Given a fixture run with one carried unit and one open finding raised inside it, when `sprint.py close` and then `sprint.py sign` run, then nothing is written under `sdlc-studio/handoffs/`, no `.local/handoff-worklist.txt` exists, run state's `handoff` stays null, and `sprint_report.py checklist` lists no handoff step. Fails on: HEAD's close step `_close_handoff` runs `handoff.py generate`, which minted HO-0093 at RUN-01M3T8N1's close
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report_replaces_handoff.py::ReportReplacesHandoffTests::test_the_close_and_sign_write_no_handoff
- [ ] **AC2** Given a fixture whose last signed report RPT0001 hands over BG0002 (an open finding) and US0003 (a carried unit), when `sprint.py plan --stories Ready` runs, then its last-run notice names RPT0001, BG0002 and US0003; and `sprint.py plan --worklist RPT0001` plans BG0002 and US0003. Fails on: HEAD reads the notice from `state["handoff"]` only, so in this repository it says `nothing carried over` while RPT0013 hands over three findings
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report_replaces_handoff.py::ReportReplacesHandoffTests::test_the_plan_reads_the_signed_reports_handed_over_ids
- [ ] **AC3** Given a fixture run ended by `sprint.py stop --force --reason x` over an unanswered unit US0004, when the next `sprint.py plan --stories Ready` runs, then its notice names US0004 as waived by the forced stop. Fails on: HEAD's `pending_handoff` returns None when run state has no `handoff`, and `stop` writes none, so the plan names nothing
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report_replaces_handoff.py::ReportReplacesHandoffTests::test_a_forced_stops_waived_units_reach_the_next_plan

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-01 | engineering seat (groomer) | Groomed under D0291 (backlog sweep 2026-10-01): criteria authored, premise executed at HEAD 85042135, Points and Affects set |
| 2026-10-01 | sprint planning | Goal review round 1 (engineering seat): Affects completed, points 5 to 8. |
| 2026-10-01 | sprint planning | Split at the 8-point ceiling (backlog triage 'oversized'): AC4 and AC5, the retirement of the handoff writers and the require-handoff gate, moved to US0978; points 8 to 5. |
