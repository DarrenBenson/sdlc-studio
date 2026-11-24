# BG1328: `artifact.py new --type story --epic <a Done epic>` leaves the epic Done, so its parent request derives Complete although the new story is Draft, and `refine apply` refuses to add the deferred slice of an already-decomposed request

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_refine.py, .claude/skills/sdlc-studio/reference-scripts-create.md, changelog.d/BG1328.md
> **Evidence:** RUN-01M7061X close: US1149, EP0302 and CR0670 (2026-11-09)
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-09T19:15:18Z

## Summary

Hit closing run nine (2026-11-09). CR0670 was refined into EP0302 for its first slice only (D0435). When US1140-US1142 were Done, reconcile derived EP0302 Done and CR0670 Complete, though CR0670's AC4 and AC5 were deferred. `refine apply --request CR0670 --into EP0302` refused ('already decomposed'), so US1149 was minted with `artifact.py new --epic EP0302`; EP0302 stayed Done and the next `reconcile apply` derived CR0670 Complete again. Both had to be moved back to In Progress by hand.

## Steps to Reproduce

1. Take a request decomposed into an epic whose stories are all Done (the epic derived Done).
2. Mint a Draft story into that epic with `artifact.py new --type story --epic <epic>`.
3. Run `reconcile apply`: the request derives Complete and the epic stays Done.

## Proposed Fix

Reopen a Done epic (and re-derive its parent) when a non-terminal story joins it, and let `refine apply --into` add a slice to an epic its request already decomposed into; pin both.

## Acceptance Criteria

- [ ] **AC1** Given an epic that is Done with every story Done, when `artifact.py new --type story --epic <epic>` mints a Draft story into it, then the epic's Status is no longer Done. Fails on: an epic reading Done over a story nobody has built.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::DoneEpicReopensTests::test_a_draft_story_minted_into_a_done_epic_reopens_it
- [ ] **AC2** Given that epic's parent request reading Complete, when the story is minted and `reconcile apply` then runs, then the request is In Progress and stays so. Fails on: the request derived Complete again while a slice of it is Draft.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::DoneEpicReopensTests::test_the_parent_request_is_not_derived_complete_after_the_mint
- [ ] **AC3** Given a request already decomposed into an epic, when `refine.py apply --request <request> --into <that epic>` gives a further slice, then the stories are minted into the epic, the request lists the epic once and a Done epic is reopened; `--into` an epic the request does not name is still refused as before. Fails on: 'already decomposed' leaving a hand mint as the only route.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::BreakdownFileTests::test_apply_into_an_epic_the_request_already_names_adds_the_slice

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
| 2026-11-24 | orchestrator (delegate under D0545) | Affects widened for run twenty-six's FA lane: refine apply --into now accepts an epic the request already names, so reference-scripts-create.md's 'a terminal target is refused' sentence changes with it |
