# US0823: every other route that ends a run reads the same unanswered-unit predicate as the close, and stop --force records what it waived

> **Status:** Ready
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/handoff.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0206
> **Points:** 5
> **Depends on:** US0626
> **Persona:** Maya Okafor

## User Story

**As a** reviewer of record reading how a run ended
**I want** every route that can end a run to judge unfinished units the way the close does
**So that** a run cannot be ended around the stop-ship question through a side door

## Acceptance Criteria

Every route reads US0626's `sprint.unanswered_units(root, state, retro_id=None)` and nothing else. THE RUN is US0626 AC5's fixture run (done rung, RETRO0001 carrying its `run_id` and ruling US0105 and US0112 `not-stop-ship`, the standing known-issues waiver, the nineteen-unit planned batch, US0106 and US0117 dropped by `batch drop --reason`), whose predicate set is the literal {US0101, US0103, US0109, US0110, US0111, US0112, US0115, US0117, BG0101}; a unit id is counted only when the fixture names it as a unit, so BG0903, US0110's filed finding, never is. That set differs from `_remaining_units` (live batch, non-terminal: it drops BG0101 Fixed, US0111 Done and the dropped US0117, and keeps US0102, US0104, US0105, US0107, US0108 and US0116), from `blocked_by_pending`'s `unblocked` (the same walk less parked units, their dependants and every Review unit `_awaits_signoff` accepts) and from handoff's `_classify` remaining list, so only a route that calls the predicate names it. THE ANSWERED RUN is a separate tree built by the same fixture builder, done rung, RETRO0001 carrying its `run_id` and ruling US0105 `not-stop-ship`, whose planned batch holds only US0626 AC5's answered shapes, each answered by the predicate's own text: US0102 (Review, a `critic.evidence_for` row, no verdict - awaiting sign-off with its pass recorded); US0104 (Review, an evidence row, REJECT completely repaired - `critic.coverage_state` reads `repaired`, so the REJECT does not hold it); US0105 (In Progress, no verdict, ruled); US0106 (In Progress, no verdict, dropped by `batch drop --reason` - walked through `batch_changes`, answered by the drop because it carries no REJECT); US0107 (Ready, no verdict, parked by `sprint decision defer`); US0108 (Ready, no verdict, `Depends on: US0107`); BG0102 Won't Fix, US0113 Superseded and US0114 Won't Implement, each with an unrepaired REJECT (abandoned, where the REJECT rule does not reach); and US0116 (Review, no verdict, covered by a sprint-level APPROVE from a reviewer distinct from its author). None of THE RUN's nine is planned, dropped or otherwise present in its batch or `batch_changes`, so the predicate never walks them and returns an empty `unanswered`. Both trees also carry FileAndCloseTests._fixture's empty change-request index and review anchor. THE RECORD is the archived run record, `run_state.read_archived(root, run_id)` (`sdlc-studio/.local/run-archive/<run_id>.json`), whose new `unanswered` field holds the predicate's `unanswered` list as returned; it is written by every route below - `handoff.generate` on its `--outcome` path only, and `_boundary_stop` itself, since it generates its handoff without `--outcome` - empty (`[]`) when nothing is unanswered, and separate from `could_have_proceeded` and `handoff_remaining`. THE SECTION is a `## Unanswered stop-ship questions` section that `handoff.render_body` writes in every handoff document, listing the predicate's unit ids - its own section, because Delivered lists US0111 and BG0101 and Remaining lists US0102. Wherever a route below is patched, `close_preflight` returns one deferrable blocker alone, the `goal-verdict` row "the Sprint Goal is unjudged" (FileAndCloseTests.ADMIN's shape): no hard blocker refuses first, and `--file-and-close` has something to file, since with nothing outstanding it refuses a correct build (`sprint.py` "nothing outstanding", rc 2).

### AC1: --file-and-close refuses THE RUN, naming exactly the predicate's set, before it files anything

- **Given** THE RUN, open, with `close_preflight` patched to the single `goal-verdict` blocker
- **When** `sprint.py close --retro RETRO0001 --file-and-close` runs through `main`
- **Then** it exits 2 and stderr carries a line beginning `file-and-close REFUSED: unanswered stop-ship question(s)` - a phrase none of the route's other refusals (hard blocker, already filed, nothing outstanding, no retro) emits - whose unit ids equal the literal set, compared with the literal; no CR file exists under `sdlc-studio/change-requests/`, RETRO0001 carries no `## Deferred at close` section, and the live run's outcome is still `running`
- **Mutant:** feed the refusal from `_remaining_units` - it still refuses, on the In Progress unit, and misses the bug rejected after Fixed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::EveryRunEndReadsThePredicateTests::test_file_and_close_refuses_an_unanswered_unit

### AC2: stop --force still stops THE RUN, and records the predicate's set as what it waived

- **Given** THE RUN, open
- **When** `sprint.py stop --force --reason "operator parks the run"` runs through `main`
- **Then** it exits 0, THE RECORD's outcome is `stopped`, and THE RECORD's `unanswered` unit ids equal the literal set - US0103 and US0110 (Review, REJECT not repaired), US0115 (Review, adversarial pass owed), US0111 and BG0101 (REJECT recorded after Done and Fixed) and US0117 (REJECT, dropped from the batch) included, none of which `could_have_proceeded` holds - compared with the literal, never with `could_have_proceeded`
- **Mutant:** fill the waived record from `blocked_by_pending`'s `unblocked` list, the source `could_have_proceeded` already reads
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::EveryRunEndReadsThePredicateTests::test_stop_force_records_the_waived_units

### AC3: handoff generate --outcome reports THE RUN's unanswered units and still closes it

- **Given** THE RUN, open
- **When** `handoff.py generate --title "run ended early" --outcome budget-spent` runs through `handoff.main`
- **Then** it exits 0 - it reports and never refuses; THE RECORD's outcome is `budget-spent` and its `unanswered` unit ids equal the literal set; and the handoff document it wrote carries THE SECTION, whose ids - parsed from that section alone - equal the literal set
- **Mutant:** fill the record from the handoff report's own Remaining list, `_classify`'s non-terminal units
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::EveryRunEndReadsThePredicateTests::test_handoff_outcome_records_and_names_the_unanswered_units

### AC4: a boundary stop reports THE RUN's unanswered units and still closes it

- **Given** THE RUN, open, carrying a rolling `policy` with one cycle unrun, and `_boundary_close_down` patched to return a failed close so the boundary stops with cause `close-gate`
- **When** `sprint.py boundary --retro RETRO0001 --no-fetch` runs through `main`
- **Then** the stop completes rather than refusing: THE RECORD's outcome is `blocked`, its `stop.cause` is `close-gate`, and its `unanswered` unit ids equal the literal set; and the handoff named by `stop.handoff` carries THE SECTION, whose ids equal the literal set
- **Mutant:** leave `_boundary_stop` writing only the stop record - it generates its handoff without `--outcome` and closes the run itself, so generate's write never reaches it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::EveryRunEndReadsThePredicateTests::test_a_boundary_stop_records_and_names_the_unanswered_units

### AC5: THE ANSWERED RUN ends by every route as today - the paired control

- **Given** THE ANSWERED RUN, in four fresh copies, `close_preflight` patched as above in the first and `_boundary_close_down` as in AC4 in the third
- **When** it is ended by `close --retro RETRO0001 --file-and-close`, `stop --force`, `boundary --retro RETRO0001 --no-fetch` and `handoff.py generate --outcome budget-spent`, one route per copy
- **Then** --file-and-close exits 0, files exactly one CR for the goal-verdict blocker and closes `closed-outstanding`; stop --force exits 0 at `stopped`; the boundary closes `blocked`; generate exits 0 at `budget-spent`; in all four THE RECORD's `unanswered` equals `[]`; and THE SECTION in the boundary's and generate's handoffs names no batch id
- **Mutant:** let a route read its own reader - each of the four holds a unit this batch has answered (US0102 and US0116 at Review, US0104 repaired, US0105 ruled, US0107 parked)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::EveryRunEndReadsThePredicateTests::test_an_answered_batch_ends_by_every_route

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in .claude/skills/sdlc-studio/scripts/sprint.py, delete the `unanswered_units` call and its refusal from `_file_and_close` | --file-and-close refuses THE RUN, naming exactly the predicate's set, before it files anything |
| AC1 | in .claude/skills/sdlc-studio/scripts/sprint.py, replace the `unanswered_units` call in `_file_and_close` with `_remaining_units(root, state)` | --file-and-close refuses THE RUN, naming exactly the predicate's set, before it files anything |
| AC1 | in .claude/skills/sdlc-studio/scripts/sprint.py, replace the `unanswered_units` call in `_file_and_close` with `blocked_by_pending(root)["unblocked"]` | --file-and-close refuses THE RUN, naming exactly the predicate's set, before it files anything |
| AC1 | in .claude/skills/sdlc-studio/scripts/sprint.py, move the unanswered refusal in `_file_and_close` below the filing loop, so the CRs and the retro section are written before it returns 2 | --file-and-close refuses THE RUN, naming exactly the predicate's set, before it files anything |
| AC2 | in .claude/skills/sdlc-studio/scripts/sprint.py, remove the `unanswered` field from the stop record `cmd_stop` writes under --force | stop --force still stops THE RUN, and records the predicate's set as what it waived |
| AC2 | in .claude/skills/sdlc-studio/scripts/sprint.py, set the `unanswered` field in `cmd_stop` from `blocked_by_pending`'s `unblocked` list | stop --force still stops THE RUN, and records the predicate's set as what it waived |
| AC2 | in .claude/skills/sdlc-studio/scripts/sprint.py, set the `unanswered` field in `cmd_stop` from `_remaining_units(root, state)` | stop --force still stops THE RUN, and records the predicate's set as what it waived |
| AC2 | in .claude/skills/sdlc-studio/scripts/sprint.py, make `cmd_stop` return 1 under --force whenever `unanswered_units` is non-empty | stop --force still stops THE RUN, and records the predicate's set as what it waived |
| AC3 | in .claude/skills/sdlc-studio/scripts/handoff.py, delete the `unanswered` run-state write from the --outcome path of `generate` | handoff generate --outcome reports THE RUN's unanswered units and still closes it |
| AC3 | in .claude/skills/sdlc-studio/scripts/handoff.py, set the `unanswered` record in `generate` from `report["remaining"]` instead of calling `sprint.unanswered_units` | handoff generate --outcome reports THE RUN's unanswered units and still closes it |
| AC3 | in .claude/skills/sdlc-studio/scripts/handoff.py, drop the Unanswered stop-ship questions section from `render_body` | handoff generate --outcome reports THE RUN's unanswered units and still closes it |
| AC3 | in .claude/skills/sdlc-studio/scripts/handoff.py, raise ValueError in `generate` when the predicate's set is non-empty, before `close_run` | handoff generate --outcome reports THE RUN's unanswered units and still closes it |
| AC3 | in .claude/skills/sdlc-studio/scripts/handoff.py, call the `unanswered` run-state write after `run_state.close_run` in `generate`, so the archive is taken before it | handoff generate --outcome reports THE RUN's unanswered units and still closes it |
| AC4 | in .claude/skills/sdlc-studio/scripts/sprint.py, delete the `unanswered` field from the run-state write in `_boundary_stop` | a boundary stop reports THE RUN's unanswered units and still closes it |
| AC4 | in .claude/skills/sdlc-studio/scripts/sprint.py, set the `unanswered` field in `_boundary_stop` from `_remaining_units(root, state)` | a boundary stop reports THE RUN's unanswered units and still closes it |
| AC4 | in .claude/skills/sdlc-studio/scripts/sprint.py, make `_boundary_stop` return 2 before `close_run` when `unanswered_units` is non-empty, leaving the run open | a boundary stop reports THE RUN's unanswered units and still closes it |
| AC4 | in .claude/skills/sdlc-studio/scripts/sprint.py, call the `unanswered` run-state write after `run_state.close_run` in `_boundary_stop`, so the archive is taken before it | a boundary stop reports THE RUN's unanswered units and still closes it |
| AC5 | in .claude/skills/sdlc-studio/scripts/sprint.py, make `_file_and_close` refuse whenever `handoff.remaining_count(root)` is non-zero | THE ANSWERED RUN ends by every route as today - the paired control |
| AC5 | in .claude/skills/sdlc-studio/scripts/sprint.py, set the `unanswered` field in `cmd_stop` to every batch unit whose critic ledger holds a REJECT verdict word, instead of calling `unanswered_units` | THE ANSWERED RUN ends by every route as today - the paired control |
| AC5 | in .claude/skills/sdlc-studio/scripts/sprint.py, set the `unanswered` field in `_boundary_stop` from the handoff report's `remaining` ids | THE ANSWERED RUN ends by every route as today - the paired control |
| AC5 | in .claude/skills/sdlc-studio/scripts/handoff.py, set the `unanswered` record in `generate` from `sprint._remaining_units` instead of `sprint.unanswered_units` | THE ANSWERED RUN ends by every route as today - the paired control |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-15 | sprint planning 2026-09-15 | Split from US0626 at the sprint goal review: close_run has six callers, and D0193 requires every route that ends a run to read the one unanswered-unit predicate - --file-and-close refuses, stop --force records what it waived, the boundary stops and handoff --outcome name what they left. |
| 2026-09-15 | sprint planning 2026-09-15 | Goal review round 2 repairs: AC2 now demands new behaviour: stop --force records the shared predicate's unanswered set, which today's could_have_proceeded record cannot see - as first written it was already green at HEAD. |
| 2026-09-15 | sprint planning 2026-09-15 | Goal review round 3: AC2's unanswered set is D0196c's - any unit whose standing REJECT critic.coverage_state does not read as repaired. |
| 2026-09-15 | sprint planning 2026-09-15 | Goal review round 4 notes (all three seats YES): AC1-AC3 reuse US0626 AC5's full fixture batch, so a route fed _remaining_units (which drops Fixed units) fails; AC4's answered batch holds a completely repaired unit. |
| 2026-09-15 | sprint plan repair 2026-09-15 | Plan repair after QA r1 REJECT. A preamble defines THE RUN (US0626 AC5's fixture, literal unanswered set {US0101, US0103, US0109, US0110, US0111, US0112, BG0101}, which differs from _remaining_units, blocked_by_pending's unblocked and handoff's _classify remaining list), THE ANSWERED RUN (the seven unanswered units dropped, leaving a completely repaired Review unit, a ruled unit, a parked unit and its dependant, and three abandoned REJECT carriers), THE RECORD (a separate unanswered field in the archived run record, [] when empty) and THE SECTION (a handoff section of its own, since Delivered and Remaining name batch ids too). close_preflight is patched to one deferrable goal-verdict blocker, so no hard blocker refuses first and --file-and-close has something to file. AC1 asserts a refusal phrase only this guard emits, ids equal to the literal set, and nothing filed. AC2 records the predicate's set under --force and still stops. AC3 (handoff generate --outcome) and new AC4 (the boundary stop, driven through sprint.py boundary with the close-down failing) each report and still close, with record and section equal to the literal set. AC5 is the paired control across all four routes, with one mutant per route reading its own reader. All tests move to test_sprint.py beside the shared fixture; test_handoff.py leaves Affects. 21 mutant rows. |
| 2026-09-15 | sprint plan repair 2026-09-15 | Re-aligned to US0626's round-2 predicate: a Review unit is answered only with its adversarial pass recorded, the walk includes ids a batch_changes drop removed, and a standing REJECT beats evidence, a drop, a park and a ruling. THE RUN's literal set is now nine, {US0101, US0103, US0109, US0110, US0111, US0112, US0115, US0117, BG0101}, and a unit id counts only when the fixture names it as a unit, so BG0903 (US0110's filed finding) never does; AC1 reads unit ids, not batch ids, because US0117 is dropped yet held. AC2 names US0115 (pass owed) and US0117 (REJECT, dropped) among the units could_have_proceeded does not hold. THE ANSWERED RUN is no longer THE RUN with its unanswered units dropped - a REJECT now beats a drop, so that tree would still hold them - but a separate tree whose planned batch holds only US0626 AC5's answered shapes (US0102, US0104 repaired, US0105 ruled, US0106 dropped without a REJECT, US0107 parked, US0108 its dependant, BG0102/US0113/US0114 abandoned, US0116 covered by a sprint-level APPROVE), each justified against the predicate's text; none of the nine is planned or dropped there, so the predicate returns an empty set. Every mutant row re-checked against both trees; all 21 kept. |
