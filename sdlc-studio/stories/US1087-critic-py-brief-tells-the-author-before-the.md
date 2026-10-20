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

- **AC1:** Given a unit with a changelog fragment, when `critic.py brief --unit <id> --seat <seat>` runs, then stderr carries an author self-check section and stdout carries none of its lines, and the brief's fingerprint is the one `critic.brief()` gives for the same unit and seat
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_author_self_check.py::AuthorStepsTests::test_the_steps_go_to_stderr_and_the_brief_is_unchanged
- **AC2:** Given a unit whose Affects declares test files, when the brief runs, then the section names `changelog.d/<id>.md` and the commit message as the claim-inventory surfaces and each declared test file as a mutation-pass target; given a unit whose Affects declares no test file, then the section says it declares none
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_author_self_check.py::AuthorStepsTests::test_the_steps_name_the_units_surfaces_and_tests
- **AC3:** Given the brief's claim-inventory text and its practice to mutate the author's tests, when either text is changed in-process, then the section's instruction changes with it, because it is derived from those texts and not restated
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_author_self_check.py::AuthorStepsTests::test_the_steps_derive_from_the_briefs_practices

## Notes

- Serves: Maya Okafor, End goal 3 (drive a batch to done, pausing only for her decisions): fewer review rounds a unit.
- Delivers CR0650 part (2) (D0382).
- AC1 must fail on: the section printed to stdout, inside the brief a reviewer reads from a file.
- AC2 must fail on: the mutation targets taken from every test in the repository, or from none, instead of the unit's declared Affects.
- AC3 must fail on: the section's instruction typed beside `_CLAIM_INVENTORY_BLOCK` and the `mutate the author's TESTS` practice rather than read from them (LL0042).
- The brief already prints its tier and fingerprint footer on stderr (critic.py `cmd_brief`); the section goes before that footer, on both the first-round and the `--rejoinder` path.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-20 | sdlc-studio | Created via `new` (deterministic) |
