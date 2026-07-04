# BG0041: old-persona-model detector is name-based and its remediation hint misdirects

> **Status:** Closed
> **Created:** 2026-06-25
> **Created-by:** sdlc-studio new
> **Severity:** medium

## Summary

`project_upgrade._old_persona_model` flags the legacy persona model **structurally**, not by
content: the nested dir names (`team/`, `stakeholders/`), an old-model section heading regex
(`_OLD_PERSONA_HEADING`: Backstory/Psychology/Decision Drivers/Personality/Interaction Guide), and
the literal word `\bamigo\b` in `index.md`. So a faithful rewrite of persona *content* to the
Cooper/charter models does not clear the flag - it only clears once the operator moves directories
and rewords the index. Worse, the manual remediation hint actively misdirects:

> "old persona model present - rewrite to the Cooper model (persona-template.md) / review-seat
> charters (review-seat-charter.md)" (`project_upgrade.py:175`)

The hint points at content rewriting, which is exactly the work that does NOT clear the detector.
The operator spent the whole first pass rewriting content, then found the flag only cleared after a
dir move + index reword.

## Steps to Reproduce

1. A project with personas under `personas/team/` and `personas/stakeholders/`, plus `amigo` in
   `index.md`.
2. Rewrite every persona's content to the Cooper model. Re-run `project upgrade --dry-run`.
3. It still reports "old persona model present - rewrite to the Cooper model" - because the trigger
   is the dir names + the word "amigo", not the content. The hint named the wrong fix.

## Proposed Fix

Make the hint name the **actual** trigger that fired (e.g. "nested persona dirs `team/`,
`stakeholders/` present - move personas flat under `personas/` and remove the word 'amigo' from
index.md", or "old-model heading found in `<file>`"). Report which structural signal tripped so the
operator fixes the right thing first time. Optionally separate "structural layout drift" (move dirs)
from "content-model drift" (rewrite) as two distinct findings, since they need different fixes.
Unit test: each trigger yields a hint that names its own cause. Relates to [[BG0040]] (the validate
side) and [[CR0120]] (the amigo/seat overlap from the same upgrade). CHANGELOG.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-25 | field | Created via `new` (deterministic) |
