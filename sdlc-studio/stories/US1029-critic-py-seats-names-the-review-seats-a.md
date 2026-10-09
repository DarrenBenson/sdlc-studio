# US1029: critic.py seats names the review seats a unit's files and type call for, and why

> **Status:** Draft
> **Delivers:** CR0620
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/spec_guard.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/reference-scripts.md, .claude/skills/sdlc-studio/reference-scripts-review.md, .claude/skills/sdlc-studio/scripts/tests/test_critic_review_seats.py, changelog.d/US1029.md
> **Epic:** EP0284
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As** a founder-engineer whose project declares QA, product and SRE seats beside engineering
**I want** `critic.py seats --unit <id>` to name the seat a unit's own files and type call for, with the path or rule that chose it
**So that** an alerting change is reviewed by the seat that owns alerting, not by engineering because nobody chose otherwise

## Acceptance Criteria

- **AC1:** Given a story whose Affects are two test files and a changelog fragment, when `critic.py seats --unit` runs, then it names qa and says every file other than paperwork is a test
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_review_seats.py::ReviewSeatsTests::test_a_test_only_unit_names_qa_and_why
- **AC2:** Given a project map sending `monitoring/**` to sre and an sre card, when `critic.py seats` runs on a story touching one monitoring file, its test, a runbook doc and a changelog fragment, then it names sre, citing the glob and the file
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_review_seats.py::ReviewSeatsTests::test_one_mapped_file_outranks_the_type_default
- **AC3:** Given a bug and a story whose Affects match no mapped path and are not test-only, when `critic.py seats` runs on each, then the bug is given qa and the story engineering, each named as its type's default seat
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_review_seats.py::ReviewSeatsTests::test_the_type_default_seat_when_no_path_matches
- **AC4:** Given a project map naming a seat no card declares, when `critic.py seats` runs on a unit touching that path, then the output names the mapped seat as having no card, lists the seat roster, and gives the unit the seat the rule would give with that mapping absent
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_review_seats.py::ReviewSeatsTests::test_a_mapped_seat_with_no_card_is_named_not_dropped
- **AC5:** Given a project map listing `ui/**` to product before `monitoring/**` to sre, when `critic.py seats` runs on a story touching two monitoring files and one ui file, then sre is named first, product as also touched, and the output says one seat reviews the unit
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_review_seats.py::ReviewSeatsTests::test_most_mapped_files_first_and_one_seat_per_unit

## Notes

- Release: 6.2 (D0355 breakdown G10, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the test-only rule counts the changelog fragment as a non-test file, or tests are ignored, so the story is given engineering
- AC2 must fail on: unmapped files vote for the type default (the first draft's majority vote), so the test, doc and fragment outvote the monitoring file; or only the shipped settings are read, never the project map
- AC3 must fail on: one default seat (engineering) for every type, so the bug is not given qa
- AC4 must fail on: a mapped seat with no card is dropped without a message, so the operator never learns the mapping is dead
- AC5 must fail on: map order rather than file count decides between mapped seats, or the also-touched seat is offered as a second review
- Rule, as the panel answered: each Affects file a project glob matches votes for that glob's seat; unmapped files and paperwork never vote. Any vote beats the type default; among mapped seats the most files come first (ties by map order) and the rest are also touched. With no vote, the shipped test-only rule gives qa when at least one file is a test and every file other than paperwork is a test; otherwise the type default (bug qa, as help/bug.md already briefs; every other type engineering). A paperwork-only unit takes the type default, not qa.
- One owner each: test files by verify_ac.is_test_path, paperwork (changelog fragments, documentation, artefacts) by sprint_report.is_paperwork, lifted into lib/sdlc_md if critic should not import the report module.
- Config: `review.seat_paths: {role: [globs]}`, shipped empty with a commented example, so a project's map is the whole map and there is nothing to merge or replace; declared in config-defaults.yaml for test_config's review-key scan.
- Glob dialect: spec_guard's matcher (fnmatch, `*` crosses `/`, case-folded, path or basename), made public, as `review.spec_paths` already uses. reference-config.md names this key's dialect and G11's whole-segment TRD component dialect beside it.
- Cards resolve through persona_resolve.resolve_card, the resolver critic.brief uses, so a seat `seats` names is one `brief` can brief.
- Until per-seat lanes ship (CR0622), the output says one seat reviews the unit: at HEAD a second seat's REJECT is counted as round 2 and carries the unit to a false bug (fixture probe, confirmed by the panel).
- `--format json` emits [{seat, why, files}] for an orchestrator. Advice only: nothing gates on the derived seat (LL0056).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G10 after the refine panel's review |
