# CR-0291: The 'test-noise' gate leg does not run in CI (hook-only, path-conditional) and its leak detector matches only one diagnostic shape

> **Status:** Proposed
> **Priority:** Medium
> **Type:** process
> **Size:** S
> **Affects:** sdlc-studio/tsd.md, .github/workflows/lint.yml, tools/skill-tests.sh, package.json
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a

## Summary

tsd.md:195 asserts 'A test-noise gate leg keeps it that way' as if the silence standard were held by the gate of record. The noise check lives only in tools/skill-tests.sh, invoked solely by the pre-commit hook's conditional leg (only when scripts/templates/tools paths are staged, only on clones that ran enable-hooks.sh). CI runs plain `npm test` (unittest discover) with no noise check, so a noisy-but-green suite merges cleanly and --no-verify/hook-less commits never meet the check (LL0027) - contradicting AGENTS.md's 'CI runs these same checks'. The detector also greps only '^`(ERROR|WARN)[[:space:]]+/`, missing 'ERROR: msg', 'WARNING:' and stray tracebacks (LL0013) - and real 'WARNING:'-shaped emissions exist in `plan_review`/critic/reconcile. The repo treated the identical hook-vs-CI parity gap as a bug for gate.py (BG0096, fixed with a dedicated lint.yml step). Verified 3x.

## Impact

tsd.md:195 asserts 'A test-noise gate leg keeps it that way' as if the silence standard were held by the gate of record.

## Acceptance Criteria

- [ ] CI runs the noise leg (skill-tests.sh or an equivalent step in lint.yml/npm test) so a leaked diagnostic fails the build, not just the opt-in hook
- [ ] The detector catches the common leak shapes ('ERROR:', 'WARNING:', 'script: ERROR', traceback lines), with an allowlist for intentional output
- [ ] tsd.md's wording matches where the gate actually runs

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Raised |
