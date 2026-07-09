# CR-0206: github_sync push: adopt an existing issue by title instead of blind create (dedupe across crash/timeout)

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Date:** 2026-07-09
> **Created-by:** sdlc-studio file

## Summary

cmd_push runs gh_issue_create (remote write) then set_github_issue_field (local stamp, itself non-atomic write_text at github_sync.py:328) at :440-444. A crash between them - or a gh timeout (rc 124 at :93-95) after the server accepted the request - leaves the record unstamped, and the re-run creates a second GitHub issue for the same artefact. Nothing checks for an existing '[CR-0001]'-titled issue before creating. Cross-system non-atomicity with no reconciliation. Found by RV0007.

## Acceptance Criteria

- [ ] Before create, push looks up open issues titled with the record id (or by label) and adopts instead of creating
- [ ] The local stamp goes through atomic_write
- [ ] A test simulates create-succeeded-stamp-lost and shows the re-run adopts, not duplicates

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | audit | Raised |
