# US1317: docs/enterprise.md answers an enterprise reviewer: harness and models, data, adopting without forking, fitting existing controls, cost, and verification for less experienced engineers, each claim checked against the code

> **Status:** Done
> **Risk-class:** standard
> **Delivers:** CR0742
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** docs/enterprise.md, docs/engineering-leaders.md, tools/tests/test_enterprise_doc.py, changelog.d/US1317.md
> **Epic:** EP0377
> **Points:** 5
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** docs/enterprise.md answers an enterprise reviewer: harness and models, data, adopting without forking, fitting existing controls, cost, and verification for less experienced engineers, each claim checked against the code
**So that** CR0742 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The page answers the six questions an enterprise reviewer asks

- **Given** `docs/enterprise.md`
- **When** its sections are read
- **Then** it has sections for harness and models, data, adopting without forking, fitting existing controls, cost, and verification for less experienced engineers, and it and `docs/engineering-leaders.md` link each other. Fails on: a section missing, or either link missing
- **Verify:** pytest tools/tests/test_enterprise_doc.py::EnterpriseDocTests::test_the_page_has_the_six_sections_and_links_the_leaders_page
- **Verified:** yes (2026-11-18)

### AC2: The data section names every network call the shipped code makes

- **Given** the installers and the skill's scripts, scanned for network calls (urllib, http.client, socket, curl, wget, `gh` and git remote operations)
- **When** the data section is compared with the scan
- **Then** every file the scan finds is named in the data section with what it contacts, and the page claims no telemetry the code does not have. Fails on: a script with a network call the page does not name, shown by a planted one
- **Verify:** pytest tools/tests/test_enterprise_doc.py::EnterpriseDocTests::test_every_network_call_is_named_in_the_data_section
- **Verified:** yes (2026-11-18)

### AC3: The controls map names evidence and claims no certification

- **Given** the fitting-existing-controls section
- **When** its mapping of requirements approved, design reviewed, tests evidenced, independent review and approval before release is read
- **Then** each gate names the artefact or command that evidences it, each named path exists, and the page uses no claim of certification or compliance. Fails on: a gate with no evidence, a path that does not exist, or a word such as certified or compliant used as a claim
- **Verify:** pytest tools/tests/test_enterprise_doc.py::EnterpriseDocTests::test_the_controls_map_names_evidence_and_claims_no_certification
- **Verified:** yes (2026-11-18)

### AC4: The cost section's commands exist and its figures come from signed reports

- **Given** the cost section
- **When** each command it names is run with `--help` and each figure it quotes is looked up
- **Then** every command parses, and every cost figure names a signed report whose committed JSON carries it. Fails on: a command that does not exist, or a figure no signed report carries
- **Verify:** pytest tools/tests/test_enterprise_doc.py::EnterpriseDocTests::test_cost_commands_exist_and_figures_cite_signed_reports
- **Verified:** yes (2026-11-18)

## Notes

- Public text names no organisation, person or internal review (CR0742 constraints). Request-based billing (for example GitHub Copilot premium requests): state what the meter reads for Copilot, from the code, and that a request count is the harness's own figure.
- `docs/engineering-leaders.md` keeps its change-board walk-through; the enterprise page links to it rather than repeating it.
- LC-019 applies (new test file).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Created via `new` (deterministic) |
