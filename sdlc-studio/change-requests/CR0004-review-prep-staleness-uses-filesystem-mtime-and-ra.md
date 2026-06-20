# CR-0004: review_prep staleness uses filesystem mtime and raw-string timestamp comparison, breaking determinism across clones and timestamp formats

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Requester:** Adversarial Audit
> **Date:** 2026-06-20
> **Affects:** .claude/skills/sdlc-studio/scripts/review_prep.py
> **Depends on:** --
> **GitHub Issue:** --

## Summary

review_prep derives last_modified from st_mtime (reset by every clone/pull/checkout) instead of the git log timestamp the docs mandate, and compares it to last_reviewed as a raw string with no parse, so staleness verdicts are non-reproducible and silently wrong when formats differ.

## Problem

Two compounding defects in the same comparison. (1) review_prep.staleness derives last_modified from path.stat().st_mtime (review_prep.py:29-32, :49-52) but reference-review.md:250-251 mandates the git log timestamp. clone/pull/checkout/worktree reset mtime to 'now', so after any of those every artifact compares greater than the stored last_reviewed and the whole repo flags as needs_review; git commit time is stable, mtime is not. (2) needs_review is decided by the lexical comparison 'modified > last_reviewed' (review_prep.py:52), but last_reviewed is whatever Claude wrote (reference-review.md:249, 'current ISO timestamp', no enforced format). Mixing date-only ('2026-06-20'), non-Z offsets ('+01:00'), and Z-ISO makes the string comparison no longer a valid time comparison, with no parse, normalisation, or validation.

## Proposed Changes

### Item 1: review_prep staleness uses filesystem mtime and raw-string timestamp comparison, breaking determinism across clones and timestamp formats

**Priority:** High **Effort:** TBD

Replace _mtime_iso with a git-derived timestamp ('git log -1 --format=%cI -- <path>', falling back to st_mtime only when untracked or git is unavailable, labelling the method in the JSON). Parse both sides with datetime.fromisoformat (normalise trailing Z to +00:00, treat naive as UTC) and compare as datetimes; if last_reviewed fails to parse, treat the artifact as needs_review and emit a warning so the malformed state is surfaced rather than silently mis-compared.

## Impact Assessment

### Existing Functionality

On any fresh clone, pull, or worktree the staleness leg reports every artifact as needing review, and verdicts can be wrong in either direction when stored timestamp formats drift, with no signal the comparison was invalid - wasting review effort and undermining trust in the deterministic inputs the unified review starts from. Quality risk high.

## Acceptance Criteria

- [ ] Change implemented and verified; lint and tests green.

## Out of Scope

- Implementation is downstream; this CR records the audit finding.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Adversarial Audit | Filed from the 2026-06-20 audit (lens: determinism; evidence: .claude/skills/sdlc-studio/scripts/review_prep.py:49-52 (modified = `_mtime_iso(path)`; needs = ... modified > last_reviewed) vs reference-review.md:250-251 (mandates git log timestamp)) |
