# BG0054: install.sh exits 1 after a successful install when the sweep refreshes another copy (set -e)

> **Status:** Closed
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Severity:** High
> **Raised-by:** Sam Eriksson (QA amigo), repository review RV0006
> **Effort:** S

## Summary

When the stale-copy sweep actually refreshes at least one other tool's copy, `sweep_stale`
returns non-zero and, under `set -e`, terminates the installer before it prints the success
and next-steps output - even though the install succeeded.

## Evidence

- `install.sh:6` (`set -e`), `install.sh:307` - the function's last command is
  `[[ "$found" == false ]] && info "sweep: no other sdlc-studio copies found"`; when
  `found=true` this compound returns 1.
- `install.sh:374` - call site inside the main flow.
- Reproduced: `bash -c 'set -e; f(){ local found=true; [[ "$found" == false ]] && echo x; }; f; echo AFTER'`
  exits 1 without printing `AFTER`.

## Impact

Any user with sdlc-studio copies in two or more tool locations - the exact case the sweep
exists for - sees the installer exit non-zero and skip the "installed for" / "next steps"
output. A `curl | bash` user or a CI step reads a failed install that in fact succeeded.

## Steps to Reproduce

1. Have a stale sdlc-studio copy in a second target dir (e.g. `~/.gemini/skills/sdlc-studio`).
2. Run `install.sh` for the primary target with the sweep enabled.
3. Sweep refreshes the second copy; script exits 1 and omits the success banner.

## Proposed Fix

End `sweep_stale` with an explicit statement rather than a bare `&&` test:
`if [[ "$found" == false ]]; then info "..."; fi`, or append `return 0`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | Sam Eriksson (QA amigo) | Created via `new` (deterministic) |
| 2026-07-06 | Sam Eriksson (QA amigo) | Repro confirmed; filed from RV0006 code-level leg |
| 2026-07-06 | Dani Okafor (Engineering amigo) | Fixed with a failing-first regression test on branch sprint/rv0006-bugfixes; transitioned to Closed |
