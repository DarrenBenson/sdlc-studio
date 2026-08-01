# US0583: A staged diff changing a literal while its own prose still states the old value is flagged, naming both sites, and a diff whose prose agrees produces no finding

> **Status:** Draft
> **Delivers:** CR0517
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/check_spec_claims.py, tools/tests/test_check_spec_claims.py
> **Epic:** EP0195
> **Points:** 5

## User Story

**As a** developer about to commit
**I want** a contradiction between my diff's code and my diff's prose flagged before I push
**So that** a stale sentence costs seconds rather than an adversarial review round

## Acceptance Criteria

> **Two severities in one script, stated rather than discovered.** `tools/check_spec_claims.py`
> is wired into the pre-commit gate as BLOCKING and its `main()` returns 1 on any error. The
> claim-drift findings must be ADVISORY while their yield is measured (D0105), so the two cannot
> share one exit code. The check reports drift findings on a separate channel that does not
> influence the return value, and the existing spec-claim errors keep the blocking contract they
> have today. A test asserts a drift finding alone exits 0 while a spec-claim error still
> exits 1. Without it, adding the lane silently converts advice into a blocked commit,
> which is where an independent seat predicted AC1's test would actually fail.

### AC1: a changed literal whose prose still states the old value is flagged

- **Given** a staged diff changing an exit code from 2 to 3 while its own changelog fragment still says 2
- **When** the claim-drift lane runs over the staged diff
- **Then** it reports the contradiction naming both the code site and the prose site, because this is decidable from the diff alone and currently costs an adversarial review round to find
- **Verify:** pytest tools/tests/test_check_spec_claims.py::ClaimDriftTests::test_a_changed_literal_contradicting_its_prose_is_flagged

### AC2: a diff whose prose agrees produces no finding

- **Given** a staged diff changing an exit code and updating every prose site with it
- **When** the lane runs
- **Then** it reports nothing - the control, so the lane cannot be satisfied by one that always fires
- **Verify:** pytest tools/tests/test_check_spec_claims.py::ClaimDriftTests::test_agreeing_prose_produces_no_finding

### AC3: prose outside the diff is not judged

- **Given** a repository full of older documents stating other values
- **When** the lane runs over one staged diff
- **Then** only claims inside that diff are considered, so the lane stays a delivery check and does not become a repo-wide audit that always finds something
- **Verify:** pytest tools/tests/test_check_spec_claims.py::ClaimDriftTests::test_only_the_staged_diff_is_judged

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
