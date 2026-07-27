# US0475: The sprint close derives the review record ahead of the gate, and the review-current lane demonstrably clears on a git fixture

> **Status:** Ready
> **Delivers:** CR0424
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_close_review_record.py, changelog.d/{{US-id}}.md
> **Epic:** EP0171
> **Points:** 5

## User Story

**As a** operator closing a sprint that already has an adversarial APPROVE on record
**I want** the close to derive the RV and the review stamp on the way past
**So that** the close accepts the review that exists instead of stopping for a second entry of the same verdict

## Acceptance Criteria

### AC1: AC1: the lane clears on a GIT fixture where a batch story changed after the anchor - and the condition cleared is named

- **Given** a git-backed fixture (tests/gitutil) in which reviews/LATEST.md was committed and a batch story artefact was then modified and committed AFTER it, so `gate._review_current` blocks naming that story (stale_by_anchor and stale_by_record both true; `review_prep.staleness` enumerates every artefact type, and the existing close stamps only the four doc legs, so batch stories keep `needs_review: True`)
- **When** `sprint.py close` runs with a sprint-review APPROVE covering the batch
- **Then** the lane blocks naming that story before the derivation step and, after it, `staleness()[<story>]['needs_review']` is False and the lane returns count 0, non-blocking. The condition cleared is stale_by_record via the per-unit stamp (gate.py:1236) - stated in the assertion, not inferred. A tmpdir fixture with no git repo does not satisfy this AC
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_review_record.py::CloseDerivesTheReviewTests::test_the_lane_clears_on_a_git_fixture_whose_batch_story_changed_after_the_anchor

### AC2: AC2: the derivation step precedes the gate step in the chain

- **Given** the shipped `_CLOSE_CHAIN` tuple
- **When** the index of the derivation step and of `gate` are read from the chain itself
- **Then** the derivation index is strictly lower, so the step is proven to run where it can change the lane's verdict rather than after it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_review_record.py::CloseDerivesTheReviewTests::test_the_derivation_step_precedes_the_gate_step_in_the_chain

### AC3: AC3: the derivation's own anchor write stays inside the close-status block, so it does not create the UNCOMMITTED refusal

- **Given** the same git fixture, after the close's derivation has written the anchor and before it is committed
- **When** `gate._review_current` runs with LATEST.md dirty
- **Then** `_only_close_status_block_differs` is True and the lane returns count 0 non-blocking, rather than the blocking 'current with all artefacts but UNCOMMITTED' branch a body change outside the block would produce (gate.py:1272-1284)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_review_record.py::CloseDerivesTheReviewTests::test_the_derived_anchor_write_keeps_the_uncommitted_branch_exempt

### AC4: AC4: nothing derivable leaves the gate blocking and says why

- **Given** an open run with no sprint-review row covering its batch and a stale review anchor on the same git fixture
- **When** the close runs
- **Then** the derivation step reports that it derived nothing and why, the close continues, and it still stops at the gate on the stale review - the step's own success message never stands in for a review
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_review_record.py::CloseDerivesTheReviewTests::test_no_derivable_review_leaves_the_gate_blocking_and_says_why

### AC5: AC5: re-running the close mints no second RV

- **Given** a close that derived the RV and then stopped at a later step
- **When** the close is re-run after the blocker is cleared
- **Then** the reviews directory still holds exactly one derived RV for that run, review-state.json still points at that same id, and the second pass reports the existing one as reused
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_review_record.py::CloseDerivesTheReviewTests::test_re_running_the_close_reuses_the_rv_and_mints_no_second_id

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: authored from the reviewed breakdown (two adversarial rounds), scope capped to the request per D0069 |
