# BG0305: parse_story's naive fence toggle executes Verify lines nested inside a double fence

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** High
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0

## Summary

The fence toggle treats any line starting with the 3-char marker as a closer, so inside a four-backtick markdown outer fence an inner three-backtick text opener mis-closes the fence and illustrative Verify lines become live shell verifiers, executed by verify_ac run and gate.py's release lane. transition.py fixed this exact bug class (close only on same char at >= opening length) but the rule was never applied to the parser that feeds shell execution.

## Steps to Reproduce

Evidence (`parse_story`, lines 120-133 (fence handling)): Repro: a story whose body opens a four-backtick markdown fence containing a three-backtick text opener, followed by an illustrative Verify line of the form dash, bold Verify marker, then "shell echo INJECTED and exit 1", yields that line as AC1's live verifier. verify_ac.py:127-133 uses stripped[:3] with no length rule; transition.py:280-289 implements the correct CommonMark rule with a comment naming the same failure.

## Proposed Fix

Port transition.py's fence rule into `parse_story`: record the fence character and opening length, and close only on a run of the same character at least that long.

## Acceptance Criteria

### AC1: an inner fence inside a longer fence does not release the block

- **Given** the defect as filed in Steps to Reproduce
- **When** the repair is in place
- **Then** the behaviour is the one the Proposed Fix describes, proven by a test written red before the fix
- **Proven by:** `pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::FencedVerifyTests::test_inner_fence_inside_a_longer_fence_does_not_release_the_block`, written red before the fix and green after
- **Verified:** yes (2026-07-27, functional)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Filed |
| 2026-07-27 | Claude Fable 5 | Affects corrected to the fix footprint incl. its test file (BG0343: the filer wrote the evidence location) |
