# US0628: a unit closed over a REJECT names, in its own record, the artefact its findings were filed to

> **Status:** In Progress
> **Delivers:** CR0526
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Epic:** EP0206
> **Points:** 3
> **Depends on:** US0627
> **Persona:** Maya Okafor

## User Story

**As a** later reader of a closed story
**I want** a story or bug closed over a REJECT to name the filed artefact in its own record
**So that** the discharge is visible on the artefact rather than only in a verdict ledger nobody opens

## Acceptance Criteria

Every test in this class reads the discharge through ONE detector, `_findings_filed_line(path)`:
the `> **Findings-filed-to:** ...` metadata line in the CLOSING unit's own file, matched as a
line whatever its value (an empty value is still a line), or `None`. No criterion asserts a bare
`assertIn(<id>, text)`: every fixture unit names its filed ids in its own prose as well, so a
whole-file search passes with no line written. Every fixture's discharge is a `filed:` closure
recorded through `critic.record_repair` against the REJECT and naming an artefact that exists,
so US0627's gate passes it; the discharge is read through `critic.repair_state`.

### AC1: a story closed over a REJECT names every filed artefact, in its own record

- **Given** a story whose delivery REJECT raised two findings, each closed `filed:` to a different existing bug (BG0002, BG0003)
- **When** `transition.py set --status Done` runs
- **Then** it exits 0, the story reads `Done`, and the detector's line in the story's own file names both BG0002 and BG0003
- **Mutant:** the filed ids stay in the repair ledger alone
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::ClosedOverRejectNamesTheBugTests::test_the_story_names_every_filed_artefact
- **Verified:** yes (2026-09-15)

### AC2: the one-call close names them too

- **Given** the AC1 fixture, closed with the one-call form `set --status Done --verdict APPROVE --reviewer <r> --author <a>`, which appends its APPROVE to the ledger BEFORE the transition runs
- **When** the transition lands
- **Then** the detector's line still names BG0002 and BG0003 - an APPROVE with no brief fingerprint retires no REJECT (`critic._unanswered_rejects`), so `repair_state` still reads the filed closures while the ledger's LAST row is an APPROVE
- **Mutant:** key the write on the latest ledger row being a REJECT
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::ClosedOverRejectNamesTheBugTests::test_the_one_call_close_names_the_filed_artefacts
- **Verified:** yes (2026-09-15)

### AC3: a bug names it at every delivered terminal

- **Given** two copies of a bug whose REJECT's one finding is closed `filed:` to an existing CR
- **When** one copy is set to `Fixed` and the other directly to `Verified` (a bug reaches Verified without passing Fixed)
- **Then** both land, and each copy's detector line names the CR
- **Mutant:** write the line for stories only
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::ClosedOverRejectNamesTheBugTests::test_a_bug_names_the_filed_artefact_at_every_delivered_terminal
- **Verified:** yes (2026-09-15)

### AC4: a terminal walk writes the line once

- **Given** the AC3 bug
- **When** it is walked `Fixed` -> `Verified` -> `Closed`, each step through `transition.py set`
- **Then** every step lands and the file carries exactly ONE `Findings-filed-to` line (counted over the whole file), naming the CR
- **Mutant:** insert a new line on every terminal step
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::ClosedOverRejectNamesTheBugTests::test_a_terminal_walk_writes_the_line_once
- **Verified:** yes (2026-09-15)

### AC5: a refused close writes no line

- **Given** the AC1 fixture carrying, in addition, one unresolved Open Question; and beside it the positive control, the same fixture with that question moved under `## Resolved Questions`
- **When** `transition.py set --status Done` runs on each
- **Then** the first is refused with a message naming the Open Question and not the REJECT (so US0627's gate passed it), its status is unchanged and the detector returns `None`; the control lands at `Done` with the line naming both bugs
- **Mutant:** stamp the field before the gated transition
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::ClosedOverRejectNamesTheBugTests::test_a_refused_close_writes_no_line
- **Verified:** yes (2026-09-15)

### AC6: an ordinary close writes no such line - paired with a close that does

- **Given** three copies of one story fixture: (a) a REJECT closed `filed:` to BG0002; (b) no REJECT recorded at all; (c) a REJECT closed only by `fixed:` closures whose evidence names an existing id (`fixed: pinned by the regression test BG0004 asked for`); and (d) a MIXED repair - finding 1 closed `filed:` to BG0002 and finding 2 closed `fixed:` with evidence naming BG0004
- **When** each is set to `Done` through `transition.py set`
- **Then** all three land at `Done`; the detector finds the line naming BG0002 on (a), and returns `None` on (b) and (c); on (d) the detector's line names BG0002 and does NOT name BG0004 - the check scoped to that line alone, since the fixture's prose names both ids - a marker on every close is one no reader looks at, and a fix is not a filing
- **Mutant:** write the field even when nothing was filed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::ClosedOverRejectNamesTheBugTests::test_an_ordinary_close_writes_no_discharge_line
- **Verified:** yes (2026-09-15)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in .claude/skills/sdlc-studio/scripts/transition.py, remove the write of the Findings-filed-to field, so the filed ids stay in the repair ledger alone | a story closed over a REJECT names every filed artefact, in its own record |
| AC1 | in .claude/skills/sdlc-studio/scripts/transition.py, change the discharge to take only the first closure's artefact (`closed[0]`), dropping every later filed id | a story closed over a REJECT names every filed artefact, in its own record |
| AC1 | in .claude/skills/sdlc-studio/scripts/transition.py, change the write's target to each filed artefact's file instead of the closing unit's | a story closed over a REJECT names every filed artefact, in its own record |
| AC2 | in .claude/skills/sdlc-studio/scripts/transition.py, replace the critic.repair_state read with a test that the unit's latest verdict row is a REJECT, so the APPROVE the one-call close appends first suppresses the write | the one-call close names them too |
| AC3 | in .claude/skills/sdlc-studio/scripts/transition.py, add a story-type condition around the discharge write so a bug skips it | a bug names it at every delivered terminal |
| AC3 | in .claude/skills/sdlc-studio/scripts/transition.py, change the write's condition from `sdlc_md.is_delivered_terminal` to membership of `_TERMINAL_FOR_PLAN` (Done, Fixed), so Verified reached directly gets nothing | a bug names it at every delivered terminal |
| AC4 | in .claude/skills/sdlc-studio/scripts/transition.py, replace the _upsert_field call with _insert_after_status, so each terminal step adds another field line | a terminal walk writes the line once |
| AC5 | in .claude/skills/sdlc-studio/scripts/transition.py, call annotate for the Findings-filed-to field in cmd_set before transition() runs, mirroring the --depth stamp, so a close the ladder refuses keeps it | a refused close writes no line |
| AC6 | in .claude/skills/sdlc-studio/scripts/transition.py, remove the non-empty guard so the field is upserted with an empty value on every delivered-terminal close | an ordinary close writes no such line - paired with a close that does |
| AC6 | in .claude/skills/sdlc-studio/scripts/transition.py, replace each closure's `artefact` with its `ids` list, so a fixed: closure naming an id is written as a filing | an ordinary close writes no such line - paired with a close that does |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-15 | sdlc-studio | Retitled: was 'a story closed this way names the bug in its own record' |
| 2026-09-15 | sprint planning 2026-09-15 | Re-groomed at the sprint goal review (round 1: all three seats refused a goal carrying CR0526) against D0193 (an unfinished unit feeds the close's stop-ship step, not a third gate) and D0194 (one stop-ship store, the retro's carried table). A bug closed over a REJECT names its filed artefact too; the stop-ship-ruling criterion is gone with D0194. |
| 2026-09-15 | sprint plan repair 2026-09-15 | Plan review r1 repairs (QA REJECT). The discharge is one metadata line, `Findings-filed-to`, read in the closing unit's own file by one shared detector that matches the line whatever its value; fixtures name their filed ids in prose too, so a whole-file id search cannot pass. AC1 files two findings to two bugs (kills a closed[0]-only build and a write into the filed artefact). AC2 pins the one-call close, whose APPROVE lands before the transition, against a latest-row reader. AC3 adds Verified reached directly (kills a _TERMINAL_FOR_PLAN condition); AC4 pins exactly one line over Fixed -> Verified -> Closed; AC5 pins that a close refused by another gate leaves no line, with its landed control. AC6 is the paired control the review asked for: one fixture closed with a filed REJECT, with none, and with a fixed-only repair naming an id, all asserted landed. The old AC3 row (drop the REJECT condition) was equivalent under a write that loops over filed ids; it is replaced by an empty-value upsert and an ids-for-artefact swap, both killable. |
| 2026-09-15 | sprint plan repair 2026-09-15 | Re-sized 2 -> 3 points after the plan repair grew it from 3 criteria to 6. |
| 2026-09-15 | sprint plan repair 2026-09-15 | Plan round 2 repair: AC6 adds a mixed repair (one finding filed to BG0002, one fixed with evidence naming BG0004) whose line names BG0002 and not BG0004, so the artefact/ids swap mutant can be killed. |
