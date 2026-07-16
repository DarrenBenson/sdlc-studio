# US0178: Migrate the amigo cast to personas/seats/ and ground each card in this repo and its Primary

> **Status:** Done
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Raised-by:** Claude Fable 5; agent; CR0292 delivery
> **Affects:** sdlc-studio/personas/seats/product.md, sdlc-studio/personas/seats/engineering.md, sdlc-studio/personas/seats/qa.md
> **Epic:** EP0050
> **Points:** 2

## User Story

**As** the operator running seat-framed reviews on this repo
**I want** the three seat cards to live in the converged seats/ home and reason from this project's ground truth
**So that** the seats that gate my stories judge against Maya Okafor and this repo's domain, not a fictional shopping app, through no deprecation path

## Acceptance Criteria

### AC1: The cast lives in seats/, the retired amigos/ home is gone

- **Given** the dogfood workspace after `migrate --apply`
- **When** the personas tree is listed
- **Then** personas/seats/ holds the three cards and personas/amigos/ no longer exists
- **Verify:** shell test -f sdlc-studio/personas/seats/product.md && test ! -e sdlc-studio/personas/amigos
- **Verified:** yes (2026-07-16)

### AC2: Each card is grounded in this project and its actual Primary

- **Given** the Product seat's scenario
- **When** it names the Primary persona
- **Then** it is Maya Okafor (no "Sam the new shopper", no shopping-app ground truth)
- **Verify:** shell sh -c 'grep -q "Maya Okafor" sdlc-studio/personas/seats/product.md && ! grep -q "new shopper" sdlc-studio/personas/seats/product.md'
- **Verified:** yes (2026-07-16)

### AC3: Seat resolution is warning-free

- **Given** any of the three seats
- **When** persona_resolve.py resolves it for a review render
- **Then** no retired-home deprecation warning is emitted
- **Verify:** shell sh -c 'python3 .claude/skills/sdlc-studio/scripts/persona_resolve.py resolve --seat engineering --render review 2>&1 | grep -qi retired && exit 1 || exit 0'
- **Verified:** yes (2026-07-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-16 | Claude Fable 5 | ACs written and delivered (CR0292; layout half via migrate --apply) |
