# US0489: The queue is inspectable and editable: show the next charter with its goal and resolved contents, insert, cancel, clear and reorder

> **Status:** Review
> **Delivers:** RFC0057
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/scripts/sprint_report.py
> **Epic:** EP0176
> **Points:** 5

## User Story

**As a** operator who planned five sprints and now needs to change one
**I want** the queue to be inspectable and editable - show the next, insert, cancel, clear and reorder
**So that** a plan somebody wrote can be corrected without hand-editing state or throwing the whole queue away

## Acceptance Criteria

### AC1: showing the next charter reports its goal and the contents it would resolve to

- **Given** a queue with charters
- **When** the next charter is shown
- **Then** its goal, scope rule and appetite are reported together with the units it would resolve to against the current backlog, so what will run is visible before it runs
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::QueueCrudTests::test_the_queue_reaches_the_SHIPPED_ENTRY_POINT
- **Verified:** yes (2026-08-04)

### AC2: insert, cancel and clear each change the queue and are each recorded

- **Given** a queue of several charters
- **When** a charter is inserted at a position, another cancelled, and the queue cleared
- **Then** each operation changes the order or membership as asked and records what it did, so the queue's history explains its current shape
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::QueueCrudTests::test_insert_cancel_and_clear_change_the_queue_and_are_recorded
- **Verified:** yes (2026-08-04)

### AC3: WSJF order is recomputed at each next, not frozen when the queue was authored

- **Given** a queue ordered by WSJF and a backlog whose values have since changed
- **When** the next charter is resolved
- **Then** the order reflects the recomputed values rather than the ranking recorded at authoring time
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::QueueCrudTests::test_wsjf_order_is_recomputed_at_each_next
- **Verified:** yes (2026-08-04)

### AC4: an operation naming a charter the queue does not hold is refused

- **Given** a queue
- **When** cancel or reorder names an id absent from it
- **Then** the operation is refused naming the id, rather than succeeding over nothing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::QueueCrudTests::test_an_operation_on_an_absent_charter_is_refused
- **Verified:** yes (2026-08-04)

## Verification evidence

Functional, driven through the shipped CLI on the live tree: `sprint.py queue show` lists
`SC0001` as the head with its goal, scope rule and appetite, and reports honestly that it
resolves to nothing runnable because `RUN-01KZ5YXM` is open.

Three mutants executed, `__pycache__` purged and each child run under `python3 -B`, anchors
asserted unique, source restored byte-identical:

| Mutant | Result |
| --- | --- |
| sort unranked charters BEFORE ranked ones | killed |
| drop the membership check from `reorder` | killed |
| cache the head resolution | killed |

The first pins a decision worth stating: **absence is not rank zero.** An unranked charter sorts
AFTER every ranked one, so giving one charter a rank does not silently reshuffle the rest, and a
queue nobody has reordered still reads in authoring order because the id already carries it. A
rank exists only where somebody made a decision.

`cancel` and `clear` WITHDRAW rather than delete, each keeping its reason on the charter. A
cancelled plan is a decision somebody made, and deleting it loses the only trace of why the
queue looks as it does - the refusal on a missing reason is there for the same purpose.

Only the head is resolved. Resolving every charter would be arithmetic over a backlog the
earlier runs will have changed before the later charters are reached, and a number that looks
precise and is not is worse than no number.

**A fifth obligation, from the CLI-grammar guard.** A per-subcommand `--root` must default to
`argparse.SUPPRESS`, never to `"."`: a concrete default overwrites a `--root X queue clear`
given BEFORE the verb, so the value the caller set is silently dropped and the command runs
against the wrong tree. Mine defaulted to `"."` on all four nested verbs. This is the fifth
thing adding a CLI verb obliges beyond the code, alongside documenting it as an invocation,
a verifier that enters `main()`, a ceremony-or-not declaration, and an accurate `Affects`.

**The lane-check refused this unit too - the fourth in a row.** US0467, US0487, US0488, now
US0489: each time I wrote the CLI test and then pointed the criterion at the library one, so the
verifier that proves the wiring existed but nothing was held to it. The pattern is now plain
enough to state as practice rather than keep rediscovering: **the criterion about what a command
DOES should name the test that runs the command**, and a library test belongs on the criteria
about the function's own behaviour. AC1 names the CLI test.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed against the D0072 rulings |
