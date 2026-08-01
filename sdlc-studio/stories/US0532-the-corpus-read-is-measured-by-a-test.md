# US0532: The corpus read is measured by a test that fails if it grows back to per-unit, so the fix cannot silently regress

> **Status:** Done
> **Delivers:** CR0465
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py
> **Epic:** EP0181
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** an engineer maintaining reconcile
**I want** the corpus read count pinned by a test that fails if it scales with the unit count
**So that** the fix cannot silently regress into per-unit reading as the workspace grows

## Acceptance Criteria

### AC1: the read count grows LINEARLY with the corpus, not quadratically, so a regression to per-unit reddens

- **Given** a workspace whose unit count is doubled, swept by a detector pass that looks up every unit
- **When** the sweep runs over both
- **Then** the reads grow about twofold and not about fourfold, because a cached sweep reads each file once however many lookups ask for it while an uncached one re-walks the corpus per lookup; the pin is the boundary between those two growth rates, so a return to per-unit reading fails the test rather than only slowing the gate
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::CorpusReadOnceTests::test_the_read_count_does_not_scale_with_unit_count
- **Verified:** yes (2026-07-31)

### AC2: the file walk behind the lookups is memoised, and that is pinned separately

- **Given** a sweep that walks the artefact corpus twice inside one cache window
- **When** the reads are counted
- **Then** the second walk reads nothing, because the ratio pin above passes on the lookup index alone - deleting the walk memo leaves it green, so the memo needs a verifier of its own rather than an assumed share of AC1's
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::CorpusReadOnceTests::test_a_repeated_file_walk_reads_the_corpus_once
- **Verified:** yes (2026-07-31)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Opus 5 | Groomed: criteria authored against this story's slice, each with an executable Verify line |
| 2026-07-31 | Claude Opus 5 | Independent review REJECTed this unit and was right twice. AC1's "the number of corpus reads is unchanged" was false - reads double - and the fixture behind it made a constant six lookups whatever the corpus size, so both the cached and uncached cases were linear and the asserted ratio sat at 2.0 either way: neutering the cache cost a ninefold read increase and moved the assertion by nothing. AC1 now states the linear-versus-quadratic boundary it actually measures, and the fixture scales its lookups with the corpus. AC2 added: the walk memo was covered only by a sibling test, so AC1's verifier alone left it deletable. See BG0456. |
