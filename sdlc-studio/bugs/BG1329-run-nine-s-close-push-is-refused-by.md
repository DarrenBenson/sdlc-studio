# BG1329: Run nine's close push is refused by two test regressions: US1142's reflow split the wsjf-inputs.json writer line its pin reads, and BG1312's known-issues test patches a sprint_report object resume_brief may not use

> **Status:** Open
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_resume_brief.py, changelog.d/BG1329.md
> **Evidence:** push-16 refusal at f9c34cd2 (devserver1 boundary suite, 3 failed) and forge run 42676771245
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-09T19:53:32Z

## Summary

The push of RUN-01M7061X's close (f9c34cd2) was refused by the full suite on devserver1 with 3 failures (2026-11-09). (1) US1142 reflowed reference-sprint.md to stay at 859 lines and split the sentence that tells the agent to write `sdlc-studio/.local/wsjf-inputs.json`, so `test_lean_v61_review_residue.py`'s line-based pin (V61ReviewResidueTests::`test_every_local_row_has_a_writer` and LocalWriterPinTests::`test_a_writer_that_stops_writing_fails_the_pin)` reports no writer line; neither US1142's commit selection nor its review ran that module. (2) `test_resume_brief.py`::KnownIssuesTests::`test_the_moment_is_read_through_the_report_helper` patches `sprint_report._stamp_timestamp` on the module object the test imported; in a full parallel suite, and under the unittest runner CI uses (forge run 42676771245), `resume_brief` can hold a different `sprint_report` object, the patch misses and the finding stays listed. It passes alone.

## Steps to Reproduce

1. Run `python3 -m pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_v61_review_residue.py -q`: two pins fail on wsjf-inputs.json.
2. Run the full suite (or tools/skill-tests.sh): `test_the_moment_is_read_through_the_report_helper` fails with the finding still listed.

## Proposed Fix

Rewrap reference-sprint.md so the wsjf-inputs.json writer sentence sits on one line again, within the 859-line budget and keeping US1142's wave-boundary text; patch the `sprint_report` object `resume_brief` itself uses (reached through `resume_brief)` so the test holds in any import order and runner.

## Acceptance Criteria

- [ ] **AC1** Given reference-sprint.md, then the sentence telling the agent to write `sdlc-studio/.local/wsjf-inputs.json` reads on one line again, the page stays at 859 lines, and US1142's wave-boundary text and every grepped sentence stand. Fails on: the writer sentence split across lines; the page over budget.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_v61_review_residue.py
- [ ] **AC2** Given `test_the_moment_is_read_through_the_report_helper`, then it patches the `sprint_report` object `resume_brief` itself uses, so it passes alone, in the full parallel suite and under the unittest runner. Fails on: the patch applied to a sprint_report object resume_brief does not read.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_resume_brief.py
- [ ] **AC3** Given the wave-boundary pages, then US1142's own test still passes.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_wave_boundary_docs.py

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
| 2026-11-09 | Claude Opus 5.5 (run nine, D0455) | Criteria and Verify lines authored when BG1329 joined the reopened run |
