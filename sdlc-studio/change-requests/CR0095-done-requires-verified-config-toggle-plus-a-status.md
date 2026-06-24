# CR-0095: done-requires-verified config toggle plus a status unverified-manual lane

> **Status:** Complete
> **Created:** 2026-06-24
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Feature

## Summary

**Estimate: 3 points.** The deferred half of CR0084: (1) a `quality.done_requires_verified`
config toggle so a project can make the story->Done verify-gate **hard for everyone**
(currently default-on with a per-call `--force`; the toggle lets a team set the policy in
`.config.yaml`), and (2) a `status` **unverified/manual lane** - `status.py` reads
`verify-report.json` and surfaces "Done with unverified ACs" and the manual-AC count as their
own line, so env-bound/manual ACs read as "deferred", not as silent gaps.

## Acceptance Criteria

- [x] `quality.done_requires_verified` (default true) is read via `config.py`; when false the
      story->Done gate (CR0084) is advisory-warn instead of blocking
- [x] `status` reads `verify-report.json` and reports a lane: stories Done-with-unverified-ACs
      (drift) and the manual-AC count (informational), distinct from failures
- [x] reuses the existing report + config readers (no new verification path)
- [x] unit tests: toggle flips the gate; status surfaces the lane; CHANGELOG entry (LL0004)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-24 | sdlc | Created via `new` (deterministic) |
