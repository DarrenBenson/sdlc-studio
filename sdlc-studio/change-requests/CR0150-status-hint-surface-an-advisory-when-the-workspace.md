# CR-0150: status/hint surface an advisory when the workspace carries artifact changes this session did not make

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Date:** 2026-07-04
> **Created-by:** sdlc-studio file

## Summary

Two sessions worked this repo's workspace concurrently on 2026-07-04: one filed CR0141, the other superseded it with CR0142 (deleting a script and staging doc edits) - and the first session discovered the in-flight work only by tripping over a gate failure mid-commit. The tools are collision-safe at the id level (next_id honoured the other session's file), but nothing SIGNALS a concurrent actor. status and hint are the re-anchoring commands; a one-line advisory there closes the awareness gap cheaply.

## Acceptance Criteria

- [ ] uncommitted or untracked changes under the sdlc-studio/ workspace are surfaced by status (and hint) as a one-line advisory naming the artifact ids affected, e.g. 'workspace has uncommitted artifact changes: CR0142 (new), _index.md - another session may be mid-flight'
- [ ] the advisory is informational only - it never blocks and never guesses authorship; git absence degrades silently
- [ ] unit tests pin present/absent cases; CHANGELOG [Unreleased]

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | audit | Raised |
