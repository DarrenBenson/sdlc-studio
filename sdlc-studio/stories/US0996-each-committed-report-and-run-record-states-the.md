# US0996: Each committed report and run record states the evidence-schema version it was written under

> **Status:** Draft
> **Delivers:** CR0609
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-evidence-schema.md, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_evidence_schema_stamp.py, changelog.d/US0996.md
> **Epic:** EP0275
> **Points:** 2
> **Depends on:** US0992
> **Persona:** Maya Okafor

## User Story

**As** a team lead upgrading the skill under a dashboard that reads our evidence
**I want** every newly filed report and run record to carry the annex version its page was written under, and the annex to state how that version moves
**So that** my reader pins a major version from the committed files alone and knows a major bump arrives with a migration note

## Acceptance Criteria

- **AC1:** Given a run closed and signed through `sprint close` and `sprint sign` and committed, when a fresh clone reads the filed report JSON and the tracked run record, then each carries `evidence_schema` equal to the version the annex masthead states.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_schema_stamp.py::EvidenceSchemaStampTests::test_report_and_run_record_carry_the_annex_version
- **AC2:** Given a run closed while the annex version is 1.0 and signed after the version moves to 1.1, when the sealed run record is read, then it carries 1.0, the version its page was stamped with.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_schema_stamp.py::EvidenceSchemaStampTests::test_the_record_keeps_its_pages_version_across_an_upgrade
- **AC3:** Given a signed page filed before the stamp and a page filed after it, when `sprint_report check` runs on each, then both read VALID and only the later page carries `evidence_schema`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_schema_stamp.py::EvidenceSchemaStampTests::test_an_unstamped_page_still_checks_valid
- **AC4:** Given the annex's compatibility policy, when the test reads it, then the masthead version parses as major.minor and the policy states that an added field is a minor bump, a removed or renamed field is a major bump carrying a migration note in the annex, and a consumer must tolerate unknown keys.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_schema_stamp.py::EvidenceSchemaStampTests::test_the_annex_states_its_compatibility_policy

## Notes

- Release: 6.2 (D0355 breakdown G1, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: stamping a constant the annex masthead does not state, or stamping the report but not the run record
- AC2 must fail on: file_tracked stamping the signer's current constant, so one run carries two versions
- AC3 must fail on: putting the stamp in the figure set, which moves every earlier fingerprint
- AC4 must fail on: deleting the policy section, or a masthead version the stamp cannot be compared with
- Serves Jonah's End goal 4 (jonah-reyes-team-lead.md:29).
- Stamped on each newly filed report and run record only (panel answer to Q1); the annex records the known limit that a project with ledgers but no closed sprint has no stamp to read.
- The stamp is an envelope key outside the fingerprint, like the rule marks. The close stamps the page; the run record copies the page's stamp when the close files it and keeps it at the sign (run_state.file_tracked, run_state.py:540).
- Distinct from the per-artefact `schema` keys already present (report schema 2, run record schema 1), which the annex documents as shape versions; evidence_schema versions the annex as a whole. Distinct from BG1004's write version.
- The fourth criterion is a docs check by design: the policy is a promise, and the first three criteria are what execute it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G1 after the refine panel's review |
