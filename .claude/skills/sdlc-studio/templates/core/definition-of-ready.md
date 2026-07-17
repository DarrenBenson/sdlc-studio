<!--
Template: Definition of Ready
File: sdlc-studio/definition-of-ready.md
Related: reference-decisions.md, help/init.md

The project's READY bar: what a backlog item must pass BEFORE it enters a sprint.
Editable per project like the PRD/TRD - these shipped defaults are a starting point.
A criterion tagged `[check: <id>]` is machine-enforced by the named existing gate
(the id must be in the registered vocabulary; validate fails loud on an unknown id).
An untagged criterion is explicitly human-judged. Human intent and enforced rule
live in this one file so they cannot drift apart.
-->
# Definition of Ready

> Under pressure cut scope, never weaken the bar. Editing a criterion changes the
> project's bar; deleting its tag downgrades it to human-judged - visibly, never
> silently.

## Story

A story or bug is ready for a sprint when:

- [ ] The user story states who it serves and why, in the persona's terms
- [ ] Acceptance criteria are single-line checkable statements [check: grooming.acs]
- [ ] `Affects:` names the files it will touch, and they resolve [check: grooming.affects]
- [ ] `Points:` sizes it on the modified Fibonacci scale [check: grooming.points]
- [ ] It sits at or under the split ceiling - above it, decompose first [check: grooming.split]
- [ ] Its dependencies are delivered, or sequenced earlier in the same batch [check: grooming.deps]

## Sprint

A batch is ready to run when:

- [ ] Every unit meets the story-level bar above
- [ ] The batch is a DELIVERY batch - requests (RFCs/CRs/Issues) are refined into stories/bugs first
- [ ] Open clarifying questions are batched and answered before the triage STOP
- [ ] The Sprint Goal is one product-outcome sentence the operator set

## Release

A release is ready to cut when:

- [ ] The release scope is decided and recorded
- [ ] Every unit in scope is Done or explicitly carried over
