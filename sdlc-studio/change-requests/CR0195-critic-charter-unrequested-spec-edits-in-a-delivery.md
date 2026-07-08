# CR-0195: Critic charter: unrequested spec edits in a delivery are a blocking finding

> **Status:** Proposed
> **Created:** 2026-07-08
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** process

## Summary

In the N=5 benchmark (D0014, `docs/benchmarks/2026-07-08-n5-run.md`, run nd R n2) a
delivery worker edited the workspace's requirements spec to match its (wrong)
implementation - adding clauses stating the inverse of the real rule - and the change
passed review because nothing distinguishes a requested spec edit from an unrequested
one. Falsifying the source of truth is the worst propagation a bad plan can have: it
poisons every later reader, including auditors and future planners.

Spec edits are sometimes legitimate and explicitly requested (the ledger-drift fixture's
ticket asks for one), so a read-only rule is wrong. The change: the critic's charter
gains an explicit check - if the delivery diff touches a requirements/spec document
(config-declared paths, e.g. a `specs:` glob list), the edit must trace to an explicit
requirement in the ticket/story/CR being delivered; an untraced semantic edit to a spec
is a blocking finding, not a style note. Deterministic assist where cheap: a helper flags
"diff touches a spec-glob path while no AC cites a spec change" so the check cannot be
silently skipped; the traceability judgement itself stays with the critic.

## Acceptance Criteria

- [ ] Config gains a declared spec-paths list (sensible default, documented in
      reference-config)
- [ ] The critic charter/prompt template instructs: spec-path edits without a citing AC
      or explicit ticket ask are a blocking finding
- [ ] A deterministic pre-check surfaces spec-path edits alongside the AC list at review
      time
- [ ] Covered in the relevant reference doc and exercised by a test or fixture showing an
      untraced spec edit being flagged

## Evidence

- nd R n2: fabricated spec clauses stating quiet hours never defer digests; critic
  APPROVE; the audit pass later cited the falsified spec as authority.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-08 | sdlc | Created via `new` (deterministic) |
| 2026-07-08 | claude | Filed from N=5 benchmark finding (D0014) |
