# BG0100: install.sh sweep overwrites a git-tracked repo working tree with the downloaded release (working-tree data loss)

> **Status:** Open
> **Severity:** High
> **Created:** 2026-07-10
> **Created-by:** sdlc-studio file

## Summary

Running install.sh from inside the development repo downloads the PUBLISHED release from GitHub (remote main), then its post-install sweep 'refreshes' every sdlc-studio copy it finds on the machine - INCLUDING the repo's own .claude/skills/sdlc-studio, the git-tracked source of truth. When the remote is behind the working tree (e.g. unpushed v4 work while the tag is frozen at 3.6.0), the sweep silently reverts the working tree to the older downloaded version. Only committed work survives (via git restore); uncommitted work in the skill dir would be lost. Compounding gap: install.sh has no local-source mode (--local sets install SCOPE, not source), so there is no supported way to install the local working copy to test an unreleased version - the manual cp -r is the only path.

## Steps to Reproduce

1. Be in the dev repo with local work ahead of the published release (e.g. 4.0.0-rc.1 local, remote main at 3.6.0). 2. Run ./install.sh (no --no-sweep). 3. Observe 'refreshed: <repo>/.claude/skills/sdlc-studio (4.0.0-rc.1 -> 3.6.0)' - the repo working tree is now the OLD downloaded version; git status shows ~199 files reverted/deleted.

## Proposed Fix

The sweep must never refresh a git-tracked working tree: skip any candidate dir that sits under a git repo whose HEAD tracks it (or that is the install SOURCE), detecting a .git ancestor and excluding it. Separately, add a real local-source install (e.g. --from ./ or install detecting it runs inside the repo and offering to install the local tree) so an unreleased version can be dogfood-tested without cp -r. Until fixed, document that ./install.sh from within the repo requires --no-sweep.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | audit | Filed |
