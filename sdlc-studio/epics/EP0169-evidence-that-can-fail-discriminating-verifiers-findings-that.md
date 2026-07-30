# EP0169: Evidence that can fail: discriminating verifiers, findings that become detectors, and no terminal artefact with open questions

> **Status:** Draft
> **Parent:** CR0438
> **Parent:** CR0435
> **Derived Point Total:** 31
> **Parent:** CR0433
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0433. Delivers the work CR0433 requested.

## Story Breakdown

- [ ] [US0461: verify_ac lint --ratchet refuses a duplicate group the baseline does not record with a reason, and the pinned pre-commit lane set gains it](../stories/US0461-verify-ac-lint-ratchet-refuses-a-duplicate-group.md)
- [ ] [US0462: A filed finding records the lens, profile and a resolvable audit run, and the existing corpus is backfilled from its Raised-by stamps](../stories/US0462-a-filed-finding-records-the-lens-profile-and.md)
- [ ] [US0463: readiness.py detector-owed flags a lens filed in two separate audit runs and files the sized unit that will build the check](../stories/US0463-readiness-py-detector-owed-flags-a-lens-filed.md)
- [ ] [US0464: Every lens pack on disk names its detector or declares manual with a reason, the column is read by header name, and the detector set covers the runners this repo ships](../stories/US0464-every-lens-pack-on-disk-names-its-detector.md)
- [ ] [US0465: No artefact reaches a terminal status carrying unchecked Open Questions, and the 16 that already did are swept](../stories/US0465-no-artefact-reaches-a-terminal-status-carrying-unchecked.md)
- [ ] [US0568: The 108 findings that hide a run id in prose are backfilled across all five run ids, with the lens honestly unknown rather than guessed](../stories/US0568-the-108-findings-that-hide-a-run-id.md)

## Acceptance Criteria (Epic Level)

- [ ] Audit close-out compares the run's survivors against prior runs' filed findings; a class filed in two separate runs is flagged detector-owed in the run report, with the mechanical check it implies named.
- [ ] The signature convention (each lens names its mechanical detector or states manual and why) is extended from the process profile to all six shipped lens packs.
- [ ] A detector-owed class gets a sized delivery unit to implement the check in gate/validate/reconcile, and once shipped the lens pack cites the detector so finders are told what the script now catches and skip it.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
