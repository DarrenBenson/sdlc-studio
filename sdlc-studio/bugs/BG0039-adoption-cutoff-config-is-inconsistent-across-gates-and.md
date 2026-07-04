# BG0039: adoption cutoff config is inconsistent across gates and silently fails

> **Status:** Closed
> **Created:** 2026-06-25
> **Created-by:** sdlc-studio new
> **Severity:** high

## Summary

Two adoption cutoffs that look identical in the same `.config.yaml` are parsed by different code
with different value formats AND different boundary operators, and one fails silently. A field
agent upgrading a consuming project rated this the single worst trap of the run.

- `conformance.adopt_after` is parsed via `id_number(str(cutoff))` (`conformance.py:56`), so it
  needs the **prefixed** form `US0103`. A bare `103` makes `id_number("103")` return `None`, the
  cutoff is dropped, and the gate stays red with **no error** - it just keeps failing.
- `provenance.adopt_after` is parsed via `int(... or 0)` (`provenance.py:70`), so it needs the
  **bare integer** `103`; the prefixed `US0103` would not behave the same way.
- The comparison also diverges: conformance exempts `rid_num < cutoff_num` (strict, `conformance.py:125`,
  so `adopt_after: US0103` still judges US0103 itself - off-by-one against the plain reading
  "US0103 and earlier are grandfathered"); provenance exempts `idn <= cutoff` (`provenance.py:78`).

Same-looking key, two parsers, two operators, one silent failure. The operator only diagnosed it
by calling `id_number` directly after the gate refused to move.

## Steps to Reproduce

1. In a consuming project set `conformance.adopt_after: 103` (bare int) to grandfather pre-103 units.
2. Run `gate` / `conformance.py`. The cutoff is silently ignored (`id_number("103") -> None`); every
   pre-103 Done unit is still flagged. No message explains why the cutoff had no effect.
3. Set `provenance.adopt_after: US0103` (prefixed) - it does not behave as the bare-int form does.
4. Note `adopt_after: US0103` on conformance exempts `< 103`, so US0103 itself is still judged.

## Proposed Fix

Unify cutoff parsing behind one shared helper (in `lib/sdlc_md.py`) that accepts BOTH a bare
integer and a prefixed id (`US0103` / `103` / `CR0103`) and returns the numeric id, and use one
agreed boundary operator across gates (decide `<=` "this id and earlier are exempt" to match the
name, and document it). The helper must **error loudly** on an unparseable cutoff rather than
returning `None` and silently disabling the gate. Update `conformance.py` and `provenance.py` to
call it; align the comparison. Unit tests: bare int and prefixed id both parse on both gates; an
unparseable value raises a clear config error (not a silent no-op); the boundary id is exempt.
CHANGELOG. Relates to [[CR0121]] (the gate should also point at this remedy).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-25 | field | Created via `new` (deterministic) |
