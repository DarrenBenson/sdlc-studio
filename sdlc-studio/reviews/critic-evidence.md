# Critic Evidence

> Append-only. The adversarial reviewer's pass per unit - findings, reviewer seat,
> author. Evidence is INPUT to the sign-off, never the sign-off itself.

| Unit | Reviewer | Author | Date | Findings |
| --- | --- | --- | --- | --- |
| US0194 | Sam Eriksson QA seat (subagent a8478a814d54c9fbb) | Claude Fable 5; agent | 2026-07-16 | APPROVE: initial REJECT (provenance tags failing lint-style; plan-review-phase reviewer accepted as delegate; evidence-requirement mutant surviving) repaired and re-verified by the reviewer re-executing its own probes and mutants: M2/M1b/M4/M5 all killed by named tests, live delegate probes refused rc=2 (case-differing principal too), tree md5-identical before/after mutations, suites 48+31 OK, full suite 2694 OK |
| US0198 | Sam Eriksson QA seat (subagent a38802d03f22e7470) | Claude Fable 5; agent | 2026-07-17 | APPROVE: initial REJECT (real chain crashed at step 1 - retro.main takes no argv, masked by all-stub tests; handoff outcome hard-coded goal-reached under a partial verdict; cost-note unmeasured-branch mutant survived) repaired: signature-aware \_run\_cli + a real-chain no-stub test proven to guard the break, outcome derived from the recorded verdict, unmeasured spend named not zeroed; reviewer re-executed all mutants (each killed) and the real-workspace probes, tree md5-identical, 147 tests OK |
