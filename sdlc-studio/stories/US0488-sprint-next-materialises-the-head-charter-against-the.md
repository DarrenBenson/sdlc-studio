# US0488: sprint next materialises the head charter against the backlog as it is at that moment, and stops when its scope resolves to nothing

> **Status:** Done
> **Delivers:** RFC0057
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/scripts/sprint_report.py
> **Epic:** EP0176
> **Points:** 5

## User Story

**As a** operator returning to a queue somebody planned days ago
**I want** the next charter planned against the backlog as it is at that moment, not as it was when written
**So that** the bugs and lessons the intervening work generated are in the batch, which is why a frozen queue was refused

## Acceptance Criteria

### AC1: the head charter is materialised against the current backlog

- **Given** a queue whose head charter names a scope rule, and a backlog that has changed since it was written
- **When** sprint next runs
- **Then** the batch is resolved from the backlog as it is now, so units created since the charter was authored are included and units since delivered are not
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::SprintNextTests::test_next_reaches_the_SHIPPED_ENTRY_POINT_not_only_the_library
- **Verified:** yes (2026-08-04)

### AC2: an empty scope stops and reports, leaving the queue intact

- **Given** a head charter whose scope rule resolves to no units
- **When** sprint next runs
- **Then** it stops, reports that the charter's scope is empty and names it, and the queue is left unchanged rather than the charter being silently skipped or dropped
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::SprintNextTests::test_an_empty_scope_stops_and_reports_without_touching_the_queue
- **Verified:** yes (2026-08-04)

### AC3: materialising respects the one open run slot

- **Given** a run already open
- **When** sprint next runs
- **Then** it refuses rather than merging the charter's batch into the run already open, preserving the single-run-slot rule
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::SprintNextTests::test_next_refuses_while_a_run_is_open
- **Verified:** yes (2026-08-04)

## Verification evidence

Functional. Exercised through the shipped CLI on the live tree: `sprint.py next --dry-run`
refuses with `run RUN-01KZ5YXM is still open - close or stop it first`, which is AC3 firing
against a genuinely open run rather than a fixture.

Three mutants executed, `__pycache__` purged and each child run under `python3 -B`, anchors
asserted unique, source restored byte-identical:

| Mutant | Result |
| --- | --- |
| cache the resolved batch instead of re-resolving | killed |
| drop the open-run refusal | killed |
| treat an empty scope as success | killed |

The first is the one AC1 exists for, and its test is the load-bearing one: a charter is
materialised, then the backlog MOVES underneath it - one unit created since, one delivered
since - and the second materialisation must return the new unit and not the delivered one. A
cached batch passes every other assertion in the class and fails only that.

**A design decision was needed and is recorded rather than assumed (D0127).** `US0487` shipped
`scope` as prose, and this criterion requires the batch to be RESOLVED from it; prose does not
resolve. A charter now carries two fields: `Scope rule` stays the human-readable intent, and
`Scope query` speaks `sprint plan`'s OWN selector vocabulary, parsed into the same `(kind,
status)` tuples `select_batches` already takes - one vocabulary rather than two that drift. A
worklist reference was rejected outright: it freezes the batch at authoring time, which would
have made this run's own goal false.

A charter may be queued with prose alone. `next` refuses it BY NAME at materialise time rather
than creation refusing it, because queueing an intention nobody has yet worked out how to
select is legitimate - and a control test pins that.

**Two defects in this delivery, both mine, both caught by a gate rather than by me.**

The charter render was left syntactically invalid - a `+` dropped between a conditional field
and the section that follows it - and I "verified" the edit by parsing `sprint.py`, which was
not the file I had changed. `artifact.py` did not import at all, and the whole skill suite went
down with it. Checking the wrong artefact is not checking.

And the lane-check refused this unit for the third time in two runs - US0467, US0487, now
US0488 - because all three verifiers exercised `materialise_next` as a library and none entered
`main()`. AC1 now drives `sprint.py next` itself, in both directions: a dry run that names the
charter and its resolved units and leaves the charter Queued, and a refusal that exits non-zero
with the open run named. It is pinned rather than remembered again.

**A third dependency direction, found by a gate.** `test_help_structure` requires every parser
verb to appear in `help/sprint.md` as an INVOCATION, not merely named in a sentence. So adding
`next` obliged documenting it immediately - while US0492, the unit that owns the queue
documentation, cannot be delivered until these verbs exist. The dependency runs BOTH ways:
US0492 reads what US0488 to US0491 create, and each of those cannot land until it has documented
itself. This unit therefore carries a minimal charter-queue section, and US0492 expands it
rather than writing it from nothing. Recorded on CR0530, which is about exactly this: a
file-disjoint unit is not necessarily an independent one.

A FOURTH direction turned up on the next attempt: the cycle-drift guard refuses a new
ceremony verb that has neither a close-checklist row nor a declaration that it is not
ceremony. `next` is declared non-ceremony, because it sits with `plan` on the OPENING
side of a run - a close-checklist row would ask the close to certify something that
happened before the run began.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed against the D0072 rulings |
