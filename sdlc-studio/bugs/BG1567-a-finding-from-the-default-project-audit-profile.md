# BG1567: A finding from the default project audit profile cannot be attributed to its lens

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/help/audit.md, changelog.d/BG1567.md
> **Evidence:** audit AUDIT-2026-11-17, filing step; file_finding.py lens lookup near line 1955 and the refusal it printed
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:30:31Z

## Summary

The audit help tells the operator to stamp each finding with its lens and its audit run, and the default profile is project. The filer resolves a lens only against the packs under templates/audit-profiles, which hold code, process, repo, skill and test. The project profile's eight lenses live in reference-audit.md, so every one of them is refused as a lens no pack declares. The 68 findings of audit AUDIT-2026-11-17 were therefore filed with no Audit-lens or Audit-run field, and the detector-owed report cannot count them.

## Steps to Reproduce

1. Record an audit run with `audit_cost.py` record and a run id.
2. Write a bug fields file carrying lens PRD and that `audit_run.`
3. Run `file_finding.py` file with --fields-file and --dry-run.
4. The filer refuses: no pack declares the lens PRD, and lists code, process, repo, skill and test.
5. Run readiness.py profile with --name project: it lists PRD among the profile's eight lenses.

## Proposed Fix

Make the filer's lens lookup include the project profile that readiness.py already resolves from reference-audit.md, so a lens the default profile declares is accepted and stamped. Pin it with a test that files a finding under each project lens.

## Acceptance Criteria

- [ ] **AC1** Given a recorded audit run and a bug fields file carrying the lens PRD and that run, when `file_finding.py file` runs with `--fields-file`, then the finding is filed with its Audit-lens, Audit-profile (project) and Audit-run fields stamped. Fails on: the refusal that no pack declares the lens PRD.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::ProjectProfileLensTests::test_a_project_profile_lens_is_accepted_and_stamped
- [ ] **AC2** Given the lenses `readiness.py profile --name project` lists, when a finding is filed under each one, then every one is accepted and stamped with the project profile. Fails on: the filer and the profile resolver disagreeing on any lens of the default profile.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::ProjectProfileLensTests::test_every_lens_the_project_profile_lists_is_accepted
- [ ] **AC3** Given a lens no profile or pack declares, and a lens that the project profile and a pack both declare filed with no profile, when each is filed, then the first is refused naming the lens and listing the project profile among what exists, and the second is refused as ambiguous as two packs already are. Fails on: an unknown lens stamped, or an ambiguous lens resolved silently to one owner.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::ProjectProfileLensTests::test_an_unknown_lens_is_still_refused_and_an_ambiguous_one_is_not_guessed

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
