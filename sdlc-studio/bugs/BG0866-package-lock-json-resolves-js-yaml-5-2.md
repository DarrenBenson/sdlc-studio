# BG0866: package-lock.json resolves js-yaml 5.2.2 through markdownlint-cli 0.49.1, inside Dependabot alert 19's vulnerable range

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** package.json, package-lock.json, tools/tests/test_lean_js_yaml_patched.py, changelog.d/BG0866.md
> **Evidence:** Executed at HEAD 85042135: `npm ls js-yaml` prints `markdownlint-cli@0.49.1 -> js-yaml@5.2.2`; `gh api repos/DarrenBenson/sdlc-studio/dependabot/alerts/19` reads state open, range `>= 5.0.0, <= 5.4.0`, first patched 5.4.1, GHSA-r3ph-w7gj-g6xm ('maxTotalMergeKeys does not limit CPU use for empty merge sources'); `npm view markdownlint-cli@latest dependencies` shows 0.49.1 is the latest and pins `js-yaml: ~5.2.1`.
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-01T08:41:49Z

## Summary

The only npm dependency is the dev tool markdownlint-cli (^0.49.0). Its latest release, 0.49.1, pins js-yaml ~5.2.1, so package-lock.json resolves `node_modules/js-yaml` to 5.2.2, inside Dependabot alert 19 (GHSA-r3ph-w7gj-g6xm, vulnerable >= 5.0.0 <= 5.4.0, patched 5.4.1). Updating markdownlint-cli cannot fix it, because no release of it allows a patched js-yaml. Exposure is low: js-yaml parses this repository's own markdownlint configuration, not untrusted input. The alert stays open on the repository until the lockfile moves.

## Steps to Reproduce

Run `npm ls js-yaml`: it shows js-yaml 5.2.2 under markdownlint-cli 0.49.1.

## Premise at HEAD

Executed at `85042135`:

```text
$ node -e "const l=require('./package-lock.json'); for (const [k,v] of Object.entries(l.packages)) if (k.endsWith('js-yaml')||k.endsWith('markdownlint-cli')) console.log(k, v.version)"
node_modules/js-yaml 5.2.2
node_modules/markdownlint-cli 0.49.1
exit=0
$ gh api repos/DarrenBenson/sdlc-studio/dependabot/alerts/19 --jq '.state, .security_vulnerability.vulnerable_version_range, .security_vulnerability.first_patched_version.identifier'
open
>= 5.0.0, <= 5.4.0
5.4.1
```

## Proposed Fix

Add an npm `overrides` entry in package.json pinning js-yaml to ^5.4.1, regenerate package-lock.json with `npm install`, and run `npm run lint` before committing so markdownlint-cli is shown to load the overridden js-yaml. Changelog fragment `changelog.d/BG0866.md`.

## Acceptance Criteria

- [ ] **AC1** Given package.json and package-lock.json, when `tools/tests/test_lean_js_yaml_patched.py` reads the lockfile, then `node_modules/js-yaml` resolves to 5.4.1 or later (a semver compare, not a string match) and package.json carries the override that holds it there. Fails on: HEAD's lockfile resolves js-yaml 5.2.2
  - **Verify:** pytest tools/tests/test_lean_js_yaml_patched.py::JsYamlPatchedTests::test_the_lockfile_resolves_a_patched_js_yaml
  - **Verified:** yes (2026-10-01)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Filed |
