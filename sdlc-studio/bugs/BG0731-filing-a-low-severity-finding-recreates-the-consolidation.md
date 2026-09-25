# BG0731: filing a Low-severity finding recreates the consolidation bucket that was just ruled not to be a change request

> **Status:** Open
> **Merged from:** BG0738 (backlog sweep 2026-09-24, sdlc-studio/reviews/backlog-sweep-2026-09-24.md)
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_low_finding_is_a_bug.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_triage_noise.py, changelog.d/BG0731.md, .claude/skills/sdlc-studio/scripts/tests/test_create_validate_roundtrip.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_issue_triage.py
> **Created:** 2026-09-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

D0217 retired CR0511 and CR0575 on 2026-09-20, ruling that a consolidation bucket is not a change request: it cannot be refined, because `refine` decomposes a request into sized units and a bucket whose only shared property is a severity band has no coherent decomposition. Both were Rejected with that reason recorded. On 2026-09-21, the very next day, filing two Low-severity findings created CR0592 `Low-severity bugs (consolidated)` - the same artefact, same `Consolidation: low-severity-bugs` key, same permanent residence at the bottom of the discovery backlog. The mechanism is `triage_noise.should_consolidate`, which routes any Low finding into a themed bucket instead of minting its own artefact. So an operator ruling that removes a bucket is undone by the next Low finding anybody files, and the ruling has no way to reach the code that recreates it.

## Steps to Reproduce

1. Note D0217 and the Rejected CR0511/CR0575. 2. File any finding with `--severity Low`. 3. A new `Low-severity X (consolidated)` CR appears in Proposed, counted by `status` as discovery awaiting refine. Observed 2026-09-21: CR0592, one day after the retirement.

## Proposed Fix

Decide what a Low finding should be and make the code and the decisions log agree - they currently do not. Either consolidation is right and D0217 was wrong, in which case the bucket needs to be refinable or excluded from the awaiting-refine count so it stops reading as a live option; or D0217 is right and Low findings should mint their own artefacts like every other severity, with the noise problem solved by triage rather than by a holding pen. What must not persist is the present state, where an operator retires a bucket and the filer silently rebuilds it. If consolidation stays, `should_consolidate` should at least refuse to reuse a consolidation key whose previous bucket was Rejected, and say why.

## Acceptance Criteria

- [ ] **AC1** Given a fresh schema-v3 project that sets no `triage` keys, when `file_finding.py file --type bug --severity Low` runs, then it creates a BG artefact at Low severity and creates or appends to no CR. Fails on: HEAD, whose shipped default `triage.low_consolidation: true` folds the finding into a `Low-severity bugs (consolidated)` CR, the bucket D0217 ruled is not a change request (CR0592 was minted this way the day after D0217)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_low_finding_is_a_bug.py::LowFindingTests::test_a_low_finding_mints_its_own_bug_by_default
- [ ] **AC2** Given a project that sets `triage.low_consolidation: true`, when a Low finding is filed, then it folds into the themed consolidation CR as it does at HEAD. Fails on: deleting consolidation outright, which removes an opt-in a project may have chosen without a migrate note
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_low_finding_is_a_bug.py::LowFindingTests::test_an_opted_in_project_still_consolidates
- [ ] **AC3** Given `reference-config.md`, then its `triage.low_consolidation` row states the default is false and cites D0217. Fails on: flipping the default in config-defaults.yaml while the reference still documents true
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_low_finding_is_a_bug.py::LowFindingTests::test_the_reference_states_the_default

## Notes

- Product ruling this implements: D0217 stands, so the shipped default is off and consolidation stays opt-in. This repository's own `.config.yaml` sets `low_consolidation: true` (line 318); removing it is US0926's (repo on shipped defaults), so it is not in this unit's Affects. Existing consolidation tests in test_artifact.py and test_triage_noise.py must set the key explicitly where they relied on the default. CR0592 stays Proposed (its remainder is DEFER in the triage ruling).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-21 | sdlc-studio | Filed |
| 2026-09-25 | sdlc-studio v6 planning | QA seat: generic AC1 replaced with falsifiable criteria for Sprint 5; fix is default off, opt-in kept (D0217) |
