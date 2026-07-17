# Reviews - LATEST (anchor)

> Derived from the sprint-close review of **RUN-01KXR6XS** (the spec-truth refresh
> sprint, 2026-07-17, RETRO0046). Supersedes the RV0012 picture.

## Where the pipeline is (2026-07-17)

The **spec-truth refresh sprint** (RUN-01KXR6XS) is delivered: **EP0071 (12 stories,
US0201-US0212) Done and every AC verified, plus the 5 open bugs BG0182-BG0186 Fixed**
(17 units, 42 points, Sprint Goal judged ACHIEVED, RETRO0046). This closes the
RV0010/RV0012 residual spec-rot: PRD/TRD/TSD/RFC0034 now match shipped `main` on the
cost model (Fibonacci points, forecast = sum(Points) x measured rate, r=+0.68), the
three network paths, the real config defaults (`require_ac_verification: false` was
wrongly documented as on), the ULID guarantee, the two-backlog model, rule 5's writer
set, the migration surface, and RFC0034's partial supersession by RFC0038. BG0184
(the batch's own unblocker) fixed the cross-epic-ac false-block; US0208 also hardened
`critic.py` `read_verdicts`.

## CODE leg

Closing full-diff adversarial pass (independent instance, refute framing, a repro per
claim): the full suite + guards were green (2817 tests, drift 0), and two findings
survived and were fixed test-first - a MAJOR (US0211 left six stale "2151 tests"/"76
modules" pins so the TRD self-contradicted; swept to bands) and a MINOR (the BG0185
near-miss detector false-positived on bracketed prose; tightened with a shape test).
The reviewer refuted nothing else and positively confirmed the cost-model, network,
ULID, config-default and TSD-gate claims against shipped source. APPROVE.

## Document legs

PRD/TRD/TSD and RFC0034/RFC0038 are the documents this sprint corrected - they now
match shipped behaviour. Every doc-truth story closed on an executable `grep`/`pytest`
Verify line.

## Next steps

- Follow-up filed this sprint: **BG0187** (TRD §9 threat model still calls `plan.py
  archive` the sole write exception, contradicting the enriched §5 rule 5).
- Standing: **CR0278** (interactive-sprint token capture) - reconfirmed; per-unit token
  actuals were not captured this run, so est/actual is uncomputable.
- **Un-owned `RFC0047`** appeared in the working tree mid-run (created via `new`, not by
  this sprint - likely a parallel session on the shared repo); left untracked for its
  author, flagged at sign-off.
- Residual audit CRs (CR0280-CR0306) remain for a future scheduled batch.
- Release freeze holds until ~2026-07-21; everything lands unreleased on `main`.
