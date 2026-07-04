# BG0033: five moderate npm dependency vulnerabilities via markdownlint-cli

> **Status:** Closed
> **Created:** 2026-06-22
> **Created-by:** sdlc-studio new
> **Severity:** Medium

## Summary

World-class review (external-benchmark lens). `npm audit` reports 5 moderate-severity vulnerabilities (brace-expansion, js-yaml, markdown-it, smol-toml) pulled transitively via `markdownlint-cli`. DoS-class; the CI lint toolchain is exposed.

## Steps to Reproduce

`npm audit` reports them; CI toolchain exposed.

## Proposed Fix

- [x] `npm audit fix` clears the non-breaking ones
- [x] bump `markdownlint-cli` to a patched line; revalidate `.markdownlint.json` + run `lint:fix`
- [x] `npm audit` reports 0 moderate+; `npm run lint` still green

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-22 | sdlc | Created via `new` (deterministic) |
