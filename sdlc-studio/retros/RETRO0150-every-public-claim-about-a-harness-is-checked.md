# RETRO-0150: Every public claim about a harness is checked against the tree, and a guard written for a phrase misses its cousins

> **Date:** 2026-11-18
> **Run:** RUN-01M7QMZ0
> **Batch:** US1315, US1316, US1317, US1318, US1319, US1320, US1321, BG1599

## Keep

- Reviewers proving each public sentence by running what it describes: US1316's reviewer ran the shipped init.py in a throwaway project and found the page claimed git hooks the skill never installs, US1317's checked all 39 links, every config key and every network call against the installers, and US1318's ran `--target auto` on a fake host.
- Resuming the reviewer who rejected a unit for its round-two review: US1316, US1320 and US1321 were judged again by the seat that found the defect, and all three passed in round two.
- Sending the reviewer whose finding became a bug to review the fix: BG1599 was judged by the US1319 reviewer, who had not seen it built, and both source findings closed in one round.
- Two waves of parallel lanes landed serially from one background job (D0530): seven units in five lanes, no land racing another.
- Folding a review's non-blocking findings into the open bug for the same file: BG1597 and BG1600 gather six reviews' test gaps instead of a bug per finding.

## Stop

- Stop prescribing exact wording in a criterion without checking it against the CR's constraints: US1319's AC1 prescribed "where the harness has sub-agents", an untested claim CR0742 rules out, so an APPROVE shipped it and BG1599 was added in-run (D0531).
- Stop claiming a denylist guard refuses a concept: US1316's AC4 and US1320's AC1 were rejected in round one, and US1319's test was flagged, for phrasings next to the listed ones, while each changelog said the guard refused the whole idea.
- Stop planning a run without its goal's seat review: run seventeen's goal was never reviewed (the recorded review was of an earlier goal), `sprint plan` only advised, and the close met the gap past its window (BG1601).
- Stop writing a markdown code span with a space at its edge in a filed finding or a verdict: BG1592's text blocked a paperwork commit and US1316's verdict was refused by `critic.py record`, both on MD038.

## Try

- [LC-018] A unit whose test is a phrase guard states in its changelog the phrasings it lists, not the concept, and its builder plants the nearest cousins (a synonym, a modal, a version, a list item) before handing back; US1316, US1319 and US1320's reviews each found cousins the builder had not tried.
- [LC-021] Until BG1591 lands, every lane brief names the allowed claim surfaces (commit message, changelog.d/<UNIT>.md, Resolutions, docstrings, comments, CHANGELOG) and says a page path refuses the self-check; US1321's land was refused on a docs-page surface and every later brief carried the rule.
- At refine, read each criterion that prescribes public wording against the request's Constraints section, so a wording the CR forbids is caught before the build, not by the review (US1319, BG1599).

## Machinery share (D0440)

Delivered 8 units, 25 points: the 7 planned (23 points) and BG1599 added in-run under D0531 (2 points). None of it is process machinery by theme: it is the public surface CR0742 asked for (the README, docs/harnesses.md, docs/enterprise.md, the package and skill metadata, llms.txt, the install and why pages, the evidence page's Model column and the GitHub About text). The tests each unit added pin that surface; they gate no other work.

## Known issues carried

| id | ruling | ruled by | date |
| --- | --- | --- | --- |
| BG1591 | not-stop-ship | orchestrator | 2026-11-18 |
| BG1592 | not-stop-ship | orchestrator | 2026-11-18 |
| BG1593 | not-stop-ship | orchestrator | 2026-11-18 |
| BG1594 | not-stop-ship | orchestrator | 2026-11-18 |
| BG1595 | not-stop-ship | orchestrator | 2026-11-18 |
| BG1596 | not-stop-ship | orchestrator | 2026-11-18 |
| BG1597 | not-stop-ship | orchestrator | 2026-11-18 |
| BG1598 | not-stop-ship | orchestrator | 2026-11-18 |
| BG1600 | not-stop-ship | orchestrator | 2026-11-18 |
