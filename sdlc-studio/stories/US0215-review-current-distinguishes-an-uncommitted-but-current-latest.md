# US0215: review-current distinguishes an uncommitted-but-current LATEST and names the commit remedy (absorbs CR0341)

> **Status:** Review
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/sprint.py
> **Epic:** EP0072
> **Depends on:** US0217
> **Points:** 3

## User Story

**As an** operator running the sprint close
**I want** an uncommitted-but-current review told apart from a stale one
**So that** the gate stops telling me to re-run the review I just ran

## Acceptance Criteria

### AC1: A current-but-uncommitted anchor names committing as the remedy

- **Given** a `reviews/LATEST.md` that has just been re-derived and is newer than every artefact, but is not yet committed
- **When** the review-current lane runs
- **Then** it reports the anchor as current but UNCOMMITTED and names committing the close paperwork as the fix, stating that re-running `review` will not change it - the previous behaviour read the last commit time and demanded the review the operator had just run.
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_gate.ReviewCurrentDirtyTests.test_uncommitted_but_current_names_the_commit_remedy
- **Verified:** yes (2026-07-18)

### AC2: An uncommitted anchor still blocks

- **Given** the same state
- **When** the close gate runs
- **Then** the lane is still blocking with a non-zero count - an uncommitted close is not a close, so naming the honest remedy must not turn the failure into a pass.
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_gate.ReviewCurrentDirtyTests.test_uncommitted_still_blocks
- **Verified:** yes (2026-07-18)

### AC3: A genuinely stale anchor is unchanged

- **Given** an uncommitted `LATEST.md` that is nonetheless older than an artefact that changed after it
- **When** the lane runs
- **Then** it still reports staleness and still says to run `review` - the dirty-anchor path must not mask a real staleness.
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_gate.ReviewCurrentDirtyTests.test_dirty_but_genuinely_stale_still_says_run_review
- **Verified:** yes (2026-07-18)

### AC4: A committed, current anchor still passes cleanly

- **Given** a committed `LATEST.md` newer than every artefact
- **When** the lane runs
- **Then** it passes with a zero count as before, so the clean path is untouched.
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_gate.ReviewCurrentDirtyTests.test_committed_and_current_passes
- **Verified:** yes (2026-07-18)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-18 | sdlc-studio | Groomed: ACs and executable Verify lines authored (absorbs CR0341) |
