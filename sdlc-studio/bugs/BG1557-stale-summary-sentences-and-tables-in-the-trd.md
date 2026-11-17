# BG1557: Stale summary sentences and tables in the TRD contradict its own detailed sections and the code

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** sdlc-studio/trd.md, tools/tests/test_lean_trd_refresh.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, trd lens, survived 3 of 3 refute votes; observed at sdlc-studio/trd.md section 3 System Context (lines 104-105); section 2 Pattern Used (lines 84-86); section 3 C4 note (line 135); section 8 Deployment Topology table (lines 699-706); section 10 cost model (line 799) and section 12 (line 1297)
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:29:02Z

## Summary

Five high-level statements in the TRD were not updated when the detail beneath them changed, so a reader who takes the summary gets a different system from one who reads the detail. System Context says the only external service is GitHub through the `gh` CLI, while sections 4, 5 and 7 list the Cursor usage API and a direct HTTPS request to the GitHub API. Section 2 calls the script layer read-only, while rule 5 of section 5 says the scripts are not read-only over the workspace. The C4 note points at a module path that does not exist, the install table is headed as the local directory but gives global paths for Gemini CLI and opencode, and the cost model cites a re-estimation of 20 units where the shipped basis string says 21 with 19 measured and carries a build-only condition the TRD drops. The TRD describes itself as a rebuild blueprint, so each of these misleads a rebuilder.

## Steps to Reproduce

1. Open sdlc-studio/trd.md at lines 104 to 105 and read that the only external service is GitHub through the `gh` CLI; then read line 253 (the Cursor usage API row) and line 333 (the HTTPS request to the GitHub API).
2. Read lines 84 to 86, which describe a read-only Python script layer; then read lines 305 to 306, which say the scripts are not read-only over the workspace.
3. Read line 135, which names modules/trd/c4-diagrams.md; list .claude/skills/sdlc-studio/modules/ and find no such file. The file is at .claude/skills/sdlc-studio/templates/modules/trd/c4-diagrams.md.
4. Read the install table at lines 699 to 706, headed Local install directory: the Gemini CLI and opencode rows give home-directory paths. Open install.sh at lines 147 and 149: the local paths are .gemini/skills and .opencode/skills.
5. Read line 799 and line 1297, which cite a blind re-estimation of 20 delivered units. Open .claude/skills/sdlc-studio/scripts/sprint.py at lines 125 to 138: the basis string says 21 delivered units of which 19 had measured actuals, and `NO_BASE_TERM_CONDITION` says the figure holds for the build only and travels with every forecast basis.

## Proposed Fix

Correct each statement in sdlc-studio/trd.md to agree with the detail and the code: name the Cursor usage API and the direct GitHub API request in System Context; describe the script layer as deterministic, not read-only, in section 2; point the C4 note at templates/modules/trd/c4-diagrams.md; give the local install paths for Gemini CLI and opencode (or add a global column and label both); and state 21 units with 19 measured, with the build-only condition, in section 10 and section 12. Add assertions to tools/tests/`test_lean_trd_refresh.py` that the C4 path named in the TRD exists, that the install table's local paths match what install.sh prints for each target, and that the unit count in the cost model matches the count in `POINTS_RATE_SEED_BASIS`.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Five high-level statements in the TRD were not updated when the detail beneath them changed, so a reader who takes the summary gets a different system from one...
- [ ] **AC2** The proposed fix lands, pinned by a test: Correct each statement in sdlc-studio/trd.md to agree with the detail and the code: name the Cursor usage API and the direct GitHub API request in System...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
