# Independent recompute note (2026-07-10)

Every figure in docs/benchmarks/2026-07-10-v4-rerun.md and in the white paper's
evidence sections was recomputed from the raw sources by an independent reviewer
instance (Sam Eriksson, QA seat) across four review rounds before publication:

- Row populations: 72 measured (30 v4-, 30 v4s-, 12 v4o-), 10 calibration-phase
  mandated addendum (5 v4sm-, 5 v4om-), 1 calibration probe (v4cal-1); no duplicate
  (prefix, fixture, arm, run_id) keys in runs.jsonl.
- Escape counts per cell, token means and overhead ratios, all 12 pricing cells
  (from the disclosed 80/20 blend at July 2026 list rates), rubric cell means and
  the behavioural-verdict convergence check (zero violations), audit scores.
- Matrix escapes: 19 recorded of 72 (26.4%); 17 behavioural (23.6%) after the two
  disclosed oracle-phrasing artefacts; 20 of 82 (24.4%) including the addendum.
- Verdicts recorded in sdlc-studio/reviews/critic-verdicts.md (CR0228, CR0227).

The full review outputs live in the session transcripts; this note is the archived
summary the white paper's claims register points at.
