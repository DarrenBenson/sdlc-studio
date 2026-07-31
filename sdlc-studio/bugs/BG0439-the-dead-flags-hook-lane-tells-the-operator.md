# BG0439: the dead-flags hook lane tells the operator it enforces the opposite of what it enforces

> **Status:** Fixed
> **Verification depth:** functional (test red-first against the inverted line; asserted case-insensitively over the lane's own window)
> **Severity:** Low
> **Points:** 1
> **Affects:** .githooks/pre-commit
> **Evidence:** Read from the shipped hook by an independent reviewer.
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (independent adversarial review of the EP0169/EP0172/EP0175 batch); agent; skill v5.0.0
> **Raised-in-batch:** 2026-07-29T15:35:33Z

## Summary

The lane's `enforces` line reads 'no flag whose parsed destination any line acts on - a documented switch that does nothing', which states the inverse of the rule: it reads as forbidding flags that ARE acted on. AGENTS.md has it right ('no line acts on'). This is the text printed to the operator on failure, so it is read at exactly the moment it needs to be correct.

## Steps to Reproduce

1. `grep -A1 'run "dead-flags"' .githooks/pre-commit`.

## Proposed Fix

Insert the missing negation so the lane text matches AGENTS.md and the detector's actual rule.

## Acceptance Criteria

### AC1: the lane states the rule it enforces, not its inverse

- **Given** the pre-commit hook's dead-flags lane
- **When** its `enforces` line is read
- **Then** it says a flag whose destination NO line acts on, not one that any line acts on - the printed text is what an operator reads at the moment the lane refuses, and a remedy describing the inverse rule sends the reader to undo the wrong thing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py::DeadFlagTests::test_the_lane_states_the_rule_it_ENFORCES_not_its_inverse
- **Verified:** yes (2026-07-31)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | Claude Opus 5 (independent adversarial review of the EP0169/EP0172/EP0175 batch) | Filed |
