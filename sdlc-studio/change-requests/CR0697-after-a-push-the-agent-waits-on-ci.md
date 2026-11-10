# CR-0697: After a push, the agent waits on CI with one blocking watch, and a red run from a known flaky test follows a recorded policy

> **Status:** Proposed
> **Priority:** High
> **Type:** enhancement
> **Size:** M
> **Related:** BG1224, BG1272, US1149, CR0670
> **Date:** 2026-11-10
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren Benson (operator); human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-10T16:58:51Z

## Summary

The shipped skill tells a consuming project to commit each unit to main and push (BG1224), but says nothing about waiting for the CI run that push starts, or what to do when it fails on a test already known to be flaky. Agents fill the gap by polling, which keeps a long-lived session growing, and by stopping when they cannot rerun a job.

Evidence (2026-11-10, a consuming project delivering with Grok 4.7 through Cursor): one agent ran a whole sprint, and requests over 200k tokens made up about 58% of its bill. Replacing CI polling with one blocking watch, and starting a fresh agent every five or so units, brought the cost to about $2.58 a unit by its first estimate (the measured figures are under Evidence). Its agents cannot rerun GitHub Actions, so a known temp-folder flake waits for the operator to rerun CI by hand. Reading guidance on preventing flakes exists (reference-test-validation.md, reference-test-best-practices.md); a policy for the wait and the rerun does not.

## Impact

Serves O11 and Abena Osei's End goal 3 (cost per point), and Graham Doyle's End goal 3 (a red main is read, not pushed over). Every consuming project on trunk integration. Related: BG1224 (trunk is the default), BG1272 (the pre-push check reads only the latest run), US1149 (the session budget).

## Acceptance Criteria

- [ ] The shipped trunk guidance tells the agent to wait on its push's CI run with one blocking command under a timeout (for GitHub, `gh run watch <id> --exit-status`), never a polling loop, and to read a red main before pushing again
- [ ] A red run whose failing test is already filed as a flaky bug is recorded against that bug; the agent reruns the failed jobs once when its token allows it, or else stops and asks the operator to rerun, and never skips the test
- [ ] A red run that matches no filed flake is treated as a regression: the agent files a bug and does not push again until main is green
- [ ] A project can set the wait's timeout and the rerun limit (default one) in its config, and the defaults are documented in reference-config.md

## Evidence

A consuming project's measured cost, delivering with Grok 4.7 through Cursor and priced at xAI's API rates (double for a prompt of 200k tokens or more), from its usage exports of 6 to 10 November 2026 (supplied by the operator, 2026-11-10). One agent running the whole sprint: $282.09 over 2,181 requests for 79 points ($3.57 a point). Prompts of 200k tokens or more were 29% of its requests and 57% of its cost, and $157.11 (56%) could not be tied to any unit, because the export stamped whole runs with one time until 9 November. A fresh agent per batch: batch A cost $25.72 for 8 points ($3.22 a point; 32% of the cost in long prompts). Batch B cost $23.08 for 5 points ($4.62 a point) counting the run that prepared its units, or $12.98 ($2.60 a point) for its delivery run alone, where long prompts were still 72% of the cost. Coordinator usage ($82.54 across all batches) is outside these figures, and batch C waits on an export past 11:41 GMT on 2026-11-10. The samples are small (8 and 5 points).

The data is in `sdlc-studio/change-requests/evidence/consumer-sprint-cost-2026-11-10.tar.gz`: per-request and per-unit CSVs, batch summaries, and the time windows and script that built them (the script imports a pricing module the bundle does not include). It is a scrubbed copy of the bundle supplied (SHA-256 fc960de33f14a39f; the copy 1d814234b30c426f): the project's repository name, two other project names, the operator's name and two local paths were replaced, and every figure is unchanged.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-10 | Darren Benson (operator) | Raised |
| 2026-11-10 | Darren Benson (operator) | Evidence: a consuming project's batch cost figures |
