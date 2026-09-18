# BG0702: The unanswered set's ways out are picked by substring and offer dead ends for a stop-ship ruling, and the set is rendered and recorded in drifting copies

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/handoff.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_handoff.py
> **Evidence:** Independent delivery review, RUN-01M2JA6J 2026-09-15: verdicts/US0626-delivery-engineering.txt (engineering seat); verdicts/US0626-delivery-engineering-r2.txt (engineering seat, round two); verdicts/US0626-delivery-qa-r2.txt (qa seat, round two); verdicts/US0823-delivery-engineering.txt (engineering seat); verdict rows in sdlc-studio/reviews/critic-verdicts.md.
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`unanswered_ways_out` picks remedies by substring over the joined why text, and 'ruling unreadable' is a bare literal beside the `WHY_` constants (sprint.py:5939, 5953). Its stop-ship case is now wrong: for a Done or dropped unit ruled stop-ship it offers 'finish it' and 'batch drop', which answer nothing since the repair (sprint.py:5956-5958), and never names revising the ruling. The close preflight reports a stop-ship-ruled batch unit twice, once in the stop-ship rows (sprint.py:7594-7599) and again in the hold line (7632-7635), so `preflight_headline` counts one fact as two blockers. `handoff._unanswered_body` re-implements the row format of `sprint.unanswered_rows`, which the same change added as the one shared row shape (handoff.py:673-675 against sprint.py:5910). A successful `unanswered_record` write carries no `unanswered_error` key and `run_state.update` merges fields, so a set written once on failure and again on success (the boundary's already-closed branch re-writes after generate --outcome) keeps a stale `unanswered_error` beside a valid list (sprint.py:5925-5933).

## Steps to Reproduce

1. Rule a Done batch unit stop-ship in the run's retro and run python3 .claude/skills/sdlc-studio/scripts/sprint.py stop - the ways-out line offers 'finish it' and 'batch drop' and does not mention revising the ruling. 2. sprint.py preflight on the same state - the unit is listed twice and counted as two blockers. 3. Record the set once with the predicate raising, then once succeeding - the archived record holds both `unanswered_error` and the list.

## Proposed Fix

Key remedies on the `WHY_` constants, not substrings, and add a constant for an unreadable ruling. For a stop-ship ruling, name revising the ruling as the way out. Count a unit once in the preflight. Render handoff rows through `unanswered_rows.` Write `unanswered_error` as null on a successful write.

## Acceptance Criteria

The set is one fact with four renderings - the close's hold line, the pre-flight's blockers, the
stop's refusal and the handoff's section - and every defect below is one rendering disagreeing with
another. So each criterion is asserted at the surface that prints it, never on the helper alone.

### AC1: a remedy is selected by the reason recorded on the held row, never by matching text in the rendered why

- **Given** a held set in which one row is held by `WHY_REJECT`, one by `WHY_PASS_OWED`, one by
  `WHY_AT_REVIEW` and one by an unreadable carried table, and a fifth row held for a single reason
  whose rendered `why` text also quotes the wording of the other three
- **When** `sprint.py stop` refuses and prints its ways-out line
- **Then** each held row carries the reasons that produced it as keys - the `WHY_` constants
  themselves, including a new one for an unreadable ruling that replaces both the bare
  `"ruling unreadable"` literal at sprint.py:5953 and the inline text the predicate writes at
  sprint.py:5898 - and `unanswered_ways_out` selects on those keys, so the fifth row earns exactly
  one remedy and the line carries four in total, not five
- **Mutant:** keep the substring tests over the joined why text (sprint.py:5939 and 5943-5955), so
  the fifth row's quoted wording earns remedies nothing in the set needs; and keep the unreadable
  literal separate from the text at 5898, so rewording one silently drops the remedy for the other
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::UnansweredUnitHoldsTheCloseTests::test_a_remedy_is_keyed_on_the_recorded_reason

### AC2: a stop-ship ruling's way out is to fix the finding or revise the ruling, and nothing that answers nothing

- **Given** a batch unit at Done ruled `stop-ship` in the retro carrying the run id, and that
  ruling holding the whole set
- **When** `sprint.py stop` refuses and prints its ways-out line
- **Then** the line names revising the ruling in that retro beside fixing the finding, and offers
  neither `finish it` nor `sprint.py batch drop` - a Done unit cannot be finished and a drop changes
  nothing the predicate reads over a stop-ship ruling. The control is the same command over a set
  holding one In Progress unruled unit, where the `finish it` and `batch drop` tail is still printed
- **Mutant:** keep the unconditional tail at sprint.py:5956-5958, so a Done stop-ship unit is
  offered two routes that close nothing and the one route that would - revising the ruling - is
  named nowhere
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::UnansweredUnitHoldsTheCloseTests::test_a_stop_ship_ruling_names_revising_the_ruling

### AC3: a stop-ship-ruled batch unit is one unmet prerequisite in the pre-flight, not two

- **Given** a run whose batch holds US0101 ruled `stop-ship` in the retro carrying the run id, with
  every other checklist item answered
- **When** `sprint.py preflight` runs and `preflight_headline` renders its count
- **Then** the headline reports one unmet prerequisite for US0101: the stop-ship row
  (sprint.py:7637-7642) and the unanswered hold line (7675-7678) are one blocker naming the unit
  once. The control is a run holding one stop-ship unit and one separately unfinished unit, which
  reports two
- **Mutant:** keep both rows, so one fact is counted twice and the pre-flight says
  `2 unmet prerequisite(s)` - the count that cries wolf `preflight_headline`'s own docstring
  (sprint.py:7586-7600) was written against
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::OnePreflightCountReadByBothRenderersTests::test_a_stop_ship_unit_is_one_unmet_prerequisite

### AC4: the handoff's rows are the shared row shape, not a second copy of it

- **Given** a run holding one unanswered unit with findings filed to a bug, and one with none filed
- **When** `handoff.py generate` renders the `Unanswered stop-ship questions` section
- **Then** each bullet's text after its list marker is what `sprint.unanswered_rows` produces for
  that row, taken from the helper rather than rebuilt at handoff.py:673-675 - so a test that changes
  `unanswered_rows`' `NONE filed` wording moves the handoff section in the same run, and the
  `filed to` and `NONE filed` arms are both asserted
- **Mutant:** keep handoff's own f-string rows and change `unanswered_rows`' wording or separator -
  every other route moves and the document keeps the old shape, which is the drift this criterion
  exists to close
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_handoff.py::BuildTests::test_the_unanswered_section_renders_the_shared_row_shape

### AC5: a successful set write clears the reason a failed one left behind

- **Given** a run state on which `unanswered_record(None, "<reason>")` has already been merged by a
  failed computation, as the boundary's already-closed branch does before it re-writes
- **When** a later successful write lands through `run_state.update(root, **unanswered_record(ua))`
- **Then** the state carries `unanswered_error` null beside the valid list, so no route reports a
  set that both could not be computed and holds units. Asserted on the merged run state, not on the
  helper's return alone, because the defect is `run_state.update`'s merge keeping the absent key
- **Mutant:** keep the success branch at sprint.py:5933 returning a dict with no `unanswered_error`
  key, leaving the failed write's reason standing beside a list the predicate did compute
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::EveryRunEndReadsThePredicateTests::test_a_successful_set_write_clears_a_stale_error

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Filed |
| 2026-09-17 | sdlc-studio | Groomed for `sprint plan`: the two derived criteria are replaced by five authored ones, one per defect the summary names - reason-keyed remedies with a constant for an unreadable ruling, the stop-ship ways out, the pre-flight's double count, the handoff's duplicated row shape, and the stale `unanswered_error`. Each is asserted at the surface that prints it and names the edit it must fail on. |
