# CR-0202: detect a disabled commit gate: nothing verifies core.hooksPath on any surface

> **Status:** Proposed
> **Priority:** High
> **Type:** tooling
> **Date:** 2026-07-09
> **Created-by:** sdlc-studio file

## Summary

Hook enablement is opt-in per clone (tools/enable-hooks.sh) and NOTHING verifies it: hooksPath is referenced only by enable-hooks.sh itself; gate.py, status.py, validate.py and the doctor-style checks never look. This clone ran unhooked for 65 commits and six markdown-breaking commits landed (see the lint bug). The stated defence-in-depth silently degrades to nothing on any clone where one command was skipped. Found by RV0007.

## Acceptance Criteria

- [ ] gate.py (advisory lane) and status.py warn when .githooks/pre-commit exists but git config core.hooksPath != .githooks
- [ ] The warning names the fix command (bash tools/enable-hooks.sh)
- [ ] A unit test covers enabled, disabled and non-git states

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | audit | Raised |
