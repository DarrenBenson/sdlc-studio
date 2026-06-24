# RV0005 - Full skill review for best-practice + progressive disclosure + token efficiency (v3.0.1)

> Review record for the post-v2.6 holistic skill review (plan:
> `ultrathink-a-plan-to-steady-meadow`). Open; findings land here as they clear the refute panel.

## Scope & decisions

- **Scope:** the whole skill (`.claude/skills/sdlc-studio/`) after CR0077-0099 + RFC0019.
- **Lenses (Claude best-practice angle):** over-engineering, token-economy, determinism,
  external-benchmark (the skill audit profile) + best-practice conformance (`claude-skill.md`),
  progressive-disclosure correctness, and the always-loaded token surface.
- **Operator decisions:** full adversarial sweep; version **3.0.1** (rename signalled, alias kept);
  **fix every confirmed finding before release**.

## Baseline (2026-06-24, read-only)

- `gate` PASS (conformance/reconcile/validate/integrity/duplicate-id/provenance/doc-coverage/
  disclosure/doc-freshness all green); `disclosure` 0; `check_versions` consistent at 2.5.0;
  850 script tests pass; SKILL.md 221/500 budget.

## Confirmed findings (pre-audit)

- **F1 (discoverability):** `/sdlc-studio decisions` (add/list/promote) is absent from
  `help/help.md` yet `doc-coverage` passes - a false-green (the command registry does not see it).
- **F2 (discoverability):** the sprint **goal ladder** (triage/plan/design/done) is not named in
  SKILL.md / `help/help.md`; only conceptual.
- **F3 (discoverability):** `init`-as-greenfield-step-1, `batch`, `--template full` are not surfaced
  in the help catalogue.
- **F4 (docs):** README.md stale (2.5.0, `autosprint` headline, no v2.6/v3.0 feature set).

## Audit survivors (from the multi-agent sweep)

Two workflow runs (the first crippled by transient rate-limiting; the gap re-run covered the 12
missed lens x bucket combos, incl. all four token-economy finders). Combined: ~61 candidates ->
3-vote refute panel -> 7 survivors -> 6 merged actionable items.

- **AUDIT-1 (cr, determinism):** the Story Completion Cascade (`reference-outputs.md`) narrates
  hand-editing the story Status, index rows, and summary counts that `transition.py` /
  `artifact.py close` now own. **Scoped narrowly** (the gap panel refuted the broad "all 12 steps
  are hand-work" framing - reconcile.md draws the script-vs-judgement line): lead the cascade with
  the deterministic close; keep only the genuine judgement residue as model steps.
- **GAP-1 (bug, P1):** `sprint plan --crs proposed` (lowercase, as `help/help.md` shows) silently
  selects an empty batch - `select_batch` compares the raw arg against the canonical title-case
  status. Untested path. Fix: canonicalise the arg + fail loudly on no-match + correct the docs.
- **GAP-2 (cr, P1):** `help/reconcile.md` never names `scripts/reconcile.py`; frames all fixes as
  model prose - invites hand-recomputing counts (the recorded corruption mode).
- **GAP-3 (cr, P2):** `--no-artifacts` suppress/enforce behaviour restated verbatim across
  `reference-epic.md` / `reference-story.md` / `reference-outputs.md`; collapse to one anchor.
- **GAP-4 (cr, P2):** best-practices omit SOTA linters (no ShellCheck/shfmt; no Ruff/mypy section
  in `python.md`); `code check` has no shell entry; teaches bare `set -e` not `set -euo pipefail`.
- **GAP-5 (cr, P3, bundled with GAP-4):** `python.md` Type Hints example uses `typing.Optional`
  against the PEP 604 / 3.10+ floor the project otherwise targets.

**Assessed, not filed (refuted or defensible):** always-loaded Type Reference "third copy" (panel
kept it - it serves the router's at-a-glance purpose; F3 *adds* `init`/`decisions` to it rather
than removing it); 11 baked language guides (progressive-disclosure tier 3, not always-loaded);
persona relevance-scoring weights (optional LLM rubric, not a deterministic-scorer claim);
architecture language-selection matrix (deliberate house opinion). One true side-finding from a
refuter: a duplicate `{#database-default}` anchor in `reference-architecture.md` that
`check_links.py` does not catch - folded into GAP-house-keeping.

## Verdict

**Lean and coherent; shipped as v3.0.1.** The full adversarial sweep (4 lenses, ~61 candidates)
plus the targeted best-practice / progressive-disclosure / token reviews produced **6 actionable
survivors** (refute rate ~90%), all fixed before the tag: BG0034 (lowercase-status silent-empty
bug), CR0100 (cascade re-anchored on `artifact.py close`), CR0101 (reconcile help -> script),
CR0102 (`--no-artifacts` to one anchor), CR0103 (SOTA linters), CR0104 (router discoverability:
`decisions` / goal ladder / `init`), CR0105 (id-allocation for review/retro). The refute panel
**kept** the always-loaded Type Reference and the 11 baked language guides (removal refuted -
progressive disclosure already tiers them). Token surface: SKILL.md stayed at ~225/500 lines; the
description is the invocation-trigger surface (kept). 855 tests, gate clean, versions consistent
at 3.0.1 across the five homes (package.json, version.yaml, SKILL.md, README, CHANGELOG).
Forward-ported to all three install targets.
