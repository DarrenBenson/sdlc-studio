# EP0219: An exemption states what would discharge it, and the mirror states what it did not compare

> **Status:** Superseded
> **Closed with findings in:** D0265 backlog sweep 2026-09-24 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md), RETIRE
> **Derived Point Total:** 10
> **Parent:** CR0496
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0496. Delivers the work CR0496 requested.

## Story Breakdown

- [x] [US0691: `forward-port --check` names the project-state files its verdict deliberately excludes](../stories/US0691-forward-port-check-names-the-project-state-files.md)
- [x] [US0692: A raised adopt_after threshold records a machine-readable restore condition beside the number](../stories/US0692-a-raised-adopt-after-threshold-records-a-machine.md)
- [x] [US0693: A fired restore condition is REPORTED, naming the number the exemption should return to](../stories/US0693-a-fired-restore-condition-is-reported-naming-the.md)
- [x] [US0694: An exemption whose condition has fired is distinguishable from one still legitimately held](../stories/US0694-an-exemption-whose-condition-has-fired-is-distinguishable.md)

## Acceptance Criteria (Epic Level)

- [ ] The forward-port check names what it does not compare. `--check` reports the scope of its verdict, naming project-state files (`sdlc-studio/.config.yaml`, `.local/`) as deliberately outside the mirror, so `in sync` cannot be read as `everything is current`.
- [ ] A grandfathering threshold carries a machine-readable restore condition. A raise to `conformance.adopt_after`, `provenance.adopt_after` or `engagement_floor.adopt_after` records the condition alongside the number in a form a tool can evaluate - which units the exemption exists for, and what discharges it.
- [ ] A fired restore condition is reported. When the condition holds, a gate lane or a status advisory says the exemption is discharged and names the number it should return to; an exemption whose condition has fired is a finding, not a silence.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-24 | Claude Opus 5.5 | Backlog sweep D0265 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md): RETIRE - exemption restore-condition bookkeeping for adopt_after thresholds: a new ledger on grandfathering the deletions make moot |
