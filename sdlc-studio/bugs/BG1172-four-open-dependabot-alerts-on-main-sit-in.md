# BG1172: Four open Dependabot alerts on main sit in development dependencies: markdown-it (High and Low), smol-toml (Medium) and katex (Low)

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** package.json, package-lock.json, changelog.d/BG1172.md
> **Evidence:** The push of 519d125c on 2026-11-02: 'GitHub found 4 vulnerabilities on DarrenBenson/sdlc-studio's default branch (1 high, 1 moderate, 2 low)'.
> **Created:** 2026-11-02
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-02T07:36:59Z

## Summary

2026-11-02, the push of 519d125c. GitHub reported 4 vulnerabilities on the default branch (1 high, 1 moderate, 2 low). The Dependabot alerts API names them: #26 markdown-it High and #27 markdown-it Low (first patched 14.3.3), #25 smol-toml Medium (1.9.0) and #24 katex Low (0.18.2), all in package-lock.json at development scope. package.json's overrides hold markdown-it at ^14.3.1, below the patched release. An installed skill carries no `node_modules`, so no consuming project is exposed. The markdownlint toolchain that the gate and CI run is.

## Steps to Reproduce

1. `gh api repos/DarrenBenson/sdlc-studio/dependabot/alerts --jq '.[] | select(.state=="open")'`.
2. Read the four open alerts and their first patched versions.

## Proposed Fix

Raise the overrides to the first patched releases (markdown-it ^14.3.3, smol-toml ^1.9.0, katex ^0.18.2), as BG0876 did for brace-expansion and markdown-it, refresh package-lock.json, and confirm `npm run lint` and `npm audit` are clean.

## Acceptance Criteria

- [ ] **AC1** `npm audit --audit-level=low` reports no vulnerability, and `npm run lint` passes.
  - **Verify:** shell npm audit --audit-level=low

## Impact

The markdown lint toolchain runs vulnerable parsers on this repository's own tracked files, and every push reports the alerts.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-02 | claude | Filed |
