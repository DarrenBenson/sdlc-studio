# BG0075: npm run lint fails at HEAD: the pre-commit gate was never enabled in this clone and CI is dark while main is unpushed

> **Status:** Fixed
> **Severity:** High
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio file
> **Verification depth:** functional (npm run lint exit 0 end-to-end; enabled hook observed running every guard lane on the fix commit itself)

## Summary

rc-verdict: BLOCKS v4.0 tag. npm run lint exits 1 at HEAD: 26 markdownlint errors across 10 files (CHANGELOG.md:29/30/34/221, sdlc-studio/decisions.md:31, decisions/ep0019-plan-integrity.md:13, ep0020-upgrade-rebaseline.md:15, and MD028/MD012 in EP0001-0004/0008/0009 from commit 841471e). Mechanism (RV0007 test/CI leg): git config core.hooksPath is UNSET in this clone (.git/hooks holds only samples), so the tracked hook (.githooks/pre-commit, which lints repo-wide from node_modules) never ran; the Lint workflow triggers only on push/PR and main is 65 commits ahead of origin under the release freeze, so the CI backstop is dark; agents ran selective guards by hand (gate.py has no markdown lane, so commit messages claiming 'gate PASS'/'style/links clean' were true-but-misleading). Six commits landed markdown-breaking content unchecked; LATEST.md:10 'lint clean' and the rc hygiene claims are falsified; the rc push itself would turn CI red.

## Steps to Reproduce

npm run lint -> exit 1 (markdownlint). git config core.hooksPath -> unset, exit 1. git log origin/main..main --oneline | wc -l -> 65.

## Proposed Fix

bash tools/enable-hooks.sh in this clone; npm run lint:fix plus hand-fix MD024/MD028; add a full 'npm run lint' row (and a hook-enablement check) to the rc-readiness checklist before tagging.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | audit | Filed |
