# CR-0431: TRD and D0020 rest on 'a script cannot observe token spend', falsified by run_state.session_tokens

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** sdlc-studio/trd.md
> **Date:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0

## Summary

The stated reason a token budget never gates - a script cannot observe token spend - is false against shipped code: `run_state.session_tokens()` measures spend from the harness transcript and maintains a baseline precisely because the measurement is real. The genuine surviving limit (delegated/sidechain spend is invisible, so totals are lower bounds) lives only in `run_state.py` comments, so a future reader weighing a token breaker reasons from a wrong premise.

## Impact

The stated reason a token budget never gates - a script cannot observe token spend - is false against shipped code: `run_state.session_tokens()` measures spend from the harness transcript and maintains a baseline precisely because the measurement is real. The genuine surviving limit (delegated/sidechain spend is invisible, so totals are lower bounds) lives only in `run_state.py` comments, so a future reader weighing a token breaker reasons from a wrong premise.

## Acceptance Criteria

- [ ] Amend the TRD sections and the D0020 row to the real premise: tokens are transcript-measured but a lower bound (delegated spend invisible), and record that as the reason a breaker is or is not appropriate.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Raised |
