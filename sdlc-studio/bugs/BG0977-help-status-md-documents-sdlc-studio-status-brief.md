# BG0977: help/status.md documents '/sdlc-studio status --brief' but status.py has no --brief, so the documented one-line summary errors

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/status.py, .claude/skills/sdlc-studio/help/status.md, .claude/skills/sdlc-studio/scripts/tests/test_status_brief.py, .claude/skills/sdlc-studio/scripts/tests/test_status.py, changelog.d/BG0977.md
> **Evidence:** Found running a consuming project on the installed skill 6.1.0, 2026-10-07; confirmed by reading the code at sdlc-studio main fb1ce886. `status.py --brief` -> 'error: unrecognized arguments: --brief'; help/status.md lines 18, 39, 260 and project agent-instruction templates recommend it.
> **Created:** 2026-10-07
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-07T12:37:44Z

## Summary

The status help advertises `--brief` as the one-line health summary, and consuming projects' AGENTS.md files copy the recommendation into their session-start steps. status.py's parser has subcommands (pillars, points, hint, backlog, tranche, triage-metrics) and no --brief, so an agent following the doc runs a command that fails.

## Steps to Reproduce

`python3 <skill>/scripts/status.py --brief` -> unrecognized arguments.

## Proposed Fix

Add `--brief` (or a `brief` subcommand) that prints the documented single line, or correct the help and the agent-instructions template to the command that exists.

## Acceptance Criteria

- [ ] **AC1** The command help/status.md documents for the one-line summary runs and prints one line
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status_brief.py -k brief_prints_one_line

## Triage

- Reproduced at 8b844a80: `status.py --brief` exits 'unrecognized arguments: --brief'; help/status.md lines 18, 39 and 260 document it. status.py has never had the flag (documented since the initial release). Low holds: it fails loudly.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | Claude Opus 5.5 | Filed |
| 2026-10-07 | Claude Opus 5.5 (triage) | Triaged: reproduced at 8b844a80, not a regression, consuming-project name generalised for the neutrality lane; changelog fragment added to Affects |
