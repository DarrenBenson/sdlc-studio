# CR-0334: verify_ac freshness should fingerprint the AC section, not the file mtime

> **Status:** In Progress
> **Decomposed-into:** EP0072
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/transition.py
> **Date:** 2026-07-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

A status-only edit invalidates the verify report: transitioning a story (Ready->Review, Review->Done) rewrites its status header, the file mtime moves past `verified_at`, and the next Done gate demands a re-verify of ACs that did not change. At the RUN-01KXPJG9 close this forced a vacuous `verify_ac` re-run for all 8 units between sign-off and Done (and once mid-sprint for US0195). Fingerprint what the verification actually proved - a hash of the Acceptance Criteria section (ACs + Verify lines) stored in the report - and treat the entry as fresh while that hash matches, regardless of unrelated edits.

## Impact

Every close under the two-role gate pays 8+ no-op verify runs; worse, agents learn that the freshness warning is usually vacuous, which is how a REAL stale verify gets waved through.

## Acceptance Criteria

- [ ] A status-only or metadata-only edit leaves a green verify entry fresh (AC-section hash unchanged)
- [ ] Any edit inside the Acceptance Criteria section still invalidates it

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Raised |
