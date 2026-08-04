# US0467: status names the open run - id, rung, Sprint Goal, batch and remaining - from the run state, with remaining derived from the same predicate the handoff uses

> **Status:** Review
> **Delivers:** CR0440
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/status.py, .claude/skills/sdlc-studio/help/status.md, .claude/skills/sdlc-studio/scripts/tests/test_status.py
> **Epic:** EP0170
> **Points:** 5

## User Story

**As a** operator or agent re-anchoring at session start or after a compaction
**I want** the dashboard the doctrine tells me to run first to report the open run
**So that** a run opened in an earlier session is resumed rather than orphaned behind unstarted-looking backlog

## Acceptance Criteria

### AC1: the run line names id, rung, Sprint Goal, batch and remaining under distinct labels

- **Given** two fixture workspaces holding an open run: one with `goal` set to a ladder rung, and one with `goal: None` and a full `sprint_goal` sentence - the live shape (RUN-01KYHVWK on disk today has goal=None and a 25-word sprint_goal)
- **When** the four-pillar dashboard is printed, and again with --format json
- **Then** both name run_id, the rung rendered from the `goal` field as `rung=<value>` and `rung=unset` when it is None (never blank, never the Sprint Goal), the Sprint Goal from `sprint_goal` under its own distinct label, the batch size and remaining; the JSON carries them as fields, not only a rendered line; the labelling reuses sprint.run_opened_line's convention (sprint.py:2337, which exists precisely because a bare `goal=` read as either) rather than status.py minting a second one
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::OpenRunLineTests::test_the_run_line_reaches_the_SHIPPED_ENTRY_POINT_not_only_the_library
- **Verified:** yes (2026-08-04)

### AC2: remaining is the handoff's predicate, not a second definition

- **Given** an open run whose batch holds four units - a Done story, a Won't Implement CR, an Open bug, and a fourth pulled out via run_state.drop_from_batch (which removes it from `batch` and appends action/id/reason/at to batch_changes)
- **When** the dashboard's remaining count is compared with handoff.build's summary over the same run state, and again after a run_state.add_to_batch mutation
- **Then** remaining counts the Open bug only; the Won't Implement unit is terminal-but-not-delivered (handoff.py:335) and is NOT remaining; the batch-dropped unit is in neither count because it left `batch`; both readers return the same number from ONE predicate (handoff's terminal test over sdlc_md.terminal_statuses), status.py holding no copy of what delivered, dropped or remaining means, and the counts follow the mutations
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::OpenRunLineTests::test_remaining_matches_handoff_over_done_wont_implement_open_and_batch_dropped
- **Verified:** yes (2026-08-04)

### AC3: no open run is an answer, not a silence

- **Given** a workspace with no run-state.json at all, and one whose only run is closed (outcome not running, ended_at set, batch still populated)
- **When** the dashboard is printed for each, text and JSON
- **Then** each states plainly that no run is open; neither emits a run id, rung, Sprint Goal or batch size read off the closed record; the JSON carries the run key explicitly as null rather than omitting it, so a consumer distinguishes absence from an older schema
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::OpenRunLineTests::test_absence_of_a_run_is_stated_not_silent
- **Verified:** yes (2026-08-04)

### AC4: an unreadable run state is named, never reported as no run

- **Given** a run-state.json that exists but does not parse (a half-written or corrupted record)
- **When** the dashboard is printed
- **Then** it names the unreadable state and the path and does NOT report `no run open` - the two facts are different, and reporting the wrong one orphans the run it failed to read
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::OpenRunLineTests::test_unreadable_run_state_is_named_not_reported_as_no_run
- **Verified:** yes (2026-08-04)

### AC5: the help page documents exactly the emitted fields and lands a reader on the re-anchor instruction

- **Given** help/status.md's run-line section
- **When** the field labels the page documents are compared with the labels the run line actually emits, in both directions, and the section's doctrine pointer is resolved
- **Then** the two sets match both ways, so a field added, renamed or dropped in code fails; and the pointer carries a #anchor that resolves to a real heading whose section contains BOTH the compaction/reset wording and a `/sdlc-studio status` invocation - a link at a file's title fails. The target is templates/agent-instructions.md#operating-doctrine, which carries that instruction (line 31-35); reference-doctrine.md does not (grep for `session start`, `compaction` and `re-anchor` over it returns zero hits), so pointing there would satisfy a presence check while landing the reader nowhere
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::RunLineDocTests::test_help_page_documents_emitted_fields_and_anchors_the_reanchor_instruction
- **Verified:** yes (2026-08-04)

## Verification evidence

Functional, driven through the shipped CLI on the live tree rather than only in fixtures:
`status.py` prints `Run: RUN-01KZ56M6 (rung=unset, sprint-goal="...", batch=7, remaining=7)` as
its FIRST line, and `status.py pillars --format json` carries the same five values as fields.

Three mutants executed, `__pycache__` purged and each child run under `python3 -B`, anchors
asserted unique, source restored byte-identical:

| Mutant | Result |
| --- | --- |
| render the rung from `sprint_goal` instead of `goal` | killed |
| count `remaining` locally instead of asking `handoff.build` | killed |
| report an unreadable run state as no run | killed |

The second mutant is the one AC2 exists for: `remaining` is `handoff.build`'s own count, so the
dashboard holds no copy of what delivered, dropped or remaining means and the two readers cannot
disagree. The third pins the three-state distinction - no run, a run, and a run-state file that
does not parse - because reporting the third as the first orphans the run it failed to read.

**One defect in this unit's own test, found by running it.** AC5's both-ways check first
compared documented field NAMES against the rendered text line, and `run_id` appears there as a
value under no label - so the check passed on four fields and could never have seen a rename of
the fifth. It now compares against the JSON field set, which is what the criterion asked for
("carries them as fields, not only a rendered line"), with the rendered labels asserted
separately.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: authored from the reviewed breakdown (two adversarial rounds), scope capped to the request per D0069 |
