# BG0756: US0900 did not converge in review: round 2 REJECT findings

> **Status:** Open
> **Carried work:** the round-2 work is saved at sdlc-studio/.local/US0900-carried-r2.patch (13 files, applies cleanly to 65cdf1ca); groomed criteria below say what remains
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/help/cr.md, .claude/skills/sdlc-studio/reference-scripts-create.md, .claude/skills/sdlc-studio/templates/agent-instructions.md, changelog.d/US0900.md, sdlc-studio/stories/US0128-undecomposed-drift-cr-creation-size-demand-respect-the.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_cr_filing.py, .claude/skills/sdlc-studio/scripts/tests/test_points.py, .claude/skills/sdlc-studio/scripts/tests/test_size_by_type.py, .claude/skills/sdlc-studio/scripts/tests/test_two_backlogs.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

US0900 was rejected at round 2, the review cap, by qa-rev-US0900, so it was carried as a known issue rather than reviewed again. The findings still open: [new] the v3 creator and validator still disagree: a minimal CR validates at inbox and Proposed but fails evidence-present once triaged to Approved, refined to In Progress or rejected, because no tool ever writes a Size or Impact onto the CR - the refusal moved again rather than retiring [LC-008]; [new] help/cr.md, the changelog and file\_finding.py say refine gives the CR its size, which is false: refine sizes the epic [LC-004]; [new] non-blocking: US0128 AC2 retired and AC3 honest (closed); [new] non-blocking: prose Affects and the Impact placeholder (closed)

## Steps to Reproduce

1. At 65cdf1ca, in a fixture, run `file_finding.py file --type cr` with a title, summary and priority. It refuses: `missing required field(s): ctype, acs, impact`. US0900 is undelivered.
2. With the worktree's round-2 diff applied to a scratch copy, on a `schema_version: 3` fixture, the same filing writes an `inbox` CR, and `validate.py check` reports errors=0.
3. Move it with `transition.py set --status Approved --triaged-by ...`, then to In Progress; both transitions succeed. Or set Status to Rejected. At each status `validate.py check` reports `[evidence-present] CR needs both an impact statement and a size`.

## Proposed Fix

Land the round-2 work, then retire the Size and Impact demand the filer cannot meet (no tool writes them onto the CR), or have a shipped step write them. Replace the worktree's `test_a_cr_past_its_opening_status_still_owes_impact_and_size`, which pins the disagreement, and correct the three texts that say refine sizes the CR.

## Acceptance Criteria

- [ ] **AC1** Given `file_finding.py file --type cr` and `artifact.py new --type cr` with a title, summary and priority but no size, impact or Affects, when each runs, then the CR is written and indexed and exits 0; a bug missing points or Affects is still refused before an id is allocated. Fails on: HEAD, whose filer refuses the CR (measured).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_cr_filing.py::CrFilingTests::test_an_unsized_cr_is_filed_by_both_creators
- [ ] **AC2** Given a minimal CR filed on a schema v3 fixture, when `transition.py set` moves it to Approved, then In Progress, and a second one to Rejected, then `validate.py check` reports zero errors at each status, while a bug with no evidence still fails `evidence-present`. Fails on: the round-2 patch's opening-status exemption, which errors from Approved on (measured); deleting the evidence rule for every type, which the bug control catches.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_cr_filing.py::CrValidatesOnSchemaV3Tests::test_a_minimal_cr_validates_at_every_status_the_shipped_tools_move_it_to
- [ ] **AC3** Given `help/cr.md`, `changelog.d/US0900.md`, `reference-scripts-create.md` and `file_finding.py`, when they are read, then none says `refine` sizes or gives a size to the CR itself; where they name who sizes the work, they name the epic `refine` writes. Fails on: the round-2 wording, "refine sizes it later" and "`refine` gives it a size", both measured in the worktree diff.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_cr_filing.py::CrDocTruthTests::test_no_shipped_text_says_refine_sizes_the_cr

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Filed |
| 2026-09-25 | QA seat | Groomed for Sprint 4: still real (HEAD refuses an unsized CR; with the round-2 diff applied, a minimal v3 CR errors `evidence-present` at Approved, In Progress and Rejected); carried work located in worktree agent-acf5678c9849cf7f0, not .local; criteria are the carried work plus the two round-2 findings, each with one Verify line and the wrong fix it fails on; Affects set to the diff's files; 1 point resized to 3 |
