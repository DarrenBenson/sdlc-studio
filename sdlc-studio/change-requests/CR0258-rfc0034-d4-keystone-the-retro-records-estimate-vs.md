# CR-0258: RFC0034 D4 (keystone): the retro records estimate-vs-actual size and accumulates velocity

> **Status:** Proposed
> **Priority:** P2
> **Type:** Feature
> **Date:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/templates/reviews/retro.md, .claude/skills/sdlc-studio/scripts/telemetry.py

## Summary

The measure half of the sizing loop, and the keystone of RFC0034 - it produces the history that calibrates the S/M/L token bands (D1) and the capacity budget (D3). **Corrected premise (RFC0034 D2):** telemetry.py has the `tokens` and `wall_time_s` FIELDS, but only wall-clock is actually captured - a script cannot observe LLM token spend, and in practice the `tokens` field has NEVER been populated (330 records, zero token values). So this CR has two parts, not one: (1) a TOKEN SUPPLIER - run each unit as an instrumented subagent and feed its reported usage into `artifact.py close --tokens`, so a real token actual exists; and (2) wire retro.py + the retro template to read that actual (tokens; wall-clock works today) against the plan's estimated size, record the accuracy ratio per unit and per sprint, and accumulate a velocity/accuracy history the next plan reads. Answers 'were the estimates accurate?' - today unanswerable because nothing measures tokens.

## Impact

Every sprint close gains an estimate-vs-actual readout and the project gains a velocity baseline it has never had. Once history accumulates, the provisional S/M/L token bands (CR0257) and the capacity budget (D3 CR) recalibrate from real data instead of a guess.

**Effort:** L

## Acceptance Criteria

- [ ] A real token actual is recorded per unit: the loop runs a unit as an instrumented subagent (or equivalent) and feeds its reported usage into `artifact.py close --tokens`, so telemetry `tokens` is populated rather than null. Verify: python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -k 'telemetry or token'
- [ ] The retro template carries an estimate-vs-actual size section, and retro.py populates it from telemetry (tokens/`wall_time_s)` against the plan estimate, recording the accuracy ratio. Verify: rg -qi 'estimate.*actual|accuracy|velocity' .claude/skills/sdlc-studio/templates/reviews/retro.md
- [ ] A velocity/accuracy history accumulates across retros and is readable by the next plan. Verify: python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -k 'retro or velocity'
- [ ] The S/M/L -> token-band mapping recalibrates from the accumulated history (LL0010: prove it against a fixture history where the naive band is wrong). Verify: python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -k calibrat

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Raised |
