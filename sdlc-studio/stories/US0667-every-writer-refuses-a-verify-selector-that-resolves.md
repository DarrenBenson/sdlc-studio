# US0667: Every writer refuses a Verify selector that resolves to nothing, naming the near miss, and reuses selector_resolves rather than reimplementing it

> **Status:** Done
> **Delivers:** CR0508
> **Created:** 2026-08-11
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py
> **Epic:** EP0215
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** Every writer refuses a Verify selector that resolves to nothing, naming the near miss, and reuses selector_resolves rather than reimplementing it
**So that** CR0508 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1

- **Given** a writer minting an artefact whose `Verify:` line names a REAL test file and a REAL
  method but the WRONG class - the exact shape that recurred twice on 2026-07-30
- **When** the artefact is written through `file_finding.file` and through `artifact.py new`
- **Then** BOTH refuse, nothing is allocated and nothing is written, and the refusal names the
  selector and the near miss it can find.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py -k a_verify_selector_naming_no_test_is_refused_at_write
- **Verified:** yes (2026-08-11)
- **Mutant:** in `file_finding.py`, remove the selector check from the write path.

### AC2

- **Given** the same check
- **When** the question "does this selector resolve" is asked
- **Then** it is answered by `verify_ac.selector_resolves` and by nothing else, proven by
  replacing that function and asserting BOTH writers follow - a second implementation of this
  question is the divergent-reader defect this repository has now filed four times.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py -k one_reader_answers_whether_a_selector_resolves
- **Verified:** yes (2026-08-11)
- **Mutant:** in `file_finding.py`, inline a copy of the resolution test that differs on a method-in-another-class selector.

### AC3

- **Given** an artefact whose `Verify:` line resolves correctly
- **When** it is written
- **Then** it is accepted, proving the guard discriminates rather than refusing every write.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py -k a_resolving_verify_selector_is_accepted
- **Verified:** yes (2026-08-11)
- **Mutant:** in `file_finding.py`, make the selector check refuse unconditionally.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `file_finding.py`, delete the selector check from the write path | |
| AC2 | in `file_finding.py`, replace the shared call with an inlined copy that differs on a method-in-another-class selector | |
| AC3 | in `file_finding.py`, change the selector check to refuse unconditionally | |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-11 | sdlc-studio | Created via `new` (deterministic) |
