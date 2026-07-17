# BG0165: Escalated units evade the mixed-model refusal and pollute per-model calibration: summed multi-model attempt tokens are attributed wholly to the last attempt's model

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a
> **Delivered-by:** claude-opus-4-8

## Summary

retro.py accuracy() sums a per-attempt record's tokens across ALL attempt models (line 594) but labels the unit with only the LAST attempt's model (line 595); the mixed-model guard (line 662) and `_by_model` then see a batch where every haiku->opus escalation is a single-model 'opus' batch: `mixed` stays False, the pooled ratio the guard exists to refuse IS computed, and `_by_model` books haiku attempt tokens into opus's calibration row. The comment above the guard says 'One ratio across two models describes neither of them' - per-attempt telemetry (this sprint's headline feature) creates exactly that condition per-unit while making it invisible to the refusal, and directly contradicts the module's sprint-level doctrine (`measured_rate` excludes `MODEL_MIXED` rows because 'tokens paid by two payers carry no rate at all'). The per-model rows the refusal tells the operator to read instead are themselves cross-contaminated. AttemptsReconcileTests blesses the attribution; nothing tests refused/`by_model` with escalated units. Defect in the in-flight US0172/US0173 work. Verified 3x.

## Steps to Reproduce

Build a batch where every unit carries attempts [{haiku, N},{opus, M}]; run accuracy() - each unit is labelled 'opus', models={'opus'}, mixed=False, the pooled ratio is computed, and `_by_model`'s opus row includes the haiku tokens.

## Proposed Fix

Derive the unit's model set from all attempts: a multi-model unit marks the batch mixed (or is excluded from per-model rows, or split per attempt into its models); add tests asserting refused/`by_model` behaviour for a batch of escalated units.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Filed |
