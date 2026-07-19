# US0250: rewrite the help files around the process spine (raise -> break down -> sprint+review; PRD/TRD/TSD/personas as levers; reconcile/review/audit as support)

> **Status:** Done
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/help/help.md
> **Epic:** EP0081
> **Points:** 5

## User Story

**As an** operator opening `/sdlc-studio help`
**I want** the catalogue grouped by the process spine rather than by the order features
were added
**So that** the path from raising work to shipping it is readable off the page

## Acceptance Criteria

### AC1: Group the catalogue by the spine stages

- **Given** `help/help.md` groups commands under accreted headings such as "Sprint,
  Product Layer & Maintenance" and "Utilities"
- **When** the "All Commands" catalogue is rewritten around the spine
- **Then** it carries one section per stage: Raise, Break Down, Sprint and Review,
  Levers, Support and Utility
- **Verify:** shell for h in "Raise" "Break Down" "Sprint and Review" "Levers" "Support" "Utility"; do grep -q "^### $h" .claude/skills/sdlc-studio/help/help.md || exit 1; done
- **Verified:** yes (2026-07-19)

### AC2: Every command sits in the group the audit maps it to

- **Given** `command_audit.SPINE` is the curated map from command to spine stage
- **When** the rewritten sections are populated
- **Then** each `/sdlc-studio <cmd>` entry appears under the section matching its SPINE
  category, and no command is listed under two sections, so the catalogue and the audit
  cannot disagree
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_help_structure.HelpSpineGroupingTests
- **Verified:** yes (2026-07-19)

### AC3: The document levers stay paramount

- **Given** the PRD, TRD, TSD and personas are the operator's top-level levers
- **When** the rewritten catalogue is read top to bottom
- **Then** the Levers section precedes Support and Utility and names `prd`, `trd`,
  `tsd` and `persona`, so the levers are reached before the incidental tooling
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_help_structure.HelpLeverPrecedenceTests
- **Verified:** yes (2026-07-19)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
