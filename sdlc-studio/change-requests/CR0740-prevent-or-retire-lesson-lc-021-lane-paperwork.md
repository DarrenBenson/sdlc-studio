# CR-0740: Prevent or retire lesson LC-021 (lane paperwork the landing refuses)

> **Status:** Deferred
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** sdlc-studio/lessons.jsonl
> **Date:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M7NTY5 close, 2026-11-18T10:02:57Z

## Summary

The failure class LC-021 (lane paperwork the landing refuses) recurred 2 time(s) after it was recorded in RUN-01M6RZQZ, while its rule was injected into the work. A rule that is read and repeated anyway needs the path it fails on fixed, not another reading and not one more check. This CR carries the class and its evidence, not a design.

Rule: A reference at its line ceiling gains a line only by cutting one no test or Verify line greps, a changelog fragment opens with `<!-- section: Added|Changed|Fixed -->` and a blank line, and self-check rulings are bare: exactly TRUE, FALSE or UNVERIFIABLE.

Behaviour asked of the agent: Run the Verify lines that grep a reference before cutting from it; put evidence in the claim text, name only the allowed surfaces (commit message, changelog.d/<UNIT>.md, Resolutions, docstrings, comments, CHANGELOG), record each mutant as killed or survived against a test file in the unit's Affects, and begin no wrapped fragment line with `+`, `-` or `*`.

Hits:

- RUN-01M7GEHM (retro:RETRO0147)
- RUN-01M7NTY5 on BG1574 (retro:RETRO0149)

## Impact

Every lane and review the class reaches: each repeat of LC-021 has cost a review round, 2 so far.

## Acceptance Criteria

- [ ] The code path each recorded hit names (its finding is under Hits above) is fixed, so the failure LC-021 describes cannot recur there: RUN-01M7GEHM (retro:RETRO0147); RUN-01M7NTY5 on BG1574.
- [ ] Any check this CR proposes names the lane, refusal, baseline or pin it retires, and ships only in exchange for it; a check that retires nothing is not added.
- [ ] Once the path is fixed and this CR closes Complete, LC-021 reads `graduated` in sdlc-studio/lessons.jsonl; a class that no longer describes a live failure is Rejected here instead, and the close then retires it until it recurs.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Raised |
| 2026-11-23 | Claude Opus 5.5 (run twenty-three orchestrator) | Triaged by the product seat during run twenty-three planning: Deferred (D0592) |
