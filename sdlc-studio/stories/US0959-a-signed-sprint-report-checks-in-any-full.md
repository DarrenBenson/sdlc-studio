# US0959: A signed sprint report checks in any full clone, from a sealed run record tracked beside it

> **Status:** In Progress
> **Created:** 2026-09-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_tracked_run_record.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, changelog.d/US0959.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0267
> **Parent:** CR0599
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer who seals each sprint with one signature
**I want** `sprint sign` to file the sealed run record into the tracked tree, and `sprint_report.py check` to read the record and its signature from there
**So that** a teammate's clone or CI can verify what I signed, and an edit to my clone's `.local` cannot re-point or strip the signature

## Acceptance Criteria

- **AC1:** Given a fixture run closed and signed with `sprint.py sign`, when the seal finishes, then `sdlc-studio/reports/runs/<RUN-ID>.json` exists carrying the run's signature, outcome and `ended_at`, and no string value in it is an absolute path. Fails on: copying `.local/run-state.json` verbatim, which commits the home directory and session transcript ids every recent record carries (`plan`, `session_token_stamps[].source`, `unit_actuals.*.start_source`)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_tracked_run_record.py::TrackedRunRecordTests::test_sign_files_a_portable_sealed_record
- **AC2:** Given that fixture committed and cloned with full history and no `.local`, when `sprint_report.py check --report` runs in the clone, then it exits 0. Fails on: HEAD's `_run_state_for`, which looks only in `.local` and exits 2 'no run record names RUN-...' (measured in a clean clone of dee380d9 for RPT0006-RPT0010)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_tracked_run_record.py::TrackedRunRecordTests::test_a_clean_clone_checks_the_signed_report
- **AC3:** Given the signing clone, when the `.local` record's signature is stripped or re-pointed at another fingerprint, then `check` still exits 0 from the tracked record; and when the tracked record's signature is re-pointed in a later commit with no recorded reopen, then `check` exits 1 naming the signature against the version first committed with it. Fails on: reading the signature from `.local` (CR0599's route) or from the tracked record's working copy, where an edit certifies itself
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_tracked_run_record.py::TrackedRunRecordTests::test_the_signature_is_read_from_tracked_history
- **AC4:** Given a signed run reopened with a recorded reason and signed again, when `check` runs on its report, then it exits 0. Fails on: anchoring the first committed signature unconditionally, which reads every legitimate re-seal as forged
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_tracked_run_record.py::TrackedRunRecordTests::test_a_reopened_and_resigned_run_checks_valid
- **AC5:** Given a depth-1 clone holding the tracked records, when `check` runs on a signed report, then it exits 2 and names shallow history as why it cannot judge, never INVALIDATED. Fails on: HEAD, which reads RPT0006 and RPT0010 INVALIDATED on `dora_band` in a depth-1 clone (measured)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_tracked_run_record.py::TrackedRunRecordTests::test_a_shallow_clone_cannot_judge_and_says_so

## Notes

- Depends on: BG0783
- Decomposed from CR0599 (with BG0795, BG0788 and US0960). Engineering calls: the record lives at sdlc-studio/reports/runs/<RUN-ID>.json; it is the run record through one projection (an absolute path under the repo becomes repo-relative, any other becomes sha256:<12 hex>, which preserves the per-session grouping `run_token_total` needs; no figure's source string is in the fingerprint). Written by `cmd_sign` after `close_run` and before `record_close_tree`, so the seal commit carries it and `tree_moved_since_close` never counts it. `_run_state_for` order: the live record when it names the run, else the tracked record, else the `.local` archive (an unmigrated project). The signature is found the way `_signed_page` finds the page: `git log --full-history --reverse` on the tracked path; a later committed signature is accepted only when the record's `reopened` list shows a reopen between the two. Land after BG0783 (both touch run_state.py and sprint_report.py). Ratchet (LC-008): no refusal added to the loop; AC5 replaces a false INVALIDATED with the existing exit 2 'cannot judge'; retires the `.local` trust root for the signature. Land in the first half of the sprint so the seal rehearsal exercises it before RPT0011 is signed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-27 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 6 from the seat planning (US0959) |
