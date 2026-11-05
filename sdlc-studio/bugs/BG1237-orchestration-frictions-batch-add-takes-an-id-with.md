# BG1237: Orchestration frictions: batch add takes an id with no file, and a re-review's prior-finding notes parse as a blocking item

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding_bare_url.py, .claude/skills/sdlc-studio/scripts/tests/test_orchestration_frictions.py, changelog.d/BG1237.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** run six transcripts; scratchpad run6/BG1236-verdict-r2.txt
> **Created:** 2026-11-05
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-05T16:46:44Z

## Summary

2026-11-05, run six. sprint.py batch add accepted BG1236 into the open run's batch and reported it added while no BG1236 file existed (its filing had been refused). A round-2 verdict that followed BLOCKING: none with a prior-finding section was parsed by critic.py record as the blocking item 'none PRIOR FINDING RULING' and refused, and the re-review brief does not say where prior-finding rulings go. The pre-existing `test_file_finding_bare_url.py`:39 starts its markdownlint search at .claude/ rather than the checkout root.

## Steps to Reproduce

1. sprint.py batch add BG9999 with no such file: it is added.
2. Record a verdict whose BLOCKING: none is followed by another section: it is refused.

## Proposed Fix

Refuse batch add for an id with no artefact; end the BLOCKING field at the line, and name in the re-review brief where prior-finding rulings go; start the lint search at the checkout root.

## Acceptance Criteria

- [ ] **AC1** batch add refuses an id with no artefact file, naming it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_orchestration_frictions.py -k batch_add
- [ ] **AC2** A verdict with BLOCKING: none followed by a further section records as having no blocking item.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_orchestration_frictions.py -k blocking_none

## Impact

Each cost an orchestrator round trip in run six.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-05 | claude | Filed |
