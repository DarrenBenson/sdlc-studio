# BG1570: The evidence pack trusts the run record as committed at the build revision, so one commit that edits a report's figures, its signature and its run record together still passes

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/evidence_pack.py, .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_build.py, changelog.d/BG1570.md
> **Evidence:** Found by the run sixteen builder of BG1524 and US1292, 2026-11-17.
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T23:01:38Z

## Summary

BG1524 (run sixteen) makes the evidence pack check that a report's signature binds the page it signs. The pack reads the run record from the tree at the revision it builds from, not from the history that wrote it, so a single later commit that rewrites the report's figures, re-enters the signature block and edits the run record to match is accepted as signed. The signature is only as strong as the record it is compared against, and that record is as editable as the page.

## Steps to Reproduce

1. Take a signed report and its tracked run record, committed by `sprint sign`.
2. In one later commit, change a figure on the report (a unit's points), re-stamp the report's
   `fingerprint` and its signature's `fingerprint` to the new digest, and set the run record's
   signature `fingerprint` to agree.
3. Build the pack at that commit: `release_cut.py evidence-pack --version 6.4.0 --reports RPT0001`.

Measured at HEAD 3791e5193 with the `test_evidence_pack_build.py` fixture: the build exits 0 and
the pack lists US0001 at 13 points, the forged figure. Swapping the principal on the report and
the record together in one later commit also builds, and the accountable line names the new
principal.

## Proposed Fix

Find the seal commit: the first commit in the history of `sdlc-studio/reports/runs/<run>.json`
reachable from the build revision whose record holds a signature for the report
(`git log --reverse --format=%H <sha> -- <record>`, then `git show <seal>:<record>`). Verify the
report at the build revision against that sealed signature, not the record at the build
revision, and refuse a pack whose record's signature at the build revision differs from the
sealed one, naming the seal commit. No amendment path exists at HEAD, so none is in scope; a
later commit that leaves the report and the record's signature alone still builds.

## Acceptance Criteria

- [ ] **AC1** Given a signed report and run record sealed in one commit, when a later commit changes a figure on the report, re-stamps both fingerprints on it and sets the run record's signature fingerprint to agree, then `evidence-pack` refuses, writes no pack and names the report and the seal commit. Fails on: HEAD, which builds the pack and lists the forged figure (measured: US0001 at 13 points).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_build.py::SealedSignatureTests::test_figures_and_signature_rewritten_after_the_seal_refuse_the_pack
- [ ] **AC2** Given the same sealed project, when a later commit changes the signature's principal on the report and on the run record together, then `evidence-pack` refuses and names the report. Fails on: HEAD, which builds and names the new principal as accountable (measured).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_build.py::SealedSignatureTests::test_a_principal_rewritten_after_the_seal_refuses_the_pack
- [ ] **AC3** Given the same sealed project, when later commits change only other files (a story, the verdict ledger), then the pack builds and each accountable line names the principal and fingerprint the seal commit's record holds. Fails on: a fix that refuses any commit after the seal, or reads the signature from the record at the build revision.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_build.py::SealedSignatureTests::test_commits_after_the_seal_that_leave_the_signature_alone_still_build

## Impact

A change board reading the pack as proof that the signed figures are the ones the operator signed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
| 2026-11-23 | Sam Eriksson (qa) | Groomed for run twenty-four: reproduced at HEAD (one commit rewriting the figure, both fingerprints and the record builds); criteria rewritten as three executable ones in a new SealedSignatureTests class, a positive control among them; Proposed Fix names the seal commit and drops the amendment path no code has |
