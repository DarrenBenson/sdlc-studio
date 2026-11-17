# CR-0727: Remove the superseded review-seat-charter template now that nothing references it

> **Status:** In Progress
> **Decomposed-into:** EP0315
> **Priority:** Low
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/templates/personas/review-seat-charter.md, tools/tests/test_persona_templates_referenced.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, personas lens, survived 2 of 3 refute votes; observed at .claude/skills/sdlc-studio/templates/personas/review-seat-charter.md Final line: 'This pointer remains so existing references do not break.'
> **Date:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:29:13Z

## Summary

The shipped template templates/personas/review-seat-charter.md was superseded by amigo-template.md and kept as a pointer, and its final line says it remains so existing references do not break. No such reference exists any more: nothing in the shipped skill, its scripts or its help names the file, and the personas template list in help/references.md leaves it out. The reference an earlier bug quoted in `project_upgrade.py` has gone from the scripts. The only live mention in the repository is a fixture string in tools/tests/`test_check_neutrality.py`, which does not depend on the file existing. The file is therefore a dead duplicate pointer that every install carries.

## Impact

A consuming project that browses the personas templates finds two seat templates and a pointer whose stated reason is false, and may start a new seat from the superseded one. Maintainers carry a file whose only purpose ended when the last reference was removed.

## Acceptance Criteria

- [ ] templates/personas/review-seat-charter.md is no longer in the shipped skill
- [ ] A search of the shipped skill, install.sh, install.ps1 and tools/ finds no path reference to review-seat-charter.md that expects the file to exist
- [ ] A test in tools/tests/`test_persona_templates_referenced.py` fails when a file under templates/personas/ is named by no shipped reference page, help page or script, so a pointer kept for references that no longer exist is caught

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Raised |
