# US0361: a shared fields-file and stdin helper in sdlc_md.py, adopted across the remaining prose scripts

> **Status:** Draft
> **Delivers:** CR0351
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0125
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/decisions.py, .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/ledger.py, .claude/skills/sdlc-studio/scripts/handoff.py, .claude/skills/sdlc-studio/scripts/tests/test_prose_writer_hazard.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py

## Already delivered - this story is the residue

`file_finding.resolve_prose_fields` / `load_fields_file` shipped as the ONE shared loader,
and `artifact.py`, `file_finding.py`, `critic.py`, `close_owed.py` and `sprint.py` all route
their prose through it. The prose-writer sweep in `test_artifact.py` records them as safe, and
`telemetry.py` / `mutation.py` as safe-by-nature. None of that is re-done here.

Three things named by the request are still absent, and only they are in scope:

1. no writer accepts `-` for stdin, so a document produced by another process must be spilled
   to a temporary file first;
2. the sweep only looks for six flag spellings (`--steps`, `--fix`, `--summary`, `--impact`,
   `--note`, `--goal`), so four writers taking prose under other names -
   `decisions.py --rationale`, `lessons.py --body`/`--reason`, `ledger.py --rationale`,
   `handoff.py --title` - are invisible to it rather than accounted for;
3. those four writers have no non-shell input path.

The helper's home is settled by what shipped: it lives in `file_finding.py`, not in
`lib/sdlc_md.py` as the request assumed. Every writer imports it from there, so the request's
real requirement - one implementation, no second idiom to drift - holds. Moving it now would
churn five callers for a filename; the divergence is recorded here instead.

## User Story

**As an** agent filing prose that quotes commands, paths and identifiers
**I want** every writer that takes free text to read it from a document rather than a shell argument, including one piped in
**So that** a backtick in the text is stored as written instead of being executed and silently removed

## Acceptance Criteria

### AC1: a fields-file of `-` reads the document from stdin

- **Given** a JSON fields document on stdin rather than on disk
- **When** a writer is run with `--fields-file -`
- **Then** the document is read from stdin and its fields are used, with a backticked value
  stored byte-for-byte
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_prose_writer_hazard.py::StdinFieldsDocumentTests::test_a_fields_file_of_dash_reads_the_document_from_stdin

### AC2: the sweep enumerates the prose spellings it currently cannot see

- **Given** `decisions.py`, `lessons.py`, `ledger.py` and `handoff.py` take free prose under
  `--rationale`, `--body`, `--reason` and `--title`
- **When** the prose-writer sweep enumerates the scripts directory
- **Then** all four are enumerated as prose writers, so a writer taking prose under a new flag
  name cannot pass the sweep by being unnamed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::ProseWriterSweepTests::test_the_sweep_enumerates_body_rationale_and_reason_spellings

### AC3: the four remaining writers take the shared fields-file path

- **Given** the four writers the widened sweep now enumerates
- **When** each is asked for its parser options and run with a fields document
- **Then** each accepts `--fields-file`, resolves its prose through `resolve_prose_fields`, and
  is listed in `SAFE_INPUT_WRITERS` rather than as a gap; the flag path still works and still
  reports a mangled field
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_prose_writer_hazard.py::RemainingProseWriterTests::test_the_four_remaining_writers_take_a_fields_file

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-24 | sdlc-studio | Groomed: real ACs + Affects authored |
| 2026-07-24 | claude | Built - `--fields-file -` reads the document from stdin in the shared loader; the sweep widened past its six flag spellings; `decisions`, `lessons`, `ledger` and `handoff` take the shared fields-file path. 3 tests RED first, 8 hand-mutants all killed |
