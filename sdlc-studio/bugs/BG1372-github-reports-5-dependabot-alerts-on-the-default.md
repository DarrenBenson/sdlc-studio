# BG1372: GitHub reports 5 Dependabot alerts on the default branch (1 high, 2 moderate, 2 low)

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** package.json, package-lock.json, changelog.d/BG1372.md
> **Evidence:** RUN-01M77177, 2026-11-12: every push; operator ruling to file for run eleven
> **Created:** 2026-11-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run ten orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-12T13:22:07Z

## Summary

Every push this run printed the alert count. Nobody has triaged them; they predate run ten.

## Steps to Reproduce

Push to main: the remote prints '5 vulnerabilities on the default branch'.

## Proposed Fix

Triage each alert; upgrade the dev dependency it names where it applies.

## Acceptance Criteria

- [ ] **AC1** Given the alerts, each is triaged: fixed by an upgrade, or recorded as not affecting the project with its reason. Fails on: an alert left untriaged.
  - **Verify:** manual: the Dependabot alerts page shows no open alert without a triage note

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-12 | Claude Opus 5.5 (run ten orchestrator) | Filed |
