# BG0985: sprint close --dry-run reports a non-blocking pre-flight row as a STOP refusal and exits 1, so a close that would proceed previews as refused

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_close_dry_run_nonblocking.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, changelog.d/BG0985.md
> **Evidence:** Found running a consuming project RUN-01M4APNQ against this repo's main 922b9d6c (the BG0962 fix), 2026-10-07. Code read at sprint.py close_dry_run (~7314) and its blocker loop (~7343).
> **Created:** 2026-10-07
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-07T14:12:58Z

## Summary

`close_dry_run` copies every pre-flight blocker into the preview as a refusal: `for blocker in pre['blockers']: note(blocker['stage'], 'refuse', ...)`, ignoring each row's own `blocking` flag. The pre-flight deliberately carries non-blocking rows (BG-era change: 'a lane that says reported and is reported nowhere has been switched off'), e.g. gate.py's review-current lane returns `blocking: False` with the text 'CADENCE DEBT (reported, not blocking) ... so the close proceeds'. The dry run then prints `STOP gate: review-current: CADENCE DEBT (reported, not blocking)`, sums it as `dry run: 1 refusal(s)`, and exits 1, while `pre['ready']` is true and every chain step previews ok. An operator reading the preview believes the close will refuse and may run a repo-wide unified review, or waive a lane, to clear a refusal the real close never makes.

## Steps to Reproduce

On a run whose units are all independently covered but whose `reviews/LATEST.md` is stale: `sprint.py close --retro <id> --goal-verdict achieved --note x --dry-run`. Output: `STOP gate: review-current: CADENCE DEBT (reported, not blocking)` ... `dry run: 1 refusal(s)`, rc=1, with every chain step `ok`.

## Proposed Fix

In `close_dry_run`, note a pre-flight row with `blocking: False` as an advisory status (rendered with the `_blocker_label` 'reported, not blocking' wording), exclude it from `blockers`, and keep `clean`/the exit code driven by blocking rows only - matching what the real close does.

## Acceptance Criteria

- [ ] **AC1** A dry run whose only pre-flight row is non-blocking prints no STOP line, counts no refusal, and exits 0, while still showing the advisory row
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_dry_run_nonblocking.py -k advisory_row_not_a_refusal
- [ ] **AC2** A blocking pre-flight row still previews as a refusal and exits 1
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_dry_run_nonblocking.py -k blocking_row_still_refuses

## Triage

- Reproduced at 34a7ee59 by the code path: `close_dry_run` notes every row of `pre['blockers']` as a refusal (sprint.py:7343), while `close_preflight` computes `ready` from the held rows only (`not held_blockers(blockers)`, sprint.py:7092), so a non-blocking row previews as a STOP. The loop dates from 210791b6 (2026-07-29) and non-blocking rows from ae95ce04 (2026-08-11); not a regression.
- Related, not duplicates: BG0971 (the dry run's step lines read as past actions) and BG0557 (Fixed: a dry-run STOP the real close did not raise, a different cause). The three are the dry run disagreeing with the close it previews. Reconcile's US0777 advisory dismissed: US0777 (Won't Implement) concerned reporting out-of-batch units, not the dry run's blocking.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | Claude Opus 5.5 | Filed |
| 2026-10-07 | Claude Opus 5.5 (triage) | Triaged: reproduced at 34a7ee59 by the code path, not a regression; consuming-project name generalised; BG0971 and BG0557 cross-referenced; changelog fragment added |
