# BG0703: The unanswered-set predicate's fail-closed handlers and the handoff behaviours around it survive mutants no test kills

> **Status:** Open
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_handoff.py, .claude/skills/sdlc-studio/scripts/tests/test_handoff_line.py
> **Evidence:** Independent delivery review, RUN-01M2JA6J 2026-09-15: verdicts/US0626-delivery-qa.txt (qa seat); verdicts/US0626-delivery-qa-r2.txt (qa seat, round two); verdicts/US0626-delivery-engineering.txt (engineering seat); verdicts/US0626-delivery-engineering-r2.txt (engineering seat, round two); verdicts/US0823-delivery-qa.txt (qa seat); verdicts/US0823-delivery-engineering.txt (engineering seat); verdict rows in sdlc-studio/reviews/critic-verdicts.md.
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Each of these mutants survives the 46 US0626 tests, though each branch refuses correctly when run alone today: the fail-closed handlers in `_close_checklist` (sprint.py:5997), `_checklist_blockers` (7626) and `cmd_stop` (10669) made pass-through; the preflight calling `unanswered_units` without `retro_id` (7625), which then holds a unit the chain step passes; the hold line dropped from the stop-ship and mutation-mode branches (6013, 6021); stop's ways-out line removed (10682); the run id matched as a bare substring (5792); rung end compared without the type vocabulary (5889); status read raw (5851); and 'not abandoned' dropped from rejected (5870), which changes only the why text. The evidence limb is restated in `unanswered_units` (5877-5879) beside `_awaits_signoff`'s own copy (10551-10553), two copies that must move together. For the routes built on the predicate, each of these left `test_sprint`, `test_handoff` and `test_handoff_line` green: dropping generate's retro pass-through (handoff.py:790), which makes generate --retro RETRO0001 read a newer RETRO0002; rendering a failed predicate as none (handoff.py:503), which makes the handoff say 'None: every batch unit is delivered...' after the predicate raised; recording a failure as an empty list instead of null (sprint.py:5931); and removing the stop --force waived line (sprint.py:10703) or the pickup note (handoff.py:702). The changelog claims each of these behaviours.

## Steps to Reproduce

Apply any listed mutant in a throwaway copy - for example replace the body of the fail-closed except in `_close_checklist` with pass, or make handoff.build render a raised predicate as an empty set - and run `test_sprint.py`, `test_handoff.py` and `test_handoff_line.py`: green.

## Proposed Fix

Add a test per branch, driven through the CLI where the behaviour is a printed line, and share one evidence-limb helper between `unanswered_units` and `_awaits_signoff.`

## Acceptance Criteria

This bug's subject IS a list of mutants, so each criterion names every edit it must fail on and the
test carries one subTest per edit - a criterion pinning one branch of a group would leave the rest
exactly as they are today. Where the behaviour is a printed line the test drives the shipped
command, because an in-process call cannot see a line the CLI never prints.

### AC1: each fail-closed handler around the predicate refuses through its own entry point

- **Given** a workspace on which `unanswered_units` raises - a carried table whose retro file cannot
  be read, and the predicate patched to raise, run as two fixtures
- **When** `sprint.py close --file-and-close --retro RETRO0001`, `sprint.py preflight` and
  `sprint.py stop` each run through `main`
- **Then** every one names `the unanswered-unit hold could not be computed` with the exception type
  and message; the close and the stop exit non-zero, and the pre-flight reports it as a blocking row
  and answers `ready` false. No route reports a pass over a set nobody could read
- **Mutant:** three edits, one subTest each - replace the body of the `except` at sprint.py:5997
  (`_close_checklist`), at 7669 (`_checklist_blockers`) and at 10712 (`cmd_stop`) with a
  pass-through that leaves the hold empty. Each must redden on its own, so repairing one cannot
  cover the other two
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::UnansweredUnitHoldsTheCloseTests::test_each_fail_closed_handler_refuses_through_its_own_entry_point

### AC2: the predicate judges a unit by its type's vocabulary and its run's id, never by raw text

- **Given** four fixtures: a retro whose text carries `RUN-01M2JA6JZ` while the run records
  `RUN-01M2JA6J`; a batch unit whose `Status` field is a non-canonical spelling of its rung-end
  status; a bug and a story both standing at their own type's rung-end status under one run; and a
  unit abandoned by a ruling that also carries a standing delivery REJECT
- **When** `sprint.py stop` runs over each
- **Then** the foreign run id answers nothing, so the rulings read unreadable; the non-canonical
  spelling is canonicalised in its own type's vocabulary before it is compared; the rung-end
  comparison goes through `_terminal_in_type_vocab`, so the bug and the story are each judged
  against their own terminal rather than one type's; and the abandoned unit's `why` names the ruling
  alone, never an unanswered delivery REJECT
- **Mutant:** four edits, one subTest each - replace the token-bounded run-id pattern at
  sprint.py:5792 with a bare `run_id in text`; read the raw `Status` at 5851 instead of
  canonicalising it; compare `status == rung_end` at 5889 without the type vocabulary; and drop
  `not abandoned` from the `rejected` limb at 5870, which changes only the why text and so is killed
  only by asserting that text
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::UnansweredUnitHoldsTheCloseTests::test_the_predicate_reads_ids_and_statuses_by_vocabulary

### AC3: no reader of the predicate carries its own copy of the question

- **Given** a run whose named retro rules US0105 while a newer retro carrying the run id rules
  nothing, and a unit at Review covered by an independent sprint-level review rather than a
  per-unit one
- **When** `sprint.py preflight --retro RETRO0001` and `sprint.py stop` run, and the close's
  checklist step runs over the same tree
- **Then** the pre-flight passes its `retro_id` to `unanswered_units` (sprint.py:7668) and so holds
  exactly what the checklist step holds, naming no unit the chain step passes; and the evidence
  limb, which decides whether an adversarial pass has been made, is ONE helper called by both
  `unanswered_units` (sprint.py:5877-5879) and `_awaits_signoff` (10594-10596), so the
  sprint-covered unit is read the same way by the close and by the stop
- **Mutant:** two edits, one subTest each - drop `retro_id` from the pre-flight's call at 7668, so
  it holds a unit the chain step answers; and leave the two evidence limbs as separate copies and
  change only the one in `unanswered_units`, so the stop reports `adversarial pass owed` over a unit
  the close counts as covered
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::UnansweredUnitHoldsTheCloseTests::test_every_reader_asks_the_predicate_the_same_question

### AC4: every line a route prints about the set is pinned by a test that reads the route's own output

- **Given** a run holding one unanswered unit, run over four states: a stop-ship ruling, a
  mutation-evidence mode the close refuses, an unforced stop and a forced one
- **When** `sprint.py close --file-and-close` and `sprint.py stop` (with and without `--force`) run
  through `main` and their stderr is read
- **Then** the close's stop-ship branch and its mutation-mode branch each carry the held line and
  the ways out; the unforced stop prints its ways-out line; and the forced stop prints the waived
  line naming the set it overrode by `unanswered_rows`
- **Mutant:** four edits, one subTest each - drop the `_with_hold` wrapper from the stop-ship return
  at sprint.py:6013 and from the mutation-mode return at 6021 (each leaving a bare refusal that
  names no held unit); remove the ways-out print at 10725; and remove the forced-stop waived line at
  10746-10748, which leaves `--force` recording the waiver and never stating it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::EveryRunEndReadsThePredicateTests::test_every_route_prints_the_line_it_claims

### AC5: the handoff renders what it read, and an uncomputed set is never rendered or recorded as none

- **Given** a run with a named retro RETRO0001 and a newer RETRO0002 that rules nothing, and a
  second tree on which the predicate raises
- **When** `handoff.py generate --retro RETRO0001 --outcome <outcome>` runs over each
- **Then** the document's section reads RETRO0001's rulings, because `generate` passes its `--retro`
  to `build` (handoff.py:790); the failed tree's section says the set could not be computed and
  names the reason, never `None: every batch unit is delivered...`; the pickup note above it states
  the count when the set is non-empty; and the run record the outcome writes carries `unanswered`
  null with its reason, never `[]`
- **Mutant:** four edits, one subTest each - drop `retro=retro` from `generate`'s `build` call at
  handoff.py:790, so `--retro RETRO0001` reads RETRO0002; render a failed predicate as `[]` rather
  than None at handoff.py:503, which makes the document claim every unit is answered; drop
  `_unanswered_note(report)` from `render_body` at handoff.py:702, so a pickup reading `nothing
  remains` sits above a stop-ship question; and return `{"unanswered": []}` from
  `unanswered_record`'s failure branch at sprint.py:5931
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_handoff.py::BuildTests::test_the_document_renders_the_set_it_read

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Filed |
| 2026-09-17 | sdlc-studio | Groomed for `sprint plan`: the three derived criteria are replaced by five authored ones covering all seventeen surviving mutants the summary names - the three fail-closed handlers, the four vocabulary and id reads, the two duplicated readers, the four printed lines, and the four handoff and record renderings. Each criterion names its edits and its test carries one subTest per edit, so no repair can cover a sibling branch. |
