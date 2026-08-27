# EP0220: An upgrade proposes its grandfathering, records each grant, and can still answer for it a year later

> **Status:** Draft
> **Derived Point Total:** 19
> **Parent:** CR0497
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0497. Delivers the work CR0497 requested.

## Story Breakdown

- [ ] [US0695: The upgrade ENUMERATES the grandfathering it proposes, per gate, before applying any of it](../stories/US0695-the-upgrade-enumerates-the-grandfathering-it-proposes-per.md)
- [ ] [US0696: Each granted exemption writes a durable artefact naming the era, the reason and the re-arm condition](../stories/US0696-each-granted-exemption-writes-a-durable-artefact-naming.md)
- [ ] [US0697: A pre-adoption cohort is discharged by a stub RETRO rather than by a baseline file](../stories/US0697-a-pre-adoption-cohort-is-discharged-by-a.md)
- [ ] [US0698: A stub retro is visibly a stub, and the accuracy and velocity paths exclude it from both sides](../stories/US0698-a-stub-retro-is-visibly-a-stub-and.md)
- [ ] [US0699: `status` shows the standing exemptions and their re-arm conditions on demand](../stories/US0699-status-shows-the-standing-exemptions-and-their-re.md)

## Acceptance Criteria (Epic Level)

- [ ] The upgrade ENUMERATES the grandfathering it proposes before applying any of it: for each gate, the cohort it would exempt, its size, the date range it spans, and what the project would be held to afterwards. Nothing about a project's own history is decided for the operator.
- [ ] Each granted exemption writes a durable artefact, not a config comment: what was exempted, the era and why that era could not have met the rule, who confirmed it, and the condition that would re-arm it. A machine-readable condition, on the same terms as CR0496.
- [ ] A pre-adoption cohort is discharged by a RECORD rather than by a baseline file. A stub retro naming the cohort and stating that these units closed before the close-down was mandated satisfies `close_owed` the same way a real retro does, and reads as what it is - a stub - rather than as a sprint that happened.
- [ ] A stub is visibly a stub. It states it accounts for no delivery, carries no lessons and contributes nothing to velocity, and the accuracy and velocity paths exclude it from both sides rather than recording it as a sprint with zero cost.
- [ ] The upgrade REPORTS what it grandfathered at the end, and `status` can show the standing exemptions and their re-arm conditions on demand, so an exemption granted at adoption is visible a year later without reading YAML.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Created via `new` (deterministic) |
