# EP0244: One concept, one name, across every verb and every document key

> **Status:** Draft
> **Derived Point Total:** 10
> **Parent:** CR0559
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0559. Delivers the work CR0559 requested.

## Story Breakdown

- [ ] [US0804: Every verb identifying a unit accepts `--unit`, including `verify_ac run` where it is refused today](../stories/US0804-every-verb-identifying-a-unit-accepts-unit-including.md)
- [ ] [US0805: A `--fields-file` document whose keys are spelled as the verb's own flags is accepted](../stories/US0805-a-fields-file-document-whose-keys-are-spelled.md)
- [ ] [US0806: A deprecated alias still works and says once that it is deprecated](../stories/US0806-a-deprecated-alias-still-works-and-says-once.md)
- [ ] [US0807: The surface reference names the accepted flags and document keys per verb](../stories/US0807-the-surface-reference-names-the-accepted-flags-and.md)

## Acceptance Criteria (Epic Level)

- [ ] Given any verb that identifies a unit, when it is invoked with `--unit <id>`, then it is accepted - including `verify_ac run`, where it is refused today
- [ ] Given a `--fields-file` document whose keys are spelled as the verb's own flags, when it is read, then those keys are accepted rather than refused as unknown - measured on `file_finding file` with `ac` and `option`, and on `decisions add` with `status`
- [ ] Given the canonical name is chosen, when the deprecated alias is used, then it still works and says once that it is deprecated - a rename that breaks existing callers costs more than the inconsistency it removes
- [ ] Given the surface reference is regenerated, then it names the accepted flags and document keys per verb, so the divergence cannot silently return

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Created via `new` (deterministic) |
