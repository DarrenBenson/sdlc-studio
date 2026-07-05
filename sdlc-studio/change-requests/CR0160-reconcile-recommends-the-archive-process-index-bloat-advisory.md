# CR-0160: reconcile recommends the archive process: index-bloat advisory when terminal rows exceed a threshold

> **Status:** Complete
> **Priority:** Medium
> **Type:** Improvement
> **Date:** 2026-07-05
> **Created-by:** sdlc-studio file

## Summary

The progressive-disclosure archive machinery (scripts/archive.py, census-union) is shipped but dormant: nothing recommends it, so even the skill's own repo carries ~213 terminal rows in live indexes and a consuming project's first reconcile ran over a 302-row index. detect gains an ADVISORY finding kind index-bloat per type when live-index terminal rows exceed indexes.archive_after (default 30), naming the archive command; status hint surfaces it; the release-gate workflow gains an archive step. Advisory only - archive stays operator-run.

## Acceptance Criteria

- [ ] detect emits one index-bloat advisory per over-threshold type naming the terminal-row count, threshold, and the archive.py command; under-threshold and already-archived indexes stay silent
- [ ] the advisory never blocks: gate and apply behaviour unchanged
- [ ] indexes.archive_after is config-overridable; status hint mirrors the advisory
- [ ] release-gate template carries the archive step; this repo's indexes archived under the v3.4.0 label with 0 census drift after

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-05 | audit | Raised |
| 2026-07-05 | Claude (tranche close) | Delivered in the token-optimisation tranche (pre-v3.5.0): Sam Eriksson (QA seat, review render) APPROVE after two adversarial rounds; details in CHANGELOG [Unreleased] |
