# CR-0246: The learning loop is doctrine with a config opt-out, and the claim goes in the benchmark

> **Status:** Proposed
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio new
> **Provenance:** RFC0032 D5
> **Raised-by:** sdlc-studio; agent; v1
> **Priority:** P2
> **Type:** docs

## Summary

Mirror the engagement floor: mandated because judgement-gated process was MEASURED to be skipped, with a config escape hatch. The same claim here must be verified rather than assumed - the white paper's claims register cuts both ways, and 'we mandated it because it sounded right' is exactly what that register exists to prevent. Ship the loop on by default, document the opt-out, and add the claim to the benchmark so it is tested.

## Impact

{{who this affects and what breaks}}

**Effort:** {{S|M|L}}

## Acceptance Criteria

- [ ] The loop is on by default and documented in the doctrine. Verify: rg -q 'learning loop|lessons' .claude/skills/sdlc-studio/reference-doctrine.md
- [ ] A config opt-out exists and is documented. Verify: rg -q 'lessons' .claude/skills/sdlc-studio/reference-config.md
- [ ] The claim that the loop reduces repeat defects is registered as a benchmark claim with a verification path, not asserted. Verify: rg -q 'learning loop|lessons' docs/whitepaper.md

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Created via `new` (deterministic) |
