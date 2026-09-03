# BG0642: the required status check never reports at push time, so every push to main bypasses branch protection and CI failures go unread

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .github/workflows, AGENTS.md
> **Created:** 2026-09-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Branch protection on main requires a status check named `ci`. Every push reports `Bypassed rule violations for refs/heads/main: Required status check "ci" is expected`, because the check has not run at the moment the push is evaluated - a direct push to main is always evaluated before its own CI. The bypass is therefore routine rather than exceptional, and nothing local compensates: there is no pre-push hook either. The consequence is not theoretical: the run for c458afec FAILED on 2026-09-01 and main stayed red for two days with nobody reading it, because the push had already been reported as successful.

## Steps to Reproduce

1. `git push origin main` on a clean fast-forward.
2. The remote prints `Bypassed rule violations ... Required status check "ci" is expected` and accepts the push.
3. `gh run list` shows the workflow starting AFTER the push.
4. `gh run view <id>` for the previous push shows conclusion `failure`, unread.

## Proposed Fix

Decide which the working practice is, then make one thing true. If direct pushes to main are intended - and trunk-based development is this project's recorded practice - then a required status check that can never be satisfied by that flow is the wrong control, and the honest fix is a post-push signal somebody reads: a failing run on main should reach the operator rather than sit in a tab nobody opens. If pushes are meant to wait for CI, the flow needs a PR or a pre-push gate. What must not persist is a rule that is bypassed every time and a red main that nobody notices.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Branch protection on main requires a status check named `ci`.
- [ ] **AC2** The proposed fix lands, pinned by a test: Decide which the working practice is, then make one thing true.

## Impact

Two days of red main is the measured cost, and the failure was real - the conformance lane naming seven non-conformant units. A control that is bypassed on every use trains everyone to read the bypass line as noise, so the one time it matters it reads the same as the times it did not.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-03 | sdlc-studio | Filed |
