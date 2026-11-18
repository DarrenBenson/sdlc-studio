# BG1524: The evidence pack accepts an edited report as signed because it never checks the fingerprint or the run record

> **Status:** Fixed
> **Severity:** High
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/evidence_pack.py, .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_build.py, .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_accountable.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, cross lens, survived 3 of 3 refute votes; observed at .claude/skills/sdlc-studio/scripts/evidence_pack.py `_signed()` (about line 108) and `_read_reports()` (about lines 155-184); claims at docs/engineering-leaders.md 'Change approval' and docs/release-notes-v6.4.0.md 'A release carries evidence a change board accepts'
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:22:23Z

## Summary

The 6.4 release notes and the engineering leaders page say the evidence pack is built from signed reports, that an unsigned report refuses the pack, and that the accountable person is whoever signed the report over its fingerprint. In `evidence_pack.py` the whole test of signed is that `signature.signed_at` in the report JSON is a non-empty string. The module has no reference to the fingerprint, to the report check, or to the committed run record under sdlc-studio/reports/runs, which is where `sprint sign` records who signed and which fingerprint. A report edited after signing, in its figures or in its signature block, is therefore packed as signed evidence, and the edited principal is printed as the accountable person. The shipped 6.4.0 pack is not affected, since its reports all still check valid, but the command that produces the artefact a change board reads does not verify what it claims.

## Steps to Reproduce

1. Make a throwaway clone of the repository.
2. In sdlc-studio/reports/RPT0034.json change `signature.principal` to another name and change the actual dollar cost figure, then commit.
3. Run `release_cut.py` evidence-pack with --version 9.9.9, --reports RPT0034 and --root set to the clone.
4. Observe: it writes the pack and exits 0, and each entry names the edited principal as accountable.
5. Read the run record for that run under sdlc-studio/reports/runs in the same tree: it still holds the original principal and fingerprint.
6. Read `_signed` in .claude/skills/sdlc-studio/scripts/`evidence_pack.py` (about line 109) and search the file for fingerprint: there is no match.

## Proposed Fix

In `_read_reports`, re-derive each report's fingerprint the way the report check does, and compare the fingerprint and principal with the signature held in the committed run record. Refuse the pack, naming the report, when the report no longer re-derives, when the run record holds no signature, or when the two disagree on principal or fingerprint. Print the verified fingerprint beside each accountable line so a reader can compare it. Pin the edited-figure and edited-principal refusals, with an untouched report as the passing control, in the evidence pack build test.

## Acceptance Criteria

- [ ] **AC1** Given a fixture clone whose signed report has a figure changed after signing, when `release_cut.py evidence-pack` is run over that report, then it refuses, naming the report as no longer re-deriving its signed fingerprint, and writes no pack. Fails on: a pack written from a report edited after its signature.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_build.py::SignedReportIsVerifiedTests::test_a_report_edited_after_signing_refuses_the_pack
  - **Verified:** yes (2026-11-18)
- [ ] **AC2** Given a signed report whose `signature.principal` was edited while the committed run record under `sdlc-studio/reports/runs` still holds the original, when the pack is built, then it refuses, naming the report and the disagreement on principal. Fails on: the edited principal printed as the accountable person.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_build.py::SignedReportIsVerifiedTests::test_an_edited_principal_refuses_the_pack
  - **Verified:** yes (2026-11-18)
- [ ] **AC3** Given a report whose JSON carries a non-empty `signature.signed_at` while its run record holds no signature, when the pack is built, then it refuses, naming the report as unsigned in the run record. Fails on: `signed_at` alone accepted as proof of a signature.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_build.py::SignedReportIsVerifiedTests::test_a_report_with_no_signature_in_the_run_record_refuses_the_pack
  - **Verified:** yes (2026-11-18)
- [ ] **AC4** Given an untouched signed report whose run record agrees with it, when the pack is built, then it is written, exits 0, and each accountable line names the run record's principal with the verified fingerprint beside it. Fails on: a valid report refused, or an accountable line with no fingerprint to compare.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_accountable.py::AccountableTests::test_the_accountable_line_carries_the_verified_fingerprint
  - **Verified:** yes (2026-11-18)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
