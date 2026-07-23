# CR-0403: Add a vibe-coding lens to the audit: find where work was done without first establishing the contract it depends on

> **Status:** Complete
> **Decomposed-into:** EP0115
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/audit.py,.claude/skills/sdlc-studio/templates/audit-profiles/test.md,.claude/skills/sdlc-studio/reference-audit.md
> **Date:** 2026-07-22
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren Benson; human; operator observation at the RUN-01KY3MFX close, filed by Claude Opus 4.8

## Summary

This skill is described as the antidote to vibe coding, and RUN-01KY3MFX showed its own author doing it throughout - which means the project has no check for the thing it exists to prevent. CR0382 shipped a `test` lens attacking claims that tests and comments make; this asks for the sibling lens attacking the PROCESS that produced them. The signature is uniform and mechanically searchable: work done before the contract it depends on was established. Instances measured in one sprint - a repair written straight from a finding with no plan, ten times, each round manufacturing the next round's defects; a path written from memory with the wrong prefix six times when the tree was one command away; a CHANGELOG block inserted without reading the section structure, orphaning existing entries; a field written as an id range without checking the parser's contract, publishing a number wrong by three orders of magnitude; a nine-minute whole-workspace run started without checking whether a scoped form existed; a `-k` selector matching nothing nearly read as a pass. None was caused by not knowing the rule. Several happened minutes after the rule was written down by the same author. What is missing is a lens that looks for the SHAPE rather than trusting the discipline.

## Impact

Every consuming project, and this one most of all: a tool that claims to be the antidote to vibe coding and cannot detect it in its own delivery is making a claim it does not check - which is precisely the defect class its own reviews have found in nine consecutive rounds. The audit surface, the lens format and the refute panel all already exist, so this is a new pack rather than new machinery.

## Acceptance Criteria

- [ ] A `process` (or equivalently named) audit lens profile ships alongside `test`, with lenses drawn from failures this project actually produced rather than invented ones.
- [ ] Each lens names a mechanically detectable signature where one exists - a commit that repairs a review finding with no recorded plan; an artefact field whose value was never resolved against the tree; a hand-maintained count or enumeration beside the mechanism it describes.
- [ ] Where a signature is NOT mechanically detectable, the lens says so rather than implying a check that does not exist.
- [ ] Every lens cites the incident it derives from, so a reader can weigh it against evidence rather than assertion.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | Darren Benson | Raised |
