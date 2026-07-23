# EP0146: Extend --fields-file to the remaining prose writers

> **Status:** In Progress
> **Derived Point Total:** 8
> **Parent:** CR0392
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0392. Delivers the work CR0392 requested.

## Story Breakdown

- [ ] [US0391: critic.py and close_owed.py accept --fields-file via the shared helper](../stories/US0391-critic-py-and-close-owed-py-accept-fields.md)
- [ ] [US0392: telemetry.py and sprint.py accept --fields-file and the registry is emptied of the four](../stories/US0392-telemetry-py-and-sprint-py-accept-fields-file.md)
- [ ] [US0393: the flag path reports a detected shell hazard rather than silently altering the field](../stories/US0393-the-flag-path-reports-a-detected-shell-hazard.md)

## Acceptance Criteria (Epic Level)

- [ ] Each of critic.py, `close_owed.py`, telemetry.py and sprint.py accepts a --fields-file carrying every free-prose field as data, sharing the one helper `file_finding` already exposes rather than growing a second idiom.
- [ ] `KNOWN_PROSE_WRITER_GAPS` is empty of these four once they are converted, and its test still fails if a new prose writer is added without the path.
- [ ] The flag path survives for compatibility on each, and reports a detected shell hazard rather than silently altering a field.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
