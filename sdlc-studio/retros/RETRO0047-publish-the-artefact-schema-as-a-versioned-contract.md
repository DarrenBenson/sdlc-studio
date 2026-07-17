# RETRO-0047: Publish the artefact schema as a versioned contract (EP0084)

> **Run:** RUN-01KXRMQT
> **Batch:** US0258, US0259, US0260 (EP0084, 3 units, 11 points)
> **Goal:** Publish the artefact schema as a versioned, drift-guarded public contract.
> **Goal verdict:** ACHIEVED.

## Delivered

- **US0258 (5 pts, Done):** `reference-schema.md` - the self-describing contract over the six
  on-disk surfaces external tooling reads (Id Grammar, Directory Layout, Header Fields, Status
  Vocabulary, Verify DSL, Index Format). Names `validate.py` the executable definition, keeps
  health judgements upstream and `_index.md` derived, marks `.local/` uncontracted (RFC0047 D2).
  Catalogued in `help/references.md`. Every claim cross-checked against the source constants.
- **US0259 (3 pts, Done):** the `schema_version` contract stamp - `config-defaults.yaml` (the
  fallback default, 2) and `templates/config.yaml` (the new-project stamp, 3) each documented,
  `reference-config.md` explains both files' roles, and the Compatibility Policy section
  (additive = minor, rename/removal = major with a migrate path) lands in `reference-schema.md`
  (RFC0047 D1).
- **US0260 (3 pts, Done):** `scripts/tests/test_schema_contract.py` - an 11-test drift guard that
  fails when the documented status vocabulary, the v3 `inbox` lane, or the version stamp diverges
  from the code constants. Mutation-proven to fail on real drift; refuses to pass vacuously.

## Blocked / deferred

None. All 3 units terminal; EP0084 Done.

## What went well

- **The two-role gate earned its cost on the exact bug the author could not see.** The plan and
  the first delivery pass concluded the contract should declare schema version 2. The independent
  adversarial reviewer REJECTed it: `init.py` seeds a new project from `templates/config.yaml`
  (schema_version 3), not `config-defaults.yaml` (2), so new projects already ship v3 and the
  contract's "stays v2 until migration" was false. The author had read `init.py:170` but assumed
  the copied file; the reviewer ran `init.py` and observed the ULID output. Round 2 APPROVEd the fix.
- **The guard is self-checking and mutation-proven.** Before shipping, the guard was proven to go
  red on a status drift, a masthead/seed version drift, and a v3-inbox applies-to drift, each
  reverting green - the contract cannot rot silently, which is the whole point of RFC0047 option C
  done cheaply as a test.
- **A breakdown-gate refusal was a real grooming gap, not a false block.** US0260's `Affects`
  named only a not-yet-existing test file; the gate (BG0144 behaviour) correctly refused it. The
  fix was to add `CHANGELOG.md` (which AC5 genuinely writes), not to override the gate.

## What was hard / what stalled

- **The version-number question had no single answer in the code.** `config-defaults.yaml` = 2,
  `templates/config.yaml` = 3, `project_upgrade.CURRENT_SCHEMA` = 2, and the code's hardcoded
  fallback = 2. Picking "the current version" for a public contract meant resolving which of these
  is authoritative (answer: the new-project seed, 3). Filed BG0189 for the code's own inconsistency.
- **`sprint plan --write` reused a closed run's state.** The prior sprint's run-state was left
  `outcome=running`, so the first `plan --write` accumulated this batch onto its 17 terminal units
  and stamped the new goal over the old verdict. Caught before the run opened; reset and re-planned.
  Filed BG0188.
- **The pre-commit hook runs the full ~118s suite,** so a commit needs a >2-minute shell timeout;
  the first attempt was killed mid-write (all checks had passed) and had to be retried.

## Critic loop, observed

The CODE leg was an **independent adversarial full-diff review** (separate instance, refute-framed,
a reproduction per claim), run twice:

- **Round 1 - REJECT (BLOCKING):** the contract asserted new projects are/stay schema v2 until an
  explicit migrate; shipped `init.py` stamps `schema_version: 3` into every new project (proven by
  running it). Decision D0033's mechanism ("config-defaults.yaml copied verbatim by init.py") was
  factually false. The reviewer verified every other surface accurate (id grammar, directory
  layout, status + terminal sets, header fields, Verify DSL, index format) and the guard real.
- **Round 2 - APPROVE:** the fix declares the contract at schema version 3 (current; v2 legacy),
  anchors the guard to `templates/config.yaml`, and adds a fallback-never-leads test. The reviewer
  re-ran the mutations, confirmed all three verifiers and lint clean, and raised two MINORs (the v3
  `inbox` lane was prose-only and unguarded; the pre-existing `CURRENT_SCHEMA=2`). The inbox MINOR
  was closed in-sprint (now a guarded `### Schema v3 additions` table + two tests); the code MINOR
  is BG0189.

## Lessons

- **Verify which file a "default" actually comes from before documenting it as the default.** New
  projects are seeded from `templates/config.yaml` (3), not the `config-defaults.yaml` fallback (2);
  reading the copy site (`init.py`) without checking the copied path produced a confident, wrong
  contract. Trace the value to the file the running code reads.
- **A public contract's version stamp must anchor to what new consumers actually meet.** Tying the
  masthead to the fallback file made the guard cement the wrong invariant while staying green. Anchor
  a drift guard to the source that governs the real artefact (the new-project seed), not a lookalike.
- **Machine-guard every vocabulary a self-describing contract claims to cover.** The v3 `inbox` lane
  shipped as prose the guard did not check - latent rot under a doc that promises the guard covers
  "the vocabularies below". Encode it as data and guard it, or do not claim coverage.
- **A create-only `Affects` is a real grooming gap, not a gate bug.** Name at least one existing file
  the unit also touches (here `CHANGELOG.md`, which the changelog AC writes) so the collision check
  has an anchor.

## Estimate vs actual

Plan-time forecast: **~275,000 tokens = 11 points x 25,000 tokens/point** (seed rate; this project
has < 5 units of its own measured evidence, so the seed still governs). Per-unit token actuals were
**not captured** to `retros/evidence/actuals-*.jsonl` - the interactive-sprint gap (CR0278). The
harness tracked total spend deterministically; it was not written to per-unit telemetry, so
est/actual is not computable this sprint. Not "unmeasurable" - uncaptured. The extra review round
(one REJECT + fix + re-review) spent tokens the point-based forecast does not model.

Velocity (points/elapsed-hour): not recorded - an interactive run's wall-clock includes operator-away
gaps.

## Actions raised

**Are there any CRs or Bugs you want to raise in this project to address any of the
issues found?** Every finding gets a disposition: file it, or decline it with a reason.

| Finding | Disposition |
| --- | --- |
| `sprint plan --write` accumulates a new batch into a prior run left `outcome=running`, reusing its id and clobbering its verdict | BG0188 (filed) |
| `project_upgrade.CURRENT_SCHEMA = 2` contradicts `init.py` seeding new projects at schema_version 3 | BG0189 (filed) |
| The contract had to pick "the current schema version" and the code gave four answers; resolved to 3 (the new-project seed) | declined: resolved as recorded decision D0034 (supersedes the wrong D0033); a decision, not a defect to action |
| The pre-commit hook's full-suite run makes a commit exceed a 2-minute shell timeout | declined: a harness-timeout friction, not a repo defect; use a longer timeout for the commit step |

<!-- file one with: scripts/file_finding.py -->

## Close loop (gated)

- Reconcile: drift 0.
- Review: this retro + the adversarial full-diff CODE leg (REJECT round 1, APPROVE round 2 after the fix); reviewer-of-record sign-off recorded.
- Gate: run at close (`gate --require-retro RETRO0047 --require-review`).

## Handoff

- [HO-0005](../handoffs/HO0005-publish-the-artefact-schema-as-a-versioned-drift.md) - 0 remaining item(s): 0 copilot-tail, 0 judgement. Pick up with `sprint plan --worklist sdlc-studio/.local/handoff-worklist.txt`.
