# RETRO-0010: Sprint 2026-07-D - field-hardening: the convention layer and adoption onboarding

> **Date:** 2026-07-05
> **Batch:** CR0151, CR0152, CR0153, CR0154, CR0155, CR0156, CR0157, CR0158 (all Proposed CRs; RFC0023 accepted as D0010, built as CR0158)
> **Goal:** close the loop on the first external consumer's field reports - retire the exact-string false-gate class, make sampling and provenance honest, and turn upgrades into onboarding
> **Delivered:** 8 / 8   **Blocked:** 0

## Delivered

- CR0152 - sampled/enumerated fraction on every mutation output path; its first
  production print was this sprint's own close run (25/3116, 0.8%)
- CR0153 - one `index-status-column` diagnostic instead of a 302-row storm;
  apply refuses the degenerate index loudly
- CR0158 - `lib/conventions.py`: the tolerant convention layer (RFC0023/D0010),
  config-declared, fail-loud, byte-identical when unconfigured
- CR0154 - header-based companion detection through the layer (wave 2 adopter)
- CR0155 - bug-readiness heading vocabularies through the layer (wave 2 adopter)
- CR0156 - the dormant `Verified` bug status defined onto the depth tiers, with
  the Fixed -> Verified promotion gated on a tier above functional
- CR0151 - sprint plan names its seat-score provenance and staleness
- CR0157 - `project upgrade` prints the capability delta and names unbaselined
  advisory gate lanes; install.sh ships the CHANGELOG

## Blocked / deferred

- None. CR0159 filed at close (critic follow-up: apply cannot insert a missing
  summary status row - pre-existing, demonstrated at the prior release commit).

## What went well

- Six of eight units were direct field reports from one consuming project,
  filed through the skill's own `file_finding`/`new` tooling - the first
  external dogfood loop closed within a day of the reports landing.
- The adversarial critic pass earned its cost twice over: two HIGH findings
  (id-collision minting via the census change; the archive row masking the
  degenerate-index diagnosis) that the 1,100-test green suite and a clean
  25/25 mutation sample both missed. Independent refute framing with mandatory
  runnable repros remains the sharpest tool in the close.
- CR0152's disclosure line fired in production the same session it shipped,
  and correctly prompted the deeper 60-budget pass that found the one real
  survivor in the new layer.

## What was hard / what stalled

- CR0154's census redefinition looked local but rewired a safety property
  four consumers away: `next_id` had silently inherited "counted = exists"
  as its allocation base. The fix separated the concerns - allocation keys
  on filenames, visibility lives in validate, counting stays header-based.
- The heading matcher went through three semantics (equality -> containment
  -> equality-or-prefix) before the false-positive space was properly mapped;
  the critic's negating-heading examples ("Unable to Reproduce - Steps
  Tried") were the decisive evidence the suite lacked.
- A `ConventionsError` designed to fail loud was silently converted to a
  non-blocking warn by the gate's crash containment - two correct local
  policies composing into a false green. Worth watching for as a class.

## Lessons

- L-0005 (added this close): a census-definition change must be swept to every
  consumer that keyed a SAFETY property on the old definition - id allocation,
  dedup, and existence checks may all silently inherit "counted = exists".
- Reaffirmed L-0001 (sibling-parser sweep) and LL0008/LL0009 (silent
  misleading failure outranks loud failure): both HIGHs were silent-clean
  classes, not crashes.

## Metrics

- Duration: ~4.6h sprint-open to close · Units: 8/8 green-committed
  individually · Critic rounds: 2 (9 findings: 2 HIGH, 3 MEDIUM, 4 LOW; all
  fixed, repros re-run by the same critic instance, final verdict APPROVE) ·
  Mutation: 25/25 sprint-wide sample killed, 41/41 viable on the new layer
  after one survivor killed via a strict-bool contract pin · Telemetry: batch
  close recorded for all 8 units (iterations=2, wall-time 4560s, verdict
  approve)
