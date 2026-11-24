# BG1597: docs/harnesses.md's install-path check accepts the global and project folders in either order, its Claude Code live-reload cell rests on one CLAUDE.md sentence, and two cells cite a file that does not hold the claim

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** docs/harnesses.md, tools/tests/test_harness_matrix_doc.py, changelog.d/BG1597.md
> **Evidence:** sdlc-studio/reviews/verdicts/US1316/ea58b65ac3c9-912d8166.txt, findings 3, 5 and 6.
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T16:27:40Z

## Summary

Non-blocking findings from US1316's round-one qa review, left by the repair: AC2 compares the install paths as a set, so a row giving the project folder before the global one passes while the page says global first; the Claude Code live-reload cell cites CLAUDE.md lines 7-8, a prose sentence nothing in the tree exercises; the Claude Code token cell cites `token_meters.py` for subagent transcripts, which `run_state.py` reads, and the four headless-lanes cells cite `harness_usage.py` for `sprint lane run --harness`, which lives in sprint.py and help/sprint.md.

The round-two review (sdlc-studio/reviews/verdicts/US1316/7dbde4017dd2-d2219ec6.txt) adds two: the untested pass still admits an unsourced claim after an opening Untested joined by a full stop, comma or colon (only the semicolon form is refused), and the AC4 denylist passes None exists, Not applicable and Cannot be done while refusing a real fallback that contains not supported. The page states both rules as the code implements them, so neither over-claims.

## Steps to Reproduce

Swap the two install paths in the Claude Code row of docs/harnesses.md and run tools/tests/`test_harness_matrix_doc.py`: it passes.

## Proposed Fix

Compare the install paths in order; mark the live-reload cell as from maintainer use or untested; cite `run_state.py` and sprint.py where the claims live.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Non-blocking findings from US1316's round-one qa review, left by the repair: AC2 compares the install paths as a set, so a row giving the project folder before...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Swap the two install paths in the Claude Code row of docs/harnesses.md and run tools/tests/`test_harness_matrix_doc.py`: it passes.
- [ ] **AC3** The proposed fix lands, pinned by a test: Compare the install paths in order; mark the live-reload cell as from maintainer use or untested; cite `run_state.py` and sprint.py where the claims live.

## Resolution

Won't Fix under D0613: the operator approved the product seat's second proposal (D0562) because it lies in this repository's own CI, hooks or tools, which the installed skill does not ship. This repository's docs/harnesses.md test.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
| 2026-11-24 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0613: the operator approved the product seat's second list (D0562); reason in Resolution |
