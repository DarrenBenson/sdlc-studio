# EP0233: A project's configuration is introduced, decided, and judged against its own measurements

> **Status:** Draft
> **Derived Point Total:** 21
> **Parent:** CR0534
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** XL

## Summary

Decomposed from CR0534. Delivers the work CR0534 requested.

## Story Breakdown

- [ ] [US0759: A command prints every configuration key in force with its value, its source and its meaning](../stories/US0759-a-command-prints-every-configuration-key-in-force.md)
- [ ] [US0760: The keys that are project JUDGEMENTS are named as such and decided explicitly as numbered decisions](../stories/US0760-the-keys-that-are-project-judgements-are-named.md)
- [ ] [US0761: The retro reads the run's measurements against the settings that governed it and proposes changes](../stories/US0761-the-retro-reads-the-run-s-measurements-against.md)
- [ ] [US0762: A proposal is never applied automatically and lands in the retro's findings table to be ruled on](../stories/US0762-a-proposal-is-never-applied-automatically-and-lands.md)
- [ ] [US0763: A setting with no measurement to judge it against is reported as UNJUDGED rather than left out](../stories/US0763-a-setting-with-no-measurement-to-judge-it.md)

## Acceptance Criteria (Epic Level)

- [ ] A command prints every configuration key in force with its effective value, its source (project file, code default, or the decision id that set it) and its one-line meaning, so an operator can answer what governs this project without reading the source
- [ ] the keys that are project judgements rather than universal truths are named as such and can be decided explicitly, each recorded as a numbered decision the way D0129 and D0130 are
- [ ] the retro reads the run's own measurements against the settings that governed it and proposes changes with the evidence attached - gate budget against measured gate time, estimator constants against the calibration record, appetite against what was delivered
- [ ] a proposal is never applied automatically and lands in the retro's findings table where it must be ruled on like any other finding
- [ ] a setting with no measurement to judge it against is reported as unjudged rather than left out, since a silent omission reads as a setting nobody needs to think about

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Created via `new` (deterministic) |
