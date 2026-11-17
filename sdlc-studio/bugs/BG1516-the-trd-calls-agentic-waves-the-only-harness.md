# BG1516: The TRD calls agentic waves the only harness-specific feature and never describes the headless lane runner

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** sdlc-studio/trd.md, tools/tests/test_lean_trd_refresh.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, trd lens, survived 3 of 3 refute votes; observed at sdlc-studio/trd.md §7 Agentic execution (lines 681-687); §5 rule 6 (307-309) and Network paths (320-338); §9 Threat Model (759-768); §12 open question 3 (1291-1293); checked against .claude/skills/sdlc-studio/scripts/lib/lanes.py:604-654
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:21:28Z

## Summary

The TRD's Agentic execution section and its third open question both say the Agent-tool wave fan-out is the one part of the skill that is not harness-neutral. The shipped lane runner contradicts that: `headless_command` in `lib/lanes.py` builds command lines for five agent CLIs (claude, cursor-agent, codex, copilot and opencode), some with blanket tool permissions such as `--allow-all-tools` and `--trust` with `--force`. The TRD mentions lane runs only as rows in the local state table, so the Network paths table and the Threat Model have no row for a spawned, networked agent process with write tools. A reader rebuilding from the TRD would miss a whole execution architecture and its trust boundary, and the open question about a porting path is stale because the code already drives four other harnesses.

## Steps to Reproduce

1. Read sdlc-studio/trd.md, the Agentic execution subsection (about lines 681 to 687) and open question 3 in section 12 (about lines 1291 to 1293): both call agentic waves the one or only non-neutral feature.
2. Read `headless_command` in .claude/skills/sdlc-studio/scripts/lib/lanes.py (about lines 629 to 654): it builds argv for claude, cursor-agent, codex, copilot and opencode.
3. Search sdlc-studio/trd.md for the words headless and lane: the only hits are the local state table rows and a changelog line, none in section 7 or section 9.
4. Read the Network paths table in section 5 and the Threat Model table in section 9: neither has a row for a spawned agent CLI.

## Proposed Fix

Add a subsection to the TRD's execution architecture describing the lane runner: what `sprint.py lane run` starts, in which worktree, for which harnesses and with which permission flags. Correct the sentence that calls agentic waves the one Claude-Code-only part, and close or reword open question 3 to say which harnesses the lane runner already drives. Add a Network paths row for the spawned agent CLI and a Threat Model row for a spawned agent holding write tools, each naming the control that bounds it. Pin the new section and rows in the TRD refresh test so a later edit cannot drop them.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: The TRD's Agentic execution section and its third open question both say the Agent-tool wave fan-out is the one part of the skill that is not harness-neutral.
- [ ] **AC2** The proposed fix lands, pinned by a test: Add a subsection to the TRD's execution architecture describing the lane runner: what `sprint.py lane run` starts, in which worktree, for which harnesses and...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
