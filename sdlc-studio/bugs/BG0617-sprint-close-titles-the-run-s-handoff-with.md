# BG0617: sprint close titles the run's handoff with the run's GOAL, so a run that missed its goal ships a handoff asserting it

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/handoff.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_handoff.py
> **Evidence:** RUN-01M0WCCG close, 2026-08-25. Title source quoted from sprint.py:5238 and the outcome derivation from the three lines below it. HO0063 was hand-retitled and its pick-up section rewritten in commit f48c8e7c, which is the workaround this bug exists to remove.
> **Verification depth:** functional [[derived: criteria 4; plan rows 4; executed 4; killed 4; survived 0; not-run 0; entry point 0 of 4 criteria through the shipped CLI, 4 in-process | fp 81eb122393d9 ]] (four criteria, every mutant applied to the real file with bytecode purged and the tree restored. Entry point reads 0 of 4 and that is stated rather than dressed up: AC1 and AC2 drive `_close_handoff` through the real module with the CLI shim stubbed, and AC3 and AC4 drive `_pickup_body` and `generate` - reaching them through `sprint.py close` needs a whole run fixture that would not exercise the title choice differently. AC4 was rewritten once during delivery for exactly this reason: it first called `artifact.meta_new` directly, and its mutant survived because the test bypassed the wiring the criterion exists to pin. AC1 and AC4 are structurally coupled - one title string reaches all three surfaces - so AC4 is an oracle over two surfaces the H1 assertion never reads rather than an independent kill.)
> **Created:** 2026-08-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`_close_handoff` takes the handoff title straight from the run's stated goal - `title = state.get("sprint_goal") or state.get("run_id") or "sprint close"` at sprint.py:5238 - and passes it to `handoff.main` as `--title`. The very NEXT lines derive the outcome honestly from the recorded goal-verdict, with a comment saying so: only an achieved goal closes `goal-reached`, and partial or missed close as `stopped`. So at the moment the title is chosen the code is about to establish that the goal was not met, and titles the artefact with it anyway. Measured on RUN-01M0WCCG, closed `partial` on 2026-08-25: the minted handoff was titled `HO-0063: The v5 release bar reaches zero open High: the twelve bugs open at run-open reach a terminal status...`, which is the single claim that run disproved, while its own Outcome field two lines below read `stopped`. The generated `Where to pick up` section said `Every unit in the batch is terminal. There is no tail: close the run and plan the next batch normally`, and named neither the withdrawn unit nor the open High that had just been re-raised.

## Steps to Reproduce

1. Open a run with a goal stated as an achievement. 2. Record a goal-verdict of `partial` or `missed` with `sprint.py goal-verdict`. 3. Run `sprint.py close --retro RETROxxxx`. 4. Read the minted handoff: its H1, its filename slug and its index row all assert the goal, while its Outcome field says stopped. Measured on RUN-01M0WCCG / HO0063, 2026-08-25.

## Proposed Fix

Title the handoff from the OUTCOME, not the ambition. The verdict is already AVAILABLE at title time - `_close_handoff` reads it out of the `state` dict it was handed, at `sprint.py`:5241, and `record_goal_verdict` wrote it long before. An earlier draft of this bug said it was "computed a few lines down"; a review measured that and it is false, which matters because it made the ordering the defect when the defect is simply that line 5237 never consults it. So the title can be derived rather than borrowed - a goal-reached run may keep the goal as its title, and a partial or missed one needs a title that does not assert what the verdict just denied. The `Where to pick up` section has the same gap, in `handoff.py::_pickup_body` rather than in `sprint.py`: the run state holds the goal-verdict note and the batch changes, so a dropped unit and the reason it was dropped can be named there instead of the current unconditional `plan the next batch normally`.

## Acceptance Criteria

- [x] **AC1** Given a run closing PARTIAL or MISSED, when the handoff is minted, then its title states the OUTCOME and does not assert the goal the verdict just denied - the title is composed at `sprint.py`:5238, which reads `sprint_goal` unconditionally while the verdict sits in the same `state` dict three lines below
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::HandoffTitleTests::test_a_partial_close_does_not_title_the_handoff_with_the_goal
  - **Verified:** yes (2026-08-28)
- [x] **AC2** Given a run closing GOAL-REACHED, when the handoff is minted, then its title DOES carry the goal - not "may", which every behaviour satisfies including the over-correction this row exists to catch. The claim is true there and the title is the one place it can be made
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::HandoffTitleTests::test_a_goal_reached_close_still_titles_from_the_goal
  - **Verified:** yes (2026-08-28)
- [x] **AC3** Given a run that DROPPED a unit, when the `Where to pick up` SECTION is generated, then it names that unit. The assertion is scoped to that section on purpose: `render_body` already emits a `Closed without delivery` section naming dropped units, so an unscoped test is green at HEAD and pins nothing
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_handoff.py::HandoffTitleTests::test_the_pick_up_section_names_a_dropped_unit
  - **Verified:** yes (2026-08-28)
- [x] **AC4** Given a run closing PARTIAL, when the handoff is minted, then its filename SLUG and its `_index.md` row do NOT contain the goal string, and both carry the outcome-derived title. Asserting they match the H1 is not an oracle: `handoff.py`:662 passes ONE title to `artifact.meta_new` and all three surfaces derive from it, so they agree at HEAD and after any fix. The Impact names three lying surfaces and the slug is derived from the title through `artifact.meta_new`, so a fix that changes the rendered heading alone leaves two of the three asserting the denied goal
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_handoff.py::HandoffTitleTests::test_the_slug_and_the_index_row_do_not_carry_the_denied_goal
  - **Verified:** yes (2026-08-28)

## Impact

The handoff is what a fresh session reads to pick up a run it did not work on, and it is indexed by that title. A partial run therefore hands its successor a document whose title, slug and index row all state the opposite of what happened, and whose guidance omits the very unit that did not land. This one had to be retitled and rewritten by hand at the close, which is the outcome the deterministic writers exist to prevent.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `.claude/skills/sdlc-studio/scripts/sprint.py`, derive the title from the outcome only when the verdict is `missed`, so a `partial` close still borrows the goal - the narrowing the `verdict == "achieved"` test four lines below invites, and `partial` is the case this run's predecessor actually hit | Given a run closing PARTIAL or MISSED, when the handoff is minted, then its title states the OUTCOME and does not assert the goal the verdict just denied - the title is composed at `sprint.py`:5238, which reads `sprint_goal` unconditionally while the verdict sits in the same `state` dict three lines below |
| AC2 | in `.claude/skills/sdlc-studio/scripts/sprint.py`, replace the goal-or-outcome choice with the outcome alone, so a goal-reached run loses the claim that is true of it | Given a run closing GOAL-REACHED, when the handoff is minted, then its title DOES carry the goal - not "may", which every behaviour satisfies including the over-correction this row exists to catch. The claim is true there and the title is the one place it can be made |
| AC3 | in `.claude/skills/sdlc-studio/scripts/handoff.py`, restore `_pickup_body`'s unconditional line for a report whose remaining set is empty, so a run that dropped a unit still reads `plan the next batch normally` | Given a run that DROPPED a unit, when the `Where to pick up` SECTION is generated, then it names that unit. The assertion is scoped to that section on purpose: `render_body` already emits a `Closed without delivery` section naming dropped units, so an unscoped test is green at HEAD and pins nothing |
| AC4 | in `.claude/skills/sdlc-studio/scripts/sprint.py`, keep passing the run's GOAL as `--title` and correct only the prose `handoff.py::render_body` puts in the body, so the heading, the filename slug and the index row all still assert the goal - the careless fix that patches the visible text and leaves the title argument alone | Given a run closing PARTIAL, when the handoff is minted, then its filename SLUG and its `_index.md` row do NOT contain the goal string, and both carry the outcome-derived title. Asserting they match the H1 is not an oracle: `handoff.py`:662 passes ONE title to `artifact.meta_new` and all three surfaces derive from it, so they agree at HEAD and after any fix. The Impact names three lying surfaces and the slug is derived from the title through `artifact.meta_new`, so a fix that changes the rendered heading alone leaves two of the three asserting the denied goal |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-26 | sdlc-studio | Filed |
