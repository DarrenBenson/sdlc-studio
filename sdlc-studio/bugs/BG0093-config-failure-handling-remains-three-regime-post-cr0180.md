# BG0093: config failure handling remains three-regime post-CR0180 and the decided PyYAML documentation never landed

> **Status:** Open
> **Severity:** Medium
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio file

## Summary

rc-verdict: post-v4 (degrades only on stdlib-only or misconfigured hosts). Three behaviours for the same declared .config.yaml: (A) warn-once degrade via project_override (sdlc_md.py:399-441 - the only path CR0180 AC1 covers); (B) silent default with no warning in six wrappers (triage_sampling.py:40-44, spec_guard.py:37-41, plan_review.py:53-57, triage_noise.py:39-43, status.py:83-89, sprint.py:256-260 - declared conventions silently ignored, the failure class CR0180 was raised to kill); (C) hard crash (config.py:23-27 RuntimeError without PyYAML) reached bare from route.py:52-53/:72 (its docstring :66-68 claims otherwise) and mutation.py:411-413 - the BG0062 class resurfaced. README.md ~:280 still claims 'pure standard library, no pip installs' and reference-config.md has zero PyYAML mentions, so CR0180 AC2/AC3 and US0076 AC2 are unmet in shipped docs. All verified adversarially (RV0007).

## Steps to Reproduce

On a machine without PyYAML: route.py estimate -> RuntimeError; misdeclare a convention consumed by sprint.py -> silently ignored, no warning; the same misdeclaration via project_override paths -> warned.

## Proposed Fix

Give config.get the _warn_unhonoured warn+default behaviour so wrappers unify; catch its errors in the route/mutation CLIs; add the PyYAML sentence to README and reference-config.md.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | audit | Filed |
