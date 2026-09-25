# BG0717: the close's handoff link leaves a trailing blank line in the retro, so every close fails this project's own markdownlint

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/handoff.py, .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_handoff.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py
> **Created:** 2026-09-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Not a duplicate of BG0590, which the filer flagged for the shared Affects. BG0590 was MD004 - the bullet MARK written into a retro that uses a different one - and is Fixed; its repair is the `document_bullet` call this writer still makes. This is MD012, the blank line left AFTER the section when `## Handoff` is the document's last. Same writer, same lesson, different rule, and the first repair is what makes the second one visible.

`handoff._link_from_retro` writes the handoff bullet through `artifact._put_section(text, ('Handoff',), body)`. When `## Handoff` is the retro's LAST section - which it is in the shipped retro template - the put leaves two trailing newlines, and markdownlint fails the file with MD012/no-multiple-blanks. The close then reports success and the very next commit, which is the close's OWN paperwork commit, is refused by the pre-commit hook. The same writer already guards MD004 (it follows the document's bullet mark) and MD026 (it strips trailing punctuation from the H1), so the class of defect is known here and this case was missed. RUN-01M2SPNS hit it twice: once before re-running PREPARE and again after, because stripping the file by hand does not stop the generator re-adding it.

## Steps to Reproduce

1. In any project, run `sprint close --retro RETROxxxx --goal-verdict achieved`. 2. It reports success and links the handoff into the retro's `## Handoff` section. 3. Run `npx markdownlint-cli2 'sdlc-studio/retros/RETROxxxx*.md'` - MD012/no-multiple-blanks at the last line. 4. Try to commit the close's paperwork: the pre-commit markdown lane refuses it. Observed on RUN-01M2SPNS at RETRO0118.

## Proposed Fix

Normalise the trailing whitespace where the section is written, not at each call site: have `_put_section` (or `_link_from_retro` before its `atomic_write`) collapse three or more consecutive newlines to two and end the document with exactly one newline. `sprint_report.render_markdown` already does exactly this for the report twin, for the same reason and with the reasoning recorded there - a page the repo refuses to accept is a page the close cannot land. Add a criterion that closes a run whose retro ends at `## Handoff` and asserts the file passes MD012.

## Acceptance Criteria

- [ ] **AC1** Given a retro whose `## Handoff` section is the last in the file, when `handoff._link_from_retro` writes the handoff link, then the file ends with exactly one newline (fixed by US0877, 6729b4f3, handoff.py:759)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_retro.py::RetroTailTests::test_linking_the_handoff_leaves_exactly_one_newline

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-18 | sdlc-studio | Filed |
| 2026-09-25 | sdlc-studio v6 planning | QA seat: criteria point at the test US0877 added, so the fix it already landed can reach Fixed through transition.py (triage ruling, Sprint 5) |
