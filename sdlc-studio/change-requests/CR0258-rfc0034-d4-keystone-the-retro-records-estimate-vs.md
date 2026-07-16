# CR-0258: RFC0034 D4 (keystone): the retro records estimate-vs-actual size and accumulates velocity

> **Status:** Complete
> **Size:** L
> **Priority:** P2
> **Type:** Feature
> **Date:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/templates/reviews/retro.md, .claude/skills/sdlc-studio/scripts/telemetry.py

## Summary

The measure half of the sizing loop, and the keystone of RFC0034 - it produces the history that calibrates the S/M/L token bands (D1) and the capacity budget (D3). **Corrected premise (RFC0034 D2):** telemetry.py has the `tokens` and `wall_time_s` FIELDS, but only wall-clock is actually captured - a script cannot observe LLM token spend, and in practice the `tokens` field has NEVER been populated (330 records, zero token values). So this CR has two parts, not one: (1) a TOKEN SUPPLIER - run each unit as an instrumented subagent and feed its reported usage into `artifact.py close --tokens`, so a real token actual exists; and (2) wire retro.py + the retro template to read that actual (tokens; wall-clock works today) against the plan's estimated size, record the accuracy ratio per unit and per sprint, and accumulate a velocity/accuracy history the next plan reads. Answers 'were the estimates accurate?' - today unanswerable because nothing measures tokens.

## Supplier PoC (proven 2026-07-14)

The token supplier is validated end-to-end. A unit (BG0126) was run as a background subagent; its completion notification carried `<usage><subagent_tokens>46792</subagent_tokens><duration_ms>271825</duration_ms></usage>`. Feeding those into `telemetry.py record --id BG0126 --type bug --tokens 46792 --wall-time-s 272` produced the **first telemetry record with a real token value** (of 330+ prior records, all null). So the mechanism this CR needs already works with the existing pieces: harness-reported subagent usage -> `telemetry.py record`. What remains for the CR is to make the sprint/autosprint loop do it automatically per unit, and to compare the actual against the plan estimate.

## BLOCKED on BG0131 (the token metric is not valid)

The supplier PoC delivered three real units and the reported token figure did NOT track the work: 42.7k-46.8k (+/-9%) across units whose wall-clock varied 240% and whose kind differed completely. It correlates with neither wall-clock nor tool-uses. So the token half of this CR is blocked until BG0131 establishes what the figure actually counts and sources a valid actual. **The wall-clock half is unaffected** and can proceed - it demonstrably differentiated all three units.

## Cross-harness portability

The supplier is a neutral SINK plus a per-harness SOURCE adapter, and must stay that way - the skill installs to five harnesses and is ecosystem-neutral. `telemetry.py record --tokens --wall-time-s` is portable (plain Python, any harness calls it). Only the token NUMBER is harness-specific: Claude Code reports `subagent_tokens` on a subagent completion (the PoC path); a raw-API harness reads the `usage` field on every response (precise, always present); Codex/Gemini CLIs expose their own usage output; a harness with no token visibility gets none. So the CR must abstract the source, not hardcode subagents. **Wall-clock is the universal floor** - every harness can measure elapsed time, so wall-clock velocity works everywhere and token velocity works wherever usage is exposed (always, for anything built on an LLM API).

## Impact

Every sprint close gains an estimate-vs-actual readout and the project gains a velocity baseline it has never had. Once history accumulates, the provisional S/M/L token bands (CR0257) and the capacity budget (D3 CR) recalibrate from real data instead of a guess.

**Effort:** L

## Acceptance Criteria

- [ ] A real token actual is recorded per unit: the loop runs a unit as an instrumented subagent
      (or equivalent) and feeds its reported usage into `artifact close --tokens`, so the
      telemetry `tokens` field carries a measured number rather than null.
- [ ] The retro template carries an estimate-vs-actual size section, and the retro spine populates
      it from telemetry (`tokens` / `wall_time_s`) against the plan estimate, recording the
      accuracy ratio - the retro states how wrong the plan was, in a number.
- [ ] A velocity/accuracy history accumulates across retros and the NEXT plan reads it, so the
      second sprint is estimated with the first sprint's evidence.
- [ ] The S/M/L -> token-band mapping recalibrates from that accumulated history rather than
      staying at its seeded guess, and the recalibration is proved against a history in which the
      naive band is demonstrably wrong (LL0010).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Raised |
