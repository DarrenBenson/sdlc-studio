# CR-0122: reconcile apply signposts fix-order and emits expected filenames for new index rows

> **Status:** Complete
> **Created:** 2026-06-25
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Improvement

## Summary

Two reconcile-workflow ergonomics gaps the field upgrade surfaced, both about the tool not guiding the
operator through its own correct use:

- **Order-of-operations is unsignposted, and drift cascades.** Fixing the status-vocab values in files
  immediately created new index status-mismatches (file vs index now disagree), so the drift count went
  4 -> 9 after fixing *started*. Counts and summaries must be recomputed **dead last**, after every
  status edit settles - but nothing tells you that ordering. The operator learned it only by watching
  the count move the wrong way. reconcile should either signpost the recommended sequence (fix files ->
  re-sync index rows -> recompute counts last) or sequence it itself.
- **New-row link needs a filename guess.** reconcile reports a missing index row by id (e.g. BG0136) but
  not the expected filename, so wiring the index link is a guess - the operator got it wrong first try
  (`-suspense.md` vs `-suspense-csr-bail.md`). reconcile knows the file on disk; it should emit the
  resolved filename/relative path, not just the id.

These are the trust-the-summary problems alongside the correctness defects [[BG0043]]/[[BG0044]]: even
when reconcile is right, it under-guides.

## Acceptance Criteria

- [ ] reconcile output states the recommended fix order (resolve file/index status mismatches first;
      recompute counts/summaries last) when both status drift and count drift are present - or applies
      that ordering itself so counts are recomputed after status edits settle
- [ ] a missing or mismatched index row finding emits the artifact's actual filename / relative path on
      disk (not only the bare id), so the index link can be wired without guessing
- [ ] documented in reference-reconcile.md; unit tests cover the filename emission and the
      ordering signpost; CHANGELOG

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-25 | field | Created via `new` (deterministic) |
