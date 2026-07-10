# EP0027: Reliability tier: crash-safe, resumable, honest under failure

> **Status:** Done
> **Verification depth:** functional (11/11 units delivered, each independently critic-approved; closing full-diff critic APPROVE - no cross-unit failures, BG0081/82/91 interactions reproduced correct; scenario-04 eval regression PASS; suite 1522 + tools 110 green, gate PASS, drift 0)
> **Created:** 2026-07-10
> **Created-by:** sdlc-studio new

## Summary

Every reproduced High in RV0007 lived in a crash, resume or concurrent window. This
epic finishes the concurrency floor CR0183 started, makes multi-step writers resumable or
honestly failing, and makes the verify oracle trustworthy - the reliability tier RFC0027 names
as what separates the project from world-class. Runs second, pre-tag.

## Story Breakdown

Unit roster (bugs fixed directly; CRs decompose via `cr action` at execution - stories land under this epic):

- [x] [BG0076](../bugs/BG0076-cr0183-concurrency-floor-is-incomplete-file-finding-and.md) - CR0183 floor completion: lock file_finding/new_batch/meta_new; atomic-write sweep
- [x] [BG0081](../bugs/BG0081-a-reopened-after-archive-artefact-creates-permanent-drift.md) - archive rows shadow live rows: permanent un-clearable drift on reopen
- [x] [BG0082](../bugs/BG0082-reconcile-index-rewriter-bleeds-a-stale-status-column.md) - index rewriter bleeds Status into status-less tables (silent corruption)
- [x] [BG0083](../bugs/BG0083-verify-ac-story-discovery-executes-companions-and-any.md) - verify_ac executes companions / any us*.md (shell from non-story docs)
- [x] [BG0084](../bugs/BG0084-verify-ac-run-story-with-a-missing-path.md) - verify_ac --story missing path exits 0 (false green)
- [x] [BG0089](../bugs/BG0089-verify-ac-run-root-mixes-roots-story-discovery.md) - verify_ac --root mixes cwd and root; Done gate reads a report never written
- [x] [BG0091](../bugs/BG0091-archive-py-is-not-idempotent-per-release-a.md) - archive.py duplicates rows on crash-resume; policy divergence
- [x] [BG0092](../bugs/BG0092-github-sync-push-exits-0-and-stamps-last.md) - github_sync push exits 0 and stamps last_push on total failure
- [x] [CR0205](../change-requests/CR0205-installers-replace-delete-then-copy-with-copy-then.md) - installers: copy-then-swap, never delete-then-copy
- [x] [CR0206](../change-requests/CR0206-github-sync-push-adopt-an-existing-issue-by.md) - push adopts an existing issue by title (crash/timeout dedupe)
- [x] [CR0207](../change-requests/CR0207-reliability-debt-low-themed-permissions-pagination-growth-scale.md) - reliability debt themed: perms, pagination, growth, scale, crash windows (14 items)
- [x] [US0117: Installers copy-then-swap so a failed install cannot destroy the previous one](../stories/US0117-installers-copy-then-swap-so-a-failed-install.md)
- [x] [US0118: github_sync push adopts an existing issue by title instead of blind create](../stories/US0118-github-sync-push-adopts-an-existing-issue-by.md)
- [x] [US0119: Reliability debt batch: atomic-write perms, atomic .local state, sync/scale hardening](../stories/US0119-reliability-debt-batch-atomic-write-perms-atomic-local.md)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | sdlc | Created via `new` (deterministic) |
