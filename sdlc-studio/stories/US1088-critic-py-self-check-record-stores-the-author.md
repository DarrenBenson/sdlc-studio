# US1088: critic.py self-check record stores the author's claim inventory, every claim ruled, and the mutation run the unit's tests were checked against, bound to the unit's diff

> **Status:** Ready
> **Delivers:** CR0650
> **Created:** 2026-10-20
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_record.py, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/help/review.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/sprint_report.py, changelog.d/US1088.md
> **Epic:** EP0291
> **Points:** 3
> **Depends on:** US1087
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, who has run her own claim inventory and mutation pass on a unit
**I want** `critic.py self-check record` to record both, bound to the content of the unit's Affects as it stands
**So that** the brief can tell a self-check of this diff from no self-check, or from one of an earlier diff

## Acceptance Criteria

- **AC1:** Given a claims file in which every claim is ruled TRUE or UNVERIFIABLE and at least one is TRUE, when `critic.py self-check record --unit <id> --claims <file> --mutants <file>` runs, then the record is written; given a claim with no ruling, a ruling outside TRUE, FALSE and UNVERIFIABLE, a claim ruled FALSE (the author corrects it before review), or an inventory ruled entirely UNVERIFIABLE (which `summarise_claim_pass` reads as checking nothing), then it is refused naming the cause and nothing is written
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_record.py::SelfCheckRecordTests::test_an_unruled_false_or_unchecked_inventory_is_refused
- **AC2:** Given a unit whose Affects declares changelog fragments, when the claims file names no claim on the commit message, or none from one of those fragments, then the record is refused naming the surface it skipped
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_record.py::SelfCheckRecordTests::test_a_claims_file_skipping_a_surface_is_refused
- **AC3:** Given a mutants file, when it lists no mutant, a mutant whose test is not in a test file the unit's Affects declares, a mutant with no result of killed or survived, or a survivor with no answer, then the record is refused naming the entry; given one listing each mutant against a declared test with its result, every survivor answered, then it is recorded; given a unit whose Affects declares no test file, an empty mutants list is recorded and the row says no test was declared
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_record.py::SelfCheckRecordTests::test_an_undeclared_test_or_unanswered_survivor_is_refused
- **AC4:** Given a recorded self-check, when the committed log `sdlc-studio/reviews/author-self-checks.md` is read, then its row names the unit, the author, the date, the claim counts by ruling, the mutant counts by result, and a digest of the content of the unit's Affects files; after an edit to one Affects file, the digest the command computes differs
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_record.py::SelfCheckRecordTests::test_the_record_binds_the_affects_content
- **AC5:** Given US1087's author self-check section, when the brief prints it, then it names the `critic.py self-check record` command for the unit
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_record.py::SelfCheckRecordTests::test_the_brief_names_the_record_command

## Notes

- Serves: Maya Okafor, End goal 3.
- Delivers CR0650's record half of part (3) (D0382). The operator chose a self-reported record knowing US0936 retired the mutation ledger and that a record is satisfied by touch (LL0023); the content checks above are what keeps it from being an empty file.
- AC1 must fail on: `validate_claim_inventory` not called; the all-UNVERIFIABLE check dropped; a FALSE ruling recorded.
- AC2 must fail on: the fragment found by id rather than read from Affects; the commit-message surface not required.
- AC3 must fail on: a mutant against a test the unit does not declare recorded; a survivor recorded with no answer; a docs-only unit refused for having no mutant, which would leave it unbriefable under `block`.
- The commit message and each declared fragment are required surfaces. Docstrings and comments are named and optional: no command can tell which claims a diff's docstrings make, so the author labels each claim's surface (Goal review amendment round, 2026-10-21).
- AC4 must fail on: the digest computed over the Affects paths rather than their content.
- AC5 must fail on: the brief's section printing no record command.
- The new verb changes the generated `reference-scripts-surface.md`, which `test_lean_mutation_ledger_retired.py` reads, so it is regenerated in the same commit. Depends on US1087. The log is committed, never under `.local` (LL0029). Goal review, 2026-10-21 (engineering, product and qa seats) added the all-UNVERIFIABLE refusal, the declared-test binding and the surface rule.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-20 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-21 | Claude Opus 5.5 | Regroomed on the run-three goal review's two rounds (engineering, product and qa seats; D0384) |
| 2026-10-22 | sdlc | Affects gains scripts/`sprint_report.py`: the new critic.py self-check verb is mechanics, declared in `NON_CEREMONY_VERBS` beside brief, so the cycle-drift guard covers it; US1089's brief refusal is its gate, so no checklist row |
