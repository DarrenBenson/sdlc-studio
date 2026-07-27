# US0484: reconcile reports a supersession only one side of the pair records

> **Status:** Ready
> **Delivers:** CR0447
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py
> **Epic:** EP0175
> **Points:** 5

## User Story

**As a** reader navigating the RFC graph
**I want** a supersession declared on one artefact and absent from its counterpart to be reported
**So that** a superseded design cannot keep reading as live from the direction that never recorded it

## Acceptance Criteria

### AC1: a one-sided supersession is reported

- **Given** an artefact declaring it supersedes another, whose counterpart records nothing
- **When** reconcile detect runs
- **Then** it reports the pair and which side is missing the declaration
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::SupersessionTests::test_a_one_sided_supersession_is_reported

### AC2: the grammar is pinned, so a second spelling is not silently exempt

- **Given** the declaration spellings the corpus already carries
- **When** each is presented to the detector
- **Then** every one is recognised against a pinned grammar, so a spelling nobody enumerated is not read as an absence of supersession
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::SupersessionTests::test_every_corpus_spelling_is_recognised

### AC3: a symmetric pair is not reported

- **Given** a pair whose both sides record the supersession
- **When** reconcile detect runs
- **Then** it reports nothing for that pair, so the detector does not manufacture work
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::SupersessionTests::test_a_symmetric_pair_is_not_reported

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: acceptance criteria authored against the slice |
