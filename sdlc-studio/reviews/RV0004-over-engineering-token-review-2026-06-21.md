# RV0004: Over-engineering & token-cost review (2026-06-21)

> A deliberate balance check before cutting v2.3.0: have we over-built, and is the operating
> loop burning unneeded tokens? Three-front read (release recon, scripts/over-engineering survey,
> RFC0016 scope map). Verdict: **lean, with one adopted trim.**

## Over-engineering: PASS

- **Zero orphaned code.** All 35 `scripts/*.py` are referenced by a reference-*.md, help/, SKILL.md,
  another script, or a test. No dead commands, flags, or modules.
- **Complexity is safety-justified, not speculative.** The few dense spots - `gate.py`'s injectable
  `DEFAULT_CHECKS` (a testability win, every check used), `provenance._add_stamp` (content-
  preservation), `artifact._wire_story_to_epic` (exact-id + MD032 guards) - earn their lines. No
  speculative generality, no single-consumer abstractions, no parallel code paths to merge.
- **Doc surface proportionate** to a full-SDLC tool; SKILL.md is CI-budgeted; minimal duplication.

## Token cost: one real hotspot, now scaled

- **Hotspot - the uniform per-unit independent critic.** The autosprint loop spawns a full
  adversarial critic subagent per unit *regardless of stakes* - a trivial doc change cost the same
  as a parser this session. **Action:** stakes-scaled review depth (CR-B): full adversarial critic
  for code/risky units; a lighter recorded review for pure-doc/mechanical units (still recorded, so
  the `critiqued` gate and its honesty hold).
- **Audit refute-panel** (~200 agents/run) is already budget-capped and on-demand (not per-tranche
  in the loop) - acceptable.
- Everything else in the loop (conformance, verify_ac, reconcile, loop_guard, lessons) is
  deterministic Python - zero per-unit agent cost.

## RFC0016 scope correction

RFC0016 as drafted leaned into the **external authored-identity machinery** (broker-reach,
drift-detection envelope, human-ratified canon) - the external-identity side the owner said sdlc-studio must
not reinvent. **Action:** accept the lean core (charters + isolated-subagent consults + ledger-as-
record), decline the heavy tail as out-of-scope (RFC0016 Decision, CR-A).

## Outcome

No rip-out needed. Two lean follow-ups adopted - CR-A (RFC0016 lean build) and CR-B (stakes-scaled
review) - then v2.3.0. The balance the owner asked for: keep the confidence machinery, make its
cost proportionate to stakes.
