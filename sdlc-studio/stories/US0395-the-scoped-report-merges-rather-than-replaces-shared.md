# US0395: the scoped report merges rather than replaces, shared-story verdicts identical to the unscoped run

> **Status:** Done
> **Delivers:** CR0395
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0147
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py,.claude/skills/sdlc-studio/help/verify.md,.claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py

## User Story

**As an** operator reading the verification report the Done gate reads
**I want** a scoped run to leave every out-of-scope verdict exactly as it found it,
and to return the same verdict for a shared story as the whole-workspace run would
**So that** narrowing the scope buys wall clock only - it never blanks a story's
green, never carries a stale one forward as fresh, and never changes what the gate
would have concluded

## Acceptance Criteria

### AC1: an out-of-scope entry survives a scoped run byte-for-byte

- **Given** an existing report holding entries for stories inside and outside the
  scope, each with its own `verified_at` and `ac_fingerprint`
- **When** a scoped run over the in-scope ids writes the report
- **Then** every out-of-scope entry is present and unchanged in all its fields,
  including `verified_at` and `ac_fingerprint`, so the Done gate can still tell a
  fresh green from a carried-forward one and a scoped run cannot promote a stale
  verdict by touching its timestamp
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::ScopedReportMergeTests::test_out_of_scope_entries_including_verified_at_are_untouched
- **Verified:** yes (2026-07-24)

### AC2: a scoped run and a whole-workspace run agree on every story they share

- **Given** a fixture workspace of stories with a mix of passing, failing and manual
  verifiers
- **When** the whole-workspace run and a scoped run over a subset of the same
  stories are each run against a fresh report
- **Then** the per-story entries for the shared stories are equal field for field,
  ignoring the timestamps, and the two runs return the same exit code for that
  subset - the scope decides which stories are judged, never how one is judged
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::ScopedUnscopedEquivalenceTests::test_shared_story_entries_and_exit_are_identical_under_both_scopes
- **Verified:** yes (2026-07-24)

### AC3: a rebuild combined with a scope is refused, not silently destructive

- **Given** a report holding out-of-scope verdicts
- **When** `--fresh` is passed together with a scope flag
- **Then** the command exits 2 before writing anything, saying that a rebuild
  discards every verdict outside the scope and naming the two ways forward (drop the
  scope, or drop `--fresh`) - the report is byte-identical afterwards
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::ScopedFreshRefusalTests::test_fresh_with_a_scope_exits_2_and_writes_nothing
- **Verified:** yes (2026-07-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-24 | sdlc-studio | Groomed: real ACs + Affects authored |
| 2026-07-24 | sdlc-studio | Built: out-of-scope preservation + scoped/unscoped equivalence pinned, `--fresh` with a scope refused |
