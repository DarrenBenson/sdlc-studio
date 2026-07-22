# US0302: Artefacts filed from survivors link back, so yield is attributable to a run

> **Status:** Draft
> **Delivers:** CR0379
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py,.claude/skills/sdlc-studio/scripts/file_finding.py
> **Epic:** EP0100
> **Points:** 2

## User Story

**As a** sprint operator weighing the mutation gate against its wall-clock
**I want** a finding filed from a surviving mutant to name the run that found it, and that run's
yield to be counted in filed artefacts rather than in raw survivor counts
**So that** the gate's value is measured by the defects it actually produced, not by a survivor
number that includes noise and equivalents

## Context

A survivor is a hypothesis, not a finding. RUN-01KY03GS produced three survivors of which two
became BG0232 and BG0233; the third produced nothing. Counting survivors would have overstated
that run by 50 per cent, and nothing on disk connects the two bug files back to the run that
raised them. `file_finding.py file` is the deterministic path an agent uses to file exactly this
kind of finding, so the link is cheap to record at filing time and impossible to reconstruct
afterwards. US0301 writes the per-run series row; this story makes the yield column of that row
mean something.

## Acceptance Criteria

### AC1: A finding filed from a survivor records the run that found it

- **Given** a mutation run recorded in the series and a survivor from that run
- **When** a Bug or CR is filed for it through `file_finding.py file` naming that run
- **Then** the filed artefact carries the run's identity and the mutated target in its metadata,
  and filing against an unknown run is refused with a message naming the run rather than stamping
  an unresolvable reference
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_file_finding.py -k MutationRunAttributionTests
- **Verified:** yes (2026-07-22)

### AC2: A run's yield is the count of linked artefacts, not its survivor count

- **Given** a run whose series row records three survivors, of which one has been filed as a Bug
- **When** the run's yield is read
- **Then** it reports one, the survivor count remains separately visible beside it, and a run with
  survivors but no filed artefact reports a yield of zero rather than inheriting its survivor count
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_mutation.py -k MutationYieldAttributionTests
- **Verified:** yes (2026-07-22)

### AC3: A survivor recorded as equivalent is excluded from yield

- **Given** a survivor that has been recorded as an equivalent mutant, meaning no behaviour changed
  and no test could have killed it
- **When** the run's yield and its outstanding-survivor count are read
- **Then** the equivalent survivor counts towards neither, and the record states it was judged
  equivalent so the exclusion is auditable rather than a silent decrement
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_mutation.py -k EquivalentMutantExclusionTests
- **Verified:** yes (2026-07-22)

## Open Questions

- Nothing in `mutation.py` records mutant equivalence today: the verdict vocabulary is
  killed / survived / error / unviable. CR0379 says an equivalent mutant "recorded as such" is
  excluded but does not say who records it or where - a fourth verdict written by a subcommand,
  or a field on the series row. AC3 is written for the exclusion behaviour, which is clear; the
  recording surface needs a decision before build.
- The CR does not say whether the link is stamped only at filing time or can be added afterwards
  to an artefact already filed. AC1 covers filing time only.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-22 | sdlc-studio | Groomed: user story and acceptance criteria authored |
