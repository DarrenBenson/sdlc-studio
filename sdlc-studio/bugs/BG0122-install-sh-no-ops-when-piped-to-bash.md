# BG0122: install.sh no-ops when piped to bash (curl | bash installs nothing)

> **Status:** Fixed
> **Verification depth:** functional
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Severity:** Critical

## Summary

The source-vs-execute guard at the bottom of install.sh compares ${`BASH_SOURCE[0]`} to $0. Piped to bash the script is read from stdin, so `BASH_SOURCE[0]` is unset while $0 is 'bash'. The test fails, main is never called, and the installer defines its functions, falls off the bottom and exits 0 - no output, no error, no install. This is the exact invocation the README advertises.

## Steps to Reproduce

Run the README's one-line install. It prints nothing, exits 0, and installs nothing:

```bash
curl -fsSL https://raw.githubusercontent.com/DarrenBenson/sdlc-studio/main/install.sh | bash
```

Contrast with the same script run as a file, which installs correctly:

```bash
curl -fsSL https://raw.githubusercontent.com/DarrenBenson/sdlc-studio/main/install.sh -o install.sh
bash install.sh   # works
```

## Proposed Fix

Use ${`BASH_SOURCE[0]`:-$0} so the fallback makes the comparison bash==bash when piped. Keeps file execution working and still suppresses main when sourced.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Created via `new` (deterministic) |
