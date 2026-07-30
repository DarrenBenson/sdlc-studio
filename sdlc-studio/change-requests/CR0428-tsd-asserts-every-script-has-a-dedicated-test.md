# CR-0428: TSD asserts 'every script has a dedicated test' twice while its own coverage map says the rule is unenforced, and both d

> **Status:** In Progress
> **Decomposed-into:** EP0168
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** sdlc-studio/tsd.md
> **Date:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0
> **Audit-lens:** unknown
> **Audit-run:** wf_804ef18d

## Summary

The TSD states the per-script test contract as met in absolute terms in two places, contradicts both in its coverage map ('a convention held in review, not an automated build gate'), and the map itself is stale both ways: triage.py and lib/tiers.py have no dedicated test module, while `test_refine.py` and `test_run_state.py` now exist despite being listed as indirect-only.

## Impact

The TSD states the per-script test contract as met in absolute terms in two places, contradicts both in its coverage map ('a convention held in review, not an automated build gate'), and the map itself is stale both ways: triage.py and lib/tiers.py have no dedicated test module, while `test_refine.py` and `test_run_state.py` now exist despite being listed as indirect-only.

## Acceptance Criteria

- [ ] Rewrite the two absolute claims to the caveated wording, refresh the exception list in both directions, and (preferably) add the enumerating sweep the TRD rule mandates so the contract stops being prose.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Raised |
