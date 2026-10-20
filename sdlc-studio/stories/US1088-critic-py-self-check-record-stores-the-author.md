# US1088: critic.py self-check record stores the author's claim inventory, every claim ruled, and the mutation run the unit's tests were checked against, bound to the unit's diff

> **Status:** Ready
> **Delivers:** CR0650
> **Created:** 2026-10-20
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_record.py, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/help/review.md, changelog.d/US1088.md
> **Epic:** EP0291
> **Points:** 3
> **Depends on:** US1087
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, who has run her own claim inventory and mutation pass on a unit
**I want** `critic.py self-check record` to record both, bound to the content of the unit's Affects as it stands
**So that** the brief can tell a self-check of this diff from no self-check, or from one of an earlier diff

## Acceptance Criteria

- **AC1:** Given a claims file in which every claim is ruled TRUE, FALSE or UNVERIFIABLE, when `critic.py self-check record --unit <id> --claims <file> --mutants <file>` runs, then the record is written; given a claim with no ruling, or a ruling outside those three, then it is refused naming that claim and nothing is written
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_record.py::SelfCheckRecordTests::test_an_unruled_claim_is_refused
- **AC2:** Given a unit whose `changelog.d/<id>.md` exists, when the claims file holds no claim taken from that fragment, then the record is refused naming the fragment
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_record.py::SelfCheckRecordTests::test_a_claims_file_skipping_the_fragment_is_refused
- **AC3:** Given a mutants file, when it lists no mutant, or a mutant with no test or no result of killed or survived, or a survivor with no answer, then the record is refused naming the entry; given one listing each mutant's test and result, with every survivor answered, then it is recorded
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_record.py::SelfCheckRecordTests::test_an_unanswered_survivor_is_refused
- **AC4:** Given a recorded self-check, when the committed log `sdlc-studio/reviews/author-self-checks.md` is read, then its row names the unit, the author, the date, the claim counts by ruling, the mutant counts by result, and a digest of the unit's Affects content; and after an edit to one Affects file the digest the record command would compute differs
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_record.py::SelfCheckRecordTests::test_the_record_binds_the_affects_content
- **AC5:** Given US1087's author self-check section, when the brief prints it, then it names the `critic.py self-check record` command for the unit
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_record.py::SelfCheckRecordTests::test_the_brief_names_the_record_command

## Notes

- Serves: Maya Okafor, End goal 3.
- Delivers CR0650's record half of part (3) (D0382). The operator chose a self-reported record knowing US0936 retired the mutation ledger and that a record is satisfied by touch (LL0023); the content checks above are what keeps it from being an empty file.
- AC1 must fail on: `validate_claim_inventory` not called, so an unruled claim is recorded as TRUE.
- AC2 must fail on: the fragment check dropped, so a claims file of the commit message alone is recorded.
- AC3 must fail on: a survivor recorded with no answer.
- AC4 must fail on: the digest computed over the Affects paths rather than their content, so an edit leaves it unchanged.
- AC5 must fail on: the brief's section printing no record command.
- Depends on US1087, which prints the section AC5 extends. The log is committed, never under `.local` (LL0029).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-20 | sdlc-studio | Created via `new` (deterministic) |
