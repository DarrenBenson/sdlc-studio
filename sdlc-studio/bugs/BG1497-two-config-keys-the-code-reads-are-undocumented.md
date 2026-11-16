# BG1497: Two config keys the code reads are undocumented: sprint.fresh_session is missing from reference-config.md and pricing.copilot_billing from config-defaults.yaml

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/templates/config-defaults.yaml, changelog.d/BG1497.md
> **Evidence:** Run fifteen (RUN-01M7HA6R) US1170 builder hand-back, 2026-11-16.
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T05:37:16Z

## Summary

Run fifteen's US1170 builder found that sprint.py reads `sprint.fresh_session` (default warn) but reference-config.md does not document it, and lib/prices.py reads `pricing.copilot_billing` but templates/config-defaults.yaml does not carry it. A project cannot find either key from the shipped documentation; the 6.4 release notes name both with the code's defaults.

## Steps to Reproduce

grep -c `fresh_session` .claude/skills/sdlc-studio/reference-config.md (0); grep -c `copilot_billing` .claude/skills/sdlc-studio/templates/config-defaults.yaml (0).

## Proposed Fix

Document `sprint.fresh_session` in reference-config.md and add `pricing.copilot_billing` to config-defaults.yaml, each with the default the code uses; extend the config-documentation test so a key the code reads must appear in both.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Run fifteen's US1170 builder found that sprint.py reads `sprint.fresh_session` (default warn) but reference-config.md does not document it, and lib/prices.py...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: grep -c `fresh_session` .claude/skills/sdlc-studio/reference-config.md (0); grep -c `copilot_billing` .claude/skills/sdlc-studio/templates/config-defaults.yaml...
- [ ] **AC3** The proposed fix lands, pinned by a test: Document `sprint.fresh_session` in reference-config.md and add `pricing.copilot_billing` to config-defaults.yaml, each with the default the code uses; extend...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
