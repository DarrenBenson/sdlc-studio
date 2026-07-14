# CR-0253: The sprint-close review is not gated - make review currency a hard gate like the retro

> **Status:** Proposed
> **Priority:** P1
> **Type:** Improvement
> **Date:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

reference-sprint.md:145 names the close as reconcile + review + retro. Reconcile blocks on drift; retro was promoted from doctrine to a hard gate (RFC0032, 'a hard gate, not doctrine'). Review was NOT: the only currency signal, `doc_freshness` (LATEST.md staleness), is blocking=False - advisory, never blocks. The other leg, review-legs, checks the document legs EXIST, not that a review was run or that LATEST.md is current for the batch (presence, not currency - BG0123's lesson: existence is not evidence). So a sprint can close with a stale review, and one did: LATEST.md still claims '4.1.0 READY TO TAG - backlog empty' while the backlog is 11+ and a major workstream (RFC0032) shipped since. The ungated ceremony got skipped - exactly the failure the retro gate was built to stop, one leg over.

## Impact

Every sprint close. The unified review (and its LATEST.md anchor, the documented first-read for a fresh conversation) can rot silently - a new session orients on a stale claim. The dogfooding contract (reconcile+review+retro at close) is only two-thirds enforced.

**Effort:** M

## Acceptance Criteria

- [ ] A blocking gate leg (e.g. --require-review, mirroring --require-retro) FAILS a sprint close when artefacts have changed since LATEST.md was written. The deterministic input already exists (`review_prep.staleness` / `needs_review)`; wire it to a blocking leg. `doc_freshness` stays, or is folded in. Validate against the bug it defends (LL0010): a close with a stale LATEST.md must FAIL. Verify: rg -q 'require.review\|review.currency' .claude/skills/sdlc-studio/scripts/gate.py

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Raised |
