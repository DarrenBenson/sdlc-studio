# US1050: A small change reaches its terminal status only on an independent approval at the derived depth while it still qualifies, and then owes no sprint close

> **Status:** Draft
> **Delivers:** CR0626
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/close_owed.py, .claude/skills/sdlc-studio/scripts/tests/test_small_change_terminal.py, changelog.d/US1050.md
> **Epic:** EP0286
> **Points:** 5
> **Depends on:** US1047, US1048
> **Persona:** Maya Okafor

## User Story

**As** a founder-engineer who skipped the run for a one-file fix
**I want** the fix to close only once someone other than its author approved it at the depth its risk asks for, while it is still a small change
**So that** the small path keeps the review and the boundary that catch defects, and leaves no standing debt behind it

## Acceptance Criteria

- **AC1:** Given a started small-change bug whose criteria pass and which has no delivery verdict, when `transition.py set --status Fixed` runs, then it exits non-zero naming `critic.py brief`, and the status is unchanged.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_small_change_terminal.py::SmallChangeTerminalTests::test_an_unreviewed_small_change_is_refused_its_terminal_status
- **AC2:** Given two started small-change bugs, one approved by its own author and one with an independent light-tier APPROVE whose risk band tiers full, when `transition.py set --status Fixed` runs on each, then each is refused, naming the self-review or the depth the band demands.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_small_change_terminal.py::SmallChangeTerminalTests::test_an_approval_that_does_not_cover_the_unit_is_refused
- **AC3:** Given a started small-change bug independently approved at its derived depth whose diff since its base now touches a second production file, when `transition.py set --status Fixed` runs, then it exits non-zero naming the check's reason and `sprint plan`, and the status is unchanged.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_small_change_terminal.py::SmallChangeTerminalTests::test_a_change_that_no_longer_qualifies_is_refused_its_terminal_status
- **AC4:** Given a started small-change bug that still qualifies and is independently approved at its derived depth, when it moves to Fixed and `close_owed.py detect` runs after a baseline, then detect exits 0 with nothing owed, and `status.py` prints no close-owed advisory for it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_small_change_terminal.py::SmallChangeTerminalTests::test_a_reviewed_small_change_owes_no_sprint_close
- **AC5:** Given a bug moved to Fixed outside any run without starting the small path, when `close_owed.py detect` runs after a baseline, then the bug is still owed.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_small_change_terminal.py::SmallChangeTerminalTests::test_a_runless_fix_off_the_path_still_owes_a_close

## Notes

- Release: 6.2 (D0355 breakdown G12, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the transition keeps today's rule, refusing only an unanswered REJECT, so a small change nobody reviewed reaches Fixed.
- AC2 must fail on: the gate asks `critic.coverage_state`, which discounts a self-review but not a shallow tier (critic.py:1971), so the light APPROVE passes; or the gate counts any APPROVE row. The test asserts each arm.
- AC3 must fail on: the transition reads the review only, so a started change that grew past the path's limits reaches Fixed and is excused its sprint close.
- AC4 must fail on: close_owed ignores the `Small-change` field, so the fix is reported as owing a retro forever.
- AC5 must fail on: close_owed excuses every unit no run held, which forgives the skipped close it exists to detect.
- Covered means `conformance.critiqued_unmet` reports nothing owed: an independent APPROVE (HALF_VERDICT) at the depth the band demands (HALF_TIER, through `verdict_half_ok` and `tier_covers`, conformance.py:351-440). `critic.coverage_state` alone does not check depth; the draft's claim that it did was wrong (panel change 1). The refusal names which half is owed.
- The boundary is held at the transition, not only at start (panel change 2, LL0027). The gate re-runs the check story's published predicate, minus the run-collision arms that only matter at start, and refuses a unit that no longer qualifies, naming `sprint plan`.
- Probed at HEAD: a bug with green criteria and no verdict reaches Fixed outside a run, and conformance is story-scoped ('a bug/CR tranche relies on the critic + gate'). Afterwards `close_owed.py detect` exits non-zero and `status.py` prints 'a sprint close is owed'.
- Scoped to units carrying the `Small-change` field, and to delivered terminals (`sdlc_md.is_delivered_terminal`), so a path unit can still be closed Won't Fix without a review. Projects that never use sprints keep today's transition.
- close_owed counts a terminal unit as accounted for when it carries the field, qualifies and is covered. The field alone accounts for nothing.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G12 after the refine panel's review |
