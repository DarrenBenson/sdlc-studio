# US0245: derive RFC decision rows from the finding's real options, not the content-free boilerplate row

> **Status:** Review
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py
> **Epic:** EP0079
> **Points:** 3

## User Story

**As an** agent filing a finding as an RFC
**I want** the generated decision rows to name the finding's real options
**So that** the RFC arrives with a decision worth taking rather than a row nobody can act on

## Acceptance Criteria

### AC1: Derive decision rows from the finding's design options

- **Given** a finding filed as an RFC with two or more design options
- **When** file_finding.py renders the RFC body
- **Then** the Open Decisions table states the choice between those named options, taking its wording from the options rather than from a fixed string
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_file_finding.py -k RfcDecisionRowsFromOptionsTests
- **Verified:** yes (2026-07-19)

### AC2: Retire the content-free boilerplate row

- **Given** any finding filed as an RFC, with or without options supplied
- **When** file_finding.py renders the RFC body
- **Then** the literal row "Act on this finding or keep status quo" is never emitted; a finding with no usable options gets a row that names the finding's own subject instead
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_file_finding.py -k RfcBoilerplateDecisionRowRetiredTests
- **Verified:** yes (2026-07-19)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
