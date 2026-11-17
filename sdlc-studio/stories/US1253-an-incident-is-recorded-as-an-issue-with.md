# US1253: An incident is recorded as an issue with a root-cause section and triaged into escaped bugs linked back to it

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0706
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/triage.py, .claude/skills/sdlc-studio/help/issue.md, .claude/skills/sdlc-studio/scripts/tests/test_incident_issue_triage.py, changelog.d/US1253.md
> **Epic:** EP0346
> **Points:** 5
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** An incident is recorded as an issue with a root-cause section and triaged into escaped bugs linked back to it
**So that** CR0706 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: An incident is filed as an issue with a root-cause section

- **Given** an initialised project
- **When** an issue is filed as an incident through `artifact.py new --type issue`, and a second issue is filed without the incident flag
- **Then** the first carries the line marking it an incident and a Root Cause section to fill, and validates clean; the second has neither and is written as it is today. Fails on: a new artefact type for incidents (D0457), or every issue gaining the section
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_incident_issue_triage.py::IncidentTriageTests::test_an_incident_issue_carries_its_marker_and_root_cause_section

### AC2: Triage turns an incident into escaped bugs linked back to it

- **Given** an incident issue and a breakdown of two bugs naming the release each shipped in
- **When** `triage.py apply --issue <id>` mints them
- **Then** each bug carries `Escaped: yes`, its `Shipped-in` release and a `Parent` naming the issue, with `Escaped-via` where a unit was named, and the issue's `Decomposed-into` lists both. Fails on: a bug minted from an incident that does not read as escaped, or a link written on one side only
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_incident_issue_triage.py::IncidentTriageTests::test_triage_mints_escaped_bugs_linked_to_the_incident

### AC3: An incident's bug with no resolvable release mints nothing

- **Given** an incident issue and a breakdown in which one bug names no release, or a release that does not resolve; beside it an ordinary issue triaged with no release named
- **When** `triage.py apply` is run for each
- **Then** the incident's triage refuses before anything is minted, naming the bug and the release it lacks, and leaves the issue as it was; the ordinary issue is triaged as it is today. Fails on: one bug of the breakdown minted before the refusal, or an ordinary issue made to name a release
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_incident_issue_triage.py::IncidentTriageTests::test_an_unresolved_release_refuses_and_mints_nothing

### AC4: The issue help says how an incident is recorded and triaged

- **Given** `help/issue.md`
- **When** its text is read
- **Then** it names the incident flag, the Root Cause section, and that triage writes the escaped bugs with their release and their link back, each matching the command's own `--help`. Fails on: help that names a flag the command does not take
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_incident_issue_triage.py::IncidentTriageTests::test_the_issue_help_names_the_incident_path

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
