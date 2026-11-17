# EP0368: PyYAML is a required dependency, refused at install and at every gate, and the specs say so

> **Status:** Draft
> **Derived Point Total:** 13
> **Parent:** CR0731
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0731. Delivers the work CR0731 requested.

## Story Breakdown

- [ ] [US1296: Both installers refuse on a machine that cannot import PyYAML, naming it and how to install it](../stories/US1296-both-installers-refuse-on-a-machine-that-cannot.md)
- [ ] [US1297: The config reader refuses without PyYAML, so no command reads a present config as the shipped defaults](../stories/US1297-the-config-reader-refuses-without-pyyaml-so-no.md)
- [ ] [US1298: The gate prerequisite check and every gate-bearing command exit non-zero when PyYAML is absent](../stories/US1298-the-gate-prerequisite-check-and-every-gate-bearing.md)
- [ ] [US1299: The PRD, TRD and README drop the standard-library-only claim, the TRD gains the ADR and the notes name the break](../stories/US1299-the-prd-trd-and-readme-drop-the-standard.md)

## Acceptance Criteria (Epic Level)

- [ ] The installer refuses, naming PyYAML and how to install it, on a machine where it cannot be imported
- [ ] The gate prerequisite check and every gate-bearing command exit non-zero when PyYAML is absent, and no command reads a present config as defaults
- [ ] The PRD and TRD no longer claim a standard-library-only runtime, and the TRD records the ruling as an ADR
- [ ] The TRD threat model carries a row for a missing or tampered PyYAML, and a test under tools/tests pins the TRD wording (carried from CR0714, closed as superseded by this request)
- [ ] The release notes for the next version name the new requirement as a breaking change for machines without PyYAML

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
