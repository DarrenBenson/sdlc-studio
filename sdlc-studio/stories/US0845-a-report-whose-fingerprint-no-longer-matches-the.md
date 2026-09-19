# US0845: a report whose fingerprint no longer matches the tree renders INVALIDATED wherever it is shown

> **Status:** Done
> **Created:** 2026-09-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/status.py, .claude/skills/sdlc-studio/scripts/tests/test_status.py
> **Epic:** EP0255
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** reviewer of record coming back to a report somebody signed
**I want** a report whose facts have moved since the signature to say so before I read a figure
**So that** a signed report cannot be quoted as current after the tree it described has changed

## Acceptance Criteria

This is the READ side of the seal; US0833 carries the write and the refusal. Both are needed
because the consult's finding was that the fingerprint is written and nothing ever reads it, so
a report stays signed while the tree moves.

RFC0059's D4 - what invalidates a signature - is open, and these criteria pin the narrowest of
its three readings: a report is INVALIDATED when RE-DERIVING it from the tree now yields a
different facts fingerprint. The two wider readings are rejected here rather than left to
delivery. "Any tracked write" marks every sealed report stale on the next commit, so the marker
stops carrying information within a day. "A write to a batch unit's declared files" invalidates
on a changelog fragment that moves no figure. Re-derivation is the only reading that is itself
re-derivable, which is the property the whole report rests on, and it uses US0835's fingerprint,
which covers the ordered figure set and excludes the signature block and the timestamp.

THE THREE TREES are copies of a run sealed under RPT0001: (i) untouched; (ii) a typo fixed in
`README.md`, a tracked write that moves no figure the report carries; (iii) a batch unit's
`Points:` changed from 5 to 8, so `points_delivered` moves. (ii) is the discriminating one -
every reading of D4 agrees about (i) and (iii).

### AC1: invalidation is decided by re-deriving the facts, not by counting writes since the signature

- **Given** THE THREE TREES
- **When** `sprint_report.py check --report RPT0001` runs through `main` in each
- **Then** (i) and (ii) print VALID and exit 0; (iii) prints INVALIDATED, exits non-zero, and names the figure that moved with its signed value and its current one; and the check writes nothing in any of the three
- **Mutant:** invalidate whenever the tree has a tracked write newer than `signed_at` - tree (ii) then reads INVALIDATED, every sealed report goes stale on the next unrelated commit, and the marker means only that time has passed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::InvalidatedReportTests::test_invalidation_is_decided_by_re_deriving_the_facts
- **Verified:** yes (2026-09-18)

### AC2: both renderings lead with the banner, and it names what moved without blanking what was signed

- **Given** trees (iii) and (i) of THE THREE TREES
- **When** the Markdown twin and the HTML rendering are produced from RPT0001 in each
- **Then** in (iii) both outputs carry `INVALIDATED` before the sprint goal - ahead of every figure - naming the signed fingerprint, the current one and the figure that moved, while the sign-off block still shows the principal and date that WERE signed rather than being emptied; in (i) neither output carries the banner
- **Mutant:** render the banner at the foot, below Provenance - the reader takes the figures as signed and meets the warning after the decision, and every assertion that the banner exists still passes
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::InvalidatedReportTests::test_both_renderings_lead_with_the_invalidation_banner
- **Verified:** yes (2026-09-18)

### AC3: status names an invalidated report, so the operator who never opens it is still told

- **Given** THE THREE TREES
- **When** `status.py pillars` (status.py:390, the verb that prints the Run line) runs in each
- **Then** only (iii) prints a line naming RPT0001 as INVALIDATED with the re-prepare command; (i) and (ii) print the report as signed, with its principal and date; and status writes nothing in any of the three
- **Mutant:** compute the banner inside the renderer alone - the operator who reads `status` and never opens the report is told nothing, which is the state the consult found and this story exists to end
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::InvalidatedReportInStatusTests::test_status_names_an_invalidated_report
- **Verified:** yes (2026-09-18)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | invalidate whenever the tree has a tracked write newer than `signed_at` - tree (ii) then reads INVALIDATED, every sealed report goes stale on the next unrelated commit, and the marker means only that time has passed | invalidation is decided by re-deriving the facts, not by counting writes since the signature |
| AC2 | render the banner at the foot, below Provenance - the reader takes the figures as signed and meets the warning after the decision, and every assertion that the banner exists still passes | both renderings lead with the banner, and it names what moved without blanking what was signed |
| AC3 | compute the banner inside the renderer alone - the operator who reads `status` and never opens the report is told nothing, which is the state the consult found and this story exists to end | status names an invalidated report, so the operator who never opens it is still told |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-17 | grooming 2026-09-17 | Groomed: three criteria, and the user story filled. D4 pinned to re-derivation, with the two wider readings rejected in the framing; the discriminating fixture is a tracked write that moves no figure. The banner leads both renderings and `status` names it, so the operator who never opens the report is still told. status.py and test_status.py added to Affects. |
