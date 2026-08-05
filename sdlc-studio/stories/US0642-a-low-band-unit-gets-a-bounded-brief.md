# US0642: A low-band unit gets a bounded brief and the claim-inventory pass runs only at high band

> **Status:** Ready
> **Delivers:** CR0510
> **Created:** 2026-08-05
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py,.claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Epic:** EP0208
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** A low-band unit gets a bounded brief and the claim-inventory pass runs only at high band
**So that** CR0510 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: the claim-inventory pass runs at full tier and not at light

- **Given** the same unit briefed at each tier
- **When** `critic.py brief` is invoked through the shipped CLI
- **Then** the full brief carries the claim-inventory block and the light brief does not
- **Mutant:** emit the block unconditionally - the light assertion reddens and the bounded brief buys nothing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::BoundedBriefTests::test_the_claim_inventory_runs_at_full_tier_and_not_at_light
- **Verified:** yes (2026-08-05)

### AC2: the depth line and the omissions come from one decision

- **Given** a light brief
- **When** its depth line and its sections are compared
- **Then** a brief that announces a lighter pass never carries a section the light tier omits, because the two are derived from the same tier value rather than written beside each other
- **Mutant:** hard-code the depth sentence independently of the section switch - a brief says light and reads full
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::BoundedBriefTests::test_the_depth_line_and_the_sections_agree
- **Verified:** yes (2026-08-05)

### AC3: bounding the light tier does not weaken the full one

- **Given** a prose surface removed from the claim-inventory enumeration
- **When** a full brief is validated
- **Then** the existing refusal still fires and names the missing surface
- **Mutant:** relax the full-tier validation while adding the light path - the enumeration guard stops guarding
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::BoundedBriefTests::test_the_full_tier_enumeration_refusal_still_fires
- **Verified:** yes (2026-08-05)

### AC4: what a light brief keeps is stated, not left to whatever survived

- **Given** a light brief
- **When** it is inspected
- **Then** it still carries the seat charter, the bounded diff scope, the canonical acceptance criteria and the return contract, because those four are what make it a briefed review rather than a hand-written prompt
- **Mutant:** drop the criteria from the light brief - a light review judges against a paraphrase, which is the failure the shipped brief exists to prevent
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::BoundedBriefTests::test_a_light_brief_keeps_the_four_load_bearing_parts
- **Verified:** yes (2026-08-05)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-05 | sdlc-studio | Created via `new` (deterministic) |
