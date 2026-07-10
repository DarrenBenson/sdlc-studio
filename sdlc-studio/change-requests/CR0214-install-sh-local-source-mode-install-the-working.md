# CR-0214: install.sh local-source mode: install the working tree, not the published release

> **Status:** Complete
> **Verification depth:** functional (live e2e in a scratch HOME: --from installs the working tree - session markers present, no download; a non-skill dir refuses rc 2 before any write; the downgrade guard still applies to a local source - all also unit-asserted; docs/INSTALL gains the dev-testing flow; tools suite 124)
> **Priority:** Medium
> **Type:** Improvement
> **Date:** 2026-07-10
> **Created-by:** sdlc-studio file

## Summary

BG0100 follow-up. install.sh only ever downloads the published release; --local sets install SCOPE, not source. There is no supported way to install unreleased work for testing - the v4 forward-port had to be a hand rsync. The downgrade guard (BG0100) stops the data loss, but the workflow gap remains: 'test before GA' requires installing the local tree.

## Acceptance Criteria

- [ ] install.sh --from <dir> (or auto-detect when run inside the skill source repo) installs the local tree instead of downloading
- [ ] The local-source path passes the same identity/downgrade guards and supports --dry-run and the sweep
- [ ] README/INSTALL document the dev-testing flow (local-source install; --no-sweep note)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | audit | Raised |
