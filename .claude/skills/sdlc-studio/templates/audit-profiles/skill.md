# Audit Profile: skill

The packaged lens pack for auditing an **agent skill itself**. The four
lenses proven on the 2026-06-20 self-audit run. Load this pack as the profile when the
project under audit *is* a skill (vs the default project profile in
`reference-audit.md#audit-project-profile`).

> **Refute panel:** shared - 3 skeptics per candidate, survive on >= 2 of 3
> (`reference-audit.md#audit-refute`). This pack does not opt out.

Use each row as the `{{lens}}` / `{{lens_question}}` of `audit-finder.md`, one finder
per lens, looped until-dry; then the shared refute panel and filer.

| Lens | Adversarial question | Hunts for |
| --- | --- | --- |
| over-engineering | What here is heavier than the problem requires? | speculative generality, unused abstraction, baked content that should generate on demand, capability files no one reaches |
| token-economy | What costs tokens out of proportion to its value? | always-loaded bloat, duplicated/triplicated guidance, prose re-derived every run that a script could do once |
| determinism | What is LLM prose that should be a deterministic script? | hand-applied index fixes, count/row drift, "the model will keep it in sync" guarantees that are false |
| external-benchmark | Where does a known external tool or standard outperform this? | reinvented rankers/parsers/metrics; claims that don't match the benchmarked state of the art (e.g. lexical vs PageRank repo maps) |

## Notes

- This pack is declarative: a lens is a name + an adversarial question + what it hunts.
  A project extends a profile by appending rows (see `reference-audit.md#audit-extend`).
- The companion **project profile** (per-artifact-type lenses + cross-artifact
  coherence) is the default and lives in `reference-audit.md#audit-project-profile`.
- Cost on the proving run: 4 lenses, loop-until-dry -> 69 candidates -> 28 survivors
  (~59% refuted) -> 18 filed. Budget accordingly (`--budget`, round caps).
