# CR-0679: Make the critic brief a complete review packet: claim surfaces first in the capped diff with the full diff written beside it, a one-line `--out` delivery read in one call, verifier and selected-test results computed at brief time against a current verify stamp, and a round-2 rejoinder scoped to the repair

> **Status:** Proposed
> **Parent:** RFC0062
> **Priority:** Medium
> **Type:** Improvement
> **Size:** L
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/reference-agent-prompt-template.md, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Evidence:** RFC0062 Phase 3, review-economy lens: findings 1, 5, 6, 7 and 8; agent-context lens: finding 6; tool-output lens: finding 3; ceremony lens: finding 7
> **Date:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T12:23:34Z

## Summary

The brief's scope line tells the reviewer to inspect with git diff the diff it already carries (critic.py:3523 against :3501-3503); reviewers then made 48 diff calls (0.77M issuing) and 30.5 artefact reads or diffs (0.48M). The 400-line cap cut the diff in 11 of 18 briefs, and because `_unit_diff_section` takes git's name order (critic.py:3397-3410) the unit's own artefact was cut in every single-unit cut whose Affects held it, though 4 of the 8 round-1 blockers were claim or prose defects. 18 reviews took 40 to 45 brief-reading calls, because the dispatch said to read with sed -n ranges and the brief prints to stdout. Each reviewer re-ran the verifier (18 messages, 197k), about half of 27 test-run messages (328k) were not mutant-driven, and the brief carries the verify command, not its result (critic.py:3427-3431). `verify_ac` stamps never refused a transition in runs five and six (0 red in 37 runs), yet a criterion runs up to three times. A rejoinder is `brief()` plus a RE-REVIEW section (critic.py:3540-3567), so each round 2 re-carried the full diff and FILE HISTORY (25k to 31k chars); six round-2 reviews cost 2.22M. FILE HISTORY is 7.2% of brief bytes and no run-six verdict cites it. Already true of the tree.

## Impact

Reviewers pay to re-fetch what the brief holds or a tool could compute, on every unit in this repository and in each consuming project that reviews with `critic.py brief`.

## Acceptance Criteria

- [ ] The capped UNIT DIFF sorts by surface (artefact, changelog.d, docs, production, tests) before the cap, the uncapped diff is written to <brief>.diff and named in the remainder line, and the scope line says the UNIT DIFF is base..HEAD for those paths; a test pins that a cut keeps the artefact and drops tests first.
- [ ] `critic.py brief --out <path>` writes the brief and prints one line (path, tokens, tier, fingerprint), and the shipped review dispatch says to read it whole in one call.
- [ ] The brief runs `verify_ac --dry-run` and the gate's test selection for the Affects and prints a RESULTS section stamped with the HEAD it ran at, red lines only; `verify_ac.py run` records the Affects digest with its stamp, transition.py and a light-tier brief accept a stamp at the current digest without re-running, and a mismatch re-runs.
- [ ] `critic.py brief --rejoinder` takes the round-1 verdict's commit from the ledger as the UNIT DIFF base, omits FILE HISTORY, keeps the per-item repair verdict, the verify command and the criteria at the round-1 tier (BG0975), and a test pins that a rejoinder's diff excludes hunks present at the round-1 commit.
- [ ] Each verdict records whether it cites FILE HISTORY, and before and after: reviewer calls per unit-review on the next sprint fall from run six's 30 (547 over 18) to at most 26.

## Recommendation

Build the packet in `critic.py brief`; the rejoinder part extends CR0615 (In Progress, the rejoinder reads the ledger). Saving 0.61M per run: diff ordering 0.30M (review-economy, order of magnitude only), one-call delivery 0.19M (review-economy's 27 extra calls x 7k; tool-output's 22 x 8k = 0.18M is the same lever, counted once), Read line-number prefixes 0.065M (agent-context) and packet results 0.35M, total 0.905M x 0.67, the review spend left once the first-time-right CRs remove their round 2s and BG1236. Counted once or not at all: agent-context's re-diff 0.20M (the same diff calls the ordering removes); the stamp's reviewer re-runs (inside packet results) and its orchestrator re-run 0.21M (inside the orchestrator replay); the rejoinder delta, 0.92M alone, carried at 0 because the first-time-right CRs are credited with removing every run-six round 2, though it is worth about 0.16M per residual single round-2 review (358k to 200k) and insures the 20% bar; FILE HISTORY 0.1M, retired only if two runs show no citation (LL0056). Risks: a packet result goes stale if the tree moves, so it is stamped with HEAD and bound by the brief fingerprint; a rejoinder misses a defect in round-1 code the first reviewer missed, which already does not block; the reviewer still runs the tests its own mutants need, and full-tier reviewers keep re-executing criteria (US0986's harness-dependent suite was found that way).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Raised |
