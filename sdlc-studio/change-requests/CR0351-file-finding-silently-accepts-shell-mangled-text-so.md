# CR-0351: file_finding silently accepts shell-mangled text, so a filed artefact can record the wrong thing

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/reference-scripts.md
> **Date:** 2026-07-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Every field reaches `file_finding` through a shell argument. A backtick in the text is a command substitution, so the shell replaces it with the output of whatever it ran - usually nothing, plus a command not found on stderr. The artefact is then written and indexed with a hole where the evidence was. This happened twice in one session to an agent that had the lesson in front of it, and once produced a bug whose Summary read 'US0251 AC2 runs .' with the command gone. The filer refuses a hollow artefact when a required FIELD is missing; it has no opinion about a field that arrived corrupted. Naming a command or a path is exactly what a finding is for, and backticks are the natural way to write one.

## Impact

A filed finding is the durable record of something learned. Silent corruption at the moment of filing means the record can be wrong in precisely the detail that made it worth filing, and nothing surfaces it - the artefact validates, indexes and reads as complete.

## Acceptance Criteria

- [ ] the filer detects a field that arrived empty or truncated where content was supplied, and refuses rather than writing it
- [ ] the documented filing path does not require the caller to shell-escape prose - a stdin or file-based form for the long fields, so evidence containing backticks, dollars or quotes survives verbatim

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Raised |
