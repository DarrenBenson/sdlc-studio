# CR-0245: Give operational and incident lessons a home, in the shape teams actually write them

> **Status:** Proposed
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio new
> **Provenance:** RFC0032 consequences
> **Raised-by:** sdlc-studio; agent; v1
> **Priority:** P2
> **Type:** feature

## Summary

an infrastructure project wrote a 750-line docs/ops-lessons.md OUTSIDE the workspace because the registry had no home for deploy, incident and DR lessons - the category with the most expensive failures has the least support. Real lessons are heavier than our entries: incident-anchored narrative, a tickable runbook, artefact citations (CR/BG/RFC + file:line), and a declared decay horizon. Add the category and let the template carry that shape, so teams stop routing around us.

## Impact

Teams doing deploy, incident and DR work - the category with the most expensive failures and, today, the least support in the registry. Nothing breaks; the cost of the gap is that such teams write their own lessons doc outside the workspace, where no tool reads it.

**Effort:** M

## Acceptance Criteria

- [ ] The registry supports an operational/incident lesson category alongside engineering/process. Verify: rg -q 'operational|incident' .claude/skills/sdlc-studio/lessons/_template.md
- [ ] The template carries the shape real lessons take: incident narrative, runbook/checklist, artefact citations, declared decay. Verify: rg -q 'Runbook|Checklist' .claude/skills/sdlc-studio/lessons/_template.md
- [ ] an infrastructure project's ops-lessons.md can be represented without loss - validated against the real file, not a fixture (LL0020). Verify: python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -k lessons

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Created via `new` (deterministic) |
