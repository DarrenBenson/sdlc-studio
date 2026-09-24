# BG0738: the low-severity consolidation writes a Consolidated Findings section with no blank line after the heading, so the commit that files a Low finding is refused by the markdown gate

> **Status:** Superseded
> **Closed with findings in:** D0265 backlog sweep 2026-09-24 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md), MERGE: merged into BG0731
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py
> **Evidence:** Reproduced 2026-09-22 during RUN-01M33WJ3. Filing a Low-severity bug consolidated it into CR0592, and the next commit was refused: `CR0592-low-severity-bugs-consolidated.md:21 error MD022/blanks-around-headings` and `:22 error MD032/blanks-around-lists`. The heading and its first bullet were written adjacent. Hand-fixing the derived file cleared the gate, which is the wrong remedy for a file a tool owns.
> **Created:** 2026-09-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`file_finding.py` routes a Low-severity finding into the shared consolidation CR instead of minting its own artefact. The section it writes puts the first bullet immediately under the `## Consolidated Findings` heading with no blank line between, which violates MD022 and MD032. The markdown lane is BLOCKING in the pre-commit gate, so the very next commit is refused - and the author is refused over a file they did not write, by a guard naming a file they were not editing.

## Steps to Reproduce

1. `file_finding.py file --type bug` with `--severity Low` so the consolidation path is taken.
2. Observe the written `## Consolidated Findings` section: the first bullet sits directly beneath the heading.
3. Stage anything and commit - the markdown lane refuses.

## Proposed Fix

Write a blank line after the heading and around the bullet list when composing the section, and pin it with a test that lints the composed output rather than asserting on its substrings - a test checking that the text contains the finding would pass on the malformed shape.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `file_finding.py` routes a Low-severity finding into the shared consolidation CR instead of minting its own artefact.
- [ ] **AC2** The proposed fix lands, pinned by a test: Write a blank line after the heading and around the bullet list when composing the section, and pin it with a test that lints the composed output rather than...

## Impact

A deterministic tool writes a file its own repository's blocking gate rejects, so filing a Low finding leaves the tree uncommittable until somebody hand-edits generated content - which the doctrine forbids. It also punishes exactly the behaviour the project wants, since filing findings is the standing instruction during dogfooding.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-22 | sdlc-studio | Filed |
| 2026-09-24 | Claude Opus 5.5 | Backlog sweep D0265 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md): MERGE, merged into BG0731 - BG0731 (the consolidation section disappears with the bucket) |
