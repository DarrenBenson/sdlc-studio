# CR-0013: TRD deployment topology lists six targets but hides that codex and agents share one directory

> **Status:** Complete
> **Priority:** Low
> **Type:** Improvement
> **Requester:** Project Audit
> **Date:** 2026-06-20
> **Affects:** trd.md
> **Depends on:** --
> **GitHub Issue:** --

## Summary

Section 8 presents six install targets with vague directory-convention text, obscuring that codex and agents both resolve to .agents/skills and omitting the real per-tool paths.

## Problem

trd.md:350-359 lists six targets, showing Codex -> 'Codex skills directory' and agents -> '.agents/skills/sdlc-studio/' as if distinct. install.sh resolves both codex:local and agents:local to .agents/skills (its help text states 'codex and agents resolve to the same directory'), and omits the concrete gemini (~/.gemini/skills) and opencode (~/.config/opencode/skills) paths. So six targets map to five distinct directories.

## Proposed Changes

### Item 1: TRD deployment topology lists six targets but hides that codex and agents share one directory

**Priority:** Low **Effort:** TBD

Replace the vague directory column with concrete paths from install.sh (claude .claude/skills, codex/agents .agents/skills, gemini ~/.gemini/skills, opencode ~/.config/opencode/skills, copilot .github/skills) and note codex and agents share .agents/skills.

## Impact Assessment

### Existing Functionality

A migration following the TRD would expect six separate install locations and miss that one .agents/skills copy serves Codex, Gemini, Copilot and Cursor - the actual portability story.

## Acceptance Criteria

- [x] Replace the vague directory column with concrete paths from install.sh (claude .claude/skills, codex/agents .agents/skills, gemini ~/.gemini

## Out of Scope

- Implementation is downstream; this CR records the audit finding.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (tooling-honesty-sprint) | Complete - doc-truth fix actioned directly (doc-only) |
| 2026-06-20 | Project Audit | Filed from the 2026-06-20 project-profile audit (lens: trd) |
