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

Evidence (2026-11-10, a consuming project delivering with Grok 4.7 through Cursor): one agent ran a whole sprint, and requests over 200k tokens made up 58% of its bill. Replacing CI polling with one blocking watch, and starting a fresh agent every five or so units, brought the cost to about $2.58 a unit. Its agents cannot rerun GitHub Actions, so a known temp-folder flake waits for the operator to rerun CI by hand. Reading guidance on preventing flakes exists (reference-test-validation.md, reference-test-best-practices.md); a policy for the wait and the rerun does not.

## Impact

Serves O11 and Abena Osei's End goal 3 (cost per point), and Graham Doyle's End goal 3 (a red main is read, not pushed over). Every consuming project on trunk integration. Related: BG1224 (trunk is the default), BG1272 (the pre-push check reads only the latest run), US1149 (the session budget).

## Acceptance Criteria

- [ ] The shipped trunk guidance tells the agent to wait on its push's CI run with one blocking command under a timeout (for GitHub, `gh run watch <id> --exit-status`), never a polling loop, and to read a red main before pushing again
- [ ] A red run whose failing test is already filed as a flaky bug is recorded against that bug; the agent reruns the failed jobs once when its token allows it, or else stops and asks the operator to rerun, and never skips the test
- [ ] A red run that matches no filed flake is treated as a regression: the agent files a bug and does not push again until main is green
- [ ] A project can set the wait's timeout and the rerun limit (default one) in its config, and the defaults are documented in reference-config.md

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-10 | Darren Benson (operator) | Raised |
