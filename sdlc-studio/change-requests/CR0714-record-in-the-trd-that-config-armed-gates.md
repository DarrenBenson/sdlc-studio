# CR-0714: Record in the TRD that config-armed gates stand down without PyYAML, and correct the sentences that deny it

> **Status:** Superseded
> **Superseded by:** CR0731
> **Priority:** High
> **Type:** Improvement
> **Size:** S
> **Affects:** sdlc-studio/trd.md, tools/tests/test_lean_trd_refresh.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, trd lens, survived 2 of 3 refute votes; observed at sdlc-studio/trd.md §1 Key Decisions (lines 58-60); §4 Core Technologies, Script language row (line 235); §9 Threat Model, 'Supply-chain risk' row (line 767); §13 Won't Have (lines 1329-1330); ADR-006
> **Date:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:21:36Z

## Summary

The TRD's Key Decisions summarise ADR-006 as an absent config blocks rather than disarms, and the Threat Model's supply-chain row says the scripts are pure stdlib with no third-party packages to compromise. In the code every `.config.yaml` key is read through PyYAML, and when the package is missing `project_override` in `lib/sdlc_md.py` returns the caller's default behind one warning on stderr. Gates a project armed by config therefore disarm on such a machine: two-backlog enforcement goes off, `review.author_self_check: block` reads as unset and a v3 workspace resolves `schema_version` to the fallback 2. The warn-and-default regime was settled deliberately by earlier work and the TRD admits it in the Script language row, but no ADR records the choice, the threat model has no row for it, and the summary sentences say the opposite.

## Impact

Anyone reading the TRD as the migration blueprint, and any operator running the gates on a machine without PyYAML. They are told the layer has no third-party dependency and that an absent config blocks, when in fact a gate-critical parser is a third-party package and its absence silently turns off every gate the project opted into.

## Acceptance Criteria

- [ ] The TRD carries an ADR, or an explicit carve-out inside ADR-006, stating that an absent PyYAML stands the whole project config down to built-in defaults with one warning, why that was chosen over a refusal, and which gates disarm as a result
- [ ] The Key Decisions sentence and the Supply-chain risk row no longer contradict that ADR: neither claims an unreadable config blocks, nor that no third-party package is on a gate's path
- [ ] The Threat Model has a row for a missing or tampered PyYAML with its likelihood, impact and mitigation
- [ ] A test in tools/tests fails when the TRD states pure stdlib or an absent config blocks without the PyYAML carve-out beside it

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Raised |
| 2026-11-17 | Claude Fable 5.2 | Closed as superseded by CR0731 at the discovery breakdown the operator asked for: D0505 (sdlc-studio/decisions.md line 519, RFC0066) makes PyYAML a required dependency refused at install and at the prerequisite check, so the stand-down this request asked the TRD to record as settled behaviour is being removed, not documented. CR0731's third criterion has the TRD drop the standard-library-only claim and record the ruling as an ADR, and its Affects names sdlc-studio/trd.md; D0505's own text says CR0714 is reconciled with it at refine. The threat-model row for a missing or tampered PyYAML and the tools/tests pin on the TRD's wording are not named in CR0731 and should be carried by its TRD story. |
