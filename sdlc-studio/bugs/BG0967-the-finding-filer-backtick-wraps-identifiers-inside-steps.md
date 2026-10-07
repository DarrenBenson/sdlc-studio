# BG0967: The finding filer backtick-wraps identifiers inside Steps to Reproduce, corrupting the shell commands a repro depends on

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding_steps_commands.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py, changelog.d/BG0967.md
> **Evidence:** Found running a consuming project on the installed skill 6.1.0, 2026-10-07; confirmed by reading the code at sdlc-studio main fb1ce886. Filing BG0949-BG0952 here: every `python3 -c "..."` repro had identifiers such as sdlc_md and critic.parse_verdict_block( wrapped in backticks, and each had to be re-fenced by hand.
> **Created:** 2026-10-07
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-07T12:36:45Z

## Summary

The markdown-safety pass that wraps `snake_case` identifiers in backticks (BG0097) runs over the `steps` field. BG0124 (won't fix) concerned Verify lines; the same pass over Steps to Reproduce turns `from lib import sdlc_md` into ``from lib import `sdlc_md` `` and `critic.parse_verdict_block(` into a broken span, so a copied repro no longer runs. A repro is the part of a bug a reviewer executes first.

## Steps to Reproduce

`file_finding.py file --fields-file f.json` where steps contains `python3 -c "import sys; from lib import sdlc_md; print(sdlc_md.x)"`. Read the filed Steps to Reproduce: identifiers are backtick-wrapped inside the command.

## Proposed Fix

Leave lines that look like commands (or any content already inside a fenced block) untouched, and emit a multi-line or command-shaped steps value as a fenced bash code block rather than prose.

## Acceptance Criteria

- [ ] **AC1** A steps value containing a shell command is filed byte-identical inside a fenced block, and still runs when copied
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding_steps_commands.py -k command_survives_filing

## Triage

- Reproduced at 8b844a80 in a scratch root: a steps value `python3 -c "import sys; from lib import sdlc_md; ..."` is filed with `sdlc_md` back-ticked and a broken span after it. Not a regression. BG0974 is the opposite failure in the same safing (the title and Evidence are left bare); fix the two together.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | Claude Opus 5.5 | Filed |
| 2026-10-07 | Claude Opus 5.5 (triage) | Triaged: reproduced at 8b844a80, not a regression, consuming-project name generalised for the neutrality lane; changelog fragment added to Affects |
