# BG0454: the confinement write detector reads list.remove as a filesystem write, so a read-only module is censused as a workspace writer

> **Status:** Fixed
> **Verification depth:** functional (tests red-first, both directions; BG0454's fix exposed a false allowlist exemption the rotted-entry guard then caught)
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_confinement.py
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** 2026-07-29T15:35:33Z

## Summary

`_write_surface` in `test_confinement.py` keys on the bare attribute name `remove`, so `ids.remove(uid)` on a plain list reports the write surface `{'remove'}`. `sprint_report.py` is read-only by construction - it composes the end-of-sprint page and the checklist and opens nothing for writing - and it was still censused into the writer roster, failing `test_every_writer_is_covered_or_allowlisted` until the list mutation was rewritten as a comprehension.

## Steps to Reproduce

python3 -c "import sys; sys.path.insert(0,'.claude/skills/sdlc-studio/scripts/tests'); from `test_confinement` import `_write_surface`; print(`_write_surface(`'ids = [1]\nids.remove(1)'))"  ->  {'remove'}

## Proposed Fix

Narrow the `remove` rule the way the `open` rules are already narrowed: qualify it (`os.remove`, `os.unlink`, `shutil.*`) or require path evidence on the receiver, and add the two positive controls (`os.remove(p)` still detected, `ids.remove(x)` not). Keep the over-inclusive principle everywhere else.

## Acceptance Criteria

### AC1: a list `remove` is not a filesystem write

- **Given** a module whose only `remove` is `ids.remove(uid)` on a plain list, or `seen.remove(x)` on a set
- **When** the write-surface detector runs
- **Then** it reports no write surface - keying on the bare attribute name censused a read-only module onto the writer roster, and the remedy the sweep offers is an allowlist entry: an exemption for a module that writes nothing reads exactly like a real one, so the roster's meaning erodes one honest-looking line at a time
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_confinement.py::ConfinementRosterSweepTests::test_a_list_remove_is_not_a_filesystem_write
- **Verified:** yes (2026-07-31)

### AC2: a qualified `remove` is still detected

- **Given** `os.remove(p)`, `shutil.rmtree(p)` and `p.unlink()`
- **When** the detector runs
- **Then** each is still reported - over-inclusion is the right default for this detector and relaxing it for the ONE name a mainstream type shares at the same arity must not lose the real call. `unlink` has no such collision and stays over-included
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_confinement.py::ConfinementRosterSweepTests::test_a_QUALIFIED_remove_is_still_detected
- **Verified:** yes (2026-07-31)

### AC3: the allowlist entry the false positive justified is retired

- **Given** the confinement allowlist
- **When** the roster is swept
- **Then** it carries no entry that no longer writes - `conformance.py` was exempted as "removes only its own scratch file" when its only `remove` was `required.remove("critiqued")` on a list, so the exemption was false from the day it was written. The rotted-entry guard is what caught it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_confinement.py::ConfinementRosterSweepTests::test_allowlist_has_no_rotted_entries
- **Verified:** yes (2026-07-31)

## Impact

The remedy the guard offers is an allowlist entry, and an allowlist entry for a module that writes nothing is a false exemption that reads as a real one - so the roster's meaning erodes one honest-looking line at a time. Over-inclusion is the deliberate direction for this detector and that is right, but `remove` is the one name in its set that a very common non-filesystem type also carries: `list.remove`, `set.remove`, and `dict`-like shims. The detector already distinguishes call FORMS for `open` (builtin, attribute, module-qualified) and could narrow `remove` the same way - a bare-name attribute call on a value with no path evidence beside it, versus `os.remove` / `shutil.rmtree` / `Path.unlink`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | sdlc-studio | Filed |
