# BG1234: Small follow-ups from run six's approved bug fixes: BG1217, BG1220, BG1223, BG1224 and BG1227

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, tools/gate_prereqs.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_trunk_integration.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_run_six_followups.py, changelog.d/BG1234.md, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, tools/tests/test_gate_prereqs.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py
> **Evidence:** run six reviews, scratchpad run6/*-verdict-r*.txt
> **Created:** 2026-11-05
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-05T15:34:58Z

## Summary

2026-11-05, run six's reviews. BG1217: a node id in a module that fails to import is refused with exit 2 and its ImportError hidden (gate.py near 2682), and the refusal's node order is unpinned. BG1220: the refusal says 'no python3.10 on PATH' when a python3.10 answering 3.12 is there, and '3.10' is hard-coded rather than read from `PYTHON_FLOOR.` BG1223: a docstring line runs to 164 characters and the helper's wait has no timeout. BG1224: the branch/PR test pattern misses 'git push origin main:feature', 'git worktree add -b' and prose; the obligation says fast-forward within the lane while the brief hands the commit to lane land. BG1227: the URL wrap also code-spans URLs inside code blocks, hrefs, link definitions and table cells (swallowing a closing pipe); a URL in a title or a Verify line, `www.` and email addresses still trip MD034.

## Steps to Reproduce

See the summary; each item was reproduced by its reviewer or builder.

## Proposed Fix

Fix each in place, each with a pin.

## Acceptance Criteria

- [ ] **AC1** Each listed edge case has a test that fails before its fix.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_six_followups.py

## Impact

Low: each is a wording or edge-case gap.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-05 | claude | Filed |
