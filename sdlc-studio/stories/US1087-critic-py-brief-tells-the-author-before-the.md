# US1087: critic.py brief tells the author, before the brief, to run a claim inventory of the commit message and changelog fragment and a mutation pass over the unit's own tests

> **Status:** Ready
> **Delivers:** CR0650
> **Created:** 2026-10-20
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_author_self_check.py, changelog.d/US1087.md
> **Epic:** EP0291
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, handing a unit she built to an independent reviewer
**I want** `critic.py brief` to tell me, before the brief, the self-check to run on my own work: a claim inventory of my commit message and changelog fragment, and a mutation pass over my own tests, worded from the practices the reviewer is given
**So that** the review confirms my work rather than finding what my own pass would have found, and the batch reaches done in fewer rounds

## Acceptance Criteria

- **AC1:** Given a unit, when `critic.py brief --unit <id> --seat <seat>` runs, then stderr carries an author self-check section and stdout carries none of its lines, and the brief's fingerprint is the one `critic.brief()` gives for the same unit and seat
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_author_self_check.py::AuthorStepsTests::test_the_steps_go_to_stderr_and_the_brief_is_unchanged
- **AC2:** Given a unit, when the brief runs, then the section names as claim-inventory surfaces the commit message, each prose surface the brief's own claim inventory names (`CLAIM_SURFACES`), and each changelog fragment the unit's Affects declares (read from its Affects, never from its id), and names each test file its Affects declares as a mutation-pass target; given Affects declaring no test file or no fragment, it says so
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_author_self_check.py::AuthorStepsTests::test_the_steps_name_the_units_surfaces_and_tests
- **AC3:** Given the brief's claim-inventory text and its practice to mutate the author's tests, when either text is changed in-process, then the section's instruction changes with it, because it is derived from those texts and not restated
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_author_self_check.py::AuthorStepsTests::test_the_steps_derive_from_the_briefs_practices

## Notes

- Serves: Maya Okafor, End goal 3 (drive a batch to done, pausing only for her decisions). Its measure is the run's first-round approval rate on the units briefed after US1089, read at the close against RETRO0135's 1 of 10; no criterion can guarantee it.
- Delivers CR0650 part (2) (D0382).
- AC1 must fail on: the section printed to stdout, inside the brief a reviewer reads from a file.
- AC2 must fail on: the fragment taken as `changelog.d/<id>.md`, which misses a carried bug's fragment (BG1078 declares `changelog.d/US1076.md`); the surfaces typed rather than read from `CLAIM_SURFACES`.
- AC3 must fail on: the section's instruction typed beside `_CLAIM_INVENTORY_BLOCK` and the `mutate the author's TESTS` practice rather than read from them (LL0042).
- The section goes before the tier and fingerprint footer `cmd_brief` already prints on stderr, on the first-round and the `--rejoinder` path. Goal review, 2026-10-21 (engineering, product and qa seats) made AC2 read fragments from Affects and name every claim surface.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-20 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-21 | Claude Opus 5.5 | Regroomed on the run-three goal review's two rounds (engineering, product and qa seats; D0384) |
| 2026-10-22 | sdlc | Correction (its round-1 QA review, 2026-10-22): 0f7acbbd's D0386 paragraph names tree cd6eb093, the tree of its worktree original d1a62be6; the cherry-pick on main has tree 77024ef4, proven only within the next push tip |
| 2026-10-22 | sdlc | Correction (round-2 QA review, 2026-10-22): 11e0d5cf's body says the suite was green 'for this tree (3228385a)', the pre-rebase tree; its D0386 paragraph names the landed tree fa03a4d5, which devserver1 proved green |
