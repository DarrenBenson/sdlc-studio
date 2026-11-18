# CR-0739: This repository declares a component map so its gate scripts are classed high risk

> **Status:** Complete
> **Decomposed-into:** EP0376
> **Priority:** High
> **Type:** Improvement
> **Size:** S
> **Affects:** sdlc-studio/.config.yaml, tools/tests/test_repo_risk_map.py
> **Evidence:** D0520, operator ruling of 2026-11-17
> **Date:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T22:15:35Z

## Summary

`lib/risk_class.py` gives each story a risk class from the project's `risk.components` map, and D0511 makes high risk the trigger for heavier review. This repository declares no map, so every unit here is standard and the trigger never acts on the scripts that refuse or sign work. D0520 rules the map: high for gate.py, critic.py, transition.py, sprint.py, `verify_ac.py` and .githooks, elevated for the rest of the skill's scripts. Stories refined before the map carry a stamped class of standard and need the class the map now gives.

## Impact

Every review of a unit that changes a gate in this repository; today none is treated as high risk.

## Acceptance Criteria

- [ ] `sdlc-studio/.config.yaml` declares the D0520 map and `lib/risk_class.py` loads it with no notes
- [ ] Open stories whose Affects touch a mapped path carry the class the map gives

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Raised |
