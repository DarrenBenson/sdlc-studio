# BG0159: The advertised pricing config key is silently unreachable: Claude models honour only pricing.<family> (not the hinted pricing.<model>), and any dotted model id is destroyed by config.get's dot-splitting

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/telemetry.py, .claude/skills/sdlc-studio/scripts/config.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, sdlc-studio/stories/US0173-true-cost-with-rework-unit-cost-sums-priced.md
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a

## Summary

Two verified-by-reproduction ways the documented pricing escape hatch fails silently. (1) US0173's AC1 and `sprint_report`'s rendered hint say 'Set pricing.<model> in .config.yaml', but `model_price` (telemetry.py:384-385) looks up only pricing.<family> for Claude models (claude-opus-4-8 -> 'opus'); an operator setting pricing.claude-opus-4-8: 12.0 per the printed hint silently gets the built-in 30.0 estimate default - and the telemetry docstring says pricing.<family>, so three surfaces disagree on the key (LL0016). (2) For foreign models, `model_price` builds a dotted key from the raw name and config.get splits every '.' as a path separator, so pricing: {"gpt-4.1": 5.0} is looked up as pricing->gpt-4->1 and missed; the unit reports UNPRICED/cost 0.0 despite the docstring's promise that a foreign model 'can still price it explicitly with pricing.<that-name>'. Dotted point-release names are the norm outside Claude. No test prices a full model id or a dotted name (LL0010). Six panel votes, all not-refuted.

## Steps to Reproduce

(1) Set `pricing:\n  claude-opus-4-8: 12.0` per `sprint_report`'s hint; price a claude-opus-4-8 unit - the 30.0 estimate default is used, no warning. (2) Set `pricing:\n  "gpt-4.1": 5.0`; `tel.model_price(root`, 'gpt-4.1') returns None and `unit_cost` reports {'cost': 0.0, 'unpriced': ['gpt-4.1']}.

## Proposed Fix

In `model_price`, resolve the price by direct dict access into the pricing mapping using the raw model id first (no dot-splitting - fetch the pricing block once and index it), falling back to the family key; align the docstring, `sprint_report` hint and US0173 AC1 on the one supported key form; add tests pricing a full Claude id and a dotted foreign id.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Filed |
