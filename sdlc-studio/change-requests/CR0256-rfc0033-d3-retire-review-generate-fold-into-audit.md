# CR-0256: RFC0033 D3: retire review generate - fold into audit --profile repo and remove it

> **Status:** In Progress
> **Decomposed-into:** EP0078
> **Size:** M
> **Priority:** P2
> **Type:** Improvement
> **Date:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/review_generate.py, README.md, docs/why-sdlc-studio.md

## Summary

RFC0033 D3 (Decided): review generate is the same weakness-hunt as audit, minus the refute panel, and is not well-known (model-invoked). Fold its three legs (architecture, code quality, security) into audit --profile repo WITH the refute panel, then remove review generate entirely - no alias. Switch the public docs to audit: README.md (two references), docs/why-sdlc-studio.md, docs/existing-users.md. Public-surface change: lands under the freeze on main, ships with v4.2. Depends on the audit command (D2 CR) existing.

## Impact

One weakness-hunt, one name. Anyone following the README's 'review generate' on-ramp is redirected to 'audit --profile repo', which additionally gains the refute panel. Removing a documented command name is why this ships at a version boundary, not mid-freeze.

**Effort:** M

## Acceptance Criteria

- [ ] `review generate` is gone from the script surface and the help, `audit --profile repo` carries
      its three legs with the refute panel, and no tracked doc still points a reader at the retired
      command - the README and the docs included. An operator following any shipped instruction
      lands on `audit`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Raised |
