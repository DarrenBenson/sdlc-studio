# CR-0104: Surface v3.0 capabilities in the always-loaded router + help catalogue (decisions, goal ladder, init-first, batch)

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Date:** 2026-06-24
> **Created-by:** sdlc-studio file

## Summary

Post-v2.6 discoverability gaps confirmed by the deterministic baseline: /sdlc-studio decisions (add/list/promote) is absent from help/help.md (doc-coverage passes anyway - a false-green); the sprint goal ladder (triage/plan/design/done) is not named in SKILL.md or help/help.md; init/decisions are missing from the SKILL.md Type Reference; init-as-greenfield-step-1 and artifact batch / --template full are not surfaced in the catalogue.

## Acceptance Criteria

- [ ] help/help.md lists the decisions command (add/list/promote) and names the sprint goal ladder triage->plan->design->done
- [ ] SKILL.md Type Reference includes init and decisions; the Sprint row/prose names the goal ladder
- [ ] init is surfaced as greenfield step 1 and batch/--template full are discoverable where bulk authoring is described
- [ ] doc_coverage no longer false-greens on decisions (the command registry sees it); CHANGELOG entry same commit

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-24 | audit | Raised |
