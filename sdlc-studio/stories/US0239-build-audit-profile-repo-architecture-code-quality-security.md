# US0239: build audit --profile repo (architecture/code-quality/security legs) wired to the refute panel

> **Status:** Done
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/audit.py, .claude/skills/sdlc-studio/templates/audit-profiles/repo.md
> **Epic:** EP0078
> **Points:** 3

## User Story

**As a** developer evaluating sdlc-studio on a repo that has never run it
**I want** the three-leg weakness hunt to run as `audit --profile repo`, refute panel included
**So that** there is one weakness-hunt under one name, and my findings survive an independent panel before they are filed

## Acceptance Criteria

### AC1: Declare the three repo legs as a loadable lens pack

- **Given** the architecture, code-quality and defensive-security legs the retired `review generate` ran
- **When** an agent loads `templates/audit-profiles/repo.md` as the profile for an audit run
- **Then** the pack declares one lens row per leg, each with its adversarial question and what it hunts, in the same declarative shape as `audit-profiles/skill.md`
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_audit_profiles.py -k RepoProfileLensTests
- **Verified:** yes (2026-07-19)

### AC2: Resolve `--profile repo` to the pack, refuse an unknown name

- **Given** `audit.py`, which today carries only the tranche-readiness check and no profile surface
- **When** the profile `repo` is resolved, and again when a name no pack declares is resolved
- **Then** `repo` resolves to `templates/audit-profiles/repo.md` and reports its three lenses plus the refute threshold; the unknown name exits non-zero naming the packs that do exist, rather than running an empty lens set
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_audit_profiles.py -k ProfileResolveTests
- **Verified:** yes (2026-07-19)

### AC3: Carry the remediation-only security posture into the pack

- **Given** the security wording that lived in `review_generate.py` as `SECURITY_POLICY`, on a script US0241 deletes
- **When** the repo pack's security lens is read by a finder agent
- **Then** the pack states the posture verbatim: location, weakness class, realistic impact and a concrete fix, no proof-of-concept payload, and a committed secret reported by location plus rotation with the value left where it is
- **Verify:** grep "Never copy a secret value into any artefact" .claude/skills/sdlc-studio/templates/audit-profiles/repo.md
- **Verified:** yes (2026-07-19)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
