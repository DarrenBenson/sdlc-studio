# BG0705: The Findings-filed-to line survives a reopen, is not reported in text output, and names only the filed subset of a partial repair

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Evidence:** Independent delivery review, RUN-01M2JA6J 2026-09-15: verdicts/US0628-delivery-engineering.txt (engineering seat); verdicts/US0628-delivery-qa.txt (qa seat); verdict rows in sdlc-studio/reviews/critic-verdicts.md.
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Done to In Progress keeps 'Findings-filed-to: BG0002', whereas Verification depth is retracted by `_retract_depth` on the same path (transition.py:1537-1538), so the line reads as a live discharge on an open unit. Text-mode set output never reports the write: `_print_result` prints `forced_override` but not `findings_filed_to` (transition.py:1869-1877); only --format json shows it, and --dry-run does not preview it. A close over a partial repair (with --force) writes a line naming only the filed subset, with nothing marking the findings still outstanding; the real ledger's US0662 and US0663 read partial with filed ids (transition.py:1555-1559). Unpinned: swapping `is_delivered_terminal` for `is_terminal_status` survives, so a decision-terminal close would write the line; removing the de-duplication survives because `_ids_on` returns a set; no negative case covers filed closures from a plan-review repair (transition.py:1432-1435, 1555).

## Steps to Reproduce

1. Close a unit whose delivery repair filed a finding to BG0002, then python3 .claude/skills/sdlc-studio/scripts/transition.py set <unit> 'In Progress' - the Findings-filed-to line remains. 2. transition.py set <unit> Done - the text output does not mention the line, and --dry-run does not preview it. 3. With a partial repair, transition.py set <unit> Done --force - the line names only the filed ids.

## Proposed Fix

Retract or annotate the line on reopen as `_retract_depth` does. Print it in text output and preview it under --dry-run. Mark outstanding findings when the repair is partial. Pin the delivered-terminal predicate, the de-duplication and the plan-review exclusion.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Done to In Progress keeps 'Findings-filed-to: BG0002', whereas Verification depth is retracted by `_retract_depth` on the same path (transition.py:1537-1538)...
- [ ] **AC2** The proposed fix lands, pinned by a test: Retract or annotate the line on reopen as `_retract_depth` does.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Filed |
