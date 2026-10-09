# US0994: A consumer reads the committed run record, awaiting signature, sealed or stopped, against the annex

> **Status:** Draft
> **Delivers:** CR0609
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-evidence-schema.md, .claude/skills/sdlc-studio/scripts/tests/test_evidence_annex_run_record.py, changelog.d/US0994.md
> **Epic:** EP0275
> **Points:** 3
> **Depends on:** US0992, CR0610
> **Persona:** Maya Okafor

## User Story

**As** a team lead whose dashboard shows which sprint run is open and who signed it
**I want** the run-record keys a consumer reads, and the rule that makes a record await its signature, stated in the annex
**So that** my dashboard reads 'awaiting signature' the same way `sprint plan` does, from the committed file alone

## Acceptance Criteria

- **AC1:** Given a run closed with `sprint close` and signed with `sprint sign` in a fixture, when the conformance test reads the tracked record after each command, then every key the annex contracts for that state is present with its documented type, and a key the annex does not contract is tolerated rather than failed.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_annex_run_record.py::RunRecordAnnexTests::test_the_tracked_record_holds_its_contracted_keys
- **AC2:** Given three tracked records from fixture runs, one closed, one closed and signed, and one closed and then ended with `sprint stop`, when the test evaluates the annex's own awaiting-signature predicate, extracted from the annex, on each record, then it agrees with `sprint plan --write` in a fresh clone, which is refused for the first and not refused for the other two.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_annex_run_record.py::RunRecordAnnexTests::test_the_annex_awaiting_rule_matches_the_plan_guard

## Notes

- Release: 6.2 (D0355 breakdown G1, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: a contracted key (report_fingerprint, say) removed or renamed by its writer with no annex change, or the annex contracting `signature` on an awaiting record
- AC2 must fail on: an annex predicate reading 'awaiting' as 'carries no signature', which wrongly reads the stopped run as open, or a change to the plan's guard with no annex change
- Serves Maya's End goal 2, 'Never lose the thread' (maya-okafor-founder-engineer.md:26), for a consumer that reads open and signed runs.
- Drafted to the panel's recommendation on drift reach (question 1): contract the keys a consumer reads (run id, report linkage, lifecycle, signature and the fields the report reads, including plan_digest and the pricing snapshot), fail on removal or rename, tolerate additions. The 13 committed records hold 49 distinct top-level keys from many writers.
- The predicate at HEAD is run_state.awaiting_signature (run_state.py:564): the record names a report and its outcome is still running. A run that the close filed and `stop` then ended carries no signature and is not running, because close_run refreshes the tracked record (run_state.py:1813); that is the case that tells the right rule from 'no signature'. `sprint stop` may need --force in the fixture.
- The annex documents BG0993's stated gap: between a `reopen` and the next close, the tracked record still reads sealed, so another clone is not refused a plan in that window.
- The legacy plan values are documented as legacy: `plan: sha256:<12 hex>` (a digest of a path, five records) and `plan: sdlc-studio/.local/sprint-plan.json`; neither is a content digest.
- If BG1004 lands first, its write version is documented here.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G1 after the refine panel's review |
