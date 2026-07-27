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

- **Given** an artefact declaring it supersedes another whose counterpart records nothing
- **When** reconcile detect runs
- **Then** it reports the pair and which side is missing the declaration
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::SupersessionTests::test_a_one_sided_supersession_is_reported

### AC2: every spelling the corpus carries is recognised, including the hyphenated id form

- **Given** the six declaration spellings present in the corpus and the hyphenated id forms two of them use
- **When** each is presented to the detector
- **Then** every one is recognised against a pinned grammar that normalises the hyphenated id, so neither an unenumerated spelling nor CR-0132 style is read as an absence
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::SupersessionTests::test_every_corpus_spelling_and_id_form_is_recognised

### AC3: the 11 pairs already in the corpus are waived or repaired before the kind can block

- **Given** the 11 one-sided pairs the corpus carries today, including RFC0038's deliberate partial supersession of RFC0034
- **When** the detector is introduced
- **Then** each is either repaired or waived with a stated reason, so introducing the kind cannot turn a blocking lane red across a clean repository
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::SupersessionTests::test_the_existing_pairs_are_waived_or_repaired

### AC4: a deliberately partial supersession stays waivable

- **Given** a declaration superseding only part of its counterpart, which remains live in the rest
- **When** the detector runs
- **Then** it is not reported once waived, because a partial supersession is legitimate asymmetry rather than drift
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::SupersessionTests::test_a_partial_supersession_is_waivable

### AC5: a symmetric pair is not reported

- **Given** a pair whose both sides record the supersession
- **When** reconcile detect runs
- **Then** it reports nothing, so the detector does not manufacture work
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::SupersessionTests::test_a_symmetric_pair_is_not_reported

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: acceptance criteria authored against the slice |
| 2026-07-27 | Claude Fable 5 | ACs repaired against the independent adversarial review |
