# US0014: review_prep staleness determinism

> **Status:** Done
> **Epic:** [EP0005: Quality & Drift Control](../epics/EP0005-quality-drift.md)
> **Owner:** Autosprint (CR0004, determinism-sprint)
> **Reviewer:** --
> **Created:** 2026-06-20
> **GitHub Issue:** --

## User Story

**As an** operator
**I want** review staleness derived from git commit times and compared as datetimes
**So that** the verdict is reproducible across clones and timestamp formats, not
reset by every checkout or broken by a format mismatch (CR0004).

## Context

Implements CR0004. `review_prep.staleness` now derives `last_modified` from
`git log -1 --format=%cI` (st_mtime fallback when untracked or git is
unavailable, method labelled), parses both sides with `datetime.fromisoformat`
(Z normalised, naive treated as UTC), and treats a malformed `last_reviewed` as
needs_review plus a surfaced warning.

## Acceptance Criteria

### AC1: git-derived last_modified with labelled method

- **Given** a tracked file in a git repo, and an untracked file outside one
- **When** `_modified_iso` runs on each
- **Then** the tracked file reports method `git` (the commit `%cI`) and the untracked file falls back to method `mtime`
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_review_prep_staleness.py::ModifiedTests
- **Verified:** yes (2026-06-20)

### AC2: datetimes compared format-insensitively

- **Given** `Z`, `+00:00` and naive timestamps
- **When** `_parse_dt` parses them
- **Then** `Z` equals `+00:00`, a naive value is treated as UTC, and an unparseable value is None
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_review_prep_staleness.py::ParseTests
- **Verified:** yes (2026-06-20)

### AC3: malformed last_reviewed warns and needs review

- **Given** a `review-state.json` with an unparseable `last_reviewed`
- **When** `staleness` runs
- **Then** the artifact is `needs_review` with a `warning`, not silently mis-compared
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_review_prep_staleness.py::MalformedTests::test_malformed_last_reviewed_warns_and_needs
- **Verified:** yes (2026-06-20)

## Implementation

`scripts/review_prep.py`: `_git_iso`, `_modified_iso`, `_parse_dt`; `staleness`
compares parsed datetimes and surfaces warnings; `cmd_prep` emits a `warnings` list.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (CR0004) | Decomposed from CR0004 (determinism sprint) |
