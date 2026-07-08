# US0072: README and positioning refresh under the three hard constraints

> **Status:** Done
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic:** EP0017
> **Persona:** Orchestrator / Operator
> **Source:** CR-0177
> **Affects:** README.md, docs/why-sdlc-studio.md

## User Story

**As a** prospective adopter (human or agent) evaluating the tool
**I want** the README framed around the differentiators as proof of the anti-vibe-coding philosophy, backed by a full progressively-disclosed value document
**So that** the tool reads as a category of one, with greenfield and brownfield equally visible and every claim resting on published evidence

## Acceptance Criteria

### AC1: The three hard constraints hold

- **Given** the reframed README
- **When** it is reviewed
- **Then** (a) anti-vibe-coding is the umbrella with brownfield+reconcile as proof, (b) greenfield
  stays an equally visible front door, (c) the command catalogue sits below the fold
- **Verify:** manual review against the three constraints
- **Verified:** manual (2026-07-08)

### AC2: No claim outruns a shipped feature, and gates pass

- **Given** the new copy
- **When** claims are checked
- **Then** the team-shape story appears only because CR0167/0168/0169 shipped (and says opt-in/dormant), the on-ramp mention exists because CR0175 shipped, every quantified claim traces to a published benchmark report or is labelled operator-reported, and the style/neutrality gates pass
- **Verify:** shell npm run lint:style && python3 tools/check_neutrality.py && python3 tools/check_links.py
- **Verified:** yes (2026-07-08)

### AC3: The full value document exists and is progressively disclosed

- **Given** docs/why-sdlc-studio.md
- **When** read top to bottom
- **Then** it layers TL;DR -> thesis -> evidence (field results labelled operator-reported; benchmark labelled with n and caveats, linking the raw reports) -> economics (including the measured 2.1-3.1x single-ticket overhead, not just the favourable numbers) -> team-shape (calibrated to opt-in status) -> what is still unproven; the README links to it
- **Verify:** grep "why-sdlc-studio" README.md
- **Verified:** yes (2026-07-08)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | sdlc | Created via `new` (deterministic) |
| 2026-07-08 | sprint: CR0177 | ACs sharpened (weak-verify fixed, AC3 added for the full document); scope extended to docs/why-sdlc-studio.md per operator direction |
