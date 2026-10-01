# BG0877: Four more places still print a schema v3 id as its hyphenless comparison key

> **Status:** Fixed
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_id_display.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** BG0825 QA review (RUN-01M3VF2J), residue of BG0825's proposed fix
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-01T16:04:40Z

## Summary

After BG0825, critic.py brief's 'Unit under review:' header, sprint.py plan's lane-partition lines, and sprint.py close's [review-coverage] and [done-gate] preflight lines still print `norm_id` (US01ABCDEF) where the file is US-01ABCDEF-*. Also unpinned: the rejoinder-path record footer (critic.py:3107) and the retro Batch line (sprint.py:5720), both correct today.

## Steps to Reproduce

1. A v3 project with story US-01ABCDEF. 2. critic.py brief --unit US-01ABCDEF -> header prints US01ABCDEF. 3. sprint.py plan and close print US01ABCDEF in the lane and preflight lines.

## Proposed Fix

Print `sdlc_md.display_id` at those four sites, and pin the rejoinder footer and Batch line.

## Acceptance Criteria

### AC1: every print site names a v3 id in its file's spelling

- **Given** a schema v3 project holding story `US-01ABCDEF` in an open run
- **When** `critic.py brief --unit US-01ABCDEF --seat qa`, `critic.py brief --rejoinder`, `sprint.py plan` and `sprint.py close` run, and the close scaffolds the retro
- **Then** the brief header, the rejoinder footer, the plan's lane-partition lines, the close's review-coverage and done-gate preflight lines and the retro's Batch line each print `US-01ABCDEF`, never `US01ABCDEF`
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_id_display.py::IdDisplayTests::test_every_remaining_print_site_uses_the_file_spelling
- **Verified:** yes (2026-10-01)
- **Fails-on:** the current code, whose brief header, plan lane lines and close preflight lines print the hyphenless key

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Filed |
| 2026-10-01 | engineering seat (orchestrator) | Groomed mid-run: premise executed by the BG0825 reviewer at c986139f, one criterion with a Verify selector |
