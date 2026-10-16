# CR-0642: Prevent or retire lesson LC-016 (a signed page reads a live source)

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** sdlc-studio/lessons.jsonl
> **Date:** 2026-10-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M4R168 close, 2026-10-16T08:11:24Z

## Summary

The failure class LC-016 (a signed page reads a live source) recurred 2 time(s) after it was recorded in RUN-01M3Y7DP, while its rule was injected into the work. A rule that is read and repeated anyway needs the path it fails on fixed, not another reading and not one more check. This CR carries the class and its evidence, not a design.

Rule: A figure on a signed page is derived only from what PREPARE froze, and a step judging the attempt in progress asks the live source, never the last attempt's freeze.

Behaviour asked of the agent: BG0890 read a unit's live status after filing, and BG0895's checklist read the previous attempt's frozen gate on a re-close.

Hits:

- RUN-01M3ZAGE on BG0911 (critic:RUN-01M3ZAGE): the AC1 test docstring claims it kills "a check that reads the note against a live re-derivation rather than the filed page" but that mutant SURVIVES - swapping `read_report` for `sprint_report.build_report(str(root)`, args.retro) in `goal_note_contradiction` (sprint.py:9337, applied and asserted in an isolated copy) leaves both tests green because the fixture's live and filed pages both derive 1.69x, so the filed-page property the changelog and docstring state ("Read off the page as filed", `test_lean_goal_note_matches_page.py`:66-67) is unpinned and the claim is FALSE [LC-016]
- RUN-01M4R168 on BG1025 (critic:RUN-01M4R168): sign reads the carried rows from the latest retro whose text names the run id, not from the retro the close named and the filed page records as its `retro_id`, and drops the unreadable reason unprinted (`_carried_rulings(Path(root), state, None)` and `_unread` at sprint.py:6171): executed, a run closed with `--retro RETRO0001` whose retro carries BG0101 but whose Run line does not name the run (the `Run: -` that `artifact.py new --type retro` writes, the route the close's own missing-retro refusal names) signs with `sign: BG0101 -> Fixed` and no warning, and an untracked RETRO0002 naming the run, added after the close and so not counted by `tree_moved_since_close`, displaces RETRO0001 the same way, so AC1 fails on both inputs while D0367 withdrew the correction route on the premise that AC1 holds, and changelog.d/BG1025.md:3, help/sprint.md:113 and the comment at sprint.py:6168-6170 over-claim accordingly (the AC1 test passes only because its fixture injects a `Run:` line, `test_sign_respects_carried_units.py`:38-40) [LC-016]

## Impact

Every lane and review the class reaches: each repeat of LC-016 has cost a review round, 2 so far.

## Acceptance Criteria

- [ ] The code path each recorded hit names (its finding is under Hits above) is fixed, so the failure LC-016 describes cannot recur there: RUN-01M3ZAGE on BG0911; RUN-01M4R168 on BG1025.
- [ ] Any check this CR proposes names the lane, refusal, baseline or pin it retires, and ships only in exchange for it; a check that retires nothing is not added.
- [ ] Once the path is fixed and this CR closes Complete, LC-016 reads `graduated` in sdlc-studio/lessons.jsonl; a class that no longer describes a live failure is Rejected here instead, and the close then retires it until it recurs.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-16 | sdlc-studio | Raised |
