# RETRO-0130: Maya signs a sprint report whose delivery, cost and DORA figures match what the run actually did

> **Date:** 2026-10-02
> **Run:** RUN-01M3Y7DP
> **Batch:** BG0890, BG0891, BG0892, US0979, US0980, BG0893, BG0894

## Keep

- Record each builder's spend through `lane return --tokens/--minutes` and the reviewers' at the close: this run's page measures cost per unit (1.87M tokens, 1.46x) where RPT0014 read 0.2x off the orchestrator's meter.
- Put the QA seat's control beside each criterion at the goal review, before any build: four units were caught in review on exactly the shapes the controls named.
- Log every seat ruling as it is made (D0295): eleven rulings (D0298-D0308) are on the record and on this page.

## Stop

- Committing anything while a builder works in the main tree: an `--only` commit hit the builder's ref lock, and a plain one swept its staged BG0890 repair into a chore commit that had to be split.
- Giving a reason without executing it: D0305 said signed pages read VELOCITY.md, the reviewer showed none does, and the rows were re-recorded under D0307.
- Freezing in one place and reading live in another: BG0890 and BG0895 each needed a second round for the same seam.

## Try

- [LC-014] Two collisions in one run, both from orchestrator commits made while the builder's hook ran (a ref lock, then a swept staged repair). Record verdicts as files and commit only when the builder has reported.
- [new: a signed page reads a live source | build, review] A figure on a signed page is derived only from what PREPARE froze, and a step judging the attempt in progress asks the live source, never the last attempt's freeze. BG0890 read a unit's live status after filing, and BG0895's checklist read the previous attempt's frozen gate on a re-close.
- [LC-005] BG0895's round-1 fix agreed with the page on one close and moved the disagreement to the re-close path; BG0891's first pairing passed AC1 and failed AC2 on a window ending red. Probe the second attempt and the second incident, not only the first.

## Known issues carried

| id | ruling | ruled by | date |
| --- | --- | --- | --- |
| BG0899 | not-stop-ship | Claude (orchestrator) | 2026-10-02 |
| BG0900 | not-stop-ship | Claude (orchestrator) | 2026-10-02 |
| BG0901 | not-stop-ship | Claude (orchestrator) | 2026-10-02 |
| BG0902 | not-stop-ship | Claude (orchestrator) | 2026-10-02 |
| BG0903 | not-stop-ship | Claude (orchestrator) | 2026-10-02 |
| BG0904 | not-stop-ship | Claude (orchestrator) | 2026-10-02 |
| BG0905 | not-stop-ship | Claude (orchestrator) | 2026-10-02 |
| BG0906 | not-stop-ship | Claude (orchestrator) | 2026-10-02 |
| BG0907 | not-stop-ship | Claude (orchestrator) | 2026-10-02 |
| BG0908 | not-stop-ship | Claude (orchestrator) | 2026-10-02 |
| BG0910 | not-stop-ship | Claude (orchestrator) | 2026-10-02 |
