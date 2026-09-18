# BG0701: Run-ending routes still read different sets: stop records from the parked derivation, the boundary stop ignores --retro, and stop cannot see the retro the close names

> **Status:** Open
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/handoff.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_handoff.py
> **Evidence:** Independent delivery review, RUN-01M2JA6J 2026-09-15: verdicts/US0626-delivery-engineering.txt (engineering seat); verdicts/US0626-delivery-qa.txt (qa seat); verdicts/US0626-delivery-engineering-r2.txt (engineering seat, round two); verdicts/US0626-delivery-qa-r2.txt (qa seat, round two); verdicts/US0823-delivery-engineering.txt (engineering seat); verdicts/US0823-delivery-qa.txt (qa seat); verdict rows in sdlc-studio/reviews/critic-verdicts.md.
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`cmd_stop` reads two derivations. It refuses on `unanswered_units` but writes the record and the cost line from `blocked_by_pending`, so an unforced stop over a ruled In Progress unit or a design-rung Ready unit exits 0 and records cause pending-decision, pending 0 and `could_have_proceeded` [US0101], and prints 'being parked with it' (sprint.py:10693-10697, 10608-10611); 3f73ab64 refuses the same state with rc 1. Raised in round one and not repaired; the later relabel covered only the forced path. The boundary stop calls the predicate with no retro (sprint.py:10174) and its handoff generate passes none: with a newer RETRO0002 that rules nothing, boundary --retro RETRO0001 records US0105 as held, read from RETRO0002, while close --file-and-close --retro RETRO0001 on the same tree does not hold it. stop reads the latest retro carrying the run id (AC8), so on a state whose named retro carries no run id and rules US0101 deferred, the close checklist passes and stop refuses; that errs in the safe direction and is to spec, but the docstring at sprint.py:5813-5815 and the `cmd_stop` comment at 10664-10665 ('can never name different sets') over-claim. AC8's premise that run state records no retro id is false: a bare close records `scaffolded_retro` (sprint.py:6262), which `_apply_signoff` already reads. stop --force refuses with exit 2 when the predicate raises (sprint.py:10670), so the override cannot end a run whose set cannot be computed. help/sprint.md:93 still says an apply-signoff re-run resumes, but after a stop between sign-off and Done the re-run now refuses at the checklist (AC10's accepted consequence), so `_apply_signoff`'s signed-but-not-Done resume branch (sprint.py:6573) can no longer be reached through close.

## Steps to Reproduce

1. Open a run whose batch holds US0101 at In Progress, ruled deferred in the run's retro. python3 .claude/skills/sdlc-studio/scripts/sprint.py stop - exit 0; the archived record holds cause pending-decision, pending 0 and `could_have_proceeded` [US0101]. The same state at 3f73ab64 exits 1. 2. With RETRO0001 ruling US0105 and a newer RETRO0002 ruling nothing, sprint.py boundary --retro RETRO0001 records US0105 as held; sprint.py close --file-and-close --retro RETRO0001 on the same tree does not hold it. 3. Make the predicate raise (an unreadable carried table) and run sprint.py stop --force - exit 2.

## Proposed Fix

Write stop's record and cost line from the set it refused on, and label parked work separately. Thread --retro through `_boundary_stop` and its handoff generate. Have stop and the boundary read the named retro, else run state's `scaffolded_retro`, else the latest retro carrying the run id, and correct the docstring and AC8's premise. Let stop --force end the run with the set recorded as not computable. Correct help/sprint.md:93 and remove or re-route the unreachable resume branch.

## Acceptance Criteria

Four routes end a run - `stop`, `stop --force`, the boundary stop and the close - and each one
reads the predicate for itself. The criteria are written against the four reads, not against the
one predicate, because every defect here is a caller's, and a test that drives the predicate
directly passes on all four today.

### AC1: an unforced stop records the cause it stopped on, and does not price a ruled unit as work thrown away

- **Given** an open run whose batch holds US0101 at In Progress, ruled `deferred` in the retro
  carrying the run id, with no decision deferred, so `blocked_by_pending` returns `pending` empty
  and `unblocked` `["US0101"]` while `unanswered_units` returns an empty held set
- **When** `python3 .claude/skills/sdlc-studio/scripts/sprint.py stop --reason '<why>'` runs and
  exits 0, the predicate having answered US0101
- **Then** the archived record's `stop.cause` is `operator` beside `stop.pending` 0, and US0101 is
  absent from `stop.could_have_proceeded` - a unit the run's own retro ruled is neither a pending
  question nor work the stop threw away. Both arms are asserted on one fixture pair: the same tree
  with a decision deferred over US0101 still records `pending-decision`, so the repair cannot be a
  blanket relabel
- **Mutant:** two edits, each killed on its own subTest - keep
  `cause = STOP_OPERATOR if forced else STOP_PENDING_DECISION` (sprint.py:10736), which records
  `pending-decision` over zero pending questions, the state RUN-01M2JA6J reached; and keep
  `"could_have_proceeded": out["unblocked"]` (sprint.py:10738), which prices a ruled unit as lost
  work and pushes the operator towards `--force`
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::StopRecordTests::test_an_unforced_stop_records_the_cause_it_stopped_on

### AC2: every run-ending route resolves the carried table by one order, and `--retro` reaches the boundary's stop and the handoff it writes

- **Given** a tree carrying RETRO0001, which rules US0105 `not-stop-ship`, and a newer RETRO0002
  which carries the run id and rules nothing; and a second tree whose run state records
  `scaffolded_retro: RETRO0003` while no retro's text carries the run id
- **When** `sprint.py boundary --retro RETRO0001`, `sprint.py close --file-and-close --retro
  RETRO0001` and `sprint.py stop` each run over those trees
- **Then** all three resolve the table by one order - the named retro, else the run's
  `scaffolded_retro`, else the latest retro carrying the run id - so the boundary reads RETRO0001
  rather than RETRO0002 and holds US0105 exactly where the close does, the handoff `_boundary_stop`
  generates is given the same `--retro` and renders the same set, `stop` on the second tree reads
  RETRO0003, and each route records `unanswered_rulings_from` as the retro it read. The docstring at
  sprint.py:5813 and the `cmd_stop` comment at 10707 state that order instead of claiming the
  routes can never name different sets
- **Mutant:** thread `--retro` into `_boundary_stop`'s `unanswered_units` call (sprint.py:10217)
  while leaving the `handoff.generate` argument list at 10206 unchanged - the stop record then holds
  RETRO0001's set beside a handoff document rendering RETRO0002's, two accounts of one run; and
  separately, order the fallback the other way, scanning for a retro carrying the run id before
  reading `scaffolded_retro`, so a stale retro beats the one this close scaffolded
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::EveryRunEndReadsThePredicateTests::test_every_route_resolves_the_carried_table_by_one_order

### AC3: `stop --force` ends a run whose unanswered set cannot be computed, recording it as not computable

- **Given** an open run whose carried table cannot be read, so `unanswered_units` raises
- **When** `sprint.py stop --force --reason '<why>'` runs
- **Then** it exits 0, the run is closed as stopped, and the archived record carries `unanswered`
  null with `unanswered_error` naming the exception type and message - never `[]`, which would read
  as a run that ended over nothing. The paired control, `stop` with no `--force` on that same tree,
  still exits 2 and refuses
- **Mutant:** keep the `return 2` at sprint.py:10715 on the forced path, so the operator's override
  cannot end a run whose set cannot be read and the run stays open with no route out
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::EveryRunEndReadsThePredicateTests::test_a_forced_stop_ends_a_run_whose_set_cannot_be_computed

### AC4: the documented apply-signoff resume is the one the close can reach

- **Given** a batch unit at Review carrying an independent sign-off and its adversarial evidence
  but not yet Done - the state a stop taken between sign-off and Done leaves
- **When** `sprint.py close --file-and-close --apply-signoff --principal '<operator>'` is re-run on
  that tree
- **Then** it exits non-zero at the checklist step, naming the unit as `remaining work at Review`,
  and no sign-off row is written - the ledger is byte-identical before and after; and
  `help/sprint.md` names the transition that answers it (`transition.py set <id> Done`) rather than
  a re-run that resumes, so its line 93 and the fan loop agree. The signed-but-not-Done branch at
  sprint.py:6644 is either removed with its comment or driven by a route the test exercises
- **Mutant:** correct help/sprint.md alone and leave sprint.py:6644's branch and its comment in
  place, documenting a resume no route reaches; or delete the branch and leave line 93 as it stands,
  which sends the operator to a re-run that refuses
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::EveryRunEndReadsThePredicateTests::test_the_documented_resume_is_the_one_the_close_reaches

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Filed |
| 2026-09-17 | sdlc-studio | Groomed for `sprint plan`: the derived criterion is replaced by four authored ones, one per defect the summary names - the stop's record and cost line, one carried-table resolution order across the four run-ending routes (with `--retro` threaded through the boundary's stop and its handoff), a forced stop over an uncomputable set, and the documented apply-signoff resume. Each names the edit it must fail on. |
