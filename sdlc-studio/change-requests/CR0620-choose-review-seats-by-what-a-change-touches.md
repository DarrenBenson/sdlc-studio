# CR-0620: Choose review seats by what a change touches, not engineering for every unit

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Feature
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/persona_resolve.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_persona_resolve.py
> **Evidence:** homelab consuming project, 2026-10-07/08 (RUN-01M4B5HP drift-check sprint, RUN-01M4BZZ9 HA sprint), operator-approved after a session retrospective
> **Date:** 2026-10-08
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-08T11:05:50Z

## Summary

In the homelab's RUN-01M4B5HP every independent delivery review ran the engineering seat (Kit Devane), although the project defines QA (Mara Feld), product (Rowan Ash) and SRE (Idris Locke) seats. The work was monitoring and alerting: a scheduled check pushing to Uptime Kuma. The defects the engineering reviewer found late were SRE-shaped - Kuma maxretries semantics (one failing push PENDING, the second DOWN), a single transient run possibly paging, host file content (a cron line with an inline password) reaching the alert text. An SRE seat at plan or review would have owned those questions. Proposal: `critic.py brief` and the plan-time seat review pick seats from the unit's Affects and type - monitoring/alerting/cron paths add SRE; UI or user-facing surfaces add product; test-only changes add QA - with a project-overridable path->seat map in .config.yaml, and the brief names why each seat was chosen. A unit can still pin a seat explicitly.

## Acceptance Criteria

_None yet: add them here, or on the stories `refine` decomposes this into._

## Triage

- Confirmed at 194951eb: `critic.py brief` requires `--seat`, so the caller picks every seat and nothing derives one from a unit's Affects or type; the run reviewed every unit from the engineering seat because that is what was asked for.
- Priority Medium stands; Size M (a seat-selection rule in config, applied by `brief` and the plan-time seat review). Related: CR-0622 (a second, different seat on high-risk units) - both decide which seats review a unit and should be refined together.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-08 | sdlc-studio | Raised |
| 2026-10-08 | Claude Opus 5.5 (triage) | Triaged: behaviour confirmed; Affects made repository paths; Size M; relations recorded |
