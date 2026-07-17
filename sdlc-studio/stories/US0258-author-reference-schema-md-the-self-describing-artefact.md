# US0258: Author reference-schema.md: the self-describing artefact schema contract

> **Status:** Ready
> **Delivers:** RFC0047
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-schema.md, .claude/skills/sdlc-studio/help/references.md
> **Epic:** EP0084
> **Points:** 5

## User Story

**As a** tool author consuming a sdlc-studio workspace from outside the skill
**I want** a single self-describing reference documenting the on-disk artefact format
**So that** I can parse artefacts against a promised contract instead of vendoring field knowledge and chasing every release

## Context

RFC0047 option B. The contract covers exactly six surfaces, each already enforced in code but nowhere gathered: id grammar, directory layout, per-type header fields, status vocabulary and transition gates, the Verify-line DSL, and the derived index format. The document describes what exists today - it invents nothing. Section headings below are fixed anchors: consumers link to them, so their exact names are part of the contract. `.local/` is explicitly out of scope (RFC0047 D2). Source material: `lib/sdlc_md.py`, `validate.py`, `transition.py`, `reference-verify.md#verify-dsl`, `templates/core/*.md`, `templates/indexes/*.md`.

## Acceptance Criteria

### AC1: The contract document exists and states its schema version

- **Given** a checkout of the skill
- **When** a consumer opens `.claude/skills/sdlc-studio/reference-schema.md`
- **Then** the masthead states the current schema version (the same value US0259 puts in config) and that the doc is the public artefact-format contract
- **Verify:** grep "Schema version" .claude/skills/sdlc-studio/reference-schema.md

### AC2: All six contract surfaces are present as fixed section anchors

- **Given** the contract document
- **When** its level-two headings are listed
- **Then** the six surfaces appear with exactly these names: `Id Grammar`, `Directory Layout`, `Header Fields`, `Status Vocabulary`, `Verify DSL`, `Index Format`
- **Verify:** shell test "$(grep -cE '^## (Id Grammar|Directory Layout|Header Fields|Status Vocabulary|Verify DSL|Index Format)' .claude/skills/sdlc-studio/reference-schema.md)" -eq 6

### AC3: The binding rule and the two supporting rules are ratified in the text

- **Given** the contract document
- **When** a consumer reads its opening section
- **Then** it names `validate.py` as the executable definition of the contract, states that health judgements stay upstream (consumers run the skill's conformance tooling, never re-implement it), and states that `_index.md` is derived output whose only write path is the skill's scripts
- **Verify:** grep "executable definition" .claude/skills/sdlc-studio/reference-schema.md

### AC4: .local/ is explicitly uncontracted

- **Given** the contract document
- **When** a consumer looks for runtime evidence JSON (sprint plan, verify reports, telemetry)
- **Then** a scope statement says `.local/` is uncontracted in schema v1 and names a future annex as the path for evidence consumers (RFC0047 D2)
- **Verify:** grep "uncontracted" .claude/skills/sdlc-studio/reference-schema.md

### AC5: The document is catalogued and passes the repo gates

- **Given** the new reference file
- **When** the repo guards run
- **Then** `help/references.md` carries its row, the file is within the standard reference line budget, and every link in it resolves
- **Verify:** shell grep -q "reference-schema.md" .claude/skills/sdlc-studio/help/references.md && python3 tools/check_budgets.py && python3 tools/check_links.py

### AC6: The change is recorded in the changelog

- **Given** the commit that ships the contract
- **When** CHANGELOG.md is read
- **Then** the [Unreleased] section records the new reference-schema.md contract
- **Verify:** grep "reference-schema" CHANGELOG.md

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-17 | sdlc-studio | ACs groomed: 6 executable ACs, fixed section anchors, D2 scope statement |
