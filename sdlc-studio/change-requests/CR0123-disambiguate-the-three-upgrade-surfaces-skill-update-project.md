# CR-0123: disambiguate the three upgrade surfaces skill-update project-upgrade and schema upgrade

> **Status:** Complete
> **Created:** 2026-06-25
> **Created-by:** sdlc-studio new
> **Priority:** Low
> **Type:** Improvement

## Summary

Three distinct operations all carry the word "upgrade", and disambiguating which one an instruction
means cost a field operator a reference read mid-run:

- **`skill-update`** - update the installed skill itself to a newer version.
- **`project upgrade`** - migrate a consuming project's artefacts/conventions to the current skill.
- **schema upgrade** - the v1 -> v2 document-shape migration of individual artifacts.

"upgrade project" is ambiguous between the second and third, and "upgrade" alone collides with the
first. The split is real and the tools are correct; the naming/discovery is the friction.

## Acceptance Criteria

- [ ] help/reference text disambiguates the three surfaces in one place (what each upgrades, when to
      reach for which), cross-linked from each command's help
- [ ] the command/help wording makes the target explicit (the skill vs the project's artefacts vs an
      artifact's schema) so "upgrade" is never bare/ambiguous in user-facing output
- [ ] CHANGELOG. Low priority - documentation/wording, no behaviour change

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-25 | field | Created via `new` (deterministic) |
