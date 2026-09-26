# US0070: review generate command with remediation-only security posture

> **Status:** Done
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic:** EP0016
> **Persona:** Consuming-project Developer
> **Source:** CR-0175

## User Story

**As a** developer with an existing repo
**I want** a review command that audits my code and files triaged findings, with no setup
**So that** I can try sdlc-studio on real code before adopting the full pipeline

## Acceptance Criteria

### AC1: Zero-setup dated report plus filed findings

- **Given** a repo with no sdlc-studio workspace
- **When** `review generate` runs
- **Then** it bootstraps the folders it needs and produces a dated `reviews/RV*` report with three
  legs (architecture, quality, defensive security) and file:line evidence per finding
- **Verify:** manual - retired by US0940: US0241 deleted `review_generate.py` and its suite when `review generate` folded into `audit --profile repo` (57196dd0, EP0078), so the command this criterion describes no longer ships
- **Verified:** manual (2026-09-26) - retired, superseded by US0241

### AC2: Remediation-only security, verbatim and enforced

- **Given** the security-findings policy paragraph
- **When** the prompt template is checked, and a fixture repo with a planted secret is reviewed
- **Then** the policy appears verbatim, and the finding gives location plus rotation with the secret
  value absent from every produced artefact
- **Verify:** manual - retired by US0940: US0241 deleted `review_generate.py`, whose planted-secret scan this criterion ran; the policy paragraph moved verbatim into `templates/audit-profiles/repo.md`, which US0239 AC3 pins
- **Verified:** manual (2026-09-26) - retired, superseded by US0241

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | sdlc | Created via `new` (deterministic) |
| 2026-09-26 | US0940 | AC1 and AC2 retired in the D0259 pattern: US0241 deleted `review generate`; the remediation-only policy lives on in the repo audit profile (US0239 AC3) |
