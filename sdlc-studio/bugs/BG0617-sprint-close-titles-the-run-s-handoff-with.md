# BG0617: sprint close titles the run's handoff with the run's GOAL, so a run that missed its goal ships a handoff asserting it

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/handoff.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_handoff.py
> **Evidence:** RUN-01M0WCCG close, 2026-08-25. Title source quoted from sprint.py:5238 and the outcome derivation from the three lines below it. HO0063 was hand-retitled and its pick-up section rewritten in commit f48c8e7c, which is the workaround this bug exists to remove.
> **Created:** 2026-08-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`_close_handoff` takes the handoff title straight from the run's stated goal - `title = state.get("sprint_goal") or state.get("run_id") or "sprint close"` at sprint.py:5238 - and passes it to `handoff.main` as `--title`. The very NEXT lines derive the outcome honestly from the recorded goal-verdict, with a comment saying so: only an achieved goal closes `goal-reached`, and partial or missed close as `stopped`. So at the moment the title is chosen the code is about to establish that the goal was not met, and titles the artefact with it anyway. Measured on RUN-01M0WCCG, closed `partial` on 2026-08-25: the minted handoff was titled `HO-0063: The v5 release bar reaches zero open High: the twelve bugs open at run-open reach a terminal status...`, which is the single claim that run disproved, while its own Outcome field two lines below read `stopped`. The generated `Where to pick up` section said `Every unit in the batch is terminal. There is no tail: close the run and plan the next batch normally`, and named neither the withdrawn unit nor the open High that had just been re-raised.

## Steps to Reproduce

1. Open a run with a goal stated as an achievement. 2. Record a goal-verdict of `partial` or `missed` with `sprint.py goal-verdict`. 3. Run `sprint.py close --retro RETROxxxx`. 4. Read the minted handoff: its H1, its filename slug and its index row all assert the goal, while its Outcome field says stopped. Measured on RUN-01M0WCCG / HO0063, 2026-08-25.

## Proposed Fix

Title the handoff from the OUTCOME, not the ambition. The verdict is already computed a few lines down, so the title can be derived rather than borrowed - a goal-reached run may keep the goal as its title, and a partial or missed one needs a title that does not assert what the verdict just denied. The `Where to pick up` section has the same gap and the same fix available to it: the run state holds the goal-verdict note and the batch changes, so a dropped unit and the reason it was dropped can be named there instead of the current unconditional `plan the next batch normally`.

## Acceptance Criteria

- [ ] **AC1** Given a run closing PARTIAL or MISSED, when the handoff is minted, then its title states the OUTCOME and does not assert the goal the verdict just denied
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::HandoffTitleTests::test_a_missed_run_is_not_titled_with_its_goal
- [ ] **AC2** Given a run closing GOAL-REACHED, when the handoff is minted, then it may carry the goal - the paired control, because the claim is true there and the fix is about honesty rather than about never naming a goal
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::HandoffTitleTests::test_a_goal_reached_run_may_keep_its_goal
- [ ] **AC3** Given a run that dropped a unit or left one open, when the `Where to pick up` section is generated, then it NAMES that unit - the section currently says to plan the next batch normally whatever happened
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::HandoffTitleTests::test_the_pickup_section_names_what_did_not_land

## Impact

The handoff is what a fresh session reads to pick up a run it did not work on, and it is indexed by that title. A partial run therefore hands its successor a document whose title, slug and index row all state the opposite of what happened, and whose guidance omits the very unit that did not land. This one had to be retitled and rewritten by hand at the close, which is the outcome the deterministic writers exist to prevent.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-26 | sdlc-studio | Filed |
