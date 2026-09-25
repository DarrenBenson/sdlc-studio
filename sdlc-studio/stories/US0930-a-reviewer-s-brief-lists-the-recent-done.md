# US0930: A reviewer's brief lists the recent Done units that changed each file the unit touches, with the defects their reviews found

> **Status:** Done
> **Delivers:** CR0594
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_file_history.py, changelog.d/US0930.md
> **Epic:** EP0264
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As** Maya Okafor, paying for every review round a unit takes
**I want** each reviewer briefed on the recent delivered units that changed the same files and the defects their reviews caught
**So that** a review looks first for the repeats the record already holds, instead of an agent rediscovering them round after round - End goal 3, "Drive a whole batch of work to "done" autonomously, pausing only when a decision is genuinely hers"

## Acceptance Criteria

- **AC1:** Given a fixture with five Done stories declaring `src/a.py` in `Affects`, whose latest Revision History dates run in a different order from their ids, when `critic.py brief --unit <open unit affecting src/a.py> --seat qa` runs, then a "History of the files this unit touches" section lists the three most recent by that date, newest first; an implementation ordering by id, oldest first, or listing all five fails it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_file_history.py::FileHistoryTests::test_the_three_most_recent_done_units_per_file_are_listed
  - **Verified:** yes (2026-09-25)
- **AC2:** Given one of those units carries REJECT rows in `sdlc-studio/reviews/critic-verdicts.md`, then its entry carries at most three of its blocking findings (items marked non-blocking or `[pre-existing]` are skipped), each cut to 200 characters with any lesson class code such as `[LC-002]` kept, and a unit with no REJECT reads "no review findings recorded"; an implementation that pastes the whole Issues cell fails it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_file_history.py::FileHistoryTests::test_each_entry_carries_at_most_three_blocking_findings
  - **Verified:** yes (2026-09-25)
- **AC3:** Given a unit whose `Affects` names twenty files each changed by many Done units, then the section lists at most five prior units, ranked by how many of this unit's files each changed and then by recency, and test modules and `changelog.d/` fragments are not matched on; concatenating a list per file, which reached 26-29 units for the widest Sprint 3 units, fails it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_file_history.py::FileHistoryTests::test_the_section_is_bounded_to_five_units
  - **Verified:** yes (2026-09-25)
- **AC4:** Given the unit itself, open units, and Superseded, Won't Implement, Won't Fix or Closed units that declare the same file, then none is listed - only Done stories and Fixed or Verified bugs changed the code - and given no qualifying unit or no verdict ledger at all, the section reads "none recorded" in one line and the brief is still produced; counting every terminal status fails it (the 2026-09-24 sweep alone closed 197 items without building them)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_file_history.py::FileHistoryTests::test_only_units_that_changed_code_are_listed
  - **Verified:** yes (2026-09-25)
- **AC5:** Given the corpus walk is shared with reconcile's already-delivered matcher, when `reconcile.py detect` runs on a fixture holding a skeleton that a Done unit already delivered, then the already-delivered advisory reports that pair exactly as before; a refactor that drops or changes the advisory fails it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_file_history.py::FileHistoryTests::test_the_already_delivered_advisory_is_unchanged
  - **Verified:** yes (2026-09-25)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-25 | Product seat | Groomed from CR0594's refinement: user story and criteria authored |
