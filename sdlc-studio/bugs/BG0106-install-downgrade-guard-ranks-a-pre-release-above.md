# BG0106: install downgrade guard ranks a pre-release above its own release - rc users refused the GA upgrade

> **Status:** Fixed
> **Verification depth:** functional (red-first: rc->GA, GA->rc, rc ordering; critic drove 17 edge cases incl. build metadata and the BG0100 scenario)
> **Severity:** High
> **Created:** 2026-07-10
> **Created-by:** sdlc-studio file

## Summary

`version_lt` in install.sh compares with plain sort -V, which orders 4.0.0 before 4.0.0-rc.1; semver pre-release precedence is the reverse (rc.1 precedes the release). Consequence: every copy installed at 4.0.0-rc.1 is refused the 4.0.0 GA upgrade with a 'NEWER than' warning unless --allow-downgrade is forced - discovered live when the GA forward-port to the local installed copy was silently refused. Fix: compare semver cores with sort -V, and when cores are equal apply pre-release precedence (a suffixed version is OLDER than its unsuffixed release; two suffixes compare via sort -V).

## Steps to Reproduce

install a copy at 4.0.0-rc.1; run install.sh --from <4.0.0 payload> -> 'is at 4.0.0-rc.1, NEWER than the 4.0.0 being installed - refusing'

## Proposed Fix

core/suffix split in `version_lt` with semver pre-release precedence; red-first tests for rc->GA upgrade, GA->rc refusal, rc.1->rc.2

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | audit | Filed |
