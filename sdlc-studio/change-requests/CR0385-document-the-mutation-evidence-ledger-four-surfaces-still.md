# CR-0385: Document the mutation evidence ledger: four surfaces still describe only the single-blob report

> **Status:** In Progress
> **Decomposed-into:** EP0141
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/help/mutation.md,.claude/skills/sdlc-studio/reference-scripts-verify.md,sdlc-studio/trd.md,sdlc-studio/tsd.md
> **Date:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

BG0238 replaced last-write-wins mutation evidence with a bounded ledger keyed on each target's content hash, and changed the gate lane from judging freshness of one blob to judging coverage of the changed surface. Four documentation surfaces still describe only mutation-report.json and the old staleness model: help/mutation.md, reference-scripts-verify.md, and the project's own trd.md and tsd.md. None of them is FALSE about the report, which still exists and is still written unchanged, so this is incompleteness rather than a lie - but a reader following any of them will not know the ledger exists, will not know coverage is now the lane's verdict, and will read a STALE warning under the old meaning.

## Impact

Any agent or operator reading the mutation docs to decide when to run the gate or how to read its verdict. It matters more than an ordinary doc lag because RFC0048 D2 was resolved this same sprint to sanction test retirement on measured kill-yield, sequenced behind CR0377 and BG0238 - so the ledger is about to become the input to a decision that DELETES tests. A retirement criterion read from documentation describing the superseded single-blob model would be built on the wrong evidence shape. The trd.md and tsd.md entries additionally feed the spec-truth checks, which is the drift EP0071 had to repair across twelve stories.

## Acceptance Criteria

- [ ] help/mutation.md describes the ledger, its content-hash key, its 200-entry bound and its dropped count
- [ ] reference-scripts-verify.md describes the coverage verdict (covered / stale / uncovered) and the degraded whole-blob fallback
- [ ] trd.md and tsd.md are reconciled with the shipped behaviour, and the reconcile pass records what was found rather than only what was changed
- [ ] The docs state that the lane is advisory and never blocks, so the RFC0048 D3 decision is readable from the docs and not only from the RFC
- [ ] A reader can determine from the docs alone what makes a file's evidence stale, without reading gate.py

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Raised |
