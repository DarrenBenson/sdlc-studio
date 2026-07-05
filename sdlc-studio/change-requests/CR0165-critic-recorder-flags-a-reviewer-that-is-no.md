# CR-0165: critic recorder flags a reviewer that is no declared seat - the persona lens must not drift out silently

> **Status:** Complete
> **Priority:** Medium
> **Type:** Improvement
> **Date:** 2026-07-05
> **Created-by:** sdlc-studio file

## Summary

The adversarial critic discipline held through four sprints but the SEAT framing drifted out unnoticed: verdicts recorded under free-text reviewer strings (adversarial-critic, independent instance) instead of the QA amigo whose review render exists for exactly this job, and nothing flagged it. critic.py record gains an advisory: when the project declares personas (seats/ or amigos/ with role fields) and --reviewer matches none of them by role or card name, print a warning naming the declared seats - advisory, never a refusal, silent on projects without personas. Reference docs state the critic runs AS the QA seat's review render via persona_resolve.

## Acceptance Criteria

- [ ] critic record warns when --reviewer matches no declared seat/amigo role or name, naming the declared options; recording still succeeds
- [ ] a reviewer matching a declared role (e.g. qa) or card name passes silently; a project with no personas dir stays silent
- [ ] reference-sprint (critic close pass) and reference-workflow-personas state the critic is framed with the QA seat's review render
- [ ] regression tests for match, no-match, and no-personas paths; CHANGELOG [Unreleased]

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-05 | audit | Raised |
| 2026-07-05 | Claude (tranche close) | Delivered in the token-optimisation tranche (pre-v3.5.0): Sam Eriksson (QA seat, review render) APPROVE after two adversarial rounds; details in CHANGELOG [Unreleased] |
