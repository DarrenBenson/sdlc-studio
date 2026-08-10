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
