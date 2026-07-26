# BG0294: duplicate detection now has two implementations with different algorithms, so they can drift

> **Status:** Fixed
> **Verification depth:** functional
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py
> **Severity:** Medium
> **Points:** 3

## Summary

The repo answered "is this a duplicate?" two ways: `file_finding.duplicate_candidates` used
Jaccard over the open backlog, `artifact.duplicate_candidates` used containment over every
artefact. They disagreed on real data - the pair that motivated the check scored 0.21 by Jaccard
(missed) and 0.44 by containment (caught) - so which answer you got depended on the entry point.

## Steps to Reproduce

1. File a near-duplicate through `artifact.py new` - it is reported (containment, 0.44).
2. File the same through the finding filer, which used `file_finding.duplicate_candidates` - it is
   NOT reported (Jaccard, 0.21, under the bar).

## Proposed Fix

Delete the second (Jaccard) implementation. `file_finding.duplicate_candidates` now delegates to
`artifact.duplicate_candidates` across the dup-types, so both entry points answer through the one
containment detector that catches the motivating case, terminal artefacts included.

## Detail

Found and reported by the agent that delivered US0413, which is the right way for this to
surface: it was told CR0413 AC2 required one implementation, could not reach the file where the
shared one belongs, and said so rather than claiming the criterion met.

There are now two duplicate-title detectors using DIFFERENT algorithms:

| | `file_finding.duplicate_candidates` | `artifact.duplicate_candidates` |
| --- | --- | --- |
| Algorithm | Jaccard | containment |
| Scope | open artefacts only | every artefact of the type, terminal included |

They disagree on real data, and the disagreement is measured rather than hypothesised: the pair
that MOTIVATED CR0413 scores 0.21 by Jaccard - under the 0.5 bar, so the older lens would have
missed the very duplicate it exists to catch - and 0.44 by containment.

So the repo now answers "is this a duplicate?" two ways depending on which entry point is used,
and nothing holds them to the same answer. This is the two-copies-of-a-rule class that
BG0290 was filed for in `validate` and `conformance`, arriving again in a different pair.

## Impact

A defect filed through one path is reported as a duplicate and through the other is not. Worse
than either behaviour alone, because which answer you get depends on a detail no user is
tracking.

## Acceptance Criteria

### AC1: one implementation, reached from both entry points

- **Given** `artifact.py new` and `file_finding.py`
- **When** each asks whether a title duplicates an existing artefact
- **Then** both call ONE function - the second implementation is deleted, not kept in sync, because keeping two in sync is what has already failed twice here
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::DuplicateSingleSourceTests::test_both_entry_points_call_one_implementation
- **Verified:** yes (2026-07-26)

### AC2: the surviving algorithm catches the case that motivated it

- **Given** the artefact pair that motivated the original filing, which Jaccard scores 0.21
- **When** the shared detector runs
- **Then** it reports them - a consolidation that kept the weaker lens would close this bug while reintroducing the defect
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::DuplicateSingleSourceTests::test_the_motivating_pair_is_still_caught
- **Verified:** yes (2026-07-26)

### AC3: terminal artefacts stay in scope

- **Given** a defect already filed and closed
- **When** the same title is filed through either entry point
- **Then** it is reported - re-filing something already fixed wastes the most time, and the narrower scope must not win the merge
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::DuplicateSingleSourceTests::test_a_terminal_artefact_is_in_scope_from_both_paths
- **Verified:** yes (2026-07-26)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
