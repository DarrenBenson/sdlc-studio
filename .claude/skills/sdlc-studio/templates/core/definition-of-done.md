<!--
Template: Definition of Done
File: sdlc-studio/definition-of-done.md
Related: reference-decisions.md, help/init.md

The project's DONE bar: the yes/no quality gate work must pass to be called
complete, at each level. Editable per project like the PRD/TRD - these shipped
defaults are a starting point. A criterion tagged `[check: <id>]` is
machine-enforced by the named existing gate (the id must be in the registered
vocabulary; validate fails loud on an unknown id). An untagged criterion is
explicitly human-judged. Human intent and enforced rule live in this one file so
they cannot drift apart.
-->
# Definition of Done

> Under pressure cut scope, never weaken the bar. A Done that is only as strong as
> whoever remembered to check it is not a bar; every tagged criterion below is
> enforced by a gate that refuses.

## Story

A story or bug is Done when:

- [ ] Its executable acceptance criteria pass and are back-annotated [check: story.verify-ac]
- [ ] An independent critic APPROVE is recorded (author never reviews its own diff) [check: review.critic-approve]
- [ ] The adversarial pass is recorded as evidence and the reviewer of record has signed off [check: review.two-role]
- [ ] Its documentation landed in the same unit (help + reference for any new command/flag)
- [ ] The paperwork shipped in the same commit as the code (changelog fragment, status, index)

## Sprint

A sprint is done when its close-down is complete:

- [ ] The batch retro exists and validates [check: close.retro]
- [ ] Lessons are extracted, revalidated, and the committed summary is current [check: close.lessons]
- [ ] The unified review is at least as new as every artefact [check: close.review]
- [ ] No index drift remains [check: close.reconcile]
- [ ] The Sprint Goal is judged (achieved / partial / missed), never defaulted

## Release

A release is done when:

- [ ] The full release gate is green [check: release.gate]
- [ ] Changelog fragments are composed into the release notes, no strays [check: release.changelog]
- [ ] Version strings agree across the authoritative files [check: release.version]
- [ ] The migration story for any breaking change ships with the change
