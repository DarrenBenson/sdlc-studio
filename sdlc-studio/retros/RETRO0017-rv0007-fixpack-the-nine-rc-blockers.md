# RETRO-0017: RV0007 fix-pack - the nine rc-blockers

> **Date:** 2026-07-10
> **Batch:** RV0007 rc-blocker fix pack (BG0071-BG0075, BG0077-BG0080; no epic - a review-driven bug tranche)
> **Goal:** clear every finding blocking the v4.0.0-rc.1 tag, one green commit per unit, and make the rc checklist's GREEN honest
> **Delivered:** 9 / 9   **Blocked:** 0

## Delivered

- BG0075 - repo lint back to green (26 markdownlint errors across 10 files), the pre-commit
  gate ENABLED in this clone (it had never been), and the rc checklist gains full-lint +
  hook-enablement rows. Every later unit committed through the live hook.
- BG0071 - `row_from_header` defaults absent date fields; `reconcile apply` heals dated
  indexes again (seam + unit tests red-first; original fixture repro re-run).
- BG0072 - `infer_type_from_id` (leading alpha prefix) replaces the all-alpha collect;
  the close cascade works on v3 ULIDs.
- BG0077 - one shared era-v3 allocator (`sdlc_md.mint_v3_id`); the finding filer mints
  ULIDs on v3 projects instead of racing sequential ids.
- BG0078 - the Low-consolidation lane prints by its own result shape: exit 0 on create,
  append and dry-run (was: exit 1 AFTER creating the CR).
- BG0074 - a completed `migrate_v3 apply` stamps `schema_version: 3` itself; the
  post-migrate filing collision (BG0001 minted over a live alias) is closed end-to-end.
- BG0073 - the migration journals its id map before the first write and resumes from the
  SAVED map; corrupt journals refuse loudly; the journal comes off only when durable.
- BG0079 - the eval gate joined the rc checklist AND the four scenarios were actually
  re-run (two-Claude loop, independent graders): 4/4 PASS -> `v4-eval-run-2026-07-10.md`.
- BG0080 - era-neutral status/hint pre-flight tables (schema 3 has a row; config-only v3
  projects recognised) and a current-major SECURITY.md support table.

## Critic loop, observed

- **One REJECT, and it was the sprint's best catch.** The closing full-diff critic
  reproduced an identity-loss defect in the first BG0073 cut: on resume, phase 1 re-rewrote
  the old id inside `> **Aliases:**` lines, making every alias self-referential - the exact
  loss class the journal exists to prevent. The shipped crash-resume test executed that very
  path but never asserted on aliases, so it passed over the damage. Repaired test-first
  (alias lines structurally exempt from rewriting); the SAME critic re-ran its own
  reproductions (phase-3 crash, mid-phase-2 crash, fresh apply) before flipping to APPROVE.
- Survivors of the adversarial pass (advisories, no artefacts - ledgered): short-ulid burst
  filing degrades to the un-collision-checked 12-char fallback (entropy defect already filed
  as BG0086); `file_finding cmd_file` dry-run Low lane prints `would file None -> None`
  (cosmetic, CR0208-class); the readiness suite figure goes stale the moment new tests land -
  recompute at the tag, as the checklist itself instructs.
- The hook earned its keep on its first day: it blocked one commit for a provenance tag in a
  new docstring (the exact US0111 guard class) - the guard chain works when it RUNS.

## What went well

- Fixing BG0075 FIRST meant all eight later units committed through a live, full gate -
  the sprint dogfooded the meta-layer fix it was shipping.
- The eval scenarios were runnable as worker/grader subagent pairs, so the "each run costs a
  real model session" gate became affordable inside the sprint instead of an operator chore.
- Every fix was seen red first, and the two reproduced-in-RV0007 defects (schema stamp,
  consolidation exit) were re-verified against the review's own repro steps end-to-end.

## What was hard / what stalled

- The crash-resume test that shipped with the first BG0073 cut crashed at the right place
  but asserted the wrong invariant (journal presence, not alias survival) - a green test over
  real damage. The critic's refute-framing found in minutes what the author's test missed.
- Mid-file `__main__` guards (CR0204, still open) forced every test append to be
  layout-checked first; one appended block needed an import patch-up.

## Lessons

- A crash-recovery test must assert the SURVIVING data, not the recovery mechanics - the
  journal existed, the resume ran, and the identities were still destroyed. Write the
  assertion about what the user keeps, not what the tool does. <!-- durable: promote -->
- When a fix pack contains its own gate repair, land the gate first and ship the rest
  through it - the ordering is free verification of the gate fix.
- Reference-rewriting migrations need a structural exemption list (alias/provenance lines),
  not just idempotency claims: "no-op on re-run" was true for bodies and false for the one
  line class phase 2 adds.

## Metrics

- Units: 9/9 delivered, 0 blocked · Critic: 1 REJECT (BG0073 alias clobber, repaired
  test-first, re-repro'd, APPROVE) + 3 advisories ledgered · Suites at close: 1472 skill +
  108 tools green, `npm run lint` exit 0 (hook live), gate PASS, drift 0 · Eval run: 4/4
  PASS · rc checklist: every row GREEN including the two new gates · Nothing pushed (rc tag
  remains the operator's call).
