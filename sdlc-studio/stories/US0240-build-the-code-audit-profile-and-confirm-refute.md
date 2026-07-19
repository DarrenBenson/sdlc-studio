# US0240: build the code audit profile and confirm refute wiring across profiles (CR0255 residual)

> **Status:** Review
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/templates/audit-profiles/code.md, .claude/skills/sdlc-studio/reference-audit.md, .claude/skills/sdlc-studio/help/audit.md
> **Epic:** EP0078
> **Points:** 2

## User Story

**As a** maintainer auditing a codebase rather than its specification set
**I want** a code profile alongside project, skill and repo, with the refute panel wired to every one of them
**So that** the profile I pick changes the lenses, never whether plausible-but-wrong findings get filed

## Acceptance Criteria

### AC1: Ship the code lens pack

- **Given** CR0255 promised repo, project and code profiles and only project and skill shipped
- **When** an agent loads `templates/audit-profiles/code.md` as the profile for an audit run
- **Then** the pack declares its code-level lenses (correctness, security smells, pattern violations, AC-vs-implementation drift), each with an adversarial question and what it hunts
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_audit_profiles.py -k CodeProfileLensTests
- **Verified:** yes (2026-07-19)

### AC2: Every shipped profile is catalogued and panel-wired

- **Given** four profiles on disk or in the reference: project, skill, repo and code
- **When** the profile catalogue in `reference-audit.md#audit-profiles` and `help/audit.md` is checked against the packs that exist
- **Then** each profile appears in both, no pack is documented that is absent (or absent that is documented), and none opts out of the shared refute panel
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_audit_profiles.py -k ProfileCatalogueTests
- **Verified:** yes (2026-07-19)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
