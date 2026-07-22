# CR-0399: The finding filer refuses an unresolvable Affects but will not say what the path probably was, and the same wrong prefix was typed six times in one session

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py,.claude/skills/sdlc-studio/scripts/artifact.py
> **Date:** 2026-07-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Measured on RUN-01KY3MFX. The author wrote a reference-doc path prefixed with the scripts directory - `.claude/skills/sdlc-studio/scripts/reference-review.md` instead of `.claude/skills/sdlc-studio/reference-review.md` - SIX separate times across one session, including twice inside artefacts filed about that very defect, and once minutes after ruling on it in a decision of record. Four further wrong or incomplete Affects were found by grooming agents in stories the same author minted. The refusal itself is correct and valuable: nothing is allocated and nothing is written, which is exactly right. What it does not do is close the loop. The basename `reference-review.md` is unique in the tree, so the intended file is unambiguously recoverable, and the filer knows the tree because it just failed to resolve the path in it. The consequence is a retry loop that costs a round trip each time and teaches nothing - the operator watched the same mistake six times without the tool ever naming the right answer it could see. Note the shape: this is not a knowledge problem, since the author knew the rule and had just written it down. It is a typing-shaped hazard, and a tool that can see the answer should offer it.

## Impact

Every agent and operator filing an artefact, on the hottest path in the skill. The cost is a wasted round trip per occurrence plus the risk that a frustrated caller drops the offending path from Affects entirely - which silently narrows the engagement floor's file-count signal and the plan's collision analysis, both of which read that field.

## Acceptance Criteria

- [ ] When a declared path does not resolve, the refusal names the closest match by basename where exactly one exists in the tree, and says nothing where the match is ambiguous.
- [ ] The suggestion is a suggestion: nothing is auto-corrected, because a silently rewritten Affects is a worse failure than a refused one.
- [ ] The same helper serves artifact.py, so the two filers cannot differ on what counts as a resolvable path.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Raised |
