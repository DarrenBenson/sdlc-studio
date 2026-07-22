# US0291: Derive shared-file clusters from the files a unit's ACs and verifiers name, not Affects alone

> **Status:** Done
> **Delivers:** CR0347
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Epic:** EP0095
> **Points:** 5

## User Story

**As an** operator parallelising a batch from the planner's waves
**I want** the shared-file clusters to include the test files each unit will touch
**So that** two agents are not sent at one file because neither unit declared it

## Context

`breakdown` fills `files_by_unit` from `_affects_files` alone, and `_shared_file_clusters` unions
over that. Every file the analysis can see is therefore a file somebody declared. Test files are
almost never declared, so the one file parallel work most often shares is the one the analysis is
blind to: CR0347 records US0252 and US0256 both writing
`.claude/skills/sdlc-studio/scripts/tests/test_reconcile.py`, which neither declared, two agents
editing it concurrently, and the suite failing with an import error belonging to neither.

A unit's own ACs already name those files. `- **Verify:** pytest <path> -k <name>` names the test
file the unit will write, in a grammar `verify_ac._build_command` already parses for every DSL
verb. Deriving the paths from that parser rather than from a second private regex is what keeps
the planner's idea of a verifier target identical to the one the verifier runs.

Derived is not declared, and the two must stay distinguishable. A shared file is a FACT and
belongs in the cluster; an `Affects` line is a DECLARATION and is what the grooming gate judges.
Letting a derived path satisfy the gate would disarm it - a unit with no `Affects` at all would
pass because it happened to cite a test path.

## Acceptance Criteria

### AC1: two units sharing only an undeclared test file are one cluster

- **Given** two units whose `Affects` lines have no file in common, and whose Verify lines both
  target the same test file
- **When** the batch breakdown runs
- **Then** the two are reported as one shared-file cluster naming that test file, so the wave
  computation stops calling them safely parallel
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_units_sharing_an_undeclared_test_file_are_one_cluster
- **Verified:** yes (2026-07-22)

### AC2: the derived paths come from the verifier parser, not a second regex

- **Given** Verify lines across the DSL verbs that carry a path, including `pytest`, `file` and
  `grep`
- **When** the planner derives the files a unit will touch
- **Then** each path is the one `verify_ac` resolves for that expression, so the planner and the
  verifier cannot disagree about what a Verify line targets
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_derived_files_come_from_the_verifier_parser
- **Verified:** yes (2026-07-22)

### AC3: a cluster says which of its files were declared and which were derived

- **Given** a cluster whose files come from both sources
- **When** the clusters are reported
- **Then** each file records which source it came from, so an operator can tell a declaration
  from a fact the planner worked out
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_cluster_files_record_declared_or_derived
- **Verified:** yes (2026-07-22)

### AC4: a derived path never satisfies the grooming gate

- **Given** a unit with no `Affects` line whose ACs name several files
- **When** the breakdown runs
- **Then** it is still reported ungroomed for a missing `Affects`, while its derived files still
  join the cluster analysis
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_derived_files_do_not_satisfy_the_affects_gate
- **Verified:** yes (2026-07-22)

## Open Questions

- [ ] CR0347 says the analysis must include "the test files a unit will touch". A path named in
  AC prose but in no Verify line is not covered here, because prose has no grammar to parse and a
  path-shaped token in a sentence is as often an example as a target - Owner: operator

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-22 | sdlc-studio | Groomed against CR0347 AC1, _shared_file_clusters and the verifier DSL parser |
