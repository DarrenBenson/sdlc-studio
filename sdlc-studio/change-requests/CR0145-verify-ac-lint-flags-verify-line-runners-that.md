# CR-0145: verify_ac lint flags Verify-line runners that are not on PATH (design-time, not delivery-time)

> **Status:** Complete
> **Priority:** Medium
> **Type:** Improvement
> **Date:** 2026-07-04
> **Created-by:** sdlc-studio file

## Summary

This repo's story convention wrote pytest Verify lines on a machine without pytest; the gap only surfaced at verify time, mid-sprint, and the lines were rewritten to unittest under delivery pressure. The soft-dependency doctrine says only the tools your verifiers reference need installing - but nothing checks that the referenced tools ARE installed at the moment the lines are authored. The audit's weak-verify check already lints Verify lines for DSL shape; runner availability is the missing half.

## Design (settled at the sprint design rung)

- Runner token = first word of the Verify expression (the existing lint lane's
  parse); check `shutil.which(token)` only for the known runner set
  (pytest/jest/vitest/go/curl/jq/rg) - anything else already falls to the
  shell-fallback lint. Finding wording per the AC owns the author-vs-CI PATH
  ambiguity. Surfaced through `verify_ac lint` and the audit's weak-verify reuse;
  never affects exit codes on its own.

## Acceptance Criteria

- [ ] verify_ac lint (and the audit weak-verify path that reuses it) flags a Verify line whose runner token (pytest/jest/vitest/go/curl/jq/rg) resolves to no executable on PATH, with the install-or-rewrite remedy in the finding
- [ ] manual lines and the shell runner are exempt (sh is always present); the check is
      STRICTLY advisory and never blocks - the finding wording owns the ambiguity that the
      author machine's PATH may differ from the verifier/CI machine's (e.g. "pytest not on
      THIS machine's PATH - install it here, rewrite the line, or ignore if verification
      runs elsewhere")
- [ ] unit tests pin present/absent runner cases; CHANGELOG [Unreleased]

## Out of Scope

- A declared-runner manifest (the sturdier design: the project names its runners once and the
  lint checks declarations, not PATH) - a follow-on if the advisory check proves noisy.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | audit | Raised |
| 2026-07-04 | claude | Operator review applied: strictly advisory, finding wording owns author-vs-CI PATH ambiguity, manifest recorded as the sturdier follow-on |
| 2026-07-04 | claude | Design settled: shutil.which over the known runner set inside the existing lint lane |
| 2026-07-04 | claude | Delivered: lint_runner_available in the lint lane, strictly advisory; 4 tests seen RED first; live-verified on this machine's missing pytest. Depth: functional |
