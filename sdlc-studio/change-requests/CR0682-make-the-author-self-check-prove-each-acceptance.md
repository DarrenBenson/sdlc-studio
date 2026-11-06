# CR-0682: Make the author self-check prove each acceptance criterion at the observable it names through the shipped entry point, list the docs outside Affects that name what the diff changed, require a captured producer sample for a unit that parses another tool's output, and tag each blocking finding with its defect class

> **Status:** Proposed
> **Parent:** RFC0062
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/templates/core/story.md, .claude/skills/sdlc-studio/templates/core/bug.md, .claude/skills/sdlc-studio/reference-agent-prompt-template.md, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** RFC0062 Phase 3, first-time-right lens: findings 4, 5, 6 and 7 and its classification; ceremony lens: finding 1 (claims tally)
> **Date:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T12:23:47Z

## Summary

Three run-six round-1 blockers held at a proxy rather than at the criterion's observable: US1117 (critic-verdicts.md:1750, AC2's priced figure only in the JSON cell), US1121 (:1749, the run window unpriced because `_priced_fields` at `run_state.py`:1301-1307 drops a non-Claude price, while the test asserts the cumulative reading) and US1119 (:1762, lane accept discards critic.py record's warnings). Run five's BG1163 changelog claim was false through the shipped verb while its self-check ruled 29 TRUE, 0 FALSE (author-self-checks.md:105). `check_self_check` (critic.py:2950-2966) requires only the commit message and fragments: the criteria are law for the reviewer and absent from the author's inventory, and the hand-ruled tally recorded FALSE 0 in all 124 rows since 2026-10-22. Both third-party-format blockers in two runs concern the Cursor CLI and were found by reading the installed vendor bundle the builder did not read (US1121 :1749, US0990 :1730). BG1236's blocker and run five's BG1116 were docs outside Affects still naming the old behaviour (:1766, :1725). This review had to classify every blocking finding by hand from free text. Already true of the tree.

## Impact

A proxy-verified criterion or a stale doc costs a round 2 (0.47M at the agent share), and the D0411 bar allows at most 20% of units in round 2 against run six's 62% (8 of 13).

## Acceptance Criteria

- [ ] The self-check lists each criterion with its quoted observable, CLAIMS.json carries one claim per criterion whose command invokes a shipped CLI rather than only a pytest selector, and `self-check record` re-runs each command once and stores its exit and an output digest; a fixture of US1119's dropped-warning case is ruled FALSE.
- [ ] `_self_check_scope` greps `reference-*.md`, `help/*.md` and README.md outside Affects for the basenames of changed scripts and the long flags the diff adds or removes, prints the hits as docs that name what changed, and `check_self_check` requires a ruling for each; a fixture reproduces BG1236's stale reference-sprint.md line.
- [ ] Story and bug templates gain an optional `Capture:` line (producer, version, recorded sample path), refine asks for it when a unit reads another tool's output, and a lint flags a unit whose Affects names a `meter_*.py` or `*_hook.py` reader without one.
- [ ] `critic.py record` accepts a defect class after the origin tag (sweep-red, vacuous-pin, proxy-observable, unstated-invariant, external-format, doc-drift, other), and the sprint report's unit table and the retro digest count round-1 blockers by class.
- [ ] Before and after: with the sweep-lane, mutation-runner and hostile-kit CRs landed, the next two sprints put at most 20% of units in a second review round.

## Recommendation

Turn the hand-ruled claims pass into executed claims per criterion, and add the doc list, the capture rule and the class tag. On tokens it is about even for run six's shape: the round 2s of US1117, US1119 and US1121 avoided at the 0.47M agent share = 1.41M (US1117 also needs the mutation runner, US1121 the capture rule), against about 1.1M of added build calls (3 criteria x 1.5 calls x 0.019M x 13 builds), 0.25M for the doc list and up to 0.11M for captures: about -0.05M, or about +0.3M if each avoided round 2 also saves 6 orchestrator calls at the 20k left after the drive loop. The lens's 1.55M uses 0.75M a unit including the orchestrator share. It earns its place on quality: by the first-time-right classification it takes run six from 4 of 12 units in round 2 to 1 of 12 once the sweep lane and the runner land, under the 20% bar. The doc list saves nothing on run six's shape, whose one instance (BG1236) the sweep lane removes; run five's BG1116 is its case. It supersedes the ceremony lens's proposal to retire the claims tally: the tally becomes executed claims, not hand rulings. Related: CR0652 and CR0658 (Proposed, claim surfaces for a doc unit's own prose). Risks: build cost rises about 0.08M a unit, and if re-running makes record slow, record the command and exit and leave the re-run to the reviewer; the doc grep over-lists, which the author rules; a wrong class tag misleads a statistic but changes no gate.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Raised |
