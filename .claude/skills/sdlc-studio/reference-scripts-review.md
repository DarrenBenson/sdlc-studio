# Script Catalogue - Audit, review & critic

<!-- Load when: you need the full detail for a script in this group. The lean
     index with all groups is reference-scripts.md. -->

Detail pages for the **audit, review & critic** scripts. See
[reference-scripts.md](reference-scripts.md) for the full index across all groups.

## Scripts

### `ac_scope.py`

Authoring lint (advisory): `check` flags a story whose acceptance criteria mention a
distinctive capability keyword owned by a **different** epic's title (e.g. an EP0001 story
asserting an "account token" when accounts are EP0006) - such a story is un-Done-able in its
own epic and should be split or re-scoped. Heuristic and read-only; false positives are
expected (the operator decides); never auto-edits. Run by the authoring loop's closing
consistency pass.

### `plan_review.py`

Plan-review gate (schema v3 only, dormant on v2). Before a story with spec-derived ACs is
implemented, an independent reviewer must challenge its ACs against the source spec. The
trigger is **deterministic** (TRD ADR-006): `triggers(text, root)` fires on any of three
signals - the Affects/ACs cite a `plan_review.spec_globs` path, `affects_files` reaches
`plan_review.affects_files_threshold`, or the routed difficulty band reaches
`plan_review.min_difficulty`. `gate(root, id)` blocks a triggered story from entering
In Progress/Review/Done (wired into `transition.py`) unless an independent plan-review APPROVE
is on record or a `> **Plan-Review-Override:**` field is present. Record with `plan_review
record --id US.. --verdict approve --reviewer <seat> --author <plan-author>` - it pins the
reviewed ACs by fingerprint (its own log, so it never satisfies the delivery critique gate),
so a later AC edit invalidates the approval. `check --id US00xx` reports the verdict.

### `spec_guard.py`

Spec-edit guard (schema v3 only, dormant on v2). A delivery must not silently falsify the
source of truth. `spec_edits(root, changed_files)` reports which changed files are
requirements/spec documents (config `review.spec_paths`); `check(root, changed, story_text)`
adds whether any AC cites a spec change and flags an `untraced` edit (a spec doc edited with no
citing AC) - the signal the critic charter treats as a blocking finding. The
traceability judgement stays with the critic; the pre-check only guarantees the edit is
surfaced. `check --changed a,b,c --story <file>` on the CLI.

### `constitution.py`

Project-constitution principle gate. Asserts the machine-checkable
principles declared in `sdlc-studio/constitution.md` - each `rule:` maps onto an
existing detector (integrity/conformance/validate/reconcile). Advisory by default;
`constitution.enforce: true` makes a violation exit non-zero.

- `check`: report (and, when enforced, fail on) principle violations

Full methodology: `reference-doctrine.md#constitution`.

### `audit_check.py`

One CI-runnable command over the schema-v3 team-schema rules, emitting STABLE rule ids so the
output is a reference implementation the wider crew audit linter can consume:

- `check`: run all rules; exit 1 on any error-severity finding, 0 on a clean repo. `--format
  json` gives `{ok, rules, findings}` with `{rule, file, message}` per finding.

Rules (all era-gated to schema v3, so a v2 project reports nothing): `authorship-structured`,
`authorship-type`, `authorship-unresolved`, `evidence-present`, `duties-separated`,
`id-format`, `index-derived`. These same rules are enforced in the blocking `gate` via
`validate` and the `index-derived` check; `audit_check.py` is the focused, stable-id view.

### `review_prep.py` (read-only)

- `prep`: deterministic inputs for the five-leg review (artifact staleness,
  persona definition-vs-PRD usage, count and AC-verification inputs, and `required_legs` -
  for each of the four required document legs, `{present, path, waiver}` so an absent leg is
  machine-visible and a downgrade-without-a-waiver is detectable). Gathers inputs only; the
  verdict stays with Claude. Full workflow: `reference-review.md`.

### `review_generate.py`

Deterministic spine of the model-driven `review generate` on-ramp. `bootstrap`
idempotently creates the `reviews/`/`bugs/`/`change-requests/` folders and indexes;
`policy`/`prompt` print the verbatim remediation-only posture and the review prompt
template (`templates/workflows/repo-review.md`); `scan --secret <value>` fails if a
secret value leaked into an artefact. Help: `help/review.md`.

### `disclosure.py`

Progressive-disclosure + Claude Code best-practice check, **advisory**. Flags reference-/
help- files missing a `Load when:` trigger or orphaned from every index (SKILL.md / help/references.md
/ help/help.md), plus best-practice items from `best-practices/claude-skill.md` (scripts executable +
expose `--help`, templates use `{{placeholder}}`, SKILL.md has a When-to-Use section). Skill-dev only
(no-op for consuming repos). Wired into the gate as NON-BLOCKING; `--strict` opts into a non-zero exit.
The token lever: a doc with no load-trigger and no index entry gets pulled in without discipline.

### `audit.py`

Adversarial audit / tranche pre-flight. `check` grooms a batch for readiness - weak-AC, unmet-deps, already-terminal, link-integrity, **already-satisfied** (a Ready unit whose executable ACs all pass in the verify-report - a close-candidate, not work to build), **weak-verify** (a non-executable Verify line, reusing `verify_ac lint`) and **cross-epic-ac** (an AC owned by another epic, reusing `ac_scope`) - before the triage STOP, so work never starts on a unit that would pass the gates vacuously or be reverse-engineered at implement time.

A `Depends on:` referent resolves through the shared cross-repo resolver (`lib/xrepo`, the same one `blocker_sweep` uses): in-repo first, then across the sibling repos a `product-manifest.yaml` names. So in a multi-repo product, a dependency **delivered in another repo meets the dependency** rather than reporting `unmet-deps`. A repo the operator has not cloned never stops the search - the remaining repos are still searched, so the verdict follows the disk state and not the manifest's ordering. The three outcomes stay distinct claims: `unmet-deps` (the referent exists and is not delivered, or is dead), **`unresolved-deps`** (no repo resolved the id AND at least one named repo was not on disk, so the dependency could not be checked either way - the repo and path are named, and the unit is never silently passed), and no finding. Single-repo projects have no manifest and are unaffected.

### `critic.py`

The independent-critic verdict ledger. `record` writes a committed verdict to `sdlc-studio/reviews/critic-verdicts.md` stamping both the **reviewer and the author** (the authoring seat / delegation id); `verdict_for` reads it. `is_independent` proves `reviewer != author`; `is_pre_gate` flags units closed before the gate (the visible `pre-gate` marker, grandfathered). Conformance's `critiqued` stage requires a committed APPROVE that is independent or pre-gate.

### `persona_resolve.py`

Resolves the worker amigo for a delegated sub-agent, most-specific-first: a project-authored practitioner amigo (`sdlc-studio/personas/amigos/<seat>.md`), else the skill default (Dani / Sam / Lena), else generic. `resolve` prints the framing the orchestrator appends *after* the contract; `--skip-personas` emits nothing (byte-equivalent generic). The stance never overrides the concrete contract, and the worker is always a separate instance from its reviewer.

The consult surface (used by `refine` and `triage`): `resolve-consult --role <role>` resolves the seat a consult critiques through (review render; a matched project seat missing it is a hard error); `panel --ceremony refine|triage [--question ...]` resolves the whole Three-Amigos panel for a ceremony, lead-first (refine engineering-led, triage QA-led), and names the seats questions go to. `consult()` and `amigo_panel()` are the library entry points refine/triage call; `record_consult()` writes the `> **Consulted:**` line and `## Amigo Consult` section onto the request/Issue as an audit trail (idempotent; a no-op without questions).
