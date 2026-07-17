# RETRO-0046: The spec-truth refresh sprint: EP0071 plus the open-bug backlog

> **Run:** RUN-01KXR6XS
> **Batch:** US0201, US0202, US0203, US0204, US0205, US0206, US0207, US0208, US0209, US0210, US0211, US0212 (EP0071), BG0182, BG0183, BG0184, BG0185, BG0186 (17 units, 42 points)
> **Goal:** PRD/TRD/TSD/RFC0034 match shipped `main` (spec-truth refresh) and the open-bug backlog is cleared.
> **Goal verdict:** ACHIEVED.

## Delivered

- **5 bugs (10 pts), all Fixed, TDD/red-first where code:**
  - BG0184 (the unblocker): `ac_scope.check` exempts a keyword whose sole owning epic is terminal - cleared the false NOT-READY block on US0201/0204/0206 at the tranche-audit gate.
  - BG0185: a mis-cased/mis-spaced `[check:]` tag now errors loudly (`check_tag_near_misses` + a `malformed-check-tag` lane in `validate.py`) instead of silently unenforcing a DoR/DoD criterion.
  - BG0186: `parent_ref` delegates to `parent_refs[0]`, so singular and plural agree on a sentinel-first `Parent:` record.
  - BG0183: a tests-dir `sys.path` shim in `test_telemetry.py` so its `gitutil` import resolves under single-module invocation.
  - BG0182: `help/mutation.md` matches the shipped refuse-on-red-baseline contract.
- **12 stories (32 pts), all Done, every AC verified:** EP0071 reconciled PRD/TRD/TSD/RFC0034 with shipped `main` - the cost model (Fibonacci points, forecast = sum(Points) x measured rate, r=+0.68), the three network paths, config defaults, the ULID guarantee, the two-backlog model, the issue type, rule 5's writer set, the migration surface, and RFC0034's partial supersession by RFC0038.
- One code change rode in a doc story: US0208 hardened `critic.py` `read_verdicts` to warn on a torn row.

## Blocked / deferred

None. All 17 units terminal.

## What went well

- **The batch carried its own unblocker.** The tranche audit's 4 false NOT-READY flags were the exact class BG0184 describes (cross-epic-ac on a terminal-epic keyword); fixing BG0184 first cleared 3 of them, and the 4th (US0205 `residual`) was a genuine false positive recorded as D0032.
- **The doc-truth work found real spec-rot, not just gaps.** The PRD claimed `require_ac_verification: on` (shipped is `false`); the TSD asserted coverage and bandit were *not* wired when both are blocking CI steps. These were false statements corrected, caught by verifying every claim against shipped source before writing.
- **File-disjoint fan-out worked.** prd-only and trd+critic clusters ran as parallel subagents on disjoint files; the coupled prd/trd straddlers (US0201/US0203) were authored centrally first to give a clean base.

## What was hard / what stalled

- **Going straight to `--goal done` over ungroomed stories.** The 12 stories were filed with placeholder `Given`/`When`/`Verify` (never groomed to Ready), so the done-run had to groom them inline - fill each AC and write an executable `grep`/`pytest` Verify. This is the `--goal design` rung, done under a `done` run.
- **The verify-DSL `grep` verb takes no flags.** Two subagents wrote `grep -E "..."`; the DSL is `grep <regex> <path>` (ripgrep/ERE assumed), so `-E` was mis-parsed as the pattern and every such Verify failed. Caught by `verify_ac`, fixed by stripping `-E` from all lines.
- **A full `verify_ac` run flips volatile `shell`/`pytest` Verify lines on unrelated Done stories** (US0021, US0112, US0115...): a `shell` check that greps live `reconcile` output for terminal-row advisories now fails because those advisories exist. Reverted each; it is pre-existing drift, not this sprint's regression, but the re-annotation churn is a friction.

## Critic loop, observed

The closing CODE leg was an **independent adversarial full-diff review** (separate instance, refute-framed, a reproduction per claim). It ran the full suite and guards (2817 green, drift 0) and attacked every doc claim against shipped source. Two findings survived, both fixed test-first and re-verified:

- **MAJOR:** US0211 banded `trd.md:131` to "90+ modules; well over 2,500 tests" but left six other pins reading "2151 tests"/"76 modules" - the TRD self-contradicted. Swept to bands; the dated changelog row kept as history.
- **MINOR:** the BG0185 near-miss detector false-positived on bracketed prose (`[check the logs]`). Tightened so a near-miss must also carry a tag shape (a colon or an id-shaped dotted token); red-first test added.

It **refuted nothing else** and positively confirmed the cost-model claim (r=+0.68, recorded not re-derived), the three-network-path claim (no fourth socket), the ULID math (6+2 chars, 10 bits = 1024, 4 dropped timestamp chars ~= 17 min), the config defaults, the TSD gates blocking in CI, the `critic.py` torn-row `else` (non-vacuous), and BG0184/BG0186 (no hole, fails safe).

## Lessons

- The verify-DSL `grep` verb takes **no flag**; a doc-truth story's executable AC is `grep "<distinctive phrase of the aligned text>" <path>`. Brief delegated agents accordingly.
- A "spec-truth refresh" must sweep **every** instance of a pinned count, not just the headline - a half-swept count leaves the document contradicting itself, the very defect being removed.
- A near-miss/fuzzy-match detector needs a positive shape test, not just a keyword: `[check ...]` prose is not a mis-written tag.
- Bulk `--goal done` over stories filed at Draft forces inline grooming; refining to the `design` rung first (real Given/When/Verify) keeps the done-run about delivery, not authoring. (Reinforces the discovery-backlog meta-lesson: build/groom the enabling state before the batch runs.)

## Estimate vs actual

Plan-time forecast: **~1,050,000 tokens = 42 points x 25,000 tokens/point** (seed rate; this project has < 5 units of its own measured evidence, so the seed still governs). Per-unit token actuals were **not captured** to `retros/evidence/actuals-*.jsonl` - the 17 close events recorded id/type but no token count, the known interactive-sprint gap (CR0278). The harness tracked total spend deterministically; it was not written to per-unit telemetry, so est/actual is not computable this sprint. Not "unmeasurable" - uncaptured. CR0278 (record interactive-sprint tokens) remains the fix.

Velocity (points/elapsed-hour): not recorded - an interactive run's wall-clock includes operator-away gaps.

## Actions raised

**Are there any CRs or Bugs you want to raise in this project to address any of the
issues found?** Every finding gets a disposition: file it, or decline it with a reason.

| Finding | Disposition |
| --- | --- |
| TRD §9 threat model still calls `plan.py archive` the sole write exception, contradicting the enriched §5 rule 5 writer set | BG0187 (filed) |
| US0205's `residual` cross-epic-ac flag is a false positive (its own subject, not a dep on EP0082) | declined: false positive on its own subject, recorded as decision D0032 |
| Per-unit token actuals were not captured this interactive sprint, so est/actual is uncomputable | declined: covered by the standing CR0278 (interactive-sprint token capture); no new artefact |
| The verify-DSL `grep` verb silently mis-parses a `grep -E "..."` line (the `-E` becomes the pattern) instead of erroring clearly | declined: a friction not a defect - the DSL is documented as `grep <regex> <path>`; revisit with a clearer error if it recurs |
| A full `verify_ac` run re-annotates and flips volatile `shell`/`pytest` Verify lines on unrelated Done stories | declined: the re-annotation churn is real but the deeper volatile-Verify smell is the issue; revisit if it bites again |

<!-- file one with: scripts/file_finding.py -->

## Close loop (gated)

- Reconcile: drift 0.
- Review: this retro + the adversarial full-diff CODE leg (APPROVE after two fixes).
- Gate: run at close (`gate --require-retro RETRO0046 --require-review`).

## Handoff

All 17 units terminal; EP0071 Done. Residual: BG0187, and the un-owned `RFC0047` that appeared in the tree mid-run (see the sign-off note) is not part of this sprint.
