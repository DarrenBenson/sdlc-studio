# CR-0246: The learning loop is doctrine with a config opt-out, and the claim goes in the benchmark

> **Status:** Complete
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio new
> **Provenance:** RFC0032 D5
> **Raised-by:** sdlc-studio; agent; v1
> **Priority:** P2
> **Type:** docs

## Summary

Mirror the engagement floor: mandated because judgement-gated process was MEASURED to be skipped, with a config escape hatch. The same claim here must be verified rather than assumed - the white paper's claims register cuts both ways, and 'we mandated it because it sounded right' is exactly what that register exists to prevent. Ship the loop on by default, document the opt-out, and add the claim to the benchmark so it is tested.

## Impact

Every project, since the loop ships on by default. Projects that do not want it set the config opt-out. The claim that the loop reduces repeat defects becomes a benchmark claim with a verification path, rather than an assertion - the register cuts both ways.

**Effort:** S

## Acceptance Criteria

- [ ] The loop is on by default, and the doctrine says so: a project that does nothing gets the
      learning loop.
- [ ] A project can turn it off through config, and the opt-out is documented where an operator
      looking for it would look.
- [ ] The claim that the loop reduces repeat defects is registered as a benchmark claim with a
      stated verification path, not asserted in prose as though it were already proved.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Created via `new` (deterministic) |
