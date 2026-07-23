# US0341: Each lens names its mechanically detectable signature, and where there is none it says so rather than implying a check that does not exist

> **Status:** Review
> **Delivers:** CR0403
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/templates/audit-profiles/process.md,.claude/skills/sdlc-studio/reference-audit.md,.claude/skills/sdlc-studio/scripts/audit.py,.claude/skills/sdlc-studio/scripts/tests/test_audit_profiles.py
> **Epic:** EP0115
> **Points:** 3

## User Story

**As a** finder agent handed one lens and told to hunt with it
**I want** each lens to state the signature that finds it, and to say plainly when there
is none
**So that** I search the tree where a search can settle the question, and reason where it
cannot, instead of trusting a cell that reads like a check and is not one

## Context

The failure mode this story exists against is a lens row phrased as though a command
stands behind it when nothing does. That is the same class the pack hunts: a label
claiming more than the thing behind it. So the pack carries a signature column the parser
surfaces as its own field, and a lens with no mechanical signature declares that in a
fixed form with its reason, which puts it where a reader can weigh it rather than where it
is indistinguishable from a detector.

The parser is extended rather than the column being read out of the raw markdown: a fifth
column the parser drops is a column a later edit can empty without anything noticing, and
a test that reads the file as text proves only that somebody wrote a sentence.

Whether a declared detector actually fires on the failure it claims cannot be settled by
any test that ships with the pack - the detector is a search over a history the test does
not have. AC4 owns that and says `manual` rather than implying a check that does not
exist, which is the same honesty this story requires of the pack.

## Acceptance Criteria

### AC1: every lens declares a signature, and the parser carries it as its own field

- **Given** the process pack and `audit.parse_pack`
- **When** each lens row is parsed
- **Then** every lens exposes a non-empty `signature` field of its own, distinct from
  `hunts` and `drawn_from`, so a lens shipped with the column blank is a parse the tests
  can see rather than a cell the parser silently drops
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_audit_profiles.py::ProcessLensSignatureTests::test_every_process_lens_declares_a_signature_the_parser_carries
- **Verified:** yes (2026-07-23)

### AC2: a lens with no mechanical signature says so, with its reason

- **Given** a lens whose failure class no search can single out
- **When** its parsed signature is read
- **Then** the cell declares the absence in the fixed form the pack documents and states
  why the class resists a search, and the parse marks it as not mechanical - a blank cell,
  a dash or a hedged sentence is a failure of this criterion, not a way of passing it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_audit_profiles.py::ProcessLensSignatureTests::test_a_lens_with_no_mechanical_signature_declares_it_and_gives_a_reason
- **Verified:** yes (2026-07-23)

### AC3: a signature claiming to be mechanical names something that can be run

- **Given** every lens whose parsed signature is marked mechanical
- **When** the signature is inspected
- **Then** its leading token is one of the detectors the pack documents, and every path it
  names exists in the tree, so a signature cannot claim a command or a file that is not
  there
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_audit_profiles.py::ProcessLensSignatureTests::test_every_mechanical_signature_names_a_detector_and_paths_that_exist
- **Verified:** yes (2026-07-23)

### AC4: each mechanical signature is shown to fire on its own incident and not on a clean neighbour

- **Given** a lens whose signature is declared mechanical, and the incident it cites
- **When** the signature is run by hand over that incident's commit range and over an
  adjacent range with no instance of the class in it
- **Then** it reports the incident and stays silent on the clean range; a signature that
  reports nothing anywhere, or everything everywhere, is recorded as not mechanical and
  moved to the declared-absent form rather than kept
- **Verify:** manual run each declared signature over the cited incident's range and a clean neighbouring range, and record both outcomes in the run report - no shipped test holds a history to search, so this cannot be executable here

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
