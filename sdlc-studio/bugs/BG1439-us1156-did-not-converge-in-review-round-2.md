# BG1439: US1156 did not converge in review: round 2 REJECT findings

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/evidence_pack.py, .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_build.py, .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_accountable.py, changelog.d/US1156.md, .claude/skills/sdlc-studio/reference-scripts.md, changelog.d/BG1439.md
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T02:42:33Z

## Summary

US1156 was rejected at round 2, the review cap, by qa-seat-US1156-r1, so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] The repair's author-record refusal reaches far beyond the authoring session. recorded\_authors (evidence\_pack.py:112) collects every Author cell in the whole verdict ledger and the whole self-check ledger, superseded rows included, and principal\_refusal (evidence\_pack.py:128-145) refuses any signer who matches one, with the message "so it is an authoring agent". critic.py record takes --author as a free-form seat or delegation id and never types a person as human, so a person who once authored any unit can never be named accountable on any later report. Probe through release\_cut.py evidence-pack: a fixture ledger records "Lee Operator" as the author of US0009, a unit in no named report, and RPT0002 is signed by "Lee Operator". The build exits 2 with "'Lee Operator' is recorded as an author in the committed review ledgers, so it is an authoring agent", and it still refuses when that one row is superseded. sprint sign's \_principal\_refusals (sprint.py:10398) refuses only an author or a reviewer of the run's own units, so sprint sign accepts Lee for a run the pack then refuses. This is the over-broad refusal of a human principal that AC3's positive control rules out. Limiting the record to the live author rows of the report's own delivered units keeps the model-name catch, since a builder that signs its own run is the author of its units; [new] changelog.d/US1156.md still says each change lists "the known issues its signed report hands over that name it", but the pack attaches a matching issue from any named report (evidence\_pack.py:316). The repair did not touch this, and the behaviour meets AC1; [new] The \_known\_issues docstring still promises each issue once, and nothing pins it: dropping `issue not in out` at evidence\_pack.py:244 leaves every US1156 test green, because no fixture repeats one issue across two reports. The repair did not touch this; [new] Nothing pins the lookbehind the repair added to \_AGENT\_RE (evidence\_pack.py:46). Removing `(?<![a-z])` leaves every test green (the mutant, applied alone, survived), yet the comment names Reagent as a person the pattern must not match. A probe shows 'Reagent Okoro' accepted at HEAD, so the code is right and only the test is missing; RULINGS: "AC3 is met only for the spellings its test lists" CLOSED as raised. Through release\_cut.py evidence-pack at bd4604ab, 'sub-agent', 'an AI agent', 'Agent (builder)' and 'agent 7' are each refused. 'Claude Opus 5.5 (builder)' is refused wherever a committed ledger records it as an author: in a fixture, and in a clone of this repository where a probe report signed with that name was committed against the real ledgers. 'Agnes', 'Agentha Ruiz', 'Reagent Okoro' and 'Dana Reviewer' are accepted. The repair that closes it opened the blocking finding above. Re-executed mutants: restoring the old anchored pattern, match in place of search, the author check switched off, the self-check ledger dropped, the typed-human exemption dropped, the typed name no longer extracted and the lookahead dropped are each killed by AccountableTests::test\_agent\_or\_blank\_principal\_is\_refused. Only the lookbehind mutant survives (fourth finding). The two non-blocking round-1 findings (the changelog wording and the issue de-duplication pin) were not repaired and are carried again above. Verify dry-run passes 3 of 3. The real packs over RPT0020 and RPT0022 to RPT0030 still build, so this repository's operator is not refused today. The clone used for mutation was byte-identical afterwards.

## Steps to Reproduce

1. Read the round 2 REJECT of US1156 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver US1156 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] The repair's author-record refusal reaches far beyond the authoring session. recorded\_authors (evidence\_pack.py:112) collects every Author cell in the whole verdict ledger and the whole self-check ledger, superseded rows included, and principal\_refusal (evidence\_pack.py:128-145) refuses any signer who matches one, with the message "so it is an authoring agent". critic.py record takes --author as a free-form seat or delegation id and never types a person as human, so a person who once authored any unit can never be named accountable on any later report. Probe through release\_cut.py evidence-pack: a fixture ledger records "Lee Operator" as the author of US0009, a unit in no named report, and RPT0002 is signed by "Lee Operator". The build exits 2 with "'Lee Operator' is recorded as an author in the committed review ledgers, so it is an authoring agent", and it still refuses when that one row is superseded. sprint sign's \_principal\_refusals (sprint.py:10398) refuses only an author or a reviewer of the run's own units, so sprint sign accepts Lee for a run the pack then refuses. This is the over-broad refusal of a human principal that AC3's positive control rules out. Limiting the record to the live author rows of the report's own delivered units keeps the model-name catch, since a builder that signs its own run is the author of its units
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** The round 2 REJECT finding no longer holds: [new] changelog.d/US1156.md still says each change lists "the known issues its signed report hands over that name it", but the pack attaches a matching issue from any named report (evidence\_pack.py:316). The repair did not touch this, and the behaviour meets AC1
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC3** The round 2 REJECT finding no longer holds: [new] The \_known\_issues docstring still promises each issue once, and nothing pins it: dropping `issue not in out` at evidence\_pack.py:244 leaves every US1156 test green, because no fixture repeats one issue across two reports. The repair did not touch this
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC4** The round 2 REJECT finding no longer holds: [new] Nothing pins the lookbehind the repair added to \_AGENT\_RE (evidence\_pack.py:46). Removing `(?<![a-z])` leaves every test green (the mutant, applied alone, survived), yet the comment names Reagent as a person the pattern must not match. A probe shows 'Reagent Okoro' accepted at HEAD, so the code is right and only the test is missing
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC5** US1156 AC1 still passes: Given a signed report whose known-issues rows name open findings, when the pack is built, then each change lists the known issues that name it, and the pack carries the report's remaining known issues in one list.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_accountable.py::KnownWrongTests::test_known_issues_listed_per_change_and_for_the_release
- [ ] **AC6** US1156 AC2 still passes: Given a signed report, when the pack is built, then each change names the accountable person recorded on that report's signature, with the signing date.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_accountable.py::AccountableTests::test_each_change_names_the_signing_principal
- [ ] **AC7** US1156 AC3 still passes: Given a report whose signature principal is blank or reads as an agent (for example 'the agent' or 'agent-<id>'), when the pack is built, then the command exits non-zero and no pack names the agent as accountable.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_accountable.py::AccountableTests::test_agent_or_blank_principal_is_refused

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Filed |
