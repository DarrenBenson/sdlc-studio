# BG0098: lint:md's glob skips dot-directories: the shipped skill payload is never markdownlint-checked

> **Status:** Fixed
> **Severity:** Medium
> **Created:** 2026-07-10
> **Created-by:** sdlc-studio file
> **Verification depth:** functional (payload lane exits 0 under the payload config and non-zero when a mechanics error is seeded; full npm lint green both parts; suite 1497 green)

## Summary

Found dogfooding EP0026/BG0095: package.json lint:md runs markdownlint '**/*.md' --ignore node_modules, and the glob does not match dot-directories - so every .md under .claude/skills/sdlc-studio/ (the SHIPPED payload: 51 reference files, 39 help, 73 templates) is invisible to the markdown lane of npm lint, the pre-commit hook AND CI, which all share the script. Proof: npm run lint:md reports 0 errors while a direct 'npx markdownlint .claude/skills/sdlc-studio/reference-story.md .claude/skills/sdlc-studio/reference-verify.md' flags pre-existing MD060 (table style, reference-story.md:603) and MD028/MD012 (reference-verify.md:10-15). Same guard-coverage family as the BG0075 mechanism: a lane everyone believes is running is structurally blind to the files that matter most to consuming projects.

## Steps to Reproduce

npm run lint:md -> exit 0. npx markdownlint --config .markdownlint.json .claude/skills/sdlc-studio/reference-story.md -> MD060 errors. Compare the glob expansion: node -e with glob('**/*.md') omits dot-dirs.

## Proposed Fix

Add the payload explicitly to lint:md (markdownlint '**/*.md' '.claude/**/*.md' --ignore node_modules) and lint:fix; sweep and fix the pre-existing payload errors the widened lane surfaces.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | audit | Filed |
