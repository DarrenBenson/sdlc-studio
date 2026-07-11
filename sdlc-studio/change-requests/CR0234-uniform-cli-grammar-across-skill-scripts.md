# CR-0234: Uniform CLI grammar across skill scripts

> **Status:** Proposed
> **Priority:** P3
> **Type:** Improvement
> **Date:** 2026-07-11
> **Created-by:** sdlc-studio file

## Summary

The scripts disagree on argument shape, so an agent must relearn each one mid-flow. Today's examples: status.py rejects a global '--root .' (root only exists per-subcommand, unlike validate.py/reconcile.py which accept it uniformly); transition.py set refuses '--author' alone on a non-terminal transition (the verdict triple is all-or-none, but recording WHO accepted an RFC is a legitimate single field); artifact.py accepts --root everywhere. One grammar: global --root on every script, and identity fields recordable without the full verdict ceremony on non-terminal transitions. Related friction noted but unfiled from the RV0007 sprint retro.

## Acceptance Criteria

- [ ] Every skill script accepts --root as a global flag (before or after the subcommand)
- [ ] transition.py set records --author on a non-terminal transition without requiring --verdict/--reviewer
- [ ] A CLI-grammar conformance test sweeps every script's argparse tree

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-11 | audit | Raised |
