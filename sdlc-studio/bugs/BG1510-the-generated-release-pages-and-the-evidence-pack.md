# BG1510: The generated release pages and the evidence pack lag every signature and filing after the cut, and the release-gate workflow names no step to regenerate them before the tag

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/templates/workflows/release-gate.md, .claude/skills/sdlc-studio/help/gate.md, .claude/skills/sdlc-studio/scripts/release_cut.py, .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_tag_no_close_owed.py, changelog.d/BG1510.md
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T17:51:50Z

## Summary

docs/evidence.md, docs/known-issues.md and the release notes' disclosed-defect line are generated at the cut, but the release run's own report is always signed after the cut and findings keep being filed. For 6.4 they named RPT0032 as the last report and an older defect count until D0500 regenerated them by hand (cd0e478e), and the evidence pack had not been written at all.

## Steps to Reproduce

1. Cut a release, then sign the release run's report or file a finding.
2. Read docs/evidence.md and docs/known-issues.md: they still name the earlier last report and the earlier open-defect count.

## Proposed Fix

Add a pre-tag step to the release-gate workflow, or a tag-check refusal, that compares the generated pages and the evidence pack with the records at the tagged commit and names the regenerating command when they differ.

## Acceptance Criteria

- [ ] **AC1** Given a release cut whose generated evidence page was written before a later run report was signed, when `release_cut.py tag-check` judges the commit, then it refuses, names the page and the report it does not carry, and prints the command that regenerates it. Fails on: a tag whose evidence page names an earlier last report.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py::GeneratedPagesFreshTests::test_tag_check_refuses_an_evidence_page_that_lags_a_later_signature
- [ ] **AC2** Given a cut whose version has no evidence pack, or one built before the records it summarises last changed, when `tag-check` runs, then it refuses naming the pack and the `evidence-pack` command. Fails on: a release tagged with no pack written, as 6.4 nearly was.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py::GeneratedPagesFreshTests::test_tag_check_refuses_a_missing_or_stale_evidence_pack
- [ ] **AC3** Given the pages and the pack regenerated from the records at the commit, with the gate green on it, when `tag-check` runs, then it passes. Fails on: the freshness check refusing a correctly regenerated release.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py::GeneratedPagesFreshTests::test_tag_check_passes_once_the_pages_and_pack_are_regenerated
- [ ] **AC4** Given the shipped release-gate workflow template, when it is read, then it carries a pre-tag step to regenerate the evidence page, the known-issues page and the evidence pack after the last signature and filing, naming `tag-check` as what refuses a stale one. Fails on: the refusal existing with no step in the workflow that tells the operator when to regenerate.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py::GeneratedPagesFreshTests::test_the_release_gate_workflow_names_the_pre_tag_regeneration_step

## Impact

A tag can ship pages that misstate the signed evidence and the open-defect disclosure the release is judged on.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
| 2026-11-23 | Claude Opus 5.5 (run twenty-three orchestrator) | Affects widened to tests/test_lean_tag_no_close_owed.py, which pins tag-check and record-green behaviour this fix changes (the REL builder stopped on it before building) |
| 2026-11-23 | Claude Opus 5.5 (run twenty-three orchestrator) | Affects widened to help/gate.md, whose tag-check sentence (asks only whether the gate was green and CI passed) the freshness check makes untrue; found by the REL builder |
