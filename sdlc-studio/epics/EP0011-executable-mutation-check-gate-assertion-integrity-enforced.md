# EP0011: Executable mutation-check gate (assertion integrity, enforced)

> **Status:** Done
> **Created:** 2026-07-04
> **Created-by:** sdlc-studio new
> **CR:** CR-0134
> **RFC:** RFC-0022 (Accepted - textual-mutation core, framework lane opt-in, static pre-filter)
> **Test Spec:** [TS0002](../test-specs/TS0002-mutation-check-gate-test-spec.md)

## Summary

The skill's named biggest blind spot made executable: apply a declared, bounded mutation set to
the changed surface, re-run the AC-mapped tests, and report **killed vs survived** - a surviving
mutation (test still green with the feature broken) is a finding, never a silent pass. Same
code plus same set gives the same report; cost proportional to the changed surface; a surface
the engine cannot mutate is reported **un-checked**, never passed. Complements `verify_ac` (checks pass) with the
can-it-fail question; v1 gate lane is advisory.

## Story Breakdown

- [x] [US0051: Textual mutation engine: declared fault classes, language profiles, anchored apply/restore](../stories/US0051-textual-mutation-engine-declared-fault-classes-language-profiles.md)
- [x] [US0052: Runner bridge and mutation report: killed vs survived per mutation, honest un-checked degrade](../stories/US0052-runner-bridge-and-mutation-report-killed-vs-survived.md)
- [x] [US0053: Mutation CLI lanes: story/files/since selection, static assertion pre-filter, cost ceiling](../stories/US0053-mutation-cli-lanes-story-files-since-selection-static.md)
- [x] [US0054: Gate wiring and docs: advisory mutation lane, discipline prose links to the executable gate](../stories/US0054-gate-wiring-and-docs-advisory-mutation-lane-discipline.md)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | sdlc | Created via `new` (deterministic) |
