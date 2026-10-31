# US1109: Each open lesson from L-0361 to L-0450 is closed with its reason or extended after a check against the current tree

> **Status:** Ready
> **Delivers:** CR0655
> **Created:** 2026-10-31
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/retros/LESSONS.md, sdlc-studio/retros/LESSONS-SUMMARY.md
> **Epic:** EP0294
> **Points:** 3
> **Depends on:** US1108
> **Persona:** Rowan Achterberg

## User Story

**As** the skill maintainer whose lessons log steers every plan
**I want** each open lesson from L-0361 to L-0450 to be judged against the current tree, closed with its reason or extended with the check that kept it
**So that** the log states only lessons still true, and the validity lane is satisfied by judgements rather than by moved dates (D0391, CR0655)

## Acceptance Criteria

- **AC1:** Given each open lesson from L-0361 to L-0450, when the pass is done, then each is closed with its reason or extended with a reason naming the check made against the current tree, both through `lessons.py revalidate`
  - **Verify:** shell python3 .claude/skills/sdlc-studio/scripts/lessons.py revalidate --unjudged-since 2026-10-31 --range L-0361:L-0450
- **AC2:** Given the judged log, when the summary is checked, then LESSONS-SUMMARY.md is current with it
  - **Verify:** shell python3 -c "import sys; sys.path.insert(0, '.claude/skills/sdlc-studio/scripts'); import lessons; sys.exit(1 if lessons.summary_status('.').get('stale') else 0)"

## Notes

- Serves: Rowan Achterberg, End goal 3.
- Depends on BG1139, which records an extension's reason and ships `--unjudged-since`; AC1's Verify does not run until it lands.
- AC1 must fail on: a lesson in the range extended with no reason, or left untouched; a bound of the range (its first or last open lesson) skipped.
- A reason names the evidence: the gate, test, script or doc line that still makes the lesson true, or what changed so it no longer is. 'Still true' alone is not a judgement.
- Write no consuming-project name in any reason; a lesson that carries one is generalised, never quoted (the neutrality guard).
- Overlap: all five ranges share LESSONS.md and its summary; land them in sequence and regenerate the summary at each landing. Covers CR0655 AC1 and AC2.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-31 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-31 | Claude Opus 5.5 | Groomed for run four (D0392): criteria with Verify lines, each criterion's mutant, overlaps and sequence |
