# US1030: critic.py brief with no --seat briefs the seat the unit calls for and says why

> **Status:** Draft
> **Delivers:** CR0620
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/reference-scripts-review.md, .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_derived_seat.py, changelog.d/US1030.md
> **Epic:** EP0284
> **Points:** 3
> **Depends on:** US1029, US1011
> **Persona:** Maya Okafor

## User Story

**As** a founder-engineer whose agent briefs a reviewer for every unit in a run
**I want** `critic.py brief --unit <id>` with no `--seat` to brief the seat `critic.py seats` derives, and to say in the brief why that seat was chosen
**So that** the seat is chosen by the command the run already calls, not by whatever the orchestrator typed

## Acceptance Criteria

- **AC1:** Given a story the project map gives to sre, when `critic.py brief --unit` runs with no `--seat`, then the brief opens as the sre review seat, names the sre card, and carries a line saying which Affects files chose it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_derived_seat.py::DerivedSeatBriefTests::test_brief_without_seat_briefs_the_derived_seat_and_says_why
- **AC2:** Given the same story, when `critic.py brief --unit --seat engineering` runs, then the brief is the engineering seat's and stderr names sre as the seat the unit's files call for
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_derived_seat.py::DerivedSeatBriefTests::test_an_explicit_seat_wins_and_the_derived_one_is_named
- **AC3:** Given a derived or an explicit seat, when the brief's footer prints the record command, then that command carries `--reviewer "<card holder> (<role>)"`, so the recorded row names its seat in the exact form the ledger reads
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_derived_seat.py::DerivedSeatBriefTests::test_the_footer_names_the_seat_as_reviewer

## Notes

- Release: 6.2 (D0355 breakdown G10, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: brief keeps --seat required, or defaults an absent --seat to engineering instead of calling seats_for
- AC2 must fail on: the derived seat overrides an explicit --seat, or the explicit path never consults seats_for
- AC3 must fail on: the footer omits --reviewer, or writes the role in free text, so the verdict is recorded as the default independent-critic with no seat
- Build after G6 story 1, which rewrites the same footer lines (critic.py:3118 and :3147) and changes the record command's shape; this story adds `--reviewer` to it. G12 story 3 also changes `brief()`: no order needed, the second to land rebases.
- `--rejoinder` keeps `--seat` required and says why when it is absent: a re-review goes to the seat that rejected, which the derivation cannot know.
- The why line is inside the fingerprinted brief; note_brief records the seat as derived or explicit beside the tier, as it already does for the tier.
- AC3's `(<role>)` group is the exact seat attribution the per-seat lanes story keys on and RFC0061's D4 spike scores from, so this story is built before both. It also removes the usual cause of the report's NO DECLARED SEAT label (BG0726).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G10 after the refine panel's review |
