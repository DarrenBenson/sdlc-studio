# US1156: Each change in the pack states what is known wrong and names the accountable person, never the agent

> **Status:** Done
> **Delivers:** CR0692
> **Created:** 2026-11-14
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/evidence_pack.py, .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_build.py, .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_accountable.py, changelog.d/US1156.md, .claude/skills/sdlc-studio/reference-scripts.md
> **Epic:** EP0308
> **Points:** 2
> **Depends on:** US1155
> **Persona:** Abena Osei

## User Story

**As a** head of engineering whose teams take changes through a change board
**I want** each change in the pack states what is known wrong and names the accountable person, never the agent
**So that** every change names an accountable person, not 'the agent'

## Acceptance Criteria

- **AC1:** Given a signed report whose known-issues rows name open findings, when the pack is built, then each change lists the known issues that name it, and the pack carries the report's remaining known issues in one list.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_accountable.py::KnownWrongTests::test_known_issues_listed_per_change_and_for_the_release
  - **Verified:** yes (2026-11-15)
- **AC2:** Given a signed report, when the pack is built, then each change names the accountable person recorded on that report's signature, with the signing date.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_accountable.py::AccountableTests::test_each_change_names_the_signing_principal
  - **Verified:** yes (2026-11-15)
- **AC3:** Given a report whose signature principal is blank or reads as an agent (for example 'the agent' or 'agent-<id>'), when the pack is built, then the command exits non-zero and no pack names the agent as accountable.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_accountable.py::AccountableTests::test_agent_or_blank_principal_is_refused
  - **Verified:** yes (2026-11-15)

## Notes

- Serves Abena Osei's End goal 2; delivers part of CR0692 (D0476).
- AC1 must fail on: Known issues dropped from the pack; every issue attached to every change; a unit with none shown blank instead of 'none recorded'.
- AC2 must fail on: The verdict's author or reviewer id shown as accountable; the principal left out; the date missing.
- AC3 must fail on: A pack written with 'the agent' or a blank accountable cell; a refusal that still leaves the pack on disk; a human principal named 'Agnes' refused by an over-broad match (positive control).
- Same file as the first story `(scripts/evidence_pack.py`): build after it.
- Known issues live in the signed report's `'known_issues'` section rows `(issue_id`, `issue_priority`, `issue_detail`; RPT0030.json shows them) built by `scripts/sprint_report.py:4311` `_known_issues_section`; the run's `close_known_issues` `(lib/run_state.py:2853`) holds gaps the close could not settle. The brief named `scripts/known_issues.py`: it does not exist.
- No per-unit accountable field exists anywhere: the only accountable person recorded is the run's signature principal (sprint.py:10300 `_principal_refusals` shows who may sign). Use it for every unit of that report; say so in the story and the pack footer.
- Per-change attribution of an issue: match the unit id in `issue_id` or `issue_detail`; anything unmatched goes in the release-level list, so nothing known is lost.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-14 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-14 | Claude Opus 5.5 (run twelve grooming, D0476) | Groomed: criteria with Verify lines, must-fail notes, Affects with the tests each change exercises and this unit's fragment |
