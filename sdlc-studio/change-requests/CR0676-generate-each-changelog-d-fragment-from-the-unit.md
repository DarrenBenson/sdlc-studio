# CR-0676: Generate each changelog.d fragment from the unit's title and acceptance criteria with one command instead of hand-writing it, so builders stop learning the format and the fragment stops over-claiming

> **Status:** Proposed
> **Parent:** RFC0062
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/sprint.py, AGENTS.md, .githooks/pre-commit, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** RFC0062 Phase 3, ceremony lens: finding 3 and the ceremony_sub.py role split
> **Date:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T12:23:20Z

## Summary

In run six 145 calls touched changelog.d at 1.82M (builders 76 calls 1.02M, orchestrator 9 calls 0.42M, reviewers 15 calls 0.20M, repairs 17 calls 0.18M; `ceremony_sub.py).` Only 25 were the Write or Edit (0.30M); the rest were builders learning the format (cat 11, ls 7, sed 4) and git and markdownlint on it. Run five: 203 calls, 5.71M. 18 of 20 REJECT rows since 2026-11-02 cite a changelog.d file in their issues cell, at least 4 as a fragment over-claim (BG1163, US1110, US1113, BG1167). The rule lives in AGENTS.md and the changelog-shape lane, and reference-agent-prompt-template.md carries no fragment obligation. This repository only; already true of the tree.

## Impact

This repository's builders pay about 13k a call to learn a format a tool could write, and a fragment over-claim costs a REJECT.

## Acceptance Criteria

- [ ] `artifact.py changelog <id>` writes changelog.d/<id>.md from the unit's title and acceptance-criteria headlines in the shape the changelog-shape lane reads, and the lane passes it unedited.
- [ ] `sprint.py lane land` writes the fragment when the hand-in has none, and the lane brief names the command instead of describing the format.
- [ ] A hand edit to a generated fragment is kept, and the changelog-shape lane still refuses a malformed hand-written fragment.
- [ ] Before and after: on the next sprint builders make at most 2 changelog.d calls per unit against run six's 5.8 (76 over 13).

## Recommendation

Add the generator and call it from lane land. Saving 0.89M per run: builders 1.02M x 13/14 (BG1236's builder goes with the sweep lane) = 0.95M, reviewers 0.20M x 0.67 (the review spend left once the first-time-right CRs land) = 0.13M, repairs about 0.05M of the 0.18M once most round 2s go, less one generate call and an optional edit per unit (12 x 1.5 x 13.4k = 0.24M). The orchestrator's 0.42M lies inside the orchestrator replay, which is why this is below the ceremony lens's orchestrator-inclusive 1.5M. Risks: notes become terser and restate the criteria `verify_ac` proves, so a nuance an author would have written is lost unless added by hand; the over-claim class disappears rather than going unnoticed; a reviewer still reads the fragment as a claim surface.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Raised |
