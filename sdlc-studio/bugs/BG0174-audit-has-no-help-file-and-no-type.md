# BG0174: audit has no help file and no Type Reference row - the universal '{type} help' contract 404s for the one command with a mandatory pre-flight gate

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/help/, .claude/skills/sdlc-studio/SKILL.md
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5; agent; audit-process-retro wf_9903a6e6-53a

## Summary

SKILL.md promises '/sdlc-studio {type} help' for any type and its Instructions step 2 says 'Load Help File: Read help/{type}.md', but help/audit.md does not exist (in the repo or the installed copy) and audit has no row in SKILL.md's Type Reference table - it appears only in the Progressive Loading Guide. An agent invoking '/sdlc-studio audit' hits a failed Read before recovering via reference-audit.md (observed 2026-07-16), and 'audit help' has nothing to load. Every other shipped command has a help/ file; audit is the one whose pre-flight cost gate most needs a crisp entry page.

## Steps to Reproduce

1. Run /sdlc-studio audit (or audit help). 2. Follow SKILL.md Instructions step 2: Read help/audit.md. 3. File-not-found; note audit is also absent from the Type Reference table.

## Proposed Fix

Add help/audit.md (command forms, the `audit_cost.py` pre-flight gate, profiles, triage-then-approve default, pointers to reference-audit.md and the templates) and an audit row to SKILL.md's Type Reference table.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 | Filed |
