# BG1106: package-lock.json resolves smol-toml 1.7.1 and katex 0.16.47 through markdownlint-cli 0.49.1, inside Dependabot alerts 25 and 24

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** package.json, package-lock.json, changelog.d/BG1106.md
> **Evidence:** GitHub's push response for 7f3e91a9 on 2026-10-21: '2 vulnerabilities on DarrenBenson/sdlc-studio's default branch (1 moderate, 1 low)'. The Dependabot API lists alert 25 (smol-toml, medium, created 2026-10-13T13:48:12Z) and alert 24 (katex, low, created 2026-10-13T13:48:11Z). `npm ls` resolves both under markdownlint-cli@0.49.1.
> **Created:** 2026-10-21
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-21T06:47:17Z

## Summary

Two Dependabot alerts have been open on main since 2026-10-13, and nothing in the backlog records them. Alert 25 (medium): smol-toml 1.7.1, whose parse() is quadratic in the document because parseKey rescans to the end on each key line; vulnerable to 1.8.0, patched in 1.9.0. Alert 24 (low): katex 0.16.47, where existing prototype pollution can bypass trust restrictions; vulnerable from 0.11.0 to before 0.18.2, patched in 0.18.2. Both reach the tree only through the markdown lint chain: markdownlint-cli 0.49.1 depends on smol-toml directly, and on katex through markdownlint 0.41.1 and micromark-extension-math 3.1.0. Neither ships in the skill.

## Steps to Reproduce

`npm ls smol-toml katex` prints both under markdownlint-cli@0.49.1; `gh api repos/DarrenBenson/sdlc-studio/dependabot/alerts` lists alerts 24 and 25 as open.

## Proposed Fix

Move the lock to patched versions: a markdownlint-cli release that resolves smol-toml 1.9.0 or later and katex 0.18.2 or later, or npm `overrides` pinning both, as BG0866 did for js-yaml. Re-run the markdown lint chain to confirm it still passes.

## Acceptance Criteria

- [ ] **AC1** package-lock.json resolves smol-toml at 1.9.0 or later and katex at 0.18.2 or later, and `npm run lint:md` still passes
  - **Verify:** shell node -e "const l=require('./package-lock.json').packages;const v=p=>(l['node_modules/'+p]||{}).version||'0';const ge=(a,b)=>{a=a.split('.').map(Number);b=b.split('.').map(Number);for(let i=0;i<3;i++){if(a[i]!==b[i])return a[i]>b[i]}return true};process.exit(ge(v('smol-toml'),'1.9.0')&&ge(v('katex'),'0.18.2')?0:1)" && npm run lint:md

## Impact

Low. Both packages run only in the repository's own lint chain, over this repository's own trusted markdown. The cost is a security page that stays red, so a real alert is harder to see.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-21 | Claude Opus 5.5 | Filed |
